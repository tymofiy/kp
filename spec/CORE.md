<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# KP:1 Core Specification

> **Status:** Editor's Draft — `KP:1 Public Draft — 2026-04`
> **Editor:** Timothy Kompanchenko
> **Date:** 2026-04-04
> **Derived from:** SPEC.md v0.7, `conformance/grammar/kp-claims.peg`, `conformance/grammar/kp-pack.schema.json`

## 1. Introduction

KP:1 is a plain-text format for packaging epistemic state — claims with confidence, evidence, relationships, and contradictions. This document specifies everything required to **implement a conformant KP:1 parser and validator**. It is the normative core of the specification.

### Scope

This document covers:
- Pack directory structure and required files
- PACK.yaml manifest schema
- claims.md syntax (Rosetta header, frontmatter, claims in dense and verbose forms)
- evidence.md structure
- Views contract
- Confidence model
- Relation types
- Validation rules and semantic constraints
- Conformance levels

This document does **not** cover: voice surfaces (VOICE.md), composition/meetings (COMPOSITION.md), lifecycle management (LIFECYCLE.md), multilingual support (MULTILINGUAL.md), pack organization patterns (ORGANIZATION.md), consistency patrol (CONSISTENCY.md), naming conventions (CONVENTIONS.md), storage formats (STORAGE.md), bundling (BUNDLE.md), definition/policy document kinds (DEFINITIONS.md), or AI note-taking (NOTES.md). These are specified in companion documents within `spec/`.

### Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

| Term | Definition |
|------|-----------|
| Pack | A directory of plain-text files representing epistemic state |
| Claim | A belief with confidence, evidence, and relationships |
| Evidence | A backing source referenced by claims |
| View | A pre-rendered markdown document derived from claims, for human consumption |
| Rosetta header | Self-describing HTML comment at the top of claims.md |
| Frontmatter | Compact metadata block between `---` fences |

---

## 2. Pack Structure

A Knowledge Pack is a directory. The `.kpack/` suffix is RECOMMENDED but not required.

```text
{name}.kpack/
├── PACK.yaml          # REQUIRED — manifest
├── claims.md          # REQUIRED — current claims
├── evidence.md        # RECOMMENDED — backing sources
├── history.md         # OPTIONAL — superseded/retracted claims
├── entities.md        # OPTIONAL — entity definitions
├── validation.yaml    # OPTIONAL — test questions
├── signatures.yaml    # OPTIONAL — cryptographic integrity
└── views/             # OPTIONAL — pre-rendered display content
    └── overview.md
```

Implementations MUST require `PACK.yaml` and `claims.md`. All other files are OPTIONAL for conformance.

---

## 3. PACK.yaml Manifest

PACK.yaml is a YAML file declaring pack identity and configuration. The normative schema is `conformance/grammar/kp-pack.schema.json` (JSON Schema 2020-12).

### Required Fields

| Field | Type | Pattern | Description |
|-------|------|---------|-------------|
| `name` | string | `^[a-z0-9][a-z0-9-]*$` | Pack identifier, kebab-case |
| `version` | string | `^YYYY.MM.DD(-revN)?$` | CalVer snapshot date |
| `domain` | string | `^[a-z0-9][a-z0-9-]*(/[a-z0-9][a-z0-9-]*)*$` | Hierarchical domain path |
| `author` | string | non-empty | Maintainer name |

