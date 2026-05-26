"""
DeFi Risk Gate. Swap/Stake/Borrow require risk evaluation before any action.
All real DeFi actions blocked in V4.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DeFiRiskDecision:
    action_id: str
    defi_protocol: str
    operation: str
    gate: str
    reason: str
    risk_score: float
    risk_flags: list[str] = field(default_factory=list)
    real_defi_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "defi_protocol": self.defi_protocol,
            "operation": self.operation,
            "gate": self.gate,
            "reason": self.reason,
            "risk_score": self.risk_score,
            "risk_flags": self.risk_flags,
            "real_defi_allowed": self.real_defi_allowed,
        }


_HIGH_RISK_OPS = {"BORROW", "LEVERAGE", "FLASH_LOAN", "LIQUIDATE"}


def evaluate_defi_risk(
    action_id: str,
    defi_protocol: str,
    operation: str,
    slippage_pct: float = 0.0,
    protocol_audited: bool = False,
    is_mainnet: bool = False,
) -> DeFiRiskDecision:
    risk_flags = []
    risk_score = 0.3
    op_upper = operation.upper()

    if is_mainnet:
        risk_flags.append("MAINNET_DEFI_BLOCKED_V4")
        risk_score = 1.0
        return DeFiRiskDecision(
            action_id=action_id,
            defi_protocol=defi_protocol,
            operation=operation,
            gate="BLOCK",
            reason="DEFI_MAINNET_BLOCKED_V4",
            risk_score=risk_score,
            risk_flags=risk_flags,
            real_defi_allowed=False,
        )

    if op_upper in _HIGH_RISK_OPS:
        risk_flags.append(f"HIGH_RISK_DEFI_OPERATION:{op_upper}")
        risk_score = max(risk_score, 0.9)

    if slippage_pct > 5.0:
        risk_flags.append("HIGH_SLIPPAGE")
        risk_score = max(risk_score, 0.7)

    if not protocol_audited:
        risk_flags.append("PROTOCOL_UNAUDITED")
        risk_score = max(risk_score, 0.6)

    gate = "HOLD" if risk_flags else "ALLOW"
    return DeFiRiskDecision(
        action_id=action_id,
        defi_protocol=defi_protocol,
        operation=operation,
        gate=gate,
        reason="DEFI_RISK_EVALUATED",
        risk_score=risk_score,
        risk_flags=risk_flags,
        real_defi_allowed=False,
    )
