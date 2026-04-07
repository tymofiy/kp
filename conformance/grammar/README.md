<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# KP:1 Formal Grammar

> **Status:** Draft — Phase C2
> **Spec version:** KP:1

This directory contains the normative grammar and schema for KP:1.

| File | Scope | Format |
|------|-------|--------|
| `kp-claims.peg` | `claims.md` document structure | PEG (Bryan Ford notation) |
| `kp-pack.schema.json` | `PACK.yaml` manifest | JSON Schema 2020-12 |
| `kp-composition.schema.json` | `composition.yaml` composite pack structure | JSON Schema 2020-12 |
| `kp-signatures.schema.json` | `signatures.yaml` integrity manifest | JSON Schema 2020-12 |

## Architecture

The grammar is split into two layers:

1. **Syntactic** (PEG) — can the document be parsed?
2. **Semantic** (post-parse constraints SC-01 through SC-11) — is the parsed document valid?

This split is intentional. PEG grammars cannot express cross-reference checks,
range constraints on parsed values, or acyclicity. Those are listed as semantic
constraints at the bottom of the PEG file and tested via the conformance fixtures.

## Ambiguity Resolutions

The following ambiguities were identified during grammar formalization. Each is
resolved here as a **normative decision** for KP:1.

### AR-01: Claim ID format

**Ambiguity:** Examples show `C001`, `C010`, `C030`, `C011-v2` — padding and
version suffix conventions unclear.

**Resolution:** Claim ID is `C` followed by one or more digits, with optional
`-v` version suffix: `C[0-9]+(-v[0-9]+)?`. Zero-padding is conventional but not
required. `C1` and `C001` are both valid but refer to different claims if both
appear in the same file.

### AR-02: Evidence ID format

**Ambiguity:** Pattern `E[0-9]+` is consistent across examples but not declared.

**Resolution:** Evidence ID is `E` followed by one or more digits. Same padding
rules as claim IDs.

### AR-03: Bold claim IDs

**Ambiguity:** Both examples use `**[C030]**` for verbose-syntax claims.

**Resolution:** Bold wrapping is **optional syntactic sugar**. Tooling MUST
accept both `[C001]` and `**[C001]**`. Bold has no semantic meaning — it does
not indicate verbose syntax or emphasis.

### AR-04: Relation symbol placement

**Ambiguity:** Relations appear "after prose" but exact line rules unspecified.

**Resolution:** Relations appear on **continuation lines** (indented 2+ spaces).
They may be:
- On the same line as context prose (trailing): `...the question. ⊗~C001`
- On a dedicated line starting with a relation symbol: `→C002, ⊗~C003`
- Mixed with prose on multi-line continuations

A relation symbol at a word boundary on a continuation line is parsed as a
relation, not prose. The Unicode symbols are unambiguous enough to serve as
implicit delimiters.

### AR-05: Verbose syntax delimiters

**Ambiguity:** Verbose form uses `|` as separator and `:` within relation
qualifiers (e.g., `contradicts:tension: C003`).

**Resolution:** In verbose metadata, `|` separates top-level fields. Within the
`relations:` field, relation names may contain one colon (qualifier separator)
but the field value after `relations:` SP is parsed as a relation list. The
full set of verbose relation names is a closed enum: `supports`, `contradicts`,
`contradicts:error`, `contradicts:tension`, `requires`, `refines`, `supersedes`,
`see_also`.

### AR-06: Evidence type vocabulary

**Ambiguity:** Multiple example types shown but no closed enum declared.

**Resolution:** Evidence `type` is an **open vocabulary**. The grammar validates
structure (field exists, is a string) but does not constrain the value. The spec
lists recommended types but implementations MUST accept unknown types.

### AR-07: Evidence file format variants

**Ambiguity:** Solar example uses blockquote format; assessment uses list format.

**Resolution:** **Both formats are valid.** The grammar accepts:
- Blockquote: `> **type:** value | **captured:** value`
- List: `- Type: value`

Field names are case-insensitive in validation (e.g., `type` and `Type` both
valid). Implementations MUST parse both formats.

### AR-08: Frontmatter format

**Ambiguity:** The pipe-delimited format is not standard YAML.

**Resolution:** The frontmatter between `---` fences is a **KP-specific compact
format**, not arbitrary YAML. It has exactly two lines with fixed field order.
This is a deliberate design choice: the frontmatter serves as both human-readable
header and machine-parseable metadata in ~50 tokens. Parsers MUST NOT attempt
to parse it as standard YAML.

