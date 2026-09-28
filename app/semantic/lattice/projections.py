"""Projections of one cognitive object and typed connection queries.

A PredicateUnit is a single object; each ProjectionAxis is a computed VIEW
of it (never a copy, so projections cannot drift apart). connection()
answers how two units are related — including "no proven connection",
which is a result, not an error. Bounded, deterministic, read-only.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum

from app.semantic.lattice.primitives import (
    EMBEDDING_KINDS, PROVENANCE_KINDS, TEMPORAL_KINDS, ConnectionKind,
    PredicateUnit, RelationKind, UtteranceFrame,
)

MAX_PATH = 6


class ProjectionAxis(str, Enum):
    GRAMMATICAL = "GRAMMATICAL"
    SEMANTIC = "SEMANTIC"
    TEMPORAL = "TEMPORAL"
    CAUSAL = "CAUSAL"
    EPISTEMIC = "EPISTEMIC"
    PRAGMATIC = "PRAGMATIC"
    PROVENANCE = "PROVENANCE"
    WORLD = "WORLD"
    AUTHORITY = "AUTHORITY"
    CONFIDENCE = "CONFIDENCE"


_CAUSAL = {RelationKind.CAUSES.value, RelationKind.CONDITIONS.value,
           RelationKind.FORBIDS.value, RelationKind.PREVENTS.value}


def _view(frame: UtteranceFrame, u: PredicateUnit, axis: ProjectionAxis) -> dict:
    if axis is ProjectionAxis.GRAMMATICAL:
        return {"verb_form": u.verb_form, "surface": u.surface, "negator": u.negator,
                "ne_expletive": u.ne_expletive, "ne_omitted": u.ne_omitted,
                "restriction": u.restriction, "clause": u.clause}
    if axis is ProjectionAxis.SEMANTIC:
        return {"predicate": u.predicate, "lemma": u.lemma, "class": u.predicate_class,
                "polarity": u.polarity, "subject": u.subject,
                "action_agent": u.action_agent, "role": u.role,
                "objects": [a.head for a in u.objects], "modality": u.modality}
    if axis is ProjectionAxis.TEMPORAL:
        order = [r.target for r in frame.relations
                 if r.kind in {k.value for k in TEMPORAL_KINDS} and r.source == u.id]
        return {"tense_aspect": u.tense_aspect, "realized": u.realized,
                "precedes": order, "deixis": list(frame.deixis)}
    if axis is ProjectionAxis.CAUSAL:
        return {"causes": [r.target for r in frame.relations if r.kind in _CAUSAL and r.source == u.id],
                "caused_by": [r.source for r in frame.relations if r.kind in _CAUSAL and r.target == u.id]}
    if axis is ProjectionAxis.EPISTEMIC:
        return {"epistemic": u.epistemic, "embedded_under": u.embedded_under}
    if axis is ProjectionAxis.PRAGMATIC:
        return {"pragmatic": u.pragmatic, "request_target": u.request_target,
                "role": u.role, "politeness": u.politeness}
    if axis is ProjectionAxis.PROVENANCE:
        return {"span": u.span, "raw_surface": frame.raw[u.span[0]:u.span[1]],
                "parser": u.provenance,
                "reported_by": [r.source for r in frame.relations
                                if r.kind in {k.value for k in PROVENANCE_KINDS} and r.target == u.id]}
    if axis is ProjectionAxis.WORLD:
        needs = [e for e in frame.evidence_needs if f"{u.predicate}" in e]
        return {"evidence_needs": needs, "world_action_mentioned": u.predicate_class == "world_action"}
    if axis is ProjectionAxis.AUTHORITY:
        requested = (u.predicate_class == "world_action" and u.polarity == "positive"
                     and u.pragmatic in {"REQUESTED", "INDIRECT_REQUEST"}
                     and u.role in {"REQUEST", "AMBIGUOUS_REQUEST"}
                     and u.request_target in {"ADDRESSEE", "ADDRESSEE_OR_POSSIBLE_ADDRESSEE"})
        return {"authority": None, "decision_authority": "KX108_ONLY", "emits_act": False,
                "requires_gate": requested}
    return {"confidence": u.confidence,
            "ambiguities": [a for a in frame.ambiguities if a.endswith(u.id)]}


def project(frame: UtteranceFrame, axis: ProjectionAxis) -> dict[str, dict]:
    """Return {unit_id: view} for one axis."""
    return {u.id: _view(frame, u, axis) for u in frame.units}


def projections_of(frame: UtteranceFrame, unit_id: str) -> dict[str, dict]:
    """All positions of one object across every axis."""
    u = frame.unit(unit_id)
    return {axis.value: _view(frame, u, axis) for axis in ProjectionAxis}


@dataclass(frozen=True)
class Connection:
    kind: ConnectionKind
    path: tuple[str, ...] = ()
    relation_kinds: tuple[str, ...] = ()


def connection(frame: UtteranceFrame, a: str, b: str) -> Connection:
    rels = frame.relations
    direct = [r for r in rels if {r.source, r.target} == {a, b}]
    if direct:
        kinds = tuple(sorted({r.kind for r in direct}))
        if all(k in {x.value for x in TEMPORAL_KINDS} for k in kinds):
            return Connection(ConnectionKind.TEMPORAL_RELATION, (a, b), kinds)
        if all(k in {x.value for x in PROVENANCE_KINDS} for k in kinds):
            return Connection(ConnectionKind.PROVENANCE_RELATION, (a, b), kinds)
        return Connection(ConnectionKind.DIRECT_RELATION, (a, b), kinds)

    causes_a = {r.source for r in rels if r.kind == RelationKind.CAUSES.value and r.target == a}
    causes_b = {r.source for r in rels if r.kind == RelationKind.CAUSES.value and r.target == b}
    shared = sorted(causes_a & causes_b)
    if shared:
        return Connection(ConnectionKind.SHARED_CAUSE, (a, shared[0], b), ("CAUSES", "CAUSES"))

    emb = {k.value for k in EMBEDDING_KINDS}
    parents_a = {r.source for r in rels if r.kind in emb and r.target == a}
    parents_b = {r.source for r in rels if r.kind in emb and r.target == b}
    common = sorted(parents_a & parents_b)
    if common:
        return Connection(ConnectionKind.SHARED_ANCESTOR, (a, common[0], b))

    # bounded BFS over the undirected relation graph
    adj: dict[str, list[tuple[str, str]]] = {}
    for r in rels:
        adj.setdefault(r.source, []).append((r.target, r.kind))
        adj.setdefault(r.target, []).append((r.source, r.kind))
    seen = {a: (None, None)}
    q = deque([(a, 0)])
    while q:
        node, depth = q.popleft()
        if node == b:
            break
        if depth >= MAX_PATH:
            continue
        for nb, kind in adj.get(node, []):
            if nb not in seen:
                seen[nb] = (node, kind)
                q.append((nb, depth + 1))
    if b in seen:
        path, kinds, cur = [b], [], b
        while seen[cur][0] is not None:
            kinds.append(seen[cur][1])
            cur = seen[cur][0]
            path.append(cur)
        return Connection(ConnectionKind.INDIRECT_PATH, tuple(reversed(path)), tuple(reversed(kinds)))

    ua, ub = frame.unit(a), frame.unit(b)
    if ua.predicate == ub.predicate:
        return Connection(ConnectionKind.SEMANTIC_SIMILARITY, (a, b))
    return Connection(ConnectionKind.NO_PROVEN_CONNECTION)
