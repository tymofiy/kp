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
pack: prediction-too-confident | v: 2026.05.09 | domain: test/conformance
confidence: simple | normalized
---

# Prediction Too Confident Fixture

> INVALID: C001 has nature=prediction with confidence 0.97, exceeding the
> 0.95 cap. Violates SC-12 (predictive claims must not exceed 0.95
> confidence; reserve >0.95 for trivially-falsifiable factual claims).

## Claims

- [C001] The widget market will reach $5B in fiscal 2027
  {0.97|i|E001|2026-05-09|investigated|prediction} A future-tense claim with
  confidence above the 0.95 prediction cap.

- [C002] Plausibly-bounded prediction (sibling control)
  {0.80|i|E001|2026-05-09|investigated|prediction} This one is within the
  0.95 cap and is therefore valid.
