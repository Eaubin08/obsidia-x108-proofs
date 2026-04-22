# Bank Outputs

## Purpose

This file explains how to read the public outputs of P2 Bank.

## Core fields

### `market_verdict`
Business-facing reading.

Typical values in public bank runs:
- `AUTHORIZE`
- `ANALYZE`

### `x108_gate`
Sovereign governance reading.

Typical values:
- `ALLOW`
- `HOLD`
- `BLOCK`

This is the primary field.

### `reason_code`
Compact explanation of the exposed decision path.

### `severity`
Severity class of the case.

### `decision_id`
Public decision identifier.

### `trace_id`
Public trace identifier.

### `ticket_required`
Whether a controlled ticket path is required.

### `ticket_id`
Ticket reference when present.

### `attestation_ref`
Attestation reference exposed by the public path.

### `sigma_report`
Public Sigma stability output.

## Interpretation hierarchy

Read in this order:
1. `x108_gate`
2. `severity`
3. `reason_code`
4. `market_verdict`
5. `decision_id`
6. `trace_id`
7. `attestation_ref`
8. `sigma_report`

## Critical rule

If `market_verdict` appears softer than the sovereign reading, the canonical interpretation remains:
- `x108_gate`

## Practical reading

### Normal case
- gate allows
- low severity
- trace present
- Sigma stable

### Suspicious case
- direct path must not be freely admissible
- elevated severity or contradiction pressure
- Sigma stable

### Blocked hard case
- sovereign block
- S4 severity
- strongest public refusal profile in P2 Bank
