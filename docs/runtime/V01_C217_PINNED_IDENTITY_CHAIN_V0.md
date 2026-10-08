# V0.1 C2.17 — pinned Ed25519 identity claim simulation

Status: DRAFT / FAIL-CLOSED / NO PROVIDER EGRESS.

Parent C2.16 `f6421d7c8f3a83721889130626cfad0ec5436083`. C2.16 targeted CI runs 37730620740 and 37730621045 succeeded.

C2.17 composes existing C2.16 durable tenant/issuer/audience-scoped public-key pin and revocation fixture with C2.15 Ed25519 claim verifier. The pin is checked first so revocation blocks even a cryptographically valid signature after restart. Exact organization, actor, issuer, audience, capability, action hash and expiration are checked. Tests cover an unrevoked valid signature, revoked key after reload, wrong actor and cross-tenant scope.

**Safety:** fixture-enrolled public keys are not independently authenticated IdP trust roots. A verified signature is integrity of a test claim, not organizational ownership/delegation. The result is always BLOCK, including when the signature and pin match (`C217_ORGANIZATION_AUTHORITY_UNATTESTED`). No real OIDC/JWKS, issuer enrollment, nonces, live consent, KX108 redecision, SovereignTicket authority, provider dispatch or receipts. No main/kernel/Monde changes.
