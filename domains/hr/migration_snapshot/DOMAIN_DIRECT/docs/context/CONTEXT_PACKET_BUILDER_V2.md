# Context Packet Builder V2

**Status:** FIRST_CLASS_X108_MODULE
**Role:** Builds structured context packets from query results, graph data, and memory candidates.
**Module:** `periphery/context/context_packet_builder_v2.py`
**Runtime:** SIGNAL_ONLY — never decides

## Role

The Context Packet Builder assembles structured context packets from multiple sources — Brody responses, Graphiti queries, memory candidates, and action data. Packets are immutable once built and carry explicit sovereignty constraints.

## Inputs

- `action_id: str`
- `brody_response: BrodyResponse | None`
- `graphiti_context: GraphitiContextResult | None`
- `memory_candidates: list[MemoryCandidate] | None`
- `source_labels: list[str]`

## Outputs

- `ContextPacketV2` with fields:
  - `packet_id: str`
  - `action_id: str`
  - `content: dict` — assembled context data
  - `decision_authority: str` — always "KX108_ONLY"
  - `readonly: bool` — always True
  - `context_signal_only: bool` — always True
  - `allowed_to_decide: bool` — always False
  - `allowed_to_act: bool` — always False

## Forbidden Actions

| Action | Status |
|--------|--------|
| Decide action | BLOCKED — allowed_to_decide=False |
| Execute action | BLOCKED — allowed_to_act=False |
| Modify packet after build | BLOCKED — readonly=True |
| Bypass X108 | BLOCKED — decision_authority=KX108_ONLY |

## Tests

- Via context packet integration tests

## Status

**CONTEXT_SIGNAL_ONLY_PASS** — Context is signal. X108 decides.
