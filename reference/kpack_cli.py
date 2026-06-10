#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Timothy Kompanchenko
"""kpack — reference CLI (one implemented subcommand; the rest are contract pointers).

The KP:1 specification (SPEC.md §13) describes a `kpack` command-line
tool. One subcommand is implemented in this repository today:

    kpack lint <path/to/pack.kpack>     # validate a pack (delegates to
                                        # conformance/run.py --pack; same
                                        # output, same exit codes)

Every other `kpack <subcommand>` is a contract to be implemented: running
it prints a pointer to the spec section that defines that command's
contract, so a fresh agent or human reader gets the authority instead of
`command not found` and a guessing game.

Argument handling is argparse end-to-end: unknown subcommands and unknown
flags fail loudly with exit code 2 — nothing is silently ignored.

This module is the implementation behind two equivalent invocations:
    ./reference/kpack ...      # thin launcher script, works from a checkout
    kpack ...                  # console script after `pip install -e .`

Usage:
    kpack lint <pack> [--strict] [--json] [--no-color]   # validate a pack
    kpack <subcommand>          # prints the spec section for that subcommand
    kpack                       # lists all known subcommands and their spec sections
    kpack --version             # prints the spec version this tool matches
"""

import argparse
import subprocess
import sys
from pathlib import Path

VERSION = "v0.8.2-preview"

# The conformance runner lives in the repository tree, not in an installed
# wheel — resolve it relative to this file (reference/ -> repo root). For a
# site-packages install this path will not exist; `kpack lint` then refuses
# loudly and names the supported layout (a checkout / editable install).
RUN_PY = Path(__file__).resolve().parent.parent / "conformance" / "run.py"

COMMAND_REGISTRY = {
    "lint": (
        "spec/SPEC.md §13 Tooling",
        "Validate a pack's structure, references, and semantic constraints. "
        "IMPLEMENTED: `kpack lint <path>` delegates to "
        "`conformance/run.py --pack` (same output, same exit codes).",
    ),
    "test": (
        "spec/SPEC.md §10 validation.yaml — Test Questions",
        "Run validation.yaml test questions against an LLM. The schema for "
        "validation.yaml lives in §10; the runner is planned.",
    ),
    "export": (
        "spec/BUNDLE.md",
        "Export a pack as a single bundled markdown artifact for sharing "
        "with humans, AI chat windows, or systems that cannot read directories. "
        "Defined in BUNDLE.md.",
    ),
    "render": (
        "spec/SPEC.md §16 Views — Pre-Rendered Display Content",
        "Generate or regenerate views (display and voice) from claims.md. "
        "Per Principle 17 (RATIONALE.md §1), the AI renders pre-built views "
        "rather than composing on the fly.",
    ),
    "translate": (
        "spec/MULTILINGUAL.md §7 Translation Workflow",
        "Translate views (NOT claims.md) into a target locale. Claims remain "
        "American English per MULTILINGUAL.md §2 P1.",
    ),
    "bundle": (
        "spec/BUNDLE.md",
        "Bundle a pack as a markdown artifact. Same surface as `export` "
        "with intent-disambiguating flags. Defined in BUNDLE.md.",
    ),
    "archive": (
        "spec/ARCHIVE.md",
        "Seal a pack as a `.kpack` archive (ZIP container with content hash "
        "and signatures.yaml). Sealed archives participate in the integrity "
        "chain. Defined in ARCHIVE.md.",
    ),
    "new": (
        "spec/CORE.md §2 Pack Structure (planned scaffold)",
        "Scaffold a new pack from a template. Templates are not specified in "
        "v0.8.2-preview; see ORGANIZATION.md for repository layout patterns.",
    ),
    "reconcile": (
        "spec/RECONCILIATION.md (stub — design deferred to v0.9 / v1.0)",
        "Cross-pack reconciliation: surface drift, orphan claims, and "
        "supersession recommendations across packs. The full design is "
        "deferred per RECONCILIATION.md.",
    ),
    "compose": (
        "spec/COMPOSITION.md",
        "Build a composite pack (meeting, briefing, presentation) that "
        "references standing packs. Defined in COMPOSITION.md.",
    ),
    "patrol": (
        "spec/CONSISTENCY.md",
        "Cross-pack consistency patrol: claim contradiction detection, "
        "real-time alerting, confidence decay. Defined in CONSISTENCY.md.",
    ),
    "promote": (
        "spec/LIFECYCLE.md §4 Consolidation & Reconciliation",
        "Promote a claim from an ephemeral pack to a standing pack. "
        "Part of the reconcile-before-archive flow per Principle 21 "
        "(RATIONALE.md §1).",
    ),
    "restore": (
        "spec/LIFECYCLE.md §3 Archival",
        "Restore a pack from the archive directory back to active. "
        "Defined in LIFECYCLE.md.",
    ),
    "play": (
        "spec/PLAYBACK.md (experimental)",
        "Drive a self-driving voice presentation of a pack via a "
        "PlaybackPlan. Defined in PLAYBACK.md.",
    ),
    "seal": (
        "spec/ARCHIVE.md §4.1 Sealing",
        "Seal a pack directory into a `.kpack` ZIP archive with a "
        "`signatures.yaml` integrity record. Defined in ARCHIVE.md.",
    ),
    "verify": (
        "spec/ARCHIVE.md §6.2 Verify",
        "Verify a `.kpack` archive's integrity (content hash, signature, "
        "ZIP safety). Optionally verify a version chain across multiple "
        "sealed archives (`--chain v1 v2 v3`).",
    ),
    "extract": (
        "spec/ARCHIVE.md §6.3 Extract",
        "Extract a sealed `.kpack` archive into a directory. Inverse of "
        "`seal`. Validates archive integrity before extraction.",
    ),
    "info": (
        "spec/ARCHIVE.md §7 CLI Commands (info)",
        "Display archive metadata (signatures, content hash, contained "
        "files) without extracting. Defined in ARCHIVE.md.",
    ),
    "unbundle": (
        "spec/BUNDLE.md",
        "Reconstruct a pack directory from a markdown bundle (the inverse "
        "of `bundle` / `export`). Defined in BUNDLE.md.",
    ),
}


