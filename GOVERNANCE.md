<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# KP:1 Governance

> **Status:** Provisional. This document describes how the KP:1 specification is governed during the public draft phase, before the Knowledge Pack Foundation is incorporated. It will be replaced by the Foundation's formal governance documents once the Foundation exists.

## What this document is

KP:1 is currently an editor's draft maintained by a single editor in a public repository. This document explains:

- who the editor is and what authority they hold
- what "editor's draft" means in practice
- how decisions get made before a foundation exists
- the scope of this governance (what it covers and what it does not)
- how contributions are accepted during the preview phase
- how `KP:1` and `Knowledge Pack` may be used by implementers
- what changes when the Knowledge Pack Foundation is formed

This document is intended to make the current authority structure and transition path explicit, so that anyone reading the spec or considering contribution understands the actual state of affairs.

## Editor

**Editor:** Timothy Kompanchenko <tymofi@mac.com>

The editor holds sole merge authority over normative specification text in `spec/` and over the conformance suite in `conformance/`. The editor is also responsible for the changelog, the decision log, and the release process during the preview phase.

The editor is currently the sole author of the specification and is named on every spec document. Future contributors will be acknowledged in `CONTRIBUTORS.md` once the contribution model opens up under the Foundation.

## What "editor's draft" means

KP:1 is published as an **editor's draft**, following standards-body convention (W3C, IETF, WHATWG). This carries specific implications:

- **Not final.** The specification may change in any way at any time, including breaking changes to syntax, semantics, conformance rules, or companion specs.
- **Not ratified.** No standards body has accepted KP:1. There is no certification, endorsement, or external review process in place yet.
- **No compatibility guarantees.** Implementers should expect to update parsers, validators, and stored packs as the spec evolves. Stable compatibility commitments will arrive only with a non-draft version.
- **Public for feedback, not commitment.** Publishing the draft is an invitation to challenge, implement, and improve. It is not a claim that the design is complete.

The version label `KP:1` refers to the major specification line; the suffix on each release tag (`-preview`, `-draft`, etc.) signals the maturity stage. The first public draft is `v0.7-preview`, released as `KP:1 Public Draft — 2026-04`.

## How decisions get made (pre-Foundation)

During the preview phase, decision-making is **editor-led with public discussion**:

1. **Issues are public.** All technical discussion happens in the public GitHub issue tracker. Discussion in private channels does not count toward the record.
2. **The editor decides.** After reasonable public discussion, the editor makes the call and merges (or declines) changes to normative text.
3. **Decisions are documented.** Significant decisions are recorded in `CHANGELOG.md` and, for substantive design choices, in dated entries in `decisions/` (one file per decision, RFC-style).
4. **Reversal is possible.** Editor decisions are not permanent. Any decision can be reopened if new evidence or argument warrants it, until the spec is frozen.
5. **No private normative debate.** The editor will not make normative decisions based on conversations that have not happened (or been summarized) in public issues. This is a hard line — it exists to prevent the project from looking like founder-managed consultation.

Conversations that legitimately stay private during the preview phase:

- Foundation formation work (legal, IP assignment, incorporation, board composition)
- Donor and funder conversations
- Trademark filings and clearance
- Partner outreach where commercial confidentiality applies
- Legal advice from counsel (Kiki and any other retained attorneys)

These categories are private because they are inherently confidential, not because they are being kept out of public view to manage the technical narrative.

## Scope

This governance covers **the KP:1 specification and its interoperability-significant artifacts**, which includes:

- normative documents in `spec/` (CORE.md, SPEC.md, and companion specs)
- the formal grammar and JSON Schema in `conformance/grammar/`
- the conformance test suite in `conformance/` (fixtures, expected outcomes, runner)
- the canonical examples in `examples/`
- the changelog and decision log

Working materials in this repository — `positioning/` and `research/` — are not under spec governance. They evolve at the editor's discretion and are not normative.

This governance does **not** cover:

- commercial implementations of KP:1, including Bernard (the for-profit company building products on top of KP:1)
- third-party products, platforms, or tools that consume or produce KP:1 packs
- forks of the specification (which are not endorsed and may not use the KP:1 mark — see trademark policy below)
- the Knowledge Pack Foundation itself, which when incorporated will have its own governing documents (bylaws, board resolutions, contribution policy)

The separation is important: the spec is a public artifact; Bernard is a commercial actor that happens to be the first commercial implementer. Bernard's involvement in the spec is the same as any other implementer — feedback through public issues, no privileged decision-making.

## Contributions

See `CONTRIBUTING.md` for the full contribution policy. The short version:

- **Preview phase = feedback-only.** External pull requests modifying normative spec text in `spec/` will be closed without merge during the preview phase. This is a deliberate posture to keep inbound IP clean until the Foundation has a contributor agreement in place.
- **Normative scope is broad.** For avoidance of doubt: any external PR that changes the formal grammar, JSON Schema, conformance fixtures, expected pass/fail outcomes, or other interoperability-significant behavior is treated as a normative change and is not merged from external PRs during the preview phase. Open an issue instead.
- **Feedback is welcome and wanted.** Open issues for ambiguity reports, edge cases, conformance bugs, missing definitions, comparison with other formats, real-world implementation experience, or any other constructive challenge.
- **Code contributions to clearly non-normative areas** (additional examples that don't redefine semantics, tooling improvements that don't change validation behavior, documentation, typo fixes) are welcome under DCO sign-off.

Once the Foundation is incorporated and has adopted a contributor agreement (likely modeled on OWFa 1.0 or a W3C Community Group CLA), this policy will be relaxed.

## Conformance and trademark use policy

`KP:1` is a pending United States trademark (USPTO Serial 99747548, Class 9, intent-to-use, filed 2026-04-06). "Knowledge Pack" is the descriptive name of the format and is not currently a registered or pending trademark. The `KP:1` mark identifies the canonical specification maintained in this repository (and, in the future, by the Knowledge Pack Foundation). Use of the mark is governed by the following policy:

### Permitted use

- **Conformant implementations may describe themselves as "KP:1 conformant"** if they pass the entire conformance test suite at `conformance/` and correctly implement all normative requirements in `spec/CORE.md`.
- **Documentation, articles, tutorials, and educational materials** may freely use the names "KP:1" and "Knowledge Pack" to describe or teach the specification.
- **Translations and annotated versions** of the specification text are permitted under the CC-BY-4.0 license, provided they are clearly labeled as translations or annotations of the canonical spec, not as competing standards.
- **Quoting and excerpting** the spec text in books, papers, and other works is permitted under CC-BY-4.0 with attribution.

### Prohibited use

- **Modified or forked specifications may not present themselves as the canonical KP:1 specification, nor use the `KP:1` mark in a way that suggests canonical or endorsed status.** A fork is welcome to exist under any other name. This is the principal anti-fragmentation defense.
- **"KP:1 conformant" is reserved for implementations that actually pass the conformance suite.** False claims of conformance are not permitted.
- **The marks may not be used in product names, company names, or domain names** in a way that suggests endorsement by the editor or the (future) Foundation, without explicit written permission.
- **The marks may not be used in association with cryptocurrency tokens, NFTs, or speculative financial instruments**, regardless of permission.

This policy is enforced through trademark law once the `KP:1` mark is registered. Until registration is complete, the same expectations apply based on pending trademark application rights, and the mark is shown as pending (™) in repository materials.

### Why trademark, not copyright restriction

The specification text is intentionally permissively licensed (CC-BY-4.0). This enables translations, annotations, educational excerpts, and ecosystem bridges. During the preview phase, anti-fragmentation is handled through naming and conformance policy, not through a no-derivatives license. This approximates common modern open-standards practice (WHATWG, OWFa 1.0, Rust RFCs, Kubernetes KEPs), but it is not yet a substitute for the contributor and patent framework the Foundation will adopt.

## What changes when the Foundation forms

The Knowledge Pack Foundation is in formation as of 2026-04. When it is incorporated and operational:

1. **Governance authority transfers to the Foundation board.** The editor's role becomes a designated position within the Foundation's structure rather than a sole-authority position.
2. **A formal RFC process replaces editor-as-decider.** Significant changes will require an RFC document, public review period, and either editorial approval (for routine changes) or board approval (for substantive ones).
3. **A contributor agreement with explicit patent terms is adopted** (likely OWFa 1.0 or a W3C Community Group equivalent). The feedback-only restriction is lifted; external normative PRs become acceptable under the contributor agreement.
4. **IP transfers from the current editor to the Foundation.** Copyright in the spec text and the `KP:1` trademark are assigned to the Foundation. The editor retains attribution but not ownership.
5. **This GOVERNANCE.md is replaced** by the Foundation's bylaws, IP policy, contribution policy, and standing committees.

## Decision log

- `CHANGELOG.md` — high-level changes between releases
- `decisions/` — substantive design decisions with rationale (one file per decision, dated)

The decision log is the canonical record of *why* the spec is shaped the way it is. If a decision is not in the log, it is not yet a decision.

## Contact

**Editor:** Timothy Kompanchenko <tymofi@mac.com>

For specification questions or feedback, please open a GitHub issue. For private matters (legal, IP, partnerships, donor conversations, foundation formation), email the editor directly.
