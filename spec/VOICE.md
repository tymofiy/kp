<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Voice Views — Knowledge Pack Companion Spec

> **Parent:** SPEC.md v0.8
> **Date:** 2026-04-12
> **Status:** Draft
> **Decisions:** D13 (voice view format), D22 (locale-before-surface ordering)

---

## 1. Purpose

Voice views are the third surface of the three-surface architecture. While claims.md serves AI reasoning and display views serve human reading, voice views serve human listening. The auditory channel is fundamentally different from the visual channel — a listener cannot scan ahead, re-read a sentence, or glance at a table. Voice views account for this by producing text optimized for spoken delivery.

Voice views are NOT transcripts, audio files, or TTS instructions. They are plain text documents written the way a knowledgeable briefer would speak to a listener. An AI reading a voice view aloud — or feeding it to a speech synthesis pipeline — should produce natural, clear, paced speech.

---

## 2. Why a Separate Surface

Display views cannot be read aloud effectively. The following table captures the seven dimensions where auditory and visual perception diverge:

| Dimension | Display View | Voice View |
|---|---|---|
| Sentence length | Complex, nested clauses acceptable | Short sentences, 10-15 words maximum |
| Structure | Headers, bullets, tables, blockquotes | Sequential narrative flow, no tables |
| Numbers | "$2,000,000" — scannable at a glance | "two million dollars" — speakable |
| Emphasis | **Bold**, *italic*, `code` | Pause markers, stress cues |
| Density | High — reader controls pace via scanning | Low — listener hears one sentence at a time |
| Proper nouns | Written once, recognized visually | Need pronunciation hints for unusual terms |
| Context | Reader sees entire page simultaneously | Listener hears only the current sentence |

A display view read aloud sounds like someone reading a document. A voice view read aloud sounds like someone briefing you. The difference is the same as the difference between a written report and a radio news segment.

---

## 3. Directory Convention

Voice views live inside `views/voice/` within the pack directory:

```text
{name}.kpack/
├── PACK.yaml
├── claims.md
├── evidence.md
├── views/
│   ├── overview.md              # Display view (English)
│   ├── pitch.md                 # Display view (English)
│   ├── voice/                   # Voice views (English)
│   │   ├── briefing.md          # Voice view — executive briefing
│   │   └── elevator.md          # Voice view — 30-second pitch
│   └── uk/                      # Ukrainian locale
│       ├── overview.md          # Translated display view
│       └── voice/               # Translated voice views
│           └── briefing.md      # Ukrainian voice briefing
```

### Locale-Before-Surface Ordering (Design Principle 22)

Locale is the higher-order grouping. A Ukrainian voice briefing lives at `views/uk/voice/briefing.md`, not `views/voice/uk/briefing.md`. Rationale: a locale directory contains everything for that language — display views and voice views together. A consumer requesting "show me everything in Ukrainian" finds it all under `views/uk/`.

---

## 4. File Format

Voice view files are plain text with minimal markup. The content is what gets spoken. Everything else is metadata in HTML comments.

### Metadata Header

Every voice view begins with HTML comment metadata:

```markdown
<!-- voice: briefing -->
<!-- duration: ~90 seconds -->
<!-- pace: measured -->
<!-- generated: 2026-03-22 | claims: v2026.03.22 -->
<!-- source: C001, C002, C010, C020, C030, C040, C050 -->
```

| Field | Required | Values | Purpose |
|-------|----------|--------|---------|
| `voice` | Yes | View identifier | Matches the `name` field in PACK.yaml voice view declaration |
| `duration` | Yes | `~N seconds` or `~N minutes` | Approximate spoken duration at natural pace |
| `pace` | Yes | `brisk`, `measured`, `deliberate` | Speaking tempo hint for TTS or human reader |
| `generated` | Recommended | ISO date + claims version | Staleness detection (same mechanism as display views) |
| `source` | Recommended | Comma-separated claim IDs | Traceability back to claims.md |

### Body Conventions

The body is written as spoken text. The following rules govern its format:

1. **No markdown formatting.** No bold, italic, headers, code blocks, or bullet lists. The file is what gets spoken — formatting characters would be read aloud or cause TTS artifacts.

2. **Numbers spelled out.** Write "two million dollars", not "$2,000,000". Write "fifty percent", not "50%". Write "March twenty-second", not "March 22nd". Write "nine hundred and six tests", not "906 tests". Exception: years remain numeric when they would sound unnatural spelled out — "twenty twenty-six" is acceptable but "2026" is also fine since TTS engines handle years well.

