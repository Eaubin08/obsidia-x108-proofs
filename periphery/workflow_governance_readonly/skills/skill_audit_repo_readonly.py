from __future__ import annotations

from typing import Any, Dict, Iterable

from ..constants import DECISION_AUTHORITY, READONLY_FLAGS

SKILL_SPEC = {
    "skill_id": "SKILL_AUDIT_REPO_READONLY",
    "contract": "scan inventory/material for boundary markers; no modification",
}

REQUIRED_MARKERS = [
    "DECISION_AUTHORITY=KX108_ONLY",
    "allowed_to_decide=false",
    "kernel_mutation=false",
    "x108_mutation=false",
]


def audit_repo_inventory_readonly(lines: Iterable[str]) -> Dict[str, Any]:
    """Readonly inventory audit for handoff files or terminal outputs."""
    material = [str(line) for line in lines]
    joined = "\n".join(material)
    found = {marker: marker in joined for marker in REQUIRED_MARKERS}
    return {
        "audit_kind": "REPO_INVENTORY_BOUNDARY_READONLY",
        "authority": DECISION_AUTHORITY,
        "readonly": True,
        "candidate_only": True,
        "line_count": len(material),
        "required_markers": found,
        "missing_markers": [k for k, ok in found.items() if not ok],
        "boundary": {"decision_authority": DECISION_AUTHORITY, **READONLY_FLAGS},
    }
