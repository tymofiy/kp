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
pack: auction-house-consignment-review | v: 2026.05.09 | domain: art/decision-support
confidence: simple | normalized
---

# Consignment Review — Late-19th-Century Bronze Sculpture [decision|2026-05-09]

> Reviewing a bronze sculpture submitted for consignment to the upcoming sale of nineteenth-century European works. The submission was accompanied by a consignor's attribution to a major sculptor of the period; the house's specialist review surfaced a foundry-mark discrepancy that the consignor disputes. This pack records the committee's decline decision and the conditions under which the work could be reconsidered.

## Submission

- [C001] The work was submitted for consignment by Vendor V on 2026-04-22, with a stated reserve of 180,000 euro and an attribution to Sculptor Y.
  {0.99|o|E001|2026-04-22} The submission letter and consignment agreement draft are on file.

- [C002] Vendor V states that the work was inherited from a family member who acquired it at a 1971 estate sale, and produces an auction catalog entry from that sale citing the work as "by Sculptor Y."
  {0.95|r|E001,E002|2026-04-22|investigated} The catalog page is genuine; the catalog's attribution is the basis of Vendor V's claim.

## Physical Examination

- [C003] The work is a 38-centimetre bronze figure, signed on the base "Y." in the lower right.
  {0.99|o|E003|2026-05-02} Direct measurement and visual inspection by the house's nineteenth-century specialist.

- [C004] Surface patina, casting weight, and bronze alloy composition are consistent with a casting executed between 1880 and 1900.
  {0.83|o|E004|2026-05-02|investigated} The specialist's metallurgical observation; not formally confirmed by laboratory analysis.

- [C005] The foundry mark on the underside is "Foundry F, Paris," which is documented in the foundry-marks reference to have begun operating in 1925 — twelve years after Sculptor Y's death in 1913.
  {0.95|o|E005,E006|2026-05-03|exhaustive} Direct observation of the mark plus verification against the published reference of Parisian art-foundry marks.

## The Attribution Dispute

- [C006] Vendor V's attribution treats the work as a lifetime cast by Sculptor Y, on the strength of the 1971 catalog entry and the family provenance chain.
  {0.91|r|E001,E002|2026-04-22|investigated} Restating the consignor's position; not the house's read.

- [C007] The house's specialist concludes that the work is a posthumous cast, executed by Foundry F between 1925 and approximately 1940, after a Sculptor Y model.
  {0.87|i|E004,E005,E006|2026-05-03|investigated|judgment} The foundry-mark evidence is dispositive: a cast produced after the sculptor's death cannot be a lifetime work, regardless of how faithfully the model is rendered. ⊗!C006

- [C008] The 1971 auction catalog described the work as "by Sculptor Y" without distinguishing lifetime from posthumous casts; this attribution conflates two materially different categories under contemporary art-market conventions.
  {0.83|i|E002|2026-05-09|investigated|judgment} The 1971 catalog is genuine and accurate to its time; conventions for distinguishing lifetime from posthumous casts strengthened in the 1980s. The pre-convention catalog is not wrong but does not establish what Vendor V claims it establishes. →C007

## Market Context

- [C009] At auction in 2024-2025, lifetime casts by Sculptor Y in this size range achieved hammer prices of 320,000 to 540,000 euro.
  {0.99|c|E007|2026-05-09} Computed from three lot results in the public auction record.

- [C010] At auction in 2024-2025, Foundry F posthumous casts after Sculptor Y achieved hammer prices of 80,000 to 140,000 euro.
  {0.99|c|E007|2026-05-09} Same source; different lot category.

- [C011] The reserve of 180,000 euro stated in the consignment agreement is above the posthumous-cast range and below the lifetime-cast range.
  {0.99|c|E001,E007|2026-05-09} Computed: 140,000 < 180,000 < 320,000.

- [C012] The reserve appears calibrated to the consignor's lifetime-cast attribution, not the house's posthumous-cast read.
  {0.83|i|E001|2026-05-09|investigated|judgment} A reading of intent; alternative readings are possible but the price level is closer to the consignor's frame than the specialist's.

## Reputational and Operational Risk

- [C013] Listing the work as "by Sculptor Y" without distinguishing the cast period would expose the house to reputational and potential legal risk if a buyer subsequently discovered the foundry-mark evidence.
  {0.91|i|E005,E006,E007|2026-05-09|investigated|judgment} The risk is not theoretical: comparable mis-cataloguing has been the subject of post-sale rescission claims and downward revaluations in the field.

- [C014] Listing the work as "after Sculptor Y, posthumous cast" would resolve the risk but would conflict with the consignor's attribution and likely lead to consignment withdrawal.
  {0.83|i|E001|2026-05-09|investigated|judgment} A reading of the consignor's likely response based on the reserve calibration (C012).

- [C015] Reattributing the work in catalog text without consignor agreement would breach the consignment agreement.
  {0.95|r|E008|2026-05-09|investigated} The standard consignment agreement reserves attribution-text rights to the house but requires consignor sign-off on attribution-language changes.

## Decision

- [C016] Recommended action: decline the consignment.
  {0.83|i|E001,E005,E007,E008|2026-05-09|investigated|judgment} A judgment grounded in the foundry-mark evidence (C005), the market-segment misalignment (C011), and the reputational risk (C013). The decision is not a verdict on the work itself; it is a decision about whether this house can accept this consignment under this attribution.

- [C017] Recommended condition: the consignment may be reconsidered if the consignor agrees to a "after Sculptor Y, posthumous cast, Foundry F, c. 1925-1940" attribution and a reserve aligned with the posthumous-cast market range.
  {0.91|i|E005,E007|2026-05-09|investigated|meta} A condition on C016. ~C016

- [C018] If the consignor declines C017 and submits the work to a different house under the lifetime-cast attribution, the work will likely be withdrawn or revalued at that house once the foundry mark is examined.
  {0.55|i|E005|2026-05-09|investigated|prediction} A prediction about a hypothetical future event; confidence is moderate because foundry-mark examination is not universal practice across all houses.

## Cross-References

- [C019] Foundry F's operating dates and known mark variations are documented in a separate reference pack maintained by the house specialist.
  {0.91|r|E006|2026-05-09|investigated} Pointer to the reference work used for the mark identification (C005).
  ↔foundry-marks-paris-1925-1960#foundry-f

- [C020] Sculptor Y's authorized cast records are not publicly available in a form the house can consult directly; the specialist relies on the published catalog raisonné and on a research pack maintained internally.
  {0.83|r|E009|2026-05-09|investigated} Documents the limitation in the attribution work.
  ↔sculptor-y-attribution-research#authorized-casts
