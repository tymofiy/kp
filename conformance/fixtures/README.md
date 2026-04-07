# KP:1 Conformance Fixtures

> **Status:** Complete — Phase C3 (automated runner passes 12/12)
> **Spec version:** KP:1

Test fixtures for KP:1 conformance validation. Each fixture is a complete
`.kpack` directory with `PACK.yaml`, `claims.md`, and `evidence.md`.

## Valid Fixtures

Implementations MUST accept all valid fixtures without errors.

| Fixture | Tests | Claims | Syntax Forms |
|---------|-------|--------|-------------|
| `minimal.kpack` | Bare minimum valid pack — only required fields | 1 | Dense (4-pos) |
| `typical.kpack` | Realistic pack with common optional fields, relations, sections | 4 | Dense (4+6 pos) |
| `verbose-claims.kpack` | All claims use verbose named-field syntax | 3 | Verbose only |
| `mixed-syntax.kpack` | Dense and verbose claims coexist in one document | 5 | Both |
| `maximal.kpack` | Every optional field, all relation types, versioned IDs, cross-pack refs | 14 | Both |

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

## Invalid Fixtures

Implementations MUST reject each fixture, flagging the specific violation.

| Fixture | Violation | Constraint | Severity |
|---------|-----------|------------|----------|
| `no-rosetta.kpack` | Missing `<!-- KP:1 ... -->` header | Syntactic (PEG) | MUST reject |
| `orphan-evidence-ref.kpack` | Claim references E999 not in evidence.md | SC-03 | MUST reject |
| `confidence-overflow.kpack` | Confidence value 1.50 exceeds [0.0, 1.0] | SC-01 | MUST reject |
| `duplicate-ids.kpack` | Two claims share ID [C001] | SC-02 | MUST reject |
| `missing-evidence-field.kpack` | Empty evidence ref position in metadata | Syntactic (PEG) | MUST reject |

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

## Running Fixtures

The automated test runner validates all fixtures:

```bash
python conformance/run.py
```

This parses each `claims.md` against `grammar/kp-claims.peg`, validates each
`PACK.yaml` against `grammar/kp-pack.schema.json`, runs semantic constraint
checks (SC-01 through SC-11), and verifies that all valid fixtures pass and all
invalid fixtures fail with expected errors. Current result: 12/12 tests pass.
