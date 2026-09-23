# Obsidia Bus Layer — Readonly Release Index

**Release palier:** F59  
**Canonical tag:** BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME_FINAL_20260529  
**Date:** 2026-05-30  
**Sovereignty:** KX108_ONLY · readonly · advisory_only · no decision · no mutation · no storage  

---

## Release Summary

The Obsidia bus layer readonly surface is complete. Three routes are implemented, tested, audited, and frozen across paliers F51→F59.

| Route | Method | Status |
|-------|--------|--------|
| `/bus/stats` | GET | RELEASED — READONLY |
| `/bus/bridge` | GET | RELEASED — READONLY |
| `/bus/signal` | POST | RELEASED — READONLY |

**Total tests:** 103 / 103 PASS  
**F47 hardening:** PASS (sovereignty injection, token neutralization, nested scan)  

---

## Sovereignty Guarantees

These properties are unconditional on all three bus routes:

| Guarantee | Value |
|-----------|-------|
| Decision authority | `KX108_ONLY` — sole authority |
| Readonly | `true` — no side effects |
| Emits ACT | `false` — never |
| Emits VERDICT | `false` — never |
| Neo4j write | `false` — never |
| Kernel mutation | `false` — never |
| Memory write | `false` — never |
| Graphiti write | `false` — never |
| Allowed to decide | `false` — KX108 only |
| Advisory only | `true` — observations, not commands |

No input, regardless of content, can override these flags.

---

## Token Neutralization (F47.2)

All user-facing string fields in POST /bus/signal are sanitized. The tokens `ALLOW`, `HOLD`, `BLOCK`, `ACT`, `DECIDE`, `VERDICT` are replaced with `[REDACTED]` at word boundaries before any exposure. Neutralization is confirmed active by:

- Unit test battery (57 tests including dedicated token neutralization class)
- F47.2 validation script
- Live smoke (F56, F57)

---

## Storage Contract (Option A)

POST /bus/signal: **no persistent storage**.

- `last_signal` in GET /bus/bridge remains `"none"` after any number of POST /bus/signal calls
- `storage_performed=false` always
- `mutation_performed=false` always
- No Neo4j write, no Graphiti write, no memory write

Persistent storage (Options B/C) is deferred and requires explicit user validation before implementation.

---

## File Inventory

### Runtime source

| File | Purpose | SHA256 prefix |
|------|---------|---------------|
| `apps/obsidia_api/routes/bus.py` | FastAPI router — 3 bus routes | `02108D08...` |
| `apps/obsidia_api/bus/__init__.py` | Package init | `125C8BD0...` |
| `apps/obsidia_api/bus/state_aggregator.py` | State builders for stats + bridge | `DEAEE896...` |
| `apps/obsidia_api/bus/signal_model.py` | Pydantic model — SignalInput | `5B63AA60...` |
| `apps/obsidia_api/bus/signal_packager.py` | Observation packet builder | `286EB58C...` |

### Tests

| File | Route | Count |
|------|-------|-------|
| `tests/api/test_output_envelope_bus_stats.py` | GET /bus/stats | 23 |
| `tests/api/test_output_envelope_bus_bridge.py` | GET /bus/bridge | 23 |
| `tests/api/test_output_envelope_bus_signal.py` | POST /bus/signal | 57 |

### Freeze manifests

| Palier | Path |
|--------|------|
| F54 | `.runtime_freezes/F54_BUS_BRIDGE_MINIMAL_ROUTE_IMPLEMENTATION_20260529_213500/MANIFEST_SHA256.json` |
| F55 | `.runtime_freezes/F55_BUS_SIGNAL_INGRESS_PLAN_20260530_000000/MANIFEST_SHA256.json` |
| F56 | `.runtime_freezes/F56_BUS_SIGNAL_MINIMAL_READONLY_ROUTE_IMPLEMENTATION_20260530_000000/MANIFEST_SHA256.json` |
| F57 | `.runtime_freezes/F57_BUS_LAYER_POST_IMPLEMENTATION_AUDIT_20260530_000000/MANIFEST_SHA256.json` |
| F58 | `.runtime_freezes/F58_BUS_LAYER_STALE_ANNOTATION_RECONCILIATION_20260530_000000/MANIFEST_SHA256.json` |
| F59 | `.runtime_freezes/F59_BUS_LAYER_FINAL_FREEZE_INDEX_20260530_000000/MANIFEST_SHA256.json` |

---

## Known Limits

| Limit | Impact | Resolution |
|-------|--------|------------|
| `last_signal` always `"none"` | No signal history across calls | Option B/C — F60+ |
| Bus counters hardcoded to `0` | No real-time bus metrics | Real bus process — F60+ |
| Advisory collectors `not_collected` | No live Graphiti/Brody/Sigma state | Live connectors — F60+ |
| Pre-existing x108_status OperationID warning | None on bus | Separate x108 palier |

---

## What This Release Is NOT

| NOT | Reason |
|-----|--------|
| A decision endpoint | `routed_to_decision=false` always |
| A command interface | `interpreted_as_command=false` always |
| A write endpoint | All write flags `false` |
| A persistent store | Option A — no storage |
| An ACT emitter | `emits_act=false` always |
| A Brody decision router | `brody_decision=false` always |
| A kernel mutator | `kernel_mutation=false` always |

---

*F59 · Bus Layer Readonly Release Index · KX108_ONLY · 2026-05-30*
