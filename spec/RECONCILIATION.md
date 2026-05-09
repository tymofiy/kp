<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Reconciliation — Knowledge Pack Companion Spec

> **Date:** 2026-05-09
> **Status:** Stub — full design deferred to v0.9 / v1.0
> **Editor:** Timothy Kompanchenko

---

## Purpose

When two or more Knowledge Packs make claims about the same entity or topic and those claims drift apart over time — different confidence values, different evidence emphasis, contradictory positions — the ecosystem needs a **reconciliation protocol**. This companion will specify how packs surface drift, how reconciliation is triggered, and how the resulting consolidated view is encoded.

## Status

This document is an **explicit placeholder**. The full reconciliation design is deferred to KP:1 v0.9 or v1.0, contingent on observing measurable drift across at least three real packs. Premature design before observed drift would be wishful architecture; the spec records the intent while honestly admitting the design is not yet ready.

The honest record of the deferred design discussion lives in workspace memory; it is not part of the public normative spec until at least three real-world drift instances have been observed and the design is informed by those instances rather than imagined ones.

## Related, but distinct

- [`CONSISTENCY.md`](CONSISTENCY.md) — current cross-pack consistency patrol. Detects contradictions and staleness across packs in a workspace; surfaces drift as a signal but does not consolidate.
- [`LIFECYCLE.md`](LIFECYCLE.md) — pack-internal claim lifecycle (active / superseded / disputed / retracted). Operates within a single pack.

Reconciliation differs from both: it is the **cross-pack consolidation protocol** for genuine multi-source drift, applied after CONSISTENCY surfaces a sustained disagreement that LIFECYCLE-internal mechanisms cannot resolve.

## What to do today (v0.8.0-preview)

Until the full protocol is specified, agents encountering cross-pack contradictions SHOULD produce a *consistency report* rather than a *reconciled pack*. The output is an annotated comparison, surfaced to a human reviewer, that uses the existing primitives:

- **`↔packB#claim-id`** — name the cross-pack reference at the point of disagreement.
- **`⊗!` / `⊗~`** from [AUTHORING.md §4](AUTHORING.md) — apply *within* a single annotated pack to characterize the disagreement (use `⊗!` only when one side is demonstrably wrong; default to `⊗~` for genuine productive tension).
- **Do NOT silently merge.** Do not produce a third "reconciled" pack that erases the disagreement. The format's value is preserving epistemic tension, not flattening it.

### Worked example

Pack A (`market-snapshot.kpack`) asserts:

```text
- [C001] Global widget market is approximately $2B {0.85|r|E001|2025-Q1|investigated}
```

Pack B (`market-snapshot-v2.kpack`) asserts:

```text
- [C001] Global widget market is approximately $3B {0.85|r|E007|2025-Q4|investigated}
```

A v0.8.0-preview reconciliation report (a new pack `widget-market-reconciliation.kpack`) would look like:

```text
- [C001] Pack A reports widget market at ~$2B (Q1 2025); Pack B reports ~$3B (Q4 2025).
  {0.95|o|E001,E002|2026-05-09} Direct observation that the two source packs assert
  different values. ↔market-snapshot#C001 ↔market-snapshot-v2#C001

- [C002] The disagreement is best read as a temporal snapshot difference rather than
  a methodological dispute, since Pack A's E001 (Q1) is older than Pack B's E007 (Q4).
  {0.78|i|E001,E007|2026-05-09|investigated|judgment} ⊗~C001

- [C003] Recommendation: treat Pack B's $3B figure as the more recent reading; cite
  Pack A's $2B as historical-snapshot context. Final reconciliation deferred to a
  human reviewer who can confirm methodology equivalence.
  {0.65|i|E001,E007|2026-05-09|investigated|judgment|meta} ←C002
```

The report pack uses CORE-conformant syntax throughout, references the source packs via `↔`, and explicitly defers the final canonical answer. This is the v0.8.0-preview answer for cross-pack disagreement: **annotate, surface, defer to human** — do not auto-flatten into consensus.

The full reconciliation protocol (when it ships in v0.9 / v1.0) will define how reports like this become canonical reconciliations and what semantic constraints govern the consolidated graph.
