# F52 — Bus/Bridge Quarantine

**Artifact:** `OBSIDIA_F52_BUS_BRIDGE_QUARANTINE_20260529_230000`  
**Palier:** F52  
**Parent:** F51_BUS_STATS_ROUTE_DEBT_AUDIT  
**Status:** PASS  
**Action:** QUARANTINE_ONLY  
**Date:** 2026-05-29  
**Head:** ad30a2e  
**Parent tag:** BRODY_F51_BUS_STATS_ROUTE_DEBT_AUDIT_PALIER_20260529  

---

## Purpose

F52 quarantines the orphan bus/bridge test files identified in F51 (`ROUTE_MISSING_CONFIRMED`). The quarantine prevents these future-contract tests from appearing as Brody V1 regressions, while fully preserving the bus/bridge architectural intent.

**F52 does NOT:**
- Delete tests
- Delete bus/bridge references
- Create routes
- Implement endpoints
- Modify runtime
- Collapse the meaning of bus/bridge into a simple stats endpoint

---

## Quarantine Applied

| File | Method | Tests affected |
|------|--------|---------------|
| `tests/api/test_output_envelope_bus_stats.py` | `pytestmark = pytest.mark.skip(...)` | 23 |
| `tests/api/test_output_envelope_bus_bridge.py` | `pytestmark = pytest.mark.skip(...)` | 23 |

**Total quarantined:** 46 tests  
**Tests deleted:** 0  
**Routes created:** 0  
**Runtime modified:** false  

### Skip reason (verbatim in both files)

```
F51_ROUTE_MISSING_CONFIRMED: bus/stats and bus/bridge are future contract surfaces.
Intended as connective interfaces for internal state, proof state, runtime state,
memory/context state, and external incoming signals.
Not implemented in Brody V1 runtime routes.
Quarantined by F52. Implementation: F53_BUS_BRIDGE_EXISTENTIAL_CONTRACT_PLAN.
```

---

## Bus/Bridge Architectural Intent — PRESERVED

**bus/bridge is NOT a dead test.** It is a planned connective surface for the entire project machinery.

The current test contract is premature relative to implementation — the architecture is correct but the routes do not exist yet. The concept remains fully active.

### Intended role of bus/bridge

bus/bridge is designed to become the connective interface able to answer for the existential state of the entire system:

| Dimension | What bus/bridge must expose |
|-----------|---------------------------|
| Internal runtime state | Process health, uvicorn status, port state |
| Output envelope state | Envelope V1 coverage across routes |
| Readiness state | Demo/runtime readiness across all surfaces |
| Proof state | F-palier chain integrity, freeze manifest status |
| Audit state | Last audit result, last test run summary |
| Route state | OpenAPI inventory, route health |
| Memory / Graphiti / Brody context state | Advisory context availability, no write |
| External incoming signals | What arrives from outside the project |
| Project-wide existential status | How the whole machinery answers at a given moment |

### Sovereignty contract (preserved for F53 implementation)

| Flag | Value |
|------|-------|
| `decision_authority` | `KX108_ONLY` |
| `brody_role` | `advisory_readonly` |
| `allowed_to_decide` | `false` |
| `emits_act` | `false` |
| `emits_verdict` | `false` |

bus/bridge exposes state — it does not decide. KX108_ONLY is the sole authority.

---

## Verification

| Check | Result |
|-------|--------|
| Quarantine result | **46 skipped, 0 failed, 0 errors** |
| Baseline after quarantine | **77/77 PASS** |
| F47.1 sovereignty unaffected | true |
| F47.2 sanitizer unaffected | true |
| F50 routes unaffected | true |
| Runtime unchanged | true |

---

## F52 Constraints

| Constraint | Status |
|------------|--------|
| No tests deleted | CONFIRMED |
| No routes created | CONFIRMED |
| No runtime modification | CONFIRMED |
| No kernel mutation | CONFIRMED |
| No Neo4j write | CONFIRMED |
| No commit | PENDING USER VALIDATION |
| No tag | PENDING USER VALIDATION |
| No push | PENDING USER VALIDATION |

---

## Next: F53_BUS_BRIDGE_EXISTENTIAL_CONTRACT_PLAN

F53 will define what bus/bridge must actually answer across the whole project machinery:

- What internal state it exposes
- What external signals it can ingest
- How it bridges Brody / Graphiti / runtime / proofs / audit
- How it preserves KX108_ONLY without becoming a decider
- How it exposes status without granting decision authority
- How it powers `/bus/stats` and `/bus/bridge` routes when implementation is ready

F53 produces the architectural contract — implementation follows in F54+.

---

## JSON Artifact

`docs/runtime/OBSIDIA_F52_BUS_BRIDGE_QUARANTINE_20260529_230000.json`  
SHA256: `A76F5BEE35B09D210E054290DAB95AD2241A7AC599E170FB15F00F4EE01C5EFA`

---

*F52 · QUARANTINE ONLY · PASS · KX108_ONLY · 2026-05-29*
