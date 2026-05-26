# Oracle Freshness Gate V1

**Status:** FIRST_CLASS_X108_MODULE
**Role:** Blocks actions that depend on stale oracle data.
**Module:** `periphery/blockchain/oracle_freshness_gate.py`
**Gate:** HOLD (stale data), ALLOW (fresh data)

## Role

The Oracle Freshness Gate ensures that any action depending on oracle data uses fresh data (< 5 minutes old by default). Stale oracle data triggers a HOLD, preventing actions from executing on outdated information.

## Inputs

- `oracle_id: str` — oracle identifier
- `last_update_iso: str | None` — ISO 8601 timestamp of last update, or None
- `threshold_seconds: float` — freshness threshold (default: 300 = 5 minutes)

## Outputs

- `OracleFreshnessDecision` with fields:
  - `data_age_seconds: float` — age of data in seconds (inf if None)
  - `is_fresh: bool` — True if within threshold
  - `stale_risk_flag: bool` — True if stale
  - `gate: str` — ALLOW or HOLD

## Gate Logic

| Condition | Gate | Reason |
|-----------|------|--------|
| last_update_iso is None | HOLD | ORACLE_STALE_DATA_NO_TIMESTAMP |
| Invalid timestamp format | HOLD | ORACLE_STALE_DATA_INVALID_TIMESTAMP |
| age > threshold (300s) | HOLD | ORACLE_STALE_DATA |
| age <= threshold | ALLOW | ORACLE_DATA_FRESH |

## Forbidden Actions

| Action | Status |
|--------|--------|
| Execute on stale oracle data | BLOCKED — gate=HOLD |
| Execute without timestamp | BLOCKED — stale_risk_flag=True |

## Relation to SovereignTicket

Oracle-dependent world calls require a SovereignTicket. The freshness check runs before the world call is authorized.

## Tests

- `tests/periphery/test_oracle_freshness_gate.py`

## Status

**HOLD (stale) / ALLOW (fresh)** — Always read-only. Never writes to oracle.
