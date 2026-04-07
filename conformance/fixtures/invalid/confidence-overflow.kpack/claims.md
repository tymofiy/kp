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
pack: confidence-overflow | v: 2026.04.04 | domain: test/conformance
confidence: simple | normalized
---

# Confidence Overflow Fixture

> INVALID: Claim C002 has confidence 1.50 which exceeds the [0.0, 1.0] range.

## Claims

- [C001] Valid claim with confidence in range
  {0.80|o|E001|2026-04-04} This is fine.

- [C002] Invalid claim with confidence exceeding 1.0
  {1.50|i|E001|2026-04-04} Confidence 1.50 is outside the normalized
  range [0.0, 1.0]. Violates semantic constraint SC-01.
