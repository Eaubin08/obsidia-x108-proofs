# On-Chain Audit Packet V1

**Status:** FIRST_CLASS_X108_MODULE
**Role:** Append-only audit trail for blockchain-related actions.
**Module:** `periphery/blockchain/onchain_audit_packet.py`
**Runtime:** DRY_RUN_ONLY

## Role

The On-Chain Audit Packet creates an append-only record of every blockchain-related action that passes through the X-108 governance perimeter. It captures action classification, gate decisions, risk assessments, and proof chain references — but never executes any on-chain action.

## Inputs

- `action_id: str` — action identifier
- `blockchain_action_class: str` — classification from BlockchainActionClassifier
- `gate_decisions: dict` — results from all security gates
- `os3_ticket_id: str | None` — OS3 proof ticket reference
- `sovereign_ticket_id: str | None` — SovereignTicket reference

## Outputs

- `OnChainAuditPacket` with fields:
  - `packet_id: str`
  - `action_id: str`
  - `audit_trail: list[dict]` — ordered list of gate decisions
  - `real_action_taken: bool` — always False
  - `chain_tx_hash: str | None` — always None (no real tx)

## Forbidden Actions

| Action | Status |
|--------|--------|
| Real on-chain execution | BLOCKED — real_action_taken=False |
| Chain transaction | BLOCKED — chain_tx_hash=None |
| Audit trail modification | BLOCKED — append-only |

## Relation to OS3

The audit packet feeds into the OS3 proof chain as evidence refs. Each gate decision is hashed and included in the trace hash.

## Tests

- Coverage via `tests/periphery/test_blockchain_action_classifier.py`

## Status

**DRY_RUN_ONLY** — Append-only audit trail. Never executes.
