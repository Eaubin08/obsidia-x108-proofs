# P60 — Test Batch 2 Import

**Status :** P60_TEST_BATCH_2_IMPORT_READY
**Branche :** p60-test-batch-2-import
**Date :** 2026-06-07

## Résumé

P60 importe les 27 fichiers de la liste `test_batch_2` de P58 (classification `TEST_BATCH_2` / surfaces `TEST_ONLY` et `PROOF_SIGMA`).
Aucun fichier runtime, sigma, apps ou proofs/V18_3_1 n'est touché.

## Fichiers importés (27)

| core_path | target_path | SHA256 (16c) | Action |
|---|---|---|---|
| tests/adversarial/test_consensus_split.py | tests/test_consensus_split.py | aaaffb7409f61f25 | COPIED_NEW |
| tests/adversarial/test_merkle_collision.py | tests/test_merkle_collision.py | 6d9c46cd5555e1d6 | COPIED_NEW |
| tests/adversarial/test_monotonic_break.py | tests/test_monotonic_break.py | 0947b93c03f37fc3 | COPIED_NEW |
| tests/adversarial/test_seal_tamper.py | tests/test_seal_tamper.py | b5dbd8693a9e91a3 | COPIED_NEW |
| tests/adversarial/test_signature_tamper.py | tests/test_signature_tamper.py | 42814e667a1063ff | COPIED_NEW |
| tests/adversarial/test_threshold_fuzz.py | tests/test_threshold_fuzz.py | 54c25b742dd19a7f | COPIED_NEW |
| tests/adversarial/ADVERSARIAL_REPORT_TEMPLATE.md | tests/ADVERSARIAL_REPORT_TEMPLATE.md | 80f3220481147669 | COPIED_NEW |
| tests/adversarial/ADVERSARIAL_RESULTS.md | tests/ADVERSARIAL_RESULTS.md | 5ccab13f03354351 | COPIED_NEW |
| tests/test_invariants_against_engine.py | tests/test_invariants_against_engine.py | 57d0d94835fe9398 | COPIED_NEW |
| tests/sigma_stress_test.py | tests/sigma_stress_test.py | e68125608fdc908e | COPIED_NEW |
| tests/test_sigma_v18_9.py | tests/test_sigma_v18_9.py | 305c63776c0ca6f7 | COPIED_NEW |
| tests/test_agents_functional.py | tests/test_agents_functional.py | c96d900179099179 | COPIED_NEW |
| distributed/test_consensus_inprocess.py | tests/test_consensus_inprocess.py | 633df2dfa2ae9d03 | COPIED_NEW |
| distributed/test_consensus_local.py | tests/test_consensus_local.py | 80c057f299c5bb46 | COPIED_NEW |
| distributed/aggregator.py | proofs/distributed/aggregator.py | 3ee870e90c659a30 | COPIED_NEW |
| engine/api_server/attestation.py | tests/attestation.py | 1e5257e9be90cceb | COPIED_NEW |
| engine/api_server/run_attestation.py | tests/run_attestation.py | 4af615566d20fb02 | COPIED_NEW |
| engine/os0/tests.py | tests/tests.py | 2b92ec33847ba82d | COPIED_NEW |
| engine/os0/tests_advanced.py | tests/tests_advanced.py | 22424c7ca22d8d8a | COPIED_NEW |
| data/strasbourg_clock/graphs/test1_baseline_delta_day.png | tests/test1_baseline_delta_day.png | fdf07fc81c6652ce | COPIED_NEW |
| data/strasbourg_clock/graphs/test2_noise_delta_day.png | tests/test2_noise_delta_day.png | ccdd4f0e04a16095 | COPIED_NEW |
| data/strasbourg_clock/graphs/test3_structural_error_delta_day.png | tests/test3_structural_error_delta_day.png | 1abe419c4e60390c | COPIED_NEW |
| data/strasbourg_clock/graphs/test4_hold_delta_day.png | tests/test4_hold_delta_day.png | ba95d12fb2eb2838 | COPIED_NEW |
| data/strasbourg_clock/test1_baseline.csv | tests/test1_baseline.csv | 6ebdd781806c4ed8 | COPIED_NEW |
| data/strasbourg_clock/test2_noise.csv | tests/test2_noise.csv | 92df9cdd27e3c292 | COPIED_NEW |
| data/strasbourg_clock/test3_structural_error.csv | tests/test3_structural_error.csv | 3f4f451490e15e15 | COPIED_NEW |
| data/strasbourg_clock/test4_hold.csv | tests/test4_hold.csv | 65e635c3410418fc | COPIED_NEW |

## Déjà présents identiques (4)

| core_path | target_path | Raison |
|---|---|---|
| evidence/os4/strasbourg_clock_x108/test1_baseline.csv | tests/test1_baseline.csv | SHA identique (data/ déjà copié) |
| evidence/os4/strasbourg_clock_x108/test2_noise.csv | tests/test2_noise.csv | SHA identique |
| evidence/os4/strasbourg_clock_x108/test3_structural_error.csv | tests/test3_structural_error.csv | SHA identique |
| evidence/os4/strasbourg_clock_x108/test4_hold.csv | tests/test4_hold.csv | SHA identique |

## Bloqués — cible différente (1)

| core_path | target_path | Raison |
|---|---|---|
| python_agents/tests/test_agents_functional.py | tests/test_agents_functional.py | SHA source ≠ cible existante (3e6bc88 ≠ c96d900) — non écrasé |

## Vérifications appliquées

- Tous les fichiers `.py` compilent : `python -m py_compile` → OK
- Aucun flag dangereux (`runtime_allowed_now`, `memory_write`, `graphiti_write`, etc.)
- Aucune cible `sigma/`, `apps/`, `runtime_wiring/`, `proofs/V18_3_1/`, `periphery/`
- Seul `proofs/distributed/aggregator.py` est hors `tests/` — surface PROOF_SIGMA, classifié TEST_BATCH_2, pas V18_3_1

## Périmètres non touchés

| Périmètre | Modifié |
|---|---|
| sigma/ | NON |
| apps/ | NON |
| runtime_wiring/ | NON |
| proofs/V18_3_1/ | NON |
| ACT | NON |

## Suite

**P61** — BUS_ADAPTER_BATCH (comparaison et adaptation engine/bus/ vs apps/obsidia_api/bus/)
