<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Composition Specification

> **Status:** Draft
> **Date:** 2026-03-22
> **Editor:** Timothy Kompanchenko
> **Parent:** [SPEC.md](../SPEC.md) v0.4, Design Principle 18
> **Implements:** Decision D14 (Meeting pack composition, agenda overlay, pre_load/on_demand)

---

## 1. Overview

Composition defines how **composite packs** reference standing packs rather than duplicating their knowledge. A composite pack is a lens -- an agenda-shaped, purpose-shaped, or narrative-shaped view over existing packs, augmented with context-specific additions.

The canonical example is a **meeting prep pack**: it references the standing packs relevant to the meeting's agenda, adds meeting-specific claims (who, when, where, what to discuss), and defines a loading strategy that matches the meeting's conversational flow.

### The Core Insight

Knowledge lives once, in its canonical pack. A meeting about supply chain diversification does not need a copy of the supply chain claims -- it needs a reference to `supply-chain-diversification.kpack` with a focus on the three claims most relevant to today's agenda. When the meeting produces new knowledge, that knowledge promotes back to the standing pack, not buried in a meeting archive.

### What Composition Solves

| Problem | Without composition | With composition |
|---------|-------------------|-----------------|
| Meeting prep duplicates standing knowledge | Pack author copies claims into meeting pack | Meeting pack references standing pack by name |
| Post-meeting knowledge is trapped | New facts stay in an ephemeral meeting pack | New claims promote to standing packs via reconciliation |
| Voice assistant has no navigation plan | LLM loads everything or guesses what's relevant | `composition.yaml` declares pre_load, on_demand, and agenda structure |
| Context budget is wasted | Full standing packs loaded regardless of meeting focus | `focus_claims` narrows what gets loaded from each pack |

---

## 2. composition.yaml

An optional file in any `.kpack/` directory that declares the pack's composition structure. Its presence signals that this pack is a composite -- it references other packs rather than containing all knowledge directly.

### Meeting Prep Example (Full)

```yaml
type: meeting-prep

meeting:
  date: 2026-03-24T14:00:00-04:00
  duration: 60m
  participants: [Jane, Dr. Webb]
  location: video-call
  context: >
    Quarterly advisory review. Dr. Webb is a senior energy
    sector advisor. He needs thorough updates on all
    active research threads and market developments.

agenda:
  - topic: "Market forecast update"
    reference: "solar-energy-market"
    focus_claims: [C001, C003, C030]
    talking_points:
      - "Cost floor thesis debate"
      - "Supply chain concentration risk update"

  - topic: "Perovskite technology assessment"
    reference: "perovskite-assessment"
    talking_points:
      - "Oxford PV durability results"
      - "Timeline for commercial viability"

  - topic: "GridScale partnership"
    reference: "gridscale-partnership"
    focus_claims: [C001, C010]
    talking_points:
      - "Proposed co-development structure"
      - "Due diligence timeline"

  - topic: "Regulatory landscape"
    reference: "regulatory-landscape"
    talking_points:
      - "IRA incentive reclassification"
      - "EU Carbon Border Adjustment impact"

pre_load:
  - solar-energy-market
  - perovskite-assessment

on_demand:
  - gridscale-partnership
  - regulatory-landscape
  - supply-chain-diversification
  - competitor-analysis
  - solar-storage-economics
```

### Field Reference

#### Top-Level Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `type` | Yes | enum | Composition type. See section 7 for all types |
| `meeting` | If type = `meeting-prep` | object | Meeting metadata |
| `agenda` | If type = `meeting-prep` | list | Ordered agenda items |
| `pre_load` | Yes | list of strings | Pack names to load before the session begins |
| `on_demand` | No | list of strings | Pack names available for loading when topics arise |

#### `meeting` Object

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `date` | Yes | ISO 8601 datetime | Meeting start time with timezone |
| `duration` | Yes | duration string | Expected duration (`30m`, `60m`, `2h`) |
| `participants` | Yes | list of strings | People in the meeting |
| `location` | No | string | `video-call`, `in-person`, `phone`, or address |
| `context` | No | string | Background context for the AI about this meeting |

#### `agenda` Items

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `topic` | Yes | string | Human-readable agenda item title |
| `reference` | No | string | Pack name this topic draws from. Uses `name` from KNOWLEDGE.yaml |
| `focus_claims` | No | list of claim IDs | Specific claims from the referenced pack to emphasize |
| `talking_points` | No | list of strings | Key points to cover under this topic |

#### Loading Lists

`pre_load` and `on_demand` contain pack names (the `name` field from KNOWLEDGE.yaml or PACK.yaml). The consuming system resolves these to pack paths.

