#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Timothy Kompanchenko
"""Quick report on a Knowledge Pack. Needs Python 3 and nothing else.

    python3 kp_quick_check.py my-pack.kpack

Takes a pack folder or a .kpack zip. It only reads the pack and it reports.
It never changes, moves, refuses or deletes anything. A pack that is not yet
conforming still belongs to the person who made it, so deliver it with this
report attached.

Exit status: 0 conforming on these checks, 1 not yet conforming, 2 nothing to
read at that path. This is a quick check of the common cases. The full
validator is conformance/run.py.
"""

import pathlib
import re
import sys
import zipfile

REQUIRED_FIELDS = ("name", "version", "domain", "author")
KNOWN_FIELDS = {
    "author", "channels", "composition", "confidence", "conflicts", "consolidation",
    "dependencies", "description", "display", "domain", "evidence_basis", "extensions", "files",
    "freshness", "kind", "license", "lifecycle", "linguistic_epoch", "locales", "name", "notes",
    "ontology", "provenance", "sensitivity", "spec_uri", "spec_version", "style", "sub_packs",
    "tags", "tier", "version", "views", "visibility", "vocabulary",
}
PATTERNS = {
    "name": r"[a-z0-9][a-z0-9-]*",
    "version": r"\d{4}\.\d{2}\.\d{2}(-rev\d+)?",
    "domain": r"[a-z0-9][a-z0-9-]*(/[a-z0-9][a-z0-9-]*)*",
}
CLAIM_ID = re.compile(r"^- (?:\*\*)?\[(C\d+(?:-v\d+)?)\](?:\*\*)?(?: |$)", re.M)
DENSE = re.compile(r"\{([^{}|]*)\|([^{}|]*)\|([^{}|]*)\|([^{}|]*)(?:\|([^{}|]*))?(?:\|([^{}|]*))?\}")
RELATION = re.compile(r"(?:→|⊗!|⊗~|⊗|←|~|⊘|↔)(C\d+(?:-v\d+)?)(?![\w#-])")
EVIDENCE_HEADING = re.compile(r"^## (E\d+)(?:\s|$)", re.M)


def read_files(path):
    """Return {file name: text} from a pack folder or a zip."""
    if path.is_dir():
        return {
            p.relative_to(path).as_posix(): p.read_bytes().decode("utf-8", "replace")
            for p in path.rglob("*")
            if p.is_file()
        }
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            return {
                name: archive.read(name).decode("utf-8", "replace")
                for name in archive.namelist()
                if not name.endswith("/")
            }
    return None


def top_level_fields(text):
    """Read the scalar top-level keys of PACK.yaml, and whether it has a scale."""
    fields = {}
    for line in text.splitlines():
        match = re.match(r"([A-Za-z_][\w-]*):[ \t]*(.*)$", line)
        if match:
            value = match.group(2).split(" #")[0].strip()
            fields[match.group(1)] = value.strip("\"'")
    scale = re.search(r"^[ \t]+scale:[ \t]*([^\s#]+)", text, re.M)
    return fields, scale.group(1).strip("\"'") if scale else None


def claim_blocks(text):
    """Yield (claim id, line number, block text) for each claim bullet."""
    starts = list(CLAIM_ID.finditer(text))
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        yield match.group(1), text.count("\n", 0, match.start()) + 1, text[match.start():end]


def check_claim(claim, line, block, problems):
    """Check one dense claim. Verbose claims are read for their ID only."""
    match = DENSE.search(block)
    if not match:
        return (), not re.search(r"`(confidence|type):", block)
    confidence, kind, evidence, date, _, nature = match.groups()
    where = f"claims.md line {line}, {claim}"
    if not re.fullmatch(r"\d\.\d+", confidence) or float(confidence) > 1:
        problems.append(f"{where}: confidence '{confidence}' should be a decimal from 0.0 to 1.0")
    elif nature == "prediction" and float(confidence) > 0.95:
        problems.append(f"{where}: a prediction stays at 0.95 or below")
    if kind not in ("o", "r", "c", "i"):
        problems.append(f"{where}: type '{kind}' should be o, r, c or i")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        problems.append(f"{where}: date '{date}' should be YYYY-MM-DD")
    refs = [item.strip() for item in evidence.split(",")]
    for ref in refs:
        if not re.fullmatch(r"E\d+", ref):
            problems.append(f"{where}: evidence '{ref}' should look like E001")
    return refs, False


def check_evidence(evidence, problems):
    """Check IDs and required fields in evidence.md, and return the IDs."""
    ids = []
    matches = list(EVIDENCE_HEADING.finditer(evidence))
    for index, match in enumerate(matches):
        name = match.group(1)
        if name in ids:
            problems.append(f"evidence.md: {name} is used twice")
        ids.append(name)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(evidence)
        body = evidence[match.end():end].lower()
        for field in ("type", "captured", "source"):
            if f"**{field}:**" not in body and f"- {field}:" not in body:
                problems.append(f"evidence.md: {name} has no {field}")
    return ids


