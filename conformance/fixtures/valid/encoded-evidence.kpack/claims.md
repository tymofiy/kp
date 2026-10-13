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
pack: encoded-evidence | v: 2026.07.11 | domain: test/conformance
confidence: simple | normalized
---

# Encoded Evidence Fixture

> A source payload may contain record-shaped Markdown without creating records.

## Claims

- [C001] The pack has exactly one canonical evidence entry
  {0.95|o|E001|2026-07-11} Encoded source scaffolding remains E001 body content.
