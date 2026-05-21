"""
Bridge Risk Gate.
BRIDGE_RISK_UNEVALUATED -> HOLD. BRIDGE_TRANSFER -> BLOCK in V4.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BridgeRiskDecision:
    bridge_id: str
    source_chain: str
    dest_chain: str
    gate: str
    reason: str
    risk_score: float
    risk_flags: list[str] = field(default_factory=list)
    real_bridge_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "bridge_id": self.bridge_id,
            "source_chain": self.source_chain,
            "dest_chain": self.dest_chain,
            "gate": self.gate,
            "reason": self.reason,
            "risk_score": self.risk_score,
            "risk_flags": self.risk_flags,
            "real_bridge_allowed": self.real_bridge_allowed,
        }


def evaluate_bridge_risk(
    bridge_id: str,
    source_chain: str,
    dest_chain: str,
    bridge_audited: bool = False,
    liquidity_verified: bool = False,
) -> BridgeRiskDecision:
    risk_flags = []
    risk_score = 0.5

    if not bridge_audited:
        risk_flags.append("BRIDGE_RISK_UNEVALUATED")
        risk_score = max(risk_score, 0.8)

    if not liquidity_verified:
        risk_flags.append("BRIDGE_LIQUIDITY_UNVERIFIED")
        risk_score = max(risk_score, 0.6)

    if source_chain.lower() in ("mainnet", "ethereum", "1") or dest_chain.lower() in ("mainnet", "ethereum", "1"):
        risk_flags.append("MAINNET_BRIDGE_BLOCKED_V4")
        risk_score = 1.0
        return BridgeRiskDecision(
            bridge_id=bridge_id,
            source_chain=source_chain,
            dest_chain=dest_chain,
            gate="BLOCK",
            reason="BRIDGE_TRANSFER_BLOCKED_V4_MAINNET",
            risk_score=risk_score,
            risk_flags=risk_flags,
            real_bridge_allowed=False,
        )

    gate = "HOLD" if risk_flags else "ALLOW"
    return BridgeRiskDecision(
        bridge_id=bridge_id,
        source_chain=source_chain,
        dest_chain=dest_chain,
        gate=gate,
        reason="BRIDGE_RISK_EVALUATED_HOLD_PENDING_REVIEW" if risk_flags else "BRIDGE_RISK_LOW",
        risk_score=risk_score,
        risk_flags=risk_flags,
        real_bridge_allowed=False,
    )
