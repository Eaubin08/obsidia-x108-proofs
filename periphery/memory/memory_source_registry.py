"""
Memory Source Registry — registers and validates memory sources.
All sources are readonly. No write to real memory systems.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .memory_source_types import MemorySourceType


@dataclass
class MemorySourceEntry:
    source_id: str
    source_type: MemorySourceType
    readonly: bool = True
    write_allowed: bool = False
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_type": self.source_type.value,
            "readonly": self.readonly,
            "write_allowed": self.write_allowed,
            "description": self.description,
        }


_DEFAULT_SOURCES = [
    MemorySourceEntry("brody_runtime", MemorySourceType.BRODY_RUNTIME, readonly=True, write_allowed=False),
    MemorySourceEntry("graphiti_graph", MemorySourceType.GRAPHITI_GRAPH, readonly=True, write_allowed=False),
    MemorySourceEntry("context_packet", MemorySourceType.CONTEXT_PACKET, readonly=True, write_allowed=False),
    MemorySourceEntry("feedback_capture", MemorySourceType.FEEDBACK_CAPTURE, readonly=True, write_allowed=False),
]

_REGISTRY: dict[str, MemorySourceEntry] = {s.source_id: s for s in _DEFAULT_SOURCES}


def register_source(entry: MemorySourceEntry) -> None:
    if entry.write_allowed:
        raise ValueError(f"MEMORY_SOURCE_WRITE_FORBIDDEN:{entry.source_id}")
    _REGISTRY[entry.source_id] = entry


def get_source(source_id: str) -> MemorySourceEntry | None:
    return _REGISTRY.get(source_id)


def list_sources() -> list[MemorySourceEntry]:
    return list(_REGISTRY.values())
