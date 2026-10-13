"""C2.6 sober audit gate: reject unverified KX108 and SovereignTicket claims.

A schema-valid decision or locally constructed ticket is not sovereign
attestation. This adapter intentionally has no execution-grant branch.
"""
from __future__ import annotations

from periphery.world_calls.sovereign_ticket import SovereignTicket

def inspect_sovereign_claims_v0(*, decision_envelope, ticket, expected_action_id,
                                expected_scope):
    if not isinstance(decision_envelope, dict):
        return "BLOCK:C26_DECISION_ENVELOPE_UNAVAILABLE"
    if decision_envelope.get("x108_gate") not in ("ALLOW", "ACT"):
        return "BLOCK:C26_NOT_KX108_ALLOW"
    if not isinstance(ticket, SovereignTicket):
        return "BLOCK:C26_TICKET_MISSING"
    if ticket.action_id != expected_action_id or not ticket.is_valid_scope(expected_scope):
        return "BLOCK:C26_TICKET_ACTION_OR_SCOPE_MISMATCH"
    if ticket.is_expired() or ticket.dry_run_only is not True:
        return "BLOCK:C26_TICKET_EXPIRED_OR_NOT_DRY_RUN"
    if ticket.x108_gate not in ("ALLOW", "ACT"):
        return "BLOCK:C26_TICKET_NOT_KX108_ALLOW"
    # The available field checks cannot authenticate the original
    # KX108 source or the ticket issuer and cannot bind a live consent.
    return "BLOCK:C26_INDEPENDENT_SOVEREIGN_ATTESTATION_UNAVAILABLE"
