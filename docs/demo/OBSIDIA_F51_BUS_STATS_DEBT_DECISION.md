# F51 — Bus Stats Debt Decision

**Artifact:** `OBSIDIA_F51_BUS_STATS_DEBT_DECISION`  
**Palier:** F51  
**Date:** 2026-05-29  
**Classification:** ROUTE_MISSING_CONFIRMED  

---

## The Debt

`GET /bus/stats` and `GET /bus/bridge` return **404**. Tests exist for both. The `output_envelope.py` module is ready. The route handlers were never implemented.

This is pre-V1 planned work (introduced 2026-05-26 in `a5f21c6`), not a regression.

---

## Impact on V1

**None.** Brody V1 routes (F33/F35/F36/F38, root, demo, operator, workbench) are unaffected. 103/103 baseline passes. Sovereignty and sanitizer contracts intact.

---

## Decision Required for F52

Choose one:

### Option A — Implement `/bus/stats` and `/bus/bridge`

- Create `apps/obsidia_api/routes/bus.py`
- Wire `GET /bus/stats` + `GET /bus/bridge` using `build_output_envelope()`
- Add `include_router()` in `main.py`
- All test infrastructure already exists and correct
- Risk: LOW (additive only, no existing code touched)
- Palier: `F52_BUS_STATS_ROUTE_CONTRACT_PATCH`

### Option B — Retire the orphan tests

- Mark `test_output_envelope_bus_stats.py` and `test_output_envelope_bus_bridge.py` as skipped or remove them
- If `/bus/stats` is not a V1 feature, remove the noise
- Risk: NONE (no runtime changes)
- Palier: `F52_BUS_STATS_TEST_RETIRE`

---

## No action taken in F51

```
PATCH=NO
COMMIT=NO
TAG=NO
PUSH=NO
```

Decision belongs to the user.

---

*F51 · DOCS ONLY · KX108_ONLY · 2026-05-29*
