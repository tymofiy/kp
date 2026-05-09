<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Authoring — Knowledge Pack Companion Spec

> **Date:** 2026-05-09
> **Status:** Draft (informative — producer-side decision rubrics)
> **Audience:** producers (human or AI) authoring a Knowledge Pack

---

## 1. Purpose

[CORE.md](CORE.md) tells you what a syntactically valid pack looks like. This document tells you **how to make epistemically sound choices** when authoring one.

CORE.md provides closed vocabularies — `o/r/c/i` for claim type, `⊗/⊗!/⊗~` for contradictions, Sherman Kent bands for confidence. CORE.md does not provide the decision rule for picking among them. Without rules, every author invents their own, packs become incomparable across producers, and the format degrades to "Markdown with extra symbols."

This file fills that gap. Each section gives you:

1. **The decision question** — what you are actually choosing between.
2. **A short test** — how to answer the question quickly.
3. **Worked examples** — positive and negative.
4. **Anti-patterns** — common ways producers (especially LLM agents) get this wrong.

If you implement an authoring agent, treat this document as the producer-side authoring guide — the discipline an author should hold themselves to. AUTHORING.md is informative, not normative: the parser does not check it, and `conformance/run.py` will pass packs that violate AUTHORING.md as long as they are syntactically valid. CORE.md is what the parser checks; AUTHORING.md is what the author should check.

> **Note on examples in this document.** Worked examples below are shown in *compact form* — `[C001] headline {metadata} relations` on a single line, without the `- ` list marker — for readability. Real KP:1 claims follow the two-line CORE.md §6.1 grammar: `- [C001] headline\n  {metadata} optional context`. When copying these examples into a real pack, prepend `- ` and break the line after the headline. See `conformance/fixtures/valid/maximal.kpack/claims.md` for the canonical real-pack form.

---

## 2. Claim type — `o` / `r` / `c` / `i`

### Decision question

Where did this claim's *truth status* come from?

### Test

| You answer | The type is |
|---|---|
| "I (or this pipeline) directly observed, measured, or recorded it." | `o` (observed) |
| "A credible external source asserts it, and I am relaying that assertion on the source's authority." | `r` (reported) |
| "It is the result of applying a deterministic operation to other data." | `c` (computed) |
| "It is the result of reasoning over other claims, evidence, or world knowledge." | `i` (inferred) |

### Worked examples

```text
✓ [C001] The 2024 SEC filing for Acme Corp contains the string "going concern" {0.99|o|E001|2025-03-15}
  o: you can open the file and verify the string is present.

✓ [C002] BloombergNEF estimates utility-scale solar LCOE at $0.029/kWh in Q1 2025 {0.85|r|E002|2025-03-15}
  r: BloombergNEF is the asserting source; you are relaying their claim.

✓ [C003] Mean reported price across 12 vendor quotes is $0.044/kWh {0.95|c|E003|2025-03-15}
  c: deterministic average over E003's quoted values.

✓ [C004] The market is approaching grid parity {0.70|i|E001,E002,E003|2025-03-15}
  i: reasoned from the LCOE trend (C002), the spread (C003), and grid-tariff context.
```

### The `o` vs `r` boundary

This is the most-confused boundary. The rule:

- If the claim is *about the source itself* — its contents, what it says, that it exists — that is **observed**. You are reporting your direct perception of the source.
- If the claim is *what the source asserts about the world*, treated as true on the source's authority — that is **reported**. You are relaying.

Example contrast:

```text
[C001] The Reuters article dated 2026-03-15 contains the phrase "voluntary recall" {0.99|o|E001|2026-03-15}
  o: about the article's contents.

[C002] Acme Corp issued a voluntary recall in March 2026 {0.85|r|E001|2026-03-15}
  r: about the world; Reuters is the source asserting it.
```

Both are valid claims. They differ in what is being asserted, and the right type follows from that.

### Anti-patterns

