# Interface Module

**Status:** FIRST_CLASS_X108_MODULE — READONLY / NO ACT
**Source:** `periphery/interface/` (4 modules)
**Tests:** `tests/periphery/test_interface_*.py`

## Modules

| Module | Role | Authority |
|--------|------|-----------|
| `interface_state_packet.py` | Interface state representation | SIGNAL_ONLY |
| `interface_event_log.py` | Append-only event log | READONLY |
| `interface_view_contracts.py` | View contract definitions | READONLY |
| `workbench_api_contract.py` | Workbench API specification | READONLY |

## Sovereignty Invariants

- `readonly = True` — interface is read-only
- `can_emit_act = False` — interface never emits ACT
- No module decides
- No module writes to kernel
- Interface = signal, not authority

## Canonical Rules

- Interface displays context. It does not decide.
- Interface = signal, signal ≠ decision.
- Brody context panel: read-only display of Brody response
- Memory candidate review: human-only interaction
