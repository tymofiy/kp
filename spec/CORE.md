<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# KP:1 Core Specification

> **Status:** Released Editor's Draft — v0.8.5-preview
> **Latest citable release:** `KP:1 — Knowledge Pack Format Specification` (`v0.8.5-preview`, 2026-10-13)
> **Editor:** Timothy Kompanchenko
> **Draft updated:** 2026-10-12
> **Derived from:** SPEC.md, `conformance/grammar/kp-claims.peg`, `conformance/grammar/kp-pack.schema.json`
> **Lane:** Implementer surface — see [README.md](README.md) for the three-lane structure (CORE = implementer, SPEC = full normative + rationale, companions = topic-authoritative for their domains).

> **If you are authoring a pack** (rather than implementing a parser/validator), read [`AUTHORING.md`](AUTHORING.md) first. CORE.md tells you what a syntactically valid pack looks like; AUTHORING.md tells you how to make epistemically sound choices when authoring one.

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

This document does **not** cover: producer-side decision rubrics ([AUTHORING.md](AUTHORING.md)), design-principles rationale and standards-comparison ([RATIONALE.md](RATIONALE.md)), voice surfaces ([VOICE.md](VOICE.md)), composition/meetings ([COMPOSITION.md](COMPOSITION.md)), lifecycle management ([LIFECYCLE.md](LIFECYCLE.md)), multilingual support ([MULTILINGUAL.md](MULTILINGUAL.md)), pack organization patterns ([ORGANIZATION.md](ORGANIZATION.md)), consistency patrol ([CONSISTENCY.md](CONSISTENCY.md)), naming conventions ([CONVENTIONS.md](CONVENTIONS.md)), storage formats ([STORAGE.md](STORAGE.md)), bundling ([BUNDLE.md](BUNDLE.md)), archive format and integrity ([ARCHIVE.md](ARCHIVE.md)), definition/policy document kinds ([DEFINITIONS.md](DEFINITIONS.md)), AI note-taking ([NOTES.md](NOTES.md)), the producer-defined `extensions.*` catalogue ([EXTENSIONS.md](EXTENSIONS.md)), self-driving voice playback ([PLAYBACK.md](PLAYBACK.md), experimental), cross-pack reconciliation ([RECONCILIATION.md](RECONCILIATION.md), stub), or RDF/JSON-LD/PROV-O mapping ([MAPPING.md](MAPPING.md), informative). These are specified in companion documents within `spec/`. Cold AI agents should start from [`AGENTS.md`](../AGENTS.md) at the repo root for a task-indexed reading map.

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
├── entities.md        # DEPRECATED (since v0.7.7) — use extensions.entities; see EXTENSIONS.md
├── validation.yaml    # OPTIONAL — test questions (schema in SPEC.md §10)
├── signatures.yaml    # OPTIONAL — cryptographic integrity (see ARCHIVE.md)
└── views/             # OPTIONAL — pre-rendered display content
    └── overview.md
