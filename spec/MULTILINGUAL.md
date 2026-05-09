<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Multilingual Support — Knowledge Pack Companion Spec

> **Date:** 2026-03-22
> **Status:** Draft

---

## 1. Scope

This companion spec defines how Knowledge Packs support multiple languages. It covers PACK.yaml locale metadata, directory layout for translated views, translation workflow, drift detection, and tooling integration.

**Out of scope:** The canonical language conventions themselves (American English rules, Merriam-Webster hierarchy, etc.) are specified in `spec/CONVENTIONS.md`.

---

## 2. Core Principles

**P1. Claims are always English.** The reasoning surface (`claims.md`) is written in American English. It is never bilingual, never translated. Translations exist only at the view layer.

**P2. Translations are derived views, never authoritative.** If a translated view disagrees with `claims.md`, claims win. Translations carry no independent authority — they are rendered presentations of the canonical knowledge, not alternative sources of truth.

**P3. Locale first, then surface.** Multilingual views are organized by locale, then by surface type. This makes locale the higher-order grouping, which is cleaner for discovery, grep, and deletion.

**P4. Non-English proper nouns preserved in original script.** Per standard linguistic conventions, proper nouns (people, companies, places) retain their original-language rendering. A Ukrainian view refers to "Timothy Kompanchenko", not a transliterated form. Ukrainian-origin names use Ukrainian script where that is the original form.

---

## 3. PACK.yaml — `locales` Section

The `locales` block declares the canonical language and enumerates available translations.

```yaml
locales:
  canonical: en-US                     # Canonical language (always American English)
  available:
    - locale: uk-UA                    # BCP 47 language tag
      display_name: "Українська"       # Native-language display name
      status: draft                    # draft | reviewed | verified
      views: [overview, briefing]      # Which views have been translated
      derived_from: "claims@2026.03.22"  # Pack version the translation was generated from
      translator: machine              # machine | human | hybrid
      reviewed_by: null                # Human reviewer (null if unreviewed)
```

### Field Reference

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `canonical` | Yes | BCP 47 tag | The canonical language. Always `en-US`. |
| `available` | No | List | Translated locales. Omit if monolingual. |
| `available[].locale` | Yes | BCP 47 tag | Language tag for the translation (e.g., `uk-UA`). |
| `available[].display_name` | Yes | String | Name of the language in its own script. |
| `available[].status` | Yes | Enum | Translation maturity: `draft`, `reviewed`, `verified`. |
| `available[].views` | Yes | List | View names that have been translated. |
| `available[].derived_from` | Yes | String | Pack version string the translation was built from. Format: `claims@{CalVer}`. |
| `available[].translator` | Yes | Enum | Who performed the translation: `machine`, `human`, `hybrid`. |
| `available[].reviewed_by` | No | String | Name of human reviewer. Required when `status` is `reviewed` or `verified`. |

### Language Tags

All language tags use **BCP 47** format (IETF BCP 47 / RFC 5646):

| Tag | Language |
|-----|----------|
| `en-US` | American English (canonical) |
| `uk-UA` | Ukrainian |
| `de-DE` | German |
| `fr-FR` | French |
| `ja-JP` | Japanese |
| `ar-SA` | Arabic |

The subtag after the hyphen is the region. Use the most specific applicable tag. The short form (e.g., `uk` without `-UA`) is acceptable in directory names for brevity.

---

## 4. Directory Structure

Translated views live in locale subdirectories under `views/`. The locale directory mirrors the structure of the root `views/` directory.

```text
{name}.kpack/
├── PACK.yaml
├── claims.md                          # Always English — never translated
├── evidence.md
├── views/
│   ├── overview.md                    # English display view
│   ├── architecture.md                # English display view
│   ├── voice/
│   │   └── briefing.md                # English voice view
│   └── uk/                            # Ukrainian locale directory
│       ├── overview.md                # Ukrainian display view
│       ├── architecture.md            # Ukrainian display view
│       └── voice/
│           └── briefing.md            # Ukrainian voice view
```

### Layout Rules

1. **Locale directory name** uses the short language code: `uk`, `de`, `fr`, `ja`, `ar` — not the full BCP 47 tag.

2. **Locale before surface type.** Ukrainian voice briefing is `views/uk/voice/briefing.md`, not `views/voice/uk/briefing.md`. Rationale: locale is the higher-order grouping. You can `rm -rf views/uk/` to remove all Ukrainian content. You can `ls views/uk/` to see everything available in Ukrainian.

3. **Mirror structure, not filenames.** The translated `views/uk/overview.md` corresponds to `views/overview.md`. No filename suffixes (not `overview.uk.md`). The directory provides the locale signal.

