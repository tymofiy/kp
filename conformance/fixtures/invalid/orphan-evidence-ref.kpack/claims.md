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
pack: orphan-evidence-ref | v: 2026.04.04 | domain: test/conformance
confidence: simple | normalized
---

# Orphan Evidence Ref Fixture

> INVALID: Claim references E999 which does not exist in evidence.md.

## Claims

- [C001] Valid claim with valid evidence reference
  {0.80|o|E001|2026-04-04} This claim is fine.

- [C002] Invalid claim referencing non-existent evidence
  {0.75|i|E001,E999|2026-04-04|investigated} E999 does not exist in
  evidence.md. This violates semantic constraint SC-03.
