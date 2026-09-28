"""ReviewJoin membership: only the four perspective relation kinds expand a
component; exact duplicate relations collapse; distinct perspectives survive.

Membership != visibility: a non-perspective relation (e.g. ABOUT) never pulls a
new event in, but stays visible when both endpoints are already members.
ALLOWED_RELATION_KIND != RELATION_SEMANTICALLY_CORRECT: a well-typed but wrong
relation passed in is trusted here; that guarantee belongs upstream (target
selection / index invariants).
"""
from __future__ import annotations

from dataclasses import replace
from itertools import product

import pytest

from app.semantic.lattice import review_join as RJ
from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.events import EventReferenceRelation, EventRelationKind
from app.semantic.lattice.french_grammar import parse_utterance

TWO_CLUSTERS = "Paul croit que Marie a lancé le test. Luc dit que Tom a lancé le build."
PERSPECTIVE = {EventRelationKind.OBSERVES, EventRelationKind.LEARNS_ABOUT,
               EventRelationKind.REPORTS_ABOUT, EventRelationKind.BELIEVES_ABOUT}


def _inject(monkeypatch, extra_builder):
    original = RJ.extract_nominal_reference_relations

    class _Result:
        def __init__(self, result, extra):
            self.relations = tuple(result.relations) + tuple(extra)
            self.targets = result.targets
            self.metadata = result.metadata

    monkeypatch.setattr(RJ, "extract_nominal_reference_relations",
                        lambda frame, index, **kw: _Result(original(frame, index, **kw), extra_builder(frame, index)))


def _setup(text=TWO_CLUSTERS):
    frame = parse_utterance(text)
    index = build_frame_event_index(frame)
    return frame, index, (lambda p: index.event_for(p).event_ref.event_id)


def _members(frame, index, center):
    return {e["predicate_ref"] for e in RJ.build_review_envelope(frame, center, index).events}


def test_membership_whitelist_is_exactly_the_four_perspective_kinds():
    assert RJ.REVIEW_MEMBERSHIP_RELATION_KINDS == frozenset(PERSPECTIVE)
    assert EventRelationKind.ABOUT not in RJ.REVIEW_MEMBERSHIP_RELATION_KINDS


def test_about_bridge_does_not_join_components(monkeypatch):
    frame, index, e = _setup()
    assert _members(frame, index, e("u1")) == {"u1", "u2"}
    _inject(monkeypatch, lambda f, i: [EventReferenceRelation(EventRelationKind.ABOUT, e("u2"), e("u3"))])
    env = RJ.build_review_envelope(frame, e("u1"), index)

    assert {x["predicate_ref"] for x in env.events} == {"u1", "u2"}
    assert _members(frame, index, e("u3")) == {"u3", "u4"}
    assert all(r.relation_kind is not EventRelationKind.ABOUT for r in env.relations)


def test_every_non_whitelisted_kind_is_excluded_by_default(monkeypatch):
    frame, index, e = _setup()
    for kind in EventRelationKind:
        _inject(monkeypatch, lambda f, i, kind=kind: [EventReferenceRelation(kind, e("u2"), e("u3"))])
        joined = _members(frame, index, e("u1")) == {"u1", "u2", "u3", "u4"}
        assert joined == (kind in PERSPECTIVE), kind
        monkeypatch.undo()


def test_internal_excluded_relation_stays_visible_without_expanding(monkeypatch):
    frame, index, e = _setup()
    _inject(monkeypatch, lambda f, i: [EventReferenceRelation(EventRelationKind.ABOUT, e("u1"), e("u2"))])
    env = RJ.build_review_envelope(frame, e("u1"), index)

    assert {x["predicate_ref"] for x in env.events} == {"u1", "u2"}
    assert (EventRelationKind.ABOUT, e("u1"), e("u2")) in {(r.relation_kind, r.source_event, r.target_event) for r in env.relations}


