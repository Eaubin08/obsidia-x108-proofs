"""OrderedMeaningFlow V0 contract tests.

These tests freeze the next semantic architecture step without introducing the
runtime yet. Implementation-dependent expectations are intentionally red first,
then strict-xfailed until minimal primitives exist.
"""
from __future__ import annotations

import pytest

from app.router.decision import decide
from app.semantic.lattice import parse_utterance



def _ordered_flow_api():
    try:
        from app.semantic.lattice.ordered_meaning_flow import (  # type: ignore[attr-defined]
            FlowFamily,
            OrderedMeaningFlow,
            derive_ordered_meaning_flows,
            infer_family_path,
        )
    except ModuleNotFoundError as exc:
        pytest.fail(f"OrderedMeaningFlow V0 contract is missing: {exc}")
    return FlowFamily, OrderedMeaningFlow, derive_ordered_meaning_flows, infer_family_path


def _predicates(frame):
    return {unit.predicate: unit for unit in frame.units}


def test_temporal_event_time_is_distinct_from_knowledge_acquisition_time():
    FlowFamily, _, derive_ordered_meaning_flows, _ = _ordered_flow_api()
    frame = parse_utterance("hier Paul a lancé le test, je viens seulement de l'apprendre")

    flows = derive_ordered_meaning_flows(frame)
    run = _predicates(frame)["EXECUTE"]
    temporal = [f for f in flows if f.family == FlowFamily.TEMPORAL_ORDER and f.source_object == run.id]

    assert run.action_agent == "THIRD_PARTY"
    assert any(f.relation_type == "EVENT_TIME" and f.state == "yesterday" for f in temporal)
    assert any(f.relation_type == "KNOWLEDGE_ACQUISITION_TIME" and f.state == "now" for f in temporal)
    assert any(f.relation_type == "UTTERANCE_TIME" and f.state == "now" for f in temporal)
    assert not any(
        f.relation_type == "EVENT_TIME" and f.state == "now" for f in temporal
    )


def test_temporal_knowledge_sentences_are_not_system_execution_requests():
    examples = [
        "hier Paul a lancé le test, je viens seulement de l'apprendre",
        "Paul a lancé le test hier et Marie l'a appris aujourd'hui",
        "j'ai appris aujourd'hui que Paul avait lancé le test hier",
        "demain je saurai si le test a réussi aujourd'hui",
    ]
    for text in examples:
        summary = decide(text, memory_index={})
        assert summary["gate"]["verdict"] != "ALLOW"
        assert summary["ir"]["semantics"]["requested_world_actions"] == []


@pytest.mark.parametrize(
    "text,event_time,knowledge_time",
    [
        ("Paul a lancé le test hier et Marie l'a appris aujourd'hui", "yesterday", "today"),
        ("j'ai appris aujourd'hui que Paul avait lancé le test hier", "yesterday", "today"),
        ("demain je saurai si le test a réussi aujourd'hui", "today", "tomorrow"),
    ],
)
def test_temporal_contract_freezes_event_vs_knowledge_coordinates(text, event_time, knowledge_time):
    FlowFamily, _, derive_ordered_meaning_flows, _ = _ordered_flow_api()
    frame = parse_utterance(text)
    flows = derive_ordered_meaning_flows(frame)

    temporal_states = {
        (f.relation_type, f.state)
        for f in flows
        if f.family == FlowFamily.TEMPORAL_ORDER
    }
    assert ("EVENT_TIME", event_time) in temporal_states
    assert ("KNOWLEDGE_ACQUISITION_TIME", knowledge_time) in temporal_states


def test_parce_que_creates_linguistic_causal_claim_not_validated_proof():
    FlowFamily, _, derive_ordered_meaning_flows, _ = _ordered_flow_api()
    frame = parse_utterance("le test a échoué parce que le build était cassé")
    flows = derive_ordered_meaning_flows(frame)

    causal = [f for f in flows if f.family == FlowFamily.CAUSAL_CLAIM]
    assert any(f.relation_type == "LINGUISTIC_CAUSAL_CLAIM" for f in causal)
    assert not any(f.relation_type == "VALIDATED_CAUSAL_PROOF" for f in causal)


