#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Timothy Kompanchenko
"""Project release metadata from CITATION.cff into docs/index.html.

The spec home page (docs/index.html) shows the current version, release date,
licence, and DOIs. Those are release-cadence values: hand-editing them means
the page is wrong the moment a new version is cut. This script makes
CITATION.cff the single source of truth and writes those values into the page,
so they cannot drift.

Usage:
    python3 scripts/build_docs.py           # inject values into docs/index.html
    python3 scripts/build_docs.py --check    # exit 1 if the page is out of sync
    make docs / make docs-check              # the same, via the Makefile

It modifies nothing else in the page. The fields it owns:
  * <meta name="..."> — citation_publication_date, citation_online_date,
    citation_technical_report_number, citation_doi, DC.date, DC.identifier,
    DC.rights
  * <span data-kp="..."> anchors in the body — version, date, license,
    concept-doi, version-doi, year, ym
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CFF = ROOT / "CITATION.cff"
PAGE = ROOT / "docs" / "index.html"


def fail(msg: str):
    sys.stderr.write(f"build_docs: error: {msg}\n")
    raise SystemExit(2)


def load_fields() -> dict:
    """Read the canonical release metadata out of CITATION.cff."""
    data = yaml.safe_load(CFF.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail("CITATION.cff did not parse as a mapping")

    version = str(data.get("version") or "").strip()
    released = str(data.get("date-released") or "").strip()
    license_id = str(data.get("license") or "").strip()
    if not (version and released and license_id):
        fail("CITATION.cff is missing version, date-released, or license")

    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", released)
    if not m:
        fail(f"date-released is not YYYY-MM-DD: {released!r}")
    year, month, day = m.groups()

    dois = [i for i in (data.get("identifiers") or []) if i.get("type") == "doi"]
    # The concept (evergreen) DOI describes itself as spanning all versions; the
    # per-version DOIs only mention "concept" to point back at it. Match the
    # evergreen wording, not the bare word "concept", so detection is unambiguous.
    concept_hits = [i["value"] for i in dois
                    if any(k in str(i.get("description", "")).lower()
                           for k in ("evergreen", "across all versions", "always resolves"))]
    version_hits = [i["value"] for i in dois if version in str(i.get("description", ""))]
    if len(concept_hits) != 1:
        fail("expected exactly one concept (evergreen) DOI: an identifier whose description says "
             f"'evergreen' / 'across all versions' / 'always resolves'; found {len(concept_hits)}")
    if len(version_hits) != 1:
        fail(f"expected exactly one DOI whose description names {version!r}; found {len(version_hits)}")
    concept = concept_hits[0]
    version_doi = version_hits[0]

    return {
        # body data-kp anchors
        "version": f"v{version}",
        "date": released,
        "license": license_id.replace("-", " "),  # display form: CC-BY-4.0 -> CC BY 4.0
        "_license_spdx": license_id,               # SPDX form for machine metadata (DC.rights)
        "concept-doi": concept,
        "version-doi": version_doi,
        "year": year,
        "ym": f"{year}-{month}",
        # head <meta> values
        "_date_slash": f"{year}/{month}/{day}",
        "_concept_url": f"https://doi.org/{concept}",
    }


def apply(html: str, f: dict):
    """Return (new_html, list_of_changes)."""
    changes: list[str] = []

    def meta(name: str, value: str, html: str) -> str:
        # Tolerate attribute order/spacing so an IDE reformat of <head> can't
        # silently skip a field (a true miss still fails loudly via search()).
        pat = re.compile(r'(<meta(?=[^>]*\bname="' + re.escape(name) + r'")[^>]*?\bcontent=")([^"]*)(")')
        mt = pat.search(html)
        if not mt:
            fail(f"meta tag not found: {name}")
        if mt.group(2) != value:
            changes.append(f"meta {name}: {mt.group(2)!r} -> {value!r}")
        return pat.sub(lambda m: m.group(1) + value + m.group(3), html, count=1)

    def anchor(key: str, value: str, html: str) -> str:
        pat = re.compile(r'(<span data-kp="' + re.escape(key) + r'"[^>]*>)([^<]*)(</span>)')
        if not pat.search(html):
            fail(f"data-kp anchor not found: {key}")

        def repl(m):
            if m.group(2) != value:
                changes.append(f"data-kp {key}: {m.group(2)!r} -> {value!r}")
            return m.group(1) + value + m.group(3)

        return pat.sub(repl, html)

    html = meta("citation_publication_date", f["_date_slash"], html)
    html = meta("citation_online_date", f["_date_slash"], html)
    html = meta("citation_technical_report_number", f["version"], html)
    html = meta("citation_doi", f["version-doi"], html)
    html = meta("DC.date", f["date"], html)
    html = meta("DC.identifier", f["_concept_url"], html)
    html = meta("DC.rights", f["_license_spdx"], html)
    for key in ("version", "date", "license", "concept-doi", "version-doi", "year", "ym"):
        html = anchor(key, f[key], html)

    return html, changes


def main() -> int:
    ap = argparse.ArgumentParser(description="Sync docs/index.html metadata from CITATION.cff")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the page is out of sync (writes nothing)")
    args = ap.parse_args()

    f = load_fields()
    original = PAGE.read_text(encoding="utf-8")
    updated, changes = apply(original, f)

    if args.check:
        if changes:
            sys.stderr.write("docs/index.html is OUT OF SYNC with CITATION.cff:\n")
            for c in changes:
                sys.stderr.write(f"  - {c}\n")
            sys.stderr.write("Run `make docs` and commit the result.\n")
            return 1
        print(f"In sync: version {f['version']}, released {f['date']}.")
        return 0

    if updated != original:
        PAGE.write_text(updated, encoding="utf-8")
        print(f"Updated docs/index.html ({len(changes)} field(s)):")
        for c in changes:
            print(f"  - {c}")
    else:
        print(f"docs/index.html already current (version {f['version']}, released {f['date']}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