- **pre_load** packs are loaded into context before the session begins. The AI starts the meeting already knowledgeable about these domains.
- **on_demand** packs are available but not loaded until the conversation enters their territory. This preserves context budget for what matters now.

---

## 3. claims.md in Composite Packs

A composite pack's `claims.md` is intentionally minimal. It contains claims about the **composition context** itself -- not about the topics being composed.

### What Belongs in a Meeting Pack's claims.md

- Claims about the meeting: who, when, why, what changed since last meeting
- Claims about relationships between participants and topics
- Claims about desired outcomes or decisions needed
- Claims about constraints (time pressure, sensitivity, pending deadlines)

### What Does NOT Belong

- Facts about the solar energy market (those live in `solar-energy-market.kpack`)
- Facts about perovskite technology (those live in `perovskite-assessment.kpack`)
- Facts about the GridScale partnership (those live in `gridscale-partnership.kpack`)

### Example: Meeting Pack claims.md

```markdown
<!-- KP:1 -- Knowledge Pack Format
Claims: - [ID] assertion {confidence|type|evidence|date} context
Types: o=observed r=reported c=computed i=inferred
Relations: ->supports *contradicts <-requires ~refines /supersedes <->see_also
Files: evidence.md=sources history.md=past entities.md=graph composition.yaml=references
-->
---
pack: webb-advisory-2026-03-24 | v: 2026.03.24 | domain: meetings/advisory
confidence: simple | normalized
---

# Webb Advisory Review [meeting|2026-03-24]

> Quarterly advisory session. Thorough update on market outlook, technology bets, and partnerships.

## Meeting Context

- [M001] Quarterly advisory meeting with Dr. Webb, scheduled March 24 2:00pm
  {0.99|o|E001|2026-03-22}

- [M002] Last meeting was February 10 -- six weeks since last sync
  {0.95|o|E002|2026-03-22} Longer-than-usual gap. Extra context on Q1 developments needed.

- [M003] GridScale partnership timeline shifted from March to May
  {0.85|r|E003|2026-03-20} Webb may not be aware of the delay.
  <->gridscale-partnership#timeline

- [M004] Decision needed: GridScale co-development terms and due diligence scope
  {0.90|i|E003|2026-03-22} Webb's input on deal structure before GridScale meeting.
  <->gridscale-partnership

- [M005] Polysilicon supply concentration is the outstanding strategic risk
  {0.90|i|E004|2026-03-22} Webb has contacts at alternative suppliers -- ask about sourcing options.
  <->supply-chain-diversification#risks
```

Notice: every claim is about the meeting situation, not about the referenced domains. The `see_also` symbols point to where the domain knowledge lives. The AI loads those packs to become knowledgeable; the meeting claims tell it what to do with that knowledge in this context.

---

## 4. Voice Assistant Integration

Composition is designed to work with the three-process voice architecture described in SPEC.md section 15 and the v2 vision document.

### The Three Processes

| Process | Role in composition | What it reads |
|---------|-------------------|---------------|
| **Voice LLM** | Conversational partner, uses composition for navigation | `composition.yaml` (agenda, talking points), pre_load pack claims |
| **Recording LLM** | Background structured capture, writes new claims | `composition.yaml` (agenda structure for organizing captures) |
| **Intelligence LLM** | On-demand deep analysis when dispatched | Relevant pack claims + conversation context |

### Pre-Meeting: Loading

1. System reads `composition.yaml`
2. All `pre_load` packs are loaded into the Voice LLM's context
3. For each agenda item with `focus_claims`, those specific claims are highlighted (the Voice LLM knows these are the most relevant points)
4. `on_demand` pack names are noted -- the Voice LLM knows they exist but their claims are not yet in context
5. The `meeting.context` field provides situational awareness

### During Meeting: Navigation

The Voice LLM uses the `agenda` list as a navigation structure:

1. **Topic tracking.** As conversation moves between topics, the Voice LLM maps utterances to agenda items. This is approximate -- conversations are not linear.

2. **On-demand loading.** When conversation enters an `on_demand` topic, the system loads the referenced pack. The Voice LLM signals: "Loading the supply chain diversification details now."

3. **Talking point coverage.** The Voice LLM can track which talking points have been covered and which remain. Near the end of the meeting, it can note: "We haven't discussed the regulatory landscape updates yet."

4. **Focus claim emphasis.** When discussing a topic with `focus_claims`, the Voice LLM prioritizes those specific claims in its responses. Other claims in the referenced pack are available but secondary.

