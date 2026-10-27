#!/usr/bin/env python3
"""OBSIDIA V4 Gate Engine.

Moteur froid :
- DONE exige evidence.
- Gate OPEN exige toutes tâches requises DONE.
- G5 exige G1/G2/G3/G4 OPEN.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def can_promote(gates: Dict[str, Dict[str, Any]]) -> bool:
    return all(gates.get(g, {}).get("status") == "OPEN" for g in ["G1","G2","G3","G4","G5"] )

def blocking_tasks(gates: Dict[str, Dict[str, Any]]) -> Dict[str, list]:
    return {g: data.get("blocking_task_ids", []) for g, data in gates.items()}

def verdict(gates: Dict[str, Dict[str, Any]]) -> str:
    return "PROMOTION_V4_AUTHORIZED" if can_promote(gates) else "PROMOTION_V4_BLOCKED"


_BOUNDARY = {
    "readonly": True,
    "emits_act": False,
    "memory_write": False,
    "decision_authority": "KX108_ONLY",
}

