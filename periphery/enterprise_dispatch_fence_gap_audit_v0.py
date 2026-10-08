"""C2.22 audit the check-to-dispatch revocation gap, with mandatory BLOCK.

A local status check and an action are not one atomic transaction.
No trusted organization issuer, dispatch fence or live provider is present.
"""
from __future__ import annotations

def inspect_dispatch_fence_v0(*, ledger, scope, generation, nonce,
                               post_check_hook=None):
    def deny(reason, observed=None):
        return {"status":"BLOCK","reason":reason,"egress_allowed":False,
                "execution_authority":False,"dispatch_attempted":False,
                "ledger_observation":observed}
    if post_check_hook is not None:
        # Do not invoke caller-controlled dispatch hooks, even in a dry run.
        return deny("C222_CALLER_HOOK_NOT_TRUSTED")
    try:
        observed=ledger.check_and_consume_fixture(
            scope,generation=generation,nonce=nonce,evidence_verified=True)
    except Exception:
        return deny("C222_LEDGER_UNAVAILABLE")
    if observed!="CHECKED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY":
        return deny("C222_LEDGER_REJECTED",observed)
    # A revoke can race immediately after this return; the observation may
    # already be stale. It must never be transformed into a dispatch ticket.
    return deny("C222_NO_ATOMIC_REVOCATION_DISPATCH_FENCE",observed)