4. **Selective translation.** Not every view needs to be translated. The `views` list in the `locales` section declares which views exist for each locale. Unlisted views are not available in that language.

5. **No translated claims or evidence.** Only files under `views/` are translated. `claims.md`, `evidence.md`, `entities.md`, and `history.md` remain English-only.

---

## 5. Translation Status

Each locale has a `status` field tracking translation maturity.

| Status | Meaning | Requirements |
|--------|---------|--------------|
| `draft` | Machine-generated or initial human translation | `translator` field set. No human review. |
| `reviewed` | A human has read the translation and confirmed accuracy | `reviewed_by` field set. Factual accuracy verified against claims. |
| `verified` | A domain-fluent native speaker has approved the translation | `reviewed_by` field set. Linguistic quality and domain terminology confirmed. |

### Status Transitions

```text
draft → reviewed → verified
  ↑                    │
  └────────────────────┘  (claims change → status resets to draft)
```

When `claims.md` is updated, all translations that derived from the previous version reset to `draft`. The `derived_from` field determines whether a translation is current or stale. Status never auto-upgrades — it requires explicit human action.

---

## 6. Translation Drift Detection

Translation drift occurs when `claims.md` has been updated but translated views still reflect a previous version.

### Detection Mechanism

Each translated view includes a generation metadata comment:

```markdown
<!-- translated: 2026-03-22 | derived_from: claims@2026.03.22 | locale: uk-UA | translator: machine -->
```

The `derived_from` value is compared against the current pack version in `PACK.yaml`. If they differ, the translation is stale.

### `derived_from` Format

```text
claims@{CalVer}
```

Example: `claims@2026.03.22` means the translation was generated from the `2026.03.22` version of `claims.md`.

### Staleness Rules

1. **Stale translation** = `derived_from` version does not match the current pack `version` in PACK.yaml.
2. **Stale translations are warnings, not errors.** A translation may intentionally lag during active editing of claims.
3. **Stale translations reset status to `draft`.** A previously `verified` translation becomes `draft` when claims change, because the content it was verified against no longer matches.
4. **`kpack lint` reports stale translations.** It compares each locale's `derived_from` against the current pack version and emits a warning for mismatches.

---

## 7. Translation Workflow

### Generation

```bash
kpack translate my-project.kpack/ --locale uk-UA
```

1. Reads `claims.md` to understand the domain knowledge.
2. Reads the English view files listed for the target locale.
3. Generates translated view files in `views/{locale}/`.
4. Inserts the generation metadata comment in each translated file.
5. Updates `PACK.yaml` — sets `derived_from` to the current pack version, `status` to `draft`, `translator` to `machine`.

### Review

A human reviewer reads the translated views, corrects errors, and updates the locale entry:

```yaml
    - locale: uk-UA
      status: reviewed              # upgraded from draft
      derived_from: "claims@2026.03.22"
      translator: hybrid            # machine + human corrections
      reviewed_by: "Olena Shevchenko"
```

### Verification

A domain-fluent native speaker confirms both linguistic quality and domain-specific terminology:

```yaml
    - locale: uk-UA
      status: verified              # upgraded from reviewed
      reviewed_by: "Olena Shevchenko"
```

### Re-translation on Claims Change

When `claims.md` is updated (new pack version):

1. Run `kpack translate --check my-project.kpack/` to identify stale translations.
2. Run `kpack translate my-project.kpack/ --locale uk-UA` to regenerate drafts.
3. Human review cycle repeats.

### Check Command

```bash
kpack translate --check my-project.kpack/
```

Output:

```text
my-project.kpack/
  uk-UA: STALE (derived_from: claims@2026.03.18, current: 2026.03.22)
    views/uk/overview.md — needs re-translation
    views/uk/voice/briefing.md — needs re-translation
```

---

## 8. Lint Integration

`kpack lint` includes the following multilingual checks:

| Check | Severity | Description |
|-------|----------|-------------|
| Locale directory exists | Error | Every locale in `available` must have a corresponding `views/{locale}/` directory. |
| Declared views exist | Error | Every view listed in a locale's `views` array must exist as a file in `views/{locale}/`. |
| `derived_from` present | Error | Every locale entry must have a `derived_from` field. |
| Translation freshness | Warning | `derived_from` version differs from current pack version. |
| Generation comment present | Warning | Translated view files should contain the `<!-- translated: ... -->` metadata comment. |
| Reviewer required | Warning | Locales with `status: reviewed` or `status: verified` should have `reviewed_by` set. |
| Orphan locale directories | Warning | `views/{locale}/` directories that are not declared in `PACK.yaml` `locales.available`. |

---

## 9. Translated View File Format

Translated views follow the same format as English views (standard GFM markdown) with two additions:

