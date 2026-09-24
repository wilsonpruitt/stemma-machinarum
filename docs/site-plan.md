# Phase 2b: stemma.network

Written 2026-09-24 (Fable). Executes in a later session (Sonnet). Three
decisions were made by Wilson before this was written; everything below
follows from them. If one of them changes, reread the whole file.

## What this is

The handoff's founding claim is that the two tracks feed each other:
each primary source read in Track A adds or verifies records in Track
B. Today that relationship is invisible. The notebook is markdown in
`narrative/`, the records are JSON in `data/`, and nothing connects them
except a filename in a note.

The site makes the relationship visible, in both directions. A station
on the path (the LLaMA paper) links to the record it produced
(`llama-7b`); the record links back to the station that read it. That
cross-link is the product. It's also what makes the path *part of
Stemma* rather than a blog standing next to it.

The site is also where Wilson keeps his notes as he reads, so the path,
the sources, the notes, and the records live in one place instead of
across a reading list, a video queue, and a folder of markdown. And
because everything on it is public and cited, anyone can take the same
route.

## The three rulings (Wilson, 2026-09-24)

1. **Public path, no accounts.** The path is published and complete:
   every source linked, every exercise spelled out, Wilson's notes shown
   as his (first person, dated). Others follow the same route and keep
   notes wherever they like; contributed notebook entries by pull
   request are a later possibility. No accounts, no per-reader state.
   This also settles HANDOFF §9: notebook entries are public.
2. **One site, two doors.** The Graph (records, edges, raw JSON,
   `llms.txt`) and the Notebook (the path), built from one repo. Phase
   3's graph view and Phase 4's v0.1 release land on this same site.
3. **Git-connected deploy: push = publish.** A push to `main` rebuilds
   the site. Wilson's existing push gate is the deploy gate. Consequence
   to hold in mind: a committed half-written note goes live on push.

## Rulings made here (Fable)

4. **Static, Astro 5, in `site/` of this repo.** Reads `../data`,
   `../narrative`, `../docs` directly at build time through Astro's
   content layer (`glob` loader with a `base` outside `src/`); nothing
   is copied into `src/content`. One source of truth. Astro because the
   content is markdown and JSON, the runtime should be near zero, the
   machine is an 8 GB Mac with a 1 GB Node heap, and Wilson already
   maintains an Astro repo (the order sites). Not Next.js (heavier, and
   nothing here is dynamic). Not hand-rolled HTML from Python (would
   reinvent markdown rendering and layouts that Astro gives for free).
5. **Notes are dated entries, appended, never rewritten in place.**
   `## My notes` holds `### YYYY-MM-DD` subheads. The notebook is a
   dated record like everything else in Stemma; the site shows the
   iteration, not a final rewrite. Corrections go in a new dated entry
   that says what changed.
6. **Status is derived, not hand-set.** A station is `not started` if
   the file has no `read_on`, `read` once it does; its notes count is
   the number of dated entries. Nothing to keep in sync by hand.
7. **Record pages render the JSON faithfully and add nothing.** Every
   field with its value, status, and source link; edges in and out; the
   `availability` line with its check date; the "read in" backlinks.
   No prose summaries, no editorializing. The graph *view* is Phase 3.
8. **Raw data is served at stable URLs, and `llms.txt` is at the root.**
   The site is the "planned home" the handoff promised agents.
   `robots.txt` allows everything: being read is the point. Before
   finalizing robots/rights wording, read the open-corpus plan
   (`~/open-corpus/PLAN.md`), which governs all of Wilson's text sites.
   The data license (CC BY 4.0, `DATA_LICENSE`) already permits this.

## What the site is not (scope guard)

No search (v1). No graph visualization (Phase 3). No accounts,
comments, in-browser editing, per-reader progress, or analytics. No
brand work: this is a scholarly site, not a Wroot Labs product. Design
is the executing session's call within: citation-forward, evidence tags
visually distinct from one another, light and dark, no hype.

## Pages

```
/                     landing: what Stemma is (from README), two doors,
                      live counts (models · datasets · edges), date of
                      the last data change
/notebook/            the path: numbered stations in reading order, then
                      "read alongside" (historiography), then exercises;
                      each with derived status and notes count
/notebook/<slug>/     one station or exercise (see "Station page")
/glossary/            terms, each linked to the station where it was met
/models/<id>/         record page (ruling 7)
/datasets/<id>/       record page
/method/  /review/  /disputes/     docs rendered
/data/**              raw JSON and edges.jsonl, verbatim, stable URLs
/llms.txt  /robots.txt
```

### Station page

In this order: title and citation · the primary source links (the
thing to read or watch) · what it introduced · what it descended from ·
**My notes** (dated entries; if none yet, say "no notes yet" rather than
hiding the section: an empty notebook is honest) · questions still open
· records added or verified in Stemma (each linked to its record page).

### Record page

Name, developer, `availability` with check date, then every sourced
field as `value · status · source`. Edges grouped the way
`docs/method.md#relations` groups them: weights descend · training data
· influence without weights · design. Parents above, children below.
Then "Read in": any station whose `records` lists this id.

## Repo changes the site needs (do these first, before any Astro)

These are changes to `narrative/`, independent of the site, and they
make the notebook consistent whether or not a site ever renders it.

