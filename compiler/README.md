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
- validate tier projections for forbidden nodes, dangling evidence links,
  dangling relations, search-table leaks, and unresolved relation pointers;
- search compiled, export-tier-safe claims with fail-fast SQLite FTS5/BM25,
  imported claim vectors, or hybrid FTS5/vector fusion, and map text queries to
  `claim_uid` results;
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

Use `--require-explicit-boundary` for stricter local builds. In that mode every
claim and evidence record must declare compiler boundary metadata explicitly;
otherwise compilation fails before projection.

It is not yet a stable public API. Current limits:

- exact claim-ID retrieval;
- vector import rather than provider-native embedding generation;
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

Vector and hybrid search are first-class retrieval modes, but they require
explicit derived vector artifacts. The compiler does not call an embedding
provider directly. Instead, pass a claim-vector JSONL file:

```json
{"contract_version":1,"claim_uid":"hello-world#C001","model_id":"text-embedding-nomic-embed-text-v1.5","dimensions":768,"distance":"cosine","embedding_surface_version":"claim-search-text-v1","normalized":false,"source_text_hash":"sha256:...","embedding":[0.01,0.02]}
```

Each vector row must match the compiler `contract_version`, embedding surface
version, compiled claim `source_text_hash`, model ID, dimension count, distance,
and coverage contract. The current embedding surface is
`claim-search-text-v1`, derived from the same claim/evidence text used for
FTS5 indexing. If any compiled claim is missing a vector, if the vector file is
stale, if unknown claim IDs appear, or if contracts are mixed, compilation
fails. Rows for source claims filtered out by an export tier are ignored and
counted in graph metadata; they are not written into the compiled graph.

Run vector search with one query-vector JSON object per `--query-text`:

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
