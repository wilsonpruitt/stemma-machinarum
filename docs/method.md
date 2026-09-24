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

## Relations

An edge's `relation` says *how* the parent reached the child. Two families:

**Weights descend.** The child starts from the parent's parameters.
- `fine_tuned_from`: further training on the parent's weights, including
  continued pretraining (Code Llama from Llama 2).
- `merged_from`, `quantized_from`, `adapter_on`: weights combined,
  compressed, or extended without retraining the whole model.

**Influence without weights.** The child never touches the parent's
parameters; the parent shaped its *training signal*. This is where closed
models enter an open model's stemma, and where contamination is hardest to see.
- `distilled_from_outputs`: the child trained on text the parent
  *wrote* (Alpaca on text-davinci-003, Vicuna on ChatGPT).
- `feedback_from`: the child learned from the parent's *judgments*
  (rankings, scores, critiques of other text) rather than from its text
  (Zephyr's DPO step on GPT-4's rankings). Copying a teacher and being
  graded by one are different inheritances, so they get separate labels.

**Series relations.** No weights or training signal pass.
- `successor_in_series`: the developer presents the child as the next
  version, trained from scratch (Llama 2 after Llama 1).
- `same_architecture_retrained`: same design, new training run, not
  presented as a successor.

**`via`.** Influence-without-weights usually arrives second-hand, through
a dataset that someone *else* built from a closed model's outputs (ShareGPT,
UltraChat, UltraFeedback). An edge records that channel in `via`, with who
built it. The edge still points at the model; `via` keeps the path readable
when the same dataset feeds many children. Datasets may become nodes of
their own later. Until then, spell the dataset name identically across
edges so the path can be traced.

Closed parents are often unversioned: "ChatGPT" named a product whose
underlying model changed over time. Such a parent is a stub record whose
version is `not_recorded`, not a guess at the snapshot.

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
