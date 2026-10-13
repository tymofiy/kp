#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Timothy Kompanchenko
"""Build a searchable PDF projection of the complete released specification.

Requires Pandoc, Typst, qpdf and the Inter / IBM Plex Mono fonts. The original
Markdown, schemas and grammar remain authoritative. No normative text is
rewritten. Usage: python3 scripts/build_pdf.py --work-dir /tmp/kp-pdf
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS = [
    'CORE', 'SPEC', 'COMPATIBILITY', 'AUTHORING', 'VOICE', 'COMPOSITION',
    'LIFECYCLE', 'MULTILINGUAL', 'ORGANIZATION', 'CONSISTENCY', 'CONVENTIONS',
    'STORAGE', 'BUNDLE', 'ARCHIVE', 'DEFINITIONS', 'EXTENSIONS', 'NOTES',
    'PLAYBACK', 'RECONCILIATION', 'RATIONALE', 'MAPPING', 'INDEPENDENCE',
    'README', 'CHANGELOG',
]
GRAMMARS = [
    'conformance/grammar/kp-claims.peg',
    'conformance/grammar/kp-pack.schema.json',
    'conformance/grammar/kp-composition.schema.json',
    'conformance/grammar/kp-signatures.schema.json',
]


def pandoc_ast(markdown: str) -> dict:
    result = subprocess.run(['pandoc', '--from=gfm', '--to=json'],
                            input=markdown, text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


def project(node, path: str, base: str):
    """Disambiguate PDF labels and resolve source links against the release tag."""
    if isinstance(node, dict):
        if node.get('t') == 'Header':
            node['c'][1][0] = path.replace('/', '-') + '-' + node['c'][1][0]
        if node.get('t') in ('Link', 'Image'):
            target = node['c'][-1][0]
            if not urlparse(target).scheme and not target.startswith('//'):
                node['c'][-1][0] = urljoin(base + path, target)
        for value in node.values():
            project(value, path, base)
    elif isinstance(node, list):
        for value in node:
            project(value, path, base)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-dir', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    cff = yaml.safe_load((ROOT / 'CITATION.cff').read_text())
    version = 'v' + str(cff['version'])
    released = str(cff['date-released'])
    title = cff['title']
    author = ' '.join([cff['authors'][0]['given-names'], cff['authors'][0]['family-names']])
    doi = next(i['value'] for i in cff['identifiers']
               if i['type'] == 'doi' and str(cff['version']) in i.get('description', ''))
    base = f'https://github.com/tymofiy/kp/blob/{version}/'
    source_paths = [f'spec/{name}.md' for name in DOCUMENTS]
    actual = {str(p.relative_to(ROOT)) for p in (ROOT / 'spec').glob('*.md')}
    if set(source_paths) != actual:
        raise SystemExit(f'Specification inventory changed: {set(source_paths) ^ actual}')
    work = args.work_dir or Path(tempfile.mkdtemp(prefix='kp-pdf-'))
    work.mkdir(parents=True, exist_ok=True)
    output = args.output or ROOT / 'docs' / f'kp-{version}.pdf'
    output.parent.mkdir(parents=True, exist_ok=True)
    hard_break = '  '
    front = f'''# {title}

**{author}**{hard_break}
ORCID: {cff['authors'][0]['orcid']}{hard_break}
**{version} · Released Editor's Draft · {released}**{hard_break}
Version DOI: https://doi.org/{doi}{hard_break}
Concept DOI: https://doi.org/10.5281/zenodo.19445262

## Abstract

{' '.join(cff['abstract'].split())}

## Reading this edition

This PDF is a reading projection of all {len(DOCUMENTS)} specification documents,
followed by the published PEG grammar and JSON Schemas. The released repository
and its original source files remain authoritative. CORE takes precedence over
overlapping legacy prose in SPEC; topic companions govern their declared
surfaces. Informative, experimental and deferred material retains its stated
status. Publication does not establish stable V1 compatibility, whole-format
implementation coverage or standards-body ratification.

The reference fixture/example suite contains 29 cases. Twenty-two reference
contract tests and 50 experimental graph compiler tests exercise bounded
behavior. These checks do not certify source truth, confidence calibration,
application workflows or archive cryptographic verification. See the
Capabilities and Compatibility chapter for the detailed boundaries.

Specification text: CC BY 4.0. Code, schemas and examples: Apache License 2.0.
The editor and acknowledgment of AI drafting assistance are recorded in
[ACKNOWLEDGMENTS.md]({base}ACKNOWLEDGMENTS.md).

Source edition: {base}spec/README.md
'''
    doc = pandoc_ast(front)
    doc['blocks'].append({'t': 'RawBlock', 'c': ['typst', '#pagebreak()\n#outline(title: "Contents", depth: 1)']})
    for path in source_paths:
        part = pandoc_ast((ROOT / path).read_text())
        project(part['blocks'], path, base)
        doc['blocks'].append({'t': 'RawBlock', 'c': ['typst', '#pagebreak()']})
        doc['blocks'].extend(part['blocks'])
    for path in GRAMMARS:
        doc['blocks'].append({'t': 'RawBlock', 'c': ['typst', '#pagebreak()']})
        doc['blocks'].extend(pandoc_ast(f'# {Path(path).name}\n\nSource: {base}{path}\n')['blocks'])
        doc['blocks'].append({'t': 'CodeBlock', 'c': [['', [], []], (ROOT / path).read_text()]})
    references = '# References and source documents\n\n'
    references += '\n'.join(f'- [{path}]({base}{path})' for path in source_paths + GRAMMARS)
    references += '\n\n- [Citation metadata](' + base + 'CITATION.cff)\n'
    references += '- [Version archive](https://doi.org/' + doi + ')\n'
    references += '- [Acknowledgments](' + base + 'ACKNOWLEDGMENTS.md)\n'
    doc['blocks'].append({'t': 'RawBlock', 'c': ['typst', '#pagebreak()']})
    doc['blocks'].extend(pandoc_ast(references)['blocks'])
    ast_path = work / 'specification.json'
    ast_path.write_text(json.dumps(doc, ensure_ascii=False))
    typst = subprocess.run(['pandoc', '--from=json', '--to=typst', str(ast_path)],
                           text=True, capture_output=True, check=True)
    template = (ROOT / 'scripts/pdf/layout.typ').read_text()
    metadata = f'#set document(title: {json.dumps(title, ensure_ascii=False)}, author: {json.dumps(author, ensure_ascii=False)}, date: datetime(year: {released[:4]}, month: {int(released[5:7])}, day: {int(released[8:])}))\n'
    source = work / 'specification.typ'
    source.write_text(metadata + template.replace('RELEASE_VERSION', version) + '\n' + typst.stdout)
    env = os.environ.copy()
    env['SOURCE_DATE_EPOCH'] = str(int(datetime.fromisoformat(released).replace(tzinfo=timezone.utc).timestamp()))
    uncompressed = work / 'uncompressed.pdf'
    subprocess.run(['typst', 'compile', str(source), str(uncompressed)], env=env, check=True)
    subprocess.run(['qpdf', '--object-streams=generate', '--compress-streams=y',
                    '--recompress-flate', '--compression-level=9', '--deterministic-id',
                    str(uncompressed), str(output)], check=True)
    inputs = source_paths + GRAMMARS + ['CITATION.cff', 'scripts/build_pdf.py', 'scripts/pdf/layout.typ']
    manifest = {
        'version': version, 'release_date': released, 'version_doi': doi,
        'projection': 'All spec/*.md files, normative grammar and published JSON Schemas; source files remain authoritative.',
        'sources': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in inputs},
        'tools': {name: subprocess.run([name, '--version'], text=True, capture_output=True, check=True).stdout.splitlines()[0] for name in ('pandoc', 'typst', 'qpdf')},
        'requested_font_families': ['Inter', 'IBM Plex Mono', 'DejaVu Sans Mono', 'Arial Unicode MS'],
        'pdf': output.name, 'pdf_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
    }
    output.with_suffix('.sources.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Built {output} ({output.stat().st_size:,} bytes); {len(source_paths)} specification documents and {len(GRAMMARS)} grammar/schema appendices.')


if __name__ == '__main__':
    main()
