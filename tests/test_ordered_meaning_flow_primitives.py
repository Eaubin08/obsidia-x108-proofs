"""Structural tests for OrderedMeaningFlow V0 primitives."""
from __future__ import annotations

import dataclasses
import json

import pytest

from app.semantic.lattice import parse_utterance
from app.semantic.lattice.ordered_meaning_flow import (
    FlowFamily,
    KX108_AUTHORITY,
    MEMORY_WRITE_AUTHORITY,
    OrderedMeaningFlow,
    derive_ordered_meaning_flows,
    infer_family_path,
)


def test_flow_is_immutable_and_serialization_safe():
    flow = OrderedMeaningFlow(
        family=FlowFamily.EPISTEMIC_STATE,
        source_object="RUN_TEST",
        state="CLAIMED",
        relation_type="STATE",
        provenance={"source": "unit-test"},
        confidence={"value": 0.5, "calibrated": False},
        metadata={"note": "descriptive"},
    )

    with pytest.raises(dataclasses.FrozenInstanceError):
        flow.state = "VERIFIED"  # type: ignore[misc]
    assert json.loads(json.dumps(flow.to_dict()))["source_object"] == "RUN_TEST"


def test_family_validation_rejects_illegal_cross_family_relation():
    with pytest.raises(ValueError, match="invalid temporal"):
        OrderedMeaningFlow(
            family=FlowFamily.TEMPORAL_ORDER,
            source_object="A",
            target_object="B",
            relation_type="CAUSES",
            direction="source_to_target",
            provenance={"source": "unit-test"},
            confidence={},
        )


def test_no_proven_connection_is_explicit_and_family_scoped():
    flows = [
        OrderedMeaningFlow(
            FlowFamily.EPISTEMIC_STATE,
            "X",
            None,
            "OBSERVED",
            "STATE",
            provenance={"source": "unit-test"},
            confidence={},
        )
    ]

    path = infer_family_path(
        flows,
        family=FlowFamily.MEMORY_LIFECYCLE,
        source="X",
        target=None,
        required_state="CONSOLIDATED_MEMORY",
    )
    assert path.connection == "NO_PROVEN_CONNECTION"


def test_temporal_transitivity_is_isolated_from_causality():
    flows = [
        OrderedMeaningFlow(FlowFamily.TEMPORAL_ORDER, "A", "B", None, "BEFORE", "source_to_target", provenance={}, confidence={}),
        OrderedMeaningFlow(FlowFamily.TEMPORAL_ORDER, "B", "C", None, "BEFORE", "source_to_target", provenance={}, confidence={}),
    ]

    assert infer_family_path(flows, family=FlowFamily.TEMPORAL_ORDER, source="A", target="C").relation_type == "BEFORE"
    assert infer_family_path(flows, family=FlowFamily.CAUSAL_CLAIM, source="A", target="C").connection == "NO_PROVEN_CONNECTION"


def test_linguistic_causal_claim_is_not_promoted_to_proof():
    flow = OrderedMeaningFlow(
        FlowFamily.CAUSAL_CLAIM,
        "BROKEN_BUILD",
        "FAIL_TEST",
        None,
        "LINGUISTIC_CAUSAL_CLAIM",
        "source_to_target",
        provenance={"source": "utterance"},
        confidence={"value": 0.95},
        metadata={"causal_relation": "CAUSES", "validated_proof": False},
    )

    assert flow.validated_proof is False
    assert infer_family_path(
        [flow],
        family=FlowFamily.CAUSAL_CLAIM,
        source="BROKEN_BUILD",
        target="FAIL_TEST",
        required_relation_type="VALIDATED_CAUSAL_PROOF",
    ).connection == "NO_PROVEN_CONNECTION"


def test_epistemic_states_are_not_a_linear_ladder():
    observed = OrderedMeaningFlow(FlowFamily.EPISTEMIC_STATE, "X", None, "OBSERVED", "STATE", provenance={}, confidence={})
    supported = OrderedMeaningFlow(FlowFamily.EPISTEMIC_STATE, "X", None, "SUPPORTED", "STATE", provenance={}, confidence={})

    assert observed.state != "VERIFIED"
    assert supported.state != "VERIFIED"
    assert infer_family_path([observed], family=FlowFamily.EPISTEMIC_STATE, source="X", target=None, required_state="VERIFIED").connection == "NO_PROVEN_CONNECTION"


def test_memory_authority_is_always_false_and_descriptive():
    flow = OrderedMeaningFlow(
        FlowFamily.MEMORY_LIFECYCLE,
        "X",
        None,
        "CONSOLIDATED_MEMORY",
        "STATE",
        provenance={"source": "unit-test"},
        confidence={},
    )

    assert MEMORY_WRITE_AUTHORITY is False
    assert flow.metadata["MEMORY_WRITE_AUTHORITY"] is False
    assert infer_family_path([flow], family=FlowFamily.EPISTEMIC_STATE, source="X", target=None, required_state="VERIFIED").connection == "NO_PROVEN_CONNECTION"


def test_governance_authority_boundary():
    requested = OrderedMeaningFlow(FlowFamily.GOVERNANCE_STATE, "RUN_TEST", None, "REQUESTED", "STATE", provenance={}, confidence={})

    with pytest.raises(ValueError, match="AUTHORIZED requires external authority"):
        requested.transition("AUTHORIZED")
    with pytest.raises(ValueError, match="requires external authority reference"):
        OrderedMeaningFlow(FlowFamily.GOVERNANCE_STATE, "RUN_TEST", None, "AUTHORIZED", "STATE", provenance={}, confidence={})
    assert KX108_AUTHORITY == "KX108_ONLY"


def test_same_object_can_carry_temporal_and_epistemic_flows_without_copying_payload():
    temporal = OrderedMeaningFlow(FlowFamily.TEMPORAL_ORDER, "RUN_TEST", None, "yesterday", "EVENT_TIME", provenance={}, confidence={})
    epistemic = OrderedMeaningFlow(FlowFamily.EPISTEMIC_STATE, "RUN_TEST", None, "REPORTED", "STATE", provenance={}, confidence={})

    assert temporal.source_object == epistemic.source_object == "RUN_TEST"
    assert "predicate" not in temporal.to_dict()
    assert "object_payload" not in epistemic.to_dict()


def test_predicate_unit_id_is_used_as_stable_reference_not_copied():
    frame = parse_utterance("hier Paul a lancé le test, je viens seulement de l'apprendre")
    run = next(unit for unit in frame.units if unit.predicate == "EXECUTE")
    flows = derive_ordered_meaning_flows(frame)

    assert any(flow.source_object == run.id for flow in flows)
    assert all(not hasattr(flow, "predicate") for flow in flows)