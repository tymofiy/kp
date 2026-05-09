<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Knowledge Pack Specification — Changelog

---

## v0.8.0-preview — 2026-05-09

**Three-lane normative architecture, EXTENSIONS validation, spec self-discovery, AI-first packaging (AGENTS.md + AUTHORING.md), and companion-doc readiness for v0.8.0.**

The v0.8.0 preview consolidates a deliberate architectural pass on the spec's normative structure (the three lanes), an honest validation of every active extension block, two new spec-level fields that let a sealed `.kpack` archive be self-explaining to a cold receiver, several companion-doc additions (RECONCILIATION stub, VOICE `register` axis, MULTILINGUAL `en-GB` row + sub-registers), and the AI-first packaging that the format's framing requires (root-level `AGENTS.md` task-routing file plus `spec/AUTHORING.md` producer-side decision rubrics). No core schema is broken; pre-v0.8.0 packs continue to validate.

### Added

- **Three normative lanes** (`spec/README.md`) — explicit declaration that KP:1 carries normative weight across CORE.md (implementer surface), SPEC.md (full spec + rationale + ecosystem), and topic-authoritative companions. Companions are NOT mere extensions of CORE/SPEC: for matters within their domain, the companion is the normative authority. CORE.md and SPEC.md gain `Lane:` lines in their metadata blocks pointing at the README overview.
- **`AGENTS.md`** (NEW, repo root) — AI-first routing file. Provides a task→reading map for the four canonical tasks (parse, author, reconcile, translate) plus composition and playback. Tells a cold AI agent exactly which files to load and which to skip per task, so the agent doesn't have to ingest 9,000+ lines of normative prose before doing useful work. Includes a MUST-NOT list distilling the most common failure modes (translating `claims.md`, omitting Rosetta header, defaulting to `⊗~` for every contradiction, emitting `1.0` confidence everywhere). Closes the central gap all four external reviewers flagged.
- **`spec/AUTHORING.md`** (NEW companion) — producer-side decision rubrics. Provides explicit decision trees for the closed vocabularies CORE.md defines but does not adjudicate: claim type (`o`/`r`/`c`/`i`), claim nature (factual / judgment / prediction / meta), contradiction qualifier (`⊗` / `⊗!` / `⊗~`), confidence calibration within Sherman Kent bands, depth (`assumed` / `investigated` / `exhaustive`), supersede vs edit vs split, granularity, and content routing (claims / evidence / views). Each rubric carries worked examples, anti-patterns, and hostile-reading sanity checks (Agreeable Pack, Atomic Dust, Confidence Hallucination, View Laundering). The format's vocabulary without rubrics was the single largest authoring gap; AUTHORING.md closes it.
- **`spec_uri` and `spec_version`** (PACK.yaml manifest root, optional) — discovery pointer that lets a previously-unfamiliar consumer (especially a cold receiver of a sealed `.kpack` archive) fetch the full spec from the URL the pack itself names. Complements the inline Rosetta header (the minimum-viable parse hint at the top of `claims.md`). New "Spec Discovery" subsection in CORE.md §3 and "Format discoverability" subsection in ARCHIVE.md §2 codify the cold-receiver protocol: consumers SHOULD read PACK.yaml first and follow `spec_uri` (when declared). Default published location: `https://github.com/tymofiy/kp`.
- **`extensions.translations`** (EXTENSIONS.md §2.8, NEW block) — evidentiary multilingual transcripts for packs whose canonical claims are English (per MULTILINGUAL §2 P1) but whose underlying evidence is in another language (handwritten witness statements, foreign-language press, recorded interviews). The English claim remains the single normative assertion; `translations` carries original-language transcripts as audit trail without making them co-canonical. Inaugural producer: the reference handwritten-inventory intake pipeline.
- **VOICE.md `register` axis** — recommended metadata header field on voice views with four spec values: `plain`, `curatorial`, `technical`, `investor`. Composes orthogonally with `pace` (speed vs diction). Distinct from app-side `AudienceProfile.persona` (consumer concept).
- **`en-GB` language tag** (MULTILINGUAL.md §3.2 table) — mechanical sibling of `en-US` distinguished by spelling, idiom, and a small set of dialect-specific terms. Other `en-*` tags reserved.
- **Register Sub-distinctions** (MULTILINGUAL.md §3.3, NEW subsection) — informational `sub_register` voice-view metadata field for locale-specific sub-registers (Western Ukrainian / Halychyna, Quebec French, peninsular Spanish, MSA vs spoken Arabic). Refines within the four VOICE.md primary registers rather than replacing them. Reviewer-responsibility note: a pack declaring `sub_register` MUST be reviewed by a native speaker of that sub-register.
- **RECONCILIATION.md** (NEW companion stub) — explicit placeholder for the cross-pack consolidation protocol. Full design deferred to v0.9 / v1.0 contingent on observing measurable drift across at least three real packs. Distinguishes from CONSISTENCY (single-workspace patrol) and LIFECYCLE (single-pack claim lifecycle).
- **`kpack` CLI status disclaimer** (SPEC.md §13) — explicit note that the `kpack` commands described in §13 (`kpack lint`, `kpack render`, `kpack reconcile`, `kpack translate`, etc.) describe **planned reference tooling**, not commands that ship in this repository today. The only command that exists today is `python3 conformance/run.py`. Closes the "fictional CLI" critique.
- **`examples/art-acquisition-decision.kpack/`** (NEW reference example) — anonymized buyer-side decision-support pack. Demonstrates the full repertoire of contradiction qualifiers (`⊗`, `⊗!`, `⊗~`), supersession (`⊘`), all four claim types (`o/r/c/i`), multiple confidence calibrations, judgment / prediction / meta natures, and three audience-specific views (overview, counsel, voice briefing in curatorial register). Walks the decision rubrics from `spec/AUTHORING.md` end-to-end on a realistic decision-support scenario.
- **`examples/auction-house-consignment-review.kpack/`** (NEW reference example) — anonymized consigner-side decision pack. An auction house declines a sculpture consignment over a foundry-mark attribution dispute, with conditions for reconsideration. Demonstrates the decline path (judgment-shaped recommendation against acquisition rather than for it), cross-pack `↔` references, evidence-diversity over consignor-supplied + house-specialist material, and four audience-specific views including a formal-register consignor decline letter. Together with `art-acquisition-decision.kpack`, the two examples cover both sides of high-stakes asset-decision support.
- **`spec/LIFECYCLE.md` §6 Claim Supersession Cascade** (NEW section) — normative rule for what happens to dependent claims (linked via `→supports` / `←requires` / `~refines`) when a parent claim is superseded with `⊘`. The cascade is reviewed by the editor, not auto-invalidated; the rationale and a worked example are inline. Cross-pack effects are explicitly deferred to RECONCILIATION.md.
- **`spec/RATIONALE.md`** (NEW companion, informative) — collected rationale, philosophy, and positioning. Houses the 25 numbered Design Principles (formerly SPEC.md §15), the Style Systems specification and rationale (formerly SPEC.md §17), and the Relationship to Existing Standards table (formerly SPEC.md §20). Bifurcation lets SPEC.md focus on the implementer-facing surface without interleaving rationale prose. Marked explicitly "informative — not normative for KP:1 conformance."

