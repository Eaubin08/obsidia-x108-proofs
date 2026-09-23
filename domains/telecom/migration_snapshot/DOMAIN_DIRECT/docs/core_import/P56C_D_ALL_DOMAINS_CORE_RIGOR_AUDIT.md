# P56C-D — All Domains Core Rigor Audit

Status: `PASS`

Invariant:

```text
State -> Agents -> Aggregation -> MetaAgents -> GuardX108 -> CanonicalDecisionEnvelope
```

Source patch authorized: `false`

## trading

- Status: `PASS`
- State: `TradingState`
- Protocol: `run_trading_pipeline`
- Aggregation: `aggregate_trading`
- Agents builder: `build_trading_agents`
- Missing: none

### Checks
- state_class_exists: `True`
- aggregate_function_exists: `True`
- agent_builder_file_exists: `True`
- agent_builder_function_exists: `True`
- protocol_function_exists: `True`
- protocol_uses_state: `True`
- protocol_uses_aggregate: `True`
- protocol_uses_agent_builder: `True`
- protocol_uses_meta_agents: `True`
- protocol_returns_guard_decide: `True`
- protocol_mentions_canonical_envelope: `True`
- runner_routes_domain: `True`
- runner_constructs_state: `True`

### Risk scan
- protocol_direct_act: `False`
- protocol_direct_write: `False`
- runner_sigma_mutation_possible: `True`
- runner_may_set_hold_alert: `True`
- runner_may_set_s4: `True`

## bank

- Status: `PASS`
- State: `BankState`
- Protocol: `run_bank_pipeline`
- Aggregation: `aggregate_bank`
- Agents builder: `build_bank_agents`
- Missing: none

### Checks
- state_class_exists: `True`
- aggregate_function_exists: `True`
- agent_builder_file_exists: `True`
- agent_builder_function_exists: `True`
- protocol_function_exists: `True`
- protocol_uses_state: `True`
- protocol_uses_aggregate: `True`
- protocol_uses_agent_builder: `True`
- protocol_uses_meta_agents: `True`
- protocol_returns_guard_decide: `True`
- protocol_mentions_canonical_envelope: `True`
- runner_routes_domain: `True`
- runner_constructs_state: `True`

### Risk scan
- protocol_direct_act: `False`
- protocol_direct_write: `False`
- runner_sigma_mutation_possible: `True`
- runner_may_set_hold_alert: `True`
- runner_may_set_s4: `True`

## ecom

- Status: `PASS`
- State: `EcomState`
- Protocol: `run_ecom_pipeline`
- Aggregation: `aggregate_ecom`
- Agents builder: `build_ecom_agents`
- Missing: none

### Checks
- state_class_exists: `True`
- aggregate_function_exists: `True`
- agent_builder_file_exists: `True`
- agent_builder_function_exists: `True`
- protocol_function_exists: `True`
- protocol_uses_state: `True`
- protocol_uses_aggregate: `True`
- protocol_uses_agent_builder: `True`
- protocol_uses_meta_agents: `True`
- protocol_returns_guard_decide: `True`
- protocol_mentions_canonical_envelope: `True`
- runner_routes_domain: `True`
- runner_constructs_state: `True`

### Risk scan
- protocol_direct_act: `False`
- protocol_direct_write: `False`
- runner_sigma_mutation_possible: `True`
- runner_may_set_hold_alert: `True`
- runner_may_set_s4: `True`

## gps_defense_aviation

- Status: `PASS`
- State: `GpsDefenseAviationState`
- Protocol: `run_gps_defense_aviation_pipeline`
- Aggregation: `aggregate_gps_defense_aviation`
- Agents builder: `build_gps_defense_aviation_agents`
- Missing: none

### Checks
- state_class_exists: `True`
- aggregate_function_exists: `True`
- agent_builder_file_exists: `True`
- agent_builder_function_exists: `True`
- protocol_function_exists: `True`
- protocol_uses_state: `True`
- protocol_uses_aggregate: `True`
- protocol_uses_agent_builder: `True`
- protocol_uses_meta_agents: `True`
- protocol_returns_guard_decide: `True`
- protocol_mentions_canonical_envelope: `True`
- runner_routes_domain: `True`
- runner_constructs_state: `True`

### Risk scan
- protocol_direct_act: `False`
- protocol_direct_write: `False`
- runner_sigma_mutation_possible: `True`
- runner_may_set_hold_alert: `True`
- runner_may_set_s4: `True`

