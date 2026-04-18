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
pack: composition-fixture | v: 2026.04.18 | domain: test/conformance
confidence: simple | normalized
---

# Composition Fixture

> Composition pack fixture. References other packs via `composition.yaml` — see `minimal-fixture` and `typical-fixture`. Evidence lives in those referenced packs, not here. This pack carries composition-context narrative only.

## Composition Context

This fixture exercises the composition-pack path in the conformance runner. It has `composition.yaml` present, no `evidence.md`, and only narrative content in `claims.md` — no dense claim bullets to cite evidence for.

A composition pack SHOULD contain claim bullets when its composition context warrants them (e.g., a meeting pack with claims about the meeting itself). This fixture intentionally omits them to prove the minimum-shape case.
