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
pack: missing-evidence-field | v: 2026.04.04 | domain: test/conformance
confidence: simple | normalized
---

# Missing Evidence Field Fixture

> INVALID: Claim C002 has no evidence references in its metadata.

## Claims

- [C001] Valid claim with evidence
  {0.80|o|E001|2026-04-04} This is fine.

- [C002] Invalid claim with empty evidence position
  {0.75|i||2026-04-04} The evidence field (position 3) is empty.
  Every claim MUST reference at least one evidence entry.
