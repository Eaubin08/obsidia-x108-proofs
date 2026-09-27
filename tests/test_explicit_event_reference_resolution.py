from __future__ import annotations

from dataclasses import replace

import pytest

from app.semantic.lattice.event_coreference import ResolutionStatus, TargetKind
from app.semantic.lattice.event_extraction import EventCandidate, OccurrenceStatus, extract_event_candidates
from app.semantic.lattice.event_reference_resolution import resolve_explicit_event_references
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.observation_event_extraction import extract_observation_event_targets


def _unit_id(frame, predicate: str) -> str:
    matches = [unit.id for unit in frame.units if unit.predicate == predicate]
    assert len(matches) == 1, (predicate, [unit.predicate for unit in frame.units])
    return matches[0]


def _candidate_for(candidates, predicate_ref: str) -> EventCandidate:
    matches = [candidate for candidate in candidates if candidate.predicate_ref == predicate_ref]
    assert len(matches) == 1
    return matches[0]


def _with_observations(frame):
    candidates = extract_event_candidates(frame)
    observation = extract_observation_event_targets(frame, candidates)
    return tuple(candidates) + tuple(observation.observation_events), observation


def _only_reference(result):
    assert len(result.references) == 1
    return result.references[0]


def _assert_not_bound(ref) -> None:
    assert ref.resolution_status is not ResolutionStatus.RESOLVED_STRUCTURAL
    assert ref.target_event is None
    assert ref.target_predicate is None


# L. True positives: compatible prior occurrence, same frame, proper ordering.

def test_specific_launch_nominal_binds_to_prior_launch_event():
    frame = parse_utterance("Paul a lancé le test. J'ai observé ce lancement.")
    candidates = extract_event_candidates(frame)
    launch = _candidate_for(candidates, _unit_id(frame, "EXECUTE"))
    ref = _only_reference(resolve_explicit_event_references(frame, candidates))

    assert ref.target_kind is TargetKind.EVENT_TARGET
    assert ref.resolution_status is ResolutionStatus.RESOLVED_STRUCTURAL
    assert ref.target_event == launch.event_ref.event_id
    assert ref.target_predicate == launch.predicate_ref
    assert ref.provenance["surface_reference"] == "ce lancement"
    assert ref.provenance["antecedent_span"][1] < ref.provenance["reference_span"][0]
    assert ref.provenance["frame_ref"] == launch.event_ref.source_frame
    assert ref.metadata["antecedent_occurrence_status"] == OccurrenceStatus.ASSERTED_OCCURRED.value
    assert ref.metadata["occurrence_conflict"] is False
    assert ref.metadata["coreference_confidence"] < 1


def test_specific_launch_nominal_binds_across_coordinated_clause():
    frame = parse_utterance("Paul a lancé le test et j'ai observé ce lancement.")
    candidates = extract_event_candidates(frame)
    ref = _only_reference(resolve_explicit_event_references(frame, candidates))

    assert ref.resolution_status is ResolutionStatus.RESOLVED_STRUCTURAL
    assert ref.target_predicate == _unit_id(frame, "EXECUTE")


def test_reported_antecedent_binds_but_preserves_reported_status():
    frame = parse_utterance("Paul dit que Marie a lancé le test. J'ai observé ce lancement.")
    candidates = extract_event_candidates(frame)
    launch = _candidate_for(candidates, _unit_id(frame, "EXECUTE"))
    assert launch.occurrence_status is OccurrenceStatus.REPORTED
    ref = _only_reference(resolve_explicit_event_references(frame, candidates))

    assert ref.resolution_status is ResolutionStatus.RESOLVED_STRUCTURAL
    assert ref.target_event == launch.event_ref.event_id
    assert ref.metadata["antecedent_occurrence_status"] == OccurrenceStatus.REPORTED.value
    assert ref.metadata["occurrence_promoted"] is False


