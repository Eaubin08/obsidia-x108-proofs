# P57 — CORE TO PROOF IMPORT PLAN

**Date :** 2026-06-06
**Scope :** Classification de tous les composants du core ZIP pour import éventuel dans le proof repo.
**Statut :** AUDIT UNIQUEMENT — aucune copie automatique.

## Résumé par catégorie

| Catégorie | Nombre |
|---|---|
| B — IMPORT AFTER TEST | 42 |
| C — KEEP PROOF VERSION | 11 |
| D — KEEP CORE AS REFERENCE | 129 |
| E — DO NOT IMPORT | 19 |
| F — NEEDS ADAPTER | 4 |
| G — NEEDS MANUAL REVIEW | 77 |

## B — IMPORT AFTER TEST (42 items)

| core_path | proof_target | risk | merge_action |
|---|---|---|---|
| `data/strasbourg_clock/graphs/test1_baseline_delta_day.png` | `tests/test1_baseline_delta_day.png` | LOW | REVIEW_BEFORE_IMPORT |
| `data/strasbourg_clock/graphs/test2_noise_delta_day.png` | `tests/test2_noise_delta_day.png` | LOW | REVIEW_BEFORE_IMPORT |
| `data/strasbourg_clock/graphs/test3_structural_error_delta_day.png` | `tests/test3_structural_error_delta_day.png` | LOW | REVIEW_BEFORE_IMPORT |
| `data/strasbourg_clock/graphs/test4_hold_delta_day.png` | `tests/test4_hold_delta_day.png` | LOW | REVIEW_BEFORE_IMPORT |
| `data/strasbourg_clock/test1_baseline.csv` | `tests/test1_baseline.csv` | LOW | REVIEW_BEFORE_IMPORT |
| `data/strasbourg_clock/test2_noise.csv` | `tests/test2_noise.csv` | LOW | REVIEW_BEFORE_IMPORT |
| `data/strasbourg_clock/test3_structural_error.csv` | `tests/test3_structural_error.csv` | LOW | REVIEW_BEFORE_IMPORT |
| `data/strasbourg_clock/test4_hold.csv` | `tests/test4_hold.csv` | LOW | REVIEW_BEFORE_IMPORT |
| `distributed/aggregator.py` | `proofs/distributed/` | LOW | IMPORT_WITH_REVIEW |
| `distributed/test_consensus_inprocess.py` | `tests/test_consensus_inprocess.py` | LOW | REVIEW_BEFORE_IMPORT |
| `distributed/test_consensus_local.py` | `tests/test_consensus_local.py` | LOW | REVIEW_BEFORE_IMPORT |
| `engine/api_server/attestation.py` | `tests/attestation.py` | LOW | REVIEW_BEFORE_IMPORT |
| `engine/api_server/run_attestation.py` | `tests/run_attestation.py` | LOW | REVIEW_BEFORE_IMPORT |
| `engine/os0/tests.py` | `tests/tests.py` | LOW | REVIEW_BEFORE_IMPORT |
| `engine/os0/tests_advanced.py` | `tests/tests_advanced.py` | LOW | REVIEW_BEFORE_IMPORT |
| `evidence/os4/strasbourg_clock_x108/test1_baseline.csv` | `tests/test1_baseline.csv` | LOW | REVIEW_BEFORE_IMPORT |
| `evidence/os4/strasbourg_clock_x108/test2_noise.csv` | `tests/test2_noise.csv` | LOW | REVIEW_BEFORE_IMPORT |
| `evidence/os4/strasbourg_clock_x108/test3_structural_error.csv` | `tests/test3_structural_error.csv` | LOW | REVIEW_BEFORE_IMPORT |
| `evidence/os4/strasbourg_clock_x108/test4_hold.csv` | `tests/test4_hold.csv` | LOW | REVIEW_BEFORE_IMPORT |
| `python_agents/tests/test_agents_functional.py` | `tests/test_agents_functional.py` | LOW | REVIEW_BEFORE_IMPORT |
| `scripts/generate_hashes.py` | `scripts/generate_hashes.py` | LOW | IMPORT_WITH_REVIEW |
| `scripts/verify_hashes.py` | `scripts/verify_hashes.py` | LOW | IMPORT_WITH_REVIEW |
| `tests/adversarial/ADVERSARIAL_REPORT_TEMPLATE.md` | `tests/ADVERSARIAL_REPORT_TEMPLATE.md` | LOW | REVIEW_BEFORE_IMPORT |
| `tests/adversarial/ADVERSARIAL_RESULTS.md` | `tests/ADVERSARIAL_RESULTS.md` | LOW | REVIEW_BEFORE_IMPORT |
| `tests/adversarial/test_consensus_split.py` | `tests/test_consensus_split.py` | LOW | REVIEW_BEFORE_IMPORT |
| `tests/adversarial/test_merkle_collision.py` | `tests/test_merkle_collision.py` | LOW | REVIEW_BEFORE_IMPORT |
| `tests/adversarial/test_monotonic_break.py` | `tests/test_monotonic_break.py` | LOW | REVIEW_BEFORE_IMPORT |
| `tests/adversarial/test_seal_tamper.py` | `tests/test_seal_tamper.py` | LOW | REVIEW_BEFORE_IMPORT |
| `tests/adversarial/test_signature_tamper.py` | `tests/test_signature_tamper.py` | LOW | REVIEW_BEFORE_IMPORT |
| `tests/adversarial/test_threshold_fuzz.py` | `tests/test_threshold_fuzz.py` | LOW | REVIEW_BEFORE_IMPORT |
| `tests/sigma_stress_test.py` | `tests/sigma_stress_test.py` | LOW | REVIEW_BEFORE_IMPORT |
| `tests/test_agents_functional.py` | `tests/test_agents_functional.py` | LOW | REVIEW_BEFORE_IMPORT |
| `tests/test_invariants_against_engine.py` | `tests/test_invariants_against_engine.py` | LOW | REVIEW_BEFORE_IMPORT |
| `tests/test_sigma_v18_9.py` | `tests/test_sigma_v18_9.py` | LOW | REVIEW_BEFORE_IMPORT |
| `tools/anchor_merkle_root.py` | `scripts/anchor_merkle_root.py` | LOW | IMPORT_WITH_REVIEW |
| `tools/calibrate_sigma.py` | `scripts/calibrate_sigma.py` | LOW | IMPORT_WITH_REVIEW |
| `tools/conformance/check_traces_x108.py` | `scripts/check_traces_x108.py` | LOW | IMPORT_WITH_REVIEW |
| `tools/conformance/run_conformance.py` | `scripts/run_conformance.py` | LOW | IMPORT_WITH_REVIEW |
| `tools/standard/x108_trace_check.py` | `scripts/x108_trace_check.py` | LOW | IMPORT_WITH_REVIEW |
| `tools/standard/x108_vectors_check.py` | `scripts/x108_vectors_check.py` | LOW | IMPORT_WITH_REVIEW |
| `tools/verify_chain_anchor.py` | `scripts/verify_chain_anchor.py` | LOW | IMPORT_WITH_REVIEW |
| `tools/verify_threat_model.py` | `scripts/verify_threat_model.py` | LOW | IMPORT_WITH_REVIEW |

