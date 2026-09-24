# Shared errors: a sketch (DRAFT, not adopted)

Status: sketch for Wilson to react to, 2026-09-24. Nothing here is in the
schema or `validate.py` yet. Citations marked *(verify)* are from memory and
must be checked against the source before they go anywhere public.

## The idea

Stemma's edges today rest almost entirely on what developers *say*
(`declared`, `declared_by_uploader`). The schema already has
`inferred_behavior` for lineage read off a model's outputs, but no edge
uses it, because there is no method for it yet.

Textual criticism has one. Lachmann's method, as Paul Maas formalised it
in *Textkritik* (1927; English 1958) *(verify)*, builds a stemma from
**shared errors**, not shared correct readings. Two copies that agree on
the right text prove nothing: the author wrote it and both copied it
faithfully. Two copies that agree on the *same mistake*, one a copyist
would not make independently, probably share an ancestor that made it.

Models have errors like that. A model that answers "I am ChatGPT, a model
trained by OpenAI" when it is neither has probably learned from ChatGPT's
text. The error is the evidence.

## Vocabulary: borrow the critics' terms

| Textual criticism | Stemma |
|---|---|
| *locus* (a place in the text where copies differ) | **probe**: one fixed prompt with fixed decoding |
| *reading* (what a given copy says at that locus) | **reading**: one model's verbatim output for one probe |
| *apparatus* (table of readings, per locus, per witness) | **apparatus**: all readings for one probe, side by side |
| *Bindefehler* (conjunctive error: binds copies together) *(verify term)* | an error two models share and are unlikely to reach independently |
| *Trennfehler* (separative error: shows B is not copied from A) *(verify term)* | an error A has that B lacks and could not easily "correct" |
| polygenesis (the same error arising independently) | two models reaching the same error through shared data, a shared tokenizer, or chance |
| contamination (a copy drawing on two lines) | already the project's term: distillation and merging |

Proposed name for the record type: **reading**, not "observation",
to keep the analogy load-bearing.

## Four rules (adapted from Maas)

1. **Only errors count.** A shared correct answer is no evidence of
   kinship. Every probe must say what the correct reading is, and why
   the target reading is an error.
2. **A shared error binds only if polygenesis is unlikely.** Each probe
   carries a polygenesis rating with a written reason. The danger in
   models is shared *data*: two unrelated models trained on the same
   web crawl, full of pasted ChatGPT transcripts, can both learn to
   say "As an AI language model". That's the model version of two
   scribes both "correcting" the same hard word the same way.
3. **Separative errors are weak here.** In manuscripts a copyist rarely
   repairs an error without another exemplar. Fine-tuning repairs
   errors routinely, the way a scribe emends by conjecture. So "B lacks
   A's error" says little about whether B descends from A. We would
   record separative readings but not build edges on them.
4. **A shared error shows a shared *source*, not which kind.** It
   cannot tell weight descent from data contamination. Maas said of
   contamination that no remedy has been found *(verify quote)*. Our
   version: a reading never chooses the relation by itself. It
   corroborates a declared edge, or supports a new edge only where
   the error class itself fixes the relation (see "Error classes").

## Error classes (first cut)

| Class | Example shape | What it can show | Polygenesis risk |
|---|---|---|---|
| Self-identification | claims to be another lab's assistant | trained on that model's outputs (`distilled_from_outputs`) | medium: web text is full of such transcripts |
| Inherited boilerplate | a distinctive refusal or disclaimer phrase | shared instruction data | high for common phrases, lower for rare ones |
| Tokenizer artifacts | "glitch tokens" that a tokenizer holds but training barely saw *(verify the GPT-2/3 case)* | shared **tokenizer**, which is classification, not lineage | low, but the evidence is structural |
| Idiosyncratic factual error | a specific wrong fact that is not common on the web | shared data or weights | depends on the fact |
| Format habits | a peculiar output template | shared SFT data | medium |

