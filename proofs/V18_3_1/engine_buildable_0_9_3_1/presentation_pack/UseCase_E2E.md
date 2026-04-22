# End-to-End Use Case — Irreversible Trading Order Governance

## Scenario
A trading agent attempts to place an irreversible BUY order.
Obsidia must evaluate the request before execution.

## Step 1 — Initial ACTION Request
- intent.type: ACTION
- governance.irreversible: true
- domain: trading

Expected decision:
→ HOLD (human gate required)

## Step 2 — Human Gate Resolution
- Signed approval provided
- Same request re-submitted with approval artifact

Expected decision:
→ ACT

## Step 3 — Audit Trail
- OS0 validation
- OS1 decision
- OS2 execution (only after approval)
- OS3 audit entry
- audit.chain updated

## Step 4 — Attestation
- audit.log hash included in daily attestation
- attestation chained to previous day

---

This demonstrates:
- Deterministic BLOCK/HOLD/ACT flow
- Temporal suspension before irreversible action
- Human override as explicit gate
- Immutable audit proof