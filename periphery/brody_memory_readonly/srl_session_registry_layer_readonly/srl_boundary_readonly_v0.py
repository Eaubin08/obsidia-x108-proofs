"""
srl_boundary_readonly_v0.py — SRL boundary readonly V0.

Définit le boundary canonique de la couche SRL.
Tous les flags write sont False. Aucun ACT. Aucune décision.
"""
from __future__ import annotations

from typing import Any, Dict

DRY_RUN_ONLY: bool = True

SRL_BOUNDARY: Dict[str, Any] = {
    "readonly": True,
    "dry_run_only": True,
    "emits_act": False,
    "emits_verdict": False,
    "emits_allow_hold_block": False,
    "emits_boundary_alert": True,
    "emits_reflex_alert": True,
    "memory_write": False,
    "memory_decision": False,
    "allowed_to_decide": False,
    "graphiti_write": False,
    "graphiti_index_write": False,
    "neo4j_write": False,
    "kernel_mutation": False,
    "x108_merge": False,
    "x108_mutation": False,
    "x108_runtime_binding": False,
    "decision_authority": "KX108_ONLY",
    "srl_role": "SESSION_REGISTRY_LAYER_READONLY",
    "produces": ["fiches", "index", "traces", "context_reload_packs"],
}

FORBIDDEN_SRL_FLAGS: frozenset = frozenset({
    "emits_allow_hold_block",
    "emits_verdict",
    "memory_write",
    "graphiti_write",
    "graphiti_index_write",
    "neo4j_write",
    "kernel_mutation",
    "x108_merge",
    "emits_act",
    "memory_intake",
})


def validate_boundary(module_boundary: Dict[str, Any]) -> Dict[str, Any]:
    """Valide qu'un boundary module respecte le SRL readonly.

    Retourne {"ok": True} ou {"ok": False, "violations": [...]}.
    Ne write pas. Ne décide pas.
    """
    violations = []
    for flag in FORBIDDEN_SRL_FLAGS:
        if module_boundary.get(flag) is True:
            violations.append(f"{flag}=True_FORBIDDEN_IN_SRL_READONLY")
    if module_boundary.get("decision_authority") not in (None, "", "KX108_ONLY"):
        violations.append("decision_authority_override_FORBIDDEN")
    if violations:
        return {"ok": False, "violations": sorted(violations)}
    return {"ok": True, "violations": []}
