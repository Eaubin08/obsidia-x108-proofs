"""
Token Policy.
Gencoin is NOT a real token. No token mint, no token deployment, no smart contract.
TOKEN_MINT -> BLOCK_CANDIDATE in V4.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TokenPolicyDecision:
    token_id: str
    action: str
    gate: str
    reason: str
    is_gencoin: bool
    mint_allowed: bool = False
    real_token_created: bool = False
    smart_contract_created: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "token_id": self.token_id,
            "action": self.action,
            "gate": self.gate,
            "reason": self.reason,
            "is_gencoin": self.is_gencoin,
            "mint_allowed": self.mint_allowed,
            "real_token_created": self.real_token_created,
            "smart_contract_created": self.smart_contract_created,
        }


_BLOCKED_TOKEN_ACTIONS = {"MINT", "DEPLOY", "CREATE", "TOKEN_MINT", "TOKEN_DEPLOY"}


def evaluate_token_policy(
    token_id: str,
    action: str,
    is_gencoin: bool = False,
) -> TokenPolicyDecision:
    action_upper = action.upper().replace("-", "_").replace(" ", "_")

    if is_gencoin:
        return TokenPolicyDecision(
            token_id=token_id,
            action=action,
            gate="BLOCK",
            reason="GENCOIN_IS_NOT_A_REAL_TOKEN_LEDGER_ONLY",
            is_gencoin=True,
            mint_allowed=False,
            real_token_created=False,
            smart_contract_created=False,
        )

    if action_upper in _BLOCKED_TOKEN_ACTIONS:
        return TokenPolicyDecision(
            token_id=token_id,
            action=action,
            gate="BLOCK",
            reason=f"TOKEN_ACTION_BLOCKED_V4:{action_upper}",
            is_gencoin=False,
            mint_allowed=False,
        )

    return TokenPolicyDecision(
        token_id=token_id,
        action=action,
        gate="HOLD",
        reason="TOKEN_ACTION_REQUIRES_REVIEW",
        is_gencoin=False,
        mint_allowed=False,
    )
