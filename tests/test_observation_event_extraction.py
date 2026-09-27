from __future__ import annotations

from app.semantic.lattice.event_coreference import ResolutionStatus, TargetKind
from app.semantic.lattice.event_extraction import OccurrenceStatus, extract_event_candidates
from app.semantic.lattice.events import EventKind, EventRelationKind
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.observation_event_extraction import extract_observation_event_targets


def _extract(raw: str):
    frame = parse_utterance(raw)
    candidates = extract_event_candidates(frame)
    return frame, candidates, extract_observation_event_targets(frame, candidates)


def test_see_embeds_action_as_structural_event_target():
    frame, candidates, result = _extract("j'ai vu Paul lancer le test")

    assert [(u.predicate, u.embedded_under) for u in frame.units] == [
        ("OBSERVE", None),
        ("EXECUTE", "u1"),
    ]
    assert [(c.predicate_ref, c.event_ref.event_kind) for c in candidates] == [
        ("u2", EventKind.ACTION),
    ]
    assert len(result.observation_events) == 1
    observe = result.observation_events[0]
    assert observe.predicate_ref == "u1"
    assert observe.event_ref.event_kind is EventKind.OBSERVATION
    assert observe.occurrence_status is OccurrenceStatus.ASSERTED_OCCURRED

    assert len(result.targets) == 1
    target = result.targets[0]
    assert target.source_event == observe.event_ref.event_id
    assert target.target_kind is TargetKind.EVENT_TARGET
    assert target.resolution_status is ResolutionStatus.RESOLVED_STRUCTURAL
    assert target.target_predicate == "u2"
    assert target.target_event == candidates[0].event_ref.event_id

    assert len(result.relations) == 1
    relation = result.relations[0]
    assert relation.relation_kind is EventRelationKind.OBSERVES
    assert relation.source_event == observe.event_ref.event_id
    assert relation.target_event == candidates[0].event_ref.event_id


def test_observe_embeds_action_as_structural_event_target():
    _frame, candidates, result = _extract("j'ai observé Paul lancer le test")

    assert len(result.observation_events) == 1
    assert result.observation_events[0].event_ref.event_kind is EventKind.OBSERVATION
    assert len(candidates) == 1
    assert candidates[0].event_ref.event_kind is EventKind.ACTION
    assert result.targets[0].target_kind is TargetKind.EVENT_TARGET
    assert result.targets[0].resolution_status is ResolutionStatus.RESOLVED_STRUCTURAL
    assert result.relations[0].relation_kind is EventRelationKind.OBSERVES


def test_detect_direct_np_keeps_entity_target_without_event_fabrication():
    frame, candidates, result = _extract("le capteur a détecté l'anomalie")

    assert [(u.predicate, u.object_head) for u in frame.units] == [("OBSERVE", "anomalie")]
    assert candidates == ()
    assert len(result.observation_events) == 1
    assert result.observation_events[0].event_ref.event_kind is EventKind.OBSERVATION
    assert len(result.targets) == 1
    assert result.targets[0].target_kind is TargetKind.ENTITY_TARGET
    assert result.targets[0].resolution_status is ResolutionStatus.RESOLVED_STRUCTURAL
    assert result.targets[0].target_predicate is None
    assert result.targets[0].target_event is None
    assert result.relations == ()


def test_observation_does_not_promote_modal_target_occurrence():
    _frame, candidates, result = _extract("j'ai vu Paul pouvoir lancer le test")

    assert len(result.observation_events) == 1
    assert result.observation_events[0].occurrence_status is OccurrenceStatus.ASSERTED_OCCURRED
    assert len(candidates) == 1
    assert candidates[0].occurrence_status is not OccurrenceStatus.ASSERTED_OCCURRED
    assert result.metadata["TARGET_OCCURRENCE_PROMOTIONS"] == 0


def test_observation_hard_boundaries_are_zero():
    _frame, _candidates, result = _extract("j'ai vu Paul lancer le test")

    assert result.metadata["VERIFIED_FLOW_CREATED"] == 0
    assert result.metadata["SUPPORTED_FLOW_CREATED"] == 0
    assert result.metadata["PHYSICAL_PROOF_CREATED"] == 0
    assert result.metadata["VALIDATED_EVIDENCE_CREATED"] == 0
    assert result.metadata["MEMORY_FLOW_CREATED"] == 0
    assert result.metadata["MEMORY_WRITE"] == 0
    assert result.metadata["AUTHORIZED_FLOW_CREATED"] == 0
    assert result.metadata["EXECUTED_FLOW_CREATED"] == 0
    assert result.metadata["KX108_CALLED"] == 0
    assert result.metadata["CAUSAL_FLOW_FROM_OBSERVATION"] == 0
    assert result.metadata["LATEST_EVENT_FALLBACK"] == 0
