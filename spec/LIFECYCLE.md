<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Lifecycle, Archival & Visibility Specification

> **Status:** Draft
> **Date:** 2026-03-22
> **Editor:** Timothy Kompanchenko
> **Decisions:** D4 (meeting pack lifecycle), D15 (archive-never-delete), D19 (reconcile-before-archive)

---

## 1. Lifecycle Types

Every Knowledge Pack has a lifecycle type that governs how long it remains in the active working set and what happens when it leaves.

| Type | Description | Auto-archive | Default retention | Examples |
|------|-------------|--------------|-------------------|----------|
| `permanent` | Standing knowledge. Never auto-archived. Evolves in place through claim supersession. | No | Indefinite | Market analysis, sector coverage, domain expertise |
| `seasonal` | Relevant for a bounded period. Archived when the period ends. | Yes, on expiry | 90 days (configurable) | Quarterly outlooks, research initiatives, conference prep |
| `ephemeral` | Short-lived. Created for a specific event or moment. Archived after retention period. | Yes, on expiry | 14 days (configurable) | Meeting prep, call notes, weekly briefings |

**Default:** `permanent`. A pack without an explicit lifecycle type is standing knowledge.

### 1.1 Memory Architecture

Standing packs and ephemeral packs serve fundamentally different cognitive functions, analogous to long-term and short-term memory.

**Long-term memory (standing packs)** is organized by semantic domain. Everything about supply chain risk clusters together regardless of which meeting surfaced it. Everything about a technology trajectory clusters together regardless of which research cycle analyzed it. The organizing principle is *what it's about*. Standing packs grow through claim supersession and evidence accumulation. They are the canonical home of knowledge.

**Short-term memory (ephemeral packs)** is organized by proximity of operational need. A meeting prep pack clusters claims from multiple domains -- market forecasts, technology assessments, regulatory updates, competitive intelligence -- because they're all needed *together* in the next 30 minutes. The organizing principle is *when and where it's needed*. This is a legitimate cognitive architecture, but it is temporary.

**Consolidation is the bridge.** Like memory consolidation in neuroscience, the episode dissolves but the knowledge persists. Novel knowledge created during meeting prep or research sprints migrates to its semantic home in a standing pack. What remains in the ephemeral pack after consolidation is:

- **Operational choreography** -- scripts, roles, timing, fallback plans, behavioral instructions. These are not epistemic state. They are procedures.
- **Temporal context** -- impressions, atmosphere, process notes. These are genuinely event-specific and do not need a permanent home.

### Content Classification Test

Every claim in an ephemeral pack falls into one of three categories:

| Category | Test | Destination |
|----------|------|-------------|
| **Knowledge** | *Would this claim be valuable if the event never happened?* If yes -> knowledge. | Consolidate into standing pack |
| **Operational** | *Is this a behavioral instruction, script, or procedure for the event?* If yes -> operational. | Stays in ephemeral pack (not knowledge) |
| **Temporal** | *Is this an observation meaningful only in the moment?* If yes -> temporal. | Stays in ephemeral pack (event-specific) |

Examples:
- "China produces 80% of global polysilicon and 95% of wafers" -> **Knowledge** (true regardless of meeting)
- "Jane presents the cost thesis first; Webb responds" -> **Operational** (behavioral instruction for one meeting)
- "Elena seemed skeptical about the perovskite timeline" -> **Temporal** (impression from the event)

### When to Use Each Type

**Permanent** packs are the backbone of your knowledge graph. They represent things you know -- about markets, technologies, domains, organizations. They grow through claim supersession (old claims get `supersedes`, new claims take their place). They are never "done."

**Seasonal** packs represent time-bounded knowledge that is authoritative during its period and historical afterward. A quarterly market outlook is the definitive source during the quarter; afterward, its claims should be absorbed into permanent packs (market analysis, technology assessment, regulatory coverage) and the pack archived. Seasonal packs have a natural lifespan measured in weeks or months.

**Ephemeral** packs are short-term memory containers. They exist to activate and generate knowledge for a specific event. Their primary lifecycle purpose is **consolidation**: novel knowledge created during prep or captured during the event migrates to standing packs. After consolidation, the ephemeral pack contains only operational choreography and temporal context -- content that is genuinely event-specific. The pack then archives cleanly because no knowledge is trapped in it. The ephemeral pack is the scaffold, not the building.

