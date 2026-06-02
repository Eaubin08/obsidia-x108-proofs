# External Category Signals — RSSI Test Matrix

| Test ID | Objective | Expected result |
|---|---|---|
| test_timeverse_sidecar_no_ACT | Ensure temporal sidecar cannot decide | No HOLD/BLOCK/ACT emitted |
| test_no_float_required | Ensure temporal math is tick-canonical | Float-based critical time rejected |
| test_duplicate_nonce_rejected | Ensure replay cannot pass | Duplicate nonce returns rejection signal |
| test_challenge_expiry | Ensure expired challenge cannot bind | Candidate blocked before KX108 |
| test_tool_call_still_requires_KX108 | Ensure temporal pass is not authorization | KX108 required after temporal pass |
| test_no_effect_receipt_before_ACT | Ensure HOLD/BLOCK cannot emit effect receipt | Only intent receipt exists |
| test_wrapper_cannot_override_KX108 | Ensure UI/wrapper cannot reauthorize | Violation signal emitted |
| test_replay_triplet_same_context | Ensure replay requires law/state/input identity | Replay accepted only under exact conditions |
| test_corridor_requires_KX108 | Ensure corridor is packaging, not authority | Corridor cannot emit ACT |
| test_refusal_no_mutation | Ensure refusal preserves state | No kernel/world mutation |
| test_protected_consequence_named | Ensure blocked consequence is explicit | protected_consequence field present |
| test_standing_scope_mismatch_rejected | Ensure standing is situated/scoped | Invalid standing rejected |
