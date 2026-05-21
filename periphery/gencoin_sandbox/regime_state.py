from __future__ import annotations

from .sandbox_engine import State, System, transition, step

__all__ = ["State", "System", "transition", "step"]


def classify_regime(system: System) -> str:
    return system.state.value


def is_false_on(system: System) -> bool:
    return system.state == State.FALSE_ON


def is_assisted_on(system: System) -> bool:
    return system.state == State.ASSISTED_ON


def is_admissible(system: System) -> bool:
    return system.state == State.ON and system.truth_score >= 0.8