### Core Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `kind` | enum | `claim` (default), `definition`, `policy`, `mixed` |
| `description` | string | Human-readable summary |
| `confidence` | object | `scale` (string, required within object), `normalize` (boolean), `labels` (object, for custom scales) |
| `freshness` | date | Last substantive review date |
| `license` | string | Reuse terms (e.g., `CC-BY-4.0`) |
| `sensitivity` | enum | `public`, `internal`, `confidential`, `restricted` |
| `visibility` | enum | `private`, `shared`, `public` |
| `channels` | array | Distribution routing strings |
| `display` | object | `short_title`, `abbreviation`, `tagline`, `hook` |
| `provenance` | object | `author` (required), `role` (required), `reviewed_by`, `review_date`, `signed` |
| `evidence_basis` | string | Narrative description of the evidence foundation underpinning this pack |
| `tags` | array | Topical tags for discovery and classification. Strict kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`), unique |
| `views` | array | View declarations with `name`, `file`, `purpose`, `display_as` (all required), `hint` (optional). Voice views add `voice` (boolean), `duration` (string, e.g. `~90 seconds`), `pace` (enum: `brisk`, `measured`, `deliberate`). When `voice` is `true`, `duration` and `pace` are REQUIRED. |
| `tier` | enum | `hub`, `detail`, `standalone` |

The full set of optional fields and conditional constraints is defined in the JSON Schema. Key conditionals: when `tier` is `hub`, `sub_packs` is REQUIRED; when `sensitivity` is `confidential` or `restricted`, `channels` MUST NOT contain `public` or `org`; when `sensitivity` is `internal`, `channels` MUST NOT contain `public`; when a view declares `voice: true`, `duration` and `pace` are REQUIRED on that view entry.

### Example

```yaml
name: solar-energy-market
version: 2026.03.18
domain: energy/market-analysis
author: Jane Chen
confidence:
  scale: sherman_kent
  normalize: true
```

---

## 4. claims.md — Rosetta Header

Every claims.md MUST begin with a self-describing HTML comment before the frontmatter. This is the **Rosetta header**.

Format: `<!-- KP:` followed by the spec version number, legend text, and `-->`. Parsers MUST check the spec version. Parsers MAY ignore the legend text.

```markdown
<!-- KP:1 — Knowledge Pack Format
Claims: - [ID] assertion {confidence|type|evidence|date|depth|nature} context
  Positions 5-6 optional. Verbose named-field syntax also accepted.
Types: o=observed r=reported c=computed i=inferred
Depth: assumed | investigated | exhaustive (optional, position 5)
Nature: judgment | prediction | meta (optional, position 6; omitted=factual)
Relations: →supports ⊗contradicts ⊗!error ⊗~tension ←requires ~refines ⊘supersedes ↔see_also
Files: evidence.md=sources history.md=past entities.md=graph
-->
```

The Rosetta header is part of the **constitutional core** (see [Section 14](#14-constitutional-core)) and is frozen across all spec versions.

---

## 5. claims.md — Frontmatter and Heading

### Frontmatter

The frontmatter is a **KP-specific compact format**, NOT arbitrary YAML (AR-08). It sits between `---` fences and has exactly two lines with fixed field order.

```text
---
pack: {name} | v: {CalVer} | domain: {domain}
confidence: {scale} | normalized
---
```

Parsers MUST NOT attempt to parse this as standard YAML.

### Document Heading

An H1 heading with an optional entity annotation in brackets, followed by an optional blockquote description.

```markdown
# Solar Energy Market [market-analysis|SEM,solar]

> Utility-scale solar market trends, cost trajectories, and regional adoption patterns.
```

Entity annotation format (AR-09): `[entity_type]` or `[entity_type|alias1,alias2,...]`. Entity type uses `[a-z0-9-]+` (lowercase alphanumeric and hyphens only). Aliases are comma-separated, each `[A-Za-z0-9_-]+` (mixed case, underscores permitted).

### Sections

Claims are grouped under `##` headings. Section headings are freeform text. One or more claims MUST follow each section heading directly — no freeform prose or subheadings are permitted between the section heading and its claims.

---

## 6. Claim Syntax

Each claim is a markdown list item. A claim uses EITHER dense OR verbose form for its metadata — never both (AR-13).

### 6.1 Dense Form

```text
- [C001] Claim headline
  {confidence|type|evidence_ids|since_date|depth|nature} Optional trailing prose.
  Additional prose continues here. →C002, ⊗~C003
```

**Claim ID:** `[C` + one or more digits + optional `-v` version suffix + `]`. Bold wrapping (`**[C001]**`) is optional syntactic sugar with no semantic meaning (AR-03). Zero-padding is conventional but not required (AR-01). IDs need not be sequential (AR-12).

