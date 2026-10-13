"""C2.11 compose fixture issuer revocation with signed ticket/record fixture.

No organizational identity authentication, no KX108 invocation, no egress.
The final verdict is always BLOCK, even if all fixture checks pass.
"""
from __future__ import annotations
import hashlib
from periphery.enterprise_record_bound_ticket_fixture_v0 import verify_ticket_record_fixture_v0

def inspect_fixture_trust_chain_v0(*, organization, registry, issuer_ref,
                                   verifier_key, binding, record, ticket, now):
    def deny(reason):
        return {"status":"BLOCK","reason":reason,"egress_allowed":False,
                "execution_authority":False}
    if not isinstance(organization,str) or not organization:
        return deny("C211_ORGANIZATION_MISSING")
    if not isinstance(verifier_key,bytes) or len(verifier_key)<32:
        return deny("C211_VERIFIER_KEY_UNAVAILABLE")
    digest=hashlib.sha256(verifier_key).hexdigest()
    trust=registry.check_fixture(organization=organization,issuer=issuer_ref,key_digest=digest)
    if trust!="FIXTURE_ISSUER_MATCH_NO_ORGANIZATION_AUTHORITY":
        return deny(trust)
    ok,reason=verify_ticket_record_fixture_v0(
        binding,trusted_fixture_issuer=issuer_ref,verifier_key=verifier_key,
        record=record,ticket=ticket,now=now)
    if not ok:
        return deny("C211_BINDING_INVALID:"+str(reason))
    # Neither fixture enrollment nor shared-key MAC establishes actual
    # organizational consent, trusted issuer authority, KX108 origin or
    # transactional provider dispatch fencing.
    return deny("C211_ORGANIZATION_AUTHORITY_UNVERIFIED")
