# P57 — Extracted Import Candidate Lists

## IMPORT_AFTER_TEST — 42 entries

| # | core_path | proof_target_path | status | risk | merge_action | required_tests | reason |
|---:|---|---|---|---|---|---|---|
| 1 | `data/strasbourg_clock/graphs/test1_baseline_delta_day.png` | `tests/test1_baseline_delta_day.png` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 2 | `data/strasbourg_clock/graphs/test2_noise_delta_day.png` | `tests/test2_noise_delta_day.png` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 3 | `data/strasbourg_clock/graphs/test3_structural_error_delta_day.png` | `tests/test3_structural_error_delta_day.png` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 4 | `data/strasbourg_clock/graphs/test4_hold_delta_day.png` | `tests/test4_hold_delta_day.png` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 5 | `data/strasbourg_clock/test1_baseline.csv` | `tests/test1_baseline.csv` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 6 | `data/strasbourg_clock/test2_noise.csv` | `tests/test2_noise.csv` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 7 | `data/strasbourg_clock/test3_structural_error.csv` | `tests/test3_structural_error.csv` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 8 | `data/strasbourg_clock/test4_hold.csv` | `tests/test4_hold.csv` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 9 | `distributed/aggregator.py` | `proofs/distributed/` | B_IMPORT_AFTER_TEST | LOW | IMPORT_WITH_REVIEW | manual_review | Distributed consensus tests — review for overlap with proof consensus. |
| 10 | `distributed/test_consensus_inprocess.py` | `tests/test_consensus_inprocess.py` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 11 | `distributed/test_consensus_local.py` | `tests/test_consensus_local.py` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 12 | `engine/api_server/attestation.py` | `tests/attestation.py` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 13 | `engine/api_server/run_attestation.py` | `tests/run_attestation.py` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 14 | `engine/os0/tests.py` | `tests/tests.py` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 15 | `engine/os0/tests_advanced.py` | `tests/tests_advanced.py` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 16 | `evidence/os4/strasbourg_clock_x108/test1_baseline.csv` | `tests/test1_baseline.csv` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 17 | `evidence/os4/strasbourg_clock_x108/test2_noise.csv` | `tests/test2_noise.csv` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 18 | `evidence/os4/strasbourg_clock_x108/test3_structural_error.csv` | `tests/test3_structural_error.csv` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 19 | `evidence/os4/strasbourg_clock_x108/test4_hold.csv` | `tests/test4_hold.csv` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 20 | `python_agents/tests/test_agents_functional.py` | `tests/test_agents_functional.py` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 21 | `scripts/generate_hashes.py` | `scripts/generate_hashes.py` | B_IMPORT_AFTER_TEST | LOW | IMPORT_WITH_REVIEW | manual_run_verification | Tooling/script — safe to import after verification. |
| 22 | `scripts/verify_hashes.py` | `scripts/verify_hashes.py` | B_IMPORT_AFTER_TEST | LOW | IMPORT_WITH_REVIEW | manual_run_verification | Tooling/script — safe to import after verification. |
| 23 | `tests/adversarial/ADVERSARIAL_REPORT_TEMPLATE.md` | `tests/ADVERSARIAL_REPORT_TEMPLATE.md` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 24 | `tests/adversarial/ADVERSARIAL_RESULTS.md` | `tests/ADVERSARIAL_RESULTS.md` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 25 | `tests/adversarial/test_consensus_split.py` | `tests/test_consensus_split.py` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 26 | `tests/adversarial/test_merkle_collision.py` | `tests/test_merkle_collision.py` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 27 | `tests/adversarial/test_monotonic_break.py` | `tests/test_monotonic_break.py` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 28 | `tests/adversarial/test_seal_tamper.py` | `tests/test_seal_tamper.py` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 29 | `tests/adversarial/test_signature_tamper.py` | `tests/test_signature_tamper.py` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 30 | `tests/adversarial/test_threshold_fuzz.py` | `tests/test_threshold_fuzz.py` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 31 | `tests/sigma_stress_test.py` | `tests/sigma_stress_test.py` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 32 | `tests/test_agents_functional.py` | `tests/test_agents_functional.py` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 33 | `tests/test_invariants_against_engine.py` | `tests/test_invariants_against_engine.py` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 34 | `tests/test_sigma_v18_9.py` | `tests/test_sigma_v18_9.py` | B_IMPORT_AFTER_TEST | LOW | REVIEW_BEFORE_IMPORT | manual_review | Core test file — review before importing. May duplicate proof tests. |
| 35 | `tools/anchor_merkle_root.py` | `scripts/anchor_merkle_root.py` | B_IMPORT_AFTER_TEST | LOW | IMPORT_WITH_REVIEW | manual_run_verification | Tooling/script — safe to import after verification. |
| 36 | `tools/calibrate_sigma.py` | `scripts/calibrate_sigma.py` | B_IMPORT_AFTER_TEST | LOW | IMPORT_WITH_REVIEW | manual_run_verification | Tooling/script — safe to import after verification. |
| 37 | `tools/conformance/check_traces_x108.py` | `scripts/check_traces_x108.py` | B_IMPORT_AFTER_TEST | LOW | IMPORT_WITH_REVIEW | manual_run_verification | Tooling/script — safe to import after verification. |
| 38 | `tools/conformance/run_conformance.py` | `scripts/run_conformance.py` | B_IMPORT_AFTER_TEST | LOW | IMPORT_WITH_REVIEW | manual_run_verification | Tooling/script — safe to import after verification. |
| 39 | `tools/standard/x108_trace_check.py` | `scripts/x108_trace_check.py` | B_IMPORT_AFTER_TEST | LOW | IMPORT_WITH_REVIEW | manual_run_verification | Tooling/script — safe to import after verification. |
| 40 | `tools/standard/x108_vectors_check.py` | `scripts/x108_vectors_check.py` | B_IMPORT_AFTER_TEST | LOW | IMPORT_WITH_REVIEW | manual_run_verification | Tooling/script — safe to import after verification. |
| 41 | `tools/verify_chain_anchor.py` | `scripts/verify_chain_anchor.py` | B_IMPORT_AFTER_TEST | LOW | IMPORT_WITH_REVIEW | manual_run_verification | Tooling/script — safe to import after verification. |
| 42 | `tools/verify_threat_model.py` | `scripts/verify_threat_model.py` | B_IMPORT_AFTER_TEST | LOW | IMPORT_WITH_REVIEW | manual_run_verification | Tooling/script — safe to import after verification. |

