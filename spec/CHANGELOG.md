<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Knowledge Pack Specification — Changelog

---

## v0.7.3 — 2026-04-12

**Archive format — sealed, hashed, versioned single-file transport for Knowledge Packs.**

### Added
- **Archive companion spec** (`ARCHIVE.md`) — Defines the ZIP-based archive format for pack transport between systems. Covers content hashing (SHA-256, deterministic, container-independent), `signatures.yaml` schema, version chains with parent hash references, sealing protocol, and verification. Resolves AR-14 (`signatures.yaml` schema deferred to Phase C2).
- **`signatures.yaml` schema** — Formalized in ARCHIVE.md §4. Fields: `algorithm`, `pack_hash`, `files` (per-file hashes), `sealed_at`, `sealed_by`, `parent` (version chain), optional `signature` (digital signing). Required in archives participating in an integrity chain.
- **Version chain model** — Each sealed pack version references its parent's `pack_hash`, forming a verifiable integrity chain. Branching and merge-parent support defined for concurrent edits.
- **Seal & transport CLI commands** — `kpack seal`, `kpack verify`, `kpack verify --chain`, `kpack extract`. (`kpack archive` remains reserved for lifecycle archival per LIFECYCLE.md.)

### Changed
- **CORE.md** AR-14 updated — `signatures.yaml` schema now resolved by ARCHIVE.md. `composition.yaml` remains deferred.
- **CORE.md** Appendix C updated — ARCHIVE.md added to companion specifications table.
- **README.md** — ARCHIVE.md added to companion documents table.
- **SPEC.md** — `signatures.yaml` file role updated to reference ARCHIVE.md.

---

## v0.7.2 — 2026-04-12

**Schema tightening and new metadata fields — informed by cross-model open-standards review.**

### Added
- **`evidence_basis`** (PACK.yaml, optional string) — Narrative description of the evidence foundation underpinning a pack. Informational, not machine-actionable.
- **`tags`** (PACK.yaml, optional array) — Topical tags for discovery and classification. Enforced as unique, strict kebab-case strings (`^[a-z0-9]+(-[a-z0-9]+)*$`; no trailing hyphens).
- **Voice view fields** on view declarations — `voice` (boolean), `duration` (string, pattern `~N seconds` or `~N minutes`), `pace` (enum: `brisk`, `measured`, `deliberate`). Formalizes the PACK.yaml ↔ VOICE.md contract.
- **Voice view conditional** — When `voice: true`, `duration` and `pace` are REQUIRED on that view entry. Prevents incomplete voice metadata.

### Changed
- **`vocabulary` additionalProperties** loosened from `string` to `oneOf [string, array<string>]`. Array branch requires `minItems: 1` and `uniqueItems: true`. Backward-compatible: existing string-valued entries remain valid.
- **`pace`** constrained to enum matching VOICE.md (`brisk`, `measured`, `deliberate`). Previously unconstrained string.
- **`duration`** constrained to pattern `^~\d+\s+(seconds?|minutes?)$`. Previously unconstrained string.
- **CORE.md** updated to document `evidence_basis`, `tags`, and voice view fields in the Core Optional Fields table.
- **VOICE.md** examples updated to include `display_as` on voice view declarations (required by schema but previously omitted in examples).
- **Maximal conformance fixture** updated to exercise all new fields.

---

## v0.5 — 2026-03-24

**Epistemic refinements — informed by Barenboim analysis of knowledge vs. information.**

### Added
- **Investigation depth** (claim field, position 5) — `assumed` / `investigated` / `exhaustive`. Distinguishes uninvestigated assumptions from informed uncertainty. A 0.50 at `exhaustive` depth is more valuable knowledge than 0.90 at `assumed`.
- **Claim nature** (claim field, position 6) — `judgment` / `prediction` / `meta`. Omitted = factual assertion. Enables agents to reason differently about interpretive conclusions, forward-looking claims, and claims about the state of knowledge itself.
- **Contradiction qualifiers** — `⊗!` (error: one is wrong) and `⊗~` (tension: both informative, preserve). Bare `⊗` remains the unqualified default.
- **Verbose alternative syntax** — Named-field format (`confidence: 0.95 | type: inferred | ...`) accepted alongside dense positional notation. Both valid KP:1. Tooling must parse both.
- **history.md format** — Defined structure for superseded and retracted claims with metadata and context.
- **Evidence reliability guidance** — Evidence prose should describe source reliability, perspective, and relationship to the claim.

