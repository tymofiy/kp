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
import re
import shutil
import sqlite3
from pathlib import Path
from typing import Any

import yaml


SCHEMA_VERSION = 1
COMPILER_VERSION = "0.2.0"

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


def claim_uid(pack_id: str, local_claim_id: str) -> str:
    return f"{pack_id}#{local_claim_id}"


def evidence_uid(pack_id: str, local_evidence_id: str) -> str:
    return f"{pack_id}#{local_evidence_id}"


def relation_uid(from_claim_uid: str, relation_type: str, target_ref: str) -> str:
    return f"{from_claim_uid}:{relation_type}:{target_ref}"


def artifact_label(claim_id: str) -> str:
    return claim_id.replace("#", "__").replace("/", "_")


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


def parse_claims(pack_id: str, claims_text: str) -> tuple[list[Claim], list[Relation]]:
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

        raw_claims.append(
            {
                "local_claim_id": local_id,
                "text": block["statement"],
                "detail": " ".join(part for part in detail_parts if part).strip(),
                "confidence": confidence,
                "claim_type": claim_type,
                "evidence_ids": evidence_ids,
                "since": since,
                "depth": depth,
                "nature": nature,
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
            tier="client",
            sensitivity="public",
            visibility="public",
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


def parse_evidence(pack_id: str, evidence_text: str) -> list[Evidence]:
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
                summary=" ".join(section["body"]).strip(),
                tier="client",
                sensitivity="public",
                visibility="public",
                source_locator=f"evidence.md:{section['line']}",
            )
        )

    return evidence


def parse_pack(pack_dir: Path) -> ParsedPack:
    pack = yaml.safe_load((pack_dir / "PACK.yaml").read_text())
    pack_id = pack["name"]
    claims, relations = parse_claims(pack_id, (pack_dir / "claims.md").read_text())
    evidence = parse_evidence(pack_id, (pack_dir / "evidence.md").read_text())
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


def compile_sqlite(parsed: ParsedPack | list[ParsedPack], db_path: Path) -> None:
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
            PRAGMA user_version = 1;

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

            CREATE INDEX idx_kp_claims_pack_local ON kp_claims(pack_id, local_claim_id);
            CREATE INDEX idx_kp_evidence_pack_local ON kp_evidence(pack_id, local_evidence_id);
            CREATE INDEX idx_kp_claim_evidence_evidence ON kp_claim_evidence_links(evidence_uid);
            CREATE INDEX idx_kp_relations_from ON kp_claim_relations(from_claim_uid);
            CREATE INDEX idx_kp_relations_to ON kp_claim_relations(to_claim_uid);
            CREATE INDEX idx_kp_relations_type ON kp_claim_relations(relation_type);
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
        relations = [
            relation
            for parsed_pack in parsed_packs
            for relation in parsed_pack.relations
        ]
        conn.executemany(
            """
            INSERT INTO kp_claims (
              claim_uid, pack_id, local_claim_id, text, detail, confidence, claim_type,
              since, depth, nature, status, tier, sensitivity, visibility, source_locator
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    claim.source_locator,
                )
                for claim in claims
            ],
        )
        conn.executemany(
            """
            INSERT INTO kp_evidence (
              evidence_uid, pack_id, local_evidence_id, title, source_type, source_uri,
              captured_at, reliability, credibility, summary, tier, sensitivity, visibility,
              source_locator
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    evidence.source_locator,
                )
                for evidence in evidence_rows
            ],
        )
        evidence_by_uid = {evidence.evidence_uid: evidence for evidence in evidence_rows}
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
        SELECT claim_uid, local_evidence_id
        FROM kp_claim_evidence_links
        WHERE claim_uid IN ({placeholders})
        ORDER BY claim_uid, local_evidence_id
        """,
        sorted(claims),
    ).fetchall()
    evidence_by_claim: dict[str, list[str]] = {claim_uid: [] for claim_uid in claims}
    for row in rows:
        evidence_by_claim[row["claim_uid"]].append(row["local_evidence_id"])
    for claim_uid, claim in claims.items():
        claim["evidence"] = evidence_by_claim.get(claim_uid, [])


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
        evidence_ids = sorted({evidence_id for node in nodes.values() for evidence_id in node["evidence"]})
        evidence_rows = []
        for local_evidence_id in evidence_ids:
            row = conn.execute(
                "SELECT * FROM kp_evidence WHERE local_evidence_id = ?",
                (local_evidence_id,),
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
                "tier": "client",
                "filtered_nodes": [],
                "filtered_edges": [],
                "edge_priority": EDGE_PRIORITY,
            },
        }
    finally:
        conn.close()


def evidence_by_id(packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["local_evidence_id"]: row for row in packet["evidence"]}


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
        for evidence_id in matched["evidence"]:
            lines.append(f"- Basis: {evidence_label(evidence.get(evidence_id))}.")

        lines.extend(["", "## Prior / Superseded Belief"])
        for relation in supersedes:
            target = claims.get(relation["target_ref"])
            if not target:
                continue
            lines.append(f"- {target['text']}")
            for evidence_id in target["evidence"]:
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
            for evidence_id in reason_claim["evidence"]:
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
            for evidence_id in node["evidence"]:
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


def compile_bundle(
    pack_dir: Path | list[Path],
    output_dir: Path,
    *,
    query_claims: list[str] | None = None,
    questions: dict[str, str] | None = None,
) -> dict[str, Any]:
    pack_dirs = pack_dir if isinstance(pack_dir, list) else [pack_dir]
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    parsed_packs = resolve_relations([parse_pack(path) for path in pack_dirs])
    db_path = output_dir / "indices" / "claim-graph.sqlite"
    compile_sqlite(parsed_packs, db_path)

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
    questions = questions or {}
    for local_claim_id in query_claims:
        question = questions.get(local_claim_id, f"What should be known about {local_claim_id}?")
        packet = retrieve_packet(db_path, local_claim_id)
        dossier = render_dossier(packet, question)
        label = artifact_label(local_claim_id)
        write_json(output_dir / "retrieval" / f"{label}.json", packet)
        dossier_path = output_dir / "dossiers" / f"{label}.md"
        dossier_path.parent.mkdir(parents=True, exist_ok=True)
        dossier_path.write_text(dossier)

        write_json(
            output_dir / "adapters" / "openai-compatible" / f"request-{label}.json",
            openai_request(dossier, question),
        )
        ollama_path = output_dir / "adapters" / "ollama" / f"prompt-{label}.txt"
        ollama_path.parent.mkdir(parents=True, exist_ok=True)
        ollama_path.write_text(ollama_prompt(dossier, question))
        write_json(
            output_dir / "adapters" / "mcp" / f"tool-response-{label}.json",
            mcp_tool_response(dossier, packet),
        )

    conn = sqlite3.connect(db_path)
    try:
        evidence_link_count = conn.execute(
            "SELECT count(*) FROM kp_claim_evidence_links"
        ).fetchone()[0]
        graph_meta_rows = conn.execute(
            "SELECT key, value FROM graph_meta ORDER BY key"
        ).fetchall()
        graph_meta = {key: value for key, value in graph_meta_rows}
    finally:
        conn.close()

    summary = {
        "output_dir": str(output_dir),
        "db_path": str(db_path),
        "schema_version": SCHEMA_VERSION,
        "compiler_version": COMPILER_VERSION,
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
        "query_claims": query_claims,
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
        "--query-claim",
        action="append",
        default=[],
        help="Claim ID to retrieve and render after compilation. May be passed more than once.",
    )
    args = parser.parse_args()

    summary = compile_bundle(args.pack_dirs, args.output, query_claims=args.query_claim)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
