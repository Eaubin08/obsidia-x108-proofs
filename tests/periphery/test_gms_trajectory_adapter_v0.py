from periphery.gms.trajectory_adapter_v0 import (
    GmsSemanticPointV0,
    build_gms_semantic_transition_v0,
    build_gms_trajectory_v0,
    semantic_point_from_brody_point_cloud_v0,
)
from periphery.world_dynamics.contracts_v0 import ContinuityStatusV0


def _point_cloud(seed: float = 0.0) -> dict:
    return {"vector_21d": {axis: seed + axis / 100.0 for axis in range(1, 22)}}


def test_wrap_existing_brody_point_cloud_without_recomputing_layers():
    point = semantic_point_from_brody_point_cloud_v0(
        point_id="gms:p1",
        semantic_entity_ref="concept:obsidia",
        observed_at="2026-10-07T00:00:00Z",
        point_cloud_output=_point_cloud(),
        point_cloud_ref="brody:pc:1",
        source_refs=("brody:output:1",),
    )
    assert isinstance(point, GmsSemanticPointV0)
    assert len(point.vector_21d) == 21
    assert point.vector_21d[9][0] == 10
    assert point.point_cloud_ref == "brody:pc:1"
    assert point.allowed_to_decide is False
    assert point.allowed_to_act is False


def test_missing_axis_fails_closed():
    raw = _point_cloud()
    raw["vector_21d"].pop(21)
    try:
        semantic_point_from_brody_point_cloud_v0(
            point_id="gms:bad",
            semantic_entity_ref="concept:obsidia",
            observed_at="2026-10-07T00:00:00Z",
            point_cloud_output=raw,
        )
    except ValueError as exc:
        assert "missing Brody point-cloud axis 21" in str(exc)
    else:
        raise AssertionError("missing 21D axis must fail closed")


def test_semantic_transition_computes_geometry_but_does_not_infer_continuity():
    p1 = semantic_point_from_brody_point_cloud_v0(
        point_id="gms:p1",
        semantic_entity_ref="concept:obsidia",
        observed_at="2026-10-07T00:00:00Z",
        point_cloud_output=_point_cloud(0.0),
        source_refs=("brody:1",),
    )
    p2 = semantic_point_from_brody_point_cloud_v0(
        point_id="gms:p2",
        semantic_entity_ref="concept:obsidia",
        observed_at="2026-10-07T00:00:01Z",
        point_cloud_output=_point_cloud(0.1),
        source_refs=("brody:2",),
    )
    transition = build_gms_semantic_transition_v0(
        transition_id="gms:t1",
        from_point=p1,
        to_point=p2,
    )
    assert transition.drift_magnitude_l1 > 0
    assert transition.declared_continuity == ContinuityStatusV0.UNKNOWN
    assert transition.transition.continuity == ContinuityStatusV0.UNKNOWN
    assert transition.transition.decision_authority == "KX108_ONLY"
    assert transition.transition.allowed_to_act is False


def test_rupture_is_explicitly_declared_not_inferred_from_distance():
    p1 = semantic_point_from_brody_point_cloud_v0(
        point_id="gms:p1",
        semantic_entity_ref="concept:obsidia",
        observed_at="2026-10-07T00:00:00Z",
        point_cloud_output=_point_cloud(0.0),
    )
    p2 = semantic_point_from_brody_point_cloud_v0(
        point_id="gms:p2",
        semantic_entity_ref="concept:obsidia",
        observed_at="2026-10-07T00:00:01Z",
        point_cloud_output=_point_cloud(10.0),
    )
    transition = build_gms_semantic_transition_v0(
        transition_id="gms:t1",
        from_point=p1,
        to_point=p2,
    )
    assert transition.drift_magnitude_l1 > 100
    assert transition.declared_continuity == ContinuityStatusV0.UNKNOWN


def test_gms_trajectory_reuses_f12_state_chain_validation():
    points = [
        semantic_point_from_brody_point_cloud_v0(
            point_id=f"gms:p{i}",
            semantic_entity_ref="concept:obsidia",
            observed_at=f"2026-10-07T00:00:0{i}Z",
            point_cloud_output=_point_cloud(i / 10.0),
        )
        for i in range(3)
    ]
    t1 = build_gms_semantic_transition_v0(
        transition_id="gms:t1",
        from_point=points[0],
        to_point=points[1],
        continuity=ContinuityStatusV0.CONTINUOUS,
    )
    t2 = build_gms_semantic_transition_v0(
        transition_id="gms:t2",
        from_point=points[1],
        to_point=points[2],
        continuity=ContinuityStatusV0.DRIFT,
    )
    trajectory = build_gms_trajectory_v0(
        trajectory_id="gms:traj:1",
        transitions=(t1, t2),
        continuity=ContinuityStatusV0.DRIFT,
    )
    assert len(trajectory.transitions) == 2
    assert trajectory.entity_ref == "concept:obsidia"
    assert trajectory.allowed_to_decide is False
    assert trajectory.allowed_to_act is False
