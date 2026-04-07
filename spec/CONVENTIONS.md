<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Linguistic Conventions — Knowledge Pack Companion Spec

> **Parent:** SPEC.md v0.4
> **Date:** 2026-03-22
> **Status:** Draft
> **Decisions:** D1 (canonical language — American English, Merriam-Webster)

Canonical conventions for American English text in Knowledge Pack claims, evidence,
entities, and views. These conventions govern all human-language content in the
Knowledge Pack system. Machine-readable identifiers (IDs, slugs, URIs) follow their
own conventions defined in the schema.

Source of truth: this document.

## Design Principles

1. **English-canonical, multilingual-derivable.** All claims are authored in American
   English. Other language views are derived, never authoritative.
2. **Dual audience.** Claims are consumed by LLMs (reasoning surface) and displayed
   to humans (view surface). When conventions conflict between the two audiences,
   the reasoning surface wins and the view surface adapts.
3. **Unambiguous over elegant.** Prefer explicit, literal phrasing over idiomatic or
   culturally dependent expression. This improves both LLM parsing and translation.
4. **Consistent over correct.** When multiple conventions are defensible, pick one and
   apply it everywhere. Consistency reduces parsing variance in LLMs more than any
   specific format choice.
5. **Atomic over compound.** One assertion per claim. Compound claims obscure
   verification scope and degrade confidence scoring.

---

## Conventions Table

| # | Area | Convention | Example | Notes |
|---|------|-----------|---------|-------|
| 1 | **Spelling authority** | Merriam-Webster (first listed entry) | "canceled" not "cancelled" | M-W is the de facto standard referenced by AP, Chicago, Google, Microsoft, Apple |
| 2 | **Style fallback** | Chicago Manual of Style, 18th ed. | — | For questions M-W doesn't answer (hyphenation edge cases, etc.) |
| 3 | **Locale tag** | `en-US` | PACK.yaml: `linguistic_epoch: en-US-2026` | BCP 47 language tag; year suffix anchors semantic drift |
| 4 | **Dates** | ISO 8601: `YYYY-MM-DD` | `2026-03-22` | Never "March 22, 2026" in claims. Views may localize |
| 5 | **Date ranges** | ISO 8601 with "to" | `2026-01-01 to 2026-03-31` | Not en-dash ranges in claims; views may use en-dash |
| 6 | **Times** | ISO 8601 with UTC | `14:30 UTC` or `2026-03-22T14:30:00Z` | UTC always; IANA zone in parentheses if local matters: `(America/New_York)` |
| 7 | **Large numbers** | Numeral + word | `$2 million`, `3.5 billion` | Not `$2M` (too informal) or `$2,000,000` (noisy). Full form in evidence when precision matters |
| 8 | **Percentages** | Symbol, no space | `50%` | Not "50 percent" or "50 %" |
| 9 | **Numeric ranges** | "to" connector | `2 to 5`, `$10K to $50K` | Not `2-5` (ambiguous hyphen) or `2–5` (en-dash requires typography). Views may upgrade to en-dash |
| 10 | **Capitalization: headings** | Sentence case | `## Team and timeline` | Not "Team and Timeline". Only proper nouns capitalized |
| 11 | **Capitalization: claims** | Sentence case | `Platform supports 7 AI capabilities` | Claims are assertions, not titles |
| 12 | **Serial comma** | Always (Oxford comma) | `types, db, and api` | Non-negotiable in claims. Eliminates a class of parsing ambiguity |
| 13 | **Dashes: hyphen** | Compound modifiers only | `well-known`, `single-GPU` | Standard hyphen character `-` (U+002D) |
| 14 | **Dashes: en-dash** | Ranges in views only | `pages 128–134` | En-dash `–` (U+2013). Never in claims.md; use "to" |
| 15 | **Dashes: em-dash** | Parenthetical breaks | `scaffolding — not matching — is the product` | Em-dash `—` (U+2014) with spaces. Sparingly in claims; acceptable in views and evidence |
| 16 | **Acronyms** | Expand on first use per section | `Model Context Protocol (MCP)` | Subsequent uses: `MCP`. Skip expansion for universals: `API`, `URL`, `USD`, `AI` |
| 17 | **Tense: current facts** | Simple present | `Platform uses Qwen 3.5` | Present tense = "true as of pack version date" |
| 18 | **Tense: historical facts** | Simple past | `Founded in 2024` | Clear temporal anchoring; avoid perfect tenses |
| 19 | **Hedging** | External to claim text | Claim: `Team has 30 mentors` / Confidence: `0.40` | Do not embed "possibly", "might", "allegedly" in claim text. Confidence scores carry uncertainty |
| 20 | **Negation** | Explicit assertion | `Platform does not store PII locally` | Never rely on absence of a claim to imply negation. State negative facts explicitly |
| 21 | **Pronouns** | Minimize; repeat nouns | `The platform supports...` not `It supports...` | Especially across sentence boundaries. Improves LLM parsing and translation accuracy |
| 22 | **Granularity** | One verifiable assertion per claim | One `[C###]` = one fact | Compound claims must be decomposed. "A and B" becomes two claims with `→supports` relation |
| 23 | **Product names** | Official capitalization, always | `Qwen 3.5`, `OpenRouter`, `Fly.io` | First use: full name. No trademark symbols in claims (too noisy) |
| 24 | **Measurement units** | SI / metric preferred, with context | `3B active params`, `85K lines` | Use K/M/B suffixes for informal magnitude in claims; precise numbers in evidence |
| 25 | **Currency** | ISO 4217 code or `$` for USD | `$2 million`, `EUR 500K` | Dollar sign for USD (dominant context). ISO code for all others |
| 26 | **Phone numbers** | E.164 with spaces | `+1 555 012 3456` | Canonical storage format. Views may add parentheses |
| 27 | **Quotation marks** | Straight double quotes | `"scaffolding"` not `"scaffolding"` | ASCII `"` (U+0022). Curly quotes in views only |
| 28 | **Lists in prose** | Semicolons for complex items | `types (6.3K); db (6.6K); api (31K)` | Commas for simple items; semicolons when items contain internal commas |
| 29 | **Non-English terms** | Preserve original script + romanization | `Київ (Kyiv)` | Follow i18n.md conventions. Never anglicize proper nouns |
| 30 | **Sentence length** | Target 15-25 words | — | Aligns with controlled language standards (ASD-STE100). Improves translation and LLM parsing |

