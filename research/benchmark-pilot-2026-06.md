<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# KP:1 Benchmark Pilot: Format Readability (2026-06)

> **Status:** Pilot results — first empirical data point for the benchmark
> programme in [benchmark-design.md](benchmark-design.md)
> **Date:** 2026-06-10
> **Verdict:** **No format effect detectable at this scale.** Both frontier
> subjects scored a perfect 1.000 in every condition — KP:1, enhanced
> prose, and neutral JSON alike. Under the pre-registered decision frame
> this is "no signal yet"; the ceiling itself is the actionable finding,
> and prose carried the same content in materially fewer tokens.
> **Scope warning:** a pilot supports "worth a bigger run" or "no signal
> yet" — never "proven." This document reports the result that cuts
> against the format's claim with the same prominence it would have given
> a positive one.

---

## 1. Question

Do AI models read **epistemic state** — confidence levels, contradiction
classes, supersession history — more accurately from a KP:1 pack than from
the same content in well-written analytical prose or in neutral JSON?

This is the *readability* half of the benchmark programme's central claim.
It is deliberately narrower than the full design's *reasoning-quality*
question: because the pilot derives all conditions from the packs
themselves (Section 2.3), gold answers are the packs' own encoded values.
The pilot therefore measures how reliably models can extract epistemic
state from each format — not whether the state itself is well-calibrated
against the world. The full design (Sections 4–5 of benchmark-design.md)
addresses the latter with independently authored conditions and expert
gold standards; that machinery is not instantiated here.

## 2. Method

### 2.1 Design

2 domains × 2 models × 3 conditions × 26 questions = 156 stateless calls,
one question per call. Full factorial: every model saw every condition on
every domain. (The full design's Latin square exists to stop a model from
seeing the same domain twice *within a session*; stateless single-question
calls make that contamination structurally impossible, so the rotation is
unnecessary at pilot scale.)

### 2.2 Conditions

| | Content | Format |
|---|---|---|
| **A** | the pack's `claims.md` + `evidence.md`, verbatim | KP:1, with a short reading primer (per design §3.2) built from the repo's `hello-world.kpack` |
| **B** | same content, derived | enhanced prose per design §5.3: explicit percentages, named contradiction types ("productive tension, not an error"), inline sources, supersession in words |
| **D** | same content, derived | neutral JSON per design §5.4: claims/contradictions/dependencies/evidence arrays, no KP:1 syntax |

Condition C (two-stage inference-time structuring) is deferred to the full
run. Condition labels follow the design document.

**Substrate:** the two public example packs —
[`solar-energy-market.kpack`](../examples/solar-energy-market.kpack/) (8
claims, one declared tension, no supersession) and
[`art-acquisition-decision.kpack`](../examples/art-acquisition-decision.kpack/)
(22 claims; error-class contradiction, tensions, supersession, all four
claim types, judgment/prediction/meta natures).

### 2.3 Derivation and equivalence

