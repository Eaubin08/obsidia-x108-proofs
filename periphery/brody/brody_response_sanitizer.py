"""
Brody Response Sanitizer — removes forbidden sovereign tokens from Brody outputs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_FORBIDDEN = {"ALLOW", "HOLD", "BLOCK", "ACT", "DECIDE", "VERDICT", "AUTHORIZE", "APPROVE"}


@dataclass
class SanitizedResponse:
    original_id: str
    sanitized_text: str
    forbidden_tokens_removed: list[str]
    sanitized: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "original_id": self.original_id,
            "sanitized_text": self.sanitized_text,
            "forbidden_tokens_removed": self.forbidden_tokens_removed,
            "sanitized": self.sanitized,
        }


def sanitize_brody_response(response_id: str, text: str) -> SanitizedResponse:
    removed = []
    result = text
    for token in _FORBIDDEN:
        if token in result:
            result = result.replace(token, f"[REDACTED_{token}]")
            removed.append(token)
    return SanitizedResponse(
        original_id=response_id,
        sanitized_text=result,
        forbidden_tokens_removed=removed,
        sanitized=len(removed) > 0,
    )
