<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Self-Driving Presentation Playback — Knowledge Pack Companion Spec

> **Date:** 2026-05-09
> **Status:** Experimental — schema may evolve before v0.9
> **Editor:** Timothy Kompanchenko

---

## 1. Purpose

PLAYBACK is the spec layer for **self-driving voice presentations** of Knowledge Packs. A presentation is a structured, multi-phase narration where an assistant walks the listener through a pack's content — claims, evidence, red flags, decisions — at a chosen depth and tier.

This companion specifies:

- **`PlaybackPlan`** — the structured plan a renderer follows to deliver a presentation.
- **`AudienceProfile`** — the listener-specific context that shapes plan composition.
- **Discovery dialogue** — how the renderer establishes the audience profile at session start.
- **Phase advancement contract** — separating "what to play next" (data-driven) from "when to advance" (app-controlled).
- **Form variants** — short / medium / long with element-selection rules.
- **Pack-play vs library-play** — same contract, different planners.

Out of scope: visual choreography (auto-scroll, image reveal, view switching). PLAYBACK v1 is voice-only; visual extensions are a v2 concern.

---

## 2. Why a separate companion

[VOICE.md](VOICE.md) governs **voice views** — pre-rendered prose delivered as a single artifact. PLAYBACK governs **dynamic narration** — a runtime composition that selects, sequences, and delivers content from a pack's claims, views, and extensions. Voice views are nouns (files); playback is a verb (process).

The relationship: PLAYBACK sits one layer above VOICE. A renderer consults the pack's voice views, claims, AI brief, and audience context, and produces a phase-by-phase narration tuned to the listener at session time.

---

## 3. AudienceProfile

`AudienceProfile` is the listener-specific context, structured as a small object passed once at the start of a presentation session. It governs which phases are included, how dense each is, and what register and emphasis the narration adopts.

```yaml
audience_profile:
  familiarity: fresh                    # fresh | some_context | expert
  duration_tier: medium                  # short | medium | long
  purpose: orientation                   # orientation | decision | risk_review | press | research | demo
  domain_lens: buyer                     # buyer | consigner | compliance | journalist | collector | general
  register: curatorial                   # plain | curatorial | technical | investor (per VOICE.md §4.1)
  inferred: false                        # true if the profile was derived from defaults rather than dialogue
```

| Field | Required | Type | Description |
|---|---|---|---|
| `familiarity` | Yes | enum | Listener's prior subject-matter exposure. Drives phase depth. |
| `duration_tier` | Yes | enum | Time budget. Drives phase count and word budget. |
| `purpose` | Yes | enum | Why the listener is here. Drives phase ordering and emphasis. |
| `domain_lens` | No | enum | Listener's role-frame within the pack's domain. Refines emphasis (e.g., a buyer hears value claims first; compliance hears risk first). |
| `register` | No | enum | Voice register from [VOICE.md §4.1](VOICE.md). Defaults to `curatorial` for art/heritage packs, `plain` otherwise. |
| `inferred` | Yes | boolean | `true` when the profile defaulted; `false` when explicitly captured via discovery dialogue. |

`AudienceProfile.register` composes with — but does not replace — VOICE's producer-side `register`. Producer-side `register` controls how voice views are *written*; `AudienceProfile.register` is the listener-side selection for the *current session*. Where they conflict, the session selection wins for that session's narration; the underlying voice view file is unchanged.

---

## 4. PlaybackPlan

A `PlaybackPlan` is the deterministic output of a planner that takes `(pack, audience_profile, duration_tier)` as input. It is the contract between the planner and the playback runtime.

```yaml
playback_plan:
  pack_id: marquet-le-passeur
  audience_profile:
    familiarity: fresh
    duration_tier: medium
    purpose: orientation
    register: curatorial
    inferred: false
  duration_tier: medium
  phases:
    - phase_id: ph_001_verdict
      narrative_hint: "Open with the headline verdict."
      source_refs:
        - extensions.ai_brief.headline
      view_target: null                  # optional view to surface during this phase (visual layer, v2)
      transition_intent: opening
      word_budget: 60
      min_tier: short                    # which duration tiers include this phase
    - phase_id: ph_002_red_flag
      narrative_hint: "Surface the highest-confidence concern."
      source_refs:
        - extensions.ai_brief.redFlags[0]
      transition_intent: emphasis
      word_budget: 80
      min_tier: short
    - phase_id: ph_003_claim_lead
      narrative_hint: "State the strongest claim with confidence."
      source_refs:
        - claims.C001
        - evidence.E007
      transition_intent: building
      word_budget: 120
      min_tier: medium
    # ... more phases ...
  resume_policy:
    on_interrupt: pause                  # pause | continue | restart_phase
    on_resume: restate_phase_lead         # restate_phase_lead | continue_seamlessly
  handoff_policy:
    on_question: bookmark_then_handle    # always interrupt for questions
    on_long_silence: pause                # pause if listener is silent past inactivity_seconds
    inactivity_seconds: 12
```

