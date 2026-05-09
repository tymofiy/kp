<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# AGENTS.md — start here if you are an AI

> **Audience:** an autonomous AI agent (Claude, GPT, Gemini, local model, etc.) reading this repository for the first time.
>
> **Purpose:** route you to the minimum required reading for your specific task, so you don't have to load all 9,000+ lines of normative prose into your context window before doing useful work.
>
> If you are a human, [`README.md`](README.md) is the better entry point.

---

## What KP:1 is, in three sentences

KP:1 (Knowledge Pack v1) is a plain-text format for representing **epistemic state** — claims with confidence, evidence, contradictions, and the trace of how beliefs evolved. It is designed to preserve the texture of knowledge (uncertainty, tension, supersession) that ordinary RAG pipelines and structured databases flatten away. The format is text-only, parser-deterministic, and AI-readable — but authoring a sound pack requires producer-side judgment that this repository documents in [`spec/AUTHORING.md`](spec/AUTHORING.md).

## The single example to read first

[`conformance/fixtures/valid/maximal.kpack/`](conformance/fixtures/valid/maximal.kpack/) demonstrates **all the hard features**: the `⊗!` (error) and `⊗~` (productive tension) qualifiers, supersession (`⊘`) chains, cross-pack `↔` references, all six metadata positions in the dense form, and meta-claims. It passes conformance. Read this before reading prose about what those features mean.

The two `examples/` packs (`solar-energy-market.kpack`, `kp-external-assessment.kpack`) are friendlier but exercise fewer features.

---

## Reading order by task

Pick your task. Read the **Required** column. The **Secondary** column is useful if your context window has room. The **Skip** column is unhelpful for your task and you should not load it.

| Your task | Required reading | Secondary | Skip |
|---|---|---|---|
| **A. Parse / validate an existing pack** | [`spec/CORE.md`](spec/CORE.md), [`conformance/grammar/kp-pack.schema.json`](conformance/grammar/kp-pack.schema.json), [`conformance/grammar/kp-claims.peg`](conformance/grammar/kp-claims.peg) | `conformance/fixtures/` (worked examples); [`spec/ARCHIVE.md`](spec/ARCHIVE.md) **if your parser handles sealed `.kpack` archives**; [`spec/COMPOSITION.md`](spec/COMPOSITION.md) **if your parser handles composition packs** (which may omit `evidence.md` and have narrative `claims.md`) | `spec/SPEC.md`, `spec/RATIONALE.md`, other companions |
| **B. Author a new pack** | [`spec/CORE.md`](spec/CORE.md), [`spec/AUTHORING.md`](spec/AUTHORING.md), [`conformance/fixtures/valid/maximal.kpack/`](conformance/fixtures/valid/maximal.kpack/) | [`spec/EXTENSIONS.md`](spec/EXTENSIONS.md) for `extensions.*` payloads | `spec/SPEC.md` (rationale; not needed for authoring), `spec/RATIONALE.md` (positioning, not authoring), `conformance/run.py` (validator internals) |
| **C. Reconcile two packs with contradictory claims** | [`spec/CORE.md`](spec/CORE.md) (relation symbols), [`spec/CONSISTENCY.md`](spec/CONSISTENCY.md), [`spec/AUTHORING.md`](spec/AUTHORING.md) §"Contradiction Qualifiers" | [`spec/RECONCILIATION.md`](spec/RECONCILIATION.md) — but note: full reconciliation algorithm is **deferred to v0.9 / v1.0**; for v0.8.0-preview you must compose `⊗!` / `⊗~` / `↔` primitives yourself per AUTHORING.md guidance | `spec/SPEC.md`, the rest of the companions |
| **D. Translate a pack into a second locale** | [`spec/MULTILINGUAL.md`](spec/MULTILINGUAL.md), [`spec/CORE.md`](spec/CORE.md) §10 (Views) | [`spec/VOICE.md`](spec/VOICE.md) if voice views are involved | `spec/SPEC.md`, `conformance/`, all companions except MULTILINGUAL/VOICE |
| **E. Compose a meeting / briefing pack from existing packs** | [`spec/COMPOSITION.md`](spec/COMPOSITION.md), [`spec/CORE.md`](spec/CORE.md) | [`conformance/fixtures/valid/composition.kpack/`](conformance/fixtures/valid/composition.kpack/) | `spec/SPEC.md`, the rest |
| **F. Self-driving voice playback of a pack** | [`spec/PLAYBACK.md`](spec/PLAYBACK.md), [`spec/VOICE.md`](spec/VOICE.md) | [`spec/CORE.md`](spec/CORE.md) §10 | All other companions |

If your task is none of A–F, default to **Task B** reading set and judge from there.

---

## Validate your own pack

The conformance runner in this repository validates the bundled fixtures and example packs but does not currently expose a `--pack PATH` flag. To validate a pack you authored:

```bash
# From the repo root, after cloning:
pip install -r conformance/requirements.txt

# Quickest: drop your pack into examples/ and run the suite
cp -r my-pack.kpack examples/
python3 conformance/run.py
```

Or in Python directly:

```python
import sys; sys.path.insert(0, 'conformance')
from run import validate_pack
errs = validate_pack('path/to/my-pack.kpack')
if errs:
    for e in errs: print(e)
else:
    print("PASS")
```

