#!/usr/bin/env python3
"""Experimental KP graph compiler.

Compiles a KP:1 pack into a small graph projection, retrieves bounded claim
neighborhoods, renders dossiers, and emits portable adapter request artifacts.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime
import hashlib
import json
import math
import re
import shutil
import sqlite3
from pathlib import Path
from typing import Any

import yaml


SCHEMA_VERSION = 4
COMPILER_VERSION = "0.8.1"
DEFAULT_QUERY_LIMIT = 3
SEARCH_MODES = ("fts5", "vector", "hybrid", "lexical")
VECTOR_SEARCH_MODES = ("vector", "hybrid")
RRF_K = 60
VECTOR_CONTRACT_VERSION = 1
EMBEDDING_SURFACE_VERSION = "claim-embedding-text-v1"
EMBEDDING_MANIFEST_VERSION = 1
EMBEDDING_PREFIX_SCHEME = "nomic-search-v1"
EMBEDDING_DOCUMENT_PREFIX = "search_document: "
EMBEDDING_QUERY_PREFIX = "search_query: "
BUNDLE_SEAL_VERSION = 1
VECTOR_INDEX_ENGINE = "sqlite-vec"
VECTOR_INDEX_TABLE = "kp_claim_vector_index"
SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")

RELATION_RE = re.compile(
    r"(\u2297~|\u2297!|\u2297|\u2192|\u2190|\u2298|\u2194|~)"
    r"(C\d+(?:-v\d+)?|[a-z][a-z0-9.-]*#[^\s,]+)"
)
VERBOSE_RELATION_RE = re.compile(
    r"(supports|contradicts:error|contradicts:tension|contradicts"
    r"|requires|refines|supersedes|see_also)\s+([\w#.-]+)"
)
CLAIM_START_RE = re.compile(r"^- (?:\*\*)?\[(C\d+(?:-v\d+)?)\](?:\*\*)?\s+(.+)")
EVIDENCE_HEADING_RE = re.compile(r"^##\s+(E\d+)(?:\s+(?:[-\u2014]\s*)?(.+))?$")
FIELD_RE = re.compile(r"\*\*([^:*]+):\*\*\s*(.+)")
ANNOTATION_RE = re.compile(r"<!--\s*kp-compiler:\s*(.*?)\s*-->")

EXPORT_TIERS = ("client", "server", "internal")
EXPORT_POLICIES = {
    "client": {
        "tiers": {"client"},
        "sensitivities": {"public"},
        "visibilities": {"public"},
        "allow_unresolved_relations": False,
    },
    "server": {
        "tiers": {"client", "server"},
        "sensitivities": {"public", "internal", "confidential"},
        "visibilities": {"public", "shared", "private"},
        "allow_unresolved_relations": False,
    },
    "internal": {
        "tiers": {"client", "server", "internal"},
        "sensitivities": {"public", "internal", "confidential", "restricted"},
        "visibilities": {"public", "shared", "private"},
        "allow_unresolved_relations": True,
    },
}
DEFAULT_TIER_BY_SENSITIVITY = {
    "public": "client",
    "internal": "server",
    "confidential": "server",
    "restricted": "internal",
}

TYPE_MAP = {
    "o": "observed",
    "r": "reported",
    "c": "computed",
    "i": "inferred",
}
VERBOSE_TYPE_MAP = {
    "observed": "observed",
    "reported": "reported",
    "computed": "computed",
    "inferred": "inferred",
}

RELATION_MAP = {
    "\u2192": "supports",
    "\u2297": "contradicts",
    "\u2297!": "contradicts:error",
    "\u2297~": "contradicts:tension",
    "\u2190": "requires",
    "~": "refines",
    "\u2298": "supersedes",
    "\u2194": "see_also",
}

EDGE_PRIORITY = [
    "supersedes",
    "contradicts:error",
    "contradicts:tension",
    "requires",
    "supports",
    "refines",
    "see_also",
]

SEARCH_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "what",
    "who",
    "which",
    "with",
    "why",
    "did",
    "do",
    "does",
}

@dataclasses.dataclass(frozen=True)
class Claim:
    claim_uid: str
    pack_id: str
    local_claim_id: str
    text: str
    detail: str
    confidence: float
    claim_type: str
    evidence_ids: list[str]
    since: str
    depth: str
    nature: str
    status: str
    tier: str
    sensitivity: str
    visibility: str
    boundary_explicit: bool
    source_locator: str


@dataclasses.dataclass(frozen=True)
class Evidence:
    evidence_uid: str
    pack_id: str
    local_evidence_id: str
    title: str
    source_type: str | None
    source_uri: str | None
    captured_at: str | None
    reliability: str | None
    credibility: int | None
    summary: str
    tier: str
    sensitivity: str
    visibility: str
    boundary_explicit: bool
    source_locator: str


@dataclasses.dataclass(frozen=True)
class Relation:
    relation_uid: str
    from_claim_uid: str
    to_claim_uid: str | None
    relation_type: str
    target_ref: str
    target_resolved: int
    source_locator: str


@dataclasses.dataclass(frozen=True)
class ParsedPack:
    pack: dict[str, Any]
    source_hash: str
    claims: list[Claim]
    evidence: list[Evidence]
    relations: list[Relation]


@dataclasses.dataclass(frozen=True)
class ClaimVector:
    claim_uid: str
    model_id: str
    model_fingerprint: str
    embedding_prefix_scheme: str
    dimensions: int
    vector: list[float]
    source_text_hash: str
    normalized: bool
    distance: str


def claim_uid(pack_id: str, local_claim_id: str) -> str:
    return f"{pack_id}#{local_claim_id}"


def evidence_uid(pack_id: str, local_evidence_id: str) -> str:
    return f"{pack_id}#{local_evidence_id}"


def relation_uid(from_claim_uid: str, relation_type: str, target_ref: str) -> str:
    return f"{from_claim_uid}:{relation_type}:{target_ref}"


def artifact_label(claim_id: str) -> str:
    return claim_id.replace("#", "__").replace("/", "_")


def slug_label(value: str, *, max_length: int = 48) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        slug = "query"
    return slug[:max_length].strip("-") or "query"


def stable_pack_hash(pack_dir: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in pack_dir.rglob("*") if p.is_file()):
        rel = path.relative_to(pack_dir).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def parse_claim_blocks(claims_text: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for line_number, line in enumerate(claims_text.splitlines(), start=1):
        match = CLAIM_START_RE.match(line)
        if match:
            if current is not None:
                blocks.append(current)
            current = {
                "id": match.group(1),
                "statement": match.group(2).strip(),
                "line": line_number,
                "continuations": [],
            }
            continue

        if current is not None and line.startswith("  "):
            current["continuations"].append((line_number, line.strip()))
            continue

        if current is not None and re.match(r"^##?\s", line):
            blocks.append(current)
            current = None

    if current is not None:
        blocks.append(current)

    return blocks


def strip_relations(text: str) -> str:
    return RELATION_RE.sub("", text).strip(" ,")


def strip_verbose_relations(text: str) -> str:
    if re.match(r"`relations:\s*", text):
        return ""
    return text.strip()


def parse_verbose_metadata(metadata: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for part in metadata.split("|"):
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def parse_annotation_fields(raw: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for part in re.split(r"[|,]\s*|\s+", raw.strip()):
        if not part:
            continue
        if "=" in part:
            key, value = part.split("=", 1)
        elif ":" in part:
            key, value = part.split(":", 1)
        else:
            continue
        fields[key.strip().lower()] = value.strip().lower()
    return fields


def remove_compiler_annotations(text: str) -> tuple[str, dict[str, str]]:
    fields: dict[str, str] = {}
    for match in ANNOTATION_RE.finditer(text):
        fields.update(parse_annotation_fields(match.group(1)))
    cleaned = ANNOTATION_RE.sub("", text)
    return re.sub(r"\s+", " ", cleaned).strip(), fields


def default_boundary_tier(sensitivity: str | None) -> str:
    return DEFAULT_TIER_BY_SENSITIVITY.get((sensitivity or "public").lower(), "client")


def normalized_boundary_metadata(
    raw: dict[str, str],
    *,
    default_tier: str,
    default_sensitivity: str,
    default_visibility: str,
) -> tuple[str, str, str]:
    tier = raw.get("tier", default_tier).lower()
    sensitivity = raw.get("sensitivity", default_sensitivity).lower()
    visibility = raw.get("visibility", default_visibility).lower()
    if tier not in EXPORT_POLICIES["internal"]["tiers"]:
        raise ValueError(f"unsupported compiler tier: {tier}")
    if sensitivity not in EXPORT_POLICIES["internal"]["sensitivities"]:
        raise ValueError(f"unsupported sensitivity: {sensitivity}")
    if visibility not in EXPORT_POLICIES["internal"]["visibilities"]:
        raise ValueError(f"unsupported visibility: {visibility}")
    return tier, sensitivity, visibility


def has_explicit_boundary(raw: dict[str, str]) -> bool:
    return {"tier", "sensitivity", "visibility"}.issubset(raw)


def parse_claims(
    pack_id: str,
    claims_text: str,
    *,
    default_tier: str,
    default_sensitivity: str,
    default_visibility: str,
) -> tuple[list[Claim], list[Relation]]:
    raw_claims: list[dict[str, Any]] = []
    raw_relations: list[tuple[str, str, str, str]] = []

    for block in parse_claim_blocks(claims_text):
        local_id = block["id"]
        continuations: list[tuple[int, str]] = block["continuations"]
        if not continuations:
            raise ValueError(f"{local_id} has no metadata continuation")

        meta_line_number, meta_line = continuations[0]
        dense = re.match(r"\{([^}]+)\}", meta_line)
        verbose = re.match(r"`(confidence:\s*[^`]*)`", meta_line)

        if dense:
            parts = [part.strip() for part in dense.group(1).split("|")]
            if len(parts) < 4:
                raise ValueError(f"{local_id} metadata has fewer than four fields")

            confidence = float(parts[0])
            claim_type = TYPE_MAP.get(parts[1], parts[1])
            evidence_ids = [ref.strip() for ref in parts[2].split(",") if ref.strip()]
            since = parts[3]
            depth = parts[4] if len(parts) >= 5 and parts[4] else ""
            nature = parts[5] if len(parts) >= 6 and parts[5] else "factual"

            detail_parts = [strip_relations(meta_line[dense.end() :])]
            relation_lines = [(meta_line_number, meta_line[dense.end() :])]
            for continuation_line_number, continuation in continuations[1:]:
                detail_parts.append(strip_relations(continuation))
                relation_lines.append((continuation_line_number, continuation))

            for relation_line_number, relation_text in relation_lines:
                for relation_match in RELATION_RE.finditer(relation_text):
                    symbol = relation_match.group(1)
                    target_ref = relation_match.group(2)
                    raw_relations.append(
                        (
                            local_id,
                            RELATION_MAP[symbol],
                            target_ref,
                            f"claims.md:{relation_line_number}",
                        )
                    )
        elif verbose:
            fields = parse_verbose_metadata(verbose.group(1))
            confidence = float(fields["confidence"])
            claim_type = VERBOSE_TYPE_MAP.get(fields["type"], fields["type"])
            evidence_ids = [ref.strip() for ref in fields["evidence"].split(",") if ref.strip()]
            since = fields["since"]
            depth = fields.get("depth", "")
            nature = fields.get("nature", "factual")

            detail_parts = []
            for continuation_line_number, continuation in continuations[1:]:
                detail_parts.append(strip_verbose_relations(continuation))
                relation_line = re.match(r"`relations:\s*(.+?)`", continuation)
                if not relation_line:
                    continue
                for relation_match in VERBOSE_RELATION_RE.finditer(relation_line.group(1)):
                    raw_relations.append(
                        (
                            local_id,
                            relation_match.group(1),
                            relation_match.group(2),
                            f"claims.md:{continuation_line_number}",
                        )
                    )
        else:
            raise ValueError(f"{local_id} has unsupported metadata syntax")

        detail, annotations = remove_compiler_annotations(
            " ".join(part for part in detail_parts if part).strip()
        )
        tier, sensitivity, visibility = normalized_boundary_metadata(
            annotations,
            default_tier=default_tier,
            default_sensitivity=default_sensitivity,
            default_visibility=default_visibility,
        )

        raw_claims.append(
            {
                "local_claim_id": local_id,
                "text": block["statement"],
                "detail": detail,
                "confidence": confidence,
                "claim_type": claim_type,
                "evidence_ids": evidence_ids,
                "since": since,
                "depth": depth,
                "nature": nature,
                "tier": tier,
                "sensitivity": sensitivity,
                "visibility": visibility,
                "boundary_explicit": has_explicit_boundary(annotations),
                "source_locator": f"claims.md:{block['line']}",
            }
        )

    local_claim_ids = {claim["local_claim_id"] for claim in raw_claims}
    superseded_ids = {
        target_ref
        for _source_id, relation_type, target_ref, _locator in raw_relations
        if relation_type == "supersedes" and target_ref in local_claim_ids
    }

    claims = [
        Claim(
            claim_uid=claim_uid(pack_id, raw["local_claim_id"]),
            pack_id=pack_id,
            local_claim_id=raw["local_claim_id"],
            text=raw["text"],
            detail=raw["detail"],
            confidence=raw["confidence"],
            claim_type=raw["claim_type"],
            evidence_ids=raw["evidence_ids"],
            since=raw["since"],
            depth=raw["depth"],
            nature=raw["nature"],
            status="superseded" if raw["local_claim_id"] in superseded_ids else "active",
            tier=raw["tier"],
            sensitivity=raw["sensitivity"],
            visibility=raw["visibility"],
            boundary_explicit=raw["boundary_explicit"],
            source_locator=raw["source_locator"],
        )
        for raw in raw_claims
    ]

    relations = []
    for source_id, relation_type, target_ref, locator in raw_relations:
        target_uid = claim_uid(pack_id, target_ref) if target_ref in local_claim_ids else None
        from_uid = claim_uid(pack_id, source_id)
        relations.append(
            Relation(
                relation_uid=relation_uid(from_uid, relation_type, target_ref),
                from_claim_uid=from_uid,
                to_claim_uid=target_uid,
                relation_type=relation_type,
                target_ref=target_ref,
                target_resolved=1 if target_uid else 0,
                source_locator=locator,
            )
        )

    return claims, relations


def parse_evidence(
    pack_id: str,
    evidence_text: str,
    *,
    default_tier: str,
    default_sensitivity: str,
    default_visibility: str,
) -> list[Evidence]:
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for line_number, line in enumerate(evidence_text.splitlines(), start=1):
        heading = EVIDENCE_HEADING_RE.match(line)
        if heading:
            if current is not None:
                sections.append(current)
            current = {
                "id": heading.group(1),
                "title": heading.group(2).strip() if heading.group(2) else heading.group(1),
                "line": line_number,
                "metadata": {},
                "body": [],
            }
            continue

        if current is None:
            continue

        if line.startswith("> "):
            metadata_line = line[2:].strip()
            for segment in metadata_line.split("|"):
                field = FIELD_RE.search(segment.strip())
                if field:
                    current["metadata"][field.group(1).strip().lower()] = field.group(2).strip()
            continue

        if line.strip():
            current["body"].append(line.strip())

    if current is not None:
        sections.append(current)

    evidence = []
    for section in sections:
        metadata = section["metadata"]
        credibility = metadata.get("credibility")
        body, body_annotations = remove_compiler_annotations(
            " ".join(section["body"]).strip()
        )
        tier, sensitivity, visibility = normalized_boundary_metadata(
            {**metadata, **body_annotations},
            default_tier=default_tier,
            default_sensitivity=default_sensitivity,
            default_visibility=default_visibility,
        )
        evidence.append(
            Evidence(
                evidence_uid=evidence_uid(pack_id, section["id"]),
                pack_id=pack_id,
                local_evidence_id=section["id"],
                title=section["title"],
                source_type=metadata.get("type"),
                source_uri=metadata.get("source"),
                captured_at=metadata.get("captured"),
                reliability=metadata.get("reliability"),
                credibility=int(credibility) if credibility and credibility.isdigit() else None,
                summary=body,
                tier=tier,
                sensitivity=sensitivity,
                visibility=visibility,
                boundary_explicit=has_explicit_boundary({**metadata, **body_annotations}),
                source_locator=f"evidence.md:{section['line']}",
            )
        )

    return evidence


def parse_pack(pack_dir: Path) -> ParsedPack:
    pack = yaml.safe_load((pack_dir / "PACK.yaml").read_text())
    pack_id = pack["name"]
    default_sensitivity = str(pack.get("sensitivity", "public")).lower()
    default_visibility = str(pack.get("visibility", "public")).lower()
    default_tier = default_boundary_tier(default_sensitivity)
    claims, relations = parse_claims(
        pack_id,
        (pack_dir / "claims.md").read_text(),
        default_tier=default_tier,
        default_sensitivity=default_sensitivity,
        default_visibility=default_visibility,
    )
    evidence = parse_evidence(
        pack_id,
        (pack_dir / "evidence.md").read_text(),
        default_tier=default_tier,
        default_sensitivity=default_sensitivity,
        default_visibility=default_visibility,
    )
    return ParsedPack(
        pack=pack,
        source_hash=stable_pack_hash(pack_dir),
        claims=claims,
        evidence=evidence,
        relations=relations,
    )


def resolve_relations(parsed_packs: list[ParsedPack]) -> list[ParsedPack]:
    all_claim_uids = {
        claim.claim_uid
        for parsed in parsed_packs
        for claim in parsed.claims
    }
    resolved_packs: list[ParsedPack] = []
    for parsed in parsed_packs:
        resolved_relations: list[Relation] = []
        for relation in parsed.relations:
            target_uid = relation.to_claim_uid
            if target_uid is None and "#" in relation.target_ref:
                target_uid = relation.target_ref
            target_resolved = 1 if target_uid in all_claim_uids else 0
            resolved_relations.append(
                Relation(
                    relation_uid=relation.relation_uid,
                    from_claim_uid=relation.from_claim_uid,
                    to_claim_uid=target_uid if target_resolved else None,
                    relation_type=relation.relation_type,
                    target_ref=relation.target_ref,
                    target_resolved=target_resolved,
                    source_locator=relation.source_locator,
                )
            )
        resolved_packs.append(dataclasses.replace(parsed, relations=resolved_relations))
    return resolved_packs


def bundle_source_hash(parsed_packs: list[ParsedPack]) -> str:
    digest = hashlib.sha256()
    for parsed in sorted(parsed_packs, key=lambda item: item.pack["name"]):
        digest.update(parsed.pack["name"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(parsed.source_hash.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def is_allowed_for_export(row: Claim | Evidence, export_tier: str) -> bool:
    policy = EXPORT_POLICIES[export_tier]
    return (
        row.tier in policy["tiers"]
        and row.sensitivity in policy["sensitivities"]
        and row.visibility in policy["visibilities"]
    )


def increment_reason(reasons: dict[str, int], reason: str) -> None:
    reasons[reason] = reasons.get(reason, 0) + 1


def boundary_tuple_key(row: Claim | Evidence) -> str:
    explicit = "true" if row.boundary_explicit else "false"
    return (
        f"tier={row.tier}|sensitivity={row.sensitivity}|"
        f"visibility={row.visibility}|explicit={explicit}"
    )


def increment_boundary_count(counts: dict[str, int], row: Claim | Evidence) -> None:
    key = boundary_tuple_key(row)
    counts[key] = counts.get(key, 0) + 1


def boundary_count_report(parsed_packs: list[ParsedPack]) -> dict[str, dict[str, int]]:
    claim_counts: dict[str, int] = {}
    evidence_counts: dict[str, int] = {}
    for parsed in parsed_packs:
        for claim in parsed.claims:
            increment_boundary_count(claim_counts, claim)
        for evidence in parsed.evidence:
            increment_boundary_count(evidence_counts, evidence)
    return {
        "claims": dict(sorted(claim_counts.items())),
        "evidence": dict(sorted(evidence_counts.items())),
    }


def project_for_export_tier(
    parsed_packs: list[ParsedPack],
    export_tier: str,
) -> tuple[list[ParsedPack], dict[str, Any]]:
    if export_tier not in EXPORT_POLICIES:
        raise ValueError(f"unsupported export tier: {export_tier}")

    parsed_packs = resolve_relations(parsed_packs)
    policy = EXPORT_POLICIES[export_tier]
    source_boundary_counts = boundary_count_report(parsed_packs)
    allowed_claim_uids: set[str] = set()
    allowed_evidence_uids: set[str] = set()
    claim_filter_reasons: dict[str, int] = {}
    evidence_filter_reasons: dict[str, int] = {}
    relation_filter_reasons: dict[str, int] = {}

    all_evidence = {
        evidence.evidence_uid: evidence
        for parsed in parsed_packs
        for evidence in parsed.evidence
    }

    for parsed in parsed_packs:
        for evidence in parsed.evidence:
            if is_allowed_for_export(evidence, export_tier):
                allowed_evidence_uids.add(evidence.evidence_uid)
            else:
                increment_reason(evidence_filter_reasons, "boundary_policy")

    for parsed in parsed_packs:
        for claim in parsed.claims:
            if not is_allowed_for_export(claim, export_tier):
                increment_reason(claim_filter_reasons, "boundary_policy")
                continue
            blocked_evidence = False
            for local_evidence_id in claim.evidence_ids:
                uid = evidence_uid(claim.pack_id, local_evidence_id)
                if uid not in all_evidence:
                    increment_reason(claim_filter_reasons, "missing_evidence")
                    blocked_evidence = True
                    break
                if uid not in allowed_evidence_uids:
                    increment_reason(claim_filter_reasons, "filtered_evidence_dependency")
                    blocked_evidence = True
                    break
            if not blocked_evidence:
                allowed_claim_uids.add(claim.claim_uid)

    projected: list[ParsedPack] = []
    filtered_relation_count = 0
    for parsed in parsed_packs:
        claims = [claim for claim in parsed.claims if claim.claim_uid in allowed_claim_uids]
        evidence = [
            evidence
            for evidence in parsed.evidence
            if evidence.evidence_uid in allowed_evidence_uids
        ]
        relations: list[Relation] = []
        for relation in parsed.relations:
            if relation.from_claim_uid not in allowed_claim_uids:
                filtered_relation_count += 1
                increment_reason(relation_filter_reasons, "filtered_source_claim")
                continue
            if relation.to_claim_uid is None:
                if policy["allow_unresolved_relations"]:
                    relations.append(relation)
                else:
                    filtered_relation_count += 1
                    increment_reason(relation_filter_reasons, "unresolved_target")
                continue
            if relation.to_claim_uid not in allowed_claim_uids:
                filtered_relation_count += 1
                increment_reason(relation_filter_reasons, "filtered_target_claim")
                continue
            relations.append(relation)
        projected.append(
            ParsedPack(
                pack=parsed.pack,
                source_hash=parsed.source_hash,
                claims=claims,
                evidence=evidence,
                relations=relations,
            )
        )

    retained_boundary_counts = boundary_count_report(projected)
    return projected, {
        "export_tier": export_tier,
        "policy": {
            "allowed_tiers": sorted(policy["tiers"]),
            "allowed_sensitivities": sorted(policy["sensitivities"]),
            "allowed_visibilities": sorted(policy["visibilities"]),
            "allow_unresolved_relations": policy["allow_unresolved_relations"],
        },
        "filtered_claims": sum(claim_filter_reasons.values()),
        "filtered_evidence": sum(evidence_filter_reasons.values()),
        "filtered_relations": filtered_relation_count,
        "claim_filter_reasons": dict(sorted(claim_filter_reasons.items())),
        "evidence_filter_reasons": dict(sorted(evidence_filter_reasons.items())),
        "relation_filter_reasons": dict(sorted(relation_filter_reasons.items())),
        "source_boundary_counts": source_boundary_counts,
        "retained_boundary_counts": retained_boundary_counts,
    }


def validate_explicit_boundaries(parsed_packs: list[ParsedPack]) -> dict[str, Any]:
    implicit_claims = [
        claim.claim_uid
        for parsed in parsed_packs
        for claim in parsed.claims
        if not claim.boundary_explicit
    ]
    implicit_evidence = [
        evidence.evidence_uid
        for parsed in parsed_packs
        for evidence in parsed.evidence
        if not evidence.boundary_explicit
    ]
    report = {
        "required": True,
        "valid": not implicit_claims and not implicit_evidence,
        "implicit_claims": len(implicit_claims),
        "implicit_evidence": len(implicit_evidence),
    }
    if not report["valid"]:
        examples = [*implicit_claims[:3], *implicit_evidence[:3]]
        raise ValueError(
            "explicit boundary metadata required; missing "
            f"{report['implicit_claims']} claims and {report['implicit_evidence']} evidence records"
            + (f" (examples: {', '.join(examples)})" if examples else "")
        )
    return report


def as_jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_jsonl(path: Path, rows: list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(as_jsonable(row), sort_keys=True) + "\n")


def jsonl_rows_sha256(rows: list[Any]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        digest.update(json.dumps(as_jsonable(row), sort_keys=True).encode("utf-8"))
        digest.update(b"\n")
    return "sha256:" + digest.hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def string_list_sha256(values: list[str]) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(value.encode("utf-8"))
        digest.update(b"\n")
    return "sha256:" + digest.hexdigest()


def claim_search_text(claim: Claim, evidence_by_uid: dict[str, Evidence]) -> str:
    evidence_parts = []
    for local_evidence_id in claim.evidence_ids:
        evidence = evidence_by_uid.get(evidence_uid(claim.pack_id, local_evidence_id))
        if evidence is None:
            continue
        evidence_parts.extend(
            part
            for part in [
                evidence.local_evidence_id,
                evidence.title,
                evidence.source_type or "",
                evidence.reliability or "",
                evidence.summary,
            ]
            if part
        )
    return " ".join(
        part
        for part in [
            claim.claim_uid,
            claim.local_claim_id,
            claim.text,
            claim.detail,
            claim.claim_type,
            claim.depth,
            claim.nature,
            claim.status,
            *evidence_parts,
        ]
        if part
    )


def claim_embedding_text(claim: Claim, evidence_by_uid: dict[str, Evidence]) -> str:
    evidence_parts = []
    for local_evidence_id in claim.evidence_ids:
        evidence = evidence_by_uid.get(evidence_uid(claim.pack_id, local_evidence_id))
        if evidence is None:
            continue
        evidence_parts.extend(
            part
            for part in [
                f"Evidence title: {evidence.title}",
                f"Evidence type: {evidence.source_type}" if evidence.source_type else "",
                f"Evidence reliability: {evidence.reliability}" if evidence.reliability else "",
                evidence.summary,
            ]
            if part
        )
    return "\n".join(
        part
        for part in [
            f"Claim: {claim.text}",
            f"Detail: {claim.detail}" if claim.detail else "",
            "Evidence:",
            *evidence_parts,
        ]
        if part
    )


def embedding_input_text(text: str, *, role: str) -> str:
    if role == "document":
        return f"{EMBEDDING_DOCUMENT_PREFIX}{text}"
    if role == "query":
        return f"{EMBEDDING_QUERY_PREFIX}{text}"
    raise ValueError(f"unsupported embedding role: {role}")


def vector_text_hash(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def is_sha256_digest(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA256_PATTERN.match(value))


def embedding_surface_rows(parsed_packs: list[ParsedPack]) -> list[dict[str, Any]]:
    evidence_rows = [
        evidence
        for parsed_pack in parsed_packs
        for evidence in parsed_pack.evidence
    ]
    evidence_by_uid = {evidence.evidence_uid: evidence for evidence in evidence_rows}
    rows = []
    for claim in sorted(
        (claim for parsed_pack in parsed_packs for claim in parsed_pack.claims),
        key=lambda item: item.claim_uid,
    ):
        embedding_text = claim_embedding_text(claim, evidence_by_uid)
        source_text = embedding_input_text(embedding_text, role="document")
        rows.append(
            {
                "contract_version": VECTOR_CONTRACT_VERSION,
                "embedding_surface_version": EMBEDDING_SURFACE_VERSION,
                "embedding_prefix_scheme": EMBEDDING_PREFIX_SCHEME,
                "embedding_role": "document",
                "claim_uid": claim.claim_uid,
                "pack_id": claim.pack_id,
                "local_claim_id": claim.local_claim_id,
                "source_text_hash": vector_text_hash(source_text),
                "source_text": source_text,
                "embedding_text": embedding_text,
                "source_locator": claim.source_locator,
            }
        )
    return rows


def vector_meta_from_graph_meta(graph_meta: dict[str, str]) -> dict[str, Any]:
    if graph_meta.get("vector_search_available") != "true":
        return {
            "status": "surfaces-ready",
            "model_id": None,
            "model_fingerprint": None,
            "embedding_prefix_scheme": EMBEDDING_PREFIX_SCHEME,
            "dimensions": None,
            "distance": None,
            "normalized": None,
            "vector_index_engine": None,
            "vector_claim_count": 0,
            "vector_claim_coverage": graph_meta.get("vector_claim_coverage", "0/0"),
        }
    return {
        "status": "vectors-imported",
        "model_id": graph_meta.get("vector_model_id") or None,
        "model_fingerprint": graph_meta.get("vector_model_fingerprint") or None,
        "embedding_prefix_scheme": graph_meta.get("embedding_prefix_scheme") or None,
        "dimensions": int(graph_meta.get("vector_dimensions", "0")),
        "distance": graph_meta.get("vector_distance") or None,
        "normalized": graph_meta.get("vector_normalized") == "true",
        "vector_index_engine": graph_meta.get("vector_index_engine") or None,
        "vector_claim_count": int(graph_meta.get("vector_claim_count", "0")),
        "vector_claim_coverage": graph_meta.get("vector_claim_coverage", "0/0"),
        "sqlite_vec_version": graph_meta.get("vector_sqlite_vec_version") or None,
    }


def build_embedding_manifest(
    parsed_packs: list[ParsedPack],
    *,
    export_tier: str,
    projection_report: dict[str, Any],
    surface_rows: list[dict[str, Any]],
    graph_meta: dict[str, str] | None = None,
    sealed: bool = False,
) -> dict[str, Any]:
    claim_uids = sorted(row["claim_uid"] for row in surface_rows)
    return {
        "kind": "kp-embedding-manifest",
        "manifest_version": EMBEDDING_MANIFEST_VERSION,
        "schema_version": SCHEMA_VERSION,
        "compiler_version": COMPILER_VERSION,
        "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "source_hash": bundle_source_hash(parsed_packs),
        "export_tier": export_tier,
        "claim_count": len(surface_rows),
        "claim_uid_set_sha256": string_list_sha256(claim_uids),
        "claim_surfaces_sha256": jsonl_rows_sha256(surface_rows),
        "vector_contract_version": VECTOR_CONTRACT_VERSION,
        "embedding_surface_version": EMBEDDING_SURFACE_VERSION,
        "embedding_prefix_scheme": EMBEDDING_PREFIX_SCHEME,
        "embedding_surfaces_path": "claim-surfaces.jsonl",
        "projection": {
            "filtered_claims": projection_report["filtered_claims"],
            "filtered_evidence": projection_report["filtered_evidence"],
            "filtered_relations": projection_report["filtered_relations"],
            "require_explicit_boundary": bool(
                projection_report.get("require_explicit_boundary", False)
            ),
        },
        "embedding": vector_meta_from_graph_meta(graph_meta or {}),
        "bundle_sealed": sealed,
    }


def load_embedding_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"embedding manifest does not exist: {path}")
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"embedding manifest is not valid JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError("embedding manifest must be a JSON object")
    if raw.get("kind") != "kp-embedding-manifest":
        raise ValueError("embedding manifest has unsupported kind")
    return raw


def validate_embedding_manifest(
    manifest_path: Path,
    expected_manifest: dict[str, Any],
) -> dict[str, Any]:
    observed = load_embedding_manifest(manifest_path)
    keys = [
        "kind",
        "manifest_version",
        "schema_version",
        "compiler_version",
        "source_hash",
        "export_tier",
        "claim_count",
        "claim_uid_set_sha256",
        "claim_surfaces_sha256",
        "vector_contract_version",
        "embedding_surface_version",
        "embedding_prefix_scheme",
    ]
    for key in keys:
        if observed.get(key) != expected_manifest.get(key):
            raise ValueError(
                "embedding manifest mismatch for "
                f"{key}: {observed.get(key)!r} != {expected_manifest.get(key)!r}"
            )

    observed_projection = observed.get("projection")
    expected_projection = expected_manifest.get("projection")
    if observed_projection != expected_projection:
        raise ValueError(
            "embedding manifest mismatch for projection: "
            f"{observed_projection!r} != {expected_projection!r}"
        )
    return observed


def write_embedding_artifacts(
    output_dir: Path,
    manifest: dict[str, Any],
    surface_rows: list[dict[str, Any]],
) -> dict[str, str]:
    embeddings_dir = output_dir / "embeddings"
    surfaces_path = embeddings_dir / "claim-surfaces.jsonl"
    manifest_path = embeddings_dir / "embedding-manifest.json"
    write_jsonl(surfaces_path, surface_rows)
    write_json(manifest_path, manifest)
    return {
        "claim_surfaces": str(surfaces_path),
        "embedding_manifest": str(manifest_path),
    }


def write_graph_meta_values(db_path: Path, values: dict[str, str]) -> dict[str, str]:
    conn = sqlite3.connect(db_path)
    try:
        conn.executemany(
            "INSERT OR REPLACE INTO graph_meta (key, value) VALUES (?, ?)",
            sorted(values.items()),
        )
        conn.commit()
        return read_graph_meta(conn)
    finally:
        conn.close()


def build_bundle_seal(
    *,
    db_path: Path,
    vectors_jsonl: Path,
    embedding_manifest_path: Path,
    current_manifest: dict[str, Any],
    graph_meta: dict[str, str],
) -> dict[str, Any]:
    claim_count = current_manifest["claim_count"]
    expected_coverage = f"{claim_count}/{claim_count}"
    checks = {
        "embedding_manifest_matches_current_projection": True,
        "vectors_present": graph_meta.get("vector_search_available") == "true",
        "sqlite_vec_index_present": graph_meta.get("vector_index") == "sqlite-vec",
        "vector_coverage_complete": graph_meta.get("vector_claim_coverage") == expected_coverage,
        "no_ignored_vector_rows": graph_meta.get("vector_ignored_row_count") == "0",
    }
    if not all(checks.values()):
        failed = ", ".join(key for key, value in checks.items() if not value)
        raise ValueError(f"bundle seal failed checks: {failed}")
    return {
        "kind": "kp-bundle-seal",
        "seal_version": BUNDLE_SEAL_VERSION,
        "sealed": True,
        "sealed_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "db_path": str(db_path),
        "source_hash": current_manifest["source_hash"],
        "export_tier": current_manifest["export_tier"],
        "schema_version": SCHEMA_VERSION,
        "compiler_version": COMPILER_VERSION,
        "embedding_manifest_path": str(embedding_manifest_path),
        "embedding_manifest_sha256": file_sha256(embedding_manifest_path),
        "vectors_jsonl_path": str(vectors_jsonl),
        "vectors_jsonl_sha256": file_sha256(vectors_jsonl),
        "claim_surfaces_sha256": current_manifest["claim_surfaces_sha256"],
        "claim_count": claim_count,
        "vector_contract": vector_meta_from_graph_meta(graph_meta),
        "checks": checks,
    }


def normalize_vector_values(raw: Any, *, label: str) -> list[float]:
    if not isinstance(raw, list) or not raw:
        raise ValueError(f"{label} must be a non-empty JSON array")
    vector = []
    for index, value in enumerate(raw):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"{label}[{index}] must be numeric")
        float_value = float(value)
        if not math.isfinite(float_value):
            raise ValueError(f"{label}[{index}] must be finite")
        vector.append(float_value)
    if vector_norm(vector) == 0:
        raise ValueError(f"{label} must not be a zero vector")
    return vector


def vector_norm(vector: list[float]) -> float:
    return math.sqrt(math.fsum(value * value for value in vector))


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError(f"vector dimensions differ: {len(left)} != {len(right)}")
    left_norm = vector_norm(left)
    right_norm = vector_norm(right)
    if left_norm == 0 or right_norm == 0:
        raise ValueError("cannot compare zero vectors")
    return math.fsum(a * b for a, b in zip(left, right, strict=True)) / (left_norm * right_norm)


def parse_claim_vector_row(raw: dict[str, Any], *, line_number: int) -> ClaimVector:
    if not isinstance(raw, dict):
        raise ValueError(f"vector row {line_number} must be a JSON object")

    contract_version = raw.get("contract_version")
    if contract_version != VECTOR_CONTRACT_VERSION:
        raise ValueError(
            f"vector row {line_number} must use contract_version {VECTOR_CONTRACT_VERSION}"
        )
    surface_version = raw.get("embedding_surface_version")
    if surface_version != EMBEDDING_SURFACE_VERSION:
        raise ValueError(
            f"vector row {line_number} must use embedding_surface_version {EMBEDDING_SURFACE_VERSION}"
        )

    claim_uid_value = raw.get("claim_uid")
    model_id = raw.get("model_id")
    model_fingerprint = raw.get("model_fingerprint")
    embedding_prefix_scheme = raw.get("embedding_prefix_scheme")
    source_text_hash = raw.get("source_text_hash")
    if not isinstance(claim_uid_value, str) or not claim_uid_value:
        raise ValueError(f"vector row {line_number} must include claim_uid")
    if not isinstance(model_id, str) or not model_id:
        raise ValueError(f"vector row {line_number} must include model_id")
    if not is_sha256_digest(model_fingerprint):
        raise ValueError(f"vector row {line_number} must include model_fingerprint")
    if embedding_prefix_scheme != EMBEDDING_PREFIX_SCHEME:
        raise ValueError(
            f"vector row {line_number} must use embedding_prefix_scheme {EMBEDDING_PREFIX_SCHEME}"
        )
    if not is_sha256_digest(source_text_hash):
        raise ValueError(f"vector row {line_number} must include source_text_hash")

    vector = normalize_vector_values(
        raw.get("embedding", raw.get("vector")),
        label=f"vector row {line_number} embedding",
    )
    dimensions = raw.get("dimensions")
    if not isinstance(dimensions, int) or dimensions < 1:
        raise ValueError(f"vector row {line_number} must include positive integer dimensions")
    if dimensions != len(vector):
        raise ValueError(
            f"vector row {line_number} dimensions mismatch: metadata {dimensions}, vector {len(vector)}"
        )

    distance = raw.get("distance", "cosine")
    if distance != "cosine":
        raise ValueError(f"vector row {line_number} has unsupported distance: {distance}")

    normalized = raw.get("normalized", False)
    if not isinstance(normalized, bool):
        raise ValueError(f"vector row {line_number} normalized must be boolean")

    return ClaimVector(
        claim_uid=claim_uid_value,
        model_id=model_id,
        model_fingerprint=model_fingerprint,
        embedding_prefix_scheme=embedding_prefix_scheme,
        dimensions=dimensions,
        vector=vector,
        source_text_hash=source_text_hash,
        normalized=normalized,
        distance=distance,
    )


def load_claim_vectors(vectors_jsonl: Path) -> list[ClaimVector]:
    if not vectors_jsonl.exists():
        raise ValueError(f"claim vector file does not exist: {vectors_jsonl}")
    vectors: list[ClaimVector] = []
    for line_number, line in enumerate(vectors_jsonl.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"vector row {line_number} is not valid JSON: {exc}") from exc
        vectors.append(parse_claim_vector_row(raw, line_number=line_number))
    if not vectors:
        raise ValueError(f"claim vector file is empty: {vectors_jsonl}")
    return vectors


def query_vector_from_json(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("query vector must be a JSON object")
    contract_version = raw.get("contract_version")
    if contract_version != VECTOR_CONTRACT_VERSION:
        raise ValueError(f"query vector must use contract_version {VECTOR_CONTRACT_VERSION}")
    model_id = raw.get("model_id")
    if not isinstance(model_id, str) or not model_id:
        raise ValueError("query vector must include model_id")
    model_fingerprint = raw.get("model_fingerprint")
    if not is_sha256_digest(model_fingerprint):
        raise ValueError("query vector must include model_fingerprint")
    embedding_prefix_scheme = raw.get("embedding_prefix_scheme")
    if embedding_prefix_scheme != EMBEDDING_PREFIX_SCHEME:
        raise ValueError(
            f"query vector must use embedding_prefix_scheme {EMBEDDING_PREFIX_SCHEME}"
        )
    vector = normalize_vector_values(
        raw.get("embedding", raw.get("vector")),
        label="query vector embedding",
    )
    dimensions = raw.get("dimensions", len(vector))
    if not isinstance(dimensions, int) or dimensions != len(vector):
        raise ValueError("query vector dimensions must match embedding length")
    distance = raw.get("distance", "cosine")
    if distance != "cosine":
        raise ValueError(f"query vector has unsupported distance: {distance}")
    return {
        "contract_version": contract_version,
        "model_id": model_id,
        "model_fingerprint": model_fingerprint,
        "embedding_prefix_scheme": embedding_prefix_scheme,
        "dimensions": dimensions,
        "vector": vector,
        "distance": distance,
    }


def load_query_vector(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"query vector file does not exist: {path}")
    return query_vector_from_json(json.loads(path.read_text()))


def load_sqlite_vec(conn: sqlite3.Connection) -> str:
    try:
        return conn.execute("SELECT vec_version()").fetchone()[0]
    except sqlite3.Error:
        pass

    try:
        import sqlite_vec
    except ModuleNotFoundError as exc:
        raise ValueError(
            "sqlite-vec backend requested but the sqlite-vec package is not installed"
        ) from exc

    try:
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
    except AttributeError as exc:
        raise ValueError(
            "sqlite-vec backend requested but this Python SQLite build cannot load extensions"
        ) from exc
    except sqlite3.Error as exc:
        raise ValueError(f"failed to load sqlite-vec extension: {exc}") from exc
    finally:
        try:
            conn.enable_load_extension(False)
        except (AttributeError, sqlite3.Error):
            pass

    return conn.execute("SELECT vec_version()").fetchone()[0]


def serialize_float32_vector(vector: list[float]) -> bytes:
    try:
        import sqlite_vec
    except ModuleNotFoundError as exc:
        raise ValueError(
            "sqlite-vec backend requested but the sqlite-vec package is not installed"
        ) from exc
    return sqlite_vec.serialize_float32(vector)


def create_fts5_claim_search(conn: sqlite3.Connection, search_rows: list[tuple[str, str, str, str]]) -> bool:
    try:
        conn.execute(
            """
            CREATE VIRTUAL TABLE kp_claim_search_fts USING fts5(
              claim_uid UNINDEXED,
              pack_id UNINDEXED,
              local_claim_id UNINDEXED,
              search_text,
              tokenize = 'unicode61 remove_diacritics 2'
            )
            """
        )
        conn.executemany(
            """
            INSERT INTO kp_claim_search_fts (
              claim_uid, pack_id, local_claim_id, search_text
            ) VALUES (?, ?, ?, ?)
            """,
            search_rows,
        )
    except sqlite3.OperationalError:
        return False
    return True


def create_sqlite_vec_claim_index(conn: sqlite3.Connection, dimensions: int) -> str:
    sqlite_vec_version = load_sqlite_vec(conn)
    conn.execute(
        f"""
        CREATE VIRTUAL TABLE {VECTOR_INDEX_TABLE} USING vec0(
          vector_rowid integer primary key,
          embedding float[{dimensions}] distance_metric=cosine
        )
        """
    )
    conn.executescript(
        f"""
        CREATE TRIGGER kp_claim_vectors_ai
        AFTER INSERT ON kp_claim_vectors
        BEGIN
          INSERT INTO {VECTOR_INDEX_TABLE} (vector_rowid, embedding)
          VALUES (new.vector_rowid, new.vector_blob);
        END;

        CREATE TRIGGER kp_claim_vectors_ad
        AFTER DELETE ON kp_claim_vectors
        BEGIN
          DELETE FROM {VECTOR_INDEX_TABLE}
          WHERE vector_rowid = old.vector_rowid;
        END;

        CREATE TRIGGER kp_claim_vectors_au
        AFTER UPDATE OF vector_rowid, vector_blob ON kp_claim_vectors
        BEGIN
          DELETE FROM {VECTOR_INDEX_TABLE}
          WHERE vector_rowid = old.vector_rowid;
          INSERT INTO {VECTOR_INDEX_TABLE} (vector_rowid, embedding)
          VALUES (new.vector_rowid, new.vector_blob);
        END;
        """
    )
    return sqlite_vec_version


def compile_sqlite(
    parsed: ParsedPack | list[ParsedPack],
    db_path: Path,
    *,
    export_tier: str,
    projection_report: dict[str, Any],
    vectors_jsonl: Path | None = None,
    source_claim_uids: set[str] | None = None,
    allow_filtered_vector_rows: bool = True,
) -> None:
    parsed_packs = parsed if isinstance(parsed, list) else [parsed]
    parsed_packs = resolve_relations(parsed_packs)

    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(
            """
            PRAGMA foreign_keys = ON;
            PRAGMA user_version = 4;

            CREATE TABLE graph_meta (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL
            );

            CREATE TABLE kp_packs (
              pack_id TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              version TEXT NOT NULL,
              domain TEXT NOT NULL,
              sensitivity TEXT,
              visibility TEXT,
              source_hash TEXT NOT NULL
            );

            CREATE TABLE kp_claims (
              claim_uid TEXT PRIMARY KEY,
              pack_id TEXT NOT NULL,
              local_claim_id TEXT NOT NULL,
              text TEXT NOT NULL,
              detail TEXT NOT NULL DEFAULT '',
              confidence REAL,
              claim_type TEXT,
              since TEXT,
              depth TEXT,
              nature TEXT,
              status TEXT NOT NULL DEFAULT 'active',
              tier TEXT NOT NULL DEFAULT 'client',
              sensitivity TEXT NOT NULL DEFAULT 'public',
              visibility TEXT NOT NULL DEFAULT 'public',
              boundary_explicit INTEGER NOT NULL DEFAULT 0,
              source_locator TEXT NOT NULL,
              FOREIGN KEY (pack_id) REFERENCES kp_packs(pack_id)
            );

            CREATE TABLE kp_evidence (
              evidence_uid TEXT PRIMARY KEY,
              pack_id TEXT NOT NULL,
              local_evidence_id TEXT NOT NULL,
              title TEXT NOT NULL,
              source_type TEXT,
              source_uri TEXT,
              captured_at TEXT,
              reliability TEXT,
              credibility INTEGER,
              summary TEXT NOT NULL DEFAULT '',
              tier TEXT NOT NULL DEFAULT 'client',
              sensitivity TEXT NOT NULL DEFAULT 'public',
              visibility TEXT NOT NULL DEFAULT 'public',
              boundary_explicit INTEGER NOT NULL DEFAULT 0,
              source_locator TEXT NOT NULL,
              FOREIGN KEY (pack_id) REFERENCES kp_packs(pack_id)
            );

            CREATE TABLE kp_claim_evidence_links (
              claim_uid TEXT NOT NULL,
              evidence_uid TEXT NOT NULL,
              local_evidence_id TEXT NOT NULL,
              source_locator TEXT NOT NULL,
              PRIMARY KEY (claim_uid, evidence_uid),
              FOREIGN KEY (claim_uid) REFERENCES kp_claims(claim_uid),
              FOREIGN KEY (evidence_uid) REFERENCES kp_evidence(evidence_uid)
            );

            CREATE TABLE kp_claim_relations (
              relation_uid TEXT PRIMARY KEY,
              from_claim_uid TEXT NOT NULL,
              to_claim_uid TEXT,
              relation_type TEXT NOT NULL,
              target_ref TEXT NOT NULL,
              target_resolved INTEGER NOT NULL,
              source_locator TEXT NOT NULL,
              FOREIGN KEY (from_claim_uid) REFERENCES kp_claims(claim_uid),
              FOREIGN KEY (to_claim_uid) REFERENCES kp_claims(claim_uid)
            );

            CREATE TABLE kp_claim_search (
              claim_uid TEXT PRIMARY KEY,
              pack_id TEXT NOT NULL,
              local_claim_id TEXT NOT NULL,
              search_text TEXT NOT NULL,
              FOREIGN KEY (claim_uid) REFERENCES kp_claims(claim_uid)
            );

            CREATE TABLE kp_claim_vectors (
              vector_rowid INTEGER PRIMARY KEY,
              claim_uid TEXT NOT NULL UNIQUE,
              model_id TEXT NOT NULL,
              model_fingerprint TEXT NOT NULL,
              embedding_prefix_scheme TEXT NOT NULL,
              dimensions INTEGER NOT NULL,
              distance TEXT NOT NULL,
              normalized INTEGER NOT NULL DEFAULT 0,
              contract_version INTEGER NOT NULL,
              embedding_surface_version TEXT NOT NULL,
              source_text_hash TEXT NOT NULL,
              vector_blob BLOB NOT NULL,
              FOREIGN KEY (claim_uid) REFERENCES kp_claims(claim_uid)
            );

            CREATE INDEX idx_kp_claims_pack_local ON kp_claims(pack_id, local_claim_id);
            CREATE INDEX idx_kp_evidence_pack_local ON kp_evidence(pack_id, local_evidence_id);
            CREATE INDEX idx_kp_claim_evidence_evidence ON kp_claim_evidence_links(evidence_uid);
            CREATE INDEX idx_kp_relations_from ON kp_claim_relations(from_claim_uid);
            CREATE INDEX idx_kp_relations_to ON kp_claim_relations(to_claim_uid);
            CREATE INDEX idx_kp_relations_type ON kp_claim_relations(relation_type);
            CREATE INDEX idx_kp_claim_search_pack ON kp_claim_search(pack_id, local_claim_id);
            CREATE INDEX idx_kp_claim_vectors_claim_uid ON kp_claim_vectors(claim_uid);
            CREATE INDEX idx_kp_claim_vectors_model ON kp_claim_vectors(
              model_id, model_fingerprint, embedding_prefix_scheme, dimensions
            );
            """
        )
        unresolved_relation_count = sum(
            1
            for parsed_pack in parsed_packs
            for relation in parsed_pack.relations
            if not relation.target_resolved
        )
        graph_meta = {
            "schema_version": str(SCHEMA_VERSION),
            "compiler_version": COMPILER_VERSION,
            "built_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "source_hash": bundle_source_hash(parsed_packs),
            "export_tier": export_tier,
            "filtered_claim_count": str(projection_report["filtered_claims"]),
            "filtered_evidence_count": str(projection_report["filtered_evidence"]),
            "filtered_relation_count": str(projection_report["filtered_relations"]),
            "require_explicit_boundary": str(projection_report.get("require_explicit_boundary", False)).lower(),
            "unresolved_relation_count": str(unresolved_relation_count),
        }
        conn.executemany(
            "INSERT INTO graph_meta (key, value) VALUES (?, ?)",
            sorted(graph_meta.items()),
        )
        conn.executemany(
            """
            INSERT INTO kp_packs (
              pack_id, name, version, domain, sensitivity, visibility, source_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    parsed_pack.pack["name"],
                    parsed_pack.pack["name"],
                    str(parsed_pack.pack["version"]),
                    parsed_pack.pack["domain"],
                    parsed_pack.pack.get("sensitivity"),
                    parsed_pack.pack.get("visibility"),
                    parsed_pack.source_hash,
                )
                for parsed_pack in parsed_packs
            ],
        )
        claims = [claim for parsed_pack in parsed_packs for claim in parsed_pack.claims]
        evidence_rows = [
            evidence
            for parsed_pack in parsed_packs
            for evidence in parsed_pack.evidence
        ]
        evidence_by_uid = {evidence.evidence_uid: evidence for evidence in evidence_rows}
        relations = [
            relation
            for parsed_pack in parsed_packs
            for relation in parsed_pack.relations
        ]
        conn.executemany(
            """
            INSERT INTO kp_claims (
              claim_uid, pack_id, local_claim_id, text, detail, confidence, claim_type,
              since, depth, nature, status, tier, sensitivity, visibility, boundary_explicit,
              source_locator
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    claim.claim_uid,
                    claim.pack_id,
                    claim.local_claim_id,
                    claim.text,
                    claim.detail,
                    claim.confidence,
                    claim.claim_type,
                    claim.since,
                    claim.depth,
                    claim.nature,
                    claim.status,
                    claim.tier,
                    claim.sensitivity,
                    claim.visibility,
                    1 if claim.boundary_explicit else 0,
                    claim.source_locator,
                )
                for claim in claims
            ],
        )
        search_rows = [
            (
                claim.claim_uid,
                claim.pack_id,
                claim.local_claim_id,
                claim_search_text(claim, evidence_by_uid),
            )
            for claim in claims
        ]
        embedding_surface_by_claim_uid = {
            row["claim_uid"]: row
            for row in embedding_surface_rows(parsed_packs)
        }
        conn.executemany(
            """
            INSERT INTO kp_claim_search (
              claim_uid, pack_id, local_claim_id, search_text
            ) VALUES (?, ?, ?, ?)
            """,
            search_rows,
        )
        fts5_available = create_fts5_claim_search(conn, search_rows)
        conn.executemany(
            "INSERT OR REPLACE INTO graph_meta (key, value) VALUES (?, ?)",
            [
                ("search_engine", "fts5" if fts5_available else "unavailable"),
                ("search_fts5_available", str(fts5_available).lower()),
            ],
        )
        vector_meta = {
            "vector_index": "absent",
            "vector_index_engine": "",
            "vector_search_available": "false",
            "vector_contract_version": str(VECTOR_CONTRACT_VERSION),
            "embedding_surface_version": EMBEDDING_SURFACE_VERSION,
            "vector_claim_count": "0",
            "vector_claim_coverage": f"0/{len(claims)}",
            "vector_ignored_row_count": "0",
            "vector_model_id": "",
            "vector_model_fingerprint": "",
            "embedding_prefix_scheme": EMBEDDING_PREFIX_SCHEME,
            "vector_dimensions": "0",
            "vector_distance": "",
            "vector_normalized": "",
            "vector_sqlite_vec_version": "",
        }
        if vectors_jsonl is not None:
            raw_vectors = load_claim_vectors(vectors_jsonl)
            claim_uids = {claim.claim_uid for claim in claims}
            if not claim_uids:
                raise ValueError("claim vector import requested but the projected graph has no claims")
            known_claim_uids = source_claim_uids or claim_uids
            vectors_by_claim_uid: dict[str, ClaimVector] = {}
            ignored_rows = 0
            model_id: str | None = None
            model_fingerprint: str | None = None
            embedding_prefix_scheme: str | None = None
            dimensions: int | None = None
            normalized: bool | None = None
            distance: str | None = None

            for vector in raw_vectors:
                if vector.claim_uid not in known_claim_uids:
                    raise ValueError(f"unknown claim vector for {vector.claim_uid}")
                if vector.claim_uid not in claim_uids:
                    if not allow_filtered_vector_rows:
                        raise ValueError(
                            "sealed vector file contains a row outside the projected "
                            f"embedding manifest: {vector.claim_uid}"
                        )
                    ignored_rows += 1
                    continue
                if vector.claim_uid in vectors_by_claim_uid:
                    raise ValueError(f"duplicate claim vector for {vector.claim_uid}")
                expected_hash = embedding_surface_by_claim_uid[vector.claim_uid]["source_text_hash"]
                if vector.source_text_hash != expected_hash:
                    raise ValueError(
                        f"stale claim vector for {vector.claim_uid}: source_text_hash mismatch"
                    )
                if model_id is None:
                    model_id = vector.model_id
                    model_fingerprint = vector.model_fingerprint
                    embedding_prefix_scheme = vector.embedding_prefix_scheme
                    dimensions = vector.dimensions
                    normalized = vector.normalized
                    distance = vector.distance
                elif (
                    vector.model_id != model_id
                    or vector.model_fingerprint != model_fingerprint
                    or vector.embedding_prefix_scheme != embedding_prefix_scheme
                    or vector.dimensions != dimensions
                    or vector.normalized != normalized
                    or vector.distance != distance
                ):
                    raise ValueError("claim vector file contains mixed vector contracts")
                vectors_by_claim_uid[vector.claim_uid] = vector

            missing_claim_uids = sorted(claim_uids - set(vectors_by_claim_uid))
            if missing_claim_uids:
                examples = ", ".join(missing_claim_uids[:3])
                raise ValueError(
                    "claim vector coverage incomplete; missing "
                    f"{len(missing_claim_uids)} claim vectors"
                    + (f" (examples: {examples})" if examples else "")
                )

            if dimensions is None:
                raise ValueError("claim vector file contains no vectors for the projected graph")
            sqlite_vec_version = create_sqlite_vec_claim_index(conn, dimensions)
            ordered_vectors = sorted(vectors_by_claim_uid.values(), key=lambda item: item.claim_uid)
            vector_rows = []
            for vector_rowid, vector in enumerate(ordered_vectors, start=1):
                vector_blob = serialize_float32_vector(vector.vector)
                vector_rows.append(
                    (
                        vector_rowid,
                        vector.claim_uid,
                        vector.model_id,
                        vector.model_fingerprint,
                        vector.embedding_prefix_scheme,
                        vector.dimensions,
                        vector.distance,
                        1 if vector.normalized else 0,
                        VECTOR_CONTRACT_VERSION,
                        EMBEDDING_SURFACE_VERSION,
                        vector.source_text_hash,
                        vector_blob,
                    )
                )

            conn.executemany(
                """
                INSERT INTO kp_claim_vectors (
                  vector_rowid, claim_uid, model_id, model_fingerprint,
                  embedding_prefix_scheme, dimensions, distance, normalized,
                  contract_version, embedding_surface_version, source_text_hash, vector_blob
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                vector_rows,
            )
            vector_meta = {
                "vector_index": "sqlite-vec",
                "vector_index_engine": VECTOR_INDEX_ENGINE,
                "vector_search_available": "true",
                "vector_contract_version": str(VECTOR_CONTRACT_VERSION),
                "embedding_surface_version": EMBEDDING_SURFACE_VERSION,
                "vector_claim_count": str(len(vectors_by_claim_uid)),
                "vector_claim_coverage": f"{len(vectors_by_claim_uid)}/{len(claim_uids)}",
                "vector_ignored_row_count": str(ignored_rows),
                "vector_model_id": model_id or "",
                "vector_model_fingerprint": model_fingerprint or "",
                "embedding_prefix_scheme": embedding_prefix_scheme or "",
                "vector_dimensions": str(dimensions or 0),
                "vector_distance": distance or "",
                "vector_normalized": str(normalized).lower() if normalized is not None else "",
                "vector_sqlite_vec_version": sqlite_vec_version,
            }
        conn.executemany(
            "INSERT OR REPLACE INTO graph_meta (key, value) VALUES (?, ?)",
            sorted(vector_meta.items()),
        )
        conn.executemany(
            """
            INSERT INTO kp_evidence (
              evidence_uid, pack_id, local_evidence_id, title, source_type, source_uri,
              captured_at, reliability, credibility, summary, tier, sensitivity, visibility,
              boundary_explicit, source_locator
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    evidence.evidence_uid,
                    evidence.pack_id,
                    evidence.local_evidence_id,
                    evidence.title,
                    evidence.source_type,
                    evidence.source_uri,
                    evidence.captured_at,
                    evidence.reliability,
                    evidence.credibility,
                    evidence.summary,
                    evidence.tier,
                    evidence.sensitivity,
                    evidence.visibility,
                    1 if evidence.boundary_explicit else 0,
                    evidence.source_locator,
                )
                for evidence in evidence_rows
            ],
        )
        claim_evidence_links = []
        for claim in claims:
            for local_evidence_id in claim.evidence_ids:
                evidence = evidence_by_uid[evidence_uid(claim.pack_id, local_evidence_id)]
                claim_evidence_links.append(
                    (
                        claim.claim_uid,
                        evidence.evidence_uid,
                        local_evidence_id,
                        claim.source_locator,
                    )
                )
        conn.executemany(
            """
            INSERT INTO kp_claim_evidence_links (
              claim_uid, evidence_uid, local_evidence_id, source_locator
            ) VALUES (?, ?, ?, ?)
            """,
            claim_evidence_links,
        )
        conn.executemany(
            """
            INSERT INTO kp_claim_relations (
              relation_uid, from_claim_uid, to_claim_uid, relation_type,
              target_ref, target_resolved, source_locator
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    relation.relation_uid,
                    relation.from_claim_uid,
                    relation.to_claim_uid,
                    relation.relation_type,
                    relation.target_ref,
                    relation.target_resolved,
                    relation.source_locator,
                )
                for relation in relations
            ],
        )
        conn.commit()
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def read_graph_meta(conn: sqlite3.Connection) -> dict[str, str]:
    rows = conn.execute("SELECT key, value FROM graph_meta ORDER BY key").fetchall()
    return {row[0]: row[1] for row in rows}


