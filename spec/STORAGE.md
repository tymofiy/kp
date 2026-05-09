<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Storage Independence — Knowledge Pack Companion Spec

> **Date:** 2026-03-29
> **Status:** Draft
> **Editor:** Timothy Kompanchenko

---

## 1. Purpose

This document formalizes the relationship between Knowledge Packs and the infrastructure that stores, indexes, and serves them. It establishes the **pack-as-master** principle: Knowledge Packs are the canonical source of truth for their contents. All operational infrastructure — databases, caches, indices — is derived from packs and rebuildable from them.

---

## 2. The Pack-as-Master Principle

### Statement

A Knowledge Pack is the authoritative representation of its epistemic contents. Any external system that stores, indexes, caches, or projects pack data is a **derived representation** that serves operational needs. When a derived representation disagrees with the pack, the pack is correct.

### Analogy

This is the relationship between a git object store and git refs/index. The objects (blobs, trees, commits) are the source of truth. Refs, the index, remote tracking branches, and merge state are operational infrastructure derived from objects. You can `git fsck` and rebuild the index from objects. You can never rebuild objects from the index.

Similarly:
- Knowledge Packs = git objects (the truth)
- Databases, caches, search indices = git index/refs (derived, rebuildable)

### Implications

1. **Writes flow through packs.** When knowledge changes, the pack changes first. Indices update to reflect the pack, not the other way around.
2. **Indices are rebuildable.** Any index or database projection of pack data can be dropped and reconstructed by re-reading packs. This is the test of whether the pack is truly master.
3. **Packs are portable without infrastructure.** A pack exported to a USB drive, emailed, or placed on a blockchain functions identically — the Voyager Principle is preserved regardless of operational storage.
4. **No infrastructure-only knowledge.** If a piece of knowledge exists only in a database column and not in any pack, it is not part of the canonical knowledge base. It may be useful operational data, but it is not mastered knowledge.

### What This Does NOT Mean

- **It does not mean you cannot have databases.** You need operational infrastructure for fast cross-pack queries, vector search, real-time session accumulation, and entity resolution. The principle says these are indices into packs, not replacements for them.
- **It does not mean packs must be files on disk.** Packs can be stored in any medium (see §3). The logical model is what matters, not the physical storage.
- **It does not mean everything must be a pack.** Task queues, UI state, authentication tokens, and operational configuration are not knowledge and should not be forced into pack format (see §5).

---

## 3. Serialization Formats

A Knowledge Pack is a logical model (manifest + claims + evidence + views + history). The SPEC.md defines the **file serialization** as the canonical human-readable form. This section defines additional serialization formats for operational storage.

### 3.1 File Serialization (Canonical)

The format defined in SPEC.md §2: a directory of plain text files (PACK.yaml, claims.md, evidence.md, views/).

- **When to use:** Curated packs, version-controlled repositories, export/import, long-term archival, Voyager-compliant distribution.
- **Properties:** Human-readable, git-diffable, zero-dependency. This is the format that satisfies the Voyager Principle.
- **Authority:** When a pack exists in file form, the files are authoritative.

### 3.2 JSON Serialization (Operational)

A single JSON document or a set of JSON records representing the pack's logical contents.

```typescript
interface KPackJSON {
  manifest: KPackManifest;     // PACK.yaml contents as JSON
  claims: KPClaim[];           // Structured claim records
  evidence: KPEvidence[];      // Evidence records
  views: KPView[];             // View records (name, surface, content)
  history: KPHistoryEntry[];   // Superseded/retracted claims
}
```

- **When to use:** Database storage (Postgres JSONB or relational), API responses, programmatic consumption.
- **Properties:** Machine-queryable, structured, parseable without markdown parsing. Loses some human readability but gains structured access.
- **Conversion:** Deterministic bidirectional conversion between file and JSON forms. Round-trip fidelity is required — `file → JSON → file` must produce semantically identical output.

### 3.3 Compact Serialization (Ephemeral)

