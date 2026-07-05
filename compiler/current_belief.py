# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Timothy Kompanchenko
"""Current-belief view — a deterministic action view over supersession.

Profile extension contributed by Bernard, the first commercial implementer
(see GOVERNANCE.md; the spec's own stance on commercial actors applies —
this module adds a derived surface and changes no KP:1 semantics).

KP:1 deliberately records disagreement without resolving it (RATIONALE.md
P4: resolution is context-dependent), and the compiler's status column
already separates active from superseded claims. What neither defines is a
single deterministic answer to "what replaced this claim?" when
supersession fans in — two active claims both superseding one predecessor —
or "which arm currently leads?" on a live ``⊗~`` tension. Agents that must
act need one answer; this module derives it. The pack record — both arms,
full history, every tension — remains authoritative and untouched: the view
is derived output, rebuildable from the record at any time, and no
previously shipped surface (statuses, relations, hashes, orderings) moves.

Normative semantics, for any implementation reproducing this view:

* **The current set** is exactly the claims whose status is in the
  implementation's current-status set (kp_core: ``{"active"}``). The view
  never shrinks or reorders it — independent active claims coexist (P4),
  and refinement splits all stay current. Confidence is deliberately NOT a
  currency input: it governs how a claim is rendered, never whether it is
  current (a low-confidence newest correction still supersedes; render
  layers hedge it). Implementations with richer status vocabularies map
  their statuses into ``current`` / ``terminal-not-current`` sets; a chain
  whose every path ends terminal-not-current has an empty frontier there
  (impossible in kp_core, where a superseded claim always has a transitive
  active superseder on acyclic input).

* **The successor row**, per superseded claim C: ``frontier(C)`` is the set
  of current claims reachable by following superseder edges (a
  ``supersedes`` edge runs from the NEW claim to the OLD one; the walk runs
  old-to-new, passing through superseded intermediates; cycles are
  conformance errors upstream — SC-04 — and a visited-set keeps the walk
  total anyway). Cross-pack supersedes edges are excluded from currency,
  matching the status rule itself and the reconciliation stance: one pack
  never rewrites another's belief.

  - one head → the pointer.
  - several heads, every head carrying a ``belief.scope`` annotation and
    all scopes pairwise distinct → a refinement SPLIT: ``pointer`` stays
    null and ``split`` is true. The line's story is "refined into", never
    "changed to".
  - several heads otherwise → the ladder (below) picks the pointer and
    ``fan_in`` keeps the render honest: the losing heads remain fully
    current in the set; only the line's one-answer pointer chose.
  - no heads → possible only in a tier-filtered bundle whose superseder was
    withheld (statuses are computed before filtering): ``pointer`` null,
    ``unresolved_in_bundle`` true. This discloses nothing the shipped
    status column does not already disclose.

* **The contention rows**: a ``contradicts:tension`` edge between two
  current claims in the same pack yields a lean — the ladder's pick — so a
  render layer can say "both stand; currently leaning …". A tension with an
  inactive arm is dormant: no row. Cross-pack tensions are surfaced WITHOUT
  a lean (surface, never merge). ``contradicts`` and ``contradicts:error``
  between current claims are surfaced as unresolved contradictions with no
  lean: an error contradiction demands resolution by an author, and a
  deterministic pick would launder an error into an answer.

* **The ladder** — a total order over contenders (frontier heads or tension
  arms). Rung applicability is CONTEST-SCOPED: a profile rung applies only
  when every contender carries a valid input for it; otherwise the whole
  rung is skipped for that contest. (Pairwise skipping breaks transitivity,
  and an absent or unrecognized value must silence a rung — never rank
  below a present one.) Rungs, in order:

  1. authority — the ``belief.authority`` annotation, ranked
     ``explicit_user > observed > inference > third_party``;
  2. recency — ``since``, newer wins (ISO-8601 strings compare
     chronologically; a missing ``since`` orders oldest);
  3. evidence strength — count of evidence references, more wins;
  4. claim uid, ascending — smallest wins. Final ties break toward the
     ESTABLISHED claim (local ids are authorship-ordered by convention):
     a new claim can never steal a total tie by id assignment; it must win
     on a real rung.

  Scope deliberately does not rank mid-ladder: "more specific wins in its
  scope" binds at read time, where a query context exists to match. What a
  context-free materialization honors structurally is that scope-disjoint
  heads are not in contention at all (the split rule above). Every
  comparison here is string or integer — floats never enter the view.

Profile annotations ride the existing ``<!-- kp-compiler: … -->`` channel:
``belief.authority=<explicit_user|observed|inference|third_party>`` and
``belief.scope=<free-string>``. Unannotated packs get the identical view
with the profile rungs silent.

Determinism: rows emit uid-sorted (claim uid for belief rows, relation uid
for contention rows), all sets are canonicalized ascending before ranking,
and the emission inherits the bundle's ``sort_keys`` / LF JSONL discipline.
"""

