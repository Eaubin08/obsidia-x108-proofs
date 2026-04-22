# OpenAPI contract (canonical)

This file is the public, stable contract:
- `docs/openapi.yaml`

It defines:
- `POST /v1/decision`
- `GET /v1/replay/{trace_id}`
- `GET /v1/audit/chain`
- `POST /auth/token`

Decisions are strictly: BLOCK | HOLD | ACT.