---

## 2. PACK.yaml Fields

```yaml
lifecycle:
  type: permanent              # permanent | seasonal | ephemeral
  archive_after_days: null     # Auto-archive trigger (null = never for permanent)
  archive_policy: reconcile    # reconcile | auto | manual
  reconciled_at: null          # ISO timestamp of last reconciliation check
  orphan_claims: []            # Claim IDs with no match in standing packs

consolidation:                 # Knowledge consolidation targets (ephemeral/seasonal packs)
  targets:                     # Standing packs that should receive knowledge claims
    - pack: solar-energy-market  #   Target pack name (by semantic domain)
      claims: [F001, F002]       #   Source claim IDs to consolidate
    - pack: perovskite-assessment
      claims: [F011, F012]
  status: pending              # pending | in-progress | complete
  completed_at: null           # ISO timestamp of consolidation completion

visibility: private            # private | shared | public
```

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `lifecycle.type` | enum | No | `permanent` (default), `seasonal`, `ephemeral` |
| `lifecycle.archive_after_days` | integer or null | No | Days after `freshness` date before auto-archive triggers. Defaults: `null` (permanent), `90` (seasonal), `14` (ephemeral) |
| `lifecycle.archive_policy` | enum | No | What happens when archive triggers. `reconcile` (default), `auto`, `manual` |
| `lifecycle.reconciled_at` | ISO datetime or null | No | Timestamp of last reconciliation. Set by tooling |
| `lifecycle.orphan_claims` | list of strings | No | Claim IDs flagged as unreconciled. Set by tooling |
| `consolidation.targets` | list of objects | No | Standing packs that should receive knowledge claims. Each entry: `pack` (name), `claims` (list of source claim IDs) |
| `consolidation.status` | enum | No | `pending`, `in-progress`, `complete`. Tracks consolidation progress |
| `consolidation.completed_at` | ISO datetime or null | No | Timestamp when consolidation finished |
| `visibility` | enum | No | `private` (default), `shared`, `public` |

### Archive Policies

| Policy | Behavior |
|--------|----------|
| `reconcile` | **Default.** Run intelligent reconciliation before archiving. Archive only if all claims are reconciled. Flag orphans for human review. |
| `auto` | Archive immediately when retention expires. No reconciliation. Use for packs where all claims are already reflected in standing packs by design (e.g., generated summaries, derivative views). |
| `manual` | Never auto-archive. User must explicitly archive. For packs that may need indefinite active access despite being time-bounded. |

---

## 3. Archival

### The Rule

**Archive, never delete.** Packs are archived, not destroyed. Archived packs remain searchable, loadable, and present in git history. Archival moves a pack out of the active working set -- it does not remove it from existence.

### Archive Location

Archived packs move to an `_archive/` subdirectory within their category:

```text
packs/
├── meetings/
│   ├── webb-advisory-2026-03-22.kpack/        # Active
│   ├── vasquez-briefing-2026-03-25.kpack/     # Active
│   └── _archive/
│       ├── park-supply-review-2026-03-10.kpack/   # Archived
│       └── chen-irena-debrief-2026-03-01.kpack/   # Archived
├── research/
│   ├── solar-energy-market.kpack/             # Active
│   └── _archive/
│       └── solar-market-q4-2025.kpack/        # Archived
└── analysis/
    └── competitor-analysis.kpack/             # Permanent -- never archived
```

### What Archival Changes

| Aspect | Active | Archived |
|--------|--------|----------|
| Location | `packs/{category}/` | `packs/{category}/_archive/` |
| Discoverable via `KNOWLEDGE.yaml` | Yes | Yes (marked `archived: true`) |
| Loadable via `load_pack` | Yes | Yes |
| Included in search results | Yes | Yes (lower ranking) |
| Included in working set for context | Yes | **No** |
| Editable | Yes | Read-only by convention |
| In git history | Yes | Yes |

### What Archival Does NOT Do

- Does not delete files
- Does not remove from git
- Does not strip claims
- Does not break cross-pack `see_also` references (references to archived packs resolve normally)
- Does not require re-indexing (the pack is the same content at a new path)

---

## 4. Consolidation & Reconciliation