- **Defaulting to `o` for everything you "saw" in training data.** An LLM's training data is not direct observation — it is reported. Use `r` and cite the source, or use `i` and acknowledge it as inferred from training.
- **Using `i` (inferred) when you mean `c` (computed).** A deterministic aggregate (sum, mean, count) is `c`. Reasoning across qualitative claims is `i`. Don't mix.

---

## 3. Claim nature — factual default vs. `judgment` / `prediction` / `meta`

### Decision question

What KIND of statement is this — about empirical reality, about your evaluation of it, about the future, or about other claims?

### Test

| You answer | Annotate as |
|---|---|
| "It is true or false based on observable evidence in the world as it exists." | (omit — factual is the default) |
| "It is my evaluation, opinion, or interpretation; another reasonable analyst could disagree." | `nature: judgment` |
| "It is about a future state of the world." | `nature: prediction` |
| "It is about claims, the pack itself, or the methodology." | `nature: meta` |

### Worked examples

```text
✓ [C001] LVMH Q3 2025 revenue was €19.1B {0.99|o|E001|2025-10-22}
  factual default, no annotation needed.

✓ [C002] LVMH's Q3 result is a strong buy signal {0.65|i|E001,E002|2025-10-22|judgment}
  judgment: this is an evaluation; another analyst could read the same data differently.

✓ [C003] LVMH Q4 2025 revenue will exceed €20B {0.55|i|E001,E002,E003|2025-10-22|prediction}
  prediction: about a future state.

✓ [C004] C002 may be revised when Q4 actuals are released {0.90|i|E001|2025-10-22|meta}
  meta: about another claim.
```

### The factual / judgment boundary

The most common authoring failure is **over-classifying empirical statements as judgments** to satisfy a hedging instinct. RLHF-tuned models in particular default to "I think" / "in my view" framing for assertions that are simply factual.

Test: if the claim could be falsified by a single piece of disconfirming evidence, it is factual.

```text
✗ [C001] LVMH revenue was likely around €19B {0.65|i|E001|2025-10-22|judgment}
  Misuse of judgment. The revenue is reported; cite it directly.

✓ [C001] LVMH Q3 2025 revenue was €19.1B {0.95|r|E001|2025-10-22}
  factual; confidence captures any source-quality concern.
```

Use *confidence* to express uncertainty about factual claims. Use *nature: judgment* only when the claim is intrinsically evaluative — when reasonable analysts with the same evidence would disagree on the conclusion.

### Anti-patterns

- **Annotating standard empirical statements as judgments to seem epistemically careful.** This degrades the pack's factual baseline.
- **Using `prediction` for past-tense statements that happen to mention a future date.** "Acme announced 2027 capacity expansion" is factual (the announcement happened); "Acme will hit 2 GW in 2027" is a prediction.

---

## 4. Contradiction qualifier — `⊗` / `⊗!` / `⊗~`

This is the most novel piece of vocabulary the format offers, and the most often misused.

### Decision question

When two claims are in conflict, which kind of conflict is this?

### Test

| The disagreement is | Use |
|---|---|
| Genuine, but you have not yet determined which side is right. | `⊗` (bare — should be temporary) |
| Investigated; one side is demonstrably wrong; the other side is correct. | `⊗!` (error) |
| Both sides are informative; the disagreement itself is knowledge that should be preserved. | `⊗~` (productive tension) |

### Worked example — the same conflict, three ways

Two sources disagree about a market size: $2B vs $3B.

**Case 1 — `⊗!`** Source A is from 2020 using definition X. Source B is from 2025 using the same definition X. The market grew. A is now wrong (out of date).

```text
[C001] Global widget market is approximately $2B (2020 figure) {0.85|r|E001|2020-12-31|investigated}
[C002] Global widget market is approximately $3B {0.85|r|E002|2025-12-31|investigated} ⊗!C001
```

C001 is now wrong relative to C002. The `⊗!` preserves the audit trail without erasing the prior belief.

