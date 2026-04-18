<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# KP:1 Specification

> **Status:** Editor's Draft
> **Editor:** Timothy Kompanchenko

The normative contract for Knowledge Pack version 1.

## How to Read This

**Start with [CORE.md](CORE.md).** It is the implementable Core specification
-- everything required to build a conformant KP:1 parser and validator. If you
are implementing KP:1, CORE.md is sufficient.

**[SPEC.md](SPEC.md)** is the full specification (~110 KB). It covers the
same ground as CORE.md plus all companion topics in a single document. It
predates CORE.md and contains additional discussion and rationale.

**Companion documents** extend the Core with optional features:

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
| [NOTES.md](NOTES.md) | AI note-taking integration |

## Interoperability

**[MAPPING.md](MAPPING.md)** maps KP:1 concepts to RDF/JSON-LD, PROV-O, and
Nanopublications with clean/lossy/impossible grades for each field.

## Validation

Formal grammar and test fixtures live in [`../conformance/`](../conformance/).