### Bifurcated

- **`spec/SPEC.md` §15 / §17 / §18 / §20** — sections moved to RATIONALE.md and replaced with stubs that link forward. SPEC.md reduced from 1,996 to ~1,780 lines.
  - §15 Design Principles → [RATIONALE.md §1](spec/RATIONALE.md). All 25 numbered principles.
  - §17 Style Systems → [RATIONALE.md §2](spec/RATIONALE.md). Style-system rationale, schema, renderer pipeline. SPEC.md §17 retains only the brief PACK.yaml `style` field reference.
  - §18 Cognitive Perception Layer → split. SPEC.md §18 retains the **normative** `display` block field list, the `hint` field, and the fallback hierarchy (the contract a renderer needs). The **rationale** (perception stages with timed budgets, Why-each-field-exists boxes, Stranger Test, Good/Bad authoring tables) moves to [RATIONALE.md §4](spec/RATIONALE.md).
  - §20 Relationship to Existing Standards → [RATIONALE.md §3](spec/RATIONALE.md). Comparison to AGENTS.md / llms.txt / SKILL.md / MCP / RDF / Nanopublications.
- **Cross-reference sweep.** All "(Principle N)" / "(SPEC.md §15, Principle N)" references in the rest of the spec corpus updated to point at `RATIONALE.md §1` instead. Touched: COMPOSITION.md, CONSISTENCY.md, DEFINITIONS.md, LIFECYCLE.md, SPEC.md, STORAGE.md.

### Tooling

