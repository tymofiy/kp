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
4. **Contradictions are knowledge** — Disagreements between claims are surfaced, not resolved. Resolution is context-dependent. (This is *epistemic* pluralism, not a metaphysical claim: the format records that observers hold conflicting beliefs, not that a contradiction is true of the world — paraconsistent at the level of the pack while leaving the world bivalent.)
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
21. **Reconcile before archive** — Ephemeral packs can contain knowledge that does not exist elsewhere. Before archiving, review which findings need standing access and which accounts remain in the retained event record. Preserve attribution, scope and references to the original material. Flag unresolved placement decisions; archival must not silently discard knowledge. See [LIFECYCLE.md §4](LIFECYCLE.md#4-consolidation--reconciliation).
22. **Knowledge is the source (pack-as-master)** — Knowledge packs are the canonical source of truth for their epistemic contents. Agent instruction files, operations (planning, tasks), and presentations (slides, documents) reference knowledge packs but are not knowledge themselves. Databases, caches, and search indices that store or project pack data are derived representations — operational infrastructure that serves packs, not the other way around. When a derived representation disagrees with the pack, the pack is correct. Any index can be dropped and rebuilt from packs. Packs can be stored in any medium (files, databases, caches) without changing their authority. Only knowledge is a knowledge pack. (See [STORAGE.md](STORAGE.md).)
23. **Locale first, then surface** — Multilingual views are organized by locale, then by surface type: `views/uk/voice/briefing.md`, not `views/voice/uk/briefing.md`. Locale is the higher-order grouping.
24. **Keep context that changes meaning** — Claims state what is believed and why; views present that knowledge with the qualifications needed to understand it. Names, roles, dates, methods and decision context belong with a claim when they affect its attribution, scope, interpretation or reasons for change. Fuller source narratives belong in evidence.md. Remove incidental process narration only when the assertion's meaning remains intact. Neither a person's request nor a tool's involvement alone establishes a conclusion, but an attributed request, decision or method can itself be knowledge worth retaining.
25. **Short-term memory, long-term memory** — Standing packs organize lasting knowledge by subject. Ephemeral packs bring material together for a particular event or task. These are organizational analogies, not a model's internal memory. Consolidation makes useful findings available to later work while preserving their source context and references to the retained event record. Event-specific roles, experiences and decisions can remain valuable after the event; archival placement does not make them non-knowledge. (See [LIFECYCLE.md §1.1](LIFECYCLE.md).)

> **Independence.** The ownership and capture-resistance commitments these principles imply —
> zero-dependency readability, freedom to fork, no required registry, optional-not-mandatory
> cryptography — are stated as a companion: see [INDEPENDENCE.md](INDEPENDENCE.md). Their throughline
> is *subtraction, not addition*: the format stays ownable by requiring less, because every dependency
> removed is a chokepoint that cannot be captured.

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

## 3. Cognitive Perception Layer

The `display` block in PACK.yaml and the per-view `hint` field help people recognize a pack, understand its purpose and find relevant material. The normative spec for these fields lives in [SPEC.md §18](SPEC.md) and [SPEC.md §3](SPEC.md) (manifest); this section explains how to author them. Its time budgets are design targets, not measured performance or extra conformance requirements.

### The Primary Constraint: Cognitive Load

**Make introductory display fields easy to understand without changing their meaning.** A person encountering the pack may:

- Have never seen it before
- Be deciding whether to open it
- Be unfamiliar with the domain
- Need a clear route to the detailed record

Use plain language and explain unfamiliar terms in short introductions. Keep attribution, uncertainty and scope when they affect meaning. Do not remove a necessary technical detail merely to make a sentence shorter.

Full display and voice views serve their declared audience. A specialist view may need terminology and detail that a brief introduction does not. Both should remain faithful to the record and keep a route to supporting claims and sources.

An accessible view helps its audience understand rich knowledge. It is not a replacement for the full record. Selecting relevant material should preserve the qualifications needed for the task.

### Perception Stages

A useful introductory view supports four common steps. The timings below are authoring targets for a brief introduction, not universal measurements of how people read.

1. **Recognize** (< 1 second) — What is this? Can I identify it in a list, on a tab, in a breadcrumb?
2. **Comprehend** (< 3 seconds) — What is it about? What does it address?
3. **Engage** (< 5 seconds) — Why should I care? What makes me want to read further?
4. **Navigate** (< 10 seconds) — Which section should I open? What will I find there?

Renderers can use the SPEC's display metadata to support these steps. The appropriate detail and time depend on the audience and task.

### Why each `display` field exists

#### `short_title` (Recognition)

A human scanning a list of 20 packs, or glancing at a tab bar, or hearing a voice assistant name a pack — they need to recognize THIS pack in under one second. The full title ("Utility-Scale Solar Energy Market Analysis and Cost Trajectories") takes too long. The abbreviation ("SEM") requires insider knowledge. The short title occupies the sweet spot: long enough to be unambiguous, short enough to be instant.

The name a human would use to refer to this pack in conversation. 2-4 words. Must be unambiguous without the full title.

| Good | Bad | Why |
|------|-----|-----|
| "Solar Market" | "Utility-Scale Solar Energy Market Analysis and Cost Trajectories" | Too long — the full title belongs in the H1, not here |
| "Wind Outlook" | "Wind Energy Assessment" | "Assessment" is vague; "Outlook" implies forward-looking analysis |
| "Battery Storage" | "battery-storage-economics-2026-03" | File names are not titles |

#### `abbreviation` (Tight Contexts)

Some display contexts have almost no space — a mobile breadcrumb, a badge next to a notification, a voice assistant referencing a pack mid-sentence. The abbreviation is the absolute minimum identifier. It sacrifices clarity for brevity, which is why it exists alongside `short_title`, not instead of it.

2-5 characters. Must be pronounceable or a recognized acronym. Used in badges, breadcrumbs, tabs.

| Good | Bad | Why |
|------|-----|-----|
| "SEM" | "USEMPV" | Not pronounceable |
| "Wind" | "WE" | Ambiguous without context |

#### `tagline` (Comprehension)

After recognizing a pack by title, the next question is "what is this about?" The tagline answers that in a single breath. It's the bridge between the title (which names the thing) and the content (which explains it in full). Without a tagline, the human must open the pack and read before they can even assess relevance. The tagline prevents that wasted effort — it's a promise of what's inside, delivered before the reader commits.

One sentence that tells a stranger what the subject IS. Not what the pack contains — what the subject is about. Should be readable aloud in under 5 seconds. Natural language, not a label.

| Good | Bad | Why |
|------|-----|-----|
| "Utility-scale solar market trends and cost analysis" | "Executive summary with key metrics and status" | That describes the pack format, not the subject |
| "Supply chain risks for global solar deployment" | "Solar risk overview pack" | Reads like a filename, not a sentence |
| "Grid storage economics for renewable integration" | "Battery analysis pack" | The good version answers WHAT and WHY |

#### `hook` (Engagement)

Comprehension without engagement is a dead end. A person can understand what a pack is about and still not care. The hook exists because human attention is not given — it's earned. A tagline tells you what the plate is; the hook is the aroma that makes you want to eat. It's the most emotionally or intellectually compelling sentence in the entire pack, surfaced to the cover because burying it on page 3 means nobody gets there.

The single most compelling sentence in the entire pack. A provocation, a surprising insight, or a promise that creates the desire to read further. If you had to convince someone to open this pack with one sentence, this is it.

| Good | Bad | Why |
|------|-----|-----|
| "The real competitor is the status quo of neglect, not other platforms." | "This pack covers risks, timeline, and team." | That's a table of contents, not a hook |
| "We're raising 1.5M euro to capture the 18-month window before incumbents wake up." | "Fundraising information for Q2 2026." | No urgency, no insight, no reason to care |

If you can't find a hook, the pack may not have a clear thesis yet. That's a content problem, not a display problem.

#### `hint` per view (Navigation)

The cover shows sections, but a title alone ("Risks", "Timeline") is a label — it tells you the category, not the value. A human deciding where to click needs to know what they'll GET from opening that section, not what category it belongs to. The hint transforms a menu of labels into a menu of promises. Without it, navigation is a guessing game — the reader has to open sections speculatively. With it, they open with intent.

One sentence per section that helps a human decide: should I open this? Describes the VALUE of the section, not its structure. Max ~15 words.

| Good | Bad | Why |
|------|-----|-----|
| "Three risks that could block the Sep 2026 pilot" | "Risk register with 3 rows" | Structure is not value |
| "6 months built, 5 months to launch" | "Timeline table" | The good version tells you the insight |
| "What to say when Scott asks about AI safety" | "Technical Q&A section" | The good version tells you what you'll GET |

### The Stranger Test

After authoring all display fields, read them in sequence:

> **[short_title]** — [tagline]. [hook]. Sections: [hint 1], [hint 2], [hint 3].

If a stranger reading this sequence can answer "what is this, why should I care, and where should I start?" — the fields pass. If not, rewrite.

### What these fields are NOT

- They are not marketing copy (that belongs in a website, not a spec).
- They are not aesthetic choices (fonts, colors, layout are renderer decisions).
- They are not summaries of the content (that's what views are for).

They are **cognitive handles** — the minimum information a human brain needs to recognize, locate, engage with, and navigate this pack across any display context.

---

## 4. Relationship to Existing Standards

KP:1 sits in a small ecosystem of AI-facing content formats. The table below records how KP:1 relates to each, where the boundary is, and what each format is for.

| Standard | Relationship |
|----------|-------------|
| Agent instruction files (e.g., AGENTS.md) | Orthogonal — agent instruction files configure behavior, Knowledge Packs provide facts |
| Agent Skills (SKILL.md) | Complementary — Skills declare `requires_knowledge` for pack dependencies |
| MCP Resources | Knowledge Packs can be served as MCP resources at runtime |
| llms.txt | Discovery — llms.txt could point to available Knowledge Packs |
| Entity-Claim-Evidence (ECS) systems | Implementation pattern — ECS is an operational index; Knowledge Packs are the canonical source. See [STORAGE.md](STORAGE.md) |
| schema.org / JSON-LD knowledge graphs | Adjacent — schema.org/JSON-LD is the dominant production approach for structured knowledge on the web. KP:1 differs in three ways: (1) plain-text density (`{0.95\|i\|E001\|2026-03-01}` is materially more token-efficient than the equivalent JSON-LD object); (2) first-class uncertainty and contradiction primitives that JSON-LD vocabularies do not standardize; (3) the three-surface architecture (claims / display / voice) is intrinsic, not a rendering layer over a single semantic graph. Both approaches can compose: a KP:1 pack can map to JSON-LD via [MAPPING.md](MAPPING.md). |
| JSON-LD / RDF | Inspiration — semantic structure, but optimized for neural nets, not symbol processors |
| Nanopublications | Spiritual ancestor — assertion + provenance, but in markdown, not RDF |

For the field-by-field translation analysis between KP:1 and RDF / JSON-LD / PROV-O / Nanopublications, see [MAPPING.md](MAPPING.md).

---

*This file is companion to [SPEC.md](SPEC.md) and [CORE.md](CORE.md). Where SPEC.md or CORE.md specify form, RATIONALE.md explains why. Where the two appear to conflict, SPEC.md and CORE.md are authoritative.*
