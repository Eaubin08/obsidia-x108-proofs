from __future__ import annotations

from app.semantic.lattice.event_coreference import ResolutionStatus, TargetKind
from app.semantic.lattice.event_extraction import extract_event_candidates
from app.semantic.lattice.events import EventKind, EventRelationKind
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.knowledge_event_extraction import extract_knowledge_event_targets
from app.semantic.lattice.observation_event_extraction import extract_observation_event_targets


def _extract(raw: str):
    frame = parse_utterance(raw)
    candidates = extract_event_candidates(frame)
    return frame, candidates, extract_observation_event_targets(frame, candidates)


def test_generic_object_pronoun_remains_unresolved_without_event_anaphora():
    frame, candidates, result = _extract("je l'ai vu")

    assert [(u.predicate, u.object_head) for u in frame.units] == [("OBSERVE", "l'")]
    assert candidates == ()
    assert len(result.observation_events) == 1
    target = result.targets[0]
    assert target.target_kind is TargetKind.UNKNOWN_TARGET
    assert target.resolution_status is ResolutionStatus.UNRESOLVED
    assert target.target_event is None
    assert target.target_predicate is None
    assert result.relations == ()


def test_generic_deictic_remains_unresolved_without_event_anaphora():
    _frame, _candidates, result = _extract("j'ai vu ça")

    assert len(result.observation_events) == 1
    target = result.targets[0]
    assert target.target_kind is TargetKind.UNKNOWN_TARGET
    assert target.resolution_status is ResolutionStatus.UNRESOLVED
    assert target.target_event is None
    assert result.metadata["LATEST_EVENT_FALLBACK"] == 0


def test_report_containing_observation_does_not_flatten_target_graph():
    frame, candidates, result = _extract("Paul dit qu'il a vu Marie lancer le test")

    assert [u.predicate for u in frame.units] == ["SAY", "OBSERVE", "EXECUTE"]
    report = next(candidate for candidate in candidates if candidate.event_ref.event_kind is EventKind.REPORT)
    action = next(candidate for candidate in candidates if candidate.event_ref.event_kind is EventKind.ACTION)
    observation = result.observation_events[0]

    assert result.targets[0].target_event == action.event_ref.event_id
    assert result.relations[0].source_event == observation.event_ref.event_id
    assert result.relations[0].target_event == action.event_ref.event_id
    assert result.relations[0].relation_kind is EventRelationKind.OBSERVES
    assert report.event_ref.event_id not in {relation.source_event for relation in result.relations}


def test_knowledge_observation_nesting_targets_observation_not_inner_action():
    frame = parse_utterance("j'ai appris que Paul avait observé Marie lancer le test")
    action_candidates = extract_event_candidates(frame)
    observation = extract_observation_event_targets(frame, action_candidates)
    all_candidates = tuple(action_candidates) + tuple(observation.observation_events)
    knowledge = extract_knowledge_event_targets(frame, all_candidates)

    assert [u.predicate for u in frame.units] == ["LEARN", "OBSERVE", "EXECUTE"]
    assert observation.targets[0].target_kind is TargetKind.EVENT_TARGET
    assert observation.relations[0].relation_kind is EventRelationKind.OBSERVES
    assert len(knowledge.knowledge_events) == 1
    assert knowledge.targets[0].target_kind is TargetKind.EVENT_TARGET
    assert knowledge.targets[0].target_event == observation.observation_events[0].event_ref.event_id
    assert knowledge.targets[0].target_event != observation.targets[0].target_event


