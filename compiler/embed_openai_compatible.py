#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Timothy Kompanchenko
"""Reference KP embedding producer for OpenAI-compatible endpoints.

This adapter is intentionally small and public-safe: it consumes the graph
compiler's embedding surfaces and manifest, calls an explicit endpoint supplied
by the operator, and emits vector JSONL/query-vector artifacts that the compiler
can validate and seal. Production runners can wrap or replace this adapter, but
the KP repository owns the artifact contract rather than a deployment-specific
embedding service.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

try:
    from compiler.graph_compiler import (
        EMBEDDING_DOCUMENT_PREFIX,
        EMBEDDING_PREFIX_SCHEME,
        EMBEDDING_SURFACE_VERSION,
        VECTOR_CONTRACT_VERSION,
        embedding_input_text,
        vector_text_hash,
    )
except ModuleNotFoundError:
    from graph_compiler import (  # type: ignore[no-redef]
        EMBEDDING_DOCUMENT_PREFIX,
        EMBEDDING_PREFIX_SCHEME,
        EMBEDDING_SURFACE_VERSION,
        VECTOR_CONTRACT_VERSION,
        embedding_input_text,
        vector_text_hash,
    )


SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


def jsonl_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text())
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return raw


def require_sha256(value: str, *, label: str) -> None:
    if not SHA256_PATTERN.match(value):
        raise ValueError(f"{label} must be sha256:<64 lowercase hex chars>")


def validate_manifest(manifest: dict[str, Any], *, surfaces_path: Path, surface_count: int) -> None:
    surfaces_hash = jsonl_sha256(surfaces_path)
    checks = {
        "claim_surfaces_sha256": surfaces_hash,
        "claim_count": surface_count,
        "vector_contract_version": VECTOR_CONTRACT_VERSION,
        "embedding_surface_version": EMBEDDING_SURFACE_VERSION,
        "embedding_prefix_scheme": EMBEDDING_PREFIX_SCHEME,
    }
    for key, expected in checks.items():
        if manifest.get(key) != expected:
            raise ValueError(
                f"embedding manifest mismatch for {key}: {manifest.get(key)!r} != {expected!r}"
            )


def load_surfaces(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"surface row {line_number} must be a JSON object")
        for key in [
            "contract_version",
            "embedding_surface_version",
            "embedding_prefix_scheme",
            "embedding_role",
            "claim_uid",
            "source_text_hash",
            "source_text",
        ]:
            if key not in row:
                raise ValueError(f"surface row {line_number} missing {key}")
        if row["contract_version"] != VECTOR_CONTRACT_VERSION:
            raise ValueError(f"surface row {line_number} has unsupported contract_version")
        if row["embedding_surface_version"] != EMBEDDING_SURFACE_VERSION:
            raise ValueError(f"surface row {line_number} has unsupported embedding_surface_version")
        if row["embedding_prefix_scheme"] != EMBEDDING_PREFIX_SCHEME:
            raise ValueError(f"surface row {line_number} has unsupported embedding_prefix_scheme")
        if row["embedding_role"] != "document":
            raise ValueError(f"surface row {line_number} must have embedding_role=document")
        source_text = row["source_text"]
        if not isinstance(source_text, str) or not source_text.startswith(EMBEDDING_DOCUMENT_PREFIX):
            raise ValueError(f"surface row {line_number} must contain a prefixed document input")
        if row["source_text_hash"] != vector_text_hash(source_text):
            raise ValueError(f"surface row {line_number} source_text_hash is stale")
        rows.append(row)
    if not rows:
        raise ValueError(f"surface file is empty: {path}")
    return rows


def normalize_vector(vector: list[float]) -> list[float]:
    magnitude = math.sqrt(sum(value * value for value in vector))
    if magnitude == 0:
        raise ValueError("cannot normalize a zero vector")
    return [value / magnitude for value in vector]


def request_embeddings(
    *,
    endpoint: str,
    model: str,
    inputs: list[str],
    timeout: int,
) -> list[list[float]]:
    request = urllib.request.Request(
        endpoint.rstrip("/") + "/embeddings",
        data=json.dumps({"model": model, "input": inputs}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise ValueError(f"embedding endpoint request failed: {exc}") from exc

    if isinstance(payload, dict) and payload.get("error"):
        raise ValueError(f"embedding endpoint error: {payload['error']}")
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, list) or len(data) != len(inputs):
        raise ValueError("embedding endpoint returned an unexpected data shape")

    embeddings: list[list[float]] = []
    for index, item in enumerate(data):
        if not isinstance(item, dict) or not isinstance(item.get("embedding"), list):
            raise ValueError(f"embedding endpoint returned no vector for input {index}")
        vector = [float(value) for value in item["embedding"]]
        if not vector:
            raise ValueError(f"embedding endpoint returned an empty vector for input {index}")
        embeddings.append(vector)
    return embeddings


def write_vectors(
    *,
    surfaces: list[dict[str, Any]],
    vectors: list[list[float]],
    output_path: Path,
    model: str,
    model_fingerprint: str,
    distance: str,
    normalize: bool,
) -> int:
    dimensions: int | None = None
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for surface, vector in zip(surfaces, vectors, strict=True):
            if normalize:
                vector = normalize_vector(vector)
            if dimensions is None:
                dimensions = len(vector)
            elif len(vector) != dimensions:
                raise ValueError("embedding endpoint returned mixed vector dimensions")
            row = {
                "contract_version": VECTOR_CONTRACT_VERSION,
                "embedding_surface_version": EMBEDDING_SURFACE_VERSION,
                "embedding_prefix_scheme": EMBEDDING_PREFIX_SCHEME,
                "claim_uid": surface["claim_uid"],
                "model_id": model,
                "model_fingerprint": model_fingerprint,
                "dimensions": len(vector),
                "distance": distance,
                "normalized": normalize,
                "source_text_hash": surface["source_text_hash"],
                "embedding": vector,
            }
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    return dimensions or 0


def write_query_vector(
    *,
    query_text: str,
    output_path: Path,
    endpoint: str,
    model: str,
    model_fingerprint: str,
    dimensions: int,
    distance: str,
    timeout: int,
    normalize: bool,
) -> None:
    query_input = embedding_input_text(query_text, role="query")
    [vector] = request_embeddings(
        endpoint=endpoint,
        model=model,
        inputs=[query_input],
        timeout=timeout,
    )
    if normalize:
        vector = normalize_vector(vector)
    if len(vector) != dimensions:
        raise ValueError(
            f"query vector dimensions mismatch: {len(vector)} != {dimensions}"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "contract_version": VECTOR_CONTRACT_VERSION,
                "model_id": model,
                "model_fingerprint": model_fingerprint,
                "embedding_prefix_scheme": EMBEDDING_PREFIX_SCHEME,
                "dimensions": dimensions,
                "distance": distance,
                "embedding": vector,
            },
            sort_keys=True,
        )
        + "\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate KP claim vectors from an OpenAI-compatible embedding endpoint."
    )
    parser.add_argument("--surfaces", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--model-fingerprint", required=True)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--distance", choices=["cosine"], default="cosine")
    parser.add_argument("--normalize", action="store_true")
    parser.add_argument("--query-text")
    parser.add_argument("--query-output", type=Path)
    parser.add_argument("--query-only", action="store_true")
    parser.add_argument("--dimensions", type=int)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    if args.batch_size < 1:
        parser.error("--batch-size must be positive")
    if bool(args.query_text) != bool(args.query_output):
        parser.error("--query-text and --query-output must be provided together")
    if args.query_only and (args.surfaces or args.manifest or args.output):
        parser.error("--query-only cannot be combined with --surfaces, --manifest, or --output")
    if args.query_only and not (args.query_text and args.query_output):
        parser.error("--query-only requires --query-text and --query-output")
    if args.query_only and (args.dimensions is None or args.dimensions < 1):
        parser.error("--query-only requires a positive --dimensions")
    require_sha256(args.model_fingerprint, label="--model-fingerprint")

    if args.query_only:
        assert args.query_text is not None
        assert args.query_output is not None
        assert args.dimensions is not None
        write_query_vector(
            query_text=args.query_text,
            output_path=args.query_output,
            endpoint=args.endpoint,
            model=args.model,
            model_fingerprint=args.model_fingerprint,
            dimensions=args.dimensions,
            distance=args.distance,
            timeout=args.timeout,
            normalize=args.normalize,
        )
        report = {
            "model_id": args.model,
            "model_fingerprint": args.model_fingerprint,
            "embedding_prefix_scheme": EMBEDDING_PREFIX_SCHEME,
            "endpoint": args.endpoint,
            "claim_count": 0,
            "dimensions": args.dimensions,
            "distance": args.distance,
            "normalized": args.normalize,
            "manifest_path": None,
            "manifest_claim_surfaces_sha256": None,
            "surfaces_path": None,
            "vectors_path": None,
            "query_output": str(args.query_output),
            "query_only": True,
        }
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(json.dumps(report, sort_keys=True))
        return 0

    if not args.surfaces:
        parser.error("--surfaces is required unless --query-only is set")
    if not args.manifest:
        parser.error("--manifest is required unless --query-only is set")
    if not args.output:
        parser.error("--output is required unless --query-only is set")

    manifest = load_json(args.manifest)
    surfaces = load_surfaces(args.surfaces)
    validate_manifest(manifest, surfaces_path=args.surfaces, surface_count=len(surfaces))

    vectors: list[list[float]] = []
    for start in range(0, len(surfaces), args.batch_size):
        batch = surfaces[start : start + args.batch_size]
        print(
            f"[embed] {start + 1}-{start + len(batch)} / {len(surfaces)}",
            file=sys.stderr,
            flush=True,
        )
        vectors.extend(
            request_embeddings(
                endpoint=args.endpoint,
                model=args.model,
                inputs=[row["source_text"] for row in batch],
                timeout=args.timeout,
            )
        )

    dimensions = write_vectors(
        surfaces=surfaces,
        vectors=vectors,
        output_path=args.output,
        model=args.model,
        model_fingerprint=args.model_fingerprint,
        distance=args.distance,
        normalize=args.normalize,
    )

    query_output = None
    if args.query_text and args.query_output:
        write_query_vector(
            query_text=args.query_text,
            output_path=args.query_output,
            endpoint=args.endpoint,
            model=args.model,
            model_fingerprint=args.model_fingerprint,
            dimensions=dimensions,
            distance=args.distance,
            timeout=args.timeout,
            normalize=args.normalize,
        )
        query_output = str(args.query_output)

    report = {
        "model_id": args.model,
        "model_fingerprint": args.model_fingerprint,
        "embedding_prefix_scheme": EMBEDDING_PREFIX_SCHEME,
        "endpoint": args.endpoint,
        "claim_count": len(surfaces),
        "dimensions": dimensions,
        "distance": args.distance,
        "normalized": args.normalize,
        "manifest_path": str(args.manifest),
        "manifest_claim_surfaces_sha256": manifest["claim_surfaces_sha256"],
        "surfaces_path": str(args.surfaces),
        "vectors_path": str(args.output),
        "query_output": query_output,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
