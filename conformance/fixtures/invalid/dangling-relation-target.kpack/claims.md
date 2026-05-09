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
pack: dangling-relation-target | v: 2026.05.09 | domain: test/conformance
confidence: simple | normalized
---

# Dangling Relation Target Fixture

> INVALID: C001 references C999 via →, but C999 does not exist in this pack.
> Violates SC-05 (intra-pack relation targets must exist).

## Claims

- [C001] Claim referencing a non-existent target
  {0.80|o|E001|2026-05-09} →C999 The target C999 is not defined anywhere
  in this pack and is not a cross-pack reference (would need pack#id form).

- [C002] Valid sibling claim
  {0.75|i|E001|2026-05-09|investigated} This one is fine.
