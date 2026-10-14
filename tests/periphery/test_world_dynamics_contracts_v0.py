from periphery.world_dynamics.contracts_v0 import (
    ContinuityStatusV0,
    RelationStatusV0,
    SpatialFrameRefV0,
    TimeEnvelopeV0,
    TrajectoryV0,
    TransitionV0,
    TypedRelationV0,
)


def test_time_envelope_preserves_missing_clocks():
    t = TimeEnvelopeV0(observed_at="2026-10-07T00:00:00Z")
    assert t.received_at is None
    assert t.processed_at is None
    assert t.decided_at is None
    assert t.executed_at is None
    assert t.verified_at is None


def test_causal_proven_requires_evidence():
    try:
        TypedRelationV0(
            relation_id="r1",
            subject_ref="a",
            object_ref="b",
            status=RelationStatusV0.CAUSAL_PROVEN,
        )
    except ValueError as exc:
        assert "CAUSAL_PROVEN requires evidence_refs" in str(exc)
    else:
        raise AssertionError("CAUSAL_PROVEN without evidence must fail closed")


def test_temporal_relation_does_not_become_causal():
    rel = TypedRelationV0(
        relation_id="r2",
        subject_ref="a",
        object_ref="b",
        status=RelationStatusV0.TEMPORAL,
    )
    assert rel.status == RelationStatusV0.TEMPORAL
    assert rel.status != RelationStatusV0.CAUSAL_PROVEN


def test_transition_is_readonly_and_non_sovereign():
    transition = TransitionV0(
        transition_id="t1",
        entity_ref="entity:1",
        from_state_ref="state:0",
        to_state_ref="state:1",
        time=TimeEnvelopeV0(observed_at="2026-10-07T00:00:00Z"),
        spatial_frame=SpatialFrameRefV0(frame_ref="ECEF"),
        continuity=ContinuityStatusV0.CONTINUOUS,
    )
    assert transition.readonly is True
    assert transition.decision_authority == "KX108_ONLY"
    assert transition.allowed_to_decide is False
    assert transition.allowed_to_act is False


def test_trajectory_requires_state_chain_continuity():
    t1 = TransitionV0(
        transition_id="t1",
        entity_ref="entity:1",
        from_state_ref="state:0",
        to_state_ref="state:1",
        time=TimeEnvelopeV0(observed_at="2026-10-07T00:00:00Z"),
    )
    t2 = TransitionV0(
        transition_id="t2",
        entity_ref="entity:1",
        from_state_ref="state:X",
        to_state_ref="state:2",
        time=TimeEnvelopeV0(observed_at="2026-10-07T00:00:01Z"),
    )
    try:
        TrajectoryV0(
            trajectory_id="traj:1",
            entity_ref="entity:1",
            transitions=(t1, t2),
        )
    except ValueError as exc:
        assert "state chain is discontinuous" in str(exc)
    else:
        raise AssertionError("discontinuous trajectory must fail closed")
