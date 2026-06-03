# runtime_wiring/ — P8B Dry-Run Skeleton

**Status:** DRY_RUN_ONLY / STDLIB_ONLY / NO_RUNTIME_EXECUTION  
**Branche:** p8-runtime-dryrun-wiring  
**Phase:** P8B

## Purpose

Demonstrate the P8B wiring pipeline in complete isolation:

1. Load and verify the 8 `runtime_contracts/` files
2. Build 4 `ContextPacket` (dry-run) via source adapters (cognitive, rssi_rgpd, atlas, compliance)
3. Route through `dry_run_packet_router` → `x108_admission_stub`
4. Produce `DecisionTicketDryRun` + `OS3EvidenceTicketDryRun`
5. Print structured JSON output

## Run

```bash
python runtime_wiring/p8b_demo.py
```

Expected decisions:
- Scenario A (no critical action): `ALLOW_CONTEXT_ONLY`
- Scenario B (critical action requested): `HOLD`

## Constraints (absolute)

- **ISOLATED**: imports NOTHING from `apps/`, `periphery/`, `connectors/`, `sigma/`, `_source_packs/`
- **STDLIB ONLY**: `dataclasses`, `hashlib`, `json`, `pathlib`, `datetime`, `typing`, `sys`
- **NO file writes** — demo is pure stdout
- **NO network** — all data is local
- **NO real DecisionTicket** — `DecisionTicketDryRun` only
- **NO real OS3 proof** — all hash/seal fields are `NOT_COMPUTED`
- **Decisions**: `ALLOW_CONTEXT_ONLY` / `HOLD` / `BLOCK` — never `ACT`

## Module Map

| File | Role |
|------|------|
| `packet_types.py` | 5 dataclasses: ContextPacket, PeripheralSignalPacket, IntentEnvelope, DecisionTicketDryRun, OS3EvidenceTicketDryRun |
| `contracts_loader.py` | Reads and verifies 8 contract files from `runtime_contracts/` (fail-closed) |
| `source_adapters.py` | 4 adapter functions → ContextPacket with forced boundaries |
| `x108_admission_stub.py` | Deterministic stub: BLOCK > HOLD > ALLOW_CONTEXT_ONLY |
| `os3_evidence_stub.py` | Honest dry-run OS3 evidence (all statuses NOT_COMPUTED) |
| `dry_run_packet_router.py` | Validates boundaries, builds IntentEnvelope, routes to stub |
| `p8b_demo.py` | Standalone demo script (two scenarios) |
| `reports/` | Documentation and reports |

## Source Boundaries

| Source | Boundary | Label |
|--------|----------|-------|
| Cognitive | `COGNITIVE_REINTEGRATION_ADVISORY_ONLY` | `COGNITIVE_ADVISORY_FUTURE` |
| RSSI/RGPD | `RSSI_EVIDENCE_ONLY\|RGPD_COMPLIANCE_SCOPE_GUARD` | `RSSI_EVIDENCE_ONLY_FUTURE`, `RGPD_SCOPE_GUARD_FUTURE` |
| Atlas | `ATLAS_READONLY_ADVISORY_ONLY` | `ATLAS_READONLY_FUTURE` |
| Compliance | `RGPD_COMPLIANCE_SCOPE_GUARD\|RSSI_EVIDENCE_ONLY` | `RGPD_SCOPE_GUARD_FUTURE`, `RSSI_EVIDENCE_ONLY_FUTURE` |

## What this is NOT

- Not a real X108 gateway
- Not connected to `periphery/`, `apps/`, or any live system
- Not a proof — all hash fields are `NOT_COMPUTED_DRY_RUN`
- Not a decision — `ALLOW_CONTEXT_ONLY` ≠ real `ALLOW`
- Not a package — no `pyproject.toml`, no pip install

## Next step

**P8C** — dry-run tests (`tests/test_runtime_wiring_p8c.py`)
