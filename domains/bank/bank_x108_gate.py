"""
domains/bank/bank_x108_gate.py — Gate de gouvernance BANK → Kernel X-108
P3-01 — V3.2.2 COMPLETION

RÈGLE ABSOLUE :
  Ce gate NE DÉCIDE JAMAIS de façon autonome.
  Il traduit le payload bank en IR et le soumet au Kernel X-108.
  La décision (ALLOW / HOLD / BLOCK) appartient au Kernel uniquement.
  Fail-Closed : si le Kernel est injoignable → HOLD systématique.

Branche depuis : connectors/bank_normal_flow.py (observateur live)
Ce gate est la couche de gouvernance formelle en amont du connecteur.
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
DOMAIN: str = "bank"
GATE_VERSION: str = "v1"

# Mapping flux métier bank → IR intent
FLOW_TO_INTENT: dict[str, str] = {
    "PAYMENT":        "CREATE_PATCH",
    "TRANSFER":       "CREATE_PATCH",
    "WITHDRAWAL":     "CREATE_PATCH",
    "DEPOSIT":        "CREATE_PATCH",
    "BALANCE_CHECK":  "AUDIT_ONLY",
    "STATEMENT":      "AUDIT_ONLY",
    "FRAUD_ALERT":    "AUDIT_ONLY",
    "COMPLIANCE_SCAN": "AUDIT_ONLY",
}

# Seuil de décision par défaut
DEFAULT_THRESHOLD_S: float = 0.6


class BankX108Gate:
    """
    Gate de gouvernance BANK → Kernel X-108.

    Traduit les payloads bank (risk_score, confidence_index, audit_score)
    en IR (T_mean, H_score, A_score, S) et délègue la décision au Kernel.

    Ne prend AUCUNE décision autonome.
    Ne réplique PAS la logique ALLOW/HOLD/BLOCK.
    """

    def translate_to_ir(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Traduit un payload bank en Représentation Interne Kernel."""
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
        """
        Soumet le payload au Kernel X-108 et retourne sa décision.
        Fail-Closed : Kernel injoignable → HOLD systématique.
        """
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


def evaluate_bank_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Évalue un payload bank via le Gate X108. Retourne la décision du Kernel."""
    return BankX108Gate().evaluate(payload)