## C — KEEP PROOF VERSION (11 items)

| core_path | proof_target | risk | merge_action |
|---|---|---|---|
| `agents/aggregation.py` | `sigma/aggregation.py` | NONE | KEEP_PROOF |
| `agents/contracts.py` | `sigma/contracts.py` | NONE | KEEP_PROOF |
| `agents/guard.py` | `sigma/guard.py` | NONE | NO_ACTION |
| `agents/obsidia_sigma_v130.py` | `sigma/obsidia_sigma_v130.py` | NONE | KEEP_PROOF |
| `agents/protocols.py` | `sigma/protocols.py` | NONE | KEEP_PROOF |
| `agents/run_pipeline.py` | `sigma/run_pipeline.py` | NONE | KEEP_PROOF |
| `engine/obsidia_kernel/contract.py` | `proofs/V18_3_1/engine_buildable_0_9_3_1/obsidia_kernel/contract.py` | NONE | NO_ACTION |
| `engine/obsidia_os2/metrics.py` | `proofs/V18_3_1/engine_buildable_0_9_3_1/obsidia_os2/metrics.py` | NONE | KEEP_PROOF |
| `engine/os0/contract.py` | `proofs/V18_3_1/engine_buildable_0_9_3_1/obsidia_os0/contract.py` | NONE | NO_ACTION |
| `engine/os1/x108.py` | `proofs/V18_3_1/engine_buildable_0_9_3_1/obsidia_os1/x108.py` | NONE | NO_ACTION |
| `engine/os3/metrics.py` | `proofs/V18_3_1/engine_buildable_0_9_3_1/obsidia_structural_core/metrics.py` | NONE | NO_ACTION |

