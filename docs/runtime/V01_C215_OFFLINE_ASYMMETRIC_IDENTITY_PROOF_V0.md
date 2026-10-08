# V0.1 C2.15 — offline asymmetric identity proof fixture

Status: DRAFT / DENY ONLY / NO LIVE EXECUTION.

C2.14 targeted GitHub CI runs 37729971914 and 37729964842 were SUCCESS. The earlier C2.14 contract could represent issuer/audience/key fingerprint, but not verify a signature.

C2.15 adds isolated Ed25519 signature verification using `cryptography` over canonical organization, actor, issuer, audience, capability, request hash and expiry claims. All keys are **ephemeral test fixtures**. Matching cryptographic evidence produces `BLOCK:C215_OFFLINE_ISSUER_NOT_ORGANIZATION_ATTESTED` and marks only `cryptographic_fixture_valid=True`, never `organization_authority_verified=True`. Tests cover valid signature, tampered scope, wrong public key, expired claim and issuer mismatch.

This does **not** establish who controls an organization or authenticate a live identity provider. The public key is supplied by the caller and has not been independently enrolled; there is no production OIDC/JWKS chain, issuer trust root, revocation or replay checking, real SovereignTicket issuance, KX108 kernel invocation, connector dispatch, or provider receipt. No changes to main, kernel or Monde.
