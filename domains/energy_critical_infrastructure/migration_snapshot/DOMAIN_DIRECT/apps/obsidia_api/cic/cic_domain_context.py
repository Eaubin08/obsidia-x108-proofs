"""
CIC Domain Context
SCOPE: READONLY_BINDING_PREP
DECISION_AUTHORITY: KX108_ONLY

Fournit un packet cic_domain_context readonly pour chaque domaine.
Chaque domaine lit UNIQUEMENT son propre sous-contexte CIC.
Aucun domaine ne bypass X108. CIC enrichit le contexte seulement.
"""
from __future__ import annotations

from typing import Any

from apps.obsidia_api.cic.cic_readonly_pack_provider import (
    _CENTRAL_RULES,
    _DOMAIN_RELEVANCE,
    build_cic_readonly_context,
)

_SUPPORTED_DOMAINS = frozenset({"bank", "trading", "gps_defense_aviation"})

_MISSING_DATA_POLICY = (
    "Critical missing data on irreversible action triggers HOLD / BLOCK / REVIEW — "
    "never ACT. Missing data review is REVIEW/HOLD/BLOCK by X108 only, not by CIC."
)

_INVARIANTS_PRIORITY = "Invariant > Reversibilite > Score > Projection"

_PROJECTION_POLICY = "Projection is not prediction."

_MEMORY_POLICY = "Memory is not sovereign."

_AUTHORITY = "KX108_ONLY"


def build_domain_cic_context(domain: str) -> dict[str, Any]:
    """
    Retourne le cic_domain_context readonly pour le domaine demandé.
    Si le domaine n'existe pas dans le registre CIC, retourne DOMAIN_NOT_FOUND.
    Si le domaine est 'ecom', retourne ECOM_NOT_FOUND (pas d'échec).
    """
    if domain == "ecom":
        return {
            "domain": "ecom",
            "status": "ECOM_NOT_FOUND",
            "readonly": True,
            "decision_authority": _AUTHORITY,
            "emits_act": False,
            "kernel_mutation": False,
        }

    if domain not in _SUPPORTED_DOMAINS:
        return {
            "domain": domain,
            "status": "DOMAIN_NOT_FOUND",
            "readonly": True,
            "decision_authority": _AUTHORITY,
            "emits_act": False,
            "kernel_mutation": False,
        }

    domain_rel = _DOMAIN_RELEVANCE.get(domain, {})

    return {
        "domain": domain,
        "relevant_metric_families": domain_rel.get("confirmed", []),
        "partial_metric_families": domain_rel.get("partial", []),
        "missing_data_policy": _MISSING_DATA_POLICY,
        "invariants_priority": _INVARIANTS_PRIORITY,
        "projection_policy": _PROJECTION_POLICY,
        "memory_policy": _MEMORY_POLICY,
        "decision_authority": _AUTHORITY,
        "central_rules": _CENTRAL_RULES,
        "missing_metrics": domain_rel.get("missing", []),
        "readonly": True,
        "emits_act": False,
        "kernel_mutation": False,
        "x108_binding": False,
        "ncp_active": False,
        "scraping_active": False,
        "authority": "NONE",
    }


def build_all_domain_contexts() -> dict[str, Any]:
    """
    Retourne un dict {domain: cic_domain_context} pour tous les domaines connus.
    ECOM absent = ECOM_NOT_FOUND, pas d'échec.
    """
    result: dict[str, Any] = {}
    for domain in sorted(_SUPPORTED_DOMAINS):
        result[domain] = build_domain_cic_context(domain)
    result["ecom"] = build_domain_cic_context("ecom")
    return result
