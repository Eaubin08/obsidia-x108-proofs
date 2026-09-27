from __future__ import annotations

from dataclasses import replace

from app.semantic.lattice.event_coreference import ResolutionStatus, TargetKind
from app.semantic.lattice.event_extraction import EventCandidate, OccurrenceStatus, extract_event_candidates
from app.semantic.lattice.events import EventKind, EventRef
from app.semantic.lattice.event_reference_resolution import resolve_explicit_event_references
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.observation_event_extraction import extract_observation_event_targets


def _candidate(event_id: str, predicate_ref: str, kind: EventKind = EventKind.ACTION) -> EventCandidate:
    return EventCandidate(
        event_ref=EventRef(
            event_id=event_id,
            predicate_ref=predicate_ref,
            event_kind=kind,
            source_frame=None,
            provenance={"span": (0, 1), "source": "test"},
        ),
        predicate_ref=predicate_ref,
        occurrence_status=OccurrenceStatus.ASSERTED_OCCURRED,
        provenance={"span": (0, 1), "source": "test"},
    )


def test_specific_failure_nominal_binds_to_compatible_prior_event():
    frame = parse_utterance("Le test a échoué. J'ai observé cet échec.")
    failure = _candidate("event-fail", "u_fail")
    result = resolve_explicit_event_references(frame, (failure,))

    assert len(result.references) == 1
    ref = result.references[0]
    assert ref.target_kind is TargetKind.EVENT_TARGET
    assert ref.resolution_status is ResolutionStatus.RESOLVED_STRUCTURAL
    assert ref.target_event == "event-fail"
    assert ref.target_predicate == "u_fail"
    assert ref.metadata["coreference_confidence"] < 1
    assert ref.provenance["surface_reference"] == "cet échec"


def test_specific_launch_nominal_binds_to_launch_event_without_report_extraction():
    frame = parse_utterance("Paul a lancé le test. Marie a rapporté ce lancement.")
    candidates = extract_event_candidates(frame)
    result = resolve_explicit_event_references(frame, candidates)

    assert len(candidates) == 1
    assert len(result.references) == 1
    assert result.references[0].target_kind is TargetKind.EVENT_TARGET
    assert result.references[0].resolution_status is ResolutionStatus.RESOLVED_STRUCTURAL
    assert result.references[0].target_event == candidates[0].event_ref.event_id
    assert result.metadata["LATEST_EVENT_BINDINGS"] == 0


def test_generic_event_nominal_with_single_candidate_can_bind_structurally():
    frame = parse_utterance("Le système s'est arrêté. J'ai appris cet événement.")
    stop = _candidate("event-stop", "u1", EventKind.CHANGE)
    result = resolve_explicit_event_references(frame, (stop,))

    assert len(result.references) == 1
    assert result.references[0].target_kind is TargetKind.EVENT_TARGET
    assert result.references[0].resolution_status is ResolutionStatus.RESOLVED_STRUCTURAL
    assert result.references[0].target_event == "event-stop"


def test_generic_fact_without_candidate_remains_unresolved():
    frame = parse_utterance("Le build a cassé. Ce fait a été signalé.")
    result = resolve_explicit_event_references(frame, ())

    assert len(result.references) == 1
    assert result.references[0].target_kind is TargetKind.UNKNOWN_TARGET
    assert result.references[0].resolution_status is ResolutionStatus.UNRESOLVED
    assert result.references[0].target_event is None


def test_two_candidate_generic_event_reference_is_ambiguous_not_latest():
    frame = parse_utterance("Paul a lancé le build et Paul a lancé le test. J'ai observé cet événement.")
    candidates = extract_event_candidates(frame)
    result = resolve_explicit_event_references(frame, candidates)

    assert len(candidates) == 2
    assert len(result.references) == 1
    assert result.references[0].resolution_status is ResolutionStatus.AMBIGUOUS
    assert result.references[0].target_event is None
    assert result.metadata["LATEST_EVENT_BINDINGS"] == 0


def test_generic_pronouns_remain_unsupported():
    for raw in ("je l'ai vu", "je l'ai appris", "j'ai vu ça"):
        frame = parse_utterance(raw)
        result = resolve_explicit_event_references(frame, (_candidate("event-prior", "u0"),))

        assert result.references == ()
        assert result.metadata["GENERIC_PRONOUN_EVENT_RESOLUTION"] == 0


def test_meta_event_reference_binds_to_observation_not_inner_action():
    frame = parse_utterance("Paul dit qu'il a vu Marie lancer le test. Marie a rapporté cette observation.")
    action_candidates = extract_event_candidates(frame)
    observation = extract_observation_event_targets(frame, action_candidates)
    all_candidates = tuple(action_candidates) + tuple(observation.observation_events)
    result = resolve_explicit_event_references(frame, all_candidates)

    assert len(result.references) == 1
    ref = result.references[0]
    assert ref.resolution_status is ResolutionStatus.RESOLVED_STRUCTURAL
    assert ref.target_event == observation.observation_events[0].event_ref.event_id
    assert ref.target_event != observation.targets[0].target_event
    assert result.metadata["META_EVENT_FLATTENING"] == 0