def test_reported_parce_que_creates_reported_causal_claim():
    FlowFamily, _, derive_ordered_meaning_flows, _ = _ordered_flow_api()
    frame = parse_utterance("Paul dit que le test a échoué parce que le build était cassé")
    flows = derive_ordered_meaning_flows(frame)

    causal = [f for f in flows if f.family == FlowFamily.CAUSAL_CLAIM]
    assert any(f.relation_type == "REPORTED_CAUSAL_CLAIM" for f in causal)
    assert not any(f.relation_type == "VALIDATED_CAUSAL_PROOF" for f in causal)


def test_temporal_succession_does_not_create_existing_causal_relation():
    frame = parse_utterance("le test a échoué après que le build a cassé")
    rels = {(r.kind, r.source, r.target) for r in frame.relations}
    assert all(kind != "CAUSES" for kind, _, _ in rels)


@pytest.mark.parametrize(
    "text,expected_state",
    [
        ("je pense que le test a réussi", "BELIEVED"),
        ("on m'a dit que le test a réussi", "REPORTED"),
        ("j'ai vu que le test a réussi", "OBSERVED"),
        ("les logs montrent que le test a réussi", "SUPPORTED"),
        ("le test a peut-être réussi", "UNCERTAIN"),
    ],
)
def test_epistemic_states_are_distinct(text, expected_state):
    FlowFamily, _, derive_ordered_meaning_flows, _ = _ordered_flow_api()
    frame = parse_utterance(text)
    flows = derive_ordered_meaning_flows(frame)

    epistemic_states = {
        f.state for f in flows if f.family == FlowFamily.EPISTEMIC_STATE
    }
    assert expected_state in epistemic_states


def test_epistemic_contradiction_preserves_old_belief_and_new_evidence():
    FlowFamily, _, derive_ordered_meaning_flows, _ = _ordered_flow_api()
    frame = parse_utterance("je croyais qu'il avait réussi, mais les logs montrent qu'il a échoué")
    flows = derive_ordered_meaning_flows(frame)

    epistemic = [f for f in flows if f.family == FlowFamily.EPISTEMIC_STATE]
    assert any(f.state == "BELIEVED" for f in epistemic)
    assert any(f.state == "SUPPORTED" for f in epistemic)
    assert any(f.state == "CONTRADICTED" for f in epistemic)
    assert any(f.status == "superseded_candidate" for f in epistemic)


def test_memory_lifecycle_is_descriptive_and_has_no_write_authority():
    FlowFamily, OrderedMeaningFlow, _, _ = _ordered_flow_api()

    runtime_trace = OrderedMeaningFlow(
        family=FlowFamily.MEMORY_LIFECYCLE,
        source_object="runtime-event-1",
        state="EPHEMERAL_TRACE",
        relation_type="TRACE_STATE",
        direction="state_on_source",
        scope="session",
        provenance={"source": "runtime"},
        confidence={"value": None, "calibrated": False},
        status="draft",
        metadata={"MEMORY_WRITE_AUTHORITY": False},
    )
    candidate = runtime_trace.transition("CANDIDATE_MEMORY", authority=False)
    promoted = candidate.transition("PROMOTED_MEMORY", authority=False)
    superseded = promoted.transition("SUPERSEDED_MEMORY", authority=False)

    assert runtime_trace.metadata["MEMORY_WRITE_AUTHORITY"] is False
    assert candidate.metadata["MEMORY_WRITE_AUTHORITY"] is False
    assert promoted.metadata["MEMORY_WRITE_AUTHORITY"] is False
    assert superseded.state == "SUPERSEDED_MEMORY"


def test_existing_governance_request_holds_without_authorizing_execution():
    result = decide("lance le test", memory_index={})
    assert result["gate"]["verdict"] == "HOLD"
    assert "EXECUTE" in result["ir"]["semantics"]["requested_world_actions"]


