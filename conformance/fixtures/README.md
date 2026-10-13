# KP:1 Conformance Fixtures

> **Status:** Complete — Phase C3 (automated runner passes 29/29: 24 fixtures + 5 example packs)
> **Spec version:** KP:1 current editor's draft (post-v0.8.4-preview)

Test fixtures for KP:1 conformance validation. Each fixture is a complete
`.kpack` directory. Standard packs include `PACK.yaml`, `claims.md`, and
`evidence.md`; composition packs (per SPEC.md §2) include `composition.yaml`
and MAY omit `evidence.md`.

## Valid Fixtures

Implementations MUST accept all valid fixtures without errors.

| Fixture | Tests | Claims | Syntax Forms |
|---------|-------|--------|-------------|
| `minimal.kpack` | Bare minimum valid pack — only required fields | 1 | Dense (4-pos) |
| `typical.kpack` | Realistic pack with common optional fields, relations, sections | 4 | Dense (4+6 pos) |
| `verbose-claims.kpack` | All claims use verbose named-field syntax | 3 | Verbose only |
| `mixed-syntax.kpack` | Dense and verbose claims coexist in one document | 5 | Both |
| `maximal.kpack` | Every optional field, all relation types, versioned IDs, cross-pack refs; also includes a populated `signatures.yaml` exercising the v0.7.5 integrity schema | 14 | Both |
| `encoded-evidence.kpack` | Canonical `markdown-backslash-v1` example; escaped record-shaped lines do not mint sibling evidence IDs (decode round-trip has additional contract tests) | 1 | Dense (4-pos) |
| `composition.kpack` | Structural fixture for composition packs: `composition.yaml` present, `evidence.md` omitted, prose-only `claims.md` (per SPEC.md §2) | 0 | N/A (structural) |
| `lifecycle.kpack` | Two supersession generations, historical relations and a verbose retraction; shared active/history namespace | 2 active, 3 historical | Both |
| `retracted.kpack` | Last active claim withdrawn; ordinary claims document structure retained and original bullet kept in history | 0 active, 1 historical | Dense (historical) |
| `selection.kpack` | Selection schema with explicit scope and live member references; narrative context | 0 | N/A (structural) |

### Feature Coverage Matrix

