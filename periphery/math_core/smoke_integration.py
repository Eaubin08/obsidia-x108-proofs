"""
periphery — periphery/math_core/smoke_integration.py
Route     : PYTHON_PATCH_PROPOSAL (tentative 1)
Objectif  : Cree periphery/math_core/smoke_integration.py module
  Python qui importe all_items depuis math_memory_index et verifie
Statut    : SANDBOX — AWAITING_HUMAN_REVIEW
RÈGLE     : kernel_mutation=False. Ne pas modifier proofs/, sealed, V18, kernel.
NOTE      : P107 (L(Phi(s))<=L(s)) est A_PROUVER — ne pas présenter comme prouvé.
"""
from __future__ import annotations
from typing import Any, Dict, List

from periphery.math_core.math_memory_index import all_items, get_by_id, items_usable_by_obsidure
from periphery.math_core.phi_graph import PhiGraph, PhiEdge
from periphery.math_core.omega_space import OmegaState, OMEGA_0, project_state_to_omega


def check_math_memory_index() -> dict:
    """Vérifie que MATH_MEMORY_INDEX contient 134 items."""
    items = all_items()
    count = len(items)
    ok = count == 134
    return {"check": "math_memory_index", "count": count, "expected": 134, "ok": ok}


def check_phi_graph() -> dict:
    """Vérifie que PhiGraph.sigma() ∈ (0, 1]."""
    g = PhiGraph(nodes=["A", "B"], edges=[PhiEdge("A", "B", "support", 0.8)])
    s = g.sigma()
    ok = 0.0 < s <= 1.0
    return {"check": "phi_graph_sigma", "sigma": s, "ok": ok}


def check_omega_stable() -> dict:
    """Vérifie que OmegaState stable classifie en ALLOW."""
    result = OMEGA_0.classify()
    ok = result == "ALLOW"
    return {"check": "omega_classify_stable", "result": result, "ok": ok}


def run_all() -> dict:
    """Lance tous les checks smoke — retourne un bilan PASS/FAIL."""
    results = []
    results.append(check_math_memory_index())
    results.append(check_phi_graph())
    results.append(check_omega_stable())
    passed = sum(1 for r in results if r.get("ok"))
    return {
        "module": "smoke_integration",
        "route": "PYTHON_PATCH_PROPOSAL",
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "status": "PASS" if passed == len(results) else "FAIL",
        "results": results,
    }


if __name__ == "__main__":
    import json as _json
    print(_json.dumps(run_all(), indent=2, ensure_ascii=False))
