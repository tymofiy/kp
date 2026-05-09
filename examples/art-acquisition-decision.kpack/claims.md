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
pack: art-acquisition-decision | v: 2026.05.09 | domain: art/decision-support
confidence: simple | normalized
---

# Acquisition Review — Mid-Century European Painting [decision|2026-05-09]

> A buyer-side decision-support pack for the prospective acquisition of an
> oil-on-canvas work by a recognized European modernist, offered by a
> reputable gallery in May 2026. The pack records what is known, what is
> uncertain, what is in tension, and what action follows.

## Offering and Authorship

- [C001] The work is offered for sale by Gallery K, dated 2026-05-08, with asking price stated in writing.
  {0.99|o|E001|2026-05-08} Direct receipt of offer letter; the offer's
  existence is verifiable from the document.

- [C002] The asking price is 950,000 euro.
  {0.99|o|E001|2026-05-08} Stated explicitly in the offer letter.

- [C003] Authorship is attributed to Artist X by the gallery and corroborated by the museum catalog raisonné.
  {0.91|r|E001,E003|2026-05-09|investigated} Two-source corroboration; the
  raisonné is the field-authoritative reference.

## Dating

- [C004] The work is dated 1957 in the auction-house specialist's report prepared for the prior owner.
  {0.83|r|E002|2025-11-15|investigated} Single-source assertion; the
  specialist's qualifications are stated in the report header.

- [C005] The work is dated 1962 in the museum catalog raisonné.
  {0.91|r|E003|2020-04-30|exhaustive|judgment} The catalog raisonné is
  field-authoritative; its dating reflects multi-year scholarly consensus.
  ⊗!C004

- [C006] The auction-house specialist accepts the catalog dating as authoritative and withdrew the 1957 attribution in November 2025.
  {0.95|r|E009|2025-11-20|investigated} Email correspondence from the
  specialist to the prior owner; archived as part of the transaction file.
  →C005

## Provenance

- [C007] Provenance is documented continuously from 1962 to the present consignor (Gallery K's vendor).
  {0.87|r|E005|2026-05-09|investigated} The 1962-onwards chain is recorded
  in the catalog raisonné and corroborated by the gallery's own ownership
  records.

- [C008] There is a gap in the documented provenance from 1953 to 1962, with no party identified as having owned or held the work during that period.
  {0.91|r|E005|2026-05-09|exhaustive} Exhaustive search of the catalog
  raisonné, two relevant national art-loss registries, and one specialized
  archive returned no record. The gap is itself a documented finding.
  ⊗~C007

- [C009] The work has not been the subject of any restitution claim or recovery filing as of 2026-05-09.
  {0.91|r|E010|2026-05-09|investigated} Confirmed against the major loss
  registries and the publicly searchable claim databases.

## Comparables and Pricing

- [C010] Three comparable works by Artist X sold at auction between 2024-Q1 and 2025-Q3.
  {0.99|r|E006|2026-05-09} Lot results published in the public auction
  record.

- [C011] The hammer-price range across the three comparable lots was 820,000 to 1,180,000 euro.
  {0.99|c|E006|2026-05-09} Computed directly from the lot results.

- [C012] The current asking price of 950,000 euro falls within the comparable hammer-price range.
  {0.99|c|E006|2026-05-09} Computed: 820,000 ≤ 950,000 ≤ 1,180,000.
  ←C002, ←C011

## Valuation History

- [C013] An independent appraisal commissioned by the prior owner in 2023 valued the work at 1,400,000 euro.
  {0.85|r|E007|2023-09-12|investigated} The 2023 appraisal predates the
  dating revision (C005) and used a comparable set that has since been
  partly invalidated by subsequent reattributions in the field.

- [C014] An updated appraisal commissioned by Gallery K in 2025 valued the work at 950,000 euro, matching the current asking price.
  {0.91|r|E008|2025-12-15|investigated} The 2025 appraisal incorporates the
  dating revision and a refreshed comparable set.
  ⊘C013

## Technical Examination

- [C015] X-ray fluorescence of the surface layer is consistent with Artist X's documented palette for the 1960-1965 period.
  {0.87|o|E004|2025-12-04|investigated} Direct laboratory observation;
  consistency assessed by reference to four documented works of the period.
  →C005

- [C016] Underdrawing visible in infrared imaging is consistent with the artist's known compositional method.
  {0.83|o|E004|2025-12-04|investigated} Single examination; conclusions
  qualified by the laboratory technician.
  →C003

## Risk Analysis

- [C017] The 1953-1962 provenance gap creates a material risk that an earlier good-faith holder may emerge with a claim against the present ownership chain.
  {0.45|i|E005,E010|2026-05-09|investigated|judgment} A judgment, not a
  measurement; another reasonable analyst could place this risk lower
  given the absence of any current claim. Confidence reflects genuine
  uncertainty.

- [C018] Comparable mid-century works with documented 5-10 year provenance gaps have not historically been the subject of successful restitution claims when the post-gap chain is well-documented.
  {0.65|r|E011|2026-05-09|investigated|judgment} Reported judgment from a
  field analyst; weight is moderate because the analyst's sample is
  limited.

## Recommendation

- [C019] Recommended action: conditional acquisition.
  {0.78|i|E001,E004,E005,E006,E008,E010|2026-05-09|investigated|judgment}
  Synthesis of the supporting and risk claims. The recommendation is a
  judgment, not a fact; another buyer with different risk tolerance might
  decline. ⊗~C017

- [C020] Recommended condition: completion of supplementary provenance research targeting the 1953-1962 period before close of escrow, with a contractual right to withdraw if a prior good-faith holder is identified.
  {0.91|i|E005|2026-05-09|investigated|meta} A condition on C019. Frames
  what "conditional" requires operationally. ~C019

- [C021] If the supplementary provenance research concludes without identifying a prior good-faith holder, the residual risk falls within the buyer's stated tolerance.
  {0.55|i|E005|2026-05-09|investigated|prediction} Prediction nature: the
  research outcome is not yet known; this is the conditional implication.

## Open Tensions

- [C022] The dating revision (C005) reduces the comparable set's relevance for valuation by approximately one third, since lots dated 1955-1959 in Artist X's market are now distinct from lots dated 1960-1965.
  {0.65|i|E006|2026-05-09|investigated|judgment} Judgment about market
  segmentation. The 2025 appraisal (C014) accounts for this; the prior
  appraisal (C013) does not, which is part of why C014 supersedes C013.
  →C014, →C012
