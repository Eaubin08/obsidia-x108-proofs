"""H02 / D5-R4: a CoordinationRef can be explicitly selected as a meta-target.

"Marie dit que P et / ou que Q" keeps one REPORTS per member and its CoordinationRef.
Without a requested target the selector stays AMBIGUOUS (MULTIPLE_TARGETS_UNSUPPORTED):
the coordination never wins by itself. With requested_target=<coordination id> it
returns COORDINATION_TARGET (RESOLVED_EXPLICIT) whose identity is the existing
CoordinationRef id (target_coordination); target_predicate / target_event stay None, no
member is a representative, no EventReferenceRelation is invented. A requested member
resolves through the existing member mechanism; anything else stays unresolved
(requested_target_not_candidate), never a fallback. ReviewJoin keeps such a target.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_coreference import EventTargetReference, ResolutionStatus, TargetKind
from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.meta_event_relations import (MULTIPLE_TARGETS_UNSUPPORTED, extract_report_event_relations,
                                                       select_immediate_meta_target)
from app.semantic.lattice.review_join import _is_non_event_target

_REPORTS = frozenset({"REPORTS"})
AND = "Marie dit que Paul lance P et que Nadia exécute Q."
OR = "Marie dit que Paul lance P ou que Nadia exécute Q."


def _select(text, requested=None):
    f = parse_utterance(text)
    kw = {} if requested is None else {"requested_target": requested}
    return f, select_immediate_meta_target(f, "u1", _REPORTS, build_frame_event_index(f), **kw)


@pytest.mark.parametrize("text", [AND, OR])
def test_default_multi_target_stays_ambiguous(text):
    f, t = _select(text)
    assert (t.target_kind, t.resolution_status, t.provenance["reason"]) == \
        (TargetKind.UNKNOWN_TARGET, ResolutionStatus.AMBIGUOUS, MULTIPLE_TARGETS_UNSUPPORTED)
    assert t.target_coordination is None and t.target_predicate is None


@pytest.mark.parametrize("text,kind,construction", [(AND, "AND", "complement_conjunction"), (OR, "OR", "disjunction")])
def test_explicit_coordination_target(text, kind, construction):
    f, t = _select(text, "c1")
    assert (t.target_kind, t.resolution_status) == (TargetKind.COORDINATION_TARGET, ResolutionStatus.RESOLVED_EXPLICIT)
    assert (t.target_coordination, t.target_predicate, t.target_event) == ("c1", None, None)
    c = f.coordination(t.target_coordination)
    assert (c.kind, c.members, c.construction) == (kind, ("u2", "u3"), construction)
    assert (t.provenance["coordination_kind"], t.provenance["coordination_construction"]) == (kind, construction)
    assert t.to_dict()["target_coordination"] == "c1"
    # one object, many projections: REPORTS per member and the CoordinationRef are untouched
    assert {(r.kind, r.target) for r in f.relations if r.source == "u1"} == {("REPORTS", "u2"), ("REPORTS", "u3")}
    assert [(x.id, x.kind) for x in f.coordinations] == [("c1", kind)]


def test_explicit_member_target_uses_the_existing_member_mechanism():
    f, t = _select(AND, "u2")
    _, single = _select("Marie dit que Paul lance P.")
    assert (t.target_kind, t.target_predicate, t.target_coordination) == (TargetKind.EVENT_TARGET, "u2", None)
    assert t.target_event is not None and single.target_kind is TargetKind.EVENT_TARGET


@pytest.mark.parametrize("text,requested", [(AND, "c9"), (AND, "u1"), (AND, "zz"), ("Marie dit que Paul lance P.", "c1")])
def test_invalid_requested_target_never_falls_back(text, requested):
    _, t = _select(text, requested)
    assert (t.target_kind, t.resolution_status, t.provenance["reason"]) == \
        (TargetKind.UNKNOWN_TARGET, ResolutionStatus.UNRESOLVED, "requested_target_not_candidate")
    assert t.target_predicate is None and t.target_coordination is None


def test_unrelated_coordination_is_not_a_candidate():
    f, t = _select("Si Paul lance P et Nadia exécute Q, Marie dit que Luc lance R.")
    src = next(u.id for u in f.units if u.lemma == "dire")
    assert f.coordinations and f.coordinations[0].id == "c1"
    t = select_immediate_meta_target(f, src, _REPORTS, build_frame_event_index(f), requested_target="c1")
    assert t.resolution_status is ResolutionStatus.UNRESOLVED and t.target_coordination is None


def test_single_target_unchanged():
    _, t = _select("Marie dit que Paul lance P.")
    assert (t.target_kind, t.resolution_status, t.target_predicate) == \
        (TargetKind.EVENT_TARGET, ResolutionStatus.RESOLVED_STRUCTURAL, "u2")


def test_no_event_relation_for_the_coordination():
    f = parse_utterance(AND)
    result = extract_report_event_relations(f, build_frame_event_index(f))
    assert result.relations == () and all(t.target_kind is TargetKind.UNKNOWN_TARGET for t in result.targets)


def _ref(**kw):
    base = dict(source_event="e1", source_predicate="u1", resolution_status=ResolutionStatus.RESOLVED_EXPLICIT)
    base.update(kw)
    return EventTargetReference(**base)


@pytest.mark.parametrize("kw", [
    {"target_kind": TargetKind.COORDINATION_TARGET},
    {"target_kind": TargetKind.COORDINATION_TARGET, "target_coordination": "c1", "target_predicate": "u2"},
    {"target_kind": TargetKind.COORDINATION_TARGET, "target_coordination": "c1", "target_event": "e2"},
    {"target_kind": TargetKind.EVENT_TARGET, "target_predicate": "u2", "target_event": "e2", "target_coordination": "c1"},
    {"target_kind": TargetKind.PROPOSITION_TARGET, "target_predicate": "u2", "target_coordination": "c1"},
    {"target_kind": TargetKind.ENTITY_TARGET, "target_coordination": "c1"},
    {"target_kind": TargetKind.UNKNOWN_TARGET, "target_coordination": "c1",
     "resolution_status": ResolutionStatus.AMBIGUOUS},
])
def test_invalid_shapes_rejected(kw):
    with pytest.raises(ValueError):
        _ref(**kw)


def test_valid_coordination_shape_and_review_join_keeps_it():
    t = _ref(target_kind=TargetKind.COORDINATION_TARGET, target_coordination="c1")
    assert _is_non_event_target(t)
    assert not _is_non_event_target(_ref(target_kind=TargetKind.UNKNOWN_TARGET, resolution_status=ResolutionStatus.AMBIGUOUS))
