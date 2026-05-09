<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# KP:1 Conformance Suite

> **Status:** Draft — Phase C3 complete
> **Spec version:** KP:1

Formal grammar, validation schema, and test fixtures for KP:1 conformance.

## Contents

```text
conformance/
  grammar/
    README.md                  Ambiguity resolutions & conformance levels
    kp-claims.peg              PEG grammar for claims.md
    kp-pack.schema.json        JSON Schema for PACK.yaml
    kp-composition.schema.json JSON Schema for composition.yaml
    kp-signatures.schema.json  JSON Schema for signatures.yaml
  fixtures/
    README.md                  Fixture catalog & coverage matrix
    valid/                     6 packs that MUST be accepted
      minimal.kpack/
      typical.kpack/
      verbose-claims.kpack/
      mixed-syntax.kpack/
      maximal.kpack/
      composition.kpack/
    invalid/                   9 packs that MUST be rejected
      no-rosetta.kpack/
      orphan-evidence-ref.kpack/
      confidence-overflow.kpack/
      duplicate-ids.kpack/
      missing-evidence-field.kpack/
      cyclic-supersession.kpack/
      dangling-relation-target.kpack/
      wrong-pack-name.kpack/
      prediction-too-confident.kpack/
```

## What This Proves

A KP:1 implementation is **conformant** if it:

1. Parses all valid fixtures without errors
2. Rejects all invalid fixtures with the expected error
3. Validates PACK.yaml against the JSON Schema
4. Enforces semantic constraints SC-01 through SC-12

## Running the Suite

From the repository root:

```bash
pip install -r requirements.txt
python3 conformance/run.py
```

Expected result: `19/19 passed`. The runner has two Python dependencies (`pyyaml`, `jsonschema`) declared in `requirements.txt`.

## Grammar vs Runner

The PEG grammar in `grammar/kp-claims.peg` is the **normative** reference for KP:1 claim syntax. It is what implementations should target.

The `run.py` runner in this preview release validates fixtures against **equivalent regular-expression patterns** rather than parsing through the PEG grammar directly. The two paths are kept in sync by hand. A future phase will replace the regex layer with a PEG-driven parser using a library such as `parsimonious` or `lark`. The fixture suite is the contract: any future runner that passes 19/19 against these fixtures is acceptable.

If you want to implement a conforming parser today, target the PEG grammar, not the runner's regexes.

## Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| C1 | Formal grammar (PEG), JSON Schema, 15 fixtures | **Done** |
| C2 | YAML schemas for signatures.yaml, composition.yaml | **Done** |
| C3 | Automated test runner (`run.py`, 19/19 pass) | **Done** |
| C4 | Round-trip consistency tests | Not started |

## Key Design Decisions

- **PEG over ABNF**: PEG's ordered choice and not-predicates naturally handle
  the dense/verbose syntax distinction and the prose/relation boundary problem.
- **Two-layer validation**: Syntactic (PEG parseable) then semantic (post-parse
  constraints). PEG cannot express cross-references, value ranges, or acyclicity.
- **16 ambiguity resolutions**: See `grammar/README.md` for the full list. Each
  is a normative decision that was not fully specified in the prose spec.
- **All four example packs validated**: `solar-energy-market.kpack`,
  `kp-external-assessment.kpack`, `art-acquisition-decision.kpack`, and
  `auction-house-consignment-review.kpack` all pass the grammar and the
  semantic constraints. The runner validates them on every run alongside
  the 15 fixture cases (19/19 total).
