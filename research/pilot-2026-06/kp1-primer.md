<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# How to read a KP:1 Knowledge Pack (reading primer)

The document you will receive is a KP:1 "Knowledge Pack": a claims file plus an
evidence file. Each claim is one assertion with explicit epistemic metadata.

## Claim anatomy

```text
- [C001] The assertion text
  {confidence|type|evidence|date|depth|nature} free-text context. →C002
```

The brace block has six positions (the last two are optional):

1. **confidence** — normalized 0.0–1.0 (0.95 = held at roughly 95%)
2. **type** — how the claim was established: `o`=observed directly,
   `r`=reported from a source, `c`=computed, `i`=inferred
3. **evidence** — IDs of supporting entries in the evidence file (`E001,E002`)
4. **date** — when the claim was established
5. **depth** (optional) — how deeply investigated: `assumed` | `investigated` | `exhaustive`
6. **nature** (optional) — `judgment` | `prediction` | `meta`; omitted = plain factual

## Relations

After the context, symbol+ID tokens declare typed relations to other claims:

| Symbol | Meaning |
|---|---|
| `→C002` | supports C002 |
| `←C002` | requires C002 (depends on it) |
| `~C002` | refines C002 |
| `⊗~C002` | contradicts C002 as a **productive tension** (both sides informative) |
| `⊗!C002` | contradicts C002 as an **error** (the other side is wrong; the declaring claim is the correction) |
| `⊘C002` | supersedes C002 (C002 is no longer operative) |
| `↔C002` | see also C002 |

## Three annotated examples (from an unrelated getting-started pack)

```text
- [C001] A Knowledge Pack is a directory of plain text
  {0.95|o|E001|2026-06-10} Verified by opening this very pack in any
  editor — PACK.yaml, claims.md, evidence.md, nothing hidden.
```
Read: *directly observed* (`o`), confidence 0.95, supported by evidence E001,
established 2026-06-10. No depth/nature given — a plain factual claim.

```text
- [C002] Every claim carries its own confidence and cites its evidence
  {0.90|o|E001,E002|2026-06-10} The block after each headline holds
  confidence, claim type, evidence IDs, and the date established. →C001
```
Read: observed, 0.90, two evidence entries, and it **supports** C001.

```text
- [C003] Uncertainty is recorded, not rounded away
  {0.60|i|E002|2026-06-10|investigated|judgment} A 0.60 stays a 0.60 —
  the reader decides what to make of it. ~C002
```
Read: an *inferred* claim (`i`), confidence 0.60, *investigated* depth,
*judgment* nature, and it **refines** C002.

## Verbose form

Some claims spell the same fields out in named form — identical meaning:

```text
- **[C030]** The assertion text
  `confidence: 0.90 | type: inferred | evidence: E001, E030 | since: 2026-03-01 | depth: exhaustive | nature: meta`
  Context text.
  `relations: requires C020`
```

## Evidence file

Each `## E001` entry in the evidence file gives the source's type, capture
date, name, and a short description. Claims cite evidence by these IDs.
