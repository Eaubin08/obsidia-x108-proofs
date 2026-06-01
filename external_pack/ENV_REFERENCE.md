# Environment Reference - Obsidia X-108

> Source: `.env.example` | Date: 2026-05-30
> IMPORTANT: No real secrets are included in this file. All values shown are template placeholders.

Copy `.env.example` to `.env` and fill in real values. Never commit `.env`.

```bash
cp .env.example .env
```

## API configuration

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `dev` | `dev` = docs exposed, no auth, no rate limit / `prod` = docs hidden, auth + rate limit active |
| `OBSIDIA_API_HOST` | `127.0.0.1` | Listen host for uvicorn |
| `OBSIDIA_API_PORT` | `8000` | Listen port for uvicorn |
| `OBSIDIA_API_BASE` | `http://127.0.0.1:8000` | Base URL used by test clients |

## CORS (F76a)

| Variable | Default | Description |
|---|---|---|
| `ALLOWED_ORIGINS` | `http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000` | Comma-separated list of allowed origins. Set to your production domain before any public exposure. |

## Graphiti / Neo4j (optional - readonly probe only)

| Variable | Default | Description |
|---|---|---|
| `GRAPHITI_V20_HTTP_BASE` | *(empty)* | Graphiti HTTP base URL. Leave empty for offline / local-index-only mode. |
| `NEO4J_URI` | *(empty)* | Neo4j bolt URI. Leave empty for degraded mode. |
| `NEO4J_USER` | *(empty)* | Neo4j username. |
| `NEO4J_PASSWORD` | *(empty)* | Neo4j password. **Never set a real value here - only in `.env` (not committed).** |

When empty: Brody operates in local-index-only mode. Graphiti probe returns graceful degradation. No error is raised.

Note: `graphiti-lab/.env.graphiti.local` is an external file not included in this repository. If Graphiti connectivity is required, create it manually outside the repo. See `docs/architecture/F74_F77_FINALIZATION_AUDIT.md` for details.

## Authentication and rate limiting (F76b)

| Variable | Default | Description |
|---|---|---|
| `OBSIDIA_AUTH_ENABLED` | `false` | `true` = API key required on `POST /api/brody/chat` in prod |
| `OBSIDIA_API_KEY` | *(empty)* | API key value. **Required if `OBSIDIA_AUTH_ENABLED=true` or `APP_ENV=prod`.** Setting empty with auth enabled -> 503 AUTH_MISCONFIGURED (no silent bypass). |
| `OBSIDIA_RATE_LIMIT_ENABLED` | `false` | `true` = 60 req/min per IP enforced |
| `RATE_LIMIT_RPM` | `60` | Requests per minute per IP |

## Security rules

- **Never commit `.env`** - `.gitignore` must include `.env`.
- **Never commit real values** for `NEO4J_PASSWORD`, `OBSIDIA_API_KEY`.
- `OBSIDIA_API_KEY` must be a strong random string in production (min 32 chars recommended).
- In docker-compose, `OBSIDIA_API_KEY` is required: the compose file will fail explicitly if empty.

## Environment behaviour matrix

| APP_ENV | `/docs` | Rate limit | Auth check |
|---|---|---|---|
| `dev` (default) | exposed | disabled | disabled |
| `development` | exposed | disabled | disabled |
| `prod` | disabled | active | active (if OBSIDIA_AUTH_ENABLED=true or APP_ENV=prod) |
| Any other value | disabled | active | active |

---

_Obsidia X-108 Environment Reference | 2026-05-30 | KX108_ONLY | No secrets included | No commit / No push_