---

## Justifications

### 1. Merriam-Webster as spelling authority

Merriam-Webster is the most widely adopted spelling reference in American English.
The AP Stylebook explicitly defers to M-W for words it doesn't cover. Apple's style
guide references M-W as its spelling standard. Google and Microsoft developer
documentation teams use M-W as their baseline. The "first listed entry" rule
(when M-W lists multiple spellings) follows AP and Chicago convention.

**Key M-W vs. alternatives:**
- M-W is descriptive and comprehensive (documents actual usage)
- American Heritage Dictionary is more conservative but less widely adopted
  institutionally
- AP Stylebook is prescriptive but narrow (journalism-focused, not a dictionary)

### 2. Chicago Manual of Style as style fallback

Chicago is the dominant style authority for non-journalistic American English writing.
It covers edge cases (complex hyphenation, citation format, number styling) that M-W
does not address. Apple explicitly uses Chicago as its style authority with M-W for
spelling. Most technical writing organizations follow the same two-tier hierarchy.

### 3-6. ISO 8601 dates/times

ISO 8601 is unambiguous, machine-parseable, and culture-neutral. LLMs show 8-12%
fewer parsing errors with ISO dates than written-out dates in multilingual contexts.
"to" connector for ranges avoids the hyphen/en-dash ambiguity problem that plagues
mixed human/machine consumption. UTC as default eliminates seasonal timezone confusion
(EST/EDT problem). IANA identifiers (`America/New_York`) handle DST automatically.

### 7-9. Numbers, percentages, ranges

"Numeral + word" (`$2 million`) is recommended by Google, Microsoft, and AP style
guides for technical documentation. The `%` symbol is universally preferred in
technical/scientific contexts. "to" for ranges is clearer for international audiences
and more reliably parsed by both LLMs and regex. These choices optimize the
dual-audience requirement: scannable by humans, unambiguous for machines.