## D — KEEP CORE AS REFERENCE (129 items)

| core_path | proof_target | risk | merge_action |
|---|---|---|---|
| `MANIFESTS/CORE_ONLY_FULL_MACHINERY_LOC_SUMMARY.csv` | `—` | NONE | REFERENCE_ONLY |
| `MANIFESTS/CORE_ONLY_FULL_MACHINERY_MANIFEST_SHA256.csv` | `—` | NONE | REFERENCE_ONLY |
| `MANIFESTS/CORE_ONLY_FULL_MACHINERY_RULES.md` | `—` | NONE | REFERENCE_ONLY |
| `MANIFESTS/CORE_ONLY_FULL_MACHINERY_SUMMARY.txt` | `—` | NONE | REFERENCE_ONLY |
| `MANIFESTS/MISSING_CORE_ONLY_FULL_MACHINERY.txt` | `—` | NONE | REFERENCE_ONLY |
| `agent_sources/OBSIDIA_TOUS_LES_AGENTS.docx` | `—` | NONE | REFERENCE_ONLY |
| `app/applet/fetch.js` | `—` | NONE | REFERENCE_ONLY |
| `app/applet/fetch.ts` | `—` | NONE | REFERENCE_ONLY |
| `automation/canonicalPipeline.ts` | `—` | NONE | REFERENCE_ONLY |
| `automation/contracts.ts` | `—` | NONE | REFERENCE_ONLY |
| `automation/payloadValidator.ts` | `—` | NONE | REFERENCE_ONLY |
| `bootstrap.sh` | `—` | NONE | REFERENCE_ONLY |
| `config/strategy.ts` | `—` | NONE | REFERENCE_ONLY |
| `data/banking/scenarios.json` | `—` | NONE | REFERENCE_ONLY |
| `data/ecommerce/scenarios.json` | `—` | NONE | REFERENCE_ONLY |
| `data/scenarios.json` | `—` | NONE | REFERENCE_ONLY |
| `data/strasbourg_clock/README.md` | `—` | NONE | REFERENCE_ONLY |
| `data/strasbourg_clock/manifest.json` | `—` | NONE | REFERENCE_ONLY |
| `data/trading/BTC_1h.json` | `—` | NONE | REFERENCE_ONLY |
| `distributed/docker-compose.yml` | `—` | NONE | REFERENCE_ONLY |
| `docker/repro.Dockerfile` | `—` | NONE | REFERENCE_ONLY |
| `docker/run_repro.sh` | `—` | NONE | REFERENCE_ONLY |
| `engine/api_server/run_api.sh` | `—` | NONE | REFERENCE_ONLY |
| `evidence/os4/strasbourg_clock_x108/EVIDENCE.md` | `—` | NONE | REFERENCE_ONLY |
| `evidence/os4/strasbourg_clock_x108/STRASBOURG_CLOCK_README.md` | `—` | NONE | REFERENCE_ONLY |
| `evidence/os4/strasbourg_clock_x108/manifest.json` | `—` | NONE | REFERENCE_ONLY |
| `evidence/os4/strasbourg_clock_x108/x108_trace_report.json` | `—` | NONE | REFERENCE_ONLY |
| `examples/bank_normal.json` | `—` | NONE | REFERENCE_ONLY |
| `examples/bank_suspicious.json` | `—` | NONE | REFERENCE_ONLY |
| `examples/ecom_normal.json` | `—` | NONE | REFERENCE_ONLY |
| `examples/trading_bullish.json` | `—` | NONE | REFERENCE_ONLY |
| `governance/integrityGate.ts` | `—` | NONE | REFERENCE_ONLY |
| `governance/invariants.ts` | `—` | NONE | REFERENCE_ONLY |
| `governance/riskKillswitch.ts` | `—` | NONE | REFERENCE_ONLY |
| `governance/x108TemporalLock.ts` | `—` | NONE | REFERENCE_ONLY |
| `hashes/engine_files.sha256` | `—` | NONE | REFERENCE_ONLY |
| `lib/banking/engine.ts` | `—` | NONE | REFERENCE_ONLY |
| `lib/core/invariants.ts` | `—` | NONE | REFERENCE_ONLY |
| `lib/ecommerce/safetyGate.ts` | `—` | NONE | REFERENCE_ONLY |
| `lib/execution/erc8004Builder.ts` | `—` | NONE | REFERENCE_ONLY |
| `lib/features/coherence.ts` | `—` | NONE | REFERENCE_ONLY |
| `lib/features/friction.ts` | `—` | NONE | REFERENCE_ONLY |
| `lib/features/regime.ts` | `—` | NONE | REFERENCE_ONLY |
| `lib/features/volatility.ts` | `—` | NONE | REFERENCE_ONLY |
| `lib/gates/integrityGate.ts` | `—` | NONE | REFERENCE_ONLY |
| `lib/gates/riskKillswitch.ts` | `—` | NONE | REFERENCE_ONLY |
| `lib/gates/x108TemporalLock.ts` | `—` | NONE | REFERENCE_ONLY |
| `lib/simulation/simLite.ts` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/canonical_components/StatusRail.tsx` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/canonical_components/canonical/AgentConstellationPanel.tsx` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/canonical_components/canonical/DecisionEnvelopeCard.tsx` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/canonical_components/canonical/HealthMatrix.tsx` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/canonical_components/canonical/IncidentCard.tsx` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/canonical_components/canonical/ProofChainView.tsx` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/canonical_components/canonical/ReplayPanel.tsx` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/canonical_ts/canonicalPipeline.ts` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/canonical_ts/contracts.ts` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/canonical_ts/payloadValidator.ts` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/contexts/WorldContext.tsx` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/pages_v2/App_v2.tsx` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/pages_v2/Control.tsx` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/pages_v2/Future.tsx` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/pages_v2/Live.tsx` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/pages_v2/Mission.tsx` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/pages_v2/Past.tsx` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/python_agents/__init__.py` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/python_agents/aggregation.py` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/python_agents/base.py` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/python_agents/contracts.py` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/python_agents/demo_run.py` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/python_agents/domains/bank_agents.py` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/python_agents/domains/ecom_agents.py` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/python_agents/domains/meta_agents.py` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/python_agents/domains/trading_agents.py` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/python_agents/guard.py` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/python_agents/protocols.py` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/python_agents/registry.py` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/python_agents/run_pipeline.py` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/python_agents/tests/test_agents_functional.py` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/python_agents/utils/indicators.py` | `—` | NONE | REFERENCE_ONLY |
| `os4-integration/ui_components/CanonicalAgentPanel.tsx` | `—` | NONE | REFERENCE_ONLY |
| `pnpm-lock.yaml` | `—` | NONE | REFERENCE_ONLY |
| `src/App.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/components/DomainCard.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/components/GlobalHeader.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/components/ModuleHeader.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/components/ProtocolOverview.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/components/Sidebar.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/components/SignalsPanel.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/components/StrategyPanel.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/components/Terminal.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/components/WorkflowProgress.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/config/domains.ts` | `—` | NONE | REFERENCE_ONLY |
| `src/config/strategy.ts` | `—` | NONE | REFERENCE_ONLY |
| `src/index.css` | `—` | NONE | REFERENCE_ONLY |
| `src/lib/banking/engine.ts` | `—` | NONE | REFERENCE_ONLY |
| `src/lib/banking/gemini.ts` | `—` | NONE | REFERENCE_ONLY |
| `src/lib/core/humanAlgebra.ts` | `—` | NONE | REFERENCE_ONLY |
| `src/lib/ecommerce/safetyGate.ts` | `—` | NONE | REFERENCE_ONLY |
| `src/lib/utils.ts` | `—` | NONE | REFERENCE_ONLY |
| `src/main.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/pages/AgentRegistry.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/pages/BankingModule.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/pages/CapitalVault.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/pages/Dashboard.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/pages/EcommerceModule.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/pages/HomeDashboard.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/pages/Leaderboard.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/pages/OS0Invariants.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/pages/OS1Observation.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/pages/OS2Simulation.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/pages/OS3Governance.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/pages/OS4Reports.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/pages/RiskRouter.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/pages/TradingTests.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/pages/TrustSignals.tsx` | `—` | NONE | REFERENCE_ONLY |
| `src/types.ts` | `—` | NONE | REFERENCE_ONLY |
| `tests/adversarial/RUN_ALL_ADVERSARIAL.sh` | `—` | NONE | REFERENCE_ONLY |
| `tests/canonical_components.test.ts` | `—` | NONE | REFERENCE_ONLY |
| `tests/engines.test.ts` | `—` | NONE | REFERENCE_ONLY |
| `tests/engines/bankEngine.ts` | `—` | NONE | REFERENCE_ONLY |
| `tests/engines/ecomEngine.ts` | `—` | NONE | REFERENCE_ONLY |
| `tests/engines/guardX108.ts` | `—` | NONE | REFERENCE_ONLY |
| `tests/engines/tradingEngine.ts` | `—` | NONE | REFERENCE_ONLY |
| `tools/standard/verify_x108_standard.sh` | `—` | NONE | REFERENCE_ONLY |
| `tools/standard/x108_lean_check.sh` | `—` | NONE | REFERENCE_ONLY |
| `tools/standard/x108_tla_check.sh` | `—` | NONE | REFERENCE_ONLY |
| `tools/verify_all_phases.sh` | `—` | NONE | REFERENCE_ONLY |
| `types/erc8004.ts` | `—` | NONE | REFERENCE_ONLY |

