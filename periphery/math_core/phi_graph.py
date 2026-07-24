"""
periphery/math_core/phi_graph.py
=================================
Source : MATH_MEMORY_INDEX[Phi_t_Structure_Formelle] — CANONICAL_CANDIDATE
Route  : PYTHON_PATCH_PROPOSAL — HUMAN_APPROVED_WRITE 2026-06-25

Φ(t) = (V, E, τ, w) — structure formelle du graphe de sens.
T_Φ = Σ max(0, -w(e))   — tension structurelle (Lemme Φ1 : T_Φ ≥ 0)
Σ   = 1 / (1 + T_Φ)     — cohérence dérivée  (Lemme Φ2 : Σ ∈ (0,1])

RÈGLE : kernel_mutation=False. Ne pas modifier proofs/, sealed, V18, kernel.
NOTE  : P107 (L(Phi(s))<=L(s)) est A_PROUVER — ne pas présenter comme prouvé.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PhiEdge:
    """Arête du graphe sémantique Φ."""
    source: str
    target: str
    rel_type: str       # ex: "support", "contradiction", "implication"
    weight: float       # négatif = contradiction (Lemme Φ3)


@dataclass
class PhiGraph:
    """
    Φ(t) = (V, E, τ, w) — graphe de sens d'Obsidia.
    Source : MATH_MEMORY_INDEX[Phi_t_Structure_Formelle]
    """
    nodes: List[str] = field(default_factory=list)
    edges: List[PhiEdge] = field(default_factory=list)

    def tension(self) -> float:
        """T_Φ = Σ max(0, -w(e)) — Lemme Φ1 : T_Φ ≥ 0."""
        return sum(max(0.0, -e.weight) for e in self.edges)

    def sigma(self) -> float:
        """Σ = 1/(1+T_Φ) — Lemme Φ2 : Σ ∈ (0, 1]."""
        return 1.0 / (1.0 + self.tension())

    def add_contradiction(self, src: str, tgt: str, weight: float) -> None:
        """Lemme Φ3 : ajout arête négative ⇒ T_Φ↑ ⇒ Σ↓."""
        if weight >= 0:
            raise ValueError("Une contradiction doit avoir un poids négatif.")
        self.edges.append(PhiEdge(src, tgt, "contradiction", weight))

    def remove_contradiction(self, src: str, tgt: str) -> None:
        """Lemme Φ4 : suppression contradiction ⇒ T_Φ↓ ⇒ Σ↑."""
        self.edges = [
            e for e in self.edges
            if not (e.source == src and e.target == tgt and e.weight < 0)
        ]

    def summary(self) -> dict:
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "tension": self.tension(),
            "sigma": self.sigma(),
        }