def print_banner() -> None:
    print(f"kpack — KP:1 reference CLI ({VERSION})")
    print()
    print("Implemented today: kpack lint <pack>  (delegates to conformance/run.py)")
    print("Every other subcommand is a contract pointer to its spec section.")
    print()


def print_command_list() -> None:
    print("Subcommands and the spec sections that define them:")
    print()
    width = max(len(c) for c in COMMAND_REGISTRY) + 2
    for cmd, (anchor, _) in COMMAND_REGISTRY.items():
        print(f"  {cmd:<{width}} → {anchor}")
    print()
    print("Run  kpack <subcommand>  for a one-paragraph summary.")


def print_command_detail(cmd: str) -> int:
    anchor, summary = COMMAND_REGISTRY[cmd]
    print(f"kpack {cmd}")
    print(f"  Spec contract: {anchor}")
    print()
    print(f"  {summary}")
    print()
    if cmd == "lint":
        print("  Run it:  kpack lint <path/to/pack.kpack> [--strict] [--json] [--no-color]")
    else:
        print("  This command is not yet implemented in this repository. The")
        print("  contract above is the authority; an implementation is planned.")
    return 0


def run_lint(args: argparse.Namespace) -> int:
    """Validate a pack by delegating to conformance/run.py --pack."""
    if not RUN_PY.exists():
        print(f"kpack: conformance runner not found at {RUN_PY}", file=sys.stderr)
        print(
            "kpack lint runs against the repository tree; install from a "
            "checkout with `pip install -e .` (or run ./reference/kpack).",
            file=sys.stderr,
        )
        return 2
    cmd = [sys.executable, str(RUN_PY), "--pack", args.pack]
    if args.strict:
        cmd.append("--strict")
    if args.json:
        cmd.append("--json")
    if args.no_color:
        cmd.append("--no-color")
    return subprocess.call(cmd)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kpack",
        description="KP:1 reference CLI — `lint` is implemented; every other "
        "subcommand prints the spec section that defines its contract.",
    )
    parser.add_argument("-v", "--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="cmd", metavar="subcommand")

    lint_p = sub.add_parser(
        "lint",
        help="validate a pack (delegates to conformance/run.py --pack)",
        description="Validate a .kpack directory. Output and exit codes are "
        "those of conformance/run.py (0 pass / 1 fail / 2 usage).",
    )
    lint_p.add_argument("pack", help="path to a .kpack directory")
    lint_p.add_argument(
        "--strict",
        action="store_true",
        help="also parse claims.md through the normative PEG grammar",
    )
    lint_p.add_argument(
        "--json", action="store_true", help="machine-readable result object"
    )
    lint_p.add_argument(
        "--no-color", action="store_true", help="disable ANSI color"
    )

    for cmd, (anchor, _) in COMMAND_REGISTRY.items():
        if cmd == "lint":
            continue
        sub.add_parser(
            cmd,
            help=f"contract pointer → {anchor}",
            description=f"Not yet implemented. Spec contract: {anchor}",
        )
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print_banner()
        print_command_list()
        return 0
    args = build_parser().parse_args(argv)  # unknown flags/subcommands: loud exit 2
    if args.cmd == "lint":
        return run_lint(args)
    return print_command_detail(args.cmd)


if __name__ == "__main__":
    sys.exit(main())
