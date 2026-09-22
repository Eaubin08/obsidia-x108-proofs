from __future__ import annotations

"""
OBSIDIA CG9 — Provider Invocation V0.

Binds a validated provider contract to a bounded capability context.

This module does NOT call providers.
This module does NOT grant authority.
This module only creates/verifies an invocation envelope.
"""

from typing import Optional

from providers.provider_contract_v0 import (
    normalize_provider,
    provider_result_kind,
    SCHEMA_VERSION as CONTRACT_SCHEMA_VERSION,
)


SCHEMA_VERSION = 1
DOMAIN_TAG = "OBSIDIA_CG9_PROVIDER_INVOCATION_V0"


def build_provider_invocation(
    *,
    relay_mission_id: str,
    mission_submission_id: str,
    capability_request_ref: str,
    lease_id: str,
    lease_record_hash: str,
    mission_capability_scope_id: str,
    selected_provider: str,
    requested_capability: str,
    reason: str,
) -> dict:
    provider = normalize_provider(selected_provider)
    if provider is None:
        raise ValueError("UNKNOWN_PROVIDER")

    return {
        "schema_version": SCHEMA_VERSION,
        "domain_tag": DOMAIN_TAG,

        "relay_mission_id": relay_mission_id,
        "mission_submission_id": mission_submission_id,
        "capability_request_ref": capability_request_ref,

        "lease_id": lease_id,
        "lease_record_hash": lease_record_hash,
        "mission_capability_scope_id": mission_capability_scope_id,

        "selected_provider": provider,
        "requested_capability": requested_capability,
        "reason": reason,

        "expected_result_kind": provider_result_kind(provider),

        "provider_execution_started": False,
        "provider_called": False,

        "is_execution_authority": False,
        "is_kx_authority": False,
        "is_sovereign": False,
        "grants_tool_access": False,
        "grants_scope": False,
        "memory_write": False,
        "repository_mutation": False,
    }


def verify_provider_invocation(invocation: object) -> tuple[bool, Optional[str]]:
    if not isinstance(invocation, dict):
        return False, "INVOCATION_MISSING"

    if invocation.get("schema_version") != SCHEMA_VERSION:
        return False, "SCHEMA_UNSUPPORTED"

    if invocation.get("domain_tag") != DOMAIN_TAG:
        return False, "DOMAIN_TAG_MISMATCH"

    provider = normalize_provider(invocation.get("selected_provider"))
    if provider is None:
        return False, "UNKNOWN_PROVIDER"

    if invocation.get("expected_result_kind") != provider_result_kind(provider):
        return False, "RESULT_KIND_MISMATCH"

    required = (
        "relay_mission_id",
        "mission_submission_id",
        "capability_request_ref",
        "lease_id",
        "lease_record_hash",
        "mission_capability_scope_id",
        "requested_capability",
        "reason",
    )

    for field in required:
        if not isinstance(invocation.get(field), str) or not invocation[field]:
            return False, f"{field.upper()}_MISSING"

    forbidden_false = (
        "provider_execution_started",
        "provider_called",
        "is_execution_authority",
        "is_kx_authority",
        "is_sovereign",
        "grants_tool_access",
        "grants_scope",
        "memory_write",
        "repository_mutation",
    )

    for field in forbidden_false:
        if invocation.get(field) is not False:
            return False, f"{field.upper()}_FORBIDDEN"

    return True, None
