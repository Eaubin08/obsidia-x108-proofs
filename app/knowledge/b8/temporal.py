"""Valid-time algebra, V1 SAME_FRAME_ONLY (spec §5.1; TEMPORAL_ORDER_AND_TRANSFORM_HOLD_V1).

Intervals are half-open [start, end) inside one TemporalFrameRef; None means unbounded (−∞ start, +∞ end).
Relations across different frames are TEMPORALLY_INDETERMINATE (never False): no transform, no conversion.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class TemporalFrameRef:
    """Opaque frame identity; compared by explicit identity only (never by name similarity)."""
    frame_id: str

    def to_canonical(self) -> dict:
        return {"frame_id": self.frame_id}


@dataclass(frozen=True)
class ValidTimeInterval:
    temporal_frame_ref: TemporalFrameRef
    start: Optional[Any]
    end: Optional[Any]

    def to_canonical(self) -> dict:
        return {"temporal_frame_ref": self.temporal_frame_ref.to_canonical(), "start": self.start, "end": self.end,
                "boundary_semantics": "HALF_OPEN"}


class _Indeterminate:
    __slots__ = ()

    def __repr__(self) -> str:
        return "TEMPORALLY_INDETERMINATE"

    def __bool__(self) -> bool:
        raise TypeError("TEMPORALLY_INDETERMINATE has no truth value")


TEMPORALLY_INDETERMINATE = _Indeterminate()


def temporally_comparable(a: ValidTimeInterval, b: ValidTimeInterval) -> bool:
    return a.temporal_frame_ref == b.temporal_frame_ref


def _start_before_end(start, end) -> bool:
    return start is None or end is None or start < end


def _start_le(outer, inner) -> bool:
    return outer is None or (inner is not None and outer <= inner)


def _end_le(inner, outer) -> bool:
    return outer is None or (inner is not None and inner <= outer)


def overlaps(a: ValidTimeInterval, b: ValidTimeInterval):
    if not temporally_comparable(a, b):
        return TEMPORALLY_INDETERMINATE
    return _start_before_end(a.start, b.end) and _start_before_end(b.start, a.end)


def contains(a: ValidTimeInterval, b: ValidTimeInterval):
    if not temporally_comparable(a, b):
        return TEMPORALLY_INDETERMINATE
    return _start_le(a.start, b.start) and _end_le(b.end, a.end)
