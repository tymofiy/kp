<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Contributing to KP:1

Thank you for your interest in KP:1. This document explains how to contribute during the **public draft preview phase**, before the Knowledge Pack Foundation is incorporated.

> **Status:** KP:1 is currently an editor's draft (`v0.8.1-preview` / `KP:1 Public Draft — 2026-05`). The contribution model described here is provisional and will change when the Foundation is formed and a contributor agreement is in place. See [GOVERNANCE.md](GOVERNANCE.md) for the full governance picture.

## What kinds of contributions we want right now

The preview phase is **feedback-driven**. The most valuable contributions are critical reviews, implementation experience, and adversarial challenges. Specifically:

| Contribution type | How to submit | Status |
|---|---|---|
| **Ambiguity reports** — places where the spec is unclear, contradictory, or open to multiple readings | GitHub issue, label `ambiguity` | Wanted |
| **Conformance edge cases** — packs or fixtures that the spec under-specifies | GitHub issue, label `conformance` | Wanted |
| **Implementation experience** — what broke when you tried to build a parser/validator from the docs | GitHub issue, label `implementation` | Wanted |
| **Comparison with other formats** — how KP:1 stacks up against RDF/JSON-LD, PROV-O, nanopublications, ARGUMENT INTERCHANGE FORMAT, etc. | GitHub issue, label `comparison` | Wanted |
| **Real-world workflow tests** — what happens when you actually try to use a pack in a workflow | GitHub issue, label `domain` | Wanted |
| **Benchmark proposals** — task designs that would empirically test KP:1 against alternatives | GitHub issue, label `benchmark` | Wanted |
| **Bug reports in the conformance suite** — fixtures that test the wrong thing, or are inconsistent with the grammar | GitHub issue, label `bug` | Wanted |
| **Bug reports in the grammar or schemas** — formal definition errors | GitHub issue, label `bug` | Wanted |
| **Translations of the spec** | Open an issue first to coordinate scope and publication path | Wanted |
| **New examples** — additional `.kpack` examples in different domains | PR to `examples/`, see Lane B below | Welcome |
| **Tooling and reference code** — improvements to the conformance runner, scripts, etc. | PR to `conformance/` or `scripts/`, see Lane C below | Welcome |

## What we are NOT accepting during the preview phase

- **Pull requests modifying normative spec text in `spec/`.** Open an issue instead. The editor will read it, discuss it publicly, and incorporate the change directly if accepted. This is a deliberate restriction to keep inbound IP clean until the Foundation has a contributor agreement in place. It is not a permanent policy.
- **For avoidance of doubt: changes to the formal grammar, JSON Schema, conformance fixtures, expected test outcomes, or other interoperability-significant artifacts are treated as normative during the preview phase and will not be merged from external PRs.** Even if a fixture or grammar change looks like a bug fix, it can shift conformance behavior, which is normative. Open an issue and propose the change there.
- **New companion specs** (additions to `spec/` beyond the existing companion documents). Open an issue to propose the topic; if it gains traction, the editor will draft it.
- **Renaming or restructuring proposals** that would break the existing layout. Open an issue first.
- **Pull requests that bundle multiple unrelated changes.** One concern per PR, please.

If you are unsure whether your contribution falls into "wanted" or "not accepted yet," open an issue and ask. We'd rather have a short conversation than turn away good work.

**The feedback-only restriction is temporary.** It exists because the Foundation has not yet adopted a contributor agreement with explicit patent terms. Once the Foundation is incorporated and has adopted that agreement (work is in progress with the goal of completion in 2026), normative pull requests become possible under the new contribution model. The closed door is short-term, not the project's long-term posture.

## How to file a high-signal issue

The most useful issues share a few qualities:

1. **Concrete.** Reference the exact section, claim, or grammar rule in question. Use file paths and line numbers.
2. **Reproducible.** If you found a problem trying to implement something, share the minimal reproduction (a fragment of a pack, a parser test, a lint result).
3. **One concern at a time.** If you have five issues, file five issues. They get triaged faster and resolved cleanly.
4. **Honest about confidence.** "I think X is wrong because Y" is better than "X is wrong." Saying "I am not sure if this is intended or a bug" is welcome and useful.
5. **Actionable.** If possible, propose what the spec should say instead. Even a wrong proposal is more useful than abstract complaint.