## E — DO NOT IMPORT (19 items)

| core_path | proof_target | risk | merge_action |
|---|---|---|---|
| `engine/core_full/modules/os_trad/vendor/obsidia_os0/__init__.py` | `—` | REDUNDANCY | DO_NOT_IMPORT |
| `engine/core_full/modules/os_trad/vendor/obsidia_os0/contract.py` | `—` | REDUNDANCY | DO_NOT_IMPORT |
| `engine/core_full/modules/os_trad/vendor/obsidia_os0/demo.py` | `—` | REDUNDANCY | DO_NOT_IMPORT |
| `engine/core_full/modules/os_trad/vendor/obsidia_os0/determinism.py` | `—` | REDUNDANCY | DO_NOT_IMPORT |
| `engine/core_full/modules/os_trad/vendor/obsidia_os0/ir.py` | `—` | REDUNDANCY | DO_NOT_IMPORT |
| `engine/core_full/modules/os_trad/vendor/obsidia_os0/sandbox.py` | `—` | REDUNDANCY | DO_NOT_IMPORT |
| `engine/core_full/modules/os_trad/vendor/obsidia_os0/tests.py` | `—` | REDUNDANCY | DO_NOT_IMPORT |
| `engine/core_full/modules/os_trad/vendor/obsidia_os0/tests_advanced.py` | `—` | REDUNDANCY | DO_NOT_IMPORT |
| `engine/core_full/modules/os_trad/vendor/obsidia_os0/translate.py` | `—` | REDUNDANCY | DO_NOT_IMPORT |
| `engine/core_full/modules/os_trad/vendor/obsidia_os1/__init__.py` | `—` | REDUNDANCY | DO_NOT_IMPORT |
| `engine/core_full/modules/os_trad/vendor/obsidia_os1/os1.py` | `—` | REDUNDANCY | DO_NOT_IMPORT |
| `engine/core_full/modules/os_trad/vendor/obsidia_os1/parse_input.py` | `—` | REDUNDANCY | DO_NOT_IMPORT |
| `engine/core_full/modules/os_trad/vendor/obsidia_os1/x108.py` | `—` | REDUNDANCY | DO_NOT_IMPORT |
| `engine/core_full/modules/os_trad/vendor/proof/__init__.py` | `—` | REDUNDANCY | DO_NOT_IMPORT |
| `engine/core_full/modules/os_trad/vendor/proof/codegen.py` | `—` | REDUNDANCY | DO_NOT_IMPORT |
| `engine/core_full/modules/os_trad/vendor/proof/runner.py` | `—` | REDUNDANCY | DO_NOT_IMPORT |
| `governance/aggregation.py` | `—` | REDUNDANCY | DO_NOT_IMPORT |
| `governance/contracts.py` | `—` | REDUNDANCY | DO_NOT_IMPORT |
| `governance/guard.py` | `—` | REDUNDANCY | DO_NOT_IMPORT |

