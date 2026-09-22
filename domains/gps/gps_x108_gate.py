"""
domains/gps/gps_x108_gate.py — Gate de gouvernance GPS/DÉFENSE/AVIATION → Kernel X-108
P3-05 — V3.2.2 COMPLETION

RÈGLE ABSOLUE :
  Ce gate NE DÉCIDE JAMAIS de façon autonome.
  Il traduit le payload GPS/aviation en IR et le soumet au Kernel X-108.
  La décision (ALLOW / HOLD / BLOCK) appartient au Kernel uniquement.
  Fail-Closed : si le Kernel est injoignable → HOLD systématique.

Branche depuis : connectors/aviation_robo.py (observateur live)
Couvre : GPS terrestre, aviation civile, défense, espace aérien.
"""

from __future__ import annotations

import os
from typing import Any
import hashlib
import json
import time
from types import SimpleNamespace
from periphery.os3_ticket import build_os3_ticket, ticket_is_valid

try:
    import requests as _requests
    _REQUESTS_OK = True
except ImportError:
    _requests = None  # type: ignore
    _REQUESTS_OK = False

KERNEL_URL: str = os.environ.get(
    "OBSIDIA_KERNEL_URL",
    "http://127.0.0.1:3001/kernel/ragnarok"
)
DOMAIN: str = "gps_defense_aviation"
GATE_VERSION: str = "v1"

FLOW_TO_INTENT: dict[str, str] = {
    "FLIGHT_PLAN":        "CREATE_PATCH",
    "ROUTE_UPDATE":       "CREATE_PATCH",
    "AIRSPACE_REQUEST":   "CREATE_PATCH",
    "POSITION_REPORT":    "AUDIT_ONLY",
    "COLLISION_AVOIDANCE": "AUDIT_ONLY",
    "RADAR_SCAN":         "AUDIT_ONLY",
    "DEFENSE_ALERT":      "AUDIT_ONLY",
    "EMERGENCY":          "AUDIT_ONLY",
}

DEFAULT_THRESHOLD_S: float = 0.7  # Seuil plus élevé pour domaine critique


