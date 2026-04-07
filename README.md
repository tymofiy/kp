<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

> *Man sieht nur, was man weiß.*  
> *We see only what we know.*  
> — Goethe
>
> *You see that the sun rises and sets and therefore you think you know. You don't.*  
> *You only know when you can answer the question: How or what for?*  
> — Barenboim
>
> *An AI knows only what we tell it.*  
> *KP:1 is for telling it whole.*  
> — KP:1

# KP:1 -- Knowledge Pack Format

> A plain-text format for packaging epistemic state -- claims with confidence,
> evidence, relationships, and contradictions.

**Editor:** Timothy Kompanchenko
**Status:** Editor's Draft — `KP:1 Public Draft — 2026-04` (`v0.7-preview`)
**See also:** [`spec/CORE.md`](spec/CORE.md), [`spec/SPEC.md`](spec/SPEC.md), [`GOVERNANCE.md`](GOVERNANCE.md), [`CONTRIBUTING.md`](CONTRIBUTING.md)

## What is KP:1?

Knowledge Packs represent what someone believes, how strongly they believe it,
based on what evidence, in tension with what other beliefs, as understood at a
particular moment in time. KP:1 encodes these properties in Markdown files that
are readable by humans and parseable by machines.

**For humans and AI alike.** Both benefit from the same thing — structured
epistemic state instead of epistemic state inferred from prose. Claims are
pre-chunked and ID'd. Evidence is explicit. Confidence is typed. Contradictions
are flagged. Humans get an auditable format; AI gets a context-engineered one —
the model doesn't have to re-derive on every pass what the document is actually
claiming. This is the same insight that motivates `llms.txt`, `AGENTS.md`, and
the current wave of "context docs" formats, pushed further into how knowledge
is represented rather than just how it's indexed.

## Quick Start

Read **[spec/CORE.md](spec/CORE.md)** -- the implementable Core specification.
It covers pack structure, manifest schema, claim syntax, evidence, confidence,
relations, and validation rules. Everything you need to build a conformant
parser.

A claim in KP:1 looks like this:

```markdown
- [C001] Cost decline is structural, not cyclical
  {0.95|i|E001,E002|2026-03-01|exhaustive|judgment}
  Learning curve has held for 40 years. →C002, ⊗~C003
```

Each claim has an ID, an assertion, a confidence/type/evidence block, and
optional context with relations to other claims.

## Repository Structure

| Directory | Purpose |
|-----------|---------|
| `spec/` | Normative specification -- [CORE.md](spec/CORE.md), [SPEC.md](spec/SPEC.md), and companion documents |
| `conformance/` | PEG grammar, JSON Schema, and 10 test fixtures |
| `examples/` | Two complete `.kpack` examples |
| `positioning/` | Public-facing positioning and design rationale |
| `research/` | Benchmark design and prior art analysis |
| `reference/` | Reference parser and tooling (planned) |
| `decisions/` | Design decision records |
| `scripts/` | Git hooks and validation helpers |

Top-level governance and policy files include `GOVERNANCE.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `LICENSE`, `LICENSE-CODE`, and `DCO.txt`.

## Examples

Two complete Knowledge Packs demonstrate the format:

- **[Solar Energy Market](examples/solar-energy-market.kpack/)** -- Market
  analysis with cost trajectories, technology trends, and regional adoption.
  Shows dense claim syntax, confidence levels, evidence references, and
  inter-claim relations including contradictions.

- **[KP External Assessment](examples/kp-external-assessment.kpack/)** -- A
  self-assessment of the KP format itself. Demonstrates meta-level claims and
  the format's ability to represent epistemic state about its own design.

## Conformance

The [conformance suite](conformance/) provides formal validation tools:

- **PEG grammar** (`conformance/grammar/kp-claims.peg`) -- parseable
  definition of claims.md syntax
- **JSON Schema** (`conformance/grammar/kp-pack.schema.json`) -- validation
  schema for PACK.yaml manifests
- **10 test fixtures** -- 5 valid packs that must be accepted, 5 invalid packs
  that must be rejected with specific errors

A conformant implementation parses all valid fixtures, rejects all invalid ones,
validates PACK.yaml against the schema, and enforces semantic constraints SC-01
through SC-11. See [conformance/README.md](conformance/README.md) for details.

## Interoperability

KP:1 has its own syntax and semantics, but it can interoperate with RDF/JSON-LD,
PROV-O, and Nanopublications. **[spec/MAPPING.md](spec/MAPPING.md)** provides a
field-by-field translation analysis grading each mapping as clean, lossy, or
impossible -- so practitioners using existing semantic web toolchains can assess
what they gain and what they lose.

## Status

This is an **editor's draft** maintained by a single editor in a public repository. It is published as `KP:1 Public Draft — 2026-04` (git tag `v0.7-preview`). It has a formal grammar, a JSON Schema, a conformance suite with 10 test fixtures, and two reference examples.

The specification is **not final** and may change in any way at any time, including breaking changes. It is **not yet ratified** by any standards body. Compatibility commitments will arrive only with a non-draft version. See [`GOVERNANCE.md`](GOVERNANCE.md) for the full governance picture, including how decisions are made during the preview phase and what changes when the Knowledge Pack Foundation is incorporated.

The current phase is **feedback-only**: the editor welcomes issues, comparisons, ambiguity reports, and adversarial review through GitHub issues, but does not accept external pull requests modifying normative spec text. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for details.

## License

KP:1 is published under two licenses:

- **Specification text** (everything in `spec/` and the prose portions of this README) is licensed under the [Creative Commons Attribution 4.0 International License (CC-BY-4.0)](LICENSE). You may share and adapt the material for any purpose, including commercially, with attribution.
- **Code, schemas, and examples** (everything in `conformance/`, `examples/`, `scripts/`) is licensed under the [Apache License 2.0](LICENSE-CODE), which includes an explicit patent grant.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the contribution policy and [`GOVERNANCE.md`](GOVERNANCE.md) for governance details.

## How to Cite

If you reference KP:1 in academic, technical, or evaluative work, please use the metadata in [`CITATION.cff`](CITATION.cff). A Zenodo DOI (`10.5281/zenodo.19445263`) is reserved for the v0.7-preview release; it will resolve once the Zenodo deposit is published. Until then, the recommended short form is:

> Kompanchenko, T. (2026). *KP:1 — Knowledge Pack Format Specification* (Version 0.7-preview). https://github.com/tymofiy/kp

The editor and an acknowledgment of AI drafting assistance are also recorded in [`ACKNOWLEDGMENTS.md`](ACKNOWLEDGMENTS.md).

## Trademarks

`KP:1`™ is a pending United States trademark. "Knowledge Pack" is the descriptive name of the format and is not currently a registered or pending trademark. See [`GOVERNANCE.md`](GOVERNANCE.md) for the conformance and trademark use policy.