**Case 2 — `⊗~`** Source A measures B2B only ($2B). Source B measures B2B+B2C ($3B). Both are correct under their respective definitions; the methodological difference is itself knowledge.

```text
[C001] B2B widget market is approximately $2B {0.85|r|E001|2025-12-31|investigated}
[C002] B2B+B2C widget market is approximately $3B {0.85|r|E002|2025-12-31|investigated} ⊗~C001
```

The `⊗~` records the productive tension. Both claims stay; a downstream analyst reading the pack learns about the methodology gap, not just the numbers.

**Case 3 — `⊗`** Two equally credible 2025 sources, same definition, no obvious methodology difference, both well-researched.

```text
[C001] Widget market is $2B {0.70|r|E001|2025-12-31|investigated}
[C002] Widget market is $3B {0.70|r|E002|2025-12-31|investigated} ⊗C001
```

Bare `⊗` says "they conflict and I haven't resolved it yet." This should be a *transitional* state. Either:

- Investigate further and upgrade to `⊗!` (with one claim moved to history.md) or `⊗~` (with both kept).
- If after exhaustive investigation you still cannot resolve, that itself is `⊗~` — the persistence of disagreement under investigation is informative.

### Anti-pattern: defaulting to `⊗~` for everything

LLMs trained with RLHF tend to default to `⊗~` for any contradiction because it requires no commitment. *"Both perspectives are valuable"* is a path-of-least-resistance answer.

This **degrades the format**. The `⊗!` qualifier exists precisely to record that one belief was wrong. If you've investigated and one side is wrong, mark it `⊗!` even though it requires asserting the wrongness. Preserving false-then-corrected beliefs is the audit trail; that is the format's value proposition.

A useful self-check: in a sealed pack with N contradictions, what fraction are `⊗!`? If the answer is zero, you are probably defaulting to `⊗~` to avoid commitment.

### Anti-pattern: hostile-reading "Agreeable Pack"

An agent optimizing for speed may tag every conflict with `⊗~` to bypass the harder reasoning of `⊗!` triage. Conformance passes, but the pack contains zero actual epistemic rigor.

If your pack has many `⊗~` and zero `⊗!` and zero `⊘`, ask: did I really investigate, or did I optimize for "acceptable to all sources"?

---

## 5. Confidence calibration

CORE.md §8 declares two scales:

- **Sherman Kent**: Certain (0.99+), Almost certain (0.93), Highly likely (0.87), Likely (0.75), Probable (0.63), Even (0.37), Probably not (0.25), Unlikely (0.13), Highly unlikely (0.07), Almost certainly not (0.01), Impossible (<0.01).
- **Simple**: Verified (0.90+), High (0.70), Moderate (0.50), Low (0.30), Unverified (<0.30).

The bands give you *which range* a claim falls in. They do not tell you which value within the range to pick. This section does.

### Within-band calibration

Inside a Sherman Kent band, calibrate by **evidence depth and diversity**:

| Evidence profile | Position within band |
|---|---|
| Single source | Low end of band |
| Two corroborating sources, similar methodology | Mid band |
| Three+ corroborating sources OR direct observation OR cross-method validation | High end |
| Source quality concerns (anonymous, advocacy-shaped, undated) | Notch one band lower |

Example: "Highly likely" band centers on 0.87.

```text
[C001] Acme Corp acquired Widget Inc in March 2025 {0.83|r|E001|2025-03-22}
  Single Reuters article. Highly likely band; low end (0.83).

[C002] Acme Corp acquired Widget Inc in March 2025 {0.87|r|E001,E002|2025-03-22}
  Reuters + WSJ. Mid band (0.87).

[C003] Acme Corp acquired Widget Inc in March 2025 {0.91|r|E001,E002,E003|2025-03-22}
  Reuters + WSJ + Acme's own press release. High end (0.91).
```

### When to use 0.99+

Reserve confidence ≥0.99 for **trivially-falsifiable claims** — assertions an unfamiliar reviewer can verify in seconds.

