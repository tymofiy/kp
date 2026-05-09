# KP:1 Conformance Fixtures

> **Status:** Complete — Phase C3 (automated runner passes 19/19: 15 fixtures + 4 example packs)
> **Spec version:** KP:1 v0.8.0-preview

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
| `composition.kpack` | Structural fixture for composition packs: `composition.yaml` present, `evidence.md` omitted, prose-only `claims.md` (per SPEC.md §2) | 0 | N/A (structural) |

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
(`kp-signatures.schema.json`).

## Invalid Fixtures

Implementations MUST reject each fixture, flagging the specific violation.

| Fixture | Violation | Constraint | Severity |
|---------|-----------|------------|----------|
| `no-rosetta.kpack` | Missing `<!-- KP:1 ... -->` header | Syntactic (PEG) | MUST reject |
| `orphan-evidence-ref.kpack` | Claim references E999 not in evidence.md | SC-03 | MUST reject |
| `confidence-overflow.kpack` | Confidence value 1.50 exceeds [0.0, 1.0] | SC-01 | MUST reject |
| `duplicate-ids.kpack` | Two claims share ID [C001] | SC-02 | MUST reject |
| `missing-evidence-field.kpack` | Empty evidence ref position in metadata | Syntactic (PEG) | MUST reject |
| `cyclic-supersession.kpack` | C001 ⊘ C002 and C002 ⊘ C001 (supersession cycle) | SC-04 | MUST reject |
| `dangling-relation-target.kpack` | Claim references C999 via → but C999 does not exist | SC-05 | MUST reject |
| `wrong-pack-name.kpack` | Rosetta `pack:` value disagrees with PACK.yaml `name:` | SC-07 | MUST reject |
| `prediction-too-confident.kpack` | nature=prediction with confidence 0.97 (>0.95 cap) | SC-12 | MUST reject |

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
unique within a document. Duplicates create ambiguous relation targets.

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

**wrong-pack-name:** Semantic constraint SC-07 requires the Rosetta header's
`pack:` field to equal the PACK.yaml `name:` field. The fixture lies in
the Rosetta header (`pack: a-different-name` vs PACK.yaml
`name: wrong-pack-name`); the disagreement triggers SC-07.

**prediction-too-confident:** Semantic constraint SC-12 caps confidence on
predictive claims (nature=prediction) at 0.95. Predictions about future
states have irreducible uncertainty; the 0.99+ band is reserved for
trivially-falsifiable claims (per AUTHORING.md §5). The fixture asserts
0.97 on a future-tense prediction and is rejected.

## Running Fixtures

The automated test runner validates all fixtures:

```bash
python conformance/run.py
```

This parses each `claims.md` against `grammar/kp-claims.peg`, validates each
`PACK.yaml` against `grammar/kp-pack.schema.json`, validates each
`signatures.yaml` against `grammar/kp-signatures.schema.json` when present,
runs semantic constraint checks (SC-01 through SC-12), and verifies that all
valid fixtures pass and all invalid fixtures fail with expected errors.
Current result: **19/19 tests pass** (15 fixtures + 4 reference example packs).

To validate a single pack outside the bundled set:

```bash
python conformance/run.py --pack path/to/your-pack.kpack
```
