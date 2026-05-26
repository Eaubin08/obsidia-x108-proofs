"""
Smart Contract Risk Gate.
No contract deployment without audit. No unverified contract calls in V4.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SmartContractRiskDecision:
    contract_id: str
    action: str
    gate: str
    reason: str
    audit_required: bool
    deploy_blocked: bool
    risk_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "action": self.action,
            "gate": self.gate,
            "reason": self.reason,
            "audit_required": self.audit_required,
            "deploy_blocked": self.deploy_blocked,
            "risk_flags": self.risk_flags,
        }


def evaluate_smart_contract_risk(
    contract_id: str,
    action: str,
    has_audit: bool = False,
    is_verified: bool = False,
    is_proxy: bool = False,
    has_unbounded_approval: bool = False,
) -> SmartContractRiskDecision:
    risk_flags = []
    action_upper = action.upper()

    if action_upper == "DEPLOY":
        if not has_audit:
            risk_flags.append("DEPLOY_WITHOUT_AUDIT")
            return SmartContractRiskDecision(
                contract_id=contract_id,
                action=action,
                gate="BLOCK",
                reason="SMART_CONTRACT_DEPLOY_WITHOUT_AUDIT",
                audit_required=True,
                deploy_blocked=True,
                risk_flags=risk_flags,
            )

    if has_unbounded_approval:
        risk_flags.append("UNBOUNDED_TOKEN_APPROVAL")

    if is_proxy and not is_verified:
        risk_flags.append("UNVERIFIED_PROXY_CONTRACT")

    if not is_verified and action_upper not in ("READ", "VIEW", "CALL_VIEW"):
        risk_flags.append("UNVERIFIED_CONTRACT")

    gate = "HOLD" if risk_flags else "ALLOW"
    return SmartContractRiskDecision(
        contract_id=contract_id,
        action=action,
        gate=gate,
        reason="CONTRACT_RISK_EVALUATED",
        audit_required=not has_audit,
        deploy_blocked=False,
        risk_flags=risk_flags,
    )
