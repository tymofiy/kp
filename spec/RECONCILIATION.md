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
