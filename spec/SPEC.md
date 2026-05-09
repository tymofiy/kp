<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Knowledge Pack Specification v0.8.0

> **Status:** Editor's Draft — `KP:1 Public Draft — 2026-04`
> **Editor:** Timothy Kompanchenko
> **Date:** 2026-03-29
> **Version history:** See `CHANGELOG.md`
> **Lane:** Full normative spec + rationale + ecosystem — see [README.md](README.md) for the three-lane structure (CORE = implementer surface, SPEC = comprehensive, companions = topic-authoritative for their domains).

## Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

---

## 1. Overview

A **Knowledge Pack** is a portable representation of epistemic state — what someone believes, how strongly they believe it, based on what evidence, in tension with what other beliefs, as understood at a particular moment in time.

This is not a database format. Databases store facts: certain, flat, internally consistent. Knowledge is none of those things. Knowledge is **inherently uncertain** — the uncertainty is the knowledge, not metadata about it. Knowledge **contains contradictions** — two sources disagree, and the disagreement itself is information, not a bug to be resolved. Knowledge **decays** — confidence should lower over time without new evidence, because the world changes. Knowledge is **perspectival** — the same beliefs serve fundamentally different purposes when reasoned over, read visually, or spoken aloud.

No existing format represents these properties. Database schemas model facts. Semantic Web standards (RDF, JSON-LD, SKOS) model relationships between entities. Personal knowledge tools (Obsidian, Roam) model notes. RAG systems model documents. None of them model **what someone believes and why** — the epistemic state that sits underneath all of those representations.

A Knowledge Pack does. It packages claims with confidence, evidence, relationships, and contradiction into a multi-file plain text format that any intelligence — human or AI — can read without special tooling.

### Why This Matters

When an AI reasons about a domain, it needs more than facts. It needs to know: *How sure are we? Who said this? Does it contradict something else we believe? When was this last confirmed? What evidence supports it?* Without these, the AI treats all information as equally true — which is how hallucinations become indistinguishable from knowledge.

When a human transfers knowledge to another human, they naturally include this context: "I think the market is about $2 billion, but that number is from last year's report and a colleague quoted a different figure." Every database, every spreadsheet, every structured format strips this away. Knowledge Packs preserve it.

### Design Philosophy

**The Voyager Principle:** Knowledge Packs must function with zero infrastructure dependencies beyond "a device that can process text." Like the Voyager Golden Record — symbols understandable by any intelligence without the sending civilization's infrastructure. No internet, no registry, no parser, no compiler. A hard drive, a computer, and a language model is all you need. This principle is a generative constraint: by designing for the most extreme portability, we free ourselves from unconsciously assuming today's infrastructure. The practical result is a format that depends on nothing but text and intelligence.

**Knowledge, not data:** Only epistemic content belongs in a Knowledge Pack — beliefs with confidence, evidence, and relationships. Instructions, procedures, configurations, and runtime data have their own formats. A knowledge pack represents what is believed to be true. An instruction set tells an agent how to behave. These are different concerns. "Only knowledge is a knowledge pack."

**Uncertainty is first-class:** Confidence scores, evidence chains, and contradiction relations are not optional metadata — they are the core of the format. A claim without a confidence level is incomplete. A contradiction between claims is surfaced, not resolved. The epistemic state IS the content.

**Three surfaces, one truth:** Knowledge Packs serve three modes of engagement through three surfaces. The **reasoning surface** (claims.md) is dense and optimized for AI inference — it represents what is believed and why. The **display surface** (views/) is pre-rendered markdown optimized for human visual comprehension. The **voice surface** (views/voice/) is optimized for spoken delivery — short sentences, pronunciation hints, pause markers. These are not cosmetic variations. Reading, seeing, and hearing are epistemically distinct acts. But all three surfaces represent the same underlying beliefs — views are derived from claims, never authoritative.

