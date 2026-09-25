"""Safe projection from language lattice objects to OrderedMeaningFlow."""
from __future__ import annotations

from app.semantic.lattice import parse_utterance
from app.semantic.lattice.ordered_meaning_flow import FlowFamily
from app.semantic.lattice.language_flow_projection import (
    project_causal_flows,
    project_epistemic_flows,
    project_governance_flows,
    project_ordered_flows,
    project_temporal_flows,
)


def _states(flows, family=None):
    return {
        flow.state
        for flow in flows
        if family is None or flow.family is family
    }


def _relation_types(flows, family=None):
    return {
        flow.relation_type
        for flow in flows
        if family is None or flow.family is family
    }


def _flows_for(text: str):
    return project_ordered_flows(parse_utterance(text))


def test_precedes_projects_to_temporal_before_only():
    frame = parse_utterance("prépare le build puis lance le test")
    flows = project_ordered_flows(frame)
    temporal = project_temporal_flows(frame)

    assert any(
        flow.family is FlowFamily.TEMPORAL_ORDER
        and flow.relation_type == "BEFORE"
        and flow.source_object == "u1"
        and flow.target_object == "u2"
        for flow in temporal
    )
    assert "BEFORE" in _relation_types(flows, FlowFamily.TEMPORAL_ORDER)
    assert not any(flow.family is FlowFamily.CAUSAL_CLAIM for flow in flows)


def test_cause_relation_projects_as_linguistic_claim_never_proof():
    flows = _flows_for("lance les tests parce que le script a changé")
    causal = [flow for flow in flows if flow.family is FlowFamily.CAUSAL_CLAIM]

    assert any(flow.relation_type == "CAUSES" for flow in causal)
    assert all(flow.metadata["claim_level"] == "LINGUISTIC_CAUSAL_CLAIM" for flow in causal)
    assert all(flow.relation_type != "VALIDATED_CAUSAL_PROOF" for flow in causal)
    assert all(flow.metadata.get("validated_proof") is False for flow in causal)


def test_condition_relation_projects_as_condition_not_cause():
    flows = _flows_for("si le test passe, alors pousse le code")
    causal = [flow for flow in flows if flow.family is FlowFamily.CAUSAL_CLAIM]

    assert any(flow.relation_type == "CONDITIONS" for flow in causal)
    assert not any(flow.relation_type == "CAUSES" for flow in causal)
    assert all(flow.metadata["claim_level"] == "LINGUISTIC_CAUSAL_CLAIM" for flow in causal)


def test_believed_action_projects_epistemic_not_governance_request():
    flows = _flows_for("je pense que tu peux lancer le test")

    assert "BELIEVED" in _states(flows, FlowFamily.EPISTEMIC_STATE)
    assert "REQUESTED" not in _states(flows, FlowFamily.GOVERNANCE_STATE)
    assert "REQUESTED_CANDIDATE" not in _states(flows, FlowFamily.GOVERNANCE_STATE)


def test_reported_action_projects_reported_not_verified():
    flows = _flows_for("on m'a dit que tu pouvais lancer le test")

    assert "REPORTED" in _states(flows, FlowFamily.EPISTEMIC_STATE)
    assert "VERIFIED" not in _states(flows, FlowFamily.EPISTEMIC_STATE)
    assert "REQUESTED" not in _states(flows, FlowFamily.GOVERNANCE_STATE)


def test_direct_request_projects_requested_governance():
    flows = _flows_for("lance le test")
    gov = [flow for flow in flows if flow.family is FlowFamily.GOVERNANCE_STATE]

    assert any(flow.state == "REQUESTED" and flow.source_object == "u1" for flow in gov)
    assert "AUTHORIZED" not in _states(gov)
    assert "EXECUTED" not in _states(gov)


def test_ambiguous_request_projects_requested_candidate_and_preserves_ambiguity():
    frame = parse_utterance("tu peux lancer le test ?")
    flows = project_ordered_flows(frame)
    gov = [flow for flow in flows if flow.family is FlowFamily.GOVERNANCE_STATE]

    assert any(flow.state == "REQUESTED_CANDIDATE" for flow in gov)
    assert "REQUESTED" not in _states(gov)
    assert any("ability_permission_or_request" in item for item in frame.ambiguities)
    assert any(
        any("ability_permission_or_request" in item for item in flow.metadata.get("ambiguities", ()))
        for flow in gov
    )


