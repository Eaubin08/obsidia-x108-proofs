from __future__ import annotations

"""
OBSIDIA CG9 Cognitive Provider Binder V0

Binds verified cognitive capability requests to external providers.

NON AUTHORITY:
- no execution authority
- no KX authority
- no scope expansion
- no lease creation
- no repository mutation

Providers are adapters.
This module only governs eligibility and result envelopes.
"""

from typing import Optional


SCHEMA_VERSION = 1
DOMAIN_TAG = "OBSIDIA_CG9_COGNITIVE_PROVIDER_BINDER_V0"

BINDER_ACTIVE = True

PROVIDER_CALL_ALLOWED = False

RESULT_EVIDENCE = "EVIDENCE"
RESULT_PROPOSAL = "PROPOSAL"


PROVIDER_REGISTRY = {
    "BRODY": {
        "kind": "COGNITIVE",
        "enabled": False,
    },
    "CLAUDE": {
        "kind": "COGNITIVE",
        "enabled": False,
    },
    "OBSIDURE": {
        "kind": "FORMAL",
        "enabled": False,
    },
}


def get_provider(name: str) -> Optional[dict]:
    if not isinstance(name, str):
        return None
    return PROVIDER_REGISTRY.get(name.upper())


def verify_provider_available(name: str) -> tuple[bool, Optional[str]]:
    provider = get_provider(name)
    if provider is None:
        return False, "PROVIDER_UNKNOWN"
    if provider["enabled"] is not True:
        return False, "PROVIDER_DISABLED"
    return True, None


def build_capability_result(
    *,
    provider: str,
    result_kind: str,
    content: str,
) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "domain_tag": DOMAIN_TAG,
        "provider": provider,
        "result_kind": result_kind,
        "content": content,
        "is_execution_authority": False,
        "is_kx_authority": False,
        "is_sovereign": False,
    }


def verify_capability_result(result: dict) -> tuple[bool, Optional[str]]:
    if not isinstance(result, dict):
        return False, "RESULT_MISSING"

    if result.get("domain_tag") != DOMAIN_TAG:
        return False, "DOMAIN_TAG_MISMATCH"

    if result.get("is_execution_authority") is not False:
        return False, "EXECUTION_AUTHORITY_FORBIDDEN"

    if result.get("is_kx_authority") is not False:
        return False, "KX_AUTHORITY_FORBIDDEN"

    if result.get("result_kind") not in (
        RESULT_EVIDENCE,
        RESULT_PROPOSAL,
    ):
        return False, "RESULT_KIND_INVALID"

    return True, None
