<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Pack Organization — Knowledge Pack Companion Spec

> **Date:** 2026-03-22
> **Status:** Draft
> **Decisions:** D3 (spec location), D12 (nested categories)

---

## 1. Repository Structure

A knowledge pack workspace separates the format specification, the pack content, and the supporting tooling. The example below shows one reasonable layout — implementations are free to organize differently as long as the pack format itself is preserved.

```text
your-knowledge-repo/
├── spec/                           # THE FORMAT — defines what a pack is
│   ├── CORE.md                     # Implementer surface (parser/validator contract)
│   ├── SPEC.md                     # Full normative spec + rationale + ecosystem
│   ├── README.md                   # Lane overview (CORE / SPEC / companions)
│   ├── VOICE.md                    # Voice view format
│   ├── COMPOSITION.md              # Meeting pack composition
│   ├── LIFECYCLE.md                # Pack lifecycle management
│   ├── MULTILINGUAL.md             # Locale conventions
│   ├── ORGANIZATION.md             # This file (pack categories and repo layout)
│   ├── CONSISTENCY.md              # Cross-pack consistency patrol
│   ├── CONVENTIONS.md              # Linguistic conventions
│   ├── STORAGE.md                  # Storage formats and serialization
│   ├── BUNDLE.md                   # Export/sharing format
│   ├── ARCHIVE.md                  # ZIP archive, integrity chain, signatures
│   ├── DEFINITIONS.md              # Definition and policy document kinds
│   ├── EXTENSIONS.md               # Producer-defined `extensions.*` blocks catalogue
│   ├── NOTES.md                    # AI note-taking metadata
│   ├── PLAYBACK.md                 # Self-driving presentation playback (experimental)
│   ├── RECONCILIATION.md           # Cross-pack reconciliation (stub — design deferred)
│   ├── MAPPING.md                  # Mapping to RDF/JSON-LD/PROV-O (informative)
│   ├── RATIONALE.md                # Design principles, positioning, philosophy (informative)
│   └── CHANGELOG.md                # Version history
│
├── packs/                          # THE CONTENT — actual knowledge packs
│   ├── KNOWLEDGE.yaml              # Pack index (discovery and routing)
│   ├── <domain-a>/                 # Domain-grouped standing packs
│   │   └── <pack-1>.kpack/
│   ├── <domain-b>/
│   │   ├── <pack-2>.kpack/
│   │   └── <pack-3>.kpack/
│   ├── meetings/                   # Ephemeral meeting packs
│   │   └── _archive/              # Auto-archived past meetings
│   └── (additional categories as needed)
│
├── templates/                      # Pack scaffolds by category
│   ├── meeting-prep.template/
│   └── project.template/
│
├── styles/                         # Narrative style definitions
├── inbox/                          # Unprocessed incoming material
└── tools/                          # CLI tooling (e.g., a `kpack` command)
```

The categories under `packs/` (`meetings/`, plus whatever domain folders fit your work) are illustrative. The only requirement is that each `.kpack/` directory follows the file structure defined in SPEC.md.

---

## 2. The Two-Zone Model

The repository has two zones:

| Zone | Contents | Rule |
|------|----------|------|
| **`packs/`** | Clean KP:1 knowledge packs only | Everything here is structured, validated, trustworthy |
| **Everything else** | Legacy data, tooling, process files | Untouched until ready to migrate |

### The Amnesia Test

If you looked at this repository with no context, you should be able to tell what's what:

- `spec/` → "this defines a format"
- `packs/` → "this contains structured knowledge"
- `packs/energy/solar-energy-market.kpack/` → "this is a knowledge pack about the solar energy market, filed under energy"
- `entities/` → "this is older, unstructured data"

The `.kpack` directory extension is the ultimate differentiator. Any directory ending in `.kpack` is a knowledge pack. Nothing else uses this extension.

---

## 3. Nested Categories

Packs are organized into category subdirectories within `packs/`. Categories provide cognitive clarity — you know where to look.

### Working Set (Not Canonical)

These categories are a starting point. They will evolve through use as more packs are created and migrated:

| Category | Purpose | Example packs |
|----------|---------|---------------|
| `energy/` | Market analysis, technology, policy | `solar-energy-market`, `wind-energy-market` |
| `meetings/` | Ephemeral, per-meeting, auto-archived | `<topic>-<YYYY-MM-DD>` |
| `creative/` | Personal creative projects | `<your-pack-name>` |
| `technical/` | Domain-agnostic technical knowledge | `ai-models`, `architecture-decisions` |

Additional categories will emerge as migration surfaces the need. The principle is:

- **Resist proliferation** — When in doubt, use an existing category
- **Split when cognitive load demands it** — If a category has 20+ packs spanning clearly different domains, split
- **Categories can be renamed** — Renaming is cheap (git move). Don't agonize over names early.

### What Doesn't Go in Categories

- The `KNOWLEDGE.yaml` index stays at `packs/` root (not inside a category)
- Templates stay in `templates/` (not inside `packs/`)
- The spec stays in `spec/` (not inside `packs/`)

---

## 4. Migration Strategy

Legacy data migrates from the old zone to `packs/` gradually, on demand:

### Migration Workflow

1. Pick something from the old zone (e.g., `entities/companies/acme-solar.md`)
2. Determine which pack it belongs to (e.g., business pack, or a contacts pack)
3. Convert the information into claims and evidence
4. Add to existing pack or create new pack in `packs/{category}/`
5. Delete the source from the old zone (or leave it — no pressure)

### Migration Principles

- **No rush** — Migrate when you touch something, not all at once
- **Don't restructure the old zone** — Leave legacy directories exactly as they are
- **One-way migration** — Knowledge flows from old to new, never back
- **The old zone shrinks over time** — Eventually it's empty and can be deleted
- **Not everything migrates** — Some legacy content is truly obsolete and can be left or deleted

---

## 5. KNOWLEDGE.yaml Updates

The pack index must reflect the category structure. Paths are relative to `packs/`:

```yaml
packs:
  # ── Energy ──
  - name: solar-energy-market
    path: energy/solar-energy-market.kpack/
    tier: hub
    category: energy
    summary: "Utility-scale solar market trends, costs, and adoption"
    topics: [solar, PV, market, cost, adoption]

  # ── Technical ──
  - name: battery-storage-economics
    path: technical/battery-storage-economics.kpack/
    tier: hub
    category: technical
    summary: "Battery storage cost trajectories, chemistry, deployment economics"
    topics: [battery, storage, lithium, cost, deployment]

  # ── Meetings ──
  - name: vendor-review-2025-Q4
    path: meetings/vendor-review-2025-Q4.kpack/
    tier: standalone
    category: meetings
    lifecycle: ephemeral
    summary: "Vendor review — supply chain status, module pricing"
    topics: [meeting, vendor, supply-chain]
```

The `category` field is informational (the directory structure is authoritative), but it enables filtering: "show me all business packs" without directory traversal.
