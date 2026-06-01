# Release Notes - F77 External Pack

> Date: 2026-05-30 | Authority: KX108_ONLY | Status: READY_FOR_REVIEW | No commit / No push / No cloud deployment

## Executive summary

Obsidia X-108 is a deterministic governance kernel with a single decision authority: **KX108_ONLY**. This pack documents the state of the system at milestone F77 after a complete audit and hardening cycle covering F74 (reproducibility), F75 (formal proofs), F76 (API security), and F77 (external pack).

**Full tests/api: 1973 PASS, 0 failed (2026-05-30, 8566.23s / 2:22:46). Targeted non-regression: 1203 PASS, 0 failed (2026-05-30, 196.49s).**

---

## Milestone summary

### F74 - Fresh Clone Reproducibility

**Status: PASS (local)**

| Item | Result |
|---|---|
| `requirements.txt` updated | YES - `fastapi`, `uvicorn[standard]`, `pydantic` added |
| `.python-version` created | YES - `3.12` (aligns with CI periphery workflow) |
| `.env.example` created | YES - all env vars documented |
| `QUICKSTART.md` created | YES - 5-command guide |
| `scripts/run_api.sh` created | YES - Linux equivalent of `.ps1` script |
| `requirements-dev.txt` created | YES - pytest, mypy, ruff, black |
| Fresh clone tests/sigma PASS | YES |
| Fresh clone tests/api PASS | YES |

**Reproducibility boundary:** Sigma + API tests pass on clean clone. Graphiti and Neo4j require external `.env` not included in repo.

### F75 - Lean Formal Proofs

**Status: PARTIAL - Noyau temporel LEAN_PROVEN**

| Layer | Status |
|---|---|
| X108 temporal kernel (5 theorems) | **LEAN_PROVEN** - `TemporalKernel.lean` |
| D1 determinism, E2 no-ACT threshold | **LEAN_PROVEN** - `Basic.lean` |
| Refinement never-blocks theorems | **LEAN_PROVEN** - `Refinement.lean` |
| Merkle immutability (strong) | **LEAN_PROVEN** - `Sensitivity.lean` |
| Seal immutability | **LEAN_PROVEN** - `Seal.lean` |
| Consensus fail-closed | **LEAN_PROVEN** - `Consensus.lean` |
| TemporalBridge properties | **LEAN_PROVEN** - `TemporalBridge.lean` |
| Sigma layer sovereignty | **PYTHON_TEST_ONLY** - FUTURE_FORMAL_TARGET |
| Bus bridge sovereignty | **PYTHON_TEST_ONLY** - FUTURE_FORMAL_TARGET |
| Brody no-ACT | **PYTHON_TEST_ONLY** - FUTURE_FORMAL_TARGET |
| TLA+ X108 temporal safety | **FORMAL_TLA** - spec present, TLC not re-run |
| P107 Lyapunov, P161 Calibration | **DOC_ONLY** - no proof, no tests |

See [LEAN_THEOREMS.md](LEAN_THEOREMS.md) for verbatim TemporalKernel.lean.
See [PROOF_INDEX.md](PROOF_INDEX.md) for the full proof landscape.

### F76a - API Security Minimal

**Status: PASS (6/10 -> resolved)**

| Item | Before F76a | After F76a |
|---|---|---|
| CORS wildcard `["*"]` | CRITICAL_BLOCKER | RESOLVED - env-based |
| Dockerfile | MISSING | CREATED - `python:3.12-slim` |
| `APP_ENV` guard for `/docs` | FAIL | PASS |
| `GET /api/health` | PASS | PASS (explicit) |
| `GET /api/readiness` | FAIL | PASS |
| Rate limiting | FAIL | Deferred -> F76b |
| Auth | FAIL | Deferred -> F76b |

### F76b - Prod Security Complete

**Status: PASS (10/10)**

