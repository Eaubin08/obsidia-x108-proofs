"""C2.19 evidence-only preflight joining C2.18 and canonical KX108/ticket boundaries.

Never returns ALLOW or authorizes dispatch. In particular, C2.8 must still
refuse an unauthenticated SovereignTicket; C2.9 is fixture MAC only.
"""
from periphery.enterprise_identity_delegation_chain_fixture_v0 import inspect_identity_delegation_fixture_v0
from periphery.enterprise_approval_ticket_boundary_v0 import inspect_approval_ticket_chain_v0
from periphery.enterprise_record_bound_ticket_fixture_v0 import verify_ticket_record_fixture_v0

def inspect_c219_preflight_v0(*, request, approval, record, ticket,
                              binding_fixture, binding_key, binding_issuer,
                              delegation_inputs, now):
    def block(reason):
        return {"status": "BLOCK", "reason": reason,
                "egress_allowed": False, "execution_authority": False}
    if not isinstance(delegation_inputs, dict):
        return block("C219_DELEGATION_INPUTS_MISSING")
    # C2.18 may consume an offline fixture nonce; never a real dispatch.
    try:
        delegation = inspect_identity_delegation_fixture_v0(**delegation_inputs)
    except Exception:
        return block("C219_DELEGATION_VERIFIER_UNAVAILABLE")
    if delegation.get("reason") != "C218_ORGANIZATION_DELEGATION_AUTHORITY_UNVERIFIED":
        return block("C219_DELEGATION_REJECTED:" + str(delegation.get("reason")))
    # C2.8 verifies the request/approval and canonical KX108 record and
    # rejects even a coherent locally constructible SovereignTicket.
    try:
        sovereign = inspect_approval_ticket_chain_v0(
            request=request, approval=approval, record=record, ticket=ticket)
    except Exception:
        return block("C219_SOVEREIGN_VERIFIER_UNAVAILABLE")
    if sovereign.get("reason") != "C28_TICKET_NOT_AUTHENTICATED_TO_KX108_RECORD":
        return block("C219_SOVEREIGN_REJECTED:" + str(sovereign.get("reason")))
    try:
        ok, reason = verify_ticket_record_fixture_v0(
            binding_fixture, trusted_fixture_issuer=binding_issuer,
            verifier_key=binding_key, record=record, ticket=ticket, now=now)
    except Exception:
        return block("C219_TICKET_BINDING_VERIFIER_UNAVAILABLE")
    if not ok:
        return block("C219_TICKET_BINDING_REJECTED:" + str(reason))
    # Test fixture signature is not a trusted ticket issuer or org authority.
    return block("C219_NO_AUTHENTICATED_ORGANIZATION_OR_TICKET_ISSUER")
