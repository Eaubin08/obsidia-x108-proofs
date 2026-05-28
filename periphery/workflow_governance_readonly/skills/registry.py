from __future__ import annotations

from typing import Any, Dict

from ..constants import DECISION_AUTHORITY, READONLY_FLAGS, SKILL_IDS, SKILL_ROLE_MATRIX


def _skill(skill_id: str, spec: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "skill_id": skill_id,
        "role": spec["role"],
        "input": spec["input"],
        "output": spec["output"],
        "runtime_effect": bool(spec.get("runtime_effect", False)),
        "authority": DECISION_AUTHORITY,
        "readonly": True,
        "advisory_only": True,
        "context_signal_only": True,
        "allowed_to_decide": False,
        "can_call_x108_runtime": False,
        "can_patch_kernel": False,
        "can_execute_workflow": False,
        "boundary": {"decision_authority": DECISION_AUTHORITY, **READONLY_FLAGS},
    }


SKILL_REGISTRY: Dict[str, Dict[str, Any]] = {
    skill_id: _skill(skill_id, SKILL_ROLE_MATRIX[skill_id]) for skill_id in SKILL_IDS
}


def get_skill_registry() -> Dict[str, Dict[str, Any]]:
    """Return a copy of the V4 skill registry with full boundary metadata."""
    return {k: dict(v) for k, v in SKILL_REGISTRY.items()}


def get_skill(skill_id: str) -> Dict[str, Any]:
    if skill_id not in SKILL_REGISTRY:
        raise KeyError(f"Unknown skill_id: {skill_id}")
    return dict(SKILL_REGISTRY[skill_id])