**Metadata block:** Curly braces with pipe-delimited positional fields:

| Position | Required | Format | Values |
|----------|----------|--------|--------|
| 1 | Yes | `0.0`–`1.0` | Confidence (normalized float) |
| 2 | Yes | single letter | `o` (observed), `r` (reported), `c` (computed), `i` (inferred) |
| 3 | Yes | comma-separated | Evidence reference IDs (`E` + digits) |
| 4 | Yes | `YYYY-MM-DD` | Date established |
| 5 | No | keyword | `assumed`, `investigated`, or `exhaustive` |
| 6 | No | keyword | `judgment`, `prediction`, or `meta` |

Positions 1–4 are REQUIRED. Positions 5–6 are OPTIONAL. Empty interior slots are valid: `{0.85|r|E020|2026-03-10||prediction}`.

**Context prose** may follow the metadata on the same line (trailing prose) or on subsequent indented continuation lines (2+ spaces, AR-11). Note: trailing prose on the metadata line is consumed greedily — relation symbols on that line are treated as prose, not parsed as relations.

**Relations** appear on subsequent continuation lines (not the metadata line) using symbol syntax:

```text
→C002, ⊗~C003
```

Relations may appear on their own line or trailing after prose (AR-04).

### 6.2 Verbose Form

```markdown
- **[C030]** Supply chain concentration
  `confidence: 0.90 | type: inferred | evidence: E001, E030 | since: 2026-03-01 | depth: exhaustive | nature: meta`
  Context prose lines.
  `relations: requires C020`
```

Metadata in a backtick-delimited line with named fields separated by `|`:

| Field | Required | Values |
|-------|----------|--------|
| `confidence:` | Yes | `0.0`–`1.0` |
| `type:` | Yes | `observed`, `reported`, `computed`, `inferred` |
| `evidence:` | Yes | comma-separated `E` + digits |
| `since:` | Yes | `YYYY-MM-DD` |
| `depth:` | No | `assumed`, `investigated`, `exhaustive` |
| `nature:` | No | `judgment`, `prediction`, `meta` |

Relations in a separate backtick-delimited line using verbose names:

```text
`relations: supports C002, contradicts:tension C003`
```

### 6.3 Complete Dense Example

```markdown
- [C001] Cost decline is structural, not cyclical — driven by manufacturing scale
  {0.95|i|E001,E002|2026-03-01|exhaustive|judgment} 10/10 analyses converged.
  Learning curve (22% cost reduction per doubling) has held for 40 years. →C002, ⊗~C003
```

### 6.4 Complete Verbose Example

```markdown
- **[C030]** Supply chain concentration in China is the highest systemic risk
  `confidence: 0.90 | type: inferred | evidence: E001, E030 | since: 2026-03-01 | depth: exhaustive | nature: meta`
  80% of polysilicon, 95% of wafers. Tariff/geopolitical disruption could
  create 12-18 month supply gaps.
  `relations: requires C020`
```

---

## 7. Claim Types

| Code | Verbose | Meaning |
|------|---------|---------|
| `o` | `observed` | Directly verified from primary source |
| `r` | `reported` | Stated by a credible source, not independently verified |
| `c` | `computed` | Output of automated analysis |
| `i` | `inferred` | Derived from other claims via reasoning |

Verbose type names MUST map to their single-letter equivalents (SC-11).

---

## 8. Confidence Model

All confidence values are **normalized floats from 0.0 to 1.0** (SC-01). PACK.yaml declares the native scale via `confidence.scale`.

### Built-In Scales

**Sherman Kent** (`sherman_kent`):

| Normalized | Label |
|------------|-------|
| 0.99+ | Certain |
| 0.93–0.99 | Almost certain |
| 0.87–0.93 | Highly likely |
| 0.75–0.87 | Likely |
| 0.63–0.75 | Probable |
| 0.37–0.63 | Chances about even |
| 0.25–0.37 | Probably not |
| 0.13–0.25 | Unlikely |
| 0.07–0.13 | Highly unlikely |
| 0.01–0.07 | Almost certainly not |
| <0.01 | Impossible |

