# Reviewing staged candidates

`scripts/ingest_hf.py` turns Hugging Face repos into candidate records in
`data/staging/models/` (gitignored), with a queue in
`data/staging/REVIEW.md`. Nothing reaches `data/` until
`scripts/promote.py` moves it, and promote refuses a candidate until a
person has marked it reviewed. This file is the procedure between those
two steps.

There are two roles:

- **Preparer** (a person or an agent session) researches each candidate
  and edits the staged JSON. The preparer writes what they found in
  `_candidate.review_notes` and never sets `reviewed`.
- **Reviewer** (Wilson, or someone he names) reads the prepared record
  and notes, sets `_candidate.reviewed: true`, and runs
  `python3 scripts/promote.py <id> --by "<name>"`.

All the rules in `method.md` apply: verify every value from a source
fetched in the same session, quote the source's words in `note`s where
wording matters, and record unknowns as `not_recorded`, never as guesses.

## What ingest filled, and what it didn't

| Field | From ingest | What the preparer does |
|---|---|---|
| Layers, hidden size, heads, vocab, context | `config.json` pinned to the repo commit, `recorded` | Keep. If the paper states a different context length, record the paper's value and put the config value in a note (see `narrative/exercises/01-…`). |
| Positional encoding, normalization, activation | `not_recorded`; a flag names config hints | Fill only from the paper or the developer's code. A config field name is not evidence. |
| Architecture family | From config `architectures` | Confirm. |
| Developer | The HF uploader org's handle | Replace with the developer's proper name. If the uploader is *not* the developer (a re-upload, a conversion, a quantizer), say so in `review_notes`. |
| Release date | HF repo creation date, `partial` | Replace with the developer's release post or paper date where one exists; keep `partial` if only the repo date is known. |
| License | Card metadata, `partial` | Confirm against the license text; then `recorded` with that URL. |
| Training data | `not_recorded` | Fill from the card text or paper. |
| Availability | Checked at ingest, dated | Keep; re-check if the candidate has sat in staging for weeks. |
| Lineage edges | Only card metadata (`base_model`, `datasets`) | **The main job. See below.** |

## Lineage: the main job

The Phase 2 pilot run found `base_model` metadata on only 5 of 48
candidates. Lineage mostly lives in the card's prose and in papers, so
read them.

For every edge in `_candidate.edges`:

1. Set `accept` to `true` or `false`. A rejected edge gets a `note` saying why.
2. Set `relation` (`method.md#relations`). The ingest's relation for a
   `base_model` edge is usually the Hub's inference, not the uploader's
   words; confirm it.
3. Set `evidence`:
   - `declared` when the developer states it in their own paper, post, or
     card (the uploader org *is* the developer). Cite that source.
   - `declared_by_uploader` when it rests only on card metadata written
     by someone who isn't the developer.
4. `parent` must be a Stemma id. If the parent isn't in Stemma yet
   (`UNRESOLVED` in the queue), either stage and prepare the parent first,
   or reject the edge with a note.

To add an edge the metadata missed, append to `_candidate.edges`:
`{"child", "parent", "relation", "evidence", "source", "note", "accept": true}`.

Common cases in this era:

- **Size siblings** (Pythia 70M…12B, OPT 125M…66B): same paper, no edges
  between siblings. Their shared training corpus is a `trained_on` edge each.
- **Developer fine-tunes** (Mistral-Instruct, Falcon-instruct, BLOOMZ, Code
  Llama variants): `fine_tuned_from`, usually `declared`.
- **Third-party fine-tunes** (OpenHermes, OpenOrca, WizardLM, Nous-Hermes):
  `fine_tuned_from` the base. Instruction data built from closed-model
  outputs needs a dataset record with its own `distilled_from_outputs`
  edge, sourced to the dataset's builder.
- **Quantizations** (TheBloke's GPTQ repos): `quantized_from`. The
  quantizer is the developer of the quantized record, not the original lab.
- **Reproductions** (OpenLLaMA): `design_follows` or
  `same_architecture_retrained` only with the developer's own wording;
  never `fine_tuned_from`.
- **Contested claims** (e.g. a lab's model said to derive from another's
  weights): `alleged` only, with sources for the claim *and* any response.
  Leave these for the reviewer; don't add them in a volume pass.

## IDs

Choose the id before promotion. After promotion it never changes.
Follow the existing family spelling (`code-llama-7b`, so
`code-llama-7b-python`, not `codellama-7b-python`). Rename by editing
`id`, the filename, and the `child` field of every candidate edge.

## Checklist per candidate

- [ ] Developer confirmed; uploader ≠ developer noted if so
- [ ] Id follows family spelling
- [ ] Release date from the developer, or kept `partial` with the repo date
- [ ] License confirmed
- [ ] Positional encoding / normalization / activation from paper or code, or left `not_recorded`
- [ ] Training data filled or `not_recorded`
- [ ] Every edge: `accept`, `relation`, `evidence`, resolved `parent`
- [ ] Lineage from the card text and paper added
- [ ] `review_notes` written (sources read, doubts, anything the reviewer should check)
- [ ] Reviewer: `reviewed: true`, then `promote.py <id> --by "<name>"`