from __future__ import annotations

import dataclasses
from typing import Any

CURRENT_STATUSES = frozenset({"active"})
SUPERSEDED_STATUS = "superseded"

AUTHORITY_KEY = "belief.authority"
SCOPE_KEY = "belief.scope"
AUTHORITY_RANK = {
    "explicit_user": 3,
    "observed": 2,
    "inference": 1,
    "third_party": 0,
}

SUPERSEDES_TYPE = "supersedes"
TENSION_TYPE = "contradicts:tension"
UNRESOLVED_TYPES = frozenset({"contradicts", "contradicts:error"})


@dataclasses.dataclass(frozen=True)
class CurrentBeliefRow:
    claim_uid: str
    pack_id: str
    status: str
    current: bool
    pointer: str | None
    frontier: list[str]
    fan_in: bool
    split: bool
    unresolved_in_bundle: bool


@dataclasses.dataclass(frozen=True)
class BeliefContentionRow:
    relation_uid: str
    kind: str  # "tension_lean" | "unresolved_contradiction"
    relation_type: str
    arms: list[str]
    lean: str | None
    cross_pack: bool


def _pack_of(uid: str) -> str:
    return uid.split("#", 1)[0]


def _ladder_pick(
    contenders: list[str],
    *,
    claims_by_uid: dict[str, Any],
    annotations: dict[str, dict[str, str]],
) -> str:
    """Rung-by-rung elimination over uid-sorted contenders (see module doc)."""
    standing = sorted(contenders)
    # Rung 1 — authority. Contest-scoped: every contender must carry a
    # RECOGNIZED vocabulary value, else the rung is silent for the contest.
    if len(standing) > 1:
        ranks = [
            AUTHORITY_RANK.get(annotations.get(uid, {}).get(AUTHORITY_KEY, ""))
            for uid in standing
        ]
        if all(rank is not None for rank in ranks):
            best = max(rank for rank in ranks if rank is not None)
            standing = [
                uid for uid, rank in zip(standing, ranks) if rank == best
            ]
    # Rung 2 — recency. The empty-string floor orders a missing `since`
    # oldest (record-completeness ordering, not a content judgment); when
    # every date ties — including all-missing — the rung eliminates nobody.
    if len(standing) > 1:
        dates = [claims_by_uid[uid].since or "" for uid in standing]
        best = max(dates)
        standing = [uid for uid, date in zip(standing, dates) if date == best]
    # Rung 3 — evidence strength (reference count; weights do not exist in
    # kp_core, and SC-03 makes references resolvable on conformant packs).
    if len(standing) > 1:
        counts = [len(claims_by_uid[uid].evidence_ids) for uid in standing]
        best = max(counts)
        standing = [
            uid for uid, count in zip(standing, counts) if count == best
        ]
    # Rung 4 — smallest uid wins the total tie.
    return standing[0]


def _frontier(
    uid: str,
    *,
    superseders: dict[str, list[str]],
    claims_by_uid: dict[str, Any],
    memo: dict[str, tuple[str, ...]],
    visiting: set[str],
) -> tuple[str, ...]:
    """Current claims reachable forward from ``uid`` along superseder edges.

    Cycles are conformance errors (SC-04) rejected upstream; the visiting
    guard keeps the walk total on malformed input without defining its
    semantics (a cycle contributes no heads).
    """
    if uid in memo:
        return memo[uid]
    if uid in visiting:
        return ()
    visiting.add(uid)
    heads: set[str] = set()
    for successor_uid in superseders.get(uid, ()):
        successor = claims_by_uid.get(successor_uid)
        if successor is None:
            continue
        if successor.status in CURRENT_STATUSES:
            heads.add(successor_uid)
        else:
            heads.update(
                _frontier(
                    successor_uid,
                    superseders=superseders,
                    claims_by_uid=claims_by_uid,
                    memo=memo,
                    visiting=visiting,
                )
            )
    visiting.discard(uid)
    result = tuple(sorted(heads))
    memo[uid] = result
    return result


