<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# KP:1 -- Knowledge Pack Format

[![CI](https://github.com/tymofiy/kp/actions/workflows/ci.yml/badge.svg)](https://github.com/tymofiy/kp/actions/workflows/ci.yml) [![Spec license: CC BY 4.0](https://img.shields.io/badge/spec-CC_BY_4.0-blue)](LICENSE) [![Code license: Apache 2.0](https://img.shields.io/badge/code-Apache_2.0-blue)](LICENSE-CODE) [![Latest tag](https://img.shields.io/github/v/tag/tymofiy/kp?label=tag)](https://github.com/tymofiy/kp/tags)

> KP:1 is an AI-first, plain-text format for keeping knowledge with its context,
> relationships, uncertainty and history. It gives people and AI a lasting record
> they can reason with and continue using across tasks and tools.

**Editor:** Timothy Kompanchenko
**Status:** Released Editor's Draft — v0.8.5-preview
**Draft updated:** 2026-10-12
**Latest citable release:** `KP:1 — Knowledge Pack Format Specification` (`v0.8.5-preview`, 2026-10-13)
**Cite:** [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19445262.svg)](https://doi.org/10.5281/zenodo.19445262) (concept DOI — always resolves to latest version)
**See also:** [`spec/CORE.md`](spec/CORE.md), [`spec/SPEC.md`](spec/SPEC.md), [`spec/AUTHORING.md`](spec/AUTHORING.md), [`AGENTS.md`](AGENTS.md) (AI-first routing), [`GOVERNANCE.md`](GOVERNANCE.md), [`CONTRIBUTING.md`](CONTRIBUTING.md)

## What is KP:1?

Knowledge includes more than settled facts. It includes explanations and connections, different perspectives, what sources say, what is disputed or missing, and why an assessment changed. An artwork's ownership history, for example, can include documented events, gaps and conflicting accounts. Removing those details changes what another person or AI can understand from the record.

KP:1 is designed to keep that richness available for reasoning. A Knowledge Pack can carry an articulated understanding of a subject: assertions and explanations, their support and relationships, perspectives, uncertainty and changes. Another person or AI can examine the recorded reasons, challenge an assessment and continue the inquiry. The record is expressed in ordinary text files; companion formats can also carry definitions and policies. This continuity is the aim of the system, while authors and applications remain responsible for the quality of the account and its use.

A short summary and a structured claim excerpt:


```text
Prose: "Solar costs are probably still falling, though some analysts disagree."

KP:1:
- [C001] Solar cost decline is structural, not cyclical
  {0.85|i|E001,E002|2026-06-10|investigated|judgment} ⊗~C003
```

The excerpt makes the confidence, evidence references, date, investigation depth, judgment and competing claim separately addressable. The supporting records supply their meaning; a confidence number alone does not prove the assertion. This is an excerpt, not a complete pack.

**Built AI-first.** An AI system can read a pack, select relevant context for a task, examine the support and relationships, and add findings or corrections. Software must provide those operations; the format supplies a common record for them. Retaining the richer record can reduce repeated explanation and avoid asking a model to guess details that a summary removed. A focused view can help with a limited context window while keeping a route back to the full record.

**Lasting knowledge.** Work can continue across conversations, people and tools when its relevant context and changes remain available. A pack is designed to provide that continuity. It is not a model's internal memory, and it does not require one particular AI provider or a central registry.

**Human-accessible.** A pack is a directory of Markdown and YAML files. People can read and edit those files with ordinary text tools. Readable views can present selected material for a particular audience while the canonical files retain the underlying record.

### When to reach for it

**Use KP:1 when** people and AI need to carry knowledge across tasks, tools
and time, keeping its context, uncertainty, different accounts, supporting
sources and history available for reasoning.

**Retrieval and applications work with that record.** Search systems, graph
databases and retrieval-augmented generation can help select relevant
material from packs. They should retain the route to the underlying record.
The format defines what is kept and how it is represented; application
software supplies retrieval, reasoning and workflow operations.

## Quick Start

Read **[spec/CORE.md](spec/CORE.md)** -- the implementable Core specification.
It covers pack structure, manifest schema, claim syntax, evidence, confidence,
relations, and validation rules. Start here for the generic claim-bearing directory surface; read the relevant
companions for additional kinds, composition, locales and archives.

A claim in KP:1 looks like this:

```markdown
- [C001] Cost decline is structural, not cyclical
  {0.95|i|E001,E002|2026-03-01|exhaustive|judgment}
  Learning curve has held for 40 years. →C002, ⊗~C003
```

Each claim has an ID, an assertion, a confidence/type/evidence block, and
optional context with relations to other claims. The metadata block, position
by position: `{confidence | type | evidence refs | date established | depth | nature}`.
Relation symbols, in brief:
`→` supports · `⊗` contradicts (`⊗!` known error, `⊗~` productive tension) ·
`←` requires · `~` refines · `⊘` supersedes · `↔` see also.

To start a pack of your own, copy
[`examples/hello-world.kpack/`](examples/hello-world.kpack/) — the smallest
idiomatic pack (three claims, two evidence entries) — and edit from there,
or scaffold the same starter with fresh dates in one step:
`./reference/kpack new my-pack`.

## Repository Structure

| Directory | Purpose |
|-----------|---------|
| `spec/` | Normative specification -- [CORE.md](spec/CORE.md), [SPEC.md](spec/SPEC.md), and companion documents |
| `conformance/` | PEG grammar, JSON Schema, and 24 test fixtures |
| `examples/` | Five `.kpack` reference examples (validated by the conformance suite), including the `hello-world` starter |
| `positioning/` | Public-facing positioning and design rationale |
| `research/` | Benchmark design and prior art analysis |
| `reference/` | Reference CLI — `kpack lint` and `kpack new` are implemented; other subcommands are contract-pointer stubs. Installable as a console script: `pip install -e .` |
| `decisions/` | Design decision records |
| `scripts/` | Git hooks and validation helpers |

Top-level governance and policy files include `GOVERNANCE.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `LICENSE`, `LICENSE-CODE`, and `DCO.txt`.

### If you are an AI agent

Start with [`AGENTS.md`](AGENTS.md). It routes you to the minimum required
reading for your specific task — parsing, authoring, reconciling, translating,
composing, or voice playback — and lists the mistakes agents most often make
with the format.

## Examples

Five Knowledge Packs demonstrate the format:

- **[Hello World](examples/hello-world.kpack/)** -- The copy-this starter:
  the smallest idiomatic pack (three claims, two evidence entries, one
  relation each of `→` and `~`). `cp -r` it to begin your own pack.

- **[Solar Energy Market](examples/solar-energy-market.kpack/)** -- Market
  analysis with cost trajectories, technology trends, and regional adoption.
  Shows dense claim syntax, confidence levels, evidence references, and
  inter-claim relations including contradictions.

- **[KP External Assessment](examples/kp-external-assessment.kpack/)** -- A
  self-assessment of the KP format itself. Demonstrates meta-level claims and
  the format's ability to describe its own uncertainties, tensions, and open
  questions about its own design.

- **[Art Acquisition Decision](examples/art-acquisition-decision.kpack/)** --
  A buyer-side decision-support pack for an anonymized mid-twentieth-century
  European painting. Demonstrates an identified error (`⊗!`), supersession (`⊘`), all four claim types,
  multiple confidence assessments, judgment / prediction / meta natures,
  and audience-specific views (buyer, counsel, voice briefing). The pack
  illustrates the rubrics from [`spec/AUTHORING.md`](spec/AUTHORING.md)
  on a realistic decision-support scenario.

- **[Auction House Consignment Review](examples/auction-house-consignment-review.kpack/)**
  -- The consigner-side counterpart: an auction house declines a sculpture
  consignment over a foundry-mark attribution dispute, with conditions for
  reconsideration. Demonstrates the *decline* path (judgment-shaped
  recommendation against acquisition), cross-pack `↔` references to
  hypothetical reference packs, evidence diversity (consignor-supplied
  documents reviewed against the house's specialist), and a different
  audience-frame than the buyer-side pack (committee decision, specialist
  notes, formal-register consignor decline letter, voice briefing).

## Conformance

The [conformance suite](conformance/) provides formal validation tools:

- **PEG grammar** (`conformance/grammar/kp-claims.peg`) -- parseable
  definition of claims.md syntax
- **JSON Schema** (`conformance/grammar/kp-pack.schema.json`) -- validation
  schema for PACK.yaml manifests
- **24 test fixtures** -- 10 valid packs that must be accepted, 14 invalid packs
  that must be rejected with specific errors
- **5 complete example packs** -- the kpacks in `examples/` are validated by
  the runner as part of the suite, so the live examples are themselves
  conformance tests

The reference suite has **29 fixture/example cases**: 24 fixture checks and 5 example validations. A pass demonstrates those cases; it is not certification of an implementation's complete conformance. Additional contract tests exercise evidence round-trip, historical references, authoring diagnostics and selection constraints. See the [capability and compatibility guide](spec/COMPATIBILITY.md) for implemented surfaces and known limits.

Run from a fresh checkout:

```bash
python3 -m venv .venv && source .venv/bin/activate  # if your Python is externally managed (PEP 668)
pip install -r requirements.txt
python3 conformance/run.py                       # full suite (29/29 expected)
python3 conformance/run.py --strict              # also parse claims.md through the PEG grammar
python3 conformance/run.py --pack path/to/x.kpack  # validate a single pack
```

See [conformance/README.md](conformance/README.md) for details.

## Interoperability

KP:1 has its own syntax and semantics. **[spec/MAPPING.md](spec/MAPPING.md)**
provides a field-by-field translation to RDF/JSON-LD, PROV-O, and
Nanopublications — grading each mapping as clean, lossy, or impossible, so
practitioners using existing semantic web toolchains can assess what they
gain and what they lose. Of the 21 concepts mapped, 4 translate cleanly,
8 with loss, and 9 have no standard equivalent, counting the best grade
achieved across the three targets. Notably, KP:1's distinction between unqualified
contradiction (⊗), error-contradiction (⊗!), and informative tension (⊗~)
has no direct equivalent in any of these standards — it is one of the
format's genuinely novel contributions.

## Status

KP:1 is published as a **released editor's draft**, `v0.8.5-preview` (2026-10-13), archived at [the version DOI](https://doi.org/10.5281/zenodo.23329922). The [changelog](spec/CHANGELOG.md) records this release and the earlier preview series. Its grammar, schemas and reference checks remain preview work. A release makes this snapshot public and citable; it does not make the specification final. See [compatibility](spec/COMPATIBILITY.md).

This is an **editor's draft** maintained by a single editor in a public repository. The specification is **not final** and may change in any way at any time, including breaking changes. It is **not yet ratified** by any standards body. Compatibility commitments will arrive only with a non-draft version. See [`GOVERNANCE.md`](GOVERNANCE.md) for the full governance picture, including how decisions are made during the preview phase and what changes when the Knowledge Pack Foundation is incorporated.

The current phase is **feedback-only**: the editor welcomes issues, comparisons, ambiguity reports, and critical review through GitHub issues, but does not accept external pull requests modifying normative spec text. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for details.

## License

KP:1 is published under two licenses:

- **Specification text** (everything in `spec/` and the prose portions of this README) is licensed under the [Creative Commons Attribution 4.0 International License (CC-BY-4.0)](LICENSE). You may share and adapt the material for any purpose, including commercially, with attribution.
- **Code, schemas, and examples** (everything in `conformance/`, `examples/`, `scripts/`) is licensed under the [Apache License 2.0](LICENSE-CODE), which includes an explicit patent grant.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the contribution policy and [`GOVERNANCE.md`](GOVERNANCE.md) for governance details.

## How to Cite

If you reference KP:1 in academic, technical, or evaluative work, please use the metadata in [`CITATION.cff`](CITATION.cff). The Zenodo **concept DOI** [`10.5281/zenodo.19445262`](https://doi.org/10.5281/zenodo.19445262) always resolves to the most recently published version. The v0.8.0-preview snapshot remains available at DOI [`10.5281/zenodo.20100689`](https://doi.org/10.5281/zenodo.20100689), and the v0.7-preview predecessor release remains available at DOI [`10.5281/zenodo.19445263`](https://doi.org/10.5281/zenodo.19445263).

For a reproducible citation, use the version DOI. A [publication abstract and searchable specification PDF](https://tymofiy.github.io/kp/kp-v0.8.5-preview.html) are also available. The recommended short form is:

> Kompanchenko, T. (2026). *KP:1 — Knowledge Pack Format Specification* (Version 0.8.5-preview). Zenodo. <https://doi.org/10.5281/zenodo.23329922>

With the Python dependencies in `requirements.txt` installed, install Pandoc, Typst, qpdf, and the Inter / IBM Plex Mono fonts, then run `python3 scripts/build_pdf.py`. The adjacent `.sources.json` file records source hashes and tool versions; byte reproducibility is scoped to the same tool and font environment.

The editor and an acknowledgment of AI drafting assistance are also recorded in [`ACKNOWLEDGMENTS.md`](ACKNOWLEDGMENTS.md).

## Trademarks

`KP:1`™ is a pending United States trademark. "Knowledge Pack" is the descriptive name of the format and is not currently a registered or pending trademark. See [`GOVERNANCE.md`](GOVERNANCE.md) for the conformance and trademark use policy.
