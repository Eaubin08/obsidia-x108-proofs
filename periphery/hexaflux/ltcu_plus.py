"""
LTCU+ — Long-Term Contextual Update (plus). Tracks context drift over time.
Advisory signal. Never authorizes actions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LTCUPlusSignal:
    signal_id: str
    context_drift: float
    temporal_coherence: float
    update_weight: float
    phase: str
    advisory_only: bool = True
    authorizes: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "context_drift": self.context_drift,
            "temporal_coherence": self.temporal_coherence,
            "update_weight": self.update_weight,
            "phase": self.phase,
            "advisory_only": self.advisory_only,
            "authorizes": self.authorizes,
        }


def compute_ltcu_plus(
    signal_id: str,
    context_drift: float,
    temporal_coherence: float,
    elapsed_steps: int = 1,
) -> LTCUPlusSignal:
    update_weight = max(0.0, min(1.0, (1.0 - context_drift) * temporal_coherence / max(elapsed_steps, 1)))

    if context_drift > 0.7:
        phase = "DRIFT_HIGH"
    elif temporal_coherence > 0.8:
        phase = "COHERENT_STABLE"
    elif update_weight > 0.5:
        phase = "UPDATING"
    else:
        phase = "DECAY"

    return LTCUPlusSignal(
        signal_id=signal_id,
        context_drift=round(context_drift, 4),
        temporal_coherence=round(temporal_coherence, 4),
        update_weight=round(update_weight, 4),
        phase=phase,
        advisory_only=True,
        authorizes=False,
    )