5. **Cross-topic connections.** When a claim in one agenda topic relates to another topic (via `see_also` or shared entities), the Voice LLM can surface the connection: "That connects to what we discussed about supply chain concentration earlier."

### During Meeting: Recording

The Recording LLM operates as a background process, receiving the transcript stream. Composition gives it structure:

1. **Agenda-organized capture.** New claims are tagged with the agenda item they arose from. The recording LLM uses the `agenda` list to categorize captures.

2. **Standing pack awareness.** The Recording LLM knows which standing packs exist (from `pre_load` and `on_demand`). When it captures a new claim, it can annotate which standing pack the claim should eventually promote to.

3. **Decision vs. discussion.** The Recording LLM distinguishes between decisions (high confidence, actionable) and discussion (lower confidence, exploratory). Decisions get immediate structured capture; discussion is noted but not over-structured.

4. **Contradiction detection.** When a participant states something that contradicts a claim in a loaded standing pack, the Recording LLM flags it. This is a signal, not an interruption -- the Voice LLM decides whether and when to surface it.

### Post-Meeting: Promotion

After the meeting ends, the Recording LLM's captures go through promotion:

1. **Per-agenda-item review.** For each agenda item, review captured claims.

2. **Standing pack routing.** Each new claim is routed to its canonical standing pack based on the `reference` field in the agenda item.

3. **Claim creation.** New claims are drafted for the standing pack with:
   - Evidence referencing the meeting (date, participants, recording if consented)
   - Confidence appropriate to the claim type (decisions get high confidence; impressions get lower)
   - `see_also` back to the meeting pack for provenance

4. **Meeting pack archival.** Once promotion is complete, the meeting pack is a historical record. Its lifecycle type is `ephemeral` -- it archives according to the schedule in its `PACK.yaml`.

### Example: Post-Meeting Promotion Flow

Meeting claim captured by Recording LLM:
```text
GridScale timeline moved to June. Webb recommends waiting until after
their Q2 earnings report. Decision: Jane will propose June 15 meeting date.
```

This promotes to `gridscale-partnership.kpack/claims.md` as:
```markdown
- [C015] GridScale meeting target date: June 15, after Q2 earnings release
  {0.90|r|E040|2026-03-24} Decision from Webb advisory session.
  Webb recommended delay; Jane to propose. ~C012
```

With evidence in `gridscale-partnership.kpack/evidence.md`:
```markdown
## E040
> **type:** meeting | **captured:** 2026-03-24
> **source:** Webb advisory session, 2026-03-24 (Jane, Dr. Webb)

Decision during quarterly advisory meeting. Webb noted GridScale
is releasing Q2 earnings in early June. Consensus to target
June 15 for next meeting.
```

The meeting pack retains its original claims as a historical record. The standing pack gains the new knowledge with full provenance.

---

## 5. PACK.yaml for Composite Packs

Composite packs declare their composition nature in PACK.yaml:

```yaml
name: webb-advisory-2026-03-24
version: 2026.03.24
domain: meetings/advisory
author: Jane Chen
tier: standalone

description: >
  Quarterly advisory review with Dr. Webb. Covers solar market
  forecast, perovskite assessment, GridScale partnership,
  and regulatory landscape.

confidence:
  scale: simple
  normalize: true

freshness: 2026-03-24
sensitivity: internal

lifecycle:
  type: ephemeral
  archive_after_days: 30
  archive_policy: reconcile

notes:
  mode: active
  participants: [Jane, Dr. Webb]
  disclosed: true
  consent: obtained

# Composition reference -- see composition.yaml for full structure
composition: composition.yaml
```

The `composition` field in PACK.yaml points to the composition file. Its presence tells tooling and consumers that this is a composite pack.

### Lint Rules for Composite Packs

- Every pack name in `pre_load` and `on_demand` must resolve via KNOWLEDGE.yaml
- Every `reference` in agenda items must be either a `pre_load` or `on_demand` pack
- `focus_claims` must reference valid claim IDs in the referenced pack (warning, not error -- claims may have been superseded)
- Meeting date must be a valid ISO 8601 datetime
- Participants list must not be empty

---

## 6. Relationship to Standing Packs

### Composition is Not Dependency

The `composition.yaml` references are distinct from PACK.yaml `dependencies`:

| | `dependencies` (PACK.yaml) | `pre_load` / `on_demand` (composition.yaml) |
|-|---------------------------|---------------------------------------------|
| **Meaning** | This pack builds on that pack's claims | This pack views that pack's claims through a lens |
| **Loading** | Dependency must be available for this pack to be valid | Referenced pack enhances but is not required |
| **Direction** | Structural (this pack's claims assume the other pack's claims) | Navigational (this pack points to the other pack for context) |
| **Graceful degradation** | Missing dependency = warning, reduced validity | Missing referenced pack = reduced context, pack still usable |

