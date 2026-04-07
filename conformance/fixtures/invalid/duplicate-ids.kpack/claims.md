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
pack: duplicate-ids | v: 2026.04.04 | domain: test/conformance
confidence: simple | normalized
---

# Duplicate IDs Fixture

> INVALID: Two claims share the ID [C001]. Violates uniqueness constraint SC-02.

## Section A

- [C001] First claim with this ID
  {0.80|o|E001|2026-04-04} This is the first C001.

## Section B

- [C001] Second claim with the same ID
  {0.60|r|E001|2026-04-04} This is a duplicate. Which C001 do relations
  target? Ambiguity is why uniqueness is required.
