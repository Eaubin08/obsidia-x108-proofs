"""CSSA-specific CRM case proposal, no CRM store or external connector writes.

Uses existing native CRM mutation/request constructors unchanged. This does not
verify entity existence or authorize apply. A linked TASKS request is a
candidate reference only; both writes remain HOLD pending real checks.
"""
from __future__ import annotations

from periphery.cssa_admin_e2e_synthetic_v0 import build_cssa_admin_case, verify_cssa_admin_case
from periphery.cssa_native_task_candidate_v0 import prepare_cssa_supporter_task, FIXTURE_TIME
from periphery.native_ops.common_v0 import ABSENT_STATE_HASH
from periphery.native_ops.crm_native_v0 import KIND_RECORD, build_crm_mutation_v0
from periphery.native_ops.world_action_bridge_v0 import build_native_world_action_request_v0


def prepare_cssa_supporter_crm(message: dict[str, str]) -> dict:
    bundle = build_cssa_admin_case(message)
    if not verify_cssa_admin_case(bundle):
        raise ValueError("CSSA_PROPOSAL_RECEIPT_INVALID")
    intake = bundle["case"]["input"]
    task = prepare_cssa_supporter_task(message)
    base = {
        "schema": "CSSA_NATIVE_CRM_CANDIDATE_V0",
        "status": "HOLD",
        "decision_authority": "KX108_ONLY",
        "kx108_decision": None,
        "human_approval": None,
        "external_actions": [],
        "crm_store_write": False,
        "calendar_write": False,
        "email_send": False,
    }
    if intake["category_candidate"] != "SUPPORTER_REQUEST":
        return {**base, "reason": "NO_SUPPORTER_CASE_OR_AMBIGUOUS",
                "crm_mutation": None, "crm_request": None, "task_request": None}
    if task["world_action_request"] is None:
        raise ValueError("CSSA_TASK_PROJECTION_MISSING")
    fingerprint = intake["source_fingerprint"]
    mutation = build_crm_mutation_v0(
        mutation_id="cssa:crm:create:" + fingerprint[:24],
        entity_kind=KIND_RECORD,
        entity_id="cssa-case-" + fingerprint[:24],
        operation="CREATE_RECORD",
        payload={
            "occurred_at": FIXTURE_TIME,
            "record_type": "CASE",
            "display_label": "Demande supporter CSSA (simulation)",
            "lifecycle_status": "OPEN",
            "owner_ref": None,
            "fields": {
                "source_kind": "SYNTHETIC",
                "source_message_id": intake["message_id"],
                "source_sha256": fingerprint,
                "proposed_task_id": task["mutation"].entity_id,
                "proposed_task_state": "NOT_CREATED",
            },
            "tags": ["CSSA", "SYNTHETIC", "SUPPORTER_REQUEST"],
        },
        expected_prestate_hash=ABSENT_STATE_HASH,
        source_refs=("cssa:synth:" + fingerprint,),
        requested_by="CSSA_TEST_OPERATOR",
    )
    request = build_native_world_action_request_v0(mutation)
    task_request = task["world_action_request"]
    for item in (request, task_request):
        if (item["decision_authority"] != "KX108_ONLY"
                or item["allowed_to_act"] is not False
                or item["allowed_to_decide"] is not False
                or item["emits_act"] is not False):
            raise ValueError("CSSA_NATIVE_AUTHORITY_BOUNDARY_INVALID")
    return {
        **base,
        "reason": "NO_KX108_DECISION_OR_HUMAN_APPROVAL;EXISTENCE_NOT_VERIFIED",
        "crm_mutation": mutation,
        "crm_request": request,
        "task_request": task_request,
        "relation_status": "CANDIDATE_ONLY_NO_CANONICAL_LINK",
    }
