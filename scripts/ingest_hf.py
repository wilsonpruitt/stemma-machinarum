#!/usr/bin/env python3
"""Pull candidate model records from the Hugging Face Hub into data/staging/.

Output is CANDIDATE data only. It never writes into data/models/ or
data/edges/. Each candidate is a model record in Stemma's schema plus a
`_candidate` block (provenance, flags for the reviewer, proposed edges).
`scripts/promote.py` moves a candidate into data/ once a person has
reviewed it and set `_candidate.reviewed` to true.

What the Hub can and can't tell us, and how the candidate records it:
  - config.json (pinned to the repo's commit) -> architecture values,
    status "recorded". The config does not say what positional encoding
    or normalization the code uses, so those stay not_recorded, with a
    hint in the flags.
  - Card metadata `base_model` is the uploader's claim -> candidate edge
    with evidence `declared_by_uploader`. If the card doesn't state
    `base_model_relation`, the Hub infers one and publishes it as a tag;
    the candidate uses that tag and says the relation is the Hub's guess.
  - Card metadata `datasets` -> candidate trained_on edges, also
    uploader-declared (these are often incomplete: an instruct model may
    list only its base model's pretraining corpus).
  - Repo creation date -> release_date with status "partial".

HF_TOKEN is read from the environment if set (never hardcoded).
Usage:
    python3 scripts/ingest_hf.py <repo-id> [<repo-id> ...]
    python3 scripts/ingest_hf.py --list scripts/pilot_candidates.txt
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
STAGING_DIR = DATA_DIR / "staging"
HF = "https://huggingface.co"
HF_TOKEN = os.environ.get("HF_TOKEN")
RATE_LIMIT_SECONDS = 1.0
TODAY = time.strftime("%Y-%m-%d", time.gmtime())

# Hub tag relation -> Stemma relation
TAG_RELATION = {
    "finetune": "fine_tuned_from",
    "adapter": "adapter_on",
    "merge": "merged_from",
    "quantized": "quantized_from",
}

# First config key present wins. Names differ by model family.
CONFIG_KEYS = {
    "n_layers": ["num_hidden_layers", "n_layer", "num_layers", "n_layers"],
    "hidden_size": ["hidden_size", "n_embd", "d_model"],
    "n_heads": ["num_attention_heads", "n_head", "num_heads", "n_heads"],
    "vocab_size": ["vocab_size"],
    "context_length": ["max_position_embeddings", "n_positions", "max_seq_len", "seq_length"],
}


def fetch(url):
    """Return (status, body_text). Network errors come back as status 0."""
    req = urllib.request.Request(url, headers={"User-Agent": "stemma-ingest"})
    if HF_TOKEN:
        req.add_header("Authorization", f"Bearer {HF_TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except urllib.error.URLError:
        return 0, ""


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    s = re.sub(r"-+", "-", s)
    # "-hf" marks a Hugging Face format conversion, not a different model
    return re.sub(r"-hf$", "", s)


def load_crosswalk():
    """Map HF repo id (lowercased) -> Stemma id, from identifiers.huggingface."""
    walk, ids = {}, set()
    for sub in ("models", "datasets"):
        for path in (DATA_DIR / sub).glob("*.json"):
            rec = json.loads(path.read_text())
            ids.add(rec["id"])
            for repo in rec.get("identifiers", {}).get("huggingface", []):
                walk[repo.lower()] = rec["id"]
    return walk, ids


def sourced(value, source, status="recorded", note=None):
    d = {"value": value, "source": source, "status": status}
    if note:
        d["note"] = note
    return d


def not_recorded(note=None):
    d = {"value": None, "status": "not_recorded"}
    if note:
        d["note"] = note
    return d


def build_candidate(repo, info, info_status, config, config_url, walk, taken, reuse_id=None, staged=None):
    card = info.get("cardData") or {}
    sha = info.get("sha")
    author = info.get("author") or repo.split("/")[0]
    repo_url = f"{HF}/{repo}"
    card_url = f"{HF}/{repo}/blob/{sha}/README.md" if sha else repo_url
    flags = []

    cid = reuse_id or slug(repo.split("/")[1])
    if not reuse_id and cid in taken:
        cid = slug(repo.replace("/", "-"))
        flags.append(f"id '{slug(repo.split('/')[1])}' already taken; used org-prefixed id")

    # availability
    gated = info.get("gated")
    if info_status == 200:
        avail = {"value": "gated" if gated else "available", "checked": TODAY, "source": repo_url}
        if gated:
            avail["note"] = f"HF gate: {gated}."
    else:
        avail = {"value": "removed" if info_status in (401, 404) else "unknown", "checked": TODAY,
                 "source": repo_url, "note": f"HF API returned HTTP {info_status}."}

    # architecture from config
    arch = {"family": "unknown"}
    if config:
        archs = config.get("architectures") or []
        if any(a.endswith("ForCausalLM") or a.endswith("LMHeadModel") for a in archs):
            arch["family"] = "decoder_only"
            arch["note"] = f"family read from config 'architectures': {archs}."
        for field, keys in CONFIG_KEYS.items():
            key = next((k for k in keys if isinstance(config.get(k), int)), None)
            arch[field] = sourced(config[key], config_url) if key else not_recorded()
        if isinstance(config.get("num_key_value_heads"), int):
            arch["n_kv_heads"] = sourced(config["num_key_value_heads"], config_url)
        elif config.get("multi_query") is True:
            arch["n_kv_heads"] = sourced(1, config_url, note="config multi_query: true")
        hints = [k for k in ("rope_theta", "rotary_dim", "rotary_pct", "rotary_emb_base", "alibi", "position_embedding_type", "sliding_window") if k in config]
        if hints:
            flags.append(f"positional_encoding left not_recorded; config has {hints}: confirm from paper or code")
        arch["positional_encoding"] = not_recorded()
    else:
        for field in CONFIG_KEYS:
            arch[field] = not_recorded()
        arch["positional_encoding"] = not_recorded()
        flags.append("config.json not retrieved (gated, missing, or removed); architecture not_recorded")
    if arch["family"] == "unknown":
        flags.append("architecture family not determined from config")

    # license (uploader-declared metadata). Some cards give a list
    # (multi-license); take the first and note the rest.
    lic = card.get("license")
    lic_note = "From HF card metadata (uploader-declared); confirm against the license text."
    if isinstance(lic, list):
        lic_note += f" Card listed multiple licenses: {lic}; using the first."
        lic = lic[0] if lic else None
    license_f = sourced(lic, card_url, status="partial", note=lic_note) if lic else not_recorded()

    # created date as a weak release date
    created = (info.get("createdAt") or "")[:10]
    release = (sourced(created, f"{HF}/api/models/{repo}", "partial", "HF repo creation date; may predate or postdate public release.")
               if created else not_recorded())

    # proposed edges
    edges, unresolved = [], []
    tag_rel = {}
    for t in info.get("tags", []):
        m = re.match(r"base_model:(finetune|adapter|merge|quantized):(.+)$", t)
        if m:
            tag_rel[m.group(2).lower()] = m.group(1)
    bases = card.get("base_model") or []
    bases = [bases] if isinstance(bases, str) else bases
    card_rel = card.get("base_model_relation")
    staged = staged or {}
    for base in bases:
        parent = walk.get(base.lower())
        if not parent and base.lower() in staged:
            parent = staged[base.lower()]
            flags.append(f"parent '{parent}' is itself a staged candidate: promote it first")
        hub_rel = card_rel or tag_rel.get(base.lower())
        note = f"HF card metadata base_model: {base}."
        if card_rel:
            note += f" Card states base_model_relation: {card_rel}."
        elif hub_rel:
            note += f" Relation '{hub_rel}' is the Hub's inference (tag), not stated in the card."
        e = {"child": cid, "parent": parent, "parent_hf": base,
             "relation": TAG_RELATION.get(hub_rel), "evidence": "declared_by_uploader",
             "source": card_url, "note": note, "accept": None}
        if not parent:
            unresolved.append(base)
        edges.append(e)
    if not bases:
        flags.append("no base_model in card metadata: check the card text and papers for lineage")
    if bases and author.lower() == bases[0].split("/")[0].lower():
        flags.append("uploader org matches the base model's org: base_model claim may qualify as `declared`")

    datasets = card.get("datasets") or []
    datasets = [datasets] if isinstance(datasets, str) else datasets
    for ds in datasets:
        parent = walk.get(ds.lower())
        edges.append({"child": cid, "parent": parent, "parent_hf": ds, "relation": "trained_on",
                      "evidence": "declared_by_uploader", "source": card_url,
                      "note": f"HF card metadata datasets: {ds}. Often incomplete; confirm which training stage used it.",
                      "accept": None})
        if not parent:
            unresolved.append(ds)

    record = {
        "id": cid,
        "name": repo.split("/")[1],
        "identifiers": {"huggingface": [repo]},
        "developer": author,
        "release_date": release,
        "weights_status": "open" if info_status == 200 else "unknown",
        "availability": avail,
        "license": license_f,
        "architecture": arch,
        "training_data": not_recorded(),
        "techniques": [],
        "primary_sources": [repo_url] + ([config_url] if config else []),
        "record_history": [{"date": TODAY, "change": f"ingested as candidate from HF ({repo}@{sha})", "by": "ingest_hf.py"}],
        "_candidate": {
            "repo": repo, "sha": sha, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "reviewed": False,
            "review_notes": "",
            "flags": flags + ["developer is the HF uploader org: confirm the actual developer",
                              "training_data left not_recorded: fill from the card text or paper"],
            "unresolved_parents": unresolved,
            "edges": edges,
            "card_metadata": {k: card.get(k) for k in ("base_model", "base_model_relation", "datasets", "license", "language", "pipeline_tag") if card.get(k) is not None},
        },
    }
    return record


def review_report():
    lines = ["# Staging review queue", "",
             "Generated by `scripts/ingest_hf.py`. Nothing here is in Stemma yet.",
             "Procedure: `docs/review.md`. A preparer edits the JSON and writes",
             "`_candidate.review_notes`; the reviewer sets `_candidate.reviewed: true`",
             "and runs `python3 scripts/promote.py <id> --by \"<name>\"`.", ""]
    for path in sorted((STAGING_DIR / "models").glob("*.json")):
        rec = json.loads(path.read_text())
        c = rec["_candidate"]
        lines.append(f"## {rec['id']}  ({c['repo']})")
        lines.append(f"- reviewed: {c['reviewed']}")
        for f in c["flags"]:
            lines.append(f"- ⚑ {f}")
        for e in c["edges"]:
            parent = e["parent"] or f"UNRESOLVED ({e['parent_hf']})"
            lines.append(f"- edge → {parent}: {e['relation'] or 'relation ?'} [{e['evidence']}]")
        lines.append("")
    (STAGING_DIR / "REVIEW.md").write_text("\n".join(lines))


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    if args[0] == "--list":
        repos = [l.split("#")[0].strip() for l in Path(args[1]).read_text().splitlines()]
        repos = [r for r in repos if r]
    else:
        repos = args
    (STAGING_DIR / "models").mkdir(parents=True, exist_ok=True)
    walk, taken = load_crosswalk()
    staged = {}  # repo (lowercased) -> staged id, so a re-run overwrites its own candidate
    for p in (STAGING_DIR / "models").glob("*.json"):
        staged[json.loads(p.read_text())["_candidate"]["repo"].lower()] = p.stem

    for i, repo in enumerate(repos):
        if i:
            time.sleep(RATE_LIMIT_SECONDS)
        if repo.lower() in walk:
            print(f"skip   {repo}: already in Stemma as '{walk[repo.lower()]}'")
            continue
        status, body = fetch(f"{HF}/api/models/{repo}")
        info = json.loads(body) if status == 200 else {}
        config, config_url = None, None
        if info.get("sha"):
            config_url = f"{HF}/{repo}/raw/{info['sha']}/config.json"
            cstatus, cbody = fetch(config_url)
            if cstatus == 200:
                try:
                    config = json.loads(cbody)
                except json.JSONDecodeError:
                    config = None
        rec = build_candidate(repo, info, status, config, config_url, walk,
                              taken | set(staged.values()), reuse_id=staged.get(repo.lower()), staged=staged)
        (STAGING_DIR / "models" / f"{rec['id']}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
        staged[repo.lower()] = rec["id"]
        n_edges = len(rec["_candidate"]["edges"])
        print(f"staged {repo} -> {rec['id']} (HTTP {status}, config {'yes' if config else 'no'}, {n_edges} proposed edge(s), {len(rec['_candidate']['flags'])} flag(s))")
    review_report()
    print(f"review queue: {STAGING_DIR / 'REVIEW.md'}")


if __name__ == "__main__":
    main()
