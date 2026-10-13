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
pack: minimal-fixture | v: 2026.04.04 | domain: test/conformance
confidence: simple | normalized
---

# Minimal Fixture

> Bare minimum valid knowledge pack for conformance testing.

## Claims

- [C001-v3] The current assessment is three days.
  {0.85|i|E001|2026-04-04|investigated|judgment} Revision after another measurement. ⊘C001-v2

- [C002] The prior note is retained for context.
  {0.90|r|E001|2026-04-04} ↔C001
