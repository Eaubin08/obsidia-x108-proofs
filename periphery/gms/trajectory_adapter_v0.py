"""F17 GMS Trajectory Adapter V0.

Conservative adapter between the existing Brody 21D cognitive point cloud and
F12 Situated World Dynamics trajectories.

This module does not create a new GMS engine. It preserves existing cognitive
geometry as readonly semantic-position snapshots and maps explicit N->N+1
changes into TransitionV0 / TrajectoryV0.

No memory ownership, no cognition authority, no decision, no ACT.
"""
from __future__ import annotations

from dataclasses import dataclass

from periphery.world_dynamics.contracts_v0 import (
    ContinuityStatusV0,
    TimeEnvelopeV0,
    TrajectoryV0,
    TransitionV0,
)


_EXPECTED_AXES = tuple(range(1, 22))


@dataclass(frozen=True)
class GmsSemanticPointV0:
    point_id: str
    semantic_entity_ref: str
    observed_at: str
    vector_21d: tuple[tuple[int, float], ...]
    point_cloud_ref: str | None = None
    context_refs: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    uncertainty: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    readonly: bool = True
    representation_only: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def __post_init__(self) -> None:
        if not self.point_id or not self.semantic_entity_ref or not self.observed_at:
            raise ValueError("GMS semantic point requires identity, entity and time")
        axes = tuple(axis for axis, _ in self.vector_21d)
        if axes != _EXPECTED_AXES:
            raise ValueError("GMS semantic point requires exactly axes 1..21 in canonical order")
        for _, value in self.vector_21d:
            if not isinstance(value, (int, float)):
                raise ValueError("GMS vector values must be numeric")
        if not self.readonly or not self.representation_only:
            raise ValueError("GMS semantic point must remain readonly representation")
        if self.decision_authority != "KX108_ONLY" or self.allowed_to_decide or self.allowed_to_act:
            raise ValueError("GMS semantic point cannot decide or act")


@dataclass(frozen=True)
class GmsAxisDeltaV0:
    axis: int
    from_value: float
    to_value: float
    delta: float

    def __post_init__(self) -> None:
        if self.axis not in _EXPECTED_AXES:
            raise ValueError("GMS axis delta must reference axis 1..21")


@dataclass(frozen=True)
class GmsSemanticTransitionV0:
    transition: TransitionV0
    axis_deltas: tuple[GmsAxisDeltaV0, ...]
    drift_magnitude_l1: float
    declared_continuity: ContinuityStatusV0

    def __post_init__(self) -> None:
        if self.transition.continuity != self.declared_continuity:
            raise ValueError("declared GMS continuity must match underlying world transition")
        if self.drift_magnitude_l1 < 0:
            raise ValueError("drift magnitude cannot be negative")


def semantic_point_from_brody_point_cloud_v0(
    *,
    point_id: str,
    semantic_entity_ref: str,
    observed_at: str,
    point_cloud_output: dict,
    point_cloud_ref: str | None = None,
    context_refs: tuple[str, ...] = (),
    source_refs: tuple[str, ...] = (),
) -> GmsSemanticPointV0:
    """Conservatively wrap an existing Brody point-cloud output.

    Only vector_21d is consumed. Layer selection, budget, authority signals and
    other Brody outputs remain owned by the cognitive subsystem.
    """
    raw = point_cloud_output.get("vector_21d")
    if not isinstance(raw, dict):
        raise ValueError("Brody point cloud output must contain vector_21d dict")

    values: list[tuple[int, float]] = []
    for axis in _EXPECTED_AXES:
        if axis in raw:
            value = raw[axis]
        elif str(axis) in raw:
            value = raw[str(axis)]
        else:
            raise ValueError(f"missing Brody point-cloud axis {axis}")
        if not isinstance(value, (int, float)):
            raise ValueError(f"non-numeric Brody point-cloud axis {axis}")
        values.append((axis, float(value)))

    return GmsSemanticPointV0(
        point_id=point_id,
        semantic_entity_ref=semantic_entity_ref,
        observed_at=observed_at,
        vector_21d=tuple(values),
        point_cloud_ref=point_cloud_ref,
        context_refs=context_refs,
        source_refs=source_refs,
    )


def build_gms_semantic_transition_v0(
    *,
    transition_id: str,
    from_point: GmsSemanticPointV0,
    to_point: GmsSemanticPointV0,
    continuity: ContinuityStatusV0 = ContinuityStatusV0.UNKNOWN,
) -> GmsSemanticTransitionV0:
    if from_point.semantic_entity_ref != to_point.semantic_entity_ref:
        raise ValueError("GMS transition requires the same semantic entity")
    if from_point.point_id == to_point.point_id:
        raise ValueError("GMS transition requires distinct point ids")

    deltas = tuple(
        GmsAxisDeltaV0(
            axis=a1,
            from_value=v1,
            to_value=v2,
            delta=round(v2 - v1, 12),
        )
        for (a1, v1), (a2, v2) in zip(from_point.vector_21d, to_point.vector_21d)
        if a1 == a2
    )
    if len(deltas) != 21:
        raise ValueError("GMS transition requires aligned 21D vectors")

    drift = round(sum(abs(d.delta) for d in deltas), 12)
    transition = TransitionV0(
        transition_id=transition_id,
        entity_ref=from_point.semantic_entity_ref,
        from_state_ref=from_point.point_id,
        to_state_ref=to_point.point_id,
        time=TimeEnvelopeV0(observed_at=to_point.observed_at),
        continuity=continuity,
        uncertainty=tuple(dict.fromkeys((*from_point.uncertainty, *to_point.uncertainty))),
        contradictions=tuple(dict.fromkeys((*from_point.contradictions, *to_point.contradictions))),
        provenance_refs=tuple(dict.fromkeys((*from_point.source_refs, *to_point.source_refs))),
    )
    return GmsSemanticTransitionV0(
        transition=transition,
        axis_deltas=deltas,
        drift_magnitude_l1=drift,
        declared_continuity=continuity,
    )


def build_gms_trajectory_v0(
    *,
    trajectory_id: str,
    transitions: tuple[GmsSemanticTransitionV0, ...],
    continuity: ContinuityStatusV0 = ContinuityStatusV0.UNKNOWN,
) -> TrajectoryV0:
    if not transitions:
        raise ValueError("GMS trajectory requires at least one transition")
    return TrajectoryV0(
        trajectory_id=trajectory_id,
        entity_ref=transitions[0].transition.entity_ref,
        transitions=tuple(item.transition for item in transitions),
        continuity=continuity,
    )
