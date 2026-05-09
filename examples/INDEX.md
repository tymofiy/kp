<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Examples — Feature and Rubric Index

> **Purpose:** map each example pack to (a) the format features it demonstrates, (b) the conformance constraints (SC / AR) it exercises, (c) the [`spec/AUTHORING.md`](../spec/AUTHORING.md) rubrics it walks. Use this to find the right example for what you want to learn or test.

## Quick reference

| Pack | Type | Features density | Best for |
|---|---|---|---|
| [`solar-energy-market.kpack`](solar-energy-market.kpack/) | Domain analysis | Light | First read; basic syntax |
| [`kp-external-assessment.kpack`](kp-external-assessment.kpack/) | Meta-assessment | Medium | Self-referential / judgment-heavy authoring |
| [`art-acquisition-decision.kpack`](art-acquisition-decision.kpack/) | Buyer-side decision | High | Full-feature reference; AUTHORING.md rubric walkthrough |
| [`auction-house-consignment-review.kpack`](auction-house-consignment-review.kpack/) | Consigner-side decision | High | Decline path; cross-pack `↔` references; multi-audience views |

---

## Feature coverage

A `✓` means the pack uses the feature; `–` means it does not. Patterns are claim grammar elements from [`spec/CORE.md`](../spec/CORE.md).

| Feature | solar | kp-external | art-acq | auction |
|---|:-:|:-:|:-:|:-:|
| Dense metadata (4 positions) | ✓ | ✓ | ✓ | ✓ |
| Dense metadata (6 positions) | ✓ | ✓ | ✓ | ✓ |
| Verbose metadata | ✓ | – | – | – |
| Mixed dense + verbose | ✓ | – | – | – |
| All four claim types (`o/r/c/i`) | – (no `c`) | – (i-heavy) | ✓ | ✓ |
| `nature: judgment` | – | ✓ | ✓ | ✓ |
| `nature: prediction` | – | – | ✓ | ✓ |
| `nature: meta` | – | – | ✓ | – |
| Relation: `→` supports | ✓ | ✓ | ✓ | ✓ |
| Relation: `←` requires | – | – | ✓ | – |
| Relation: `~` refines | – | – | ✓ | – |
| Relation: `⊗` bare contradiction | ✓ | – | – | – |
| Relation: `⊗!` error contradiction | – | – | ✓ | ✓ |
| Relation: `⊗~` productive tension | ✓ | – | ✓ | – |
| Relation: `⊘` supersedes | – | – | ✓ | – |
| Relation: `↔` cross-pack | – | – | – | ✓ (illustrative — see pack note) |
| Versioned claim ID (`Cnnn-vN`) | – | – | ✓ | – |
| Multiple evidence refs per claim | ✓ | ✓ | ✓ | ✓ |
| Per-claim entity annotation in H1 | ✓ | ✓ | ✓ | ✓ |
| `display` block fields | ✓ | ✓ | ✓ | ✓ |
| Multiple views (display + voice) | – (overview only) | ✓ | ✓ | ✓ |
| `register` axis on voice view | – | – | ✓ (curatorial) | ✓ (curatorial) |
| Explicit decline / negative recommendation | – | – | – | ✓ |
| `extensions.*` blocks | – | – | – | – |

The four packs together cover every feature in the format's grammar. `solar-energy-market` is the syntactic sampler; `art-acquisition-decision` is the rubric walkthrough; `auction-house-consignment-review` is the decline-path counterpart with cross-pack references.

---

## Conformance constraint exercise (SC / AR)

Conformance constraints are defined in [`spec/CORE.md`](../spec/CORE.md) §12 (Semantic Constraints) and Appendix B (Ambiguity Resolutions). A pack does not need to *fail* a constraint to exercise it — it exercises a constraint by being a valid example of the rule the constraint enforces. The [`conformance/fixtures/invalid/`](../conformance/fixtures/invalid/) packs are the negative-case demonstrations.

| Constraint | What it enforces | Solar | KP-ext | Art-acq | Auction |
|---|---|:-:|:-:|:-:|:-:|
| SC-01 | Confidence ∈ [0.0, 1.0] | ✓ | ✓ | ✓ | ✓ |
| SC-02 | Claim IDs unique within pack | ✓ | ✓ | ✓ | ✓ |
| SC-03 | All evidence refs in claims have entries in evidence.md | ✓ | ✓ | ✓ | ✓ |
| SC-04 | Supersession chains (`⊘`) acyclic | n/a | n/a | ✓ (one chain) | n/a |
| SC-05 | Relation targets exist (cross-pack `#` exempt) | ✓ | ✓ | ✓ | ✓ (cross-pack exempt) |
| SC-06 | KP version compatible | ✓ | ✓ | ✓ | ✓ |
| SC-07 | Rosetta `pack:` matches PACK.yaml `name` | ✓ | ✓ | ✓ | ✓ |
| SC-08 | Rosetta `v:` matches PACK.yaml `version` | ✓ | ✓ | ✓ | ✓ |
| SC-09 | Rosetta `domain:` matches PACK.yaml `domain` | ✓ | ✓ | ✓ | ✓ |
| SC-10 | Rosetta `confidence:` scale matches PACK.yaml | ✓ | ✓ | ✓ | ✓ |
| SC-11 | Claim type vocabulary matches PACK.yaml `confidence` | ✓ | ✓ | ✓ | ✓ |
| SC-12 | Predictions have confidence ≤ 0.95 | n/a | n/a | ✓ (C021 at 0.55) | ✓ (C018 at 0.55) |
| AR-01 | Claim ID is `C\d+(?:-v\d+)?` | ✓ | ✓ | ✓ (versioned) | ✓ |
| AR-02 | Evidence ID is `E\d+` | ✓ | ✓ | ✓ | ✓ |
| AR-04 | Relations on metadata-line-after-`}` and/or continuation | ✓ | ✓ | ✓ | ✓ |
| AR-07 | Both blockquote and list evidence formats valid | ✓ | – (blockquote only) | ✓ (blockquote w/ bold) | ✓ (blockquote w/ bold) |
| AR-13 | A claim uses dense OR verbose, not both | ✓ | ✓ | ✓ | ✓ |
| AR-16 | Cross-pack ref format `pack#section` | – | – | – | ✓ (illustrative) |

