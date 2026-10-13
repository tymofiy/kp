<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Examples — Feature and Rubric Index

> **Purpose:** map each example pack to (a) the format features it demonstrates, (b) the conformance constraints (SC / AR) it exercises, (c) the [`spec/AUTHORING.md`](../spec/AUTHORING.md) rubrics it walks. Use this to find the right example for what you want to learn or test.

## Quick reference

| Pack | Type | Features density | Best for |
|---|---|---|---|
| [`hello-world.kpack`](hello-world.kpack/) | Starter template | Minimal | Copying to start your own pack |
| [`solar-energy-market.kpack`](solar-energy-market.kpack/) | Domain analysis | Light | First read; basic syntax |
| [`kp-external-assessment.kpack`](kp-external-assessment.kpack/) | Meta-assessment | Medium | Self-referential / judgment-heavy authoring |
| [`art-acquisition-decision.kpack`](art-acquisition-decision.kpack/) | Buyer-side decision | High | Worked acquisition scenario; AUTHORING.md decision examples |
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
| `nature: meta` | – | – | ✓ | ✓ |
| Relation: `→` supports | ✓ | ✓ | ✓ | – |
| Relation: `←` requires | ✓ | – | ✓ | – |
| Relation: `~` refines | – | – | ✓ | ✓ |
| Relation: `⊗` bare contradiction | – | – | – | – |
| Relation: `⊗!` error contradiction | – | – | ✓ | – |
| Relation: `⊗~` productive tension | ✓ | – | – | – |
| Relation: `⊘` supersedes | – | – | ✓ | – |
| Relation: `↔` cross-pack | – | – | – | ✓ (illustrative — see pack note) |
| Versioned claim ID (`Cnnn-vN`) | – | – | – | – |
| Multiple evidence refs per claim | ✓ | ✓ | ✓ | ✓ |
| Per-claim entity annotation in H1 | ✓ | ✓ | ✓ | ✓ |
| `display` block fields | ✓ | ✓ | ✓ | ✓ |
| Multiple views (display + voice) | – (overview only) | ✓ | ✓ | ✓ |
| `register` axis on voice view | – | – | ✓ (curatorial) | ✓ (curatorial) |
| Explicit decline / negative recommendation | – | – | – | ✓ |
| `extensions.*` blocks | – | – | – | – |

The four domain packs illustrate selected grammar and authoring features (`hello-world` is a minimum-shape starter and is deliberately outside the matrices). `solar-energy-market` is the syntactic sampler; `art-acquisition-decision` is the rubric walkthrough; `auction-house-consignment-review` is the decline-path counterpart with cross-pack references.

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
| AR-01 | Claim ID is `C\d+(?:-v\d+)?` | ✓ | ✓ | ✓ (unversioned) | ✓ |
| AR-02 | Evidence ID is `E\d+` | ✓ | ✓ | ✓ | ✓ |
| AR-04 | Relations on metadata-line-after-`}` and/or continuation | ✓ | ✓ | ✓ | ✓ |
| AR-07 | Both blockquote and list evidence formats valid | ✓ | ✓ (list metadata) | ✓ (blockquote w/ bold) | ✓ (blockquote w/ bold) |
| AR-13 | A claim uses dense OR verbose, not both | ✓ | ✓ | ✓ | ✓ |
| AR-16 | Cross-pack ref format `pack#section` | – | – | – | ✓ (illustrative) |

---

## AUTHORING.md rubric walkthrough

[`spec/AUTHORING.md`](../spec/AUTHORING.md) defines producer-side decision rubrics. Each example pack walks a subset of the rubrics:

### `art-acquisition-decision.kpack` — worked authoring decisions

The pack illustrates authoring decisions in a single coherent scenario. For productive tension, use the solar example; for bare contradiction, read [AUTHORING.md §4](../spec/AUTHORING.md).

