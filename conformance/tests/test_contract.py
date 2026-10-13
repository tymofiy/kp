# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Timothy Kompanchenko
"""Ordinary authoring and round-trip regressions for the reference contract."""
import contextlib
import io
import itertools
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from conformance.evidence import MARKER, parse_evidence, transform_body
from conformance import run
from compiler.graph_compiler import parse_evidence as compiler_evidence
from compiler.graph_compiler import parse_claims as compiler_claims

ROOT = Path(__file__).resolve().parents[2]


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.pack = Path(self.temp.name) / 'draft.kpack'
        shutil.copytree(ROOT / 'conformance/fixtures/valid/minimal.kpack', self.pack)

    def categories(self, *, strict=True):
        return [e.cat for e in run.validate_pack(self.pack, strict=strict)]

    def test_two_generation_history_and_retraction(self):
        shutil.rmtree(self.pack)
        shutil.copytree(ROOT / 'conformance/fixtures/valid/lifecycle.kpack', self.pack)
        self.assertEqual(self.categories(), [])
        # Moving the original into history must not lose its evidence obligation.
        history = self.pack / 'history.md'
        history.write_text(history.read_text().replace('E001|', 'E099|'))
        self.assertIn('SC-03', self.categories())

    def test_history_namespace_and_cycle(self):
        claims = (self.pack / 'claims.md').read_text()
        entry = claims[claims.index('- [C001]'):]
        (self.pack / 'history.md').write_text('# History\n\n' + entry)
        self.assertIn('SC-02', self.categories())
        (self.pack / 'history.md').write_text('# History\n\n' + entry.replace('C001', 'C002') + '  ⊘C001\n')
        (self.pack / 'claims.md').write_text(claims + '  ⊘C002\n')
        self.assertIn('SC-04', self.categories())

    def test_final_claim_retraction(self):
        shutil.rmtree(self.pack)
        shutil.copytree(ROOT / 'conformance/fixtures/valid/retracted.kpack', self.pack)
        self.assertEqual(self.categories(), [])
        # Empty current state still requires the ordinary document structure.
        path = self.pack / 'claims.md'
        path.write_text(path.read_text().replace('## Claims', '# Claims'))
        self.assertIn('strict', self.categories())

    def test_literal_history_record_boundaries(self):
        claims = (self.pack / 'claims.md').read_text()
        entry = claims[claims.index('- [C001]'):].replace('C001', 'C002')
        history = self.pack / 'history.md'
        history.write_text('# History\n\n' + entry)
        self.assertEqual(self.categories(), [])
        history.write_text('# History\n\n' + entry.replace('\n  {', '\n\n  {'))
        self.assertIn('strict', self.categories())
        history.write_text('# History\n\n' + entry.rstrip('\n'))
        self.assertIn('strict', self.categories())
        # Separated editorial text is not an outgoing historical relation.
        history.write_text('# History\n\n' + entry + '\n  ⊘C999\n')
        self.assertEqual(self.categories(), [])

    def test_verbose_field_order_and_cardinality(self):
        path = self.pack / 'claims.md'
        original = path.read_text()
        start, end = original.index('{', original.index('- [C001]')), original.index('}', original.index('- [C001]')) + 1
        trailing, _, rest = original[end:].partition('\n')
        suffix = '\n' + ('  ' + trailing.strip() + '\n' if trailing.strip() else '') + rest
        fields = ['confidence: 0.90', 'type: reported', 'evidence: E001', 'since: 2026-04-04']
        for order in itertools.permutations(fields):
            path.write_text(original[:start] + '`' + ' | '.join(order) + '`' + suffix)
            self.assertEqual(self.categories(), [], order)
            compiled, relations, _ = compiler_claims('draft', path.read_text(), default_tier='client',
                                                     default_sensitivity='public', default_visibility='public',
                                                     default_boundary_explicit=False)
            self.assertEqual(len(compiled), 1)
            self.assertEqual(compiled[0].confidence, 0.90)
            self.assertEqual(compiled[0].since, '2026-04-04')
            self.assertEqual(compiled[0].claim_type, 'reported')
            self.assertEqual(relations, [])
        for altered in (fields[:-1], fields + [fields[0]], fields + ['identity: local-key']):
            path.write_text(original[:start] + '`' + ' | '.join(altered) + '`' + suffix)
            self.assertIn('parse', self.categories())

    def test_manifest_empty_is_diagnostic(self):
        (self.pack / 'PACK.yaml').write_text('')
        self.assertEqual(self.categories(), ['schema'])

    def test_required_evidence_metadata_both_forms(self):
        path = self.pack / 'evidence.md'
        path.write_text('# Evidence\n\n## E001\n- Type: unfamiliar_source\n- Captured: 2026-04-04\n- Source: Original note\n\nQuoted text.\n')
        self.assertEqual(self.categories(), [])
        for field in ('Type', 'Captured', 'Source'):
            text = path.read_text()
            path.write_text('\n'.join(line for line in text.split('\n') if not line.startswith('- ' + field + ':')))
            self.assertIn('evidence', self.categories())
            path.write_text(text)
        path.write_text(path.read_text().replace('2026-04-04', '2026-02-30'))
        self.assertIn('evidence', self.categories())

    def test_encoding_round_trip_line_endings_and_indentation(self):
        logical = ('## E001\r\n  ## Heading\r\n\t- [E42] excerpt\r\n'
                   '\\source escape\r\n  \\## retained escape\r\n' + MARKER + '\r\n'
                   '\\ordinary\r\n##not-a-heading\r\n- [E1]suffix\r\n\r\nlast')
        encoded = transform_body(logical)
        self.assertEqual(transform_body(encoded, decode=True), logical)
        self.assertIn('  \\## Heading', encoded)
        # A stray escape not emitted by this encoding remains unchanged.
        self.assertEqual(transform_body('\\ordinary\n', decode=True), '\\ordinary\n')

    def test_evidence_blockquote_optional_space(self):
        path = self.pack / 'evidence.md'
        original = path.read_text()
        for prefix in ('>', '> '):
            with self.subTest(prefix=prefix):
                text = original.replace('> ', prefix)
                path.write_text(text)
                self.assertEqual(self.categories(strict=False), [])
                self.assertEqual(self.categories(), [])
                compiled = compiler_evidence('draft', text, default_tier='client',
                                             default_sensitivity='public', default_visibility='public',
                                             default_boundary_explicit=False)
                self.assertEqual(compiled[0].source_uri, parse_evidence(original)[0].fields['source'])

    def test_unregistered_evidence_metadata_and_quoted_body(self):
        path = self.pack / 'evidence.md'
        for unknown in ('> **reliabilty:** A', '- Reliabilty: A'):
            with self.subTest(unknown=unknown):
                metadata = ('## E001\n- Type: note\n- Captured: 2026-04-04\n'
                            '- Source: Original note\n')
                path.write_text(metadata + unknown + '\n\nQuoted text.\n')
                for strict in (False, True):
                    errors = run.validate_pack(self.pack, strict=strict)
                    self.assertTrue(any(e.cat == 'evidence' and 'unregistered field reliabilty' in e.msg
                                        for e in errors), errors)
                # Field-shaped quotations after the separator are retained source text.
                path.write_text(metadata + '\n' + unknown + '\n')
                self.assertEqual(self.categories(), [])
                self.assertEqual(parse_evidence(path.read_text())[0].logical_body, unknown + '\n')

    def test_segmentation_then_decode_and_source_quote(self):
        logical = '## E099\n- [E099] source bullet\n> **source:** part of excerpt\n' + MARKER + '\n'
        encoded = transform_body(logical)
        text = ('# Evidence\n\n## E001 — Original\n> **type:** document | **captured:** 2026-04-04\n'
                '> **source:** Original source\n' + MARKER + '\n\n' + encoded +
                '## Appendix\nExcluded commentary.\n## E002\n- Type: note\n- Captured: 2026-04-04\n- Source: Another source\n\nSecond body.\n')
        records = parse_evidence(text)
        self.assertEqual([r.id for r in records], ['E001', 'E002'])
        self.assertEqual(records[0].logical_body, logical)
        self.assertEqual(records[0].fields['source'], 'Original source')
        compiled = compiler_evidence('example', text, default_tier='client', default_sensitivity='public',
                                     default_visibility='public', default_boundary_explicit=False)
        self.assertEqual([r.local_evidence_id for r in compiled], ['E001', 'E002'])
        self.assertEqual(compiled[1].source_uri, 'Another source')
        self.assertIn('## E099', compiled[0].summary)
        self.assertNotIn('Excluded commentary', compiled[0].summary)

    def test_unknown_encoding_preserves_body(self):
        text = '## E001\n> **kp-content-encoding:** future-v1\n\n\\## original\n'
        record = parse_evidence(text)[0]
        self.assertEqual(record.logical_body, record.encoded_body)
        self.assertTrue(record.warnings)

    def test_assessment_metadata_and_body(self):
        text = (ROOT / 'examples/kp-external-assessment.kpack/evidence.md').read_text()
        records = parse_evidence(text)
        expected = [
            'High-level synthesis and recommendations spanning novelty, grounding, contested bets, gaps, competitive landscape, and next moves. Imported into this pack as a sanitized, pack-native view.',
            'Theoretical grounding across epistemology, knowledge representation, uncertainty modeling, argumentation, preservation, and the philosophical knowledge/data question.',
            'Landscape scan of the 2024-2026 AI memory, context engineering, MCP, voice, and open-format ecosystem relevant to KP:1.',
            'Comparative study of Semantic Web standards, knowledge graphs, PKM tools, RAG formats, argumentation systems, preservation standards, ADRs, and context protocols.',
        ]
        self.assertEqual([r.fields['notes'] for r in records], expected)
        self.assertEqual([r.logical_body for r in records], ['', '', '', ''])

    def test_declared_composition_file(self):
        import yaml
        manifest = self.pack / 'PACK.yaml'
        pack = yaml.safe_load(manifest.read_text())
        manifest.write_text(yaml.safe_dump({**pack, 'composition': 'composition.yaml'}))
        self.assertIn('parse', self.categories())
        manifest.write_text(yaml.safe_dump({**pack, 'composition': 'another.yaml'}))
        self.assertEqual(self.categories(), ['schema'])

    def test_literal_reconciliation_example(self):
        import re
        text = (ROOT / 'spec/RECONCILIATION.md').read_text()
        fragment = re.findall(r'```text\n(.*?)```', text, re.S)[-1]
        claims = (self.pack / 'claims.md').read_text()
        (self.pack / 'claims.md').write_text(claims[:claims.index('- [C001]')] + fragment)
        evidence = (self.pack / 'evidence.md').read_text()
        (self.pack / 'evidence.md').write_text(evidence + '\n' + evidence[evidence.index('## E001'):].replace('E001', 'E002'))
        self.assertEqual(self.categories(), [])

    def test_composition_embedded_claim_syntax(self):
        minimal = self.pack / 'claims.md'
        text = minimal.read_text()
        claim = text[text.index('- [C001]'):]
        evidence = (self.pack / 'evidence.md').read_text()
        shutil.rmtree(self.pack)
        shutil.copytree(ROOT / 'conformance/fixtures/valid/composition.kpack', self.pack)
        self.assertEqual(self.categories(), [])
        path = self.pack / 'claims.md'
        narrative = path.read_text()
        (self.pack / 'evidence.md').write_text(evidence)
        path.write_text(narrative + '\n' + claim + '\nFurther composition narrative.\n')
        self.assertEqual(self.categories(), [])
        path.write_text(path.read_text().replace('} Single', '}Single'))
        self.assertEqual(self.categories(strict=False), [])
        self.assertIn('strict', self.categories())
        # The narrative exemption also leaves semantic obligations in place.
        path.write_text(narrative + '\n' + claim.replace('E001|', 'E099|'))
        self.assertIn('SC-03', self.categories())

    def test_literal_site_claim_excerpt(self):
        from html.parser import HTMLParser
        import re

        class ExcerptParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.collecting = False
                self.parts = []

            def handle_starttag(self, tag, attrs):
                if tag == 'pre' and ('class', 'specimen-code') in attrs:
                    self.collecting = True

            def handle_endtag(self, tag):
                if tag == 'pre':
                    self.collecting = False

            def handle_data(self, data):
                if self.collecting:
                    self.parts.append(data)

        parser = ExcerptParser()
        parser.feed((ROOT / 'docs/index.html').read_text())
        excerpt = ''.join(parser.parts).split('-->', 1)[1].lstrip()
        ids = re.findall(r'^- \[(C\d+)\]', excerpt, re.M)
        self.assertEqual(ids, ['C005', 'C024', 'C019'])
        # Exercise the displayed text with the actual example's full records.
        shutil.rmtree(self.pack)
        shutil.copytree(ROOT / 'examples/art-acquisition-decision.kpack', self.pack)
        path = self.pack / 'claims.md'
        claims = path.read_text()
        for cid in ids:
            claims = re.sub(r'^- \[' + cid + r'\].*?(?=\n\n|\Z)', '', claims,
                            count=1, flags=re.M | re.S)
        path.write_text(claims + '\n## Displayed Excerpt\n\n' + excerpt + '\n')
        self.assertEqual(self.categories(), [])

    def test_definition_policy_file_requirements(self):
        import yaml
        manifest = self.pack / 'PACK.yaml'
        pack = yaml.safe_load(manifest.read_text())
        (self.pack / 'claims.md').unlink()
        (self.pack / 'evidence.md').unlink()
        for kind, directory in (('definition', 'definitions'), ('policy', 'policies')):
            pack['kind'] = kind
            manifest.write_text(yaml.safe_dump(pack))
            self.assertIn('parse', self.categories())
            (self.pack / directory).mkdir()
            (self.pack / directory / 'example.yaml').write_text('name: example\n')
            # This validates the manifest/file matrix, not definition/policy schemas.
            self.assertEqual(self.categories(), [])

    def test_selection_scope_and_empty_result(self):
        import json
        import jsonschema
        import yaml
        selection = run._stringify_dates(yaml.safe_load((ROOT / 'conformance/fixtures/valid/selection.kpack/composition.yaml').read_text()))
        schema = json.loads((ROOT / 'conformance/grammar/kp-composition.schema.json').read_text())
        jsonschema.validate(selection, schema)
        for scope in (None, '', '   '):
            altered = {**selection, 'selection': {**selection['selection']}}
            if scope is None:
                altered['selection'].pop('scope')
            else:
                altered['selection']['scope'] = scope
            with self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate(altered, schema)
        # An explicitly scoped empty selection is a useful no-matches result.
        jsonschema.validate({**selection, 'members': []}, schema)

    def test_selection_member_reference_is_nonempty(self):
        import json
        import jsonschema
        import yaml
        selection = run._stringify_dates(yaml.safe_load((ROOT / 'conformance/fixtures/valid/selection.kpack/composition.yaml').read_text()))
        schema = json.loads((ROOT / 'conformance/grammar/kp-composition.schema.json').read_text())
        for reference in ('', '   ', '\t\n'):
            with self.subTest(reference=reference), self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate({**selection, 'members': [{'reference': reference}]}, schema)
        jsonschema.validate({**selection, 'members': [{'reference': 'member-pack'}]}, schema)

    def test_missing_declared_fixture_fails_suite(self):
        with patch.object(run, 'VALID_ORDER', ['absent.kpack']), patch.object(run, 'INVALID_ORDER', []), \
             patch.object(run, 'EXAMPLE_ORDER', []), patch('sys.argv', ['run.py']), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            with self.assertRaises(SystemExit) as result:
                run.main()
        self.assertEqual(result.exception.code, 1)
        self.assertIn('Result: 0/1 passed', output.getvalue())


class ArchiveHashTests(unittest.TestCase):
    def test_fixed_vectors(self):
        import json
        from conformance.archive_hash import content_hash
        vectors = json.loads((ROOT / 'conformance/fixtures/archive-hash-vectors.json').read_text())['vectors']
        hashes = {}
        for vector in vectors:
            with self.subTest(vector=vector['name']):
                actual_hash, actual_files = content_hash({p: bytes.fromhex(h) for p, h in vector['files_hex'].items()})
                self.assertEqual(actual_hash, vector['expected_pack_hash'])
                self.assertEqual(actual_files, vector['expected_files'])
                hashes[vector['name']] = actual_hash
        self.assertEqual(hashes['plain'], hashes['metadata'])
        self.assertEqual(hashes['unicode-nfd'], hashes['unicode-nfc'])
        self.assertNotEqual(hashes['plain'], hashes['ordinary-dotfiles'])
        self.assertNotEqual(hashes['plain'], hashes['line-endings'])


if __name__ == '__main__':
    unittest.main()
