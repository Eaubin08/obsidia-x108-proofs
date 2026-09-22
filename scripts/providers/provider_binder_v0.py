from __future__ import annotations

from typing import Optional

from providers.provider_contract_v0 import select_provider
from providers.provider_invocation_v0 import (
    build_provider_invocation,
    verify_provider_invocation,
)
from providers.provider_result_envelope_v0 import (
    verify_provider_result,
)


SCHEMA_VERSION = 1
DOMAIN_TAG = "OBSIDIA_CG9_PROVIDER_BINDER_V0"


def prepare_provider_binding(
    *,
    relay_mission_id: str,
    mission_submission_id: str,
    capability_request_ref: str,
    lease_id: str,
    lease_record_hash: str,
    mission_capability_scope_id: str,
    allowed_providers: list[str],
    requested_capability: str,
    reason: str,
    selected_provider: Optional[str] = None,
) -> dict:

    selection = select_provider(
        allowed_providers,
        selected_provider=selected_provider,
    )

    if selection["status"] != "PROVIDER_SELECTED":
        return {
            "status": "BINDER_REJECTED",
            "reason": selection["reason"],
        }

    invocation = build_provider_invocation(
        relay_mission_id=relay_mission_id,
        mission_submission_id=mission_submission_id,
        capability_request_ref=capability_request_ref,
        lease_id=lease_id,
        lease_record_hash=lease_record_hash,
        mission_capability_scope_id=mission_capability_scope_id,
        selected_provider=selection["selected_provider"],
        requested_capability=requested_capability,
        reason=reason,
    )

    ok, why = verify_provider_invocation(invocation)

    if not ok:
        return {
            "status": "BINDER_REJECTED",
            "reason": why,
        }

    return {
        "status": "BINDER_READY",
        "schema_version": SCHEMA_VERSION,
        "domain_tag": DOMAIN_TAG,
        "provider": selection["selected_provider"],
        "invocation": invocation,
        "provider_called": False,
        "execution_started": False,
    }


def accept_provider_result(result: object) -> dict:
    ok, why = verify_provider_result(result)

    if not ok:
        return {
            "status": "RESULT_REJECTED",
            "reason": why,
        }

    return {
        "status": "RESULT_ACCEPTED",
        "provider_called": True,
        "execution_started": False,
        "result": result,
    }
