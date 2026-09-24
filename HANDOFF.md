# Stemma Machinarum — Claude Code Handoff

Handoff date: 2026-09-24
Owner: Wilson Pruitt
Working name: **Stemma Machinarum** (short form "Stemma")
Home: https://stemma.network (live 2026-09-24; Cloudflare DNS to Vercel) · GitHub org `stemma-machinarum` (claim if not yet done)

---

## 1. What this project is

A genealogy of machine-learning models, starting with open-weight language models. It records which model descends from which, what changed at each step, and the evidence for every claim. The name comes from textual criticism: a *stemma* is the family tree of manuscript copies, and stemmatics already has a term, **contamination**, for a copy drawing on two lines at once. Distillation and model merging are contamination in exactly that sense, so the structure is a network, not a strict tree.

Two audiences, equally important:

1. **People**: developers, policymakers, advocates, and historians who need a factual account of where AI systems came from instead of hype or doom narratives.
2. **LLM agents**: models that need a trustworthy, machine-readable, dated record of model lineage, with fact and inference clearly separated.

There are two workstreams in this repo:

- **Track A, the narrative:** Wilson's own learning, written as a field notebook that becomes the project's history.
- **Track B, the build:** the Stemma data, schema, and tooling.

The tracks feed each other. Each primary source read in Track A should add or verify records in Track B.

## 2. About the owner (so you calibrate)

- Ph.D. in Curriculum and Instruction. Journal editor. Independent scholar who does open-access translation (Latin and other languages). Runs a small software company, so he's comfortable with repos and tooling but is **not** an ML specialist.
- Strongly prefers **primary sources** over secondary summaries, and sharp distinctions over hedged blends.
- Wants honest, direct engagement. Correct his misconceptions plainly.
- In Track A, explain at an informed-non-specialist level. **Wilson writes the narrative; you explain, check, and cite.** Don't ghostwrite his conclusions.

## 3. Non-negotiable principles

