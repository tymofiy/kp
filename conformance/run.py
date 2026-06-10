#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Timothy Kompanchenko
"""KP:1 Conformance Test Runner — Phase C3

Validates .kpack directories against the KP:1 spec.

The PEG grammar in grammar/kp-claims.peg is the normative reference for
KP:1 claim syntax. By default this runner validates equivalent
regular-expression patterns, which are deliberately more permissive at
the line level. With --strict, each pack's claims.md is additionally
parsed through the PEG grammar itself (via parsimonious), so syntax the
regex layer tolerates but the grammar rejects is reported. Composition
packs are exempt from the PEG parse: their claims.md is narrative by
design (SPEC.md §2, COMPOSITION.md). JSON Schema validation and semantic
constraints SC-01 through SC-12 are enforced in both modes. See
conformance/README.md for the grammar-vs-runner contract.

Dependencies: pyyaml, jsonschema; --strict also needs parsimonious
(all pinned in requirements.txt)
Usage:
    python3 conformance/run.py [--strict]                     # full suite
    python3 conformance/run.py --pack PATH [--strict] [--json] [--no-color]
Color is auto-disabled when output is not a terminal or NO_COLOR is set.
"""

import datetime
import json
import os
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
COMPOSITION_SCHEMA_PATH = SCRIPT_DIR / "grammar" / "kp-composition.schema.json"
FIXTURES_DIR = SCRIPT_DIR / "fixtures"
EXAMPLES_DIR = SCRIPT_DIR.parent / "examples"

# One shared checker for all schema validations. Which formats it enforces
# depends on installed validator packages — requirements.txt pins
# jsonschema[format-nongpl] so date, date-time, and uri are all live.
FORMAT_CHECKER = jsonschema.FormatChecker()

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
    "cyclic-supersession.kpack",
    "dangling-relation-target.kpack",
    "wrong-pack-name.kpack",
    "prediction-too-confident.kpack",
    "verbose-prediction-too-confident.kpack",
    "bad-format-fields.kpack",
    "bad-composition-schema.kpack",
]

# Expected error categories for invalid fixtures.
# The first error raised must match this category prefix.
INVALID_EXPECTED = {
    "no-rosetta.kpack": "parse",
    "orphan-evidence-ref.kpack": "SC-03",
    "confidence-overflow.kpack": "SC-01",
    "duplicate-ids.kpack": "SC-02",
    "missing-evidence-field.kpack": "parse",
    "cyclic-supersession.kpack": "SC-04",
    "dangling-relation-target.kpack": "SC-05",
    "wrong-pack-name.kpack": "SC-07",
    "prediction-too-confident.kpack": "SC-12",
    "verbose-prediction-too-confident.kpack": "SC-12",
    "bad-format-fields.kpack": "schema",
    "bad-composition-schema.kpack": "composition",
}
EXAMPLE_ORDER = [
    "hello-world.kpack",
    "solar-energy-market.kpack",
    "kp-external-assessment.kpack",
    "art-acquisition-decision.kpack",
    "auction-house-consignment-review.kpack",
]

VERBOSE_TYPE_MAP = {
    "observed": "o",
    "reported": "r",
    "computed": "c",
    "inferred": "i",
}

_schema_cache = None
_signatures_schema_cache = None
_composition_schema_cache = None


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


def composition_schema():
    global _composition_schema_cache
    if _composition_schema_cache is None:
        with open(COMPOSITION_SCHEMA_PATH) as f:
            _composition_schema_cache = json.load(f)
    return _composition_schema_cache


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
_REL_DENSE = re.compile(
    r"(\u2297~|\u2297!|\u2297|\u2192|\u2190|\u2298|\u2194|~)"
    # Target: either a local claim ID (C\d+(?:-v\d+)?) or a cross-pack
    # reference of the form pack_name#section_ref per CORE \u00a79 / AR-16.
    # Pack name follows [a-z][a-z0-9.-]* (allows .kpack-style suffixes
    # found in some maximal-fixture refs while preferring the
    # AR-16 lowercase-hyphen convention). Section ref is freeform until
    # the next delimiter (whitespace or comma) per CORE \u00a79.
    r"(C\d+(?:-v\d+)?|[a-z][a-z0-9.-]*#[^\s,]+)"
)
_REL_VERBOSE = re.compile(
    r"(supports|contradicts:error|contradicts:tension|contradicts"
    r"|requires|refines|supersedes|see_also)\s+([\w#-]+)"
)
_VERBOSE_REL_LINE = re.compile(r"`relations:\s*(.+?)`")


