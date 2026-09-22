from __future__ import annotations

from typing import Optional

from providers.provider_contract_v0 import normalize_provider


SCHEMA_VERSION = 1
DOMAIN_TAG = "OBSIDIA_CG9_PROVIDER_ADAPTER_V0"


SUPPORTED_ADAPTERS = {
    "brody": "BRODY_ADAPTER_V0",
    "obsidure": "OBSIDURE_ADAPTER_V0",
    "claude": "CLAUDE_ADAPTER_V0",
}


def resolve_adapter(provider: str) -> dict:
    normalized = normalize_provider(provider)

    if normalized is None:
        return {
            "status": "ADAPTER_REJECTED",
            "reason": "UNKNOWN_PROVIDER",
        }

    return {
        "status": "ADAPTER_READY",
        "schema_version": SCHEMA_VERSION,
        "domain_tag": DOMAIN_TAG,
        "provider": normalized,
        "adapter_id": SUPPORTED_ADAPTERS[normalized],
        "connected": False,
    }


def prepare_provider_payload(
    *,
    adapter: dict,
    invocation: dict,
) -> dict:

    if adapter.get("status") != "ADAPTER_READY":
        raise ValueError("ADAPTER_NOT_READY")

    return {
        "schema_version": SCHEMA_VERSION,
        "adapter_id": adapter["adapter_id"],
        "provider": adapter["provider"],

        "invocation_id": invocation.get(
            "capability_request_ref"
        ),

        "payload_only": True,

        "execution_authority": False,
        "kx_authority": False,
        "memory_write": False,
        "tool_access": False,
    }


def verify_adapter_payload(payload: object) -> tuple[bool, Optional[str]]:

    if not isinstance(payload, dict):
        return False, "PAYLOAD_MISSING"

    if payload.get("payload_only") is not True:
        return False, "PAYLOAD_ONLY_REQUIRED"

    forbidden = (
        "execution_authority",
        "kx_authority",
        "memory_write",
        "tool_access",
    )

    for key in forbidden:
        if payload.get(key) is not False:
            return False, f"{key.upper()}_FORBIDDEN"

    return True, None
