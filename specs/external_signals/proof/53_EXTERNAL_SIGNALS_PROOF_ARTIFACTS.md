# External Category Signals — Proof Artifacts

Required proof artifacts for RSSI review:

- `temporal_context_header`
- `tick_canonical_validation_report`
- `anti_replay_horizon_log`
- `temporal_challenge_receipt`
- `temporal_receipt_metadata`
- `receipt_anchor_hash`
- `executable_standing_status`
- `continuation_legitimacy_status`
- `consequence_binding_status`
- `intent_receipt`
- `effect_receipt_only_after_ACT`
- `law_state_input_replay_triplet`
- `protected_consequence_statement`
- `visible_enforcement_surface_report`

Non-authority rule:

```text
External signals may enrich proof/context.
External signals may not decide.
DECISION_AUTHORITY = KX108_ONLY.
```
