# Ecom Conformance Notes

Status: SCAFFOLD ONLY / DOMAIN PROFILE DOCUMENTED

Runtime conformance: PARTIALLY EVIDENCED, DOMAIN INCOMPLETE
UDIP runtime promotion: NONE
Decision authority: KX108_ONLY

## 1. Source basis

This profile is grounded in the exact Ecom source set:

- `sigma/domains/ecom_agents.py`
- `tests/integration/test_sigma_bridge_ecom.py`
- `tests/run_combinatorial_ecom.py`
- `tests/run_combinatorial_ecom_report.json`
- `specs/09_CRITICAL_WORLDS/BANK_TRADING_ECOM_INTENT_ONLY_SPEC.md`
- `specs/09_CRITICAL_WORLDS/AGENTIC_COMMERCE_GUARD_LITE_RABATTEMENT_SPEC.md`
- `domains/ecom/ECOM_MIGRATION_MANIFEST.md`

Ecom remains `PARTIAL_REFERENCE` because major business/execution pieces are explicitly absent.

## 2. Intent-only authority boundary

The Bank/Trading/Ecom intent-only spec declares:

```text
Authority: KX108_ONLY
Bank/Trading/Ecom = intent only avant X108
```

For Ecom:

```text
ORDER INTENT
!=
PAYMENT AUTHORIZATION

CHECKOUT SIGNAL
!=
PAYMENT EXECUTION
```

The spec is `DOC_ONLY`; it defines a required boundary, not complete runtime proof.

## 3. Agentic-commerce guard limitation

The Agentic Commerce Guard Lite source explicitly says:

```text
Status: ABSENT_LOCAL_REPO
Source Status: ABSENT_LOCAL_REPO
Forbidden: rabattre sans audit
```

Therefore the UDIP Ecom pack MUST NOT claim that this guard exists locally or protects execution.

```text
SPEC STUB != LOCAL GUARD
ABSENT SOURCE != IMPLEMENTED CONTROL
```

## 4. Existing Ecom bridge evidence

`tests/integration/test_sigma_bridge_ecom.py` is substantive.

It verifies that a non-sovereign `PeripheralSignalPacket`:

- can carry unknowns;
- can carry evidence refs;
- can recommend HOLD;
- is propagated into the canonical framework.

More importantly, it verifies that:

```text
can_emit_act = true
→ rejected
→ PERIPHERY_CANNOT_EMIT_ACT
```

This is real branch-local evidence for a non-sovereignty boundary.

It is not proof of payment/fulfillment execution safety.

## 5. Partial-domain boundary

The migration manifest explicitly lists missing business mechanisms:

- compensation mechanism;
- customer identity model;
- execution result;
- order lifecycle;
- payment adapter;
- refund mechanism;
- shipment / fulfillment adapter.

Therefore:

```text
Ecom agents present
!= complete commerce domain

order intent present
!= executable order lifecycle

compensation_ref extension
!= compensation mechanism implemented
```

## 6. Payment / fulfillment / compensation separation

A future Ecom path MUST preserve:

```text
customer context
→ order intent
→ domain analysis
→ DomainSignal
→ KX108
→ Binder
→ payment/fulfillment capability
→ ExecutionOutcome
→ Receipt
→ compensation reference if needed
```

Forbidden collapses:

```text
ORDER INTENT == PAYMENT
PAYMENT CAPABILITY == PERMISSION
CHECKOUT == ACT
EXECUTION ATTEMPT == EXECUTION SUCCESS
COMPENSATION REF == COMPENSATION EXECUTED
REFUND INTENT == REFUND EXECUTED
```

## 7. Evidence / provenance

The current bridge test proves evidence refs can survive into the Ecom envelope.

Future conformance MUST preserve:

- evidence refs;
- unknowns;
- risk flags;
- contradictions;
- source provenance;
- order/payment identifiers where defined.

But the current pack still lacks a full domain object/lifecycle model.

## 8. Required Ecom invariants

```text
DOMAIN != AUTHORITY
ORDER INTENT != PAYMENT
CHECKOUT != ACT
PAYMENT CAPABILITY != PERMISSION
FULFILLMENT CAPABILITY != PERMISSION
EXECUTION ATTEMPT != EXECUTION SUCCESS
COMPENSATION REF != COMPENSATION EXECUTED
REFUND INTENT != REFUND EXECUTED
PERIPHERY CANNOT EMIT ACT
REPLAY != EXECUTION
KX108_ONLY
```

## 9. Existing evidence classification

### Meaningful

- `tests/integration/test_sigma_bridge_ecom.py`
  - evidence propagation;
  - HOLD recommendation propagation;
  - sovereign packet rejection.

### Reference-only / incomplete

- combinatorial harness/report;
- Ecom agents;
- intent-only spec.

### Explicitly absent

- local Agentic Commerce Guard Lite source;
- payment adapter;
- refund mechanism;
- shipment/fulfillment adapter;
- compensation mechanism;
- complete order lifecycle.

## 10. Candidate future tests

- `test_ecom_order_intent_not_payment`
- `test_ecom_payment_requires_kx108`
- `test_ecom_payment_requires_binder`
- `test_ecom_fulfillment_requires_permission`
- `test_ecom_execution_outcome_separate_from_decision`
- `test_ecom_compensation_ref_not_compensation_execution`
- `test_ecom_replay_does_not_pay_or_fulfill`
- `test_ecom_no_kernel_mutation`
- `test_ecom_kx108_only`

## 11. Promotion condition

Ecom remains `PARTIAL_REFERENCE / SCAFFOLD_ONLY` until:

1. order lifecycle is defined;
2. payment/refund/fulfillment adapters exist and are bounded;
3. KX108 exclusivity is tested;
4. Binder separation is tested;
5. execution outcome is explicit;
6. compensation semantics are real rather than nominal;
7. replay cannot trigger payment or fulfillment;
8. object mapping is evidence-backed;
9. meaningful end-to-end tests pass.
