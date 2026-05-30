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
pack: verbose-prediction-too-confident | v: 2026.05.09 | domain: test/conformance
confidence: simple | normalized
---

# Verbose Prediction Too Confident Fixture

> INVALID: C001 uses the verbose named-field syntax with nature=prediction and
> confidence 0.97, exceeding the 0.95 cap. Violates SC-12. This is the verbose
> counterpart of prediction-too-confident.kpack (dense syntax), so SC-12 is
> exercised on both metadata forms.

## Claims

- **[C001]** The widget market will reach $5B in fiscal 2027
  `confidence: 0.97 | type: inferred | evidence: E001 | since: 2026-05-09 | depth: investigated | nature: prediction`
  A future-tense claim with confidence above the 0.95 prediction cap.

- **[C002]** Plausibly-bounded prediction (sibling control)
  `confidence: 0.80 | type: inferred | evidence: E001 | since: 2026-05-09 | depth: investigated | nature: prediction`
  This one is within the 0.95 cap and is therefore valid.
