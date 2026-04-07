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
pack: verbose-claims-fixture | v: 2026.04.04 | domain: test/conformance
confidence: simple | normalized
---

# Verbose Claims Fixture [test-pack|VERB]

> All claims use the verbose named-field syntax exclusively.

## Assertions

- **[C001]** First verbose claim with all six fields
  `confidence: 0.95 | type: inferred | evidence: E001, E002 | since: 2026-04-01 | depth: exhaustive | nature: judgment`
  Both evidence sources converge. This is the strongest claim in the pack.
  `relations: supports C002`

- **[C002]** Second verbose claim with only required fields
  `confidence: 0.70 | type: reported | evidence: E002 | since: 2026-04-01`
  Reported finding without depth or nature annotation.

- **[C003]** Verbose claim demonstrating contradiction qualifier
  `confidence: 0.55 | type: inferred | evidence: E003 | since: 2026-03-20 | depth: investigated | nature: judgment`
  This finding is in productive tension with C001.
  `relations: contradicts:tension C001`
