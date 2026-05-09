<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Notes Metadata — Knowledge Pack Companion Spec

> **Date:** 2026-03-22
> **Status:** Draft
> **Decisions:** D16 (recording consent reframed as notes)

---

## 1. Purpose

When an AI assistant participates in meetings, it can take structured notes — capturing key decisions, action items, names, and facts in knowledge pack format. This document specifies the metadata that tracks note-taking mode, disclosure status, and participant awareness.

---

## 2. Terminology

The system uses **"notes"**, not **"recording."**

| Term | Meaning | Connotation |
|------|---------|-------------|
| Recording | Passive capture of everything, full transcript | Surveillance-adjacent |
| Notes | Selective capture of important information | Professional assistance |

An AI assistant taking notes during a meeting is analogous to a human assistant who sits in and writes down key points, action items, and decisions. This is the correct frame for the system's behavior.

---

## 3. Modes

The `notes.mode` field in PACK.yaml controls what the AI captures:

| Mode | Captures | Use case | Disclosure | Consent |
|------|----------|----------|------------|---------|
| `active` | Structured extraction: decisions, action items, claims, key facts | Normal meetings | Disclosure recommended | Not required |
| `passive` | Full transcript + structured extraction | Legal depositions, formal negotiations | Required | **Required** |
| `off` | Nothing | No AI note-taking | N/A | N/A |

### Active Mode (Default for Meeting Packs)

The AI extracts structured information in real-time:
- Decisions made
- Action items with owners and deadlines
- New facts (names, numbers, dates)
- Claims that update or contradict standing knowledge

The output is a knowledge pack with claims.md (structured) and optionally a summary view. No raw transcript is stored as a primary artifact.

### Passive Mode

Full transcript capture plus structured extraction. This mode is subject to recording consent laws, which vary by jurisdiction. The pack stores consent status explicitly.

### Off Mode

The AI participates in the conversation but does not capture anything into a knowledge pack. Useful for informal conversations or when participants decline note-taking.

---

## 4. PACK.yaml Fields

```yaml
notes:
  mode: active                # active | passive | off
  participants: [Alice, Bob]  # All meeting participants
  disclosed: true             # Was AI note-taking disclosed?
  consent: null               # Required for mode: passive
                              #   obtained | declined | pending
```

### Field Semantics

| Field | Required | Description |
|-------|----------|-------------|
| `mode` | Yes | Note-taking mode for this pack |
| `participants` | Yes | All participants in the meeting/conversation |
| `disclosed` | Yes | Whether AI note-taking was disclosed to all participants |
| `consent` | Only for passive | Explicit consent status for full transcript recording |

---

## 5. Disclosure vs Consent

**Disclosure** (for active mode): Informational. "My AI assistant is taking notes." This is professional courtesy, analogous to saying "Sarah is joining to take notes." The AI should be able to check this field and remind the user: "Note-taking disclosure is pending for this meeting."

**Consent** (for passive mode): Legal. "May I record this conversation?" Required in two-party consent jurisdictions. The AI must not activate passive mode without `consent: obtained`.

### Consent Workflow

1. Meeting starts with `consent: pending`
2. User discloses AI note-taking to participants
3. User updates `disclosed: true`
4. If passive mode needed: user obtains and records consent
5. If consent declined: system falls back to `mode: active` or `mode: off`

---

## 6. Internal-Only Shorthand

For conversations where Tim is the only human participant (solo work sessions, Tim + AI only):

```yaml
notes:
  mode: active
  participants: [Tim]
  disclosed: true              # Always true for internal
  consent: null                # Not applicable
```

No disclosure or consent needed. The AI takes notes freely.

---

## 7. Three-LLM Architecture Integration

The notes system integrates with the three-LLM conversation architecture:

| LLM | Role in note-taking |
|-----|---------------------|
| **Voice LLM** | Fast conversation partner. Does not take notes directly. |
| **Recording LLM** | The note-taker. Receives transcript stream, extracts structured claims. Checks `notes.mode` to determine behavior. |
| **Intelligence LLM** | On-demand analyst. Results feed back to recording LLM for capture. |

The recording LLM checks `notes.mode` before activating:
- `active` → Extract claims, action items, decisions
- `passive` → Full transcript + extraction (requires `consent: obtained`)
- `off` → Do not activate

---

## 8. Real-Time Consistency Checking

During `mode: active` or `mode: passive`, the recording LLM cross-references spoken claims against loaded knowledge packs. When a discrepancy is detected:

1. Recording LLM identifies the contradiction
2. Alert sent to visual channel (Canvas, phone notification — never spoken aloud)
3. Alert is non-accusatory: "Pack says X. Spoken claim was Y. Worth clarifying?"
4. User decides whether to address it in the conversation

Alert configuration in PACK.yaml:

```yaml
notes:
  alert_threshold: 0.70        # Only alert on claims with confidence > threshold
  alert_channel: canvas         # canvas | notification | both
```

Low-confidence claims (`{0.40}`) are already uncertain — no need to alert. High-confidence claims (`{0.95}`) contradicted in conversation are a real signal.