def test_status_does_not_filter_membership(monkeypatch):
    frame, index, e = _setup()
    for status in ("structural", "nominal_reference"):
        _inject(monkeypatch, lambda f, i, status=status: [
            EventReferenceRelation(EventRelationKind.REPORTS_ABOUT, e("u2"), e("u3"), status=status)])
        assert _members(frame, index, e("u1")) == {"u1", "u2", "u3", "u4"}, status
        monkeypatch.undo()


def test_real_nominal_perspectives_still_join():
    frame, index, e = _setup("Paul a lancé le test. J'ai observé ce lancement. Marie a mentionné ce lancement. "
                             "Luc croit ce lancement. Anne a appris ce lancement.")
    env = RJ.build_review_envelope(frame, e("u1"), index)

    assert {x["predicate_ref"] for x in env.events} == {"u1", "u2", "u3", "u4", "u5"}
    assert sorted((r.relation_kind.value, r.status) for r in env.relations) == [
        ("BELIEVES_ABOUT", "nominal_reference"), ("LEARNS_ABOUT", "nominal_reference"),
        ("OBSERVES", "nominal_reference"), ("REPORTS_ABOUT", "nominal_reference")]


def _real_believes(frame, index):
    env = RJ.build_review_envelope(frame, index.events()[0].event_ref.event_id, index)
    return next(r for r in env.relations if r.relation_kind is EventRelationKind.BELIEVES_ABOUT)


def test_exact_duplicate_relation_collapses(monkeypatch):
    frame, index, e = _setup()
    real = _real_believes(frame, index)
    _inject(monkeypatch, lambda f, i: [replace(real), replace(real)])
    env = RJ.build_review_envelope(frame, e("u1"), index)

    assert len(env.relations) == 1
    assert sum(c["origin"] == "event_relation" for c in env.epistemic_contributions) == 1
    assert dict(env.relations[0].provenance) == dict(real.provenance)


@pytest.mark.parametrize("variant", [
    lambda r: replace(r, relation_kind=EventRelationKind.OBSERVES),
    lambda r: replace(r, provenance={**dict(r.provenance), "source": "another_producer"}),
    lambda r: replace(r, metadata={**dict(r.metadata), "extra": 1}),
    lambda r: replace(r, confidence={"value": 0.5, "calibrated": False}),
    lambda r: replace(r, status="nominal_reference"),
])
def test_non_identical_relations_are_not_collapsed(monkeypatch, variant):
    frame, index, e = _setup()
    real = _real_believes(frame, index)
    _inject(monkeypatch, lambda f, i: [variant(real)])
    env = RJ.build_review_envelope(frame, e("u1"), index)

    assert len(env.relations) == 2
    assert sum(c["origin"] == "event_relation" for c in env.epistemic_contributions) == 2


def test_two_sources_same_target_stay_two_perspectives():
    frame, index, e = _setup("Paul a lancé le test. Marie a mentionné ce lancement. Luc a mentionné ce lancement.")
    env = RJ.build_review_envelope(frame, e("u1"), index)
    reports = [r for r in env.relations if r.relation_kind is EventRelationKind.REPORTS_ABOUT]

    assert len(reports) == 2 and len({r.source_event for r in reports}) == 2


@pytest.mark.parametrize("text", [
    "Paul croit que Marie a dit que Jean a lancé le test.",
    "Paul a lancé le test. J'ai observé ce lancement. Marie a mentionné ce lancement.",
    "Paul dit que Marie a vu Jean lancer le test.",
])
def test_valid_transitive_chains_center_invariant_and_directed(text):
    frame, index, _ = _setup(text)
    envelopes = [RJ.build_review_envelope(frame, c.event_ref.event_id, index) for c in index.events()]
    member_sets = {frozenset(x["event_id"] for x in env.events) for env in envelopes}

    assert member_sets == {frozenset(c.event_ref.event_id for c in index.events())}
    for env in envelopes:
        for r in env.relations:
            assert index.by_event_id(r.target_event).predicate_ref != index.by_event_id(r.source_event).predicate_ref
            assert frame.unit(index.by_event_id(r.target_event).predicate_ref).span[0] >= 0