```

File requirements depend on the manifest's `kind` (default `claim`):

| Kind | Required files | Additional content |
|------|----------------|--------------------|
| `claim` | `PACK.yaml`, `claims.md` | Evidence for every cited evidence ID |
| `definition` | `PACK.yaml`, at least one `definitions/*.yaml` | Optional claims, evidence and views |
| `policy` | `PACK.yaml`, at least one `policies/*.yaml` | Optional claims, evidence and views |
| `mixed` | `PACK.yaml`, `claims.md`, at least one definition or policy document | Evidence for every cited evidence ID |

Definition and policy document formats are defined in [DEFINITIONS.md](DEFINITIONS.md). They do not require probabilistic claims merely to represent deterministic rules. Whenever `claims.md` is present, its ordinary header, frontmatter and claim rules apply. `evidence.md` is optional as a file, but SC-03 still requires every active or historical evidence reference to resolve.

> **Composition-pack exception.** The presence of `composition.yaml` requires `claims.md` and validation of the composition schema. The claims document MAY be narrative-only, retaining the Rosetta header and compact frontmatter. A composition MAY omit `evidence.md` when it has no evidence references. See [COMPOSITION.md](COMPOSITION.md). This exception does not relax metadata or reference rules for any claim bullets it does contain.

The default file names above are the interoperable directory surface. The schema's optional `files` object is reserved for application mappings; schema acceptance alone does not define override behavior. Producers targeting the generic reader MUST retain the canonical files. A profile that uses alternate carriers must define its mapping and declare the required reader capability.

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
| `spec_uri` | URL | Onboarding pointer to the KP:1 specification this pack conforms to. Informational, not a runtime parse dependency. Default published location: `https://github.com/tymofiy/kp`. See "Spec Onboarding Pointer" below. |
| `spec_version` | string | Version label of the KP:1 spec this pack conforms to (typically a tag, e.g., `v0.8.5-preview`). Pairs with `spec_uri` to pin against a specific revision. |
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
| `extensions` | object | Extension lane for experimental or implementation-specific manifest metadata. Consumers ignore unknown extension content. |
| `composition` | string | Optional declaration of the canonical `composition.yaml` file; if declared, that file MUST exist. Alternate filenames are not generic CORE carriers. See [COMPOSITION.md](COMPOSITION.md). |
| `files` | object | Application filename mappings; the generic reader retains canonical filenames (see §2). |

The full set of optional fields and conditional constraints is defined in the JSON Schema. Key conditionals: when `tier` is `hub`, `sub_packs` is REQUIRED; when `sensitivity` is `confidential` or `restricted`, `channels` MUST NOT contain `public` or `org`; when `sensitivity` is `internal`, `channels` MUST NOT contain `public`; when a view declares `voice: true`, `duration` and `pace` are REQUIRED on that view entry.

**Decoration fields** (`linguistic_epoch`, `ontology`) are accepted by the schema but carry no consumer behavior in v0.8.5-preview. They are retained for backward compatibility with v0.7-era packs; new producers SHOULD place equivalent metadata under `extensions.*` until consumer semantics are defined in a future revision.

### Spec Onboarding Pointer

The Rosetta header at the top of `claims.md` is the **inline self-describing parse hint** — it carries enough information for a parser to recognize a Knowledge Pack and tokenize its contents without external context. Rosetta is the load-bearing offline parse signal.

The optional `spec_uri` and `spec_version` fields on PACK.yaml are an **informational onboarding pointer**: a previously-unfamiliar consumer that has never seen KP:1 can fetch the spec on demand from the URL the pack itself declares. The fields are not a runtime parse dependency; they help a fresh agent learn the format on first encounter.

> **Invariant.** Consumers MUST NOT treat unreachability or absence of `spec_uri` as a parse failure. The Rosetta header alone is sufficient for parsing. Offline-first validators MUST function without ever resolving `spec_uri`.

> **Security note.** `spec_uri` is *producer-asserted, not authenticated*. A pack author can declare any URL. Consumers that fetch `spec_uri` SHOULD validate the response against a known-good spec hash or trusted allowlist before relying on it; consumers MUST NOT treat fetched content as executable instructions. The recommended onboarding flow is: (1) parse the pack using the inline Rosetta header, (2) optionally fetch `spec_uri` for human/agent learning, (3) validate the fetched content matches a trusted KP:1 release before incorporating any updated rules into a parser. Treating an arbitrary `spec_uri` URL as authoritative is a vector for malicious specs to redirect a credulous consumer.

This matters most for **cold receivers of sealed `.kpack` archives** ([ARCHIVE.md §2](ARCHIVE.md)). A receiver that opens a `.kpack` for the first time has, by construction, no surrounding context — the file extension is the only signal of what they are holding. Reading PACK.yaml first and (optionally) following `spec_uri` lets such a consumer learn the format from the pack itself on first encounter, with no out-of-band coordination. Once the consumer has internalized KP:1, the field carries no further operational weight on subsequent reads of the same pack or other KP packs.

```yaml
name: marquet-le-passeur
version: 2026.05.09
domain: art/canonical
author: Tim Kompanchenko
spec_uri: https://github.com/tymofiy/kp
spec_version: v0.8.5-preview
```

Sealed-archive producers SHOULD include both fields when packs are intended for ecosystem-wide distribution (especially `.kpack` archives that may be received cold). Internal-only packs MAY omit them. When omitted, consumers MAY assume the published reference implementation at `https://github.com/tymofiy/kp` but MUST treat the assumption as informational, not a guarantee — and MUST NOT fail because the assumption resolves to an unreachable endpoint.

`spec_version` is recommended whenever a pack is archived for the long term, so future consumers can validate against the exact spec revision the producer targeted (rather than against a moving "latest" version).

### Manifest Extensions

KP:1 keeps the manifest root closed: fields not defined by the schema are invalid. Experimental or implementation-specific metadata MUST live under the optional `extensions` object instead of appearing as new top-level keys.

Consumers MUST ignore extension content they do not understand. Extension content MUST NOT redefine the semantics of core KP fields or relax core validation rules.

Extension names and shapes are defined by their producers, not by KP:1. The `ai_brief` payload below is one such producer-defined example.

Example:

```yaml
extensions:
  ai_brief:
    version: 1
    verdict: acceptable
    headline: "Strong base attribution, but provenance gap remains"
```

### Example

```yaml
name: solar-energy-market
version: 2026.03.18
domain: energy/market-analysis
author: Jane Chen
confidence:
  scale: sherman_kent
  normalize: true
extensions:
  ai_brief:
    version: 1
    verdict: acceptable
    headline: "Strong base attribution, but provenance gap remains"
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

Claims are grouped under `##` headings. Section headings are freeform text. A section MAY open with a blockquote description before its claims, mirroring the document-level description (AR-17). A claims document MUST retain at least one section, but a section MAY contain zero claims. This represents an empty current state, including withdrawal of the final active claim with its original record retained in history, without inventing a replacement assertion. Apart from the optional blockquote and blank lines, no freeform prose or subheadings are permitted between a section heading and its claims.

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

**One identifier per claim.** A claim's `[C…]` id is both its reference target (for relations and evidence cross-references) and its human-readable label — there is no second, separate id in the file form (see *Single claim identity (normative)* below for the normative rule). Any globally-unique `claim_id` an operational index keeps is assigned by the indexing process, not the pack author, and is never serialized into `claims.md` (see [STORAGE.md](STORAGE.md)). Rationale: `decisions/2026-06-22-claim-identity.md`.

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

**Single claim identity (normative).** The bracket id (`[C001]`) is a claim's sole serialized identity — relations, history entries, and cross-pack references (AR-16) all resolve to it. The dense metadata block carries EXACTLY the positional fields defined above and no others: a producer MUST NOT append fields beyond position 6, and a conforming reader MUST treat any non-empty token past them as a malformed claim (rejecting it) rather than silently discarding it. An opaque or storage-layer identifier a system keeps for a claim (e.g. a database key) is non-wire — it is never emitted into, nor reconstructed from, the serialized claim; preserve it out-of-band if it must survive a round-trip. Storage-layer identity is a non-normative concern (see [STORAGE.md](STORAGE.md)).

**Context prose** may follow the metadata on the same line (trailing prose) or on subsequent indented continuation lines (2+ spaces, AR-11).

**Relations** MAY appear on the metadata line after the closing `}` (separated from it by a space) — either starting the trailing text or following the context prose — and/or on subsequent continuation lines. In every position, relations form a comma-separated list that ends the line, and a relation symbol is parsed as a relation only when immediately followed by a valid claim-ID reference (`C` + digits or a cross-pack reference, per AR-10); other occurrences are prose. Relations use symbol syntax:

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

Required fields MUST occur exactly once; optional fields MUST occur at most once. Field order is not significant. Unknown fields and duplicate fields MUST be rejected, rather than interpreted by first-value or last-value precedence.

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

The numeric confidence is authoritative. These label tables are illustrative display bands, not a deterministic interval-selection algorithm: shared endpoints and values between printed two-decimal bands have no universal label assignment. A profile requiring consistent labels MUST declare its thresholds and endpoint policy; labels never replace the stored number.

Confidence records the producer's assessment. Decimal precision and labels such as "Verified" do not establish that a verification procedure occurred or that the values are empirically calibrated. Explaining the evidential basis and method helps consumers assess what the value represents; see [AUTHORING.md §5](AUTHORING.md#5-confidence-calibration). This clarification does not change the wire value or scale rules.

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

Optional fields:

- `reliability` — NATO Admiralty source reliability tier. Single uppercase letter `A`–`F`. `A` = completely reliable, `F` = reliability cannot be judged.
- `credibility` — NATO Admiralty information credibility for this specific fact. Single digit `1`–`6`. `1` = confirmed by other independent sources, `6` = credibility cannot be judged. Orthogonal to `reliability`: an `A`-tier source can carry a `6`-credibility statement when uncorroborated.
- `kp-content-encoding` — registered reversible encoding for record-shaped Markdown in an evidence body. The only KP:1 value is `markdown-backslash-v1`; see “Record-safe encoded bodies” below.
- `SHA-256` / `sha-256`, `Notes` / `notes`, `Prepared` / `prepared`.

Required evidence fields MUST be nonempty and occur exactly once. Other metadata fields MUST NOT repeat. Each field value occupies one physical line; indented or folded metadata continuations are not defined. `captured` MUST be a valid calendar date in `YYYY-MM-DD` form. The initial metadata block is separated from body content by one blank line; additional blank lines belong to the body. Once body content begins, field-shaped source quotations are body text, not metadata.

Field names are case-insensitive in validation (AR-07), including `kp-content-encoding`; its encoding value is case-sensitive. The combined `reliability` + `credibility` pair (e.g. `A1`, `B2`, `F6`) is the standard intelligence-tradecraft Admiralty grade and renderers MAY surface it as such.

Evidence IDs use the pattern `E` + one or more digits (AR-02). IDs are stable — once assigned, an ID always refers to the same source material.

### Record-Safe Encoded Bodies

An evidence excerpt can contain Markdown that looks like KP structure — for example, a source-local
`## E001` heading or `- [E001]` bullet. Emitting those lines verbatim makes record boundaries
ambiguous. A producer MAY make the body reversible and record-safe by placing this exact blockquote
metadata line after the ordinary evidence fields and immediately before the body:

```markdown
> **kp-content-encoding:** markdown-backslash-v1
```

Producers MUST use the canonical lowercase field spelling shown above. Consumers match the field
name case-insensitively per AR-07, but MUST compare `markdown-backslash-v1` case-sensitively.

For `markdown-backslash-v1`, the producer MUST preserve leading spaces and tabs, then prefix one
backslash after that indentation when the remaining logical body line:

1. begins with a backslash;
2. equals the encoding marker line above;
3. is exactly `##`, or begins with `##` followed by whitespace; or
4. begins with `-`, then one or more whitespace characters, then `[E` + one or more digits + `]`,
   followed by whitespace or end of line.

All other body lines remain byte-for-byte unchanged. Escaping an existing leading backslash makes
the transform reversible rather than treating source-authored escapes as encoder output.

Consumers MUST segment evidence records on the encoded text before decoding. Any unescaped,
top-level H2 terminates the current evidence record; only a conforming `## E` + digits heading begins
another evidence record. Escaped headings and evidence-shaped bullets remain body content. A
consumer that exposes the logical body MUST remove exactly one post-indentation backslash when the
remainder matches one of the four encoder cases above, and MUST leave every other leading backslash
intact. The marker is metadata, not user-facing body content.

An implementation that does not recognize the declared value MUST preserve the encoded body as-is,
MUST NOT reinterpret escaped lines as structural records, and SHOULD warn that logical-body decoding
was skipped. Producers SHOULD NOT emit unregistered `kp-content-encoding` values (AR-19).

---

## 11. Views (views/*.md)

Views are pre-rendered GFM (GitHub-Flavored Markdown) documents for human consumption. Views are OPTIONAL.

### Rules

1. Views introduce no knowledge absent from the canonical primary files for the pack's kind. In a claim-bearing pack, a corresponding claim SHOULD exist for each stated fact. Definition and policy views derive from their canonical definition/policy documents and any claims present. This is editorial discipline — the conformance runner does not detect unsupported view assertions. Authors are responsible; see [AUTHORING.md §11](AUTHORING.md) anti-pattern #4.
2. Views are **derived**; the canonical primary files are authoritative when a view disagrees. A composition may navigate to member sources. Combined member-content rendering requires the source and revision contract described in [COMPOSITION.md](COMPOSITION.md); a local view alone does not supply it.
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
| SC-02 | All claim IDs MUST be unique across claims.md and history.md within a pack |
| SC-03 | All evidence references in active and historical claims MUST have corresponding entries in evidence.md |
| SC-04 | Supersession chains (`⊘`) MUST be acyclic |
| SC-05 | All claim ID targets in relations MUST exist (within active/history records or as valid cross-pack references) |
| SC-06 | Spec version in Rosetta header MUST equal `1` for KP:1 conformance |
| SC-07 | Frontmatter pack name MUST match PACK.yaml `name` field |
| SC-08 | Frontmatter CalVer MUST match PACK.yaml `version` field |
| SC-09 | Frontmatter domain MUST match PACK.yaml `domain` field |
| SC-10 | Frontmatter scale name MUST match PACK.yaml `confidence.scale` |
| SC-11 | Verbose type names MUST map to their single-letter equivalents: observed=o, reported=r, computed=c, inferred=i |
| SC-12 | When `nature` is `prediction`, confidence MUST be ≤ 0.95. Predictions about future states have irreducible uncertainty; the 0.99+ band is reserved for trivially-falsifiable claims per [AUTHORING.md §5](AUTHORING.md). |
| SC-13 | All evidence IDs MUST be unique within evidence.md. Duplicate serialized identities are ambiguous even when their bodies are identical. |

### Historical claim records

`history.md` retains each superseded or retracted claim's original bullet, metadata, prose and outgoing relations. Editorial headings identify the transition date, reason and successor (if any); they are not replacement claim identities. Historical claim bullets use the same dense or verbose syntax as active claims, without a second claims-document frontmatter. Local relation targets resolve across the union of active and historical claims. Supersession acyclicity is checked over that union, including multiple generations. Retraction does not imply a successor, and unresolved disputes remain active. See [SPEC.md §9](SPEC.md#9-claim-lifecycle) and the [lifecycle fixture](../conformance/fixtures/valid/lifecycle.kpack/history.md).

### Formal Grammar

The normative PEG grammar for claims.md is in `conformance/grammar/kp-claims.peg`. The normative JSON Schema for PACK.yaml is in `conformance/grammar/kp-pack.schema.json`. Implementations MUST accept all documents that match the grammar and MUST reject documents that fail to match, subject to conformance level.

---

## 13. Conformance

### Strict Level

All three checks MUST pass:

| Check | Scope | Criteria |
|-------|-------|----------|
| Syntactic | claims.md | Document matches PEG grammar |
| Semantic | claims.md + evidence.md | All constraints SC-01 through SC-13 pass |
| Schema | PACK.yaml | Validates against JSON Schema |

### Permissive Level

| Check | Scope | Criteria |
|-------|-------|----------|
| Syntactic | claims.md | Document matches PEG grammar (MUST pass) |
| Semantic (errors) | claims.md + evidence.md | SC-01 through SC-06 and SC-13 MUST pass |
| Semantic (warnings) | cross-file | SC-07 through SC-12 produce warnings, not errors |
| Schema | PACK.yaml | Required fields validate; optional field types produce warnings |

These are normative conformance levels. The reference runner currently reports SC-07 through SC-12 as errors in both CLI modes; `--strict` adds PEG syntax checks and is not the normative strict/permissive switch. See [the capability guide](COMPATIBILITY.md).

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
| AR-04 | Relations MAY appear on the metadata line after the closing `}` (separated by a space; starting the trailing text or following the context prose), and/or on subsequent continuation lines (2+ spaces). Relations form a comma-separated list ending the line. A relation symbol is parsed as a relation only when immediately followed by a valid claim-ID reference (per AR-10); other occurrences are prose. |
| AR-05 | Verbose relation names are a closed enum of 8 values. |
| AR-06 | Evidence `type` is open vocabulary. Unknown types MUST be accepted. |
| AR-07 | Both blockquote and list evidence formats are valid. Field names are case-insensitive. |
| AR-08 | Frontmatter is KP-specific compact format, NOT arbitrary YAML. |
| AR-09 | Entity annotation: `[entity_type]` or `[entity_type|alias1,alias2]` at end of H1. Entity type is `[a-z0-9-]+`; aliases are `[A-Za-z0-9_-]+`. |
| AR-10 | Tilde `~` is a relation only when immediately followed by a valid claim ID reference (`C` + digits or cross-pack ref). Examples: `~C002` is the *refines* relation; `~refines` (the legend token in the Rosetta header) and `~the manuscript` (mid-prose tilde) are prose, not relations. |
| AR-11 | Continuation lines use 2+ spaces of indentation. |
| AR-12 | Claim ID gaps are permitted. Uniqueness is the only constraint (SC-02). |
| AR-13 | A claim uses EITHER dense OR verbose metadata. No mixing within a single claim. |
| AR-14 | `signatures.yaml` schema defined in ARCHIVE.md. `composition.yaml` schema is published at `conformance/grammar/kp-composition.schema.json` (normative for supported composition types); the conformance runner detects composition packs by `composition.yaml` presence (per [SPEC.md §2](SPEC.md), [COMPOSITION.md](COMPOSITION.md)) and validates `composition.yaml` against the published schema when the file is present. |
| AR-15 | `tier` is optional. When `hub`, `sub_packs` is required. |
| AR-16 | Cross-pack references: `pack_name#section_ref`. `#` is the separator. |
| AR-17 | Blank lines are permitted between structural elements (frontmatter, headings, descriptions, sections, claims). A section MAY open with a blockquote description, mirroring the document heading. Whitespace-only lines are not blank lines. |
| AR-18 | The bracket id is a claim's sole serialized identity; relations, history, and cross-pack references (AR-16) resolve to it. A claim's metadata block (dense §6.1 or verbose §6.2) carries exactly its defined fields — producers MUST NOT add fields beyond them, and readers MUST reject a non-empty undefined/trailing token rather than silently dropping it. Opaque or storage-layer identifiers are non-wire (storage is non-normative; see STORAGE.md). |
| AR-19 | Evidence bodies that contain record-shaped Markdown use the exact `kp-content-encoding: markdown-backslash-v1` marker and reversible escape algorithm in §10. Record segmentation precedes decoding; an unescaped top-level H2 ends the current record; unknown encodings are preserved, never guessed. |

---

## Appendix C: Companion Specifications

| Document | Covers | When you need it |
|----------|--------|-----------------|
| AUTHORING.md | Producer-side decision rubrics — claim type, nature, contradiction qualifier, confidence calibration, granularity, content routing | Authoring a pack from source material (informative) |
| VOICE.md | Voice surface format, spoken delivery conventions, register axis | Building voice/audio interfaces |
| COMPOSITION.md | Meeting packs, composite packs, agenda overlays, `composition.yaml` | Composing packs from multiple sources |
| LIFECYCLE.md | Ephemeral/seasonal/permanent packs, archival, supersession cascade, reconciliation | Managing pack lifecycles |
| MULTILINGUAL.md | Locale subdirectories, translation workflow, register sub-distinctions, evidentiary multilingual exception | Supporting multiple languages |
| ORGANIZATION.md | Hub/detail hierarchy, working sets, repo structure | Organizing large pack collections |
| CONSISTENCY.md | Cross-pack patrol, contradiction detection, confidence decay | Maintaining consistency across packs |
| CONVENTIONS.md | Linguistic conventions, naming style | Standardizing prose style |
| STORAGE.md | Pack-as-master, serialization, index contract | Storing packs in databases/caches |
| BUNDLE.md | Export formats, clipboard format, sharing | Exporting and sharing packs |
| ARCHIVE.md | ZIP archive, content hashing, integrity chain, signatures.yaml | Transporting packs between systems |
| DEFINITIONS.md | Definition/policy YAML schemas, entity types, codegen | Building ontology layers |
| EXTENSIONS.md | Producer-defined `extensions.*` blocks catalogue, canonical entity ID format | Adding `extensions.*` payloads or interpreting them |
| NOTES.md | AI note-taking metadata, disclosure, consent | Recording meetings with AI |
| PLAYBACK.md | Self-driving voice playback, PlaybackPlan, AudienceProfile (experimental) | Building voice presentation runtimes |
| RECONCILIATION.md | Cross-pack reconciliation protocol (stub — design deferred to v0.9 / v1.0) | Multi-pack drift detection (design pending) |
| MAPPING.md | RDF / JSON-LD / PROV-O / Nanopublications field-by-field translation (informative) | Interoperability with semantic-web standards |
| RATIONALE.md | Design principles, style systems rationale, cognitive perception rationale, relationship to existing standards (informative) | Understanding *why* the format is shaped the way it is |
| INDEPENDENCE.md | Ownership & capture-resistance guarantees — zero-dependency readability, freedom to fork, no required registry, optional cryptography | Understanding the independence commitments and their limits |