| Field | Required | Description |
|---|---|---|
| `pack_id` | Yes | Pack identity from PACK.yaml `name`. For library-play, `pack_id` is the library identifier. |
| `audience_profile` | Yes | The profile this plan was composed against. Stored for audit. |
| `duration_tier` | Yes | The selected tier; controls which phases are included via `min_tier`. |
| `phases[]` | Yes | Ordered phase list. Each phase has `phase_id`, `narrative_hint`, `source_refs[]`, optional `view_target`, `transition_intent`, `word_budget`, `min_tier`. |
| `phases[].source_refs[]` | Yes | References into pack content the renderer reads from. See "Source-ref grammar" below for the normative path syntax. |
| `phases[].view_target` | No | Optional view name the renderer surfaces during the phase (visual layer extension). |
| `phases[].transition_intent` | Yes | Hint for prosody between phases: `opening`, `emphasis`, `building`, `qualifying`, `closing`. |
| `phases[].word_budget` | Yes | Approximate word count budget for the phase narration. |
| `phases[].min_tier` | Yes | Smallest `duration_tier` that includes this phase. Lets one plan describe short/medium/long with a single ordered list. |
| `resume_policy` | Yes | Contract for what the runtime does when narration is paused (interruption or barge-in). |
| `handoff_policy` | Yes | Contract for question-handling and inactivity. |

### 4.1 Source-ref grammar (normative)

Each entry in `source_refs[]` is a string with one of the following prefixes. Validators MUST reject plans whose `source_refs[]` entries do not match this grammar.

| Prefix | Meaning | Example |
|---|---|---|
| `claims.<ID>` | A claim ID from `claims.md` (matches the claim ID grammar in [CORE.md §5](CORE.md)). | `claims.C001` |
| `evidence.<ID>` | An evidence ID from `evidence.md`. | `evidence.E007` |
| `history.<ID>` | A superseded or retracted claim from `history.md`. Used when the playback plan needs to narrate why a claim changed. | `history.C001` |
| `views.<name>` | A view declared in PACK.yaml's `views` array (`name` field). | `views.briefing` |
| `extensions.<path>` | A dotted path into the manifest's `extensions` block. Path segments are object keys; bracketed indices select array members. | `extensions.ai_brief.headline`, `extensions.ai_brief.redFlags[0]` |

The grammar is regular: `^(claims|evidence|history|views)\.[^.]+$` for the first four forms; `^extensions\.[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*|\[\d+\])*$` for the extensions form. Producers MUST emit references that resolve to existing content in the pack at plan-generation time. Consumers SHOULD treat unresolvable references as soft errors (skip the phase or substitute a fallback) rather than fatal validation failures, since pack content can drift between plan generation and playback.

### 4.2 Form variants

A single `PlaybackPlan` can describe all three duration tiers via `min_tier` filtering on phases:

| Tier | Target duration | Phase count | Includes |
|---|---|---|---|
| `short` | ≤ 90 seconds | 3-4 | verdict + headline + 1 red flag + 1 next step |
| `medium` | ~3 minutes | 5-7 | + 2 primary claims + best evidence + uncertainty + closing |
| `long` | ~8 minutes | 10-14 | + counterpoints + Q&A pause invitations |

The planner emits ONE plan that covers all three; the runtime filters by `min_tier ≤ duration_tier` to select the active phase set. This lets a listener say "give me the longer version" mid-session without re-planning — the runtime promotes to the next tier and includes additional phases.

---

## 5. Discovery dialogue

When `AudienceProfile.inferred` would be `true`, the renderer SHOULD attempt a brief dialogue at session start to capture the profile explicitly. The default dialogue is three short questions:

- **Q1** — "Before I walk this, are you hearing it fresh, or do you already know the subject?"
  Sets `familiarity`.
- **Q2** — "Do you want the quick read, the three-minute version, or the deep dive?"
  Sets `duration_tier`.
- **Q3** — (only if context is unclear) "And are you listening as a buyer, a consigner, compliance, press, or just orienting?"
  Sets `purpose` + optional `domain_lens`.

### 5.1 Defaults

When the listener says "just play it" without dialogue, the renderer SHOULD default to `{familiarity: fresh, duration_tier: medium, purpose: orientation}` and set `inferred: true`.