The lifecycle of an ephemeral pack has two distinct phases: **consolidation** (the primary purpose) and **reconciliation** (the safety net).

### 4.1 Consolidation -- The Primary Purpose

Consolidation is the process of migrating novel knowledge from an ephemeral pack to its semantic home in standing packs. This is not a cleanup step -- it is the reason ephemeral packs exist. The ephemeral pack is a temporary workspace that generates knowledge; standing packs are where that knowledge lives permanently.

**When consolidation happens:** Ideally, knowledge should be created in standing packs *during prep* (before the event) and referenced by the ephemeral pack. For knowledge discovered during or after the event, consolidation runs as soon as practical -- not deferred until the archive trigger fires.

**The consolidation process:**

1. **Classify every claim** as knowledge, operational, or temporal (see Section 1.1 Content Classification Test)
2. **For each knowledge claim**, identify the target standing pack by semantic domain
3. **Create or update the claim** in the standing pack with proper evidence and relations
4. **Mark the source claim** as consolidated (add `->consolidated:{target-pack}#{claim-id}` relation)
5. **Update PACK.yaml** `consolidation.status` to reflect progress

**What consolidates (knowledge):**
- New facts learned during research or the event -> relevant standing pack
- Intelligence about organizations, technologies, markets -> domain packs
- Strategic assessments and analyses -> strategy packs
- Commitments and decisions -> project packs
- Changed assumptions -> updates to existing claims in standing packs

**What stays (operational + temporal):**
- Meeting-specific choreography ("Jane presents cost thesis first; Webb responds")
- Temporal observations ("Elena seemed skeptical about the perovskite timeline")
- Process notes ("We ran 10 minutes over; shorten the technology section next time")
- Fallback plans and behavioral instructions

### 4.2 Reconciliation -- The Safety Net

Reconciliation runs before archival to catch knowledge claims that were missed during consolidation. It solves a psychological problem: **people resist archiving because they fear losing information.**

### The Psychology

Information hoarding is a well-documented cognitive pattern. People keep files, emails, and notes they will never read again because the act of discarding triggers anxiety -- "what if I need this?" The Zeigarnik effect compounds this: unfinished cognitive tasks (like "did I capture everything from that meeting?") create persistent mental load until explicitly closed.

The standard advice -- "just delete what you don't need" -- fails because it requires a keep-vs-delete decision for every item. This decision is cognitively expensive and emotionally aversive, so people defer it indefinitely.

**Our solution draws from the PARA method insight:** reframe "keep vs delete" as "active vs archived." Both states preserve the information. The only question is whether it's in your working set. This eliminates the loss anxiety.

When consolidation has been done well, reconciliation is a formality -- it confirms that all knowledge claims already have a permanent home. When consolidation was skipped or incomplete, reconciliation catches the orphans.

### The Three-Step Process

Reconciliation is a three-step process that runs before any ephemeral or seasonal pack is archived:

#### Step 1: Post-Event Consolidation Review

Verify that consolidation (Section 4.1) was completed. If `consolidation.status` is not `complete`, run consolidation first. This step should happen soon after the event, not weeks later when context has decayed.

**Already consolidated -> skip to Step 2.**

**Not yet consolidated:**
- New facts learned during the meeting -> relevant standing pack
- Commitments and action items -> project or entity packs
- Changed assumptions -> updates to existing claims in standing packs
- New relationships discovered -> entity updates

**What stays in the ephemeral pack:**
- Meeting-specific context ("Dr. Webb seemed optimistic about the perovskite timeline")
- Temporal observations ("Polysilicon prices were volatile this week")
- Process notes ("We ran 10 minutes over; shorten the technology section next time")

#### Step 2: Reconciliation Check

When the archive trigger fires (retention period elapsed), an AI reviews every claim in the ephemeral pack against all standing packs. For each claim, one of three outcomes:

| Outcome | Meaning | Action |
|---------|---------|--------|
| Reconciled | Claim is reflected in a standing pack (identical, superseded, or refined) | None -- safe to archive |
| Promoted | Claim was promoted during post-event review (Step 1) | None -- already handled |
| Orphan | Claim has NO match in any standing pack | Flag for human review |

#### Step 3: Archive with Receipt

