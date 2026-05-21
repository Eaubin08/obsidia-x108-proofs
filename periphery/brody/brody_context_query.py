"""
Brody Context Query — queries context for Brody response generation.
Read-only. No memory write.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BrodyContextQuery:
    query_id: str
    query_text: str
    language: str
    context_filters: list[str]
    max_context_items: int = 10
    readonly: bool = True
    memory_write: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_id": self.query_id,
            "query_text": self.query_text,
            "language": self.language,
            "context_filters": self.context_filters,
            "max_context_items": self.max_context_items,
            "readonly": self.readonly,
            "memory_write": self.memory_write,
        }


def build_context_query(
    query_id: str,
    query_text: str,
    language: str = "en",
    context_filters: list[str] | None = None,
) -> BrodyContextQuery:
    return BrodyContextQuery(
        query_id=query_id,
        query_text=query_text[:500],
        language=language,
        context_filters=context_filters or [],
        readonly=True,
        memory_write=False,
    )
