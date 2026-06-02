"""
apps/obsidia_api/bus/sigma_bridge.py — F65 Sigma Bus Bridge (readonly)

Bridges Sigma layer state into the Bus layer.
Pure in-process calls — no HTTP, no writes, no decisions, no ACT.
KX108_ONLY decision authority preserved.
"""
from __future__ import annotations

from typing import Any

from sigma.registry import list_sigma_domains, validate_sigma_registry
from sigma.evaluate import validate_sigma_dispatcher
from sigma.connectors import validate_sigma_connectors, get_sigma_connector_map

BRIDGE_VERSION = "F65"

_BRIDGE_BOUNDARY: dict[str, Any] = {
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


def build_sigma_bus_state() -> dict[str, Any]:
    """Return a readonly Sigma state snapshot for the Bus bridge layer.

    Pure in-process calls — no HTTP, no writes, no decisions.
    """
    domains = list_sigma_domains()
    connector_map = get_sigma_connector_map()
    return {
        "bridge_version": BRIDGE_VERSION,
        "sigma_available": True,
        "canonical_domains": domains,
        "domain_count": len(domains),
        "monitoring_routes_count": connector_map.get("route_count", 0),
        "connector_version": connector_map.get("connector_version"),
        "connector_type": connector_map.get("connector_type"),
        **_BRIDGE_BOUNDARY,
    }


def validate_sigma_bus_bridge() -> dict[str, Any]:
    """Validate the Sigma bus bridge structure (registry + dispatcher + connectors).

    Returns status=PASS/FAIL with aggregated error list.
    Pure structural validation — no HTTP calls.
    """
    errors: list[str] = []

    registry_result = validate_sigma_registry()
    if registry_result.get("status") != "PASS":
        errors.extend(
            f"registry:{e}" for e in registry_result.get("errors", [])
        )

    dispatcher_result = validate_sigma_dispatcher()
    if dispatcher_result.get("status") != "PASS":
        errors.extend(
            f"dispatcher:{e}" for e in dispatcher_result.get("errors", [])
        )

    connector_result = validate_sigma_connectors()
    if connector_result.get("status") != "PASS":
        errors.extend(
            f"connector:{e}" for e in connector_result.get("errors", [])
        )

    domains = list_sigma_domains()

    return {
        "status": "PASS" if not errors else "FAIL",
        "bridge_version": BRIDGE_VERSION,
        "registry_status": registry_result.get("status"),
        "dispatcher_status": dispatcher_result.get("status"),
        "connector_status": connector_result.get("status"),
        "canonical_domains": domains,
        "domain_count": len(domains),
        "errors": errors,
        **_BRIDGE_BOUNDARY,
    }
