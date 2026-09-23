# LIVE_CONNECTORS_PHASE7E_BIS_DECISION_GATEWAY_OPENAPI_20260527

Status: READ_ONLY_OPENAPI_INSPECTION_COMPLETE

## Scope

Inspect Decision Gateway 8001 OpenAPI and allowed methods after Phase 7E found /v1/audit/chain returning HTTP 500.

No POST was executed in this phase.

## Routes inspected

- /health: methods=get
- /auth/token: methods=post
- /v1/decision: methods=post
- /v1/audit/chain: methods=get

## OpenAPI details

### /health

- method = GET
- operation_id = health_health_get
- response = 200

### /auth/token

- method = POST
- operation_id = token_auth_token_post
- request_body = application/x-www-form-urlencoded
- responses = 200, 422

### /v1/decision

- method = POST
- operation_id = decision_v1_decision_post
- request_body = application/json object
- responses = 200, 422

### /v1/audit/chain

- method = GET
- operation_id = audit_chain_v1_audit_chain_get
- responses = 200, 422

## OPTIONS checks

- /health: FAIL code=405 allow=GET
- /auth/token: FAIL code=405 allow=POST
- /v1/decision: FAIL code=405 allow=POST
- /v1/audit/chain: FAIL code=405 allow=GET

## Interpretation

/v1/audit/chain is a real GET route.

The previous HTTP 500 is not caused by using the wrong HTTP method.

The likely cause is internal handler/runtime state, such as missing audit chain storage, missing file path, missing dependency, or unhandled empty chain.

## Boundary

- No POST executed.
- No decision request sent.
- No token request sent.
- No mutation.
- Decision Gateway remains outside Brody/Graphiti runtime flow.
- KX108_ONLY remains sole decision authority.

## Next

Phase 7E-ter should inspect the Decision Gateway source code and logs for the audit_chain_v1_audit_chain_get handler.

No patch before locating the exact 500 cause.