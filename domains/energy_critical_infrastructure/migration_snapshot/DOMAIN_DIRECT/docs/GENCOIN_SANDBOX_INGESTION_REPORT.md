# Gencoin Sandbox Ingestion Report

**Date:** 2026-05-19

## Source

Extracted from `Demo-obsidia-x108-proof-main (5).zip` → Gencoin Large Sandbox Pre-Freeze pack.

## Files Extracted

Destination: `docs/gencoin/sandbox_pre_freeze/`

- `AVDR_CANON.md` — AVDR phase doctrine
- `BALANCE_CANON.md` — Balance obsidienne doctrine
- `GENCOIN_CANON.md` — Gencoin canonical spec
- `ZONES_SECURITE_CANON.md` — Security zones
- `FORMULAS.md` — All math formulas
- `STATES.md` — State machine states
- `TRANSITIONS.csv` — State transition table
- `PACK_A` through `PACK_J` — 10 physics packs
- `LIMITS_AND_STATUS.md` — Pre-freeze limits
- `PROTOS.md` — Prototype notes
- `README.md` — Pack overview
- `MANIFEST_SHA256.json` — Content hashes
- `sandbox_engine.py` — Original sandbox engine (reference only)
- `test_sandbox_engine.py` — Original sandbox tests (reference only)

## Ingested Into Periphery

- `periphery/gencoin_sandbox/sandbox_engine.py` — Production copy
- `periphery/gencoin_sandbox/regime_state.py`
- `periphery/gencoin_sandbox/regime_metrics.py`
- `periphery/gencoin_sandbox/balance_operator.py`
- `periphery/gencoin_sandbox/avdr_phase_mapper.py`
- `periphery/gencoin_sandbox/regime_truth_gate.py`

## Key Invariants

- `mint_allowed=False` always
- `FALSE_ON` state → blocks all Gencoin value candidates
- `assisted_ratio > 0.5` → blocks (ASSISTED_ON dominant)
- `truth_score < 0.8` → blocks (truth threshold not met)
- Balance: canonique≥0.80, compatible≥0.60, orbite≥0.40, rejeté<0.40
- AVDR: RESOLUTION≥(0.85, 0.75), DEPLOIEMENT≥(0.65, 0.55), VIBRATION≥(0.40, 0.30), ACCUEIL otherwise
