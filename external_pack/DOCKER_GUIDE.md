# Docker Guide - Obsidia X-108

> Sources: `Dockerfile`, `docker-compose.yml` | Date: 2026-05-30 | F76a validated

## Prerequisites

- Docker 24+ (or Docker Desktop)
- `.env` file created from `.env.example` (see [ENV_REFERENCE.md](ENV_REFERENCE.md))
- `OBSIDIA_API_KEY` set in `.env` (required for production mode)

## Dockerfile (verbatim)

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Runtime configuration
ENV APP_ENV=prod
ENV OBSIDIA_API_HOST=0.0.0.0
ENV OBSIDIA_API_PORT=8000

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "apps.obsidia_api.main:app", \
     "--host", "0.0.0.0", "--port", "8000"]
```

## Build

```bash
docker build -t obsidia-x108-api:latest .
```

Expected: EXIT=0. Build validated locally 2026-05-30 (~27s).

The default `APP_ENV=prod` in the Dockerfile means:
- `/docs`, `/redoc`, `/openapi.json` are disabled
- Rate limiting is active (60 req/min per IP)
- Auth is enforced on `POST /api/brody/chat` if `OBSIDIA_API_KEY` is set

## docker-compose.yml (verbatim)

```yaml
version: "3.9"

services:
  obsidia-api:
    build: .
    image: obsidia-x108-api:latest
    ports:
      - "${OBSIDIA_API_PORT:-8000}:8000"
    environment:
      APP_ENV: ${APP_ENV:-prod}
      ALLOWED_ORIGINS: ${ALLOWED_ORIGINS:-http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000}
      OBSIDIA_AUTH_ENABLED: ${OBSIDIA_AUTH_ENABLED:-true}
      OBSIDIA_API_KEY: ${OBSIDIA_API_KEY:?OBSIDIA_API_KEY is required in production. Set it in .env}
      OBSIDIA_RATE_LIMIT_ENABLED: ${OBSIDIA_RATE_LIMIT_ENABLED:-true}
      RATE_LIMIT_RPM: ${RATE_LIMIT_RPM:-60}
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')\""]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

## Run with docker-compose

```bash
# 1. Create .env from template
cp .env.example .env
# Edit .env - set OBSIDIA_API_KEY

# 2. Start
docker compose up --build

# 3. Verify
curl http://localhost:8000/api/health
# Expected: {"status":"ok","decision_authority":"KX108_ONLY","readonly":true,"emits_act":false}
```

Note: `docker-compose` will fail explicitly if `OBSIDIA_API_KEY` is empty:
```
OBSIDIA_API_KEY is required in production. Set it in .env
```
This is intentional - no silent bypass in production.

## Run without authentication (development)

```bash
OBSIDIA_AUTH_ENABLED=false \
OBSIDIA_API_KEY="" \
APP_ENV=dev \
docker compose up --build
```

## Verify the image

```bash
# Health check
curl http://localhost:8000/api/health

# Readiness check
curl http://localhost:8000/api/readiness

# Confirm sovereignty invariants in response
curl http://localhost:8000/api/health | python -m json.tool
# Expect: decision_authority=KX108_ONLY, readonly=true, emits_act=false
```

## Security notes

- `COPY . .` copies the full source - ensure `.env` is in `.dockerignore` before building.
- `.dockerignore` is present in the repository.
- Neo4j and Graphiti are optional - the API runs in degraded mode if not connected.
- No cloud deployment is active. Docker is for local and internal validation.

---

_Obsidia X-108 Docker Guide | 2026-05-30 | KX108_ONLY | No commit / No push_

