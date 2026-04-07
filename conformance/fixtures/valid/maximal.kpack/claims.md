<!-- KP:1 — Knowledge Pack Format
Claims: - [ID] assertion {confidence|type|evidence|date|depth|nature} context
  Positions 5-6 optional. Verbose named-field syntax also accepted.
Types: o=observed r=reported c=computed i=inferred
Depth: assumed | investigated | exhaustive (optional, position 5)
Nature: judgment | prediction | meta (optional, position 6; omitted=factual)
Relations: →supports ⊗contradicts ⊗!error ⊗~tension ←requires ~refines ⊘supersedes ↔see_also
Files: evidence.md=sources history.md=past entities.md=graph
-->
---
pack: maximal-fixture | v: 2026.04.04-rev2 | domain: test/conformance/deep
confidence: sherman_kent | normalized
---

# Maximal Fixture [test-pack|MAX,full-coverage]

> Every claim syntax feature exercised in one document.

## Dense — All Relation Types

- [C001] Claim demonstrating the supports relation
  {0.95|i|E001,E002|2026-04-01|exhaustive|judgment} Primary thesis.
  →C002

- [C002] Claim supported by C001
  {0.90|o|E001|2026-04-01|investigated} Confirmed independently.
  ←C001

- [C003] Claim in productive tension with C001
  {0.40|r|E003|2026-03-15|investigated|judgment} Minority view.
  ⊗~C001

- [C004] Claim that flatly contradicts C003
  {0.85|c|E004|2026-04-01|exhaustive} Computational reanalysis.
  ⊗!C003

- [C005] Claim that refines C002 with additional detail
  {0.88|i|E002,E004|2026-04-01|investigated} Narrower scope. ~C002

- [C006] Claim that supersedes an earlier version
  {0.92|i|E001|2026-04-01|exhaustive|judgment} Updated analysis. ⊘C001-v1

- [C001-v1] Original version of C001 now superseded
  {0.80|i|E001|2026-03-01|assumed|judgment} Initial assessment.

## Dense — Edge Cases

- [C010] Claim with empty depth slot and nature set
  {0.85|r|E003|2026-03-20||prediction} Position 5 empty, position 6 set.

- [C011] Claim with every evidence source referenced
  {0.75|i|E001,E002,E003,E004|2026-04-01|investigated|meta} Meta-claim
  about the state of knowledge across all evidence.

- [C012] Claim with multiple relations on same line
  {0.70|c|E004|2026-04-01} Computational output. →C001, ←C011, ⊗~C003

## Verbose — All Features

- **[C020]** Verbose claim with all six fields and relations
  `confidence: 0.93 | type: inferred | evidence: E001, E002 | since: 2026-04-01 | depth: exhaustive | nature: judgment`
  Full verbose syntax with every field populated.
  `relations: supports C002, contradicts:tension C003`

- **[C021]** Verbose claim demonstrating error-type contradiction
  `confidence: 0.88 | type: computed | evidence: E004 | since: 2026-04-01 | depth: exhaustive`
  Recomputed analysis shows C003 contains an error.
  `relations: contradicts:error C003`

- **[C022]** Verbose claim with cross-pack reference
  `confidence: 0.70 | type: reported | evidence: E003 | since: 2026-03-15 | depth: assumed`
  Related work in a separate pack.
  `relations: see_also typical-fixture#Findings`
