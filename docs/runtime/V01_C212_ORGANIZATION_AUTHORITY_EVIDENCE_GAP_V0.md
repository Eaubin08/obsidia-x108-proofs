# C2.12 — Organizational authority evidence: missing verifier boundary

Status: DRAFT / DENY-ONLY / NO EGRESS.

Parent C2.11 `c78aed4065bd7a4c8fd51f76eeb6752b74a562d6`, targeted CI #37728155886 SUCCESS.

Source audit:
- `periphery/enterprise_org_stack_lifecycle_v0.py` explicitly records `organization_authority_verified=False` and does not grant provider calls.
- C2.10 issuer registry is fixture-enrolled, not independently authenticated.
- C2.11 combines fixture enrollment, local revocation and MAC test signature, and always BLOCKs.
- No actual organization identity service or authenticated approver enrollment was found attached to this enterprise proof chain.

C2.12 introduces a non-authorizing evidence contract linking organization, actor, issuer, requested capability and references to identity, delegation and organization-control proof. Even when every reference string is present, it returns `BLOCK:C212_INDEPENDENT_ORGANIZATION_VERIFIER_NOT_BOUND`, because names/URLs are not independent identity or corporate authority attestation.

Tests refuse unknown evidence, cross-org and capability drift, incomplete evidence, and fully-populated forged references.

For production, must independently establish verified organization/tenant ownership, authorized actor consent, delegation scope, issuer public-key enrollment + key rotation, trustworthy revocation timestamp and audit; then bind to exact KX108 world-action decision and ticket at the connector boundary. Not implemented, do not treat the fixture reference fields as authorization. No main merge, kernel/Monde mutation, real connector calls.
