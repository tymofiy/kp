<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# KP:1 Empirical Benchmark: Pre-Structured vs Inference-Time Epistemic Reasoning

> **Status:** Design specification (ready for implementation)
> **Date:** 2026-04-04
> **Purpose:** Executable benchmark for testing KP:1's core empirical claim
> **Tradeoffs:** Key design decisions and the alternatives considered are recorded in Appendix A.

---

## 1. Hypothesis

**AI systems reason more accurately when consuming KP:1 packs than when
consuming equivalent information in other formats, for tasks that involve
uncertainty, contradiction, and belief evolution.**

This is the central empirical question identified in the KP:1 external
assessment (C005, confidence 0.90) and recommended benchmark direction
(C011, confidence 0.91). The benchmark tests reasoning quality — not
authoring efficiency, encoding compactness, or parse speed.

### What a Positive Result Would Show

Pre-structured epistemic state reduces inference-time cognitive load enough
to measurably improve reasoning accuracy on uncertainty-sensitive tasks.
The comparison across four conditions (Section 3) further isolates whether
any advantage comes from KP:1 specifically or from structured representation
in general.

### What a Negative Result Would Show

LLMs can reconstruct epistemic structure from well-written prose as
effectively as they can consume it pre-structured, weakening KP:1's AI
consumption value proposition. This would not invalidate KP:1 for human
authoring, audit trails, or knowledge management, but it would narrow the
claimed benefits to those domains.

---

## 2. Related Work

**StructRAG** (Li et al., 2024; ICLR 2025). Inference-time hybrid
structurization: a DPO-trained router selects among five structure types
(table, graph, algorithm, catalogue, chunk), converts documents, then
reasons over the result. Evaluated on the Loong benchmark across four
document-length bands (10K--250K tokens). Performance gap over baselines
widens with document length. This benchmark's Condition C adapts
StructRAG's core idea — model-driven structuring before reasoning — to
the epistemic domain.

**KG-LLM-Bench** (Mavi et al., 2025; NAACL 2025). Tests LLMs on five
knowledge graph tasks across different textualization strategies. Choice
of format swings performance by up to 17.5% absolute — confirming that
representation matters.

**GraphRAG-Bench** (Xiang et al., 2026; ICLR 2026). Compares seven
graph-augmented retrieval systems. Vanilla RAG matches GraphRAG on simple
retrieval; GraphRAG wins on complex reasoning and summarization —
pre-structuring helps most for harder tasks.

**Gap this benchmark fills.** No existing evaluation tests pre-structured
*epistemic state* (confidence, typed contradiction, evidence attribution,
investigation depth) against inference-time structuring or other structured
formats. Existing benchmarks focus on entity-relationship structure, not
belief-level metadata.

---

## 3. Experimental Design

### 3.1 Conditions

Each test item is administered under four conditions. All conditions
contain the same factual content derived from the same source dossier
(see Section 5.1). All conditions receive a chain-of-thought instruction
("Reason step by step before answering") appended to the task question,
ensuring reasoning effort is equalized.

| Condition | Label | Description |
|-----------|-------|-------------|
| **A** | KP:1 | `.kpack` format: structured claims with confidence values, typed relations, evidence IDs. Rosetta header included. Prefixed with a 3-example KP:1 reading primer (see Section 3.2). |
| **B** | Enhanced Prose | Well-written analytical text with **explicit uncertainty language** — specific probability ranges ("we estimate a 70-80% likelihood"), named contradiction types ("these findings are in productive tension"), and inline source citations. Not vague hedging — precise analytical writing that encodes the same epistemic judgments in natural language. |
| **C** | Inference-Time Structuring | Two-stage pipeline. **Stage 1:** model receives Condition B text and extracts structured claims, confidence, evidence, and contradictions into a specified JSON schema. **Stage 2:** model receives *only* the extracted structure (not the original text) and answers the task question. This mirrors StructRAG's actual approach: structure first, reason from structure. |
| **D** | Neutral JSON | The same claims, confidence, evidence, and contradictions represented as plain JSON objects — no KP:1 syntax, no Rosetta header, no relation symbols. Tests whether *any* structured format helps, isolating KP:1-specific value from generic structure. |