class GpsX108Gate:
    """
    Gate de gouvernance GPS/DÉFENSE/AVIATION → Kernel X-108.
    Ne prend AUCUNE décision autonome.
    Seuil S par défaut plus conservateur (0.7) pour ce domaine critique.
    """

    def translate_to_ir(self, payload: dict[str, Any]) -> dict[str, Any]:
        flow_type = str(payload.get("flow_type", "UNKNOWN")).upper()
        return {
            "domain": DOMAIN,
            "data": {
                "T_mean": float(payload.get("risk_score", 0.5)),
                "H_score": float(payload.get("confidence_index", 0.5)),
                "A_score": float(payload.get("audit_score", 0.5)),
                "S": float(payload.get("threshold_s", DEFAULT_THRESHOLD_S)),
            },
            "meta": {
                "flow_type":    flow_type,
                "ir_intent":    FLOW_TO_INTENT.get(flow_type, "GENERAL_FLOW"),
                "risk_class":   payload.get("risk_class", ""),
                "zone":         payload.get("zone", ""),
                "gate_version": GATE_VERSION,
            },
        }

    def evaluate(
        self,
        payload: dict[str, Any],
        timeout: float = 10.0,
    ) -> dict[str, Any]:
        ir_payload = self.translate_to_ir(payload)

        if not _REQUESTS_OK or _requests is None:
            verdict = "HOLD"
            return {
                "verdict": verdict,
                "domain": DOMAIN,
                "source": "GATE_REQUESTS_UNAVAILABLE",
                "ir_payload": ir_payload,
                "receipt": self.build_decision_receipt(
                    verdict,
                    ir_payload,
                    source="GATE_REQUESTS_UNAVAILABLE",
                ),
            }

        try:
            response = _requests.post(
                KERNEL_URL,
                json=ir_payload,
                timeout=timeout,
            )
            response.raise_for_status()
            kernel_decision = response.json()

        except Exception as exc:
            verdict = "HOLD"
            return {
                "verdict": verdict,
                "domain": DOMAIN,
                "source": "GATE_FAIL_CLOSED",
                "error": str(exc)[:200],
                "ir_payload": ir_payload,
                "receipt": self.build_decision_receipt(
                    verdict,
                    ir_payload,
                    source="GATE_FAIL_CLOSED",
                ),
            }

        verdict = kernel_decision.get(
            "verdict",
            "HOLD",
        )

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
            "ir_payload": ir_payload,
            "kernel_decision": kernel_decision or {},
            "created_at_ms": int(time.time() * 1000),
        }

        signature = hashlib.sha256(
            json.dumps(
                unsigned,
                sort_keys=True,
                ensure_ascii=False,
                default=str,
            ).encode("utf-8")
        ).hexdigest()

        os3_ticket = self.build_os3_ticket(
            verdict=verdict,
            ir_payload=ir_payload,
            kernel_decision=kernel_decision,
            source=source,
        )

        return {
            **unsigned,
            "signature_kind":
                "LOCAL_SHA256_DEMO_NOT_PRODUCTION_SIGNING",
            "signed_decision_receipt_sha256":
                signature,
            "os3_ticket":
                os3_ticket.to_dict(),
            "os3_ticket_valid":
                ticket_is_valid(os3_ticket),
        }

    def build_os3_ticket(
        self,
        verdict: str,
        ir_payload: dict[str, Any],
        kernel_decision: dict[str, Any] | None = None,
        *,
        source: str,
    ):
        kernel_decision = (
            kernel_decision
            if isinstance(kernel_decision, dict)
            else {}
        )

        canonical_gate = str(
            kernel_decision.get("x108_gate")
            or verdict
            or "HOLD"
        ).upper()

        if canonical_gate == "BLOCK":
            severity = "S4"
        elif canonical_gate == "HOLD":
            severity = "S2"
        else:
            severity = "S0"

        severity = str(
            kernel_decision.get("severity")
            or severity
        )

        reason_code = str(
            kernel_decision.get("reason_code")
            or source
        )

        ir_hash = hashlib.sha256(
            json.dumps(
                ir_payload,
                sort_keys=True,
                ensure_ascii=False,
                default=str,
            ).encode("utf-8")
        ).hexdigest()

        meta = (
            ir_payload.get("meta", {})
            if isinstance(ir_payload, dict)
            else {}
        )

        data = (
            ir_payload.get("data", {})
            if isinstance(ir_payload, dict)
            else {}
        )

        action_candidate = SimpleNamespace(
            action_id=f"gps-{ir_hash[:16]}",
            domain=DOMAIN,
            intent=meta.get(
                "ir_intent",
                "GENERAL_FLOW",
            ),
            action_type=meta.get(
                "flow_type",
                "UNKNOWN",
            ),
            payload=ir_payload,
        )

        packet = SimpleNamespace(
            domain=DOMAIN,
            gate="P3-05",
            gate_version=GATE_VERSION,
            ir_payload=ir_payload,
        )

        envelope = SimpleNamespace(
            x108_gate=canonical_gate,
            reason_code=reason_code,
            severity=severity,
            metrics=dict(
                kernel_decision.get("metrics")
                or data
                or {}
            ),
            unknowns=list(
                kernel_decision.get("unknowns")
                or []
            ),
            risk_flags=list(
                kernel_decision.get("risk_flags")
                or []
            ),
            contradictions=list(
                kernel_decision.get("contradictions")
                or []
            ),
            evidence_refs=[
                "domains/gps/gps_x108_gate.py",
                "periphery/os3_ticket.py",
                f"ir_payload_sha256:{ir_hash}",
            ],
        )

        return build_os3_ticket(
            action_candidate,
            packet,
            envelope,
        )


def evaluate_gps_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return GpsX108Gate().evaluate(payload)