1. **One notebook file per station**, from `reading-order.md`:
   `narrative/notebook/01-rosenblatt-1958.md` … `06-touvron-2023.md`,
   and `h1-basalla-1988.md`, `h2-olazaran-1996.md`,
   `h3-reuleaux-1875.md` for the historiography. Each starts from
   `_template.md` with the citation and links moved in from
   `reading-order.md`. `reading-order.md` stays as the human-readable
   index (the site builds its own from frontmatter).
2. **Frontmatter on every notebook and exercise file:**
   ```yaml
   ---
   station: 5                    # order on the path; h1–h3 use "alongside"
   kind: source                  # source | alongside | exercise
   title: "Radford et al. (2019), Language Models are Unsupervised Multitask Learners"
   short: "GPT-2"
   sources:
     - label: Paper
       url: https://cdn.openai.com/better-language-models/…
     - label: Model card
       url: https://huggingface.co/openai-community/gpt2-xl
   records: [gpt2-xl, webtext]   # Stemma ids this station added or verified
   read_on: 2026-10-02           # omit until read; status derives from it
   ---
   ```
   Exercise 1 already exists; give it frontmatter (`kind: exercise`,
   `records: [gpt2-xl, mistral-7b-v0-1]`, `read_on: 2026-09-24`).
3. **Glossary entries carry where they were met**, as the existing
   comment already specifies: `Met in:` a link to the station file. The
   build turns that into a backlink. Nothing else changes.
4. **`llms.txt` gains two lines** near the top: the live address, and
   that `data/` is mirrored at `https://stemma.network/data/`.
5. **HANDOFF §5's notebook template** gets the frontmatter block above
   and the dated-entries rule under "My notes."

## Build

- `site/` at the repo root. Astro 5, `output: 'static'`. Content
  collections: `notebook` (glob over `../narrative/notebook/*.md` and
  `../narrative/exercises/*.md`), `models` and `datasets` (glob over
  `../data/*/*.json`), `docs` (glob over `../docs/*.md`). Edges: read
  `../data/edges/edges.jsonl` in a small loader and index by child and
  by parent. `glossary.md` is parsed once at build.
- Backlinks: from every notebook entry's `records`, build a map
  record-id → stations. Record pages read it.
- Counts on the landing page come from the collections at build time,
  not from a hand-maintained number.
- `/data/**`: copy `../data` into the build output as-is. Astro's
  `publicDir` can't point outside `site/`, so do it in an integration
  hook or a one-line prebuild copy; either way it is generated, never
  committed.
- Local check before the first deploy: `astro build` completes on this
  machine (1 GB heap is plenty for this size), every station renders,
  every `records` id resolves to a real record (fail the build if one
  doesn't; a dangling id is a broken cross-link, which is the one thing
  this site exists to prevent), `validate.py` still passes.

## Deploy

- Vercel project `stemma`, team wilson-pruitts-projects, root directory
  `site/`, framework Astro (auto-detected), git-connected to
  `wilsonpruitt/stemma-machinarum` on `main`. Commits must carry the
  team's required author email (see the account note in the global
  CLAUDE.md); that's already how this repo commits.
- Domain: `stemma.network` is registered at Cloudflare. Wire it with
  DNS-only records per Wilson's domains note; never `vercel domains
  buy`.
- ⛔ Two hard stops for the executing session, each needing Wilson's
  per-action OK: the first production deploy, and the domain wiring.
  After that, per ruling 3, every push to `main` is a deploy.
- Because the site is git-connected, the GitHub org transfer in HANDOFF
  §9 (`stemma-machinarum`) will need the Vercel connection re-pointed.
  Do the transfer first if it's imminent; otherwise note it.

## After it's live: the reading workflow

1. Read a station's source (the links are on its page).
2. Open its notebook file (in a Claude session, an editor, or Ulysses
   → paste). Add a `### YYYY-MM-DD` entry under **My notes**. Set
   `read_on` if this is the first pass. Add terms to the glossary only
   as they're met, with the station link.
3. If the reading touched Stemma records (it should), add or verify
   them per `docs/review.md`, and list the ids in `records`.
4. Commit. Push (= publish).

Exercises 2 and 3 from HANDOFF §5 follow the same loop.

## Sequencing for the executing session

1. Repo changes above (notebook files, frontmatter, llms.txt,
   template). Commit.
2. Astro scaffold, collections, layouts. Record pages and edges first
   (they're the largest and most mechanical), then notebook, glossary,
   landing, docs.
3. Data mirror, `llms.txt`, `robots.txt`.
4. Local build check. Commit.
5. ⛔ Vercel project and first deploy. ⛔ Domain.
6. Update HANDOFF §4's layout tree to include `site/`, and mark §9's
   site-setup decision done.

Estimate: one Sonnet session, roughly 150–300K tokens. The panel
protocol in `docs/review.md` doesn't apply here; nothing in this build
is a taxonomy judgment.

## Later, not now

- Phase 3's graph view lives on this site (`/graph/`), edges styled by
  evidence tag.
- The path is itself a stemma: each station's "what it descended from"
  is an edge. Rendering the reading order as a small lineage graph, in
  the same visual language as the data graph, is the conceptual hook
  that makes the two doors one building. A Phase 3 candidate.
- Contributed notebook entries (another reader's dated notes on the
  same station) by pull request, rendered alongside Wilson's and
  labeled by author. Ruling 1 leaves the door open; nothing in v1
  should make it harder.
- Search, once there's enough to search.
