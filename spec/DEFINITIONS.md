<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Definition & Policy Kinds — Knowledge Pack Companion Spec

> **Parent:** SPEC.md, §5
> **Date:** 2026-03-29
> **Status:** Draft
> **Editor:** Timothy Kompanchenko
> **Origin:** Cross-cutting architecture decision — knowledge packs as master knowledge

---

## 1. Purpose

This document specifies the `definition` and `policy` document kinds introduced in SPEC.md §5. These kinds represent **deterministic domain knowledge** — structural facts about how a domain is organized (definitions) and behavioral rules for operating within that domain (policies). Unlike claims, which are probabilistic and evidence-backed, definitions and policies are authoritative declarations that constrain the vocabulary and behavior of the knowledge system.

---

## 2. Relationship to Claims

### The Two-Layer Model

Knowledge Packs operate on two layers:

| Layer | Kind(s) | Epistemology | Purpose |
|-------|---------|-------------|---------|
| **Ontology** | `definition`, `policy` | Deterministic — these ARE the domain | Define what exists and how it works |
| **Knowledge** | `claim` | Probabilistic — beliefs about entities | Assert what's true about specific entities |

**The ontology layer constrains the knowledge layer.** A claim references entity types, attributes, and relations that are defined in the ontology. A research perspective is routed by policies that determine which perspectives apply to which entity types.

### Constraint Is Informational

An LLM reading a claims pack can reason about claims without definitions loaded. The claims are self-contained. But with definitions loaded, the LLM can:

1. **Validate** — Is `painting` a valid entity type? Is `medium` a valid attribute for art?
2. **Complete** — What attributes should a complete art entity have? What perspectives are missing?
3. **Navigate** — What other entity types exist in this domain? What relations connect them?
4. **Detect anomalies** — A claim about a `painting`'s `horsepower` doesn't match the taxonomy.

---

## 3. Definition Schema

### File Location

Definitions live in the `definitions/` subdirectory of a `.kpack/` directory:

```text
core-taxonomy.kpack/
├── PACK.yaml                    # kind: definition
└── definitions/
    ├── entity-types.yaml        # Entity type catalog
    ├── attributes.yaml          # Attribute vocabulary
    └── relation-types.yaml      # Relation type catalog
```

### Document Header (Required)

Every definition YAML file begins with these fields:

```yaml
kind: definition
authority: platform-team         # Who established this
version: "2026.1"                # CalVer or SemVer
status: active                   # active | deprecated | draft
effective_from: "2026-03-29"     # Optional: when this takes effect
effective_to: null               # Optional: when this expires (null = open-ended)
superseded_by: null              # Optional: replacement path/URI if deprecated
rationale: null                  # Optional: why this definition exists
```

### Entity Type Schema

```yaml
kind: definition
authority: platform-team
version: "2026.1"
status: active
effective_from: "2026-03-29"
rationale: >
  Core entity types for alternative asset verticals.
  Covers the primary collectible and luxury categories.

entity_types:
  - id: art                              # Unique identifier (kebab_case)
    name: Artwork                        # Human-readable name
    description: >                       # What this type covers
      Fine art — paintings, sculptures, prints,
      drawings, photographs, and mixed media works
    subtypes:                            # Enumerated subtypes
      - painting
      - sculpture
      - print
      - drawing
      - photograph
      - mixed_media
      - installation
    key_attributes:                      # Primary attributes for this type
      - medium
      - dimensions
      - period
      - movement
      - technique
      - condition
      - provenance_length
    relations:                           # Common relation types for this entity
      - created_by                       # artist → artwork
      - exhibited_at                     # artwork → venue
      - part_of_series                   # artwork → series
    # NOTE: Perspective coverage (which perspectives apply to this type)
    # belongs in a POLICY pack, not in the taxonomy definition.
    # See §4 Policy Schema for perspective-coverage rules.
```

### Attribute Schema

