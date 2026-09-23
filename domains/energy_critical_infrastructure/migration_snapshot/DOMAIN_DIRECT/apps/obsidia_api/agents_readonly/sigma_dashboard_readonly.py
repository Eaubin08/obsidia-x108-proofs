"""
apps/obsidia_api/agents_readonly/sigma_dashboard_readonly.py

P73 — Sigma Dashboard Readonly Adapter
Adapte de agents/sigma_dashboard.py (core, pas d'equivalent sigma).

ADAPTATION P73 :
- Suppression de la generation PNG et de tout file write
- Suppression de matplotlib (no-write mode)
- Retourne un dict de donnees de stabilite (pas de PNG)
- Lecture seule de proofs/PROOFKIT_REPORT.json

Source originale : agents/sigma_dashboard.py
Categorie P73 : ADAPT_READONLY_SIGNAL
Risque supprime : generation PNG (ecrivait proofs/V18_9/sigma_dashboard.png)

BOUNDARY P73 :
DRY_RUN_ONLY = True
READONLY = True
DECISION_AUTHORITY = "KX108_ONLY"
EMITS_ACT = False
EMITS_VERDICT = False
MEMORY_WRITE = False
GRAPHITI_WRITE = False
NEO4J_WRITE = False
KERNEL_MUTATION = False
SIGMA_OVERRIDE = False
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

DRY_RUN_ONLY: bool = True
READONLY: bool = True
DECISION_AUTHORITY: str = "KX108_ONLY"
EMITS_ACT: bool = False
EMITS_VERDICT: bool = False
MEMORY_WRITE: bool = False
GRAPHITI_WRITE: bool = False
NEO4J_WRITE: bool = False
KERNEL_MUTATION: bool = False
SIGMA_OVERRIDE: bool = False

_BOUNDARY = {
    "dry_run_only": DRY_RUN_ONLY,
    "readonly": READONLY,
    "decision_authority": DECISION_AUTHORITY,
    "emits_act": EMITS_ACT,
    "emits_verdict": EMITS_VERDICT,
    "memory_write": MEMORY_WRITE,
    "graphiti_write": GRAPHITI_WRITE,
    "neo4j_write": NEO4J_WRITE,
    "kernel_mutation": KERNEL_MUTATION,
    "sigma_override": SIGMA_OVERRIDE,
}


def get_sigma_stability_data(
    report_path: str = "proofs/PROOFKIT_REPORT.json",
) -> Dict[str, Any]:
    """
    Lit proofs/PROOFKIT_REPORT.json et retourne les donnees de stabilite Sigma.
    Ne genere aucun fichier PNG. Ne modifie aucun etat.
    Retourne un dict avec les metriques de stabilite.
    """
    path = Path(report_path)

    if not path.exists():
        return {
            "status": "REPORT_NOT_FOUND",
            "report_path": str(path),
            "boundary": _BOUNDARY,
            "advisory": True,
            "error": f"Rapport introuvable : {path}. Lancez d'abord proofs/verify_all.py",
        }

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        return {
            "status": "REPORT_READ_ERROR",
            "report_path": str(path),
            "boundary": _BOUNDARY,
            "advisory": True,
            "error": str(e),
        }

    if "V18_9_sigma_stability" not in data:
        return {
            "status": "KEY_ABSENT",
            "report_path": str(path),
            "boundary": _BOUNDARY,
            "advisory": True,
            "error": "Cle V18_9_sigma_stability absente du rapport.",
            "available_keys": list(data.keys())[:20],
        }

    sigma = data["V18_9_sigma_stability"]
    metrics = sigma.get("metrics", {})
    steps_detail = sigma.get("steps_detail", [])
    constraints = sigma.get("constraints", {})

    return {
        "status": sigma.get("status", "UNKNOWN"),
        "steps_evaluated": sigma.get("steps_evaluated", 0),
        "violations_total": sigma.get("violations_total", 0),
        "mean_velocity": metrics.get("mean_velocity", 0.0),
        "tau_max_used": metrics.get("tau_max_used", 0.75),
        "accel_limit_used": metrics.get("accel_limit_used", 0.40),
        "steps_detail": steps_detail,
        "constraints": constraints,
        "boundary": _BOUNDARY,
        "advisory": True,
        "source": "proofkit_report_readonly",
        "report_path": str(path),
    }


def get_boundary() -> Dict[str, Any]:
    return dict(_BOUNDARY)


def check_stability_pass(report_path: str = "proofs/PROOFKIT_REPORT.json") -> bool:
    data = get_sigma_stability_data(report_path)
    return data.get("status") == "PASS"
