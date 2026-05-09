<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# KP:1 Mapping to RDF/JSON-LD/PROV

> **Status:** Draft (informative — not normative for KP:1 conformance)
> **Date:** 2026-04-04
> **Audience:** Semantic Web practitioners evaluating KP:1 interoperability
>
> This is not advocacy. It is an honest field-by-field translation analysis.
> For the *why KP:1 exists* argument, see
> [`positioning/kp-why-not-existing-standards.md`](../positioning/kp-why-not-existing-standards.md).

---

## 1. Purpose

KP:1 has its own claim syntax, evidence model, and relation types. This
document shows what happens when you try to translate between KP:1 and three
standards: RDF/JSON-LD, PROV-O, and Nanopublications. For each KP:1 concept,
it identifies whether the translation is clean (round-trips without loss),
lossy (information degrades), or impossible (no target equivalent).

The goal is to let someone who knows RDF answer: *Can I use my existing
toolchain? What do I lose? What do I gain?*

---

## 2. Methodology

Every KP:1 concept is mapped to its closest target representation. Each
mapping is graded:

- **Clean** — round-trips without loss. The target representation preserves
  all semantics and can reconstruct the KP:1 original.
- **Lossy** — a reasonable representation exists, but information degrades.
  The target captures the broad intent but loses precision, nuance, or
  structure.
- **None** — no standard equivalent. Representing this requires inventing
  custom vocabulary.

"Custom vocabulary" is not a failure — it's how RDF works. But it means
your existing SPARQL queries, reasoners, and validators won't understand
the concept without extension.

---

## 3. RDF/JSON-LD Mapping

### 3.1 Pack → Named Graph

A Knowledge Pack maps naturally to an **RDF named graph** (or a
**TriG dataset**). The pack URI serves as the graph name; pack metadata
becomes triples in a metadata graph.

| KP:1 field | RDF representation | Grade |
|---|---|---|
| `name` | Graph URI (e.g., `<kp:solar-energy-market>`) | Clean |
| `version` (CalVer) | `dct:issued` with `xsd:date` | Lossy — CalVer semantics (snapshot date, not SemVer) are lost |
| `domain` | `dct:subject` with a SKOS concept or custom hierarchy | Lossy — KP's hierarchical path (`energy/market-analysis`) has no standard encoding |
| `author` | `dct:creator` | Clean |
| `kind` | Custom predicate (`kp:kind`) | None — no RDF equivalent for claim/definition/policy/mixed |
| `confidence.scale` | Custom predicate (`kp:confidenceScale`) | None |
| `freshness` | `dct:modified` | Clean |
| `license` | `dct:license` | Clean |
| `sensitivity` | Custom predicate (`kp:sensitivity`) | None |
| `visibility` | Custom predicate (`kp:visibility`) | None |
| `channels` | Custom predicate (`kp:channel`) | None |
| `provenance.role` | Custom predicate (`kp:authorRole`) | None — PROV-O has `prov:hadRole` but no vocabulary for manufacturer/independent/etc. |
| `tier` | Custom predicate (`kp:tier`) | None |
| `display` | Custom predicates | None — cognitive perception layer has no RDF analogue |

**Verdict:** Pack-level metadata is roughly 40% clean (standard Dublin Core
fields), 60% custom vocabulary. The pack *structure* (directory of files)
has no RDF equivalent — RDF models graphs, not file systems.

### 3.2 Claim → RDF Statement

A KP:1 claim maps to an **RDF-star reified triple** (RDF 1.2) or a
**named graph per claim** (RDF 1.1). The headline becomes the object of an
assertion triple; metadata attaches to the reifier.

Using RDF 1.2 reifiers:

```turtle
PREFIX kp:   <https://kp.dev/ontology/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>

:C001 rdf:reifies << :solar-energy-market kp:claims "Cost decline is structural, not cyclical — driven by manufacturing scale" >> .
:C001 kp:confidence    "0.95"^^xsd:float .
:C001 kp:claimType     kp:inferred .
:C001 kp:evidence      :E001, :E002 .
:C001 dct:date         "2026-03-01"^^xsd:date .
:C001 kp:depth         kp:exhaustive .
:C001 kp:nature        kp:judgment .
```

This captures the structured metadata but loses:

- **The headline as an independent assertion.** In KP:1, the headline is a
  self-contained proposition ("Cost decline is structural"). In RDF, it
  becomes a string literal — the triple is *about* the pack having that
  claim, not an assertion of the claim's content as a first-class statement.
- **Claim ID semantics.** KP:1 IDs (`C001`) are pack-local, sequential,
  versionable (`C001-v2`). RDF URIs are global. The local-ID convention is
  lost.
- **Context prose.** The free-text context ("10/10 analyses converged.
  Learning curve held for 40 years.") has no structured home. It becomes
  `rdfs:comment` or a custom annotation — searchable but not semantic.

### 3.3 Confidence

| KP:1 | RDF | Grade |
|---|---|---|
| Confidence value (0.0–1.0 float) | Custom `kp:confidence` with `xsd:float` | Lossy — no standard confidence predicate exists |
| Confidence scale (e.g., `sherman_kent`) | Custom `kp:confidenceScale` on pack graph | None — RDF has no confidence scale concept |
| `normalize: true` declaration | Implicit (values are floats) | Lossy — the explicit "these are normalized" signal is lost |

RDF has no standard vocabulary for epistemic confidence. The W3C Uncertainty
Ontology (URW3-XG) defined `urw3:weight` but never advanced beyond incubator
status. In practice, everyone uses custom predicates. KP:1's confidence model
is *richer* than anything standard in RDF — the combination of numeric value +
named scale + normalization flag + investigation depth has no off-the-shelf
target.

### 3.4 Claim Metadata (Type, Depth, Nature)

| KP:1 concept | Closest RDF | Grade |
|---|---|---|
| Claim type (`o`/`r`/`c`/`i`) | PROV-O derivation types (partial) | Lossy — see §4 |
| Investigation depth (`assumed`/`investigated`/`exhaustive`) | No standard equivalent | None |
| Claim nature (`judgment`/`prediction`/`meta`) | No standard equivalent | None |

**Claim type** partially maps to provenance concepts — `observed` ≈ primary
source, `reported` ≈ secondary source, `computed` ≈ algorithmic derivation,
`inferred` ≈ reasoning. But PROV-O models *how entities were derived*, not
*how claims were acquired*. The epistemological distinction (what kind of
knowledge is this?) has no standard RDF encoding.

**Investigation depth** is KP:1's novel two-axis model: confidence × depth.
A claim at 0.50/exhaustive means "we looked hard and it's genuinely
uncertain." A claim at 0.90/assumed means "we haven't checked but it feels
right." No RDF vocabulary captures this distinction.

**Claim nature** distinguishes factual assertions from judgments, predictions,
and meta-claims. RDF has no equivalent — all triples are equally assertional.

### 3.5 Relations

| KP:1 relation | Closest RDF/ontology | Grade |
|---|---|---|
| `→` supports | CiTO `cito:supports` | Lossy — CiTO captures citation-level support but not KP:1's epistemic "this belief strengthens that belief" |
| `⊗` contradicts | CiTO `cito:disagreesWith` | Lossy — CiTO has disagrees/disputes/refutes intensity levels but no qualifier for *why* |
| `⊗!` contradicts:error | No standard equivalent | None — CiTO's `cito:refutes` is closest but doesn't encode "one is wrong, prioritize resolution" |
| `⊗~` contradicts:tension | No standard equivalent | None — "both informative, preserve as productive disagreement" has no standard encoding |
| `←` requires | Custom or `dct:requires` | Lossy — Dublin Core `requires` is for resource dependencies |
| `~` refines | `skos:narrower` (partial) | Lossy — SKOS narrower is taxonomic, not epistemic refinement |
| `⊘` supersedes | `prov:wasRevisionOf` | Clean — good semantic match |
| `↔` see_also | `rdfs:seeAlso` | Clean |

The best standard vocabulary for KP:1 relations is **CiTO** (Citation Typing
Ontology, `http://purl.org/spar/cito/`), not AIF. CiTO provides
`cito:supports`, `cito:agreesWith`, `cito:disagreesWith`, `cito:disputes`,
`cito:critiques`, and `cito:refutes` — a better fit than AIF's abstract
argument nodes.

**But contradiction qualifiers remain the hardest mapping.** CiTO
distinguishes intensity (disagrees < disputes < refutes) but not the *nature*
of the conflict. KP:1's three-way distinction — unqualified (`⊗`), error
(`⊗!`: one is wrong), tension (`⊗~`: both informative) — encodes why the
contradiction matters, not how strongly someone disagrees. No standard
vocabulary captures this.

An export would use CiTO for the base relations and custom `kp:` predicates
for the qualifiers. Consumers with CiTO would understand the support/attack
structure; the error/tension distinction would degrade to opaque custom
properties.

### 3.6 Evidence

| KP:1 field | RDF | Grade |
|---|---|---|
| Evidence ID (`E001`) | URI for a `prov:Entity` | Clean |
| Evidence type (`observed`/`reported`/`computed`/`inferred`) | See §4.1 | Lossy |
| Source (free text) | `dct:source` or `prov:wasAttributedTo` | Clean |
| Captured date | `prov:generatedAtTime` | Clean |
| Evidence prose | `rdfs:comment` | Lossy — loses structured role |
| Claim → Evidence link | `prov:wasDerivedFrom` or `prov:hadPrimarySource` | Clean |

Evidence entries map well to PROV-O entities. The main loss is evidence
*type* — KP:1's four-way classification (observed/reported/computed/inferred)
doesn't map cleanly to PROV-O's derivation subtypes (see §4).

### 3.7 Example: Solar C001 as JSON-LD

```json
{
  "@context": {
    "kp": "https://kp.dev/ontology/",
    "kpd": "https://kp.dev/data/",
    "prov": "http://www.w3.org/ns/prov#",
    "cito": "http://purl.org/spar/cito/",
    "dct": "http://purl.org/dc/terms/",
    "xsd": "http://www.w3.org/2001/XMLSchema#"
  },
  "@id": "kpd:solar-energy-market/C001",
  "@type": "kp:Claim",
  "kp:headline": "Cost decline is structural, not cyclical — driven by manufacturing scale",
  "kp:confidence": { "@value": "0.95", "@type": "xsd:float" },
  "kp:claimType": { "@id": "kp:inferred" },
  "kp:depth": { "@id": "kp:exhaustive" },
  "kp:nature": { "@id": "kp:judgment" },
  "dct:date": { "@value": "2026-03-01", "@type": "xsd:date" },
  "prov:wasDerivedFrom": [
    { "@id": "kpd:solar-energy-market/E001" },
    { "@id": "kpd:solar-energy-market/E002" }
  ],
  "cito:supports": { "@id": "kpd:solar-energy-market/C002" },
  "kp:contradictsTension": { "@id": "kpd:solar-energy-market/C003" },
  "kp:context": "10/10 analyses converged. Learning curve (22% cost reduction per doubling) has held for 40 years."
}
```

**Note on JSON-LD version:** This example uses JSON-LD 1.1, which cannot
represent RDF 1.2 triple terms or reifiers natively. The Turtle examples
in §3.2 use RDF 1.2 reifier syntax (`rdf:reifies`); a full JSON-LD
representation of that pattern would require JSON-LD 1.2 (in development).
The example above models the claim as a typed node with custom predicates,
which is valid JSON-LD 1.1 but does not capture the reification semantics.

**What's preserved:** claim identity, headline, confidence value, evidence
links, date, support relation (via CiTO), context prose.

**What's lost:** confidence scale semantics (Sherman Kent), the Rosetta
header (self-describing format), frontmatter (pack identity in claims.md),
the dense/verbose encoding distinction, positional field semantics, claim
ID locality (C001 is now a global URI), contradiction qualifier semantics
(tension degrades to a custom predicate), and the fact that this is one
claim in a file designed for sequential AI consumption.

**What's gained:** global identity (URI), machine-queryable via SPARQL,
composable with any RDF graph, processable by standard RDF tooling,
standard citation semantics via CiTO.

---

## 4. PROV-O Mapping

### 4.1 Evidence Provenance Chain

KP:1 evidence entries map to PROV-O entities with generation activities:

```turtle
:E001 a prov:Entity ;
    prov:wasGeneratedBy :analysis_activity ;
    prov:generatedAtTime "2026-03-01"^^xsd:date ;
    prov:wasAttributedTo :jane_chen ;
    dct:source "Internal analysis — 10 independent assessments across multiple AI models" .

:analysis_activity a prov:Activity ;
    prov:used :irena_report, :bnef_data .
```

This is a good fit. PROV-O was designed for exactly this — tracking where
data came from.

### 4.2 Claim Derivation

KP:1 claims that reference evidence map to PROV-O derivation:

```turtle
:C001 a prov:Entity ;
    prov:wasDerivedFrom :E001, :E002 ;
    prov:wasAttributedTo :jane_chen ;
    prov:generatedAtTime "2026-03-01"^^xsd:date .
```

The derivation is clean. But PROV-O's derivation subtypes don't align with
KP:1's claim types:

| KP:1 claim type | PROV-O closest | Fit |
|---|---|---|
| `observed` (primary source) | `prov:hadPrimarySource` | Good |
| `reported` (secondary source) | `prov:wasQuotedFrom` | Partial — quoting is narrower than reporting |
| `computed` (algorithmic) | `prov:qualifiedDerivation` with `prov:hadActivity` | Lossy — requires the qualified derivation pattern to link the computation Activity |
| `inferred` (reasoned) | `prov:wasDerivedFrom` (generic) | Lossy — no standard "inferred via reasoning" subtype |

### 4.3 Supersession → prov:wasRevisionOf

KP:1's `⊘` (supersedes) maps cleanly:

```turtle
:C001-v2 prov:wasRevisionOf :C001 .
:C001 prov:wasInvalidatedBy :supersession_activity .
```

This is one of the best mappings in this document. PROV-O's revision and
invalidation model closely matches KP:1's supersession semantics, including
the audit trail (history.md ≈ invalidated entities).

### 4.4 What PROV-O Adds That KP:1 Lacks

- **Activity modeling.** PROV-O can represent the *process* that produced
  a claim (who ran what analysis, when, using what tools). KP:1 evidence
  records the *result* but not the process chain.
- **Qualified patterns.** PROV-O's qualified counterparts
  (`prov:qualifiedDerivation`, `prov:qualifiedAssociation`,
  `prov:qualifiedAttribution`, etc.) allow attaching arbitrary metadata
  to any provenance relationship — timestamps, roles, confidence, methods.
  This is where most of PROV-O's real expressive power lives, and it's
  more flexible than KP:1's fixed-field model. A `prov:Derivation` node
  can carry `prov:hadActivity`, `prov:hadUsage`, and custom annotations
  that KP:1 evidence entries cannot express.
- **Agent roles.** `prov:hadRole` on qualified associations can model
  reviewer, editor, approver roles per claim. KP:1 has `provenance.role`
  at the pack level only. The PAV ontology (`pav:authoredBy`,
  `pav:curatedBy`, `pav:createdBy`) provides finer author-role
  distinctions that plug into PROV-O.
- **Delegation chains.** `prov:actedOnBehalfOf` models organizational
  authority. KP:1 has no delegation concept.
- **Plans.** `prov:hadPlan` on qualified associations can link activities
  to their governing methodology. KP:1's `ontology` field is a freeform
  string, not a structured plan reference.

### 4.5 What KP:1 Has That PROV-O Cannot Represent

- **Confidence values.** PROV-O has no uncertainty model.
- **Investigation depth.** No PROV-O equivalent.
- **Claim nature.** No distinction between factual/judgment/prediction/meta.
- **Typed contradiction.** PROV-O models derivation, not disagreement.
  Two entities can both exist in a PROV graph, but there's no way to say
  "these two conflict, and the conflict is informative."
- **Views.** PROV-O models provenance, not presentation.

---

## 5. Nanopublication Mapping

### 5.1 Structural Alignment

Nanopublications have three named graphs: assertion, provenance, publication
info. KP:1 claims have a parallel structure:

| Nanopub graph | KP:1 equivalent | Alignment |
|---|---|---|
| **Assertion** (the claim itself) | Claim headline + context prose | Good — both are atomic assertions |
| **Provenance** (how the assertion was derived) | Evidence entries + claim type + depth | Partial — KP:1 evidence is richer but less formally structured |
| **Publication Info** (who published, when, signature) | PACK.yaml provenance + version + freshness | Good — both track authorship and timing |

A single KP:1 claim maps to one nanopublication. A KP:1 pack maps to a
*set* of nanopublications sharing publication info.

### 5.2 Where the Analogy Holds

- **Atomic assertions.** Both formats center on individual, identifiable
  claims rather than documents. A nanopub assertion graph ≈ a KP:1 claim
  headline.
- **Provenance per claim.** Both attach provenance to individual assertions,
  not to documents. KP:1's per-claim evidence references mirror nanopub's
  per-assertion provenance graph.
- **Immutability + versioning.** Nanopubs use trusty URIs (content-addressed,
  immutable). KP:1 uses CalVer + supersession. Different mechanisms, same
  intent: you don't edit published claims, you supersede them.
- **Author attribution.** Both record who made the assertion and when.

### 5.3 Example: Solar C001 as Nanopublication

```trig
@prefix np:   <http://www.nanopub.org/nschema#> .
@prefix kp:   <https://kp.dev/ontology/> .
@prefix kpd:  <https://kp.dev/data/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix cito: <http://purl.org/spar/cito/> .
@prefix dct:  <http://purl.org/dc/terms/> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

:C001-nanopub {
  :C001-nanopub a np:Nanopublication ;
    np:hasAssertion       :C001-assertion ;
    np:hasProvenance      :C001-provenance ;
    np:hasPublicationInfo :C001-pubinfo .
}

:C001-assertion {
  kpd:solar-energy-market kp:claims
    "Cost decline is structural, not cyclical — driven by manufacturing scale" .
}

:C001-provenance {
  :C001-assertion prov:wasDerivedFrom kpd:solar-energy-market/E001 ,
                                       kpd:solar-energy-market/E002 .
  :C001-assertion prov:generatedAtTime "2026-03-01"^^xsd:date .
}

:C001-pubinfo {
  :C001-nanopub prov:wasAttributedTo <https://orcid.org/example/jane-chen> .
  :C001-nanopub dct:created "2026-03-18"^^xsd:date .
  :C001-nanopub dct:license <https://creativecommons.org/licenses/by/4.0/> .
}
```

**What's preserved:** assertion content, evidence links, timestamp, authorship,
license.

**What's lost:** confidence (0.95), claim type (inferred), investigation depth
(exhaustive), claim nature (judgment), context prose, relations (→C002, ⊗~C003),
section membership, the Rosetta header, and the fact that this is one claim in a
curated pack of 8. These would require custom annotations on the assertion or
provenance graphs with no standard vocabulary.

### 5.4 Where It Breaks

**Confidence model.** Nanopubs have no standard confidence annotation.
Some life-science nanopubs use custom predicates for evidence strength, but
there's no shared vocabulary. KP:1's confidence + depth + nature model has
no nanopub equivalent.

**Relations between claims.** Nanopubs are self-contained units. Relations
between nanopubs (A supports B, A contradicts C) require external
association graphs or conventions like `npx:introduces` and custom
association predicates.
KP:1's inline relation syntax (`→C002, ⊗~C003`) is first-class, not an
afterthought.

**Contradiction preservation.** Nanopubs in the same network can make
conflicting assertions, but the conflict is implicit — there's no typed
contradiction relation. KP:1's `⊗`/`⊗!`/`⊗~` distinction has no nanopub
analogue.

**Views.** Nanopubs have no presentation layer. KP:1's views
(display, voice) are a separate concern with no nanopub equivalent.

**Pack as container.** A nanopub is a standalone unit. KP:1 packs are
*curated collections* with shared metadata, confidence scales, and
cross-claim relations. The container semantics (sections, frontmatter,
Rosetta header) have no nanopub equivalent — the closest analogue would be
a nanopub index or collection, which is not yet standardized.

**Authoring format.** Nanopubs are RDF (serialized as TriG). KP:1 is
Markdown. This is not a mapping issue but a practical one: KP:1 is designed
for human authoring and LLM consumption; nanopubs are designed for machine
interchange.

---

## 6. Translation Loss Summary

| KP:1 Concept | RDF/JSON-LD | PROV-O | Nanopub |
|---|---|---|---|
| Pack (PACK.yaml) | Lossy (named graph + Dublin Core, ~40% custom) | N/A | Lossy (publication info graph, no container) |
| Claim (ID + headline + metadata) | Lossy (reified triple, headline becomes literal) | Lossy (entity, no claim semantics) | Lossy (assertion graph, no confidence) |
| Confidence (0–1 float) | None (custom predicate) | None | None |
| Confidence scale (sherman_kent, etc.) | None (custom predicate) | None | None |
| Claim type (o/r/c/i) | Lossy (PROV derivation subtypes, partial) | Lossy (partial via derivation) | None |
| Investigation depth | None | None | None |
| Claim nature (judgment/prediction/meta) | None | None | None |
| Relation: supports (→) | Lossy (CiTO `cito:supports`) | None | None (external association) |
| Relation: contradicts (⊗) | Lossy (CiTO `cito:disagreesWith`) | None | None |
| Contradiction qualifiers (⊗! / ⊗~) | None | None | None |
| Relation: requires (←) | Lossy (dct:requires) | None | None |
| Relation: refines (~) | Lossy (skos:narrower) | None | None |
| Relation: supersedes (⊘) | Clean (prov:wasRevisionOf) | Clean | Lossy (trusty URI versioning) |
| Relation: see_also (↔) | Clean (rdfs:seeAlso) | None | None |
| Evidence entry | Clean (prov:Entity) | Clean | Clean (provenance graph) |
| Evidence type | Lossy (PROV derivation subtypes) | Lossy | None |
| Evidence source/captured | Clean (dct:source + prov:generatedAtTime) | Clean | Clean |
| Rosetta header | None | None | None |
| Frontmatter (pipe-delimited) | None (encoding-level, no semantic target) | None | None |
| Views (display/voice) | None | None | None |
| Sections (## headings) | None (organizational, no RDF equivalent) | None | None |

**Score: 4 clean, 8 lossy, 9 none** out of 21 concepts mapped across
three standards (counting the best grade achieved across any target).

Restated: ~19% of KP:1 concepts translate cleanly to existing standards.
~38% translate with degradation. ~43% require custom vocabulary.

---

## 7. Implications

### Export: KP → RDF

**What you'd build:** A serializer that emits one typed `kp:Claim` node
per claim, with CiTO predicates for support/contradiction relations,
custom `kp:` namespace predicates for confidence, depth, nature, claim
type, and contradiction qualifiers. Evidence maps to PROV-O entities.
Pack metadata maps to Dublin Core + custom predicates in a metadata
graph. Relations use a mix of standard (`prov:wasRevisionOf`,
`rdfs:seeAlso`, `cito:supports`, `cito:disagreesWith`) and custom
(`kp:contradictsTension`, `kp:contradictsError`) predicates.

**What you'd lose:** The self-describing Rosetta header. The compact
encoding (dense/verbose distinction). The file-system structure (pack as
directory). The three-surface rendering model (views). The confidence
scale semantics. Claim ID locality. The authoring-optimized format.

**What you'd gain:** SPARQL queryability. Composability with any RDF
graph. Standard tooling (validators, visualizers, reasoners — though
reasoners won't understand the custom predicates). Global identity via URIs.
The ability to merge claims from different packs into a single graph.

### Import: RDF → KP

**What you'd gain:** Confidence, investigation depth, and claim nature as
first-class fields (not annotations). Typed contradiction preservation.
A self-describing, LLM-optimized format. A curated container (pack) with
lifecycle, versioning, and views. Zero-dependency consumption.

**What you'd invent:** Confidence values (RDF triples don't carry
uncertainty). Investigation depth (no source signal). Claim nature
classification. Contradiction qualifiers. Section organization. Views.
Essentially, the import would require a human or AI to perform epistemic
annotation — deciding how confident each triple is, how thoroughly it's
been investigated, and whether conflicting triples represent errors or
productive tensions.

### Interoperability Strategy: Bridge vs Native

A **bridge** approach — export KP:1 to RDF for query and interchange, with
documented loss — is practical today. The KP ontology (`kp:`) would be
small (~20 classes/properties) and could be published as OWL. Consumers
without the ontology would still see standard PROV-O provenance and Dublin
Core metadata; the KP-specific semantics (confidence, depth, contradiction
types) would degrade to opaque custom predicates.

A **native** approach — treating KP:1 as the authoritative format and
building tooling around it — is the current trajectory. RDF becomes an
export target, not the source of truth.

The two are not mutually exclusive. The most pragmatic path: author in
KP:1 (human-friendly, LLM-optimized), export to RDF/JSON-LD (machine
interchange, SPARQL query), accept the documented loss, and don't pretend
the round-trip is lossless.

---

*This document follows the same honesty standard as the positioning piece
it extends. If a mapping is wrong, imprecise, or unfair to a cited
standard, that is a bug.*