```yaml
kind: definition
authority: platform-team
version: "2026.1"
status: active

attributes:
  - id: medium
    name: Medium
    description: "Materials and technique used to create the work"
    applies_to: [art]                    # Which entity types use this
    value_type: string                   # string | number | enum | date | boolean
    indexed: true                        # Should this be searchable?
    required: false                      # Is this attribute mandatory?
    sensitive: false                     # Contains PII or confidential data?
    examples:
      - "Oil on canvas"
      - "Bronze"
      - "Lithograph on paper"

  - id: movement_type
    name: Movement Type
    description: "Watch movement mechanism"
    applies_to: [watch]
    value_type: enum
    enum_values: [mechanical_manual, mechanical_automatic, quartz, spring_drive, hybrid]
    indexed: true
    required: true
    sensitive: false
```

### Relation Type Schema

```yaml
kind: definition
authority: platform-team
version: "2026.1"
status: active

relation_types:
  - id: created_by
    name: Created By
    description: "Links a work to its creator/artist/maker"
    source_types: [art, watch, jewelry, instrument]
    target_types: [person, brand, workshop]
    cardinality: many_to_one             # many_to_one | one_to_many | many_to_many
    inverse: creator_of                  # The reverse relation ID

  - id: provenance_chain
    name: Provenance Chain
    description: "Ownership history — ordered sequence of possession events"
    source_types: [art, watch, jewelry, wine, numismatic]
    target_types: [person, institution, auction_house]
    cardinality: many_to_many
    ordered: true                        # Sequence matters
    temporal: true                       # Has date ranges
    edge_attributes:                     # Properties on the relation itself
      - id: start_date
        type: date
        description: "When this ownership period began"
      - id: end_date
        type: date
        description: "When this ownership period ended (null = current)"
      - id: acquisition_method
        type: enum
        enum_values: [purchase, inheritance, gift, auction, commission]
        description: "How the entity was acquired"
      - id: sale_price
        type: number
        description: "Transaction price if known"
        sensitive: true
```

### Relation Edge Attributes

Relations with `temporal: true` or complex semantics often carry their own properties. The `edge_attributes` field defines the data model for properties on the relation itself (not on the source or target entities).

```yaml
edge_attributes:
  - id: start_date               # Attribute identifier
    type: date                   # date | number | string | enum | boolean
    description: "When this edge became active"
  - id: sale_price
    type: number
    description: "Transaction value"
    sensitive: true              # Contains financially sensitive data
```

Edge attributes are particularly important for:
- **Temporal relations** — `start_date`, `end_date` for ownership periods
- **Transactional relations** — `price`, `currency`, `terms` for sales
- **Qualified relations** — `role`, `capacity`, `authority` for participation

**Graph modeling note:** A `provenance_chain` with edge attributes is equivalent to an event-based model where each ownership transition is a discrete event. The relation-with-attributes model is more compact for simple chains; for complex provenance with multiple parties per event, consider modeling `OwnershipEvent` as a separate entity type with dedicated relations. The right choice depends on domain complexity — start with edge attributes, promote to event entities when the edges become too heavy.

### Consumer Pattern — `extensions.relations` in PACK.yaml

