<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Why Not Existing Standards?

> Honest comparison of KP:1 against adjacent formats, tools, and protocols.
>
> **Audience:** Knowledge representation researchers, semantic web practitioners,
> AI engineers, and anyone whose first reaction to KP:1 is "why not just use X?"
>
> **Posture:** Truth over posture. Each tradition does things KP:1 does not.
> KP:1 does one thing none of them do. This document makes both sides explicit.

---

## The Short Answer

KP:1 is a portable, plain-text format for representing **epistemic state** —
what someone believes, how confident they are, based on what evidence, in tension
with what other beliefs, as understood at a particular moment in time.

No existing format represents all of these properties together. Many formats
represent some of them better than KP:1 does. Existing standards *can* model
most of what KP:1 does — but usually at the cost of heavier tooling, weaker
authorability, or splitting the problem across incompatible layers. The question
is not "is KP:1 better than X?" but "does the specific combination KP:1
provides fill a gap that X leaves open?"

KP:1 is best understood as a **thin waist** between formal knowledge
representation systems and LLM context pipelines — a constrained Markdown
format for epistemic state that composes with existing standards rather than
replacing them.

For each tradition below, we answer three questions:

1. **What does it do well?** — genuine strengths we do not claim to match
2. **What does KP:1 add?** — the specific gap KP:1 is designed to fill
3. **What does KP:1 not do?** — explicit concessions

---

## 1. RDF / JSON-LD / PROV-O (Semantic Web)

### What it does well

The semantic web family is the most mature infrastructure for structured
knowledge on the web. RDF provides a universal data model (subject-predicate-
object triples) with global identity via URIs. JSON-LD makes RDF embeddable in
web APIs. OWL enables formal ontological reasoning. PROV-O provides a rigorous
provenance model with well-defined semantics. SKOS handles taxonomy and concept
schemes. SHACL validates graph shapes.

These standards have 20+ years of implementation, tooling, and academic
scrutiny. They interoperate across organizations through shared ontologies.
They support formal reasoning that KP:1 does not attempt.

### What KP:1 adds

RDF represents **relationships between entities**. KP:1 represents **beliefs
about entities** — a different layer.

In RDF, a triple like `<Company> <revenue> "2B"` is an assertion of fact.
You *can* represent "we believe revenue is approximately $2 billion, confidence
0.72, based on an analyst report from March, which contradicts a competitor
estimate of $1.5 billion, and we haven't investigated this deeply" — using
reification, RDF-star, named graphs, PROV-O annotations, or nanopublications.
But the epistemic metadata is always an annotation on the primary
representation, never the primary representation itself.

In KP:1, the epistemic state **is** the content:

```markdown
- revenue_estimate [0.72|moderate] Revenue is approximately $2B
  ~ revenue_lower_estimate :: conflicting-data "Competitor analysis suggests $1.5B"
  @source: analyst-report-march-2026 [primary]
```

Confidence, investigation depth, typed contradiction, and evidence attribution
are first-class — not annotations on something else.

Additionally:

- **LLM-native consumption.** KP:1 is plain-text Markdown, consumable by any
  language model without parsing, transformation, or SPARQL. RDF requires
  serialization choices (Turtle, N-Triples, JSON-LD) and typically a query
  layer between the data and the consumer.
- **Zero infrastructure.** A Knowledge Pack is a directory of text files. No
  triple store, no SPARQL endpoint, no ontology registry. This is a design
  choice (the Voyager Principle), not an oversight.
- **Typed contradiction.** RDF treats inconsistency as an error. KP:1 treats
  it as information — two claims can coexist in typed tension (conflicting-data,
  methodological, temporal, perspective) because real-world knowledge contains
  genuine disagreements.

### What KP:1 does not do

- **Global identity.** KP:1 claim IDs are pack-local. RDF URIs are globally
  unique and dereferenceable. If you need to merge knowledge graphs across
  organizations, RDF's identity model is stronger.
- **Formal reasoning.** KP:1 has no inference rules, no entailment regime, no
  model-theoretic semantics. OWL can derive new knowledge from existing
  assertions. KP:1 relies on the consuming intelligence (human or AI) for
  inference.
- **Interoperability at scale.** The semantic web's shared ontologies enable
  systems that have never communicated to exchange structured data. KP:1 packs
  are self-contained units — they compose through lifecycle operations, not
  through shared schemas.
