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
pack: hello-world | v: 2026.06.10 | domain: examples/getting-started
confidence: simple | normalized
---

# Hello World [example]

> The smallest idiomatic Knowledge Pack: three claims, two evidence entries,
> one relation each of `→` (supports) and `~` (refines). Copy this directory
> and edit to start your own pack.

## Getting Started

- [C001] A Knowledge Pack is a directory of plain text
  {0.95|o|E001|2026-06-10} Verified by opening this very pack in any
  editor — PACK.yaml, claims.md, evidence.md, nothing hidden.

- [C002] Every claim carries its own confidence and cites its evidence
  {0.90|o|E001,E002|2026-06-10} The block after each headline holds
  confidence, claim type, evidence IDs, and the date established. →C001

- [C003] Uncertainty is recorded, not rounded away
  {0.60|i|E002|2026-06-10|investigated|judgment} A 0.60 stays a 0.60 —
  the reader decides what to make of it. ~C002