def sqlite_table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE name = ? AND type IN ('table', 'view')",
        (table_name,),
    ).fetchone()
    return row is not None


def validate_projection(db_path: Path, export_tier: str) -> dict[str, Any]:
    policy = EXPORT_POLICIES[export_tier]
    conn = sqlite3.connect(db_path)
    try:
        graph_meta = read_graph_meta(conn)
        claim_count = conn.execute("SELECT count(*) FROM kp_claims").fetchone()[0]
        vector_count = conn.execute("SELECT count(*) FROM kp_claim_vectors").fetchone()[0]
        vector_index_expected = graph_meta.get("vector_index") == "sqlite-vec"
        if vector_index_expected:
            load_sqlite_vec(conn)
        vector_index_exists = sqlite_table_exists(conn, VECTOR_INDEX_TABLE)
        if vector_index_expected and vector_index_exists:
            vector_index_count = conn.execute(f"SELECT count(*) FROM {VECTOR_INDEX_TABLE}").fetchone()[0]
            dangling_vector_index_rows = conn.execute(
                f"""
                SELECT count(*)
                FROM {VECTOR_INDEX_TABLE} index_row
                LEFT JOIN kp_claim_vectors vector ON vector.vector_rowid = index_row.vector_rowid
                WHERE vector.vector_rowid IS NULL
                """
            ).fetchone()[0]
        else:
            vector_index_count = 0
            dangling_vector_index_rows = 0
        claim_policy_violations = conn.execute(
            f"""
            SELECT count(*)
            FROM kp_claims
            WHERE tier NOT IN ({",".join("?" for _ in policy["tiers"])})
               OR sensitivity NOT IN ({",".join("?" for _ in policy["sensitivities"])})
               OR visibility NOT IN ({",".join("?" for _ in policy["visibilities"])})
            """,
            [
                *sorted(policy["tiers"]),
                *sorted(policy["sensitivities"]),
                *sorted(policy["visibilities"]),
            ],
        ).fetchone()[0]
        evidence_policy_violations = conn.execute(
            f"""
            SELECT count(*)
            FROM kp_evidence
            WHERE tier NOT IN ({",".join("?" for _ in policy["tiers"])})
               OR sensitivity NOT IN ({",".join("?" for _ in policy["sensitivities"])})
               OR visibility NOT IN ({",".join("?" for _ in policy["visibilities"])})
            """,
            [
                *sorted(policy["tiers"]),
                *sorted(policy["sensitivities"]),
                *sorted(policy["visibilities"]),
            ],
        ).fetchone()[0]
        dangling_evidence_links = conn.execute(
            """
            SELECT count(*)
            FROM kp_claim_evidence_links link
            LEFT JOIN kp_claims claim ON claim.claim_uid = link.claim_uid
            LEFT JOIN kp_evidence evidence ON evidence.evidence_uid = link.evidence_uid
            WHERE claim.claim_uid IS NULL OR evidence.evidence_uid IS NULL
            """
        ).fetchone()[0]
        dangling_relations = conn.execute(
            """
            SELECT count(*)
            FROM kp_claim_relations relation
            LEFT JOIN kp_claims source_claim ON source_claim.claim_uid = relation.from_claim_uid
            LEFT JOIN kp_claims target_claim ON target_claim.claim_uid = relation.to_claim_uid
            WHERE source_claim.claim_uid IS NULL
               OR (relation.target_resolved = 1 AND target_claim.claim_uid IS NULL)
            """
        ).fetchone()[0]
        unresolved_relations = conn.execute(
            "SELECT count(*) FROM kp_claim_relations WHERE target_resolved = 0"
        ).fetchone()[0]
        dangling_search_rows = conn.execute(
            """
            SELECT count(*)
            FROM kp_claim_search search
            LEFT JOIN kp_claims claim ON claim.claim_uid = search.claim_uid
            WHERE claim.claim_uid IS NULL
            """
        ).fetchone()[0]
        dangling_vector_rows = conn.execute(
            """
            SELECT count(*)
            FROM kp_claim_vectors vector
            LEFT JOIN kp_claims claim ON claim.claim_uid = vector.claim_uid
            WHERE claim.claim_uid IS NULL
            """
        ).fetchone()[0]
        if sqlite_table_exists(conn, "kp_claim_search_fts"):
            dangling_fts_rows = conn.execute(
                """
                SELECT count(*)
                FROM kp_claim_search_fts search
                LEFT JOIN kp_claims claim ON claim.claim_uid = search.claim_uid
                WHERE claim.claim_uid IS NULL
                """
            ).fetchone()[0]
        else:
            dangling_fts_rows = 0
    finally:
        conn.close()

    blocked_unresolved_relations = (
        0 if policy["allow_unresolved_relations"] else unresolved_relations
    )
    checks = {
        "claim_policy_violations": claim_policy_violations,
        "evidence_policy_violations": evidence_policy_violations,
        "dangling_evidence_links": dangling_evidence_links,
        "dangling_relations": dangling_relations,
        "dangling_search_rows": dangling_search_rows,
        "dangling_vector_rows": dangling_vector_rows,
        "dangling_vector_index_rows": dangling_vector_index_rows,
        "dangling_fts_rows": dangling_fts_rows,
        "missing_vector_index": 1 if vector_index_expected and not vector_index_exists else 0,
        "incomplete_vector_coverage": (
            max(0, claim_count - vector_count)
            if vector_index_expected
            else 0
        ),
        "incomplete_vector_index_coverage": (
            max(0, claim_count - vector_index_count)
            if vector_index_expected
            else 0
        ),
        "blocked_unresolved_relations": blocked_unresolved_relations,
    }
    return {
        "valid": all(count == 0 for count in checks.values()),
        "checks": checks,
    }


