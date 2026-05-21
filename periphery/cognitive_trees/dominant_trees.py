"""
Dominant Trees — DominantTrees(e) = {i | a_i >= theta}.
theta_default = 0.15. Dominant tree != authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .tree_registry import get_tree_by_id
from .tree_activation_vector import TreeActivationVector, DEFAULT_THETA


@dataclass
class DominantTreeResult:
    vector_id: str
    theta: float
    dominant_ids: list[int]
    dominant_names: list[str]
    dominant_count: int
    context_signal_only: bool = True
    dominant_is_authority: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "vector_id": self.vector_id,
            "theta": self.theta,
            "dominant_ids": self.dominant_ids,
            "dominant_names": self.dominant_names,
            "dominant_count": self.dominant_count,
            "context_signal_only": self.context_signal_only,
            "dominant_is_authority": self.dominant_is_authority,
        }


def find_dominant_trees(
    vector: TreeActivationVector,
    theta: float = DEFAULT_THETA,
) -> DominantTreeResult:
    dominant_ids = [i for i, a in enumerate(vector.activations) if a >= theta]
    dominant_names = []
    for i in dominant_ids:
        tree = get_tree_by_id(i)
        dominant_names.append(tree.name if tree else f"TREE_{i}")

    return DominantTreeResult(
        vector_id=vector.vector_id,
        theta=theta,
        dominant_ids=dominant_ids,
        dominant_names=dominant_names,
        dominant_count=len(dominant_ids),
        context_signal_only=True,
        dominant_is_authority=False,
    )
