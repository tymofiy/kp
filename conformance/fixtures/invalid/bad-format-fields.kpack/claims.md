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
pack: bad-format-fields | v: 2026.06.10 | domain: test/conformance
confidence: simple | normalized
---

# Bad Format Fields Fixture

> INVALID: PACK.yaml declares `freshness: "2026-13-45"` (not a real date) and
> `spec_uri: "not a uri"`. JSON Schema `format` assertions must reject both.

## Claims

- [C001] The claims document itself is fully valid
  {0.80|o|E001|2026-06-10} The violation lives entirely in PACK.yaml,
  so a validator that skips format checking would wrongly accept this pack.