def test_past_execution_assertion_is_not_requested():
    result = decide("le test a été lancé hier", memory_index={})
    assert result["ir"]["semantics"]["requested_world_actions"] == []


def test_permission_question_is_request_candidate_but_not_allow():
    result = decide("tu peux lancer le test ?", memory_index={})
    assert result["gate"]["verdict"] == "HOLD"
    assert "EXECUTE" in result["ir"]["semantics"]["requested_world_actions"]


def test_temporal_transitivity_never_implies_causal_proof():
    FlowFamily, OrderedMeaningFlow, _, infer_family_path = _ordered_flow_api()
    flows = [
        OrderedMeaningFlow(FlowFamily.TEMPORAL_ORDER, "A", "B", None, "BEFORE", "source_to_target", "test", {}, {}, "asserted", {}),
        OrderedMeaningFlow(FlowFamily.TEMPORAL_ORDER, "B", "C", None, "BEFORE", "source_to_target", "test", {}, {}, "asserted", {}),
    ]

    temporal_path = infer_family_path(flows, family=FlowFamily.TEMPORAL_ORDER, source="A", target="C")
    causal_path = infer_family_path(flows, family=FlowFamily.CAUSAL_CLAIM, source="A", target="C")
    assert temporal_path.relation_type == "BEFORE"
    assert causal_path.connection == "NO_PROVEN_CONNECTION"


def test_linguistic_causal_claim_does_not_upgrade_to_validated_proof():
    FlowFamily, OrderedMeaningFlow, _, infer_family_path = _ordered_flow_api()
    flows = [
        OrderedMeaningFlow(FlowFamily.CAUSAL_CLAIM, "A", "B", None, "LINGUISTIC_CAUSAL_CLAIM", "source_to_target", "utterance", {}, {}, "asserted", {}),
    ]

    proof_path = infer_family_path(
        flows,
        family=FlowFamily.CAUSAL_CLAIM,
        source="A",
        target="B",
        required_relation_type="VALIDATED_CAUSAL_PROOF",
    )
    assert proof_path.connection == "NO_PROVEN_CONNECTION"


@pytest.mark.parametrize(
    "source_family,source_state,forbidden_family,forbidden_state",
    [
        ("EPISTEMIC_STATE", "OBSERVED", "MEMORY_LIFECYCLE", "CONSOLIDATED_MEMORY"),
        ("MEMORY_LIFECYCLE", "CONSOLIDATED_MEMORY", "EPISTEMIC_STATE", "VERIFIED"),
        ("GOVERNANCE_STATE", "REQUESTED", "GOVERNANCE_STATE", "AUTHORIZED"),
    ],
)
def test_cross_family_states_do_not_imply_forbidden_states(
    source_family, source_state, forbidden_family, forbidden_state
):
    FlowFamily, OrderedMeaningFlow, _, infer_family_path = _ordered_flow_api()
    flows = [
        OrderedMeaningFlow(
            getattr(FlowFamily, source_family),
            "X",
            None,
            source_state,
            "STATE",
            "state_on_source",
            "test",
            {},
            {},
            "asserted",
            {},
        )
    ]

    path = infer_family_path(
        flows,
        family=getattr(FlowFamily, forbidden_family),
        source="X",
        target=None,
        required_state=forbidden_state,
    )
    assert path.connection == "NO_PROVEN_CONNECTION"


def test_confidence_does_not_imply_evidence_exists():
    FlowFamily, OrderedMeaningFlow, _, _ = _ordered_flow_api()
    flow = OrderedMeaningFlow(
        family=FlowFamily.EPISTEMIC_STATE,
        source_object="X",
        target_object=None,
        state="CLAIMED",
        relation_type="STATE",
        direction="state_on_source",
        scope="test",
        provenance={"evidence": None},
        confidence={"value": 0.95, "calibrated": False},
        status="asserted",
        metadata={},
    )

    assert flow.confidence["value"] == 0.95
    assert flow.provenance["evidence"] is None
    assert flow.has_evidence is False
