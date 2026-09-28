"""Typed event/proposition target reference contracts."""
from __future__ import annotations

from app.semantic.lattice.event_coreference import (
    EventTargetReference,
    ResolutionStatus,
    TargetKind,
)
from app.semantic.lattice.event_extraction import extract_event_candidates
from app.semantic.lattice.events import EventKind, EventRef, EventReferenceRelation, EventRelationKind
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.knowledge_event_extraction import extract_knowledge_event_targets


def test_event_target_reference_preserves_target_semantics_and_identity():
    ref = EventTargetReference(
        source_event="event:learn",
        source_predicate="u-learn",
        target_kind=TargetKind.EVENT_TARGET,
        resolution_status=ResolutionStatus.RESOLVED_EXPLICIT,
        target_predicate="u-run",
        target_event="event:run",
        provenance={"source": "unit-test"},
    )

    assert ref.target_kind is TargetKind.EVENT_TARGET
    assert ref.target_predicate == "u-run"
    assert ref.target_event == "event:run"
    assert ref.to_dict()["target_kind"] == "EVENT_TARGET"
    assert "target_event_payload" not in ref.to_dict()


def test_proposition_target_is_valid_without_event_ref():
    ref = EventTargetReference(
        source_event="event:learn",
        source_predicate="u-learn",
        target_kind=TargetKind.PROPOSITION_TARGET,
        resolution_status=ResolutionStatus.RESOLVED_EXPLICIT,
        target_predicate="u-prop",
        target_event=None,
        provenance={"source": "unit-test"},
    )

    assert ref.target_event is None
    assert ref.target_predicate == "u-prop"
    assert ref.target_kind is TargetKind.PROPOSITION_TARGET


def test_unknown_pronoun_target_remains_unresolved_without_event_coreference():
    frame = parse_utterance("je l'ai appris")
    candidates = extract_event_candidates(frame)
    extraction = extract_knowledge_event_targets(frame, candidates)

    assert extraction.knowledge_events
    assert extraction.targets[0].target_kind is TargetKind.UNKNOWN_TARGET
    assert extraction.targets[0].resolution_status is ResolutionStatus.UNRESOLVED
    assert extraction.targets[0].target_event is None
    assert extraction.targets[0].metadata.get("event_coreference_heuristic") is False


def test_demonstrative_target_remains_unresolved_without_nearest_event_fallback():
    frame = parse_utterance("j'ai appris ça")
    candidates = extract_event_candidates(frame)
    extraction = extract_knowledge_event_targets(frame, candidates)

    assert extraction.targets[0].target_kind is TargetKind.UNKNOWN_TARGET
    assert extraction.targets[0].resolution_status is ResolutionStatus.UNRESOLVED
    assert extraction.targets[0].target_event is None
    assert extraction.targets[0].metadata.get("nearest_event_fallback") is False


def test_existing_entity_pronoun_resolution_is_not_event_resolution():
    frame = parse_utterance("prépare le script puis lance-le")

    assert any(rel.kind == "REFERS_TO" for rel in frame.relations)
    candidates = extract_event_candidates(frame)
    extraction = extract_knowledge_event_targets(frame, candidates)
    assert extraction.targets == ()


def test_same_target_event_can_support_future_meta_events_without_payload_duplication():
    target = EventRef("event:target", "u-target", EventKind.ACTION, provenance={"source": "unit-test"})
    learn = EventRef("event:learn", "u-learn", EventKind.KNOWLEDGE_ACQUISITION, provenance={"source": "unit-test"})
    report = EventRef("event:report", "u-report", EventKind.REPORT, provenance={"source": "unit-test"})
    belief = EventRef("event:belief", "u-belief", EventKind.BELIEF, provenance={"source": "unit-test"})
    relations = (
        EventReferenceRelation(EventRelationKind.LEARNS_ABOUT, learn.event_id, target.event_id),
        EventReferenceRelation(EventRelationKind.REPORTS_ABOUT, report.event_id, target.event_id),
        EventReferenceRelation(EventRelationKind.BELIEVES_ABOUT, belief.event_id, target.event_id),
    )

    assert {rel.target_event for rel in relations} == {target.event_id}
    assert all("target_event_payload" not in rel.to_dict() for rel in relations)
    assert len({target.event_id, learn.event_id, report.event_id, belief.event_id}) == 4


