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
pack: duplicate-evidence-ids | v: 2026.07.11 | domain: test/conformance
confidence: simple | normalized
---

# Duplicate Evidence IDs Fixture

> INVALID: Two top-level evidence records share E001. Violates SC-13.

## Claims

- [C001] This claim references an ambiguous evidence identifier
  {0.80|o|E001|2026-07-11} A consumer cannot know which E001 is authoritative.
