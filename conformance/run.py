#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Timothy Kompanchenko
"""KP:1 Conformance Test Runner — Phase C3

Validates .kpack directories against the KP:1 spec.

The PEG grammar in grammar/kp-claims.peg is the normative reference for
KP:1 claim syntax. This runner validates equivalent regular-expression
patterns for the v0.7-preview release; a PEG-driven parser using
parsimonious or lark is planned for a future phase. JSON Schema
validation and semantic constraints SC-01 through SC-11 are also
enforced. See conformance/README.md for the grammar-vs-runner contract.

Dependencies: pyyaml, jsonschema (see requirements.txt)
Usage: python3 conformance/run.py
"""

import datetime
import json
import re
import sys
from pathlib import Path

import yaml
import jsonschema


# ── Formatting ─────────────────────────────────────────────────────

GREEN = "\033[32m"
RED = "\033[31m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


# ── Paths ──────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = SCRIPT_DIR / "grammar" / "kp-pack.schema.json"
SIGNATURES_SCHEMA_PATH = SCRIPT_DIR / "grammar" / "kp-signatures.schema.json"
FIXTURES_DIR = SCRIPT_DIR / "fixtures"
EXAMPLES_DIR = SCRIPT_DIR.parent / "examples"

VALID_ORDER = [
    "minimal.kpack",
    "typical.kpack",
    "verbose-claims.kpack",
    "mixed-syntax.kpack",
    "maximal.kpack",
    "composition.kpack",
]
INVALID_ORDER = [
    "no-rosetta.kpack",
    "orphan-evidence-ref.kpack",
    "confidence-overflow.kpack",
    "duplicate-ids.kpack",
    "missing-evidence-field.kpack",
]

# Expected error categories for invalid fixtures.
# The first error raised must match this category prefix.
INVALID_EXPECTED = {
    "no-rosetta.kpack": "parse",
    "orphan-evidence-ref.kpack": "SC-03",
    "confidence-overflow.kpack": "SC-01",
    "duplicate-ids.kpack": "SC-02",
    "missing-evidence-field.kpack": "parse",
}
EXAMPLE_ORDER = [
    "solar-energy-market.kpack",
    "kp-external-assessment.kpack",
]

VERBOSE_TYPE_MAP = {
    "observed": "o",
    "reported": "r",
    "computed": "c",
    "inferred": "i",
}

_schema_cache = None
_signatures_schema_cache = None


def schema():
    global _schema_cache
    if _schema_cache is None:
        with open(SCHEMA_PATH) as f:
            _schema_cache = json.load(f)
    return _schema_cache


def signatures_schema():
    global _signatures_schema_cache
    if _signatures_schema_cache is None:
        with open(SIGNATURES_SCHEMA_PATH) as f:
            _signatures_schema_cache = json.load(f)
    return _signatures_schema_cache


def _stringify_dates(obj):
    """Convert datetime.date objects from PyYAML back to ISO strings."""
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _stringify_dates(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_stringify_dates(i) for i in obj]
    return obj


# ── Validation ─────────────────────────────────────────────────────

class Err:
    """Single validation error with category and message."""

    __slots__ = ("cat", "msg")

    def __init__(self, cat: str, msg: str):
        self.cat = cat
        self.msg = msg

    def __str__(self):
        return f"{self.cat}: {self.msg}"


# Compiled regexes used during claim parsing
_CLAIM_START = re.compile(r"^- (?:\*\*)?(\[C[^\]]+\])(?:\*\*)?\s+(.+)")
_CLAIM_ID = re.compile(r"\[(C\d+(?:-v\d+)?)\]")
_REL_DENSE = re.compile(r"(\u2297~|\u2297!|\u2297|\u2192|\u2190|\u2298|\u2194|~)(C\d+(?:-v\d+)?)")
_REL_VERBOSE = re.compile(
    r"(supports|contradicts:error|contradicts:tension|contradicts"
    r"|requires|refines|supersedes|see_also)\s+([\w#-]+)"
)
_VERBOSE_REL_LINE = re.compile(r"`relations:\s*(.+?)`")