def test_reviewer_join_keys_are_preserved_without_flattening():
    frame = parse_utterance("j'ai appris que Paul a lancé le test")
    candidates = extract_event_candidates(frame)
    extraction = extract_knowledge_event_targets(frame, candidates)
    target = extraction.targets[0]
    relation = extraction.relations[0]

    assert target.source_predicate
    assert target.source_event == relation.source_event
    assert target.target_predicate
    assert target.target_event == relation.target_event
    assert target.source_event != target.target_event
    assert target.source_predicate != target.target_predicate


def test_adversarial_matrix_keeps_targeting_hard_boundaries():
    templates = (
        "j'ai appris que Paul a lancé le test {suffix}",
        "je sais que Paul a lancé le test {suffix}",
        "Paul m'a dit que Marie a lancé le test {suffix}",
        "je pense que Paul a lancé le test {suffix}",
        "j'ai appris que Paul pourrait lancer le test {suffix}",
        "j'ai appris que Paul n'a pas lancé le test {suffix}",
        "si j'apprends que Paul lance le test, prépare le rapport {suffix}",
        "je l'ai appris {suffix}",
        "j'ai appris ça {suffix}",
        "prépare le script puis lance-le {suffix}",
        "j'ai vu le test échouer {suffix}",
    )
    metrics = {
        "CASES": 0,
        "LEARN_EVENTS": 0,
        "RESOLVED_EVENT_TARGETS": 0,
        "RESOLVED_PROPOSITION_TARGETS": 0,
        "UNRESOLVED_TARGETS": 0,
        "FALSE_LEARN_EVENTS": 0,
        "FALSE_EVENT_COREFERENCE": 0,
        "TARGET_OCCURRENCE_PROMOTIONS": 0,
        "VERIFIED_FLOW_CREATED": 0,
        "MEMORY_FLOW_CREATED": 0,
        "AUTHORIZED_FLOW_CREATED": 0,
        "OBSERVATION_EVENT_CREATED": 0,
    }

    for i in range(100):
        for template in templates:
            raw = template.format(suffix=f"cas{i}")
            metrics["CASES"] += 1
            frame = parse_utterance(raw)
            candidates = extract_event_candidates(frame)
            extraction = extract_knowledge_event_targets(frame, candidates)
            metrics["LEARN_EVENTS"] += len(extraction.knowledge_events)
            if "appris" not in raw and "apprends" not in raw and extraction.knowledge_events:
                metrics["FALSE_LEARN_EVENTS"] += len(extraction.knowledge_events)
            for target in extraction.targets:
                if target.target_kind is TargetKind.EVENT_TARGET and target.resolution_status is ResolutionStatus.RESOLVED_EXPLICIT:
                    metrics["RESOLVED_EVENT_TARGETS"] += 1
                if target.target_kind is TargetKind.PROPOSITION_TARGET:
                    metrics["RESOLVED_PROPOSITION_TARGETS"] += 1
                if target.resolution_status is ResolutionStatus.UNRESOLVED:
                    metrics["UNRESOLVED_TARGETS"] += 1
                if target.metadata.get("event_coreference_heuristic") is True:
                    metrics["FALSE_EVENT_COREFERENCE"] += 1
            for candidate in candidates:
                if candidate.event_ref.event_kind is EventKind.OBSERVATION:
                    metrics["OBSERVATION_EVENT_CREATED"] += 1
            metrics["VERIFIED_FLOW_CREATED"] += int(extraction.metadata.get("VERIFIED_FLOW_CREATED", 0))
            metrics["MEMORY_FLOW_CREATED"] += int(extraction.metadata.get("MEMORY_FLOW_CREATED", 0))
            metrics["AUTHORIZED_FLOW_CREATED"] += int(extraction.metadata.get("AUTHORIZED_FLOW_CREATED", 0))
            metrics["TARGET_OCCURRENCE_PROMOTIONS"] += int(extraction.metadata.get("TARGET_OCCURRENCE_PROMOTIONS", 0))

    assert metrics["CASES"] >= 1000
    assert metrics["LEARN_EVENTS"] >= 600
    assert metrics["FALSE_LEARN_EVENTS"] == 0
    assert metrics["FALSE_EVENT_COREFERENCE"] == 0
    assert metrics["TARGET_OCCURRENCE_PROMOTIONS"] == 0
    assert metrics["VERIFIED_FLOW_CREATED"] == 0
    assert metrics["MEMORY_FLOW_CREATED"] == 0
    assert metrics["AUTHORIZED_FLOW_CREATED"] == 0
    assert metrics["OBSERVATION_EVENT_CREATED"] == 0
