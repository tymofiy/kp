<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Experimental Graph Compiler

This directory contains an experimental compiler for deriving a graph projection
from KP:1 `.kpack` directories.

The current compiler is intentionally small. It can:

- parse dense and verbose KP:1 claims and evidence entries;
- compile one or more packs, claims, evidence, claim-evidence links, and claim
  relations into SQLite tables;
- resolve cross-pack claim relations when all referenced packs are compiled in
  the same bundle;
- store graph metadata such as schema version, compiler version, source hash,
  and unresolved relation count;
- project the graph for `client`, `server`, or `internal` export tiers;
- report projection policy plus source/retained boundary tuple counts for
  claims and evidence;
- validate tier projections for forbidden nodes, dangling evidence links,
  dangling relations, search-table leaks, and unresolved relation pointers;
- search compiled, export-tier-safe claims with fail-fast SQLite FTS5/BM25,
  imported sqlite-vec claim vectors, or hybrid FTS5/vector fusion, and map text
  queries to `claim_uid` results;
- emit stable embedding input surfaces and an embedding manifest for external
  embedding production;
- seal an imported vector bundle against an embedding manifest so stale or
  over-broad vector files fail visibly;
- retrieve a bounded one-hop claim neighborhood;
- render a dossier for a selected claim;
- emit OpenAI-compatible, Ollama-style, and MCP-style adapter artifacts.

Compiler-local boundary annotations can be attached with Markdown comments in
claim detail text:

```markdown
<!-- kp-compiler: tier=server sensitivity=internal visibility=private -->
```

Evidence entries can also use blockquote metadata fields:

```markdown
> **tier:** server | **sensitivity:** internal | **visibility:** private
```

The default export tier is `client`, which only emits `client` / `public` /
`public` material. `server` includes client and server material, while
`internal` is the full-trust profile.

Each compile summary includes the projection policy and boundary tuple counts in
the form `tier=<tier>|sensitivity=<sensitivity>|visibility=<visibility>|explicit=<true|false>`.
This lets downstream promotion gates distinguish "filtered for the expected
boundary reason" from "empty because source rows disappeared."

Boundary tuple counts are build-side audit metadata. They disclose the volume
and labels of filtered material, so they must not be copied into client runtime
bundles or user-facing adapter artifacts. The compiler keeps them in
`summary.json` and out of SQLite `graph_meta`.

Use `--require-explicit-boundary` for stricter local builds. In that mode every
claim and evidence record must declare compiler boundary metadata explicitly;
otherwise compilation fails before projection.

It is not yet a stable public API. Current limits:

- exact claim-ID retrieval;
- vector import rather than provider-native embedding generation;
- sqlite-vec is the current vector search backend;
- uncompressed vector sidecar output;
- approximate token counting;
- no encrypted bundle output;
- no redacted evidence stubs for claims that depend on filtered evidence.

Run the tests from the repository root:

```bash
python3 -m unittest compiler.tests.test_graph_compiler
```

Or:

```bash
make compiler-test
```

Compile one pack:

```bash
python3 compiler/graph_compiler.py examples/hello-world.kpack --output /tmp/kp-graph
```

Compile a server projection:

```bash
python3 compiler/graph_compiler.py examples/hello-world.kpack \
  --output /tmp/kp-graph-server \
  --export-tier server
```

Compile with strict boundary checks:

```bash
python3 compiler/graph_compiler.py examples/hello-world.kpack \
  --output /tmp/kp-graph-strict \
  --require-explicit-boundary
```

This intentionally fails unless every claim and evidence entry has explicit
compiler boundary metadata.

Compile and render a text-query hit:

```bash
python3 compiler/graph_compiler.py examples/hello-world.kpack \
  --output /tmp/kp-graph-search \
  --query-text "what should I know about hello world" \
  --query-limit 1
```

This writes a search report under `search/`, then renders retrieval packets,
dossiers, and adapter payloads for the selected claim hits.

Text queries default to `--search-mode fts5`, which fails if the compiled graph
does not contain an FTS5 index. `--search-mode lexical` exists only as an
explicit debug/test path; it is not used as a silent fallback.

Every compile emits embedding-production inputs under `embeddings/`:

- `claim-surfaces.jsonl`: one projected claim per row, containing the exact
  `claim-embedding-text-v1` document input to embed and its
  `source_text_hash`;
- `embedding-manifest.json`: the source hash, export tier, compiler version,
  surface hash, claim-count contract, vector contract version, and embedding
  prefix scheme for those rows.

Generate these inputs without importing vectors:

```bash
python3 compiler/graph_compiler.py examples/hello-world.kpack \
  --output /tmp/kp-graph-inputs
```

