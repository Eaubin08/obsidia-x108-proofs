# Context Packet Module

**Status:** FIRST_CLASS_X108_MODULE — SIGNAL ONLY
**Source:** `periphery/context/` (5 modules)
**Tests:** `tests/periphery/test_context_*.py` + `tests/non_sovereignty/test_context_*.py`

## Modules

| Module | Role | Authority |
|--------|------|-----------|
| `context_packet_builder_v2.py` | Builds structured context packets | SIGNAL_ONLY |
| `context_packet_validator.py` | Validates packet integrity | VALIDATOR |
| `context_packet_sanitizer.py` | Sanitizes packet content | SANITIZER |
| `context_packet_exporter.py` | Exports packets for downstream use | EXPORTER |

## Sovereignty Invariants

- `context_signal_only = True` — context is signal, never decision
- `decision_authority = "KX108_ONLY"` — never decides
- `readonly = True` — packets are immutable once built
- `allowed_to_decide = False` — cannot approve actions
- `allowed_to_act = False` — cannot execute actions

## Canonical Rules

- Contexte = signal. Signal ≠ décision.
- Le contexte informe. Il ne décide pas.
- ContextPacket → X108 readonly ingress → X108 décision.