```text
✓ [C001] The 10-K filing for Acme Corp at SEC EDGAR contains the phrase "going concern" {0.99|o|E001|2025-03-15}
  Falsification: open the filing, search the phrase. <30 seconds.

✓ [C002] The mean of {3.1, 4.2, 3.8, 4.0, 3.5} is 3.72 {0.99|c|E002|2025-03-15}
  Falsification: compute the mean.

✗ [C003] Acme Corp will increase capacity in 2027 {0.99|i|E001|2025-03-15|prediction}
  Predictions cannot be 0.99. Future-state claims have irreducible uncertainty.
```

### Anti-patterns

- **The `0.95` ceiling.** Many LLM-authored packs cluster every claim between 0.85 and 0.95 because those numbers "feel high." The actual distribution should reflect actual evidence — a meaningful pack will have claims at 0.40, 0.60, 0.80, 0.90, 0.99, with the value tied to the evidence profile.
- **Round-number snap.** Confidence values like 0.85 / 0.90 / 0.95 dominate when authors snap to band centers. Aim for two-decimal precision (0.83, 0.87, 0.91) — it forces actual calibration.
- **The Confidence Hallucination.** Emitting 1.0 for every claim because it is "easy to write." Conformance passes; the calibration is meaningless. The schema accepts but the format is degraded.

---

## 6. Depth — `assumed` / `investigated` / `exhaustive`

### Decision question

How thorough was the verification effort behind this claim?

### Test

| Effort profile | Depth |
|---|---|
| Trusted training data, single quick lookup, or unverified working assumption. | `assumed` |
| Read the relevant primary sources; corroborated key facts. | `investigated` |
| Searched the field; no contradiction found in available primary sources. | `exhaustive` |

### Worked examples

```text
[C001] Solar PV global capacity exceeded 1 TW in 2022 {0.85|r|E001|2025-03-15|assumed}
  Single trade-press source; not corroborated.

[C002] Solar PV global capacity exceeded 1 TW in 2022 {0.91|r|E001,E002|2025-03-15|investigated}
  IEA + IRENA both report. Cross-checked.

[C003] Solar PV global capacity exceeded 1 TW in 2022 {0.95|r|E001,E002,E003|2025-03-15|exhaustive}
  IEA + IRENA + BloombergNEF + national grid statistics from top-5 markets. No contradicting source found.
```

### Pack-level honesty

Most packs in early drafts have many `assumed` claims. That is acceptable as long as the depth is **declared honestly**. A pack that marks every claim `exhaustive` to look authoritative is misleading; conformance passes but the producer is lying about effort.

### Anti-pattern

- **Depth inflation.** Marking all claims `investigated` because "investigated" sounds professional. Declared depth should match actual effort.

---

## 7. Supersede vs edit-in-place vs split

When a claim needs to change after a pack version exists, you have three options. They are not interchangeable.

### Decision tree

1. **The new information OPPOSES the old (contradicts the truth value).** → `⊘` supersede. The old claim moves to `history.md`; the new claim takes its slot.
2. **The new information REFINES the old (more specific, narrower scope, additional context, no truth-value change).** → keep both, link the new claim to the old with `~` (refines).
3. **The old claim conflated two distinct assertions, and review now wants them separately addressable.** → split. The old claim is superseded (`⊘`) by two new claims, each with its own ID.
4. **The old claim has a typographical or formatting error and the meaning is unchanged.** → edit in place — but **only if the pack has not been sealed**. Once a `signatures.yaml` has been issued for a version, edit-in-place is forbidden; use `⊘` even for typos so the trail is preserved.

### Worked examples

**Supersede (truth-value change):**

```text
# claims.md (version 2026.05.09)
[C001-v2] Acme Corp Q3 2025 revenue was $4.7B {0.91|r|E007|2026-05-09|investigated} ⊘C001-v1

# history.md
[C001-v1] Acme Corp Q3 2025 revenue was $5.1B {0.85|r|E001|2026-03-15|assumed}
  Superseded 2026-05-09: revised figure from audited 10-K. See C001-v2.
```