If validation fails, the runner names the **semantic constraint** (`SC-01` … `SC-11`) or **ambiguity resolution** (`AR-01` … `AR-16`) you violated. Look those up in [`spec/CORE.md`](spec/CORE.md) §12 and Appendix B.

---

## What you MUST NOT do

These rules are absolute. They are the most common ways a fresh agent breaks the format.

1. **MUST NOT translate `claims.md`.** Claims are always American English (per [`spec/MULTILINGUAL.md`](spec/MULTILINGUAL.md) §2 P1). Translations live in `views/{locale}/`. The single normative exception is `extensions.translations` for evidentiary multilingual domains (see MULTILINGUAL.md §12) — translations there are audit trail, not co-canonical claims.

2. **MUST NOT omit the Rosetta header** at the top of `claims.md`. Without it, conformance fails immediately. Copy from any fixture under `conformance/fixtures/valid/`.

3. **MUST NOT mix dense and verbose claim metadata within a single claim** ([`spec/CORE.md`](spec/CORE.md) AR-13). A claim uses either `{conf|type|ev|date|...}` (dense) OR `` `confidence: ... | type: ... | ...` `` (verbose). Not both.

4. **MUST NOT default to `⊗~` (productive tension) for every contradiction** to avoid making a judgment call. The whole point of the qualifier is to distinguish *known wrong* (`⊗!`) from *both informative* (`⊗~`). See [`spec/AUTHORING.md`](spec/AUTHORING.md) §"Contradiction Qualifiers" for the decision rubric.

5. **MUST NOT emit `1.0` confidence by default.** Reserve `1.0` for trivially-falsifiable claims (e.g., "this PDF contains the string 'X'"). For everything else, the volume and quality of evidence determines the value within a Sherman Kent band — see [`spec/AUTHORING.md`](spec/AUTHORING.md) §"Confidence Calibration".

6. **MUST NOT edit a claim in place after a pack version has been sealed.** Use `⊘` (supersedes) to replace; the original moves to `history.md`. The audit trail is the format's value proposition.

7. **MUST NOT add fields to PACK.yaml that are not in the schema** ([`conformance/grammar/kp-pack.schema.json`](conformance/grammar/kp-pack.schema.json)). The manifest root is closed. Producer-defined metadata goes under `extensions.*` (see [`spec/EXTENSIONS.md`](spec/EXTENSIONS.md)).

8. **MUST NOT translate or alter the syntactic operators (`→ ⊗ ⊗! ⊗~ ← ~ ⊘ ↔`) when localizing**. They are part of the syntax, not the prose. Translate the claim text only.

---

## What you can ignore

These exist in the repository but are not load-bearing for any of Tasks A–F:

- `positioning/` — public-facing positioning material, not normative
- `research/` — benchmark design and prior-art analysis, not normative
- `decisions/` — decision records, useful for understanding *why* but not *what*
- `scripts/` — git hooks and validation helpers, not normative
- `reference/` — placeholder for reference parser/tooling that ships separately
- `GOVERNANCE.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `LICENSE*`, `DCO.txt` — governance, not format

---

## Status as of v0.8.0-preview

The KP:1 specification is an **editor's draft**. The substantive format (claim grammar, manifest schema, conformance suite) is stable. Some companion documents are explicit stubs:

- [`spec/RECONCILIATION.md`](spec/RECONCILIATION.md) — concept-only stub. Full design deferred to v0.9 / v1.0 contingent on observing real cross-pack drift in ≥3 packs.
- [`spec/PLAYBACK.md`](spec/PLAYBACK.md) — experimental. Schema may evolve before v0.9.

The CLI tool sketches in `spec/SPEC.md` §13 (`kpack render`, `kpack reconcile`, `kpack lint`, etc.) describe **planned reference tooling**. The only command that exists today is `python3 conformance/run.py`. A contract-pointer stub at [`reference/kpack`](reference/kpack) tells you which spec section defines each subcommand's contract — run `./reference/kpack <subcommand>` to find out where to look. References to `kpack <command>` in the spec should be read as "the eventual reference tool will offer this command" — they are not currently runnable.

---

## If something seems wrong

The four most common false alarms when an agent first reads this repo:

1. **"The Quick Start example seems to be missing X."** It probably is intentionally minimal. Read [`conformance/fixtures/valid/maximal.kpack/`](conformance/fixtures/valid/maximal.kpack/) for the full feature surface.
2. **"CORE.md and SPEC.md disagree."** Where they appear to disagree on the implementable surface, **CORE.md wins** (per [`spec/README.md`](spec/README.md) "Three normative lanes"). SPEC.md provides surrounding rationale.
3. **"I cannot find a decision rule for X."** Check [`spec/AUTHORING.md`](spec/AUTHORING.md) first — that file is the producer-side rubric. If it isn't there, the spec genuinely does not yet specify it; report this as feedback rather than inventing one.
4. **"The conformance runner says my pack is invalid but I don't see why."** The error message names a specific `SC-NN` or `AR-NN`. Search [`spec/CORE.md`](spec/CORE.md) for that exact identifier; the rule and rationale are co-located.

---

*This file is a navigation aid, not a normative document. Where it conflicts with [`spec/CORE.md`](spec/CORE.md), CORE wins.*
