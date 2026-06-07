"""
srl_taxonomy_readonly_v0.py — SRL Session Registry Layer V0 taxonomy.

Taxonomie readonly des zones de session. Ne décide pas. Ne write pas.
Sert uniquement à la canonisation des états SRL.
"""
from __future__ import annotations

from typing import Dict, Tuple

DRY_RUN_ONLY: bool = True

# Taxonomie SRL V0
SRL_ZONES: Dict[str, str] = {
    "ACTIVE": "Session en cours — interaction opérateur active.",
    "SEMI_ACTIVE": "Session récente — activité partielle, candidat reload.",
    "COLD": "Session ancienne — archive, reload possible sur demande.",
    "GHOST": "Session inactive / rejetée — ne pas charger par défaut.",
    "REFLEX_ALERT": "Session déclenchant une alerte reflex non-décisionnelle.",
    "BOUNDARY_ALERT": "Session déclenchant une alerte boundary non-décisionnelle.",
}

# Mapping zones canoniques depuis taxonomies antérieures
ZONE_MAPPING: Dict[str, str] = {
    "CRISTAL": "ACTIVE",
    "TRANSITION": "SEMI_ACTIVE",
    "NEANT": "GHOST",
    "NEANT_REJECTED": "GHOST",
    "REFLEX": "REFLEX_ALERT",
    "MANDATORY_HOLD": "BOUNDARY_ALERT",
    "MANDATORY_HOLD_IMMEDIATE_BLOCK": "BOUNDARY_ALERT",
    "BOUNDARY_ALERT_NON_DECISIONAL": "BOUNDARY_ALERT",
}

# Mapping P1 : renommage décisionnel interdit
FORBIDDEN_LABELS_MAPPING: Dict[str, str] = {
    "NEANT_REJECTED": "GHOST_SIDE_TABLE",
    "DO_NOT_KEEP": "DO_NOT_LOAD_BY_DEFAULT",
}

CANDIDATE_ZONES: frozenset = frozenset({"ACTIVE"})
NON_CANDIDATE_ZONES: frozenset = frozenset({"SEMI_ACTIVE", "COLD", "GHOST", "REFLEX_ALERT", "BOUNDARY_ALERT"})
ALERT_ZONES: frozenset = frozenset({"REFLEX_ALERT", "BOUNDARY_ALERT"})


def canonical_zone(raw_zone: str) -> str:
    if raw_zone in SRL_ZONES:
        return raw_zone
    return ZONE_MAPPING.get(raw_zone, "GHOST")


def is_candidate(zone: str) -> bool:
    return canonical_zone(zone) in CANDIDATE_ZONES


def is_alert(zone: str) -> bool:
    return canonical_zone(zone) in ALERT_ZONES
