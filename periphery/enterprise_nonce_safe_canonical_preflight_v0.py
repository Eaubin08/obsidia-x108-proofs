"""C2.20 non-consuming sovereign barrier before fixture nonce checks.

The C2.8 authenticated-ticket gap is mandatory BLOCK. This preflight never
touches the C2.3 ledger; a failed upstream check cannot burn a nonce.
A future live adapter requires shared atomic dispatch fencing, not this code.
"""
from __future__ import annotations
from periphery.enterprise_approval_ticket_boundary_v0 import inspect_approval_ticket_chain_v0

def inspect_nonce_safe_canonical_preflight_v0(*, request, approval, record, ticket,
                                              delegation_inputs):
    def deny(reason):
        return {"status":"BLOCK","reason":reason,"egress_allowed":False,
                "execution_authority":False,"nonce_consumed":False}
    if not isinstance(delegation_inputs,dict):
        return deny("C220_DELEGATION_CONTEXT_MISSING")
    try:
        checked=inspect_approval_ticket_chain_v0(
            request=request,approval=approval,record=record,ticket=ticket)
    except Exception:
        return deny("C220_SOVEREIGN_VERIFIER_UNAVAILABLE")
    # C2.8 NEVER authenticates current SovereignTicket issuer. In particular,
    # never evaluate any fixture ledger/nonce while this boundary is blocked.
    return deny("C220_SOVEREIGN_BLOCKED:"+str(checked.get("reason")))
