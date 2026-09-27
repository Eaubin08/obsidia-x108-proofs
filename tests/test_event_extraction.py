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


# B1: belief context must not present the believed event as occurred.

def _statuses_by_predicate(text: str):
    frame, candidates = _candidate_by_predicate(text)
    return frame, {unit.id: (unit, candidates.get(unit.id)) for unit in frame.units}


def _only(frame, candidates, predicate: str):
    matches = [pair for pair in candidates.values() if pair[0].predicate == predicate]
    assert len(matches) == 1, (predicate, [unit.predicate for unit in frame.units])
    return matches[0]


def test_believed_past_action_is_not_asserted_occurred():
    frame, candidates = _statuses_by_predicate("Paul croit que Marie a lancé le test.")
    believe_unit, believe = _only(frame, candidates, "BELIEVE")
    run_unit, run = _only(frame, candidates, "EXECUTE")

    assert believe.event_ref.event_kind is EventKind.BELIEF
    assert believe.occurrence_status is OccurrenceStatus.ASSERTED_OCCURRED
    assert run_unit.role == "BELIEVED"
    assert run_unit.embedded_under == believe_unit.id
    assert run.occurrence_status is OccurrenceStatus.UNKNOWN
    assert run.metadata["event_occurred_claim"] is False


def test_first_person_and_penser_beliefs_are_not_asserted_occurred():
    for text in ("Je crois que Marie a lancé le test.", "Paul pense que Marie a lancé le test."):
        frame, candidates = _statuses_by_predicate(text)
        assert _only(frame, candidates, "EXECUTE")[1].occurrence_status is OccurrenceStatus.UNKNOWN


def test_belief_preserves_stronger_occurrence_signals():
    expected = {
        "Paul croit que Marie n'a pas lancé le test.": OccurrenceStatus.NEGATED,
        "Paul croit que Marie lancera le test.": OccurrenceStatus.FUTURE,
        "Paul croit que Marie pourrait lancer le test.": OccurrenceStatus.UNCERTAIN,
    }
    for text, status in expected.items():
        frame, candidates = _statuses_by_predicate(text)
        assert _only(frame, candidates, "EXECUTE")[1].occurrence_status is status, text


def test_nested_belief_keeps_immediate_nesting_and_does_not_assert_inner_action():
    frame, candidates = _statuses_by_predicate("Paul croit que Marie pense que Jean a lancé le test.")
    outer, inner = sorted(
        (pair for pair in candidates.values() if pair[0].predicate == "BELIEVE"),
        key=lambda pair: pair[0].span[0],
    )
    run_unit, run = _only(frame, candidates, "EXECUTE")

    assert inner[0].embedded_under == outer[0].id
    assert run_unit.embedded_under == inner[0].id
    assert run.occurrence_status is OccurrenceStatus.UNKNOWN
    assert inner[1].occurrence_status is not OccurrenceStatus.ASSERTED_OCCURRED


def test_belief_around_report_keeps_report_layer_and_does_not_assert():
    frame, candidates = _statuses_by_predicate("Paul croit que Marie a dit que Jean a lancé le test.")
    believe_unit, _ = _only(frame, candidates, "BELIEVE")
    say_unit, say = _only(frame, candidates, "SAY")
    run_unit, run = _only(frame, candidates, "EXECUTE")

    assert say_unit.embedded_under == believe_unit.id
    assert run_unit.embedded_under == say_unit.id
    assert say.event_ref.event_kind is EventKind.REPORT
    assert say.occurrence_status is OccurrenceStatus.UNKNOWN
    assert run.occurrence_status is OccurrenceStatus.REPORTED


def test_report_and_plain_assertion_are_unchanged():
    frame, candidates = _statuses_by_predicate("Paul dit que Marie a lancé le test.")
    assert _only(frame, candidates, "SAY")[1].occurrence_status is OccurrenceStatus.ASSERTED_OCCURRED
    assert _only(frame, candidates, "EXECUTE")[1].occurrence_status is OccurrenceStatus.REPORTED

    frame, candidates = _statuses_by_predicate("Marie a lancé le test.")
    assert _only(frame, candidates, "EXECUTE")[1].occurrence_status is OccurrenceStatus.ASSERTED_OCCURRED