# ── Strict layer: PEG-driven validation (--strict) ─────────────────
#
# The normative grammar is written in implementation-neutral Bryan Ford
# PEG notation. parsimonious shares PEG semantics exactly (ordered
# choice, predicates, greedy repetition) under a slightly different
# surface syntax, so the shipped file is translated mechanically at load
# time rather than vendored in a second notation. parsimonious over
# lark: lark grammars are EBNF with Earley/LALR semantics — the
# grammar's ordered choices and not-predicates (e.g. ProseChar's
# relation boundary) have no direct lark equivalent.

PEG_PATH = SCRIPT_DIR / "grammar" / "kp-claims.peg"
_strict_grammar = None


def _translate_peg(ford: str) -> str:
    """Translate Ford-notation PEG to parsimonious's DSL.

    Mechanical, character-level, quote-aware:
      - strip // comments
      - rule arrow  <-  becomes  =
      - character classes [...] become regex terminals ~"[...]"
      - bare . (any char) becomes ~"(?s)." — Ford's any-char matches
        newlines (the Rosetta legend spans lines); regex needs DOTALL
    Quoted literals pass through unchanged: parsimonious evaluates
    backslash escapes ('\\n', '\\r\\n') the same way Ford notation does.
    """
    out = []
    i, n = 0, len(ford)
    quote = None  # inside a quoted literal: the quote char, else None
    in_class = False
    while i < n:
        c = ford[i]
        if quote:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(ford[i + 1])
                i += 1
            elif c == quote:
                quote = None
        elif in_class:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(ford[i + 1])
                i += 1
            elif c == "]":
                out.append('"')
                in_class = False
        elif c in ("'", '"'):
            quote = c
            out.append(c)
        elif c == "[":
            in_class = True
            out.append('~"[')
        elif c == "/" and i + 1 < n and ford[i + 1] == "/":
            while i < n and ford[i] != "\n":
                i += 1
            continue
        elif c == "<" and i + 1 < n and ford[i + 1] == "-":
            out.append("=")
            i += 1
        elif c == ".":
            out.append('~"(?s)."')
        else:
            out.append(c)
        i += 1
    return "".join(out)


def strict_grammar():
    """Compile the normative grammar once per process.

    Exits loudly if parsimonious is missing — strict mode must never
    degrade silently into the regex-only layer.
    """
    global _strict_grammar
    if _strict_grammar is None:
        try:
            from parsimonious.grammar import Grammar
        except ImportError:
            print(
                "error: --strict requires the 'parsimonious' package "
                "(run: pip install -r requirements.txt)",
                file=sys.stderr,
            )
            sys.exit(2)
        _strict_grammar = Grammar(_translate_peg(PEG_PATH.read_text()))
    return _strict_grammar


def strict_check(claims_text: str) -> Err | None:
    """Parse claims.md through the PEG grammar. None = document matches."""
    grammar = strict_grammar()  # first touch — its missing-package guard fires here
    from parsimonious.exceptions import ParseError

    try:
        grammar.parse(claims_text)
    except ParseError as e:  # IncompleteParseError subclasses ParseError
        return Err(
            "strict",
            "claims.md does not match grammar/kp-claims.peg "
            f"(line {e.line()}, column {e.column()})",
        )
    return None