An external embedding lane can then read
`/tmp/kp-graph-inputs/embeddings/claim-surfaces.jsonl` and write a matching
claim-vector JSONL file. KP includes a small OpenAI-compatible reference
producer for local/conformance use, but production embedding orchestration is
expected to live outside this public repository:

```bash
python3 compiler/embed_openai_compatible.py \
  --surfaces /tmp/kp-graph-inputs/embeddings/claim-surfaces.jsonl \
  --manifest /tmp/kp-graph-inputs/embeddings/embedding-manifest.json \
  --output /tmp/claim-vectors.jsonl \
  --endpoint http://localhost:1234/v1 \
  --model text-embedding-nomic-embed-text-v1.5 \
  --model-fingerprint sha256:<64 lowercase hex chars>
```

Vector and hybrid search are first-class retrieval modes, but they require
explicit derived vector artifacts. The compiler does not call an embedding
provider directly. Instead, pass a claim-vector JSONL file; the compiler
validates it, stores compact float32 vector blobs in SQLite, and builds a
sqlite-vec `vec0` index for KNN search:

```json
{"contract_version":1,"claim_uid":"hello-world#C001","model_id":"text-embedding-nomic-embed-text-v1.5","model_fingerprint":"sha256:...","embedding_prefix_scheme":"nomic-search-v1","dimensions":768,"distance":"cosine","embedding_surface_version":"claim-embedding-text-v1","normalized":false,"source_text_hash":"sha256:...","embedding":[0.01,0.02]}
```

Each vector row must match the compiler `contract_version`, embedding surface
version, compiled claim `source_text_hash`, model ID, model fingerprint,
embedding prefix scheme, dimension count, distance, normalization flag, and
coverage contract. The current embedding surface is
`claim-embedding-text-v1`, separate from the FTS5 search surface, and document
embedding inputs are prefixed with `search_document:` under
`nomic-search-v1`. Query vectors for vector or hybrid search must be produced by
the same model fingerprint and prefix scheme, using the matching
`search_query:` input convention before embedding. If any compiled claim is
missing a vector, if the vector file is stale, if unknown claim IDs appear, or
if contracts are mixed, compilation fails. Rows for source claims filtered out
by an export tier are ignored and counted in graph metadata; they are not
written into the compiled graph.

The compiled graph stores vector contract metadata in `kp_claim_vectors` and the
actual KNN index in `kp_claim_vector_index`, a sqlite-vec `vec0` virtual table.
SQLite triggers keep the `vec0` index synchronized with `kp_claim_vectors`.
Vector and hybrid search fail if sqlite-vec cannot be loaded or if the `vec0`
index is missing/incomplete.

For production-style imports, seal the bundle against the embedding manifest
that was used to create the vectors:

```bash
python3 compiler/graph_compiler.py examples/hello-world.kpack \
  --output /tmp/kp-graph-sealed \
  --vectors-jsonl /tmp/claim-vectors.jsonl \
  --embedding-manifest /tmp/kp-graph-inputs/embeddings/embedding-manifest.json \
  --seal-bundle
```

Sealing requires the manifest to match the current projected bundle exactly:
compiler version, schema version, source hash, export tier, projection counts,
embedding surface version, embedding prefix scheme, claim count, claim UID set
hash, and claim-surface hash. It also requires the vector file to cover the
projected claims exactly.
In ordinary unsealed vector imports, rows for source claims filtered out by an
export tier may be ignored and counted. In sealed mode, those extra rows are a
hard error because the vector file must belong to this projected manifest.

Run vector search with one query-vector JSON object per `--query-text`:

```json
{"contract_version":1,"model_id":"text-embedding-nomic-embed-text-v1.5","model_fingerprint":"sha256:...","embedding_prefix_scheme":"nomic-search-v1","dimensions":768,"distance":"cosine","embedding":[0.01,0.02]}
```

```bash
python3 compiler/graph_compiler.py examples/hello-world.kpack \
  --output /tmp/kp-graph-vector \
  --vectors-jsonl /tmp/claim-vectors.jsonl \
  --query-text "what should I know about hello world" \
  --query-vector /tmp/query-vector.json \
  --search-mode vector \
  --query-limit 1
```

Run hybrid search by switching `--search-mode hybrid`. Hybrid requires both the
FTS5 index and a matching vector index/query vector. If either side is missing,
it fails rather than silently degrading.

Compile more than one pack:

```bash
python3 compiler/graph_compiler.py \
  examples/hello-world.kpack \
  examples/solar-energy-market.kpack \
  --output /tmp/kp-graph
```
