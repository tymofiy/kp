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
pack: typical-fixture | v: 2026.04.04 | domain: test/conformance
confidence: sherman_kent | normalized
---

# Typical Fixture [test-pack|TYP,conformance]

> A realistic mid-range pack exercising common KP:1 features.

## Findings

- [C001] Primary finding supported by multiple evidence sources
  {0.92|i|E001,E002|2026-04-01|exhaustive|judgment} Cross-referenced across
  two independent sources with consistent conclusions. →C002

- [C002] Secondary finding that follows from the primary
  {0.85|i|E002|2026-04-01|investigated} Derived from E002 analysis.
  Strengthened by C001 convergence. ←C001

## Risks

- [C010] Known risk that contradicts optimistic findings
  {0.60|r|E003|2026-03-15|investigated|judgment} Reported by a single
  source with moderate credibility. Tension with C001 is productive —
  it highlights the timeline uncertainty. ⊗~C001

- [C011] Mitigation path exists but is unverified
  {0.45|i|E003|2026-03-15|assumed|prediction} If the risk in C010
  materializes, this mitigation is the most likely response. ←C010
