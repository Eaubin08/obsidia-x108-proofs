"""C2.8 evidence-only approval/record/ticket cross-check, no egress.

Approval is a hashed human *claim*, not independently authenticated consent.
The current SovereignTicket is locally constructible, not signed to a KX108
decision record. Even exact field agreement must therefore fail closed.
"""
from __future__ import annotations
from periphery.enterprise_world_action_kx108_record_boundary_v0 import (
    inspect_world_action_kx108_record_v0,
)
from scripts import obsidia_world_action_pre_execution_context_v0 as context
from periphery.world_calls.sovereign_ticket import SovereignTicket


def inspect_approval_ticket_chain_v0(*, request, approval, record, ticket):
    denied = lambda reason: {"status": "BLOCK", "reason": reason,
                              "egress_allowed": False, "execution_authority": False}
    ok, reason = context.verify_world_action_request_mapping(request)
    if not ok:
        return denied("C28_REQUEST_INVALID:" + str(reason))
    ok, reason = context.verify_world_action_human_approval(approval, request)
    if not ok:
        return denied("C28_APPROVAL_INVALID:" + str(reason))
    expected = {
        "world_action_request_hash": request["request_hash"],
        "connector_call_hash": request["connector_call_hash"],
        "human_approval_hash": approval["approval_hash"],
        "target_prestate_hash": request["target_prestate_hash"],
        "required_scope": request["required_scope"],
        "idempotency_key": request["idempotency_key"],
        "source_domain": request["domain_id"],
        "action_id": request["request_id"],
    }
    checked = inspect_world_action_kx108_record_v0(
        record=record, expected_binding=expected
    )
    if checked["status"] != "VERIFIED_RECORD_ONLY_NO_EXECUTION_AUTHORITY":
        return denied("C28_KX108_RECORD_REJECTED:" + checked["reason"])
    if not isinstance(ticket, SovereignTicket):
        return denied("C28_TICKET_MISSING")
    if (ticket.action_id != request["request_id"]
            or ticket.scope != request["required_scope"]):
        return denied("C28_TICKET_ACTION_OR_SCOPE_MISMATCH")
    if ticket.is_expired() or ticket.dry_run_only is not True:
        return denied("C28_TICKET_EXPIRED_OR_NOT_DRY_RUN")
    if ticket.x108_gate != record["x108_gate"]:
        return denied("C28_TICKET_GATE_MISMATCH")
    # SovereignTicket has no authenticated record hash/issuer binding.
    return denied("C28_TICKET_NOT_AUTHENTICATED_TO_KX108_RECORD")