def test_meta_event_reference_binds_to_observation_not_inner_action():
    frame = parse_utterance("Paul dit qu'il a vu Marie lancer le test. Marie a rapporté cette observation.")
    all_candidates, observation = _with_observations(frame)
    ref = _only_reference(resolve_explicit_event_references(frame, all_candidates))

    assert ref.resolution_status is ResolutionStatus.RESOLVED_STRUCTURAL
    assert ref.target_event == observation.observation_events[0].event_ref.event_id
    assert ref.target_event != observation.targets[0].target_event


# A / J. Generic nominal policy: cardinality is never evidence.

@pytest.mark.parametrize("noun", ["cet événement", "cette action", "cette opération", "cette décision"])
def test_generic_nominal_with_single_candidate_is_not_resolved(noun):
    frame = parse_utterance(f"Paul a lancé le test. J'ai observé {noun}.")
    candidates = extract_event_candidates(frame)
    assert len(candidates) == 1
    ref = _only_reference(resolve_explicit_event_references(frame, candidates))

    _assert_not_bound(ref)
    assert ref.resolution_status in {ResolutionStatus.AMBIGUOUS, ResolutionStatus.UNRESOLVED}


def test_generic_nominal_with_multiple_candidates_is_ambiguous():
    frame = parse_utterance("Paul a lancé le build et Paul a lancé le test. J'ai observé cet événement.")
    candidates = extract_event_candidates(frame)
    assert len(candidates) == 2
    result = resolve_explicit_event_references(frame, candidates)
    ref = _only_reference(result)

    assert ref.resolution_status is ResolutionStatus.AMBIGUOUS
    assert ref.target_event is None
    assert result.metadata["LATEST_EVENT_BINDINGS"] == 0


# B. Cataphora.

def test_cataphoric_reference_is_unresolved():
    frame = parse_utterance("J'ai observé ce lancement. Paul a lancé le test.")
    candidates = extract_event_candidates(frame)
    ref = _only_reference(resolve_explicit_event_references(frame, candidates))

    _assert_not_bound(ref)
    assert ref.resolution_status is ResolutionStatus.UNRESOLVED


# C. world_action is not "lancement".

def test_delete_does_not_satisfy_launch_nominal():
    frame = parse_utterance("Paul a supprimé le fichier. Marie a rapporté ce lancement.")
    candidates = extract_event_candidates(frame)
    assert len(candidates) == 1
    ref = _only_reference(resolve_explicit_event_references(frame, candidates))

    _assert_not_bound(ref)
    assert ref.resolution_status is ResolutionStatus.UNRESOLVED


# D. Identifiers carry no meaning.

def test_candidate_without_frame_unit_is_unresolved_despite_semantic_looking_id():
    frame = parse_utterance("Paul a lancé le test. J'ai observé ce lancement.")
    real = extract_event_candidates(frame)[0]
    forged = replace(
        real,
        predicate_ref="u_launch_run_fail",
        event_ref=replace(real.event_ref, event_id="event:launch-run-fail-execute", predicate_ref="u_launch_run_fail"),
    )
    ref = _only_reference(resolve_explicit_event_references(frame, (forged,)))

    _assert_not_bound(ref)
    assert ref.resolution_status is ResolutionStatus.UNRESOLVED


def test_semantic_looking_event_id_on_incompatible_unit_is_ignored():
    frame = parse_utterance("Paul a supprimé le fichier. J'ai observé ce lancement.")
    real = extract_event_candidates(frame)[0]
    relabelled = replace(real, event_ref=replace(real.event_ref, event_id="event:launch-run-execute"))
    ref = _only_reference(resolve_explicit_event_references(frame, (relabelled,)))

    _assert_not_bound(ref)


def test_failure_nominal_without_parser_backed_failure_event_is_unresolved():
    frame = parse_utterance("Le test a échoué. J'ai observé cet échec.")
    ref = _only_reference(resolve_explicit_event_references(frame, extract_event_candidates(frame)))

    _assert_not_bound(ref)


# E / F. Occurrence status participates in resolution.