**Refine (narrowing or specification):**

```text
[C001] Acme Corp acquired Widget Inc in 2025 {0.87|r|E001|2025-03-15|investigated}
[C002] Acme Corp acquired Widget Inc on March 18, 2025 for $312M {0.91|r|E002|2025-03-15|investigated} ~C001
```

C001 stays; C002 refines the date and price without contradicting the broader fact.

**Split:**

```text
# Old (in history.md)
[C001-v1] Acme Q3 2025 revenue was $4.7B and operating margin was 18% {0.85|r|E001|2025-03-15}

# New (in claims.md)
[C001a] Acme Q3 2025 revenue was $4.7B {0.91|r|E007|2026-05-09|investigated} ⊘C001-v1
[C001b] Acme Q3 2025 operating margin was 18% {0.91|r|E007|2026-05-09|investigated} ⊘C001-v1
```

Both new claims supersede C001-v1; each is independently falsifiable.

### Anti-pattern: silent edit

Editing a sealed claim in place to fix a discovered error destroys the audit trail — the very property the format exists to preserve. Always supersede; the cost is one entry in `history.md`.

---

## 8. Granularity — sizing a claim

A claim should be the **smallest unit that is independently falsifiable**.

### Test

Ask: "Can I disprove just one part of this claim and have the rest still stand?"

- If yes → the claim contains multiple independent assertions; **split**.
- If no → the claim is one indivisible assertion; **right size**.

### Worked examples

```text
✗ Too big — multiple independent assertions:
[C001] The market is large, growing at 26% YoY, dominated by China (80% supply), with cost down 89% since 2010 {0.85|i|E001|2025-03-15}
  Four claims compressed into one. If 2010 cost trajectory is later revised, the entire claim must be superseded.

✓ Right-sized — one assertion each:
[C001] Global widget market is $24B in 2025 {0.85|r|E001|2025-03-15}
[C002] Global widget market grew 26% YoY in 2025 {0.85|r|E002|2025-03-15}
[C003] China produces 80% of global widget supply {0.83|r|E003|2025-03-15}
[C004] Global widget cost has fallen 89% since 2010 {0.87|r|E004|2025-03-15}
```

### The other failure mode — too small

```text
✗ Too small — atomic dust:
[C001] The market exists {0.99|o|E001|2025-03-15}
[C002] The market is large {0.85|i|E001|2025-03-15}
[C003] The market is growing {0.85|i|E001|2025-03-15}
  Each is too vague to falsify or build on. Combine into specific assertions.
```

A useful guideline: a right-sized claim usually fits in a single sentence of 8–25 words, names a specific entity, predicate, and value, and survives the "what would falsify this?" question with a concrete answer.

### Anti-pattern: hostile-reading "Atomic Dust"

An agent that turns every sentence of a source document into an isolated `o` claim with no relations produces a fragmented, queryless cloud of data. Conformance passes; the pack is unusable. Granularity is not just about size — it is about each claim being a load-bearing assertion.

---

## 9. Content routing — `claims.md` / `evidence.md` / `views/`

| File | Contains | Question it answers |
|---|---|---|
| `claims.md` | The assertions. *X is Y because Z.* | What is believed? |
| `evidence.md` | The sources. *Document W on date D says X.* | Where did it come from? |
| `views/` | Pre-rendered presentations of claims for human consumption. | How should it be presented? |

### Routing rules

1. **A direct quote belongs in `evidence.md`.** The claim it backs belongs in `claims.md`.

   ```text
   # evidence.md
   ## E001
   > **type:** research | **captured:** 2025-03-15
   > **source:** BloombergNEF Q1 2025 Renewables Report, p. 14
   "Utility-scale solar LCOE in low-cost markets has fallen to $0.029/kWh, with continued downward pressure from polysilicon overcapacity."

   # claims.md
   [C001] Utility-scale solar LCOE was $0.029/kWh in low-cost markets in Q1 2025 {0.91|r|E001|2025-03-15|investigated}
   ```