| Feature | min | typ | verb | mix | max |
|---------|-----|-----|------|-----|-----|
| Dense metadata (4 positions) | x | x | | x | x |
| Dense metadata (6 positions) | | x | | x | x |
| Dense metadata (empty slot) | | | | x | x |
| Verbose metadata (all fields) | | | x | | x |
| Verbose metadata (required only) | | | x | | |
| Bold-wrapped claim ID | | | x | x | x |
| Relation: supports (→) | | x | x | | x |
| Relation: contradicts (⊗) | | | | | x |
| Relation: contradicts:tension (⊗~) | | x | | x | x |
| Relation: contradicts:error (⊗!) | | | | | x |
| Relation: requires (←) | | x | | | x |
| Relation: refines (~) | | | | | x |
| Relation: supersedes (⊘) | | | | x | x |
| Relation: see_also (↔) | | | | | x |
| Versioned claim ID (C###-v#) | | | | | x |
| Cross-pack reference | | | | | x |
| Multiple evidence refs | | x | x | | x |
| Entity annotation in H1 | | x | x | x | x |
| Multi-line description (>) | | | | | |
| CalVer with -rev suffix | | | | | x |
| Evidence: blockquote format | x | x | x | x | x |
| Evidence: list format | | | | | x |

The matrix covers claim-syntax features; `composition.kpack` is a structural
fixture (it has no claim bullets) and exercises the composition-pack
file-requirement rules from SPEC.md §2 instead. `maximal.kpack`'s
`signatures.yaml` exercises the v0.7.5 integrity schema
(`kp-signatures.schema.json`). `encoded-evidence.kpack` is the canonical CORE
§10 / AR-19 acceptance example, including source-authored leading backslashes,
bare and indented headings, and marker-shaped content. Phase C3 proves those
escaped lines do not define sibling evidence IDs; logical-body decoding is additionally exercised by the contract tests; whole-pack round-trip remains open.

## Invalid Fixtures

Implementations MUST reject each fixture, flagging the specific violation.

| Fixture | Violation | Constraint | Severity |
|---------|-----------|------------|----------|
| `no-rosetta.kpack` | Missing `<!-- KP:1 ... -->` header | Syntactic (PEG) | MUST reject |
| `orphan-evidence-ref.kpack` | Claim references E999 not in evidence.md | SC-03 | MUST reject |
| `confidence-overflow.kpack` | Confidence value 1.50 exceeds [0.0, 1.0] | SC-01 | MUST reject |
| `duplicate-ids.kpack` | Two claims share ID [C001] | SC-02 | MUST reject |
| `duplicate-evidence-ids.kpack` | Two top-level evidence records share ID E001 | SC-13 | MUST reject |
| `malformed-evidence-heading.kpack` | `## E001 appendix` lacks a normative title separator and does not define E001 | SC-03 | MUST reject |
| `missing-evidence-field.kpack` | Empty evidence ref position in metadata | Syntactic (PEG) | MUST reject |
| `cyclic-supersession.kpack` | C001 ⊘ C002 and C002 ⊘ C001 (supersession cycle) | SC-04 | MUST reject |
| `dangling-relation-target.kpack` | Claim references C999 via → but C999 does not exist | SC-05 | MUST reject |
| `wrong-pack-name.kpack` | Frontmatter `pack:` value disagrees with PACK.yaml `name:` | SC-07 | MUST reject |
| `prediction-too-confident.kpack` | nature=prediction with confidence 0.97 (>0.95 cap) | SC-12 | MUST reject |
| `verbose-prediction-too-confident.kpack` | Same SC-12 violation in verbose named-field syntax | SC-12 | MUST reject |
| `bad-format-fields.kpack` | PACK.yaml `freshness` is not a date, `spec_uri` is not a URI | Schema (format) | MUST reject |
| `bad-composition-schema.kpack` | composition.yaml `meeting.date` is not an ISO 8601 datetime | Composition schema (format) | MUST reject |

### Violation Details

**no-rosetta:** The Rosetta header is the format's self-describing bootstrap.
Without it, a file named `claims.md` cannot be identified as KP:1 content.
Syntactic failure — the document cannot be parsed at all.

**orphan-evidence-ref:** Semantic constraint SC-03 requires every evidence
reference in claims to have a corresponding entry in `evidence.md`. This
catches typos and ensures the evidence chain is complete.

**confidence-overflow:** Semantic constraint SC-01 requires confidence in
[0.0, 1.0]. The PEG grammar accepts `1.50` syntactically (it matches
`DIGIT '.' DIGIT+`) but post-parse validation must reject it.

**duplicate-ids:** Semantic constraint SC-02 requires all claim IDs to be
unique across active and historical claims within a pack. Duplicates create ambiguous relation targets.

**duplicate-evidence-ids:** Semantic constraint SC-13 requires all top-level
evidence record IDs to be unique within `evidence.md`. Duplicate serialized
identities are ambiguous to parsers and renderers even when their bodies happen
to be identical. Record-shaped source content must use the AR-19 encoding rather
than an unescaped top-level evidence heading.

**malformed-evidence-heading:** Evidence headings are full-line records, not ID
prefix searches. `## E001 appendix` lacks the normative em dash or double-hyphen
title separator, so it does not define E001 and the claim's reference fails
SC-03. This guards parsers that would otherwise accept a malformed heading by
matching only its prefix.

**missing-evidence-field:** The PEG grammar requires `EvidenceRefList` to
contain at least one `EvidenceRef`. An empty position 3 (`{0.75|i||2026}`)
fails to match `EvidenceRefList <- EvidenceRef (',' EvidenceRef)*`.

**cyclic-supersession:** Semantic constraint SC-04 requires the supersession
graph to be a directed acyclic graph (DAG). C001 ⊘ C002 ⊘ C001 forms a
2-cycle and is rejected. The runner detects cycles via DFS over the
supersession edge set after parse.

**dangling-relation-target:** Semantic constraint SC-05 requires every
intra-pack relation target to resolve to a defined claim ID in the same
pack. Cross-pack references using the `pack#section` form are exempt; this
fixture uses bare `→C999` (no `#`), so the dangling-target rule applies.

**wrong-pack-name:** Semantic constraint SC-07 requires the frontmatter's
`pack:` field (the YAML block between `---` markers at the top of `claims.md`,
distinct from the `<!-- KP:1 ... -->` Rosetta header comment that precedes it)
to equal the PACK.yaml `name:` field. The fixture lies in the frontmatter
(`pack: a-different-name` vs PACK.yaml `name: wrong-pack-name`); the
disagreement triggers SC-07.

**prediction-too-confident:** Semantic constraint SC-12 caps confidence on
predictive claims (nature=prediction) at 0.95. Predictions about future
states have irreducible uncertainty; the 0.99+ band is reserved for
trivially-falsifiable claims (per AUTHORING.md §5). The fixture asserts
0.97 on a future-tense prediction and is rejected.

**verbose-prediction-too-confident:** The same SC-12 violation expressed in
verbose named-field syntax (`` `confidence: 0.97 | … | nature: prediction` ``).
Guards the constraint on both metadata forms — a validator that only checks
the dense position-6 slot would miss it.

**bad-format-fields:** PACK.yaml declares `freshness: "2026-13-45"` (month 13)
and `spec_uri: "not a uri"`. Both violate JSON Schema `format` assertions; the
claims document itself is fully valid, so a validator that skips format
checking wrongly accepts the pack.

**bad-composition-schema:** A composition pack whose `composition.yaml` sets
`meeting.date: next tuesday` — every other field is valid, so the only
violation is the `date-time` format assertion. Catches validators that do not
check `composition.yaml` against `kp-composition.schema.json` at all, and
validators without format enforcement. Note the dependency sensitivity: the
`date-time` validator ships in jsonschema's `format-nongpl` extra (pinned in
`requirements.txt`); with bare `jsonschema`, this violation goes undetected
while `bad-format-fields`' date violation is still caught (the `date` checker
is stdlib-backed).

## Running Fixtures

The automated test runner validates all fixtures:

```bash
python conformance/run.py
```

This validates each `claims.md` with diagnostic regex parsing of
`grammar/kp-claims.peg` (the PEG file is the normative reference; see
`../README.md` "Grammar vs Runner"), validates each `PACK.yaml` against
`grammar/kp-pack.schema.json`, validates each `signatures.yaml` against
`grammar/kp-signatures.schema.json` when present, runs semantic constraint
checks (SC-01 through SC-13), and verifies that all valid fixtures pass and
all invalid fixtures fail with expected errors.
Current result: **29/29 tests pass** (24 fixtures + 5 reference example packs).

To validate a single pack outside the bundled set:

```bash
python conformance/run.py --pack path/to/your-pack.kpack
```
