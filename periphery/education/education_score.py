"""
Score_i = w1*S + w2*C + w3*R + w4*F + w5*D
S=stability, C=coherence, R=memory_reuse, F=correct_refusal, D=absence_of_drift
"""
from __future__ import annotations

from dataclasses import dataclass

_W1, _W2, _W3, _W4, _W5 = 0.25, 0.25, 0.20, 0.15, 0.15


@dataclass
class EducationScore:
    episode_id: str
    stability: float
    coherence: float
    memory_reuse: float
    correct_refusal: float
    absence_of_drift: float
    score: float
    level: str

    def to_dict(self) -> dict:
        return {
            "episode_id": self.episode_id,
            "score": self.score,
            "level": self.level,
            "stability": self.stability,
            "coherence": self.coherence,
            "memory_reuse": self.memory_reuse,
            "correct_refusal": self.correct_refusal,
            "absence_of_drift": self.absence_of_drift,
        }


def compute_education_score(
    episode_id: str,
    stability: float,
    coherence: float,
    memory_reuse: float,
    correct_refusal: float,
    absence_of_drift: float,
) -> EducationScore:
    score = (
        _W1 * stability
        + _W2 * coherence
        + _W3 * memory_reuse
        + _W4 * correct_refusal
        + _W5 * absence_of_drift
    )
    score = max(0.0, min(1.0, score))

    if score >= 0.85:
        level = "ADVANCED"
    elif score >= 0.65:
        level = "INTERMEDIATE"
    elif score >= 0.40:
        level = "BASIC"
    else:
        level = "BELOW_THRESHOLD"

    return EducationScore(
        episode_id=episode_id,
        stability=stability,
        coherence=coherence,
        memory_reuse=memory_reuse,
        correct_refusal=correct_refusal,
        absence_of_drift=absence_of_drift,
        score=score,
        level=level,
    )
