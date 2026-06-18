import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from compiler.graph_compiler import (
    claim_search_text,
    compile_bundle,
    load_sqlite_vec,
    parse_pack,
    project_for_export_tier,
    render_dossier,
    retrieve_packet,
    search_claims,
    VECTOR_INDEX_TABLE,
    vector_text_hash,
)


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

    def write_vectors(
        self,
        path: Path,
        pack: Path,
        vectors_by_local_id: dict[str, list[float]],
        *,
        model_id: str = "test-embedder-v1",
        export_tier: str = "client",
        stale_claim_uid: str | None = None,
        extra_rows: list[dict[str, object]] | None = None,
    ) -> Path:
        parsed_packs, _projection = project_for_export_tier([parse_pack(pack)], export_tier)
        evidence_by_uid = {
            evidence.evidence_uid: evidence
            for parsed_pack in parsed_packs
            for evidence in parsed_pack.evidence
        }
        rows = []
        for parsed_pack in parsed_packs:
            for claim in parsed_pack.claims:
                embedding = vectors_by_local_id[claim.local_claim_id]
                search_text = claim_search_text(claim, evidence_by_uid)
                source_hash = vector_text_hash(search_text)
                if claim.claim_uid == stale_claim_uid:
                    source_hash = "sha256:" + "0" * 64
                rows.append(
                    {
                        "contract_version": 1,
                        "claim_uid": claim.claim_uid,
                        "model_id": model_id,
                        "dimensions": len(embedding),
                        "distance": "cosine",
                        "embedding_surface_version": "claim-search-text-v1",
                        "normalized": False,
                        "source_text_hash": source_hash,
                        "embedding": embedding,
                    }
                )
        rows.extend(extra_rows or [])
        path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n")
        return path

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
  {{0.80|i|E001|2026-06-18|investigated|judgment}} Public rationale. ↔C002 <!-- kp-compiler: tier=client sensitivity=public visibility=public -->

- [C002] The server-only method explains the conclusion.
  {{0.90|i|E002|2026-06-18|investigated|meta}} Server method. <!-- kp-compiler: tier=server sensitivity=internal visibility=private -->

- [C003] This claim looks public but depends on server-only evidence.
  {{0.70|i|E002|2026-06-18|investigated|judgment}} Must not survive client slicing. <!-- kp-compiler: tier=client sensitivity=public visibility=public -->

- [C004] The internal operator note is not server-shippable.
  {{0.95|i|E003|2026-06-18|investigated|meta}} Operator-only note. <!-- kp-compiler: tier=internal sensitivity=restricted visibility=private -->
"""
        )
        (pack / "evidence.md").write_text(
            """# Evidence

