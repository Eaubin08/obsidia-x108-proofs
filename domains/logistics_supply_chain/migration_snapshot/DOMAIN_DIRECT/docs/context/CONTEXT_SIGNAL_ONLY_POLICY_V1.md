# Context Signal-Only Policy V1

**Status:** ABSOLUTE INVARIANT
**Role:** Context is signal. Signal is not decision. Context packets inform — they never decide.

## The Invariant

**Contexte = signal. Signal ≠ décision.** Every context packet in the Obsidia X-108 system is a signal carrier — it provides structured information to X108 for decision-making. It never makes the decision itself.

## Enforcement

- `decision_authority = "KX108_ONLY"` in every context packet
- `context_signal_only = True` — packets are explicitly marked as signal
- `allowed_to_decide = False` — cannot approve or deny actions
- `allowed_to_act = False` — cannot execute actions
- `readonly = True` — immutable once built

## The Signal Flow

```
Brody response  ──┐
Graphiti query  ──┤
Memory candidate ──┼── ContextPacketV2 (SIGNAL)
Action data      ──┘        │
                            ▼
                    X108 Readonly Ingress
                            │
                            ▼
                    Sigma Aggregator
                            │
                            ▼
                    X108 Decision (sole authority)
```

## What Context Packets ARE

- Structured information carriers
- Signal from periphery to kernel
- Immutable records
- Input to X108 decision process

## What Context Packets ARE NOT

- Decision makers
- Authority holders
- Action executors
- Gate overriders

## Tests

- `tests/non_sovereignty/test_context_packet_no_authority.py`

## Status

**CONTEXT_SIGNAL_ONLY_PASS** — Absolute invariant.