@pytest.mark.parametrize("raw, expected_status", [
    ("Paul n'a pas lancé le test. J'ai observé ce lancement.", OccurrenceStatus.NEGATED),
    ("Paul lancera le test. J'ai observé ce lancement.", OccurrenceStatus.FUTURE),
    ("Paul pourrait lancer le test. J'ai observé ce lancement.", OccurrenceStatus.UNCERTAIN),
    ("Paul aurait lancé le test. J'ai observé ce lancement.", OccurrenceStatus.UNKNOWN),
])
def test_non_occurred_parser_antecedent_is_flagged_not_silently_bound(raw, expected_status):
    frame = parse_utterance(raw)
    candidates = extract_event_candidates(frame)
    assert _candidate_for(candidates, _unit_id(frame, "EXECUTE")).occurrence_status is expected_status
    ref = _only_reference(resolve_explicit_event_references(frame, candidates))

    _assert_not_bound(ref)
    assert ref.metadata["occurrence_conflict"] is True
    assert ref.metadata["antecedent_occurrence_status"] == expected_status.value


@pytest.mark.parametrize("status", [OccurrenceStatus.HYPOTHETICAL, OccurrenceStatus.CONDITIONAL])
def test_hypothetical_and_conditional_antecedents_are_flagged(status):
    frame = parse_utterance("Paul a lancé le test. J'ai observé ce lancement.")
    real = extract_event_candidates(frame)[0]
    ref = _only_reference(resolve_explicit_event_references(frame, (replace(real, occurrence_status=status),)))

    _assert_not_bound(ref)
    assert ref.metadata["occurrence_conflict"] is True


# G / H. "fait" is proposition-oriented; "le fait que" is not a reference.

def test_generic_fact_is_proposition_oriented_and_not_event_bound():
    frame = parse_utterance("Paul a lancé le test. J'ai observé ce fait.")
    ref = _only_reference(resolve_explicit_event_references(frame, extract_event_candidates(frame)))

    _assert_not_bound(ref)
    assert ref.target_kind is TargetKind.PROPOSITION_TARGET


def test_generic_fact_without_candidate_remains_unresolved():
    frame = parse_utterance("Le build a cassé. Ce fait a été signalé.")
    ref = _only_reference(resolve_explicit_event_references(frame, ()))

    assert ref.target_kind is TargetKind.PROPOSITION_TARGET
    assert ref.resolution_status is ResolutionStatus.UNRESOLVED
    assert ref.target_event is None


@pytest.mark.parametrize("raw", [
    "Marie a vu le fait que Paul a lancé le test.",
    "Paul a lancé le test. Marie a observé ce fait que tout le monde connaît.",
    "Paul a lancé le test. Marie a observé ce fait qu'on connaît.",
])
def test_fait_que_construction_is_not_extracted(raw):
    frame = parse_utterance(raw)
    result = resolve_explicit_event_references(frame, extract_event_candidates(frame))

    assert result.references == ()


def test_definite_articles_are_not_event_anaphor_markers():
    frame = parse_utterance("Paul a lancé le test. Marie a observé le lancement.")
    result = resolve_explicit_event_references(frame, extract_event_candidates(frame))

    assert result.references == ()


# I / cross-frame. Scope must be confirmed, not assumed.

def test_source_frame_none_is_not_local():
    frame = parse_utterance("Paul a lancé le test. J'ai observé ce lancement.")
    real = extract_event_candidates(frame)[0]
    unscoped = replace(real, event_ref=replace(real.event_ref, source_frame=None))
    ref = _only_reference(resolve_explicit_event_references(frame, (unscoped,)))

    _assert_not_bound(ref)
    assert ref.resolution_status is ResolutionStatus.UNRESOLVED


def test_cross_message_boundary_is_unsupported():
    antecedent_frame = parse_utterance("Paul a lancé le test.")
    candidates = extract_event_candidates(antecedent_frame)
    reference_frame = parse_utterance("J'ai observé ce lancement.")
    result = resolve_explicit_event_references(reference_frame, candidates)

    assert _only_reference(result).resolution_status is ResolutionStatus.UNRESOLVED
    assert result.metadata["CROSS_MESSAGE_BINDINGS"] == 0


