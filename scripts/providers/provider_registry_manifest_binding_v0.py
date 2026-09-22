from __future__ import annotations

from typing import Optional

from providers.provider_registry_v0 import load_registry
from providers.provider_capability_manifest_v0 import load_manifest


SCHEMA_VERSION = 1
DOMAIN_TAG = "OBSIDIA_CG9_PROVIDER_REGISTRY_MANIFEST_BINDING_V0"


def build_provider_capability_surface() -> dict:
    registry = load_registry()
    manifest = load_manifest()

    providers = registry.get("providers", {})
    capabilities = manifest.get("capabilities", {})

    return {
        "registry_schema_version": registry.get("schema_version"),
        "manifest_schema_version": manifest.get("schema_version"),
        "providers": providers,
        "capabilities": capabilities,
    }


def verify_registry_manifest_binding(
    surface: object,
) -> tuple[bool, Optional[str]]:

    if not isinstance(surface, dict):
        return False, "SURFACE_MISSING"

    providers = surface.get("providers")
    capabilities = surface.get("capabilities")

    if not isinstance(providers, dict):
        return False, "PROVIDER_MAP_INVALID"

    if not isinstance(capabilities, dict):
        return False, "CAPABILITY_MAP_INVALID"

    declared_providers = set(providers.keys())

    for capability_providers in capabilities.values():

        if not isinstance(capability_providers, list):
            return False, "CAPABILITY_PROVIDER_LIST_INVALID"

        for provider in capability_providers:

            if provider not in declared_providers:
                return False, "PROVIDER_NOT_IN_REGISTRY"

    return True, None


def get_provider_capabilities(provider_id: str) -> list[str]:

    surface = build_provider_capability_surface()

    out = []

    for capability, providers in surface["capabilities"].items():

        if provider_id in providers:
            out.append(capability)

    return sorted(out)
