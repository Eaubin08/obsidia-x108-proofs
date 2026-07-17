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
            return {
                "verdict":  "HOLD",
                "domain":   DOMAIN,
                "source":   "GATE_REQUESTS_UNAVAILABLE",
                "ir_payload": ir_payload,
            }

        try:
            response = _requests.post(
                KERNEL_URL, json=ir_payload, timeout=timeout
            )
            response.raise_for_status()
            kernel_decision = response.json()
        except Exception as exc:
            return {
                "verdict":  "HOLD",
                "domain":   DOMAIN,
                "source":   "GATE_FAIL_CLOSED",
                "error":    str(exc)[:200],
                "ir_payload": ir_payload,
            }

        return {
            "verdict":         kernel_decision.get("verdict", "HOLD"),
            "domain":          DOMAIN,
            "source":          "KERNEL_X108",
            "kernel_response": kernel_decision,
            "ir_payload":      ir_payload,
            "gate_version":    GATE_VERSION,
        }


def evaluate_gps_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return GpsX108Gate().evaluate(payload)
