<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Authority, Capabilities and Compatibility

> **Status:** Informative implementation guide for the unreleased editor's draft

## Authority and versions

[CORE.md](CORE.md) defines the generic directory/claim contract. Its normative PEG and manifest schema define syntax and shape; semantic checks apply after parsing. Topic companions govern their declared surfaces, including ARCHIVE, COMPOSITION and DEFINITIONS. CORE takes precedence over overlapping legacy prose in SPEC. Informative documents (AUTHORING, MAPPING, RATIONALE, STORAGE and this guide) explain practice, not extra universal wire requirements. EXTENSIONS catalogs producer profiles: a profile's rules apply when an implementation claims support for that profile, and cannot relax CORE. PLAYBACK is experimental; RECONCILIATION is a design stub.

`KP:1` in the Rosetta header identifies the format epoch. A manifest `spec_version` identifies a specification revision or release tag; it is not the pack's CalVer `version`, the archive's `seal_version`, or an application profile version. Pin a tag or commit when reporting validation. `spec_uri` remains an offline-safe informational pointer, never a required network dependency.

Reference tooling identifies this changed draft with a `+unreleased` version suffix; this is not a release tag. Verification still needs the source commit.

The latest citable release remains `v0.8.4-preview` (2026-06-13). The changes under [CHANGELOG.md — Unreleased](CHANGELOG.md#unreleased--editors-draft) have no new release tag or DOI. Preview/editor's-draft status does not promise stable V1 compatibility. Cite the released snapshot for that snapshot's requirements and a commit for newer requirements.

## Capability boundaries

| Surface | Reference coverage | What a passing check does not establish |
|---------|--------------------|----------------------------------------|
| Manifest, claims, history and evidence | `conformance/run.py --strict`, fixture suite and contract tests | Source truth, confidence calibration, complete coverage of every clause, cross-pack target resolution |
| Definition/policy kinds | Manifest and required-file matrix | Validation of the companion's definition/policy YAML document shapes |
| Composition | Published schema, narrative claims exception and selection fixture | Resolver availability, collection membership, historical member snapshots |
| Archives | Signatures schema and fixed content-hash vectors | ZIP extraction behavior, digest verification of a supplied archive, cryptographic signature verification or chain ancestry |
| Voice/locales and views | Companion rules; editorial review | Automatic drift detection, provenance completeness or implemented rendering commands |
| Producer extensions | Manifest's open `extensions` lane | Support for a particular profile, unknown-payload interpretation or portable operational claim associations |
| Graph compiler | Experimental claim-bearing canonical-file projection and its unit tests | Whole-format conformance, full history reconstruction or byte-preserving archival |
| Reference CLI | `lint` delegates to the validator; `new` scaffolds a starter | Other commands: they print contract pointers, not implemented behavior |

The default runner uses diagnostic regex parsing. `--strict` additionally executes the PEG for `claims.md` and the Claim subrule for historical bullets. Neither CLI mode implements CORE's normative permissive warning policy: SC-07 through SC-12 are errors in both. A suite pass is evidence for the exercised cases, not certification of every format surface. Missing declared fixtures fail the suite.

## Compatibility changes in this draft

- **Empty current state:** A claim document may contain a section with no active claims after withdrawal. The header, compact frontmatter, H1 and at least one H2 remain required; history retains the original claim.
- **History:** IDs are pack-local across active and historical records. Existing successors pointing into `history.md` now resolve in the validator. Duplicate active/history IDs are rejected; retain original historical metadata and relations.
- **Composition declaration:** If PACK.yaml declares `composition`, its value must be `composition.yaml` and that file must exist. An existing canonical file is detected without the field. Alternate filenames are outside generic reference support.
- **Metadata vocabulary and dates:** Invalid calendar dates and unknown depth/nature values now return diagnostics instead of slipping through a regex-only parse.
- **Evidence:** Both metadata layouts are parsed. Required fields and real captured dates are checked. `markdown-backslash-v1` decodes only declared, registered bodies after segmentation; unmarked bodies are never heuristically decoded. Unknown encodings preserve the encoded text and expose a warning.
- **Seal payload v2:** Quoted `seal_version: "2"` selects the identity-binding payload in ARCHIVE. Absence selects legacy v1. This does not select file-exclusion/hash rules or guarantee the authenticity of referenced packs.
- **Archive exclusions:** Component matching at every depth and AppleDouble exclusions can change a pack hash compared with a historical policy. Do not rewrite accepted pack bytes or reissue a seal silently. When historical verification is requested, use its pinned historical rules and record that revision/mode in the receipt. This does not require a retrospective scan, migration or new compatibility implementation. If a verifier offers a historical compatibility mode, selection must be explicit; never turn a current-rule mismatch into an unqualified success through automatic fallback. No new hash-policy wire field is defined here.
- **Selection:** `scope` is now required and nonempty, agreeing with the prose contract. New or revised selection manifests must state their authored scope; this does not require rewriting retained historical packs. Core references remain live pack names; dated reproducibility requires a declared snapshot profile and retained member revisions.
- **Bundles and storage:** A reading bundle, clipboard projection or semantic JSON round-trip does not preserve all pack files or sealed bytes. Keep the original directory or archive for lossless export. Re-sealing changed bytes creates a new receipt, not preservation of the old signature.

## Reporting support

Report the exact specification revision, supported kinds, syntax modes, companions and application profiles, then the fixtures/checks actually exercised. Distinguish schema acceptance, semantic validation, logical-text round-trip, file-byte equality, content-hash verification and signature/chain verification. Do not collapse these into one “KP:1 verified” claim.

Unresolved design remains explicit: generic cross-pack reconciliation; a versioned file carrier for per-claim operational entity associations; a multi-transcript-per-locale extension shape; profile-specific revision resolution; and full compiler history support. None is supplied by adding an undocumented claim metadata field.