**Simple** (`simple`):

| Normalized | Label |
|------------|-------|
| 0.90+ | Verified |
| 0.70–0.89 | High confidence |
| 0.50–0.69 | Moderate confidence |
| 0.30–0.49 | Low confidence |
| <0.30 | Unverified |

Custom scales use `confidence.scale: custom` with a `confidence.labels` mapping in PACK.yaml.

### Investigation Depth (Position 5)

| Value | Meaning |
|-------|---------|
| `assumed` | Minimal investigation, taken at face value |
| `investigated` | Multiple sources consulted and cross-referenced |
| `exhaustive` | Thorough investigation; remaining uncertainty is genuine |

When omitted, depth is unspecified.

### Claim Nature (Position 6)

| Value | Meaning |
|-------|---------|
| `judgment` | Interpretive conclusion drawn from evidence |
| `prediction` | Forward-looking claim with a resolution horizon |
| `meta` | Claim about the state of knowledge itself |

When omitted, the claim is a factual assertion (the default).

---

## 9. Relations

### Relation Symbols (Dense Form)

| Symbol | Name | Meaning |
|--------|------|---------|
| `→` | supports | Provides evidence for another claim |
| `⊗` | contradicts | Conflicts with another claim (unqualified) |
| `⊗!` | contradicts:error | One claim is wrong — prioritize resolution |
| `⊗~` | contradicts:tension | Both informative — disagreement is knowledge |
| `←` | requires | Depends on another claim being true |
| `~` | refines | Adds detail to another claim |
| `⊘` | supersedes | Replaces a prior claim |
| `↔` | see_also | Cross-reference (cross-pack: `pack_name#section`) |

Multi-character symbols MUST be matched before single-character symbols in parsing (ordered choice: `⊗~`, `⊗!`, `⊗` before `~`).

Tilde `~` is parsed as a relation ONLY when immediately followed by a valid claim ID reference — either `C` + digits (local) or a cross-pack reference (`pack_name#section`). Otherwise it is prose (AR-10).

### Verbose Relation Names

The verbose relation vocabulary is a **closed enum** (AR-05):

`supports`, `contradicts`, `contradicts:error`, `contradicts:tension`, `requires`, `refines`, `supersedes`, `see_also`

### Cross-Pack References

Format: `pack_name#section_ref` (AR-16). Pack name follows `[a-z0-9-]+`. Section ref is freeform text until the next delimiter (comma, space, newline, or end of line).

---

## 10. Evidence Document (evidence.md)

Evidence entries are referenced by ID from claims. Two formats are valid (AR-07); implementations MUST parse both.

Evidence entries begin with an H2 heading containing the evidence ID, optionally followed by `—` or `--` and a title:

```markdown
## E001
## E001 — Interview Notes
```

### Blockquote Format

Field names MUST be bold-wrapped (`**field:**`) and separated by `|`:

```markdown
## E001
> **type:** multi_source_synthesis | **captured:** 2026-03-01
> **source:** Internal analysis — 10 independent assessments

Description prose.
```

### List Format

Field names are plain (not bold), each on its own `- ` line:

```markdown
## E001 — Interview Notes
- Type: multi_source_synthesis
- Captured: 2026-03-01
- Source: Internal analysis — 10 independent assessments

Description prose.
```

### Evidence Fields

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | Source type (open vocabulary — unknown types MUST be accepted, AR-06) |
| `captured` | Yes | ISO date when evidence was obtained |
| `source` | Yes | URI, file path, or description of the source |

Optional fields: `SHA-256` / `sha-256`, `Notes` / `notes`, `Prepared` / `prepared`. Field names are case-insensitive in validation (AR-07).

Evidence IDs use the pattern `E` + one or more digits (AR-02). IDs are stable — once assigned, an ID always refers to the same source material.

---

## 11. Views (views/*.md)

Views are pre-rendered GFM (GitHub-Flavored Markdown) documents for human consumption. Views are OPTIONAL.

### Rules