def split_evidence_ids(raw: str) -> list[str]:
    return [part for part in raw.split(",") if part]


def approximate_tokens(text: str) -> int:
    return max(1, (len(text) + 3) // 4)


def claim_token_cost(claim: dict[str, Any]) -> int:
    return approximate_tokens(
        " ".join(
            str(claim.get(key, ""))
            for key in ("local_claim_id", "text", "detail", "claim_type", "depth", "nature", "status")
        )
    )


def search_terms(query: str) -> list[str]:
    terms = [
        term
        for term in re.findall(r"[a-z0-9]+", query.lower())
        if len(term) >= 2 and term not in SEARCH_STOPWORDS
    ]
    seen: set[str] = set()
    unique_terms = []
    for term in terms:
        if term in seen:
            continue
        seen.add(term)
        unique_terms.append(term)
    return unique_terms


def fts5_term_variants(term: str) -> list[str]:
    variants = [term]
    if term.endswith("ly") and len(term) > 5:
        variants.append(term[:-2])
    if term.endswith("ed") and len(term) > 4:
        variants.append(term[:-2])
    if term.endswith("ing") and len(term) > 5:
        variants.append(term[:-3])
    if term.endswith("s") and len(term) > 3:
        variants.append(term[:-1])
    seen: set[str] = set()
    result = []
    for variant in variants:
        if len(variant) < 2 or variant in seen:
            continue
        seen.add(variant)
        result.append(variant)
    return result


def fts5_match_query(query: str) -> str:
    terms: list[str] = []
    for term in search_terms(query):
        terms.extend(fts5_term_variants(term))
    seen: set[str] = set()
    unique_terms = []
    for term in terms:
        if term in seen:
            continue
        seen.add(term)
        unique_terms.append(term)
    return " OR ".join(f"{term}*" for term in unique_terms)


def normalized_search_text(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def lexical_score(query: str, text: str, confidence: float | None) -> tuple[float, list[str]]:
    terms = search_terms(query)
    if not terms:
        return 0.0, []
    normalized_query = normalized_search_text(query)
    normalized_text = normalized_search_text(text)
    matched_terms = [term for term in terms if term in normalized_text]
    if not matched_terms:
        return 0.0, []

    term_score = 0.0
    padded_text = f" {normalized_text} "
    for term in matched_terms:
        exact_count = padded_text.count(f" {term} ")
        partial_count = normalized_text.count(term)
        term_score += 3.0 + exact_count + max(0, partial_count - exact_count) * 0.25

    phrase_bonus = 8.0 if normalized_query and normalized_query in normalized_text else 0.0
    coverage_bonus = 4.0 * (len(matched_terms) / len(terms))
    confidence_bonus = confidence or 0.0
    return term_score + phrase_bonus + coverage_bonus + confidence_bonus, matched_terms


def structured_search_bonus(query: str, claim: dict[str, Any], search_text: str) -> float:
    normalized_query = normalized_search_text(query)
    normalized_text = normalized_search_text(search_text)
    bonus = 0.0

    if claim.get("status") == "superseded":
        bonus -= 3.0
    else:
        bonus += 0.4

    asks_current = any(term in normalized_query for term in ("current", "currently", "now", "best"))
    if asks_current and "current" in normalized_text:
        bonus += 2.5
    if asks_current and claim.get("status") == "active":
        bonus += 0.8

    asks_change = any(term in normalized_query for term in ("change", "changed", "why", "because"))
    change_terms = ("supersedes", "superseded", "rejecting", "unreliable", "forged", "invalidates")
    if asks_change and any(term in normalized_text for term in change_terms):
        bonus += 2.0

    asks_ownership = any(term in normalized_query for term in ("own", "owned", "owner", "ownership"))
    if asks_ownership and any(term in normalized_text for term in ("own", "owned", "owner", "ownership")):
        bonus += 1.0

    if claim.get("confidence") is not None:
        bonus += float(claim["confidence"]) * 0.2

    return bonus


def search_claims_lexical(
    conn: sqlite3.Connection,
    query: str,
    *,
    limit: int,
) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT claim.*, search.search_text
        FROM kp_claim_search search
        JOIN kp_claims claim ON claim.claim_uid = search.claim_uid
        ORDER BY claim.pack_id, claim.local_claim_id
        """
    ).fetchall()
    hits = []
    for row in rows:
        claim = row_to_dict(row)
        score, matched_terms = lexical_score(query, claim["search_text"], claim["confidence"])
        if score <= 0:
            continue
        score += structured_search_bonus(query, claim, claim["search_text"])
        claim.pop("search_text", None)
        hits.append(
            {
                **claim,
                "score": round(score, 4),
                "matched_terms": matched_terms,
                "search_engine": "lexical",
            }
        )
    return sorted(
        hits,
        key=lambda hit: (-hit["score"], -float(hit.get("confidence") or 0.0), hit["claim_uid"]),
    )[:limit]


def search_claims_fts5(
    conn: sqlite3.Connection,
    query: str,
    *,
    limit: int,
) -> list[dict[str, Any]]:
    match_query = fts5_match_query(query)
    if not match_query:
        return []
    rows = conn.execute(
        """
        SELECT claim.*, fts.search_text, bm25(kp_claim_search_fts, 2.0, 0.2, 2.0, 8.0) AS bm25_rank
        FROM kp_claim_search_fts AS fts
        JOIN kp_claims AS claim ON claim.claim_uid = fts.claim_uid
        WHERE kp_claim_search_fts MATCH ?
        ORDER BY bm25_rank ASC, claim.confidence DESC, claim.claim_uid ASC
        LIMIT ?
        """,
        (match_query, max(limit * 8, 20)),
    ).fetchall()
    hits = []
    for row in rows:
        claim = row_to_dict(row)
        bm25_rank = claim.pop("bm25_rank")
        search_text = claim.pop("search_text")
        _lexical_score, matched_terms = lexical_score(query, search_text, claim["confidence"])
        score = -float(bm25_rank) + structured_search_bonus(query, claim, search_text)
        hits.append(
            {
                **claim,
                "score": round(score, 6),
                "bm25_rank": round(float(bm25_rank), 6),
                "matched_terms": matched_terms,
                "search_engine": "fts5",
            }
        )
    return sorted(
        hits,
        key=lambda hit: (-hit["score"], hit["bm25_rank"], -float(hit.get("confidence") or 0.0), hit["claim_uid"]),
    )[:limit]


def vector_search_contract(conn: sqlite3.Connection) -> dict[str, Any]:
    if not sqlite_table_exists(conn, "kp_claim_vectors"):
        raise ValueError("vector search requested but the compiled graph has no claim vector index")
    claim_count = conn.execute("SELECT count(*) FROM kp_claims").fetchone()[0]
    vector_count = conn.execute("SELECT count(*) FROM kp_claim_vectors").fetchone()[0]
    if vector_count == 0:
        raise ValueError("vector search requested but the compiled graph has no claim vector index")
    if vector_count != claim_count:
        raise ValueError(
            f"vector search requested but vector coverage is incomplete: {vector_count}/{claim_count}"
        )
    sqlite_vec_version = load_sqlite_vec(conn)
    if not sqlite_table_exists(conn, VECTOR_INDEX_TABLE):
        raise ValueError("vector search requested but the compiled graph has no sqlite-vec index")
    vector_index_count = conn.execute(f"SELECT count(*) FROM {VECTOR_INDEX_TABLE}").fetchone()[0]
    if vector_index_count != claim_count:
        raise ValueError(
            "vector search requested but sqlite-vec index coverage is incomplete: "
            f"{vector_index_count}/{claim_count}"
        )
    rows = conn.execute(
        """
        SELECT model_id, model_fingerprint, embedding_prefix_scheme,
               dimensions, distance, normalized, contract_version,
               embedding_surface_version, count(*) AS count
        FROM kp_claim_vectors
        GROUP BY model_id, model_fingerprint, embedding_prefix_scheme,
                 dimensions, distance, normalized, contract_version,
                 embedding_surface_version
        """
    ).fetchall()
    if len(rows) != 1:
        raise ValueError("vector search requested but the claim vector contract is mixed")
    row = rows[0]
    if int(row["contract_version"]) != VECTOR_CONTRACT_VERSION:
        raise ValueError("vector search requested but the vector contract version is unsupported")
    if row["embedding_surface_version"] != EMBEDDING_SURFACE_VERSION:
        raise ValueError("vector search requested but the embedding surface version is unsupported")
    if row["embedding_prefix_scheme"] != EMBEDDING_PREFIX_SCHEME:
        raise ValueError("vector search requested but the embedding prefix scheme is unsupported")
    return {
        "model_id": row["model_id"],
        "model_fingerprint": row["model_fingerprint"],
        "embedding_prefix_scheme": row["embedding_prefix_scheme"],
        "dimensions": int(row["dimensions"]),
        "distance": row["distance"],
        "normalized": bool(row["normalized"]),
        "contract_version": int(row["contract_version"]),
        "embedding_surface_version": row["embedding_surface_version"],
        "claim_count": int(row["count"]),
        "sqlite_vec_version": sqlite_vec_version,
    }


def validate_query_vector(query_vector: dict[str, Any] | None, contract: dict[str, Any]) -> dict[str, Any]:
    if query_vector is None:
        raise ValueError("vector search requested but no query vector was provided")
    normalized_query_vector = query_vector_from_json(query_vector)
    if normalized_query_vector["model_id"] != contract["model_id"]:
        raise ValueError(
            "query vector model_id mismatch: "
            f"{normalized_query_vector['model_id']} != {contract['model_id']}"
        )
    if normalized_query_vector["model_fingerprint"] != contract["model_fingerprint"]:
        raise ValueError(
            "query vector model_fingerprint mismatch: "
            f"{normalized_query_vector['model_fingerprint']} != {contract['model_fingerprint']}"
        )
    if normalized_query_vector["embedding_prefix_scheme"] != contract["embedding_prefix_scheme"]:
        raise ValueError(
            "query vector embedding_prefix_scheme mismatch: "
            f"{normalized_query_vector['embedding_prefix_scheme']} != "
            f"{contract['embedding_prefix_scheme']}"
        )
    if normalized_query_vector["dimensions"] != contract["dimensions"]:
        raise ValueError(
            "query vector dimensions mismatch: "
            f"{normalized_query_vector['dimensions']} != {contract['dimensions']}"
        )
    if normalized_query_vector["distance"] != contract["distance"]:
        raise ValueError(
            "query vector distance mismatch: "
            f"{normalized_query_vector['distance']} != {contract['distance']}"
        )
    return normalized_query_vector


def search_claims_vector(
    conn: sqlite3.Connection,
    query: str,
    *,
    limit: int,
    query_vector: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    contract = vector_search_contract(conn)
    normalized_query_vector = validate_query_vector(query_vector, contract)
    query_blob = serialize_float32_vector(normalized_query_vector["vector"])
    candidate_limit = max(limit * 8, 20)
    rows = conn.execute(
        f"""
        SELECT claim.*, search.search_text, vec.distance AS vector_distance
        FROM {VECTOR_INDEX_TABLE} AS vec
        JOIN kp_claim_vectors vector ON vector.vector_rowid = vec.vector_rowid
        JOIN kp_claims claim ON claim.claim_uid = vector.claim_uid
        JOIN kp_claim_search search ON search.claim_uid = vector.claim_uid
        WHERE vec.embedding MATCH ?
          AND k = ?
        ORDER BY vec.distance ASC, claim.confidence DESC, claim.claim_uid ASC
        """
        ,
        (query_blob, candidate_limit),
    ).fetchall()
    hits = []
    for row in rows:
        claim = row_to_dict(row)
        search_text = claim.pop("search_text")
        vector_distance = float(claim.pop("vector_distance"))
        vector_similarity = 1.0 - vector_distance
        _lexical_score, matched_terms = lexical_score(query, search_text, claim["confidence"])
        structured_bonus = structured_search_bonus(query, claim, search_text)
        score = -vector_distance + (structured_bonus * 0.05)
        hits.append(
            {
                **claim,
                "score": round(score, 6),
                "matched_terms": matched_terms,
                "search_engine": "vector",
                "vector_distance": round(vector_distance, 6),
                "vector_similarity": round(vector_similarity, 6),
                "vector_model_id": contract["model_id"],
                "vector_model_fingerprint": contract["model_fingerprint"],
                "embedding_prefix_scheme": contract["embedding_prefix_scheme"],
                "vector_index_engine": VECTOR_INDEX_ENGINE,
            }
        )
    return sorted(
        hits,
        key=lambda hit: (
            -hit["score"],
            hit["vector_distance"],
            -float(hit.get("confidence") or 0.0),
            hit["claim_uid"],
        ),
    )[:limit]


def fetch_search_texts(conn: sqlite3.Connection, claim_uids: set[str]) -> dict[str, str]:
    if not claim_uids:
        return {}
    placeholders = ",".join("?" for _ in claim_uids)
    rows = conn.execute(
        f"SELECT claim_uid, search_text FROM kp_claim_search WHERE claim_uid IN ({placeholders})",
        sorted(claim_uids),
    ).fetchall()
    return {row["claim_uid"]: row["search_text"] for row in rows}


def search_claims_hybrid(
    conn: sqlite3.Connection,
    query: str,
    *,
    limit: int,
    query_vector: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if not sqlite_table_exists(conn, "kp_claim_search_fts"):
        raise ValueError("hybrid search requested but the compiled graph has no FTS5 index")

    candidate_limit = max(limit * 8, 20)
    fts_hits = search_claims_fts5(conn, query, limit=candidate_limit)
    vector_hits = search_claims_vector(
        conn,
        query,
        limit=candidate_limit,
        query_vector=query_vector,
    )
    combined: dict[str, dict[str, Any]] = {}

    for engine, hits in [("fts5", fts_hits), ("vector", vector_hits)]:
        for rank, hit in enumerate(hits, start=1):
            uid = hit["claim_uid"]
            combined_hit = combined.setdefault(
                uid,
                {
                    **{
                        key: value
                        for key, value in hit.items()
                        if key
                        not in {
                            "score",
                            "search_engine",
                            "bm25_rank",
                            "vector_distance",
                            "vector_similarity",
                            "vector_model_id",
                            "vector_model_fingerprint",
                            "embedding_prefix_scheme",
                            "vector_index_engine",
                        }
                    },
                    "_rrf_score": 0.0,
                    "component_ranks": {},
                    "component_scores": {},
                    "matched_terms": [],
                },
            )
            combined_hit["_rrf_score"] += 1.0 / (RRF_K + rank)
            combined_hit["component_ranks"][engine] = rank
            if engine == "fts5":
                combined_hit["component_scores"]["fts5_score"] = hit["score"]
                combined_hit["component_scores"]["bm25_rank"] = hit.get("bm25_rank")
            else:
                combined_hit["component_scores"]["vector_score"] = hit["score"]
                combined_hit["component_scores"]["vector_distance"] = hit.get("vector_distance")
                combined_hit["component_scores"]["vector_similarity"] = hit.get("vector_similarity")
                combined_hit["vector_distance"] = hit.get("vector_distance")
                combined_hit["vector_similarity"] = hit.get("vector_similarity")
                combined_hit["vector_model_id"] = hit.get("vector_model_id")
                combined_hit["vector_model_fingerprint"] = hit.get("vector_model_fingerprint")
                combined_hit["embedding_prefix_scheme"] = hit.get("embedding_prefix_scheme")
                combined_hit["vector_index_engine"] = hit.get("vector_index_engine")
            combined_hit["matched_terms"] = sorted(
                set(combined_hit["matched_terms"]) | set(hit.get("matched_terms", []))
            )

    search_texts = fetch_search_texts(conn, set(combined))
    for uid, hit in combined.items():
        search_text = search_texts.get(uid, "")
        structured_bonus = structured_search_bonus(query, hit, search_text)
        hit["_structured_bonus"] = structured_bonus
        hit["score"] = round(hit["_rrf_score"] + (structured_bonus * 0.001), 6)
        hit["search_engine"] = "hybrid"
        hit["component_scores"] = {
            key: value
            for key, value in sorted(hit["component_scores"].items())
            if value is not None
        }

    ranked_hits = sorted(
        combined.values(),
        key=lambda hit: (
            -hit["_rrf_score"],
            -hit["_structured_bonus"],
            -float(hit.get("confidence") or 0.0),
            hit["claim_uid"],
        ),
    )[:limit]
    for hit in ranked_hits:
        hit.pop("_rrf_score", None)
        hit.pop("_structured_bonus", None)
    return ranked_hits


def search_claims(
    db_path: Path,
    query: str,
    *,
    limit: int = DEFAULT_QUERY_LIMIT,
    mode: str = "fts5",
    query_vector: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if limit < 1:
        raise ValueError("search limit must be at least 1")
    if mode not in SEARCH_MODES:
        raise ValueError(f"unsupported search mode: {mode}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        fts5_ready = sqlite_table_exists(conn, "kp_claim_search_fts")
        if mode == "fts5":
            if not fts5_ready:
                raise ValueError("FTS5 search requested but the compiled graph has no FTS5 index")
            return search_claims_fts5(conn, query, limit=limit)
        if mode == "vector":
            return search_claims_vector(conn, query, limit=limit, query_vector=query_vector)
        if mode == "hybrid":
            return search_claims_hybrid(conn, query, limit=limit, query_vector=query_vector)
        return search_claims_lexical(conn, query, limit=limit)
    finally:
        conn.close()


def fetch_claims(conn: sqlite3.Connection, claim_uids: set[str]) -> dict[str, dict[str, Any]]:
    if not claim_uids:
        return {}
    placeholders = ",".join("?" for _ in claim_uids)
    rows = conn.execute(
        f"SELECT * FROM kp_claims WHERE claim_uid IN ({placeholders})",
        sorted(claim_uids),
    ).fetchall()
    return {row["claim_uid"]: row_to_dict(row) for row in rows}


def attach_evidence_lists(conn: sqlite3.Connection, claims: dict[str, dict[str, Any]]) -> None:
    if not claims:
        return
    placeholders = ",".join("?" for _ in claims)
    rows = conn.execute(
        f"""
        SELECT claim_uid, evidence_uid, local_evidence_id
        FROM kp_claim_evidence_links
        WHERE claim_uid IN ({placeholders})
        ORDER BY claim_uid, local_evidence_id
        """,
        sorted(claims),
    ).fetchall()
    evidence_by_claim: dict[str, list[str]] = {claim_uid: [] for claim_uid in claims}
    evidence_uids_by_claim: dict[str, list[str]] = {claim_uid: [] for claim_uid in claims}
    for row in rows:
        evidence_by_claim[row["claim_uid"]].append(row["local_evidence_id"])
        evidence_uids_by_claim[row["claim_uid"]].append(row["evidence_uid"])
    for claim_uid, claim in claims.items():
        claim["evidence"] = evidence_by_claim.get(claim_uid, [])
        claim["evidence_uids"] = evidence_uids_by_claim.get(claim_uid, [])


def relation_sort_key(relation: dict[str, Any]) -> tuple[int, str]:
    try:
        priority = EDGE_PRIORITY.index(relation["relation_type"])
    except ValueError:
        priority = len(EDGE_PRIORITY)
    return priority, relation["relation_uid"]


def reason_for_relation(relation_type: str, source_id: str, target_id: str) -> str:
    if relation_type == "supersedes":
        return f"{source_id} supersedes {target_id}, so the prior belief must remain visible."
    if relation_type == "requires":
        return f"{source_id} depends on {target_id} to explain the reasoning path."
    if relation_type == "contradicts:error":
        return f"{source_id} is a known-error contradiction for {target_id}."
    if relation_type == "contradicts:tension":
        return f"{source_id} remains in productive tension with {target_id}."
    if relation_type == "supports":
        return f"{source_id} supports {target_id}."
    return f"{source_id} relates to {target_id} through {relation_type}."


def retrieve_packet(
    db_path: Path,
    claim_id: str,
    *,
    max_nodes: int = 12,
    max_hops: int = 1,
    excluded_relation_uids: set[str] | None = None,
) -> dict[str, Any]:
    del max_hops  # v0 is exact-ID plus one bounded explanatory pass.
    excluded_relation_uids = excluded_relation_uids or set()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        if "#" in claim_id:
            matched_row = conn.execute(
                "SELECT * FROM kp_claims WHERE claim_uid = ?",
                (claim_id,),
            ).fetchone()
        else:
            matched_row = conn.execute(
                "SELECT * FROM kp_claims WHERE local_claim_id = ?",
                (claim_id,),
            ).fetchone()
        if matched_row is None:
            raise ValueError(f"claim not found: {claim_id}")

        matched = row_to_dict(matched_row)
        graph_meta = read_graph_meta(conn)
        export_tier = graph_meta.get("export_tier", "client")
        policy = EXPORT_POLICIES.get(export_tier, EXPORT_POLICIES["client"])

        nodes: dict[str, dict[str, Any]] = {matched["claim_uid"]: matched}
        included_by: dict[str, list[str]] = {}
        relation_reasons: dict[str, list[str]] = {}
        used_relations: list[dict[str, Any]] = []
        truncated = False
        token_budget_used = claim_token_cost(matched)

        outbound_rows = conn.execute(
            "SELECT * FROM kp_claim_relations WHERE from_claim_uid = ?",
            (matched["claim_uid"],),
        ).fetchall()
        outbound_relations = [
            row_to_dict(row)
            for row in outbound_rows
            if row["relation_uid"] not in excluded_relation_uids and row["to_claim_uid"]
        ]
        outbound_claims = fetch_claims(
            conn,
            {relation["to_claim_uid"] for relation in outbound_relations if relation["to_claim_uid"]},
        )
        for relation in sorted(outbound_relations, key=relation_sort_key):
            if len(nodes) >= max_nodes and relation["to_claim_uid"] not in nodes:
                truncated = True
                continue
            target = outbound_claims.get(relation["to_claim_uid"])
            if target is None:
                continue
            if relation["to_claim_uid"] not in nodes:
                projected_tokens = token_budget_used + claim_token_cost(target)
                if projected_tokens > 1800:
                    truncated = True
                    continue
                token_budget_used = projected_tokens
            nodes[target["claim_uid"]] = target
            included_by.setdefault(target["claim_uid"], []).append(relation["relation_type"])
            relation_reasons.setdefault(target["claim_uid"], []).append(
                reason_for_relation(
                    relation["relation_type"],
                    matched["local_claim_id"],
                    target["local_claim_id"],
                )
            )
            used_relations.append(relation)

        explanatory_relation_types = {"contradicts:error", "supports"}
        included_node_uids = {uid for uid in nodes if uid != matched["claim_uid"]}
        if included_node_uids:
            placeholders = ",".join("?" for _ in included_node_uids)
            inbound_rows = conn.execute(
                f"""
                SELECT * FROM kp_claim_relations
                WHERE to_claim_uid IN ({placeholders})
                  AND relation_type IN ('contradicts:error', 'supports')
                """,
                sorted(included_node_uids),
            ).fetchall()
            inbound_relations = [
                row_to_dict(row)
                for row in inbound_rows
                if row["relation_uid"] not in excluded_relation_uids
                and row["from_claim_uid"] != matched["claim_uid"]
                and row["relation_type"] in explanatory_relation_types
            ]
            inbound_claims = fetch_claims(
                conn,
                {relation["from_claim_uid"] for relation in inbound_relations},
            )
            for relation in sorted(inbound_relations, key=relation_sort_key):
                if len(nodes) >= max_nodes and relation["from_claim_uid"] not in nodes:
                    truncated = True
                    continue
                source = inbound_claims.get(relation["from_claim_uid"])
                if source is None:
                    continue
                if relation["from_claim_uid"] not in nodes:
                    projected_tokens = token_budget_used + claim_token_cost(source)
                    if projected_tokens > 1800:
                        truncated = True
                        continue
                    token_budget_used = projected_tokens
                nodes[source["claim_uid"]] = source
                included_by.setdefault(source["claim_uid"], []).append(relation["relation_type"])
                target = nodes[relation["to_claim_uid"]]
                relation_reasons.setdefault(source["claim_uid"], []).append(
                    reason_for_relation(
                        relation["relation_type"],
                        source["local_claim_id"],
                        target["local_claim_id"],
                    )
                )
                used_relations.append(relation)

        attach_evidence_lists(conn, nodes)
        evidence_uids = sorted(
            {
                evidence_uid
                for node in nodes.values()
                for evidence_uid in node.get("evidence_uids", [])
            }
        )
        evidence_rows = []
        for uid in evidence_uids:
            row = conn.execute(
                "SELECT * FROM kp_evidence WHERE evidence_uid = ?",
                (uid,),
            ).fetchone()
            if row is not None:
                evidence_rows.append(row_to_dict(row))

        neighbors = []
        for uid, node in sorted(nodes.items(), key=lambda item: item[1]["local_claim_id"]):
            if uid == matched["claim_uid"]:
                continue
            neighbors.append(
                {
                    **node,
                    "included_by": included_by.get(uid, []),
                    "reasons": relation_reasons.get(uid, []),
                }
            )

        return {
            "matched": matched,
            "neighbors": neighbors,
            "relations": sorted(used_relations, key=relation_sort_key),
            "evidence": evidence_rows,
            "bounds": {
                "max_hops": 1,
                "max_nodes": max_nodes,
                "max_tokens": 1800,
                "estimated_tokens": token_budget_used,
                "nodes_returned": len(nodes),
                "truncated": truncated,
            },
            "policy": {
                "export_tier": export_tier,
                "allowed_tiers": sorted(policy["tiers"]),
                "allowed_sensitivities": sorted(policy["sensitivities"]),
                "allowed_visibilities": sorted(policy["visibilities"]),
                "filtered_claim_count": int(graph_meta.get("filtered_claim_count", "0")),
                "filtered_evidence_count": int(graph_meta.get("filtered_evidence_count", "0")),
                "filtered_relation_count": int(graph_meta.get("filtered_relation_count", "0")),
                "edge_priority": EDGE_PRIORITY,
            },
        }
    finally:
        conn.close()


def evidence_by_id(packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    evidence: dict[str, dict[str, Any]] = {}
    for row in packet["evidence"]:
        evidence[row["evidence_uid"]] = row
        # Compatibility fallback only. Runtime claims should carry full evidence_uids.
        evidence.setdefault(row["local_evidence_id"], row)
    return evidence


def claim_evidence_ids(claim: dict[str, Any]) -> list[str]:
    return claim.get("evidence_uids") or claim.get("evidence", [])


def claim_by_id(packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    claims = {packet["matched"]["local_claim_id"]: packet["matched"]}
    for neighbor in packet["neighbors"]:
        claims[neighbor["local_claim_id"]] = neighbor
    return claims


def evidence_label(evidence: dict[str, Any] | None) -> str:
    if not evidence:
        return "unresolved evidence"
    return f"{evidence['local_evidence_id']} {evidence['title']}"


def render_dossier(packet: dict[str, Any], question: str) -> str:
    matched = packet["matched"]
    claims = claim_by_id(packet)
    evidence = evidence_by_id(packet)
    relations = packet["relations"]

    supersedes = [rel for rel in relations if rel["from_claim_uid"] == matched["claim_uid"] and rel["relation_type"] == "supersedes"]
    tensions = [rel for rel in relations if rel["relation_type"] == "contradicts:tension"]

    lines: list[str] = [
        f"# Dossier: {matched['local_claim_id']}",
        "",
        f"Question: {question}",
        "",
    ]

    if supersedes:
        lines.extend(
            [
                "## Current Best Reading",
                f"- {matched['text']}",
                f"- Confidence: {matched['confidence']:.2f}; type: {matched['claim_type']}; depth: {matched['depth']}; nature: {matched['nature']}.",
            ]
        )
        for evidence_id in claim_evidence_ids(matched):
            lines.append(f"- Basis: {evidence_label(evidence.get(evidence_id))}.")

        lines.extend(["", "## Prior / Superseded Belief"])
        for relation in supersedes:
            target = claims.get(relation["target_ref"])
            if not target:
                continue
            lines.append(f"- {target['text']}")
            for evidence_id in claim_evidence_ids(target):
                lines.append(f"- Prior basis: {evidence_label(evidence.get(evidence_id))}.")
            lines.append(f"- Status: superseded by {matched['local_claim_id']}, not equally live.")

        lines.extend(["", "## Why It Changed"])
        reason_claims = [
            neighbor
            for neighbor in packet["neighbors"]
            if "requires" in neighbor.get("included_by", [])
            or "contradicts:error" in neighbor.get("included_by", [])
        ]
        for reason_claim in reason_claims:
            lines.append(f"- {reason_claim['text']}")
            for evidence_id in claim_evidence_ids(reason_claim):
                lines.append(f"- Reason evidence: {evidence_label(evidence.get(evidence_id))}.")

        known_error_edges = [rel for rel in relations if rel["relation_type"] == "contradicts:error"]
        if known_error_edges:
            lines.append("- This is a known-error contradiction, not a live tie between alternatives.")

        lines.extend(
            [
                "",
                "## Do Not Flatten",
                "- Do not answer as if the superseded claim never appeared.",
                f"- Do not answer as if superseded claims and {matched['local_claim_id']} are equally live alternatives.",
                f"- State that {matched['local_claim_id']} is the current best reading and identify which prior claim it superseded.",
            ]
        )
    elif tensions:
        lines.extend(
            [
                "## Live Attribution Tension",
                "- This is a productive tension, not a settled attribution and not vague uncertainty.",
                f"- {matched['text']}",
            ]
        )
        for relation in tensions:
            other_id = relation["target_ref"]
            other = claims.get(other_id)
            if other:
                lines.append(f"- {other['text']}")
        lines.extend(["", "## Evidence Basis"])
        seen_evidence: set[str] = set()
        for node in [matched, *packet["neighbors"]]:
            for evidence_id in claim_evidence_ids(node):
                if evidence_id in seen_evidence:
                    continue
                seen_evidence.add(evidence_id)
                lines.append(f"- {evidence_label(evidence.get(evidence_id))}.")
        lines.extend(
            [
                "",
                "## Do Not Flatten",
                "- Do not choose one side as final unless a resolving or superseding claim exists.",
                "- Do not average the disagreement into vague uncertainty.",
                "- State that the disagreement is structured and still informative.",
            ]
        )
    else:
        lines.extend(
            [
                "## Matched Claim",
                f"- {matched['text']}",
                "",
                "## Do Not Flatten",
                "- Preserve confidence, evidence, and relation context from the packet.",
            ]
        )

    if packet["bounds"]["truncated"]:
        lines.extend(["", "## Bounds", "- The graph neighborhood was bounded and may omit lower-priority neighbors."])

    return "\n".join(lines).rstrip() + "\n"


def openai_request(dossier: str, question: str) -> dict[str, Any]:
    return {
        "model": "runtime-selected-model",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Use the dossier as structured knowledge. Preserve current-vs-prior belief, "
                    "known-error contradiction, productive tension, confidence, and evidence. "
                    "Do not collapse the dossier into a single unqualified fact when it records "
                    "supersession or tension."
                ),
            },
            {
                "role": "user",
                "content": f"{dossier}\nQuestion: {question}",
            },
        ],
        "temperature": 0.2,
        "max_tokens": 800,
    }


def ollama_prompt(dossier: str, question: str) -> str:
    return (
        "SYSTEM:\n"
        "Use the dossier as structured knowledge. Preserve current-vs-prior belief, "
        "known-error contradiction, productive tension, confidence, and evidence.\n\n"
        "DOSSIER:\n"
        f"{dossier}\n"
        f"USER QUESTION:\n{question}\n"
    )


def mcp_tool_response(dossier: str, packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool": "render_dossier",
        "content": [{"type": "text", "text": dossier}],
        "metadata": {
            "claim_uid": packet["matched"]["claim_uid"],
            "local_claim_id": packet["matched"]["local_claim_id"],
            "nodes_returned": packet["bounds"]["nodes_returned"],
            "truncated": packet["bounds"]["truncated"],
        },
    }


def write_runtime_artifacts(
    output_dir: Path,
    db_path: Path,
    claim_id: str,
    question: str,
    label: str,
) -> dict[str, str]:
    packet = retrieve_packet(db_path, claim_id)
    dossier = render_dossier(packet, question)
    retrieval_path = output_dir / "retrieval" / f"{label}.json"
    write_json(retrieval_path, packet)

    dossier_path = output_dir / "dossiers" / f"{label}.md"
    dossier_path.parent.mkdir(parents=True, exist_ok=True)
    dossier_path.write_text(dossier)

    openai_path = output_dir / "adapters" / "openai-compatible" / f"request-{label}.json"
    write_json(openai_path, openai_request(dossier, question))

    ollama_path = output_dir / "adapters" / "ollama" / f"prompt-{label}.txt"
    ollama_path.parent.mkdir(parents=True, exist_ok=True)
    ollama_path.write_text(ollama_prompt(dossier, question))

    mcp_path = output_dir / "adapters" / "mcp" / f"tool-response-{label}.json"
    write_json(mcp_path, mcp_tool_response(dossier, packet))

    return {
        "retrieval": str(retrieval_path),
        "dossier": str(dossier_path),
        "openai_request": str(openai_path),
        "ollama_prompt": str(ollama_path),
        "mcp_tool_response": str(mcp_path),
    }


def compile_bundle(
    pack_dir: Path | list[Path],
    output_dir: Path,
    *,
    export_tier: str = "client",
    require_explicit_boundary: bool = False,
    vectors_jsonl: Path | None = None,
    embedding_manifest: Path | None = None,
    seal_bundle: bool = False,
    query_claims: list[str] | None = None,
    query_texts: list[str] | None = None,
    query_vectors: list[dict[str, Any]] | None = None,
    query_limit: int = DEFAULT_QUERY_LIMIT,
    search_mode: str = "fts5",
    questions: dict[str, str] | None = None,
) -> dict[str, Any]:
    pack_dirs = pack_dir if isinstance(pack_dir, list) else [pack_dir]
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    source_packs = [parse_pack(path) for path in pack_dirs]
    source_claim_uids = {
        claim.claim_uid
        for parsed_pack in source_packs
        for claim in parsed_pack.claims
    }
    boundary_report = (
        validate_explicit_boundaries(source_packs)
        if require_explicit_boundary
        else {"required": False, "valid": True, "implicit_claims": None, "implicit_evidence": None}
    )
    parsed_packs, projection_report = project_for_export_tier(
        source_packs,
        export_tier,
    )
    projection_report["require_explicit_boundary"] = require_explicit_boundary
    if seal_bundle and vectors_jsonl is None:
        raise ValueError("bundle sealing requires --vectors-jsonl")
    if seal_bundle and embedding_manifest is None:
        raise ValueError("bundle sealing requires --embedding-manifest")
    surface_rows = embedding_surface_rows(parsed_packs)
    expected_input_manifest = build_embedding_manifest(
        parsed_packs,
        export_tier=export_tier,
        projection_report=projection_report,
        surface_rows=surface_rows,
    )
    validated_embedding_manifest = (
        validate_embedding_manifest(embedding_manifest, expected_input_manifest)
        if embedding_manifest is not None
        else None
    )
    db_path = output_dir / "indices" / "claim-graph.sqlite"
    compile_sqlite(
        parsed_packs,
        db_path,
        export_tier=export_tier,
        projection_report=projection_report,
        vectors_jsonl=vectors_jsonl,
        source_claim_uids=source_claim_uids,
        allow_filtered_vector_rows=not seal_bundle,
    )

    write_jsonl(
        output_dir / "logical" / "packs.jsonl",
        [
            {
                "pack_id": parsed_pack.pack["name"],
                "name": parsed_pack.pack["name"],
                "version": str(parsed_pack.pack["version"]),
                "domain": parsed_pack.pack["domain"],
                "sensitivity": parsed_pack.pack.get("sensitivity"),
                "visibility": parsed_pack.pack.get("visibility"),
                "source_hash": parsed_pack.source_hash,
            }
            for parsed_pack in parsed_packs
        ],
    )
    write_jsonl(
        output_dir / "logical" / "claims.jsonl",
        [claim for parsed_pack in parsed_packs for claim in parsed_pack.claims],
    )
    write_jsonl(
        output_dir / "logical" / "evidence.jsonl",
        [evidence for parsed_pack in parsed_packs for evidence in parsed_pack.evidence],
    )
    write_jsonl(
        output_dir / "logical" / "claim-relations.jsonl",
        [relation for parsed_pack in parsed_packs for relation in parsed_pack.relations],
    )

    query_claims = query_claims or []
    query_texts = query_texts or []
    query_vectors = query_vectors or []
    questions = questions or {}
    if query_texts and search_mode in VECTOR_SEARCH_MODES and len(query_vectors) != len(query_texts):
        raise ValueError(
            f"{search_mode} search requires one query vector per query text "
            f"({len(query_vectors)} vectors for {len(query_texts)} queries)"
        )
    if query_vectors and search_mode not in VECTOR_SEARCH_MODES:
        raise ValueError(f"query vectors were provided but {search_mode} search does not use vectors")
    for local_claim_id in query_claims:
        question = questions.get(local_claim_id, f"What should be known about {local_claim_id}?")
        label = artifact_label(local_claim_id)
        write_runtime_artifacts(output_dir, db_path, local_claim_id, question, label)

    search_reports: list[dict[str, Any]] = []
    for query_index, query_text in enumerate(query_texts, start=1):
        query_slug = slug_label(query_text)
        query_vector = (
            query_vectors[query_index - 1]
            if search_mode in VECTOR_SEARCH_MODES
            else None
        )
        hits = search_claims(
            db_path,
            query_text,
            limit=query_limit,
            mode=search_mode,
            query_vector=query_vector,
        )
        hit_reports = []
        for rank, hit in enumerate(hits, start=1):
            label = f"search-{query_index}-{query_slug}-r{rank}-{artifact_label(hit['claim_uid'])}"
            artifacts = write_runtime_artifacts(
                output_dir,
                db_path,
                hit["claim_uid"],
                query_text,
                label,
            )
            hit_reports.append(
                {
                    "rank": rank,
                    "claim_uid": hit["claim_uid"],
                    "local_claim_id": hit["local_claim_id"],
                    "score": hit["score"],
                    "search_engine": hit["search_engine"],
                    "matched_terms": hit["matched_terms"],
                    "artifacts": artifacts,
                }
                | {
                    key: hit[key]
                    for key in [
                        "bm25_rank",
                        "vector_distance",
                        "vector_similarity",
                        "vector_model_id",
                        "vector_model_fingerprint",
                        "embedding_prefix_scheme",
                        "vector_index_engine",
                        "component_ranks",
                        "component_scores",
                    ]
                    if key in hit
                }
            )
        search_report = {
            "query": query_text,
            "limit": query_limit,
            "search_mode": search_mode,
            "hits": hit_reports,
        }
        write_json(output_dir / "search" / f"{query_index}-{query_slug}.json", search_report)
        search_reports.append(search_report)

    conn = sqlite3.connect(db_path)
    try:
        evidence_link_count = conn.execute(
            "SELECT count(*) FROM kp_claim_evidence_links"
        ).fetchone()[0]
        graph_meta = read_graph_meta(conn)
    finally:
        conn.close()

    validation = validate_projection(db_path, export_tier)
    if not validation["valid"]:
        raise ValueError(f"{export_tier} projection failed validation: {validation['checks']}")
    output_embedding_manifest = build_embedding_manifest(
        parsed_packs,
        export_tier=export_tier,
        projection_report=projection_report,
        surface_rows=surface_rows,
        graph_meta=graph_meta,
        sealed=seal_bundle,
    )
    embedding_artifacts = write_embedding_artifacts(
        output_dir,
        output_embedding_manifest,
        surface_rows,
    )
    bundle_seal = None
    if seal_bundle:
        assert vectors_jsonl is not None
        assert embedding_manifest is not None
        bundle_seal = build_bundle_seal(
            db_path=db_path,
            vectors_jsonl=vectors_jsonl,
            embedding_manifest_path=embedding_manifest,
            current_manifest=expected_input_manifest,
            graph_meta=graph_meta,
        )
        bundle_seal_path = output_dir / "embeddings" / "bundle-seal.json"
        write_json(bundle_seal_path, bundle_seal)
        embedding_artifacts["bundle_seal"] = str(bundle_seal_path)
        graph_meta = write_graph_meta_values(
            db_path,
            {
                "bundle_sealed": "true",
                "bundle_seal_version": str(BUNDLE_SEAL_VERSION),
                "embedding_manifest_sha256": bundle_seal["embedding_manifest_sha256"],
                "claim_surfaces_sha256": bundle_seal["claim_surfaces_sha256"],
            },
        )
    else:
        graph_meta = write_graph_meta_values(
            db_path,
            {
                "bundle_sealed": "false",
                "claim_surfaces_sha256": expected_input_manifest["claim_surfaces_sha256"],
            },
        )
    summary = {
        "output_dir": str(output_dir),
        "db_path": str(db_path),
        "schema_version": SCHEMA_VERSION,
        "compiler_version": COMPILER_VERSION,
        "export_tier": export_tier,
        "packs": len(parsed_packs),
        "claims": sum(len(parsed_pack.claims) for parsed_pack in parsed_packs),
        "evidence": sum(len(parsed_pack.evidence) for parsed_pack in parsed_packs),
        "evidence_links": evidence_link_count,
        "relations": sum(len(parsed_pack.relations) for parsed_pack in parsed_packs),
        "unresolved_relations": sum(
            1
            for parsed_pack in parsed_packs
            for relation in parsed_pack.relations
            if not relation.target_resolved
        ),
        "graph_meta": graph_meta,
        "projection": projection_report,
        "boundary": boundary_report,
        "validation": validation,
        "embedding": {
            "artifacts": embedding_artifacts,
            "manifest": output_embedding_manifest,
            "validated_input_manifest": validated_embedding_manifest is not None,
            "sealed": bundle_seal is not None,
        },
        "bundle_seal": bundle_seal,
        "query_claims": query_claims,
        "query_texts": query_texts,
        "search_mode": search_mode,
        "search_reports": search_reports,
    }
    write_json(output_dir / "summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile a KP:1 pack into graph artifacts.")
    parser.add_argument(
        "pack_dirs",
        type=Path,
        nargs="+",
        help="Path to one or more .kpack directories.",
    )
    parser.add_argument("--output", type=Path, required=True, help="Output directory.")
    parser.add_argument(
        "--export-tier",
        choices=EXPORT_TIERS,
        default="client",
        help="Trust boundary to compile for. Defaults to the restrictive client projection.",
    )
    parser.add_argument(
        "--require-explicit-boundary",
        action="store_true",
        help="Refuse packs whose claims or evidence omit explicit compiler boundary metadata.",
    )
    parser.add_argument(
        "--vectors-jsonl",
        type=Path,
        help="Optional claim vector JSONL file to import as a derived vector index.",
    )
    parser.add_argument(
        "--embedding-manifest",
        type=Path,
        help=(
            "Optional embedding manifest to validate against the current projected "
            "claim surfaces. Required with --seal-bundle."
        ),
    )
    parser.add_argument(
        "--seal-bundle",
        action="store_true",
        help=(
            "Require vectors and an embedding manifest, then write a bundle seal "
            "only if every vector belongs to this exact projected bundle."
        ),
    )
    parser.add_argument(
        "--query-claim",
        action="append",
        default=[],
        help="Claim ID to retrieve and render after compilation. May be passed more than once.",
    )
    parser.add_argument(
        "--query-text",
        action="append",
        default=[],
        help="Text query to search, retrieve, and render after compilation. May be passed more than once.",
    )
    parser.add_argument(
        "--query-vector",
        type=Path,
        action="append",
        default=[],
        help=(
            "Path to a JSON query vector object for the corresponding --query-text. "
            "Required for vector and hybrid search."
        ),
    )
    parser.add_argument(
        "--query-limit",
        type=int,
        default=DEFAULT_QUERY_LIMIT,
        help=f"Maximum search hits to render for each text query. Defaults to {DEFAULT_QUERY_LIMIT}.",
    )
    parser.add_argument(
        "--search-mode",
        choices=SEARCH_MODES,
        default="fts5",
        help=(
            "Search engine for text queries. Defaults to fail-fast FTS5/BM25. "
            "Vector and hybrid require imported vectors plus matching query vectors. "
            "Use lexical only explicitly for tests or debugging."
        ),
    )
    args = parser.parse_args()
    query_vectors = [load_query_vector(path) for path in args.query_vector]

    summary = compile_bundle(
        args.pack_dirs,
        args.output,
        export_tier=args.export_tier,
        require_explicit_boundary=args.require_explicit_boundary,
        vectors_jsonl=args.vectors_jsonl,
        embedding_manifest=args.embedding_manifest,
        seal_bundle=args.seal_bundle,
        query_claims=args.query_claim,
        query_texts=args.query_text,
        query_vectors=query_vectors,
        query_limit=args.query_limit,
        search_mode=args.search_mode,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