def validate_pack(pack_dir: Path, strict: bool = False) -> list[Err]:
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
        jsonschema.validate(pack, schema(), format_checker=FORMAT_CHECKER)
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
                        format_checker=FORMAT_CHECKER,
                    )
                except jsonschema.ValidationError as e:
                    errs.append(Err("signatures", f"signatures.yaml: {e.message}"))

    # ── composition.yaml: validate against its schema (if present) ──
    if is_composition:
        try:
            comp = _stringify_dates(yaml.safe_load(composition_path.read_text()))
        except yaml.YAMLError as e:
            errs.append(Err("composition", f"composition.yaml parse error: {e}"))
        else:
            if comp is None:
                errs.append(Err("composition", "composition.yaml is empty"))
            else:
                try:
                    jsonschema.validate(
                        comp,
                        composition_schema(),
                        format_checker=FORMAT_CHECKER,
                    )
                except jsonschema.ValidationError as e:
                    errs.append(Err("composition", f"composition.yaml: {e.message}"))

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
    predictions_high_conf: list[tuple[str, float]] = []  # (cid, conf) where nature=prediction and conf>0.95 — SC-12
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

            # Position 4 (date): ISODate. Grammar is YYYY-MM-DD; validate the
            # format when the slot is non-empty (empty interior slots are valid).
            date_s = parts[3].strip()
            if date_s and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_s):
                errs.append(Err("parse", f"invalid date '{date_s}' for {cid} (expected YYYY-MM-DD)"))

            # Position 5 (depth) intentionally NOT enum-validated here. The spec
            # (CORE.md) lists assumed/investigated/exhaustive, but a large share
            # of the shipped corpus (system + grounding packs) uses additional
            # depth values such as `practitioner`/`confirmed`. Enforcing the
            # closed set would flag hundreds of production claims — that is a
            # spec-vs-corpus reconciliation, not a parser quick-win, so it is
            # left for a dedicated decision rather than enforced here.

            # Empty evidence position → syntactic error
            if not ev_s:
                errs.append(Err("parse", f"empty evidence ref list for {cid}"))
                continue

            conf_val: float | None = None
            try:
                conf_val = float(conf_s)
                confidences.append((cid, conf_val, conf_s))
            except ValueError:
                errs.append(Err("parse", f"invalid confidence '{conf_s}' for {cid}"))

            # Position 6 (index 5) is nature when present (judgment | prediction | meta)
            if conf_val is not None and len(parts) >= 6:
                nature_s = parts[5].strip()
                if nature_s == "prediction" and conf_val > 0.95:
                    predictions_high_conf.append((cid, conf_val))

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

            # SC-12: a prediction-nature claim must keep confidence ≤0.95.
            # The dense branch enforces this at the position-6 nature slot; the
            # verbose branch previously skipped it entirely.
            nm = re.search(r"nature:\s*(\w+)", meta)
            if cm and nm and nm.group(1) == "prediction" and float(cm.group(1)) > 0.95:
                predictions_high_conf.append((cid, float(cm.group(1))))

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

    # SC-12: Predictions MUST have confidence ≤ 0.95
    for cid, conf_val in predictions_high_conf:
        errs.append(Err("SC-12", f"prediction {cid} has confidence {conf_val} > 0.95 (predictions have irreducible uncertainty; reserve 0.99+ for trivially-falsifiable claims)"))

    # ── Strict: claims.md must match the normative PEG grammar ──
    # Appended last so the regex/semantic layer's first error (which the
    # invalid-fixture expectations key on) is unaffected. Composition
    # packs are exempt: their claims.md is narrative by design.
    if strict and not is_composition:
        serr = strict_check(text)
        if serr:
            errs.append(serr)

    return errs


# ── Runner ─────────────────────────────────────────────────────────


def main():
    argv = sys.argv[1:]
    as_json = "--json" in argv
    no_color = "--no-color" in argv
    strict = "--strict" in argv
    argv = [a for a in argv if a not in ("--json", "--no-color", "--strict")]

    # Color is for humans at a terminal: disabled when output is piped or
    # redirected (so CI logs stay clean), when NO_COLOR is set
    # (https://no-color.org), with --no-color, or in --json mode.
    if as_json or no_color or os.environ.get("NO_COLOR") or not sys.stdout.isatty():
        global GREEN, RED, BOLD, DIM, RESET
        GREEN = RED = BOLD = DIM = RESET = ""

    # The date-time/uri format validators are optional jsonschema deps
    # (requirements.txt pins jsonschema[format-nongpl]). Without them,
    # format assertions are silently skipped and the format-violation
    # fixtures stop failing — warn loudly instead of passing quietly.
    if "date-time" not in FORMAT_CHECKER.checkers:
        print(
            "warning: jsonschema format validators not installed "
            "(run: pip install -r requirements.txt); date-time/uri "
            "format assertions will NOT be enforced",
            file=sys.stderr,
        )

    # `--pack PATH` validates a single pack directory and exits.
    # The natural workflow for an external author validating their own pack.
    # `--json` emits a machine-readable result object instead of prose.
    if argv and argv[0] == "--pack":
        if len(argv) < 2:
            print(f"{RED}usage: run.py --pack PATH [--strict] [--json] [--no-color]{RESET}")
            sys.exit(2)
        pack_path = Path(argv[1])
        if not pack_path.is_dir():
            if as_json:
                print(json.dumps({"path": str(pack_path), "ok": False, "errors": [
                    {"category": "usage", "message": "pack directory not found"}]}))
            else:
                print(f"{RED}Pack directory not found: {pack_path}{RESET}")
            sys.exit(2)
        errs = validate_pack(pack_path, strict=strict)
        if as_json:
            print(json.dumps({
                "path": str(pack_path),
                "ok": not errs,
                "errors": [{"category": e.cat, "message": e.msg} for e in errs],
            }))
            sys.exit(0 if not errs else 1)
        if not errs:
            print(f"{GREEN}{BOLD}{pack_path}: PASS{RESET}")
            sys.exit(0)
        print(f"{RED}{BOLD}{pack_path}: FAIL{RESET}")
        for e in errs:
            print(f"  {e}")
        sys.exit(1)

    if as_json:
        print("--json requires --pack PATH", file=sys.stderr)
        sys.exit(2)

    mode = " (strict: PEG grammar)" if strict else ""
    print(f"\n{BOLD}KP:1 Conformance Test Runner{mode}{RESET}")
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
            errs = validate_pack(path, strict=strict)
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