def test_belief_occurrence_adversarial_matrix():
    from app.semantic.lattice.language_flow_projection import project_ordered_flows

    templates = (
        ("belief_past", "{s} croit que {o} a lancé le test {i}.", OccurrenceStatus.UNKNOWN),
        ("belief_past", "{s} pense que {o} a lancé le build {i}.", OccurrenceStatus.UNKNOWN),
        ("belief_negated", "{s} croit que {o} n'a pas lancé le test {i}.", OccurrenceStatus.NEGATED),
        ("belief_future", "{s} croit que {o} lancera le test {i}.", OccurrenceStatus.FUTURE),
        ("belief_modal", "{s} croit que {o} pourrait lancer le test {i}.", OccurrenceStatus.UNCERTAIN),
        ("belief_report", "{s} croit que {o} a dit que Jean a lancé le test {i}.", OccurrenceStatus.REPORTED),
        ("belief_nested", "{s} croit que {o} pense que Jean a lancé le test {i}.", OccurrenceStatus.UNKNOWN),
        ("report", "{s} dit que {o} a lancé le test {i}.", OccurrenceStatus.REPORTED),
        ("plain", "{o} a lancé le test {i}.", OccurrenceStatus.ASSERTED_OCCURRED),
        ("plain_negated", "{o} n'a pas lancé le test {i}.", OccurrenceStatus.NEGATED),
    )
    subjects = ("Paul", "Je", "Luc", "Anne")
    objects = ("Marie", "Paul", "Claire")
    metrics = dict.fromkeys((
        "CASES", "BELIEVED_TARGETS", "BELIEVED_ASSERTED_OCCURRED", "NEGATION_LOST", "FUTURE_LOST",
        "MODALITY_LOST", "REPORTED_CHANGED", "PLAIN_ASSERTION_CHANGED", "UNEXPECTED_STATUS",
        "VERIFIED_FLOW_CREATED", "OBSERVED_FLOW_CREATED", "AUTHORIZED_FLOW_CREATED", "EXECUTED_FLOW_CREATED",
    ), 0)
    lost_metric = {
        "belief_negated": "NEGATION_LOST",
        "plain_negated": "NEGATION_LOST",
        "belief_future": "FUTURE_LOST",
        "belief_modal": "MODALITY_LOST",
        "report": "REPORTED_CHANGED",
        "belief_report": "REPORTED_CHANGED",
        "plain": "PLAIN_ASSERTION_CHANGED",
    }

    for i in range(10):
        for subject in subjects:
            for obj in objects:
                for kind, template, expected in templates:
                    text = template.format(s=subject, o=obj, i=i)
                    if subject == "Je":
                        text = text.replace("Je croit", "Je crois").replace("Je dit", "Je dis")
                    frame, candidates = _candidate_by_predicate(text)
                    metrics["CASES"] += 1
                    runs = [unit for unit in frame.units if unit.predicate == "EXECUTE"]
                    assert len(runs) == 1, text
                    status = candidates[runs[0].id].occurrence_status
                    for unit in frame.units:
                        candidate = candidates.get(unit.id)
                        if candidate is not None and unit.pragmatic == "BELIEVED":
                            metrics["BELIEVED_TARGETS"] += 1
                            if candidate.occurrence_status is OccurrenceStatus.ASSERTED_OCCURRED:
                                metrics["BELIEVED_ASSERTED_OCCURRED"] += 1
                    if status is not expected:
                        metrics[lost_metric.get(kind, "UNEXPECTED_STATUS")] += 1
                    for flow in project_ordered_flows(frame):
                        if flow.state in {"VERIFIED", "OBSERVED", "AUTHORIZED", "EXECUTED"}:
                            metrics[f"{flow.state}_FLOW_CREATED"] += 1

    assert metrics["CASES"] >= 1000
    assert metrics["BELIEVED_TARGETS"] > 0
    for key, value in metrics.items():
        if key not in {"CASES", "BELIEVED_TARGETS"}:
            assert value == 0, (key, metrics)
