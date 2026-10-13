<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# KP:1 Intent and Principles for Public Sharing

## Intent

KP:1 is intended as an AI-first, lasting knowledge system. It can carry an articulated understanding of a subject: explanations and connections, perspectives, reasoning and grounds, including disagreement, uncertainty and changes. Evidence and validation support that purpose; they are not its whole scope. People and AI should be able to examine, challenge and continue work from the record across tasks and tools.

The common format provides a record. Applications provide retrieval, reasoning, execution and review. Rich retained context and task-specific views serve different needs: a view selects what is useful now, while the original record remains available for later understanding and correction.

The specification should remain useful beyond its initial author and applications. Its public contract, examples and evidence must be open to other people's purposes, implementations and criticism. Continuing the inquiry can mean disagreeing with an assessment or choosing a different action.

The goal of publishing KP:1 is not status signaling or claiming authority.  
The goal is to improve the work by exposing it to rigorous, constructive critique.

Public release is used as an improvement engine:

1. force clearer articulation
2. force cleaner boundaries
3. force reproducible implementation behavior
4. invite challenge from peers and domain experts
5. convert criticism into concrete iterations

## Success Definition

Success is not "being called a standard."
Success is:

- more precise and coherent contract definitions
- better conformance and fewer ambiguities
- stronger implementation portability
- clearer evidence about where KP:1 helps and where it does not
- meaningful external participation in critique and refinement

## Non-Goals

- claiming universal supremacy over other formats
- locking governance before evidence and adoption feedback
- optimizing for hype over technical correctness
- hiding weaknesses to look polished
- introducing any required registry, index, or central service for conformance
- embedding model-specific artifacts (vector indexes, feature embeddings) inside a pack, which would tie portable knowledge to one model or provider
- requiring cryptographic signing, keys, or verification tooling in order to *read* a pack
- anchoring provenance to external identity or ledger systems (e.g. decentralized-identity credentials, blockchain) that a pack cannot be read without
- gating the core read / own / local-model path behind certification, membership, or a paid tier

## Operating Principles

1. **Truth over posture**  
   We state what is draft, what is stable, and what is unresolved.

2. **Challenge is a feature**  
   Critical feedback is welcomed and routed into concrete artifacts.

3. **Strict core, explicit extensions**  
   Canonical contract and profile-specific behavior are clearly separated.

4. **Evidence before strong claims**  
   Major positioning statements should be tied to measurable validation.

5. **Reproducibility over persuasion**  
   If others cannot reproduce behavior, the spec is not ready.

6. **Independence by design**  
   Owning the files must remain sufficient to read them: no required tool, registry, key, or
   permission, in perpetuity. Capture-resistance comes from requiring *less*, not adding governance.
   See [INDEPENDENCE.md](../spec/INDEPENDENCE.md).

## Practical Framing Statement

"We are publishing KP:1 as a public draft to actively improve it. We want critique,
implementation feedback, and empirical challenge. The objective is a clearer and
more reliable epistemic-state format, not premature standard branding."