When the listener says "give me the short version" or similar, the renderer SHOULD skip discovery, set `duration_tier: short`, and proceed.

When the listener is a returning user (the renderer has prior-session context), the dialogue MAY be replaced with: "short, three-minute, or continue where we left off?"

---

## 6. Phase advancement — renderer-owned, not model-decided

The runtime that advances phases is part of the **renderer** (the application that consumes a `PlaybackPlan` and drives the voice pipeline), not a tool the language model can call. This is normative for renderers, since it is the contract that makes a `PlaybackPlan` interpretable consistently across renderer implementations:

> **Rule (P1).** A KP:1-conformant renderer MUST NOT expose a phase-advancement tool to the language model. Phase advancement is decided by the renderer based on `PlaybackPlan` ordering, the listener's interruption signals, and the resume / handoff policies. A renderer that does expose such a tool MUST document the resulting non-conformance and SHOULD NOT advertise itself as KP:1 PLAYBACK-conformant.

Rationale: if the model could advance phases, it could also produce inconsistent narration sequences (skipping ahead, looping, going back) that would conflict with the deterministic plan. Keeping advancement in the renderer preserves the plan's value as a contract — a plan emitted by one composer renders identically across conformant renderers.

The model MAY have a tool that **captures the audience profile** at session start (one tool call). The model MAY have tools that **navigate to a view** or **read a section** as part of the visual layer (out of scope for v1). The phase-advancement tool is the one explicitly forbidden.

---

## 7. Pack-play vs library-play

The same `PlaybackPlan` schema serves both:

- **Pack-play** — narration of a single pack. The planner reads from `claims.md`, `views/voice/*.md`, `extensions.ai_brief`, etc.
- **Library-play** — narration of a library snapshot ("3 packs need attention; here are the highest-priority red flags"). The planner reads from a library-aggregator output that selects items across packs, and the `pack_id` field identifies the library rather than a single pack.

Library-play is **triage**, not concatenation. The planner SHOULD NOT produce a synthetic "mega-pack" by joining pack claims — that produces a shapeless narration. Instead, library-play selects the most decision-relevant items across packs and narrates them with cross-pack framing.

---

## 8. Concurrency

A presentation session typically uses a real-time voice pipeline (e.g., a streaming TTS / dialogue system) plus the application's playback controller.

> **Rule (P2).** Only the real-time voice pipeline's actor MAY send the protocol's "create response" / "cancel response" / "create item" messages. Only the playback controller (or equivalent) MAY decide which phase is current. Stale calls — those originating from a previous phase epoch — MUST verify the current playback epoch before mutating playback state.

This rule prevents two well-known races: (a) advancing a phase mid-response causes the runtime to commit to two narrations at once; (b) a stale interrupt handler from a previous phase cancels the current phase's response.

The contract is enforceable at the application layer; PLAYBACK does not specify a wire-level invariant.

---

## 9. Status and stability

This entire companion is **experimental** for v0.8.0-preview. The schema may evolve before v0.9 based on observed behavior:

- The phase `source_refs[]` vocabulary is likely to expand once real packs ship presentations.
- `transition_intent` enum values may consolidate or expand based on prosody experiments.
- `handoff_policy.inactivity_seconds` defaults will be tuned empirically.
- The `register` field's interaction with [VOICE.md §4.1](VOICE.md) may need clarification once both fields ship in real packs.

Producers MAY emit `PlaybackPlan` artifacts in v0.8.0-preview packs as advisory metadata; consumers SHOULD treat them as informational and tolerant of schema drift.

The status will graduate from experimental to active after at least three real packs ship with playback plans and at least two distinct renderers have demonstrated successful end-to-end narration against the plans.

---

## 10. Related

- [VOICE.md §4.1](VOICE.md) — the four primary voice registers (`plain`, `curatorial`, `technical`, `investor`). `AudienceProfile.register` is the session-time selector across this axis.
- [MULTILINGUAL.md §3.3](MULTILINGUAL.md) — locale-specific sub-registers (Halychyna, Quebec, MSA, etc.). `sub_register` is informational per MULTILINGUAL.md §3.3 (not a normative enum); the runtime MAY honor it if set on the source voice view, but MUST not depend on its presence and SHOULD not treat its absence as an error.
- [EXTENSIONS.md §2.1 `ai_brief`](EXTENSIONS.md) — `ai_brief.headline` / `redFlags` / `beCarefulAbout` / `next` are common phase `source_refs`.
- [COMPOSITION.md](COMPOSITION.md) — multi-pack composition for meeting packs. A meeting-pack `PlaybackPlan` may aggregate phases across the composed packs in the order COMPOSITION declares.