Conditions B and D were derived mechanically from the packs (parser →
master inventory → generated JSON; prose authored from the inventory in
pack order), then audited: every confidence value (as a percentage), every
claim and evidence date, every source name, and every depth/nature marker
verified present in B by script; relations and contradiction types carried
in words. Six inline KP:1-specific cross-references (e.g. a claim ID
mentioned inside another claim's context) were neutralized via an explicit
replacement map, with a fail-closed guard against any surviving KP:1 token
in B or D.

Size parity (design §5.3 rule 5, gated on characters as the closest
offline token proxy): B/A = 1.11 (solar), 1.04 (art). Word ratios 1.26 and
1.15 — prose spends words where KP:1 spends symbols. Measured token usage
from the actual runs appears in Section 3.3.

Known cost of this derivation strategy: it guarantees content equivalence
but not authoring independence — one author derived all three conditions.
The full design's three-author + fidelity-auditor pipeline addresses this;
a pilot cannot.

### 2.4 Models

Two frontier models from different major providers — **Claude
(Anthropic)** and **GPT (OpenAI)**, current frontier versions as of June
2026 — as subjects, and a third-family grader, **Gemini (Google)**, so no
response is graded by its own model family. Exact pinned model
identifiers, per-call settings, and raw transcripts are retained in the
editor's run records and are available on request; this report
deliberately names model families rather than versions because the format
question is provider-independent and version names go stale.

Both subjects rejected an explicit temperature-0 setting (the parameter is
deprecated or restricted on current flagships); both ran at provider
default temperature, recorded per call. Each question was asked once per
cell (no reruns — within-cell stability is not measured; see Limitations).

### 2.5 Questions and scoring

26 pre-registered questions across four bands:

| Band | n | Tests |
|---|---|---|
| recall (control) | 8 | plain fact extraction — no format effect expected |
| calibration | 8 | reading/comparing stated confidence, incl. two items with 0.02–0.03 confidence gaps |
| contradiction | 6 | identifying conflicts and their declared class (tension vs error) |
| dynamics | 4 | supersession history (art); declared dependency (solar — that pack contains no supersession) |

Every question has a gold answer and an explicit 0 / 0.5 / 1 rubric, both
fixed before the first model call (the question set and rubrics are
published alongside this report). Each prompt appends the same
chain-of-thought instruction in all conditions (design §3.1) and an
instruction to answer only from the document.

The grader scored all 156 responses against the rubrics, blind to
condition and model (it saw only question + gold + rubric + response
text). A stratified 23% spot-check (36 of 156, six per condition × model
cell, seeded sample) was reviewed independently of the grader; the human
editor's pass is recorded in Section 3.4.

### 2.6 Pre-registration

The question set, rubrics, analysis plan (contrasts, bootstrap procedure,
decision frame), and model/settings table were committed to the project's
private session records before the first pinned call, with one documented
pre-run amendment (subject model upgraded to the provider's latest
flagship; public naming policy; spot-check timing). The pre-registered
primary endpoints are exactly the two contrasts reported in Section 3.1.

## 3. Results

### 3.1 Pre-registered primary contrasts: exact zero, at ceiling

All 156 responses scored 1.0. Every cell of the design — both models,
all three conditions, all four bands, both domains — is at ceiling.

| Contrast (paired over questions × models) | Band set | Mean diff | 95% CI* | n pairs |
|---|---|---|---|---|
| A−B (KP:1 − prose) | epistemic composite (18q) | 0.000 | [0.000, 0.000] | 36 |
| A−D (KP:1 − JSON) | epistemic composite (18q) | 0.000 | [0.000, 0.000] | 36 |
| A−B | recall control (8q) | 0.000 | [0.000, 0.000] | 16 |
| A−D | recall control (8q) | 0.000 | [0.000, 0.000] | 16 |

*Cluster bootstrap over questions, 10,000 resamples. With zero variance
the intervals are degenerate — reported for protocol fidelity, not
information.

### 3.2 The ceiling is real, not a grading artifact

The pre-registered hard items were answered correctly — with the right
values cited — in every condition by both subjects. On the 0.02-gap item
("which is held with higher confidence: the attribution (0.91) or the
1962 dating (0.93)?") both models, in all three formats, picked the dating
and cited both numbers. Multi-element open-ended items (supersession
rationale, the 1957 dating's origin-withdrawal-status history, the
evidential asymmetry behind the declared tension) were answered completely
in all cells. The grader's perfect scores trace to genuinely correct
answers, not leniency.

### 3.3 Token economics (exploratory): prose is the cheapest carrier

Mean input tokens per call, from API usage (Condition A includes its fixed
reading primer):

| Model · domain | A (KP:1) | B (prose) | D (JSON) |
|---|---|---|---|
| Claude · solar | 3,514 | 2,258 | 2,953 |
| Claude · art | 5,584 | 3,980 | 6,101 |
| GPT · solar | 2,424 | 1,406 | 2,077 |
| GPT · art | 3,951 | 2,571 | 4,381 |

Differencing the two domains cancels the primer and the prompt template,
giving a format-only comparison on the art pack's content increment over
the solar pack's: that increment cost **+20–31% more tokens in KP:1 than
in prose**, and **+83–98% more in JSON than in prose** (range across the
two providers' tokenizers). Output-token differences were trivial and
directionally inconsistent across models (≤35 tokens between conditions).

For the same epistemic content at this scale, enhanced prose is the most
token-efficient carrier; KP:1 also pays a fixed primer overhead that can
only amortize over larger packs.

### 3.4 Grading verification

Grader agreement on the stratified 36-item sample: 36/36, twice over —
the pilot operator's independent pass and the editor's human spot-check
each confirmed every sampled grade.

## 4. Reading the result

Under the pre-registered decision frame this is **"no signal yet"** — and
the specific shape of the null is informative:

1. **At small-pack scale, frontier models do not need pre-structured
   epistemic state to read epistemic state.** Given explicit confidence
   numbers, named contradiction types, and supersession stated in words,
   current flagships extract all of it from prose exactly as reliably as
   from KP:1 — and from neutral JSON too. This matches the design
   document's outcome row "Prose wins or ties": at this scale, the AI
   consumption advantage claim is **not supported**.
2. **The test as instantiated had no headroom.** 8–22 claims in a
   3–6K-token document, questioned directly, is simply not hard enough to
   discriminate between formats for models of this strength. A perfect
   board is a statement about the task's difficulty as much as about the
   formats.
3. **What survives at this scale is not accuracy but cost — and it favors
   prose.** The same content costs 20–31% more tokens in KP:1 and 83–98%
   more in JSON (Section 3.3). KP:1's near-term case therefore rests on
   the things this pilot did not test: authoring discipline, human
   readability, audit trails, diff-ability, composition — and on possible
   accuracy effects at scales and difficulties this pilot could not reach.

What this does *not* establish: that format never matters. Related work
found representation effects concentrated in harder regimes — long
contexts (StructRAG's gains grew with document length), complex relational
reasoning (GraphRAG-Bench), and format swings of up to 17.5% on knowledge
graph tasks (KG-LLM-Bench). The pilot's regime — short documents, direct
questions, frontier models — is exactly where those effects would be
smallest.

## 5. Limitations

1. **Readability, not reasoning-vs-world.** Gold answers are the packs' own
   encoded values (Section 1). A model could score perfectly here and still
   reason badly from a miscalibrated pack.
2. **Derived conditions, single author.** Content equivalence is guaranteed
   by construction; authoring independence is not. Prose quality is one
   author's craft, audited mechanically.
3. **Small n.** 18 epistemic questions × 2 models; at ceiling the CIs are
   degenerate and per-band splits are descriptive only.
4. **Two models, one run each.** Provider-default temperature (explicit 0
   rejected by both current flagships); no rerun stability estimate. At
   ceiling, rerun variance could only have moved scores down, not up.
5. **Parametric-knowledge leakage.** The art pack is explicitly fictional
   (anonymized); the solar pack cites real 2026 reports, but every question
   targets the pack's *encoded state* (its confidence values, its declared
   relations), which no model can know from pretraining. Recall-band
   questions about real-world solar facts are the most exposed; the
   instruction "answer only from the document" plus the control-band
   framing mitigate but do not eliminate this.
6. **LLM grader.** Rubrics are tight and the scores were spot-checked
   (Section 3.4), but responses can echo their input format, so the grader
   is blind to condition labels yet not necessarily to format style. With
   every score at 1.0 and verified correct on the sampled items, grader
   bias had no room to shape the result.
7. **Two domains, small packs.** Both packs are small (8 and 22 claims).
   Structure effects concentrate at scale; this pilot cannot see that
   regime.

## 6. Next step

The cheapest discriminating experiment is **a headroom probe before any
full-design build**: construct one deliberately hard instance — a pack of
one-to-several hundred claims (or several overlapping packs with
distractor content and cross-pack tensions, per the design's Task 5) — and
confirm sub-ceiling performance on direct readability questions. Only
where models fall off the ceiling can the four-condition comparison
(including the deferred Condition C, inference-time structuring) say
anything. Two further cheap probes suggested by this pilot:

- **Weaker models.** If smaller models fall off the ceiling, format
  effects may appear there first — relevant because packs are also meant
  to be consumed by small local models, not only flagships.
- **Indirect tasks.** The full design's belief-update and synthesis tasks
  (Tasks 4–5) require *using* the epistemic state, not just reading it —
  plausibly harder, and untouched by this pilot.

The full six-domain build (independent authoring, expert gold standards,
~10,000 calls) should wait until a headroom probe shows the measurement
instrument can register a difference at all.

---

## Appendix A: per-band and per-domain scores

All cells 1.000: every band (recall 8q, calibration 8q, contradiction 6q,
dynamics 4q) × every condition (A, B, D) × both models × both domains.
The full per-item score matrix ships in `pilot-2026-06/scores.csv`.

## Appendix B: artifacts

Published alongside this report in `research/pilot-2026-06/`:

- `questions.json` — the 26 pre-registered questions, gold answers, rubrics
- `solar-prose.md`, `art-prose.md` — Condition B documents
- `solar-neutral.json`, `art-neutral.json` — Condition D documents
- `kp1-primer.md` — the Condition A reading primer
- `scores.csv` — per-item scores with per-call input-token counts

Condition A is the packs themselves (`examples/`). Raw transcripts and
pinned model identifiers are retained in the editor's run records,
available on request.
