"""C2.17 offline signature + pinned-key inspection, never an authority grant."""
from __future__ import annotations
from periphery.enterprise_offline_asymmetric_identity_fixture_v0 import inspect_offline_identity_claim_v0

def inspect_pinned_identity_claim_fixture_v0(*, registry, claim, public_key_pem,
                                               expected_organization, expected_actor,
                                               expected_issuer, expected_audience,
                                               expected_capability, expected_request_hash, now):
    def block(reason, crypto=False):
        return {"status":"BLOCK","reason":reason,"cryptographic_fixture_valid":crypto,
                "organization_authority_verified":False,"execution_authority":False,
                "egress_allowed":False}
    # Pin check is first, so even a genuine signature by a revoked key fails.
    try:
        status=registry.inspect_fixture(
            organization=expected_organization,issuer=expected_issuer,
            audience=expected_audience,public_key_pem=public_key_pem)
    except Exception:
        return block("C217_PIN_REGISTRY_UNAVAILABLE")
    if status!="PINNED_FIXTURE_ONLY_NO_ORGANIZATION_AUTHORITY":
        return block("C217_PIN_REJECTED:"+status)
    verified=inspect_offline_identity_claim_v0(
        claim=claim,pinned_public_key_pem=public_key_pem,
        expected_organization=expected_organization,expected_actor=expected_actor,
        expected_issuer=expected_issuer,expected_audience=expected_audience,
        expected_capability=expected_capability,expected_request_hash=expected_request_hash,
        now=now)
    if not verified.get("cryptographic_fixture_valid"):
        return block("C217_CLAIM_REJECTED:"+str(verified.get("reason")))
    return block("C217_ORGANIZATION_AUTHORITY_UNATTESTED",crypto=True)
