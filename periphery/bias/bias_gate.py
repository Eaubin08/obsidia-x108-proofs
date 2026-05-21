"""
BiasGate — intercepts unvalidated bias before it reaches a sovereign decision.
Bias ≠ 0 is expected. Bias -> sovereign decision without validation is blocked.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BiasGateResult:
    action_id: str
    bias_detected: bool
    bias_validated: bool
    gate_result: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "bias_detected": self.bias_detected,
            "bias_validated": self.bias_validated,
            "gate_result": self.gate_result,
            "reason": self.reason,
        }


def apply_bias_gate(action_id: str, bias_score: float, bias_validated: bool) -> BiasGateResult:
    bias_detected = bias_score > 0.0

    if bias_detected and not bias_validated:
        return BiasGateResult(
            action_id=action_id,
            bias_detected=True,
            bias_validated=False,
            gate_result="HOLD",
            reason="UNVALIDATED_BIAS_DETECTED_BLOCKED_FROM_SOVEREIGN_DECISION",
        )

    return BiasGateResult(
        action_id=action_id,
        bias_detected=bias_detected,
        bias_validated=bias_validated,
        gate_result="PASS",
        reason="BIAS_VALIDATED_OR_ZERO" if bias_detected else "NO_BIAS_DETECTED",
    )