def validate_pack(pack_dir: Path) -> list[Err]:
    """Validate a .kpack directory. Returns list of errors (empty = valid)."""
    pack_dir = Path(pack_dir)
    errs: list[Err] = []

    # ── Required files ──
    pack_yaml_path = pack_dir / "PACK.yaml"
    claims_path = pack_dir / "claims.md"
    evidence_path = pack_dir / "evidence.md"
    composition_path = pack_dir / "composition.yaml"
    signatures_path = pack_dir / "signatures.yaml"

    # Composition packs MAY omit evidence.md (SPEC.md §2,
    # "Composition-pack File Requirements"). claims.md remains required.
    is_composition = composition_path.exists()
    required_files = [pack_yaml_path, claims_path]
    if not is_composition:
        required_files.append(evidence_path)

    for p in required_files:
        if not p.exists():
            errs.append(Err("parse", f"missing {p.name}"))
    if errs:
        return errs

    # ── PACK.yaml: load and validate against JSON Schema ──
    try:
        pack = _stringify_dates(yaml.safe_load(pack_yaml_path.read_text()))
    except yaml.YAMLError as e:
        return [Err("schema", f"PACK.yaml parse error: {e}")]

    try:
        jsonschema.validate(pack, schema())
    except jsonschema.ValidationError as e:
        errs.append(Err("schema", e.message))

    # ── signatures.yaml: validate against its schema (if present) ──
    if signatures_path.exists():
        try:
            sigs = _stringify_dates(yaml.safe_load(signatures_path.read_text()))
        except yaml.YAMLError as e:
            errs.append(Err("signatures", f"signatures.yaml parse error: {e}"))
        else:
            if sigs is None:
                errs.append(Err("signatures", "signatures.yaml is empty"))
            else:
                try:
                    jsonschema.validate(
                        sigs,
                        signatures_schema(),
                        format_checker=jsonschema.FormatChecker(),
                    )
                except jsonschema.ValidationError as e:
                    errs.append(Err("signatures", f"signatures.yaml: {e.message}"))

    # ── claims.md: Rosetta header ──
    text = claims_path.read_text()
    rosetta = re.match(r"<!-- KP:(\d+)\s", text)
    if not rosetta:
        return [Err("parse", "missing Rosetta header")]

    spec_ver = int(rosetta.group(1))
    if spec_ver != 1:  # SC-06
        errs.append(Err("SC-06", f"spec version {spec_ver} != 1"))

    # ── claims.md: frontmatter ──
    fm = re.search(
        r"^---\s*\n"
        r"pack:\s+(\S+)\s+\|\s+v:\s+(\S+)\s+\|\s+domain:\s+(\S+)\s*\n"
        r"confidence:\s+(\S+)\s+\|\s+normalized\s*\n"
        r"---",
        text,
        re.MULTILINE,
    )
    if not fm:
        return errs + [Err("parse", "invalid frontmatter")]

    fm_name, fm_ver, fm_dom, fm_scale = fm.group(1), fm.group(2), fm.group(3), fm.group(4)

    # SC-07 through SC-10: frontmatter ↔ PACK.yaml consistency
    if pack.get("name") != fm_name:
        errs.append(Err("SC-07", f"pack name '{fm_name}' != PACK.yaml '{pack.get('name')}'"))
    if pack.get("version") != fm_ver:
        errs.append(Err("SC-08", f"version '{fm_ver}' != PACK.yaml '{pack.get('version')}'"))
    if pack.get("domain") != fm_dom:
        errs.append(Err("SC-09", f"domain '{fm_dom}' != PACK.yaml '{pack.get('domain')}'"))
    pc = pack.get("confidence")
    if isinstance(pc, dict) and "scale" in pc and pc["scale"] != fm_scale:
        errs.append(Err("SC-10", f"scale '{fm_scale}' != PACK.yaml '{pc['scale']}'"))

    # ── evidence.md: extract defined evidence IDs (empty set if absent) ──
    ev_ids: set[str] = set()
    if evidence_path.exists():
        ev_ids = set(re.findall(r"^## (E\d+)", evidence_path.read_text(), re.MULTILINE))

    # ── claims.md: parse claim blocks ──
    # A claim block starts with `- [C###]` or `- **[C###]**` and includes
    # all subsequent continuation lines (indented 2+ spaces).

    blocks: list[dict] = []
    cur = None
    for line in text.split("\n"):
        m = _CLAIM_START.match(line)
        if m:
            if cur:
                blocks.append(cur)
            cur = {"raw_id": m.group(1), "cont": []}
        elif cur is not None and line.startswith("  "):
            cur["cont"].append(line.strip())
        elif cur is not None and re.match(r"^##?\s", line):
            blocks.append(cur)
            cur = None
    if cur:
        blocks.append(cur)

    # Accumulators for semantic checks
    claim_ids: list[str] = []
    confidences: list[tuple[str, float, str]] = []  # (cid, value, original_str)
    ev_refs: list[tuple[str, str]] = []  # (cid, "E###")
    relations: list[tuple[str, str, str]] = []  # (source, symbol/name, target)

    for blk in blocks:
        id_m = _CLAIM_ID.match(blk["raw_id"])
        if not id_m:
            errs.append(Err("parse", f"invalid claim ID: {blk['raw_id']}"))
            continue
        cid = id_m.group(1)
        claim_ids.append(cid)

        if not blk["cont"]:
            errs.append(Err("parse", f"no metadata for {cid}"))
            continue

        first = blk["cont"][0]

        # Detect metadata format from the first continuation line
        dense = re.match(r"\{([^}]+)\}", first)
        verbose = re.match(r"`(confidence:\s*\d+\.\d+[^`]*)`", first)

        if dense:
            parts = dense.group(1).split("|")
            if len(parts) < 4:
                errs.append(Err("parse", f"dense metadata <4 fields for {cid}"))
                continue

            conf_s = parts[0].strip()
            type_s = parts[1].strip()
            ev_s = parts[2].strip()

            # Validate dense claim type letter
            if type_s not in {"o", "r", "c", "i"}:
                errs.append(Err("parse", f"invalid claim type '{type_s}' for {cid} (expected o/r/c/i)"))

            # Empty evidence position → syntactic error
            if not ev_s:
                errs.append(Err("parse", f"empty evidence ref list for {cid}"))
                continue

            try:
                confidences.append((cid, float(conf_s), conf_s))
            except ValueError:
                errs.append(Err("parse", f"invalid confidence '{conf_s}' for {cid}"))

            for ref in ev_s.split(","):
                ref = ref.strip()
                if ref:
                    ev_refs.append((cid, ref))

            # Dense relations: search after closing } on metadata line,
            # plus all subsequent continuation lines
            after_brace = first[dense.end():]
            for rm in _REL_DENSE.finditer(after_brace):
                relations.append((cid, rm.group(1), rm.group(2)))
            for cl in blk["cont"][1:]:
                for rm in _REL_DENSE.finditer(cl):
                    relations.append((cid, rm.group(1), rm.group(2)))

        elif verbose:
            meta = verbose.group(1)

            # Confidence
            cm = re.search(r"confidence:\s*(\d+\.\d+)", meta)
            if cm:
                confidences.append((cid, float(cm.group(1)), cm.group(1)))

            # Evidence refs
            em = re.search(r"evidence:\s*([^|]+)", meta)
            if em:
                for ref in em.group(1).strip().split(","):
                    ref = ref.strip()
                    if ref:
                        ev_refs.append((cid, ref))

            # SC-11: verbose type names
            tm = re.search(r"type:\s*(\w+)", meta)
            if tm and tm.group(1) not in VERBOSE_TYPE_MAP:
                errs.append(Err("SC-11", f"unknown verbose type '{tm.group(1)}' for {cid}"))

            # Verbose relations
            for cl in blk["cont"]:
                rl = _VERBOSE_REL_LINE.search(cl)
                if rl:
                    for rm in _REL_VERBOSE.finditer(rl.group(1)):
                        relations.append((cid, rm.group(1), rm.group(2)))

        else:
            errs.append(Err("parse", f"no metadata for {cid}"))

    # ── Semantic constraints ──

    # SC-01: Confidence in [0.0, 1.0]
    for cid, val, orig in confidences:
        if val < 0.0 or val > 1.0:
            errs.append(Err("SC-01", f"confidence {orig} out of range for {cid}"))

    # SC-02: Unique claim IDs
    seen: set[str] = set()
    for cid in claim_ids:
        if cid in seen:
            errs.append(Err("SC-02", f"duplicate claim ID {cid}"))
        seen.add(cid)

    # SC-03: All evidence refs must exist in evidence.md
    for cid, ref in ev_refs:
        if ref not in ev_ids:
            errs.append(Err("SC-03", f"{ref} not in evidence.md (referenced by {cid})"))

    # SC-04: Supersession chains must be acyclic
    sup_graph: dict[str, list[str]] = {}
    for src, sym, tgt in relations:
        if sym in ("\u2298", "supersedes"):  # ⊘
            sup_graph.setdefault(src, []).append(tgt)

    def has_cycle(graph: dict) -> bool:
        visited: set[str] = set()
        in_stack: set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            in_stack.add(node)
            for nb in graph.get(node, []):
                if nb in in_stack:
                    return True
                if nb not in visited and dfs(nb):
                    return True
            in_stack.discard(node)
            return False

        return any(dfs(n) for n in graph if n not in visited)

    if has_cycle(sup_graph):
        errs.append(Err("SC-04", "supersession cycle detected"))

    # SC-05: All relation targets must exist (cross-pack refs exempt)
    cid_set = set(claim_ids)
    for src, _sym, tgt in relations:
        if "#" in tgt:
            continue  # cross-pack reference
        if tgt not in cid_set:
            errs.append(Err("SC-05", f"relation target {tgt} not found (from {src})"))

    return errs