## E001 — Public Note
> **type:** synthetic_document | **captured:** 2026-06-18 | **tier:** client | **sensitivity:** public | **visibility:** public
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
                    "3",
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
                    "dangling_search_rows": 0,
                    "dangling_vector_rows": 0,
                    "dangling_vector_index_rows": 0,
                    "dangling_fts_rows": 0,
                    "missing_vector_index": 0,
                    "incomplete_vector_coverage": 0,
                    "incomplete_vector_index_coverage": 0,
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

    def test_require_explicit_boundary_rejects_implicit_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = self.write_fixture(root)

            with self.assertRaisesRegex(ValueError, "explicit boundary metadata required"):
                compile_bundle(
                    pack,
                    root / "strict",
                    require_explicit_boundary=True,
                )

    def test_require_explicit_boundary_accepts_annotated_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = self.write_tier_fixture(root)
            out = root / "strict"

            summary = compile_bundle(
                pack,
                out,
                require_explicit_boundary=True,
                query_texts=["client safe conclusion"],
                query_limit=1,
            )

            self.assertEqual(
                summary["boundary"],
                {
                    "required": True,
                    "valid": True,
                    "implicit_claims": 0,
                    "implicit_evidence": 0,
                },
            )
            self.assertEqual(summary["search_reports"][0]["hits"][0]["claim_uid"], "example-tiered#C001")

    def test_text_query_renders_graph_expanded_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = self.write_fixture(root)
            out = root / "search"

            summary = compile_bundle(
                pack,
                out,
                query_texts=["current reading"],
                query_limit=1,
            )

            self.assertEqual(summary["query_texts"], ["current reading"])
            self.assertEqual(len(summary["search_reports"]), 1)
            hits = summary["search_reports"][0]["hits"]
            self.assertEqual(len(hits), 1)
            self.assertEqual(hits[0]["claim_uid"], "example-supersession#C002")
            self.assertEqual(hits[0]["search_engine"], "fts5")
            self.assertTrue(Path(hits[0]["artifacts"]["retrieval"]).exists())
            self.assertTrue(Path(hits[0]["artifacts"]["dossier"]).exists())
            self.assertTrue(Path(hits[0]["artifacts"]["openai_request"]).exists())
            self.assertTrue(Path(hits[0]["artifacts"]["ollama_prompt"]).exists())
            self.assertTrue(Path(hits[0]["artifacts"]["mcp_tool_response"]).exists())

            search_report_path = out / "search" / "1-current-reading.json"
            search_report = json.loads(search_report_path.read_text())
            self.assertEqual(search_report["hits"][0]["claim_uid"], "example-supersession#C002")

            packet = json.loads(Path(hits[0]["artifacts"]["retrieval"]).read_text())
            neighbors = {neighbor["local_claim_id"] for neighbor in packet["neighbors"]}
            self.assertTrue({"C001", "C003"}.issubset(neighbors))

    def test_client_search_excludes_filtered_claims(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = self.write_tier_fixture(root)
            out = root / "client-search"

            summary = compile_bundle(
                pack,
                out,
                export_tier="client",
                query_texts=["server method"],
                query_limit=3,
            )

            self.assertEqual(summary["claims"], 1)
            self.assertEqual(summary["search_reports"][0]["hits"], [])

            db_path = out / "indices" / "claim-graph.sqlite"
            self.assertEqual(search_claims(db_path, "server method", limit=3), [])

            public_hits = search_claims(db_path, "client safe conclusion", limit=3)
            self.assertEqual([hit["claim_uid"] for hit in public_hits], ["example-tiered#C001"])

    def test_text_query_can_use_explicit_lexical_debug_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = self.write_fixture(root)
            out = root / "lexical-search"

            summary = compile_bundle(
                pack,
                out,
                query_texts=["current reading"],
                query_limit=1,
                search_mode="lexical",
            )

            hits = summary["search_reports"][0]["hits"]
            self.assertEqual(hits[0]["claim_uid"], "example-supersession#C002")
            self.assertEqual(hits[0]["search_engine"], "lexical")

            db_path = out / "indices" / "claim-graph.sqlite"
            direct_hits = search_claims(db_path, "current reading", limit=1, mode="lexical")
            self.assertEqual(direct_hits[0]["search_engine"], "lexical")
            self.assertEqual(direct_hits[0]["claim_uid"], "example-supersession#C002")

    def test_fts5_search_fails_when_index_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = self.write_fixture(root)
            out = root / "missing-fts"

            summary = compile_bundle(pack, out)
            self.assertEqual(summary["graph_meta"]["search_engine"], "fts5")

            db_path = out / "indices" / "claim-graph.sqlite"
            conn = sqlite3.connect(db_path)
            try:
                conn.execute("DROP TABLE kp_claim_search_fts")
                conn.commit()
            finally:
                conn.close()

            with self.assertRaisesRegex(ValueError, "FTS5 search requested"):
                search_claims(db_path, "current reading", limit=1, mode="fts5")

            lexical_hits = search_claims(db_path, "current reading", limit=1, mode="lexical")
            self.assertEqual(lexical_hits[0]["search_engine"], "lexical")

    def test_default_text_query_uses_fts5(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = self.write_fixture(root)
            out = root / "fts5-search"

            summary = compile_bundle(
                pack,
                out,
                query_texts=["current reading"],
                query_limit=1,
            )

            self.assertEqual(summary["graph_meta"]["search_engine"], "fts5")
            self.assertEqual(summary["search_mode"], "fts5")
            self.assertEqual(summary["search_reports"][0]["hits"][0]["search_engine"], "fts5")

    def test_vector_query_uses_imported_claim_vectors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = self.write_fixture(root)
            vectors_path = self.write_vectors(
                root / "claim-vectors.jsonl",
                pack,
                {
                    "C001": [0.0, 1.0, 0.0],
                    "C002": [1.0, 0.0, 0.0],
                    "C003": [0.0, 0.0, 1.0],
                },
            )
            out = root / "vector-search"

            query_vector = {
                "contract_version": 1,
                "model_id": "test-embedder-v1",
                "dimensions": 3,
                "distance": "cosine",
                "embedding": [1.0, 0.0, 0.0],
            }
            summary = compile_bundle(
                pack,
                out,
                vectors_jsonl=vectors_path,
                query_texts=["semantic current reading"],
                query_vectors=[query_vector],
                query_limit=1,
                search_mode="vector",
            )

            self.assertEqual(summary["graph_meta"]["vector_index"], "sqlite-vec")
            self.assertEqual(summary["graph_meta"]["vector_index_engine"], "sqlite-vec")
            self.assertEqual(summary["graph_meta"]["vector_claim_count"], "3")
            hit = summary["search_reports"][0]["hits"][0]
            self.assertEqual(hit["claim_uid"], "example-supersession#C002")
            self.assertEqual(hit["search_engine"], "vector")
            self.assertEqual(hit["vector_model_id"], "test-embedder-v1")
            self.assertEqual(hit["vector_index_engine"], "sqlite-vec")
            self.assertEqual(hit["vector_distance"], 0.0)

            db_path = out / "indices" / "claim-graph.sqlite"
            conn = sqlite3.connect(db_path)
            try:
                load_sqlite_vec(conn)
                self.assertEqual(
                    conn.execute("SELECT typeof(vector_blob) FROM kp_claim_vectors LIMIT 1").fetchone()[0],
                    "blob",
                )
                self.assertEqual(
                    conn.execute(f"SELECT count(*) FROM {VECTOR_INDEX_TABLE}").fetchone()[0],
                    3,
                )
            finally:
                conn.close()
            direct_hits = search_claims(
                db_path,
                "semantic current reading",
                limit=1,
                mode="vector",
                query_vector=query_vector,
            )
            self.assertEqual(direct_hits[0]["claim_uid"], "example-supersession#C002")

            conn = sqlite3.connect(db_path)
            try:
                load_sqlite_vec(conn)
                conn.execute("DELETE FROM kp_claim_vectors WHERE claim_uid = 'example-supersession#C003'")
                conn.commit()
                self.assertEqual(
                    conn.execute(f"SELECT count(*) FROM {VECTOR_INDEX_TABLE}").fetchone()[0],
                    2,
                )
            finally:
                conn.close()

    def test_hybrid_query_requires_and_fuses_fts5_and_vectors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = self.write_fixture(root)
            vectors_path = self.write_vectors(
                root / "claim-vectors.jsonl",
                pack,
                {
                    "C001": [0.0, 1.0, 0.0],
                    "C002": [1.0, 0.0, 0.0],
                    "C003": [0.0, 0.0, 1.0],
                },
            )
            out = root / "hybrid-search"

            summary = compile_bundle(
                pack,
                out,
                vectors_jsonl=vectors_path,
                query_texts=["current reading"],
                query_vectors=[
                    {
                        "contract_version": 1,
                        "model_id": "test-embedder-v1",
                        "dimensions": 3,
                        "distance": "cosine",
                        "embedding": [1.0, 0.0, 0.0],
                    }
                ],
                query_limit=1,
                search_mode="hybrid",
            )

            hit = summary["search_reports"][0]["hits"][0]
            self.assertEqual(hit["claim_uid"], "example-supersession#C002")
            self.assertEqual(hit["search_engine"], "hybrid")
            self.assertEqual(hit["component_ranks"]["fts5"], 1)
            self.assertEqual(hit["component_ranks"]["vector"], 1)

    def test_hybrid_search_fails_when_fts5_index_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = self.write_fixture(root)
            vectors_path = self.write_vectors(
                root / "claim-vectors.jsonl",
                pack,
                {
                    "C001": [0.0, 1.0, 0.0],
                    "C002": [1.0, 0.0, 0.0],
                    "C003": [0.0, 0.0, 1.0],
                },
            )
            out = root / "hybrid-missing-fts"

            compile_bundle(pack, out, vectors_jsonl=vectors_path)

            db_path = out / "indices" / "claim-graph.sqlite"
            conn = sqlite3.connect(db_path)
            try:
                conn.execute("DROP TABLE kp_claim_search_fts")
                conn.commit()
            finally:
                conn.close()

            with self.assertRaisesRegex(ValueError, "no FTS5 index"):
                search_claims(
                    db_path,
                    "current reading",
                    limit=1,
                    mode="hybrid",
                    query_vector={
                        "contract_version": 1,
                        "model_id": "test-embedder-v1",
                        "dimensions": 3,
                        "embedding": [1.0, 0.0, 0.0],
                    },
                )

    def test_vector_search_fails_when_index_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = self.write_fixture(root)
            out = root / "missing-vector"

            compile_bundle(pack, out)

            db_path = out / "indices" / "claim-graph.sqlite"
            with self.assertRaisesRegex(ValueError, "no claim vector index"):
                search_claims(
                    db_path,
                    "semantic current reading",
                    limit=1,
                    mode="vector",
                    query_vector={
                        "contract_version": 1,
                        "model_id": "test-embedder-v1",
                        "dimensions": 3,
                        "embedding": [1.0, 0.0, 0.0],
                    },
                )

    def test_vector_search_fails_when_sqlite_vec_table_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = self.write_fixture(root)
            vectors_path = self.write_vectors(
                root / "claim-vectors.jsonl",
                pack,
                {
                    "C001": [0.0, 1.0, 0.0],
                    "C002": [1.0, 0.0, 0.0],
                    "C003": [0.0, 0.0, 1.0],
                },
            )
            out = root / "missing-vec0"

            compile_bundle(pack, out, vectors_jsonl=vectors_path)

            db_path = out / "indices" / "claim-graph.sqlite"
            conn = sqlite3.connect(db_path)
            try:
                load_sqlite_vec(conn)
                conn.execute(f"DROP TABLE {VECTOR_INDEX_TABLE}")
                conn.commit()
            finally:
                conn.close()

            with self.assertRaisesRegex(ValueError, "no sqlite-vec index"):
                search_claims(
                    db_path,
                    "semantic current reading",
                    limit=1,
                    mode="vector",
                    query_vector={
                        "contract_version": 1,
                        "model_id": "test-embedder-v1",
                        "dimensions": 3,
                        "embedding": [1.0, 0.0, 0.0],
                    },
                )

    def test_vector_search_requires_query_vector(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = self.write_fixture(root)
            vectors_path = self.write_vectors(
                root / "claim-vectors.jsonl",
                pack,
                {
                    "C001": [0.0, 1.0, 0.0],
                    "C002": [1.0, 0.0, 0.0],
                    "C003": [0.0, 0.0, 1.0],
                },
            )

            with self.assertRaisesRegex(ValueError, "one query vector per query text"):
                compile_bundle(
                    pack,
                    root / "missing-query-vector",
                    vectors_jsonl=vectors_path,
                    query_texts=["current reading"],
                    search_mode="vector",
                )

    def test_client_vector_import_ignores_filtered_source_vectors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = self.write_tier_fixture(root)
            vectors_path = self.write_vectors(
                root / "tier-vectors.jsonl",
                pack,
                {
                    "C001": [1.0, 0.0, 0.0],
                    "C002": [0.0, 1.0, 0.0],
                    "C003": [0.0, 0.0, 1.0],
                    "C004": [1.0, 1.0, 0.0],
                },
                export_tier="internal",
            )
            out = root / "client-vector"

            summary = compile_bundle(
                pack,
                out,
                export_tier="client",
                vectors_jsonl=vectors_path,
                query_texts=["client safe conclusion"],
                query_vectors=[
                    {
                        "contract_version": 1,
                        "model_id": "test-embedder-v1",
                        "dimensions": 3,
                        "embedding": [1.0, 0.0, 0.0],
                    }
                ],
                query_limit=1,
                search_mode="vector",
            )

            self.assertEqual(summary["claims"], 1)
            self.assertEqual(summary["graph_meta"]["vector_claim_count"], "1")
            self.assertEqual(summary["graph_meta"]["vector_ignored_row_count"], "3")
            self.assertEqual(summary["search_reports"][0]["hits"][0]["claim_uid"], "example-tiered#C001")

            db_path = out / "indices" / "claim-graph.sqlite"
            conn = sqlite3.connect(db_path)
            try:
                self.assertEqual(
                    conn.execute("SELECT group_concat(claim_uid) FROM kp_claim_vectors").fetchone()[0],
                    "example-tiered#C001",
                )
            finally:
                conn.close()

    def test_vector_import_rejects_unknown_claim_uid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = self.write_fixture(root)
            vectors_path = self.write_vectors(
                root / "claim-vectors.jsonl",
                pack,
                {
                    "C001": [0.0, 1.0, 0.0],
                    "C002": [1.0, 0.0, 0.0],
                    "C003": [0.0, 0.0, 1.0],
                },
                extra_rows=[
                    {
                        "contract_version": 1,
                        "claim_uid": "other-pack#C999",
                        "model_id": "test-embedder-v1",
                        "dimensions": 3,
                        "distance": "cosine",
                        "embedding_surface_version": "claim-search-text-v1",
                        "normalized": False,
                        "source_text_hash": "sha256:" + "1" * 64,
                        "embedding": [1.0, 0.0, 0.0],
                    }
                ],
            )

            with self.assertRaisesRegex(ValueError, "unknown claim vector"):
                compile_bundle(
                    pack,
                    root / "unknown-vector",
                    vectors_jsonl=vectors_path,
                )

    def test_vector_import_fails_when_source_hash_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = self.write_fixture(root)
            vectors_path = self.write_vectors(
                root / "claim-vectors.jsonl",
                pack,
                {
                    "C001": [0.0, 1.0, 0.0],
                    "C002": [1.0, 0.0, 0.0],
                    "C003": [0.0, 0.0, 1.0],
                },
                stale_claim_uid="example-supersession#C002",
            )

            with self.assertRaisesRegex(ValueError, "source_text_hash mismatch"):
                compile_bundle(
                    pack,
                    root / "stale-vector",
                    vectors_jsonl=vectors_path,
                )

    def test_query_vector_model_mismatch_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = self.write_fixture(root)
            vectors_path = self.write_vectors(
                root / "claim-vectors.jsonl",
                pack,
                {
                    "C001": [0.0, 1.0, 0.0],
                    "C002": [1.0, 0.0, 0.0],
                    "C003": [0.0, 0.0, 1.0],
                },
            )

            with self.assertRaisesRegex(ValueError, "query vector model_id mismatch"):
                compile_bundle(
                    pack,
                    root / "bad-query-vector",
                    vectors_jsonl=vectors_path,
                    query_texts=["current reading"],
                    query_vectors=[
                        {
                            "contract_version": 1,
                            "model_id": "other-embedder",
                            "dimensions": 3,
                            "embedding": [1.0, 0.0, 0.0],
                        }
                    ],
                    search_mode="vector",
                )


if __name__ == "__main__":
    unittest.main()
