"""
periphery/math_core/math_memory_index.py
==========================================
Source canonique : periphery/obsidure_math_memory_readonly/MATH_MEMORY_INDEX.json
Route  : PYTHON_PATCH_PROPOSAL — HUMAN_APPROVED_WRITE 2026-06-25

Loader read-only vers MATH_MEMORY_INDEX.json.
Aucune copie — aucune dilution — référence unique.

RÈGLE : kernel_mutation=False. Ne pas modifier proofs/, sealed, V18, kernel.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

_CANONICAL_PATH = Path(__file__).parent.parent / "obsidure_math_memory_readonly" / "MATH_MEMORY_INDEX.json"


def _load_raw() -> Dict[str, Any]:
    with _CANONICAL_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def all_items() -> List[Dict[str, Any]]:
    """Retourne tous les items de MATH_MEMORY_INDEX (read-only)."""
    return _load_raw().get("items", [])


def get_by_id(item_id: str) -> Optional[Dict[str, Any]]:
    """Cherche un item par son champ 'id'."""
    return next((i for i in all_items() if i.get("id") == item_id), None)


def get_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Cherche un item par son champ 'name'."""
    return next((i for i in all_items() if i.get("name") == name), None)


def items_by_status(status: str) -> List[Dict[str, Any]]:
    """Filtre les items par status (CANONICAL_CANDIDATE, PROVISIONAL, etc.)."""
    return [i for i in all_items() if i.get("status") == status]


def items_usable_by_obsidure() -> List[Dict[str, Any]]:
    """Items marqués can_be_used_by_obsidure=true."""
    return [i for i in all_items() if i.get("can_be_used_by_obsidure") is True]


def canonical_path() -> Path:
    """Retourne le chemin canonique (pour audit — pas pour écriture)."""
    return _CANONICAL_PATH
