<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Independence — Knowledge Pack Companion Spec

> **Status:** Draft companion (normative in intent, documentary in force — see "What makes these
> guarantees binding" below).
> **Date:** 2026-06-13
> **Editor:** Timothy Kompanchenko

---

## Purpose

KP:1 exists so that knowledge can be **owned**, not rented. A person (or organization) should be able
to hold their knowledge as files, hand those files to someone else in fifty or five hundred years, and
have them remain readable and usable — without paying anyone to maintain them, without a blessed tool,
without a registry, and without permission from whoever happens to steward the format at the time.

This companion states the independence guarantees that the format already provides, and commits the
project to preserving them. It does not introduce new mechanisms; it names the ones that exist and
makes the commitment explicit so that future stewardship cannot quietly erode it.

## What makes these guarantees binding

A sentence in a specification document is **not** itself a lock — a future editor or foundation that
controls this repository can revise any prose. The real, irrevocable guarantees live one layer beneath
this document:

- the **CC-BY-4.0 license** on every published version of the specification (a perpetual, irrevocable
  grant — anyone may use, adapt, and fork the text of any released version, forever); and
- the **distributed copies** of packs and of the spec that already exist outside any single party's
  control.

This document is therefore a **commitment and a Schelling point**, not the lock itself. Its force is
that it states plainly what the license and the format design already make true, so that a departure
from these guarantees is visible as a departure.

## The guarantees

1. **Zero-dependency readability (the directory is sufficient).** A conforming pack MUST be fully
   parseable and usable from the directory contents and the Rosetta header alone — no network, no
   registry, no server, no blessed runtime, no living maintainer, and no resolution of any external
   URL. The Rosetta header ([CORE.md §4](CORE.md)) carries the minimum parse hint inline; the optional
   `spec_uri` is an onboarding convenience and MUST NOT be fetched as a condition of validation
   ([CORE.md §3](CORE.md)). Any conforming reader — from a small local model running on consumer
   hardware to a frontier model — must be able to read a pack with nothing else.

2. **Freedom to fork.** The specification text is CC-BY-4.0; anyone may fork it. The `KP:1` trademark
   exists only to prevent a fork from impersonating the canonical specification — it is **defensive
   only and MUST NEVER be used to hinder a clean fork**. A fork is welcome to exist under any other
   name (see [GOVERNANCE.md](../GOVERNANCE.md)). Forking the content is a right, not a transgression; only
   the name is protected.

3. **No required registry or central service — ever.** Conformance MUST NOT depend on any central
   index, discovery service, certification authority, reconciliation service, or other coordination
   point. Composition and cross-pack reference are peer-to-peer (by relative reference), never via a
   mandated hub.

4. **Cryptography is optional for use.** Signing and integrity metadata are available
   ([ARCHIVE.md](ARCHIVE.md)) and recommended for sealed distribution, but **reading and using a pack
   MUST NEVER require keys, signatures, or verification tooling.** A plain, unsigned directory is a
   valid pack.

5. **Accrued knowledge stays portable.** A system that accumulates knowledge or memory on a person's
   behalf SHOULD let that person export the accrued state as a portable KP pack at any time. The
   format's purpose is defeated if the knowledge a person generates can be read back only through the
   tool that produced it.

## A principle: capture-resistance is subtraction, not addition

No artifact with a name and a maintainer can be made *impossible* to capture. What can be made
**pointless** to capture is one that requires nothing: capture the name, the registry, or the
stewarding organization, and every existing pack keeps working, in everyone's hands, forkable forever.
The captured thing is then an empty shell.

It follows that the durable defense of independence is **fewer dependencies and fewer authorities**,
not more governance. Every structure added to "protect" the format — a registry, a certification
program, a mandatory anything — is itself a new thing that can be captured. The guarantees above are
deliberately framed as removals (no required service, no required tool, no required key, no required
permission), because removals cannot be turned into chokepoints.

## Honest limits

- This is **capture-resistant, not capture-proof.** The goal is to make capture worthless, not
  impossible.
- The format is independent; **intelligence is not free.** Running a powerful model over a pack costs
  real compute, which may concentrate in whoever pays for it. The guarantee the format can make is the
  **floor**: a local-model path over your own packs must always remain a fully functional way to read
  and reason, even when a more capable hosted option exists. Independence means the floor is never
  removed — not that the ceiling is free. That floor itself rests on the continued availability of
  open-weight models and capable consumer hardware; it relocates dependence to a diffuse, competitive
  base rather than eliminating it.
- Stewardship of the specification should be funded **independently of any single implementer**, with
  no funder holding authority over normative decisions, so that the standard never bends to the
  commercial interest of one of its consumers.

---

*This file is a companion to [SPEC.md](SPEC.md), [CORE.md](CORE.md), and [GOVERNANCE.md](../GOVERNANCE.md).
Where it appears to specify parser behavior, the normative contract lives in CORE.md, the JSON Schema,
and the PEG grammar; where it appears to specify governance, GOVERNANCE.md is authoritative.*
