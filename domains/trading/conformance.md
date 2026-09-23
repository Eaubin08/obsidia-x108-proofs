# Trading Conformance Notes

Status: SCAFFOLD ONLY / DOMAIN PROFILE DOCUMENTED

Runtime conformance: NOT PROVEN
UDIP Trading runtime promotion: NONE
Decision authority: KX108_ONLY

## 1. Source basis

This profile is grounded in the current branch sources:

- `domain_packets/trading_decisional_form_v0.yaml`
- `domains/trading/trading_x108_gate.py`
- `sigma/domains/trading_agents.py`
- `tests/integration/test_sigma_bridge_trading.py`
- `tests/integration/test_full_stack_static_trading.py`
- `specs/09_CRITICAL_WORLDS/BANK_TRADING_ECOM_INTENT_ONLY_SPEC.md`

The external `OBSIDIA_TRADING` repository remains an external reference and is not treated here as proof of UDIP runtime conformance.

## 2. Existing authority contract

The decisional form declares:

```text
calls_kernel = true
decides_alone = false
decision_authority = KX108_ONLY
kernel_mutation = false
fail_closed = true
```

The real Trading gate states that it:

- translates Trading payloads into IR;
- submits them to X-108;
- never decides autonomously;
- returns local `HOLD` if the kernel is unavailable.

Therefore the permitted local safety behavior is:

```text
kernel unavailable
→ local fail-closed HOLD
```

It MUST NOT become:

```text
local ALLOW
local positive authorization
local execution permission
```

## 3. Trading proposal vs KX108 decision

Trading agents produce domain proposals such as:

- BUY;
- SELL;
- HOLD;
- risk flags;
- contradictions;
- confidence.

These are market-domain outputs.

They MUST NOT be interpreted as KX108 authority.

```text
BUY != ACT
SELL != BLOCK
Trading HOLD proposal != KX108 HOLD authority
AgentVote != DecisionTicket
market verdict != execution permission
```

The naming overlap around `HOLD` must not collapse the two semantic layers.

## 4. Intent-only boundary

The Bank/Trading/Ecom intent-only spec is `DOC_ONLY` and states that these worlds are intent-only before X108.

For Trading this means:

```text
market intent
→ X108 evaluation
→ separate execution permission
```

and not:

```text
market signal
→ broker execution
```

The same spec explicitly forbids Trading production execution in its referenced Plan 2 context.

This remains design/reference evidence, not production-runtime proof.

## 5. Broker / execution boundary

The Trading Domain Pack may eventually expose:

- market observations;
- portfolio state;
- order intent;
- execution-quality context;
- risk evidence.

It MUST NOT:

- submit a broker order merely because agents agree;
- treat a BUY/SELL proposal as Binder permission;
- let broker capability imply execution authority;
- bypass KX108;
- bypass Binder;
- convert replay into live execution.

```text
BROKER CAPABILITY != PERMISSION
ORDER INTENT != ORDER SUBMISSION
PROPOSAL != ACTION
```

## 6. Fail-closed

The current gate returns `HOLD` when:

- requests support is unavailable;
- the kernel call fails.

This is compatible with non-sovereignty only because it is a **negative/safety admission result**, not positive execution authority.

Future implementations MUST preserve:

```text
error / unknown authority state
→ HOLD
never
→ ALLOW by default
```

## 7. Existing tests on this branch

### `tests/integration/test_sigma_bridge_trading.py`

This verifies that the Trading Sigma/periphery bridge returns an X108 gate value in:

```text
ALLOW / HOLD / BLOCK
```

It demonstrates bridge reachability at a basic level.

It does **not** by itself prove:

- KX108 exclusivity;
- Binder separation;
- broker non-execution;
- no kernel mutation.

### `tests/integration/test_full_stack_static_trading.py`

Current content is only:

```python
def test_integration_placeholder():
    assert True
```

Classification:

```text
PLACEHOLDER_ONLY
```

It MUST NOT be cited as Trading full-stack proof.

## 8. Required Trading invariants

```text
DOMAIN != AUTHORITY
MARKET SIGNAL != DECISION
BUY/SELL/HOLD PROPOSAL != KX108 VERDICT
ORDER INTENT != ORDER SUBMISSION
BROKER CAPABILITY != PERMISSION
PORTFOLIO RISK != AUTHORITY
FAIL_CLOSED HOLD != POSITIVE AUTHORIZATION
REPLAY != EXECUTION
KX108_ONLY
```

## 9. Candidate future tests

These requirements are not claimed as implemented by this Domain Pack profile:

- `test_trading_gate_cannot_allow_without_kernel`
- `test_trading_agent_buy_cannot_emit_act`
- `test_trading_agent_sell_cannot_emit_block_authority`
- `test_trading_order_intent_requires_kx108`
- `test_trading_execution_requires_binder`
- `test_trading_broker_capability_not_permission`
- `test_trading_replay_never_submits_order`
- `test_trading_no_kernel_mutation`
- `test_trading_kx108_only`

## 10. Promotion condition

Trading remains `SCAFFOLD_ONLY` until at minimum:

1. Trading DomainSignal mapping is explicit;
2. market proposals remain distinct from authority;
3. KX108 exclusivity is tested;
4. Binder separation is tested;
5. broker execution is proven impossible without permission;
6. receipts bind decision context and execution attempt;
7. replay cannot execute;
8. meaningful non-sovereignty tests pass.

Historical Trading maturity does not automatically promote the UDIP Trading Domain Pack.