A minimal representation for space-constrained contexts (Redis capsules, context window injection, transfer).

```typescript
interface KPackCompact {
  name: string;
  version: string;
  claims: Array<{
    id: string;
    text: string;
    confidence: number;
    type: string;
    status: string;
  }>;
  // Evidence, views, and history omitted — loadable on demand
}
```

- **When to use:** Redis restart capsules, context window injection, WebSocket transfer, in-flight session accumulation.
- **Properties:** Minimal token footprint. Intentionally lossy — strips evidence chains, views, and history. The compact form is sufficient for reasoning but not for full epistemic audit.
- **Conversion:** One-way: full pack → compact (lossy). Compact → full requires access to the evidence and history from the original source.

### 3.4 Format Equivalence

All three serializations represent the same logical model. The relationship:

```text
File (canonical) ←→ JSON (operational) → Compact (ephemeral)
     ↑                    ↑                    ↑
  authoritative     round-trippable        lossy projection
  human-readable    machine-queryable      minimal footprint
  Voyager-compliant DB-storable            cache-friendly
```

---

## 4. The Index Contract

Operational indices enable capabilities that individual packs cannot provide: cross-pack search, entity resolution, statistical aggregation, vector similarity. This section defines what indices must guarantee.

### 4.1 What Indices Provide

| Capability | Description | Why packs alone can't do this |
|-----------|-------------|-------------------------------|
| Cross-pack claim search | "What do I know about Picasso?" across all packs | Requires reading all packs; too slow at scale |
| Entity resolution | Match entities across packs by name, alias, URI | Requires global entity registry |
| Vector similarity | "Find claims similar to X" | Requires embeddings and approximate nearest neighbor |
| Statistical aggregation | Market overviews, claim counts, confidence distributions | Requires structured query across many packs |
| Temporal queries | "What changed since last week?" | Requires timestamped index entries |

### 4.2 Index Invariants

1. **Rebuildable.** The entire index can be dropped and reconstructed by reading all packs. This is the master test. If rebuilding the index from packs loses information that was in the index, that information was not properly mastered in a pack.

2. **Eventually consistent.** When a pack changes, the index may lag briefly. This is acceptable. The index is a cache, not a source of truth.

3. **Additive only.** Indices add capabilities (search, aggregation, speed). They never add knowledge. A claim that exists only in an index and not in any pack is an orphan that should be flagged and resolved.

4. **Pack-attributed.** Every index entry traces back to a specific pack and claim. The index knows where each piece of knowledge came from.

### 4.3 Index Schema (Reference)

This is a reference schema, not a mandate. Implementations may vary.

```sql
-- Pack registry
CREATE TABLE pack_index (
  pack_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  version TEXT NOT NULL,
  domain TEXT,
  tier TEXT,
  lifecycle_type TEXT,
  storage_backend TEXT,      -- 'file', 'postgres', 'redis'
  storage_location TEXT,     -- file path, table name, redis key
  indexed_at TIMESTAMPTZ
);

-- Claim index (cross-pack searchable)
CREATE TABLE claim_index (
  claim_id TEXT PRIMARY KEY,      -- globally unique (ULID/UUIDv7)
  pack_id TEXT REFERENCES pack_index(pack_id),
  display_id TEXT,                -- human-readable alias (C001)
  assertion TEXT,
  confidence NUMERIC(3,2),
  claim_type TEXT,
  depth TEXT,
  nature TEXT,
  status TEXT,
  since DATE,
  valid_to DATE,
  indexed_at TIMESTAMPTZ
);

-- Claim relations (cross-pack)
CREATE TABLE claim_relation_index (
  from_claim_id TEXT,
  to_claim_id TEXT,
  relation TEXT,     -- supports, contradicts, supersedes, etc.
  PRIMARY KEY (from_claim_id, to_claim_id, relation)
);

-- Vector embeddings for semantic search
CREATE TABLE claim_embeddings (
  claim_id TEXT PRIMARY KEY,
  embedding vector(1536),
  model TEXT
);
```

