<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# KP:1 — Rationale and Positioning

> **Status:** Draft (informative — not normative for KP:1 conformance)
> **Date:** 2026-05-09

This companion holds the parts of the KP:1 specification that are
**rationale, philosophy, and positioning** rather than implementable
contract. Sections that previously lived in SPEC.md as numbered chapters
(§15 Design Principles, §17 Style Systems, §20 Relationship to Existing
Standards) are collected here so that SPEC.md and CORE.md can serve their
implementer-facing purpose without interleaving rationale with normative
prose.

This document is **informative only**. Where it appears to specify
behavior that is not also specified in CORE.md, SPEC.md, or a
topic-authoritative companion, the rationale here does not constrain
implementations. It records the reasoning behind the format's choices.

---

## 1. Design Principles

The 25 principles below informed the format's choices. They are reference
material for understanding why KP:1 is shaped the way it is. They are not
themselves a conformance contract — the conformance contract lives in
CORE.md, the JSON Schema, and the PEG grammar.

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
22. **Knowledge is the source (pack-as-master)** — Knowledge packs are the canonical source of truth for their epistemic contents. Agent instruction files, operations (planning, tasks), and presentations (slides, documents) reference knowledge packs but are not knowledge themselves. Databases, caches, and search indices that store or project pack data are derived representations — operational infrastructure that serves packs, not the other way around. When a derived representation disagrees with the pack, the pack is correct. Any index can be dropped and rebuilt from packs. Packs can be stored in any medium (files, databases, caches) without changing their authority. Only knowledge is a knowledge pack. (See [STORAGE.md](STORAGE.md).)
23. **Locale first, then surface** — Multilingual views are organized by locale, then by surface type: `views/uk/voice/briefing.md`, not `views/voice/uk/briefing.md`. Locale is the higher-order grouping.
24. **Knowledge, not journal** — Claims state what is believed and why. Views render what something IS. Neither describes the process of arriving at the knowledge: who commissioned a finding, which meeting crystallized an insight, which tool generated a draft, which framework was applied. Process provenance belongs in evidence.md (as source documentation) or nowhere. A claim's confidence and evidence links carry its epistemic provenance. Narrative provenance ("a stakeholder asked for this", "crystallized during the Q1 review session", "generated by an LLM") leaks operational history into canonical knowledge. Test: remove all proper nouns of people, meetings, tools, and session dates from a claim's context prose — if the epistemic content is intact, the claim is clean.
25. **Short-term memory, long-term memory** — Standing packs (permanent, seasonal) are long-term memory: organized by semantic domain, where things that are *about* the same subject cluster together regardless of when or how they were learned. Ephemeral packs are short-term memory: organized by *proximity of need*, where things needed together in a specific moment cluster together regardless of domain. These are different cognitive architectures serving different purposes — both legitimate, but with different lifespans. Novel knowledge created during short-term operations (meeting prep, research sprints) must consolidate into its long-term semantic home before the ephemeral pack archives. The ephemeral pack is the scaffold, not the building. Consolidation is not a safety net before archival — it is the primary purpose of the ephemeral lifecycle. (See [LIFECYCLE.md §1.1](LIFECYCLE.md).)

---

## 2. Style Systems

A style system is an external, versioned specification that tells a renderer how to visually present view content. **Style systems are NOT part of the Knowledge Pack** — they are referenced by packs and defined externally. This section records the rationale for keeping them external and a recommended shape for producers building their own.

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

## 3. Relationship to Existing Standards

KP:1 sits in a small ecosystem of AI-facing content formats. The table below records how KP:1 relates to each, where the boundary is, and what each format is for.

| Standard | Relationship |
|----------|-------------|
| Agent instruction files (e.g., AGENTS.md) | Orthogonal — agent instruction files configure behavior, Knowledge Packs provide facts |
| Agent Skills (SKILL.md) | Complementary — Skills declare `requires_knowledge` for pack dependencies |
| MCP Resources | Knowledge Packs can be served as MCP resources at runtime |
| llms.txt | Discovery — llms.txt could point to available Knowledge Packs |
| Entity-Claim-Evidence (ECS) systems | Implementation pattern — ECS is an operational index; Knowledge Packs are the canonical source. See [STORAGE.md](STORAGE.md) |
| JSON-LD / RDF | Inspiration — semantic structure, but optimized for neural nets, not symbol processors |
| Nanopublications | Spiritual ancestor — assertion + provenance, but in markdown, not RDF |

For the field-by-field translation analysis between KP:1 and RDF / JSON-LD / PROV-O / Nanopublications, see [MAPPING.md](MAPPING.md).

---

## Status of §18 (Cognitive Perception Layer)

[SPEC.md §18](SPEC.md) is intentionally retained in SPEC.md for v0.8.0-preview because its content is hybrid — partly normative (the `display` block field semantics, the fallback hierarchy) and partly rationale (the perception stages, the Stranger Test, the Why-it-exists boxes). A future pass may bifurcate §18 with the normative `display` field specification consolidated into §3 of SPEC.md (PACK.yaml manifest) and the rationale moved to a new RATIONALE.md §4. That work is deferred so the bifurcation pattern can ship without destabilizing §18's hybrid content.

---

*This file is companion to [SPEC.md](SPEC.md) and [CORE.md](CORE.md). Where SPEC.md or CORE.md specify form, RATIONALE.md explains why. Where the two appear to conflict, SPEC.md and CORE.md are authoritative.*