| Item | Before F76b | After F76b |
|---|---|---|
| Rate limiting | FAIL | PASS - `_RateLimitMiddleware`, 60 req/min |
| Auth APIKey | FAIL | PASS - `require_api_key` on `/api/brody/chat` |
| `docker-compose.yml` | FAIL | PASS - with `OBSIDIA_API_KEY` guard |
| `ROLLBACK_PLAN.md` | FAIL | PASS - documented |

Regression validation: 1103 PASS (sigma + F63 + F65 + Brody) + 14 F76b targeted = 1117 PASS.

### F77 - External Pack

**Status: CREATED (this pack)**

| File | Status |
|---|---|
| `external_pack/README.md` | CREATED |
| `external_pack/SOVEREIGNTY_MANIFEST.md` | CREATED |
| `external_pack/PROOF_INDEX.md` | CREATED |
| `external_pack/LEAN_THEOREMS.md` | CREATED |
| `external_pack/COMPLIANCE_CHECKLIST.md` | CREATED |
| `external_pack/KNOWN_LIMITS.md` | CREATED |
| `external_pack/SECURITY_SURFACE.md` | CREATED |
| `external_pack/DEFERRED_PHASES.md` | CREATED |
| `external_pack/DOCKER_GUIDE.md` | CREATED |
| `external_pack/ENV_REFERENCE.md` | CREATED |
| `external_pack/RELEASE_NOTES_F77.md` | CREATED (this file) |

---

## Session patch summary (2026-05-30)

The following code patches were applied during this session before the external pack was created:

| File | Patch | Test coverage |
|---|---|---|
| `apps/obsidia_api/safe_response.py` | Added `graphiti_write: False` to `_SOVEREIGNTY_PROTECTED` | `test_writes_are_false` PASS |
| `apps/obsidia_api/brody_true_voice_adapter.py` | domain_raccord exclusion for `BRODY_MEMORY_RESPONSE_CHAIN_PASS` and `LOCAL_INDEX_FALLBACK_PARTIAL` with items | 4 voice_source tests PASS |
| `apps/obsidia_api/routes/blockchain.py` | Switched to `build_output_envelope` with compact/debug support | 9 fraud-check envelope tests PASS |

All patches: backup created before modification, no hardcoded values, no test bypasses.

---

## Test state at F77

| Suite | Count | Status | Date |
|---|---|---|---|
| Full tests/api | **1973** | **PASS, 0 failed** | 2026-05-30, 8566.23s (2:22:46) |
| Targeted non-regression | **1203** | **PASS, 0 failed** | 2026-05-30, 196.49s |
| Pipeline output envelope (7 fixes) | 7 | PASS | 2026-05-30 |
| Blockchain fraud-check envelope (9 fixes) | 9 | PASS | 2026-05-30 |
| Brody voice_source priority (4 fixes) | 4 | PASS | 2026-05-30 |
| F76b targeted (auth + rate-limit) | 14 | PASS | 2026-05-30 |
| F76a regression (sigma + F63 + F65) | 1097 | PASS | 2026-05-30 |

---

## Formal message for external reviewers

> Obsidia X-108 is a deterministic governance kernel with a single decision authority: **KX108_ONLY**. The temporal kernel is formally proven in Lean 4 (14 theorems). Operational constraints - no ACT, readonly, no mutation - are validated by the full API suite: **1973 PASS, 0 failed** (2026-05-30, 8566.23s / 2:22:46), covering F60-F76b. The system has reached milestone F77 (READY_FOR_REVIEW). API security hardening (CORS, rate limit, auth) is complete locally. Cloud deployment is not active. Deferred phases (Sigma/Bus/Graphiti formal proofs, auth on x108 routes, Redis rate limit) are explicitly declared in DEFERRED_PHASES.md.

---

## Absolute constraints active throughout

- `decision_authority=KX108_ONLY` - enforced at every output boundary
- `readonly=True` - no write operations in any API response
- `emits_act=False` - no ACT signal from any layer
- No commit / No tag / No push - all artefacts local only
- No cloud deployment - no Docker push
- No secrets in any committed file

---

_Obsidia X-108 Release Notes F77 | 2026-05-30 | KX108_ONLY | No commit / No push / No cloud deployment_