def current_belief_rows(
    parsed_packs: list[Any],
) -> tuple[list[CurrentBeliefRow], list[BeliefContentionRow]]:
    """Compute the current-belief view over a bundle's (projected) packs.

    Operates on whatever claim set the caller passes — compile_bundle passes
    the post-export-tier packs so the view is consistent with the bundle it
    ships in (see ``unresolved_in_bundle`` in the module doc).
    """
    claims_by_uid: dict[str, Any] = {}
    annotations: dict[str, dict[str, str]] = {}
    for parsed in parsed_packs:
        for claim in parsed.claims:
            claims_by_uid[claim.claim_uid] = claim
        annotations.update(getattr(parsed, "profile_annotations", {}) or {})

    superseders: dict[str, list[str]] = {}
    tension_edges: list[tuple[Any, bool]] = []
    unresolved_edges: list[tuple[Any, bool]] = []
    for parsed in parsed_packs:
        for relation in parsed.relations:
            target_uid = relation.to_claim_uid
            if target_uid is None:
                continue
            if (
                relation.from_claim_uid not in claims_by_uid
                or target_uid not in claims_by_uid
                or relation.from_claim_uid == target_uid
            ):
                continue
            same_pack = _pack_of(relation.from_claim_uid) == _pack_of(target_uid)
            if relation.relation_type == SUPERSEDES_TYPE:
                # Cross-pack supersession never affects currency — the
                # status rule itself only honors local supersedes, and one
                # pack never rewrites another's belief.
                if same_pack:
                    superseders.setdefault(target_uid, []).append(
                        relation.from_claim_uid
                    )
                continue
            if relation.relation_type == TENSION_TYPE:
                tension_edges.append((relation, same_pack))
            elif relation.relation_type in UNRESOLVED_TYPES:
                unresolved_edges.append((relation, same_pack))

    for successor_uids in superseders.values():
        successor_uids.sort()

    memo: dict[str, tuple[str, ...]] = {}
    belief_rows: list[CurrentBeliefRow] = []
    for uid in sorted(claims_by_uid):
        claim = claims_by_uid[uid]
        current = claim.status in CURRENT_STATUSES
        pointer: str | None = None
        frontier: tuple[str, ...] = ()
        fan_in = False
        split = False
        unresolved_in_bundle = False
        if not current and claim.status == SUPERSEDED_STATUS:
            frontier = _frontier(
                uid,
                superseders=superseders,
                claims_by_uid=claims_by_uid,
                memo=memo,
                visiting=set(),
            )
            if not frontier:
                unresolved_in_bundle = True
            elif len(frontier) == 1:
                pointer = frontier[0]
            else:
                scopes = [
                    annotations.get(head, {}).get(SCOPE_KEY)
                    for head in frontier
                ]
                if all(scopes) and len(set(scopes)) == len(scopes):
                    split = True
                else:
                    fan_in = True
                    pointer = _ladder_pick(
                        list(frontier),
                        claims_by_uid=claims_by_uid,
                        annotations=annotations,
                    )
        belief_rows.append(
            CurrentBeliefRow(
                claim_uid=uid,
                pack_id=claim.pack_id,
                status=claim.status,
                current=current,
                pointer=pointer,
                frontier=list(frontier),
                fan_in=fan_in,
                split=split,
                unresolved_in_bundle=unresolved_in_bundle,
            )
        )

    contention_rows: list[BeliefContentionRow] = []
    for relation, same_pack in tension_edges:
        arm_a, arm_b = relation.from_claim_uid, relation.to_claim_uid
        if not (
            claims_by_uid[arm_a].status in CURRENT_STATUSES
            and claims_by_uid[arm_b].status in CURRENT_STATUSES
        ):
            continue  # dormant — an inactive arm ends the live tension
        arms = sorted([arm_a, arm_b])
        lean = (
            _ladder_pick(
                arms,
                claims_by_uid=claims_by_uid,
                annotations=annotations,
            )
            if same_pack
            else None
        )
        contention_rows.append(
            BeliefContentionRow(
                relation_uid=relation.relation_uid,
                kind="tension_lean",
                relation_type=relation.relation_type,
                arms=arms,
                lean=lean,
                cross_pack=not same_pack,
            )
        )
    for relation, same_pack in unresolved_edges:
        arm_a, arm_b = relation.from_claim_uid, relation.to_claim_uid
        if not (
            claims_by_uid[arm_a].status in CURRENT_STATUSES
            and claims_by_uid[arm_b].status in CURRENT_STATUSES
        ):
            continue
        contention_rows.append(
            BeliefContentionRow(
                relation_uid=relation.relation_uid,
                kind="unresolved_contradiction",
                relation_type=relation.relation_type,
                arms=sorted([arm_a, arm_b]),
                lean=None,
                cross_pack=not same_pack,
            )
        )

    contention_rows.sort(key=lambda row: row.relation_uid)
    return belief_rows, contention_rows