**Why four conditions.** Without Condition D, a KP:1 advantage could mean
"structure helps" rather than "KP:1 helps." Without two-stage Condition C,
the comparison to StructRAG is not faithful. Without enhanced prose
(Condition B), the information is not equivalent across conditions — vague
hedging carries less information than numeric confidence.

### 3.2 KP:1 Format Primer (Condition A Only)

Because KP:1 syntax is rare in training data, Condition A includes a
system-level primer with three annotated examples showing how to read
claim syntax, confidence values, relation symbols, and evidence references.
This prevents conflating "model can't parse novel syntax" with "structure
doesn't help."

### 3.3 Condition C: Two-Stage Protocol

**Stage 1 prompt:**

```text
Extract the epistemic structure from the text below into the following
JSON format. Be thorough — capture every distinct claim, its confidence
level (0.0-1.0), supporting evidence, investigation depth, claim nature,
and any contradictions.

{
  "claims": [
    {
      "id": "1",
      "statement": "...",
      "confidence": 0.0-1.0,
      "evidence": ["source description"],
      "type": "observed|reported|computed|inferred",
      "depth": "assumed|investigated|exhaustive",
      "nature": "factual|judgment|prediction|meta"
    }
  ],
  "contradictions": [
    {
      "claims": ["id1", "id2"],
      "type": "tension|error",
      "explanation": "..."
    }
  ],
  "dependencies": [
    { "from": "id1", "to": "id2", "relation": "supports|requires|refines" }
  ]
}

Text:
[Condition B enhanced prose]
```

**Stage 2 prompt:** The extracted JSON (from Stage 1 output) is provided
as context, followed by the task question with chain-of-thought
instruction. The original prose is *not* included — the model must reason
from its own extracted structure.

### 3.4 Models

Run on four frontier models (e.g., Claude Opus, GPT-5, Gemini Ultra,
Grok) to enable a clean Latin square with four conditions. Each model is
assigned to conditions via Latin square rotation across *domains* (not
tasks), so every model sees every condition and every domain, but no model
sees the same domain content in more than one condition. This is a
between-item, within-model design. Model is treated as a fixed blocking
factor (too few levels to support a random effect).

Example rotation for 4 models, 6 domains (balanced incomplete block):

| Domain | Model 1 | Model 2 | Model 3 | Model 4 |
|--------|---------|---------|---------|---------|
| Solar | A | B | C | D |
| Chips | B | C | D | A |
| Climate | C | D | A | B |
| Biotech | D | A | B | C |
| Water | A | D | B | C |
| Transport | B | C | A | D |

Each model sees all four conditions across different domains. No model
sees the same domain in more than one condition. Each condition appears
on each domain exactly once across models.

---

## 4. Gold Standard Construction

