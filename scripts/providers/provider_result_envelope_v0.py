from __future__ import annotations

"""
OBSIDIA CG9 — Provider Result Envelope V0.

Represents a cognitive provider output.

Allowed:
- EVIDENCE
- PROPOSAL

Forbidden:
- authority
- execution
- scope mutation
- memory mutation
- decision emission
"""

from typing import Optional

from providers.provider_contract_v0 import (
    normalize_provider,
    RESULT_EVIDENCE,
    RESULT_PROPOSAL,
)


SCHEMA_VERSION = 1
DOMAIN_TAG = "OBSIDIA_CG9_PROVIDER_RESULT_ENVELOPE_V0"

_ALLOWED_RESULTS = (
    RESULT_EVIDENCE,
    RESULT_PROPOSAL,
)


def build_provider_result(
    *,
    invocation_id: str,
    selected_provider: str,
    result_kind: str,
    summary: str,
    evidence_refs: list[str] | None = None,
) -> dict:

    provider = normalize_provider(selected_provider)

    if provider is None:
        raise ValueError("UNKNOWN_PROVIDER")

    if result_kind not in _ALLOWED_RESULTS:
        raise ValueError("RESULT_KIND_FORBIDDEN")

    return {
        "schema_version": SCHEMA_VERSION,
        "domain_tag": DOMAIN_TAG,

        "provider_invocation_id": invocation_id,
        "selected_provider": provider,

        "result_kind": result_kind,
        "summary": summary,
        "evidence_refs": list(evidence_refs or []),

        "is_execution_authority": False,
        "is_kx_authority": False,
        "is_sovereign": False,

        "emits_act": False,
        "emits_decision": False,
        "memory_write": False,
        "scope_mutation": False,
    }


def verify_provider_result(
    envelope: object,
) -> tuple[bool, Optional[str]]:

    if not isinstance(envelope, dict):
        return False, "RESULT_MISSING"

    if envelope.get("schema_version") != SCHEMA_VERSION:
        return False, "SCHEMA_UNSUPPORTED"

    if envelope.get("domain_tag") != DOMAIN_TAG:
        return False, "DOMAIN_TAG_MISMATCH"

    if normalize_provider(envelope.get("selected_provider")) is None:
        return False, "UNKNOWN_PROVIDER"

    if envelope.get("result_kind") not in _ALLOWED_RESULTS:
        return False, "RESULT_KIND_FORBIDDEN"

    for field in (
        "provider_invocation_id",
        "summary",
    ):
        if not isinstance(envelope.get(field), str) or not envelope[field]:
            return False, f"{field.upper()}_MISSING"

    for field in (
        "is_execution_authority",
        "is_kx_authority",
        "is_sovereign",
        "emits_act",
        "emits_decision",
        "memory_write",
        "scope_mutation",
    ):
        if envelope.get(field) is not False:
            return False, f"{field.upper()}_FORBIDDEN"

    return True, None
