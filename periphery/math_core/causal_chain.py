"""
periphery/math_core/causal_chain.py
======================================
Source : MATH_MEMORY_INDEX[Chaine_Causale_Complete] — CANONICAL_CANDIDATE
Route  : PYTHON_PATCH_PROPOSAL — HUMAN_APPROVED_WRITE 2026-06-25

Chaîne causale complète :
  contexte → perception → invariant check → ticket → décision → action → bilan
  Propriété A1 : toute décision tracée a un ticket.
  Propriété A2 : tout ticket pointe vers un état contexte non nul.
  Propriété A3 : aucune décision ne court-circuite la vérification invariant.

RÈGLE : kernel_mutation=False. Ne pas modifier proofs/, sealed, V18, kernel.
NOTE  : P107 est A_PROUVER — ne pas présenter comme prouvé.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class CausalStep:
    name: str
    data: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class CausalChain:
    """
    Représentation d'une chaîne causale complète d'Obsidia.
    Source : MATH_MEMORY_INDEX[Chaine_Causale_Complete]
    """
    steps: List[CausalStep] = field(default_factory=list)

    _EXPECTED_ORDER = (
        "contexte",
        "perception",
        "invariant_check",
        "ticket",
        "decision",
        "action",
        "bilan",
    )

    def append(self, name: str, data: Dict[str, Any]) -> None:
        self.steps.append(CausalStep(name=name, data=data))

    def validate_order(self) -> List[str]:
        """Retourne la liste des violations d'ordre."""
        present = [s.name for s in self.steps]
        errors: List[str] = []
        prev_idx = -1
        for step_name in present:
            if step_name in self._EXPECTED_ORDER:
                idx = self._EXPECTED_ORDER.index(step_name)
                if idx <= prev_idx:
                    errors.append(f"Ordre invalide : {step_name} après index {prev_idx}")
                prev_idx = idx
        return errors

    def check_a1(self) -> bool:
        """A1 : toute décision tracée a un ticket."""
        names = [s.name for s in self.steps]
        if "decision" not in names:
            return True
        return "ticket" in names

    def check_a2(self) -> bool:
        """A2 : tout ticket pointe vers un état contexte non nul."""
        ticket_step = next((s for s in self.steps if s.name == "ticket"), None)
        if ticket_step is None:
            return True
        contexte_step = next((s for s in self.steps if s.name == "contexte"), None)
        if contexte_step is None:
            return False
        return bool(contexte_step.data)

    def check_a3(self) -> bool:
        """A3 : aucune décision ne court-circuite la vérification invariant."""
        names = [s.name for s in self.steps]
        if "decision" not in names:
            return True
        return "invariant_check" in names

    def audit(self) -> Dict[str, Any]:
        return {
            "steps": [s.name for s in self.steps],
            "order_errors": self.validate_order(),
            "A1_ok": self.check_a1(),
            "A2_ok": self.check_a2(),
            "A3_ok": self.check_a3(),
        }
