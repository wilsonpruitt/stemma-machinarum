# Disputed claims

Some lineage claims are legally or reputationally sensitive — for
example, a public allegation that one company's model was trained on
another company's outputs without permission.

## Policy

- These are tagged `alleged` in the edge record, never `declared` or
  `inferred_*`, regardless of how credible the claim seems.
- An `alleged` edge needs a public source for the claim itself.
- If the accused party has responded publicly (denial, clarification,
  silence noted as such), that response gets its own source, either on
  the same edge record (a `note` field pointing to it) or as a
  companion entry. The record shows both sides; it doesn't adjudicate
  between them.
- No editorializing language in the `note` field — state what was
  claimed, by whom, and what the response (if any) was.