# ── Runner ─────────────────────────────────────────────────────────


def main():
    print(f"\n{BOLD}KP:1 Conformance Test Runner{RESET}")
    print("=" * 29)

    total = 0
    passed = 0

    def run_group(title: str, base_dir: Path, names: list[str], expect_pass: bool):
        nonlocal total, passed
        print(f"\n{BOLD}{title}{RESET}")
        for name in names:
            path = base_dir / name
            if not path.is_dir():
                print(f"  {name:<35} {DIM}SKIP (not found){RESET}")
                continue
            errs = validate_pack(path)
            total += 1
            if expect_pass:
                if not errs:
                    passed += 1
                    print(f"  {name:<35} {GREEN}PASS{RESET}")
                else:
                    print(f"  {name:<35} {RED}FAIL{RESET}  ({errs[0]})")
            else:
                # Invalid fixture: we EXPECT errors with the right category
                expected_cat = INVALID_EXPECTED.get(name)
                if errs and errs[0].cat == expected_cat:
                    passed += 1
                    print(f"  {name:<35} {GREEN}FAIL{RESET}  ({errs[0]})")
                elif errs:
                    print(f"  {name:<35} {RED}FAIL{RESET}  (wrong error: {errs[0]}, expected {expected_cat})")
                else:
                    print(f"  {name:<35} {RED}PASS{RESET}  (expected failure)")

    run_group("Valid fixtures (expect PASS):", FIXTURES_DIR / "valid", VALID_ORDER, True)
    run_group("Invalid fixtures (expect FAIL):", FIXTURES_DIR / "invalid", INVALID_ORDER, False)
    run_group("Examples:", EXAMPLES_DIR, EXAMPLE_ORDER, True)

    # Summary
    print()
    color = GREEN if passed == total else RED
    print(f"{color}{BOLD}Result: {passed}/{total} passed{RESET}\n")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
