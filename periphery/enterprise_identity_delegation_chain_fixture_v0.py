"""C2.18 offline identity and scoped delegation join; deny-only.

Every check is backed by isolated fixtures. No corporate identity
attestation or real connector authorization is established.
"""
from __future__ import annotations
from periphery.enterprise_pinned_identity_chain_v0 import inspect_pinned_identity_claim_fixture_v0
from periphery.enterprise_scoped_delegation_proof_v0 import verify_scoped_delegation_v0

def inspect_identity_delegation_fixture_v0(*, registry, claim, public_key_pem,
    delegation, delegation_secret, delegation_issuer, organization, actor,
    delegate, connector, capability, request_hash, audience, identity_issuer, now,
    revocation_ledger, generation):
    def denied(reason):
        return {"status":"BLOCK","reason":reason,"egress_allowed":False,
                "organization_authority_verified":False,"execution_authority":False}
    identity = inspect_pinned_identity_claim_fixture_v0(
        registry=registry, claim=claim, public_key_pem=public_key_pem,
        expected_organization=organization, expected_actor=actor,
        expected_issuer=identity_issuer, expected_audience=audience,
        expected_capability=capability, expected_request_hash=request_hash, now=now)
    if not identity.get("cryptographic_fixture_valid"):
        return denied("C218_IDENTITY_REJECTED:"+str(identity.get("reason")))
    ok, reason=verify_scoped_delegation_v0(
        delegation,trusted_issuer_id=delegation_issuer,verifier_secret=delegation_secret,
        organization_id=organization,principal_id=actor,delegate_id=delegate,
        connector_id=connector,capability_id=capability,action_request_hash=request_hash,
        now=now)
    if not ok:
        return denied("C218_DELEGATION_REJECTED:"+str(reason))
    scope=(organization,delegate,connector,capability)
    try:
        ledger_result=revocation_ledger.check_and_consume_fixture(
            scope,generation=generation,nonce=delegation.nonce,evidence_verified=True)
    except Exception:
        return denied("C218_REVOCATION_LEDGER_UNAVAILABLE")
    if ledger_result!="CHECKED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY":
        return denied("C218_REVOCATION_REJECTED:"+ledger_result)
    return denied("C218_ORGANIZATION_DELEGATION_AUTHORITY_UNVERIFIED")
