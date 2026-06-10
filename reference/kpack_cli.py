#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Timothy Kompanchenko
"""kpack — reference CLI (one implemented subcommand; the rest are contract pointers).

The KP:1 specification (SPEC.md §13) describes a `kpack` command-line
tool. Two subcommands are implemented in this repository today:

    kpack lint <path/to/pack.kpack>     # validate a pack (delegates to
                                        # conformance/run.py --pack; same
                                        # output, same exit codes)
    kpack new <name>                    # scaffold a pack from the
                                        # hello-world starter and validate
                                        # it before reporting success

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
    kpack new <name> [--from hello-world]   # scaffold + validate a new pack
    kpack <subcommand>          # prints the spec section for that subcommand
    kpack                       # lists all known subcommands and their spec sections
    kpack --version             # prints the spec version this tool matches
"""

import argparse
import datetime
import re
import shutil
import subprocess
import sys
from pathlib import Path

VERSION = "v0.8.3-preview"

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
        "spec/CORE.md §2 Pack Structure",
        "Scaffold a new pack from the hello-world starter. IMPLEMENTED: "
        "`kpack new <name> [--from hello-world]` copies the starter, rewrites "
        "the pack identity (name, version, dates — SC-07/SC-08 kept "
        "consistent), and validates the result before reporting success.",
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
    print("                   kpack new <name>   (scaffold from the hello-world starter)")
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
    elif cmd == "new":
        print("  Run it:  kpack new <name> [--from hello-world]")
    else:
        print("  This command is not yet implemented in this repository. The")
        print("  contract above is the authority; an implementation is planned.")
    return 0


# Pack names follow the PackName grammar (kp-claims.peg):
# LOWER_ALNUM IDENT_CHAR* — i.e. [a-z0-9][a-z0-9-]*
PACK_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
TEMPLATES = {"hello-world": Path(__file__).resolve().parent.parent / "examples" / "hello-world.kpack"}
ISO_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
CALVER_RE = re.compile(r"\d{4}\.\d{2}\.\d{2}")
# Lines whose ISO dates are scaffold slots: dense claim metadata lines
# (indented `{...}` — including any trailing prose CORE permits on them)
# and evidence captured-fields (case-insensitive per AR-07: the list
# format spells it `Captured:`).
DATE_SLOT_LINE_RE = re.compile(r"^\s*\{|captured:", re.IGNORECASE)


def _rewrite_slot_dates(text: str, today_iso: str) -> str:
    """Rewrite ISO dates to today, but only on metadata/captured lines."""
    return "".join(
        ISO_DATE_RE.sub(today_iso, line) if DATE_SLOT_LINE_RE.search(line) else line
        for line in text.splitlines(keepends=True)
    )


