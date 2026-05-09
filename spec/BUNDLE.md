<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Bundle Format — Knowledge Pack Companion Spec

> **Date:** 2026-03-22
> **Status:** Draft
> **Decisions:** D11 (sharing format), D19 (bundle marker)

---

## 1. Purpose

Knowledge Packs are multi-file directories. When sharing outside the IDE — pasting into a web AI chat, emailing to a collaborator, uploading to an external system — a single-file format is needed.

The bundle format concatenates pack files into one markdown document with clear section markers. Any AI can parse it. Any human can read it.

---

## 2. Format Identifier

All bundles begin with a KP:1 format marker in an HTML comment:

```markdown
<!-- KP:1 BUNDLE — {pack-name} v{version} -->
```

This reuses the existing KP:1 format identifier from the Rosetta Header. Any system that understands KP:1 can parse the bundle. Any system that doesn't sees a markdown comment and ignores it. The Voyager Principle applies — the marker is self-describing.

---

## 3. Full Bundle Format

For persistent sharing, complete pack transfer, or archival:

```markdown
<!-- KP:1 BUNDLE — {pack-name} v{version} -->
<!-- Generated: {ISO-8601 timestamp} -->
<!-- Files: {count} -->

--- PACK.YAML ---
{contents of PACK.yaml}

--- CLAIMS ---
{contents of claims.md}

--- EVIDENCE ---
{contents of evidence.md}

--- ENTITIES ---
{contents of entities.md, if present}

--- VIEW: {view-name} ---
{contents of views/{view-name}.md}

--- VIEW: {view-name-2} ---
{contents of views/{view-name-2}.md}

--- END BUNDLE ---
```

### Parsing Rules

- Section markers are lines matching the pattern `--- {SECTION_TYPE}(: {name})? ---`
- Content between markers belongs to that section
- The `--- END BUNDLE ---` marker is required — it signals clean termination
- Sections may appear in any order, but the recommended order is: PACK.YAML, CLAIMS, EVIDENCE, ENTITIES, then VIEWs
- Missing sections are valid — a pack without evidence simply has no `--- EVIDENCE ---` section

### Optional Sections

| Section | Included by default | Flag to include |
|---------|-------------------|-----------------|
| PACK.YAML | Always | — |
| CLAIMS | Always | — |
| EVIDENCE | Yes | `--no-evidence` to exclude |
| ENTITIES | If present | `--no-entities` to exclude |
| VIEWS | All declared views | `--views overview,briefing` to select |
| HISTORY | No | `--include-history` to include |
| VALIDATION | No | `--include-validation` to include |
| VOICE VIEWS | No | `--include-voice` to include |
| LOCALE VIEWS | No | `--locale uk-UA` to include |

---

## 4. Clipboard Bundle Format

For quick paste into web AI chat interfaces. Optimized for 8K-32K context windows typical of consumer AI interfaces. Strips everything except claims and the primary view:

```markdown
<!-- KP:1 CLIP — {pack-name} -->
{contents of claims.md}

---
{contents of views/overview.md}
```

Evidence, entities, history, and secondary views are omitted. Claims + primary view is usually sufficient for a web chat session. The AI receiving this gets the full reasoning surface plus a human-readable summary.

---

## 5. Visibility Interaction

Bundle generation respects the pack's `visibility` field:

| Visibility | `kpack bundle` behavior |
|------------|------------------------|
| `private` | Warning: "This pack is marked private." Requires `--force` flag. |
| `shared` | Allowed. Private annotations (if any) are stripped. |
| `public` | Allowed. Full content. |

This prevents accidental sharing of sensitive knowledge. The friction is minimal (one flag) but intentional.

---

## 6. CLI Commands

```bash
# Full bundle to stdout
kpack bundle solar-energy-market

# Clipboard format, copied to system clipboard
kpack bundle solar-energy-market --clip

# Full bundle to file
kpack bundle solar-energy-market -o bundle.md

# Selective views
kpack bundle solar-energy-market --views overview,architecture

# Include locale views
kpack bundle solar-energy-market --locale uk-UA

# Include voice views
kpack bundle solar-energy-market --include-voice

# Shareable URL (requires publishing configuration)
kpack bundle solar-energy-market --url

# Force bundle of private pack
kpack bundle personal-contacts --force
```

---

## 7. Round-Trip

A bundle can be unpacked back into a directory:

```bash
kpack unbundle bundle.md -o my-project.kpack/
```

The parser splits on section markers and writes each section to its canonical file. This enables the full round-trip: directory → bundle → transfer → unbundle → directory.

---

## 8. QR Code / Deep Link (Future)

For mobile use: a QR code that encodes a URL pointing to a bundle file. Scan to load a knowledge pack into a voice session. Specification deferred until URL-based sharing infrastructure exists.
