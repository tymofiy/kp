<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

> *An AI knows only what we tell it.*  
> *KP:1 is for telling it whole.*  
> — KP:1

# KP:1 -- Knowledge Pack Format

[![CI](https://github.com/tymofiy/kp/actions/workflows/ci.yml/badge.svg)](https://github.com/tymofiy/kp/actions/workflows/ci.yml) [![Spec license: CC BY 4.0](https://img.shields.io/badge/spec-CC_BY_4.0-blue)](LICENSE) [![Code license: Apache 2.0](https://img.shields.io/badge/code-Apache_2.0-blue)](LICENSE-CODE) [![Latest tag](https://img.shields.io/github/v/tag/tymofiy/kp?label=tag)](https://github.com/tymofiy/kp/tags)

> KP:1 is a format that doesn't flatten knowledge. Uncertainties stay uncertain,
> contradictions stay in tension, and the trace of how beliefs evolved is kept
> as structure. AI-first, human-accessible.

**Editor:** Timothy Kompanchenko
**Status:** Editor's Draft — `KP:1 Public Draft — 2026-06` (`v0.8.3-preview`)
**Cite:** [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19445262.svg)](https://doi.org/10.5281/zenodo.19445262) (concept DOI — always resolves to latest version)
**See also:** [`spec/CORE.md`](spec/CORE.md), [`spec/SPEC.md`](spec/SPEC.md), [`spec/AUTHORING.md`](spec/AUTHORING.md), [`AGENTS.md`](AGENTS.md) (AI-first routing), [`GOVERNANCE.md`](GOVERNANCE.md), [`CONTRIBUTING.md`](CONTRIBUTING.md)

## What is KP:1?

> *Man sieht nur, was man weiß. / We see only what we know.*  
> — Goethe
>
> *You see that the sun rises and sets and therefore you think you know. You don't.*  
> *You only know when you can answer the question: How or what for?*  
> — Barenboim

Think about what anyone actually knows about a real artwork: contradictory
accounts of provenance, overlapping stories that reinforce each other, uncertain
events, details that mattered ten years ago and matter less now. A lot of it
is unfinished, probabilistic information. The value of the knowledge comes from
that texture — the uncertainty, the tension, the trace of how beliefs evolved.
Flatten it — average it out into a list of settled facts — and you've destroyed
what made it knowledge.

That's the difference between knowledge and data. Data answers yes or no.
Knowledge has the shape of belief — its uncertainties, its tensions, its
history. **KP:1 is a format that keeps the shape.**

The same knowledge, flattened and kept:

```text
Prose: "Solar costs are probably still falling, though some analysts disagree."

KP:1:
- [C001] Solar cost decline is structural, not cyclical
  {0.85|i|E001,E002|2026-06-10|investigated|judgment} ⊗~C003
```

The prose flattens confidence, evidence, recency, and a live disagreement
into hedge-words. The claim keeps each one addressable: held at 0.85, on two
cited pieces of evidence, dated, investigated but not exhaustively, a
judgment — and in productive tension (`⊗~`) with a competing claim.

**Built AI-first.** Every AI reading knowledge from prose today hits the
same problem: amnesia. Between sessions, between context windows, between tools,
the model loses the thread and has to reconstruct from prose what's being
asserted, how certain each point is, where the contradictions are, which
beliefs superseded which. That reconstruction is lossy, expensive in context
window, and unreliable. KP:1 is designed to fix that. It's a structured
format for AI to read, reason over, and carry forward between sessions —
handing the model what's believed, how strongly, on what evidence, in tension
with what, and how those beliefs evolved. No guessing. No re-derivation.
No reconstruction from prose.

**Human-accessible.** A knowledge pack is a directory of Markdown and YAML
files. Humans read it, print it, edit it, and work with it using ordinary text
tools. But the primary consumer is AI — the structure exists to let AI reason
without reconstructing from scratch. This is the same wave as
`llms.txt` and `AGENTS.md` — formats built for AI to read directly —
applied to knowledge itself.

### When to reach for it — and when not

**Use KP:1 when** beliefs need to survive transport: an AI or a human team
carrying claims forward — with their uncertainty, contradictions, evidence
trail, and supersession history intact — across sessions, tools, and time.

**Don't use KP:1 when** you need search or live retrieval over a large corpus
(that is a RAG pipeline's job), a queryable graph database, or a free-form
notes app. KP:1 is the packaging for authored, curated knowledge; it
complements those systems rather than replacing them.

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
| `conformance/` | PEG grammar, JSON Schema, and 18 test fixtures |
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
  European painting. Demonstrates the full repertoire of contradiction
  qualifiers (`⊗`, `⊗!`, `⊗~`), supersession (`⊘`), all four claim types,
  multiple confidence calibrations, judgment / prediction / meta natures,
  and audience-specific views (buyer, counsel, voice briefing). The pack
  walks the rubrics from [`spec/AUTHORING.md`](spec/AUTHORING.md) end-to-end
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
- **18 test fixtures** -- 6 valid packs that must be accepted, 12 invalid packs
  that must be rejected with specific errors
- **5 complete example packs** -- the kpacks in `examples/` are validated by
  the runner as part of the suite, so the live examples are themselves
  conformance tests

The runner (`conformance/run.py`) reports **23/23 passed** on a conformant
implementation: 18 fixture tests + 5 example validations. A conformant
implementation parses all valid fixtures, rejects all invalid ones, validates
PACK.yaml against the schema (including its `format` assertions), validates
`signatures.yaml` and `composition.yaml` against their schemas when present,
and enforces semantic constraints SC-01 through SC-12.

Run from a fresh checkout:

```bash
python3 -m venv .venv && source .venv/bin/activate  # if your Python is externally managed (PEP 668)
pip install -r requirements.txt
python3 conformance/run.py                       # full suite (23/23 expected)
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

KP:1 is published as `KP:1 Public Draft — 2026-06` (current git tag `v0.8.3-preview`, with the v0.7.x preview series and the iterative v0.8.x preview line documented in [`spec/CHANGELOG.md`](spec/CHANGELOG.md)). It has a formal grammar, a JSON Schema, a conformance suite with 18 test fixtures plus 5 reference examples (23/23 validated).

This is an **editor's draft** maintained by a single editor in a public repository. The specification is **not final** and may change in any way at any time, including breaking changes. It is **not yet ratified** by any standards body. Compatibility commitments will arrive only with a non-draft version. See [`GOVERNANCE.md`](GOVERNANCE.md) for the full governance picture, including how decisions are made during the preview phase and what changes when the Knowledge Pack Foundation is incorporated.

The current phase is **feedback-only**: the editor welcomes issues, comparisons, ambiguity reports, and critical review through GitHub issues, but does not accept external pull requests modifying normative spec text. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for details.

## License

KP:1 is published under two licenses:

- **Specification text** (everything in `spec/` and the prose portions of this README) is licensed under the [Creative Commons Attribution 4.0 International License (CC-BY-4.0)](LICENSE). You may share and adapt the material for any purpose, including commercially, with attribution.
- **Code, schemas, and examples** (everything in `conformance/`, `examples/`, `scripts/`) is licensed under the [Apache License 2.0](LICENSE-CODE), which includes an explicit patent grant.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the contribution policy and [`GOVERNANCE.md`](GOVERNANCE.md) for governance details.

## How to Cite

If you reference KP:1 in academic, technical, or evaluative work, please use the metadata in [`CITATION.cff`](CITATION.cff). The Zenodo **concept DOI** [`10.5281/zenodo.19445262`](https://doi.org/10.5281/zenodo.19445262) always resolves to the most recently published version. The v0.8.0-preview snapshot remains available at DOI [`10.5281/zenodo.20100689`](https://doi.org/10.5281/zenodo.20100689), and the v0.7-preview predecessor release remains available at DOI [`10.5281/zenodo.19445263`](https://doi.org/10.5281/zenodo.19445263).

The recommended short form (using the concept DOI for the current preview) is:

> Kompanchenko, T. (2026). *KP:1 — Knowledge Pack Format Specification* (Version 0.8.3-preview). Zenodo. <https://doi.org/10.5281/zenodo.19445262>

The editor and an acknowledgment of AI drafting assistance are also recorded in [`ACKNOWLEDGMENTS.md`](ACKNOWLEDGMENTS.md).

## Trademarks

`KP:1`™ is a pending United States trademark. "Knowledge Pack" is the descriptive name of the format and is not currently a registered or pending trademark. See [`GOVERNANCE.md`](GOVERNANCE.md) for the conformance and trademark use policy.
