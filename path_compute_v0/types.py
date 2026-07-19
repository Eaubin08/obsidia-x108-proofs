"""Readonly advisory data shapes."""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class PathCandidateNote:
    candidate_id: str
    label: str
    confidence: float = 0.0
    evidence_refs: Tuple[str, ...] = ()
    advisory_only: bool = True