def test_speaker_permission_question_does_not_project_requested():
    flows = _flows_for("je peux lancer le test ?")

    assert "REQUESTED" not in _states(flows, FlowFamily.GOVERNANCE_STATE)
    assert "REQUESTED_CANDIDATE" not in _states(flows, FlowFamily.GOVERNANCE_STATE)


def test_explanation_content_does_not_request_embedded_run():
    flows = _flows_for("explique comment lancer le test")
    execute_flows = [flow for flow in flows if flow.source_object == "u2"]

    assert "REQUESTED" not in _states(execute_flows, FlowFamily.GOVERNANCE_STATE)
    assert "REQUESTED_CANDIDATE" not in _states(execute_flows, FlowFamily.GOVERNANCE_STATE)


def test_temporal_context_run_is_not_requested():
    flows = _flows_for("avant de lancer le test, vérifie le build")
    run_flows = [flow for flow in flows if flow.source_object == "u1"]

    assert "REQUESTED" not in _states(run_flows, FlowFamily.GOVERNANCE_STATE)
    assert "REQUESTED_CANDIDATE" not in _states(run_flows, FlowFamily.GOVERNANCE_STATE)


def test_language_projection_never_creates_memory_lifecycle_flows():
    examples = [
        "prépare le build puis lance le test",
        "lance les tests parce que le script a changé",
        "si le test passe, alors pousse le code",
        "je pense que tu peux lancer le test",
        "on m'a dit que tu pouvais lancer le test",
        "lance le test",
        "tu peux lancer le test ?",
        "je peux lancer le test ?",
        "explique comment lancer le test",
        "avant de lancer le test, vérifie le build",
    ]

    for text in examples:
        assert not any(flow.family is FlowFamily.MEMORY_LIFECYCLE for flow in _flows_for(text))


def test_same_object_can_participate_in_temporal_epistemic_and_governance_flows():
    frame = parse_utterance("je pense que tu peux lancer le test puis lance le test")
    flows = project_ordered_flows(frame)
    by_source = {}
    for flow in flows:
        by_source.setdefault(flow.source_object, set()).add(flow.family)

    assert any(
        {FlowFamily.TEMPORAL_ORDER, FlowFamily.EPISTEMIC_STATE, FlowFamily.GOVERNANCE_STATE}
        <= families
        for families in by_source.values()
    )
    assert all("predicate" not in flow.to_dict() for flow in flows)
    assert all("object_payload" not in flow.to_dict() for flow in flows)


def test_cross_family_collision_guards():
    flows = _flows_for("je pense que tu peux lancer le test puis lance les tests parce que le script a changé")

    assert all(
        flow.family is FlowFamily.TEMPORAL_ORDER
        for flow in flows
        if flow.relation_type == "BEFORE"
    )
    assert all(
        flow.family is FlowFamily.CAUSAL_CLAIM
        for flow in flows
        if flow.relation_type in {"CAUSES", "CONDITIONS", "PREVENTS"}
    )
    assert all(
        flow.family is FlowFamily.EPISTEMIC_STATE
        for flow in flows
        if flow.state == "BELIEVED"
    )
    assert all(
        flow.family is FlowFamily.GOVERNANCE_STATE
        for flow in flows
        if flow.state in {"REQUESTED", "REQUESTED_CANDIDATE"}
    )
    assert "AUTHORIZED" not in _states(flows, FlowFamily.GOVERNANCE_STATE)
    assert not any(flow.validated_proof for flow in flows)


def test_confidence_does_not_create_evidence_or_proof_flow():
    flows = _flows_for("lance le test")

    assert any(flow.confidence.get("value") is not None for flow in flows)
    assert all(flow.has_evidence is False for flow in flows)
    assert not any(flow.validated_proof for flow in flows)


def test_deictic_cues_are_metadata_not_event_or_knowledge_time():
    flows = _flows_for("hier Paul a lancé le test, je viens seulement de l'apprendre")

    assert not any(flow.relation_type == "EVENT_TIME" for flow in flows)
    assert not any(flow.relation_type == "KNOWLEDGE_ACQUISITION_TIME" for flow in flows)
    assert any(
        flow.family is FlowFamily.TEMPORAL_ORDER
        and flow.relation_type == "UTTERANCE_TIME"
        and "hier" in flow.metadata.get("deixis", ())
        for flow in flows
    )
    assert all(flow.metadata.get("object_id_scope") == "frame_local" for flow in flows)