#!/usr/bin/env python3
"""Move a reviewed candidate from data/staging/ into Stemma.

Refuses unless the reviewer has:
  - set `_candidate.reviewed` to true, and
  - set every proposed edge's `accept` to true or false; accepted edges
    need a resolved `parent` (a Stemma id), a `relation` and an `evidence`.

Then it strips `_candidate`, logs the review in `record_history`, writes
the record to data/models/, appends accepted edges to edges.jsonl, and
runs scripts/validate.py. If validation fails, every change is undone.

Usage:
    python3 scripts/promote.py <candidate-id> --by "Reviewer Name"
"""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGED = ROOT / "data" / "staging" / "models"
MODELS = ROOT / "data" / "models"
EDGES = ROOT / "data" / "edges" / "edges.jsonl"
EDGE_KEYS = ("child", "parent", "relation", "evidence", "source", "note")


def fail(msg):
    print(f"NOT PROMOTED: {msg}")
    sys.exit(1)


def main():
    args = sys.argv[1:]
    if len(args) != 3 or args[1] != "--by":
        fail('usage: promote.py <candidate-id> --by "Reviewer Name"')
    cid, reviewer = args[0], args[2]
    src = STAGED / f"{cid}.json"
    if not src.exists():
        fail(f"no staged candidate {src}")
    rec = json.loads(src.read_text())
    cand = rec.get("_candidate") or {}
    if cand.get("reviewed") is not True:
        fail("_candidate.reviewed is not true")
    dest = MODELS / f"{rec['id']}.json"
    if dest.exists():
        fail(f"{dest.name} already exists in data/models/")

    accepted = []
    for i, e in enumerate(cand.get("edges", [])):
        if e.get("accept") not in (True, False):
            fail(f"edge {i} ({e.get('parent_hf')}): set accept to true or false")
        if e["accept"]:
            missing = [k for k in ("parent", "relation", "evidence", "source") if not e.get(k)]
            if missing:
                fail(f"edge {i} ({e.get('parent_hf')}): accepted but missing {missing}")
            accepted.append({k: e[k] for k in EDGE_KEYS if e.get(k)})

    del rec["_candidate"]
    rec["record_history"].append({"date": time.strftime("%Y-%m-%d", time.gmtime()),
                                  "change": f"reviewed and promoted from staging ({len(accepted)} edge(s) accepted)",
                                  "by": reviewer})
    edges_before = EDGES.read_text()
    dest.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
    with open(EDGES, "a") as f:
        for e in accepted:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

    result = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate.py")], capture_output=True, text=True)
    if result.returncode != 0:
        dest.unlink()
        EDGES.write_text(edges_before)
        print(result.stdout)
        fail("validation failed; nothing was changed")
    src.unlink()
    print(f"promoted {rec['id']} with {len(accepted)} edge(s); validation OK")


if __name__ == "__main__":
    main()