### No Duplication Rule

A composite pack MUST NOT duplicate claims from its referenced packs. If a fact exists in `solar-energy-market.kpack`, the meeting pack references it -- it does not restate it.

Exceptions:

1. **Meeting-specific framing.** A meeting claim may restate a standing claim with meeting-specific context: "Cost floor thesis revised based on new manufacturing data (Webb hasn't seen the latest analysis yet)." This is a claim about the meeting situation, not a duplicate of the cost thesis claim.

2. **Contradictions discovered during meeting.** If a participant states something that contradicts a standing claim, the meeting pack records both the participant's statement and the contradiction reference. This is new knowledge, not duplication.

3. **Temporal snapshots.** A meeting pack may note "As of meeting date, market forecast was X" -- this is provenance, not duplication. The standing pack's claim may have since changed.

---

## 7. Composition Types

Meeting prep is the primary composition type, but the `composition.yaml` format supports other composite pack patterns.

### meeting-prep

The canonical composition type. Covered in full above.

```yaml
type: meeting-prep
meeting: { ... }
agenda: [ ... ]
pre_load: [ ... ]
on_demand: [ ... ]
```

### briefing

A briefing pack composes knowledge for a recipient who needs to get up to speed. Unlike a meeting, there is no interactive agenda -- the briefing is a one-directional knowledge transfer.

```yaml
type: briefing

briefing:
  recipient: "Elena Vasquez"
  purpose: "Quarterly market intelligence briefing"
  date: 2026-03-22
  format: voice              # voice | document | presentation
  duration: 15m              # Target delivery time

sections:
  - heading: "Market forecast"
    reference: "solar-energy-market"
    focus_claims: [C001, C003, C030]
    narrative_hint: "Lead with cost floor debate"

  - heading: "Technology outlook"
    reference: "perovskite-assessment"
    focus_claims: [C011, C012]
    narrative_hint: "Oxford PV durability update"

  - heading: "Competitive landscape"
    reference: "competitor-analysis"
    focus_claims: [C040, C041, C042]

pre_load:
  - solar-energy-market
  - perovskite-assessment
```

**Key differences from meeting-prep:**
- `sections` instead of `agenda` (one-directional, not interactive)
- `narrative_hint` guides the voice or document renderer on framing
- `format` declares the intended delivery surface
- No `on_demand` -- briefings are pre-composed, not exploratory

### research

A research composition assembles knowledge from multiple packs to investigate a question. The composition defines the research question, relevant packs, and the analytical frame.

```yaml
type: research

research:
  question: "Is perovskite tandem commercially viable by 2028 given current durability constraints?"
  hypothesis: "Commercial viability achievable if moisture degradation pathway is resolved by mid-2027"
  date: 2026-03-22
  depth: thorough             # quick | thorough | exhaustive

sources:
  - pack: "perovskite-assessment"
    relevance: "Primary subject -- lab efficiency and degradation data"
    focus_claims: [C001, C005, C010, C012]

  - pack: "solar-energy-market"
    relevance: "Market context and cost trajectory baseline"
    focus_claims: [C001, C011]

  - pack: "webb-advisory-2026-03-24"
    relevance: "Webb's perspective on commercialization timeline"

pre_load:
  - perovskite-assessment
  - solar-energy-market

on_demand:
  - competitor-analysis            # For comparison
```

**Key differences from meeting-prep:**
- `question` and `hypothesis` define the analytical frame
- `sources` with `relevance` annotations explain why each pack matters
- `depth` hints at the level of analysis expected
- Output is analytical claims, not meeting minutes

### presentation

A presentation composition assembles knowledge for a slide deck, pitch, or visual narrative. It maps pack claims to presentation structure.

```yaml
type: presentation

presentation:
  title: "Solar Market Outlook 2026-2030"
  audience: "Industry conference attendees"
  date: 2026-03-25
  slide_count: 12             # Target slide count
  style: corporate

slides:
  - title: "Cost Trajectory"
    reference: "solar-energy-market"
    focus_claims: [C001, C002]
    visual_hint: "Learning curve chart -- 22% per doubling"

  - title: "Technology Roadmap"
    reference: "solar-energy-market"
    focus_claims: [C010, C011, C012]

  - title: "Market Adoption"
    reference: "solar-energy-market"
    focus_claims: [C002, C003]
    visual_hint: "Grid parity map by region"

  - title: "Systemic Risks"
    reference: "solar-energy-market"
    focus_claims: [C030]

pre_load:
  - solar-energy-market
```