### AR-09: H1 entity annotation

**Ambiguity:** `# Title [entity_type|aliases]` mini-syntax shown by example only.

**Resolution:** Entity annotation is optional, appears at end of H1. Format:
`[entity_type]` or `[entity_type|alias1,alias2,...]`. Entity type is required
within brackets; aliases are comma-separated, optional. Entity type uses
`[a-z0-9-]+` (lowercase, no underscores); aliases use `[A-Za-z0-9_-]+`
(mixed case, underscores allowed). This distinction allows entity types to
be machine-normalized while aliases preserve human conventions (e.g., `SEM`).

### AR-10: Context prose boundaries

**Ambiguity:** No explicit delimiter between prose and relation symbols.

**Resolution:** The 8 relation symbols (→ ⊗ ⊗! ⊗~ ← ~ ⊘ ↔) are unambiguous
Unicode codepoints that do not appear in natural prose. A relation symbol
followed immediately by a claim ID reference (`C[0-9]+`) is a relation, not
prose. The tilde `~` is the only ambiguous case — it is parsed as a relation
only when immediately followed by `C` and digits.

### AR-11: Continuation line indentation

**Ambiguity:** 2-space indent shown by example, not declared as rule.

**Resolution:** Continuation lines use **2 or more spaces** of indentation.
This matches standard Markdown list continuation. Implementations MUST accept
2+ spaces; implementations SHOULD produce exactly 2 spaces.

### AR-12: Claim ID gaps

**Ambiguity:** Non-sequential IDs (C001, C010, C030) appear in examples.

**Resolution:** **Gaps are permitted.** IDs need not be sequential. Section-
aligned numbering (C001-C009 for section 1, C010-C019 for section 2) is a
recommended convention but not enforced. The only hard constraint is uniqueness
within the document (SC-02).

### AR-13: Mixed syntax within a single claim

**Ambiguity:** Can one claim use dense metadata with verbose relations?

**Resolution:** **No.** A single claim uses either dense or verbose for its
metadata block. However, relations are independently formatted:
- Dense claims: relations use symbol syntax (→, ⊗, etc.)
- Verbose claims: relations use `\`relations: ...\`` syntax

A claim MUST NOT have both `{...}` dense metadata and `` `confidence: ...` ``
verbose metadata. This simplifies parsing and avoids precedence ambiguity.

### AR-14: Signatures and composition schemas

**Ambiguity:** `signatures.yaml` and `composition.yaml` schemas undefined.

**Resolution (C1):** Deferred to Phase C2.

**Resolution (C2 — resolved):** Schemas now formalized:
- `kp-composition.schema.json` — validates `composition.yaml` with type-conditional
  fields (`meeting-prep`, `briefing`, `research`, `presentation`), shared `pre_load`/`on_demand`
  loading lists, and per-type metadata and content structures derived from COMPOSITION.md.
- `kp-signatures.schema.json` — validates `signatures.yaml` with required hash algorithm
  and per-file digest map, optional signing key and signature with conditional enforcement
  (signature present requires signing_key and signed_at).

### AR-15: Tier field normative status

**Ambiguity:** `tier` used in examples but not in the required/optional table.

**Resolution:** `tier` is an **optional field** with enum values `hub`,
`detail`, `standalone`. When `tier: hub`, the `sub_packs` field is required
(enforced in JSON Schema via conditional).

### AR-16: Cross-pack relation references

**Ambiguity:** `↔pack_name#section` format shown in spec but not formalized.

**Resolution:** Cross-pack references in the `↔` (see_also) relation use the
format `pack_name#section_ref`. The `#` is the separator. Pack name follows
the same `[a-z0-9-]+` pattern as PACK.yaml names. Section ref is freeform
text until the next delimiter (comma, newline, or end of line).

## Conformance Levels

**Strict** (MUST pass all):
- Syntactic: document matches PEG grammar
- Semantic: all SC-01 through SC-11 constraints pass
- Schema: PACK.yaml validates against JSON Schema

**Permissive** (MUST pass syntactic, MAY warn on semantic):
- Syntactic: document matches PEG grammar
- Semantic: SC-01 through SC-06 are errors; SC-07 through SC-11 are warnings
- Schema: PACK.yaml required fields validate; optional field types warn

The distinction matters for tooling: an editor can operate in permissive mode
during drafting, switching to strict for publishing.
