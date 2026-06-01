# Compliance Checklist - Obsidia X-108

> Source: `REPRODUCIBILITY_CHECKLIST.md` | Date: 2026-05-30

This checklist covers the conditions required to reproduce the Obsidia X-108 verification environment from a clean clone.

## Environment configuration

| Item | Status |
|---|---|
| `Dockerfile` present | YES - `python:3.12-slim`, F76a |
| `docker-compose.yml` present | YES - with healthcheck and auth guard, F76b |
| `.env.example` present | YES - see [ENV_REFERENCE.md](ENV_REFERENCE.md) |
| `.python-version` | 3.12 (aligns with CI periphery workflow) |
| `requirements.txt` | Present - includes `fastapi`, `uvicorn`, `pydantic` as of F74 |

## Python dependencies

```bash
pip install -r requirements.txt
# Includes: pytest, fastapi, uvicorn[standard], pydantic, pyopenssl, cryptography, requests, pyyaml
```

## Sigma test suite (baseline)

```bash
python -m pytest tests/sigma/ -q --tb=short
```

Expected: all Sigma tests PASS. Full suite includes 650+ KX108_ONLY checks, 195 readonly checks, 85 bus sovereignty checks.

## API test suite

```bash
python -m pytest tests/api/ -q --tb=short
```

Expected: PASS. Full tests/api: **1973 PASS, 0 failed** (2026-05-30, 8566.23s / 2:22:46). Targeted non-regression: **1203 PASS, 0 failed** (2026-05-30, 196.49s).

## Docker build (F76a)

```bash
docker build -t obsidia-x108-api:f76a .
```

Expected: EXIT=0. Build validated locally in session (2026-05-30, ~27s).

## No-fake guarantees

The following guarantees are verified by test and code, not placeholders:

| Guarantee | Enforced by |
|---|---|
| RFC3161 `verified=true` only if openssl passes | `traces/rfc3161/verify.json` |
| TLA status = `"incomplete"` if TLC absent | TLA specs only - no fake `"verified"` |
| Sigma returns real metrics (no mock) | test suite 650+ PASS |
| Audit log append-only | `traces/audit/audit.jsonl` |
| X108 kernel never modified | readonly architecture |
| No placeholder in artefacts | `readonly=True`, `emits_act=False` enforced |

## Security checks

| Item | Status |
|---|---|
| No secrets hardcoded in `apps/` | VERIFIED - grep found no credentials |
| Secrets via env vars only | YES - `.env.example` template |
| `OBSIDIA_API_KEY` required in prod docker-compose | YES - `${OBSIDIA_API_KEY:?...}` guard |
| CORS wildcard removed | YES - F76a patch |
| `APP_ENV=prod` disables `/docs` | YES - F76a patch |

## Reproducibility boundary

A clean clone can:
- Run all `tests/sigma/` tests (PASS)
- Run all `tests/api/` tests (PASS)
- Build the Docker image

A clean clone cannot (without additional setup):
- Connect to Graphiti (requires `graphiti-lab/.env.graphiti.local` - external)
- Connect to Neo4j (requires `NEO4J_URI` + `NEO4J_PASSWORD` - external)
- Verify RFC3161 timestamps against a live TSA server (requires network)

These limitations are declared in [KNOWN_LIMITS.md](KNOWN_LIMITS.md).

---

_Obsidia X-108 Compliance Checklist | 2026-05-30 | KX108_ONLY | No commit / No push_