Issue templates may be added after the initial public release; until then, use a normal GitHub issue and include the information above.

## Review lanes (for the contribution types we DO accept as PRs)

External PRs to non-normative areas follow these review lanes. (Normative spec text PRs will be closed; see above.)

### Lane B — Additional examples (non-normative)

Required in the PR:

- clear intent (what the example is meant to demonstrate)
- explicit declaration that the example uses ONLY features the spec already defines (no hidden normative expansion)
- the example must validate cleanly under both strict and permissive modes against the existing conformance suite
- DCO sign-off on commits (see below)

**Note:** New conformance fixtures (especially invalid-pack fixtures that test specific failure modes) are treated as normative changes during the preview phase and are not accepted as external PRs. Open an issue to propose them; the editor will incorporate them if accepted. This is part of the broader rule that interoperability-significant artifacts are normative.

### Lane C — Reference tooling and scripts (non-validation-affecting)

Required in the PR:

- the change must NOT alter validation behavior, parser semantics, or conformance outcomes — those are normative and are not accepted as external PRs during preview
- existing conformance suite must still pass
- behavior diff notes (what changed and why)
- DCO sign-off on commits

If a tooling change would affect what packs validate or how they validate, it is a normative change. Open an issue instead.

### Lane D — Documentation, READMEs, typos

Required in the PR:

- one concern per PR
- DCO sign-off on commits

For documentation work, the bar is informal. Typo fixes and clarifications are welcome with minimal ceremony.

## Decision states (for issues and PRs)

After review, an issue or PR will be marked with one of:

- `accepted` — change merged or, for an issue, the editor has incorporated the resolution into the spec
- `accepted-with-followups` — incorporated, with linked issues for the unresolved parts
- `rejected-with-reason` — declined, with a written explanation in the thread
- `deferred` — held for later consideration; the editor will revisit when conditions change

Significant decisions are recorded in `decisions/` (RFC-style entries) so the rationale is traceable.

## Developer Certificate of Origin (DCO)

Code and documentation contributions require **DCO sign-off** on each commit. The DCO is a simple statement that you wrote the contribution (or have the right to submit it) and are licensing it under the project's terms.

To sign off, add `Signed-off-by: Your Name <your@email>` to each commit message. With git, use:

```bash
git commit -s
```

The full DCO text is in [DCO.txt](DCO.txt) (Linux Foundation Developer Certificate of Origin v1.1).

The DCO is sufficient for code, examples, conformance fixtures, and documentation. **It is not sufficient for normative spec contributions**, which is part of why those are not currently accepted as external PRs. When the Foundation adopts a contributor agreement (likely OWFa 1.0 or a W3C Community Group equivalent), normative contributions will become possible under that agreement.

## Code of Conduct

All contributors are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md). The short version: be respectful, assume good faith, and focus on the work.

## Decisions and rationale

All decisions on accepted, deferred, and rejected contributions are documented in the issue or PR thread itself. Significant design decisions also get a dated entry in `decisions/`. The decision log is the canonical record of *why* the spec is shaped the way it is.

If you disagree with a decision, the right path is to open a new issue with the additional argument or evidence. The editor explicitly reserves the right to reverse decisions when new information warrants it.

## Escalation

If a discussion reaches an impasse on a contract semantics question:

1. Discussion is paused.
2. A focused RFC issue is opened with the specific question and the positions in tension.
3. The editor weighs the arguments and writes a decision into `decisions/`.
4. The thread is closed with a link to the decision.

This is provisional. Once the Foundation exists, contested decisions will go through a formal RFC process with broader review.

## What changes when the Foundation is formed

When the Knowledge Pack Foundation is incorporated:

- The feedback-only restriction on normative contributions is **lifted**.
- A formal contributor agreement (likely OWFa 1.0) is adopted, with explicit patent grant terms.
- A formal RFC process replaces editor-as-decider for substantive design changes.
- IP in the spec text and the trademark transfers to the Foundation.
- This document is replaced by the Foundation's contribution policy.

## Questions

Open an issue, or for private matters (legal, IP, partnerships, donor conversations, foundation formation), email the editor: Timothy Kompanchenko <tymofi@mac.com>.

Thank you for contributing.
