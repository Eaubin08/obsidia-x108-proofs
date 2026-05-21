# Interface Ready Contracts V1

**Status:** FIRST_CLASS_X108_MODULE
**Role:** Defines the contract for human-interface interactions.
**Modules:** `interface_state_packet.py`, `interface_view_contracts.py`
**Runtime:** READONLY — NO ACT

## Contracts

### Interface State Packet
- Represents the current state of the interface
- `readonly = True` — never mutates
- `can_emit_act = False` — never authorizes actions
- Fields: `packet_id`, `session_id`, `phase`, `memory_status`, `brody_status`, `graphiti_status`, `context_ready`

### Brody Context Panel Contract
- Displays Brody responses in read-only panel
- No edit, no write-back
- Advisory labels on every piece of content
- Language routing preserves user language

### Memory Candidate Review Contract
- Displays memory candidates for human review
- Human must explicitly approve promotion
- No automatic promotion trigger in UI
- Review decision logged in interface event log

## Forbidden Actions

| Action | Status |
|--------|--------|
| Emit ACT from interface | BLOCKED — can_emit_act=False |
| Auto-approve promotion | BLOCKED — requires explicit human action |
| Write to kernel from interface | BLOCKED — readonly=True |
| Bypass X108 via interface | BLOCKED — decision_authority=KX108_ONLY |

## Tests

- `tests/periphery/test_interface_state_packet.py`

## Status

**INTERFACE_READONLY_PASS** — Interface is display. X108 decides.