def run_new(args: argparse.Namespace) -> int:
    """Scaffold a new pack: copy the starter, rewrite identity, validate."""
    name = args.name
    if not PACK_NAME_RE.match(name):
        print(
            f"kpack: invalid pack name '{name}' — names are lowercase "
            "alphanumeric plus hyphens, starting with a letter or digit "
            "([a-z0-9][a-z0-9-]*)",
            file=sys.stderr,
        )
        return 2

    template = TEMPLATES[args.template]
    if not template.is_dir():
        print(f"kpack: starter template not found at {template}", file=sys.stderr)
        print(
            "kpack new runs against the repository tree; install from a "
            "checkout with `pip install -e .` (or run ./reference/kpack).",
            file=sys.stderr,
        )
        return 2

    dest = Path.cwd() / f"{name}.kpack"
    if dest.exists():
        print(f"kpack: {dest} already exists — refusing to overwrite", file=sys.stderr)
        return 2

    today_iso = datetime.date.today().isoformat()        # 2026-06-10
    today_calver = today_iso.replace("-", ".")            # 2026.06.10
    title = " ".join(w.capitalize() for w in name.split("-"))

    shutil.copytree(template, dest)

    # PACK.yaml: identity + dates. SC-07/SC-08 require name and version to
    # match the claims.md frontmatter — both are rewritten in lockstep.
    pack_yaml = dest / "PACK.yaml"
    text = pack_yaml.read_text()
    text = text.replace("name: hello-world", f"name: {name}")
    text = CALVER_RE.sub(today_calver, text)
    text = text.replace(
        "description: The smallest idiomatic Knowledge Pack — copy this directory to start your own.",
        f"description: {title} — scaffolded from the hello-world starter; edit claims.md to begin.",
    )
    pack_yaml.write_text(text)

    # claims.md: frontmatter identity, title, dates. ISO dates are rewritten
    # only on metadata lines ({...} position 4) and evidence captured-lines —
    # never in prose — so a starter that one day mentions a date in running
    # text keeps it.
    claims = dest / "claims.md"
    text = claims.read_text()
    text = text.replace(
        "pack: hello-world | v: ", f"pack: {name} | v: "
    )
    text = CALVER_RE.sub(today_calver, text)
    text = text.replace("# Hello World [example]", f"# {title}")
    text = _rewrite_slot_dates(text, today_iso)
    claims.write_text(text)

    # evidence.md: title + captured dates.
    evidence = dest / "evidence.md"
    text = evidence.read_text()
    text = text.replace("# Evidence — Hello World", f"# Evidence — {title}")
    text = _rewrite_slot_dates(text, today_iso)
    evidence.write_text(text)

    # Drift detector: the rewrites above are anchored to the starter's
    # current text. If the starter evolves and an anchor stops matching,
    # the leftover identity shows up here — warn, don't fail (the scaffold
    # still validates; the user can finish the rename by hand). The text
    # is tested minus the identities placed on purpose — the description's
    # provenance mention and the user's own name/title — so a pristine
    # scaffold never warns, and real drift is caught even for names that
    # themselves contain "hello-world".
    intentional = "scaffolded from the hello-world starter"
    residue = []
    for f in (pack_yaml, claims, evidence):
        text = f.read_text().replace(intentional, "").replace(name, "").replace(title, "")
        if "hello-world" in text or "Hello World" in text:
            residue.append(f.name)
    if residue:
        print(
            f"kpack: warning — starter identity remains in {', '.join(residue)} "
            "(the starter's text has drifted from kpack new's rewrite anchors); "
            "finish the rename by hand and report this as a kpack-new bug",
            file=sys.stderr,
        )

    # Validate before claiming success — strict, so the scaffold is proven
    # against the PEG grammar, not just the permissive layer.
    if not RUN_PY.exists():
        print(f"kpack: conformance runner not found at {RUN_PY}", file=sys.stderr)
        return 2
    result = subprocess.call(
        [sys.executable, str(RUN_PY), "--pack", str(dest), "--strict", "--no-color"]
    )
    if result == 2:
        # run.py exit 2 is an environment/usage problem (e.g. parsimonious
        # missing for --strict), not an invalid scaffold.
        print(
            f"kpack: could not validate the scaffold (see error above). "
            f"It was created at {dest} — install the dependencies "
            "(pip install -r requirements.txt) and run "
            f"`kpack lint {dest.name} --strict` to verify it.",
            file=sys.stderr,
        )
        return 2
    if result != 0:
        print(
            f"kpack: scaffold failed validation — left in place at {dest} "
            "for inspection. This is a bug in `kpack new`; please report it.",
            file=sys.stderr,
        )
        return 1
    print(f"Next steps: edit {dest.name}/claims.md (your claims), evidence.md")
    print("(your sources), and PACK.yaml (domain, author, description).")
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

    new_p = sub.add_parser(
        "new",
        help="scaffold a new pack from the hello-world starter",
        description="Copy the hello-world starter to <name>.kpack in the "
        "current directory, rewrite the pack identity (name, version, "
        "dates), and validate the result (strict) before reporting success.",
    )
    new_p.add_argument("name", help="pack name ([a-z0-9][a-z0-9-]*)")
    new_p.add_argument(
        "--from",
        dest="template",
        choices=sorted(TEMPLATES),
        default="hello-world",
        help="starter template (default: hello-world)",
    )

    for cmd, (anchor, _) in COMMAND_REGISTRY.items():
        if cmd in ("lint", "new"):
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
    if args.cmd == "new":
        return run_new(args)
    return print_command_detail(args.cmd)


if __name__ == "__main__":
    sys.exit(main())
