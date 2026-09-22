"""
domains/gps/nuisance_registry.py — Registre des nuisances GPS/DÉFENSE/AVIATION
P3-06 — V3.2.2 COMPLETION
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List

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
    NuisanceEntry(
        nuisance_id="GPS_N07",
        label="MULTI_SOURCE_CONTRADICTION",
        risk_class="NAVIGATION_INTEGRITY",
        domain=DOMAIN,
        severity="CRITICAL",
        description="Divergence GNSS / inertiel / radio.",
    ),
    NuisanceEntry(
        nuisance_id="GPS_N08",
        label="REPLAY_ATTACK",
        risk_class="PROVENANCE_FAILURE",
        domain=DOMAIN,
        severity="CRITICAL",
        description="Telemetrie ancienne ou rejouee hors fenetre de fraicheur.",
    ),
    NuisanceEntry(
        nuisance_id="GPS_N09",
        label="CIC_ATTESTATION_FAILURE",
        risk_class="PROVENANCE_FAILURE",
        domain=DOMAIN,
        severity="CRITICAL",
        description="Identite du capteur ou contexte causal non atteste.",
    ),
    NuisanceEntry(
        nuisance_id="GPS_N10",
        label="PATH_FIDELITY_BREACH",
        risk_class="SAFETY_CRITICAL",
        domain=DOMAIN,
        severity="CRITICAL",
        description="Trajectoire incompatible avec le plan autorise ou l'enveloppe physique.",
    ),
]


def get_active_nuisances() -> List[NuisanceEntry]:
    return [n for n in NUISANCES if n.active]


def get_by_risk_class(risk_class: str) -> List[NuisanceEntry]:
    return [n for n in NUISANCES if n.risk_class == risk_class]


def get_critical() -> List[NuisanceEntry]:
    return [n for n in NUISANCES if n.severity == "CRITICAL" and n.active]


def get_by_label(label: str) -> NuisanceEntry | None:
    normalized = str(label or "").upper()
    for nuisance in NUISANCES:
        if nuisance.label == normalized and nuisance.active:
            return nuisance
    return None


def classify_gps_payload(payload: dict[str, Any]) -> List[NuisanceEntry]:
    """Classify GPS/aviation telemetry into domain nuisances.

    This function names threats only. It does not decide ALLOW/HOLD/BLOCK.
    """
    labels: list[str] = []
    spoof_score = float(payload.get("spoof_score", payload.get("trajectory_drift_score", 0.0)) or 0.0)
    drift_score = float(payload.get("trajectory_drift_score", 0.0) or 0.0)
    source_conflict = float(payload.get("source_conflict_score", 0.0) or 0.0)
    time_skew = float(payload.get("time_skew_score", 0.0) or 0.0)
    brownout = float(payload.get("brownout_score", 0.0) or 0.0)
    freshness_ms = float(payload.get("freshness_ms", 0.0) or 0.0)
    velocity_kt = float(payload.get("ground_speed", payload.get("velocity_kt", 0.0)) or 0.0)
    g_load = float(payload.get("g_load", 1.0) or 1.0)

    if spoof_score >= 0.35 or drift_score >= 0.45:
        labels.append("GPS_SPOOFING")
    if source_conflict >= 0.35:
        labels.append("MULTI_SOURCE_CONTRADICTION")
    if brownout >= 0.40:
        labels.append("JAMMING_DETECTED")
    if time_skew >= 0.30 or freshness_ms > 1000 or payload.get("replay_window_detected") is True:
        labels.append("REPLAY_ATTACK")
    if payload.get("attestation_ready") is False or payload.get("sensor_attested") is False:
        labels.append("CIC_ATTESTATION_FAILURE")
    if velocity_kt > 520 or g_load > 2.1:
        labels.append("PATH_FIDELITY_BREACH")
    if payload.get("restricted_zone") is True:
        labels.append("RESTRICTED_ZONE_APPROACH")
    if payload.get("collision_risk") is True:
        labels.append("COLLISION_RISK")

    entries: list[NuisanceEntry] = []
    seen: set[str] = set()
    for label in labels:
        if label in seen:
            continue
        seen.add(label)
        entry = get_by_label(label)
        if entry is not None:
            entries.append(entry)
    return entries
