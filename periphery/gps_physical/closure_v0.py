"""F21 GPS Physical-World Closure V0.

Closes the recorded-real GPS path across F5/F20 into the existing GPS domain
reality-authenticity gate without upgrading recorded evidence into live physical
truth.

The closure is intentionally fail-closed:
- RECORDED_* evidence remains recorded;
- cross-modal coherence remains advisory;
- missing live attestation/corroboration remains explicit;
- the GPS domain gate can therefore produce the correct HOLD state.

No network call is performed by this module.
"""
from __future__ import annotations

from dataclasses import dataclass

from domains.gps.gps_x108_gate import GpsDefenseAviationState, GpsX108Gate
from periphery.cross_modal.contracts_v0 import CrossModalCoherenceReportV0
from periphery.gps_physical.bridge_v0 import (
    RecordedGpsEvidenceV0,
    recorded_gps_to_domain,
    recorded_gps_to_world,
)


@dataclass(frozen=True)
class GpsPhysicalWorldClosureV0:
    closure_id: str
    evidence_id: str
    proof_level: str
    world_state_ref: str
    domain_state_ref: str
    cross_modal_report_ref: str | None
    receiver_status: str
    blockers: tuple[str, ...]
    claim_scope: str
    recorded_real: bool
    live_claim_closed: bool = False
    attack_claim_closed: bool = False
    physical_authenticity_proven: bool = False
    readonly: bool = True
    advisory_only: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def __post_init__(self) -> None:
        if not self.closure_id or not self.evidence_id:
            raise ValueError("GPS physical-world closure requires identity and evidence id")
        if self.live_claim_closed or self.attack_claim_closed or self.physical_authenticity_proven:
            raise ValueError("F21 recorded closure cannot self-promote live/attack/authenticity claims")
        if not self.readonly or not self.advisory_only:
            raise ValueError("GPS physical-world closure must remain readonly/advisory")
        if self.decision_authority != "KX108_ONLY" or self.allowed_to_decide or self.allowed_to_act:
            raise ValueError("GPS physical-world closure cannot decide or act")


def build_gps_physical_world_closure_v0(
    evidence: RecordedGpsEvidenceV0,
    *,
    cross_modal_report: CrossModalCoherenceReportV0 | None = None,
) -> GpsPhysicalWorldClosureV0:
    world = recorded_gps_to_world(evidence)
    domain = recorded_gps_to_domain(evidence)

    blockers: list[str] = []
    recorded_real = evidence.proof_level in {"RECORDED_REAL_GNSS", "RECORDED_REAL_RF", "RECORDED_RF_ATTACK"}

    if evidence.proof_level.startswith("RECORDED_"):
        blockers.append("LIVE_SENSOR_ATTESTATION_NOT_PROVEN")

    if evidence.receiver_status == "BLOCKED_RECEIVER_CONFIGURATION":
        blockers.append("RECEIVER_CONFIGURATION_BLOCKED")

    if cross_modal_report is None:
        blockers.append("MULTI_SOURCE_CORROBORATION_NOT_PROVEN")
        cross_ref = None
    else:
        cross_ref = cross_modal_report.report_id
        if cross_modal_report.generated_present:
            blockers.append("GENERATED_MODALITY_NOT_PHYSICAL_TRUTH")
        if not cross_modal_report.physical_coherence_proven:
            blockers.append("MULTI_SOURCE_CORROBORATION_NOT_PROVEN")

    if not evidence.evidence_refs:
        blockers.append("PHYSICAL_EVIDENCE_REFS_MISSING")

    claim_scope = evidence.proof_level if recorded_real else "NON_PUBLIC_PHYSICAL_CLAIM"

    return GpsPhysicalWorldClosureV0(
        closure_id=f"gps-physical-closure:{evidence.evidence_id}",
        evidence_id=evidence.evidence_id,
        proof_level=evidence.proof_level,
        world_state_ref=world.world_state_id,
        domain_state_ref=f"{domain.domain_id}:{domain.world_state_ref}:{domain.valid_at}",
        cross_modal_report_ref=cross_ref,
        receiver_status=evidence.receiver_status,
        blockers=tuple(dict.fromkeys(blockers)),
        claim_scope=claim_scope,
        recorded_real=recorded_real,
    )


def gps_closure_to_gate_payload_v0(
    evidence: RecordedGpsEvidenceV0,
    closure: GpsPhysicalWorldClosureV0,
) -> dict[str, object]:
    """Build a conservative GPS-domain payload for the existing P3-05 gate.

    Recorded evidence can carry real measurements, but cannot assert live sensor
    attestation or multi-source physical authenticity. Any unavailable physical
    field defaults toward HOLD, never toward ALLOW.
    """
    if closure.evidence_id != evidence.evidence_id:
        raise ValueError("GPS closure/evidence binding mismatch")

    state = dict(evidence.state)

    return {
        "flow_type": "POSITION_REPORT",
        "mission_id": str(state.get("mission_id", "GPS-PHYSICAL-WORLD-CLOSURE-V0")),
        "flight_id": str(state.get("flight_id", evidence.evidence_id)),
        "altitude": float(state.get("altitude", state.get("altitude_m", 0.0)) or 0.0),
        "ground_speed": float(state.get("ground_speed", state.get("velocity_kt", 0.0)) or 0.0),
        "gps_status": str(state.get("gps_status", "RECORDED")),
        "satellites_count": int(state.get("satellites_count", 0) or 0),
        "signal_noise_ratio": float(state.get("signal_noise_ratio", state.get("confidence_index", 0.5)) or 0.5),
        "gps_available": True,
        "inertial_available": bool(state.get("inertial_available", False)),
        "radio_available": bool(state.get("radio_available", False)),
        "trajectory_drift_score": float(state.get("trajectory_drift_score", 0.0) or 0.0),
        "source_conflict_score": float(state.get("source_conflict_score", 0.0) or 0.0),
        "time_skew_score": float(state.get("time_skew_score", 0.0) or 0.0),
        "brownout_score": float(state.get("brownout_score", 0.0) or 0.0),
        "freshness_ms": float(state.get("freshness_ms", 0.0) or 0.0),
        "g_load": float(state.get("g_load", 1.0) or 1.0),
        "replay_window_detected": bool(state.get("replay_window_detected", False)),
        # Critical F21 boundary: recorded provenance is not live attestation.
        "sensor_attested": False,
        "attestation_ready": False,
        "rollback_possible": True,
        "risk_score": float(state.get("risk_score", 0.5) or 0.5),
        "confidence_index": float(state.get("confidence_index", state.get("signal_noise_ratio", 0.5)) or 0.5),
        "audit_score": float(state.get("audit_score", 1.0) or 1.0),
        "gps_physical_closure_ref": closure.closure_id,
        "gps_physical_blockers": list(closure.blockers),
        "gps_physical_claim_scope": closure.claim_scope,
    }


def build_gps_domain_gate_state_v0(
    evidence: RecordedGpsEvidenceV0,
    closure: GpsPhysicalWorldClosureV0,
) -> GpsDefenseAviationState:
    """Evaluate only the existing local GPS domain-state gate. No HTTP/kernel call."""
    payload = gps_closure_to_gate_payload_v0(evidence, closure)
    return GpsX108Gate().build_domain_state(payload)
