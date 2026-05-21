"""
Format Projection — maps context to output format recommendation. Advisory only.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class FormatProjection:
    projection_id: str
    recommended_format: str
    rationale: str
    advisory_only: bool = True
    can_decide: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "projection_id": self.projection_id,
            "recommended_format": self.recommended_format,
            "rationale": self.rationale,
            "advisory_only": self.advisory_only,
            "can_decide": self.can_decide,
        }


_FORMAT_MAP = {
    "technical": "structured_markdown",
    "executive": "bullet_summary",
    "operator": "step_by_step",
    "general": "narrative_prose",
    "auditor": "evidence_table",
}


def project_format(projection_id: str, audience: str) -> FormatProjection:
    fmt = _FORMAT_MAP.get(audience, "narrative_prose")
    return FormatProjection(
        projection_id=projection_id,
        recommended_format=fmt,
        rationale=f"FORMAT_FOR_AUDIENCE_{audience.upper()}",
        advisory_only=True,
        can_decide=False,
    )
