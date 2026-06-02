# External Category Signals — Formula Appendix

## Timeverse-inspired formulas

```text
tick_valid = tick_window_min <= tick_distance <= tick_window_max AND no_float = true

challenge_valid =
current_tick <= expires_at_tick
AND payload_hash = signed_payload_hash

tool_temporal_pass =
temporal_header_present
AND signature_valid
AND anti_replay_pass
AND tick_window_valid

stale_execution =
current_tick > challenge_expires_at_tick
OR cycle_anchor_mismatch = true

anchor_hash = SHA256(canonical_json(obsidia_receipt))
```

## Consequence-boundary formulas

```text
standing_valid =
actor_valid
AND mandate_valid
AND context_valid
AND not_expired
AND not_revoked
AND scope_valid

continuation_valid =
parent_hash_match
AND lawful_state_delta
AND receipt_chain_intact

replay_valid =
same_kernel_law
AND same_memory_state
AND same_input_packet
AND same_temporal_constraint
AND same_policy_version

preserved_refusal =
no_kernel_mutation
AND no_world_action
AND proof_emitted
AND no_silent_fallback

decision ∈ {BLOCK,HOLD} => effect_receipt = null
decision = ACT => effect_receipt may_exist
```
