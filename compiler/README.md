<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- SPDX-FileCopyrightText: 2026 Timothy Kompanchenko -->

# Experimental Graph Compiler

This directory contains an experimental compiler for deriving a graph projection
from KP:1 `.kpack` directories.

The current compiler is intentionally small. It can:

- parse dense KP:1 claims and evidence entries;
- compile one or more packs, claims, evidence, claim-evidence links, and claim
  relations into SQLite tables;
- resolve cross-pack claim relations when all referenced packs are compiled in
  the same bundle;
- store graph metadata such as schema version, compiler version, source hash,
  and unresolved relation count;
- retrieve a bounded one-hop claim neighborhood;
- render a dossier for a selected claim;
- emit OpenAI-compatible, Ollama-style, and MCP-style adapter artifacts.

It is not yet a stable public API. Current limits:

- dense claim metadata only;
- exact claim-ID retrieval;
- approximate token counting;
- no encrypted bundle output;
- no tier-slicing compiler yet.

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

Compile more than one pack:

```bash
python3 compiler/graph_compiler.py \
  examples/hello-world.kpack \
  examples/solar-energy-market.kpack \
  --output /tmp/kp-graph
```