**If all claims are reconciled or promoted:** Auto-archive. Move the pack to `_archive/`. Update `KNOWLEDGE.yaml`. Done.

**If orphan claims exist:** Do NOT archive. Notify the user with the specific orphan claims listed. The user decides: promote them to a standing pack, or acknowledge that they are meeting-specific context and clear the flag.

### Reconciliation Output Example

When `kpack reconcile meetings/webb-advisory-2026-03-22.kpack/` runs, it produces a report like this:

```text
Reconciliation Report: webb-advisory-2026-03-22.kpack
══════════════════════════════════════════════════════
Pack: Dr. Webb — Quarterly Advisory Review
Type: ephemeral | Retention: 14 days | Created: 2026-03-22

Claims reviewed: 8
  ✅ Reconciled:  5
  ✅ Promoted:    1
  ⚠️  Orphan:     2

─── Reconciled ─────────────────────────────────────

[C001] Dr. Webb advises three utility-scale solar developers
  → MATCHED in contacts/marcus-webb.kpack [C003]
    "Webb advises SolarFirst, GridScale, and Helios Energy"

[C002] GridScale's pipeline exceeds 2 GW across four states
  → MATCHED in research/gridscale-partnership.kpack [C004]
    "GridScale: 2.1 GW pipeline — Texas, Arizona, Nevada, Colorado"

[C003] Perovskite durability results from Oxford PV were positive
  → MATCHED in research/perovskite-assessment.kpack [C015]
    "Oxford PV Q1 2026 field test: <5% degradation at 18 months"

[C004] Webb suggested connecting us with Helios Energy's CTO
  → MATCHED in research/solar-energy-market.kpack [C046]
    "Warm intro to Helios Energy CTO via Webb (pending)"

[C005] Webb's advisory clients include three thin-film manufacturers
  → MATCHED in contacts/marcus-webb.kpack [C007]
    "Advisory clients: NanoSolar, ThinFilm Corp, FlexPV (thin-film)"

─── Promoted (during post-meeting review) ──────────

[C006] Webb wants to see a live comparison of bifacial vs monofacial yield data
  → PROMOTED to research/solar-energy-market.kpack [C047]
    "Bifacial vs monofacial field yield comparison requested by Webb (prepare by Apr 5)"

─── Orphan (not found in any standing pack) ────────

⚠️  [C007] Webb mentioned IRA incentive reclassification expected Q3
    2026 — may affect GridScale's project economics
    {0.70|r|E003|2026-03-22}
    NOT FOUND in any standing pack.
    Suggested target: research/regulatory-landscape.kpack § IRA Incentives

⚠️  [C008] GridScale is considering a dedicated perovskite pilot
    project, timeline late 2027
    {0.60|r|E004|2026-03-22}
    NOT FOUND in any standing pack.
    Suggested target: research/gridscale-partnership.kpack § Technology Pilots

══════════════════════════════════════════════════════
Result: BLOCKED — 2 orphan claims require review.
  Run: kpack promote M007 --to research/regulatory-landscape.kpack
  Run: kpack promote M008 --to research/gridscale-partnership.kpack
  Or:  kpack archive --force webb-advisory-2026-03-22.kpack
       (acknowledges orphans as meeting-specific context)
```

### Why This Works

The reconciliation report closes every open loop:

1. **For each claim, the user sees proof** that it landed somewhere permanent. Not "trust us, it's fine" -- actual matched claim IDs in actual packs.

2. **Orphan claims get specific routing suggestions.** The system doesn't just say "2 claims not found." It says "this claim about IRA incentive reclassification should probably go in your regulatory landscape section."

3. **The user can always force-archive.** Sometimes a claim genuinely is meeting-specific context that doesn't belong in any standing pack. The `--force` flag acknowledges this explicitly rather than silently dropping it.

4. **1-2 click retrieval.** Research on personal information management (Jones, 2007; Bergman & Whittaker, 2016) consistently shows that archival systems are trusted only when retrieval is fast and reliable. Archived packs are loadable with the same `load_pack` command, searchable through the same search index, and visible in `KNOWLEDGE.yaml`. The archive is not a graveyard -- it is a quieter shelf.

---

## 5. CLI Commands

