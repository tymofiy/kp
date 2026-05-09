<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# KP:1 Specification

> **Status:** Editor's Draft
> **Editor:** Timothy Kompanchenko

The normative contract for Knowledge Pack version 1.

## Three normative lanes

KP:1 carries normative weight across three documents, each with a distinct role. A correct implementation reads from all three.

**[CORE.md](CORE.md) — implementer surface.** The minimum required to be KP:1-conformant. CORE.md is intentionally narrow: just enough to build interoperable parsers and validators. If you are implementing KP:1, start here; CORE.md is sufficient to ship a conformant parser.

**[SPEC.md](SPEC.md) — full normative spec, rationale, and ecosystem.** The comprehensive document. SPEC.md predates CORE.md and covers the same ground plus rationale, ecosystem context, and historical decisions. Where CORE.md and SPEC.md appear to disagree on the implementable surface, CORE.md (the narrower, more recent extraction) is authoritative; SPEC.md provides the surrounding "why."

**Companion documents — topic-authoritative for their domains.** Each companion (VOICE, MULTILINGUAL, ARCHIVE, COMPOSITION, EXTENSIONS, etc.) owns its topic. For matters within its domain, the companion is the normative authority — not merely an "extension" of CORE/SPEC. A producer or consumer that needs to handle locales correctly must read MULTILINGUAL.md; CORE.md alone is not sufficient.

Companions do not weaken CORE: where CORE makes a claim, that claim holds. But for topics CORE explicitly punts to a companion (per CORE's `see [COMPANION]` cross-references), the companion carries the full normative weight on that topic.

| Document | Topic |
|----------|-------|
| [VOICE.md](VOICE.md) | Voice surfaces for rendering claims as prose |
| [COMPOSITION.md](COMPOSITION.md) | Multi-pack composition and meetings |
| [LIFECYCLE.md](LIFECYCLE.md) | Pack lifecycle management |
| [MULTILINGUAL.md](MULTILINGUAL.md) | Multilingual support |
| [ORGANIZATION.md](ORGANIZATION.md) | Pack organization and categories |
| [CONSISTENCY.md](CONSISTENCY.md) | Cross-pack consistency patrol |
| [CONVENTIONS.md](CONVENTIONS.md) | Naming conventions |
| [STORAGE.md](STORAGE.md) | Storage formats and serialization |
| [BUNDLE.md](BUNDLE.md) | Bundling and distribution |
| [ARCHIVE.md](ARCHIVE.md) | ZIP archive, integrity chain, signatures |
| [DEFINITIONS.md](DEFINITIONS.md) | Definition and policy document kinds |
| [EXTENSIONS.md](EXTENSIONS.md) | Producer-defined `extensions.*` blocks catalogue |
| [NOTES.md](NOTES.md) | AI note-taking integration |
| [PLAYBACK.md](PLAYBACK.md) | Self-driving presentation playback (experimental) |
| [RECONCILIATION.md](RECONCILIATION.md) | Cross-pack reconciliation protocol (stub — design deferred to v0.9 / v1.0) |

## Interoperability

**[MAPPING.md](MAPPING.md)** maps KP:1 concepts to RDF/JSON-LD, PROV-O, and
Nanopublications with clean/lossy/impossible grades for each field.

## Validation

Formal grammar and test fixtures live in [`../conformance/`](../conformance/).