The `relation_types` schema above defines the *vocabulary*. Producers in
the Nova ecosystem write *instances* of relations under
[`extensions.relations`](EXTENSIONS.md#23-extensionsrelations--typed-edges)
in PACK.yaml, where each instance references entities declared under
[`extensions.entities`](EXTENSIONS.md#22-extensionsentities--typed-entity-graph):

```yaml
# In PACK.yaml — instance of `provenance_chain` with edge_attributes
extensions:
  entities:
    - id: ent_a_artwork_xyz
      type: asset
      canonical: "Untitled (1962)"
    - id: ent_p_collector_a
      type: person
      canonical: "Sarah Whitfield"
  relations:
    - id: rel_001
      from: ent_a_artwork_xyz
      to: ent_p_collector_a
      type: provenance_chain               # vocabulary above
      since: "1989-04-12"                  # maps to start_date edge_attribute
      until: "2003-11-08"                  # maps to end_date edge_attribute
      attributes:
        acquisition_method: auction        # enum from edge_attributes
        sale_price: 425000                 # sensitive — audit-only surface
        evidence_ids: [E007]
```

Edge attributes carrying `sensitive: true` (e.g. `sale_price`) MUST NOT
appear in user-facing dossier prose; they surface in audit views only. See
EXTENSIONS.md §3 for the cross-cutting discipline.

---

## 4. Policy Schema

### File Location

Policies live in the `policies/` subdirectory:

```text
routing.kpack/
├── PACK.yaml                    # kind: policy
└── policies/
    ├── perspective-routing.yaml
    ├── priority-rules.yaml
    └── coverage-requirements.yaml
```

### Document Header (Required)

Same metadata fields as definitions:

```yaml
kind: policy
authority: domain-expert-review
version: "2026.1"
status: active
effective_from: "2026-03-29"
```

### Rule Schema

```yaml
kind: policy
authority: domain-expert-review
version: "2026.1"
status: active

rules:
  - id: art-provenance-priority          # Unique rule identifier
    description: >                       # What this rule does
      Art entities prioritize authentication and provenance
      perspectives — forgery risk makes these critical
    condition: "entity.type == 'art'"    # When this rule applies
    action: >                            # What to do
      prioritize perspectives:
        [authentication, provenance, condition, valuation]
    priority: 1                          # Lower = higher priority (for conflict resolution)
    rationale: >                         # Why this rule exists (domain justification)
      Art authentication is a prerequisite for meaningful
      valuation — an unverified work may be worth nothing

  - id: watch-authentication-first
    description: "Watches require authentication before valuation"
    condition: "entity.type == 'watch'"
    action: "require perspectives: [authentication] before [valuation]"
    priority: 1
    scope: research-intake               # Which system context this rule applies to
    rationale: >
      Watch counterfeiting is industrialized — authentication
      must gate all downstream analysis
```

### Rule Scope

The `scope` field declares which system context a rule applies to. This prevents routing rules meant for research intake from accidentally affecting display rendering or voice briefings.

| Scope | Meaning |
|-------|---------|
| `research-intake` | Rules for the research/analysis pipeline |
| `display` | Rules for view rendering and presentation |
| `voice` | Rules for voice delivery and briefing |
| `global` | Applies to all contexts (use sparingly) |

Scope is freeform — implementations define their own scope vocabulary. The spec recommends but does not mandate specific scope values.

### Conflict Resolution

When multiple rules match the same entity, conflicts are resolved by:

1. **Priority** — Lower number wins (priority 1 beats priority 2)
2. **Specificity** — More specific conditions win over general ones (`entity.subtype == 'painting'` beats `entity.type == 'art'`)
3. **Scope** — Context-specific rules win over `global` rules
4. **Recency** — Among equal priority/specificity, the rule with the later `effective_from` date wins

If a conflict cannot be resolved by these criteria, the consuming system should flag it for human review rather than silently choosing.

### Condition Language

Conditions are freeform strings evaluated by the consuming system. The KP:1 spec does not mandate a condition language — implementations choose their own. Common patterns:

```yaml
# Simple type match
condition: "entity.type == 'art'"

# Subtype match
condition: "entity.subtype in ['painting', 'sculpture']"

# Attribute-based
condition: "entity.estimated_value > 100000"

# Compound
condition: "entity.type == 'art' && entity.provenance_length < 3"
```

The condition is a **hint** for the consuming system, not executable code. An LLM reading the policy can interpret conditions in natural language. A code system can parse them into whatever evaluation engine it uses.

---

## 5. PACK.yaml for Definition and Policy Packs

### Kind Declaration

```yaml
# PACK.yaml for a definition pack
name: core-taxonomy
kind: definition                         # Required for non-claim packs
version: 2026.03.29
domain: platform/taxonomy
author: Timothy Kompanchenko

description: >
  Core entity type taxonomy for an alternative assets platform —
  entity types, subtypes, attributes, and relation types.
```

### Kind Values

| Value | Primary Content | Required Files | Optional Files |
|-------|----------------|----------------|----------------|
| `claim` (default) | `claims.md` | PACK.yaml, claims.md | evidence.md, history.md, entities.md, views/ |
| `definition` | `definitions/*.yaml` | PACK.yaml, definitions/ | views/ |
| `policy` | `policies/*.yaml` | PACK.yaml, policies/ | views/ |
| `mixed` | All of the above | PACK.yaml, claims.md, definitions/ or policies/ | All optional files |

### Mixed Packs

A pack with `kind: mixed` contains both ontological content (definitions/policies) and probabilistic content (claims). This is useful when a domain's structural knowledge and entity knowledge are tightly coupled. However, prefer separate packs when possible — mixed packs are harder to version and review.

---

## 6. Versioning and Lifecycle

### Authority

The `authority` field identifies who established the definition or policy. This is not a confidence signal (definitions are deterministic) but a provenance signal — who is responsible for this structural decision.

| Authority | Meaning |
|-----------|---------|
| `platform-team` | Core platform team decision |
| `domain-expert-review` | Reviewed by domain subject matter expert |
| `industry-standard` | Based on industry classification (e.g., Getty AAT) |
| `regulatory` | Required by regulation |

### Status Lifecycle

```text
draft → active → deprecated
                      ↓
               (superseded_by points to replacement)
```

- **draft** — Under development. May be incomplete. Not consumed by production systems.
- **active** — Current and authoritative. Consumed by production systems.
- **deprecated** — Still loadable but a replacement exists. `superseded_by` points to the replacement. Consuming systems should emit warnings.

### Version Strategy

Definitions and policies use CalVer (`YYYY.N`) or SemVer, declared in the `version` field. Version changes signal:

- **Additive changes** (new entity type, new attribute): minor version bump
- **Breaking changes** (removed type, renamed attribute, changed cardinality): major version bump
- **Corrections** (typo in description, reworded rationale): patch or no version change

### Effective Dates

The `effective_from` and `effective_to` fields mark the active window for a definition or policy:

- `effective_from` — When this takes effect (required for temporal queries)
- `effective_to` — When this expires. `null` or omitted means open-ended (no expiry). A non-null value means the definition/policy is time-bounded.

This enables:

- **Scheduled rollouts** — Author a new taxonomy version today, effective next quarter
- **Temporal queries** — "What entity types were active on 2026-01-15?"
- **Sunset planning** — Set `effective_to` on rules with known expiry dates
- **Audit trails** — When combined with git history, full evolution is traceable

---

## 7. Codegen Concept

### The Bridge

Definition packs are YAML designed for domain expert readability and AI consumption. Many runtime systems need TypeScript types, Zod schemas, or enum maps. The codegen bridge connects these:

```text
definitions/*.yaml  →  codegen script  →  generated/*.ts
      ↑                                        ↓
  Domain experts                         Runtime consumers
  review YAML                            import TypeScript
```

### What Gets Generated

| Definition Content | Generated Artifact |
|-------------------|--------------------|
| Entity types + subtypes | TypeScript union types, enum maps |
| Attributes | Zod validation schemas, type interfaces |
| Relation types | Type-safe relation constructors |
| Policy rules | Lookup tables, routing maps |

### Example

From this definition:

```yaml
entity_types:
  - id: art
    subtypes: [painting, sculpture, print]
```

A codegen script produces:

```typescript
// GENERATED — DO NOT EDIT
// Source: core-taxonomy.kpack/definitions/entity-types.yaml

export const EntityType = {
  Art: "art",
  // ...
} as const;

export type EntityType = (typeof EntityType)[keyof typeof EntityType];

export const ArtSubtype = {
  Painting: "painting",
  Sculpture: "sculpture",
  Print: "print",
} as const;

export type ArtSubtype = (typeof ArtSubtype)[keyof typeof ArtSubtype];
```

### Codegen Is Not Part of KP:1

The codegen pipeline is an **implementation concern**. KP:1 specifies the YAML schema; how consumers transform it is their business. The spec guarantees that the YAML is machine-parseable and that the schema is stable within a version.

---

## 8. Migration Path

### From TypeScript to KP Definitions

For existing systems with hand-maintained TypeScript types (e.g., `timbuktu-registry/src/taxonomy/definitions.ts`):

1. **Extract** — Read existing TypeScript and produce equivalent YAML definitions
2. **Author** — Create the `.kpack/` directory with `PACK.yaml` and `definitions/`
3. **Generate** — Build codegen script that produces TypeScript from YAML
4. **Parity test** — Generated TypeScript must be functionally identical to hand-written
5. **Flip** — Switch consumers to import from generated artifacts
6. **Delete** — Remove hand-maintained source after a stable cycle

### Migration Order (Recommended)

| Phase | Content | Difficulty | Impact |
|-------|---------|-----------|--------|
| 1 | **Spec extension** (this document) | Low | Foundation for everything else |
| 2 | **Facet routing policies** | Low | Already declarative YAML |
| 3 | **Core taxonomy definitions** | Medium | 45+ entity types, many attributes |
| 4 | **Perspective catalog** | Medium | Prompt templates add complexity |
| 5 | **CI validation** | Low | Ensures ongoing correctness |

---

## 9. Validation Rules

### Definition Validation

- Every definition file has `kind: definition` and `authority` and `version` and `status`
- Entity type `id` values are unique across all definition files in the pack
- Attribute `applies_to` references existing entity type IDs
- Relation type `source_types` and `target_types` reference existing entity type IDs
- Subtypes are unique within their parent entity type
- If `status: deprecated`, `superseded_by` should be set

### Policy Validation

- Every policy file has `kind: policy` and `authority` and `version` and `status`
- Rule `id` values are unique across all policy files in the pack
- Rules have a non-empty `condition` and `action`
- Priority values are positive integers
- If a rule references entity types (in conditions), those types should exist in a definition pack

### Cross-Pack Validation

- Claims referencing entity types should match types defined in the ontology layer
- Policies routing to perspectives should reference perspectives defined in a definition pack
- Deprecated definitions should not be referenced by active claims or policies without a warning

### Deprecation and Orphan Handling

When a definition is deprecated, existing claims referencing it are not invalidated:

1. **Claims are historical assertions.** A claim made when `entity.type == 'widget'` was active remains valid even after `widget` is deprecated. The claim's `since` date establishes its temporal context.
2. **Tooling should warn, not reject.** When a claim references a deprecated entity type, attribute, or relation, emit a warning: "entity type `widget` deprecated since 2026-06-01 — consider updating to `gadget`."
3. **`superseded_by` enables migration.** If the deprecated definition has `superseded_by: gadget`, tooling can suggest the replacement. Automated migration is an implementation choice, not a spec requirement.
4. **Orphan detection.** A claim referencing an entity type that exists in NO definition pack (not deprecated, not active — simply absent) is an orphan. Tooling should flag orphans for review — they may indicate a missing dependency declaration or a data entry error.
5. **Retroactive invalidation is forbidden.** Changing a definition must never silently invalidate existing claims. This follows from the append-only principle ([RATIONALE.md §1, Principle 5](RATIONALE.md)): the past is preserved.

---

## 10. Design Principles

1. **Deterministic, not probabilistic.** Definitions and policies have no confidence scores. "A painting is a type of artwork" is a structural decision, not an uncertain belief.
2. **Authoritative, not evidenced — but not uncited.** Definitions cite authority (who decided) rather than evidence (what proves it). Domain structure is declared, not discovered. However, the optional `rationale` field documents *why* a definition exists — deterministic does not mean unexplained.
3. **YAML, not markdown.** Definitions are structured data (YAML) because they're consumed programmatically. Claims are markdown because they're consumed by LLMs. Match the format to the consumer.
4. **Constraining, not enforcing.** Definitions inform but do not block. An LLM can reason about a claim that doesn't match the taxonomy — the mismatch is a signal, not an error.
5. **Portable.** Definition packs follow the Voyager Principle. A `.kpack/` directory with YAML definitions is readable by any intelligence without infrastructure.
6. **Versionable.** Definitions evolve. The `version`, `status`, `effective_from`, `effective_to`, and `superseded_by` fields support graceful evolution without breaking consumers.

### Boundary Decision Table

When classifying domain content, use this table to determine the correct kind:

| Content | Kind | Why NOT the other? |
|---------|------|--------------------|
| Entity type catalog (art, watch, wine) | `definition` | Structural vocabulary, not a rule about what to do |
| "Art entities should prioritize authentication" | `policy` | Behavioral rule, not structural vocabulary |
| Attribute vocabulary (medium, dimensions) | `definition` | What attributes exist, not what to do with them |
| "Which perspectives apply to which entity types" | `policy` | Routing behavior, not domain structure |
| Relation types (created_by, provenance_chain) | `definition` | What relations exist, not when to use them |
| "High-value items require expedited review" | `policy` | Threshold rule governing behavior |
| "This specific Monet is oil on canvas" | `claim` | Assertion about a real entity (has uncertainty) |
| Industry classification standard (e.g., Getty AAT) | `definition` | External vocabulary adopted as structure |

**The test:** Remove all verbs like "should", "must", "prioritize", "require." If the content still makes sense, it's a definition. If the verbs are the point, it's a policy. If it's about a specific entity instance, it's a claim.

### Catalog-Level Entities (The Gray Area)

Alternative assets often have a hierarchy between the abstract type and the specific item:

```text
Domain (Watch) → Brand (Rolex) → Model (Daytona) → Reference (116500LN) → Item (Serial #78432)
```

Where does the **definition** end and the **claim** begin?

| Level | Kind | Rationale |
|-------|------|-----------|
| Domain (`watch`) | `definition` | Structural — defines the vertical |
| Brand (`rolex`) | Edge case | Could be a definition (vocabulary) or a claim entity |
| Model (`daytona`) | `claim` entity | Specific enough to have disputed properties |
| Reference (`116500LN`) | `claim` entity | Has attributes that change over time (market price) |
| Item (`serial #78432`) | `claim` entity | Specific real-world thing with unique provenance |

**The rule of thumb:** If it's stable enough to appear in a dropdown menu and never needs a confidence score, it can be a definition (entity type or subtype). If it has properties that different sources might dispute or that change over time, it's a claim entity.

**For most domains:** Brands and product lines sit at the boundary. The pragmatic choice is:
- **Subtypes in definitions** for broad categories (painting, sculpture) that are universally agreed
- **Claim entities** for specific brands, models, and references that have market-relevant properties

This keeps definitions stable (slow-changing vocabulary) and claims dynamic (fast-changing facts about specific things). A definition pack should not need to update when Rolex releases a new reference number — that's entity knowledge, not domain structure.

### Future Work

The following are recognized gaps deferred to future spec revisions:

- **Attribute inheritance.** If `art` defines `dimensions` as a key attribute, subtypes like `painting` should inherit it. The schema currently has no inheritance or override mechanism. Until formalized, the convention is: subtypes inherit all parent attributes implicitly; overrides are documented in comments.
- **Temporal claim validation.** When a definition changes (`effective_from: 2026-06-01`), claims made under the old definition (`since: 2025-01-01`) should validate against the definition active at claim time, not the current definition. This requires a temporal resolution mechanism that is not yet specified.
- **Local attribute constraints.** Entity-type-level overrides for attribute properties (e.g., `condition` required for `watch` but optional for `real_estate`) are not supported. The `attributes.yaml` schema defines global defaults; type-specific overrides require a mechanism for local constraint declaration.