2. **A view never asserts knowledge that is not in `claims.md`.** Views derive from claims, not the other way around.

   ```text
   ✗ Wrong — view contains a fact that is not in claims:
   # views/overview.md
   "The market is poised for consolidation, with Acme positioned as the dominant acquirer."
   (No corresponding claim in claims.md.)

   ✓ Right — view is derived from claims:
   # views/overview.md
   "Three claims (C001, C002, C003) together suggest the market is poised for consolidation, with Acme as a likely acquirer."
   ```

3. **Process metadata belongs in evidence or out of the pack entirely.** Notes like *"During our Q1 review meeting we decided…"* are session prose, not knowledge. Either they support a claim (then they are evidence, attributed to that meeting as the source) or they have no place in the pack.

### Anti-pattern: view laundering

The most common form of unsupported assertion is a view that introduces facts the claims file does not contain. Conformance passes (no SC checks views against claims for completeness). The pack is degraded.

A useful self-check: for every assertion in a view, name the claim ID it derives from. If you cannot, remove it from the view or add it to `claims.md`.

---

## 10. Self-check before sealing

Before you seal a pack version (issue a `signatures.yaml`, distribute, or stop authoring), run this checklist.

### Type distribution

- Do you have a mix of `o`, `r`, `c`, and `i` types? A pack of all one type usually means you have not done the routing work.
- Are `r` claims tied to specific named sources in evidence?
- Are `i` claims tied to the lower-level claims they reason from (via `←requires` or in the prose)?

### Confidence distribution

- Is your confidence histogram diverse, or does it cluster at 0.85–0.95? Cluster suggests model self-rating, not calibration.
- Have you used confidence ≥0.99 only for trivially-falsifiable claims?
- Have you used confidence ≤0.5 for any claim that is genuinely speculative?

### Contradiction discipline

- For every contradiction in the pack, did you correctly choose `⊗`, `⊗!`, or `⊗~`? In particular, are there any conflicts you marked `⊗~` only because the choice was hard?
- If your pack has zero contradictions in a domain that has real disagreements, you have flattened the epistemic state.

### Granularity

- Pick three random claims. For each, ask: "What single piece of evidence would falsify this?" If you cannot answer in one sentence, the claim is probably too big.
- Pick another three. For each, ask: "Is this claim load-bearing — does anything else depend on it?" If not, consider whether it should exist.

### Routing

- For every assertion in any view file, can you name the claim ID it derives from?
- For every quote-shaped fragment in `claims.md`, ask: should this be in evidence instead?

### Lifecycle

- For every superseded claim, is the prior version in `history.md` with a supersession reason?
- Are any claims edited-in-place since the last sealed version? If so, supersede instead.

---

## 11. Hostile-reading sanity checks

These are the "look-fine but degraded" patterns to actively avoid:

1. **The Agreeable Pack.** Many `⊗~`, zero `⊗!`, zero `⊘`. → You defaulted to non-commitment. Re-triage.
2. **Atomic Dust.** Hundreds of tiny `o` claims with no relations and no `c` / `i` claims building on them. → No reasoning structure; the pack is data, not knowledge.
3. **Confidence Hallucination.** Every claim at 0.95 or 1.0. → Self-rating, not calibration. Re-distribute against actual evidence depth.
4. **View Laundering.** A polished `views/overview.md` that contains assertions absent from `claims.md`. → The view is making up knowledge. Move assertions to claims or remove from view.
5. **Self-Referential Evidence.** A claim cites `E001`; the `E001` entry's `source` field is "see C001" (the same claim). → Circular justification with no external grounding. The evidence-claim chain must terminate at something outside the pack (a document, a measurement, an interview, a database snapshot). If the source field can only be filled by pointing back at a claim ID, the claim has no real evidence and should either be marked `nature: judgment` or removed. Note: as of v0.8.0-preview, this pattern is editorial-only — the runner does not detect circular evidence; AUTHORING.md flags it.
6. **Future-Date Confidence Inflation.** A claim with `nature: prediction` and `since:` set to a future date carries confidence 0.99+ — the runner now rejects this via SC-12 (predictions MUST have confidence ≤ 0.95). The pattern existed in v0.7 and was caught only editorially; v0.8.0-preview makes it a normative semantic constraint. If you genuinely believe a future-state claim at 0.99+, you are either wrong about confidence or wrong about it being a prediction.