**Key differences from meeting-prep:**
- `slides` instead of `agenda` -- each entry maps to a presentation slide
- `visual_hint` guides the presentation renderer
- `slide_count` constrains scope
- `style` reference for visual consistency
- Typically references fewer packs (focused narrative)

---

## 8. Context Budget Management

Composition's loading strategy is fundamentally a context budget optimization.

### Budget Allocation

For a typical meeting with a 128K-token model:

| Component | Budget | Notes |
|-----------|--------|-------|
| System prompt + instructions | ~4K | Fixed overhead |
| Conversation history | ~20-40K | Grows during meeting |
| `pre_load` packs (claims only) | ~4-12K | 2-3 hub packs |
| `on_demand` packs (when loaded) | ~4-8K | 1-2 detail packs at a time |
| Meeting pack claims.md | ~1-2K | Minimal by design |
| composition.yaml | ~0.5K | Agenda and structure |
| **Available for reasoning** | **~60-90K** | Comfortable margin |

### Loading Priority

When context budget is tight:

1. **Always load:** composition.yaml and the meeting pack's claims.md
2. **Always load:** All `pre_load` pack claims.md files
3. **Load on trigger:** `on_demand` packs when conversation enters their territory
4. **Load on citation:** Evidence files when specific citations are needed
5. **Never pre-load:** History files, entity files, views (unless displaying)

### Focus Claims Optimization

When a `pre_load` pack is large (detail tier, ~6-8K tokens), `focus_claims` provides a secondary optimization. The system can:

1. Load the full claims.md (preferred -- the AI has complete context)
2. Or, if budget is tight, load only the sections containing `focus_claims` plus the pack header

Option 1 is always preferred. Option 2 is a graceful degradation, not the default.

---

## 9. Tooling

### CLI Commands

```bash
# Create a meeting prep pack from template
kpack new --template meeting-prep "webb-advisory-2026-03-24"

# Validate composition references
kpack lint webb-advisory-2026-03-24.kpack/
#   Checks: pack references resolve, focus_claims exist, dates valid

# Preview what would be loaded
kpack compose webb-advisory-2026-03-24.kpack/ --dry-run
#   Shows: total token budget, pre_load packs, on_demand packs

# Generate post-meeting promotion suggestions
kpack reconcile webb-advisory-2026-03-24.kpack/
#   Scans meeting pack claims for promotable content
#   Outputs: suggested claim additions to standing packs

# Archive after reconciliation
kpack archive webb-advisory-2026-03-24.kpack/
#   Moves to archive after confirming all claims reconciled
```

### Composition Validation (kpack lint)

For composite packs, `kpack lint` adds these checks:

| Check | Severity | Description |
|-------|----------|-------------|
| Pack references resolve | Error | Every name in `pre_load`, `on_demand`, and `reference` must exist in KNOWLEDGE.yaml |
| Focus claims exist | Warning | Referenced claim IDs should exist in the referenced pack (warning because claims may have been superseded) |
| Meeting date is future or recent | Warning | Linting a meeting pack dated >30 days ago suggests it should be archived |
| No claim duplication | Warning | Claims in the composite pack should not restate claims from referenced packs |
| Context budget estimate | Info | Estimated total tokens for all pre_load packs |

---

## 10. Design Principles (Composition-Specific)

These extend the core design principles in SPEC.md section 14.

1. **Composition over duplication** (Principle 18). The foundational rule. Knowledge lives once. Composite packs are lenses, not copies.

2. **Minimal claims.** A composite pack's claims.md should be the smallest file in the ecosystem. 5-10 claims about the composition context, not 40 claims restating domain knowledge.

3. **Agenda as navigation.** The agenda is not documentation -- it is a runtime navigation structure that the Voice LLM uses to track conversation and manage context loading.

4. **Pre_load for certainty, on_demand for possibility.** Pre-load what you know you will discuss. On-demand what you might discuss. When in doubt, on_demand -- context budget is finite.

5. **Promote, don't hoard.** Post-meeting, new knowledge flows outward to standing packs. The meeting pack is a temporary vessel, not a permanent home.

6. **Standing packs are canonical.** If a composite pack's claim conflicts with a standing pack's claim, investigate -- the standing pack is the default source of truth unless the meeting produced genuinely new information.

7. **Composition types share structure.** All composition types use `pre_load` and `on_demand`. The type-specific fields (meeting, briefing, research, presentation) are overlays on this shared loading model.
