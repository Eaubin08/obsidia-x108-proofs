"""
domains/trading/trading_x108_gate.py — Gate de gouvernance TRADING → Kernel X-108
P3-03 — V3.2.2 COMPLETION

RÈGLE ABSOLUE :
  Ce gate NE DÉCIDE JAMAIS de façon autonome.
  Il traduit le payload trading en IR et le soumet au Kernel X-108.
  La décision (ALLOW / HOLD / BLOCK) appartient au Kernel uniquement.
  Fail-Closed : si le Kernel est injoignable → HOLD systématique.

Branche depuis : connectors/trading_live.py (observateur live)
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
DOMAIN: str = "trading"
GATE_VERSION: str = "v1"

FLOW_TO_INTENT: dict[str, str] = {
    "BUY":            "CREATE_PATCH",
    "SELL":           "CREATE_PATCH",
    "LIMIT_ORDER":    "CREATE_PATCH",
    "MARKET_ORDER":   "CREATE_PATCH",
    "CANCEL":         "AUDIT_ONLY",
    "POSITION_CHECK": "AUDIT_ONLY",
    "RISK_SCAN":      "AUDIT_ONLY",
    "MARGIN_CALL":    "AUDIT_ONLY",
}

DEFAULT_THRESHOLD_S: float = 0.6


class TradingX108Gate:
    """
    Gate de gouvernance TRADING → Kernel X-108.
    Ne prend AUCUNE décision autonome.
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


def evaluate_trading_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return TradingX108Gate().evaluate(payload)
