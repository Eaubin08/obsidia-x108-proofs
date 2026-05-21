"""
Frequency Tag Mapper — maps symbolic frequency labels to Hz ranges.
Symbolic frequency != physical proof. Tags are heuristic labels only.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_FREQUENCY_TAGS = {
    "delta": (0.5, 4.0, "deep_sleep_brainwave"),
    "theta": (4.0, 8.0, "drowsy_meditative"),
    "alpha": (8.0, 13.0, "relaxed_alert"),
    "beta": (13.0, 30.0, "active_thinking"),
    "gamma": (30.0, 100.0, "high_cognition"),
    "infrasound": (0.0, 20.0, "below_human_hearing"),
    "audible": (20.0, 20000.0, "human_hearing_range"),
    "ultrasound": (20000.0, 1e9, "above_human_hearing"),
    "radio_lf": (30e3, 300e3, "low_frequency_radio"),
    "microwave": (1e9, 300e9, "microwave_band"),
    "visible_light": (4e14, 7.9e14, "visible_electromagnetic"),
}


@dataclass
class FrequencyTagResult:
    frequency_hz: float
    matched_tags: list[str]
    symbolic_meaning: list[str]
    is_symbolic_only: bool = True
    is_physical_claim: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "frequency_hz": self.frequency_hz,
            "matched_tags": self.matched_tags,
            "symbolic_meaning": self.symbolic_meaning,
            "is_symbolic_only": self.is_symbolic_only,
            "is_physical_claim": self.is_physical_claim,
        }


def map_frequency_tag(frequency_hz: float) -> FrequencyTagResult:
    matched = []
    meanings = []
    for tag, (lo, hi, meaning) in _FREQUENCY_TAGS.items():
        if lo <= frequency_hz < hi:
            matched.append(tag)
            meanings.append(meaning)
    return FrequencyTagResult(
        frequency_hz=frequency_hz,
        matched_tags=matched,
        symbolic_meaning=meanings,
        is_symbolic_only=True,
        is_physical_claim=False,
    )