If your pack has any of these patterns, conformance may pass (depending on the pattern — SC-12 catches #6) and the pack may still be epistemically degraded. The format protects against syntactic errors and a small set of named semantic ones; only the author can protect against the rest.

---

## 12. Worked end-to-end transformation

A short example of "raw observation → KP claims" to anchor the rubrics above.

### Source material (raw)

> A Reuters article dated 2025-03-15 reports that Acme Corp's Q3 2025 revenue was $4.7B, up 12% year-over-year, exceeding analyst consensus of $4.5B. The company's CFO stated on the earnings call that Q4 revenue was "very likely" to surpass $5B. Bloomberg's separate analysis of the same earnings suggests the operating margin compression to 16% (from 18% in Q3 2024) reflects a pricing-driven slowdown.

### As KP claims

```text
[C001] Acme Corp Q3 2025 revenue was $4.7B {0.91|r|E001,E002|2025-03-15|investigated}
  Reuters and Bloomberg both report. Two-source corroboration; high band.

[C002] Acme Corp Q3 2025 revenue grew 12% year-over-year {0.91|r|E001|2025-03-15|investigated}

[C003] Acme Corp Q3 2025 revenue exceeded analyst consensus of $4.5B {0.91|c|E001|2025-03-15}
  Computed: 4.7 > 4.5.

[C004] Acme Corp Q4 2025 revenue is likely to exceed $5B {0.65|r|E001|2025-03-15|prediction}
  Reported on the basis of the CFO's statement; downgraded from 0.85 because forward statements on earnings calls have known biases. Prediction nature.

[C005] Acme Corp Q3 2025 operating margin was 16% {0.85|r|E002|2025-03-15|investigated}

[C006] Acme Corp Q3 2024 operating margin was 18% {0.85|r|E002|2025-03-15|investigated}

[C007] Acme Corp's operating margin has compressed by 2 percentage points YoY {0.85|c|E002|2025-03-15}
  Computed from C005 - C006.

[C008] The margin compression reflects a pricing-driven slowdown {0.55|r|E002|2025-03-15|judgment}
  Reported as Bloomberg's analysis (judgment-shaped). Judgment nature; downgraded confidence because Bloomberg's analyst opinion is one read of the data.
```

Note the result:

- Five `r` claims, one `i` would have been wrong here (we are reporting, not reasoning).
- Two `c` claims for arithmetic operations.
- Confidence values span 0.55 to 0.91, calibrated to evidence quality and claim nature.
- One `prediction`, one `judgment`, six factual defaults.
- C003 and C007 are computed and tied to their inputs by evidence ID.
- No contradictions in this pack — both sources agree on the underlying numbers.

A pack like this is what the rubrics aim to produce. It is testably grounded, calibrated, and routes information correctly between claims and evidence.

---

## 13. Relationship to CORE.md

CORE.md is **normative** for syntax. AUTHORING.md is **informative** for judgment. Where they appear to disagree, CORE.md wins on the implementable surface — but if a pack passes CORE.md and violates AUTHORING.md, the pack is syntactically valid and epistemically degraded.

A future revision of the spec may promote some of the rubrics here to enforced semantic constraints (`SC-12` and beyond). For v0.8.0-preview, AUTHORING.md is the producer-side contract; the conformance suite does not check against it.

---

*This file is companion to [CORE.md](CORE.md). Where CORE specifies form, AUTHORING specifies judgment. Both are needed for a sound pack.*
