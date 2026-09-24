# Method

Stemma Machinarum records the lineage of machine-learning models the way a
textual critic records the lineage of manuscripts: every claim of descent
carries a tag for how well it's evidenced, and every non-trivial field
carries a source.

## Evidence tags

Used on every lineage edge:

- **`declared`** — stated by the model's own developer, in a paper, model
  card, or official release post.
- **`declared_by_uploader`** — stated in a Hugging Face (or similar)
  upload's metadata, by whoever uploaded the model. Only counts as
  `declared` if the uploader *is* the original developer; otherwise it's
  a weaker claim and stays tagged this way.
- **`inferred_weights`** — inferred by comparing weights or architecture,
  not stated by anyone.
- **`inferred_behavior`** — inferred from model outputs (for example, a
  model that misidentifies itself as another company's assistant).
- **`alleged`** — claimed publicly by a third party, and disputed or
  unverified. See `disputes.md` for how these are handled.

## Sourcing rules

- **No source, no edge.** Every edge in `data/edges/edges.jsonl` has a
  `source` URL. An edge without one doesn't go in.
- **Primary sources first.** A primary source is the paper itself, the
  official model card, the release announcement, or a config file in the
  model's own repository. A blog post or news article *about* the paper
  is secondary — it can point to a primary source, but it can't replace
  one as the citation on a record.
- Architecture fields (layer count, hidden size, etc.) are sourced to the
  specific `config.json` (or equivalent) used, ideally with a commit hash
  or access date, since these files can change upstream.

## Unknown is a value

Every sourced field in the schema takes the shape
`{"value": ..., "source": ..., "status": "recorded" | "partial" | "not_recorded"}`.

- If something isn't known, the field still exists: `"value": null`,
  `"status": "not_recorded"`.
- `"status": "recorded"` is only valid when `value` and `source` are both
  present — `scripts/validate.py` enforces this.
- An optional `"note"` carries a caveat that must travel with the value —
  e.g. the source says "32k" and the record stores `32000`, or the date
  is the paper's rather than the weights'. If a value needs more than a
  sentence of qualification, it probably belongs at `"partial"`.
- Never fill a gap with a plausible-sounding guess. A missing value is
  data (it tells an agent or reader "this hasn't been checked yet"); a
  guessed value is misinformation with the same shape as a fact.

## Classification vs. lineage

`data/techniques/` groups models by structural character (Reuleaux-style
classification — what a model *is*). `data/edges/` records what a model
*descended from*. These are kept deliberately separate and are not
derived from one another. Comparing the two — does structural similarity
track actual descent, or not — is part of the point of the project.

## Corrections

If a record turns out to be wrong, it's corrected in place and the
change is logged in that record's `record_history`. Nothing is silently
edited; the record shows what was believed, when, and why it changed.
