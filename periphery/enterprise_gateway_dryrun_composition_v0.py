"""C2.4 offline proof-to-gateway composition; strictly non-authorizing."""
from __future__ import annotations

from periphery.enterprise_scoped_delegation_proof_v0 import verify_scoped_delegation_v0
from periphery.world_calls.obsidia_gateway import ObsidiaGateway

def inspect_fixture_composition_v0(*, proof, verifier_args, ledger, scope,
                                  generation, nonce, ticket, world_call_class,
                                  required_scope):
    """No real dispatch: even a valid signature + local ledger + ticket
    cannot authorize a provider call or independently attest KX108.
    """
    valid, reason = verify_scoped_delegation_v0(proof, **verifier_args)
    if not valid:
        return {"status": "BLOCK", "reason": reason, "egress_allowed": False}
    # Deny HOLD/BLOCK/missing KX108 fields before touching the nonce ledger.
    # ACT here is only an untrusted fixture label, NEVER independent attestation.
    if ticket is None or getattr(ticket, "x108_gate", None) != "ACT":
        return {"status": "BLOCK", "reason": "C25_KX108_ALLOW_NOT_VERIFIED",
                "egress_allowed": False}
    decision = ObsidiaGateway().check(
        ticket, world_call_class, required_scope=required_scope
    )
    if decision.gate_result != "DRY_RUN_PASS" or decision.egress_allowed is not False:
        return {"status": "BLOCK", "reason": "C25_GATEWAY_PREFLIGHT_DENIED",
                "gateway_reason": decision.reason, "egress_allowed": False}
    ledger_result = ledger.check_and_consume_fixture(
        scope, generation=generation, nonce=nonce, evidence_verified=True
    )
    if ledger_result != "CHECKED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY":
        return {"status": "BLOCK", "reason": ledger_result, "egress_allowed": False}
    return {
        "status": "NO_EXECUTION",
        "reason": "C24_OFFLINE_FIXTURE_COMPOSITION_ONLY",
        "gateway_gate_result": decision.gate_result,
        "gateway_reason": decision.reason,
        "egress_allowed": False,
        "kx108_live_verified": False,
        "organization_authority_live_verified": False,
    }