### Changed
- **claims.md is active-only** — Resolves the v0.4 contradiction between "active claims ONLY" and "append-only lifecycle." Superseded/retracted claims move to history.md. Disputed claims stay active (the dispute IS the current state).
- **Split rule reframed** — Hub packs provide the interpretive framework (thesis, tensions, confidence landscape), not just the most important facts.
- **Consistency checking** updated for contradiction qualifiers: `⊗~` (tension) skipped by patrol, `⊗!` (error) prioritized, stale disputes (>90 days) flagged.

---

## v0.4 — 2026-03-22

**Three-surface architecture and ecosystem expansion.**

### Added
- **Three-surface architecture** — Voice views join reasoning (claims.md) and display (views/) as a third surface optimized for spoken delivery
- **Multilingual support** — Locale subdirectories (`views/{locale}/`), translation workflow, drift detection, status tracking. Companion spec: `MULTILINGUAL.md`
- **Pack lifecycle management** — Three lifecycle types (permanent, seasonal, ephemeral), intelligent archival with claim reconciliation, visibility controls. Companion spec: `LIFECYCLE.md`
- **Meeting pack composition** — Composition over standing packs via `composition.yaml`, pre-load/on-demand references, agenda-driven structure. Companion spec: `COMPOSITION.md`
- **Bundle/export format** — Single-file format for sharing outside IDE (full bundle + clipboard variant). KP:1 marker. Companion spec: `BUNDLE.md`
- **Notes metadata** — AI note-taking mode (active/passive/off), disclosure tracking, consent for passive mode. Companion spec: `NOTES.md`
- **Cross-pack consistency** — Automated patrol for contradictions, staleness, broken references. Real-time alerting during conversations. Companion spec: `CONSISTENCY.md`
- **Linguistic conventions** — 30-rule American English convention table, Merriam-Webster as spelling authority, 7-level fallback hierarchy. Companion spec: `CONVENTIONS.md`
- **Pack organization** — Nested categories, two-zone model (clean packs vs legacy), migration strategy. Companion spec: `ORGANIZATION.md`
- **7 new design principles** (§14, #16-22): three surfaces one truth, composition over duplication, archive never delete, reconcile before archive, knowledge is the source, locale first then surface, renderer not compositor

### Changed
- Two-surface architecture → **three-surface architecture** throughout
- PACK.yaml: added `visibility`, `lifecycle`, `locales`, `notes` optional field blocks
- File structure: added `composition.yaml`, voice view directory, locale subdirectories
- Tooling: added extended CLI commands (bundle, archive, reconcile, translate, patrol, new)
- Spec now lives in `spec/` directory with companion documents, not as a single file in `packs/`

---

## v0.3 — 2026-03-21

**Views layer and two-surface architecture.**

### Added
- Views layer (pre-rendered display content in `views/`)
- Two-surface architecture (reasoning + display)
- Style system references (STYLE.yaml)
- Collection semantics (entity cards, analytics views)
- View generation (`kpack render`), staleness detection
- Semantic markers (`> [!metric]`, `> [!highlight]`, etc.)

---

## v0.2 — 2026-03-19

**Density optimization.**

### Added
- Density-optimized claim format with compressed metadata `{confidence|type|evidence|date}`
- Voyager Principle — self-describing files with Rosetta Header
- Inspectability over readability philosophy
- Symbolic relations (`→⊗←~⊘↔`)

---

## v0.1 — 2026-03-10

**Initial specification.**

### Added
- Core file structure (PACK.yaml, claims.md, evidence.md, entities.md)
- Confidence model with Sherman Kent scale
- Claim lifecycle (active, superseded, disputed, retracted)
- Pack hierarchy (hub, detail, standalone)
- Navigation (KNOWLEDGE.yaml, sub_packs, inline cross-references)
- Validation framework (validation.yaml)
