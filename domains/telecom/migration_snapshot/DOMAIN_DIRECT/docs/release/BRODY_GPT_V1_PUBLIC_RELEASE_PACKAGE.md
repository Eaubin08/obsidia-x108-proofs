# Brody GPT V1 — Public Release Package

**Canonical name:** `BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME`  
**Version:** V1.0.0-RC-CLOSED  
**Sealed at:** HEAD `b67b2c3` · 2026-05-29  
**Audit chain closed at:** HEAD `378867f` · F48 · 2026-05-29  
**Status:** SEALED · LIVE-CHECKED · CANON-AUDITED · OBSERVATION-TESTED · HARDENED · RELEASE-READINESS-CHECKED  
**Public release gate:** LIFTED (F48)

---

## What This Package Is

This package documents Brody GPT V1 — the first closed, auditable version of the Brody advisory runtime component of the Obsidia X-108 governance system.

It is a **read-only advisory AI component**. It does not decide. It does not execute. It does not mutate state.

This package contains:
- Public release overview (this file)
- Demo commands guide (`BRODY_GPT_V1_DEMO_COMMANDS.md`)
- Proof chain index F42→F48 (`BRODY_GPT_V1_PROOF_INDEX_F42_F48.md`)
- Explicit limitations (`BRODY_GPT_V1_LIMITATIONS_AND_BOUNDARIES.md`)

---

## What Brody GPT V1 Does

Brody is the advisory AI layer of Obsidia X-108. It:

- Reads the runtime context of 7 governance surfaces
- Aggregates their state into a structured advisory packet
- Produces context-only responses across 4 domains (bank, gps_defense_aviation, trading, unknown_refusal)
- Exposes 7 read-only API routes
- Keeps the decision authority boundary visible at every output

**Brody does not decide. `KX108_ONLY` is the decision authority.**

This constraint is enforced simultaneously at three independent layers:

| Layer | Mechanism |
|-------|-----------|
| Module | Every function returns a 15-flag `BOUNDARY` dict — `can_decide=false`, `emits_act=false`, `emits_verdict=false`, etc. |
| Route | Every FastAPI endpoint wraps output through `safe_backend_response()` which re-applies sovereignty flags unconditionally after merge (F47.1) |
| Response | Word-boundary regex scan of `controlled_response.text` and `response`/`response_text` fields removes forbidden decision tokens before output (F47.2) |

---

## What Brody GPT V1 Does NOT Do

| Claim | Status |
|-------|--------|
| Decide anything | NO — `KX108_ONLY` decides |
| Execute actions | NO — `emits_act=false` at every layer |
| Emit verdicts | NO — `emits_verdict=false` at every layer |
| Mutate the kernel | NO — `kernel_mutation=false` |
| Mutate X108 | NO — `x108_mutation=false` |
| Write to Neo4j | NO — `neo4j_write=false` |
| Write to memory | NO — `memory_write=false` |
| Connect to live KX108 kernel | NO — kernel is declared authority, not instantiated |
| Production-ready deployment | NOT CLAIMED |
| Formal Lean proof | NOT CLAIMED — runtime smoke + unit tests only |
| Cloud-ready | NOT CLAIMED |
| Adversarial-hardened | NOT CLAIMED — not red-teamed |
| Load-tested | NOT CLAIMED — no load testing performed |

---

## API Routes (7 — all READY_READONLY)

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/api/periphery/brody-runtime/f33/integration-packet` | 7-surface runtime integration packet |
| `GET`  | `/api/periphery/operator/runtime-panel` | Operator panel (JSON) |
| `GET`  | `/api/periphery/operator/runtime-panel.html` | Operator panel (HTML) |
| `GET`  | `/api/periphery/demo/runtime-readiness` | Runtime readiness |
| `GET`  | `/api/periphery/workbench/runtime-connector` | Workbench connector |
| `POST` | `/api/periphery/brody-runtime/f36/user-scenario` | End-to-end user scenario |
| `POST` | `/api/periphery/brody-runtime/f38/multi-domain-scenarios` | 4-domain scenario packet |

---

## Verified Metrics (V1)

| Metric | Value |
|--------|-------|
| Unit tests | **103/103 PASS** |
| Smoke checks (cumulative) | **474** |
| Live-server proofs | **3** (F34B / F36B / F38) |
| API routes | **7 READY_READONLY** |
| Git tags (F24→F48) | **17 present** |
| Forbidden tokens in user-facing output | **0** |
| Mutation flags triggered | **0** |
| Sovereignty flags enforced | **13/13** (F47.1) |
| F47 sanitizer checks | **42/42** (F47.2) |

---

## Boundary Contract

Every response from every route carries this verifiable contract:

| Flag | Value |
|------|-------|
| `decision_authority` | `KX108_ONLY` |
| `allowed_to_decide` | `false` |
| `can_decide` | `false` |
| `emits_act` | `false` |
| `emits_verdict` | `false` |
| `kernel_mutation` | `false` |
| `x108_mutation` | `false` |
| `neo4j_write` | `false` |
| `memory_write` | `false` |
| `brody_decision` | `false` |

---

## Proof Chain

| Palier | Description | Status |
|--------|-------------|--------|
| F42 | Final release seal | SEALED |
| F43 | Live server / port matrix audit | LIVE-CHECKED |
| F44 | Canonical integrity audit (7 findings) | CANON-AUDITED |
| F45 | Terminal observation battery | OBSERVATION-TESTED |
| F46 | Hardening plan | PLANNED |
| F47 | Hardening patch sequence | HARDENED |
| F48 | Post-hardening release readiness check | READINESS-CHECKED |

Full index with SHA256: `docs/release/BRODY_GPT_V1_PROOF_INDEX_F42_F48.md`

---

## Quick Verification

```powershell
cd "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"

# Baseline tests
python -m pytest tests\api\ -q
# Expected: 103 passed

# Sovereignty enforcement
python scripts\_f47_test_sovereignty.py
# Expected: F47_1_PROTECTED_RESPONSE_ENVELOPE=PASS

# Forbidden token sanitizer
python scripts\_f47_test_sanitizer.py
# Expected: F47_2_CONTROLLED_RESPONSE_SANITIZER=PASS
```

Full demo commands: `docs/release/BRODY_GPT_V1_DEMO_COMMANDS.md`

---

## Known Limitations

See `docs/release/BRODY_GPT_V1_LIMITATIONS_AND_BOUNDARIES.md` for the complete limitations document.

Summary:
- Formal Lean proof: not available
- KX108 kernel: declared authority only — not instantiated
- Adversarial testing: not performed
- Load testing: not performed
- Full Graphiti binding: outside V1 scope

---

## Repository

```
Canonical name:  BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME
V1 seal tag:     BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME_FINAL_20260529
Sealed HEAD:     b67b2c3
Audit HEAD:      378867f
V1 tag range:    F24 → F48
```

---

*Brody GPT V1 · READONLY · KX108_ONLY · Public Release Package · 2026-05-29*
