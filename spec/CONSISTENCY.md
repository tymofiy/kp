<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Cross-Pack Consistency — Knowledge Pack Companion Spec

> **Date:** 2026-03-22
> **Status:** Draft
> **Decisions:** D18 (automated consistency checking)

---

## 1. Purpose

As the number of knowledge packs grows, the same entities appear across multiple packs. Claims about the same entity in different packs can drift, contradict, or become stale independently. Cross-pack consistency checking detects these issues automatically.

---

## 2. Issue Types

| Issue | Description | Example | Severity |
|-------|-------------|---------|----------|
| **Contradiction (unqualified `⊗`)** | Same entity, conflicting claims — not yet assessed | Market pack says "TAM $50B", proposal says "TAM $2B" | High |
| **Contradiction (error `⊗!`)** | One claim is wrong — prioritize resolution | Market size claim uses outdated methodology | Critical |
| **Contradiction (tension `⊗~`)** | Both informative — productive disagreement, do NOT flag | Different methodologies give different TAM; both valid | Skip |
| **Stale claim** | Claim's temporal anchor is old, likely outdated | Team size claim from 6 months ago | Medium |
| **Stale dispute** | Disputed claims (`⊗` or `⊗!`) unresolved for >90 days | Two contradicting claims with no new evidence since January | Medium |
| **Broken reference** | `↔pack_name` points to nonexistent pack | `↔competitor-analysis` but pack doesn't exist | High |
| **Confidence decay** | Low-confidence claim older than 90 days, unreviewed | `{0.70}` from 4 months ago | Low |
| **Orphan pack** | Pack not referenced by any other pack or KNOWLEDGE.yaml | Disconnected pack with no inbound links | Low |
| **Duplicate claims** | Same fact in two packs with different confidence | Both market pack and deployment pack claim team size | Medium |
| **Evidence link rot** | Evidence references a URL or document that no longer exists | Source URL returns 404 | Medium |
| **Provenance contamination** | Process language in claims or views — tool names, meeting names, person requests as justification | Claims.md says "crystallized during the March 24 session" | Medium |
| **Canonical duplication** | Same concept independently defined in multiple packs without cross-reference | Six-layer stack fully restated in pitch pack instead of referencing hub pack | High |

---

## 3. Pack Patrol

Cross-pack consistency checks integrate with the existing patrol system. A new `knowledge` category of checks runs against the `packs/` directory.

### Configuration

```yaml
# config/patrol.yaml (addition)
categories:
  knowledge:
    path: packs/
    checks:
      - cross-pack-consistency    # Same entity, conflicting claims
      - claim-staleness           # Temporal anchor + freshness check
      - reference-integrity       # ↔ cross-references resolve
      - confidence-decay          # Old low-confidence claims
      - orphan-detection          # Packs with no inbound references
      - evidence-link-check       # Evidence URLs/paths exist
      - duplicate-detection       # Same fact in multiple packs
      - provenance-contamination  # Process language in claims or views
      - canonical-duplication     # Same concept defined without cross-reference
```

### CLI

```bash
kpack patrol packs/                           # Run all consistency checks
kpack patrol packs/ --check cross-pack        # Run specific check
kpack patrol packs/ --pack solar-energy-market  # Check one pack against all others
kpack patrol packs/ --fix                     # Interactive fix mode
```

### Output Format

```text
Pack Patrol Report — 2026-03-22

CONTRADICTIONS (2 found)
  ⚠ solar-energy-market.kpack C007 vs competitor-analysis.kpack C003
    market: "TAM is $50 billion" {0.85}
    competitor: "Addressable market is $2 billion" {0.70}
    Likely: different scope (TAM vs SAM). Consider adding scope qualifier.

  ⚠ solar-energy-market.kpack C021 vs solar-deployment-risks.kpack C005
    market: "Team: 7 analysts" {0.95}
    deployment: "Core team: 3 analysts" {0.90}
    Likely: different definition (full team vs core team). Consistent.

STALE CLAIMS (5 found)
  ℹ solar-energy-market.kpack C030 — "polysilicon prices stable" dated 2026-03-01 (21 days)
    Confidence: 0.90. Recommend refresh.

BROKEN REFERENCES (0 found)
  ✅ All cross-references resolve.

ORPHAN PACKS (1 found)
  ℹ solar-storage-economics.kpack — Not referenced by KNOWLEDGE.yaml
    Action: Add to KNOWLEDGE.yaml or link from hub pack.
```

---

