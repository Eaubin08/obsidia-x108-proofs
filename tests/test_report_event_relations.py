"""REPORT EventRef -> REPORTS_ABOUT -> immediate target EventRef.

No flattening of nested meta-events, no EventRef for proposition-only targets,
no promotion of target occurrence, no verification semantics.
"""
from __future__ import annotations

from app.semantic.lattice.event_coreference import ResolutionStatus, TargetKind
from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.events import EventKind, EventRelationKind
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.meta_event_relations import extract_report_event_relations
from app.semantic.lattice.observation_event_extraction import extract_observation_event_targets
from app.semantic.lattice.event_extraction import extract_event_candidates


def _run(text: str):
    frame = parse_utterance(text)
    index = build_frame_event_index(frame)
    return frame, index, extract_report_event_relations(frame, index)


def _pred(frame, index, event_id):
    return next(u.predicate for u in frame.units if index.event_for(u.id) and index.event_for(u.id).event_ref.event_id == event_id)


def test_simple_report_relation():
    frame, index, result = _run("Paul dit que Marie a lancé le test.")

    assert len(result.relations) == 1
    rel = result.relations[0]
    assert rel.relation_kind is EventRelationKind.REPORTS_ABOUT
    assert _pred(frame, index, rel.source_event) == "SAY"
    assert _pred(frame, index, rel.target_event) == "EXECUTE"
    assert rel.metadata["target_occurrence_status"] == "REPORTED"
    assert rel.metadata["verified"] is False and rel.metadata["validated_evidence"] is False
    assert rel.metadata["target_occurrence_promoted"] is False


def test_new_report_lexicon_is_covered():
    for verb in ("affirme", "déclare", "mentionne"):
        _, _, result = _run(f"Paul {verb} que Marie a lancé le test.")
        assert len(result.relations) == 1


def test_nested_reports_are_not_flattened():
    frame, index, result = _run("Paul dit que Marie dit que Jean a lancé le test.")
    pairs = {(_pred(frame, index, r.source_event), _pred(frame, index, r.target_event)) for r in result.relations}
    outer, inner = [u for u in frame.units if u.predicate == "SAY"]
    run = next(u for u in frame.units if u.predicate == "EXECUTE")
    by_source = {r.source_event: r.target_event for r in result.relations}

    assert pairs == {("SAY", "SAY"), ("SAY", "EXECUTE")}
    assert by_source[index.event_for(outer.id).event_ref.event_id] == index.event_for(inner.id).event_ref.event_id
    assert by_source[index.event_for(inner.id).event_ref.event_id] == index.event_for(run.id).event_ref.event_id


def test_report_targets_observation_which_keeps_its_own_observes_relation():
    frame, index, result = _run("Paul dit qu'il a vu Marie lancer le test.")
    observe = next(u for u in frame.units if u.predicate == "OBSERVE")
    run = next(u for u in frame.units if u.predicate == "EXECUTE")

    assert [r.target_event for r in result.relations] == [index.event_for(observe.id).event_ref.event_id]
    assert index.event_for(observe.id).event_ref.event_kind is EventKind.OBSERVATION
    observes = extract_observation_event_targets(frame, extract_event_candidates(frame)).relations
    assert [(r.source_event, r.target_event) for r in observes] == [
        (index.event_for(observe.id).event_ref.event_id, index.event_for(run.id).event_ref.event_id)]


def test_report_targets_learning_event():
    frame, index, result = _run("Paul dit que Marie a appris que Jean a lancé le test.")
    learn = next(u for u in frame.units if u.predicate == "LEARN")

    assert [r.target_event for r in result.relations] == [index.event_for(learn.id).event_ref.event_id]


def test_proposition_only_target_creates_no_relation():
    frame, index, result = _run("Paul dit que le système s'est arrêté.")

    assert result.relations == ()
    assert [(t.target_kind, t.resolution_status) for t in result.targets] == [
        (TargetKind.PROPOSITION_TARGET, ResolutionStatus.RESOLVED_STRUCTURAL)]


def test_report_without_complement_is_unknown_and_unrelated():
    for text in ("Paul dit bonjour.", "Paul déclare ses revenus."):
        _, _, result = _run(text)
        assert result.relations == ()
        assert [t.target_kind for t in result.targets] == [TargetKind.UNKNOWN_TARGET]


def test_report_under_belief_keeps_both_layers():
    frame, index, result = _run("Paul croit que Marie a dit que Jean a lancé le test.")
    say = next(u for u in frame.units if u.predicate == "SAY")

    assert [r.source_event for r in result.relations] == [index.event_for(say.id).event_ref.event_id]
    assert result.relations[0].metadata["source_occurrence_status"] == "UNKNOWN"


def test_extraction_is_non_mutating_and_non_authoritative():
    frame = parse_utterance("Paul dit que Marie a lancé le test.")
    index = build_frame_event_index(frame)
    before = {p: c.to_dict() for p, c in index.by_predicate.items()}
    result = extract_report_event_relations(frame, index)

    assert {p: c.to_dict() for p, c in index.by_predicate.items()} == before
    for key in ("VERIFIED_FLOW_CREATED", "OBSERVED_FLOW_CREATED", "MEMORY_WRITE", "AUTHORIZED_FLOW_CREATED",
                "TARGET_OCCURRENCE_PROMOTIONS", "KX108_CALLED"):
        assert result.metadata[key] == 0


def test_report_relation_matrix_targets_are_always_immediate():
    templates = (
        "{s} dit que {o} a lancé le test {i}.", "{s} affirme que {o} n'a pas lancé le test {i}.",
        "{s} dit que {o} dit que Jean a lancé le test {i}.", "{s} dit que {o} croit que Jean a lancé le test {i}.",
        "{s} déclare qu'il a vu {o} lancer le test {i}.", "{s} dit que {o} a appris que Jean a lancé le test {i}.",
        "{s} croit que {o} a dit que Jean a lancé le test {i}.", "{s} dit que {o} nie que Jean a lancé le test {i}.",
        "{s} dit que {o} confirme que Jean a lancé le test {i}.", "{s} mentionne {o} {i}.",
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
                        assert source.event_ref.event_kind is EventKind.REPORT
                        assert units[target.predicate_ref].embedded_under == source.predicate_ref
                        assert rel.metadata["target_occurrence_status"] == target.occurrence_status.value
    assert cases >= 1000 and relations > 0