Tokenizer artifacts are a trap. A retrained model that reuses a tokenizer
(GPT-Neo reusing GPT-2's, say) shares its glitch tokens with no weights or
data passing. HANDOFF says to keep classification separate from lineage,
and this is exactly where the two blur. Tokenizer evidence belongs with the
architectural characters, not with edges.

## Record shapes (sketch)

**Probe** (`data/probes/<id>.json`): the locus.
```json
{
  "id": "self-id-001",
  "class": "self_identification",
  "prompt": "Who created you?",
  "paraphrases": ["What company trained you?", "Which model are you?"],
  "decoding": {"temperature": 0, "max_new_tokens": 64},
  "template": "the model's own chat template, as recorded per reading",
  "correct_reading": "names its actual developer, or says it doesn't know",
  "error_reading": "names a developer or product it is not",
  "polygenesis": {"value": "medium", "reason": "web-scale corpora contain ChatGPT transcripts"},
  "record_history": []
}
```

**Reading** (`data/readings/<probe-id>.jsonl`): one line per model and
prompt variant. It records a fact about what happened, with no inference.
```json
{"probe": "self-id-001", "variant": 0, "model": "alpaca-7b",
 "weights": {"repo": "...", "sha": "...", "quantization": "none"},
 "runtime": {"library": "transformers 4.x", "dtype": "bf16"},
 "run_on": "YYYY-MM-DD", "by": "...",
 "output": "verbatim text",
 "classified_as": "error | correct | other", "classified_by": "blind panel"}
```

**Edge use**: an `inferred_behavior` edge cites its probes. Proposal: add an
optional `readings` field (list of probe ids) to the edge schema, required
when evidence is `inferred_behavior`. A declared edge may also carry
`readings` as corroboration. That's the apparatus under the text.

## Protocol

1. **Calibrate on known lineage first.** Before inferring anything new,
   run probes on models whose lineage is already declared. Alpaca,
   Vicuna, Baize and GPT4All-J were trained on ChatGPT or
   text-davinci-003 text by their builders' own accounts. Llama 2 base,
   Pythia and GPT-J were not. If shared errors don't recover the known
   edges, the method fails before it can mislead. Stemmatics does the
   same with artificial traditions: scribes copying a text under
   controlled conditions so the true stemma is known *(verify: Spencer
   et al. 2004; Roos and Heikkilä 2009)*.
2. **Negative controls.** Include models from unrelated families to
   measure how often the error turns up with no known link. That base
   rate *is* the polygenesis rating. Without it, rule 2 is only a guess.
3. **Blind classification.** Whoever classifies a reading as error or
   correct does not know which model produced it, the same discipline
   as `docs/review.md`'s panel and the Arabic blind-control rule.
4. **Pin the specimen.** Weights by commit sha. A reading from a
   quantized copy is a reading from a *copy*, not the exemplar, so the
   quantization goes on the record.
5. **Several variants per probe.** One phrasing is one sample. The
   error has to hold across paraphrases before it counts as a reading
   of the model rather than of the prompt.
6. **Contested claims stay `alleged`.** A shared error suggesting one
   company's model derives from another's is the sensitive case
   (HANDOFF §8). Readings are facts about outputs on a date. Any claim
   about a company gets the `alleged` treatment in `docs/disputes.md`,
   and never in a volume pass.

## Practical limits on this machine

8 GB RAM runs models up to about 1–3B comfortably (Pythia, GPT-2,
TinyLlama, GPT-Neo). A 7B chat model runs only quantized and one at a
time, which by rule 4 makes the reading a copy's reading. The chat models
where self-identification errors live are mostly 7B+. Options: pilot on
the small models with a different error class, rent GPU time for one
calibration run (small cost, to estimate), or use hosted inference where
the exact weights can be pinned.

## A first pilot, if adopted

- One error class: self-identification.
- About 8 models: 4 with a declared ChatGPT/davinci data parent and 4
  controls.
- 3 probes × 3 paraphrases each.
- Readings classified blind.
- Deliverable: the apparatus table and one question answered: do the
  shared errors recover the declared edges, and at what false-positive
  rate?

That is Track A material as much as Track B: the notebook entry is
Wilson's to write.

## Questions for Wilson

1. Adopt "reading", "probe" and "apparatus" as the terms, or keep plain
   words on the site?
2. Is calibration-first (no new inferred edges until the method
   recovers known ones) the right gate?
3. Compute: small models locally, or budget a rented-GPU run for the
   7B chat models?
4. Should Maas and Bédier join the reading order as "alongside"
   stations?
