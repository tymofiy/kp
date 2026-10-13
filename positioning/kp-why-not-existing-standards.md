<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Why Not Existing Standards?

> A design comparison of KP:1 with adjacent formats, tools and protocols.
>
> **Audience:** knowledge representation researchers, AI engineers and anyone
> asking why this work needs a separate format.
>
> **Posture:** explain the choices, acknowledge the overlap and invite better
> mappings. This is not an exhaustive prior-art survey or a performance benchmark.

---

## The Short Answer

KP:1 combines assertions, explanations, evidence, confidence, disagreement and
revision in a portable record made of ordinary text files. People and AI can
follow the recorded connections, inspect the grounds and continue the inquiry.
The format supplies that record; applications supply retrieval, reasoning and
workflow operations.

These concerns are not unique to KP:1. Existing standards and applications can
represent many of them, sometimes with stronger formal semantics or more mature
tooling. The proposal is a particular authoring and interchange contract, not
proof that other formats are incapable of carrying uncertainty or understanding.

The question is whether this combination is useful for its intended tasks, and
whether an existing profile or a documented mapping could serve them better.
Comparative benefits require evidence. A conformant pack does not by itself prove
truth, calibrated confidence or successful understanding by a recipient.

For the actual implementable contract, use [CORE.md](../spec/CORE.md). For the
implemented and deferred surfaces, use
[COMPATIBILITY.md](../spec/COMPATIBILITY.md).

---

## 1. RDF / JSON-LD / PROV-O (Semantic Web)

### What it does well