def test_cross_message_boundary_is_unsupported_without_frame_local_reference():
    antecedent_frame = parse_utterance("Paul a lancé le test.")
    candidates = extract_event_candidates(antecedent_frame)
    reference_frame = parse_utterance("J'ai observé ce lancement.")
    result = resolve_explicit_event_references(reference_frame, candidates)

    assert len(result.references) == 1
    assert result.references[0].resolution_status is ResolutionStatus.UNRESOLVED
    assert result.metadata["CROSS_MESSAGE_BINDINGS"] == 0


def test_adversarial_matrix_keeps_reference_boundaries():
    templates = (
        ("Paul a lancé le test {i}. J'ai observé ce lancement.", "resolved"),
        ("Paul a lancé le build {i} et Paul a lancé le test {i}. J'ai observé cet événement.", "ambiguous"),
        ("Paul a lancé le build {i} et Paul a lancé le test {i}. J'ai observé ce fait.", "ambiguous"),
        ("Le test a échoué {i}. J'ai observé cet échec.", "synthetic_resolved"),
        ("Le système s'est arrêté {i}. J'ai appris cet arrêt.", "synthetic_resolved"),
        ("Paul a vu Marie lancer le test {i}. Marie a rapporté cette observation.", "meta"),
        ("je l'ai vu {i}", "pronoun"),
        ("j'ai vu ça {i}", "pronoun"),
        ("j'en ai parlé {i}", "pronoun"),
        ("J'ai observé cet événement {i}.", "unresolved"),
        ("Marie a rapporté cette opération {i}.", "unresolved"),
        ("Paul a lancé le test {i}.", "none"),
        ("j'ai appris que Paul a lancé le test {i}", "none"),
        ("Paul a lancé le test {i}", "cross_antecedent"),
        ("J'ai observé ce lancement {i}.", "cross_reference"),
    )
    metrics = {
        "CASES": 0,
        "EXPLICIT_REFERENCES": 0,
        "RESOLVED_STRUCTURAL": 0,
        "AMBIGUOUS": 0,
        "UNRESOLVED": 0,
        "FALSE_EVENT_BINDINGS": 0,
        "LATEST_EVENT_BINDINGS": 0,
        "PRONOUN_EVENT_BINDINGS": 0,
        "META_EVENT_FLATTENING": 0,
        "CROSS_MESSAGE_BINDINGS": 0,
    }

    cross_candidates = ()
    for idx in range(108):
        for template, kind in templates:
            raw = template.format(i=idx)
            frame = parse_utterance(raw)
            candidates = extract_event_candidates(frame)
            if kind == "synthetic_resolved":
                semantic_id = "event-fail" if "échec" in raw else "event-stop"
                candidates = tuple(candidates) + (_candidate(f"{semantic_id}-{idx}", "u_synth"),)
            if kind == "meta":
                observation = extract_observation_event_targets(frame, candidates)
                candidates = tuple(candidates) + tuple(observation.observation_events)
            if kind == "cross_antecedent":
                cross_candidates = candidates
                continue
            if kind == "cross_reference":
                candidates = cross_candidates
            result = resolve_explicit_event_references(frame, candidates)
            metrics["CASES"] += 1
            metrics["EXPLICIT_REFERENCES"] += len(result.references)
            for ref in result.references:
                if ref.resolution_status is ResolutionStatus.RESOLVED_STRUCTURAL:
                    metrics["RESOLVED_STRUCTURAL"] += 1
                if ref.resolution_status is ResolutionStatus.AMBIGUOUS:
                    metrics["AMBIGUOUS"] += 1
                if ref.resolution_status is ResolutionStatus.UNRESOLVED:
                    metrics["UNRESOLVED"] += 1
                if kind in {"pronoun", "unresolved", "cross_reference"} and ref.target_event:
                    metrics["FALSE_EVENT_BINDINGS"] += 1
            for key in (
                "LATEST_EVENT_BINDINGS",
                "PRONOUN_EVENT_BINDINGS",
                "META_EVENT_FLATTENING",
                "CROSS_MESSAGE_BINDINGS",
            ):
                metrics[key] += int(result.metadata.get(key, 0))

    assert metrics["CASES"] >= 1400
    assert metrics["EXPLICIT_REFERENCES"] >= 900
    assert metrics["RESOLVED_STRUCTURAL"] >= 400
    assert metrics["AMBIGUOUS"] >= 200
    assert metrics["UNRESOLVED"] >= 300
    assert metrics["FALSE_EVENT_BINDINGS"] == 0
    assert metrics["LATEST_EVENT_BINDINGS"] == 0
    assert metrics["PRONOUN_EVENT_BINDINGS"] == 0
    assert metrics["META_EVENT_FLATTENING"] == 0
    assert metrics["CROSS_MESSAGE_BINDINGS"] == 0