---

## AUTHORING.md rubric walkthrough

[`spec/AUTHORING.md`](../spec/AUTHORING.md) defines producer-side decision rubrics. Each example pack walks a subset of the rubrics:

### `art-acquisition-decision.kpack` — full rubric walkthrough

The pack is designed to walk every AUTHORING.md rubric end-to-end on a single coherent scenario.

| AUTHORING § | Rubric | How the pack demonstrates |
|---|---|---|
| §2 | Claim type `o/r/c/i` | C001 `o` (offer letter direct receipt), C002 `o` (asking price), C003 `r` (gallery + raisonné corroboration), C015 `o` (XRF observation), C019 `i` (synthesis) |
| §3 | Claim nature | Mostly factual default; C005 reported-source-content (no judgment annotation); C019 judgment; C021 prediction; C016/C020 meta |
| §4 | Contradiction qualifier | C005 `⊗!` C004 (dating revision: previously wrong attribution superseded); C008 `⊗~` C007 (provenance gap: documented post-1962 chain coexists with documented pre-1962 absence — both informative); C019 `⊗~` C017 (recommendation in tension with risk) |
| §5 | Confidence calibration | Spread 0.45 to 0.99; calibrated to evidence depth; C001/C002 at 0.99 (trivially-falsifiable: offer letter contains the offer); C017 at 0.45 (contested judgment about provenance-gap risk) |
| §6 | Depth | `investigated` for most; `exhaustive` for C005 (catalog raisonné), C008 (provenance gap search) |
| §7 | Supersede / refine / split | C014 `⊘` C013 (2025 appraisal supersedes 2023 appraisal that used pre-revision dating) |
| §8 | Granularity | Each claim is one independently-falsifiable assertion; C012 ("the price falls within the comparable range") is computed and minimal |
| §9 | Content routing | claims.md asserts; evidence.md sources; views/{overview, counsel, voice/briefing} render audience-specific surfaces |

### `auction-house-consignment-review.kpack` — decline path + cross-pack

| AUTHORING § | Rubric | How the pack demonstrates |
|---|---|---|
| §2-3 | Type and nature | Full mix; the recommendation (C016) is a judgment-shaped *decline* |
| §4 | Contradiction qualifier | C007 `⊗!` C006 (foundry-mark dispositive: house's posthumous-cast read overrides consignor's lifetime-cast claim) |
| §5 | Confidence calibration | Spread 0.55 to 0.99; SC-12-conformant prediction at C018 (0.55) |
| §9 | Content routing | views/{decision (committee), specialist (working notes), consignor-letter (formal-register decline), voice/briefing} — four audience-specific renderings of the same claim graph |
| AR-16 | Cross-pack `↔` | C019 / C020 use `↔` to point at illustrative reference packs (the targets are explicitly disclaimed as not-in-this-repo placeholders demonstrating the grammar; see the pack's Cross-References section note) |

### `kp-external-assessment.kpack` — judgment-heavy meta example

Walks the `nature: judgment` annotation discipline and the §5 confidence-calibration rubric on a meta-domain. Confidence values are correlated with depth (`investigated` lower, `exhaustive` higher) and with the contestability of each claim — the three most-provisional findings (C006, C007, C009) carry confidence in the 0.68-0.78 range; durable findings sit at 0.84-0.93.

### `solar-energy-market.kpack` — basic syntax sampler

The hello-world. Demonstrates dense + verbose claim metadata, a representative subset of relation symbols (`→`, `⊗~`, `←`; not the full eight — see the matrix above), and a single overview view. Use this to learn the syntax before opening the larger packs.

---

## How to use this index

- **Building a parser?** Start with `solar-energy-market.kpack` for the syntax, then run `python3 conformance/run.py --pack examples/solar-energy-market.kpack` (from the repo root) to see the validator pipeline.
- **Authoring a new pack?** Read [`spec/AUTHORING.md`](../spec/AUTHORING.md) alongside `art-acquisition-decision.kpack`; the rubric walkthrough above shows which sections to consult for each authoring decision.
- **Implementing a renderer?** All four packs have multiple views; the audience-specific views in `art-acquisition-decision.kpack` and `auction-house-consignment-review.kpack` show how `display_as` / `purpose` / `register` differentiate audience targeting.
- **Validating cross-pack references?** Only `auction-house-consignment-review.kpack` exercises `↔`. Note the pack's explicit Cross-References disclaimer about illustrative targets.

---

*Generated 2026-05-09 alongside v0.8.0-preview. The index is regenerated when example packs change; verify by running `python3 conformance/run.py` (19/19 expected) before relying on the table data.*
