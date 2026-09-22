"""
domains/gps/nuisance_registry.py — Registre des nuisances GPS/DÉFENSE/AVIATION
P3-06 — V3.2.2 COMPLETION
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

DOMAIN: str = "gps_defense_aviation"


@dataclass
class NuisanceEntry:
    nuisance_id: str
    label: str
    risk_class: str
    domain: str
    severity: str = "MEDIUM"
    description: str = ""
    active: bool = True


NUISANCES: List[NuisanceEntry] = [
    NuisanceEntry(
        nuisance_id="GPS_N01",
        label="GPS_SPOOFING",
        risk_class="NAVIGATION_INTEGRITY",
        domain=DOMAIN,
        severity="CRITICAL",
        description="Signal GPS potentiellement falsifié — intégrité de navigation compromise.",
    ),
    NuisanceEntry(
        nuisance_id="GPS_N02",
        label="AIRSPACE_INTRUSION",
        risk_class="AIRSPACE_VIOLATION",
        domain=DOMAIN,
        severity="CRITICAL",
        description="Intrusion détectée dans espace aérien contrôlé ou restreint.",
    ),
    NuisanceEntry(
        nuisance_id="GPS_N03",
        label="COLLISION_RISK",
        risk_class="SAFETY_CRITICAL",
        domain=DOMAIN,
        severity="CRITICAL",
        description="Risque de collision calculé — TCAS ou équivalent requis.",
    ),
    NuisanceEntry(
        nuisance_id="GPS_N04",
        label="JAMMING_DETECTED",
        risk_class="ELECTRONIC_WARFARE",
        domain=DOMAIN,
        severity="CRITICAL",
        description="Brouillage électronique GPS détecté.",
    ),
    NuisanceEntry(
        nuisance_id="GPS_N05",
        label="FLIGHT_PLAN_DEVIATION",
        risk_class="OPERATIONAL_DEVIATION",
        domain=DOMAIN,
        severity="HIGH",
        description="Écart significatif entre plan de vol déclaré et trajectoire réelle.",
    ),
    NuisanceEntry(
        nuisance_id="GPS_N06",
        label="RESTRICTED_ZONE_APPROACH",
        risk_class="REGULATORY_RESTRICTION",
        domain=DOMAIN,
        severity="HIGH",
        description="Approche d'une zone réglementaire sensible (no-fly zone, défense).",
    ),
]


def get_active_nuisances() -> List[NuisanceEntry]:
    return [n for n in NUISANCES if n.active]


def get_by_risk_class(risk_class: str) -> List[NuisanceEntry]:
    return [n for n in NUISANCES if n.risk_class == risk_class]


def get_critical() -> List[NuisanceEntry]:
    return [n for n in NUISANCES if n.severity == "CRITICAL" and n.active]
