"""
Audience Projection — maps context to target audience profile. Advisory only.
Reverse OS projects, never decides.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_AUDIENCE_PROFILES = {
    "technical": {"complexity": "high", "jargon": "allowed", "format": "structured"},
    "executive": {"complexity": "low", "jargon": "minimal", "format": "summary"},
    "operator": {"complexity": "medium", "jargon": "domain", "format": "operational"},
    "general": {"complexity": "low", "jargon": "none", "format": "narrative"},
    "auditor": {"complexity": "high", "jargon": "formal", "format": "evidence_based"},
}

_FORBIDDEN_SOVEREIGN_TOKENS = {"ALLOW", "HOLD", "BLOCK", "ACT", "DECIDE", "VERDICT"}


@dataclass
class AudienceProjection:
    projection_id: str
    audience: str
    complexity: str
    jargon: str
    format: str
    advisory_only: bool = True
    can_decide: bool = False
    forbidden_tokens_detected: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "projection_id": self.projection_id,
            "audience": self.audience,
            "complexity": self.complexity,
            "jargon": self.jargon,
            "format": self.format,
            "advisory_only": self.advisory_only,
            "can_decide": self.can_decide,
            "forbidden_tokens_detected": self.forbidden_tokens_detected,
        }


def project_audience(projection_id: str, context: str, preferred_audience: str = "general") -> AudienceProjection:
    profile = _AUDIENCE_PROFILES.get(preferred_audience, _AUDIENCE_PROFILES["general"])
    tokens = [t for t in _FORBIDDEN_SOVEREIGN_TOKENS if t.lower() in context.lower()]
    return AudienceProjection(
        projection_id=projection_id,
        audience=preferred_audience,
        complexity=profile["complexity"],
        jargon=profile["jargon"],
        format=profile["format"],
        advisory_only=True,
        can_decide=False,
        forbidden_tokens_detected=tokens,
    )
