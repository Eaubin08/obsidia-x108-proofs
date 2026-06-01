# Security Surface - Obsidia X-108

> Sources: `SECURITY.md`, `docs/architecture/F76A_API_SECURITY_MINIMAL.md`, `docs/architecture/F76B_PROD_SECURITY_COMPLETE.md`
> Date: 2026-05-30 | F76 score: 10/10

## Scope of this repository

This repository contains only the public verification perimeter of Obsidia X-108:
- Formal specifications (Lean 4, TLA+)
- Verification scripts (Merkle, decisions)
- Input scenario examples
- API layer with sovereignty enforcement

**This repository does not contain the proprietary production engine.** Vulnerabilities in the proprietary engine must be reported via the private channel below.

## Reporting a vulnerability

If you discover a vulnerability in the scripts or API of this repository:
1. Do NOT open a public issue.
2. Email: **security@obsidia.io**
3. Include: description, reproduction steps, potential impact.

Response commitment: 72 hours.

For a deep technical audit of the production engine (under NDA):
- Email: **contact@obsidia.io**
- Subject: "Demande d'audit NDA - [Your organisation]"

---

## API security posture (F76 - 10/10 PASS)

### CORS (F76a - RESOLVED)

| Item | Status |
|---|---|
| Wildcard `allow_origins=["*"]` | REMOVED - replaced with env-based list |
| `ALLOWED_ORIGINS` env var | Comma-separated, dev default: localhost:3000, 8000, 127.0.0.1:8000 |
| Production | Set `ALLOWED_ORIGINS=https://your-domain.com` in `.env` |

### Documentation exposure (F76a - RESOLVED)

| `APP_ENV` | `/docs` | `/redoc` | `/openapi.json` |
|---|---|---|---|
| `dev` (default) | exposed | exposed | exposed |
| `prod` | `None` | `None` | `None` |

### Health endpoints (F76a - RESOLVED)

```
GET /api/health    -> {"status":"ok","decision_authority":"KX108_ONLY","readonly":true,"emits_act":false}
GET /api/readiness -> {"status":"ready","mode":"READONLY_READY","decision_authority":"KX108_ONLY"}
```

Both are public - no authentication required.

### Rate limiting (F76b - RESOLVED)

| Condition | Behaviour |
|---|---|
| `APP_ENV=dev` | Middleware no-op (dev pass-through) |
| `OBSIDIA_RATE_LIMIT_ENABLED=false` | no-op |
| `OBSIDIA_RATE_LIMIT_ENABLED=true` or `APP_ENV=prod` | 60 req/min per IP (default) |
| 429 response | `{"error":"rate_limit_exceeded","decision_authority":"KX108_ONLY","emits_act":false}` |

Exempt paths: `/api/health`, `/api/readiness`, `/api/status`, `/`.

Zero external dependencies - built on `starlette.BaseHTTPMiddleware`.

### Authentication (F76b - RESOLVED)

| Condition | Behaviour |
|---|---|
| `APP_ENV=dev` | Pass-through - no key check |
| `OBSIDIA_AUTH_ENABLED=false` | Pass-through |
| `OBSIDIA_AUTH_ENABLED=true` + `OBSIDIA_API_KEY=""` | 503 AUTH_MISCONFIGURED - no silent bypass |
| `APP_ENV=prod` + `OBSIDIA_API_KEY=""` | 503 AUTH_MISCONFIGURED |
| Auth enabled + wrong key | 401 INVALID_API_KEY |
| Auth enabled + correct key | pass |

Protected endpoint: `POST /api/brody/chat`.
All 401/503 responses carry `decision_authority=KX108_ONLY`, `emits_act=False`.

### Docker (F76a - RESOLVED)

`Dockerfile` present - `python:3.12-slim`. Build validated locally EXIT=0.

`docker-compose.yml` requires `OBSIDIA_API_KEY` explicitly:
```
OBSIDIA_API_KEY: ${OBSIDIA_API_KEY:?OBSIDIA_API_KEY is required in production}
```

### Hardcoded secrets

No hardcoded credentials found in `apps/`. All secrets via environment variables.

---

## What is NOT covered (deferred)

| Item | Status | Priority |
|---|---|---|
| Auth on `POST /api/x108/*` | DEFERRED - F76c | P1 - requires route analysis first |
| Redis-backed rate limit (multi-process) | DEFERRED | P2 - if horizontal scaling required |
| Structured access logs | PARTIAL | P2 - audit middleware present |
| Nginx reverse proxy | DEFERRED | Infra-level - out of repo scope |
| HTTPS/TLS | INFRA | Handled at reverse proxy / cloud level |

---

## Sovereignty invariants (no-ACT, no-write)

These are enforced at the code layer, not the network layer:

| Invariant | Enforcement |
|---|---|
| No ACT emitted | `emits_act=False` in `_CORE_BOUNDARY` (output_envelope.py) |
| No memory write | `memory_write=False` in `_SOVEREIGNTY_PROTECTED` (safe_response.py) |
| No Graphiti write | `graphiti_write=False` in both layers |
| No Neo4j write | `neo4j_write=False` in `_SOVEREIGNTY_PROTECTED` |
| No kernel mutation | `kernel_mutation=False` in `_SOVEREIGNTY_PROTECTED` |

These invariants are validated by the full API suite: **1973 PASS, 0 failed** (2026-05-30, 8566.23s / 2:22:46).

---

_Obsidia X-108 Security Surface | 2026-05-30 | KX108_ONLY | No commit / No push_