3. **Short sentences.** Target 10-15 words per sentence. Never exceed 20. If a sentence needs a comma, consider splitting it into two sentences.

4. **Pause markers.** Use `(pause)` on its own line between sections or where a speaker would take a deliberate breath. This signals a 1-2 second silence in speech synthesis or a natural break point for a human reader.

5. **Pronunciation hints.** For terms an English TTS engine might mispronounce, add hints in parentheses after the first occurrence: `Qwen (pronounced "chwen")`, `Hono (pronounced "hoh-no")`, `Neon (pronounced "nee-on")`. Subsequent occurrences do not need the hint.

6. **Sequential narrative flow.** Information builds linearly. A listener cannot skip ahead. Open with context ("Here is a briefing on..."), build through the key points, close with what matters next. No forward references — do not say "as we will discuss later."

7. **Source traceability.** HTML comments `<!-- source: C001, C002 -->` may appear between sections to trace content back to claims. These are not spoken.

8. **Repetition for retention.** Unlike display views where a reader can glance back, voice views may restate a key term or number if it is referenced later. A display view says "906 tests" once; a voice view may say "those nine hundred tests" again when referencing them in a risk section.

---

## 5. Full Example

```markdown
<!-- voice: briefing -->
<!-- duration: ~75 seconds -->
<!-- pace: measured -->
<!-- generated: 2026-03-22 | claims: v2026.03.22 -->
<!-- source: C001, C002, C004, C010, C020, C030, C040, C050 -->

Here is a briefing on the solar energy market.

Utility-scale solar is now the cheapest new electricity source in most markets.
The levelized cost has fallen eighty-nine percent since twenty ten.
This decline is driven by three factors.
Manufacturing scale, cell efficiency gains, and financing maturity.

(pause)

The market is growing at twenty-six percent annually.
China produces over eighty percent of global polysilicon supply.
This concentration is the single largest supply chain risk.
Trade policy changes could disrupt module availability within months.

<!-- source: C001, C002 -->

(pause)

Perovskite tandem cells are the leading next-generation technology.
Lab efficiency has reached thirty-three point seven percent.
Commercial deployment is expected between twenty twenty-seven and twenty twenty-nine.
The manufacturing challenge is long-term stability under field conditions.

<!-- source: C010 -->

(pause)

Three systemic risks dominate the outlook.
First, polysilicon supply concentration in a single country.
Second, grid interconnection queues averaging four point one years.
Third, permitting timelines that vary by a factor of ten across jurisdictions.

<!-- source: C020, C040 -->

(pause)

The biggest opportunity is in emerging markets.
Sub-Saharan Africa and Southeast Asia have the highest unmet demand.
Financing, not technology, is the primary barrier in these regions.

<!-- source: C050 -->

(pause)

That concludes this briefing on the solar energy market.
```

---

## 6. PACK.yaml Declaration

Voice views are declared alongside display views in the `views` array, distinguished by their path within `voice/`:

```yaml
views:
  # Display views
  - name: overview
    file: views/overview.md
    purpose: "Executive summary — what it is, where it stands, key risks"
    display_as: "Overview"

  - name: pitch
    file: views/pitch.md
    purpose: "Stakeholder pitch — messaging, objection handling, demo strategy"
    display_as: "Pitch & Demo"

  # Voice views
  - name: briefing
    file: views/voice/briefing.md
    purpose: "Spoken executive briefing — key facts, status, top risk"
    display_as: "Voice Briefing"   # Required on all views
    voice: true                    # Marks this as a voice view
    duration: "~75 seconds"        # Expected spoken duration
    pace: measured                 # brisk | measured | deliberate

  - name: elevator
    file: views/voice/elevator.md
    purpose: "30-second spoken pitch for casual conversation"
    display_as: "Elevator Pitch"   # Required on all views
    voice: true
    duration: "~30 seconds"
    pace: brisk
```

The `voice: true` field distinguishes voice views from display views in the manifest. Consumers that do not support voice can skip entries with `voice: true`. Consumers that only want voice views can filter to them.

### Locale Voice Views

Translated voice views follow the locale-before-surface pattern:

```yaml
locales:
  canonical: en-US
  available:
    - locale: uk-UA
      display_name: "Українська"
      status: draft
      views: [overview, briefing]           # Both display and voice
      derived_from: "claims@2026.03.22"
      translator: machine
```

