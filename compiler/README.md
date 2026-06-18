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
  dangling relations, and unresolved relation pointers;
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

It is not yet a stable public API. Current limits:

- exact claim-ID retrieval;
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

Compile more than one pack:

```bash
python3 compiler/graph_compiler.py \
  examples/hello-world.kpack \
  examples/solar-energy-market.kpack \
  --output /tmp/kp-graph
```
