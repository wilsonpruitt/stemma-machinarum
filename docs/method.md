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

An edge's `relation` says *how* the parent reached the child. The graph
holds two kinds of record, models and datasets, in one id namespace.

**Weights descend.** The child starts from the parent's parameters.
- `fine_tuned_from`: further training on the parent's weights, including
  continued pretraining (Code Llama from Llama 2).
- `merged_from`, `quantized_from`, `adapter_on`: weights combined,
  compressed, or extended without retraining the whole model.

**Training data.** The child learned from a corpus.
- `trained_on`: model → dataset. Pretraining corpora (GPT-J on the Pile)
  and fine-tuning sets (Zephyr on UltraChat) alike. Several models on one
  dataset share a source text, which is not a parent–child relation
  between the models themselves.

**Influence without weights.** A model shaped a *training signal* without
passing on its parameters. This is where closed models enter an open
model's stemma. The child here is usually a dataset: the closed model
wrote or graded the data, and open models are then `trained_on` that
dataset. Read the path in two steps: Zephyr → UltraChat → ChatGPT.
- `distilled_from_outputs`: the child holds, or trained on, text the
  parent *wrote* (Alpaca's 52K set from text-davinci-003; UltraChat from
  ChatGPT).
- `feedback_from`: the child holds, or trained on, the parent's
  *judgments*: rankings, scores or critiques of other text (UltraFeedback
  from GPT-4). Copying a teacher and being graded by one are different
  inheritances, so they get separate labels.

A dataset with no model parents is taken to be human-written or scraped
text; the absence means only that no generating model is recorded.

**Design.** No weights or training signal pass; the developer declares
that one model's design is based on another's.
- `successor_in_series`: the developer presents the child as the next
  version, trained from scratch (Llama 2 after Llama 1).
- `same_architecture_retrained`: the developer says the architecture is
  the *same* or *almost identical*, allowing listed minor exceptions
  (GPT-NeoX-20B and GPT-J; GPT-3 and GPT-2; GPT-Neo's "replication of
  the GPT-3 architecture").
- `design_follows`: the developer says the design *largely follows*, is
  *adapted from*, or is *modeled on* the parent (OPT, Pythia, Falcon and
  GPT-NeoX-20B on GPT-3). The wording decides between this and
  `same_architecture_retrained`; both need the developer's own words.
  Shared techniques alone, with no such statement, are classification,
  not lineage (Mistral uses the LLaMA recipe but its paper only says
  "Compared to Llama", without saying which Llama, so no edge is recorded).

`scripts/validate.py` enforces the kinds: `trained_on` runs model →
dataset; `distilled_from_outputs` and `feedback_from` need a model
parent; every other relation joins two models.

Closed parents are often unversioned: "ChatGPT" named a product whose
underlying model changed over time. Such a parent is a stub record whose
version is `not_recorded`, not a guess at the snapshot.

## Availability

Every model and dataset carries `availability`: whether the artifact
itself (weights or dataset files) could be obtained, **as checked on a
stated date**, with the URL checked:

`available` · `partial` (only a portion released) · `gated` (released
behind an approval step) · `removed` (unreachable at its original
address) · `never_released` · `unknown` (could not be determined; the
note says why).

It describes the artifact, not API access. `removed` records what was
found at the original address, not why; a takedown is recorded only
with a source for it. Availability changes over time, so re-checking
adds a `record_history` entry, not a silent overwrite.

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
