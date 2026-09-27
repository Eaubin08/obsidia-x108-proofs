"""BELIEF EventRef -> BELIEVES_ABOUT -> immediate target EventRef.

The believed target keeps its own occurrence (never promoted); no SUPPORTED or
VERIFIED semantics; nested chains stay one hop per relation.
"""
from __future__ import annotations

from app.semantic.lattice.event_coreference import TargetKind
from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.events import EventKind, EventRelationKind
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.meta_event_relations import (
    extract_belief_event_relations,
    extract_report_event_relations,
)


def _run(text: str):
    frame = parse_utterance(text)
    index = build_frame_event_index(frame)
    return frame, index, extract_belief_event_relations(frame, index)


def _eid(index, unit):
    return index.event_for(unit.id).event_ref.event_id


def test_simple_belief_relation_keeps_target_unknown():
    frame, index, result = _run("Paul croit que Marie a lancé le test.")
    believe = next(u for u in frame.units if u.predicate == "BELIEVE")
    run = next(u for u in frame.units if u.predicate == "EXECUTE")

    assert [(r.relation_kind, r.source_event, r.target_event) for r in result.relations] == [
        (EventRelationKind.BELIEVES_ABOUT, _eid(index, believe), _eid(index, run))]
    rel = result.relations[0]
    assert rel.metadata["target_occurrence_status"] == "UNKNOWN"
    assert rel.metadata["supported"] is False and rel.metadata["verified"] is False
    assert index.event_for(run.id).occurrence_status.value == "UNKNOWN"


def test_supposer_and_inflections_are_covered():
    for text in ("Paul suppose que Marie a lancé le test.", "Paul croyait que Marie avait lancé le test.",
                 "Paul pensait que Marie avait lancé le test."):
        _, _, result = _run(text)
        assert len(result.relations) == 1


def test_nested_beliefs_are_not_flattened():
    frame, index, result = _run("Paul croit que Marie pense que Jean a lancé le test.")
    outer, inner = [u for u in frame.units if u.predicate == "BELIEVE"]
    run = next(u for u in frame.units if u.predicate == "EXECUTE")

    assert {(r.source_event, r.target_event) for r in result.relations} == {
        (_eid(index, outer), _eid(index, inner)), (_eid(index, inner), _eid(index, run))}


def test_belief_around_report_keeps_report_layer():
    frame, index, result = _run("Paul croit que Marie a dit que Jean a lancé le test.")
    believe = next(u for u in frame.units if u.predicate == "BELIEVE")
    say = next(u for u in frame.units if u.predicate == "SAY")
    run = next(u for u in frame.units if u.predicate == "EXECUTE")
    reports = extract_report_event_relations(frame, index)

    assert [(r.source_event, r.target_event) for r in result.relations] == [(_eid(index, believe), _eid(index, say))]
    assert [(r.source_event, r.target_event) for r in reports.relations] == [(_eid(index, say), _eid(index, run))]


def test_belief_around_observation_targets_the_observation():
    frame, index, result = _run("Paul croit que Marie a vu Jean lancer le test.")
    observe = next(u for u in frame.units if u.predicate == "OBSERVE")

    assert [r.target_event for r in result.relations] == [_eid(index, observe)]
    assert index.event_for(observe.id).event_ref.event_kind is EventKind.OBSERVATION
    assert result.relations[0].metadata["target_occurrence_status"] == "UNKNOWN"


def test_belief_without_complement_creates_no_relation():
    for text in ("Paul pense à Marie.", "Paul suppose une erreur."):
        _, _, result = _run(text)
        assert result.relations == ()
        assert all(t.target_kind is TargetKind.UNKNOWN_TARGET for t in result.targets)


def test_reports_and_beliefs_do_not_cross():
    frame, index, beliefs = _run("Paul dit que Marie a lancé le test.")
    assert beliefs.relations == () and beliefs.targets == ()
    reports = extract_report_event_relations(*_run("Paul croit que Marie a lancé le test.")[:2])
    assert reports.relations == () and reports.targets == ()


def test_belief_relation_matrix_is_immediate_and_non_promoting():
    templates = (
        "{s} croit que {o} a lancé le test {i}.", "{s} pense que {o} n'a pas lancé le test {i}.",
        "{s} suppose que {o} lancera le test {i}.", "{s} croit que {o} pense que Jean a lancé le test {i}.",
        "{s} croit que {o} a dit que Jean a lancé le test {i}.", "{s} croit que {o} a vu Jean lancer le test {i}.",
        "{s} croit que {o} a appris que Jean a lancé le test {i}.", "{s} dit que {o} croit que Jean a lancé le test {i}.",
        "{s} croit que {o} nie que Jean a lancé le test {i}.", "{s} pense à {o} {i}.",
    )
    cases = relations = 0
    for i in range(20):
        for s in ("Paul", "Anne", "Le chef"):
            for o in ("Marie", "Claire"):
                for template in templates:
                    frame, index, result = _run(template.format(s=s, o=o, i=i))
                    units = {u.id: u for u in frame.units}
                    cases += 1
                    for rel in result.relations:
                        relations += 1
                        source = index.by_event_id(rel.source_event)
                        target = index.by_event_id(rel.target_event)
                        assert source.event_ref.event_kind is EventKind.BELIEF
                        assert units[target.predicate_ref].embedded_under == source.predicate_ref
                        assert target.occurrence_status.value != "ASSERTED_OCCURRED"
                        assert rel.metadata["target_occurrence_status"] == target.occurrence_status.value
                    assert result.metadata["SUPPORTED_FLOW_CREATED"] == 0
    assert cases >= 1000 and relations > 0
