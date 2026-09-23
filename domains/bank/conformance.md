# Bank Conformance Notes

Status: SCAFFOLD ONLY / DOMAIN PROFILE DOCUMENTED

Runtime conformance: NOT PROVEN
UDIP Bank runtime promotion: NONE
Decision authority: KX108_ONLY

## 1. Source basis

This profile is grounded in:

- `domain_packets/bank_decisional_form_v0.yaml`
- `domains/bank/bank_x108_gate.py`
- `sigma/domains/bank_agents.py`
- `tests/integration/test_sigma_bridge_bank.py`
- `tests/integration/test_full_stack_static_bank.py`
- `specs/09_CRITICAL_WORLDS/BANK_TRADING_ECOM_INTENT_ONLY_SPEC.md`

Historical Bank migration evidence remains reference material and is not automatically UDIP conformance proof.

## 2. Existing authority contract

The Bank decisional form declares:

```text
calls_kernel = true
decides_alone = false
decision_authority = KX108_ONLY
kernel_mutation = false
fail_closed = true
```

The real Bank gate translates Bank payloads into IR and delegates the decision to X-108.

It explicitly states:

```text
Ne prend AUCUNE décision autonome.
Ne réplique PAS la logique ALLOW/HOLD/BLOCK.
```

On kernel failure it returns local `HOLD`.

## 3. Bank business signal vs authority

Bank may produce or carry:

- transaction risk;
- fraud indicators;
- AML/compliance context;
- limit violations;
- audit/data quality;
- payment/transfer intent.

None of those is authority.

```text
FRAUD SIGNAL != BLOCK AUTHORITY
AML SIGNAL != LEGAL VERDICT
LIMIT VIOLATION != EXECUTION PERMISSION
COMPLIANCE SIGNAL != DECISION
PAYMENT INTENT != PAYMENT EXECUTION
```

## 4. Intent-only boundary

The Bank/Trading/Ecom intent-only spec states:

```text
Bank actions = intent_packet → X108 evaluation
```

and forbids Bank actions without X108.

The source is `DOC_ONLY`, so this is a contractual direction that still requires runtime/test proof.

## 5. Payment / transfer boundary

Future Bank execution MUST preserve:

```text
transaction observation
→ domain analysis
→ Bank DomainSignal
→ KX108
→ Binder
→ bank execution capability
→ ExecutionOutcome
→ Receipt
```

Forbidden collapses:

```text
PAYMENT REQUEST == PAYMENT EXECUTED
KX108 ACT == PROVIDER SUCCESS
PROVIDER CAPABILITY == PERMISSION
FRAUD SCORE == BLOCK
```

## 6. Fail-closed

The current Bank gate returns `HOLD` when kernel access is unavailable or fails.

This local HOLD is allowed as a fail-closed safety outcome.

It MUST NOT be generalized into autonomous Bank ALLOW/BLOCK authority.

## 7. Existing tests on this branch

### `tests/integration/test_sigma_bridge_bank.py`

This verifies a real Bank adapter/control-plane/Sigma bridge path and asserts that the resulting X108 gate is one of:

```text
ALLOW / HOLD / BLOCK
```

This is bridge evidence.

It does not by itself prove Binder separation or payment non-execution.

### `tests/integration/test_full_stack_static_bank.py`

Current content:

```python
def test_integration_placeholder():
    assert True
```

Classification:

```text
PLACEHOLDER_ONLY
```

It is not full-stack proof.

## 8. Required Bank invariants

```text
DOMAIN != AUTHORITY
TRANSACTION != DECISION
FRAUD SIGNAL != BLOCK AUTHORITY
COMPLIANCE SIGNAL != LEGAL VERDICT
PAYMENT INTENT != PAYMENT EXECUTION
PROVIDER CAPABILITY != PERMISSION
KX108 ACT != EXECUTION SUCCESS
FAIL_CLOSED HOLD != POSITIVE AUTHORIZATION
REPLAY != EXECUTION
KX108_ONLY
```

## 9. Candidate future tests

- `test_bank_gate_cannot_allow_without_kernel`
- `test_bank_fraud_signal_not_block_authority`
- `test_bank_payment_intent_requires_kx108`
- `test_bank_execution_requires_binder`
- `test_bank_provider_capability_not_permission`
- `test_bank_kx108_act_not_execution_success`
- `test_bank_replay_does_not_pay`
- `test_bank_no_kernel_mutation`
- `test_bank_kx108_only`

These are requirements, not current UDIP proof claims.

## 10. Promotion condition

Bank remains `SCAFFOLD_ONLY` until:

1. Bank DomainSignal mapping is explicit;
2. fraud/compliance signals remain advisory to authority;
3. KX108 exclusivity is tested;
4. Binder separation is tested;
5. payment execution is impossible without permission;
6. provider outcome is separated from decision;
7. receipts/replay are bound and non-executing;
8. meaningful non-sovereignty tests pass.
