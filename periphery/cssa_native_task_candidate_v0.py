"""CSSA-only projection to existing Native TASKS contracts, proposal-only.

No native store is instantiated, no apply function is imported or called, and
no KX108 authorization is claimed. Explicitly synthetic fixture timestamp.
"""
from __future__ import annotations

from periphery.cssa_admin_e2e_synthetic_v0 import (
    build_cssa_admin_case,
    verify_cssa_admin_case,
)
from periphery.native_ops.common_v0 import ABSENT_STATE_HASH
from periphery.native_ops.tasks_native_v0 import build_task_mutation_v0
from periphery.native_ops.world_action_bridge_v0 import build_native_world_action_request_v0

FIXTURE_TIME = "2026-10-08T10:00:00+00:00"


def prepare_cssa_supporter_task(message: dict[str, str]) -> dict:
    bundle = build_cssa_admin_case(message)
    if not verify_cssa_admin_case(bundle):
        raise ValueError("CSSA_PROPOSAL_RECEIPT_INVALID")
    intake = bundle["case"]["input"]
    if intake["category_candidate"] != "SUPPORTER_REQUEST":
        return {
            "schema": "CSSA_NATIVE_TASK_PROPOSAL_V0",
            "status": "HOLD",
            "reason": "NO_SUPPORTER_TASK_NEEDED_OR_AMBIGUOUS",
            "mutation": None,
            "world_action_request": None,
            "external_actions": [],
        }
    task_id = "cssa-" + intake["source_fingerprint"][:24]
    mutation = build_task_mutation_v0(
        mutation_id="cssa:create:" + task_id,
        task_id=task_id,
        operation="CREATE_TASK",
        payload={
            "occurred_at": FIXTURE_TIME,
            "title": "Examiner la demande du supporter",
            "description": "Synthétique, contrôle humain requis; source " + intake["message_id"],
            "priority": "NORMAL",
            "assignee_ref": None,
            "due_at": None,
            "dependency_ids": [],
            "tags": ["CSSA", "SYNTHETIC"],
        },
        expected_prestate_hash=ABSENT_STATE_HASH,
        source_refs=("cssa:synth:" + intake["source_fingerprint"],),
        requested_by="CSSA_TEST_OPERATOR",
    )
    request = build_native_world_action_request_v0(mutation)
    if request["decision_authority"] != "KX108_ONLY" or request["allowed_to_act"] is not False:
        raise ValueError("CSSA_NATIVE_REQUEST_BOUNDARY_INVALID")
    return {
        "schema": "CSSA_NATIVE_TASK_PROPOSAL_V0",
        "status": "HOLD",
        "reason": "NO_KX108_DECISION_OR_HUMAN_APPROVAL",
        "mutation": mutation,
        "world_action_request": request,
        "external_actions": [],
        "native_store_write": False,
        "human_approval": None,
        "kx108_decision": None,
    }
