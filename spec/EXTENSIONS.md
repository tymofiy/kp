<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Extensions — Producer-Defined Manifest Metadata

> **Status:** Draft
> **Date:** 2026-04-28
> **Editor:** Timothy Kompanchenko
> **Parent:** [SPEC.md](SPEC.md) §3.2, [CORE.md](CORE.md) §3

---

## 1. Overview

KP:1 keeps the manifest root closed: fields not defined by the schema are
invalid. Experimental or implementation-specific metadata MUST live under
the optional `extensions` object instead of appearing as new top-level keys
([CORE.md §3 "Manifest Extensions"](CORE.md#manifest-extensions),
[SPEC.md §3.2](SPEC.md)).

This document is the catalogue of **producer-defined** extension blocks in
active use across the reference implementation (the public `kp-forge`,
`kp-packs`, and `kp-viewer` repositories). It is informative — KP:1 does
not require any extension to exist, and consumers MUST ignore extension
content they do not understand. New extensions are listed here so producers and
consumers can converge on shared shapes without forcing schema breaks or
prematurely promoting a payload into the core standard.

### Reading Guide

Each extension below specifies:

- **Owner** — which subsystem produces or consumes the block.
- **Status** — `experimental`, `active`, or `deprecated`.
- **Shape** — the YAML/JSON structure under `extensions.<key>`.
- **Compatibility** — what consumers are expected to do when the block is
  absent, malformed, or carries unknown keys.

---

## 2. Producer-defined extension blocks

### 2.1 `extensions.ai_brief` — analyst-facing verdict line

**Owner:** kp-forge enrichment pipeline.
**Status:** active.

The illustrative extension shipped with v0.7.4 ([SPEC.md §3.2](SPEC.md)). A
short headline and verdict produced at end-of-enrichment, surfaced by analyst
tooling as a one-line summary above the dossier. See SPEC.md for the
canonical example.

### 2.2 `extensions.entities` — typed entity graph

**Owner:** kp-forge entity-extraction pipeline.
**Status:** experimental (introduced 2026-04-28).

Promotes the in-memory entity graph to first-class manifest metadata.
Consumed by Decision Workspace materialization and the cross-pack
`entity_index` in the kp-packs relay.

```yaml
extensions:
  entities:
    - id: ent_p_8a3f2c                  # canonical reference ID, see §3.1
      type: person                      # person | company | asset | event
      canonical: Alexei Mordashov       # display name, single source
      aliases:
        - Алексей Александрович Мордашов
        - Mordashov
      external_ids:                     # see §3.2; producers fill what they have
        opensanctions: Q123456
        companies_house: "01495478"
        ofsi: RUS0770
        wikidata: Q1413288
      first_seen_in: [E001, E007]       # evidence IDs that established this entity
      confidence: high                  # high | medium | low | unknown
      role_in_pack: subject             # subject | counterparty | beneficiary
                                        # | sibling | director | other
```

**Cardinality.** A pack MAY emit zero or more entities. The pack's
foreground entity (when one exists) is conventionally first in the array but
order is non-semantic; consumers MUST identify the foreground via
`role_in_pack: subject` rather than position.

**ID stability.** Within a pack, an entity ID never changes once written to
a sealed manifest. Across packs, the relay's `entity_index` resolves
identity by `external_ids` first, then by `(canonical, aliases)` overlap.
See §3.1.

**Compatibility.** Consumers that do not understand the block MUST ignore
it. Producers MAY omit the block entirely; downstream consumers fall back
to the H1 entity annotation in `claims.md`
([CORE.md AR-09](CORE.md#claim-grammar)) when present.

### 2.3 `extensions.relations` — typed edges

**Owner:** kp-forge entity-extraction pipeline.
**Status:** experimental (introduced 2026-04-28).

Typed edges between entities declared in `extensions.entities`. Vocabulary
mirrors `relation_types` defined in [DEFINITIONS.md §3](DEFINITIONS.md).

```yaml
extensions:
  relations:
    - id: rel_001
      from: ent_p_8a3f2c
      to: ent_c_4b1d9e
      type: director_of                 # vocabulary from DEFINITIONS.md §3
      since: "2018-03-15"               # ISO-8601 date, optional
      until: null                       # ISO-8601 date, optional (null = current)
      attributes:                       # edge_attributes from DEFINITIONS.md §3
        confidence: 0.9
        evidence_ids: [E007, E012]
```

**Edge attribute discipline.** Numeric `confidence` on a relation is
machine-internal — surfaces in audit views only, never in user-facing
prose. User-facing dossier copy uses the high/medium/low/unknown labels
defined elsewhere.

**Compatibility.** As with §2.2.

### 2.4 `extensions.intent` — decision frame

**Owner:** kp-forge intent inference module.
**Status:** experimental (introduced 2026-04-28).

The decision-frame tag selected for the pack. Used by the reference
implementation's playbook module to choose `(domain, intent) → Playbook`.

```yaml
extensions:
  intent: SanctionScreen                # current reference vocabulary, v1
  intent_schema_version: "1"            # pin against future intent-set expansions
  intent_derivation: explicit           # explicit | from_case_type | from_workspace
```

**Intent vocabulary (reference implementation, v1):** `Buy`, `Consign`,
`Comply`, `SanctionScreen`, `Advise`, `Cover`, `Discover`. This is the
producer-defined vocabulary used by the reference implementation; other
producers MAY define their own values under `extensions.intent` per the
informative-catalog disclaimer at the top of this document. Future
reference-vocabulary expansions bump `intent_schema_version`; older
clients detect-and-degrade.

**Relationship to `case_type`.** `case_type` (compliance | academic |
canonical | journalism) is a stylistic / verdict-shape tag retained
unchanged. `intent` is a sibling axis, not a replacement. A pack MAY carry
both; defaults derive `intent` from `case_type` when absent.

### 2.5 `extensions.playbook` — runtime trace

**Owner:** kp-forge enrichment loop, in concert with the reference
intelligence pipeline.
**Status:** experimental (introduced 2026-04-28).

The structured trace of a playbook execution. Written incrementally as
steps complete; the final manifest carries the full record. Consumed by
the dossier renderer and the audit view.

```yaml
extensions:
  playbook:
    id: sanction-screen.person          # playbook identifier
    intent_schema_version: "1"          # mirrors WorkspaceState.intentSchemaVersion
    started_at: "2026-04-28T15:00:00Z"
    completed_at: "2026-04-28T15:08:23Z"
    results:                            # one entry per executed step
      step_001_sanctions:
        status: complete                # pending | running | complete | skipped | failed
        confidence: high
        entities: [ent_p_8a3f2c]        # entity IDs targeted by this step
        provider: opensanctions         # primary provider (canonical for findings)
        provider_attempts:              # full provider sequence trail
          - { provider: opensanctions, status: success, latency_ms: 412 }
          - { provider: ofsi, status: success, latency_ms: 1180 }
        findings_by_entity:             # per-entity verdict
          ent_p_8a3f2c:
            finding: present
            evidence_ids: [E007, E008]
        new_entities: []                # entities surfaced by this step (see §2.2)
        new_relations: []               # relations surfaced (see §2.3)
        gaps: []                        # per Gap shape — {field, why, suggestedAction}
```

**Streaming.** Producers MAY write `results[step_id]` entries
incrementally during enrichment; consumers MUST treat partial blocks as
in-flight rather than malformed.

### 2.6 `extensions.workspace` — Decision Workspace metadata

**Owner:** kp-forge workspace materialization module.
**Status:** experimental (introduced 2026-04-28).

Per-pack workspace bookkeeping. The wedge ships with single-pack
workspaces persisted as a `workspace.yaml` sidecar in the `.kpack/`
directory; a small pointer block in the manifest records which workspace
this pack belongs to.

```yaml
extensions:
  workspace:
    id: ws_lemos_2026_04_28              # workspace ID, opaque
    constructor_enabled: true            # kill switch — when false, Bernard Live
                                         # constructor tool is not registered
    role: foreground                     # foreground | evidence (multi-pack only)
```

**Compatibility.** Pre-reframe packs without the block continue to enrich
through the existing pipeline.

### 2.7 `extensions.research` — research metadata

**Owner:** kp-forge research-metadata module.
**Status:** active (precedent for the producer-defined pattern; emitted by
~16 packs in the reference implementation as of v0.7.7).

Free-text anchor subject and surrounding research metadata. Predates the
typed entity graph; coexists with it. New work targets `extensions.entities`
as the structured channel; `extensions.research.anchor_subject` remains
valid for legacy and lightweight cases.

### 2.8 `extensions.translations` — evidentiary multilingual transcripts

**Owner:** the reference handwritten-inventory intake pipeline + the
kp-packs relay's intake module. Consumed by kp-viewer and downstream
relays.
**Status:** active (introduced 2026-05-09 with the inaugural
field-collected corpus).

When a claim's canonical text is English (per
[MULTILINGUAL.md §2 P1](MULTILINGUAL.md)) but the underlying evidence is in
another language — handwritten Russian/Ukrainian witness statements,
foreign-language press, recorded interviews — the `translations` block
carries original-language transcripts as audit trail without making them
co-canonical. The English claim remains the single normative assertion;
the transcripts are evidence-shaped, not claim-shaped.

```yaml
extensions:
  translations:
    ru:
      transcript: |
        Оригинальный текст показаний свидетеля...
      transcript_format: verbatim          # verbatim | summary | excerpt
      source_evidence_id: E007             # which evidence this transcript backs
      transcribed_by: field-team-mariupol
      transcribed_at: "2026-04-22T14:30:00Z"
    uk:
      transcript: |
        Оригінальний текст свідчення...
      transcript_format: verbatim
      source_evidence_id: E007
```

**Schema.** `translations: { [locale: string]: { transcript: string,
transcript_format?: "verbatim" | "summary" | "excerpt", source_evidence_id?:
string, transcribed_by?: string, transcribed_at?: string } }`. Locale keys
are BCP-47 strings (per [MULTILINGUAL.md](MULTILINGUAL.md)).

**Producer expectations.** Producers SHOULD include `source_evidence_id`
whenever the transcript is excerpted from a larger evidence record, so
audit-trail reconstruction can map transcript → evidence → claim. When
multiple transcripts back the same evidence record, locales sit side-by-side
under the same `translations` block keyed by BCP-47 locale.

**Cross-reference.** See [MULTILINGUAL.md §12](MULTILINGUAL.md) for the
normative exception this block carries — it is the sanctioned location for
non-canonical-language text whose canonicalization-to-English would lose
evidentiary fidelity.

**Compatibility.** Consumers that do not understand the block MUST ignore
it. The English claim remains valid and complete on its own; the
translations block adds audit trail without creating a parallel canonical
surface.

---

## 3. Cross-cutting concerns

### 3.1 Canonical entity IDs

Entity IDs in `extensions.entities[].id` follow the form:

```text
ent_<type>_<6-hex>            # ent_p_8a3f2c, ent_c_4b1d9e, ent_a_7e2f01, ent_v_3ab9cc
```

Where `<type>` is `p` (person), `c` (company), `a` (asset), `v` (event —
`v` chosen to avoid collision with evidence's `e` prefix).

IDs are deterministic SHA-256 of `(type, canonical, first_external_id_if_any)`,
truncated to six hex characters. Re-runs of the extractor on the same source
produce the same ID.

Cross-pack stability is provided by the relay's `entity_index` table, which
maps `(canonical, external_ids)` triples to `[pack_id, ent_id]` pairs.
Two packs with the same `external_ids.opensanctions: Q123456` resolve to
the same entity even when the per-pack IDs differ.

### 3.2 External identifier vocabulary

`extensions.entities[].external_ids` is an open-keyed map. Producers fill
what they have; consumers MUST tolerate unknown keys. The recommended
vocabulary:

| Key | Source | Format |
|---|---|---|
| `opensanctions` | OpenSanctions API | string ("Q123456") |
| `companies_house` | UK Companies House | 8-digit string |
| `ofsi` | UK OFSI list | string ("RUS0770") |
| `ofac_sdn` | OFAC SDN list | integer |
| `eu_consolidated` | EU consolidated list | string |
| `un_consolidated` | UN consolidated list | string |
| `orcid` | ORCID API | "0000-0001-2345-6789" |
| `opencorporates_<jurisdiction>` | OpenCorporates | path-style ID |
| `sec_cik` | SEC EDGAR | 10-digit CIK |
| `wikidata` | Wikidata | "Q\d+" |
| `courtlistener_party` | CourtListener | integer |
| `lei` | GLEIF | 20-character LEI |

Producers MUST NOT emit malformed external IDs. The reference
implementation's external-ID parsers validate format strictly; values that
fail validation are dropped from the pack and recorded as a Gap in the
playbook trace.

### 3.3 Per-claim entity references

Claims MAY annotate which entities they describe via the existing
`extensions` lane on `KPClaim` ([CORE.md §4](CORE.md#claims)):

```yaml
- id: C014
  text: "Mordashov became Severstal CEO in 1996."
  extensions:
    entity_refs:                          # which entities this claim is about
      - id: ent_p_8a3f2c
        role: subject                     # subject | object | other
      - id: ent_c_severstal
        role: object
    relation_refs: [rel_001]              # relations established by this claim
```

This complements the H1 entity annotation in claims.md
([CORE.md AR-09](CORE.md)). The annotation declares the pack's *one*
foreground entity for legacy compatibility; per-claim `entity_refs[]` link
specific claims to the typed entities under `extensions.entities`.

---

## 4. Migration

### 4.1 From `entities.md` to `extensions.entities`

The `entities.md` file ([SPEC.md §7](SPEC.md)) is **deprecated** as of
2026-04-28. It saw use in five packs out of ~770 and never landed as a
practical primitive — its free-text `Relationships` block was never
machine-consumed.

New packs MUST NOT emit `entities.md`. Producers MUST write
`extensions.entities` and `extensions.relations` instead. A one-shot
migration script (`scripts/migrate-entities-md-to-extensions.mjs`) walks
the legacy packs and rewrites their content into the new shape.

### 4.2 From free-text `anchor_subject` to typed entities

`extensions.research.anchor_subject` (a free-text string) coexists with
`extensions.entities` for the wedge. New work targets the typed channel;
the free-text field is retained for legacy packs and for lightweight cases
that do not warrant the full entity record.

---

## 5. Status and stability

Every extension in this document is **producer-defined** — its shape and
semantics are governed by the producing subsystem, not by KP:1. Extensions
graduate to core fields only after a future KP revision standardizes them.

Consumers MUST ignore extension content they do not understand. Extension
content MUST NOT redefine the semantics of core KP fields or relax core
validation rules.

The catalogue in this document is informative: producers register their
extensions here so consumers can converge on shared shapes, but the
authoritative shape lives in producer code (cited at the top of each
section).
