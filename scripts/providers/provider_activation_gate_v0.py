from __future__ import annotations

from typing import Optional

from providers.provider_registry_v0 import resolve_provider
from providers.provider_registry_manifest_binding_v0 import (
    get_provider_capabilities,
)


SCHEMA_VERSION = 1
DOMAIN_TAG = "OBSIDIA_CG9_PROVIDER_ACTIVATION_GATE_V0"


def evaluate_provider_activation(
    provider_id: str,
    requested_capability: str,
) -> dict:

    provider = resolve_provider(provider_id)

    if provider.get("status") != "REGISTRY_READY":
        return {
            "status": "ACTIVATION_REJECTED",
            "reason": "PROVIDER_NOT_REGISTERED",
        }

    if provider.get("enabled") is not True:
        return {
            "status": "ACTIVATION_REJECTED",
            "reason": "PROVIDER_DISABLED",
        }

    capabilities = get_provider_capabilities(
        provider_id
    )

    if requested_capability not in capabilities:
        return {
            "status": "ACTIVATION_REJECTED",
            "reason": "CAPABILITY_NOT_BOUND",
        }

    return {
        "status": "ACTIVATION_READY",
        "schema_version": SCHEMA_VERSION,
        "domain_tag": DOMAIN_TAG,
        "provider_id": provider_id,
        "requested_capability": requested_capability,
        "invocable": True,
        "execution_authority": False,
        "kx_authority": False,
    }


def verify_activation(
    activation: object,
) -> tuple[bool, Optional[str]]:

    if not isinstance(activation, dict):
        return False, "ACTIVATION_MISSING"

    if activation.get("status") != "ACTIVATION_READY":
        return False, "ACTIVATION_NOT_READY"

    if activation.get("invocable") is not True:
        return False, "INVOCATION_NOT_GRANTED"

    if activation.get("execution_authority") is not False:
        return False, "EXECUTION_AUTHORITY_FORBIDDEN"

    if activation.get("kx_authority") is not False:
        return False, "KX_AUTHORITY_FORBIDDEN"

    return True, None
