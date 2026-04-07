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
pack: mixed-syntax-fixture | v: 2026.04.04 | domain: test/conformance
confidence: sherman_kent | normalized
---

# Mixed Syntax Fixture [test-pack|MIX]

> Tests that dense and verbose claims coexist in the same document.

## Section A — Dense Claims

- [C001] Dense claim with all six positions
  {0.95|i|E001,E002|2026-04-01|exhaustive|judgment} Full metadata.
  →C002, ⊗~C010

- [C002] Dense claim with only required positions
  {0.80|o|E001|2026-04-01} Four required positions, no optionals.

- [C003] Dense claim with empty slot (skip depth, set nature)
  {0.85|r|E003|2026-03-20||prediction} Position 5 empty, position 6 set.

## Section B — Verbose Claims

- **[C010]** Verbose claim with full fields
  `confidence: 0.60 | type: inferred | evidence: E002, E003 | since: 2026-03-20 | depth: investigated | nature: judgment`
  This claim is in tension with C001 — both are informative.
  `relations: contradicts:tension C001`

- **[C011]** Verbose claim that supersedes an older version
  `confidence: 0.90 | type: computed | evidence: E001 | since: 2026-04-01 | depth: exhaustive`
  Updated analysis replaces a prior finding.
  `relations: supersedes C003`
