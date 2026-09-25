"""Conservative PredicateUnit -> EventRef bridge contracts."""
from __future__ import annotations

from app.semantic.lattice.event_extraction import (
    ExtractionStatus,
    OccurrenceStatus,
    extract_event_candidates,
)
from app.semantic.lattice.events import EventKind
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ordered_meaning_flow import FlowFamily, OrderedMeaningFlow


def _candidate_by_predicate(text: str):
    frame = parse_utterance(text)
    candidates = extract_event_candidates(frame)
    return frame, {candidate.predicate_ref: candidate for candidate in candidates}


def test_positive_past_action_creates_asserted_action_event():
    frame, candidates = _candidate_by_predicate("Paul a lancé le test")
    run = next(unit for unit in frame.units if unit.predicate == "EXECUTE")
    candidate = candidates[run.id]

    assert candidate.event_ref.event_kind is EventKind.ACTION
    assert candidate.occurrence_status is OccurrenceStatus.ASSERTED_OCCURRED
    assert candidate.extraction_status is ExtractionStatus.EXTRACTED
    assert candidate.event_ref.predicate_ref == run.id


def test_negated_action_creates_candidate_but_not_occurred():
    frame, candidates = _candidate_by_predicate("Paul n'a pas lancé le test")
    run = next(unit for unit in frame.units if unit.predicate == "EXECUTE")
    candidate = candidates[run.id]

    assert candidate.event_ref.event_kind is EventKind.ACTION
    assert candidate.occurrence_status is OccurrenceStatus.NEGATED
    assert candidate.occurrence_status is not OccurrenceStatus.ASSERTED_OCCURRED


def test_conditional_action_creates_conditional_candidate():
    frame, candidates = _candidate_by_predicate("si tu lances le test, alors prépare le rapport")
    run = next(unit for unit in frame.units if unit.predicate == "EXECUTE")
    candidate = candidates[run.id]

    assert candidate.event_ref.event_kind is EventKind.ACTION
    assert candidate.occurrence_status in {OccurrenceStatus.CONDITIONAL, OccurrenceStatus.HYPOTHETICAL}
    assert candidate.occurrence_status is not OccurrenceStatus.ASSERTED_OCCURRED


def test_modal_possibility_never_becomes_asserted_occurred():
    frame, candidates = _candidate_by_predicate("Paul peut lancer le test")
    run = next(unit for unit in frame.units if unit.predicate == "EXECUTE")
    candidate = candidates[run.id]

    assert candidate.event_ref.event_kind is EventKind.ACTION
    assert candidate.occurrence_status in {OccurrenceStatus.UNCERTAIN, OccurrenceStatus.HYPOTHETICAL}
    assert candidate.occurrence_status is not OccurrenceStatus.ASSERTED_OCCURRED


def test_report_predicate_creates_report_event():
    frame, candidates = _candidate_by_predicate("Paul dit que Marie lance le test")
    say = next(unit for unit in frame.units if unit.predicate == "SAY")

    assert candidates[say.id].event_ref.event_kind is EventKind.REPORT


def test_belief_predicate_creates_belief_event():
    frame, candidates = _candidate_by_predicate("je pense que tu peux lancer le test")
    belief = next(unit for unit in frame.units if unit.predicate == "BELIEVE")

    assert candidates[belief.id].event_ref.event_kind is EventKind.BELIEF


def test_unsupported_observation_and_acquisition_are_not_invented():
    for text in (
        "j'ai appris aujourd'hui que Paul avait lancé le test hier",
        "j'ai vu le test échouer",
    ):
        candidates = extract_event_candidates(parse_utterance(text))
        kinds = {candidate.event_ref.event_kind for candidate in candidates}
        assert EventKind.OBSERVATION not in kinds
        assert EventKind.KNOWLEDGE_ACQUISITION not in kinds


def test_event_id_is_deterministic_frame_local_and_distinct_from_predicate_id():
    frame = parse_utterance("Paul a lancé le test")
    first = extract_event_candidates(frame)
    second = extract_event_candidates(frame)

    assert [candidate.event_ref.event_id for candidate in first] == [candidate.event_ref.event_id for candidate in second]
    for candidate in first:
        assert candidate.event_ref.event_id != candidate.predicate_ref
        assert candidate.event_ref.metadata["event_id_scope"] == "frame_local"
        assert candidate.event_ref.metadata["extraction_version"] == "event_extraction_v0"


def test_zero_or_one_event_ref_per_predicate_unit():
    frame = parse_utterance("Paul dit que Marie lance le test puis je pense que Paul peut lancer le test")
    candidates = extract_event_candidates(frame)
    predicate_refs = [candidate.predicate_ref for candidate in candidates]

    assert len(predicate_refs) == len(set(predicate_refs))
    assert set(predicate_refs) <= {unit.id for unit in frame.units}


def test_extracted_event_can_be_referenced_by_independent_flow_families():
    frame = parse_utterance("Paul a lancé le test")
    event = extract_event_candidates(frame)[0].event_ref
    flows = (
        OrderedMeaningFlow(
            family=FlowFamily.TEMPORAL_ORDER,
            source_object=event.event_id,
            state="UNRESOLVED_RELATIVE",
            relation_type="EVENT_TIME",
            provenance={"source": "unit-test"},
            confidence={},
            metadata={"flow_id": "f-temporal"},
        ),
        OrderedMeaningFlow(
            family=FlowFamily.EPISTEMIC_STATE,
            source_object=event.event_id,
            state="REPORTED",
            relation_type="STATE",
            provenance={"source": "unit-test"},
            confidence={},
            metadata={"flow_id": "f-epistemic"},
        ),
        OrderedMeaningFlow(
            family=FlowFamily.GOVERNANCE_STATE,
            source_object=event.event_id,
            state="MENTIONED",
            relation_type="STATE",
            provenance={"source": "unit-test"},
            confidence={},
            metadata={"flow_id": "f-governance"},
        ),
    )

    assert {flow.source_object for flow in flows} == {event.event_id}
    assert all(flow.metadata["flow_id"] != event.event_id for flow in flows)