```bash
# Check what would be archived (dry run)
kpack archive --dry-run
# Output: lists all packs past retention with reconciliation status

# Archive all reconciled packs past retention
kpack archive
# Archives packs where all claims are reconciled. Skips packs with orphans.

# Archive a specific pack
kpack archive meetings/webb-advisory-2026-03-22.kpack/

# Force-archive despite orphan claims
kpack archive --force meetings/webb-advisory-2026-03-22.kpack/
# Logs acknowledgment that orphan claims were accepted as-is

# Run reconciliation without archiving
kpack reconcile meetings/webb-advisory-2026-03-22.kpack/
# Produces the reconciliation report shown in Section 4

# Reconcile all ephemeral packs
kpack reconcile --all

# Promote a specific claim to a standing pack
kpack promote M007 --to research/regulatory-landscape.kpack
# Adds the claim to the target pack, marks it as promoted in the source

# Restore a pack from archive
kpack restore meetings/webb-advisory-2026-03-22.kpack/
# Moves from _archive/ back to active directory
```

> The `kpack` commands above describe planned reference tooling. As of v0.8.0-preview, the only command that ships in this repository is `python3 conformance/run.py`. See [SPEC.md §13 Tooling](SPEC.md) for status.

---

## 6. Claim Supersession Cascade

