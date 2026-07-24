"""
domains/trading/nuisance_registry.py — Registre des nuisances TRADING
P3-04 — V3.2.2 COMPLETION
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

DOMAIN: str = "trading"


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
        nuisance_id="TRADING_N01",
        label="MARKET_MANIPULATION",
        risk_class="REGULATORY_MARKET_ABUSE",
        domain=DOMAIN,
        severity="CRITICAL",
        description="Signal de manipulation de marché détecté — spoofing/layering.",
    ),
    NuisanceEntry(
        nuisance_id="TRADING_N02",
        label="INSIDER_TRADING_SIGNAL",
        risk_class="REGULATORY_INSIDER",
        domain=DOMAIN,
        severity="CRITICAL",
        description="Pattern d'opération suspect avant annonce — délit d'initié potentiel.",
    ),
    NuisanceEntry(
        nuisance_id="TRADING_N03",
        label="POSITION_LIMIT_BREACH",
        risk_class="LIMIT_VIOLATION",
        domain=DOMAIN,
        severity="HIGH",
        description="Dépassement des limites de position réglementaires.",
    ),
    NuisanceEntry(
        nuisance_id="TRADING_N04",
        label="VOLATILITY_SPIKE",
        risk_class="MARKET_RISK",
        domain=DOMAIN,
        severity="HIGH",
        description="Pic de volatilité anormal — T_mean élevé, H_score faible.",
    ),
    NuisanceEntry(
        nuisance_id="TRADING_N05",
        label="ALGO_RUNAWAY",
        risk_class="OPERATIONAL_RISK",
        domain=DOMAIN,
        severity="CRITICAL",
        description="Comportement d'algorithme hors-normes — circuit breaker requis.",
    ),
]


def get_active_nuisances() -> List[NuisanceEntry]:
    return [n for n in NUISANCES if n.active]


def get_by_risk_class(risk_class: str) -> List[NuisanceEntry]:
    return [n for n in NUISANCES if n.risk_class == risk_class]


def get_critical() -> List[NuisanceEntry]:
    return [n for n in NUISANCES if n.severity == "CRITICAL" and n.active]
