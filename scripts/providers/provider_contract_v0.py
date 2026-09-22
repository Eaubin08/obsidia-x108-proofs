from __future__ import annotations

"""
OBSIDIA CG9 — Generic Cognitive Provider Contract V0.

Defines the provider-facing data contract only.

NO provider is invoked here.
NO provider selection policy is inferred here.
NO tool access, execution authority, KX authority, scope expansion,
memory write, repository mutation, apply, commit, push or deploy.
"""

from typing import Optional


SCHEMA_VERSION = 1
DOMAIN_TAG = "OBSIDIA_CG9_PROVIDER_CONTRACT_V0"

KNOWN_PROVIDERS = ("brody", "obsidure", "claude")

RESULT_EVIDENCE = "EVIDENCE"
RESULT_PROPOSAL = "PROPOSAL"

_PROVIDER_RESULT_KIND = {
    "brody": RESULT_EVIDENCE,
    "claude": RESULT_EVIDENCE,
    "obsidure": RESULT_PROPOSAL,
}


def normalize_provider(provider: object) -> Optional[str]:
    if not isinstance(provider, str):
        return None
    p = provider.strip().lower()
    return p if p in KNOWN_PROVIDERS else None


def select_provider(
    allowed_providers: object,
    *,
    selected_provider: Optional[str] = None,
) -> dict:
    """
    Closed deterministic selection seam.

    0 allowed  -> reject
    1 allowed  -> select sole provider
    >1 allowed -> explicit selected_provider required

    No priority or implicit model preference exists in V0.
    """
    if not isinstance(allowed_providers, list):
        return {"status": "PROVIDER_SELECTION_REJECTED",
                "reason": "ALLOWED_PROVIDERS_NOT_LIST",
                "selected_provider": None}

    normalized = []
    for raw in allowed_providers:
        p = normalize_provider(raw)
        if p is None:
            return {"status": "PROVIDER_SELECTION_REJECTED",
                    "reason": "UNKNOWN_PROVIDER_IN_SCOPE",
                    "selected_provider": None}
        if p not in normalized:
            normalized.append(p)

    if not normalized:
        return {"status": "PROVIDER_SELECTION_REJECTED",
                "reason": "NO_ALLOWED_PROVIDER",
                "selected_provider": None}

    if len(normalized) == 1:
        if selected_provider is not None:
            explicit = normalize_provider(selected_provider)
            if explicit != normalized[0]:
                return {"status": "PROVIDER_SELECTION_REJECTED",
                        "reason": "SELECTED_PROVIDER_NOT_ALLOWED",
                        "selected_provider": None}
        return {"status": "PROVIDER_SELECTED",
                "reason": None,
                "selected_provider": normalized[0]}

    if selected_provider is None:
        return {"status": "PROVIDER_SELECTION_REJECTED",
                "reason": "EXPLICIT_PROVIDER_REQUIRED",
                "selected_provider": None}

    explicit = normalize_provider(selected_provider)
    if explicit is None:
        return {"status": "PROVIDER_SELECTION_REJECTED",
                "reason": "SELECTED_PROVIDER_UNKNOWN",
                "selected_provider": None}
    if explicit not in normalized:
        return {"status": "PROVIDER_SELECTION_REJECTED",
                "reason": "SELECTED_PROVIDER_NOT_ALLOWED",
                "selected_provider": None}

    return {"status": "PROVIDER_SELECTED",
            "reason": None,
            "selected_provider": explicit}


def provider_result_kind(provider: str) -> Optional[str]:
    p = normalize_provider(provider)
    return _PROVIDER_RESULT_KIND.get(p) if p is not None else None


def build_provider_invocation(
    *,
    relay_mission_id: str,
    mission_submission_id: str,
    capability_request_ref: str,
    lease_id: str,
    lease_record_hash: str,
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
        "selected_provider": provider,
        "requested_capability": requested_capability,
        "reason": reason,
        "result_kind_expected": provider_result_kind(provider),
        "is_execution_authority": False,
        "is_kx_authority": False,
        "is_sovereign": False,
        "grants_tool_access": False,
        "grants_scope": False,
    }


def verify_provider_invocation(record: object) -> tuple[bool, Optional[str]]:
    if not isinstance(record, dict):
        return False, "INVOCATION_MISSING"
    if record.get("schema_version") != SCHEMA_VERSION:
        return False, "SCHEMA_UNSUPPORTED"
    if record.get("domain_tag") != DOMAIN_TAG:
        return False, "DOMAIN_TAG_MISMATCH"

    provider = normalize_provider(record.get("selected_provider"))
    if provider is None:
        return False, "PROVIDER_UNKNOWN"
    if record.get("result_kind_expected") != provider_result_kind(provider):
        return False, "RESULT_KIND_MAPPING_MISMATCH"

    required_prefixes = {
        "relay_mission_id": "rmis-",
        "mission_submission_id": "gsub-",
        "capability_request_ref": "gcap-",
        "lease_id": "cclease-",
    }
    for field, prefix in required_prefixes.items():
        value = record.get(field)
        if not (isinstance(value, str) and value.startswith(prefix)):
            return False, f"{field.upper()}_MALFORMED"

    for field in ("lease_record_hash", "requested_capability", "reason"):
        if not (isinstance(record.get(field), str) and record.get(field)):
            return False, f"{field.upper()}_MISSING"

    for field in (
        "is_execution_authority",
        "is_kx_authority",
        "is_sovereign",
        "grants_tool_access",
        "grants_scope",
    ):
        if record.get(field) is not False:
            return False, f"{field.upper()}_FORBIDDEN"

    return True, None