- **Mature tooling ecosystem.** RDF has decades of parsers, validators,
  visualizers, and query engines. KP:1 has a spec and two examples.

### The honest framing

KP:1 is not competing with RDF. It sits at a different layer — epistemic state
rather than entity relationships. A future bridge that exports KP:1 claims as
nanopublication-style RDF (with explicit loss/gain documentation) would be
valuable. That bridge does not exist yet.

---

## 2. Knowledge Graphs (Neo4j, Wikidata)

### What they do well

Knowledge graphs excel at representing entities, their properties, and
relationships — then querying across those relationships at scale. Neo4j
handles traversals over millions of nodes with Cypher (now backed by ISO GQL).
Wikidata provides a collaboratively maintained, globally identified knowledge
base with 100M+ items — and its data model already supports statements with
qualifiers, references, ranks, and constraints. Both support graph queries
that can answer structural questions ("which companies in sector X have revenue
above Y and are connected to person Z?").

### What KP:1 adds

Knowledge graphs represent **what is known**. KP:1 represents **what someone
believes and how sure they are**.

A Wikidata entry for a company's revenue is a community-consensus fact. A KP:1
claim about the same revenue includes: whose belief it is, how confident they
are, what evidence supports it, what investigation produced it, and whether it
contradicts other beliefs held simultaneously.

Knowledge graphs are infrastructure — they require servers, databases, query
languages, and maintenance. A Knowledge Pack is a portable artifact — a
directory of files that can be emailed, committed to git, or dropped into an
LLM context window.

### What KP:1 does not do

- **Large-scale querying.** You cannot run Cypher or SPARQL against a Knowledge
  Pack. Graph databases are purpose-built for structural traversal; KP:1 is not.
- **Entity resolution at scale.** Knowledge graphs have sophisticated identity
  and disambiguation systems. KP:1's entity references are local.
- **Collaborative editing.** Wikidata supports thousands of concurrent editors
  with conflict resolution. KP:1 is authored by individuals or small teams,
  versioned through git.

### The honest framing

Knowledge graphs and Knowledge Packs serve different functions. A graph
database might index and query the contents of many Knowledge Packs as a
derived representation. The pack is the authored artifact; the graph is the
queryable infrastructure built from it.

---

## 3. PKM Tools (Obsidian, Notion, Roam)

### What they do well

Personal knowledge management tools optimize for **authoring experience**.
Obsidian provides a beautiful graph view, bidirectional linking, and a plugin
ecosystem. Notion offers collaborative databases with flexible views. Roam
pioneered block-level referencing and daily notes. All three make it easy to
capture, organize, and navigate personal knowledge.

### What KP:1 adds

PKM tools model **notes** — unstructured or semi-structured text organized by
links and tags. KP:1 models **epistemic state** — structured claims with
machine-readable confidence, evidence chains, typed contradictions, and
lifecycle.

The difference matters for AI consumption. An LLM reading an Obsidian vault
gets text and links. It cannot distinguish high-confidence claims from
speculation, cannot identify which sources support which beliefs, cannot detect
that two notes contradict each other, and cannot determine how thoroughly a
topic has been investigated.

An LLM reading a Knowledge Pack gets all of this as structured, parseable
content — not because the format is more complex, but because it requires the
author to make epistemic commitments explicit.

### What KP:1 does not do

- **Friendly authoring.** PKM tools are designed for humans to write in
  comfortably. KP:1's reasoning surface (claims.md) is optimized for
  information density, not writing comfort. The format assumes tooling will
  mediate the authoring experience.
- **Exploratory note-taking.** KP:1 requires structured claims with confidence
  and evidence. Early-stage thinking that hasn't crystallized into beliefs
  doesn't belong in a Knowledge Pack.
- **Graph visualization.** Obsidian's graph view is a powerful thinking tool.
  KP:1 has no visual interface — it's a data format, not an application.
- **Plugin ecosystem.** PKM tools have thousands of community extensions.
  KP:1 has a reference parser on the roadmap.

### The honest framing

PKM tools and KP:1 address different stages of the knowledge lifecycle. Notes
capture and explore. Knowledge Packs formalize and preserve. A plausible
workflow: think in Obsidian, formalize in KP:1 when beliefs stabilize. The two
are complementary, not competing.

---

## 4. RAG / StructRAG / Context Engineering

### What they do well

Retrieval-Augmented Generation is the dominant pattern for grounding LLM
responses in external knowledge. Vector databases (Pinecone, Weaviate, Chroma)
enable semantic search over document chunks. StructRAG and similar approaches
add structure — tables, hierarchies, knowledge graphs — to improve retrieval
quality. Context engineering (prompt design, context window management,
tool-use orchestration) has become a discipline in itself.

These systems solve the practical problem of getting relevant information into
an LLM's context window at inference time. GraphRAG (Microsoft, 2024) and
similar approaches extract entity-relationship graphs from text corpora to
improve query-focused summarization.

Agent memory systems (Mem0, Letta, LangMem) represent a related but distinct
category: they manage runtime episodic and semantic memory for AI agents,
typically backed by vector stores and databases.

### What KP:1 adds

RAG retrieves **documents**. Agent memory manages **runtime state**. KP:1
represents **authored beliefs**.

The strongest contemporary objection is: "Context windows are now 2M+ tokens.
Why pre-structure knowledge when I can dump raw documents into the prompt and
let the model figure it out?" The answer is not about context size — it's
about **inference-time cognitive load**. Models suffer from "lost in the middle"
effects and hallucinate when synthesizing contradicting claims from unstructured
text. Pre-structuring doesn't save tokens; it saves the model from having to
reconstruct epistemic state every time.

A RAG system might retrieve three document chunks about a market's size. The LLM
sees three text fragments and must infer: are these consistent? Which is more
recent? How confident should I be? The epistemic work happens at inference time,
every time, with no guarantee of consistency.

A Knowledge Pack pre-structures this epistemic work: the claims are stated with
confidence, the contradictions are typed, the evidence is attributed, the
investigation depth is recorded. The AI doesn't need to reconstruct the
epistemic state from raw text — it's already represented.

A Knowledge Pack can also serve as clean, structured input to a GraphRAG
pipeline, or as the authored output that a GraphRAG extraction process feeds
into for human review and confidence annotation.

This is the core question the prior art analysis identifies: **does author-
curated, pre-structured epistemic state outperform inference-time structuring
for the tasks KP:1 is designed to support?** That question requires empirical
validation, not theoretical argument.

### What KP:1 does not do

- **Retrieval.** KP:1 is a representation format, not a retrieval system. It's
  the input to a RAG pipeline, not the pipeline itself. You still need a way
  to select which pack (or which claims within a pack) to load into context.
- **Scale to millions of documents.** RAG pipelines handle large corpora.
  A single Knowledge Pack represents one domain's epistemic state — it is a
  curated artifact, not a document index.
- **Real-time knowledge.** RAG can retrieve up-to-the-minute information.
  Knowledge Packs are versioned snapshots — they capture belief at a point in
  time, not live data.
- **Automatic structuring.** StructRAG can auto-generate structure from
  unstructured text. KP:1 requires deliberate authoring of claims and evidence.

### The honest framing

KP:1 and RAG operate at different layers. RAG is plumbing — how knowledge gets
into context. KP:1 is packaging — how knowledge is represented once it's there.
Agent memory is runtime state management — how an AI remembers across sessions.
A Knowledge Pack can be the source that any of these systems consume. The three
are complementary.

---

## 5. Argumentation Frameworks (IBIS, Toulmin)

### What they do well

IBIS (Issue-Based Information System) provides a clean model for deliberation:
issues, positions, and arguments. Toulmin's model decomposes arguments into
claims, grounds, warrants, backing, qualifiers, and rebuttals. The Argument
Interchange Format (AIF) provides a formal ontology for representing argument
networks across systems. All have decades of academic grounding and are
well-understood in argumentation theory and design rationale research.

These frameworks excel at modeling **the structure of arguments and disputes**.

### What KP:1 adds

Argumentation frameworks model **how arguments relate to each other**. KP:1
models **what is believed as a result** — the epistemic state that emerges from
(or exists alongside) argumentation.

KP:1 borrows from this tradition: typed contradictions are explicitly influenced
by argumentation theory. But KP:1 is not an argumentation framework. It does
not model the back-and-forth of debate, the warrant structure of individual
arguments, or the procedural rules of deliberation.

What KP:1 adds to the argumentation tradition:

- **Confidence as a continuous value** alongside investigation depth — not just
  "supported/attacked" but "how sure, and how thoroughly investigated?"
- **Lifecycle and consolidation** — beliefs evolve, get superseded, and
  consolidate over time. Argumentation frameworks model a snapshot of a debate;
  KP:1 models the evolving state of belief.
- **Multi-surface rendering** — the same beliefs can be rendered for reasoning
  (dense, structured), display (human-readable), or voice (spoken delivery).
  This is an engineering advantage for practical use, not a scholarly claim
  about argumentation theory.

### What KP:1 does not do

- **Model argument structure.** Toulmin's warrant/backing/rebuttal decomposition
  is richer than KP:1's evidence + contradiction model. AIF's formal ontology
  enables computational argument analysis. If you need to analyze the logical
  structure of arguments, these frameworks are better.
- **Support formal deliberation.** IBIS is designed for structured decision-
  making with multiple participants. KP:1 is an individual or small-team
  representation, not a deliberation protocol.
- **Provide formal dispute resolution.** Argumentation frameworks can define
  winning conditions and acceptability semantics (Dung-style abstract
  argumentation). KP:1 preserves contradictions without resolving them.

### The honest framing

KP:1 is genealogically related to argumentation frameworks — it inherits the
insight that disagreement is information. But it's a different kind of artifact:
a representation of resulting belief state, not a model of the argumentative
process.

---

## 6. ADRs and Decision Records

### What they do well

Architecture Decision Records (ADRs) provide a lightweight, version-controlled
format for capturing decisions and their context. The format is simple
(status, context, decision, consequences), well-adopted in software engineering,
and easy to author. ADRs integrate naturally with code repositories and
development workflows.

### What KP:1 adds

ADRs capture **decisions**. KP:1 captures **beliefs**.

An ADR says "we decided to use PostgreSQL because..." — it records a choice and
its rationale. A Knowledge Pack says "we believe PostgreSQL is the best fit
(confidence 0.68, investigation: moderate) because of evidence A and B, but
this contradicts the team's earlier assessment that MongoDB would scale better."

KP:1 borrows from the ADR tradition: lifecycle with supersession (claims can be
superseded like ADRs), and the principle that context matters as much as the
conclusion. But KP:1 extends this to continuous belief with uncertainty, not
binary decisions.

Specifically:

- **Confidence gradients.** ADRs are decided or not. KP:1 claims have
  continuous confidence and investigation depth — the two-axis model captures
  "how sure" and "how hard did we look" independently.
- **Typed relationships.** ADR relationships are limited (supersedes, relates
  to). KP:1 has supports, contradicts (with typed contradiction), informs,
  depends-on, and more.
- **Multi-domain scope.** ADRs are scoped to architectural decisions. Knowledge
  Packs represent epistemic state across any domain.

### What KP:1 does not do

- **Decision workflow.** ADRs have a clear lifecycle (proposed → accepted →
  deprecated → superseded) designed for team decision-making. KP:1's lifecycle
  is for belief evolution, not organizational decision processes.
- **Simplicity.** An ADR is a single markdown file with four sections. A
  Knowledge Pack is a multi-file directory with structured syntax. The
  overhead is justified only when you need the epistemic richness.
- **Broad adoption.** ADRs are widely used and understood across the software
  industry. KP:1 is a draft with no external implementations.

### The honest framing

ADRs are a proven, lightweight tool for their specific purpose. KP:1 is a
heavier-weight format for a broader purpose. If all you need is decision
records, ADRs are simpler and better supported. If you need to represent
uncertain, evolving beliefs with evidence and contradiction across a domain,
KP:1 provides structure that ADRs don't.

---

## 7. MCP / Context Protocols

### What they do well

The Model Context Protocol (MCP) provides a standardized way for AI systems to
access external tools and data sources at runtime. It solves the **access**
problem — how does an LLM connect to a database, an API, a file system? MCP
does this well: it's becoming the standard plumbing for AI tool use.

### What KP:1 adds

MCP is a **transport protocol**. KP:1 is a **representation format**.

MCP answers "how does the AI get the data?" KP:1 answers "what does the data
look like once it arrives?"

A Knowledge Pack could be served via MCP — an MCP resource that returns a
pack's claims, or an MCP tool that queries a pack's evidence chains. But the
pack itself is the content; MCP is the delivery mechanism.

### What KP:1 does not do

- **Runtime data access.** MCP connects to live data sources. Knowledge Packs
  are versioned snapshots, not live endpoints.
- **Tool orchestration.** MCP enables function calling, tool use, and system
  integration. KP:1 is passive content, not an interactive protocol.
- **Standardized transport.** MCP provides a wire format and handshake protocol.
  KP:1 provides a content format — the two operate at different layers.

### The honest framing

KP:1 and MCP are complementary by design. The spec's "Position in the AI Stack"
table explicitly places them at different layers: MCP at the runtime access
layer, Knowledge Packs at the epistemic state layer. They are not alternatives.

---

## Other Adjacent Standards Worth Naming

Several other standards overlap with parts of KP:1. None replaces it, but each
weakens an overbroad novelty claim. Acknowledging them is essential for
credibility.

- **Nanopublications** — probably the nearest scientific analogue. Small
  assertion units (assertion + provenance + publication info) based on RDF,
  active in 2025-2026. KP:1 is less formally rigorous but more authorable and
  LLM-native. If KP:1 ignores nanopublications, KR readers will notice.
- **RO-Crate** — portable research object packaging with rich metadata. Solves
  the "bundle of files with provenance" problem well. KP:1 adds epistemic
  structure (confidence, contradiction) that RO-Crate doesn't model.
- **Croissant (MLCommons)** — agent-ready dataset metadata with provenance
  and governance (v1.1, February 2026). Targets dataset description, not
  epistemic state, but shares the "structured metadata for AI" design space.
- **C2PA / Verifiable Credentials 2.0** — cryptographic provenance and
  attestation. If KP:1 claims provenance without signing, these standards do
  it more rigorously. KP:1's provenance is attribution-level, not
  cryptographic-level — this should be stated explicitly.
- **ClaimReview (schema.org)** — structured fact-checking markup. Narrower
  scope (individual factual claims with ratings) but same neighborhood of
  "structured belief about truth."

---

## The Meta-Question: Why a New Format at All?

The strongest objection is not "why not X?" but "why not adapt X?" — why create
a new format rather than building epistemic extensions on top of RDF, or
structured overlays on top of Obsidian, or richer metadata on top of RAG chunks?

Three reasons:

### 1. Epistemic state is the primary content, not metadata

In every existing format, the "data" is entities, relationships, notes, or
documents. Epistemic properties (confidence, evidence, contradiction) are bolted
on as annotations. This means they're optional, inconsistently supported, and
easily stripped away.

In KP:1, the epistemic state **is** the content. Confidence is not metadata
about a claim — it's part of the claim. Contradiction is not an error condition
— it's a relationship type. This inversion is difficult to achieve by extending
a format that treats these properties as secondary.

### 2. LLM-native consumption is a design constraint, not a feature

KP:1 is designed for a world where the primary consumer of structured knowledge
is a language model. This means: plain text over binary, high information
density over reading comfort, zero-dependency consumption over rich tooling.
The 2024-2025 explosion of AI-native plain-text protocols (`.mdc`, `.clauderules`,
`AGENTS.md`, MCP configuration) confirms that developers want Markdown-based,
LLM-targeted formats. KP:1 shares lineage with this trend.

Adapting RDF for LLM consumption means choosing a text serialization (Turtle?
JSON-LD? N-Triples?), stripping the parts LLMs can't use (SPARQL, reasoning),
and adding the parts they need (confidence, investigation depth). At that point,
you've built a new format that happens to be serialization-compatible with RDF
but shares none of its ecosystem advantages.

### 3. The synthesis is the contribution

KP:1 does not invent confidence scoring (decision theory), typed contradiction
(argumentation theory), evidence chains (provenance standards), lifecycle
management (ADRs), or text-native formats (Markdown). What it does is combine
them into a single, coherent representation designed for a specific use case:
portable epistemic state for AI systems.

The prior art report identifies six traditions that converge in KP:1: semantic
web thinking, compact argumentation syntax, nanopublications, ADR-style
lifecycle, literate programming, and Markdown for AI. None of these traditions
individually solves the problem KP:1 addresses. The combination is the
contribution — and combinations are easier to build cleanly from a coherent
design than to bolt together from independent standards.

---

## Summary Table

| Tradition | Their strength | KP:1's addition | KP:1's gap |
|-----------|---------------|-----------------|------------|
| RDF / JSON-LD / PROV-O | Formal semantics, global identity, interoperability | Epistemic state as primary content, LLM-native, zero infrastructure | No formal reasoning, local identity only, no tooling ecosystem |
| Knowledge graphs | Large-scale querying, entity resolution, graph traversal | Belief with uncertainty, portable artifact, no infrastructure | No query language, no scale, no collaborative editing |
| PKM tools | Authoring experience, exploration, graph visualization | Structured claims, machine-readable confidence, typed contradiction | Not designed for human writing comfort, no visual interface |
| RAG / StructRAG | Retrieval at scale, automatic structuring, real-time | Pre-structured epistemic state, authored certainty assessment | No retrieval, no auto-structuring, versioned snapshots only |
| Argumentation (IBIS, Toulmin, AIF) | Argument structure, deliberation, formal dispute | Continuous confidence, lifecycle/evolution, multi-surface rendering | No warrant decomposition, no deliberation protocol |
| ADRs | Simplicity, adoption, decision workflow | Continuous confidence, typed relationships, multi-domain scope | Heavier format, no adoption, not designed for decision workflow |
| MCP | Runtime access, tool orchestration, standardized transport | Epistemic content format (complementary layer) | Not a protocol, not live, not interactive |
| Nanopublications | RDF-based atomic assertions with provenance | Authorability, LLM-native, richer epistemic model | Less formal, no global identity, no RDF ecosystem |
| C2PA / VCs | Cryptographic provenance and attestation | Richer epistemic structure (confidence, contradiction) | No signing, attribution-level provenance only |

---

## What We Owe These Traditions

KP:1 is not built in isolation. It borrows explicitly:

- **From the semantic web:** the principle that structured assertions need
  provenance and should be machine-readable
- **From nanopublications:** the atomic-assertion-with-metadata pattern
- **From argumentation theory:** the insight that contradiction is information
- **From ADRs:** lifecycle with supersession and the value of recording context
- **From literate programming:** the union of reasoning and human-readable
  artifact
- **From the Markdown ecosystem:** text-native, git-friendly, zero-dependency

This genealogy is not a fig leaf. These are genuine debts, and the communities
behind these traditions are the audiences whose critique will matter most.

The interoperability story follows from this genealogy: KP:1 → RDF/JSON-LD
export (with explicit loss/gain documentation), KP:1 → graph ingestion for
queryable infrastructure, KP:1 → ADR snapshot for decision records, KP:1 →
MCP resource for runtime access. These bridges are on the roadmap, not yet
built.

---

## Open Questions We Cannot Yet Answer

Intellectual honesty requires acknowledging what we don't know:

1. **Does pre-structured epistemic state outperform inference-time structuring?**
   This is the fundamental empirical question. If LLMs can reconstruct
   confidence, evidence chains, and contradictions from unstructured text as
   well as they can read them from KP:1, the format's value proposition weakens
   significantly. Benchmarks are on the roadmap but do not yet exist.

2. **Can confidence be represented in a calibrated way?** The field's experience
   with precise confidence values is mixed. KP:1 supports both numeric (0.0–1.0)
   and qualitative (simple scale) confidence, but the calibration problem is
   real and unresolved.

3. **Will anyone else implement it?** A single-implementation format is a
   proprietary export, regardless of how public the spec is. External
   implementations are the real test of whether the format is coherent enough
   to be useful beyond its origin.

4. **Do the claimed differentiators hold up under formal analysis?** Knowledge
   representation researchers may find that KP:1's epistemic model is
   expressible as a profile of existing standards we haven't considered. If so,
   the right response is to adopt that mapping, not to defend the new format
   for its own sake.

5. **What are the semantics of preserved contradiction?** KP:1 preserves typed
   contradictions rather than resolving them. Researchers familiar with belief
   revision (AGM theory), truth-maintenance systems, and paraconsistent
   reasoning will ask: what is the intended downstream revision or resolution
   story? KP:1 deliberately does not specify one — the consuming intelligence
   decides. Whether that is a feature or an underspecification is an open
   question.

---

*This document follows the KP:1 positioning principle: truth over posture.
If something here is wrong, imprecise, or unfair to a cited tradition, that
is a bug — please file it.*
