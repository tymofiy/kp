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
pack: a-different-name | v: 2026.05.09 | domain: test/conformance
confidence: simple | normalized
---

# Wrong Pack Name Fixture

> INVALID: Rosetta header `pack:` field is "a-different-name" but PACK.yaml
> `name:` is "wrong-pack-name". Violates SC-07 (Rosetta pack identifier must
> match PACK.yaml name).

## Claims

- [C001] A claim in a pack whose Rosetta header lies about the pack's name
  {0.80|o|E001|2026-05-09} The semantics are otherwise valid; only the
  identity disagreement triggers the violation.