def test_adversarial_matrix_keeps_observation_boundaries():
    templates = (
        "j'ai vu Paul lancer le test {suffix}",
        "j'ai observé Paul lancer le test {suffix}",
        "le capteur a détecté l'anomalie {suffix}",
        "Paul dit qu'il a vu Marie lancer le test {suffix}",
        "j'ai appris que Paul avait observé Marie lancer le test {suffix}",
        "j'ai vu Paul pouvoir lancer le test {suffix}",
        "j'ai vu Paul ne pas lancer le test {suffix}",
        "si je vois Paul lancer le test, prépare le rapport {suffix}",
        "je l'ai vu {suffix}",
        "j'ai vu ça {suffix}",
        "j'ai constaté que le test a échoué {suffix}",
        "j'ai mesuré le signal {suffix}",
        "prépare le script puis lance-le {suffix}",
        "Paul dit que Marie lance le test {suffix}",
        "je crois que Marie lance le test {suffix}",
    )
    metrics = {
        "CASES": 0,
        "OBSERVATION_EVENTS": 0,
        "EVENT_TARGETS": 0,
        "ENTITY_TARGETS": 0,
        "PROPOSITION_TARGETS": 0,
        "UNRESOLVED_TARGETS": 0,
        "FALSE_OBSERVATION_EVENTS": 0,
        "FALSE_EVENT_COREFERENCE": 0,
        "TARGET_OCCURRENCE_PROMOTIONS": 0,
        "VERIFIED_FLOW_CREATED": 0,
        "PHYSICAL_PROOF_CREATED": 0,
        "MEMORY_FLOW_CREATED": 0,
        "AUTHORIZED_FLOW_CREATED": 0,
        "CAUSAL_FLOW_FROM_OBSERVATION": 0,
    }

    supported = ("vu", "vois", "observé", "détecté")
    for idx in range(100):
        for template in templates:
            raw = template.format(suffix=f"cas{idx}")
            metrics["CASES"] += 1
            frame, candidates, result = _extract(raw)
            metrics["OBSERVATION_EVENTS"] += len(result.observation_events)
            if not any(marker in raw for marker in supported) and result.observation_events:
                metrics["FALSE_OBSERVATION_EVENTS"] += len(result.observation_events)
            for target in result.targets:
                if target.target_kind is TargetKind.EVENT_TARGET:
                    metrics["EVENT_TARGETS"] += 1
                if target.target_kind is TargetKind.ENTITY_TARGET:
                    metrics["ENTITY_TARGETS"] += 1
                if target.target_kind is TargetKind.PROPOSITION_TARGET:
                    metrics["PROPOSITION_TARGETS"] += 1
                if target.resolution_status is ResolutionStatus.UNRESOLVED:
                    metrics["UNRESOLVED_TARGETS"] += 1
                if target.metadata.get("nearest_event_fallback") is True:
                    metrics["FALSE_EVENT_COREFERENCE"] += 1
            metrics["TARGET_OCCURRENCE_PROMOTIONS"] += int(result.metadata.get("TARGET_OCCURRENCE_PROMOTIONS", 0))
            metrics["VERIFIED_FLOW_CREATED"] += int(result.metadata.get("VERIFIED_FLOW_CREATED", 0))
            metrics["PHYSICAL_PROOF_CREATED"] += int(result.metadata.get("PHYSICAL_PROOF_CREATED", 0))
            metrics["MEMORY_FLOW_CREATED"] += int(result.metadata.get("MEMORY_FLOW_CREATED", 0))
            metrics["AUTHORIZED_FLOW_CREATED"] += int(result.metadata.get("AUTHORIZED_FLOW_CREATED", 0))
            metrics["CAUSAL_FLOW_FROM_OBSERVATION"] += int(result.metadata.get("CAUSAL_FLOW_FROM_OBSERVATION", 0))

    assert metrics["CASES"] >= 1500
    assert metrics["OBSERVATION_EVENTS"] >= 900
    assert metrics["EVENT_TARGETS"] >= 500
    assert metrics["ENTITY_TARGETS"] >= 100
    assert metrics["UNRESOLVED_TARGETS"] >= 200
    assert metrics["FALSE_OBSERVATION_EVENTS"] == 0
    assert metrics["FALSE_EVENT_COREFERENCE"] == 0
    assert metrics["TARGET_OCCURRENCE_PROMOTIONS"] == 0
    assert metrics["VERIFIED_FLOW_CREATED"] == 0
    assert metrics["PHYSICAL_PROOF_CREATED"] == 0
    assert metrics["MEMORY_FLOW_CREATED"] == 0
    assert metrics["AUTHORIZED_FLOW_CREATED"] == 0
    assert metrics["CAUSAL_FLOW_FROM_OBSERVATION"] == 0