- **`reference/kpack`** (NEW contract-pointer stub) — closes the "fictional CLI" critique with a concrete pointer rather than just a SPEC.md disclaimer. Running `./reference/kpack <subcommand>` prints the spec section that defines that subcommand's contract (e.g., `kpack reconcile` → `spec/RECONCILIATION.md`, `kpack lint` → `spec/SPEC.md §13`, `kpack play` → `spec/PLAYBACK.md`). The stub does not implement any subcommand; it points at the contract. The only fully-implemented validator in this repo remains `python3 conformance/run.py`.

Conformance after these additions: 15/15 (was 13/13 at v0.8.0-preview ship; new examples added to the auto-validated suite).

### Changed

- **EXTENSIONS.md** — validation pass against producer evidence in `repos/packs/`. Status grid honest as-of v0.8.0: `ai_brief` (active, ~21 producers), `research` (active, ~16 producers), `entities` / `relations` / `intent` / `playbook` / `workspace` (experimental, 0–1 producers each). Added explicit producer counts on the `research` block. New `extensions.translations` block at §2.8 is tagged `active` despite single inaugural producer; the policy tension is documented inline. Subsequent editorial pass (post-cleanup commit) replaced internal monorepo paths and project codenames with public repo references plus generic "reference implementation" language so the public spec doesn't leak internal identifiers.
- **Companion-doc Parent: lines** — dropped stale `> **Parent:** SPEC.md v0.X` lines from MULTILINGUAL, CONVENTIONS, BUNDLE, ORGANIZATION, CONSISTENCY, NOTES, STORAGE in the master-plan release; the post-master-plan cleanup commit extended this to ARCHIVE / VOICE / LIFECYCLE (no anchor → drop entire line) and softened version pins on COMPOSITION / DEFINITIONS / EXTENSIONS while preserving section anchors. CORE.md `Derived from: SPEC.md v0.7` was also drift-stripped to `Derived from: SPEC.md`. Several `(v0.4)` / `(v0.6)` section header pins removed from SPEC.md.
- **`spec/CORE.md`** — added cross-references to AUTHORING.md from §1 (scope) and to SPEC.md §10 from §2 (validation.yaml schema). AR-10 row gained worked positive/negative tokenization examples (`~C002` is the relation, `~refines` and `~the manuscript` are prose).
- **`spec/EXTENSIONS.md`** — `extensions.intent` enum framing softened to clarify it is the reference implementation's vocabulary (producers MAY define alternative values), not a closed normative enum embedded in an explicitly informative document.
- **`spec/SPEC.md`** — Quick Start `claims.md` example gained the previously-omitted Rosetta header, so a fresh agent copying the example produces a pack that actually passes conformance. The cleanup commit also fixed pedagogical examples in COMPOSITION.md §3 (ASCII relation glyphs `-> * <- ~ / <->` → KP symbols `→ ⊗ ← ~ ⊘ ↔`; `[M001]–[M005]` → `[C001]–[C005]`) and LIFECYCLE.md (`[M001]–[M008]` → `[C001]–[C008]`; `EM003`/`EM004` → `E003`/`E004`) so the worked examples actually validate against CORE.
- **`spec/MULTILINGUAL.md`** — section ordering corrected (Evidentiary multilingual exception is §12; Decision Log is §13; the master-plan ship had them reversed). Decision Log D1a entry updated correspondingly. The §12 + D1a inaugural-producer narrative replaced specific project codenames with the generic `witness statements collected in the field` framing.
- **`spec/MAPPING.md`** — `Status: Reference document` → `Status: Draft (informative — not normative for KP:1 conformance)` to harmonize sibling vocabulary while preserving the informative-vs-normative distinction.
- **`spec/ORGANIZATION.md`** — directory listing in §1 refreshed to include all 19 spec files (CORE, README, ARCHIVE, DEFINITIONS, EXTENSIONS, MAPPING, PLAYBACK, RECONCILIATION, STORAGE were missing from the v0.7-era listing).
- **`SPEC.md` title** — `v0.7` → `v0.8.0`.
- **`README.md`** — status banner v0.7-preview → v0.8.0-preview; conformance fixture count corrected (`11 test fixtures plus 4 reference examples`, totaling `15/15 validated`); `pip install -r conformance/requirements.txt` bootstrap line added; citation example updated to v0.8.0-preview while preserving the v0.7-preview Zenodo DOI as historical reference.
- **`CITATION.cff`** — version `0.7-preview` → `0.8.0-preview`; date-released `2026-04-06` → `2026-05-09`. v0.7-preview Zenodo DOI tagged `(historical)` pending v0.8.0-preview Zenodo deposit (queued as WS-TAG).

