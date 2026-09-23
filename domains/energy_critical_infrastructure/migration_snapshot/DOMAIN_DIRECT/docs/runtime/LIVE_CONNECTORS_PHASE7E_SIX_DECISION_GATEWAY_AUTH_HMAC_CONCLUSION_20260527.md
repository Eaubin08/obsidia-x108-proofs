# LIVE_CONNECTORS_PHASE7E_SIX_DECISION_GATEWAY_AUTH_HMAC_CONCLUSION_20260527

Status: PASS_DIAGNOSTIC_CONCLUSION

## Scope

Conclude Decision Gateway 8001 audit-chain diagnostics after OpenAPI, handler, Docker, and auth/HMAC inspection.

## Confirmed

- 8001 is Docker container deploy-obsidia_api-1.
- 8001 maps host 8001 to container 8000.
- Service is Decision Gateway, not Brody.
- /health is public and returns OK.
- /v1/audit/chain is a real GET route.
- /v1/audit/chain returns HTTP 500 without auth/HMAC headers.
- /v1/audit/chain also returns HTTP 500 with dummy X-API-Key.
- Docker environment enables API key auth.
- Docker environment enables HMAC protection.
- Docker environment uses OBSIDIA_STORE_DIR=/store.
- Docker container contains audit chain/log material.

## Interpretation

The audit-chain endpoint failure is not caused by:

- missing route
- wrong HTTP method
- Brody
- Graphiti
- Workbench
- missing audit.chain alone

The likely cause is auth/HMAC handling before the route handler.

The endpoint should ideally return 401/403 when auth/HMAC is missing or invalid, instead of HTTP 500.

## Boundary

- No POST executed.
- No token request sent.
- No decision request sent.
- No mutation.
- No secret committed.
- KX108_ONLY remains sole decision authority.
- Decision Gateway remains outside Brody/Graphiti runtime flow.

## Decision

Phase 7E is closed as diagnostic.

Decision Gateway 8001 is alive but protected.

The current Brody live path does not depend on /v1/audit/chain.

Critical flow remains valid:

Workbench 5173 -> Brody API 8012 -> Graphiti V20 readonly proxy -> ObsidiaShell 8011.

## Next options

Option A — leave Decision Gateway as protected/out-of-scope for current Brody flow.

Option B — later patch Decision Gateway middleware so missing/invalid HMAC returns 401/403 instead of 500.

Option C — later add a signed read-only audit-chain smoke test using real HMAC headers, without sending /v1/decision.