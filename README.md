# Stemma Machinarum

A genealogy of machine-learning models, starting with open-weight
language models. It records which model descends from which, what
changed at each step, and the evidence for every claim.

The name comes from textual criticism: a *stemma* is the family tree of
manuscript copies, and stemmatics already has a term — **contamination**
— for a copy that draws on two lines at once. Distillation and model
merging are contamination in exactly that sense, so the structure here
is a network, not a strict tree.

Two audiences:

1. **People** — developers, policymakers, advocates, historians — who
   need a factual account of where AI systems came from.
2. **LLM agents** — models that need a trustworthy, machine-readable,
   dated record of lineage, with fact and inference clearly separated.
   Start at [`llms.txt`](llms.txt).

## Structure

- `schema/` — JSON Schema for model, edge, and technique records.
- `data/models/` — one specimen per file.
- `data/datasets/` — training corpora, one per file; models link to them with `trained_on`.
- `data/edges/edges.jsonl` — one lineage edge per line, each with an
  evidence tag and a source.
- `data/techniques/` — technique records (transformer-decoder, RLHF,
  etc.), kept deliberately separate from lineage.
- `scripts/` — `validate.py` (schema + sourcing rules), `ingest_hf.py`
  (Hugging Face candidate ingest, staging only), `promote.py` (moves a
  reviewed candidate into `data/`; see `docs/review.md`), `export_graph.py`
  (graph export).
- `narrative/` — a field notebook of primary sources read while
  building this, which becomes the project's own history over time.
- `docs/method.md` — evidence tags, sourcing rules, the
  unknown-is-a-value rule. Read this first.
- `docs/disputes.md` — how contested/alleged lineage claims are handled.

## Principles

1. Every claim carries an evidence tag.
2. Every edge and every non-trivial field has a source URL. No source,
   no edge.
3. Unknown is a value (`"status": "not_recorded"`), never a blank.
4. Primary sources first — papers, official model cards, release posts,
   config files. Secondary coverage can point to a primary source but
   can't stand in for one.
5. Neutrality on contested claims — the claim, the response if any, and
   sources for both.

See `docs/method.md` for the full account.

## Current scope

Open-weight, decoder-only language models, roughly 2018–2023 (GPT-2
through the Llama 2 / Mistral era). Target: 50–100 specimens for the
pilot.

## Validating data

```
python3 -m venv .venv && .venv/bin/pip install jsonschema
.venv/bin/python scripts/validate.py
```

## License

Code: MIT (`LICENSE`). Data and schema: CC BY 4.0 (`DATA_LICENSE`).
