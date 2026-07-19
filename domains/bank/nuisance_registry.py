"""
domains/bank/nuisance_registry.py — Registre des nuisances BANK
P3-02 — V3.2.2 COMPLETION

Ce registre informe le Gate et le sigma agent — il ne décide pas.
Toute décision appartient au Kernel X-108.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

DOMAIN: str = "bank"


@dataclass
class NuisanceEntry:
    nuisance_id: str
    label: str
    risk_class: str
    domain: str
    severity: str = "MEDIUM"   # LOW | MEDIUM | HIGH | CRITICAL
    description: str = ""
    active: bool = True


NUISANCES: List[NuisanceEntry] = [
    NuisanceEntry(
        nuisance_id="BANK_N01",
        label="FRAUD_TRANSACTION",
        risk_class="FINANCIAL_FRAUD",
        domain=DOMAIN,
        severity="CRITICAL",
        description="Transaction suspecte déclenchant un signal de fraude. Seuil S élevé.",
    ),
    NuisanceEntry(
        nuisance_id="BANK_N02",
        label="AML_FLAG",
        risk_class="ANTI_MONEY_LAUNDERING",
        domain=DOMAIN,
        severity="CRITICAL",
        description="Signal LCB-FT détecté — audit obligatoire avant traitement.",
    ),
    NuisanceEntry(
        nuisance_id="BANK_N03",
        label="LIMIT_BREACH",
        risk_class="LIMIT_VIOLATION",
        domain=DOMAIN,
        severity="HIGH",
        description="Dépassement de plafond réglementaire détecté.",
    ),
    NuisanceEntry(
        nuisance_id="BANK_N04",
        label="SANCTION_MATCH",
        risk_class="REGULATORY_SANCTION",
        domain=DOMAIN,
        severity="CRITICAL",
        description="Correspondance avec liste de sanctions internationales.",
    ),
    NuisanceEntry(
        nuisance_id="BANK_N05",
        label="LOW_AUDIT_SCORE",
        risk_class="AUDIT_QUALITY",
        domain=DOMAIN,
        severity="MEDIUM",
        description="Score d'audit insuffisant — A_score < 0.5.",
    ),
    NuisanceEntry(
        nuisance_id="BANK_N06",
        label="CONFIDENCE_GAP",
        risk_class="DATA_QUALITY",
        domain=DOMAIN,
        severity="MEDIUM",
        description="Indice de confiance H_score faible — données incomplètes.",
    ),
]


def get_active_nuisances() -> List[NuisanceEntry]:
    return [n for n in NUISANCES if n.active]


def get_by_risk_class(risk_class: str) -> List[NuisanceEntry]:
    return [n for n in NUISANCES if n.risk_class == risk_class]


def get_critical() -> List[NuisanceEntry]:
    return [n for n in NUISANCES if n.severity == "CRITICAL" and n.active]
