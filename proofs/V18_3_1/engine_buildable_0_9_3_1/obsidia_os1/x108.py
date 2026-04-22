from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class X108Check:
    decision: str  # ACT | HOLD
    wait_s: float
    reason: str


class X108Gate:
    """Gate X108 minimal, compatible with your x108.py logic.

    Règle : si l'action est irréversible, on exige un temps minimum d'attente.
    La fonction renvoie HOLD/ACT + raison.
    """

    def __init__(self, min_wait_s: float = 108.0):
        self.min_wait_s = float(min_wait_s)

    def check(self, elapsed_s: float, irreversible: bool, note: str = "") -> X108Check:
        elapsed_s = float(elapsed_s)
        if not irreversible:
            return X108Check("ACT", 0.0, f"Reversible action; X108 bypass. {note}".strip())
        if elapsed_s >= self.min_wait_s:
            return X108Check("ACT", 0.0, f"X108 satisfied (elapsed={elapsed_s:.2f}s >= {self.min_wait_s:.2f}s). {note}".strip())
        wait = self.min_wait_s - elapsed_s
        return X108Check(
            "HOLD",
            wait,
            f"X108 HOLD: need +{wait:.2f}s (elapsed={elapsed_s:.2f}s, min={self.min_wait_s:.2f}s). {note}".strip(),
        )
