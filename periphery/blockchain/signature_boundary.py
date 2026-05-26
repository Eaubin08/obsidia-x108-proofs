"""
Signature Boundary.
SIGNATURE_REQUESTED -> BLOCK in V4.
TRANSACTION_SIGNING_REQUESTED -> BLOCK in V4.
Never stores, reads, or passes private keys.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SignatureBoundaryDecision:
    request_id: str
    signature_type: str
    blocked: bool
    reason: str
    signing_attempted: bool = False
    key_exposed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "signature_type": self.signature_type,
            "blocked": self.blocked,
            "reason": self.reason,
            "signing_attempted": self.signing_attempted,
            "key_exposed": self.key_exposed,
        }


_ALWAYS_BLOCKED = {
    "SIGN_MESSAGE", "SIGN_TRANSACTION", "ETH_SIGN", "PERSONAL_SIGN",
    "SIGN_TYPED_DATA", "WALLET_SIGN", "EIP712_SIGN",
}


def evaluate_signature_request(request_id: str, signature_type: str) -> SignatureBoundaryDecision:
    sig_upper = signature_type.upper().replace("-", "_").replace(" ", "_")

    if sig_upper in _ALWAYS_BLOCKED or "SIGN" in sig_upper:
        return SignatureBoundaryDecision(
            request_id=request_id,
            signature_type=signature_type,
            blocked=True,
            reason=f"SIGNATURE_REQUESTED_BLOCKED_V4:{sig_upper}",
            signing_attempted=False,
            key_exposed=False,
        )

    return SignatureBoundaryDecision(
        request_id=request_id,
        signature_type=signature_type,
        blocked=False,
        reason="SIGNATURE_TYPE_NOT_DETECTED",
        signing_attempted=False,
        key_exposed=False,
    )


def assert_no_private_key_in_payload(payload: dict) -> None:
    payload_str = str(payload).lower()
    forbidden = ["private_key", "privatekey", "secret_key", "secretkey", "seed_phrase", "mnemonic", "keystore"]
    for kw in forbidden:
        if kw in payload_str:
            raise AssertionError(f"PRIVATE_KEY_OR_SEED_IN_PAYLOAD:{kw}")
