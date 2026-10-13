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

It also creates the current version’s abstract page alongside its PDF.
It modifies nothing else in the main page. The fields it owns:
  * <meta name="..."> — citation_publication_date, citation_online_date,
    citation_technical_report_number, citation_doi, DC.date, DC.identifier,
    DC.rights, citation_pdf_url and citation_abstract
  * <span data-kp="..."> anchors in the body — version, date, license,
    concept-doi, version-doi, year, ym
  * Abstract paragraph and specification PDF link
"""
from __future__ import annotations

import argparse
from html import escape
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
        "_pdf_url": f"https://tymofiy.github.io/kp/kp-v{version}.pdf",
        "_edition_url": f"https://tymofiy.github.io/kp/kp-v{version}.html",
        "_abstract": " ".join(str(data.get("abstract") or "").split()),
        "_title": str(data["title"]),
        "_author": str(data["authors"][0]["given-names"]) + " " + str(data["authors"][0]["family-names"]),
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
    html = meta("citation_pdf_url", f["_pdf_url"], html)
    html = meta("citation_abstract", escape(f["_abstract"], quote=True), html)
    abstract_pattern = re.compile(r'(data-kp="abstract">)([^<]*)(</p>)')
    if not abstract_pattern.search(html):
        fail("data-kp abstract paragraph not found")
    abstract_value = escape(f["_abstract"], quote=False)
    if abstract_pattern.search(html).group(2) != abstract_value:
        changes.append("abstract paragraph")
    html = abstract_pattern.sub(lambda m: m.group(1) + abstract_value + m.group(3), html, count=1)
    for key in ("pdf", "edition"):
        link_pattern = re.compile(r'(data-kp-link="' + key + r'" href=")([^"]*)(")')
        if not link_pattern.search(html):
            fail(f"data-kp-link {key} not found")
        value = f[f"_{key}_url"]
        if link_pattern.search(html).group(2) != value:
            changes.append(f"{key} link")
        html = link_pattern.sub(lambda m: m.group(1) + value + m.group(3), html, count=1)
    html = meta("DC.date", f["date"], html)
    html = meta("DC.identifier", f["_concept_url"], html)
    html = meta("DC.rights", f["_license_spdx"], html)
    for key in ("version", "date", "license", "concept-doi", "version-doi", "year", "ym"):
        html = anchor(key, f[key], html)

    return html, changes


def release_page(f: dict) -> str:
    """A version-specific, freely readable abstract and same-directory PDF."""
    title, author, abstract = (escape(f[key]) for key in ("_title", "_author", "_abstract"))
    version, date, doi = (escape(f[key]) for key in ("version", "date", "version-doi"))
    url = f"https://tymofiy.github.io/kp/kp-{version}.html"
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — {version}</title>
<meta name="citation_title" content="{title}">
<meta name="citation_author" content="{author}">
<meta name="citation_publication_date" content="{f['_date_slash']}">
<meta name="citation_technical_report_number" content="{version}">
<meta name="citation_technical_report_institution" content="Independent">
<meta name="citation_doi" content="{doi}">
<meta name="citation_pdf_url" content="{f['_pdf_url']}">
<meta name="citation_public_url" content="{url}">
<meta name="citation_abstract" content="{abstract}">
<link rel="canonical" href="{url}">
<link rel="icon" href="kp.svg" type="image/svg+xml">
<style>
@font-face{{font-family:Inter;src:url(fonts/InterVariable.woff2) format("woff2");font-weight:300 700}}
body{{font-family:Inter,system-ui,sans-serif;margin:3rem auto;max-width:48rem;padding:0 1.25rem;color:#142a40;line-height:1.65;background:#fff}}
h1{{font-family:Georgia,serif;font-size:clamp(1.8rem,5vw,2.7rem);line-height:1.2;margin-bottom:1rem}}
h2{{font-size:1rem;margin-top:2rem}}a{{color:#35677d}}.edition{{color:#617184;font-size:.95rem}}
</style>
</head>
<body>
<main>
<h1>{title}</h1>
<p>{author} · <a href="https://orcid.org/0009-0007-5355-2764">ORCID</a></p>
<p class="edition">{version} · Released Editor's Draft · {date}</p>
<h2>Abstract</h2>
<p>{abstract}</p>
<p><a href="{f['_pdf_url']}">Read or download the full specification PDF</a></p>
<h2>Citation</h2>
<p>Kompanchenko, T. ({f['year']}). <i>{title}</i> (Version {version}). Zenodo.
<a href="https://doi.org/{doi}">https://doi.org/{doi}</a>.</p>
<p class="edition">A released editor's draft is public and citable. The specification remains a preview;
publication does not establish stable V1 compatibility or standards-body ratification.</p>
<p><a href="./">KP:1 specification website</a> ·
<a href="https://github.com/tymofiy/kp/tree/{version}">Source edition</a> ·
<a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></p>
</main>
</body>
</html>
'''


def main() -> int:
    ap = argparse.ArgumentParser(description="Sync docs/index.html metadata from CITATION.cff")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the page is out of sync (writes nothing)")
    args = ap.parse_args()

    f = load_fields()
    original = PAGE.read_text(encoding="utf-8")
    updated, changes = apply(original, f)
    edition = PAGE.parent / f"kp-{f['version']}.html"
    edition_html = release_page(f)
    edition_current = edition.exists() and edition.read_text(encoding="utf-8") == edition_html
    if not edition_current:
        changes.append(f"version-specific abstract page: {edition.name}")

    if args.check:
        if changes:
            sys.stderr.write("docs/index.html is OUT OF SYNC with CITATION.cff:\n")
            for c in changes:
                sys.stderr.write(f"  - {c}\n")
            sys.stderr.write("Run `make docs` and commit the result.\n")
            return 1
        print(f"In sync: version {f['version']}, released {f['date']}.")
        return 0

    if not edition_current:
        edition.write_text(edition_html, encoding="utf-8")
    if updated != original or not edition_current:
        PAGE.write_text(updated, encoding="utf-8")
        print(f"Updated docs/index.html ({len(changes)} field(s)):")
        for c in changes:
            print(f"  - {c}")
    else:
        print(f"docs/index.html already current (version {f['version']}, released {f['date']}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
