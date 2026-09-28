"""EventRef / CognitiveEvent primitive contracts.

These tests keep predicate meaning, event occurrence, and ordered flows as
separate identities. They do not wire the parser.
"""
from __future__ import annotations

import dataclasses
import json

import pytest

from app.semantic.lattice.events import (
    EventKind,
    EventRef,
    EventReferenceRelation,
    EventRelationKind,
)
from app.semantic.lattice.ordered_meaning_flow import FlowFamily, OrderedMeaningFlow


def _event(event_id: str, predicate_ref: str, kind: EventKind) -> EventRef:
    return EventRef(
        event_id=event_id,
        predicate_ref=predicate_ref,
        event_kind=kind,
        source_frame="frame-1",
        provenance={"source": "unit-test"},
        confidence={"value": None, "calibrated": False},
    )


def test_event_ref_is_immutable_frame_local_and_serializable():
    event = _event("e1", "u1", EventKind.ACTION)

    with pytest.raises(dataclasses.FrozenInstanceError):
        event.event_id = "e2"  # type: ignore[misc]
    assert event.metadata["event_id_scope"] == "frame_local"
    assert event.to_dict()["predicate_ref"] == "u1"
    assert json.loads(json.dumps(event.to_dict()))["event_kind"] == "ACTION"


def test_event_ref_references_predicate_without_copying_payload():
    event = EventRef(
        event_id="e-run-1",
        predicate_ref="u-run-1",
        event_kind=EventKind.ACTION,
        actor_ref="Paul",
        object_refs=("test",),
        source_frame="frame-1",
        provenance={"source": "unit-test"},
        confidence={},
    )

    as_dict = event.to_dict()
    assert event.event_id != event.predicate_ref
    assert as_dict["predicate_ref"] == "u-run-1"
    assert "predicate" not in as_dict
    assert "semantic_payload" not in as_dict
    assert "object_payload" not in as_dict


def test_knowledge_acquisition_event_learns_about_action_event():
    run = _event("e1", "u1", EventKind.ACTION)
    learn = _event("e2", "u2", EventKind.KNOWLEDGE_ACQUISITION)
    relation = EventReferenceRelation(
        relation_kind=EventRelationKind.LEARNS_ABOUT,
        source_event=learn.event_id,
        target_event=run.event_id,
        provenance={"source": "unit-test"},
    )

    assert run.event_id != learn.event_id
    assert run.predicate_ref != learn.predicate_ref
    assert relation.source_event == learn.event_id
    assert relation.target_event == run.event_id
    assert "target_event_payload" not in relation.to_dict()


def test_observation_event_observes_without_verifying_truth():
    fail = _event("e-fail", "u-fail", EventKind.CHANGE)
    observe = _event("e-observe", "u-observe", EventKind.OBSERVATION)
    relation = EventReferenceRelation(
        relation_kind=EventRelationKind.OBSERVES,
        source_event=observe.event_id,
        target_event=fail.event_id,
        provenance={"source": "unit-test"},
    )

    assert relation.relation_kind is EventRelationKind.OBSERVES
    assert relation.metadata.get("verified") is not True
    assert observe.event_kind is EventKind.OBSERVATION


def test_report_event_reports_about_without_validating_evidence():
    fail = _event("e-fail", "u-fail", EventKind.CHANGE)
    report = _event("e-report", "u-report", EventKind.REPORT)
    relation = EventReferenceRelation(
        relation_kind=EventRelationKind.REPORTS_ABOUT,
        source_event=report.event_id,
        target_event=fail.event_id,
        provenance={"source": "unit-test"},
    )

    assert relation.relation_kind is EventRelationKind.REPORTS_ABOUT
    assert relation.metadata.get("validated_evidence") is not True


def test_belief_event_believes_about_without_truth_claim():
    success = _event("e-success", "u-success", EventKind.STATE)
    belief = _event("e-belief", "u-belief", EventKind.BELIEF)
    relation = EventReferenceRelation(
        relation_kind=EventRelationKind.BELIEVES_ABOUT,
        source_event=belief.event_id,
        target_event=success.event_id,
        provenance={"source": "unit-test"},
    )

    assert relation.relation_kind is EventRelationKind.BELIEVES_ABOUT
    assert relation.metadata.get("truth") is not True


def test_same_event_can_participate_in_multiple_ordered_flows():
    run = _event("e-run", "u-run", EventKind.ACTION)
    flows = (
        OrderedMeaningFlow(
            family=FlowFamily.TEMPORAL_ORDER,
            source_object=run.event_id,
            state="yesterday",
            relation_type="EVENT_TIME",
            provenance={"source": "unit-test"},
            confidence={},
            metadata={"flow_id": "f-temporal"},
        ),
        OrderedMeaningFlow(
            family=FlowFamily.EPISTEMIC_STATE,
            source_object=run.event_id,
            state="REPORTED",
            relation_type="STATE",
            provenance={"source": "unit-test"},
            confidence={},
            metadata={"flow_id": "f-epistemic"},
        ),
        OrderedMeaningFlow(
            family=FlowFamily.GOVERNANCE_STATE,
            source_object=run.event_id,
            state="MENTIONED",
            relation_type="STATE",
            provenance={"source": "unit-test"},
            confidence={},
            metadata={"flow_id": "f-governance"},
        ),
    )

    assert {flow.source_object for flow in flows} == {run.event_id}
    assert all("event_payload" not in flow.to_dict() for flow in flows)


def test_predicate_event_and_flow_ids_stay_distinct_for_reviewer_join():
    predicate_id = "u-run"
    event = _event("e-run", predicate_id, EventKind.ACTION)
    flow = OrderedMeaningFlow(
        family=FlowFamily.EPISTEMIC_STATE,
        source_object=event.event_id,
        state="REPORTED",
        relation_type="STATE",
        provenance={"source": "unit-test"},
        confidence={},
        metadata={"flow_id": "f-reported"},
    )

    assert predicate_id != event.event_id
    assert event.event_id != flow.metadata["flow_id"]
    assert predicate_id != flow.metadata["flow_id"]
    assert event.predicate_ref == predicate_id
    assert flow.source_object == event.event_id


def test_memory_and_receipt_identities_are_not_collapsed_into_event_id():
    event = _event("e-run", "u-run", EventKind.ACTION)

    assert event.event_id != event.predicate_ref
    assert event.metadata["event_id_scope"] == "frame_local"
    assert "memory_trace_id" not in event.to_dict()
    assert "receipt_id" not in event.to_dict()


def test_event_reference_relation_rejects_unknown_relation_kind():
    with pytest.raises(ValueError):
        EventReferenceRelation(
            relation_kind="TRUTH_PROOF",
            source_event="e1",
            target_event="e2",
            provenance={"source": "unit-test"},
        )