When a claim is superseded with `⊘`, the original moves to `history.md` and a successor claim takes its slot in `claims.md`. Other claims in the same pack may have linked to the superseded claim — typically via `→supports` (this claim provides evidence for the parent), `←requires` (this claim depends on the parent's truth), or `~refines` (this claim adds detail to the parent).

The cascade rule:

> **Rule (L1).** When a claim is superseded with `⊘`, every dependent claim that links to it via `→supports`, `←requires`, or `~refines` MUST be reviewed by the editor for whether it still stands under the new parent. Dependent claims are NOT automatically invalidated. The editor decides whether each dependent claim still holds, requires its own supersession, or requires only its relation to be re-pointed at the successor.

This is the conservative default. It treats the parser as authoritative for syntax and the editor as authoritative for epistemic state.

### Why not auto-invalidate

A stricter rule — automatically marking every `←requires` dependent as invalid when its parent is superseded — was considered and rejected for v0.8.0-preview. The reasons:

1. **Many supersessions narrow rather than negate.** A successor claim that refines the parent (e.g., from "the work is dated 1957" to "the work is dated 1962") may leave most dependent claims standing under the new parent's truth. Auto-invalidation would force unnecessary supersession of claims that remain accurate.

2. **The graph topology is the editor's responsibility.** Whether a dependent's relation is still meaningful under the new parent is an epistemic call, not a structural one. The format gives the editor the primitives (`⊘`, `~`, supersession in `history.md`); the editor composes them.

3. **The parser stays simple.** A parser that auto-invalidates a transitive closure across multiple files would need graph-traversal semantics that the current PEG grammar deliberately avoids. The supersession cascade rule lives at the editorial layer, not the parsing layer.

### Worked example

Suppose `claims.md` contains:

```text
- [C001] The work is dated 1957 in the auction-house specialist's report.
  {0.83|r|E001|2025-11-15|investigated}

- [C002] X-ray fluorescence is consistent with the artist's documented palette for the 1955-1959 period.
  {0.87|o|E002|2025-12-04|investigated} →C001

- [C003] Comparable lots dated 1955-1959 sold in 2024-2025 at €820,000-€1,180,000.
  {0.99|c|E003|2026-05-09} ←C001
```

Now C001 is superseded by C001-v2 (dated 1962, after a catalog raisonné review):

```text
- [C001-v2] The work is dated 1962 in the catalog raisonné.
  {0.91|r|E004|2020-04-30|exhaustive|judgment} ⊘C001
```

Per Rule L1, the editor reviews C002 and C003:

- **C002** said XRF was consistent with the 1955-1959 palette. Under C001-v2 (dating 1962), this claim is no longer supportive of the parent — it asserts the wrong period. The editor supersedes C002 with C002-v2 reflecting the 1960-1965 palette consistency, OR re-points the relation if XRF is consistent with both periods.
- **C003** cited 1955-1959 comparables. Under C001-v2, the comparable set is wrong; C003's predicate ("comparables sold in 2024-2025 at...") becomes a non-sequitur unless the comparable set is updated. The editor either supersedes C003 with a 1960-1965 comparable set or re-points to a different supporting frame.

The cascade decisions are recorded in `history.md` alongside the supersession entry for C001.

### Cross-pack supersession

Supersession is local to a pack. A claim in pack A superseded with `⊘` does not propagate to claims in pack B that referenced the original via `↔` (cross-pack see-also). Cross-pack effects are a [`RECONCILIATION.md`](RECONCILIATION.md) concern (currently a stub; full design deferred to v0.9 / v1.0).

The conservative reading for v0.8.0-preview: a cross-pack `↔` reference is a navigational pointer, not a binding dependency. Pack B's claim with `↔packA#section` does not require pack A to be reconciled before pack B is published. If pack A's referenced claim is superseded, pack B's `↔` continues to point at the same heading; the heading typically contains the successor claim by then.

---

## 7. Visibility

Visibility controls who can access a pack and how it behaves during bundling and sharing operations.

| Level | Who can access | Bundle behavior | Sync behavior |
|-------|----------------|-----------------|---------------|
| `private` | Pack owner only | Requires `--force` flag to bundle | Never syncs to shared systems |
| `shared` | Named collaborators | Bundles normally; private annotations stripped | Syncs to authorized systems only |
| `public` | Anyone | Full content bundled | May be published and distributed freely |

### Private Packs

Private packs contain knowledge that should not leave the owner's systems. Financial details, personal contacts, health information, legal matters.

**Constraints:**
- `kpack bundle` on a private pack fails with a warning unless `--force` is passed
- Private packs are excluded from shared search indexes
- Private packs never sync to collaborative platforms (e.g., team knowledge bases)
- Cross-pack `see_also` references TO private packs are allowed (the reference is visible; the content is not accessible to unauthorized consumers)

### Shared Packs

Shared packs are accessible to named collaborators. During bundling, **private annotations** (inline notes prefixed with `<!-- PRIVATE: ... -->`) are stripped from the output. The claims and evidence remain; the author's private commentary does not.

```markdown
- [C045] GridScale requested access to the full market analysis dataset (2026-03-22)
  {0.95|o|E045|2026-03-22} Follow-up meeting scheduled for next week.
  <!-- PRIVATE: Elena seemed very interested. Strong partnership signal. -->
```

In a shared bundle, the `<!-- PRIVATE: ... -->` comment is removed.

### Public Packs

Public packs have no access restrictions. They can be bundled, published, distributed, and referenced without constraint. Open-source project documentation, published research, public market reports.

### Interaction with `sensitivity`

`visibility` and `sensitivity` are independent fields. `sensitivity` (from PACK.yaml) describes the classification of the content. `visibility` describes who is allowed to access it.

| Combination | Valid | Example |
|-------------|-------|---------|
| `sensitivity: confidential` + `visibility: private` | Yes | Proprietary market intelligence |
| `sensitivity: confidential` + `visibility: shared` | Yes | Research shared with co-analysts |
| `sensitivity: confidential` + `visibility: public` | **No** | Lint error -- confidential content cannot be public |
| `sensitivity: public` + `visibility: private` | Yes | Public data you haven't published yet |

---

## 8. Lifecycle Transitions

```text
                    ┌──────────────────────────────┐
                    │         ACTIVE                │
                    │                               │
  ┌─────────┐      │  ┌───────────┐                │
  │  CREATE  │─────►│  │ permanent │ (evolves in    │
  └─────────┘      │  │           │  place forever) │
                    │  └───────────┘                │
  ┌─────────┐      │  ┌───────────┐   reconcile    │     ┌───────────┐
  │  CREATE  │─────►│  │ seasonal  │───────────────►│────►│  ARCHIVE  │
  └─────────┘      │  └───────────┘   (on expiry)  │     └───────────┘
                    │                               │           │
  ┌─────────┐      │  ┌───────────┐   reconcile    │     ┌─────▼─────┐
  │  CREATE  │─────►│  │ ephemeral │───────────────►│────►│  ARCHIVE  │
  └─────────┘      │  └───────────┘   (on expiry)  │     └───────────┘
                    │                               │           │
                    └──────────────────────────────┘           │
                              ▲                                │
                              │         kpack restore          │
                              └────────────────────────────────┘
```

### Lifecycle Events

| Event | Trigger | Effect |
|-------|---------|--------|
| Create | `kpack new` or manual | Pack enters active working set |
| Evolve | Claim supersession | Pack stays active, claims update |
| Archive trigger | `archive_after_days` elapsed since `freshness` | Reconciliation check begins |
| Reconcile | `kpack reconcile` | Claims reviewed against standing packs |
| Archive | All reconciled, or `--force` | Pack moves to `_archive/` |
| Restore | `kpack restore` | Pack moves from `_archive/` back to active |

### Permanent Pack Lifecycle

Permanent packs do not have an archive trigger. They evolve through claim supersession:

1. New information arrives
2. New claim is added (or existing claim superseded with `supersedes`)
3. `freshness` date is updated
4. `version` bumps to new CalVer date

A permanent pack may be manually archived if the domain itself becomes irrelevant (e.g., a superseded technology sector). This is a deliberate human decision, not an automated process.

### Seasonal Pack Lifecycle

1. Pack is created for a bounded period (e.g., "Q2 2026 market outlook")
2. Pack is actively used during the period
3. Retention period elapses
4. Reconciliation runs -- valuable claims are checked against standing packs
5. Pack archives to `_archive/`

### Ephemeral Pack Lifecycle

1. **Activation** -- Pack is created for a specific event. Research generates knowledge claims. Ideally, novel knowledge is created in standing packs first and referenced by the ephemeral pack.
2. **Event** -- The event occurs. New claims are captured.
3. **Consolidation** -- Knowledge claims migrate to standing packs (Section 4.1). This should happen soon after the event, while context is fresh. `consolidation.status` tracks progress.
4. **Retention** -- Period elapses (default: 14 days). Only operational and temporal content remains.
5. **Reconciliation** -- Safety net confirms no knowledge claims were missed (Section 4.2).
6. **Archive** -- Pack moves to `_archive/` with receipt. Clean -- no knowledge trapped.

---

## 9. KNOWLEDGE.yaml Integration

The root `KNOWLEDGE.yaml` index tracks lifecycle and archive status:

```yaml
packs:
  - name: solar-energy-market
    path: packs/research/solar-energy-market.kpack/
    lifecycle: permanent
    visibility: shared

  - name: webb-advisory-2026-03-22
    path: packs/meetings/webb-advisory-2026-03-22.kpack/
    lifecycle: ephemeral
    visibility: private
    archive_after: 2026-04-05         # Computed: created + 14 days

  - name: park-supply-review-2026-03-10
    path: packs/meetings/_archive/park-supply-review-2026-03-10.kpack/
    lifecycle: ephemeral
    visibility: private
    archived: true
    archived_at: 2026-03-25
    reconciliation: complete           # all claims reconciled
```

---

## 10. Design Principles

These principles are normative. Tooling that implements lifecycle management MUST adhere to them.

1. **Archive, never delete.** ([RATIONALE.md §1, Principle 19](RATIONALE.md).) Deletion requires explicit, deliberate action and should be exceptional. Archival is the default lifecycle outcome.

2. **Reconcile before archive.** ([RATIONALE.md §1, Principle 21](RATIONALE.md).) Every claim in an ephemeral pack represents knowledge that someone thought was worth capturing. Before burying it in an archive, verify it landed somewhere permanent. Orphan claims are the system catching what humans miss.

3. **Close the loop explicitly.** The reconciliation report is not a formality -- it is the mechanism that makes archival psychologically safe. Users trust the system because it proves nothing was lost, not because it promises nothing was lost.

4. **1-2 click retrieval.** An archived pack must be loadable with the same command as an active pack. Search must include archived packs (with lower ranking). If retrieval from the archive is difficult, users will resist archiving -- and the working set will grow without bound.

5. **Defaults favor safety.** The default lifecycle type is `permanent` (never auto-archived). The default archive policy is `reconcile` (check before archiving). The default visibility is `private` (no accidental sharing). Unsafe behavior requires explicit opt-in.

6. **Visibility is access control, not classification.** `visibility` says who can see the pack. `sensitivity` says what kind of information it contains. These are independent axes. A pack can be publicly accessible but low-sensitivity, or highly sensitive but shared with co-analysts.
