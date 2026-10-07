"""B6 tiered capability disclosure: a view over the existing Brody capability matrix.

The truth source stays apps/obsidia_api/brody_rights_authority_matrix.get_brody_capability_matrix;
nothing here creates capabilities. DISCLOSURE != PERMISSION != AUTHORITY (KX108_ONLY).
"""
from __future__ import annotations

import copy
from enum import Enum
from typing import Any, Iterable, Mapping


class DisclosureLevel(str, Enum):
    SUMMARY = "SUMMARY"
    CATEGORY = "CATEGORY"
    EXACT = "EXACT"


def load_capability_matrix() -> Mapping[str, Any]:
    from apps.obsidia_api.brody_rights_authority_matrix import get_brody_capability_matrix
    return get_brody_capability_matrix()


def disclose(matrix: Mapping[str, Any], level: DisclosureLevel,
             categories: Iterable[str] | None = None) -> dict[str, Any]:
    level = DisclosureLevel(level)
    table = dict(matrix.get("matrix") or {})
    out: dict[str, Any] = {"level": level.value, "category_count": len(table),
                           "disclosure_is_permission": False, "execution_authority": "KX108_ONLY",
                           "source_ref": "apps.obsidia_api.brody_rights_authority_matrix"}
    if level == DisclosureLevel.SUMMARY:
        return out
    out["categories"] = sorted(table)
    if level == DisclosureLevel.EXACT:
        wanted = sorted(set(categories) & set(table)) if categories is not None else sorted(table)
        out["capabilities"] = {c: copy.deepcopy(table[c]) for c in wanted}
    return out