## 4. Real-Time Consistency Checking

Beyond scheduled patrol scans, the system supports real-time consistency checking during voice conversations. This is specified in `spec/NOTES.md` §8.

### Architecture

The recording LLM (from the three-LLM architecture) continuously cross-references spoken claims against loaded knowledge packs:

1. A claim is made in conversation (by any participant)
2. Recording LLM matches it against the nearest claim in loaded packs
3. If confidence-weighted distance exceeds threshold → alert
4. Alert delivered via visual channel (Canvas, notification)

### Alert Design

Alerts are **non-accusatory**. They do not say "this is wrong." They say "this doesn't match what we have." The user determines the correct interpretation:

- "Maybe the pack is stale and the spoken claim is the update"
- "Maybe the speaker misspoke"
- "Maybe they're talking about a different scope"

```text
⚠ Pack: solar-energy-market C007 says "TAM is $50 billion" {0.85}
  Spoken: "The market is about $500 million"
  Possible: different scope? Worth clarifying.
```

### Alert Threshold

Only claims with confidence above the configured threshold trigger alerts. Low-confidence claims are already uncertain — alerting on them creates noise.

```yaml
# In PACK.yaml notes section
notes:
  alert_threshold: 0.70    # Only alert when contradicting claims ≥ 0.70
```

---

## 5. Consistency Scan Schedule

| Scan Type | Frequency | Scope | Cost |
|-----------|-----------|-------|------|
| Real-time | During conversations | Loaded packs only | Per-token (recording LLM) |
| On-demand | Manual trigger | Selected packs | Per-scan |
| Nightly | Automated (patrol) | All packs | Per-run |
| Weekly deep | Automated (deep patrol) | All packs, all checks | Per-run |

---

## 6. Suppression

Some contradictions are known and intentional (different methodologies, different scopes). These can be suppressed to avoid repeated alerts:

```yaml
# config/patrol-suppressions.yaml (addition)
knowledge:
  - check: cross-pack-consistency
    packs: [solar-energy-market, competitor-analysis]
    claims: [C007, C003]
    reason: "Different scope — TAM vs SAM. Both correct."
    expires: 2026-06-22    # Re-check in 3 months
```

Suppressions expire. Knowledge changes; a suppression valid today may mask a real problem in six months.

---

## 7. Author Quality Checklist

Run before committing any pack. Six checks, in order:

1. **Knowledge-process separation** ([RATIONALE.md §1, Principle 24](RATIONALE.md)). Remove all names of people, meetings, tools, sessions, and dates from every claim's context prose. If the epistemic content is intact, the claim is clean. If removing a name destroys the meaning, the claim is about process, not knowledge.

2. **No process language in views** ([RATIONALE.md §1, Principle 24](RATIONALE.md)). Views describe what something IS. Grep for: "redesign", "pivot", "shifted from", "session", tool names. Zero hits required.

3. **Canonical ownership** ([RATIONALE.md §1, Principle 18](RATIONALE.md)). Every concept is defined in exactly one pack. If a claim restates content from another pack, it must carry an explicit derivation marker ("Pitch rendering. Canonical: pack#claim") and a `see_also` link to the canonical home.

4. **Meeting/pitch composition.** Meeting and pitch pack claims contain only meeting- or pitch-specific context. Standing knowledge (product architecture, competitive positioning, technical details) is cross-referenced to standing packs, not independently defined.

5. **Display block stranger test** ([RATIONALE.md §4 "The Stranger Test"](RATIONALE.md)). Can someone who has never heard of this product understand the tagline and hook in one reading? No insider jargon, no acronyms requiring context, no process language, no version numbers.

6. **Hub routing, not restating.** Hub pack overview claims summarize and route to detail packs via `see_also` links. If a hub claim contains >3 sentences of detail about a concept that lives in a detail sub-pack, move the detail down.

---

## 8. Pattern Definitions for Automated Checks

Grep-able patterns for the `provenance-contamination` and `canonical-duplication` patrol checks.

### 8.1 Provenance Contamination

**Scope:** `claims.md` context prose (text inside curly braces after metadata, and any following prose) and `views/*.md` content. Evidence files (`evidence.md`) are **exempt** — process provenance belongs there. Meeting pack claims about the meeting itself (who said what, what was decided) are **exempt**.

#### In claims.md context prose