[RDF](https://www.w3.org/TR/rdf11-concepts/) defines a graph model with globally
scoped identifiers. [JSON-LD](https://www.w3.org/TR/json-ld11/) provides a JSON
serialization of Linked Data. [PROV-O](https://www.w3.org/TR/prov-o/) defines an
ontology for representing and exchanging provenance. These are reusable building
blocks for describing assertions, sources and relationships across systems.

RDF can represent assertions about other assertions, including attribution and
uncertainty when the vocabulary supplies those concepts. It also has text
serializations; reading an RDF document does not require running a triple store.
KP:1 should not claim those capabilities as its exclusive contribution.

### What KP:1 adds

KP:1 chooses a fixed, authorable claim record with a confidence value, type,
evidence references and date. Optional investigation depth and nature accompany
ordinary explanatory prose. A small relation vocabulary records support,
dependency, refinement, disagreement and change.

For example, these fictional adopted estimates concern the same revenue target:

```markdown
- [C001] Acme Corp's 2025 revenue is estimated at $2 billion.
  {0.72|i|E001|2026-03-15|investigated|judgment} Based on the analyst report's estimate; its method differs from E002. ⊗~C002

- [C002] Acme Corp's 2025 revenue is estimated at $1.5 billion.
  {0.68|i|E002|2026-03-15|investigated|judgment} A competing estimate of the same target; the difference remains unresolved. ↔C001
```

This is a syntax excerpt, not a complete pack. A pack must define E001 and E002,
include the required headers and manifest, and retain the methods and scope that
make the assessed tension intelligible. Reports that two sources gave different
numbers can both be true; a relation between adopted estimates must not erase
those source accounts.

### What KP:1 does not do

KP:1 does not supply RDF's global identifier model, shared ontology ecosystem or
formal entailment semantics. Its relations are recorded assessments, not a proof
calculus. The core does not require a registry or query service, but that choice
alone does not distinguish it from every RDF use.

### The honest framing

A mapping to RDF or nanopublications could clarify the overlap and expose losses
in either direction. No such general bridge is implemented here. Whether KP:1
should become a profile of another standard remains a legitimate design question.

---

## 2. Knowledge Graphs (Neo4j, Wikidata)

### What they do well

Graph databases and knowledge bases organize entities and relationships for
querying and shared use. They need not contain only settled facts.
[Wikidata's data model](https://www.wikidata.org/wiki/Wikidata:Data_model), for
example, includes statements with qualifiers, references and ranks. Qualifiers
can change a statement's scope; dropping them can change its meaning.

### What KP:1 adds

KP:1 makes an authored record portable outside the database that indexes it.
Explanations, claim relationships, support and historical assessments can travel
together as files. A graph database can then index those files as a derived
representation for a particular task.

### What KP:1 does not do

The format is not a graph query engine, a large-scale identity-resolution service
or a concurrent editing application. Its experimental compiler is a derived
projection with explicit limits, not a replacement for the retained pack.
See [compiler/README.md](../compiler/README.md).

### The honest framing

A pack and a graph service can complement each other. A useful integration must
show which meanings survive indexing and export, including disputed identities,
qualifications and superseded assessments. A graph-shaped output alone does not
establish that fidelity.

---

## 3. PKM Tools (Obsidian, Notion, Roam)

### What they do well

Personal knowledge tools support writing, linking and exploring notes.
[Obsidian's internal links](https://help.obsidian.md/links), for example, connect
notes and their sections. Authors can express reasons, uncertainty and sources
in ordinary prose or add structured properties where a tool supports them.

### What KP:1 adds

KP:1 gives selected assertions and their relationships a common serialized form.
A consumer can locate the recorded confidence, evidence references and revision
links without guessing their placement from an author's individual note style.
It must still interpret the prose, assess the grounds and understand the context.
No comparative gain in model accuracy is established by the syntax alone.

### What KP:1 does not do

KP:1 is not a freeform notebook or an interactive authoring application. Claim
bullets have a structured contract. That does not exclude early inquiry:
attributed hypotheses, uncertain judgments and questions can retain their scope
in prose, with fuller exploratory accounts in evidence. They must not be promoted
to established findings merely to fit the syntax.

The repository has a reference validator and starter scaffolding. Other CLI
operations are contract pointers; authoring and application tooling remain work
for implementations. See [reference/README.md](../reference/README.md).

### The honest framing

A note application can be a place to explore, while a pack carries the expressed
account chosen for reuse. That account can remain uncertain and revisable.
Formalizing it need not mean waiting until every belief has stabilized.

---

## 4. RAG / StructRAG / Context Engineering

### What they do well

Retrieval-augmented generation selects external material for a model's task.
Structured retrieval can preserve more than isolated text chunks:
[Microsoft's GraphRAG](https://microsoft.github.io/graphrag/) describes extracting
an entity graph, community hierarchy and summaries from source text.
Agent memory and context-management systems also maintain or select material
across tasks. Their fidelity depends on the particular implementation.

### What KP:1 adds

KP:1 provides an authored record such systems can retrieve or use as input.
Recorded explanations and relations give the consumer an explicit starting point
for reasoning, while retained sources make that starting point challengeable.
The consumer still needs to evaluate relevance, source meaning and whether an
assessment remains warranted.

### What KP:1 does not do

The format does not run retrieval, choose a model, perform investigations or
refresh sources. A pack is a versioned account; applications must handle its
selection, maintenance and use. Explicit structure is not a guarantee of better
reasoning or immunity to omitted qualifications.

### The honest framing

The empirical question is whether authoring and retaining this structure improves
particular tasks compared with other representations. Relevant comparisons must
include source fidelity, correction, effort and meaningful usefulness, rather
than token counts or confident prose alone. This repository does not establish
that result.

---

## 5. Argumentation Frameworks (IBIS, Toulmin)

### What they do well

Argumentation frameworks address how positions, reasons and objections relate.
The [Argument Interchange Format](https://www.arg.tech/research/contributing-to-the-argument-interchange-format/)
is an effort to exchange argument resources using a semantically rich language.
Such work is important prior art for any format that records reasoning and
conflicting assessments.

### What KP:1 adds

KP:1 combines a small claim-relation vocabulary with confidence, evidence and
historical records. Context prose and evidence can carry an explanation beyond
what those relation labels express. Views can present that account to different
audiences while preserving the necessary qualifications.

### What KP:1 does not do

The core does not specify a complete argument ontology, formal deliberation
protocol or automatic dispute-resolution algorithm. It does not demonstrate
that other argumentation systems cannot represent confidence or change.

### The honest framing

KP:1 borrows the insight that disagreement can be information. A mapping should
make clear which reasoning is explicit, which remains in prose and which a
consumer would have to infer. Preserving opposing accounts does not establish
that their underlying propositions are equally well supported.

---

## 6. ADRs and Decision Records

### What they do well

[Architecture Decision Records](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
retain a decision's context, status and consequences. Their reasons can remain
useful when the team changes. A decision record can include uncertainty and
alternatives in its narrative; it need not be a bare choice.

### What KP:1 adds

KP:1 gives supporting observations, reported accounts, computations and
inferences separate identities. Those records can support different decisions
or later interpretations. A recommendation can be marked as judgment, with its
conditions and grounds available independently of the action someone chooses.

### What KP:1 does not do

The format does not replace a team's decision workflow or make a recommendation
binding. A simple decision may be adequately recorded in one document. The extra
structure is useful when the assertions, competing accounts and revisions need
to be addressed separately.

### The honest framing

A pack can supply the basis of a decision record and retain knowledge that later
work can reconsider. A decision record can explain the chosen action. A mapping
between them must preserve that distinction.

---

## 7. MCP / Context Protocols

### What they do well

The [Model Context Protocol](https://modelcontextprotocol.io/docs/getting-started/intro)
connects AI applications to external data, tools and workflows. It defines how
applications interact with those capabilities.

### What KP:1 adds

KP:1 defines content that an application could make available through MCP or
another access mechanism. Explanations, assertions and their supporting records
remain the content; the protocol supplies access to them.

### What KP:1 does not do

A pack does not expose an endpoint, orchestrate tools or perform a live lookup.
Serving or querying packs through MCP requires an implementation. A protocol
connection does not by itself prove faithful knowledge interchange.

### The honest framing

These address different responsibilities. A useful integration must specify what
is returned, how the recipient resolves references and how revisions remain
visible. This document does not claim a general KP-to-MCP bridge is implemented.

---

## Other Adjacent Standards Worth Naming

- [Nanopublications](https://nanopub.net/guidelines/working_draft/) combine RDF
  assertion, provenance and publication-information graphs. They can carry
  hypotheses and opinions as well as scientific findings. They are close prior
  art, not a fact-only format that KP:1 has surpassed.
- [RO-Crate](https://www.researchobject.org/ro-crate/specification/1.2/introduction.html)
  packages and describes resources with contextual metadata in JSON-LD. A mapping
  should examine which KP claim and revision semantics a profile could express.
- [Croissant](https://docs.mlcommons.org/croissant/docs/croissant-spec.html)
  describes datasets for machine learning. Its scope differs from an authored
  account of a subject, while its metadata and reuse concerns are relevant.
- [C2PA](https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html)
  and [Verifiable Credentials](https://www.w3.org/TR/vc-data-model-2.0/)
  address verifiable provenance or credentials. KP evidence references provide
  attribution; its archive contract separately describes hashes and optional
  signatures. These mechanisms do not establish the truth of an assertion.
  See [ARCHIVE.md](../spec/ARCHIVE.md).
- [ClaimReview](https://schema.org/ClaimReview) describes a fact-checking review
  of a claim. It overlaps with a focused part of the broader inquiry KP aims to
  retain.

These are entry points for comparison, not a complete evaluation of every
extension or implementation. A useful bridge must document preserved meaning,
losses and implementation evidence before claiming interoperability.

---

## The Meta-Question: Why a New Format at All?

The case for a separate format rests on whether its combination is useful:

1. **An explicit authored account.** Required claim fields and addressable
   relations make selected assessments and their grounds inspectable. Narrative
   context carries explanation; it is not disposable decoration around facts.
2. **Portable text.** A directory can be read with ordinary text tools, independent
   of the service that created it. Reliable interpretation and automated
   validation still need the relevant specification and implementation.
3. **A common contract for continued work.** Keeping source accounts, uncertainty
   and revisions available can let another person or AI challenge and extend an
   explanation instead of receiving only its conclusion.

Those are design aims. They do not establish unique expressiveness, universal
superiority or complete capture of an expert's understanding. Others should be
able to develop the format, test these aims and propose stronger mappings to
existing standards. The specification should stand on its contract and evidence
beyond any one author or application.

---

## Summary Table

| Tradition | Relevant focus | KP:1 relationship | Work still required |
| --- | --- | --- | --- |
| RDF / JSON-LD / PROV-O | Graph representation and provenance | A fixed text contract for an authored account | Formal mappings and loss analysis |
| Knowledge graphs | Entities, statements and graph queries | Packs can supply retained source records | Faithful indexing and export |
| PKM tools | Authoring and exploration | Selected accounts can be formalized for reuse | Authoring integration and evaluation |
| RAG / context systems | Retrieval and context selection | Packs can supply structured input | Task-specific comparative evidence |
| Argumentation | Reasons, positions and objections | A small relation vocabulary plus narrative explanation | Semantic mappings and richer consumer reasoning |
| ADRs | Decisions, context and consequences | Separately addressable grounds for decisions | Mappings that retain belief/action distinctions |
| MCP | Access to data and tools | A possible delivery route for pack content | Implemented integrations and fidelity checks |

---

## What We Owe These Traditions

KP:1 draws on structured assertions and provenance, argumentation, historical
decision records, literate explanation and plain-text authoring. Those debts
should be explicit. Contributions from these communities can improve the
contract, expose unnecessary novelty and establish useful interoperability.
See [CONTRIBUTING.md](../CONTRIBUTING.md) and
[intent and principles](kp-intent-and-principles.md).

---

## Open Questions We Cannot Yet Answer

1. **Where does this structure help?** Comparative research must examine tasks
   such as continuing an inquiry, finding material qualifications and reusing a
   correction. Conformance is not that benchmark.
2. **How well is confidence calibrated?** The wire value is a normalized float;
   display labels accompany it. Evidential reasons and numerical precision alone
   do not demonstrate outcome calibration.
3. **Can others implement and extend it reliably?** Independent implementations
   and round trips are evidence needed for practical interoperability.
4. **Would a profile of another standard serve the purpose better?** A successful
   mapping should influence the design, rather than become something to defend
   against merely because KP:1 already exists.
5. **How should consumers handle disagreement and revision?** The format records
   distinctions; applications must make their consequences visible. Reconciliation
   and other deferred surfaces must not be treated as demonstrated behavior.

---

*If this comparison misrepresents a tradition or omits relevant prior art, please
raise it. The public draft exists to be challenged and developed by others.*