1. Views contain **no knowledge that is not in claims.md**. If a view states a fact, a corresponding claim MUST exist.
2. Views are **derived** from claims. If a view disagrees with claims.md, claims.md is authoritative.
3. Each view is independently displayable — no cross-view dependencies.
4. Views SHOULD NOT contain claim notation (`{0.95|i|E001}` metadata). They contain readable prose.

### Source Traceability

Views MAY include HTML comments linking content to claims:

```markdown
<!-- source: C001, C002 -->
```

### Declaration

When views are present, they SHOULD be declared in PACK.yaml under the `views` array with `name`, `file`, `purpose`, and `display_as` fields.

---

## 12. Validation Rules

### Semantic Constraints

These constraints MUST be validated after parsing succeeds. They are not expressible in the PEG grammar and are checked as a post-parse pass.

| ID | Constraint |
|----|-----------|
| SC-01 | Confidence MUST be in range [0.0, 1.0] |
| SC-02 | All claim IDs MUST be unique within the document |
| SC-03 | All evidence references in claims MUST have corresponding entries in evidence.md |
| SC-04 | Supersession chains (`⊘`) MUST be acyclic |
| SC-05 | All claim ID targets in relations MUST exist (within pack or as valid cross-pack references) |
| SC-06 | Spec version in Rosetta header MUST equal `1` for KP:1 conformance |
| SC-07 | Frontmatter pack name MUST match PACK.yaml `name` field |
| SC-08 | Frontmatter CalVer MUST match PACK.yaml `version` field |
| SC-09 | Frontmatter domain MUST match PACK.yaml `domain` field |
| SC-10 | Frontmatter scale name MUST match PACK.yaml `confidence.scale` |
| SC-11 | Verbose type names MUST map to their single-letter equivalents: observed=o, reported=r, computed=c, inferred=i |

### Formal Grammar

The normative PEG grammar for claims.md is in `conformance/grammar/kp-claims.peg`. The normative JSON Schema for PACK.yaml is in `conformance/grammar/kp-pack.schema.json`. Implementations MUST accept all documents that match the grammar and MUST reject documents that fail to match, subject to conformance level.

---

## 13. Conformance

### Strict Level

All three checks MUST pass:

| Check | Scope | Criteria |
|-------|-------|----------|
| Syntactic | claims.md | Document matches PEG grammar |
| Semantic | claims.md + evidence.md | All constraints SC-01 through SC-11 pass |
| Schema | PACK.yaml | Validates against JSON Schema |

### Permissive Level

| Check | Scope | Criteria |
|-------|-------|----------|
| Syntactic | claims.md | Document matches PEG grammar (MUST pass) |
| Semantic (errors) | claims.md | SC-01 through SC-06 MUST pass |
| Semantic (warnings) | cross-file | SC-07 through SC-11 produce warnings, not errors |
| Schema | PACK.yaml | Required fields validate; optional field types produce warnings |

The distinction serves tooling: editors operate in permissive mode during drafting, switching to strict for publishing.

---

## 14. Constitutional Core

The following elements are **frozen across all KP spec versions** and MUST NOT change:

| Element | Specification |
|---------|--------------|
| Claim syntax | `- [ID] headline {metadata} prose` |
| Confidence range | Normalized 0.0–1.0 |
| Evidence references | `E` + digits |
| Relation symbols | `→` `⊗` `←` `~` `⊘` `↔` |
| Rosetta header | `<!-- KP:N ... -->` |

Everything outside the constitutional core MAY evolve across spec versions.

---

## Appendix A: Quick Reference

### Dense Claim Syntax

```text
- [CID] Headline
  {confidence|type|evidence|date|depth|nature} Trailing prose.
  Continuation prose. →CID, ⊗~CID
```

Positions: `{0.95|i|E001,E002|2026-03-01|exhaustive|judgment}`

### Verbose Claim Syntax

```text
- [CID] Headline
  `confidence: 0.95 | type: inferred | evidence: E001, E002 | since: 2026-03-01 | depth: exhaustive | nature: judgment`
  Prose.
  `relations: supports C002, contradicts:tension C003`
```

### Relation Symbol Table