| AUTHORING § | Rubric | How the pack demonstrates |
|---|---|---|
| §2 | Claim type `o/r/c/i` | C001 `o` (offer letter direct receipt), C002 `o` (asking price), C003 `r` (gallery + raisonné corroboration), C015 `o` (XRF observation), C019 `i` (synthesis) |
| §3 | Claim nature | Mostly factual default; C005 reported-source-content (no judgment annotation); C019 judgment; C021 prediction; C020 meta |
| §4 | Contradiction qualifier | C024 `⊗!` C023 corrects an adopted dating, with C023 retained in history; source reports C004/C005 both remain; C007/C008 cover different provenance intervals; C019 considers C017 through `←`, rather than denying the risk |
| §5 | Confidence assessment | Spread 0.45 to 0.99, with reasons tied to evidence and claim nature; C001/C002 at 0.99 (offer letter contains the offer); C017 at 0.45 (contested judgment about provenance-gap risk). The example does not demonstrate empirical calibration. |
| §6 | Depth | `investigated` for most; `exhaustive` for C005 (catalog raisonné), C008 (provenance gap search) |
| §7 | Supersede / refine / split | C024 `⊘` C023 (new adopted dating replaces the withdrawn assessment); C013/C014 remain dated appraisal reports, with the current preference stated separately at C025 |
| §8 | Granularity | Each claim is one independently-falsifiable assertion; C012 ("the price falls within the comparable range") is computed and minimal |
| §9 | Content routing | claims.md asserts; evidence.md sources; views/{overview, counsel, voice/briefing} render audience-specific surfaces |

### `auction-house-consignment-review.kpack` — decline path + cross-pack

| AUTHORING § | Rubric | How the pack demonstrates |
|---|---|---|
| §2-3 | Type and nature | Full mix; the recommendation (C016) is a judgment-shaped *decline* |
| §4 | Source accounts and adopted assessments | C006 preserves the consignor's lifetime-cast account; C007 and C008 state the house's assessment and distinguish its grounds from the catalogue wording, using `↔` to relate the claims. Disagreement over the cast date does not make the source account false. |
| §5 | Confidence assessment | Spread 0.55 to 0.99; SC-12-conformant prediction at C018 (0.55). Values express assessed confidence, not demonstrated empirical calibration. |
| §9 | Content routing | views/{decision (committee), specialist (working notes), consignor-letter (formal-register decline), voice/briefing} — four audience-specific renderings of the same claim graph |
| AR-16 | Cross-pack `↔` | C019 / C020 use `↔` to point at illustrative reference packs (the targets are explicitly disclaimed as not-in-this-repo placeholders demonstrating the grammar; see the pack's Cross-References section note) |

### `kp-external-assessment.kpack` — judgment-heavy meta example

Walks the `nature: judgment` annotation discipline and the §5 confidence-assessment heuristics on a meta-domain. The stated reasons consider investigation depth and the contestability of each claim. The three most-provisional findings (C006, C007, C009) carry confidence in the 0.68-0.78 range; the other assessments sit at 0.89-0.93. These are producer assessments, not measured calibration results.

### `solar-energy-market.kpack` — basic syntax sampler

The first full example. Demonstrates dense + verbose claim metadata, a representative subset of relation symbols (`→`, `⊗~`, `←`; not the full eight — see the matrix above), and a single overview view. Use this to learn the syntax before opening the larger packs. (For a bare copy-this template, use `hello-world.kpack` instead.)

---

## How to use this index

- **Building a parser?** Start with `solar-energy-market.kpack` for the syntax, then run `python3 conformance/run.py --pack examples/solar-energy-market.kpack` (from the repo root) to see the validator pipeline.
- **Authoring a new pack?** Read [`spec/AUTHORING.md`](../spec/AUTHORING.md) alongside `art-acquisition-decision.kpack`; the rubric walkthrough above shows which sections to consult for each authoring decision.
- **Implementing a renderer?** The four domain packs have views; three have multiple views; the audience-specific views in `art-acquisition-decision.kpack` and `auction-house-consignment-review.kpack` show how `display_as` / `purpose` / `register` differentiate audience targeting.
- **Validating cross-pack references?** Only `auction-house-consignment-review.kpack` exercises `↔`. Note the pack's explicit Cross-References disclaimer about illustrative targets.

---

*Reviewed for the released v0.8.5-preview editor's draft. Validate the examples with `python3 conformance/run.py --strict` (29/29 expected for the complete fixture/example suite). These examples illustrate selected features; conformance fixtures supply additional positive and negative cases.*
