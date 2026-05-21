# V5A Test Results

**Date:** 2026-05-19
**Python:** 3.13.3
**pytest:** 9.0.3

## Final Count: 500 passed, 0 failed

| Suite | Count |
|-------|-------|
| Original V3/V4 tests | 397 |
| Phase 1 — Internal demo flows | 25 |
| Phase 2 — Blockchain non-sovereignty | 36 |
| Phase 3 — Memory/Brody/Graphiti non-sovereignty | 28 |
| Phase 6 — Manifest tests | 14 |
| **Total** | **500** |

## New Test Files (V5A)

- `tests/integration/test_internal_demo_flows_exist.py` (9)
- `tests/integration/test_internal_demo_flows_dryrun.py` (8)
- `tests/non_sovereignty/test_internal_demo_flows_no_real_act.py` (8)
- `tests/non_sovereignty/test_blockchain_no_authority.py` (7)
- `tests/non_sovereignty/test_wallet_security_no_secret_exposure.py` (5)
- `tests/non_sovereignty/test_signature_boundary_blocks_all_signing.py` (9)
- `tests/non_sovereignty/test_transaction_simulator_never_broadcasts.py` (6)
- `tests/non_sovereignty/test_gencoin_tokenization_blocked.py` (5)
- `tests/non_sovereignty/test_context_packet_no_authority.py` (7)
- `tests/non_sovereignty/test_brody_response_never_emits_verdict.py` (6)
- `tests/non_sovereignty/test_graphiti_bridge_readonly_only.py` (5)
- `tests/non_sovereignty/test_memory_candidate_ledger_no_promotion.py` (5)
- `tests/non_sovereignty/test_x108_context_ingress_readonly_only.py` (5)
- `tests/periphery/test_recursive_manifest_schema.py` (6)
- `tests/periphery/test_recursive_manifest_excludes_forbidden.py` (5)
- `tests/periphery/test_recursive_manifest_root_hash.py` (3)

**Status: ALL_TESTS_PASS** — 500 passed, 0 failed.