The `views` list uses view names, not file paths. The tooling resolves `briefing` for locale `uk-UA` to `views/uk/voice/briefing.md` using the locale-before-surface convention.

---

## 7. When Voice Views Are Loaded

Voice views serve a different consumption context than display views. They are loaded when the AI needs to speak, not when it needs to show.

| Context | What loads | Why |
|---------|-----------|-----|
| Voice conversation (OpenAI Realtime, etc.) | Voice views | The AI is speaking; it needs speakable content |
| Briefing mode ("brief me on solar energy") | Voice views | The user expects a spoken-style summary even in text |
| Display context (Canvas, UI panel, chat) | Display views | The user is reading, not listening |
| AI reasoning about the domain | claims.md | Neither view type — the AI reads claims |

### Progressive Loading for Voice

The same progressive loading model applies:

| Level | Always loaded | Loaded on demand |
|-------|---------------|------------------|
| Within a pack | claims.md | voice views when speaking |
| Across packs | Hub pack claims | Voice views from relevant pack |
| Across locales | Canonical (en-US) voice view | Translated voice view by locale |

An AI in a voice session loads claims.md to become knowledgeable, then renders the appropriate voice view when it is time to deliver information. It does not compose speech from claims on the fly — the voice view exists precisely to avoid that.

---

## 8. Voice View Generation

### Manual Authoring

Voice views can be hand-written. This produces the highest quality output — a human author naturally writes for the ear. Hand-authored voice views should still include the metadata header and source traceability comments.

### `kpack render --voice`

The `kpack render` command generates voice views from claims:

```bash
# Generate all declared voice views
kpack render my-project.kpack/ --voice

# Generate a specific voice view
kpack render my-project.kpack/ --voice --view briefing

# Generate voice views for a specific locale
kpack render my-project.kpack/ --voice --locale uk-UA

# Check which voice views are stale
kpack render my-project.kpack/ --voice --check
```

The `--voice` flag instructs the renderer to apply voice conventions (short sentences, spelled-out numbers, pause markers, pronunciation hints) instead of display conventions (headers, tables, formatting). The renderer reads claims.md, selects claims relevant to the view's declared purpose, and produces spoken-style text.

### Generation Prompt Pattern

When an LLM generates a voice view from claims, it should receive instructions equivalent to:

> Write this as if you are briefing someone aloud. Use short sentences — fifteen words maximum. Spell out all numbers. No markdown formatting. Add pause markers between topic transitions. Include pronunciation hints for unusual proper nouns. The listener cannot see any text — they hear only your words, one sentence at a time.

### Hybrid Workflow

The recommended workflow mirrors display views: generate with `kpack render --voice`, then refine by hand. AI-generated voice views tend to be correct but stilted. A human pass adds natural pacing and conversational rhythm.

---

## 9. Staleness Detection

Voice view staleness uses the same mechanism as display views. The generation metadata comment tracks the claims version:

```markdown
<!-- generated: 2026-03-22 | claims: v2026.03.22 -->
```

`kpack lint` compares the `claims:` version against the current claims.md version. If they differ, it emits a staleness warning:

```text
WARN: views/voice/briefing.md is stale (claims: v2026.03.21, current: v2026.03.22)
```

Staleness is a warning, not an error. Voice views may intentionally lag during active claims editing. The `--check` flag on `kpack render --voice` reports stale voice views without regenerating them.

### Staleness Priority

Voice views are more sensitive to staleness than display views. A display view with a slightly outdated number is still scannable and correctable by the reader. A voice view with an outdated number is stated as fact to a listener who cannot cross-reference. Tooling should surface voice view staleness at higher priority than display view staleness.

---

## 10. Pace Guidance

The `pace` field provides a tempo hint for speech synthesis or human delivery:

| Pace | Words per minute | Use when |
|------|-----------------|----------|
| `brisk` | ~170 wpm | Elevator pitches, time-constrained updates, action-oriented summaries |
| `measured` | ~140 wpm | Standard briefings, executive summaries, most voice views |
| `deliberate` | ~110 wpm | Complex topics, risk discussions, bad news, content requiring absorption time |

Pace is advisory. A TTS engine may map it to a speech rate parameter. A human reader uses it as a cue for how much silence to leave between sentences.

### Duration Estimation

Duration is estimated from word count and pace:

```text
duration = word_count / words_per_minute * 60
```

The `duration` metadata field records the estimate. Authors should verify by reading the view aloud — estimated and actual duration should agree within ten seconds. If they diverge, the content is either too dense (listener cannot absorb at the stated pace) or too sparse (unnecessary padding).