| Dense | Verbose | Meaning |
|-------|---------|---------|
| `→` | `supports` | Provides evidence for |
| `⊗` | `contradicts` | Conflicts with (unqualified) |
| `⊗!` | `contradicts:error` | One is wrong |
| `⊗~` | `contradicts:tension` | Both informative |
| `←` | `requires` | Depends on |
| `~` | `refines` | Adds detail to |
| `⊘` | `supersedes` | Replaces |
| `↔` | `see_also` | Cross-reference |

### Confidence Scales

**Sherman Kent:** Certain (0.99+) > Almost certain (0.93) > Highly likely (0.87) > Likely (0.75) > Probable (0.63) > Even (0.37) > Probably not (0.25) > Unlikely (0.13) > Highly unlikely (0.07) > Almost certainly not (0.01) > Impossible (<0.01)

**Simple:** Verified (0.90+) > High (0.70) > Moderate (0.50) > Low (0.30) > Unverified (<0.30)

---

## Appendix B: Ambiguity Resolutions

The following normative decisions resolve ambiguities identified during grammar formalization. Full details in `conformance/grammar/README.md`.

| ID | Resolution |
|----|-----------|
| AR-01 | Claim ID is `C[0-9]+(-v[0-9]+)?`. Zero-padding conventional, not required. |
| AR-02 | Evidence ID is `E[0-9]+`. Same padding rules as claim IDs. |
| AR-03 | Bold wrapping (`**[C001]**`) is optional syntactic sugar. No semantic meaning. |
| AR-04 | Relations appear on continuation lines (2+ spaces). May trail prose or start a line. |
| AR-05 | Verbose relation names are a closed enum of 8 values. |
| AR-06 | Evidence `type` is open vocabulary. Unknown types MUST be accepted. |
| AR-07 | Both blockquote and list evidence formats are valid. Field names are case-insensitive. |
| AR-08 | Frontmatter is KP-specific compact format, NOT arbitrary YAML. |
| AR-09 | Entity annotation: `[entity_type]` or `[entity_type|alias1,alias2]` at end of H1. Entity type is `[a-z0-9-]+`; aliases are `[A-Za-z0-9_-]+`. |
| AR-10 | Tilde `~` is a relation only when immediately followed by a valid claim ID reference (`C` + digits or cross-pack ref). |
| AR-11 | Continuation lines use 2+ spaces of indentation. |
| AR-12 | Claim ID gaps are permitted. Uniqueness is the only constraint (SC-02). |
| AR-13 | A claim uses EITHER dense OR verbose metadata. No mixing within a single claim. |
| AR-14 | `signatures.yaml` and `composition.yaml` schemas deferred to Phase C2. |
| AR-15 | `tier` is optional. When `hub`, `sub_packs` is required. |
| AR-16 | Cross-pack references: `pack_name#section_ref`. `#` is the separator. |

---

## Appendix C: Companion Specifications

| Document | Covers | When you need it |
|----------|--------|-----------------|
| VOICE.md | Voice surface format and spoken delivery conventions | Building voice/audio interfaces |
| COMPOSITION.md | Meeting packs, composite packs, agenda overlays | Composing packs from multiple sources |
| LIFECYCLE.md | Ephemeral/seasonal/permanent packs, archival, reconciliation | Managing pack lifecycles |
| MULTILINGUAL.md | Locale subdirectories, translation workflow | Supporting multiple languages |
| ORGANIZATION.md | Hub/detail hierarchy, working sets, repo structure | Organizing large pack collections |
| CONSISTENCY.md | Cross-pack patrol, contradiction detection, confidence decay | Maintaining consistency across packs |
| CONVENTIONS.md | Linguistic conventions, naming style | Standardizing prose style |
| STORAGE.md | Pack-as-master, serialization, index contract | Storing packs in databases/caches |
| BUNDLE.md | Export formats, clipboard format, sharing | Exporting and sharing packs |
| DEFINITIONS.md | Definition/policy YAML schemas, codegen | Building ontology layers |
| NOTES.md | AI note-taking metadata, disclosure, consent | Recording meetings with AI |