def test_foreign_frame_candidate_with_colliding_unit_id_is_rejected():
    foreign = extract_event_candidates(parse_utterance("Paul a lancé le test."))
    frame = parse_utterance("Paul a lancé le build. J'ai observé ce lancement.")
    assert foreign[0].predicate_ref == _unit_id(frame, "EXECUTE")
    ref = _only_reference(resolve_explicit_event_references(frame, foreign))

    _assert_not_bound(ref)


# K. Governing / self event exclusion.

@pytest.mark.parametrize("raw", ["J'ai observé cette observation.", "J'ai observé cet événement."])
def test_governing_event_is_never_its_own_antecedent(raw):
    frame = parse_utterance(raw)
    all_candidates, observation = _with_observations(frame)
    assert len(observation.observation_events) == 1
    ref = _only_reference(resolve_explicit_event_references(frame, all_candidates))

    _assert_not_bound(ref)


# Generic pronouns stay out of scope.

def test_generic_pronouns_remain_unsupported():
    antecedent = extract_event_candidates(parse_utterance("Paul a lancé le test."))
    for raw in ("je l'ai vu", "je l'ai appris", "j'ai vu ça", "j'en ai parlé", "cela a été vu"):
        result = resolve_explicit_event_references(parse_utterance(raw), antecedent)

        assert result.references == ()
        assert result.metadata["GENERIC_PRONOUN_EVENT_RESOLUTION"] == 0


# Adversarial matrix V2.

_OCCURRED_OK = {OccurrenceStatus.ASSERTED_OCCURRED.value, OccurrenceStatus.REPORTED.value}