def check_pack(files):
    """Return (problems, notes) for one pack."""
    problems, notes = [], []
    if "PACK.yaml" not in files:
        return ["PACK.yaml is missing"], notes

    fields, scale = top_level_fields(files["PACK.yaml"])
    for field in REQUIRED_FIELDS:
        if not fields.get(field):
            problems.append(f"PACK.yaml: {field} is missing")
    for field, pattern in PATTERNS.items():
        value = fields.get(field)
        if value and not re.fullmatch(pattern, value):
            problems.append(f"PACK.yaml: {field} '{value}' has the wrong form")
    for field in sorted(set(fields) - KNOWN_FIELDS):
        problems.append(f"PACK.yaml: readers will not interpret the field '{field}'")

    claims = files.get("claims.md")
    if claims is None:
        if fields.get("kind") in (None, "claim", "mixed"):
            problems.append("claims.md is missing")
        return problems, notes
    if "composition.yaml" in files:
        notes.append("This is a composition pack. Its narrative was not checked here.")
        return problems, notes

    if not re.match(r"<!-- KP:\d+ ", claims):
        problems.append("claims.md: the opening comment is missing, or it is not at the very top")
    elif not claims.startswith("<!-- KP:1 "):
        problems.append("claims.md: the opening comment should name KP:1")
    front = re.search(r"^pack: (\S+) \| v: (\S+) \| domain: (\S+)[ \t]*$", claims, re.M)
    conf = re.search(r"^confidence: (\S+) \| normalized[ \t]*$", claims, re.M)
    if not front or not conf:
        problems.append("claims.md: the --- header block does not have the expected two lines")
    else:
        for field, value in zip(("name", "version", "domain"), front.groups()):
            if fields.get(field) and fields[field] != value:
                problems.append(f"claims.md header says {value}, PACK.yaml {field} says {fields[field]}")
        if scale and scale != conf.group(1):
            problems.append(f"claims.md header says scale {conf.group(1)}, PACK.yaml says {scale}")

    heading = re.search(r"^# .*\[(.*)\][ \t]*$", claims, re.M)
    if heading and not re.fullmatch(r"[a-z0-9-]+(\|[A-Za-z0-9_-]+(,[A-Za-z0-9_-]+)*)?", heading.group(1)):
        problems.append(f"claims.md: the title's bracket label '{heading.group(1)}' should be one lowercase word")

    evidence = files.get("evidence.md", "")
    if "evidence.md" not in files:
        notes.append("evidence.md is missing, so cited sources could not be checked.")
    evidence_ids = check_evidence(evidence, problems)

    history = files.get("history.md", "")
    known = {claim for claim, _, _ in claim_blocks(history)}
    seen = []
    cited = set()
    verbose = False
    for claim, line, block in claim_blocks(claims):
        if claim in seen or claim in known:
            problems.append(f"claims.md line {line}: {claim} is used twice")
        seen.append(claim)
        refs, missing = check_claim(claim, line, block, problems)
        cited.update(refs)
        if missing:
            problems.append(f"claims.md line {line}, {claim}: there is no {{...}} line under this claim")
        verbose = verbose or not DENSE.search(block)
    if verbose:
        notes.append("Some claims use the verbose form. Only their IDs were checked here.")

    all_claims = set(seen) | known
    for claim, line, block in claim_blocks(claims):
        for target in RELATION.findall(block):
            if target not in all_claims:
                problems.append(f"claims.md line {line}, {claim}: relation points to {target}, which is not in the pack")
    if "evidence.md" in files:
        for ref in sorted(cited - set(evidence_ids)):
            if re.fullmatch(r"E\d+", ref):
                problems.append(f"evidence.md has no entry for {ref}, which a claim cites")
    notes.insert(0, f"Read {len(seen)} claims and {len(evidence_ids)} evidence entries.")
    return problems, notes


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 kp_quick_check.py <pack folder or .kpack file>")
        return 2
    path = pathlib.Path(sys.argv[1])
    files = read_files(path) if path.exists() else None
    if files is None:
        print(f"Nothing to read at {path}. It is not a folder or a zip file.")
        return 2

    problems, notes = check_pack(files)
    for note in notes:
        print(note)
    if not problems:
        print("Result: conforming on these quick checks.")
        return 0
    print(f"Result: not yet conforming. {len(problems)} thing(s) to look at:")
    for problem in problems:
        print(f"  - {problem}")
    print("Deliver the pack anyway, with this report. It is the person's pack.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
