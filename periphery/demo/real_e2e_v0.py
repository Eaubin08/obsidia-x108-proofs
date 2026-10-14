"""F22 Real E2E Demonstrations V0.

Offline replay adapters over already-recorded real GPS artifacts.

The goal is not to rerun acquisition or claim live operation. The goal is to
prove that stored real-world artifacts can be re-ingested through the canonical
F5 -> MMonde/UDIP -> F21 closure -> existing GPS domain gate path while
preserving claim scope and fail-closed behavior.
"""
from __future__ import annotations

from dataclasses import dataclass

from periphery.gps_physical.bridge_v0 import RecordedGpsEvidenceV0
from periphery.gps_physical.closure_v0 import (
    GpsPhysicalWorldClosureV0,
    build_gps_domain_gate_state_v0,
    build_gps_physical_world_closure_v0,
)


@dataclass(frozen=True)
class RealE2EDemoResultV0:
    demo_id: str
    artifact_kind: str
    source_artifact_ref: str
    proof_level: str
    evidence_id: str
    closure: GpsPhysicalWorldClosureV0
    domain_state_name: str
    fail_closed: bool
    reality_authenticity_reasons: tuple[str, ...]
    historical_kernel_verdict: str | None = None
    historical_kernel_reason: str | None = None
    replay_mode: str = "OFFLINE_CANONICAL_REPLAY"
    live_execution_performed: bool = False
    readonly: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def __post_init__(self) -> None:
        if not self.demo_id or not self.source_artifact_ref:
            raise ValueError("real E2E demo result requires identity and source artifact")
        if self.live_execution_performed:
            raise ValueError("F22 offline replay must not claim live execution")
        if not self.readonly:
            raise ValueError("F22 demo result must remain readonly")
        if self.decision_authority != "KX108_ONLY" or self.allowed_to_decide or self.allowed_to_act:
            raise ValueError("F22 demo result cannot decide or act")


def recorded_evidence_from_real_artifact_v0(
    artifact: dict,
    *,
    source_artifact_ref: str,
) -> RecordedGpsEvidenceV0:
    envelope = artifact.get("observation_envelope")
    if not isinstance(envelope, dict):
        raise ValueError("real artifact requires observation_envelope")

    proof_level = str(envelope.get("proof_level") or artifact.get("proof_level") or "")
    if proof_level not in {"RECORDED_REAL_GNSS", "RECORDED_REAL_RF"}:
        raise ValueError("F22 accepts only recorded-real GNSS/RF artifacts")

    observation_id = str(envelope.get("observation_id") or "")
    capture_timestamp = str(envelope.get("capture_timestamp") or "")
    input_hash = str(envelope.get("input_hash") or "")
    observables = envelope.get("observables")

    if not observation_id or not capture_timestamp or not input_hash or not isinstance(observables, dict):
        raise ValueError("real artifact is missing canonical observation identity/provenance")

    limitations = tuple(str(x) for x in (envelope.get("limitations") or ()))
    uncertainty: list[str] = []
    if "NO_SENSOR_PRIVATE_KEY_ATTESTATION" in limitations:
        uncertainty.append("LIVE_SENSOR_ATTESTATION_NOT_PROVEN")
    if "NO_INERTIAL_CORROBORATION" in limitations or not bool(observables.get("inertial_available", False)):
        uncertainty.append("INERTIAL_CORROBORATION_NOT_PROVEN")

    evidence_refs = (
        source_artifact_ref,
        f"input_hash:{input_hash}",
        f"observables_hash:{envelope.get('observables_hash', 'UNKNOWN')}",
    )

    state = dict(observables)
    if isinstance(observables.get("pvt"), dict):
        pvt = observables["pvt"]
        state.setdefault("altitude_m", pvt.get("altitude_m", 0.0))
        state.setdefault("ground_speed", pvt.get("speed_kt", 0.0))

    return RecordedGpsEvidenceV0(
        evidence_id=observation_id,
        observed_at=capture_timestamp,
        source_ref=source_artifact_ref,
        source_hash=input_hash,
        proof_level=proof_level,
        state=state,
        evidence_refs=evidence_refs,
        uncertainty=tuple(dict.fromkeys(uncertainty)),
        contradictions=(),
        physical_authenticity_proven=False,
        receiver_status="UNKNOWN",
    )


def _historical_kernel_fields(artifact: dict) -> tuple[str | None, str | None]:
    x108 = artifact.get("x108_result")
    if isinstance(x108, dict):
        verdict = x108.get("verdict")
        kernel_response = x108.get("kernel_response")
        if isinstance(kernel_response, dict):
            reason = kernel_response.get("reason_code")
        else:
            reason = x108.get("reason")
        return (
            str(verdict) if verdict is not None else None,
            str(reason) if reason is not None else None,
        )

    http = artifact.get("kernel_http_evidence")
    if isinstance(http, dict):
        raw = http.get("raw_response")
        if isinstance(raw, str):
            # We intentionally do not parse arbitrary nested historical payloads
            # here. Historical verdict is optional metadata, never authority.
            return None, None
    return None, None


def run_recorded_real_e2e_demo_v0(
    artifact: dict,
    *,
    demo_id: str,
    source_artifact_ref: str,
) -> RealE2EDemoResultV0:
    evidence = recorded_evidence_from_real_artifact_v0(
        artifact,
        source_artifact_ref=source_artifact_ref,
    )
    closure = build_gps_physical_world_closure_v0(evidence)
    domain_state = build_gps_domain_gate_state_v0(evidence, closure)
    historical_verdict, historical_reason = _historical_kernel_fields(artifact)

    return RealE2EDemoResultV0(
        demo_id=demo_id,
        artifact_kind=str(artifact.get("mode") or evidence.proof_level),
        source_artifact_ref=source_artifact_ref,
        proof_level=evidence.proof_level,
        evidence_id=evidence.evidence_id,
        closure=closure,
        domain_state_name=domain_state.state_name,
        fail_closed=domain_state.fail_closed,
        reality_authenticity_reasons=domain_state.reality_authenticity.reasons,
        historical_kernel_verdict=historical_verdict,
        historical_kernel_reason=historical_reason,
    )
