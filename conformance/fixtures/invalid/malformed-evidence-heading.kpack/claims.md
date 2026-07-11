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
pack: malformed-evidence-heading | v: 2026.07.11 | domain: test/conformance
confidence: simple | normalized
---

# Malformed Evidence Heading Fixture

> INVALID: A heading prefix is not a conforming evidence-record identity.

## Claims

- [C001] This claim references evidence that is not canonically defined
  {0.80|o|E001|2026-07-11} The malformed heading must not satisfy SC-03.
