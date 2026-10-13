<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Draft coherence and preservation boundaries

> **Status:** Proposed for editor review and public discussion
> **Date:** 2026-10-11

## Problem

The draft's prose, schemas and reference behavior differ on ordinary workflows: an active successor cannot resolve a claim moved to history; evidence metadata and reversible bodies are interpreted differently by tools; selection prose requires a scope the schema omits. Some portability statements promise more than the defined carriers provide. Preview publication needs a coherent contract and honest capability boundaries.

## Proposed decisions

1. **Keep one pack-local claim identity namespace.** Active and historical claims share uniqueness, evidence obligations, relation targets and acyclic supersession. Preserve the original historical bullet and its relations; editorial transition headings are context, not identities. Exercise two generations, retraction and withdrawal of the last active claim while retaining document structure. Strict history checks preserve literal record boundaries.
2. **Share evidence segmentation and registered body decoding.** Parse both metadata forms, require nonempty unique required fields and valid captured dates, segment encoded records before decoding and preserve unknown encodings. Decode round-trip concerns logical text; byte custody remains with original files.
3. **Align authoring checks with the specified metadata contract.** Verbose field order is insignificant; cardinality and known fields are enforced after syntax parsing. Missing declared test cases fail. Empty manifests return diagnostics. Preserve the documented distinction between the CLI PEG toggle and normative warning levels.
4. **Align kind requirements without inventing assertions.** Definition and policy packs use their document directories; mixed packs carry claims plus at least one such document. Generic readers retain canonical filenames; alternate carrier mappings need an explicit profile. If the optional `composition` field is declared, it names only the canonical `composition.yaml`, which must exist. The reference checker does not yet validate definition/policy document schemas.
5. **Make selection scope explicit.** Require nonempty purpose, collection and scope; keep purpose free text. Members may be empty for an explicitly scoped no-matches result. Pack-name references are live; preparation date is not a freeze. Resolvers establish membership and report ambiguity. Reproducible schedules need retained, pinned revisions in a declared profile.
6. **State changed hash rules and historical verification modes.** Match the enumerated OS metadata by components at any depth, including AppleDouble. Keep ordinary dotfiles and non-root receipt files. Pin the applied rules in verification receipts; do not silently retrofit historical artifacts or turn fallback into current-rule success. Signing payload version and hash policy are separate concepts.
7. **Limit carrier promises to defined formats.** Reading bundles and semantic JSON cannot preserve every file or an existing seal. Integer-valued data does not establish byte stability. Operational entity/claim associations lack a generic file carrier; avoid portable reconstruction guarantees until a versioned mapping exists.
8. **Preserve epistemic distinctions.** Source reports, dated world facts and current assessments are different propositions. A newer report does not refute an accurate historical report. Preserve material attribution, roles, methods, dates and decision context in claims and their views; event-specific knowledge can remain valuable after archival. Scope absence findings to the search actually recorded. Changed support judgments need separate assessments or complete preserved successors, not mutation of issued relations. Preserve original multilingual evidence, make locale-to-path resolution unambiguous, and expose the one-transcript-per-locale limit instead of silently overwriting sources.
9. **Separate draft, release and implemented support.** Retain existing citable release metadata; record the complete unreleased range and capabilities. Compiler ranking is a deterministic presentation preference, not an adopted assessment, authority to act, source-truth adjudication, chronology inferred from IDs or proof of independent evidence.

## Alternatives and limits

A new universal identity registry, a seventh claim field, a new transcript carrier or a lossless bundle format would enlarge the wire contract without resolving these immediate inconsistencies. They are deferred. Full compiler history reconstruction, definition/policy validation, generic reconciliation, profile-specific snapshot resolution and archive cryptographic verification remain separately scoped work.

[COMPATIBILITY.md](../spec/COMPATIBILITY.md) records behavior changes and reference coverage. The editor must summarize the proposal in the public issue record before normative acceptance under [GOVERNANCE.md](../GOVERNANCE.md). This decision record does not claim that discussion or acceptance has already happened.
