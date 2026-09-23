# LIVE_CONNECTORS_PHASE7E_DECISION_GATEWAY_AUDIT_20260527

Status: DIAGNOSTIC_ONLY

## Route checks
- /health: OK code=200 length=15 content_type=application/json
- /openapi.json: OK code=200 length=3152 content_type=application/json
- /docs: OK code=200 length=1023 content_type=text/html; charset=utf-8
- /v1/decision: FAIL code=405 length= content_type=
- /auth/token: FAIL code=405 length= content_type=
- /v1/audit/chain: FAIL code=500 length= content_type=
- /v1/audit: FAIL code=404 length= content_type=
- /audit/chain: FAIL code=404 length= content_type=
- /api/audit/chain: FAIL code=404 length= content_type=

## OpenAPI relevant routes
- /auth/token
- /health
- /v1/audit/chain
- /v1/decision

## Boundary

- Decision Gateway is not Brody.
- Decision Gateway is not Graphiti.
- No connector is granted authority over X108.
- KX108_ONLY remains sole decision authority.

## Next

If /v1/audit/chain requires auth, Phase 7E-bis must test auth flow read-only.
If route is absent, mark old audit-chain check obsolete.