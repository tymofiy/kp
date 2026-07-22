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
active use across the reference implementation. It is informative — KP:1 does
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

**Owner:** reference producer-side enrichment implementation.
**Status:** active.

The illustrative extension shipped with v0.7.4 ([SPEC.md §3.2](SPEC.md)). A
short headline and verdict produced at end-of-enrichment, surfaced by analyst
tooling as a one-line summary above the dossier. See SPEC.md for the
canonical example.

### 2.2 `extensions.entities` — typed entity graph

**Owner:** reference entity-extraction implementation.
**Status:** experimental (introduced 2026-04-28).

Promotes the in-memory entity graph to first-class manifest metadata.
Consumed by Decision Workspace materialization and the cross-pack
`entity_index` in the reference relay.

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
([CORE.md AR-09](CORE.md#appendix-b-ambiguity-resolutions)) when present.

### 2.3 `extensions.relations` — typed edges

**Owner:** reference entity-extraction implementation.
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

**Owner:** reference producer-side intent inference implementation.
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

**Owner:** reference producer-side enrichment loop, in concert with the
reference intelligence pipeline.
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

**Owner:** reference workspace materialization implementation.
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

**Owner:** reference research-metadata implementation.
**Status:** active (precedent for the producer-defined pattern; emitted by
~16 packs in the reference implementation as of v0.7.7).

Free-text anchor subject and surrounding research metadata. Predates the
typed entity graph; coexists with it. New work targets `extensions.entities`
as the structured channel; `extensions.research.anchor_subject` remains
valid for legacy and lightweight cases.

### 2.8 `extensions.translations` — evidentiary multilingual transcripts

**Owner:** the reference handwritten-inventory intake pipeline + the
reference relay's intake module. Consumed by the reference macOS viewer and
downstream relays.
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

### 2.9 `extensions.collection` — pack-bundle membership

**Owner:** reference intake implementation + reference macOS viewer library
organization.
**Status:** active (introduced 2026-05-24).

Declares that a pack belongs to a user-facing **collection** — a bundle of
related packs sharing a real-world origin (a private art collection, a watch
collection, a wine cellar, a portfolio of holdings). Collections are an
**orthogonal organizational axis** alongside `tier:` (claim-clustering hubs,
≤20 sub_packs) and the viewer-derived `category` (first segment of `domain:`).
A collection MAY span multiple categories — e.g., a private art collection
may contain both antiquities and fine art under the `art/*` root.

```yaml
extensions:
  collection:
    name: "Example Antiquities Collection"  # required — display name, grouping key
    id: example-antiquities-collection      # optional — stable identifier (see compat)
    role: member                        # optional — hub | member | standalone (default: member)
    item_kind: object                   # optional — see "Inventory taxonomy" below
    item_role: artist                   # optional — finer classification within item_kind
```

**Field semantics.**

- `name` — required. The display name shown in the viewer's scope chip and
  used today as the grouping key. Two packs with the same `name` are treated
  as belonging to the same collection.
- `id` — optional. A stable, opaque identifier (e.g., kebab-case slug).
  Reserved for future use when collections become a top-level spec field with
  rename-safe references. Today, consumers MAY ignore `id` and group by `name`.
- `role` — optional enum (`hub` | `member` | `standalone`), defaults to
  `member`. `hub` marks a spine pack that describes the collection itself
  (typically `domain: art/private-collection` or similar) — viewer renders it
  as the collection cover when present. `member` is a regular pack in the
  collection. `standalone` is reserved for packs that historically carried the
  block but stand alone in the viewer; treat as "no collection" for grouping.
- `item_kind` — optional controlled-vocabulary enum identifying what kind of
  thing this pack represents *within the collection's inventory*. Drives the
  viewer's inventory-dashboard layout when the user scopes to a collection.
  Generalizable across art, watches, wine, real estate, and auction inventory.
  See the table below.
- `item_role` — optional free-form string narrowing the `item_kind`. e.g. a
  pack with `item_kind: person` might carry `item_role: artist | scholar |
  dealer | family | owner | auctioneer`; a `place` might carry `item_role:
  room | gallery | auction_house | residence | region`; an `event` might carry
  `item_role: exhibition | auction | sale | acquisition | appraisal`. Consumers
  MAY surface these as filter pills within the kind's section. Unknown values
  are ignored gracefully.

### Inventory taxonomy (`item_kind`)

| Value | Meaning | Private-collection example | Auction-house analogue |
|---|---|---|---|
| `spine` | Collection's overview/hub pack (typically one per collection) | `example-antiquities-collection` | The auction-house catalog pack |
| `subcollection` | Category hub that groups objects (a sub-bucket within the collection) | `category-antiquities` | Department (Impressionist, Contemporary) |
| `object` | Individual inventory item | `category-antiquities-001-example-jade-figure` | Lot |
| `person` | Any human entity | Artists, scholars, family members, owners | Consigners, buyers, specialists |
| `place` | Physical location or organization-with-location | Rooms, residences, galleries, auction houses | Sale rooms, regions |
| `period` | Temporal classification (era, dynasty, vintage) | Tang Dynasty, Hellenistic period | Era, vintage year |
| `event` | Exhibition, auction, sale, acquisition, appraisal | 1985 university loan exhibition | Auctions, sales |
| `document` | Records (appraisals, catalogs, certificates, invoices) | 2022 specialist appraisal | Sale catalogs, condition reports |
| `narrative` | Story content (voice briefings, monographs, voice scripts) | `narration-collection-overview` | Sale-room essays |

**Item kinds are display-axes, not access-control or routing axes.** A pack's
`item_kind` controls how it appears in the collection inventory dashboard
(which section, which filter pill). It does not affect search, embeddings,
sealing, or any other system. Producers MAY omit `item_kind` entirely; the
viewer falls back to name-prefix inference for legacy packs and otherwise
shows the pack as a generic "other" entry.

**One spine per collection (convention, not enforced).** A collection should
have at most one pack with `item_kind: spine` — the cover/overview pack. If
multiple are present, the viewer picks one deterministically (typically the
oldest-sealed or alphabetically first). This is a convention, not a hard
constraint; the parser does not error.

**Distinction from `tier: hub`.** `tier: hub` (spec) is for small claim
clusters (≤20 sub_packs) that declare their children explicitly via
`sub_packs:`. `extensions.collection` is for large user-facing bundles
(hundreds of items possible) where members share a `name` rather than being
pre-declared. Both MAY coexist on the same pack; they describe different
concerns.

**Distinction from `category`.** `category` is derived at scan time from the
first segment of `domain:` and is not authored. A collection MAY span
multiple categories. Producers MUST NOT use `extensions.collection` to
override or canonicalize category derivation.

**Compatibility.** Consumers that do not understand the block MUST ignore
it. Producers MAY omit the block entirely; packs without it appear in the
viewer's "Uncollected" section (or the category section, depending on
grouping mode). The reference macOS viewer treats `name` as
authoritative for grouping today; if/when `collection:` is promoted to a
top-level spec field with `id` semantics, this catalogue entry will be
updated and an alias-and-migrate path documented.

**Authoring expectations.** When an intake pipeline detects sibling structure
(shared origin, similar domains, shared creator/location/period metadata) it
SHOULD propose a collection name to the user rather than emit individual
standalone packs. The user accepts, edits, or rejects the proposal; on
acceptance, every pack in the batch receives the same `name` and `role:
member` (or `role: hub` for the spine pack if one exists).

### 2.10 `extensions.audience` — producer-side named recipients

**Owner:** authored manifests + the reference macOS viewer's audience badges
and recipient gates.
**Status:** active (canonical location as of 2026-06-14; migrated from the legacy
top-level `audience:` key).

A flat list of opaque producer-defined identifiers naming **who a pack is authored
for** — the producer-side answer to "who is this for."

```yaml
extensions:
  audience: [alice, bob]
```

**Distinct from the two existing audience mechanisms.** KP:1 already expresses
audience two other ways; this field is neither:

- **Views** ([CORE.md §11](CORE.md)) — each view is an *aimed surface*
  (register/voice for a reader). `extensions.audience` names *people*, not surfaces.
- **PLAYBACK `AudienceProfile`** ([PLAYBACK.md §3](PLAYBACK.md)) — the *session-time*
  listener context (familiarity, purpose, domain_lens, register) chosen at playback.
  `extensions.audience` is *authoring-time* recipient identity — an orthogonal axis
  that deliberately keeps a separate vocabulary.

**Shape.** A flat array of string identifiers, mirroring `PackManifest.audience:
[String]` in the reference runtime. A richer per-recipient form (`[{id, role, view}]`
distinguishing recipient vs. operator) was considered and deferred: the surprise gate
that would consume `role` is currently retired (see §2.11), so the enrichment is not
yet load-bearing.

**Compatibility.** Consumers that do not understand the block MUST ignore it. The
reference loader accepts the field in either location — `extensions.audience`
(canonical) or the legacy top-level `audience:` key — so packs may be migrated one at
a time without a flag day.
New packs SHOULD write `extensions.audience`; the top-level `audience:` key is
**deprecated** — it violated the closed manifest root
([CORE.md §3 "Manifest Extensions"](CORE.md#manifest-extensions)).

### 2.11 `extensions.sharing` — gift-gating / do-not-share metadata

**Owner:** the reference macOS viewer's surprise-pack gate and library
filtering.
**Status:** active, gate-dormant (canonical location as of 2026-06-14; migrated from
the legacy `lifecycle.surprise` / `lifecycle.do_not_share` keys).

Marks a pack as a **sealed gift** that must not surface in demos, pack browsers,
screenshots, or shared contexts until a human has presented it to its recipient.

```yaml
extensions:
  sharing:
    surprise: true
    do_not_share: >
      This pack is a surprise gift — treat it as a sealed envelope addressed to
      someone else.
```

**Gate status.** Per the reference implementation's 2026-05-20 "just on, singular
solution" directive, `SurprisePackGate.isUnlocked` returns `true` unconditionally —
the gate is **retired** and these fields are dormant metadata, preserved so a
re-enable stays a one-line revert. Relocating them changes no live behavior.

**Why not `lifecycle`.** These were authored under `lifecycle.{surprise,do_not_share}`,
but `lifecycle` is a *closed* core object (CORE §3 / the schema) reserved for
archive-management fields. Gift-gating is implementation-specific viewer behavior, so
it belongs under `extensions` per the closed-root rule.

**Compatibility.** Consumers that do not understand the block MUST ignore it. The
reference loader accepts these fields in either location — `extensions.sharing.*`
(canonical) or the legacy `lifecycle.surprise` / `lifecycle.do_not_share` keys — so
packs may be migrated one at a time. New packs SHOULD write `extensions.sharing`; the
`lifecycle.*` gift-gate keys are **deprecated**.

### 2.12 `extensions.case` — situation-anchored case composition

**Owner:** producer-side case materialization implementation (writer) + consuming library
(case cards, roster surfaces); member resolution by the consuming library or
relay at serve time.
**Status:** experimental (introduced 2026-07-19).

A **case pack** is an ordinary pack whose single subject is a *situation* —
a deal under review, a client-development campaign, a matter to be decided —
rather than a person, company, or asset. The `case` block declares the
situation's flavor (`kind`) and the case's **member references**: pinned
pointers to the standalone packs the case draws on.

A case is not a new artifact class. It is a pack, and it inherits sealing,
provenance, views, sharing, and supersession unchanged. The one-subject rule
is also unchanged ([CORE.md AR-09](CORE.md#appendix-b-ambiguity-resolutions)):
a case pack has exactly one foreground entity — the situation itself,
conventionally an event entity (`ent_v_`, §3.1; usage conventions in §3.5).
People, companies, and assets involved in the situation are *participants*,
declared under `extensions.entities` (§2.2) with roles and per-claim
`entity_refs` (§3.3); they are never additional anchors. If a design appears
to need a second anchor, model the situation that is actually the subject
and anchor there.

```yaml
extensions:
  case:
    kind: deal                          # deal | campaign — reference vocabulary v1
    members:
      - pack_id: "0b3c1f9a-4d7e-4a1c-9f2b-3e4a5b6c7d8e"
        revision: "2026.07.02"          # the member's PACK.yaml `version`, pinned
        role: subject                   # subject | evidence | inventory | prospect
        entity: ent_p_8a3f2c            # optional — participant this member documents
      - pack_id: "3f9e2d61-8c4b-4f2e-b1a7-5d6e7f8a9b0c"
        revision: "2026.06.28"
        role: subject
        entity: ent_a_7e2f01
      - pack_id: "9d8c7b6a-5e4f-4d3c-a2b1-0f9e8d7c6b5a"
        revision: "2026.05.30"
        role: evidence
```

**Case kinds (reference vocabulary v1).**

- `deal` — a small-cast situation: two or three central participants plus a
  bridge of relationship questions between them. The canonical shape is a
  consignment review — consignor, work, and the institution's decision.
  `examples/auction-house-consignment-review.kpack` models the scenario
  (the example predates this block and does not carry it).
- `campaign` — a cohort situation: many prospective participants, an
  inventory of assets, and a purpose (an outreach program around an
  exhibition, fair, or season). Most of a campaign's cohort enters as
  in-pack **stubs**, not members — see "Members vs stubs" below.

The kind vocabulary is closed in the same spirit as the relation vocabulary
(§3.4): new kinds are deliberate registrations in this catalogue, not ad hoc
values. Consumers encountering an unknown `kind` SHOULD degrade to generic
case handling (render members; skip kind-specific surfaces).

**Member fields.**

- `pack_id` — required. The member's stable identity across versions — the
  `pack_id` documented in [ARCHIVE.md](ARCHIVE.md) §4. This is reference
  *identity*, deliberately not content.
- `revision` — required. The member's `PACK.yaml` `version` string as
  sealed (the `pack_version` receipt in the member's `signatures.yaml`).
  References are **pinned, always**: a case records what was known when the
  decision was made — the audit question is "what did you know when you
  advised this?", and a floating reference cannot answer it. Producers MUST
  NOT emit revision-less members. Freshness is a serving/UI concern — see
  the staleness signal below.
- `role` — required. One of the closed v1 vocabulary below. Consumers that
  do not recognize a role MUST still treat the entry as a well-formed
  member (resolvable, renderable) without role-specific behavior.
- `entity` — optional. The `ent_*` ID (§3.1) of the participant in this
  case's `extensions.entities` that the member pack documents. This is what
  ties a roster row to its dossier after promotion.

| Role | Meaning | Typical kind |
|---|---|---|
| `subject` | Dossier for a central participant of the situation | deal |
| `evidence` | Supporting material the case's findings draw on | any |
| `inventory` | Member of the asset set the situation offers or matches against | campaign |
| `prospect` | Dossier for a cohort member under consideration | campaign |

**Reference pinning and verification (no member hashes — by design).** A
member reference pins *identity* (`pack_id` + `revision`) and deliberately
does **not** carry the member's `pack_hash` or any content digest. This
dissolves the composite signing-chain problem instead of solving it:

- *No hash cycles.* The case's seal ([ARCHIVE.md](ARCHIVE.md) §3–§4) is
  computed over the case's own files only. Since member entries embed no
  member digests, sealing order between packs never matters, and packs that
  reference each other cannot deadlock each other's seals.
- *No parent-deed / child-deed entanglement.* Re-sealing a member (a new
  dossier revision) never invalidates the case's seal, and a case's seal
  asserts nothing about member content. No custody chain flows through a
  case into its members.
- *A case verifies standalone.* "Verified" for a case archive means: its own
  seal is valid and its member references are well-formed. Verifiers MUST
  NOT require member archives to be present or resolvable to verify a case.
- *Member presence is a serving question, never a validity question.*
  Whether a pinned member is **present**, **absent**, or **superseded** (a
  newer revision with the same `pack_id` exists — [ARCHIVE.md](ARCHIVE.md)
  §5, [LIFECYCLE.md](LIFECYCLE.md) §6) is answered by the consuming library
  or relay at serve time, and MUST be reported *alongside* verification
  results, never conflated with them.
- *Member authenticity is the member's own.* Because the reference is a name
  and version, not a checksum, content authenticity of a resolved member is
  established by the member's own seal at resolve time — never by the case.

**Staleness signal.** Supersession already gives consumers "this dossier has
moved on" for free: a member is *superseded* exactly when the serving side
knows a later revision in the same `pack_id` family. Surfaces SHOULD offer
re-pinning as a deliberate act that produces a new case revision; they MUST
NOT silently re-resolve a pinned reference to a newer member revision.

**Members vs stubs; promotion.** Members are references to *real packs*. A
campaign's cohort largely is not that: bulk intake produces **stubs** —
participant entities and their claims *inside* the case pack (roster rows),
with honest resolution-fidelity downgrades, not dozens of thin packs.
Promotion is the deliberate act that turns a stub into a dossier: a precise
identity resolution, a standalone pack created through the normal research
flow (seeded from the stub's external IDs and the case's evidence), and a
**new case revision** whose member list gains a pinned reference (`role:
prospect` or `subject`, with `entity` pointing at the participant). Claims
never migrate between packs: the stub's claims are superseded in the case
revision per the ordinary supersession rules, and the new dossier's claims
carry their own provenance from birth. Fidelity metadata (stub vs promoted)
SHOULD travel with any retrieval or roster surface, so bulk-resolved and
precise-resolved knowledge are never presented as equivalent.

**Distinct from the neighboring mechanisms.** Four existing features solve
adjacent problems; `case` replaces none of them:

- [COMPOSITION.md](COMPOSITION.md) `composition.yaml` — a *loading lens*:
  agenda-shaped references **by pack name**, un-pinned, chosen for a session
  (`pre_load` / `on_demand`). A case pins identity + revision for the
  decision record. A case pack MAY additionally carry `composition.yaml`
  (e.g., to brief a meeting about the case).
- `extensions.collection` (§2.9) — organizational bundling by shared
  `name`; no pinning, no per-member roles, no decision semantics.
- `tier: hub` + `sub_packs` — small claim-clustering hubs with pre-declared
  children.
- `extensions.workspace` `role: foreground | evidence` (§2.6) — per-pack
  workspace bookkeeping recorded *on the member side*. Case membership is
  recorded *on the case side*; only the case's own list is authoritative
  for the case.

**Compatibility.** Consumers that do not understand the block MUST ignore
it; the pack remains an ordinary pack whose claims and views stand alone.
Consumers that understand `case` but cannot resolve members (offline, a
single shared archive, a partial library) MUST NOT report the pack as
invalid or incomplete — member resolution is a serving feature layered on
top of an already-complete pack. Producers MAY emit `members: []` (a case
that so far contains only stubs and in-case findings).

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

Claims MAY annotate which entities they describe via the `extensions`
lane on the structured claim record (`KPClaim`,
[STORAGE.md §3.2](STORAGE.md#32-json-serialization-operational)):

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

### 3.4 Relation vocabulary conventions (closed sets, extended per playbook)

`extensions.relations[].type` (§2.3) draws from the relation-type vocabulary
defined in [DEFINITIONS.md](DEFINITIONS.md) §3. The growth convention: the
vocabulary is a **closed set, extended per playbook** — each playbook family
declares the relation types its steps may emit, and additions are deliberate
registrations (a definition-pack change plus a row here), never ad hoc
strings invented at emission time. Consumers MUST ignore relation instances
whose type they do not recognize (§2.3 compatibility), so registration cost
stays low while the graph stays queryable.

The case playbooks (§2.12) introduce the initial case vocabulary:

| id | From → to | Semantics |
|---|---|---|
| `consigns` | person → asset | The person offers the asset for consignment (the deal bridge). Temporal (`since`/`until`); inverse `consigned_by`. |
| `fits_budget` | person → asset | The participant's documented budget range accommodates the asset's expected price. A matching *finding* — verdict-less, evidence-cited. |
| `interested_in` | person → asset \| person | Documented interest in a work, a maker, or a category. A matching *finding* — verdict-less, evidence-cited. |
| `possibly_same` | entity ↔ entity (same type) | Uncertain identity between two entities. A *question*, never an assertion. Symmetric; self-inverse. |

**Findings-shaped relations.** `fits_budget` and `interested_in` are written
by the matching steps of a campaign playbook (§2.5 `findings_by_entity` is
the per-step trace shape; the durable edges land here). They MUST carry
`attributes.evidence_ids`, and SHOULD cite both endpoints' evidence — the
participant-side evidence (budget, stated interest) and the asset-side
evidence (estimate, attribution). They are findings, not verdicts: the edge
encodes no recommendation, and numeric confidence stays machine-internal
per §2.3.

**`possibly_same` discipline.** Cross-pack identity merges happen only on
*established* identity — matching `external_ids` (§3.2) or a resolved
canonical (§3.1). When identity is merely suspected, producers MUST keep
the entities separate and connect them with `possibly_same`. Consumers MUST
NOT treat `possibly_same` as established identity (no index merging, no
claim pooling across the edge); surfaces SHOULD present it as an open
question. A silent merge is the graph-level wrong-subject dossier — the
error class this discipline exists to prevent.

### 3.5 Event entities (`ent_v_`) — usage conventions

The `v` prefix has been reserved since this catalogue was introduced
(§3.1); these conventions make event entities operational. An **event** is
an occurrence that relates persons, companies, and assets over time: an
exhibition, an auction, a sale, an acquisition, an appraisal, a loan, a
restitution — or a client-development campaign anchored on one (§2.12).

**Projection fields.** Consumers that compute typed per-entity projections
SHOULD project three well-known fields for events:

| Field | Shape | Projected from |
|---|---|---|
| `date` | ISO-8601 date or `{start, end}` range | Claims about when the event occurs, via `entity_refs` (§3.3) |
| `location` | string (venue / city) | Claims about where, via `entity_refs` |
| `participants` | list of `ent_*` refs with roles | Union of (a) entities co-referenced with the event on a claim (§3.3) and (b) entities linked to the event by a relation edge (§2.3) |

Projections are **computed from claims, never authored**: each projected
field carries the provenance of the claims it was computed from, disagreeing
claims surface as disputes rather than silent overwrites, and a projection
can always be rebuilt from the pack. Records are cache; claims are truth.

**Events as case anchors.** A campaign case pack (§2.12) conventionally
anchors on an event entity: the foreground entity (`role_in_pack: subject`)
is the `ent_v_` for the campaign or the occasion it targets, and cohort
participants relate to it.

**Why events matter to provenance.** A provenance history is a chain of
events — sale, exhibition, transfer, restitution — each relating persons to
a work over time. Modeling those occurrences as first-class `ent_v_`
entities with `date` projections makes provenance graph-traversable
(artwork → events → persons, with dates) instead of prose-bound; questions
like "is there a gap in this ownership window?" become traversals over
event sequences.

**Distinct from `item_kind: event`.** The collection taxonomy's `event`
(§2.9) is a *display axis* — which dashboard section a pack renders in. An
`ent_v_` entity is *graph identity* — a node that claims and relations
attach to. A pack about an exhibition may well carry both; they answer
different questions.

---

## 4. Migration

### 4.1 From `entities.md` to `extensions.entities`

The `entities.md` file ([SPEC.md §7](SPEC.md)) is **deprecated** as of
v0.7.7 (2026-04-28). It saw use in five packs out of ~770 and never landed as a
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
