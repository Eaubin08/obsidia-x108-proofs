"""
Sigma Monitoring endpoints — F63 readonly.

GET /api/periphery/monitoring/sigma/domains
GET /api/periphery/monitoring/sigma/evaluate
GET /api/periphery/monitoring/sigma/bank
GET /api/periphery/monitoring/sigma/trading
GET /api/periphery/monitoring/sigma/ecom
GET /api/periphery/monitoring/sigma/gps-defense-aviation

All routes:
  - GET only — no POST, no action endpoint, no decision endpoint
  - Return F62-normalized domain packets from sigma.evaluate / sigma.packets
  - All sovereignty flags enforced via safe_backend_response() + explicit boundary
  - Never decides. Never writes. Never mutates. Never emits ACT or verdict.
  - decision_authority = KX108_ONLY at all times.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from apps.obsidia_api.safe_response import safe_backend_response
from sigma.evaluate import evaluate_sigma_domain, evaluate_sigma_registry
from sigma.registry import list_sigma_domains

router = APIRouter(
    prefix="/api/periphery/monitoring/sigma",
    tags=["sigma-monitoring"],
)

# Explicit boundary — graphiti_write not in safe_backend_response._SOVEREIGNTY_PROTECTED
_SIGMA_BOUNDARY: dict[str, Any] = {
    "decision_authority": "KX108_ONLY",
    "readonly": True,
    "advisory_only": True,
    "allowed_to_decide": False,
    "emits_act": False,
    "emits_verdict": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "neo4j_write": False,
    "graphiti_write": False,
    "memory_write": False,
    "brody_decision": False,
}

_SOURCE = "SIGMA_MONITORING_F63"


def _wrap(data: dict[str, Any], route: str) -> dict[str, Any]:
    """Merge data + explicit boundary, then apply safe_backend_response."""
    merged = {**data, **_SIGMA_BOUNDARY, "route": route, "monitoring_readonly": True}
    return safe_backend_response(merged, source=_SOURCE)


@router.get("/domains")
async def sigma_domains():
    """List all canonical Sigma domains."""
    domains = list_sigma_domains()
    return _wrap(
        {
            "mode": "SIGMA_DOMAINS_LIST",
            "domains": domains,
            "domain_count": len(domains),
        },
        route="/api/periphery/monitoring/sigma/domains",
    )


@router.get("/evaluate")
async def sigma_evaluate():
    """Readonly multi-domain Sigma registry evaluation (F62 normalized packets)."""
    result = evaluate_sigma_registry(None)
    return _wrap(
        {
            "mode": "SIGMA_REGISTRY_EVALUATION",
            **result,
        },
        route="/api/periphery/monitoring/sigma/evaluate",
    )


@router.get("/bank")
async def sigma_bank():
    """Readonly Sigma evaluation for the bank domain."""
    result = evaluate_sigma_domain("bank", None)
    return _wrap(
        {"mode": "SIGMA_DOMAIN_EVALUATION", **result},
        route="/api/periphery/monitoring/sigma/bank",
    )


@router.get("/trading")
async def sigma_trading():
    """Readonly Sigma evaluation for the trading domain."""
    result = evaluate_sigma_domain("trading", None)
    return _wrap(
        {"mode": "SIGMA_DOMAIN_EVALUATION", **result},
        route="/api/periphery/monitoring/sigma/trading",
    )


@router.get("/ecom")
async def sigma_ecom():
    """Readonly Sigma evaluation for the ecom domain."""
    result = evaluate_sigma_domain("ecom", None)
    return _wrap(
        {"mode": "SIGMA_DOMAIN_EVALUATION", **result},
        route="/api/periphery/monitoring/sigma/ecom",
    )


@router.get("/gps-defense-aviation")
async def sigma_gps_defense_aviation():
    """Readonly Sigma evaluation for the gps_defense_aviation domain."""
    result = evaluate_sigma_domain("gps_defense_aviation", None)
    return _wrap(
        {"mode": "SIGMA_DOMAIN_EVALUATION", **result},
        route="/api/periphery/monitoring/sigma/gps-defense-aviation",
    )