def test_forged_allowed_kind_relation_is_trusted_documented_limit(monkeypatch):
    frame, index, e = _setup()
    _inject(monkeypatch, lambda f, i: [EventReferenceRelation(EventRelationKind.REPORTS_ABOUT, e("u2"), e("u3"))])
    # Expected at this layer: an allowed kind is trusted; correctness is an upstream invariant.
    assert _members(frame, index, e("u1")) == {"u1", "u2", "u3", "u4"}


def test_parser_conditions_cannot_enter_review_membership():
    with pytest.raises(ValueError):
        EventRelationKind("CONDITIONS")
    frame, index, e = _setup("Si Paul lance le test, Marie dit que Jean relance le build.")
    assert _members(frame, index, e("u1")) == {"u1"}
    assert _members(frame, index, e("u2")) == {"u2", "u3"}


def test_review_join_whitelist_adversarial_matrix(monkeypatch):
    people = ("Nadia", "Omar", "Léa", "Hugo", "Anne", "Karim", "Sofia")
    things = ("le script", "la suite", "le job", "le lot", "le test")
    metrics = dict.fromkeys((
        "CASES", "ABOUT_MEMBERSHIP_BRIDGE", "VALID_EDGE_EXCLUDED", "NOMINAL_JOIN_REGRESSION",
        "STATUS_MEMBERSHIP_DIVERGENCE", "EXACT_DUPLICATE_RELATIONS_RETAINED", "EXACT_DUPLICATE_CONTRIBUTIONS_RETAINED",
        "DISTINCT_SOURCE_COLLAPSE", "DISTINCT_KIND_COLLAPSE", "DISTINCT_PROVENANCE_COLLAPSE",
        "CENTER_INVARIANCE_FAILURE", "VALID_TRANSITIVE_JOIN_FAILURE", "INVALID_TRANSITIVE_BRIDGE",
        "RELATION_DIRECTION_CHANGED", "VALID_MEMBERSHIP_EDGES", "NOMINAL_MEMBERSHIP_EDGES", "FORGED_ABOUT_EDGES",
        "EXACT_DUPLICATES_INJECTED", "FORGED_ALLOWED_KIND_EDGES",
    ), 0)
    for (a, b), x in product(product(people, repeat=2), things):
        if a == b:
            continue
        # real graphs: every produced perspective edge joins, centers agree, direction kept
        for text in (f"{a} croit que {b} a dit que Tom a relancé {x}.",
                     f"{a} a relancé {x}. J'ai observé ce lancement. {b} a mentionné ce lancement. Tom croit ce lancement.",
                     f"{a} dit que {b} a appris que Tom a relancé {x}."):
            frame, index, _ = _setup(text)
            member_sets = set()
            for candidate in index.events():
                metrics["CASES"] += 1
                env = RJ.build_review_envelope(frame, candidate.event_ref.event_id, index)
                ids = frozenset(v["event_id"] for v in env.events)
                member_sets.add(ids)
                for r in env.relations:
                    metrics["VALID_MEMBERSHIP_EDGES"] += r.relation_kind in PERSPECTIVE
                    metrics["NOMINAL_MEMBERSHIP_EDGES"] += r.status == "nominal_reference"
                    if r.source_event not in ids or r.target_event not in ids:
                        metrics["VALID_EDGE_EXCLUDED"] += 1
            if len(member_sets) != 1:
                metrics["CENTER_INVARIANCE_FAILURE"] += 1
            if member_sets and len(next(iter(member_sets))) != len(index.events()):
                metrics["VALID_TRANSITIVE_JOIN_FAILURE"] += 1
        # forged edges on two independent clusters
        frame, index, e = _setup(f"{a} croit que {b} a relancé {x}. Tom dit que Luc a relancé le build.")
        base = RJ.build_review_envelope(frame, e("u1"), index)
        real = base.relations[0]
        forged = {
            "about_bridge": [EventReferenceRelation(EventRelationKind.ABOUT, e("u2"), e("u3"))],
            "allowed_bridge": [EventReferenceRelation(EventRelationKind.REPORTS_ABOUT, e("u2"), e("u3"))],
            "allowed_bridge_nominal": [EventReferenceRelation(EventRelationKind.REPORTS_ABOUT, e("u2"), e("u3"),
                                                              status="nominal_reference")],
            "exact_dup": [replace(real), replace(real)],
            "other_kind": [replace(real, relation_kind=EventRelationKind.OBSERVES)],
            "other_provenance": [replace(real, provenance={**dict(real.provenance), "source": "x"})],
            "other_source": [EventReferenceRelation(EventRelationKind.BELIEVES_ABOUT, e("u3"), e("u2"))],
        }
        results = {}
        for name, extra in forged.items():
            _inject(monkeypatch, lambda f, i, extra=extra: extra)
            env = RJ.build_review_envelope(frame, e("u1"), index)
            monkeypatch.undo()
            metrics["CASES"] += 1
            results[name] = env
            for r in env.relations:
                if (r.source_event, r.target_event) == (e("u2"), e("u1")):
                    metrics["RELATION_DIRECTION_CHANGED"] += 1
        members = lambda env: {v["predicate_ref"] for v in env.events}
        metrics["FORGED_ABOUT_EDGES"] += 1
        metrics["ABOUT_MEMBERSHIP_BRIDGE"] += members(results["about_bridge"]) != {"u1", "u2"}
        metrics["INVALID_TRANSITIVE_BRIDGE"] += "u4" in members(results["about_bridge"])
        metrics["FORGED_ALLOWED_KIND_EDGES"] += 2
        metrics["STATUS_MEMBERSHIP_DIVERGENCE"] += members(results["allowed_bridge"]) != members(results["allowed_bridge_nominal"])
        metrics["EXACT_DUPLICATES_INJECTED"] += 2
        metrics["EXACT_DUPLICATE_RELATIONS_RETAINED"] += len(results["exact_dup"].relations) != 1
        metrics["EXACT_DUPLICATE_CONTRIBUTIONS_RETAINED"] += sum(
            c["origin"] == "event_relation" for c in results["exact_dup"].epistemic_contributions) != 1
        metrics["DISTINCT_KIND_COLLAPSE"] += len(results["other_kind"].relations) != 2
        metrics["DISTINCT_PROVENANCE_COLLAPSE"] += len(results["other_provenance"].relations) != 2
        # A second source (u3) on the same target (u2): both perspectives must survive.
        to_target = [r for r in results["other_source"].relations if r.target_event == e("u2")]
        metrics["DISTINCT_SOURCE_COLLAPSE"] += len({r.source_event for r in to_target}) != 2
        # real nominal join still present
        frame2, index2, e2 = _setup(f"{a} a relancé {x}. {b} a mentionné ce lancement.")
        metrics["NOMINAL_JOIN_REGRESSION"] += _members(frame2, index2, e2("u1")) != {"u1", "u2"}

    assert metrics["CASES"] >= 3000
    for key in ("VALID_MEMBERSHIP_EDGES", "NOMINAL_MEMBERSHIP_EDGES", "FORGED_ABOUT_EDGES",
                "EXACT_DUPLICATES_INJECTED", "FORGED_ALLOWED_KIND_EDGES"):
        assert metrics[key] > 0, (key, metrics)
    for key in ("ABOUT_MEMBERSHIP_BRIDGE", "VALID_EDGE_EXCLUDED", "NOMINAL_JOIN_REGRESSION",
                "STATUS_MEMBERSHIP_DIVERGENCE", "EXACT_DUPLICATE_RELATIONS_RETAINED",
                "EXACT_DUPLICATE_CONTRIBUTIONS_RETAINED", "DISTINCT_SOURCE_COLLAPSE", "DISTINCT_KIND_COLLAPSE",
                "DISTINCT_PROVENANCE_COLLAPSE", "CENTER_INVARIANCE_FAILURE", "VALID_TRANSITIVE_JOIN_FAILURE",
                "INVALID_TRANSITIVE_BRIDGE", "RELATION_DIRECTION_CHANGED"):
        assert metrics[key] == 0, (key, metrics)