## F — NEEDS ADAPTER (4 items)

| core_path | proof_target | risk | merge_action |
|---|---|---|---|
| `engine/bus/__init__.py` | `apps/obsidia_api/bus/` | MEDIUM | COMPARE_AND_ADAPT |
| `engine/bus/message.py` | `apps/obsidia_api/bus/` | MEDIUM | COMPARE_AND_ADAPT |
| `engine/bus/registry.py` | `apps/obsidia_api/bus/` | MEDIUM | COMPARE_AND_ADAPT |
| `engine/bus/router.py` | `apps/obsidia_api/bus/` | MEDIUM | COMPARE_AND_ADAPT |

## G — NEEDS MANUAL REVIEW (77 items)

| core_path | proof_target | risk | merge_action |
|---|---|---|---|
| `.env.example` | `—` | UNKNOWN | MANUAL_REVIEW |
| `.gitignore` | `—` | UNKNOWN | MANUAL_REVIEW |
| `ARCHITECTURE.md` | `—` | UNKNOWN | MANUAL_REVIEW |
| `AUDIT_GUIDE.md` | `—` | UNKNOWN | MANUAL_REVIEW |
| `CHALLENGE_PROTOCOL.md` | `—` | UNKNOWN | MANUAL_REVIEW |
| `Caddyfile` | `—` | UNKNOWN | MANUAL_REVIEW |
| `EXECUTION_LOG_FINAL_v120.txt` | `—` | UNKNOWN | MANUAL_REVIEW |
| `EXECUTION_LOG_v1.3.0.txt` | `—` | UNKNOWN | MANUAL_REVIEW |
| `README.md` | `—` | UNKNOWN | MANUAL_REVIEW |
| `agents/__init__.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `agents/base.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `agents/domains/bank_agents.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `agents/domains/ecom_agents.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `agents/domains/meta_agents.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `agents/domains/trading_agents.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `agents/registry.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `agents/sigma_config.json` | `—` | UNKNOWN | MANUAL_REVIEW |
| `agents/sigma_dashboard.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `agents/sigma_monitor.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `agents/utils/__init__.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `agents/utils/indicators.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `core/engine` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/api_server/audit_log.py` | `—` | MEDIUM | MANUAL_REVIEW |
| `engine/api_server/main.py` | `—` | MEDIUM | MANUAL_REVIEW |
| `engine/api_server/security.py` | `—` | MEDIUM | MANUAL_REVIEW |
| `engine/api_server/signing.py` | `—` | MEDIUM | MANUAL_REVIEW |
| `engine/api_server/worm_uploader.py` | `—` | MEDIUM | MANUAL_REVIEW |
| `engine/cli/obsidia_cli.py` | `—` | MEDIUM | MANUAL_REVIEW |
| `engine/core_full/entrypoint.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/core_full/modules/__init__.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/core_full/modules/os_trad/__init__.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/core_full/modules/os_trad/adapter.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/demo/request_approved.json` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/demo/request_initial.json` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/demo/run_demo.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/obsidia_kernel/__init__.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/obsidia_kernel/kernel.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/obsidia_os2/__init__.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/obsidia_os2_metrics.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/obsidia_runtime/__init__.py` | `—` | MEDIUM | MANUAL_REVIEW |
| `engine/obsidia_runtime/engine_final.py` | `—` | MEDIUM | MANUAL_REVIEW |
| `engine/obsidia_runtime/engine_runtime.py` | `—` | MEDIUM | MANUAL_REVIEW |
| `engine/os0/__init__.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/os0/demo.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/os0/determinism.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/os0/ir.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/os0/sandbox.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/os0/translate.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/os1/__init__.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/os1/os1.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/os1/parse_input.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/os3/__init__.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/os3/core_split.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/os3/svg.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `engine/registry/__init__.py` | `—` | LOW | MANUAL_REVIEW |
| `engine/registry/loader.py` | `—` | LOW | MANUAL_REVIEW |
| `engine/unified/__init__.py` | `—` | MEDIUM | MANUAL_REVIEW |
| `engine/unified/orchestrator.py` | `—` | MEDIUM | MANUAL_REVIEW |
| `engine/unified/pipeline.py` | `—` | MEDIUM | MANUAL_REVIEW |
| `package-lock.json` | `—` | UNKNOWN | MANUAL_REVIEW |
| `package.json` | `—` | UNKNOWN | MANUAL_REVIEW |
| `python_agents/__init__.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `python_agents/aggregation.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `python_agents/base.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `python_agents/contracts.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `python_agents/demo_run.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `python_agents/domains/bank_agents.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `python_agents/domains/ecom_agents.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `python_agents/domains/meta_agents.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `python_agents/domains/trading_agents.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `python_agents/guard.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `python_agents/protocols.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `python_agents/registry.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `python_agents/run_pipeline.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `python_agents/utils/indicators.py` | `—` | UNKNOWN | MANUAL_REVIEW |
| `requirements.txt` | `—` | UNKNOWN | MANUAL_REVIEW |
| `tsconfig.json` | `—` | UNKNOWN | MANUAL_REVIEW |