def _case(kind: str, i: int):
    """Return (frame, candidates, allowed_target_events) for one adversarial case."""
    def base(raw):
        frame = parse_utterance(raw)
        return frame, tuple(extract_event_candidates(frame))

    if kind == "tp_launch":
        frame, cands = base(f"Paul a lancé le test {i}. J'ai observé ce lancement.")
        return frame, cands, {_candidate_for(cands, _unit_id(frame, "EXECUTE")).event_ref.event_id}
    if kind == "tp_coordinated":
        frame, cands = base(f"Paul a lancé le test {i} et j'ai observé ce lancement.")
        return frame, cands, {_candidate_for(cands, _unit_id(frame, "EXECUTE")).event_ref.event_id}
    if kind == "tp_reported":
        frame, cands = base(f"Paul dit que Marie a lancé le test {i}. J'ai observé ce lancement.")
        return frame, cands, {_candidate_for(cands, _unit_id(frame, "EXECUTE")).event_ref.event_id}
    if kind == "tp_meta":
        frame = parse_utterance(f"Paul dit qu'il a vu Marie lancer le test {i}. Marie a rapporté cette observation.")
        cands, observation = _with_observations(frame)
        return frame, cands, {observation.observation_events[0].event_ref.event_id}
    if kind == "tp_launch_with_meta":
        frame = parse_utterance(f"Paul a lancé le test {i}. J'ai observé ce lancement.")
        cands, _ = _with_observations(frame)
        return frame, cands, {_candidate_for(cands, _unit_id(frame, "EXECUTE")).event_ref.event_id}
    if kind == "generic_single":
        noun = ("cet événement", "cette action", "cette opération", "cette décision")[i % 4]
        frame, cands = base(f"Paul a lancé le test {i}. J'ai observé {noun}.")
        return frame, cands, set()
    if kind == "generic_multi":
        frame, cands = base(f"Paul a lancé le build {i} et Paul a lancé le test {i}. J'ai observé cet événement.")
        return frame, cands, set()
    if kind == "generic_with_meta":
        frame = parse_utterance(f"Paul a lancé le test {i}. J'ai observé cet événement.")
        cands, _ = _with_observations(frame)
        return frame, cands, set()
    if kind == "cataphora":
        frame, cands = base(f"J'ai observé ce lancement. Paul a lancé le test {i}.")
        return frame, cands, set()
    if kind == "self":
        frame = parse_utterance(("J'ai observé cette observation {i}.", "J'ai observé cet événement {i}.")[i % 2].format(i=i))
        cands, _ = _with_observations(frame)
        return frame, cands, set()
    if kind == "negated":
        frame, cands = base(f"Paul n'a pas lancé le test {i}. J'ai observé ce lancement.")
        return frame, cands, set()
    if kind == "future":
        frame, cands = base(f"Paul lancera le test {i}. J'ai observé ce lancement.")
        return frame, cands, set()
    if kind == "unknown":
        raw = (f"Paul aurait lancé le test {i}. J'ai observé ce lancement.",
               f"Paul va lancer le test {i}. J'ai observé ce lancement.",
               f"Paul pourrait lancer le test {i}. J'ai observé ce lancement.")[i % 3]
        frame, cands = base(raw)
        return frame, cands, set()
    if kind == "hypothetical":
        frame, cands = base(f"Paul a lancé le test {i}. J'ai observé ce lancement.")
        status = (OccurrenceStatus.HYPOTHETICAL, OccurrenceStatus.CONDITIONAL)[i % 2]
        return frame, tuple(replace(c, occurrence_status=status) for c in cands), set()
    if kind == "unit_none":
        frame, cands = base(f"Paul a lancé le test {i}. J'ai observé {('ce lancement', 'cet échec', 'cet arrêt')[i % 3]}.")
        forged = tuple(
            replace(c, predicate_ref=f"u_fail_run_{i}",
                    event_ref=replace(c.event_ref, predicate_ref=f"u_fail_run_{i}", event_id=f"event:launch-fail-stop-{i}"))
            for c in cands
        )
        return frame, forged, set()
    if kind == "semantic_id":
        frame, cands = base(f"Paul a supprimé le fichier {i}. J'ai observé ce lancement.")
        return frame, tuple(replace(c, event_ref=replace(c.event_ref, event_id=f"event:launch-run-{i}")) for c in cands), set()
    if kind == "delete":
        frame, cands = base(f"Paul a supprimé le fichier {i}. Marie a rapporté ce lancement.")
        return frame, cands, set()
    if kind == "pronoun":
        raw = (f"je l'ai vu {i}", f"j'ai vu ça {i}", f"j'en ai parlé {i}", f"je l'ai appris {i}")[i % 4]
        frame = parse_utterance(raw)
        return frame, tuple(extract_event_candidates(parse_utterance(f"Paul a lancé le test {i}."))), set()
    if kind == "fait_que":
        frame, cands = base(f"Paul a lancé le test {i}. Marie a vu le fait que Paul a lancé le test {i}.")
        return frame, cands, set()
    if kind == "ce_fait":
        frame, cands = base(f"Paul a lancé le test {i}. J'ai observé ce fait.")
        return frame, cands, set()
    if kind == "none_frame":
        frame, cands = base(f"Paul a lancé le test {i}. J'ai observé ce lancement.")
        return frame, tuple(replace(c, event_ref=replace(c.event_ref, source_frame=None)) for c in cands), set()
    if kind == "different_frame":
        foreign = tuple(extract_event_candidates(parse_utterance(f"Paul a lancé le test {i}.")))
        frame = parse_utterance(f"Paul a lancé le build {i}. J'ai observé ce lancement.")
        return frame, foreign, set()
    raise AssertionError(kind)


_MATRIX_KINDS = (
    "tp_launch", "tp_coordinated", "tp_reported", "tp_meta", "tp_launch_with_meta",
    "generic_single", "generic_multi", "generic_with_meta", "cataphora", "self",
    "negated", "future", "unknown", "hypothetical", "unit_none", "semantic_id",
    "delete", "pronoun", "fait_que", "ce_fait", "none_frame", "different_frame",
)

