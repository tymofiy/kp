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
pack: cyclic-supersession | v: 2026.05.09 | domain: test/conformance
confidence: simple | normalized
---

# Cyclic Supersession Fixture

> INVALID: C001 ⊘ C002 and C002 ⊘ C001 forms a cycle. Violates SC-04
> (supersession graph must be a DAG).

## Claims

- [C001] First claim that supersedes the second
  {0.80|o|E001|2026-05-09} ⊘C002

- [C002] Second claim that supersedes the first
  {0.80|o|E001|2026-05-09} ⊘C001