### 10-11. Sentence case

Sentence case is the consensus standard across Google Developer Docs, Microsoft
Writing Style Guide, Apple Style Guide, and Wikipedia Manual of Style. It mirrors
natural reading patterns, reduces cognitive load, and is unambiguous (no debates
about which words to capitalize in title case). Schema.org uses TitleCase for
programmatic type names but sentence case for human-readable labels and descriptions.

### 12. Serial comma (Oxford comma)

The Oxford comma eliminates a class of parsing ambiguity without any downside.
Most academic and technical style guides recommend it. AP is the notable exception
(journalism context, not applicable here). In structured claims where precision
matters, the Oxford comma is non-negotiable.

### 13-15. Dash hierarchy

Hyphens for compounds, en-dashes for ranges, em-dashes for breaks. These are distinct
Unicode codepoints that tokenize differently in LLMs. Using the correct character
improves machine parsing. In claims.md (the reasoning surface), we avoid en-dashes
for ranges because "to" is unambiguous even in plain ASCII contexts. Views can use
proper typographic en-dashes.

### 16. Acronyms

Expand-on-first-use is universal across Google, Microsoft, Apple, and Wikipedia.
Skip expansion for universally understood acronyms (API, URL, etc.). Per-section
expansion (not per-document) accounts for the fact that claims.md sections may be
loaded independently.

### 17-18. Tense

Simple present for current facts (true as of version date) and simple past for
completed events. This follows Wikipedia's convention and aligns with Wikidata's
temporal qualifier pattern. Avoiding perfect and continuous tenses reduces translation
complexity and ambiguity.

### 19. Hedging externalized

Embedding "possibly" or "might" in claim text creates dual ambiguity: is the
uncertainty about the fact or about the phrasing? Knowledge Packs have a dedicated
confidence system (0.0-1.0 normalized scores). The claim text states the assertion;
the confidence score carries the uncertainty. This separation is validated by
fact-checking systems (FEVER, Full Fact) which universally separate claim text
from truth-value metadata.

### 20. Explicit negation

Following Wikidata and open-world assumption principles. The absence of a claim does
not imply its negation. Negative facts ("X does not Y") must be stated explicitly
with their own evidence and confidence scores.

### 21. Pronoun minimization

Controlled language standards (ASD-STE100, Caterpillar Technical English) and
translation-readiness research agree: repeating nouns instead of using pronouns
reduces ambiguity by 15-40%. LLMs are more sensitive to ambiguous pronoun resolution
than human readers who use real-world context.

### 22. Atomic claims

Validated by FEVER dataset methodology, Full Fact practice, and atomic fact
extraction research (AFEV framework). Compound claims create ambiguity in
verification and confidence scoring. The Knowledge Pack relation system
(`→supports`, `←requires`) captures relationships between atomic claims.

### 23-25. Product names, units, currency

Official capitalization for product names follows the ACID test (International
Trademark Association). SI/metric preferred for internationalization. Dollar sign
for USD (dominant context in this corpus) with ISO 4217 codes for other currencies
follows AP and financial industry convention.

### 26-28. Phone, quotes, lists

E.164 for phones is the international standard and machine-parseable. Straight
quotes avoid Unicode encoding issues in plain text and are consistent with Markdown
conventions. Semicolons for complex list items follows Chicago Manual of Style.

### 29-30. Non-English terms, sentence length

Follows the existing i18n.md convention. Sentence length target of 15-25 words
aligns with ASD-STE100 Simplified Technical English and improves both human
comprehension and machine translation accuracy.

---

## Fallback Hierarchy

When a linguistic question arises that is not covered by this document:

```text
1. This document (linguistic.md)
   ↓ not covered
2. Merriam-Webster Dictionary (first listed spelling)
   ↓ not covered (style question, not spelling)
3. Chicago Manual of Style, 18th edition
   ↓ not covered (domain-specific terminology)
4. ISO 704:2022 (Terminology work — Principles and methods)
   ↓ not covered (controlled language question)
5. ASD-STE100 Simplified Technical English principles
   ↓ not covered (knowledge representation question)
6. Wikidata conventions (temporal, multilingual, negation)
   ↓ truly novel
7. Author judgment, documented as a decision in this file
```

