import sqlite3
import tempfile
import unittest
from pathlib import Path

from compiler.graph_compiler import compile_bundle, render_dossier, retrieve_packet


ROSETTA = """<!-- KP:1 — Knowledge Pack Format
Claims: - [ID] assertion {confidence|type|evidence|date|depth|nature} context
  Positions 5-6 optional. Verbose named-field syntax also accepted.
Types: o=observed r=reported c=computed i=inferred
Depth: assumed | investigated | exhaustive (optional, position 5)
Nature: judgment | prediction | meta (optional, position 6; omitted=factual)
Relations: →supports ⊗contradicts ⊗!error ⊗~tension ←requires ~refines ⊘supersedes ↔see_also
Files: evidence.md=sources history.md=past entities.md=graph
-->"""


class GraphCompilerTests(unittest.TestCase):
    def write_fixture(self, root: Path) -> Path:
        pack = root / "example-supersession.kpack"
        pack.mkdir()
        (pack / "PACK.yaml").write_text(
            """name: example-supersession
version: 2026.06.18
domain: test/compiler
kind: claim
author: KP Compiler Tests

description: Synthetic compiler fixture.

confidence:
  scale: simple
  normalize: true

freshness: "2026-06-18"
license: CC-BY-4.0
sensitivity: public
visibility: public
tier: standalone

provenance:
  author: KP Compiler Tests
  role: independent
  reviewed_by: null
  review_date: null
  signed: false
"""
        )
        (pack / "claims.md").write_text(
            f"""{ROSETTA}
---
pack: example-supersession | v: 2026.06.18 | domain: test/compiler
confidence: simple | normalized
---

# Example Supersession Fixture

## Claims

- [C001] The prior reading was Example A.
  {{0.70|r|E001|2026-06-18|investigated}} Preserved as prior belief.

- [C002] The current reading is Example B.
  {{0.86|i|E002|2026-06-18|investigated|judgment}} Supersedes the prior reading. ⊘C001, ←C003

- [C003] The source behind Example A is unreliable.
  {{0.88|i|E002|2026-06-18|investigated|judgment}} Explains why Example A changed. ⊗!C001
"""
        )
        (pack / "evidence.md").write_text(
            """# Evidence

## E001 — Prior Note
> **type:** synthetic_document | **captured:** 2026-06-18
> **source:** fixture://prior-note.txt

Synthetic prior note.

## E002 — Review Note
> **type:** synthetic_report | **captured:** 2026-06-18
> **source:** fixture://review-note.txt

Synthetic review note.
"""
        )
        return pack

    def write_cross_pack_fixtures(self, root: Path) -> tuple[Path, Path]:
        pack_a = root / "example-a.kpack"
        pack_b = root / "example-b.kpack"
        pack_a.mkdir()
        pack_b.mkdir()

        for pack, name in [(pack_a, "example-a"), (pack_b, "example-b")]:
            (pack / "PACK.yaml").write_text(
                f"""name: {name}
version: 2026.06.18
domain: test/compiler
kind: claim
author: KP Compiler Tests

description: Synthetic cross-pack compiler fixture.

confidence:
  scale: simple
  normalize: true

freshness: "2026-06-18"
license: CC-BY-4.0
sensitivity: public
visibility: public
tier: standalone

provenance:
  author: KP Compiler Tests
  role: independent
  reviewed_by: null
  review_date: null
  signed: false
"""
            )

        (pack_a / "claims.md").write_text(
            f"""{ROSETTA}
---
pack: example-a | v: 2026.06.18 | domain: test/compiler
confidence: simple | normalized
---

# Example A

## Claims

- [C001] Example A should be read with Example B.
  {{0.76|i|E001|2026-06-18|investigated|judgment}} Cross-pack context is required. ↔example-b#C001
"""
        )
        (pack_a / "evidence.md").write_text(
            """# Evidence

## E001 — A Note
> **type:** synthetic_document | **captured:** 2026-06-18
> **source:** fixture://a-note.txt

Synthetic A note.
"""
        )
        (pack_b / "claims.md").write_text(
            f"""{ROSETTA}
---
pack: example-b | v: 2026.06.18 | domain: test/compiler
confidence: simple | normalized
---

# Example B

## Claims

- [C001] Example B provides cross-pack context.
  {{0.80|r|E001|2026-06-18|investigated}} Related contextual claim.
"""
        )
        (pack_b / "evidence.md").write_text(
            """# Evidence

## E001 — B Note
> **type:** synthetic_document | **captured:** 2026-06-18
> **source:** fixture://b-note.txt

Synthetic B note.
"""
        )
        return pack_a, pack_b

    def write_tier_fixture(self, root: Path) -> Path:
        pack = root / "example-tiered.kpack"
        pack.mkdir()
        (pack / "PACK.yaml").write_text(
            """name: example-tiered
version: 2026.06.18
domain: test/compiler
kind: claim
author: KP Compiler Tests

description: Synthetic tier-slicing compiler fixture.

confidence:
  scale: simple
  normalize: true

freshness: "2026-06-18"
license: CC-BY-4.0
sensitivity: public
visibility: public
tier: standalone

provenance:
  author: KP Compiler Tests
  role: independent
  reviewed_by: null
  review_date: null
  signed: false
"""
        )
        (pack / "claims.md").write_text(
            f"""{ROSETTA}
---
pack: example-tiered | v: 2026.06.18 | domain: test/compiler
confidence: simple | normalized
---

# Example Tiered Fixture

## Claims

- [C001] The client-safe conclusion can be shown.
  {{0.80|i|E001|2026-06-18|investigated|judgment}} Public rationale. ↔C002

- [C002] The server-only method explains the conclusion.
  {{0.90|i|E002|2026-06-18|investigated|meta}} Server method. <!-- kp-compiler: tier=server sensitivity=internal visibility=private -->

- [C003] This claim looks public but depends on server-only evidence.
  {{0.70|i|E002|2026-06-18|investigated|judgment}} Must not survive client slicing.

- [C004] The internal operator note is not server-shippable.
  {{0.95|i|E003|2026-06-18|investigated|meta}} Operator-only note. <!-- kp-compiler: tier=internal sensitivity=restricted visibility=private -->
"""
        )
        (pack / "evidence.md").write_text(
            """# Evidence

## E001 — Public Note
> **type:** synthetic_document | **captured:** 2026-06-18
> **source:** fixture://public-note.txt

Synthetic public note.

## E002 — Server Method
> **type:** synthetic_report | **captured:** 2026-06-18 | **tier:** server | **sensitivity:** internal | **visibility:** private
> **source:** fixture://server-method.txt

Synthetic server-only method.

## E003 — Internal Note
> **type:** synthetic_report | **captured:** 2026-06-18 | **tier:** internal | **sensitivity:** restricted | **visibility:** private
> **source:** fixture://internal-note.txt

Synthetic internal-only note.
"""
        )
        return pack

    def test_compile_bundle_retrieves_supersession_neighborhood(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = self.write_fixture(root)
            out = root / "out"

            summary = compile_bundle(
                pack,
                out,
                query_claims=["C002"],
                questions={"C002": "What is the current reading?"},
            )

            self.assertEqual(summary["claims"], 3)
            self.assertEqual(summary["evidence"], 2)
            self.assertEqual(summary["evidence_links"], 3)
            self.assertEqual(summary["relations"], 3)
            self.assertEqual(summary["unresolved_relations"], 0)

            db_path = out / "indices" / "claim-graph.sqlite"
            conn = sqlite3.connect(db_path)
            try:
                self.assertEqual(
                    conn.execute("SELECT value FROM graph_meta WHERE key = 'schema_version'").fetchone()[0],
                    "1",
                )
                self.assertEqual(
                    conn.execute("SELECT count(*) FROM kp_claim_evidence_links").fetchone()[0],
                    3,
                )
            finally:
                conn.close()

            packet = retrieve_packet(db_path, "C002")
            neighbors = {neighbor["local_claim_id"] for neighbor in packet["neighbors"]}
            self.assertTrue({"C001", "C003"}.issubset(neighbors))

            dossier = render_dossier(packet, "What is the current reading?")
            self.assertIn("current best reading", dossier.lower())
            self.assertIn("superseded", dossier.lower())
            self.assertIn("not equally live", dossier.lower())

            self.assertTrue((out / "adapters/openai-compatible/request-C002.json").exists())
            self.assertTrue((out / "adapters/ollama/prompt-C002.txt").exists())
            self.assertTrue((out / "adapters/mcp/tool-response-C002.json").exists())

    def test_compile_bundle_resolves_cross_pack_relation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack_a, pack_b = self.write_cross_pack_fixtures(root)
            out = root / "out"

            summary = compile_bundle(
                [pack_a, pack_b],
                out,
                query_claims=["example-a#C001"],
                questions={"example-a#C001": "What context is required?"},
            )

            self.assertEqual(summary["packs"], 2)
            self.assertEqual(summary["claims"], 2)
            self.assertEqual(summary["relations"], 1)
            self.assertEqual(summary["unresolved_relations"], 0)

            db_path = out / "indices" / "claim-graph.sqlite"
            conn = sqlite3.connect(db_path)
            try:
                relation = conn.execute(
                    """
                    SELECT to_claim_uid, target_resolved
                    FROM kp_claim_relations
                    WHERE from_claim_uid = 'example-a#C001'
                    """
                ).fetchone()
            finally:
                conn.close()

            self.assertEqual(relation[0], "example-b#C001")
            self.assertEqual(relation[1], 1)

            packet = retrieve_packet(db_path, "example-a#C001")
            neighbors = {neighbor["claim_uid"] for neighbor in packet["neighbors"]}
            self.assertIn("example-b#C001", neighbors)

            self.assertTrue((out / "retrieval/example-a__C001.json").exists())
            self.assertTrue((out / "adapters/openai-compatible/request-example-a__C001.json").exists())

    def test_client_export_filters_forbidden_nodes_edges_and_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = self.write_tier_fixture(root)
            out = root / "client"

            summary = compile_bundle(
                pack,
                out,
                export_tier="client",
                query_claims=["C001"],
                questions={"C001": "What can the client see?"},
            )

            self.assertEqual(summary["export_tier"], "client")
            self.assertEqual(summary["claims"], 1)
            self.assertEqual(summary["evidence"], 1)
            self.assertEqual(summary["relations"], 0)
            self.assertEqual(summary["unresolved_relations"], 0)
            self.assertEqual(summary["projection"]["filtered_claims"], 3)
            self.assertEqual(summary["projection"]["filtered_evidence"], 2)
            self.assertGreaterEqual(summary["projection"]["filtered_relations"], 1)
            self.assertTrue(summary["validation"]["valid"])
            self.assertEqual(
                summary["validation"]["checks"],
                {
                    "claim_policy_violations": 0,
                    "evidence_policy_violations": 0,
                    "dangling_evidence_links": 0,
                    "dangling_relations": 0,
                    "blocked_unresolved_relations": 0,
                },
            )

            db_path = out / "indices" / "claim-graph.sqlite"
            conn = sqlite3.connect(db_path)
            try:
                self.assertEqual(
                    conn.execute("SELECT group_concat(local_claim_id) FROM kp_claims").fetchone()[0],
                    "C001",
                )
                self.assertEqual(
                    conn.execute("SELECT group_concat(local_evidence_id) FROM kp_evidence").fetchone()[0],
                    "E001",
                )
                self.assertEqual(
                    conn.execute("SELECT count(*) FROM kp_claim_relations").fetchone()[0],
                    0,
                )
            finally:
                conn.close()

            packet = retrieve_packet(db_path, "C001")
            self.assertEqual(packet["policy"]["export_tier"], "client")
            self.assertEqual(packet["policy"]["filtered_claim_count"], 3)
            self.assertEqual(packet["neighbors"], [])
            self.assertEqual([row["local_evidence_id"] for row in packet["evidence"]], ["E001"])

            with self.assertRaisesRegex(ValueError, "claim not found"):
                retrieve_packet(db_path, "C002")

    def test_server_export_keeps_server_material_but_filters_internal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = self.write_tier_fixture(root)
            out = root / "server"

            summary = compile_bundle(
                pack,
                out,
                export_tier="server",
                query_claims=["C001"],
                questions={"C001": "What can the server see?"},
            )

            self.assertEqual(summary["export_tier"], "server")
            self.assertEqual(summary["claims"], 3)
            self.assertEqual(summary["evidence"], 2)
            self.assertEqual(summary["relations"], 1)
            self.assertEqual(summary["unresolved_relations"], 0)
            self.assertEqual(summary["projection"]["filtered_claims"], 1)
            self.assertEqual(summary["projection"]["filtered_evidence"], 1)
            self.assertTrue(summary["validation"]["valid"])

            db_path = out / "indices" / "claim-graph.sqlite"
            packet = retrieve_packet(db_path, "C001")
            neighbors = {neighbor["local_claim_id"] for neighbor in packet["neighbors"]}
            evidence_ids = {row["local_evidence_id"] for row in packet["evidence"]}
            self.assertEqual(packet["policy"]["export_tier"], "server")
            self.assertIn("C002", neighbors)
            self.assertEqual(evidence_ids, {"E001", "E002"})

            with self.assertRaisesRegex(ValueError, "claim not found"):
                retrieve_packet(db_path, "C004")


if __name__ == "__main__":
    unittest.main()