**Inspectability over readability:** The reasoning surface is optimized for AI consumption and information density. A human CAN inspect and verify the contents (it's plain text, not binary), but the format does not waste tokens on reading comfort. LLMs are the natural interface for humans engaging with the reasoning surface. Display and voice views serve human perception directly.

### What a Knowledge Pack Is

- A directory of plain text files (UTF-8 markdown + YAML) representing epistemic state
- Claims — beliefs with confidence, provenance, evidence, and relationships to other claims
- Contradictions preserved as knowledge, not eliminated as errors
- Zero-dependency — no tooling, parser, or infrastructure required to consume
- Portable across any AI system that can read text
- Versionable, diffable, reviewable via standard git workflows

### What a Knowledge Pack Is NOT

- A database (it represents beliefs with uncertainty, not facts with certainty — but databases can store and index packs as derived representations; see `spec/STORAGE.md`)
- A RAG pipeline (it's the input to one, not the system itself)
- A fine-tuning dataset (it's consumed at inference time, not training time)
- An instruction set (that's Agent Skills / SKILL.md)
- A context configuration (that's the role of agent instruction files like AGENTS.md)
- A runtime data protocol (that's MCP Resources)
- A note-taking format (unstructured notes are not knowledge packs; however, packs CAN contain structured notes and action items alongside claims — see `spec/STORAGE.md` §6)

### Position in the AI Stack

| Layer | Standard | Packages |
|-------|----------|----------|
| Context configuration | Agent instruction files (e.g., AGENTS.md) | Agent behavior, preferences |
| Capabilities | Agent Skills (SKILL.md) | Procedures, tools, scripts |
| **Epistemic state** | **Knowledge Packs** | **Beliefs, confidence, evidence, contradictions** |
| Runtime access | MCP Resources | Live data endpoints |

---

## Quick Start — Create a Knowledge Pack in 5 Minutes

1. Create a directory:
```bash
mkdir my-project.kpack && cd my-project.kpack
```

2. Write `PACK.yaml`:
```yaml
name: my-project
version: 2026.03.19
domain: technology/saas
author: Your Name
confidence: { scale: simple, normalize: true }
```

3. Write `claims.md`:
```markdown
<!-- KP:1 — Knowledge Pack Format
Claims: - [ID] assertion {confidence|type|evidence|date|depth|nature} context
  Positions 5-6 optional. Verbose named-field syntax also accepted.
Types: o=observed r=reported c=computed i=inferred
Depth: assumed | investigated | exhaustive (optional, position 5)
Nature: judgment | prediction | meta (optional, position 6; omitted=factual)
Relations: →supports ⊗contradicts ⊗!error ⊗~tension ←requires ~refines ⊘supersedes ↔see_also
Files: evidence.md=sources history.md=past entities.md=graph
-->
---
pack: my-project | v: 2026.03.19 | domain: technology/saas
confidence: simple | normalized
---

# My Project [product|MyProject,MP]

> B2B SaaS platform for widget management.

## Overview

- [C001] B2B SaaS for widget management, 50 enterprise customers
  {0.99|o|E001|2026-01-01}

- [C002] AI-powered widget classification = primary differentiator
  {0.85|i|E002,E003|2026-02-15} 40% misclassification reduction vs.
  competitors' rule-based systems (12-account A/B test). →C001
```

The HTML comment at the top is the **Rosetta header** ([CORE.md §4](CORE.md#4-claimsmd--rosetta-header) — required, self-describing). It lets a previously-unfamiliar consumer recognize a Knowledge Pack and tokenize its contents without external context.

4. Write `evidence.md`:
```markdown
# Evidence

## E001
> type: observed | captured: 2026-01-01
> source: Company records, CRM dashboard

Customer count and platform functionality verified directly.

## E002
> type: research | captured: 2026-02-15
> source: Internal A/B test — Q4 2025, 12 enterprise accounts

40% reduction in misclassification. AI classification vs. rule-based.

## E003
> type: web | captured: 2026-02-10
> source: Competitor documentation review (5 platforms)

All 5 competitors use rule-based classification, no ML/AI component.
```

5. Done. Any LLM can read `claims.md` and reason about your project. Any human can inspect it and verify what's claimed.

---

## 2. File Structure

A Knowledge Pack is a directory with a conventional name ending in `.kpack/` (recommended but not required).

```text
{name}.kpack/
├── PACK.yaml              # REQUIRED — Manifest
├── claims.md              # REQUIRED — Current truth (the primary file)
├── evidence.md            # RECOMMENDED — Backing sources and citations
├── history.md             # RECOMMENDED — Superseded claims (audit trail)
├── entities.md            # OPTIONAL — Entity definitions and relationships
├── composition.yaml       # OPTIONAL — Meeting/composite pack references (see spec/COMPOSITION.md)
├── validation.yaml        # OPTIONAL — Test questions for verification
├── signatures.yaml        # OPTIONAL — Cryptographic integrity proof (see spec/ARCHIVE.md)
├── definitions/           # OPTIONAL — Deterministic domain definitions (kind: definition)
│   └── {topic}.yaml       #   Entity types, attributes, relation types
├── policies/              # OPTIONAL — Domain rules and prioritization (kind: policy)
│   └── {topic}.yaml       #   Routing rules, applicability, priorities
└── views/                 # OPTIONAL — Pre-rendered display content
    ├── overview.md        # Display view — visual (recommended first view)
    ├── {facet}.md         # Domain-specific display views
    ├── voice/             # Voice views — spoken delivery
    │   └── briefing.md    # Voice-optimized briefing
    └── {locale}/          # Locale-specific views (e.g., uk/)
        ├── overview.md    # Translated display view
        └── voice/         # Translated voice views
            └── briefing.md
```

### File Roles

| File | Loaded | Purpose |
|------|--------|---------|
| `PACK.yaml` | Always (metadata only) | Manifest: version, domain, dependencies, confidence scale |
| `claims.md` | **Always — this is THE file** | Current active claims ONLY. Maximally dense. The LLM's complete picture of current truth. (~2-8K tokens) |
| `evidence.md` | On demand | Backing data: source URIs, content excerpts, timestamps. Referenced by claim IDs |
| `history.md` | On demand | Superseded and retracted claims. The audit trail. Preserves every past state |
| `entities.md` | On demand | Entity definitions with types, aliases, URIs, relationship graph |
| `views/*.md` | On display | Pre-rendered markdown for human visual consumption. Derived from claims. See §16 |
| `validation.yaml` | Tooling only | Test questions to verify an LLM can reason from the pack |
| `signatures.yaml` | Tooling only | Cryptographic hashes + signing key for integrity verification (see spec/ARCHIVE.md) |
| `definitions/*.yaml` | On demand | Deterministic domain definitions: entity types, attributes, relations. See §5 |
| `policies/*.yaml` | On demand | Domain rules and prioritization logic. See §5 |

### The Core Contract

**claims.md gives the LLM everything it needs to reason AND everything it needs to know where to look for more.** An LLM reading only claims.md should:

1. Understand the domain's current truth (all active claims)
2. Know that evidence.md exists and can be loaded for citations
3. Know that history.md exists and can be loaded for audit/temporal questions
4. Know that entities.md exists and can be loaded for relationship graphs
5. See `↔` cross-references to other packs for deeper exploration

The primary file is a **complete reasoning surface** AND a **navigation map** to everything else.

### Composition-pack File Requirements

A pack whose `composition.yaml` is present is a **composition pack** (also called a *composite pack* — see `spec/COMPOSITION.md` for the full semantics). Composition packs reference claims in other packs via `↔` see_also relations rather than carrying their own evidence. The file requirements adjust as follows:

| File | Standard pack | Composition pack |
|------|---------------|------------------|
| `PACK.yaml` | REQUIRED | REQUIRED |
| `composition.yaml` | ABSENT | REQUIRED (defines the composition) |
| `claims.md` | REQUIRED | REQUIRED — contents are intentionally minimal: claims describe the composition context itself (who, when, why, what changed), not the topics being composed (see COMPOSITION.md §3) |
| `evidence.md` | RECOMMENDED — required in practice whenever any claim cites an evidence ID | OPTIONAL — may be omitted entirely |
| Everything else (`history.md`, `entities.md`, `views/`, `definitions/`, `policies/`, `signatures.yaml`, `validation.yaml`) | unchanged | unchanged |

A composition pack MUST NOT redefine the claims or evidence of a pack it references. Its `claims.md` contains only claims about the composition itself; the referenced packs remain the canonical source for their own content.

---

## 3. PACK.yaml — Manifest

### Required Fields

```yaml
name: solar-energy-market              # Identifier (kebab-case, unique within scope)
version: 2026.03.18                    # CalVer (YYYY.MM.DD) — snapshot date
domain: energy/market-analysis         # Hierarchical domain path
author: Jane Chen                      # Maintainer
```

### Optional Fields

```yaml
kind: claim                            # claim (default) | definition | policy | mixed
                                       #   See §5 for document kinds

description: >                         # Human-readable summary
  Solar energy market analysis — technology trends, cost trajectories,
  and regional adoption patterns for utility-scale photovoltaic systems.

confidence:                            # Confidence model declaration
  scale: sherman_kent                  #   Native scale identifier
  normalize: true                      #   Claims use 0-1 normalized values

freshness: "2026-03-18"                # Last substantive review date
license: CC-BY-4.0                     # Reuse terms
sensitivity: public                    # public | internal | confidential | restricted
visibility: private                    # private | shared | public (see spec/LIFECYCLE.md)

channels: [team]                       # Distribution routing (see §3.1 Channels)
                                       #   Spec-defined: team | org | public
                                       #   Custom: namespace/name (e.g., acme/demo)
                                       #   Default: [] (owner-only, no distribution)

linguistic_epoch: en-US-2026           # Language era for semantic anchoring
ontology: western-empirical            # Knowledge framework (freeform declaration)

dependencies:                          # Other packs this builds on
  - uri: github.com/example/energy-taxonomy.kpack
    version: ">=2026.01"
  - uri: local:../shared-entities.kpack
  - uri: local:../core-taxonomy.kpack   # Ontology dependency (see §5)
    version: ">=2026.1"                 #   Claims validated against these definitions
    kind: definition                    #   Declares this is an ontology dependency

conflicts:                             # Known contradictions with other packs
  - pack: market-research-v2
    note: "Uses different TAM methodology"
    basis: methodology                 #   methodology | data_source | temporal | interpretation | scope
    resolution: prefer-this            # prefer-this | prefer-other | flag-for-review

provenance:                            # Trust context (S-C1: Poisoned Pack)
  author: Jane Chen                    #   Who created/maintains this
  role: independent                    #   manufacturer | independent | regulator | academic | individual
  reviewed_by: null                    #   Independent reviewer's name, if any
  review_date: null                    #   When independently reviewed
  signed: false                        #   Cryptographic signature present?

vocabulary:                            # Predicate conventions
  custom:                              #   Domain-specific predicates
    - cost_trajectory
    - adoption_rate

files:                                 # Non-standard file names (defaults assumed if omitted)
  claims: claims.md
  evidence: evidence.md
  entities: entities.md
  validation: validation.yaml

display:                               # Cognitive perception layer (see §18)
  short_title: "Solar Market"          #   Condensed title for constrained contexts
  abbreviation: "SEM"                  #   2-5 chars for badges, pills, breadcrumbs
  tagline: >                           #   One sentence: what this IS (recognition < 3s)
    Utility-scale solar market trends and cost analysis

views:                                 # Pre-rendered display views (see §16)
  - name: overview                     #   View identifier
    file: views/overview.md            #   Path within pack
    purpose: "Executive summary with key metrics and status"
    display_as: "Overview"             #   UI tab/section label
    hint: "Market size, growth rate, key players, cost trends"  # Human navigation aid (see §18)
  - name: technology
    file: views/technology.md
    purpose: "Technology comparison and efficiency trajectories"
    display_as: "Technology"
    hint: "Panel types, efficiency curves, emerging technologies"

style: null                            # External style system reference (see §17)
                                       #   style-id string | null = unstyled markdown

lifecycle:                             # Pack lifecycle management (see spec/LIFECYCLE.md)
  type: permanent                      #   permanent | seasonal | ephemeral
  archive_after_days: null             #   Auto-archive after N days (ephemeral packs)
  archive_policy: reconcile            #   reconcile | auto | manual
  reconciled_at: null                  #   Timestamp of last reconciliation check
  orphan_claims: []                    #   Unreconciled claims found during review

consolidation:                         # Knowledge consolidation targets (ephemeral/seasonal packs)
  targets:                             #   Standing packs that should receive consolidated claims
    - pack: renewable-strategy         #   Target pack name
      claims: [F001, F002, A001]       #   Claims to consolidate (or "all-knowledge" for auto-classify)
    - pack: market-landscape
      claims: [F011, F012]
  status: pending                      #   pending | in-progress | complete
  completed_at: null                   #   ISO timestamp of consolidation completion

locales:                               # Multilingual support (see spec/MULTILINGUAL.md)
  canonical: en-US                     #   Canonical language (always American English)
  available:                           #   Translated locale views
    - locale: uk-UA
      display_name: "Українська"
      status: draft                    #   draft | reviewed | verified
      views: [overview, briefing]
      derived_from: "claims@2026.03.22"
      translator: machine             #   machine | human | hybrid
      reviewed_by: null

notes:                                 # AI note-taking metadata (see spec/NOTES.md)
  mode: "off"                          #   active (structured extraction) | passive (full transcript) | off
  participants: []                     #   Meeting participants
  disclosed: false                     #   Was AI note-taking disclosed to participants?
  consent: null                        #   Required for mode: passive — obtained | declined | pending

extensions:                            # Experimental / implementation-specific manifest metadata
  ai_brief:                            #   Example extension payload (not core KP:1)
    version: 1
    verdict: acceptable
    headline: "Strong base attribution, but provenance gap remains"
```

### Version Semantics

Packs use **Calendar Versioning (CalVer)**: `YYYY.MM.DD`, optionally with a revision suffix (`2026.03.18-rev2`).

Rationale: Facts are snapshots in time, not API contracts. CalVer is natural for knowledge that evolves by date, not by breaking-change semantics.

### 3.1 Channels — Distribution Routing

The `channels` field declares which distribution cohorts may receive a pack. It is
the third axis of access control, orthogonal to the other two:

| Axis | Question | Values |
|------|----------|--------|
| `sensitivity` | How strictly must this data be handled? | `public`, `internal`, `confidential`, `restricted` |
| `visibility` | Who can discover/query this once deployed? | `private`, `shared`, `public` |
| `channels` | Which deployment cohorts receive this pack? | Set of strings (see below) |

**Syntax:** An optional array of unique, lowercase strings with set semantics.
Order is non-semantic. Default is `[]` (owner-only — no automated distribution).

```yaml
channels: []                           # Owner-only (default if omitted)
channels: [team]                       # Internal team environments
channels: [team, org]                  # Organization-wide
channels: [team, acme/investor]        # Team + custom channel
channels: [public]                     # Openly distributable
```

**Spec-defined vocabulary** (bare names, reserved):

| Channel | Meaning |
|---------|---------|
| `team` | Named collaborators and internal team environments |
| `org` | Broader authenticated organization environments |
| `public` | Eligible for unrestricted public distribution |

**Custom channels** use namespaced format: `{namespace}/{name}`. Bare names
not in the spec vocabulary SHOULD be rejected by linters. Examples:

```yaml
channels: [acme/investor]              # Investor demo environments
channels: [acme/stakeholder]           # Stakeholder previews
channels: [acme/partner]               # Partner-facing content
```

**Validation rules:**

| Constraint | Rule |
|------------|------|
| `sensitivity: confidential` | `channels` MUST NOT contain `public` or `org` |
| `sensitivity: internal` | `channels` MUST NOT contain `public` |
| `channels` contains `public` | `visibility` SHOULD be `public` |
| Unknown bare name | MUST warn (likely typo or missing namespace) |
| Duplicate entries | MUST reject |

**Inheritance:** Sub-packs (tier: detail) do NOT inherit channels from their
hub pack. Each pack declares its own channels explicitly. This prevents
accidental over-distribution through implicit inheritance.

**Deployment mapping:** Channels are mapped to concrete environments by
deployment configuration (outside this spec). A typical mapping:

```yaml
# deployment/environments/alpha.yaml (NOT part of KP:1 spec)
name: alpha
channels: ["*"]                        # Everything
---
# deployment/environments/beta.yaml
name: beta
channels: [team, org]
---
# deployment/environments/production.yaml
name: production
channels: [org, public]
```

The spec defines the `channels` field and its vocabulary. How channels map to
infrastructure is a deployment concern.

### 3.2 Manifest Extensions

The PACK.yaml root is intentionally closed. New or experimental manifest keys MUST NOT be added at the top level unless and until they are standardized by a future KP revision.

Implementation-specific or experimental metadata MUST live under the optional `extensions` object. Consumers MUST ignore extension content they do not understand. Extension content MUST NOT override or redefine the meaning of core KP fields.

The example payload shown earlier (`ai_brief`) is illustrative — extension names and shapes are defined by their producers, not by KP:1. This creates a narrow compatibility lane: tools can ship experiments without forcing a schema break or prematurely promoting the payload into the core standard.

---

## 4. claims.md — The Primary File

### Structure

```markdown
<!-- KP:1 — Knowledge Pack Format
Claims: - [ID] assertion {confidence|type|evidence|date|depth|nature} context
  Positions 5-6 optional. Verbose named-field syntax also accepted.
Types: o=observed r=reported c=computed i=inferred
Depth: assumed | investigated | exhaustive (optional, position 5)
Nature: judgment | prediction | meta (optional, position 6; omitted=factual)
Relations: →supports ⊗contradicts ⊗!error ⊗~tension ←requires ~refines ⊘supersedes ↔see_also
Files: evidence.md=sources history.md=past entities.md=graph
-->
---
pack: {name} | v: {CalVer} | domain: {domain}
confidence: {scale} | normalized
---

# {Pack Title} [{entity_type}|{aliases}]

> {One-line description}

## {Section}

- [{claim_id}] {Claim headline — single assertable proposition}
  {confidence|type|evidence_ids|since_date|depth|nature} Optional context prose.
  {relation_symbols}{claim_ids}
```

### Rosetta Header (Mandatory)

Every claims.md MUST begin with a self-describing legend comment before the frontmatter. This serves three purposes:

1. **Self-describing:** Any intelligence encountering the file for the first time can decode the notation without external documentation
2. **Format versioning:** `KP:1` identifies the spec version — future versions use `KP:2`, `KP:3`, giving any parser an immediate signal
3. **Navigation map:** Lists the companion files and their roles — the LLM knows what else exists without reading PACK.yaml

Cost: ~50 tokens. Non-negotiable — the Voyager Principle demands the file explain itself.

### Frontmatter

Compact YAML frontmatter using pipe-delimited fields. An LLM encountering just `claims.md` (without `PACK.yaml`) should still understand the pack identity and confidence model.

### Claim Anatomy

Each claim is a markdown list item with two layers:

1. **Headline** — The claim itself. A single, independently verifiable assertion. Claim ID in brackets.
2. **Metadata + prose line** — Curly-brace metadata block followed by optional prose. Prose is minimal — only what adds meaning beyond the structured data. Many claims need zero prose.

Relation symbols follow the prose (or metadata if no prose):

| Symbol | Meaning |
|--------|---------|
| `→` | supports |
| `⊗` | contradicts (unqualified — flag for review) |
| `⊗!` | contradicts:error (one is wrong — prioritize resolution) |
| `⊗~` | contradicts:tension (both informative — preserve as productive disagreement) |
| `←` | requires / depends on |
| `~` | refines / adds detail to |
| `⊘` | supersedes |
| `↔` | see_also (cross-pack: `pack_name#section`) |

Contradiction qualifiers: bare `⊗` is the default when the nature of the disagreement hasn't been assessed. Use `⊗!` when investigation shows one claim is wrong. Use `⊗~` when both claims are informative and the tension itself is knowledge (different methodologies, different scopes, different perspectives).

### Claim Fields (inside `{}`)

Pipe-delimited, positional: `{confidence|type|evidence_ids|since_date|depth|nature}`

Positions 1-4 are required. Positions 5-6 are optional — omit trailing fields when not needed. To specify position 6 without position 5, use an empty slot: `{0.85|r|E020|2026-03-10||prediction}`. Empty interior slots are always valid and mean "unspecified."

| Position | Required | Values | Description |
|----------|----------|--------|-------------|
| 1 | Yes | 0.0 - 1.0 | Normalized confidence |
| 2 | Yes | `o` (observed), `r` (reported), `c` (computed), `i` (inferred) | Claim type (single letter) |
| 3 | Yes | Comma-separated IDs | Evidence references |
| 4 | Yes | YYYY-MM-DD | When established |
| 5 | No | `assumed`, `investigated`, `exhaustive` | Investigation depth (omit if unspecified) |
| 6 | No | `judgment`, `prediction`, `meta` | Claim nature (omit = factual assertion) |

### Claim Types (position 2)

| Type | Meaning | Example |
|------|---------|---------|
| `observed` | Directly verified from primary source | "Codebase has 85K lines of TypeScript" |
| `reported` | Stated by a credible source, not independently verified | "CEO says revenue grew 40%" |
| `computed` | Output of automated analysis | "Match score: 0.73 for mentor-student pair" |
| `inferred` | Derived from other claims via reasoning | "Scaffolding is the product, not matching" |

### Investigation Depth (position 5, optional)

Investigation depth captures how thoroughly a claim has been examined. This is distinct from confidence — confidence measures how sure we are, depth measures how much we've looked into it.

| Depth | Meaning |
|-------|---------|
| `assumed` | Taken at face value — minimal investigation, gut feel, placeholder |
| `investigated` | Multiple sources consulted, cross-referenced, actively researched |
| `exhaustive` | Thorough investigation — remaining uncertainty is genuine, not ignorance |

A claim at 0.50 confidence with `exhaustive` depth is more valuable knowledge than a claim at 0.90 confidence with `assumed` depth. The former represents informed uncertainty — the ambiguity itself is what we know. The latter is an uninvestigated assumption that may collapse under scrutiny.

When omitted, depth is unspecified — the consumer cannot distinguish ignorance from informed uncertainty. New claims and claim updates should record depth when the distinction matters.

### Claim Nature (position 6, optional)

Claim nature describes what KIND of knowledge the claim represents. This is distinct from claim type (position 2), which describes how the claim was ACQUIRED (provenance).

| Nature | Meaning | Example |
|--------|---------|---------|
| `judgment` | Interpretive conclusion drawn from evidence | "Scaffolding is the product, not matching" |
| `prediction` | Forward-looking claim with a resolution horizon | "Pilot launches September 2026" |
| `meta` | Claim about the state of knowledge itself | "Our market size estimates are unreliable" |

When omitted, the claim is a factual assertion (the default). Only annotate claims that are NOT straightforward facts.

**Predictions** have temporal semantics: the `since` date is when the prediction was made, and the claim text implies a resolution date. There is no structured horizon field — patrol extracts resolution dates from claim text on a best-effort basis. If the prediction text does not contain a recognizable date, patrol cannot flag it automatically.

**Meta-claims** signal where the knowledge system is weakest. An agent loading a meta-claim like "our competitive analysis is shallow" `{0.60|i|E001|2026-03-01|assumed|meta}` knows to be cautious about competitive claims and to seek additional evidence.

### Relation Verbs

| Verb | Meaning |
|------|---------|
| `supports` | This claim provides evidence for another |
| `contradicts` | This claim conflicts with another (unqualified — needs review) |
| `contradicts:error` | One of these claims is wrong — prioritize resolution |
| `contradicts:tension` | Both claims are informative — the disagreement itself is knowledge |
| `requires` | This claim depends on another being true |
| `refines` | This claim adds detail to another |
| `supersedes` | This claim replaces a prior claim |

### Alternative Verbose Syntax

The dense positional notation is the primary format, but KP:1 also accepts a verbose named-field syntax. Both are valid. Tooling MUST parse both forms.

**Dense (positional):**
```markdown
- [C001] Scaffolding = product; matching = infrastructure
  {0.95|i|E001,E002|2026-03-01|exhaustive|judgment} →C002 ⊗~C003
```

**Verbose (named fields):**
```markdown
- **[C001]** Scaffolding = product; matching = infrastructure
  `confidence: 0.95 | type: inferred | evidence: E001, E002 | since: 2026-03-01 | depth: exhaustive | nature: judgment`
  Context prose goes here.
  `relations: supports C002, contradicts:tension C003`
```

The claim headline (first line) and prose context are identical in both forms. Only the metadata and relation notation differ. Verbose metadata is wrapped in backtick delimiters; relations use a separate backtick-delimited `relations:` line with comma-separated entries. Dense is more compact for context injection. Packs may mix forms — individual claims within the same file can use either syntax.

### Sections

Claims are organized into sections (`## headings`) by topic. Section organization is freeform — the author chooses what grouping makes sense for the domain. Common patterns:

- By facet: `## Thesis`, `## Architecture`, `## Team`, `## Risks`
- By entity: `## Apple Inc.`, `## Microsoft Corp.`
- By time: `## Q1 2026`, `## Q2 2026`

### Example

```markdown
---
pack: solar-energy-market | v: 2026.03.18 | domain: energy/market-analysis
confidence: sherman_kent | normalized
---

# Solar Energy Market [market-analysis|SEM,solar]

> Utility-scale solar market trends, cost trajectories, and regional adoption patterns.

## Thesis

- [C001] Cost decline is structural, not cyclical — driven by manufacturing scale
  {0.95|i|E001,E002|2026-03-01|exhaustive|judgment} 10/10 analyses converged.
  Learning curve (22% cost reduction per doubling) has held for 40 years. →C002, ⊗~C003

- [C002] Grid parity already achieved in 75% of global markets
  {0.90|i|E001|2026-03-01|investigated|judgment} IRENA/BloombergNEF data.
  Subsidy removal in mature markets has not reversed adoption. →C001

- [C003] Cost floor approaching — further declines will slow significantly
  {0.30|r|E003|2026-02-14|investigated|judgment} Silicon material costs
  impose theoretical floor. 3/10 analyses supported this framing.
  Tension with C001 is informative — reveals the timeline question. ⊗~C001

## Technology

- [C010] Bifacial modules now 70% of new installations globally
  {0.99|o|E010|2026-03-18} Rear-side gain 5-25% depending on albedo.
  Bankability established. Monofacial declining to niche applications.

- [C011] Perovskite tandem cells: 33.7% lab efficiency (Oxford PV)
  {0.99|o|E011|2026-03-18} Lab-to-fab gap remains. Commercial viability
  estimated 2028-2030 for utility scale. →C012

- [C012] Durability is the unsolved risk for perovskite commercialization
  {0.75|i|E012,E013|2026-03-10} Moisture/heat degradation pathways known
  but not fully mitigated. 25-year warranty requirement is the hard gate. ←C011

## Market & Adoption

- [C020] Global installed capacity will exceed 2 TW by end of 2027
  {0.85|r|E020|2026-03-10||prediction} Depends on China production + India demand.

- **[C021]** Key markets: China (45%), US (15%), India (12%), EU (10%)
  `confidence: 0.95 | type: observed | evidence: E020 | since: 2026-03-10`
  China dominates manufacturing and deployment. US growth driven by IRA
  incentives with political risk. India accelerating from low base.

## Risks

- **[C030]** Supply chain concentration in China is the highest systemic risk
  `confidence: 0.90 | type: inferred | evidence: E001, E030 | since: 2026-03-01 | depth: exhaustive | nature: meta`
  80% of polysilicon, 95% of wafers. Tariff/geopolitical disruption could
  create 12-18 month supply gaps. 8/10 analyses flagged this. Not a technology
  problem — a trade policy and diversification problem.
  `relations: requires C020`
```

---

## 5. Document Kinds — Three Knowledge Types

Knowledge Packs contain three kinds of documents, distinguished by the `kind` field.

### The Principle

**If it defines the domain, it's a definition. If it governs behavior within the domain, it's a policy. If it asserts something about a specific real-world entity, it's a claim.**

| Kind | Purpose | Epistemology | Key Fields |
|------|---------|-------------|------------|
| `claim` | Assert facts about entities | Probabilistic — confidence, evidence, contradictions | `confidence`, `type`, `evidence_ids`, `since` |
| `definition` | Define domain structure | Deterministic — what the domain IS | `authority`, `version`, `status`, `effective_from` |
| `policy` | Govern domain behavior | Deterministic — rules and priorities | `authority`, `version`, `status`, `effective_from` |

### Two-Layer Model

Claims are the **knowledge layer** — probabilistic assertions about specific real-world entities. Definitions and policies are the **ontology layer** — deterministic facts about the domain itself.

```text
Ontology Layer (deterministic)          Knowledge Layer (probabilistic)
├── core-taxonomy.kpack/                ├── monet-water-lilies.kpack/
│   └── definitions/                    │   └── claims.md
│       ├── entity-types.yaml           │
│       └── relation-types.yaml         ├── my-collection.kpack/
│                                       │   └── claims.md
├── perspectives.kpack/                 │
│   └── definitions/                    └── market-trends-2026.kpack/
│       └── catalog.yaml                    └── claims.md
│
└── routing.kpack/
    └── policies/
        └── rules.yaml
```

**The ontology layer defines what's possible. The knowledge layer says what's true.** Definitions establish the vocabulary that claims operate within. When definitions are loaded, an LLM can validate claims against the domain model — flag unknown entity types, detect attribute mismatches, check relation validity. When definitions are absent, claims remain fully interpretable on their own. The constraint is **advisory**: it improves reasoning quality but is never required for comprehension.

### Boundary Decision Table

| Content | Kind | Why |
|---------|------|-----|
| "Painting is a subtype of Artwork" | `definition` | Structural — what the domain IS |
| "Art entities should prioritize authentication" | `policy` | Behavioral — what the system should DO |
| "This Monet is oil on canvas, 1906" | `claim` | Assertion about a specific entity |
| "The art market grew 12% in 2025" | `claim` | Assertion about the world (has uncertainty) |
| "Art entities have a `medium` attribute" | `definition` | Structural — what attributes exist |
| "High-value items require two authentication sources" | `policy` | Behavioral — a business rule |
| "Provenance chains link assets to owners over time" | `definition` | Structural — what relations exist |
| "Items over $100K get expedited review" | `policy` | Behavioral — a threshold rule |

### Definitions

Ontological facts about the domain: entity types, attributes, subtypes, relation types. No confidence scores — these are not uncertain beliefs but structural decisions about how the domain is organized.

```yaml
# definitions/entity-types.yaml
kind: definition
authority: domain-taxonomy-v1
version: "2026.1"
status: active          # active | deprecated | draft
effective_from: "2026-03-29"

entity_types:
  - id: energy_source
    name: Energy Source
    description: "Primary energy generation technology or fuel type"
    subtypes: [solar_pv, solar_thermal, wind_onshore, wind_offshore, hydro, nuclear]
    key_attributes: [capacity_factor, lcoe_range, maturity, grid_impact]
```

### Policies

Domain rules and prioritization logic: routing rules, applicability conditions, priority ordering. Encode expert judgment about what matters when.

```yaml
# policies/perspective-routing.yaml
kind: policy
authority: domain-expert-review
version: "2026.1"
status: active
effective_from: "2026-03-29"

rules:
  - id: energy-cost-priority
    condition: "entity.type == 'energy_source'"
    action: "prioritize perspectives: [cost_trajectory, grid_impact, maturity, scalability]"
    priority: 1
    scope: "analysis-intake"         # Which system context this rule applies to
```

### Metadata Fields (definition and policy)

| Field | Required | Values | Description |
|-------|----------|--------|-------------|
| `kind` | Yes | `definition` or `policy` | Document kind |
| `authority` | Yes | Free text | Who established this (e.g., `domain-taxonomy-v1`) |
| `version` | Yes | CalVer or SemVer | Document version |
| `status` | Yes | `active`, `deprecated`, `draft` | Lifecycle status |
| `effective_from` | No | ISO date | When this takes effect |
| `effective_to` | No | ISO date | When this expires (open-ended if omitted) |
| `superseded_by` | No | URI or path | Replacement if deprecated |
| `rationale` | No | Free text | Why this definition/policy exists (deterministic does not mean uncited) |

### Pack-Level Kind Indicator

PACK.yaml declares the pack's primary kind:

```yaml
name: core-taxonomy
kind: definition          # claim (default) | definition | policy | mixed
```

Packs with `kind: claim` (the default, may be omitted) use claims.md as their primary file. Packs with `kind: definition` use `definitions/` as their primary content. Packs with `kind: policy` use `policies/`. Packs with `kind: mixed` contain both ontological and claim content.

**Mixed packs** should be rare. When a pack contains both definitions and claims, the definitions establish local vocabulary and the claims operate within it. Versioning follows the pack's CalVer (not separate definition/claim versions). Validation applies to both layers. Prefer separate packs when the ontological and epistemic content have different change cadences or different audiences.

### Ontology Dependencies

Claim packs that reference entity types, attributes, or relations from a definition pack should declare the dependency in `PACK.yaml`:

```yaml
dependencies:
  - uri: local:../core-taxonomy.kpack
    version: ">=2026.1"
    kind: definition          # Signals this is an ontology dependency
```

The `kind: definition` field on a dependency entry signals that this pack provides vocabulary constraints (not epistemic content). When this dependency is loaded, tooling can validate claims against the ontology. When it's absent, claims remain self-contained — the Voyager Principle is preserved.

**Deprecation handling:** When a definition pack deprecates an entity type, claim packs referencing that type are not invalidated. The claim's `since` date establishes when it was made. Tooling should warn ("entity type `X` deprecated since 2026-06-01") but not reject. Claims are historical assertions — retroactive invalidation by ontology changes would violate the append-only principle (§15, Principle 5).

### Cross-Pack Reference Semantics (Future Work)

Formal namespace resolution, version pinning, and import mechanisms for cross-pack references are deferred to a future spec revision. Until then, the convention is: definition packs declare canonical IDs; claim packs use those IDs as strings; tooling validates the match via the `dependencies` declaration above.

### Codegen Bridge

Definition and policy YAML are designed for domain expert review and AI consumption. For runtime type safety, a codegen step can produce TypeScript types and validation schemas from definition YAML. This pipeline is an implementation concern, not part of the KP:1 spec. See `spec/DEFINITIONS.md` for full schema documentation.

---

## 6. evidence.md — Backing Sources

### Structure

```markdown
# Evidence

## E001
> **type:** multi_source_synthesis | **captured:** 2026-03-01
> **source:** Internal analysis — 10 independent assessments across multiple AI models

Aggregate synthesis across 10 analyses and 8 distinct models. All converged
on cost decline being structural (manufacturing learning curve) rather than
cyclical (subsidy-driven).

## E002
> **type:** research | **captured:** 2026-03-01
> **source:** IRENA Renewable Power Generation Costs 2025

Comprehensive dataset on utility-scale solar PV LCOE trends across 40 countries.
Learning rate of 22% per capacity doubling confirmed across 1976-2025 data.

## E010
> **type:** observed | **captured:** 2026-03-18
> **source:** IEA Photovoltaic Power Systems Programme — Trends Report 2026

Global installed PV capacity figures and market share by technology type.
Bifacial module share crossed 70% in Q4 2025.

## E011
> **type:** observed | **captured:** 2026-03-18
> **source:** Oxford PV press release — certified tandem efficiency record

33.7% certified efficiency for perovskite-silicon tandem cell. Certification
by Fraunhofer ISE CalLab. Commercial module target: 2028.
```

### Evidence Fields

| Field | Required | Values | Description |
|-------|----------|--------|-------------|
| `type` | Yes | Source type string | `document`, `web`, `expert`, `observed`, `research`, `multi_source_synthesis`, `interview`, `measurement`, etc. |
| `captured` | Yes | ISO date | When the evidence was obtained |
| `source` | Yes | Free text | URI, file path, or description of the source |

### Design Principles

- Evidence entries are **referenced by ID** from claims.md — the LLM doesn't need to read evidence.md to reason, only to cite
- Evidence content should be **excerpts and summaries**, not full documents — enough to verify the claim, not to reconstruct the source
- Evidence IDs are **stable** — once assigned, an ID always refers to the same source material
- Evidence descriptions should include enough context for an AI to **assess source reliability** — who provided this, what is their relationship to the claim, and how was it obtained. A CEO's self-reported revenue figure and an independent audit of the same figure have different epistemic weight even if both are `type: expert`

---

## 7. Deprecated: entities.md — Entity Definitions

> **Deprecated as of v0.7.6 (2026-04-28).** New packs MUST NOT emit
> `entities.md`. Use [`extensions.entities`](EXTENSIONS.md#22-extensionsentities--typed-entity-graph)
> for the typed entity graph and [`extensions.relations`](EXTENSIONS.md#23-extensionsrelations--typed-edges)
> for typed edges. The successor surfaces carry stable Nova IDs, an external-ID
> vocabulary suitable for cross-pack resolution, per-claim `entity_refs`, and
> the `relation_types` schema from [DEFINITIONS.md §3](DEFINITIONS.md). A
> one-shot migration script in kp-forge rewrites legacy packs into the new
> shape. Legacy `entities.md` packs continue to validate; the change is
> producer-side guidance, not a validation removal.

The following sections are preserved for legacy reference.

### Structure

```markdown
# Entities

## Utility-Scale Solar PV
> uri: org.irena.solar-pv | type: technology | aliases: solar, PV, photovoltaic

Photovoltaic electricity generation at utility scale (>1 MW). Dominant
renewable energy technology by installed capacity since 2023. Cost decline
driven by silicon manufacturing scale and cell efficiency improvements.

### Relationships
- `competes_with` → [Wind Onshore], [Nuclear]
- `depends_on` → [Polysilicon Supply Chain]
- `measured_by` → [LCOE], [Capacity Factor]

## Perovskite Tandem Cells
> uri: org.example.perovskite-tandem | type: technology | aliases: perovskite, tandem

Emerging PV technology layering perovskite on silicon for higher efficiency.
Lab record 33.7% (Oxford PV). Commercial viability estimated 2028-2030.

### Relationships
- `extends` → [Utility-Scale Solar PV]
- `blocked_by` → [Durability Challenge]
```

### Entity Fields

| Field | Required | Values | Description |
|-------|----------|--------|-------------|
| `uri` | Recommended | Reverse-domain identifier | Disambiguates across packs |
| `type` | Yes | Free text | Entity type (person, product, organization, etc.) |
| `aliases` | No | Comma-separated | Alternative names |

### Entity Resolution Across Packs

When multiple packs are composed:
1. Match on `uri` if present (exact match)
2. Match on `type` + `name` if no URI (same-type, same-name = likely same entity)
3. Flag ambiguous matches as `potential_alias` for human review

---

## 8. Confidence Model

### Canonical Representation

All confidence values in `claims.md` are **normalized floats from 0.0 to 1.0**.

### Native Scale Declaration

`PACK.yaml` declares the native confidence scale. This tells consumers how to interpret the numbers and what human-readable labels to use.

### Built-In Scales

#### Sherman Kent (intelligence analysis)

| Normalized | Native (0-10) | Label |
|------------|---------------|-------|
| 0.99+ | 10 | Certain |
| 0.93-0.99 | 9 | Almost certain |
| 0.87-0.93 | 8 | Highly likely |
| 0.75-0.87 | 7 | Likely |
| 0.63-0.75 | 6 | Probable |
| 0.37-0.63 | 5 | Chances about even |
| 0.25-0.37 | 4 | Probably not |
| 0.13-0.25 | 3 | Unlikely |
| 0.07-0.13 | 2 | Highly unlikely |
| 0.01-0.07 | 1 | Almost certainly not |
| <0.01 | 0 | Impossible |

#### Simple (general purpose)

| Normalized | Label |
|------------|-------|
| 0.90+ | Verified |
| 0.70-0.89 | High confidence |
| 0.50-0.69 | Moderate confidence |
| 0.30-0.49 | Low confidence |
| <0.30 | Unverified |

Custom scales can be declared in `PACK.yaml` via `confidence.scale: custom` with a `confidence.labels` mapping.

---

## 9. Claim Lifecycle

**claims.md contains active claims only.** It is the reasoning surface — what an agent needs to perceive the current epistemic state. Superseded and retracted claims move to `history.md`, which preserves the full audit trail.

Claims are never edited in place — they are superseded by new claims.

### States

| State | Location | Meaning |
|-------|----------|---------|
| Active | claims.md | Current, best-known assertion (default) |
| Disputed | claims.md | Contradicted by another active claim; both remain — the dispute IS the current state |
| Superseded | history.md | Replaced by a newer claim (`supersedes` reference in the replacement) |
| Retracted | history.md | Withdrawn — found to be incorrect |

**Disputed claims** stay in claims.md because both sides of the dispute represent the current epistemic state. Use `⊗!` (error) for disputes where one side is wrong and resolution is needed, or bare `⊗` when unassessed. Patrol should flag `⊗` and `⊗!` disputes older than 90 days without new evidence for review.

**Productive tensions** (`⊗~`) are NOT disputes — they are intentional. Both claims are informative and the disagreement itself is knowledge. Tensions are exempt from the 90-day flag and are skipped by patrol. Use `⊗~` only when you have assessed the contradiction and determined that both sides contribute understanding.

### Supersession

When new evidence changes a fact:

1. The new claim is added to claims.md with a `supersedes` reference
2. The old claim is moved to history.md with its full metadata

```markdown
<!-- In claims.md — the new claim -->
- **[C011-v2]** AI advisor migrated to Qwen 4.0 70B-A5B
  `confidence: 0.99 | type: observed | evidence: E040 | since: 2026-06-15`
  Upgraded from Qwen 3.5 35B-A3B after benchmarking showed 15% improvement
  in conversational quality with minimal cost increase due to larger MoE routing.
  `supersedes: C011`
```

### history.md — Audit Trail

`history.md` preserves every superseded and retracted claim with its original metadata plus context about what happened.

```markdown
# History

## Superseded

### C011 (superseded 2026-06-15 by C011-v2)
- [C011] Perovskite tandem cells: 33.7% lab efficiency (Oxford PV)
  {0.99|o|E011|2026-03-18}
  Lab record for perovskite-silicon tandem. Commercial viability 2028-2030.
  Superseded after LONGi announced 34.2% certified efficiency in June 2026.

## Retracted

### C003 (retracted 2026-04-01)
- [C003] Cost floor approaching — further declines will slow significantly
  {0.85|r|E003|2026-02-14}
  Original framing based on silicon material costs.
  Retracted after perovskite tandem results showed a new cost reduction
  pathway independent of silicon learning curve (see E011).
  Reason: New technology pathway invalidated the cost floor assumption.
```

Each entry preserves: the original claim text, original metadata, and a prose explanation of why it was superseded or retracted. The `since` date in the metadata is the original establishment date; the supersession/retraction date appears in the section header.

---

## 10. validation.yaml — Test Questions (Optional)

```yaml
schema_version: "0.1"

tests:
  - id: V001
    question: "What is driving solar cost decline?"
    expected_claims: [C001, C002]
    expected_keywords: ["structural", "manufacturing", "learning curve"]
    not_expected: ["subsidy", "temporary"]
    difficulty: basic

  - id: V002
    question: "What is the commercialization risk for perovskite cells?"
    expected_claims: [C011, C012]
    expected_keywords: ["durability", "degradation", "warranty"]
    difficulty: reasoning

  - id: V003
    question: "What is the biggest systemic risk to solar deployment?"
    expected_claims: [C030]
    expected_keywords: ["supply chain", "China", "concentration"]
    not_expected: ["technology", "efficiency"]
    difficulty: inference

  - id: V004
    question: "Are solar cost declines slowing down?"
    expected_claims: [C001, C003]
    expected_keywords: ["structural", "learning curve"]
    not_expected: ["yes", "approaching floor"]
    difficulty: reasoning
    note: "Tests whether the LLM correctly prioritizes C001 (0.95) over C003 (0.30)"
```

### Test Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique test identifier |
| `question` | Yes | The question to ask an LLM with the pack loaded |
| `expected_claims` | Yes | Which claims should inform the answer |
| `expected_keywords` | No | Words/phrases the answer should contain |
| `not_expected` | No | Anti-hallucination — words the answer should NOT contain |
| `difficulty` | No | `basic` (retrieval), `reasoning` (synthesis), `inference` (implied) |
| `note` | No | Explanation of what this test validates |

### Automated Extraction Confidence (Multi-Run Calibration)

When Knowledge Packs are generated automatically (via automated extraction or document processing), confidence levels should be empirically calibrated using multi-run extraction rather than relying on the LLM's self-reported confidence.

**Primary intervention: Constrained decoding.** Before voting, use logit-level constrained decoding (e.g., Outlines, SGLang) to a strict claim schema. This compresses the probability space at generation time, crushing non-determinism at the source at 1x cost. Voting is a secondary intervention for when constrained decoding alone doesn't achieve sufficient stability.

**Voting method (when needed):** Run extraction N=3 as a screening pass. If any disagreement, escalate to N=5. If 3-2 split at N=5, preserve both as contradicting claims (genuine ambiguity, not noise). For critical/regulated domains, use N=10+ with proper statistical tests.

**The deterministic contract pipeline (preferred over voting):**
```text
Constrain (logit-level schema) → Canonicalize (normalize) → Validate (deterministic rules) → Escalate (only on failure)
```
This is cheaper (1x inference) and more principled than N=3-5 voting (3-5x inference). Voting becomes a fallback for when validation fails, not the primary strategy.

**Claim comparison:** Use **semantic comparison** (meaning-level consistency), not raw string matching. Two extractions that phrase the same fact differently should count as agreement. Semantic entropy (Kuhn et al., 2024) provides the theoretical basis.

**Theoretical basis:** Baldwin et al. (arXiv:2408.04667v5, 2025) demonstrate that LLMs at temperature=0 produce up to 15% accuracy variation across identical runs, with multi-step systems compounding to ~77% stability over 5 steps. Non-determinism as a confidence signal: if the model can't agree with itself, it's telling you something about extraction difficulty.

**Key caveats (from five-model analysis of Baldwin paper):**
- Agreement is a **routing signal**, not a **truth signal** — models can be stably wrong ("confident idiot" problem)
- High agreement does NOT guarantee correctness when: input is ambiguous, evidence is incomplete, schema nudges a canonical-but-wrong answer, or error is an omission rather than a contradiction
- Calibration against labeled data (200+ examples) is a prerequisite before deploying agreement-as-confidence in production
- Track the **stable-wrong rate**: proportion of wrong outputs with high cross-run agreement — this is the failure mode that can't be detected by agreement alone
- Temperature is task-dependent: **T=0 to T=0.1 for claim extraction** (factual recall — higher T increases hallucination risk); **T=0.3-0.5 for narrative generation** from verified claims (diversity in expression is acceptable when facts are locked); **T=0.4 for reasoning** over claims (standard self-consistency range)
- Structured atomic claims are inherently more stable than narrative outputs (shorter outputs = higher agreement, paper's ρ = -0.64) AND more factual (Google long-form factuality study: factuality degrades with output length)
- **Hallucination is mathematically inevitable** (Liu et al. 2025, formal proof). Knowledge Packs do not eliminate hallucination — they make it detectable and traceable through confidence levels, evidence chains, and contradiction tracking. Design for tolerance, not elimination

### Cross-Claim Consistency Validation

Beyond question-answer testing, `kpack validate` should run an LLM over the full claims.md to detect:
- **Arithmetic inconsistencies** (e.g., raise amount / burn rate ≠ stated runway)
- **Logical contradictions** not explicitly marked with `⊗`
- **Temporal impossibilities** (claim dated before its evidence)
- **Confidence/evidence mismatches** (high confidence with weak evidence, or low confidence with strong evidence)

This was validated empirically: in blind testing of a fundraise knowledge pack, an independent AI model caught a runway calculation error ($2.5M raise / $120K burn ≠ stated runway) that the pack author hadn't flagged.

### Harm-Weighted Validation

For regulated or high-stakes domains, not all errors are equal. A false claim is far more damaging than a missing claim (especially for legal, financial, or medical knowledge). Validation should support harm-weighted metrics:

```yaml
# In validation.yaml
harm_weights:
  false_claim: 10          # A wrong claim actively misleads
  missing_claim: 1          # An omission is incomplete, not dangerous
  wrong_confidence: 3       # Overstated confidence erodes trust
  broken_evidence: 5        # Unsupported claim looks verified
```

The `kpack validate` tool should report harm-weighted error scores alongside standard precision/recall.

---

## 11. Sizing & Hierarchy

### Context Budget

A Knowledge Pack's claims.md must fit within a practical LLM context budget alongside system prompts, conversation history, and other context. The format enforces this through recommended size tiers, not hard limits.

### Size Tiers

| Tier | Claims | Token Budget | When to use |
|------|--------|-------------|-------------|
| **Hub** | 10-20 | 2-4K tokens | Always loaded. Executive-level understanding of a domain. |
| **Detail** | 20-40 | 4-8K tokens | Loaded on demand when conversation goes deep on a specific facet. |
| **Standalone** | 15-30 | 3-6K tokens | Self-contained pack for a single, bounded topic. |

### The Split Rule

**If claims.md exceeds ~40 claims or ~8K tokens, split the pack.**

Ask: "What claims give an agent the framework to correctly interpret everything in the detail packs?" That's the hub. A good hub includes the domain thesis, key unresolved tensions, and the confidence landscape — not just the most important facts, but the interpretive context that makes the facts meaningful. Everything else becomes detail packs.

### Pack Hierarchy

Large domains are organized as a hub pack with detail packs:

```text
solar-energy-market.kpack/              # Hub — always loaded
├── PACK.yaml                          # tier: hub, declares sub_packs
├── claims.md                          # ~15 claims: thesis, market state, cost trends, outlook
└── evidence.md

solar-technology.kpack/                 # Detail — loaded on demand
├── PACK.yaml                         # tier: detail, dependency: solar-energy-market.kpack
├── claims.md                         # ~25 claims: PV efficiency, perovskite, manufacturing
└── evidence.md

solar-policy.kpack/                     # Detail — loaded on demand
├── PACK.yaml                         # tier: detail, dependency: solar-energy-market.kpack
├── claims.md                         # ~20 claims: tariffs, subsidies, permitting, grid access
└── evidence.md

solar-deployment-risks.kpack/           # Detail — loaded on demand
├── PACK.yaml                         # tier: detail, dependency: solar-energy-market.kpack
├── claims.md                         # ~15 claims: supply chain, grid capacity, financing
└── evidence.md
```

### Hub Pack PACK.yaml

```yaml
name: solar-energy-market
version: 2026.03.18
domain: energy/market-analysis
tier: hub

sub_packs:
  - name: solar-technology
    uri: local:../solar-technology.kpack
    summary: "PV efficiency, perovskite advances, manufacturing trends, module costs"
    load_when: "questions about technology, panels, efficiency, manufacturing"

  - name: solar-policy
    uri: local:../solar-policy.kpack
    summary: "Tariffs, subsidies, permitting timelines, grid access regulations"
    load_when: "questions about policy, regulation, tariffs, incentives"

  - name: solar-deployment-risks
    uri: local:../solar-deployment-risks.kpack
    summary: "Supply chain concentration, grid capacity, financing gaps, labor shortages"
    load_when: "questions about risks, supply chain, deployment barriers"
```

The `load_when` field is a natural language hint — it helps the consuming system (or the LLM itself) decide when to pull in a detail pack.

### Progressive Loading

The loading model applies at every level, with views as a separate display channel:

| Level | Always loaded | Loaded on demand | Loaded for display |
|-------|---------------|------------------|--------------------|
| Within a pack | claims.md | evidence.md, entities.md | views/*.md |
| Across packs | Hub pack | Detail packs | Views from relevant pack |
| Across domains | KNOWLEDGE.yaml index | Relevant packs by topic | Views from selected pack |

Views are loaded when the AI needs to **show** content to a human, not when it needs to **reason** about it. This keeps reasoning context lean while enabling rich display.

---

## 12. Navigation

Knowledge Packs are most powerful when connected. Navigation operates at three layers.

### Layer 1: Root Index — KNOWLEDGE.yaml

A `KNOWLEDGE.yaml` file at the root of a knowledge collection serves as the sitemap — discovery and routing for every pack in the ecosystem.

```yaml
# KNOWLEDGE.yaml
name: energy-research
description: Complete knowledge ecosystem for energy market research
updated: 2026-03-18

packs:
  # ── Solar Cluster ──
  - name: solar-energy-market
    path: solar-energy-market.kpack/
    tier: hub
    summary: "Utility-scale solar market trends, costs, and adoption"
    topics: [solar, PV, market, cost, adoption]

  - name: solar-technology
    path: solar-technology.kpack/
    tier: detail
    parent: solar-energy-market
    summary: "Panel types, efficiency trends, emerging technologies"
    topics: [technology, perovskite, bifacial, efficiency, manufacturing]

  - name: solar-policy
    path: solar-policy.kpack/
    tier: detail
    parent: solar-energy-market
    summary: "IRA incentives, tariffs, trade policy, grid regulations"
    topics: [policy, IRA, tariffs, grid, regulation]

  # ── Wind Cluster ──
  - name: wind-energy-market
    path: wind-energy-market.kpack/
    tier: standalone
    summary: "Onshore and offshore wind — costs, capacity, outlook"
    topics: [wind, onshore, offshore, turbine, market]

  - name: battery-storage-economics
    path: battery-storage-economics.kpack/
    tier: hub
    summary: "Storage cost trajectories, chemistry, deployment economics"
    topics: [battery, storage, lithium, deployment, cost]
```

An LLM reading this index knows every available knowledge pack, organized by cluster, with topic tags for routing. When someone asks about tariffs, the `topics` field routes to `solar-policy`. When someone asks about storage, it routes to `battery-storage-economics`.

The index is lightweight enough to be always available — it's metadata, not content.

### Layer 2: Hub → Detail — sub_packs

Declared in the hub's `PACK.yaml` (see §11). The hub knows its children and provides `load_when` hints for contextual loading.

### Layer 3: Inline Cross-References — `↔`

Within claims.md, individual claims can point to other packs using the `↔` symbol:

```markdown
- [C011] Perovskite tandem cells: 33.7% lab efficiency (Oxford PV)
  {0.99|o|E011|2026-03-18} Commercial viability estimated 2028-2030.
  →C012 ↔solar-technology.kpack#perovskite ↔solar-policy.kpack#manufacturing
```

The `↔` symbol uses the format `↔{pack_name}#{section}`, where `#{section}` references a `## heading` in the target pack's claims.md. This acts as a hyperlink — the LLM knows where to go for more depth.

### Navigation in Practice

A conversation flow using navigation:

1. **Session start.** System loads `KNOWLEDGE.yaml`. LLM sees all available packs.
2. **Topic identified.** User says "tell me about solar energy costs." System loads `solar-energy-market.kpack/claims.md` (hub).
3. **Depth needed.** User asks "explain the perovskite opportunity." LLM sees `see_also: solar-technology.kpack#perovskite` on C011 and the hub's `sub_packs` entry. System loads the detail pack.
4. **Cross-domain.** User asks "how does this compare to wind?" LLM sees `wind-energy-market` in the root index, system loads it.
5. **Total context.** Hub (3K) + one detail pack (6K) + standalone pack (4K) = ~13K tokens of structured, relevant, navigable knowledge. Not a megabyte of raw documents.

---

## 13. Tooling

### MVP Commands

```bash
kpack lint [path]              # Validate structure and references
kpack test [path]              # Run validation.yaml against an LLM
kpack export [path] --format   # Export to JSONL, JSON, or other formats
kpack render [path]            # Generate/regenerate views from claims
kpack render [path] --view X   # Regenerate a specific view
```

### Extended Commands

```bash
# Pack creation
kpack new [name]                       # Create new pack (interactive)
kpack new --template meeting-prep [name]  # Create from template

# Bundle & sharing (see spec/BUNDLE.md)
kpack bundle [path]                    # Full bundle → stdout
kpack bundle [path] --clip             # Clipboard format → clipboard
kpack bundle [path] --url              # Shareable URL (if published)

# Lifecycle & archival (see spec/LIFECYCLE.md)
kpack archive --dry-run                # Preview what would be archived
kpack archive                          # Archive ephemeral packs past retention
kpack reconcile [path]                 # Check claims against standing packs

# Seal & transport (see spec/ARCHIVE.md)
kpack seal [path] -o [dir]             # Seal pack directory → .kpack ZIP with signatures.yaml
kpack verify [path]                    # Verify archive integrity (hash + signature + ZIP safety)
kpack verify --chain v1 v2 v3          # Verify version chain integrity
kpack extract [archive] -o [dir]       # Extract archive → pack directory
kpack info [archive]                   # Show archive metadata without extracting

# Multilingual (see spec/MULTILINGUAL.md)
kpack translate [path] --locale uk-UA  # Generate translated views
kpack translate --check [path]         # Report stale translations

# Consistency (see spec/CONSISTENCY.md)
kpack patrol [path]                    # Run cross-pack consistency checks
kpack validate [path]                  # Full validation suite
```

### Lint Checks

- PACK.yaml has all required fields and is valid YAML
- Every claim has a unique ID matching pattern `[C{id}]`
- Every claim has confidence in range 0.0-1.0
- Every claim has at least one evidence reference
- Every evidence reference in claims.md has a corresponding entry in evidence.md
- Supersession chains are valid (referenced claims exist)
- No circular supersession
- Relation targets exist
- Cross-references in `see_also` point to existing packs and sections
- Hub packs have `sub_packs` declared
- KNOWLEDGE.yaml paths resolve to existing pack directories
- Dependency graph is acyclic (no circular references between packs)
- Dependencies use exact version pins (no "latest" or floating versions)
- Evidence provenance chains do not form cycles across packs
- Warning: claims with confidence >0.90 citing only self-authored evidence
- Views declared in PACK.yaml exist as files in views/
- View source comments (`<!-- source: C001 -->`) reference existing claims
- View generation timestamps are not older than claims.md modification date (staleness warning)
- Warning: view exceeding 80 lines (split signal — see §16 View Sizing)
- Warning: only 1 view for a pack with >15 claims (likely needs decomposition)
- Warning: overview view exceeding 35 lines (should be a router, not a summary)
- Channels array contains no duplicates and only lowercase strings
- Bare channel names are in spec vocabulary (`team`, `org`, `public`) — unknown bare names warn
- Custom channels use `namespace/name` format
- Channels respect sensitivity constraints (§3.1): no `public` on `confidential` packs

### Export Formats

| Format | Use Case |
|--------|----------|
| `jsonl` | Database import (one record per line) |
| `json` | API consumption (single structured document) |
| `summary` | Human-readable summary (claims without metadata) |

---

## 14. Composition

### Loading Multiple Packs

When a system loads multiple Knowledge Packs:

1. **Entity resolution** — Match entities across packs by URI (exact), then type+name (fuzzy)
2. **Claim merging** — Claims from all packs are available. Same-entity, same-predicate claims from different packs coexist.
3. **Conflict surfacing** — If claims contradict (different values for same entity+predicate), the contradiction is made visible to the LLM, not hidden.
4. **Confidence ordering** — When the LLM must choose, higher-confidence claims are preferred. But both are available for reasoning.

### Dependency Resolution

Packs declare dependencies in `PACK.yaml`. The consuming system is responsible for ensuring dependencies are available. If a required pack is missing, the system should warn but not fail — graceful degradation.

---

## 15. Design Principles

1. **The Voyager Principle** — Zero dependencies beyond "a device that can process text." No internet, no registry, no parser. The files are the knowledge.
2. **Inspectability over readability** — Optimized for AI consumption. Humans CAN inspect (it's plain text), but format favors density over reading comfort.
3. **Density-optimized plain text** — Maximum knowledge per token. Compressed metadata `{0.95|i|E001|2026-03-01}`, symbolic relations `→⊗←`, minimal prose.
4. **Contradictions are knowledge** — Disagreements between claims are surfaced, not resolved. Resolution is context-dependent.
5. **Append-only** — Claims are superseded (`⊘`), not edited. The past is preserved.
6. **Freeform with conventions** — Predicates, entity types, and sections are freeform. Vocabulary overlays are optional.
7. **Claims file is self-contained** — An LLM reading only claims.md can reason about the domain. Evidence and entities are supporting.
8. **Git-native** — Files, directories, diffs, PRs. No special infrastructure required.
9. **Any LLM, any system** — Portable by default. No platform lock-in. From a 7B local model to a frontier model.
10. **Progressive loading** — Hub always loaded, detail on demand, evidence on citation. Never dump everything into context.
11. **Navigable** — Every pack knows what's adjacent. Root index (`KNOWLEDGE.yaml`) for discovery, hub `sub_packs` for structure, inline `↔` for depth.
12. **Constitutional core** — The claim syntax (`- [ID] headline {metadata} prose`), confidence range (0-1), evidence references (`E` + id), relation symbols (`→⊗←~⊘↔`), and Rosetta Header (`<!-- KP:N`) are frozen across ALL spec versions. Everything else may evolve.
13. **Don't over-atomize** — Claims need enough context to prevent semantically valid but context-wrong extractions. Not every domain benefits from decomposition. A claim should be the smallest unit that is independently falsifiable — no smaller (Hu et al., Decomposition Dilemmas, NAACL 2025).
14. **Hallucination tolerance, not elimination** — Hallucination is mathematically inevitable even for optimal estimators (Liu et al. 2025). Knowledge Packs make hallucination detectable and traceable through confidence, evidence, and contradictions. They do not make it impossible.
15. **Constrain before voting** — Logit-level constrained decoding (1x cost) is the primary stability intervention. Multi-run voting (3-5x cost) is a fallback. The deterministic contract pipeline: constrain → canonicalize → validate → escalate.
16. **Three surfaces, one truth** — Claims.md is the reasoning surface (AI-optimized). Display views are the visual surface (human-reading-optimized). Voice views are the auditory surface (human-listening-optimized). All represent the same knowledge. Views are derived from claims, never authoritative. If they disagree, claims win.
17. **Renderer, not compositor** — When the AI presents knowledge to humans, it should render pre-built views, not compose content on the fly. This is faster, more consistent, and separates the reasoning task (understanding) from the presentation task (showing).
18. **Composition over duplication** — Meeting and composite packs reference standing packs rather than duplicating their knowledge. A meeting pack is a lens — an agenda-shaped view over existing packs with meeting-specific additions. Knowledge lives once, in its canonical pack. Every piece of knowledge has exactly one canonical home — the standing pack where it is authored and maintained. Other packs may reference via see_also links or render content via composition. A pitch pack or meeting pack that independently re-defines a concept owned by a standing pack is a duplication violation. Test: if the standing pack's claim changes, do all other appearances automatically reflect it? If not, the knowledge is duplicated.
19. **Archive, never delete** — Packs are archived, not deleted. Archived packs remain searchable, loadable, and in git history. Archival is the default lifecycle outcome for ephemeral packs; deletion requires explicit, deliberate action.
20. **One view, one question** — Each display view answers one question a human would ask. The overview is a router (what, why, where-to-go), not a summary of everything. Split on meaning, never on arbitrary line counts. A view exceeding 80 lines almost always needs splitting; a view under 10 lines almost always needs merging. (Shneiderman: overview first, then details on demand.)
21. **Reconcile before archive** — Ephemeral packs (meetings, conversations) contain knowledge that may not exist elsewhere. Before archiving, an intelligent reconciliation step verifies that all valuable claims have been promoted to standing packs. Orphan claims are flagged, never silently lost.
22. **Knowledge is the source (pack-as-master)** — Knowledge packs are the canonical source of truth for their epistemic contents. Agent instruction files, operations (planning, tasks), and presentations (slides, documents) reference knowledge packs but are not knowledge themselves. Databases, caches, and search indices that store or project pack data are derived representations — operational infrastructure that serves packs, not the other way around. When a derived representation disagrees with the pack, the pack is correct. Any index can be dropped and rebuilt from packs. Packs can be stored in any medium (files, databases, caches) without changing their authority. Only knowledge is a knowledge pack. (See `spec/STORAGE.md`.)
23. **Locale first, then surface** — Multilingual views are organized by locale, then by surface type: `views/uk/voice/briefing.md`, not `views/voice/uk/briefing.md`. Locale is the higher-order grouping.
24. **Knowledge, not journal** — Claims state what is believed and why. Views render what something IS. Neither describes the process of arriving at the knowledge: who commissioned a finding, which meeting crystallized an insight, which tool generated a draft, which framework was applied. Process provenance belongs in evidence.md (as source documentation) or nowhere. A claim's confidence and evidence links carry its epistemic provenance. Narrative provenance ("a stakeholder asked for this", "crystallized during the Q1 review session", "generated by an LLM") leaks operational history into canonical knowledge. Test: remove all proper nouns of people, meetings, tools, and session dates from a claim's context prose — if the epistemic content is intact, the claim is clean.
25. **Short-term memory, long-term memory** — Standing packs (permanent, seasonal) are long-term memory: organized by semantic domain, where things that are *about* the same subject cluster together regardless of when or how they were learned. Ephemeral packs are short-term memory: organized by *proximity of need*, where things needed together in a specific moment cluster together regardless of domain. These are different cognitive architectures serving different purposes — both legitimate, but with different lifespans. Novel knowledge created during short-term operations (meeting prep, research sprints) must consolidate into its long-term semantic home before the ephemeral pack archives. The ephemeral pack is the scaffold, not the building. Consolidation is not a safety net before archival — it is the primary purpose of the ephemeral lifecycle. (See `spec/LIFECYCLE.md` §1.1.)

---

## 16. Views — Pre-Rendered Display Content

### Purpose

Views are pre-rendered markdown documents designed for **human visual consumption**. While claims.md is optimized for AI reasoning (dense, compressed, navigable), views are optimized for human perception (readable, formatted, displayable on Canvas or screen).

### The Three-Surface Architecture

| Surface | File | Audience | Optimization | When loaded |
|---------|------|----------|--------------|-------------|
| Reasoning | claims.md | AI/LLM | Max knowledge per token | Always — for thinking |
| Display | views/*.md | Humans (visual) | Max comprehension per glance | On demand — for showing |
| Voice | views/voice/*.md | Humans (auditory) | Max clarity per spoken sentence | On demand — for speaking |

An AI assistant loading a Knowledge Pack uses claims.md to become knowledgeable about the domain. When it needs to *show* information to a human — on Canvas, in a UI panel, as a formatted response — it renders a pre-built display view. When it needs to *speak* information — in a voice conversation, as a briefing — it renders a pre-built voice view. Neither surface is composed on the fly from claims.

Voice views differ from display views in fundamental ways: shorter sentences (10-15 words), no tables or complex formatting, numbers spelled out, pronunciation hints for proper nouns, pause markers for pacing. See `spec/VOICE.md` for the full voice view specification.

This separation means:
- **Faster display** — No inference tokens spent on formatting
- **Consistent rendering** — Same view looks the same every time
- **Traceable content** — Every view statement traces back to a claim
- **Independent evolution** — Claims can be dense; views can be beautiful

### View File Format

Each view is a standard GFM (GitHub-Flavored Markdown) document. Views MAY include:

1. **Source traceability comments** — HTML comments linking content back to claims:
   ```markdown
   <!-- source: C001, C002 -->
   ```

2. **Generation metadata** — When and from what version the view was generated:
   ```markdown
   <!-- generated: 2026-03-21 | claims: v2026.03.21 | style: default -->
   ```

3. **Semantic markers** — Optional hints that a style system interprets:
   ```markdown
   > [!metric] Grid parity achieved in 75% of global markets
   > [!highlight] 22% learning rate sustained over 40 years
   > [!risk] Supply chain: 80% polysilicon concentrated in one country
   > [!status] Q1 2026 — bifacial modules reach 70% market share
   ```
   Without a style system, markers render as standard blockquotes — graceful degradation.

### PACK.yaml Declaration

```yaml
views:
  - name: overview
    file: views/overview.md
    purpose: "Router — what it is, why it matters, map to detail views"
    display_as: "Overview"           # UI label (tab name, section header)
    hint: "What this is, key takeaways, and where to go next"

  - name: architecture
    file: views/architecture.md
    purpose: "Technical stack, package structure, key design decisions"
    display_as: "Architecture"
    hint: "Panel types, efficiency curves, manufacturing trends"

  - name: market
    file: views/market.md
    purpose: "Regional adoption, market sizing, growth projections"
    display_as: "Market"
    hint: "Key markets by installed capacity and growth rate"

  - name: risks
    file: views/risks.md
    purpose: "Supply chain, policy, and technology risk assessment"
    display_as: "Risks"
    hint: "Three systemic risks to global solar deployment"
```

The `purpose` field tells the AI **when** to display this view. The `display_as` field provides the **label** for UI navigation (tabs, menus, section headers). The `hint` field helps a human **decide** whether to open this view (see §18).

### View Content Rules

1. **Markdown only** — Standard GFM: tables, headings, blockquotes, lists, code blocks. No HTML beyond traceability comments.
2. **Derived from claims** — Views contain no knowledge that isn't in claims.md. If a view states a fact, a corresponding claim exists. Source comments make this traceable.
3. **Self-contained** — Each view is independently displayable. No cross-view dependencies (a user can see "Overview" without having seen "Architecture").
4. **Consistent structure** — Views within the same style system use consistent formatting: same table styles, same heading hierarchy, same callout patterns.
5. **No claim notation** — Views contain readable prose and formatted data, not `{0.95|i|E001}` compressed metadata. The whole point is human readability.
6. **One view, one question** — Each view should answer one question a human would ask. If you cannot title the view as a clear question or noun phrase ("How does it work?", "Architecture", "Risks"), it is underspecified. If a view answers multiple distinct questions, split it.
7. **Inverted pyramid** — Lead with the answer, then supporting explanation, then nuance. A reader who stops after the first paragraph should still get the main point.

### View Sizing & Decomposition

Views exist to be browsed, not scrolled. A view that requires excessive scrolling or contains the entire pack's knowledge has failed its purpose — it is a claims.md with better formatting, not a display surface. The guidance below ensures views serve human perception at Canvas/screen scale.

#### The Governing Principle: Progressive Disclosure

> "Overview first, zoom and filter, then details-on-demand."
> — Shneiderman (1996)

A human encountering a pack should:
1. See the **overview** — understand what this is and why it matters (30-60 seconds)
2. **Choose** a detail view — based on clear labels and hints (< 10 seconds)
3. **Read** the detail — get a focused, complete answer to one question (1-3 minutes)

The overview is a **router**, not a summary of everything. It orients the reader and maps the territory. Detail views are the territory.

#### Size Guidelines

| View type | Target lines | Target words | Reading time | When to use |
|-----------|-------------|-------------|--------------|-------------|
| Overview (router) | 15-35 | 75-180 | 30-60 sec | Every pack — the entry point |
| Compact detail | 15-35 | 150-250 | 1-2 min | Focused facet, single entity, narrow question |
| Standard detail | 35-60 | 250-400 | 2-3 min | Most detail views — one topic, well-structured |
| Heavy detail | 60-80 | 400-600 | 3-4 min | Evidence-dense views with tables, only when strongly structured |

**Split signal:** A view exceeding **80 lines** or **600 words** should almost always be split.

**Merge signal:** A view under **10 lines** that cannot stand alone should be merged into a related view.

These are authoring heuristics, not hard limits. A 90-line view with excellent structure (tables, clear headings, scannable bullets) may be fine. A 50-line wall of prose is worse than a 90-line well-structured view. Structure determines whether length works.

Within views, body text should stay around **50-75 characters per line** for readability. WCAG 2.2 (SC 1.4.8) sets the accessibility ceiling at 80 characters.

#### View Count Guidance

| Pack claims | Too few views | Sweet spot | Needs grouping | Too many |
|-------------|--------------|------------|----------------|----------|
| 10-20 | 1-2 | 3-5 | — | 8+ |
| 20-40 | 1-3 | 5-9 | 10-12 | 13+ |
| 40+ | 1-4 | 6-10 | 11-15 | 16+ |

**Heuristic:** Aim for roughly **4-8 claims per detail view**. The overview references all claims but contains none of them in full — it states conclusions, not evidence.

Beyond **~12 sibling views**, introduce grouping or a two-level hierarchy (view folders, section prefixes) rather than a flat list. Navigating a flat menu of 15+ items exceeds working memory (Cowan, 2001: ~4 chunks).

#### The Overview View

The overview is the most important view and the most commonly miswritten. An overview that contains all the pack's knowledge is not an overview — it is the pack reformatted. A good overview does exactly four things:

1. **Says what it is** — One sentence identifying the subject (not the pack format)
2. **Says why it matters now** — The hook, the urgency, the "so what?"
3. **Surfaces 3-5 key takeaways** — The 20% of information that 80% of readers need
4. **Maps the pack** — What other views exist and what you'll find in each

An overview should be readable in **under 60 seconds**. If someone reads only the overview and nothing else, they should leave knowing what this is, why it matters, and where to go next.

**What the overview must NOT do:**
- Restate every claim in prose form (that's what detail views are for)
- Include detailed evidence, methodology, or technical specifications
- Contain sections that could be their own views
- Exceed 35 lines

#### Decomposition Principles

When splitting a pack into views, apply these principles in order of preference. Choose the one that best matches how a human would naturally browse the content:

| Principle | Best for | Example |
|-----------|----------|---------|
| **By question answered** | Most packs (default) | "What is it?", "How does it work?", "Who is it for?" |
| **By entity / actor** | Personas, team, portfolio packs | One view per persona, per team member, per asset |
| **By abstraction level** | Research, decision, technical packs | Overview → thesis → evidence → provenance |
| **By workflow step** | Process, operational, meeting prep packs | Phase 1 → Phase 2 → Phase 3 |
| **By time slice** | Roadmap, history, timeline packs | Now → Next → Later |
| **By audience** | Only when framing truly changes | Use sparingly — often creates duplication |

**"By question answered" is the default.** If you're unsure which principle to use, structure each view as the answer to a question a reader would ask. This works for almost every domain.

**Avoid arbitrary pagination.** Never split on a fixed line count ("every 40 lines"). Split on meaning — a natural boundary where the question changes.

#### Default View Template

For a typical detail pack (20-40 claims), this decomposition works as a starting point:

```text
views/
├── overview.md              # What it is, why it matters, view map (15-35 lines)
├── [core-thesis].md         # The main story or positioning (35-60 lines)
├── [how-it-works].md        # Architecture, process, mechanics (35-60 lines)
├── [who-or-what].md         # Entities, personas, segments, market (35-60 lines)
├── [risks-or-unknowns].md   # Counterevidence, gaps, tensions (25-50 lines)
└── [state-or-next].md       # Current status, timeline, next actions (25-50 lines)
```

The bracketed names are placeholders — use domain-appropriate names. Not every pack needs all six. Some need more. The principle is: **each file answers one question**.

#### When to Split a View

Split when any of these are true:
- The first screen does not tell the reader if they're in the right place
- The view answers more than one distinct question
- Headings within the view could each stand alone as separate screens
- The reader must scroll significantly before reaching the key point
- The view exceeds 80 lines

#### When to Merge Views

Merge when any of these are true:
- View titles are hard to distinguish from each other
- Readers would almost always read both views together
- A view is too short (< 10 lines) to provide standalone value

#### Cross-View Claim References

A claim may be relevant to multiple views. The overview references many claims at summary level; detail views reference them in full. This is not duplication — it is progressive disclosure. The same claim appears as a one-line takeaway in the overview and as a paragraph with context in the detail view. Source comments (`<!-- source: C001, C002 -->`) track the mapping.

#### Deep Links and Self-Containment

A reader may arrive at any view directly (via search, deep link, or voice navigation). Every view — not just the overview — must include a brief framing sentence at the top that answers: "what pack is this from, and what question does this view answer?" This is implicit in the `<!-- generated: ... -->` metadata and the view's H1, but the first paragraph of prose should also orient a cold reader.

### View Generation

Views can be created three ways:

1. **Hand-authored** — Written by a human for maximum editorial quality
2. **AI-generated** — `kpack render` uses an LLM to generate views from claims
3. **Hybrid** — AI generates a first draft; human refines

The `kpack render` command:
```bash
kpack render my-project.kpack/                    # Generate all declared views
kpack render my-project.kpack/ --view overview     # Generate a specific view
kpack render my-project.kpack/ --style my-style  # Apply style system
kpack render my-project.kpack/ --check             # Report stale views (claims newer than views)
```

### View Staleness

When claims.md is updated, views may become stale (they reflect old facts). The generation comment tracks this:

```markdown
<!-- generated: 2026-03-21 | claims: v2026.03.21 -->
```

`kpack lint` compares the view's `claims:` version against the current claims.md version. If they differ, it emits a staleness warning — not an error, since views may intentionally lag (e.g., during active editing of claims).

### Views for Collections (Address Book Pattern)

For packs that represent collections (registries, portfolios, contact books), views can include:

- **Collection overview** — Summary of the entire collection (count, categories, health)
- **Entity cards** — Individual views per entity or entity group
- **Analytics** — Aggregate views (distribution, trends, comparisons)

The pack's `entities.md` defines the records; views present them for human consumption. Example:

```text
asset-registry.kpack/
├── claims.md                    # Claims about the collection itself
├── entities.md                  # Entity definitions (the "contacts")
└── views/
    ├── overview.md              # Collection summary
    ├── by-category.md           # Entities grouped by type
    └── highlights.md            # Featured entities with detail
```

When individual entities have enough depth, they warrant their own packs (the hub → detail pattern applied to entities).

---

## 17. Style Systems — Visual Rendering Rules

### Purpose

A style system is an external, versioned specification that tells a renderer how to visually present view content. Style systems are **NOT** part of the Knowledge Pack — they are referenced by packs and defined externally.

### Why External

- **Separation of concerns** — Knowledge is stable; presentation evolves independently
- **Reusability** — One style system serves many packs across a product
- **Voyager Principle preserved** — Packs work without a style system (markdown is self-rendering)
- **Brand consistency** — All packs in a product share visual identity

### PACK.yaml Reference

```yaml
style: acme-professional          # Style system identifier
```

A `null` or omitted `style` field means the views render as plain markdown — which is always valid.

### Style System Contents

A style system defines:

| Component | Purpose | Example |
|-----------|---------|---------|
| Semantic markers | What `> [!metric]` etc. mean visually | Green badge with large number |
| Table formatting | Column alignment, header styles | Zebra-striped, right-aligned numbers |
| Typography | Heading hierarchy, emphasis | H1 for title, H2 for sections, bold for key terms |
| Color semantics | What colors mean in context | Green = confirmed, amber = tentative, red = disputed |
| Layout patterns | Structural arrangements | Card grid, sidebar + main, timeline |
| Confidence rendering | How to display confidence levels | Color-coded bars, Sherman Kent labels |

### The Rendering Stack

```text
claims.md  →  views/*.md  →  style system  →  rendered output
(knowledge)   (content)      (presentation)   (platform-specific)
```

Each layer can exist independently:
- Claims without views = AI can reason, can't display pre-built content
- Views without style = renders as clean markdown (always works)
- Views with style = renders with visual richness and consistency

### Style System Format (Recommended)

Style systems are defined as YAML files:

```yaml
# STYLE.yaml
name: acme-professional
version: 2026.03.21
description: "Professional style system — data-rich, confidence-aware, clean typography"

markers:
  metric:
    render: "highlighted-badge"
    description: "Key metric — prominent display with large value"
  highlight:
    render: "callout-primary"
    description: "Important insight — visually distinct callout"
  risk:
    render: "callout-warning"
    description: "Risk indicator — amber/red callout"
  status:
    render: "status-pill"
    description: "Current state — compact status indicator"
  source:
    render: "attribution-subtle"
    description: "Source attribution — small, muted text"

confidence:
  display: "bar"                      # bar | label | badge | none
  colors:
    high: "#22c55e"                   # 0.85+
    medium: "#f59e0b"                 # 0.50-0.84
    low: "#ef4444"                    # <0.50

tables:
  header: "bold"
  alignment: "auto"                   # auto-detect from content
  numbers: "right-aligned"

typography:
  h1: "Pack title — large, bold"
  h2: "Section — medium, with subtle divider"
  h3: "Subsection — small caps or bold"
```

### Platform-Specific Renderers

The style system is platform-neutral. Renderers interpret it for specific targets:

| Renderer | Output |
|----------|--------|
| Canvas (OpenAI) | Rendered markdown with formatting hints |
| HTML | CSS-styled web page |
| PDF | Formatted document via reportlab/Typst |
| Terminal | ANSI-colored markdown |
| Slack | Slack-formatted blocks |

The renderer is NOT part of the Knowledge Pack spec — it's part of the consuming platform. The style system bridges the gap between platform-neutral views and platform-specific rendering.

---

## 18. Cognitive Perception Layer

Knowledge Packs serve three surfaces: reasoning (AI), display (visual), and voice (spoken). The reasoning surface is dense and optimized for inference. The display and voice surfaces are optimized for human perception.

### The Primary Constraint: Cognitive Load

**Cognitive load is the first and most important criterion for all human-facing fields.** Not aesthetics, not completeness, not technical accuracy — cognitive load. Every field that a human will see must be authored for someone who:

- Has never seen this pack before
- Has 5 seconds of attention
- Does not know the domain jargon
- Will leave immediately if they don't understand what they're looking at

This means: no abbreviations that require context, no category labels that require domain knowledge, no technical metrics that require interpretation. Every human-facing field must be **self-explanatory at first read**.

The reasoning surface (claims.md) is exempt — it optimizes for AI inference, not human perception. But the display surface, voice surface, and all `display` block fields must pass the cognitive load test: **would a stranger understand this in one reading?**

This is the hardest part of building a Knowledge Pack. The underlying knowledge is expert-level. The display surface must be beginner-level. That translation — from expert knowledge to cognitively accessible language — is the core value of the cognitive perception layer. It is not a formatting step. It is an authoring act.

### Perception Stages

A human encountering a Knowledge Pack progresses through four stages. Each stage has a time budget. If the pack fails at any stage, the human disengages.

1. **Recognize** (< 1 second) — What is this? Can I identify it in a list, on a tab, in a breadcrumb?
2. **Comprehend** (< 3 seconds) — What is it about? What does it address?
3. **Engage** (< 5 seconds) — Why should I care? What makes me want to read further?
4. **Navigate** (< 10 seconds) — Which section should I open? What will I find there?

These are cognitive requirements, not aesthetic choices. They hold regardless of whether the pack is rendered as a web page, a mobile card, a terminal table, a TV dashboard, or a PDF cover page. The fields below provide the structured metadata that any renderer needs to support human perception at each stage.

### Manifest: `display` Block

The `display` block sits at the pack level in PACK.yaml. All fields are OPTIONAL. When absent, renderers fall back to parsing the overview view's markdown (H1 for title, first blockquote for tagline). Pre-articulated fields are always preferred over parsed fallbacks — they represent **authored intent**, not extracted approximation.

```yaml
display:
  short_title: "Solar Market"           # Condensed form for recognition in constrained contexts
                                        #   (list items, tab labels, breadcrumbs, mobile headers)
                                        #   Target: 2-4 words. Must be unambiguous without the full title.
  abbreviation: "SEM"                   # 2-5 character identifier for the most constrained contexts
                                        #   (badges, pill tags, keyboard shortcuts, voice references)
                                        #   Must be pronounceable or a recognized acronym.
  tagline: >                            # One sentence capturing what this pack IS — not what it contains.
    Utility-scale solar market trends   #   Enables comprehension < 3 seconds.
    and cost analysis                   #   Not a description of the pack format — a statement of its subject.
  hook: >                               # The sentence that creates the desire to know more.
    The cost decline is structural,     #   Enables engagement < 5 seconds.
    not cyclical — and it has held      #   Not a summary — a provocation, a key insight, or a promise.
    for 40 years.                       #   The best sentence in the entire pack.
```

The `tagline` tells you what this IS. The `hook` tells you why you should CARE.

A tagline without a hook is an empty plate with a menu. The hook is the amuse-bouche — the thing that makes you stay and want the rest. Without it, no one navigates further.

**What these fields are NOT:**
- They are not marketing copy (that belongs in a website, not a spec)
- They are not aesthetic choices (fonts, colors, layout are renderer decisions)
- They are not summaries of the content (that's what views are for)

They are **cognitive handles** — the minimum information a human brain needs to recognize, locate, engage with, and navigate this pack across any display context.

### Authoring Guidelines

Each field has a cognitive job. The guidelines below ensure that job is done regardless of who authors the pack or which renderer displays it.

#### `short_title` (Recognition)

**Why it exists:** A human scanning a list of 20 packs, or glancing at a tab bar, or hearing a voice assistant name a pack — they need to recognize THIS pack in under one second. The full title ("Utility-Scale Solar Energy Market Analysis and Cost Trajectories") takes too long. The abbreviation ("SEM") requires insider knowledge. The short title occupies the sweet spot: long enough to be unambiguous, short enough to be instant.

The name a human would use to refer to this pack in conversation. 2-4 words. Must be unambiguous without the full title.

| Good | Bad | Why |
|------|-----|-----|
| "Solar Market" | "Utility-Scale Solar Energy Market Analysis and Cost Trajectories" | Too long — the full title belongs in the H1, not here |
| "Wind Outlook" | "Wind Energy Assessment" | "Assessment" is vague; "Outlook" implies forward-looking analysis |
| "Battery Storage" | "battery-storage-economics-2026-03" | File names are not titles |

#### `abbreviation` (Tight Contexts)

**Why it exists:** Some display contexts have almost no space — a mobile breadcrumb, a badge next to a notification, a voice assistant referencing a pack mid-sentence. The abbreviation is the absolute minimum identifier. It sacrifices clarity for brevity, which is why it exists alongside `short_title`, not instead of it.

2-5 characters. Must be pronounceable or a recognized acronym. Used in badges, breadcrumbs, tabs.

| Good | Bad | Why |
|------|-----|-----|
| "SEM" | "USEMPV" | Not pronounceable |
| "Wind" | "WE" | Ambiguous without context |

#### `tagline` (Comprehension)

**Why it exists:** After recognizing a pack by title, the next question is "what is this about?" The tagline answers that in a single breath. It's the bridge between the title (which names the thing) and the content (which explains it in full). Without a tagline, the human must open the pack and read before they can even assess relevance. The tagline prevents that wasted effort — it's a promise of what's inside, delivered before the reader commits.

One sentence that tells a stranger what the subject IS. Not what the pack contains — what the subject is about. Should be readable aloud in under 5 seconds. Natural language, not a label.

| Good | Bad | Why |
|------|-----|-----|
| "Utility-scale solar market trends and cost analysis" | "Executive summary with key metrics and status" | That describes the pack format, not the subject |
| "Supply chain risks for global solar deployment" | "Solar risk overview pack" | Reads like a filename, not a sentence |
| "Grid storage economics for renewable integration" | "Battery analysis pack" | The good version answers WHAT and WHY |

#### `hook` (Engagement)

**Why it exists:** Comprehension without engagement is a dead end. A person can understand what a pack is about and still not care. The hook exists because human attention is not given — it's earned. A tagline tells you what the plate is; the hook is the aroma that makes you want to eat. It's the most emotionally or intellectually compelling sentence in the entire pack, surfaced to the cover because burying it on page 3 means nobody gets there.

The single most compelling sentence in the entire pack. A provocation, a surprising insight, or a promise that creates the desire to read further. If you had to convince someone to open this pack with one sentence, this is it.

| Good | Bad | Why |
|------|-----|-----|
| "The real competitor is the status quo of neglect, not other platforms." | "This pack covers risks, timeline, and team." | That's a table of contents, not a hook |
| "We're raising $1.5M to capture the 18-month window before incumbents wake up." | "Fundraising information for Q2 2026." | No urgency, no insight, no reason to care |

If you can't find a hook, the pack may not have a clear thesis yet. That's a content problem, not a display problem.

#### `hint` per view (Navigation)

**Why it exists:** The cover shows sections, but a title alone ("Risks", "Timeline") is a label — it tells you the category, not the value. A human deciding where to click needs to know what they'll GET from opening that section, not what category it belongs to. The hint transforms a menu of labels into a menu of promises. Without it, navigation is a guessing game — the reader has to open sections speculatively. With it, they open with intent.

One sentence per section that helps a human decide: should I open this? Describes the VALUE of the section, not its structure. Max ~15 words.

| Good | Bad | Why |
|------|-----|-----|
| "Three risks that could block the Sep 2026 pilot" | "Risk register with 3 rows" | Structure is not value |
| "6 months built, 5 months to launch" | "Timeline table" | The good version tells you the insight |
| "What to say when Scott asks about AI safety" | "Technical Q&A section" | The good version tells you what you'll GET |

#### The Stranger Test

After authoring all display fields, read them in sequence:

> **[short_title]** — [tagline]. [hook]. Sections: [hint 1], [hint 2], [hint 3].

If a stranger reading this sequence can answer "what is this, why should I care, and where should I start?" — the fields pass. If not, rewrite.

### View-Level: `hint` Field

Each view entry in PACK.yaml may include a `hint` — a single sentence that helps a human decide whether to open this section.

```yaml
views:
  - name: risks
    file: views/02_risks.md
    purpose: "Risk register — mentor supply, FERPA, faculty adoption"
    display_as: "Risks"
    hint: "Three risks that could block the Sep 2026 pilot"
```

The `hint` differs from `purpose` in audience and intent:

| Field | Audience | Intent | Example |
|-------|----------|--------|---------|
| `purpose` | AI | When to display this view | "Risk register — mentor supply, FERPA, faculty adoption" |
| `display_as` | Human | Section label (recognition) | "Risks" |
| `hint` | Human | Should I open this? (navigation) | "Three risks that could block the Sep 2026 pilot" |

**Hint authoring rules:**
- One sentence, max ~15 words
- Describes the **insight or value** of the section, not its structure
- Must pass the navigation test: *does this help a human decide whether to open this section?*
- "3 tables and 12 claims" fails — it describes structure, not value
- "Three risks that could block the Sep 2026 pilot" passes — it describes what you'll learn

When `hint` is absent, renderers may extract one from the view's markdown (first blockquote, first paragraph sentence). But extracted hints are approximations — pre-authored hints are always better.

### Fallback Hierarchy

Renderers should resolve display metadata in this order:

| Need | Primary source | Fallback |
|------|---------------|----------|
| Pack title | `display.short_title` or pack `name` in `PACK.yaml` | H1 from overview view |
| Pack tagline | `display.tagline` | First blockquote from overview view |
| Section label | `display_as` | View `name` with title case |
| Section hint | `hint` | First blockquote or paragraph from view |

This hierarchy ensures packs work without display metadata (backward-compatible), while rewarding authors who provide it with better human perception.

---

## 19. Companion Specifications

The following topics are specified in companion documents within the `spec/` directory. Each extends the core spec without increasing the size of this document.

| Document | Topic | Decisions |
|----------|-------|-----------|
| `spec/MULTILINGUAL.md` | Locale subdirectories, translation workflow, drift detection, status tracking | D1, D2 |
| `spec/VOICE.md` | Voice view format, spoken delivery conventions, duration/pace metadata | D13 |
| `spec/COMPOSITION.md` | Meeting pack composition, agenda overlay, pre_load/on_demand, composition.yaml | D14 |
| `spec/BUNDLE.md` | Export format (full bundle + clipboard), KP:1 markers, CLI commands | D11, D19 |
| `spec/LIFECYCLE.md` | Pack types (ephemeral/seasonal/permanent), archival, intelligent reconciliation, visibility | D4, D15, D19 |
| `spec/NOTES.md` | AI note-taking metadata, disclosure vs consent, active vs passive modes | D16 |
| `spec/CONSISTENCY.md` | Cross-pack patrol, claim contradiction detection, real-time alerting, confidence decay | D18 |
| `spec/CONVENTIONS.md` | Linguistic conventions — American English, Merriam-Webster, 30-rule table, fallback hierarchy | D1 |
| `spec/ORGANIZATION.md` | Nested pack categories, working set, migration strategy, repo structure | D3, D12 |
| `spec/STORAGE.md` | Pack-as-master principle, serialization formats, index contract, storage independence | — |
| `spec/DEFINITIONS.md` | Definition and policy document kinds, YAML schemas, codegen concept, migration guidance | — |

These documents are normative — they carry the same authority as this core spec. The core spec defines the format; companion specs define the ecosystem.

---

## 20. Relationship to Existing Standards

| Standard | Relationship |
|----------|-------------|
| Agent instruction files (e.g., AGENTS.md) | Orthogonal — agent instruction files configure behavior, Knowledge Packs provide facts |
| Agent Skills (SKILL.md) | Complementary — Skills declare `requires_knowledge` for pack dependencies |
| MCP Resources | Knowledge Packs can be served as MCP resources at runtime |
| llms.txt | Discovery — llms.txt could point to available Knowledge Packs |
| Entity-Claim-Evidence (ECS) systems | Implementation pattern — ECS is an operational index; Knowledge Packs are the canonical source. See `spec/STORAGE.md` |
| JSON-LD / RDF | Inspiration — semantic structure, but optimized for neural nets, not symbol processors |
| Nanopublications | Spiritual ancestor — assertion + provenance, but in markdown, not RDF |

---

## Appendix A: Changelog

See `CHANGELOG.md` for version history.