_KIND_METRIC = {
    "generic_single": "ONLY_EVENT_HEURISTIC_BINDINGS",
    "generic_with_meta": "ONLY_EVENT_HEURISTIC_BINDINGS",
    "generic_multi": "ONLY_EVENT_HEURISTIC_BINDINGS",
    "cataphora": "CATAPHORIC_BINDINGS",
    "self": "SELF_BINDINGS",
    "unit_none": "ID_SUBSTRING_BINDINGS",
    "semantic_id": "ID_SUBSTRING_BINDINGS",
    "delete": "FALSE_LAUNCH_BINDINGS",
    "negated": "NEGATED_SILENT_BINDINGS",
    "future": "HYPOTHETICAL_SILENT_BINDINGS",
    "unknown": "HYPOTHETICAL_SILENT_BINDINGS",
    "hypothetical": "HYPOTHETICAL_SILENT_BINDINGS",
    "none_frame": "UNKNOWN_SCOPE_BINDINGS",
    "pronoun": "GENERIC_PRONOUN_BINDINGS",
    "fait_que": "LE_FAIT_QUE_BINDINGS",
    "ce_fait": "FALSE_EVENT_BINDINGS",
    "different_frame": "CROSS_FRAME_BINDINGS",
}


def test_adversarial_matrix_v2_keeps_reference_boundaries():
    metrics = dict.fromkeys((
        "CASES", "TRUE_POSITIVE_BINDINGS", "FALSE_EVENT_BINDINGS", "ONLY_EVENT_HEURISTIC_BINDINGS",
        "CATAPHORIC_BINDINGS", "SELF_BINDINGS", "ID_SUBSTRING_BINDINGS", "FALSE_LAUNCH_BINDINGS",
        "NEGATED_SILENT_BINDINGS", "HYPOTHETICAL_SILENT_BINDINGS", "UNKNOWN_SCOPE_BINDINGS",
        "GENERIC_PRONOUN_BINDINGS", "LE_FAIT_QUE_BINDINGS", "CROSS_FRAME_BINDINGS", "META_EVENT_FLATTENING",
        "MISSED_TRUE_POSITIVES",
    ), 0)

    for i in range(140):
        for kind in _MATRIX_KINDS:
            frame, candidates, allowed = _case(kind, i)
            result = resolve_explicit_event_references(frame, candidates)
            metrics["CASES"] += 1
            if kind in {"pronoun", "fait_que"}:
                fait_or_pronoun_refs = [r for r in result.references if kind == "pronoun" or "fait" in r.provenance["surface_reference"]]
                metrics[_KIND_METRIC[kind]] += len(fait_or_pronoun_refs)
            bound = [r for r in result.references if r.target_event is not None]
            for ref in bound:
                assert ref.resolution_status is ResolutionStatus.RESOLVED_STRUCTURAL
                if ref.target_event in allowed:
                    assert ref.metadata["antecedent_occurrence_status"] in _OCCURRED_OK
                    assert ref.metadata["occurrence_conflict"] is False
                    metrics["TRUE_POSITIVE_BINDINGS"] += 1
                else:
                    metrics["FALSE_EVENT_BINDINGS"] += 1
                    metrics[_KIND_METRIC.get(kind, "FALSE_EVENT_BINDINGS")] += 1
                if kind == "tp_meta" and ref.target_event not in allowed:
                    metrics["META_EVENT_FLATTENING"] += 1
            if allowed and not any(r.target_event in allowed for r in bound):
                metrics["MISSED_TRUE_POSITIVES"] += 1

    assert metrics["CASES"] >= 3000
    assert metrics["TRUE_POSITIVE_BINDINGS"] > 0
    assert metrics["MISSED_TRUE_POSITIVES"] == 0
    for key, value in metrics.items():
        if key not in {"CASES", "TRUE_POSITIVE_BINDINGS"}:
            assert value == 0, (key, metrics)