## NEEDS_ADAPTER — 4 entries

| # | core_path | proof_target_path | status | risk | merge_action | required_tests | reason |
|---:|---|---|---|---|---|---|---|
| 1 | `engine/bus/__init__.py` | `apps/obsidia_api/bus/` | F_NEEDS_ADAPTER | MEDIUM | COMPARE_AND_ADAPT | test_bus_dry_run_only, test_no_act_emission | Bus layer has proof equivalent in apps/obsidia_api/bus/ — needs adapter comparison. |
| 2 | `engine/bus/message.py` | `apps/obsidia_api/bus/` | F_NEEDS_ADAPTER | MEDIUM | COMPARE_AND_ADAPT | test_bus_dry_run_only, test_no_act_emission | Bus layer has proof equivalent in apps/obsidia_api/bus/ — needs adapter comparison. |
| 3 | `engine/bus/registry.py` | `apps/obsidia_api/bus/` | F_NEEDS_ADAPTER | MEDIUM | COMPARE_AND_ADAPT | test_bus_dry_run_only, test_no_act_emission | Bus layer has proof equivalent in apps/obsidia_api/bus/ — needs adapter comparison. |
| 4 | `engine/bus/router.py` | `apps/obsidia_api/bus/` | F_NEEDS_ADAPTER | MEDIUM | COMPARE_AND_ADAPT | test_bus_dry_run_only, test_no_act_emission | Bus layer has proof equivalent in apps/obsidia_api/bus/ — needs adapter comparison. |

## NEEDS_MANUAL_REVIEW — 77 entries

