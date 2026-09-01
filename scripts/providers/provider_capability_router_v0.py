from __future__ import annotations

from typing import Optional

from providers.provider_contract_v0 import normalize_provider


SCHEMA_VERSION = 1
DOMAIN_TAG = "OBSIDIA_CG9_PROVIDER_CAPABILITY_ROUTER_V0"


# Déclaration statique.
# Aucun apprentissage, aucune sélection autonome.
CAPABILITY_MATRIX = {
    "ENGINEERING_REASONING": {
        "brody",
        "obsidure",
    },
    "FORMAL_VERIFICATION": {
        "obsidure",
    },
    "LANGUAGE_REASONING": {
        "brody",
        "claude",
    },
}


def route_capability(
    *,
    requested_capability: str,
    allowed_providers: list[str],
) -> dict:

    if requested_capability not in CAPABILITY_MATRIX:
        return {
            "status": "ROUTING_REJECTED",
            "reason": "UNKNOWN_CAPABILITY",
        }

    compatible = []

    for provider in allowed_providers:
        normalized = normalize_provider(provider)

        if normalized is None:
            continue

        if normalized in CAPABILITY_MATRIX[requested_capability]:
            compatible.append(normalized)

    if not compatible:
        return {
            "status": "ROUTING_REJECTED",
            "reason": "NO_COMPATIBLE_PROVIDER",
        }

    return {
        "status": "ROUTING_READY",
        "schema_version": SCHEMA_VERSION,
        "domain_tag": DOMAIN_TAG,
        "requested_capability": requested_capability,
        "compatible_providers": sorted(compatible),
    }


def verify_routing(route: object) -> tuple[bool, Optional[str]]:

    if not isinstance(route, dict):
        return False, "ROUTE_MISSING"

    if route.get("schema_version") != SCHEMA_VERSION:
        return False, "SCHEMA_UNSUPPORTED"

    if route.get("status") != "ROUTING_READY":
        return False, "ROUTING_NOT_READY"

    if not isinstance(route.get("compatible_providers"), list):
        return False, "PROVIDER_LIST_INVALID"

    if len(route["compatible_providers"]) == 0:
        return False, "EMPTY_PROVIDER_LIST"

    return True, None