---

## 11. Pronunciation Hints

Voice views include pronunciation hints for terms that a standard English TTS engine might mispronounce. The format is the term followed by its pronunciation in parentheses:

```text
Qwen (pronounced "chwen")
Hono (pronounced "hoh-no")
Kompanchenko (pronounced "kom-pan-CHEN-ko")
pnpm (pronounced "pee-en-pee-em")
CalVer (pronounced "kal-ver")
```

### Rules

1. **First occurrence only.** The hint appears once, at the first mention. Subsequent uses of the term do not include the hint.

2. **English phonetic approximation.** Hints use informal English phonetics, not IPA. The audience is AI systems and non-specialist human readers, not linguists.

3. **Stress marking.** Use ALL CAPS for the stressed syllable when stress placement is non-obvious: `"kom-pan-CHEN-ko"`.

4. **Skip common terms.** Do not add hints for terms that TTS engines handle reliably: common English words, well-known brand names (Google, Microsoft, Amazon), standard technical terms (API, PostgreSQL, JavaScript).

5. **Locale-specific hints.** Translated voice views may need different pronunciation hints. A Ukrainian voice view does not need hints for Ukrainian words but may need them for English technical terms.

---

## 12. Relationship to Display Views

Voice views and display views coexist as peer surfaces. Neither is derived from the other. Both are derived from claims.md.

```text
claims.md (reasoning surface)
    |
    ├── views/overview.md (display surface — visual)
    └── views/voice/briefing.md (voice surface — auditory)
```

The same knowledge produces fundamentally different artifacts for each channel. A claim like:

```markdown
- [C010] 7 packages, ~85K lines TS, pnpm monorepo
  {0.99|o|E010|2026-03-18} types(6.3K) db(6.6K) api(31K) demo(33.2K)
  matching(4.4K) scaffolding(3.3K) knowledge(650)
```

Becomes this in a display view:

```markdown
| Layer | Technology |
|-------|-----------|
| Codebase | ~85K lines TypeScript, 7 packages |
| Monorepo | pnpm |
```

And this in a voice view:

```text
The codebase has about eighty-five thousand lines of TypeScript across seven packages.
It is organized as a monorepo using pnpm.
```

Same fact. Three representations. Each optimized for its channel.

### When to Create Voice Views

Not every pack needs voice views. Create them when:

- The pack's knowledge will be delivered in voice conversations
- The pack serves a briefing function (meeting prep, status updates)
- The domain includes terms requiring pronunciation guidance
- The pack is used with speech synthesis (OpenAI Realtime, etc.)

Display-only packs (technical architecture, code documentation) rarely need voice views. Briefing-oriented packs (fundraise, project status, meeting prep) almost always do.

---

## 13. Bundle Integration

Voice views are included in bundles with the `--include-voice` flag (see `spec/BUNDLE.md`):

```bash
kpack bundle my-project --include-voice
```

In the bundle format, voice views use the section marker `--- VOICE: {view-name} ---`:

```markdown
--- VOICE: briefing ---
<!-- voice: briefing -->
<!-- duration: ~75 seconds -->
...spoken content...

--- VOICE: elevator ---
<!-- voice: elevator -->
<!-- duration: ~30 seconds -->
...spoken content...
```

Voice views are excluded from bundles by default. They are also excluded from clipboard bundles (`--clip`), which include only claims and the primary display view. The rationale: clipboard bundles target web chat interfaces where voice is not the consumption mode.

---

## 14. Antipatterns

| Antipattern | Why it fails | Correct approach |
|---|---|---|
| Reading a display view aloud | Tables become incomprehensible, numbers are unspeakable, density overwhelms | Use the voice view |
| Adding markdown formatting to voice views | Bold markers are spoken or cause TTS glitches | Keep voice views as plain spoken text |
| Writing voice views longer than three minutes | Listener attention degrades; they cannot rewind | Split into multiple views or reduce scope |
| Composing speech from claims on the fly | Inconsistent, slow, spends inference tokens on formatting | Render voice views in advance |
| Using voice views for visual display | Missing structure, too sparse, no tables or formatting | Use display views for visual contexts |
| Omitting pronunciation hints for domain terms | TTS mispronounces key terms, breaking listener trust | Add hints at first occurrence |
| Putting claim notation in voice views | `{0.95|i|E001}` is unpronounceable | Voice views contain no claim notation |
