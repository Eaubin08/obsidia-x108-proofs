"""
Wallet Security Gate.
PRIVATE_KEY_REQUESTED -> BLOCK (absolute)
SEED_PHRASE_REQUESTED -> BLOCK (absolute)
No wallet connection, no key storage, no signing in V4.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_BLOCKED_KEYWORDS = {
    "private_key", "privatekey", "secret_key", "secretkey",
    "seed_phrase", "seedphrase", "mnemonic", "keystore",
    "wallet_connect", "walletconnect",
}


@dataclass
class WalletSecurityDecision:
    request_id: str
    request_type: str
    blocked: bool
    reason: str
    private_key_requested: bool = False
    seed_phrase_requested: bool = False
    wallet_connect_requested: bool = False
    real_wallet_access_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "request_type": self.request_type,
            "blocked": self.blocked,
            "reason": self.reason,
            "private_key_requested": self.private_key_requested,
            "seed_phrase_requested": self.seed_phrase_requested,
            "wallet_connect_requested": self.wallet_connect_requested,
            "real_wallet_access_allowed": self.real_wallet_access_allowed,
        }


def evaluate_wallet_request(request_id: str, request_type: str, payload: dict | None = None) -> WalletSecurityDecision:
    rt = request_type.lower().replace("-", "_").replace(" ", "_")
    p_str = str(payload or {}).lower()

    pk_requested = any(k in rt or k in p_str for k in ("private_key", "privatekey", "secret_key"))
    seed_requested = any(k in rt or k in p_str for k in ("seed_phrase", "seedphrase", "mnemonic"))
    wc_requested = any(k in rt or k in p_str for k in ("wallet_connect", "walletconnect", "connect_wallet"))

    if pk_requested:
        return WalletSecurityDecision(
            request_id=request_id,
            request_type=request_type,
            blocked=True,
            reason="PRIVATE_KEY_REQUESTED_ABSOLUTE_BLOCK",
            private_key_requested=True,
        )
    if seed_requested:
        return WalletSecurityDecision(
            request_id=request_id,
            request_type=request_type,
            blocked=True,
            reason="SEED_PHRASE_REQUESTED_ABSOLUTE_BLOCK",
            seed_phrase_requested=True,
        )
    if wc_requested:
        return WalletSecurityDecision(
            request_id=request_id,
            request_type=request_type,
            blocked=True,
            reason="WALLET_CONNECT_BLOCKED_V4",
            wallet_connect_requested=True,
        )

    return WalletSecurityDecision(
        request_id=request_id,
        request_type=request_type,
        blocked=False,
        reason="WALLET_READ_ADVISORY_ONLY",
        real_wallet_access_allowed=False,
    )
