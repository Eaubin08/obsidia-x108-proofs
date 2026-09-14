from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class PathFidelityEvidence:
    path_fidelity_ok: bool
    coherence_ok: bool
    drift_bound_ok: bool
    authorized_route_ok: bool
    replay_consistent: bool
    physical_envelope_ok: bool
    reason_codes: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    evidence_hash: str
    emits_verdict: bool = False
    decision_authority: str = "KX108_ONLY"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _hash_evidence(core: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(core, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()


def evaluate_path_fidelity(payload: dict[str, Any]) -> PathFidelityEvidence:
    source_conflict = float(payload.get("source_conflict_score", 0.0) or 0.0)
    drift = float(payload.get("trajectory_drift_score", 0.0) or 0.0)
    freshness_ms = float(payload.get("freshness_ms", 0.0) or 0.0)
    ground_speed = float(payload.get("ground_speed", 0.0) or 0.0)
    g_load = float(payload.get("g_load", 1.0) or 1.0)

    coherence_ok = (
        bool(payload.get("gps_available", True))
        and bool(payload.get("inertial_available", True))
        and bool(payload.get("radio_available", True))
        and source_conflict < 0.35
    )
    drift_bound_ok = drift < 0.45
    authorized_route_ok = bool(
        payload.get("authorized_route_hash")
        or payload.get("trajectory_id")
        or payload.get("flight_id")
    )
    replay_consistent = freshness_ms <= 1000 and not bool(payload.get("replay_window_detected", False))
    physical_envelope_ok = ground_speed <= 520 and g_load <= 2.1

    reasons: list[str] = []
    if not coherence_ok:
        reasons.append("P4_20_SOURCE_COHERENCE_FAILED")
    if not drift_bound_ok:
        reasons.append("P4_20_DRIFT_BOUND_FAILED")
    if not authorized_route_ok:
        reasons.append("P4_20_AUTHORIZED_ROUTE_MISSING")
    if not replay_consistent:
        reasons.append("P4_20_REPLAY_CONSISTENCY_FAILED")
    if not physical_envelope_ok:
        reasons.append("P4_20_PHYSICAL_ENVELOPE_FAILED")

    core = {
        "coherence_ok": coherence_ok,
        "drift_bound_ok": drift_bound_ok,
        "authorized_route_ok": authorized_route_ok,
        "replay_consistent": replay_consistent,
        "physical_envelope_ok": physical_envelope_ok,
        "reason_codes": reasons,
    }
    return PathFidelityEvidence(
        path_fidelity_ok=all(
            [coherence_ok, drift_bound_ok, authorized_route_ok, replay_consistent, physical_envelope_ok]
        ),
        coherence_ok=coherence_ok,
        drift_bound_ok=drift_bound_ok,
        authorized_route_ok=authorized_route_ok,
        replay_consistent=replay_consistent,
        physical_envelope_ok=physical_envelope_ok,
        reason_codes=tuple(reasons),
        evidence_refs=(
            "obsidia_core/guardians/path_fidelity_guard.py",
            "proofs/lean/Obsidia/GeneratedPeripheral/P_DomainKernel_PathFidelity_RequiresCoherence.lean",
        ),
        evidence_hash=_hash_evidence(core),
    )
