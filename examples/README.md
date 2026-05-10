<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# KP Examples

> **Status:** Four reference examples — two carryover from v0.7, two new in v0.8.0-preview.

Curated sample Knowledge Packs that demonstrate the format. Every example pack is validated by `python3 conformance/run.py` as part of the conformance suite (19/19 passing as of v0.8.1-preview).

## Examples

| Pack | Claims | Evidence | Views | Purpose |
|------|--------|----------|-------|---------|
| [`solar-energy-market.kpack`](solar-energy-market.kpack/) | 8 | 8 | 1 | Hello-world — dense + verbose syntax, a subset of relation types (`→`, `⊗~`, `←`), solar energy domain |
| [`kp-external-assessment.kpack`](kp-external-assessment.kpack/) | 12 | 4 | 4 | Self-assessment — KP:1's own external assessment, demonstrates truth-over-posture positioning |
| [`art-acquisition-decision.kpack`](art-acquisition-decision.kpack/) | 22 | 11 | 3 | Buyer-side decision pack — anonymized art acquisition demonstrating all four claim types, all three contradiction qualifiers (`⊗` / `⊗!` / `⊗~`), supersession (`⊘`), multiple confidence calibrations, judgment / prediction / meta natures, and three audience-specific views (overview, counsel, voice briefing). Walks the [AUTHORING.md](../spec/AUTHORING.md) decision rubrics end-to-end. |
| [`auction-house-consignment-review.kpack`](auction-house-consignment-review.kpack/) | 20 | 9 | 4 | Consigner-side decision pack — anonymized auction-house review of a sculpture consignment over a foundry-mark attribution dispute. The complement to `art-acquisition-decision.kpack`: same domain, opposite role, the *decline* path, cross-pack `↔` references, and four audience-specific views including a formal-register consignor decline letter. |

## Where to start

For a fresh reader of KP:1:

1. **`solar-energy-market.kpack`** is the simplest entry point. Read its [`claims.md`](solar-energy-market.kpack/claims.md) to see the claim syntax in action, then check [`PACK.yaml`](solar-energy-market.kpack/PACK.yaml) for the manifest format.
2. **`art-acquisition-decision.kpack`** is the comprehensive feature demo. Read it alongside [`spec/AUTHORING.md`](../spec/AUTHORING.md) to see how the decision rubrics translate into a real pack. This pack exercises every interesting feature of the format on a single coherent scenario.
3. **`auction-house-consignment-review.kpack`** demonstrates the *other side* of high-stakes asset-decision support — the decline path and cross-pack references.
4. **`kp-external-assessment.kpack`** is the meta example — KP:1 reasoning about itself.

## What each pack demonstrates

- **All four claim types (`o/r/c/i`):** `art-acquisition-decision` and `auction-house-consignment-review` exercise all four with a deliberate mix.
- **All three contradiction qualifiers (`⊗`, `⊗!`, `⊗~`):** `art-acquisition-decision` shows `⊗!` (one source demonstrably wrong) and `⊗~` (productive tension). `auction-house-consignment-review` shows `⊗!` over the foundry-mark attribution and `⊗~` over the recommendation/risk balance.
- **Supersession (`⊘`):** Both new packs have a superseded claim chain (an older valuation/dating replaced by a newer one).
- **Multiple natures:** Both new packs mix factual default with judgment, prediction, and meta annotations.
- **Confidence calibration:** Both new packs span 0.45–0.99 confidence, calibrated to evidence depth per [AUTHORING.md §5](../spec/AUTHORING.md).
- **Audience-specific views:** The new packs ship with overview / counsel / specialist / consignor-letter / voice-briefing views — each genuinely tuned to its audience, not cosmetic re-rendering.
- **Cross-pack `↔` references:** `auction-house-consignment-review` uses `↔` to point at hypothetical reference packs (with an inline note disclaiming their illustrative status — see that pack's `claims.md` Cross-References section).

## Validation

```bash
pip install -r ../requirements.txt
python3 ../conformance/run.py
```

Expected output: `19/19 passed` (15 fixtures in `../conformance/fixtures/` + 4 examples here).
