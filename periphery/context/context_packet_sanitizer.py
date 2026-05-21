"""
Context Packet Sanitizer — strips or redacts forbidden sovereign tokens from context items.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_FORBIDDEN_TOKENS = {"ALLOW", "HOLD", "BLOCK", "ACT", "DECIDE", "VERDICT",
                     "AUTHORIZE", "APPROVE", "EXECUTE", "DEPLOY"}


@dataclass
class SanitizedContextPacket:
    packet_id: str
    sanitized_items: list[str]
    tokens_redacted: list[str] = field(default_factory=list)
    readonly: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "sanitized_items": self.sanitized_items,
            "tokens_redacted": self.tokens_redacted,
            "readonly": self.readonly,
        }


def sanitize_context_packet(packet_id: str, context_items: list[str]) -> SanitizedContextPacket:
    sanitized: list[str] = []
    redacted: list[str] = []

    for item in context_items:
        words = item.split()
        new_words = []
        for word in words:
            clean = word.strip(".,;:!?\"'")
            if clean.upper() in _FORBIDDEN_TOKENS:
                new_words.append(f"[REDACTED_{clean.upper()}]")
                redacted.append(clean.upper())
            else:
                new_words.append(word)
        sanitized.append(" ".join(new_words))

    return SanitizedContextPacket(
        packet_id=packet_id,
        sanitized_items=sanitized,
        tokens_redacted=list(set(redacted)),
        readonly=True,
    )