1. **Every claim carries an evidence tag.** For lineage edges:
   - `declared`: stated by the developer in a paper, model card, or official release.
   - `declared_by_uploader`: stated in Hugging Face metadata by whoever uploaded the model, who may not be the original developer.
   - `inferred_weights`: inferred from weight or architecture comparison.
   - `inferred_behavior`: inferred from outputs (for example, a model misidentifying itself as another company's assistant).
   - `alleged`: publicly claimed by a third party and disputed or unverified.
2. **Every edge and every non-trivial field has a source URL.** No source means no edge.
3. **Unknown is a value, not a blank.** Use `"unknown"` or `null` with `"status": "not_recorded"`. Never fill a gap with a plausible guess.
4. **Primary sources first.** These are papers, official model cards, release posts, and config files. Secondary coverage can point to a primary source but can't stand in for one.
5. **Neutrality.** Contested claims about companies get the claim, the response if any, and sources for both. No editorializing in data records.
6. **No secrets in the repo.** API tokens (Hugging Face, etc.) live in environment variables only. Add `.env` to `.gitignore` on day one.
7. **Publish early.** The schema and method get a public, timestamped release (a Zenodo DOI) as soon as v0.1 is stable. Public priority is part of the protection strategy.

## 4. Proposed repo layout

```
stemma/
├── README.md
├── HANDOFF.md                  # this file
├── LICENSE                     # code license (decision pending, see section 9)
├── DATA_LICENSE                # data license (decision pending)
├── llms.txt                    # agent-facing description + entry points
├── schema/
│   ├── model.schema.json
│   ├── edge.schema.json
│   ├── dataset.schema.json
│   └── technique.schema.json
├── data/
│   ├── models/<model-id>.json      # one specimen per file
│   ├── datasets/<dataset-id>.json  # training corpora (added 2026-09-24)
│   ├── edges/edges.jsonl           # one lineage edge per line
│   └── techniques/<technique-id>.json
├── scripts/
│   ├── ingest_hf.py            # pulls candidate records from Hugging Face
│   ├── promote.py              # moves a reviewed candidate from staging into data/
│   ├── pilot_candidates.txt    # Phase 2 repo list
│   ├── validate.py             # schema + evidence-rule checks
│   └── export_graph.py         # graph export (JSON, GraphML)
├── site/                       # Astro static site (stemma.network); see docs/site-plan.md
├── narrative/
│   ├── reading-order.md
│   ├── notebook/                # one entry per source read
│   ├── exercises/               # hands-on exercises (section 5)
│   └── glossary.md
└── docs/
    ├── method.md               # evidence tags, sourcing rules, corrections policy
    ├── disputes.md             # policy for contested edges
    └── review.md               # procedure for reviewing staged candidates
```

## 5. Track A: the narrative (Wilson's learning)

### Goal
Build real understanding through primary sources, and produce a notebook that later becomes the project's written history. The focus is the artifacts: which ideas and models came from which.

### Reading order (type specimens)
Verify each citation and link before adding it to `narrative/reading-order.md`.

1. Rosenblatt (1958), the perceptron paper.
2. Minsky and Papert, *Perceptrons* (1969), introduction only.
3. Rumelhart, Hinton and Williams (1986), backpropagation.
4. Vaswani et al. (2017), "Attention Is All You Need."
5. Radford et al. (2019), the GPT-2 paper and model card.
6. Touvron et al. (2023), the LLaMA paper, notable for disclosing its training data.

Historiography, read alongside:
- George Basalla, *The Evolution of Technology* (1988).
- Mikel Olazaran's work on the perceptron controversy (1990s).
- Franz Reuleaux, *Kinematics of Machinery* (1875; English 1876), for classification method.

### Notebook entry template (`narrative/notebook/NN-short-name.md`)

```
---
station: 5                    # order on the path; historiography uses "alongside"
kind: source                  # source | alongside | exercise
title: "Author (Year), Title"
short: "Short name"
sources:
  - label: Paper
    url: https://...
records: [gpt2-xl, webtext]   # Stemma ids this station added or verified
read_on: YYYY-MM-DD           # omit until read; status derives from it
---

# Author (Year), Title

## What it introduced
(techniques, in plain words; link to data/techniques/ records)

## What it descended from
(prior work it explicitly builds on, per its own citations)

## My notes
### YYYY-MM-DD
(Wilson writes this section. Dated entries, appended, never rewritten in
place; a correction goes in a new entry that says what changed.)

## Questions I still have

## Records added or verified in Stemma
```

### Hands-on exercises
1. **Read a specimen.** Open GPT-2's and a LLaMA-family model's `config.json` on Hugging Face. Build a side-by-side table of their architectural "characters" (layers, hidden size, attention heads, vocabulary size, positional encoding, normalization, activation). Explain each row in one plain sentence.
2. **Watch one build-through.** Andrej Karpathy's "Let's build GPT" video. Afterward, help Wilson map what he saw onto the config fields from exercise 1.
3. **Glossary.** Maintain `narrative/glossary.md`. Add terms only when Wilson meets them in a source, and cite where.

### Your role in Track A
- Explain concepts when asked, grounded in the specific source being read.
- Check Wilson's notes for factual errors and say so directly.
- Don't write the "My notes" sections.

## 6. Track B: the build

### Pilot scope
Open-weight, decoder-style language models, roughly 2018–2023 (the GPT-2 through Llama 2 era). Target is 50–100 specimens. This era is well documented and has simpler lineages, so the structure can be tested before it has to handle modern complexity.

Seed candidates (verify each against primary sources; don't assume dates or details):
GPT-2 (all sizes) · GPT-Neo · GPT-J · GPT-NeoX-20B · Pythia suite · OPT · BLOOM · LLaMA 1 · Alpaca · Vicuna · Falcon · MPT · Llama 2 · Mistral 7B · Zephyr · Mixtral · Code Llama

Useful early test cases: Alpaca and Vicuna. Their developers publicly described both a base-model parent (LLaMA) and training data generated from another company's model's outputs. So the record should show two parents, one of them through distillation, both `declared`. That's contamination in the stemmatic sense, documented by the developers themselves.

### Draft schemas (starting points; refine in session)

**Model record** (`data/models/<id>.json`):
```json
{
  "id": "gpt2-xl",
  "name": "GPT-2 XL",
  "developer": "OpenAI",
  "release_date": {"value": "YYYY-MM", "source": "https://...", "status": "recorded"},
  "weights_status": "open | api_only | closed",
  "license": {"value": "...", "source": "https://..."},
  "architecture": {
    "family": "decoder_only",
    "n_layers": {"value": 48, "source": "https://.../config.json"},
    "hidden_size": {"value": 1600, "source": "..."},
    "n_heads": {"value": 25, "source": "..."},
    "vocab_size": {"value": 50257, "source": "..."},
    "positional_encoding": {"value": "learned_absolute", "source": "..."}
  },
  "training_data": {"value": "...", "source": "...", "status": "recorded | partial | not_recorded"},
  "techniques": ["transformer-decoder", "..."],
  "primary_sources": ["https://..."],
  "record_history": [{"date": "YYYY-MM-DD", "change": "created", "by": "..."}]
}
```
(Values shown are placeholders for shape only. Pull real values from the actual config and paper.)

**Edge record** (one line in `data/edges/edges.jsonl`):
```json
{"child": "alpaca-7b", "parent": "llama-7b", "relation": "fine_tuned_from", "evidence": "declared", "source": "https://...", "note": ""}
```
Relation types: `fine_tuned_from` · `distilled_from_outputs` · `merged_from` · `quantized_from` · `adapter_on` · `same_architecture_retrained` · `successor_in_series`

**Technique record** (`data/techniques/<id>.json`): id, name, first appearance (with source), plain-language description, and the models that use it (with sources).

Keep **classification** (grouping by structural characters, Reuleaux-style) separate from **lineage** (descent). Don't derive one from the other; comparing them is part of the point.

### Hugging Face ingest notes
- Model cards may carry `base_model` and `base_model_relation` in their YAML metadata. Treat these as `declared_by_uploader`, not `declared`, unless the uploader is the original developer.
- Pull `config.json` for architecture characters. Record the file URL and the commit hash or date so the value can be traced even after the file changes.
- Ingest output is **candidate** data. Write it to a staging area; nothing reaches `data/` without review.
- Respect rate limits. Hugging Face tokens go in environment variables only.

### Phases
0. **Repo setup.** Layout, `.gitignore`, draft schemas, `validate.py` that enforces "no edge without source" and "no blank where unknown belongs."
1. **Hand-curated seed.** 15–20 records built directly from papers and model cards, with Wilson reviewing each. This sets the quality bar.
2. **Ingest.** `ingest_hf.py` generates candidates for the remaining pilot models, staged for review.
2b. **Site.** `stemma.network` hosts both doors: the Graph (records, raw JSON, `llms.txt`) and the Notebook (Track A's path, with Wilson's dated notes), cross-linked. **`docs/site-plan.md` is the score** (three rulings by Wilson, five by Fable, 2026-09-24). Phases 3 and 4 land on this site.
   **Done 2026-09-24:** live at https://stemma.network (Vercel project `stemma`, root `site/`, git-connected: a push to `main` is a production deploy). Beyond the plan: an About page (genealogy vs. taxonomy, the two audiences), a `/records/` index, and a Phase 3 pilot at `/graph/`: the LLaMA family drawn as a manuscript stemma (time down the page, closed models hollow, contamination dashed), with a separate phone layout. Renderer: `site/src/lib/stemma-svg.ts`; its columns are hand-set for that one family (`LANES`), so new records appear on record pages automatically but not in the drawing.
3. **Graph and export.** `export_graph.py` produces a JSON graph and GraphML, plus one simple visualization of the pilot network, with edges styled by evidence tag.
4. **Publish v0.1.** README, `docs/method.md`, `llms.txt`, a tagged GitHub release, and a Zenodo DOI for schema and method.

### Agent-facing requirements (design for these from the start)
- Stable IDs that never get reused.
- Every record is valid JSON with a published schema.
- Versioned, dated snapshots, so an agent can tell what was known when.
- `llms.txt` at the root describing the project, the evidence tags, and where the data lives.
- Later: a small query API or MCP server supporting queries like "ancestors of X, declared edges only."

## 7. First session: concrete tasks

1. Create the repo structure in section 4. Add `.gitignore` covering `.env`.
2. Write `schema/*.schema.json` from the drafts above, and `scripts/validate.py`.
3. Write `docs/method.md`: evidence tags, sourcing rules, and the unknown-is-a-value rule, in plain language.
4. Build **three** hand-curated model records (GPT-2 XL, LLaMA 7B, Alpaca 7B) and their edges from primary sources, and walk Wilson through each source used.
5. Start `narrative/reading-order.md` with verified citations and links.
6. Summarize what was done and list open questions for Wilson.

## 8. Things to watch out for

- **Invented specifics.** Don't cite a paper, date, parameter count, or lineage claim you haven't verified from a fetched source in this session. If you can't verify something, mark it unknown.
- **Uploader versus developer.** Hugging Face has many re-uploads and quantizations of the same model. Don't treat a re-upload as a new specimen unless it changes the weights, and record it with the right relation.
- **Contested claims.** Allegations that one company's model derives from another's are legally and reputationally sensitive. `alleged` edges need public sources for both the claim and any response.
- **Scope creep.** Stay in the pilot era until v0.1 ships.

## 9. Open decisions for Wilson

- [ ] Code license (MIT or Apache 2.0) and data license (CC BY 4.0 is the usual choice for open data).
- [x] Whether narrative notebook entries are public in the repo or kept private until later. **Public** (Wilson, 2026-09-24; `docs/site-plan.md` ruling 1).
- [ ] Register `stemma.foundation` defensively now, or later?
- [x] Which static site setup for `stemma.network`. **Decided, brought forward from "after v0.1": Astro, static, `site/` in this repo, git-connected to Vercel** (`docs/site-plan.md`). Domain is registered at Cloudflare; wire it with DNS-only records.
