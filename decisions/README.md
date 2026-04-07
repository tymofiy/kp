# KP:1 Decisions

This directory contains substantive editor decisions made during the development and preview of KP:1. Each decision is captured as a dated Markdown file (one file per decision), recording the question, the options considered, the choice made, and the rationale.

## Why a decision log

Editor's drafts evolve. When the editor merges a normative change or chooses one option over another, the *reasoning* behind that choice tends to disappear into chat logs, issue threads, and memory. A decision log makes the reasoning durable and citable, so anyone reading the spec later can understand not just what it says but why it says it.

This is a common practice in standards work and in long-lived software projects. Examples of similar logs:

- W3C and IETF use issue trackers and meeting minutes to record design decisions, often summarized into rationale documents.
- Many software projects keep an `adr/` (Architecture Decision Records) directory that follows the [Michael Nygard ADR format](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).
- Rust uses a public RFC process where the rationale lives in the merged RFC document itself.

KP's decision log uses a simpler structure than ADRs because the project is small and the editor is the only decider during the preview phase.

## Format

Each decision is a single Markdown file named `YYYY-MM-DD-short-slug.md`, with this structure:

```markdown
# Decision: Short title

**Date:** YYYY-MM-DD
**Status:** accepted | superseded by YYYY-MM-DD-other-slug | reversed
**Editor:** Timothy Kompanchenko

## Question

What was being decided.

## Options considered

- Option A: ...
- Option B: ...
- Option C: ...

## Choice

Which option was selected.

## Rationale

Why. This is the part that matters most.

## Consequences

What this implies for downstream behavior, future decisions, or open questions.

## References

- Issues, PRs, prior discussions, external precedents
```

## Status of this directory

This directory is intentionally **minimal at the start of the preview phase**. The first decisions to be recorded here will likely be the resolutions of substantive issues raised by the initial preview cohort. Until then, the directory exists as a placeholder and a commitment: when significant decisions are made, they will be recorded here, in public, as the canonical record.

If you are reading this and wondering "where is the decision about X?" — the answer is either:

1. The decision was made before the public draft and is captured in the spec text itself or in `spec/CHANGELOG.md`.
2. The decision has not yet been made and is open for input via a GitHub issue.

Open an issue if there's a decision you think needs to be made or recorded.

## What changes when the Foundation forms

When the Knowledge Pack Foundation is incorporated, the decision-making model changes:

- Substantive changes will go through a formal RFC process, not just an editor decision
- RFCs will live in a dedicated `rfcs/` directory with a stricter template
- This `decisions/` directory will likely be preserved as a historical record of the pre-foundation period

See `GOVERNANCE.md` for the broader governance picture and the transition plan.
