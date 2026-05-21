"""
Crypto Boundary — enforces sandbox limits. Never claims to break or replace
SHA-256, ECDSA, EdDSA, or any standard cryptographic primitive.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

_CLAIM_KEYWORDS = {
    "break", "crack", "bypass", "replace_sha", "replace_ecdsa",
    "custom_crypto", "proprietary_hash", "better_than_sha",
}


@dataclass
class CryptoBoundaryResult:
    input_id: str
    sandbox_only: bool = True
    crypto_claim_detected: bool = False
    claim_blocked: bool = False
    sha256_hash: str = ""
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_id": self.input_id,
            "sandbox_only": self.sandbox_only,
            "crypto_claim_detected": self.crypto_claim_detected,
            "claim_blocked": self.claim_blocked,
            "sha256_hash": self.sha256_hash,
            "reason": self.reason,
        }


def evaluate_crypto_boundary(input_id: str, content: str) -> CryptoBoundaryResult:
    content_lower = content.lower()
    claim_detected = any(kw in content_lower for kw in _CLAIM_KEYWORDS)

    if claim_detected:
        return CryptoBoundaryResult(
            input_id=input_id,
            sandbox_only=True,
            crypto_claim_detected=True,
            claim_blocked=True,
            reason="UNSUPPORTED_CRYPTO_CLAIM_BLOCKED",
        )

    h = hashlib.sha256(content.encode()).hexdigest()
    return CryptoBoundaryResult(
        input_id=input_id,
        sandbox_only=True,
        crypto_claim_detected=False,
        claim_blocked=False,
        sha256_hash=h,
        reason="SANDBOX_HASH_ONLY_NOT_CRYPTO_PROTOCOL",
    )
