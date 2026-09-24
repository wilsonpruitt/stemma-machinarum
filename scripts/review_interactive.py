#!/usr/bin/env python3
"""Interactive reviewer for staged candidates -- the sign-off step, made
into a guided walkthrough instead of hand-editing JSON.

Walks data/staging/models/ in a safe order (a candidate whose accepted
edges point at another staged candidate comes after it, so parents
promote before children), shows a plain-English summary of each one,
and lets you approve or skip it. Approving sets `_candidate.reviewed:
true` and immediately runs scripts/promote.py -- you never touch the
JSON by hand, and nothing reaches data/ without your say-so here.

Usage:
    python3 scripts/review_interactive.py [--by "Your Name"] [--list]

--list just prints the computed order and a one-line summary of each
candidate, with no prompts -- useful to see the whole queue first.

At each candidate:
    a  approve and promote it now
    A  approve this and every remaining candidate, no more prompts
    s  skip (leaves it in staging; come back later)
    d  show the full staged JSON for this one
    q  quit -- everything not yet promoted stays in staging, untouched
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGING = ROOT / "data" / "staging" / "models"


def load_all():
    return {p.stem: json.loads(p.read_text()) for p in STAGING.glob("*.json")}


def order(candidates):
    """Topological sort on accepted edges whose parent is itself a staged
    candidate. A cycle or other snag just means that ordering couldn't be
    fully worked out -- the leftovers go in alphabetically, flagged, rather
    than silently guessing."""
    ids = set(candidates)
    deps = {cid: set() for cid in ids}
    for cid, d in candidates.items():
        for e in d["_candidate"]["edges"]:
            if e["accept"] is True and e.get("parent") in ids:
                deps[cid].add(e["parent"])
    placed, remaining, seq = set(), set(ids), []
    while remaining:
        ready = sorted(c for c in remaining if deps[c] <= placed)
        if not ready:
            seq += [(c, True) for c in sorted(remaining)]
            break
        for c in ready:
            seq.append((c, False))
            placed.add(c)
            remaining.discard(c)
    return seq


def summarize(cid, d):
    c = d["_candidate"]
    lines = [f"\n{'=' * 72}", f"{cid}   ({c['repo']})", "=" * 72]

    undecided = [e for e in c["edges"] if e["accept"] is None]
    if undecided:
        lines.append("⚠ NEEDS YOUR READ -- an edge below has no decision yet. This is the")
        lines.append("  actual judgment call; everything else here is settled.")
    else:
        lines.append("✓ Routine. Every edge below already has a decision, with the reasoning")
        lines.append("  right next to it -- there's nothing here that needs weighing, just a")
        lines.append("  read to confirm it looks right. What follows the edges (if anything)")
        lines.append("  is FYI for later, not something to decide today.")

    lines.append(f"\ndeveloper:    {d['developer']}")
    lines.append(f"release:      {d['release_date'].get('value')}  [{d['release_date']['status']}]")
    lines.append(f"license:      {d['license'].get('value')}  [{d['license']['status']}]")
    lines.append(f"availability: {d['availability']['value']}  (checked {d['availability']['checked']})")
    arch = d["architecture"]
    dims = ", ".join(f"{k}={v.get('value')}" for k, v in arch.items()
                      if isinstance(v, dict) and "value" in v and v.get("value") is not None)
    lines.append(f"architecture: {arch.get('family')}" + (f"  ({dims})" if dims else ""))
    lines.append("")
    lines.append("edges -- the actual lineage decision, one per parent:")
    for e in c["edges"]:
        mark = {True: "ACCEPT ", False: "reject ", None: "?? YOUR CALL ??"}[e["accept"]]
        parent = e.get("parent") or f"UNRESOLVED({e.get('parent_hf')})"
        lines.append(f"  [{mark}] -> {parent:30s} {e.get('relation') or '?':28s} [{e.get('evidence')}]")
        if e.get("note"):
            note = e["note"]
            lines.append(f"             {note[:220]}" + ("..." if len(note) > 220 else ""))
    if c["flags"]:
        lines.append("")
        lines.append("for later (not blocking; nothing to decide today):")
        for f in c["flags"]:
            lines.append(f"  • {f}")
    if c.get("review_notes"):
        lines.append("")
        lines.append(f"review notes: {c['review_notes']}")
    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    reviewer = args[args.index("--by") + 1] if "--by" in args else "Wilson Pruitt"
    list_only = "--list" in args

    candidates = load_all()
    if not candidates:
        print("Nothing staged in data/staging/models/.")
        return
    seq = order(candidates)

    if list_only:
        print(f"{len(seq)} candidate(s), in promotion order:\n")
        for i, (cid, flagged) in enumerate(seq, 1):
            d = candidates[cid]
            n_accept = sum(1 for e in d["_candidate"]["edges"] if e["accept"] is True)
            n_undecided = sum(1 for e in d["_candidate"]["edges"] if e["accept"] is None)
            note = "  ⚠ order unresolved -- check its parent is promoted first" if flagged else ""
            undecided_note = f"  ({n_undecided} edge(s) still undecided!)" if n_undecided else ""
            print(f"{i:3d}. {cid:32s} {n_accept} edge(s) to accept{undecided_note}{note}")
        return

    approve_all = False
    promoted, skipped = [], []
    for i, (cid, flagged) in enumerate(seq, 1):
        path = STAGING / f"{cid}.json"
        if not path.exists():
            continue  # promoted earlier in this same run, or removed
        d = json.loads(path.read_text())
        n_undecided = sum(1 for e in d["_candidate"]["edges"] if e["accept"] is None)

        print(f"\n[{i}/{len(seq)}]" + (" ⚠ ordering couldn't be fully worked out -- confirm its parent is already promoted" if flagged else ""))
        print(summarize(cid, d))
        if n_undecided:
            print(f"\n⚠ {n_undecided} edge(s) above still show [??????] -- this candidate needs a decision before it can promote cleanly.")

        if approve_all:
            choice = "a"
        else:
            while True:
                choice = input("\n[a]pprove  [A]pprove all remaining  [s]kip  [d]etails  [q]uit > ").strip()
                if choice == "d":
                    print(json.dumps(d, indent=2, ensure_ascii=False))
                    continue
                if choice in ("a", "A", "s", "q"):
                    break
                print("type a, A, s, d, or q")
            if choice == "A":
                approve_all, choice = True, "a"

        if choice == "q":
            print(f"\nStopped. Promoted {len(promoted)}, skipped {len(skipped)}, {len(seq) - i} not reached.")
            break
        if choice == "s":
            skipped.append(cid)
            continue

        d["_candidate"]["reviewed"] = True
        path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "promote.py"), cid, "--by", reviewer],
                                capture_output=True, text=True)
        print(result.stdout.strip())
        if result.returncode != 0:
            print(result.stderr.strip())
            print(f"NOT promoted -- {cid} stays in staging.")
            d["_candidate"]["reviewed"] = False
            path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
            skipped.append(cid)
        else:
            promoted.append(cid)
    else:
        print(f"\nDone. Promoted {len(promoted)}, skipped {len(skipped)}.")

    if promoted:
        print("Promoted:", ", ".join(promoted))
    if skipped:
        print("Still in staging:", ", ".join(skipped))


if __name__ == "__main__":
    main()
