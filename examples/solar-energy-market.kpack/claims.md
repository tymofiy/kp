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
pack: solar-energy-market | v: 2026.03.18 | domain: energy/market-analysis
confidence: sherman_kent | normalized
---

# Solar Energy Market [market-analysis|SEM,solar]

> Utility-scale solar market trends, cost trajectories, and regional adoption patterns.

## Thesis

- [C001] Cost decline is structural, not cyclical — driven by manufacturing scale
  {0.95|i|E001,E002|2026-03-01|exhaustive|judgment} 10/10 analyses converged.
  Learning curve (22% cost reduction per doubling) has held for 40 years. →C002, ⊗~C003

- [C002] Grid parity already achieved in 75% of global markets
  {0.90|i|E001|2026-03-01|investigated|judgment} IRENA/BloombergNEF data.
  Subsidy removal in mature markets has not reversed adoption. →C001

- [C003] Cost floor approaching — further declines will slow significantly
  {0.30|r|E003|2026-02-14|investigated|judgment} Silicon material costs
  impose theoretical floor. 3/10 analyses supported this framing.
  Tension with C001 is informative — reveals the timeline question. ⊗~C001

## Technology

- [C010] Bifacial modules now 70% of new installations globally
  {0.99|o|E010|2026-03-18} Rear-side gain 5-25% depending on albedo.
  Bankability established. Monofacial declining to niche applications.

- [C011] Perovskite tandem cells: 33.7% lab efficiency (Oxford PV)
  {0.99|o|E011|2026-03-18} Lab-to-fab gap remains. Commercial viability
  estimated 2028-2030 for utility scale. →C012

- [C012] Durability is the unsolved risk for perovskite commercialization
  {0.75|i|E012,E013|2026-03-10} Moisture/heat degradation pathways known
  but not fully mitigated. 25-year warranty requirement is the hard gate. ←C011

## Market

- [C020] Utility-scale solar is now the cheapest new electricity source globally
  {0.92|o|E001,E002|2026-03-01|investigated} LCOE below gas and wind in most
  markets. Subsidy-independent growth trajectory confirmed. →C001, →C002

## Risks

- **[C030]** Supply chain concentration in China is the highest systemic risk
  `confidence: 0.90 | type: inferred | evidence: E001, E030 | since: 2026-03-01 | depth: exhaustive | nature: meta`
  80% of polysilicon, 95% of wafers. Tariff/geopolitical disruption could
  create 12-18 month supply gaps. 8/10 analyses flagged this. Not a technology
  problem — a trade policy and diversification problem.
  `relations: requires C020`