### Compatibility

- **No core schema break.** `spec_uri` and `spec_version` are optional manifest fields. `extensions.translations` lives in the existing `extensions` lane (added in v0.7.4). The VOICE `register` field is recommended, not required. Pre-v0.8.0 packs continue to validate against the v0.8.0-preview conformance runner.
- **Companions reaffirmed normative.** The "Three normative lanes" framing does not weaken CORE: where CORE makes a claim, that claim still holds. But for topics CORE explicitly punts to a companion (per CORE's `see [COMPANION]` cross-references), the companion now carries explicit full normative weight on that topic, codifying what was implicit.

### Notes

- A v0.8.0-preview Zenodo deposit will follow this entry (WS-TAG: tag, deposit, GitHub release).
- The v0.8.0 *final* (non-preview) release will follow once the deferred RECONCILIATION design is observed-and-grounded (≥3 real drift instances) and the remaining iPad / Mariupol implementation tracks have shipped against the spec.

---

## v0.7.7.1 — 2026-05-09

**Schema-only conformance relaxations.**

Schema-side fixes for two classes of conformance failures surfaced in
the 2026-04-30 ecosystem audit. No core spec or companion-document
changes; pure schema bumps.

### Changed
- **`display.short_title` `maxLength` 30 → 60** — Real canonical names of
  organisations and people overflow 30 chars (e.g., "LVMH Moët Hennessy
  Louis Vuitton", "Ministry of Culture and Strategic Communications of
  Ukraine"). The field's intent (constrained display contexts) is preserved
  — UI ellipsis at smaller widths is the rendering layer's job, not the
  schema's. Description updated to reflect the wider envelope and the
  rendering-layer responsibility.
- **`role` enum gained `"co-author"`** — Authorship role for packs
  co-authored by humans and AI (substrate authoring with parallel
  cross-model sessions). Existing roles unchanged.

### Compatibility
- **Monotonic relaxation, no breaking changes.** Pre-v0.7.7.1 packs
  continue to validate (anything that fit the 30-char `short_title` cap
  still fits the 60-char cap; the new `role` value is additive). Producers
  MAY now emit `short_title` up to 60 chars and `role: "co-author"`.

---

## v0.7.7 — 2026-04-28

**Extensions catalogue + `entities.md` deprecation.**

The KP:1 manifest root remains closed; the `extensions` lane (added in v0.7.4)
is the sanctioned compatibility surface for producer-defined metadata. This
release catalogues the producer-defined extension blocks that the Nova
ecosystem uses today and retires the never-fully-realized `entities.md`
companion file in favour of the typed `extensions.entities` block.

### Added
- **EXTENSIONS.md** (NEW companion document) — informative catalogue of
  producer-defined extension blocks under `extensions.*` in active use across
  the Nova ecosystem. Documents `extensions.ai_brief` (the v0.7.4 example),
  `extensions.entities` (typed entity graph), `extensions.relations` (typed
  edges between entities, mirroring the relation_types vocabulary in
  DEFINITIONS.md §3), `extensions.intent` + `extensions.intent_schema_version`
  + `extensions.intent_derivation` (decision-frame layer), `extensions.playbook`
  (runtime trace of playbook execution), `extensions.workspace` (Decision
  Workspace bookkeeping), and `extensions.research` (free-text research
  metadata). Cross-cutting sections cover canonical entity ID minting
  (`ent_<type>_<6-hex>`), the recommended `external_ids` vocabulary, and the
  per-claim `extensions.entity_refs` / `extensions.relation_refs` annotation.
  Migration notes cover `entities.md` → `extensions.entities` and free-text
  `anchor_subject` → typed entities.
- **README.md companion table entry** for EXTENSIONS.md.

### Changed
- **DEFINITIONS.md §3** — relation_types example block prose extended with a
  pointer to the `extensions.relations` consumer pattern. The vocabulary
  itself is unchanged; the addition documents that producers now write
  relation instances under `extensions.relations` in PACK.yaml rather than
  in a separate file.
- **SPEC.md §7 (entities.md)** — section retitled "Deprecated: entities.md"
  with a deprecation banner pointing to `extensions.entities` as the
  successor. The full prior content is preserved for legacy reference.

### Deprecated
- **`entities.md`** — used in only five packs out of ~770 and never landed as
  a practical primitive. Producers MUST NOT emit `entities.md` in new packs.
  Equivalent and richer information now lives under `extensions.entities`
  (typed entity records with stable Nova IDs and external-ID vocabulary)
  and `extensions.relations` (typed edges with optional temporal and
  attribute data per DEFINITIONS.md §3). A one-shot migration script
  (`scripts/migrate-entities-md-to-extensions.mjs`, shipped with kp-forge)
  rewrites legacy packs into the new shape.

### Compatibility
- **No core schema change.** The manifest root is unchanged. Producers and
  consumers continue to round-trip pre-v0.7.7 packs without modification.
- **Consumers MUST ignore unknown extension content** per the extensions
  lane contract (CORE.md §1.1, SPEC.md §3.2). Pre-existing producers and
  consumers that do not understand the new blocks continue to function;
  the new blocks are additive.
- **Legacy `entities.md` packs continue to validate** against the v0.7.7
  conformance runner. The deprecation is a producer-side guidance, not a
  validation removal.

---

## v0.7.6 — 2026-04-19

**Documented optional Admiralty grading fields on evidence.**

### Added

- **`reliability` and `credibility` evidence fields** — Documented in CORE.md §10 as optional evidence fields with normative values from the NATO Admiralty Code. `reliability` is the source-tier letter (`A`–`F`); `credibility` is the per-fact information credibility digit (`1`–`6`). Together they form the standard intelligence-tradecraft `A1`–`F6` grade. Both were previously accepted as open-vocabulary AR-07 fields and ignored by validators; this change makes the values normative without breaking any existing pack (both remain optional, parsers MUST tolerate absence).

### Notes

No breaking changes. Packs produced before this entry remain valid. Packs that already used `reliability` informally (e.g. `**reliability:** moderate`) MAY continue to do so but SHOULD migrate to the single-letter `A`–`F` form for renderer interoperability.

---

## v0.7.5 — 2026-04-18

**Signatures schema alignment + composition-pack file requirements.**

### Added
- **`pack_id` in `signatures.yaml`** — Stable pack identity across versions, emitted by current sealers and used by relays. Documented in ARCHIVE.md §4 with a prose MAY/SHOULD policy for backwards compatibility (schema accepts absence; new archives SHOULD include it). `pack_name` and `pack_version` also documented as optional self-describing receipts.
- **`parent.merge_parents`** — Optional array inside the `parent` block for branch-merge lineage. Each entry has the same `version`/`pack_hash` shape as `parent` itself. Documents a latent capability declared in the sealer implementation so the refreshed schema does not reject valid merge-lineage archives.
- **Composition-pack file requirements** — New subsection in SPEC.md §2 listing the file-presence rules for composition packs: `composition.yaml` REQUIRED, `claims.md` REQUIRED (intentionally minimal, about the composition context only), `evidence.md` OPTIONAL. Cross-references `spec/COMPOSITION.md` for semantics.
- **Signatures schema validation in the conformance runner** — `conformance/run.py` now validates any `signatures.yaml` it finds against `kp-signatures.schema.json`, with `jsonschema.FormatChecker` enabled so declared formats (`date-time`) are actually enforced. Empty-file and YAML parse errors are surfaced with friendly messages. Previously the runner was silent on signatures.
- **Fixture: `composition.kpack`** — Valid-pack fixture demonstrating the composition-pack minimum shape (composition.yaml present, no evidence.md, prose-only claims.md).
- **Fixture: `signatures.yaml` on `maximal.kpack`** — Exercises the signatures schema with a populated `parent` block and the optional `pack_name`/`pack_version` fields.

### Changed
- **`kp-signatures.schema.json`** — Regenerated to match ARCHIVE.md §4 (v0.7.3+ shape). Required fields are now `algorithm`, `pack_hash`, `files`, `sealed_at`, `sealed_by`. Optional: `pack_id`, `pack_name`, `pack_version`, `parent` (with `version` + `pack_hash` + optional `merge_parents`), `signature` (with `method` + `value` + `key_id`). Previous pre-v0.7.3 fields (`signed_at`, `signing_key`, `signature` as a flat string) removed. Schema root closed with `additionalProperties: false`, mirroring the manifest-schema pattern. The `files` map now enforces "MUST NOT include signatures.yaml itself" via `propertyNames`, not prose alone.
- **`conformance/run.py`** — `validate_pack()` detects composition packs (those with `composition.yaml`) and skips the `evidence.md` presence check for them. Evidence-ID extraction now tolerates a missing `evidence.md` (empty set rather than exception). `signatures.yaml` is validated against the new schema when present, with `FormatChecker` enabled so `format: date-time` on `sealed_at` is actually enforced.

### Fixed
- **Schema-vs-impl drift** — The prior `kp-signatures.schema.json` required fields (`signed_at`, `signing_key`, `signature` as a flat string) that neither the sealer (kp-forge) nor the relay (kp-packs) have produced or consumed since v0.7.3. Any current sealed archive would have failed schema validation. Aligned.
- **Composition-pack validation hole** — Packs with `composition.yaml` and no `evidence.md` (valid per `COMPOSITION.md` design) were being rejected by the conformance runner for the missing-file reason. No longer.

---

## v0.7.4 — 2026-04-16

**Manifest extension lane — standardizes where experiments belong without widening the core schema.**

### Added
- **`extensions`** (PACK.yaml, optional object) — Explicit lane for experimental or implementation-specific manifest metadata. Root-level unknown fields remain invalid; experiments now belong under `extensions`.

### Changed
- **CORE.md** — Documents the manifest root as closed and defines the `extensions` object as the sanctioned compatibility lane.
- **SPEC.md** — Adds example manifest usage and guidance that experimental fields such as `ai_brief` belong under `extensions`, not at the manifest root.
- **Schema** — Adds `extensions` as an allowed top-level object while preserving `additionalProperties: false` at the manifest root.

---

## v0.7.3 — 2026-04-12

**Archive format — sealed, hashed, versioned single-file transport for Knowledge Packs.**

### Added
- **Archive companion spec** (`ARCHIVE.md`) — Defines the ZIP-based archive format for pack transport between systems. Covers content hashing (SHA-256, deterministic, container-independent), `signatures.yaml` schema, version chains with parent hash references, sealing protocol, and verification. Resolves AR-14 (`signatures.yaml` schema deferred to Phase C2).
- **`signatures.yaml` schema** — Formalized in ARCHIVE.md §4 with normative field types. Fields: `algorithm`, `pack_hash`, `files` (per-file hashes, lowercase hex), `sealed_at`, `sealed_by`, `parent` (version chain), optional `signature` (digital signing). Required in sealed archives.
- **Version chain model** — Each sealed pack version references its parent's `pack_hash`, forming a verifiable integrity chain. Branching acknowledged; merge-parent semantics deferred to a future version.
- **Seal & transport CLI commands** — `kpack seal`, `kpack verify`, `kpack verify --chain`, `kpack extract`, `kpack info`. (`kpack archive` remains reserved for lifecycle archival per LIFECYCLE.md.)
- **Security considerations** (§10) — ZipSlip/path traversal protection, symlink rejection, duplicate entry rejection, OS metadata exclusion, line ending advisory, Unicode NFC normalization.
- **Conformance levels** — Sealed archive (with `signatures.yaml`, integrity chain) vs. export archive (without, convenience only).
- **Signing payload** — Signature binds `algorithm` + `pack_hash` + `sealed_at` + `sealed_by` + `parent.version` + `parent.pack_hash`, preventing metadata tampering.

### Changed
- **CORE.md** AR-14 updated — `signatures.yaml` schema now resolved by ARCHIVE.md. `composition.yaml` remains deferred.
- **CORE.md** scope paragraph updated — ARCHIVE.md added to the list of companion documents.
- **CORE.md** Appendix C updated — ARCHIVE.md added to companion specifications table.
- **README.md** — ARCHIVE.md added to companion documents table.
- **SPEC.md** — `signatures.yaml` file role updated to reference ARCHIVE.md.
- **Hash computation** (§3) — Mandates NFC Unicode normalization for paths, lowercase hex digests, bare relative paths (no `./` prefix), and root-only `signatures.yaml` exclusion. Adds canonicalization notes for line endings and OS metadata.
- **Signing methods** — Clarified that HMAC-SHA256 provides tamper detection only, not non-repudiation. Ed25519 recommended as default. RSA uses PSS padding.
- **ZIP safety** — Added mandatory safety requirements (§2): path traversal rejection, symlink rejection, duplicate entry rejection, OS metadata stripping.
- **ZIP64** — Changed from SHOULD to MUST for archives exceeding 4 GB.
- **CLI examples** — Updated to show `-o` output paths, avoiding the `.kpack` file-vs-directory coexistence issue.
- **Visibility table** — Corrected from `kpack archive` to `kpack seal`.

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