**This is the most critical methodological decision.** Gold labels must
not come from KP:1 annotations — that would make the benchmark circular
(testing whether models can recover KP:1's own encoding).

### 4.1 Process

1. **Assemble source dossiers.** For each domain, compile the raw source
   materials (research reports, datasets, press releases) that an analyst
   would use. These are the ground truth.

2. **Independent expert assessment.** Two domain experts independently
   read the source dossier (not any KP:1 pack or prose version) and
   produce:
   - A ranked list of claims by certainty, with reasoning
   - Identification and classification of contradictions (tension vs error)
   - Evidence quality ranking
   - Belief update predictions for specified new-evidence scenarios

3. **Agreement check.** Measure inter-rater reliability using
   Krippendorff's alpha (appropriate for ordinal and nominal data).
   Items with alpha < 0.67 are retained with **soft labels** (both raters'
   judgments are recorded as a distribution, not collapsed to a single
   answer). This preserves ambiguous items rather than discarding them —
   ambiguity is where epistemic structure should matter most.

4. **Adjudication.** Items with alpha < 0.40 are reviewed by a third
   expert. If three-way agreement remains below 0.50, the item is
   excluded as genuinely unresolvable.

### 4.2 Scoring Against Soft Labels

For items with high agreement (alpha >= 0.67), scoring uses exact match
against the consensus label. For items with soft labels (alpha 0.40-0.67),
scoring is weighted by rater agreement:

- **Classification tasks** (tension vs error, direction of update): a model
  response matching the majority rater scores 1.0; matching only the
  minority rater scores 0.5; matching neither scores 0.0.
- **Ranking tasks** (uncertainty, evidence): Kendall's tau is computed
  against both raters' rankings and the higher correlation is used,
  discounted by 0.8 (reflecting the inherent ambiguity).
- **Open-ended tasks** (reasoning, synthesis): scored against both gold
  references; the higher score is used, discounted by 0.8.

This avoids the crude "0.5 for matching either rater" rule while still
giving partial credit for genuinely ambiguous items.

---

## 5. Stimulus Creation

### 5.1 Source Dossiers

Six domains provide independent source material. Each dossier is 3-5 raw
documents (reports, papers, datasets) from which all four conditions are
independently constructed.

| Domain | Topic | Claims | Source Material |
|--------|-------|--------|-----------------|
| Solar energy | Utility-scale market trends | 8 | IRENA, BloombergNEF, IEA reports |
| AI chips | Semiconductor supply, accelerator market | 10 | Industry analyses, SEC filings |
| Climate adaptation | Urban resilience strategies | 10 | IPCC, municipal reports |
| Biotech regulation | Gene therapy approval pathways | 10 | FDA guidance, clinical data |
| Water infrastructure | Aging systems, investment gaps | 8 | EPA reports, engineering studies |
| Urban transport | Autonomous vehicle policy | 10 | DOT data, pilot program reports |

Total: ~56 claims across 6 domains, generating ~105 task items.

### 5.2 Master Claim Inventory and Condition Construction

Conditions must encode the same epistemic content in different formats.
Without this guarantee, the benchmark tests authoring quality rather than
format quality. A three-stage pipeline enforces equivalence:

**Stage 1: Master Claim Inventory.** The gold-standard experts (Section 4)
produce a canonical, format-neutral inventory from the raw source dossier.
For each domain, this inventory specifies:
- The exact claims (as plain-language statements)
- Confidence assessments (numeric + reasoning)
- Evidence links (which sources support which claims)
- Contradiction pairs with classifications (tension vs error)
- Investigation depth and claim nature per claim

This inventory is the **single source of truth** for what all conditions
must contain. It is not in KP:1 format — it is a structured spreadsheet
or annotated list.

**Stage 2: Faithful encoding.** Three separate authors each encode the
master inventory into their assigned format:

- **Author A** encodes into KP:1 (Condition A)
- **Author B** encodes into enhanced prose (Condition B)
- **Author D** encodes into neutral JSON (Condition D)
- **Condition C** is derived from Condition B at inference time (the model
  does the structuring)

Each author receives the master inventory and the raw source dossier (for
context and prose quality), but **not** the other conditions. Authors are
instructed to encode the inventory with 100% fidelity — same claims, same
confidence values, same contradictions — using the conventions of their
assigned format.

**Stage 3: Fidelity audit.** An independent auditor (who did not author
any condition) verifies that all conditions contain the same claim
inventory, contradiction inventory, evidence links, and epistemic metadata.
Discrepancies are corrected before any benchmark run. The auditor produces
a parity report documenting any remaining representational differences
inherent to the format (e.g., KP:1 uses relation symbols while prose uses
sentences — this is expected, not a fidelity failure).

This pipeline ensures that format presentation is the sole independent
variable while preventing conditions from being mechanical "translations
of KP:1" — each author applies genuine craft to their format.

### 5.3 Condition B: Enhanced Prose Protocol

1. **Preserve all factual content.** Every claim, evidence source, and
   contradiction in the source dossier must appear.
2. **Use explicit uncertainty language.** Not vague hedging — specific
   ranges: "we estimate a 90-95% likelihood," "this remains a
   low-confidence assessment (roughly 30%)," "the evidence is evenly
   split."
3. **Name contradiction types.** "These two findings are in productive
   tension — both are supported by credible evidence and the disagreement
   itself is informative" vs "this finding likely contains an error, as
   the evidence strongly favors the alternative."
4. **Cite sources by name.** "According to the IRENA 2025 report..."
5. **Match token count.** Within +/- 20% of the KP:1 version.
6. **Quality gate.** An independent reader (who has not seen any other
   condition) rates the prose as clear, professional analytical writing.

### 5.4 Condition D: Neutral JSON Schema

```json
{
  "domain": "solar-energy-market",
  "claims": [
    {
      "id": "1",
      "statement": "Cost decline is structural, not cyclical",
      "confidence": 0.95,
      "type": "inferred",
      "depth": "exhaustive",
      "nature": "judgment",
      "evidence": [
        {"id": "E1", "source": "IRENA Renewable Power Generation Costs 2025", "type": "research"},
        {"id": "E2", "source": "Multi-model synthesis — 10 assessments", "type": "multi_source_synthesis"}
      ],
      "context": "Learning curve (22% cost reduction per doubling) held for 40 years. 10/10 analyses converged."
    }
  ],
  "contradictions": [
    {"claims": ["1", "3"], "type": "tension", "explanation": "..."}
  ],
  "dependencies": [
    {"from": "1", "to": "2", "relation": "supports"}
  ]
}
```

No KP:1 syntax, no Rosetta header, no relation symbols — just standard
JSON that any developer would recognize.

### 5.5 Item Generation

Each domain produces items across task types by:

- **Subsetting:** Different claim subsets per task type
- **Reordering:** Randomized claim order to prevent position bias
- **Difficulty tiers:** Easy (confidence gaps > 0.30), medium (0.10-0.30),
  hard (< 0.10)
- **Uniform handles:** All conditions use neutral identifiers ([1], [2],
  etc.) in task questions so scoring doesn't depend on format-specific IDs

---

## 6. Task Types

### Task 1: Uncertainty Reasoning (20 items)

**Tests:** Can the model rank claims by certainty and explain why?

**Prompt (appended to all conditions):**

> Reason step by step. Identify the three most certain and three least
> certain claims. For each, explain what makes it more or less certain —
> citing evidence quality, source convergence, or investigation thoroughness.

**Scoring:** Top-3/bottom-3 identification (6 pts), reasoning quality per
claim (1 pt per valid justification, max 6). Total: 12 pts.

**Gold:** Expert consensus ranking from source dossier review (Section 4).

### Task 2: Contradiction Navigation (18 items)

**Tests:** Can the model identify contradictions and classify them as
productive tensions vs errors?

**Prompt:**

> Reason step by step. Identify contradictions between claims. For each:
> (a) state which claims conflict, (b) classify as productive tension
> (both perspectives are informative) or error (one side is likely wrong),
> (c) explain your classification based on evidence.

**Scoring:** Identification (2 pts/pair), classification (2 pts/pair),
explanation quality (2 pts/pair). Typically 3 pairs per item = 18 pts.

**Gold:** Expert consensus on contradiction type from source dossier
review.

### Task 3: Evidence Attribution (20 items)

**Tests:** Can the model assess evidence strength and trace support?

**Prompt:**

> Reason step by step. Rank the claims by strength of evidence support.
> For each, identify the supporting evidence and assess its quality
> (source diversity, methodology, recency).

**Scoring:** Kendall's tau with gold ranking (scaled 0-6), evidence
identification (1 pt/claim), quality assessment (1 pt/claim). Total:
~18 pts.

**Gold:** Expert evidence ranking from source dossier. Note: "multi-source
synthesis" is not automatically ranked highest — experts assess actual
methodological rigor, not just source count.

### Task 4: Belief Update (18 items)

**Tests:** Given new evidence, can the model identify which beliefs should
shift and in which direction?

**Prompt:**

> New evidence has emerged: [description]. Reason step by step. Which
> claims should have their confidence revised? For each, state whether
> confidence should increase or decrease, and by roughly how much
> (small / moderate / large).

**Example new evidence (solar domain):**

> Three independent labs report 5-year accelerated aging results for
> perovskite tandem cells with <5% degradation using atomic-layer
> encapsulation.

This should increase confidence in perovskite commercialization viability
and decrease confidence in durability being an unsolved blocker.

**Scoring:** Affected claim identification (2 pts/claim), direction
(1 pt/claim), magnitude calibration (1 pt/claim), stability — no false
flags (2 pts). Total: ~14 pts.

**Gold:** Expert consensus on update direction and magnitude from source
dossier review.

### Task 5: Cross-Pack Synthesis (12 items)

**Tests:** Given two overlapping analyses, can the model synthesize while
preserving tensions and flagging errors?

**Stimulus construction.** For each domain, two variant analyses are
created from the same source dossier by different authors — each sharing
~60% of claims but with different confidence assessments on some shared
claims, 1-2 contradictions between them, and 2-3 claims unique to each.
The model receives both analyses in its assigned condition format.

**Prompt:**

> Reason step by step. Synthesize these two analyses: (a) identify
> agreements, (b) preserve productive tensions, (c) flag likely errors
> with evidence, (d) assess unique claims from each source.

**Scoring:** Agreement identification (3 pts), tension preservation
(4 pts), error flagging (4 pts), unique claim handling (3 pts),
coherence (2 pts). Total: 16 pts.

**Gold:** Reference synthesis produced by an expert working from the
source dossiers only, blind to all four condition formats.

---

## 7. Evaluation Protocol

### 7.1 Automated Scoring

| Component | Method |
|-----------|--------|
| Claim identification | Semantic match (embedding similarity > 0.85 against gold claim text) |
| Ranking accuracy | Kendall's tau rank correlation |
| Classification (tension vs error) | Exact match against gold label; partial credit (0.5) for soft-label items |
| Direction of belief update | Exact match |
| Magnitude calibration | Within one step of gold (small/moderate/large) |

### 7.2 Human Scoring

Reasoning quality and synthesis coherence require human judgment. Two
independent raters score each response using the rubrics above.

**Blinding.** Raters see only the model's response and the task question —
never the condition label, the input format, or the model name. Responses
are stripped of any format-echoing artifacts (e.g., if a model reproduces
KP:1 notation in its answer, that notation is normalized to plain language
before rating). This prevents raters from unconsciously favoring
structured-sounding outputs.

**Calibration.** Before scoring the main benchmark, raters score 10
held-out calibration items (not included in the final analysis) and
discuss disagreements to align on rubric interpretation.

Inter-rater reliability is measured with Krippendorff's alpha (ordinal).
Items with alpha < 0.67 are adjudicated by a third rater.

### 7.3 Statistical Analysis

**Primary model.** Linear mixed-effects regression with:
- **Fixed effects:** Condition (A/B/C/D), Task type, Model (fixed blocking
  factor — too few levels for random effect)
- **Random effects:** Item (intercept), Domain (intercept)
- **Outcome:** Normalized task score (0-1)

This correctly accounts for the fact that items within a domain are
correlated, models have different baselines, and some items are inherently
harder. Avoids the pseudoreplication error of pooling across models and
items as if they were independent observations.

**Planned contrasts** (Bonferroni-corrected):
1. A vs B — Does KP:1 beat enhanced prose?
2. A vs D — Does KP:1 beat generic structure (JSON)?
3. A vs C — Does KP:1 beat inference-time structuring?
4. D vs B — Does any structure beat prose?
5. A vs C by task type — Where does pre-structuring matter most?

**Effect size.** Report Cohen's d for each contrast. Threshold for
meaningful effect: d > 0.3.

**Power.** With ~105 items across 4 conditions and 4 models, the design
yields ~420 scored responses (after averaging reruns). Power adequacy for
detecting d = 0.3 effects should be verified by simulation before
running — simulate data under the mixed-effects model structure with
realistic variance components (estimated from a 10-item pilot) and
confirm that the planned contrasts achieve 80% power at alpha = 0.05.

**Pre-registration.** The five planned contrasts above are the primary
endpoints. All other analyses (interactions, subgroup splits) are
exploratory and reported as such.

---

## 8. Controls

### 8.1 Counterbalancing

Latin square rotation across domains (Section 3.4). Each model sees each
condition on different domains. No model sees the same domain content in
multiple conditions.

### 8.2 Prompt Sensitivity

Two prompt phrasings per task. If phrasing produces significantly different
scores (p < 0.01 after correction), report both and flag the task.

### 8.3 Temperature and Reruns

Temperature 0 (or lowest available). Three runs per item to measure
within-condition variance. The three runs are **averaged into a single
score per item** before entering the statistical model — they do not
count as separate observations. Report per-item mean and standard
deviation as a stability metric alongside the primary analysis.

### 8.4 Contamination Check

Before running, probe all four models on domain-specific facts from each
of the six domains (10 questions per domain, no context provided). If any
domain exceeds 60% accuracy, replace it with a synthetic domain constructed
from fictional but realistic source material.

---

## 9. Outcome Scenarios

| Scenario | Pattern | Interpretation |
|----------|---------|----------------|
| **KP:1 wins broadly** | A > B, A > C, A > D across tasks | Pre-structured epistemic state aids AI reasoning; KP:1 format specifically adds value beyond generic structure |
| **Structure wins, KP:1 ties JSON** | A ≈ D > B > C, or A ≈ D > B ≈ C | Any structured format helps; KP:1's specific syntax is not the driver. Value proposition shifts to authoring discipline and human readability |
| **KP:1 wins on hard tasks only** | A > others on Tasks 2, 4, 5 only | KP:1's value concentrates in relational reasoning (contradiction, update, synthesis) where inference-time reconstruction is hardest. Echoes GraphRAG-Bench findings |
| **Condition C closes the gap** | C ≈ A > B | Inference-time structuring works. Value is in having structure, not who creates it. KP:1's value shifts to authoring efficiency |
| **Prose wins or ties** | B ≈ A, or B > A | KP:1's AI consumption claim is not supported. Format's value narrows to human knowledge management, audit trails, and authoring discipline |

---

## 10. Limitations

**What this benchmark tests:**
- Whether KP:1 format improves model accuracy on uncertainty-sensitive tasks
- Whether the advantage (if any) comes from KP:1 specifically or from
  structure generally (via Condition D)
- Whether inference-time structuring can substitute for pre-structuring
- Whether effects are consistent across models, domains, and task types

**What this benchmark does not test:**
- **Authoring quality** — whether KP:1 is easier or harder to write
- **Retrieval interaction** — stimuli are presented in full, not retrieved
- **Scale** — packs have 8-10 claims; real-world packs may have hundreds.
  StructRAG showed largest gains at 200K+ tokens; a long-context extension
  is the natural follow-up if this benchmark shows signal
- **Authoring fidelity** — assumes competent authoring; a miscalibrated
  KP:1 pack might underperform good prose
- **Human reasoning** — tests AI models only

---

## 11. Implementation Checklist

| Step | Deliverable | Effort |
|------|-------------|--------|
| 1. Compile source dossiers | 6 domains x 3-5 raw documents | 6-8 hrs |
| 2. Recruit domain experts | 2 raters + 1 adjudicator + 1 fidelity auditor | 2 hrs |
| 3. Expert gold-standard + master claim inventories | Rankings, classifications, update predictions, canonical claim inventory per domain | 10-14 hrs |
| 4. Build Condition A (KP:1 packs) | 6 `.kpack` directories from master inventories | 6-8 hrs |
| 5. Build Condition B (enhanced prose) | 6 prose documents from master inventories | 6-8 hrs |
| 6. Build Condition D (neutral JSON) | 6 JSON files from master inventories | 4-6 hrs |
| 7. Fidelity audit + quality gate | Auditor verifies parity; independent reader reviews prose quality | 4-6 hrs |
| 8. Generate task items | ~105 items across 5 task types | 4-6 hrs |
| 9. Power simulation | Simulate mixed-effects model with pilot variance estimates | 2-3 hrs |
| 10. Contamination check | 60 probe questions across 6 domains x 4 models | 1-2 hrs |
| 11. Human-rater calibration | 10 held-out calibration items, rater alignment session | 2-3 hrs |
| 12. Run benchmark | ~105 items x 4 conditions x 4 models x 2 phrasings x 3 runs = ~10,080 API calls | 4-6 hrs |
| 13. Score and analyze | Automated + blinded human rating + mixed-effects modeling | 6-8 hrs |
| 14. Write results | Analysis with tables, effect sizes, interpretation | 3-4 hrs |

**Total effort:** 55-80 hours across all contributors. Approximately two
focused weeks with 3-4 people.

**API cost estimate:** ~10,000 calls at ~2K tokens each = ~20M tokens.
Approximately $70-200 depending on model and pricing tier.

---

## 12. Artifact Summary

| Artifact | Format | Count |
|----------|--------|-------|
| Source dossiers | PDF/Markdown collections | 6 |
| Master claim inventories | Structured spreadsheet/JSON | 6 |
| Expert gold standards | JSON (rankings, classifications, soft labels) | 6 |
| KP:1 packs (Condition A) | `.kpack` directories | 6 |
| Enhanced prose (Condition B) | Markdown | 6 |
| Neutral JSON (Condition D) | JSON | 6 |
| Fidelity parity reports | Markdown | 6 |
| Task items | JSON (question, condition assignments, gold answers) | ~105 |
| Scoring rubrics | This document, Section 6 | 5 |
| Power simulation | R/Python script + results | 1 |
| Results | CSV (raw) + Markdown (analysis) | 1 each |

---

## Appendix A: Design Tradeoffs Considered

The following concerns were identified during pre-implementation review and resolved before this design was finalized. They are recorded here so that anyone implementing or replicating the benchmark can see what alternatives were rejected and why.

### Foundational design

| Concern | Resolution |
|---|---|
| Gold labels derived from KP:1 annotations create circular evaluation. | Gold standards come from independent expert assessment of raw source dossiers (Section 4). |
| Condition B (prose) uses vague hedging while KP:1 uses precise numbers — this is an information asymmetry, not a format difference. | Condition B upgraded to "enhanced prose" with explicit probability ranges and named contradiction types. |
| Condition C is a zero-shot prompt, not faithful to StructRAG's multi-stage pipeline. | Condition C redesigned as true two-stage: extract structure first, then reason only from the extracted structure. |
| No way to isolate KP:1-specific value from generic structural value. | Added Condition D (neutral JSON) as a structure-but-not-KP:1 control. |
| Conditions B and D originally derived from KP:1 packs rather than independently constructed. | Each condition is now built independently from raw source dossiers by separate authors. |

### Statistical design

| Concern | Resolution |
|---|---|
| Repeated-measures ANOVA with pooled model and item observations is pseudoreplication. | Replaced with a linear mixed-effects model with crossed random effects. |
| Three domains are insufficient for generalization; 62 items is a pilot. | Expanded to 6 domains and approximately 105 items. |
| Chain-of-thought confound: Condition C's extraction forces step-by-step reasoning that A and B do not get. | All conditions now receive an explicit "reason step by step" instruction. |
| Internal contradiction between within-subject and between-subject framing across sections. | Clarified as a between-item, within-model design with Latin square rotation across domains. |
| Latin square does not work cleanly with 4 conditions and 3 models. | Expanded to 4 models; uses a balanced incomplete block design (Section 3.4). |
| Power claim asserted without justification. | Power adequacy now requires simulation verification with pilot variance estimates (Section 7.3). |
| Model treated as a random factor with only 4 levels is statistically inappropriate. | Model is now a fixed blocking factor in the mixed-effects specification (Section 7.3). |
| Three temperature-0 reruns could quietly inflate N. | Reruns are averaged into a single per-item score before entering the statistical model (Section 8.3). |

### Stimulus and inventory construction

| Concern | Resolution |
|---|---|
| Independent authors building conditions from raw dossiers will produce different claim inventories — the benchmark would be measuring authoring quality, not format. | Added a master claim inventory stage: experts produce a canonical inventory, authors encode it faithfully, an auditor verifies parity (Section 5.2). |
| Condition C extraction schema initially omitted `depth` and `nature` fields that later tasks score. | Added `depth` and `nature` fields to the Condition C extraction schema (Section 3.3). |
| KP:1 syntax is out-of-distribution for models — poor performance in Condition A could reflect parsing difficulty rather than reasoning quality. | Added a KP:1 format primer with 3 annotated examples for Condition A. |
| Unclear where Task 5's "two overlapping analyses" come from. | Added a stimulus construction note: two variant analyses per domain with ~60% shared claims (Section 6, Task 5). |

### Scoring and rating

| Concern | Resolution |
|---|---|
| Excluding low-agreement items removes exactly the cases where structure should help. | Ambiguous items are retained with soft labels and partial-credit scoring. |
| Cohen's kappa is inappropriate for ordinal human ratings. | Switched to Krippendorff's alpha. |
| "0.5 for matching either rater" is crude for soft labels. | Replaced with differentiated scoring by task type: majority/minority weighting for classifications, best-of-two with discount for rankings and open-ended responses (Section 4.2). |
| Human raters not blinded to condition — subjective scores can absorb format prejudice. | Added a blinding protocol: raters see only responses, not conditions or model names; format artifacts are normalized (Section 7.2). |
| Human raters need calibration before scoring. | Added 10 held-out calibration items and a rater alignment session (Section 7.2). |

---

*This benchmark can show that KP:1 loses. That is the point. A test
designed to confirm a foregone conclusion has no scientific value. The
format's advocates should want to know the truth — and the truth requires
a test that can fail.*