| # | core_path | proof_target_path | status | risk | merge_action | required_tests | reason |
|---:|---|---|---|---|---|---|---|
| 1 | `.env.example` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 2 | `.gitignore` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 3 | `ARCHITECTURE.md` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 4 | `AUDIT_GUIDE.md` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 5 | `CHALLENGE_PROTOCOL.md` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 6 | `Caddyfile` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 7 | `EXECUTION_LOG_FINAL_v120.txt` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 8 | `EXECUTION_LOG_v1.3.0.txt` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 9 | `README.md` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 10 | `agents/__init__.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 11 | `agents/base.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 12 | `agents/domains/bank_agents.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 13 | `agents/domains/ecom_agents.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 14 | `agents/domains/meta_agents.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 15 | `agents/domains/trading_agents.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 16 | `agents/registry.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 17 | `agents/sigma_config.json` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 18 | `agents/sigma_dashboard.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 19 | `agents/sigma_monitor.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 20 | `agents/utils/__init__.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 21 | `agents/utils/indicators.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 22 | `core/engine` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 23 | `engine/api_server/audit_log.py` | `` | G_NEEDS_MANUAL_REVIEW | MEDIUM | MANUAL_REVIEW | test_api_route_binding | API server has proof equivalent (apps/obsidia_api/) — architectural comparison needed. |
| 24 | `engine/api_server/main.py` | `` | G_NEEDS_MANUAL_REVIEW | MEDIUM | MANUAL_REVIEW | test_api_route_binding | API server has proof equivalent (apps/obsidia_api/) — architectural comparison needed. |
| 25 | `engine/api_server/security.py` | `` | G_NEEDS_MANUAL_REVIEW | MEDIUM | MANUAL_REVIEW | test_api_route_binding | API server has proof equivalent (apps/obsidia_api/) — architectural comparison needed. |
| 26 | `engine/api_server/signing.py` | `` | G_NEEDS_MANUAL_REVIEW | MEDIUM | MANUAL_REVIEW | test_api_route_binding | API server has proof equivalent (apps/obsidia_api/) — architectural comparison needed. |
| 27 | `engine/api_server/worm_uploader.py` | `` | G_NEEDS_MANUAL_REVIEW | MEDIUM | MANUAL_REVIEW | test_api_route_binding | API server has proof equivalent (apps/obsidia_api/) — architectural comparison needed. |
| 28 | `engine/cli/obsidia_cli.py` | `` | G_NEEDS_MANUAL_REVIEW | MEDIUM | MANUAL_REVIEW | test_api_route_binding | API server has proof equivalent (apps/obsidia_api/) — architectural comparison needed. |
| 29 | `engine/core_full/entrypoint.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 30 | `engine/core_full/modules/__init__.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 31 | `engine/core_full/modules/os_trad/__init__.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 32 | `engine/core_full/modules/os_trad/adapter.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 33 | `engine/demo/request_approved.json` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 34 | `engine/demo/request_initial.json` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 35 | `engine/demo/run_demo.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 36 | `engine/obsidia_kernel/__init__.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 37 | `engine/obsidia_kernel/kernel.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 38 | `engine/obsidia_os2/__init__.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 39 | `engine/obsidia_os2_metrics.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 40 | `engine/obsidia_runtime/__init__.py` | `` | G_NEEDS_MANUAL_REVIEW | MEDIUM | MANUAL_REVIEW | test_runtime_binding, test_no_runtime_side_effects | Runtime engine layer — needs architectural review before import. |
| 41 | `engine/obsidia_runtime/engine_final.py` | `` | G_NEEDS_MANUAL_REVIEW | MEDIUM | MANUAL_REVIEW | test_runtime_binding, test_no_runtime_side_effects | Runtime engine layer — needs architectural review before import. |
| 42 | `engine/obsidia_runtime/engine_runtime.py` | `` | G_NEEDS_MANUAL_REVIEW | MEDIUM | MANUAL_REVIEW | test_runtime_binding, test_no_runtime_side_effects | Runtime engine layer — needs architectural review before import. |
| 43 | `engine/os0/__init__.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 44 | `engine/os0/demo.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 45 | `engine/os0/determinism.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 46 | `engine/os0/ir.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 47 | `engine/os0/sandbox.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 48 | `engine/os0/translate.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 49 | `engine/os1/__init__.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 50 | `engine/os1/os1.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 51 | `engine/os1/parse_input.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 52 | `engine/os3/__init__.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 53 | `engine/os3/core_split.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 54 | `engine/os3/svg.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 55 | `engine/registry/__init__.py` | `` | G_NEEDS_MANUAL_REVIEW | LOW | MANUAL_REVIEW | manual_review | Unknown import candidacy for layer REGISTRY. |
| 56 | `engine/registry/loader.py` | `` | G_NEEDS_MANUAL_REVIEW | LOW | MANUAL_REVIEW | manual_review | Unknown import candidacy for layer REGISTRY. |
| 57 | `engine/unified/__init__.py` | `` | G_NEEDS_MANUAL_REVIEW | MEDIUM | MANUAL_REVIEW | test_runtime_binding, test_no_runtime_side_effects | Runtime engine layer — needs architectural review before import. |
| 58 | `engine/unified/orchestrator.py` | `` | G_NEEDS_MANUAL_REVIEW | MEDIUM | MANUAL_REVIEW | test_runtime_binding, test_no_runtime_side_effects | Runtime engine layer — needs architectural review before import. |
| 59 | `engine/unified/pipeline.py` | `` | G_NEEDS_MANUAL_REVIEW | MEDIUM | MANUAL_REVIEW | test_runtime_binding, test_no_runtime_side_effects | Runtime engine layer — needs architectural review before import. |
| 60 | `package-lock.json` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 61 | `package.json` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 62 | `python_agents/__init__.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 63 | `python_agents/aggregation.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 64 | `python_agents/base.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 65 | `python_agents/contracts.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 66 | `python_agents/demo_run.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 67 | `python_agents/domains/bank_agents.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 68 | `python_agents/domains/ecom_agents.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 69 | `python_agents/domains/meta_agents.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 70 | `python_agents/domains/trading_agents.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 71 | `python_agents/guard.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 72 | `python_agents/protocols.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 73 | `python_agents/registry.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 74 | `python_agents/run_pipeline.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 75 | `python_agents/utils/indicators.py` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 76 | `requirements.txt` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |
| 77 | `tsconfig.json` | `` | G_NEEDS_MANUAL_REVIEW | UNKNOWN | MANUAL_REVIEW | manual_review | Unknown status — manual review required. |

