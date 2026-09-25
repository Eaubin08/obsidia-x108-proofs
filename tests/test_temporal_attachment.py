"""Temporal cue attachment contracts for conservative EventRef bridge."""
from __future__ import annotations

from app.semantic.lattice.event_extraction import extract_event_candidates
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.temporal_attachment import (
    AttachmentStatus,
    ResolutionStatus,
    attach_temporal_cues,
)


def _attachments_for(text: str):
    frame = parse_utterance(text)
    candidates = extract_event_candidates(frame)
    return frame, candidates, attach_temporal_cues(frame, candidates)


def test_precedes_between_event_backed_predicates_attaches_relative_before():
    frame, candidates, attachments = _attachments_for("prépare le build puis lance le test")
    events = {candidate.predicate_ref: candidate.event_ref.event_id for candidate in candidates}

    before = [item for item in attachments if item.relation_type == "BEFORE"]
    assert before
    assert before[0].attachment_status is AttachmentStatus.ATTACHED
    assert before[0].resolution_status is ResolutionStatus.RELATIVE_ORDER_ONLY
    assert before[0].event_ref == events["u1"]
    assert before[0].metadata["target_event_ref"] == events["u2"]
    assert before[0].metadata["source_relation_kind"] == "PRECEDES"


def test_precedes_attachment_does_not_create_causality():
    _, _, attachments = _attachments_for("prépare le build puis lance le test")

    assert all(item.relation_type != "CAUSES" for item in attachments)
    assert all(item.metadata.get("causal_flow_invented") is not True for item in attachments)


def test_frame_global_deixis_with_two_events_stays_unresolved():
    _, _, attachments = _attachments_for("hier prépare le build puis lance le test")
    unresolved = [item for item in attachments if item.cue == "hier"]

    assert unresolved
    assert unresolved[0].attachment_status is AttachmentStatus.UNRESOLVED_TEMPORAL_CUE
    assert unresolved[0].resolution_status is ResolutionStatus.UNRESOLVED_RELATIVE
    assert unresolved[0].event_ref is None
    assert unresolved[0].predicate_ref is None


def test_single_event_frame_global_deixis_still_unresolved_without_clause_evidence():
    _, _, attachments = _attachments_for("Paul lancera le test demain")
    unresolved = [item for item in attachments if item.cue == "demain"]

    assert unresolved
    assert unresolved[0].attachment_status is AttachmentStatus.UNRESOLVED_TEMPORAL_CUE
    assert unresolved[0].event_ref is None
    assert unresolved[0].resolution_status is ResolutionStatus.UNRESOLVED_RELATIVE


def test_unknown_or_unsupported_cue_is_not_guessed():
    _, _, attachments = _attachments_for("ce matin Paul a lancé le test")

    assert not any(item.cue == "ce matin" and item.attachment_status is AttachmentStatus.ATTACHED for item in attachments)
    assert not any(item.metadata.get("nearest_predicate_fallback") is True for item in attachments)


def test_no_utterance_timestamp_or_absolute_resolution_is_created():
    _, _, attachments = _attachments_for("hier Paul a lancé le test")

    assert attachments
    assert all(item.resolution_status is not ResolutionStatus.RESOLVED_EXTERNAL for item in attachments)
    assert all("timestamp" not in item.to_dict() for item in attachments)
    assert all("resolved_time" not in item.to_dict() for item in attachments)


def test_adversarial_matrix_preserves_hard_invariants():
    templates = (
        "Paul a lancé le test {suffix}",
        "Paul n'a pas lancé le test {suffix}",
        "si tu lances le test, alors prépare le rapport {suffix}",
        "Paul peut lancer le test {suffix}",
        "Paul lancera le test {suffix}",
        "Paul dit que Marie lance le test {suffix}",
        "je pense que tu peux lancer le test {suffix}",
        "lance le test {suffix}",
        "explique pourquoi Paul lance le test {suffix}",
        "prépare le build puis lance le test {suffix}",
        "hier prépare le build puis lance le test {suffix}",
    )
    suffixes = tuple(f"cas{i}" for i in range(100))
    metrics = {
        "EVENT_CANDIDATES": 0,
        "ASSERTED_OCCURRED": 0,
        "NEGATED": 0,
        "HYPOTHETICAL": 0,
        "CONDITIONAL": 0,
        "FALSE_OCCURRED": 0,
        "OBSERVATION_INVENTED": 0,
        "KNOWLEDGE_ACQUISITION_INVENTED": 0,
        "TEMPORAL_FALSE_ATTACHMENT": 0,
        "ABSOLUTE_TIME_INVENTED": 0,
        "CAUSAL_FLOW_INVENTED": 0,
    }

    for template in templates:
        for suffix in suffixes:
            raw = template.format(suffix=suffix)
            frame = parse_utterance(raw)
            candidates = extract_event_candidates(frame)
            attachments = attach_temporal_cues(frame, candidates)
            metrics["EVENT_CANDIDATES"] += len(candidates)
            for candidate in candidates:
                metrics[candidate.occurrence_status.value] = metrics.get(candidate.occurrence_status.value, 0) + 1
                if candidate.event_ref.event_kind.value == "OBSERVATION":
                    metrics["OBSERVATION_INVENTED"] += 1
                if candidate.event_ref.event_kind.value == "KNOWLEDGE_ACQUISITION":
                    metrics["KNOWLEDGE_ACQUISITION_INVENTED"] += 1
                if candidate.occurrence_status.value == "ASSERTED_OCCURRED" and (
                    "n'a pas" in raw or raw.startswith("si ") or "peut lancer" in raw
                    or "lancera" in raw or raw.startswith("lance ")
                ):
                    metrics["FALSE_OCCURRED"] += 1
            for item in attachments:
                if item.resolution_status is ResolutionStatus.RESOLVED_EXTERNAL:
                    metrics["ABSOLUTE_TIME_INVENTED"] += 1
                if item.attachment_status is AttachmentStatus.ATTACHED and item.relation_type != "BEFORE":
                    metrics["TEMPORAL_FALSE_ATTACHMENT"] += 1
                if item.relation_type == "CAUSES":
                    metrics["CAUSAL_FLOW_INVENTED"] += 1

    assert metrics["EVENT_CANDIDATES"] >= 1000
    assert metrics["FALSE_OCCURRED"] == 0
    assert metrics["OBSERVATION_INVENTED"] == 0
    assert metrics["KNOWLEDGE_ACQUISITION_INVENTED"] == 0
    assert metrics["TEMPORAL_FALSE_ATTACHMENT"] == 0
    assert metrics["ABSOLUTE_TIME_INVENTED"] == 0
    assert metrics["CAUSAL_FLOW_INVENTED"] == 0