### Generation Metadata Comment

Every translated view begins with a generation metadata comment:

```markdown
<!-- translated: 2026-03-22 | derived_from: claims@2026.03.22 | locale: uk-UA | translator: machine -->
```

| Field | Description |
|-------|-------------|
| `translated` | Date the translation was generated or last updated. |
| `derived_from` | Pack version the translation was built from. |
| `locale` | BCP 47 tag of the target language. |
| `translator` | Who performed the translation: `machine`, `human`, `hybrid`. |

### Source Traceability

Translated views preserve the same `<!-- source: C001, C002 -->` comments as English views. Claim IDs are language-independent — they always reference the English `claims.md`.

### Proper Noun Handling

Non-English proper nouns are preserved in their original script:

- **Ukrainian names in Ukrainian text:** Use Ukrainian script (e.g., "Тимофій Компанченко").
- **English names in Ukrainian text:** Keep Latin script (e.g., "Timothy Kompanchenko" remains as-is — do not transliterate to Cyrillic).
- **Company/product names:** Retain original form unless an established localized name exists (e.g., "Google" stays "Google", not "Гугл").
- **Technical terms:** Preserve English technical terms where no standard translation exists in the target language. Provide a parenthetical gloss on first use if the term may be unfamiliar.

---

## 10. First Target Locale: Ukrainian (uk-UA)

Ukrainian is the first non-English locale for Knowledge Packs. Implementation notes:

- **Script:** Cyrillic. No RTL considerations.
- **BCP 47 tag:** `uk-UA`
- **Directory name:** `uk`
- **Display name:** `Українська`
- **Use case:** Knowledge packs readable by Ukrainian-speaking family members and collaborators.
- **Initial translator:** `machine` (LLM-generated), with human review planned.

### Example Pack Structure

```text
solar-energy-market.kpack/
├── PACK.yaml
├── claims.md                          # English
├── views/
│   ├── overview.md                    # English
│   ├── voice/
│   │   └── briefing.md                # English
│   └── uk/
│       ├── overview.md                # Ukrainian
│       └── voice/
│           └── briefing.md            # Ukrainian
```

### Example PACK.yaml

```yaml
name: solar-energy-market
version: 2026.03.22
domain: energy/market-analysis

locales:
  canonical: en-US
  available:
    - locale: uk-UA
      display_name: "Українська"
      status: draft
      views: [overview, briefing]
      derived_from: "claims@2026.03.22"
      translator: machine
      reviewed_by: null
```

---

## 11. Future Considerations

These are not specified in this version but inform the design:

- **Right-to-left scripts (Arabic, Hebrew).** The directory convention and metadata format support RTL languages without changes. Rendering is a platform concern, not a pack concern.
- **CJK languages.** No structural changes needed. Character encoding is UTF-8 throughout.
- **Claim-level language anchoring.** Some claims contain language-specific content (quotes, proper nouns). A future spec version may add per-claim language markers. For now, the pack-level `linguistic_epoch` field in PACK.yaml provides sufficient anchoring.
- **Translation memory.** Repeated translations of similar packs could benefit from shared glossaries or translation memory. Not specified here — this is a tooling optimization, not a format concern.
- **Automated quality scoring.** Machine translations could carry a quality confidence score. Deferred until there is enough translation volume to calibrate such scores.

---

## 12. Decision Log

| # | Decision | Alternatives Considered | Rationale |
|---|----------|------------------------|-----------|
| D1 | Canonical language is American English; claims are never bilingual | Bilingual claims, per-claim language tags | Complexity explosion. Claims are the reasoning surface — one language keeps them unambiguous. Translations belong at the view layer. |
| D2 | Translation storage uses locale subdirectories (`views/{locale}/`) | Filename suffixes (`overview.uk.md`), flat directories | Subdirectories are cleaner for discovery (`ls views/uk/`), removal (`rm -rf views/uk/`), and grep. Filename suffixes create visual clutter and complicate glob patterns. |
| D2a | Locale before surface type (`views/uk/voice/`) | Surface before locale (`views/voice/uk/`) | Locale is the higher-order grouping. A locale is a complete translation; a surface type is a rendering format. You add/remove entire locales, rarely individual surface types within a locale. |
| D2b | Short language code for directory names (`uk`, `de`) | Full BCP 47 tag (`uk-UA`, `de-DE`) | Directories are for humans too. Short codes are sufficient for disambiguation in practice. Full tags remain in PACK.yaml metadata. |
| D2c | Translations are derived views, never authoritative | Co-equal translations, authoritative translations | Knowledge lives in claims.md. Views — including translations — are presentations. If translation disagrees with claims, it is the translation that is wrong. |