---

## 5. Pack Boundaries — What Is and Isn't a Pack

### Clear Knowledge Packs

These are unambiguously knowledge packs:

| Content | Pack Type | Lifecycle | Example |
|---------|-----------|-----------|---------|
| Curated domain knowledge | standalone/hub | permanent | `solar-energy-market.kpack` |
| Entity intelligence | detail | permanent | `picasso-provenance.kpack` |
| Meeting notes | standalone | ephemeral | `meeting-jackson-2026-04-02.kpack` |
| Conversation capture | standalone | ephemeral | `session-2YC6M-2026-03-29.kpack` |
| Research findings | standalone | permanent | `market-analysis-pe.kpack` |

### Incremental Adoption Candidates

These may evolve into knowledge packs as the model matures:

| Content | Current System | Path to KP:1 | When Ready |
|---------|---------------|--------------|------------|
| Memory suggestions | Postgres flat rows | Claims in a staging pack with review workflow | When the pack model naturally accommodates the review lifecycle |
| Session notes ("take a note") | Not yet built | Notes in the session's conversation pack | When conversation packs are proven end-to-end |
| Action items | Extracted by passive analyzer | Already in conversation packs as view content | Already there — formalize as first-class content type |

### Not Knowledge Packs

These should NOT be forced into pack format:

| Content | Why Not | What They Are |
|---------|---------|---------------|
| Task queues | Operational state, not epistemic content | Workflow infrastructure |
| UI state | Transient, per-client | Application state |
| Auth tokens | Security infrastructure | Configuration |
| Build artifacts | Computational output | DevOps |
| Raw event logs | Undifferentiated data stream | Operational telemetry |

The test: **Does this content represent beliefs with confidence, evidence, and relationships?** If yes, it's a candidate for KP:1. If it's operational state, workflow data, or infrastructure configuration, it isn't.

---

## 6. Pack Content Types

### 6.1 Claims (Existing)

The primary content type, defined in SPEC.md §4. Structured assertions with confidence, type, evidence, depth, nature, and relations.

### 6.2 Non-Claim Content (New)

Packs may contain content that is not a formal claim but is epistemically relevant to the pack's domain. These are captured in views or in structured sections within claims.md.

| Content Type | Description | Example | Where It Lives |
|-------------|-------------|---------|----------------|
| **Decision** | A choice made, with rationale | "Decided to use Clerk for auth" | Claim with `nature: judgment` or `views/decisions.md` |
| **Action Item** | Something to be done, with owner/deadline | "Team lead to contact supplier by Friday" | `views/action-items.md` |
| **Note** | User-directed capture ("take a note of this") | "Analyst quoted $800M TAM" | Claim with `type: reported` if epistemic, or `views/notes.md` if operational |
| **Question** | Unresolved question worth tracking | "What's the actual TAM?" | `views/questions.md` or meta-claim |

**The rule:** If content has epistemic value (confidence, evidence, relationships matter), it should be a claim. If it's operational (tracking who does what by when), it belongs in a view. Both live inside the same pack. The pack is the container; claims and views are the content types.

**Notes specifically:** When a user says "take a note," the system determines whether the note is:
- **Epistemic** ("The analyst said the TAM is $800M") → becomes a claim: `[N001] Analyst quoted $800M TAM {0.70|r|session-transcript|2026-03-29}`
- **Operational** ("Call the supplier tomorrow") → goes to `views/action-items.md` or `views/notes.md`

This distinction matters because epistemic notes gain the full benefit of KP:1's confidence, evidence, and contradiction tracking. Operational notes don't need that overhead.

---

## 7. In-Flight Pack Accumulation

During live sessions (voice conversations, meetings, research), packs are accumulated in real time. The pack-in-progress is conceptually a pack even before it's finalized.

### Lifecycle

```text
Accumulating (Redis)  →  Materialized (Postgres/File)  →  Archived/Promoted
   in-flight                  durable                      long-term
   high write freq            queryable                    indexed
   session-scoped             room-scoped                  tenant-scoped
```