The chain reflects a deliberate narrowing: general English → technical English →
terminology science → controlled language → knowledge representation. Each level
addresses questions the previous level cannot.

---

## Knowledge-Pack-Specific Conventions

These conventions are specific to Knowledge Packs and would not appear in a
standard style guide.

### Claim text vs. metadata separation

Claim text is a pure declarative assertion. All epistemic qualification (confidence,
evidence type, temporal scope) lives in the `{confidence|type|evidence|date}` block.
Never mix these layers.

**Wrong:** `Platform probably uses Qwen 3.5 (based on code review in March)`
**Right:** `Platform uses Qwen 3.5` `{0.99|o|E011|2026-03-18}`

### Temporal anchoring

All claims are implicitly anchored to the pack version date. A claim `Platform has
906 tests` means "as of the version date in PACK.yaml." If a claim has a different
temporal anchor, make it explicit: `Platform had 400 tests at v0.30.0`.

### Entity reference style

When referencing entities in claims, use the canonical display name on first mention,
then aliases for brevity. Cross-pack references use `↔pack_name#section` notation.

### Confidence-appropriate language

Even though hedging is externalized to confidence scores, claim text should not
overstate. A claim with 0.60 confidence should not be phrased as an absolute:

**Poor:** `The market is $50 billion` at {0.60}
**Better:** `The addressable market is estimated at $50 billion` at {0.60}

The word "estimated" is not hedging — it describes the claim type (estimation vs.
measurement). This is a factual descriptor, not epistemic qualification.

### Density notation in claims.md

Claims.md uses compressed notation optimized for token efficiency. Conventions that
apply only in claims.md (not views):

- Parenthetical abbreviations: `types(6.3K) db(6.6K) api(31K)` — no spaces
- Slash notation for alternatives: `GPT-3.5-class cost / single-GPU self-hostable`
- Pipe-delimited metadata: `{0.95|i|E001,E002|2026-03-01}`
- Relation symbols inline: `→C002, ⊗C003`

Views expand these into full prose with proper punctuation and spacing.

### Claims across domains

When a Knowledge Pack spans multiple domains (business + technical + legal), each
domain's terminology follows its own standards, but connective language follows this
document. If a legal claim uses "shall" and a technical claim uses "must," both are
correct within their domains. The linguistic conventions here govern the connective
tissue, not domain jargon.

### Translation-ready claim writing

Claims destined for multilingual views should additionally:

- Avoid idioms, metaphors, and cultural references entirely
- Use explicit rather than implicit causal chains
  (**Not:** `Given the burn rate, runway is 18 months`
  **Instead:** `Monthly burn rate is $120K. At $120K/month, $2.1M gives 18 months runway`)
- Make all quantifiers explicit (`several` → `3 to 5`)
- Avoid relative descriptions (`large`, `small`) — use absolute measures
- Keep subject-verb-object order; avoid inverted or embedded clauses

### View-layer typographic upgrades

Views may upgrade plain claims.md notation to proper typography:

| Claims.md | Views |
|-----------|-------|
| `"quoted"` | "quoted" (curly quotes) |
| `2 to 5` | 2–5 (en-dash) |
| `$2 million` | $2,000,000 (when precision needed) |
| `--` | — (em-dash) |
| `2026-03-22` | March 22, 2026 (when locale-appropriate) |

The claims.md form is always canonical. Views are derived presentations.

---

## Scope and Governance

This document governs all human-language content in Knowledge Packs:
- `claims.md` — claim text and prose annotations
- `evidence.md` — source descriptions and excerpts
- `entities.md` — entity labels, descriptions, and relationship labels
- `views/*.md` — pre-rendered display content
- `PACK.yaml` — `description` and other prose fields

It does **not** govern:
- Machine identifiers (IDs, slugs, URIs) — see `namespaces.md`
- Metadata field names — see `system/schemas/knowledge-schema.yaml`
- Name romanization — see `i18n.md`
- Privacy and sensitivity classification — see `privacy.md`

Changes to this document should be versioned in git and noted in the `updated_at`
frontmatter field.
