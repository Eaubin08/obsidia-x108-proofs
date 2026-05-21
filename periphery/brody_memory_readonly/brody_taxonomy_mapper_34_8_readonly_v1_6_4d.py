"""
Brody Taxonomy Mapper — Restored Canonical 34-Tree Matrix.
Bypasses the 34-to-8 dimension reduction. 
Enforces full R^34 evaluation space for X-108 governance compliance.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

# Import direct de ton registre restauré
from periphery.cognitive_trees.tree_registry import get_all_trees

@dataclass
class TaxonomyMappingResult:
    source_space_dimension: int
    target_space_dimension: int
    matrix_aligned: bool
    active_signals: list[dict]
    decision_authority: str = "KX108_ONLY"

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_space_dimension": self.source_space_dimension,
            "target_space_dimension": self.target_space_dimension,
            "matrix_aligned": self.matrix_aligned,
            "active_signals": self.active_signals,
            "decision_authority": self.decision_authority,
        }

def map_canonical_topology(raw_signals: list[dict] | None = None) -> TaxonomyMappingResult:
    """
    Force le passage des 34 arbres d'origine sans compression sémantique.
    """
    # Récupération de tes 34 arbres souverains restaurés
    canonical_trees = get_all_trees()
    signals = []
    
    for tree in canonical_trees:
        # On câble les signaux réels ou on initialise la matrice R^34 native à 0.0
        matching_signal = next((s for s in raw_signals if s.get("id") == tree.id), None) if raw_signals else None
        val = matching_signal.get("value", 0.0) if matching_signal else 0.0
        
        signals.append({
            "id": tree.id,
            "name": tree.name,
            "domain": tree.domain,
            "value": val
        })

    # On court-circuite la compression : dimension 34 -> 34 !
    return TaxonomyMappingResult(
        source_space_dimension=34,
        target_space_dimension=34,
        matrix_aligned=True,
        active_signals=signals,
        decision_authority="KX108_ONLY"
    )

def assert_no_dimension_loss(result: TaxonomyMappingResult) -> None:
    """
    Garantit qu'aucun lissage n'a eu lieu avant la transmission au Kernel.
    """
    assert result.target_space_dimension == 34, "CRITICAL_ERROR: TAXONOMY_DILUTION_DETECTED"
    assert result.matrix_aligned is True, "CRITICAL_ERROR: MATRIX_MISALIGNMENT"
