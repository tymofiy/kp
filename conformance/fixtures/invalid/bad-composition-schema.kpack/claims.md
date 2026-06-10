<!-- KP:1 — Knowledge Pack Format
Claims: - [ID] assertion {confidence|type|evidence|date|depth|nature} context
  Positions 5-6 optional. Verbose named-field syntax also accepted.
Types: o=observed r=reported c=computed i=inferred
Depth: assumed | investigated | exhaustive (optional, position 5)
Nature: judgment | prediction | meta (optional, position 6; omitted=factual)
Relations: →supports ⊗contradicts ⊗!error ⊗~tension ←requires ~refines ⊘supersedes ↔see_also
Files: evidence.md=sources history.md=past entities.md=graph composition.yaml=references
-->
---
pack: bad-composition-schema | v: 2026.06.10 | domain: test/conformance
confidence: simple | normalized
---

# Bad Composition Schema Fixture

> INVALID: `composition.yaml` declares `meeting.date: next tuesday`, which is
> not an ISO 8601 datetime. Every other field is valid, so the only violation
> is the `date-time` format assertion — a validator that does not check
> `composition.yaml` against its schema (or skips format checking) would
> wrongly accept this pack.

## Composition Context

This fixture mirrors the valid `composition.kpack` shape: `composition.yaml`
present, no `evidence.md`, narrative-only claims content.
