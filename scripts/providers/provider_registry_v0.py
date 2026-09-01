from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


SCHEMA_VERSION = 1
DOMAIN_TAG = "OBSIDIA_CG9_PROVIDER_REGISTRY_V0"


_REGISTRY = (
    Path(__file__).resolve().parent
    / "provider_registry_v0.json"
)


def load_registry() -> dict:
    with _REGISTRY.open(
        "r",
        encoding="utf-8-sig"
    ) as f:
        return json.load(f)


def resolve_provider(provider_id: str) -> dict:

    registry = load_registry()

    provider = registry.get(
        "providers",
        {}
    ).get(provider_id)

    if provider is None:
        return {
            "status": "REGISTRY_REJECTED",
            "reason": "UNKNOWN_PROVIDER",
        }

    return {
        "status": "REGISTRY_READY",
        "schema_version": SCHEMA_VERSION,
        "domain_tag": DOMAIN_TAG,
        "provider_id": provider_id,
        "provider_status": provider.get("status"),
        "contract_version": provider.get("contract_version"),
        "adapter_id": provider.get("adapter_id"),
        "enabled": provider.get("enabled"),
    }


def verify_registry(
    registry: object
) -> tuple[bool, Optional[str]]:

    if not isinstance(registry, dict):
        return False, "REGISTRY_MISSING"

    if registry.get(
        "schema_version"
    ) != SCHEMA_VERSION:
        return False, "SCHEMA_UNSUPPORTED"

    if not isinstance(
        registry.get("providers"),
        dict
    ):
        return False, "PROVIDER_MAP_INVALID"

    return True, None
