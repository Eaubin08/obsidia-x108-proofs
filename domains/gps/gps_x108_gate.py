"""
domains/gps/gps_x108_gate.py - Gate GPS/DEFENSE/AVIATION -> Kernel X-108.

P3-05 runtime bridge.

Rule: DOMAIN_BRIDGE_ONLY. This gate observes, normalizes and translates a
GPS/aviation packet into a kernel-readable IR. It never emits an executable
action and never grants authority to the connector. If reality authenticity is
not proven, the bridge fails closed with HOLD before any physical execution path.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass
from types import SimpleNamespace
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request

from periphery.os3_ticket import build_os3_ticket, ticket_is_valid

from .nuisance_registry import NuisanceEntry, classify_gps_payload

try:
    import requests as _requests

    _REQUESTS_OK = True
except ImportError:
    _requests = None  # type: ignore
    _REQUESTS_OK = False

KERNEL_URL: str = os.environ.get(
    "OBSIDIA_KERNEL_URL",
    "http://127.0.0.1:3001/kernel/ragnarok",
)
DOMAIN: str = "gps_defense_aviation"
GATE_VERSION: str = "v2-reality-authenticity"
FRESHNESS_LIMIT_MS: float = 1000.0
DEFAULT_THRESHOLD_S: float = 0.7

FLOW_TO_INTENT: dict[str, str] = {
    "FLIGHT_PLAN": "CREATE_PATCH",
    "ROUTE_UPDATE": "CREATE_PATCH",
    "AIRSPACE_REQUEST": "CREATE_PATCH",
    "POSITION_REPORT": "AUDIT_ONLY",
    "COLLISION_AVOIDANCE": "AUDIT_ONLY",
    "RADAR_SCAN": "AUDIT_ONLY",
    "DEFENSE_ALERT": "AUDIT_ONLY",
    "EMERGENCY": "AUDIT_ONLY",
    "TRAJECTORY_DECISION": "AUDIT_ONLY",
}


@dataclass(frozen=True)
class RealityAuthenticityResult:
    is_fresh: bool
    sensor_attested: bool
    anti_replay_ok: bool
    multisource_coherent: bool
    physical_envelope_ok: bool
    freshness_ms: float
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class GpsDefenseAviationState:
    state_name: str
    flight_id: str
    flow_type: str
    nuisances: tuple[str, ...]
    nuisance_risk_classes: tuple[str, ...]
    reality_authenticity: RealityAuthenticityResult
    risk_score: float
    confidence_index: float
    audit_score: float
    threshold_s: float
    fail_closed: bool
    domain_state_hash: str


class GpsX108Gate:
    """GPS/defense/aviation bridge into the X-108 kernel.

    The bridge can return HOLD locally only as a fail-closed admission verdict.
    It never returns ALLOW by itself; ALLOW can only come from the kernel.
    """

    def evaluate_reality_authenticity(self, payload: dict[str, Any]) -> RealityAuthenticityResult:
        freshness_ms = float(payload.get("freshness_ms", 0.0) or 0.0)
        gps_available = bool(payload.get("gps_available", True))
        inertial_available = bool(payload.get("inertial_available", True))
        radio_available = bool(payload.get("radio_available", True))
        source_conflict = float(payload.get("source_conflict_score", 0.0) or 0.0)
        drift_score = float(payload.get("trajectory_drift_score", 0.0) or 0.0)
        velocity_kt = float(payload.get("ground_speed", payload.get("velocity_kt", 0.0)) or 0.0)
        g_load = float(payload.get("g_load", 1.0) or 1.0)

        is_fresh = 0 <= freshness_ms <= FRESHNESS_LIMIT_MS
        sensor_attested = bool(payload.get("attestation_ready", payload.get("sensor_attested", False)))
        anti_replay_ok = not bool(payload.get("replay_window_detected", False))
        multisource_coherent = (
            gps_available
            and inertial_available
            and radio_available
            and source_conflict < 0.35
            and drift_score < 0.45
        )
        physical_envelope_ok = velocity_kt <= 520 and g_load <= 2.1

        reasons: list[str] = []
        if not is_fresh:
            reasons.append("ORACLE_FRESHNESS_FAILED")
        if not sensor_attested:
            reasons.append("CIC_ATTESTATION_FAILED")
        if not anti_replay_ok:
            reasons.append("ANTI_REPLAY_FAILED")
        if not multisource_coherent:
            reasons.append("MULTI_SOURCE_COHERENCE_FAILED")
        if not physical_envelope_ok:
            reasons.append("PHYSICAL_ENVELOPE_FAILED")

        return RealityAuthenticityResult(
            is_fresh=is_fresh,
            sensor_attested=sensor_attested,
            anti_replay_ok=anti_replay_ok,
            multisource_coherent=multisource_coherent,
            physical_envelope_ok=physical_envelope_ok,
            freshness_ms=freshness_ms,
            reasons=tuple(reasons),
        )

    def build_domain_state(self, payload: dict[str, Any]) -> GpsDefenseAviationState:
        flow_type = str(payload.get("flow_type", payload.get("action_type", "UNKNOWN"))).upper()
        nuisances: list[NuisanceEntry] = classify_gps_payload(payload)
        authenticity = self.evaluate_reality_authenticity(payload)
        risk_score = float(payload.get("risk_score", payload.get("trajectory_drift_score", 0.5)) or 0.5)
        confidence_index = float(payload.get("confidence_index", payload.get("signal_noise_ratio", 0.5)) or 0.5)
        audit_score = float(payload.get("audit_score", 1.0 if payload.get("rollback_possible") else 0.4) or 0.4)
        threshold_s = float(payload.get("threshold_s", DEFAULT_THRESHOLD_S))
        fail_closed = bool(nuisances or authenticity.reasons)

        state_core = {
            "domain": DOMAIN,
            "flight_id": str(payload.get("flight_id", "UNKNOWN")),
            "flow_type": flow_type,
            "nuisances": [n.label for n in nuisances],
            "authenticity": asdict(authenticity),
            "risk_score": risk_score,
            "confidence_index": confidence_index,
            "audit_score": audit_score,
            "threshold_s": threshold_s,
            "fail_closed": fail_closed,
        }
        digest = hashlib.sha256(
            json.dumps(state_core, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()

        return GpsDefenseAviationState(
            state_name="GPS_DEFENSE_AVIATION_UNTRUSTED" if fail_closed else "GPS_DEFENSE_AVIATION_COHERENT",
            flight_id=str(payload.get("flight_id", "UNKNOWN")),
            flow_type=flow_type,
            nuisances=tuple(n.label for n in nuisances),
            nuisance_risk_classes=tuple(n.risk_class for n in nuisances),
            reality_authenticity=authenticity,
            risk_score=risk_score,
            confidence_index=confidence_index,
            audit_score=audit_score,
            threshold_s=threshold_s,
            fail_closed=fail_closed,
            domain_state_hash=digest,
        )

    def translate_to_ir(self, payload: dict[str, Any]) -> dict[str, Any]:
        domain_state = self.build_domain_state(payload)
        flow_type = domain_state.flow_type
        return {
            "domain": DOMAIN,
            "data": self.build_kernel_state_payload(payload, domain_state),
            "meta": {
                "flow_type": flow_type,
                "ir_intent": FLOW_TO_INTENT.get(flow_type, "GENERAL_FLOW"),
                "risk_class": payload.get("risk_class", ""),
                "zone": payload.get("zone", ""),
                "gate_version": GATE_VERSION,
                "contract": "DOMAIN_BRIDGE_ONLY",
                "decision_authority": "KX108_ONLY",
                "decides_alone": False,
                "domain_state": asdict(domain_state),
            },
        }

    def build_kernel_state_payload(
        self,
        payload: dict[str, Any],
        domain_state: GpsDefenseAviationState,
    ) -> dict[str, Any]:
        return {
            "mission_id": str(payload.get("mission_id", "GPS-V01-DEMO")),
            "flight_id": domain_state.flight_id,
            "altitude": float(payload.get("altitude", 32000.0) or 0.0),
            "ground_speed": float(payload.get("ground_speed", 430.0) or 0.0),
            "gps_status": str(payload.get("gps_status", "ONLINE")),
            "satellites_count": int(payload.get("satellites_count", 10) or 0),
            "signal_noise_ratio": domain_state.confidence_index,
            "gps_available": bool(payload.get("gps_available", True)),
            "inertial_available": bool(payload.get("inertial_available", True)),
            "radio_available": bool(payload.get("radio_available", True)),
            "trajectory_drift_score": float(payload.get("trajectory_drift_score", 0.0) or 0.0),
            "source_conflict_score": float(payload.get("source_conflict_score", 0.0) or 0.0),
            "time_skew_score": float(payload.get("time_skew_score", 0.0) or 0.0),
            "brownout_score": float(payload.get("brownout_score", 0.0) or 0.0),
            "attestation_ready": bool(payload.get("attestation_ready", payload.get("sensor_attested", False))),
            "rollback_possible": bool(payload.get("rollback_possible", True)),
            "T_mean": domain_state.risk_score,
            "H_score": domain_state.confidence_index,
            "A_score": domain_state.audit_score,
            "S": domain_state.threshold_s,
            "domain_state_hash": domain_state.domain_state_hash,
            "reality_authenticity_reasons": list(domain_state.reality_authenticity.reasons),
            "nuisances": list(domain_state.nuisances),
        }

    def evaluate(self, payload: dict[str, Any], timeout: float = 10.0) -> dict[str, Any]:
        ir_payload = self.translate_to_ir(payload)
        domain_state = ir_payload["meta"]["domain_state"]

        if domain_state.get("fail_closed"):
            return {
                "verdict": "HOLD",
                "domain": DOMAIN,
                "source": "REALITY_AUTHENTICITY_GATE_FAIL_CLOSED",
                "reason": "INPUT_NOT_CANONIZED_FOR_KERNEL_EXECUTION",
                "ir_payload": ir_payload,
                "gate_version": GATE_VERSION,
                "receipt": self.build_decision_receipt(
                    "HOLD",
                    ir_payload,
                    source="P3_05_FAIL_CLOSED",
                ),
            }

        try:
            kernel_decision = self.post_to_kernel(ir_payload, timeout=timeout)
        except Exception as exc:
            return {
                "verdict": "HOLD",
                "domain": DOMAIN,
                "source": "GATE_FAIL_CLOSED",
                "error": str(exc)[:200],
                "ir_payload": ir_payload,
                "receipt": self.build_decision_receipt(
                    "HOLD",
                    ir_payload,
                    source="KERNEL_UNREACHABLE",
                ),
            }

        verdict = kernel_decision.get("x108_gate") or kernel_decision.get("verdict") or "HOLD"
        return {
            "verdict": verdict,
            "domain": DOMAIN,
            "source": "KERNEL_X108",
            "kernel_response": kernel_decision,
            "ir_payload": ir_payload,
            "gate_version": GATE_VERSION,
            "receipt": self.build_decision_receipt(
                verdict,
                ir_payload,
                kernel_decision,
                source="KERNEL_X108",
            ),
        }

    def post_to_kernel(self, ir_payload: dict[str, Any], timeout: float = 10.0) -> dict[str, Any]:
        if _REQUESTS_OK and _requests is not None:
            response = _requests.post(KERNEL_URL, json=ir_payload, timeout=timeout)
            response.raise_for_status()
            return response.json()

        body = json.dumps(ir_payload, ensure_ascii=False, default=str).encode("utf-8")
        req = urllib_request.Request(
            KERNEL_URL,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib_request.urlopen(req, timeout=timeout) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw)
        except urllib_error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"kernel_http_{exc.code}:{raw[:200]}") from exc

    def build_decision_receipt(
        self,
        verdict: str,
        ir_payload: dict[str, Any],
        kernel_decision: dict[str, Any] | None = None,
        *,
        source: str,
    ) -> dict[str, Any]:
        unsigned = {
            "domain": DOMAIN,
            "gate": "P3-05",
            "gate_file": "domains/gps/gps_x108_gate.py",
            "contract": "DOMAIN_BRIDGE_ONLY",
            "decision_authority": "KX108_ONLY",
            "connector_decides": False,
            "verdict": verdict,
            "source": source,
            "domain_state_hash": ir_payload.get("meta", {}).get("domain_state", {}).get("domain_state_hash"),
            "ir_payload": ir_payload,
            "kernel_decision": kernel_decision or {},
            "created_at_ms": int(time.time() * 1000),
        }
        signature = hashlib.sha256(
            json.dumps(unsigned, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
        ).hexdigest()

        os3_ticket = self.build_os3_ticket(
            verdict=verdict,
            ir_payload=ir_payload,
            kernel_decision=kernel_decision,
            source=source,
        )
        return {
            **unsigned,
            "signature_kind": "LOCAL_SHA256_DEMO_NOT_PRODUCTION_SIGNING",
            "signed_decision_receipt_sha256": signature,
            "os3_ticket": os3_ticket.to_dict(),
            "os3_ticket_valid": ticket_is_valid(os3_ticket),
        }

    def build_os3_ticket(
        self,
        verdict: str,
        ir_payload: dict[str, Any],
        kernel_decision: dict[str, Any] | None = None,
        *,
        source: str,
    ):
        domain_state = ir_payload.get("meta", {}).get("domain_state", {}) or {}
        authenticity = domain_state.get("reality_authenticity", {}) or {}
        nuisances = list(domain_state.get("nuisances", []) or [])
        reasons = list(authenticity.get("reasons", []) or [])
        contradictions = [
            reason
            for reason in reasons
            if reason in {"MULTI_SOURCE_COHERENCE_FAILED", "PHYSICAL_ENVELOPE_FAILED"}
        ]
        risk_flags = sorted(set(nuisances + reasons))
        x108_gate = str(verdict or "HOLD").upper()
        fail_closed = bool(domain_state.get("fail_closed", False))

        if x108_gate == "BLOCK" or fail_closed:
            severity = "S4"
        elif x108_gate == "HOLD":
            severity = "S2"
        else:
            severity = "S0"

        action_candidate = SimpleNamespace(
            action_id=f"gps-{domain_state.get('flight_id', 'UNKNOWN')}-{domain_state.get('domain_state_hash', 'NOHASH')[:12]}",
            domain=DOMAIN,
            intent=ir_payload.get("meta", {}).get("ir_intent", "GENERAL_FLOW"),
            action_type=domain_state.get("flow_type", "UNKNOWN"),
            payload=ir_payload,
        )
        packet = SimpleNamespace(
            domain=DOMAIN,
            gate="P3-05",
            gate_version=GATE_VERSION,
            domain_state_hash=domain_state.get("domain_state_hash"),
            ir_payload=ir_payload,
        )
        envelope = SimpleNamespace(
            x108_gate=x108_gate,
            reason_code=source,
            severity=severity,
            metrics={
                "risk_score": domain_state.get("risk_score"),
                "confidence_index": domain_state.get("confidence_index"),
                "audit_score": domain_state.get("audit_score"),
                "freshness_ms": authenticity.get("freshness_ms"),
            },
            unknowns=reasons,
            risk_flags=risk_flags,
            contradictions=contradictions,
            evidence_refs=[
                "domains/gps/gps_x108_gate.py",
                "periphery/os3_ticket.py",
                f"domain_state_hash:{domain_state.get('domain_state_hash', 'UNKNOWN')}",
            ],
            kernel_decision=kernel_decision or {},
        )
        return build_os3_ticket(action_candidate, packet, envelope)


def evaluate_gps_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return GpsX108Gate().evaluate(payload)
