"""
Brody Language Router — routes to language-specific response chains.
Read-only. No memory write.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_SUPPORTED_LANGUAGES = {"en", "fr", "es", "de", "pt", "it"}


@dataclass
class BrodyLanguageRoute:
    query_id: str
    detected_language: str
    routed_to: str
    is_supported: bool
    memory_write: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_id": self.query_id,
            "detected_language": self.detected_language,
            "routed_to": self.routed_to,
            "is_supported": self.is_supported,
            "memory_write": self.memory_write,
        }


def route_brody_language(query_id: str, language_code: str) -> BrodyLanguageRoute:
    lang = language_code.lower()[:2]
    is_supported = lang in _SUPPORTED_LANGUAGES
    routed = f"brody_{lang}_chain" if is_supported else "brody_default_chain"
    return BrodyLanguageRoute(
        query_id=query_id,
        detected_language=lang,
        routed_to=routed,
        is_supported=is_supported,
        memory_write=False,
    )