| Pattern Category | Examples | Regex |
|-----------------|----------|-------|
| Person-as-trigger | "[Name] asked", "[Name] requested", "[Name] wanted" | `\b[A-Z][a-z]+\s+(asked|requested|wanted|suggested|proposed)\b` |
| Session attribution | "crystallized during", "decided in the [date] session", "from the [date] meeting" | `\b(crystallized|decided|established|agreed)\s+(during|in|at)\s+(the\s+)?\w+` |
| Tool attribution | "generated by [tool]", "via [framework]", "using NotebookLM" | `\b(generated by|via|using|produced by)\s+[A-Z][a-zA-Z]+` |
| Framework-as-source | "from Positioning Pyramid", "established via [framework]" | `\bfrom\s+[A-Z][a-zA-Z]+\s+(Pyramid|Framework|Canvas|Matrix)\b` |
| Date-process coupling | "the March 2026 redesign", "the Q1 pivot" | `\bthe\s+\w+\s+\d{4}\s+(redesign|pivot|shift|migration|overhaul)\b` |

#### In views/*.md content

| Pattern Category | Examples | Regex |
|-----------------|----------|-------|
| Process verbs as descriptors | "redesign", "pivot", "shifted from", "transitioned to" | `\b(redesign|pivot|shifted from|transitioned to|migrated from)\b` |
| Tool names in non-comment text | "NotebookLM", tool-specific names | `\b(NotebookLM|Positioning Pyramid|GMIV)\b` |
| Session references | "positioning session", "strategic session", "March 24 session" | `\b\w+\s+session\b` |
| Temporal process markers as headers | "## Something (Month Year)" where date marks a decision | `^##\s+.*\([A-Z][a-z]+\s+\d{4}\)` |

#### In PACK.yaml display block

| Pattern Category | Examples | Regex |
|-----------------|----------|-------|
| Version/sprint details | "v0.49", "sprint", "wave", release identifiers | `\bv\d+\.\d+\b\|sprint\|wave\s+\d` |
| Process words | "redesign", "migration" | `\b(redesign\|migration\|overhaul\|pivot)\b` |
| Person attribution | "[Name]'s ask" | `\b[A-Z][a-z]+'s\s+(ask\|request\|requirement)\b` |

### 8.2 Canonical Duplication

**Detection requires cross-pack comparison.** These patterns identify candidates for manual review.

#### Cross-pack claim similarity

| Pattern | Detection Method |
|---------|-----------------|
| Same concept, different packs, no derivation marker | Two claims in different packs with the same noun phrase in the assertion headline AND no derivation marker in context ("Pitch rendering", "Hub-level summary", "Meeting-specific") |
| Verbose cross-reference without link | A non-hub pack claim containing >3 sentences of descriptive context about a concept with a canonical home in another pack, without a `see_also` link |
| Standing knowledge in meeting packs | Meeting pack claims that define product architecture, competitive positioning, or technical details rather than meeting-specific context (who said what, what was decided, what actions were agreed) |

#### Single-pack self-duplication

| Pattern | Detection Method |
|---------|-----------------|
| Hub restating detail | A hub pack claim with >3 sentences of detail about a concept that should live in its detail sub-pack |

#### Derivation markers (valid — do not flag)

Claims containing these phrases in their context prose are legitimate cross-references:
- "Pitch rendering. Canonical: ..."
- "Hub-level summary. See ..."
- "Meeting-specific context. Standing knowledge at ..."
- Any `see_also` link to the canonical pack

### 8.3 Formatting Hygiene

Grep-able patterns for text hygiene checks across `claims.md` files.

| Check | Pattern | Description | Exceptions |
|-------|---------|-------------|------------|
| Orphaned relations | `^\s{2}[→⊗←~⊘↔]\S` | Standalone relation line that should be merged onto preceding context line | Lines where `~` means "approximately" (e.g., `~8,400`), prose flow arrows (e.g., `→portfolio→certificate`), or pipeline descriptions (e.g., `→ Provenance → Compliance`) |
| Mid-sentence breaks | `^\s{2}[a-z]` | Continuation line starting with a lowercase letter that isn't a relation symbol — likely a broken sentence | Legitimate multi-line context prose (most continuation lines are valid; flag only when the preceding line ends mid-word or mid-phrase) |
| ASCII arrows in claims | `->` or `<-` in claims context | Should use Unicode `→` and `←` for KP:1 relation symbols | Prose flow descriptions (e.g., `Discovery -> Definition -> Execution`), environment variable cascades, code examples |
| Verbose see_also | `↔see_also\s` | Should use compact `↔pack#claim` format | None — always normalize |
