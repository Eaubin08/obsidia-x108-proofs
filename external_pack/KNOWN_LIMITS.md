# Known Limits - Obsidia X-108

> Source: `docs/status/KNOWN_LIMITS.md` + F74/F76 audit | Date: 2026-05-30

This document explicitly declares the known limitations of the system. These are not hidden - they are a required part of honest external communication.

## Scope of this repository

- This repository is **not** the full proprietary production engine.
- This repository is **not** a full business product.
- This repository is **not** the final operator cockpit.
- P1 is a closed public proof / verification / execution perimeter.

It does not claim:
- Production rollout completeness
- Institutional integration completeness
- Complete business deployment completeness
- Full multi-world operationalization

## External dependencies

- TSA providers are third-party services - network reachability varies by environment.
- QA validates probe robustness, not ownership of external TSA servers.
- Graphiti connectivity requires an external `graphiti-lab/.env.graphiti.local` file not included in this repository.
- Neo4j connectivity requires external environment variables (`NEO4J_URI`, `NEO4J_PASSWORD`).

## Proof limitations (F75 audit)

| Property | Status | Note |
|---|---|---|
| X108 temporal kernel | LEAN_PROVEN | 5 theorems in TemporalKernel.lean |
| Sigma layer sovereignty | PYTHON_TEST_ONLY | Not formally proven in Lean |
| Bus bridge sovereignty | PYTHON_TEST_ONLY | Not formally proven in Lean |
| Brody no-ACT | PYTHON_TEST_ONLY | Not formally proven in Lean |
| `graphiti_write=False` | PYTHON_TEST_ONLY | Not formally proven in Lean |
| TLA+ X108 temporal safety | FORMAL_TLA - spec present | TLC not re-run this session |
| `P107 Lyapunov stability` | DOC_ONLY | No tests, no Lean proof |
| `P161 Calibration energetique` | DOC_ONLY | No tests, no Lean proof |

## Security limitations (F76 audit)

| Item | Status | Note |
|---|---|---|
| CORS wildcard | RESOLVED - F76a | `allow_origins=["*"]` removed |
| Dockerfile | RESOLVED - F76a | `python:3.12-slim` |
| `GET /health` | RESOLVED - F76a | `/api/health` responds |
| Rate limiting | RESOLVED - F76b | `_RateLimitMiddleware`, 60 req/min |
| Auth on `/api/brody/chat` | RESOLVED - F76b | `require_api_key` (prod only) |
| Auth on `POST /api/x108/*` | DEFERRED - F76c | Routes not yet analysed for protection |
| Redis-backed rate limit | DEFERRED - optional | Current: in-memory, single process |
| Reverse proxy (nginx) | DEFERRED | uvicorn exposed directly |
| HTTPS/TLS | INFRA - out of scope | Handled at reverse proxy level |
| Structured access logs | PARTIAL | Audit middleware present, not yet enriched |

## Reproducibility limitations (F74 audit)

| Item | Status |
|---|---|
| Fresh clone + pip install + tests/sigma PASS | YES |
| Fresh clone + pip install + tests/api PASS | YES |
| Docker build EXIT=0 | YES (F76a) |
| Starting API on clone propre | YES - requirements.txt updated (F74) |
| Graphiti mode (full memory chain) | Requires external `.env.graphiti.local` |
| TLC model checking on clone | Requires Java + tla2tools.jar |
| RFC3161 live verification | Requires network access to TSA |

## Deferred phases

See [DEFERRED_PHASES.md](DEFERRED_PHASES.md) for the full list of modules explicitly deferred.

---

_Obsidia X-108 Known Limits | 2026-05-30 | KX108_ONLY | No commit / No push_