### Accumulation Rules

1. **In-flight packs use compact serialization** in Redis. Claims are appended as they're extracted.
2. **Session end triggers materialization.** The conversation-kpack materializer produces the full pack (all serialization formats).
3. **Materialized packs are indexed.** The index updates to include the new pack's claims.
4. **Ephemeral lifecycle.** Session packs have `lifecycle.type: ephemeral` with `archive_after_days` set. Before archival, the reconciliation step ([RATIONALE.md §1, Principle 21](RATIONALE.md)) ensures valuable claims are promoted to standing packs.

### Restart Capsules

Restart capsules (used for voice session recovery) are compact serializations of the in-flight pack. They contain enough information to resume accumulation but are not full packs. When a session restarts, the capsule seeds the new accumulation context.

---

## 8. Relationship to Entity-Claim-Evidence Indices

An entity-claim-evidence index — a database (relational, document, or graph) that stores entities, claims, and evidence as queryable rows or nodes — is a natural **operational index** for a knowledge pack corpus. It provides cross-pack entity resolution, claim querying, and evidence lookup at scales where scanning files is impractical.

This section is non-normative. It describes how such an index would relate to packs under the pack-as-master principle (§3), not how it must be implemented.

### Index as derived view

In the pack-as-master model, an entity-claim-evidence index is a derived projection of the pack corpus:

| Index Component | Role | Derived From |
|-----------------|------|--------------|
| Entities | Global entity registry | `entities.md` across all packs |
| Claims | Cross-pack claim index | `claims.md` across all packs |
| Evidence | Evidence lookup | `evidence.md` across all packs |
| Entity Links | Cross-entity relationships | Claim relations + entity references |

The index can be dropped and rebuilt from packs at any time. It is operational infrastructure, not a source of truth.

### Structural alignment considerations

Any index schema that materializes packs must reconcile differences in vocabulary, ranges, and structure. Common alignment work includes:

| Gap | Typical Resolution |
|-----|-------------------|
| Index uses an integer or enumerated confidence; KP:1 uses 0.0–1.0 | Normalize at ingest using the source pack's `confidence.normalize` declaration |
| Index lacks `depth` or `nature` fields | Extend the index schema or store as opaque metadata |
| Index uses structured `predicate` + `value`; KP:1 uses prose `text` | Index keeps structured form; serializers generate prose for export |
| Index claim statuses do not match KP:1's four | Map index statuses onto KP:1's set; document the mapping |
| Index has only entity-level links; KP:1 has claim-level relations | Extend the index schema to support per-claim relations |

These gaps are illustrative. Specific implementations will encounter their own.

### Bidirectional flow

```text
File pack  →  parse  →  index  →  query, resolve, aggregate
   index  →  materialize  →  file pack (export, distribute)
```

Both directions should be deterministic given a fixed pack corpus and a stable index schema. Materializers that reconstruct packs from index rows are an existing pattern in conversation-derived pack tooling.

---

## 9. Design Principles for Storage Independence

1. **Pack is master.** When pack and index disagree, trust the pack. Rebuild the index.
2. **Serialize, don't reshape.** Packs stored in Postgres are serialized packs, not database-shaped data that happens to contain pack fields. The logical model comes first.
3. **Index for speed, pack for truth.** Indices exist because reading all packs for every query is slow. They are performance infrastructure, not knowledge infrastructure.
4. **One authority per pack.** Each pack has exactly one authoritative backend at any time. A file-authored pack is authoritative in its file form. A session pack is authoritative in Redis during the session, then in Postgres after materialization.
5. **Export is always possible.** Any pack in any backend can be exported to the file serialization (the Voyager-compliant form). This is the escape hatch that guarantees portability.
6. **Incremental adoption.** Not everything needs to become a pack today. Existing systems (memories, session ledgers) continue to work. As the pack model proves itself for each use case, content migrates naturally.
