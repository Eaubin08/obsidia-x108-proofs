# P58 — Core Import Triage Operational Path-Aware

**Mode:** APPLY  
**Layer:** TOOLING  
**Scope:** Triage opérationnel des candidats d'import core, classification par surface d'exécution réelle  
**Risk:** LOW — aucun import effectif, aucune modification runtime  
**Files touched:** docs/core_import/P58_CORE_IMPORT_TRIAGE_OPERATIONAL_PATH_AWARE.json, docs/core_import/P58_CORE_IMPORT_TRIAGE_OPERATIONAL_PATH_AWARE.md, tests/test_p58_core_import_triage_operational_path_aware.py

---

## Statut

```
P58_CORE_IMPORT_TRIAGE_OPERATIONAL_PATH_AWARE_READY
source_patch_applied: false
core_files_imported: 0
```

## Contexte

- P56 : mergé (PASS)
- P57 : pushé et en PR (PASS)
- P57 a produit : 282 fichiers inventoriés, 42 IMPORT_AFTER_TEST, 4 NEEDS_ADAPTER, 77 NEEDS_MANUAL_REVIEW, 19 DO_NOT_IMPORT, 11 KEEP_PROOF_VERSION

P58 transforme cette cartographie en plan d'action par lots, en tenant compte des **chemins d'exécution réels** (pas des noms de dossiers).

---

## Surfaces d'exécution

| Surface | Description | Chemin type |
|---|---|---|
| `CORE_STANDALONE` | Moteur seul, aucun proof actif | engine/, agents/, governance/, automation/ |
| `PROOF_SIGMA` | Surface proof/sigma active | sigma/, proofs/, formal/ |
| `TERRAIN_PORTABLE` | Branchement terrain | terrain.zip, MonProjet/server.kernel.sealed.cjs, localhost:3018 |
| `API_REVERSE_IR` | Route IR readonly | apps/obsidia_api/routes/os_trad_ir_reverse.py |
| `RESPONSE_TEMPLATE_READONLY` | Réponse française template | f36_*, f37_* — aucune autorité décisionnelle |
| `PRIVATE_UI_IGNORE` | UI privée exclue | BankWorld, Gemini, TRPC, composants TSX |
| `AUDIT_TOOLING` | Outillage audit pur | scripts/, tools/ — lecture seule |
| `TEST_ONLY` | Tests adversariaux / invariants | tests/adversarial/, tests/*.py |
| `BUS_ADAPTER` | Adaptateur bus contrôlé | engine/bus/ → apps/obsidia_api/bus/ |
| `UNKNOWN_DEFER` | Surface inconnue, reporter | config, package.json, requirements |

---

## LOT 1 — SAFE_BATCH_1 (10 fichiers)

Critères de sélection :
- Outillage audit/preuve uniquement
- Pas de runtime, pas d'ACT, pas de write
- Pas de remplacement d'une version proof supérieure
- Testable immédiatement
- `execution_surface = AUDIT_TOOLING`

| # | core_path | target_path | Surface |
|--:|---|---|---|
| 1 | `scripts/generate_hashes.py` | `scripts/generate_hashes.py` | AUDIT_TOOLING |
| 2 | `scripts/verify_hashes.py` | `scripts/verify_hashes.py` | AUDIT_TOOLING |
| 3 | `tools/anchor_merkle_root.py` | `scripts/anchor_merkle_root.py` | AUDIT_TOOLING |
| 4 | `tools/calibrate_sigma.py` | `scripts/calibrate_sigma.py` | AUDIT_TOOLING |
| 5 | `tools/conformance/check_traces_x108.py` | `scripts/check_traces_x108.py` | AUDIT_TOOLING |
| 6 | `tools/conformance/run_conformance.py` | `scripts/run_conformance.py` | AUDIT_TOOLING |
| 7 | `tools/standard/x108_trace_check.py` | `scripts/x108_trace_check.py` | AUDIT_TOOLING |
| 8 | `tools/standard/x108_vectors_check.py` | `scripts/x108_vectors_check.py` | AUDIT_TOOLING |
| 9 | `tools/verify_chain_anchor.py` | `scripts/verify_chain_anchor.py` | AUDIT_TOOLING |
| 10 | `tools/verify_threat_model.py` | `scripts/verify_threat_model.py` | AUDIT_TOOLING |

**Tests requis pour chaque entrée :**
- `test_no_write_side_effects`
- `test_no_act_emission`
- `test_no_runtime_activation`
- `manual_run_verification`

**Prochaine étape :** P59 — import contrôlé de ces 10 fichiers.

---

## LOT 2 — TEST_BATCH_2 (32 fichiers)

Tests adversariaux, invariants, données de test — pas de mutation possible.

### Adversarial (6 tests + 2 docs)

| core_path | target_path |
|---|---|
| `tests/adversarial/test_consensus_split.py` | `tests/test_consensus_split.py` |
| `tests/adversarial/test_merkle_collision.py` | `tests/test_merkle_collision.py` |
| `tests/adversarial/test_monotonic_break.py` | `tests/test_monotonic_break.py` |
| `tests/adversarial/test_seal_tamper.py` | `tests/test_seal_tamper.py` |
| `tests/adversarial/test_signature_tamper.py` | `tests/test_signature_tamper.py` |
| `tests/adversarial/test_threshold_fuzz.py` | `tests/test_threshold_fuzz.py` |
| `tests/adversarial/ADVERSARIAL_REPORT_TEMPLATE.md` | `tests/ADVERSARIAL_REPORT_TEMPLATE.md` |
| `tests/adversarial/ADVERSARIAL_RESULTS.md` | `tests/ADVERSARIAL_RESULTS.md` |

### Tests fonctionnels / invariants

| core_path | target_path |
|---|---|
| `tests/test_invariants_against_engine.py` | `tests/test_invariants_against_engine.py` |
| `tests/sigma_stress_test.py` | `tests/sigma_stress_test.py` |
| `tests/test_sigma_v18_9.py` | `tests/test_sigma_v18_9.py` |
| `tests/test_agents_functional.py` | `tests/test_agents_functional.py` |
| `python_agents/tests/test_agents_functional.py` | `tests/test_agents_functional.py` |
| `distributed/test_consensus_inprocess.py` | `tests/test_consensus_inprocess.py` |
| `distributed/test_consensus_local.py` | `tests/test_consensus_local.py` |
| `distributed/aggregator.py` | `proofs/distributed/` |
| `engine/api_server/attestation.py` | `tests/attestation.py` |
| `engine/api_server/run_attestation.py` | `tests/run_attestation.py` |
| `engine/os0/tests.py` | `tests/tests.py` |
| `engine/os0/tests_advanced.py` | `tests/tests_advanced.py` |

### Données de test (CSVs / PNGs — 12 fichiers)

- `data/strasbourg_clock/graphs/test{1,2,3,4}_*.png` → `tests/`
- `data/strasbourg_clock/test{1,2,3,4}.csv` → `tests/`
- `evidence/os4/strasbourg_clock_x108/test{1,2,3,4}.csv` → `tests/`

**Vérifier doublon** entre `data/` et `evidence/` avant import.

---

## LOT 3 — BUS_ADAPTER_BATCH (4 fichiers)

**Stratégie :** Comparaison avec `apps/obsidia_api/bus/` — pas de copie brute.

| core_path | target_path |
|---|---|
| `engine/bus/__init__.py` | `apps/obsidia_api/bus/` |
| `engine/bus/message.py` | `apps/obsidia_api/bus/` |
| `engine/bus/registry.py` | `apps/obsidia_api/bus/` |
| `engine/bus/router.py` | `apps/obsidia_api/bus/` |

**Tests requis :** `test_bus_dry_run_only`, `test_no_act_emission`, `test_adapter_equivalence`

---

## LOT 4 — MANUAL_REVIEW_DEFERRED (77 fichiers)

### Sous-famille : agents (12)
`agents/__init__.py`, `agents/base.py`, `agents/domains/bank_agents.py`, `agents/domains/ecom_agents.py`, `agents/domains/meta_agents.py`, `agents/domains/trading_agents.py`, `agents/registry.py`, `agents/sigma_config.json`, `agents/sigma_dashboard.py`, `agents/sigma_monitor.py`, `agents/utils/__init__.py`, `agents/utils/indicators.py`

### Sous-famille : python_agents (14)
`python_agents/__init__.py`, `python_agents/aggregation.py`, `python_agents/base.py`, `python_agents/contracts.py`, `python_agents/demo_run.py`, `python_agents/domains/{bank,ecom,meta,trading}_agents.py`, `python_agents/guard.py`, `python_agents/protocols.py`, `python_agents/registry.py`, `python_agents/run_pipeline.py`, `python_agents/utils/indicators.py`

### Sous-famille : engine/obsidia_runtime (3) — RISK MEDIUM
`engine/obsidia_runtime/__init__.py`, `engine/obsidia_runtime/engine_final.py`, `engine/obsidia_runtime/engine_runtime.py`

> Couche runtime — ne pas importer sans revue architecturale complète + `test_runtime_binding`.

### Sous-famille : engine/unified (3) — RISK MEDIUM
`engine/unified/__init__.py`, `engine/unified/orchestrator.py`, `engine/unified/pipeline.py`

### Sous-famille : engine/api_server (6) — RISK MEDIUM
`engine/api_server/audit_log.py`, `engine/api_server/main.py`, `engine/api_server/security.py`, `engine/api_server/signing.py`, `engine/api_server/worm_uploader.py`, `engine/cli/obsidia_cli.py`

> Surface API_REVERSE_IR — équivalent `apps/obsidia_api/` existant, comparaison architecturale requise.

### Sous-famille : os0/os1/os3 (26)
Toutes les entrées `engine/os0/`, `engine/os1/`, `engine/os3/`, `engine/obsidia_kernel/`, `engine/obsidia_os2/`, `engine/registry/`, `engine/core_full/`, `engine/demo/`, `core/engine`

### Sous-famille : requirements/package (13)
`.env.example`, `.gitignore`, `ARCHITECTURE.md`, `AUDIT_GUIDE.md`, `CHALLENGE_PROTOCOL.md`, `Caddyfile`, `EXECUTION_LOG_FINAL_v120.txt`, `EXECUTION_LOG_v1.3.0.txt`, `README.md`, `package-lock.json`, `package.json`, `requirements.txt`, `tsconfig.json`

---

## LOT 5 — DO_NOT_TOUCH_CONFIRMATION (30 fichiers)

### DO_NOT_IMPORT — 19 fichiers (doublons vendor)

Tous les chemins `engine/core_full/modules/os_trad/vendor/obsidia_os{0,1}/` et `engine/core_full/modules/os_trad/vendor/proof/` — déjà présents dans proof.

Plus : `governance/aggregation.py`, `governance/contracts.py`, `governance/guard.py`

### KEEP_PROOF_VERSION — 11 fichiers

| core_path | target_path proof | Raison |
|---|---|---|
| `agents/aggregation.py` | `sigma/aggregation.py` | Patch P56B gamma |
| `agents/contracts.py` | `sigma/contracts.py` | Patch P56B gamma |
| `agents/guard.py` | `sigma/guard.py` | SHA identique |
| `agents/obsidia_sigma_v130.py` | `sigma/obsidia_sigma_v130.py` | Patch P56B gamma |
| `agents/protocols.py` | `sigma/protocols.py` | Patch P56B gamma |
| `agents/run_pipeline.py` | `sigma/run_pipeline.py` | Patch P56B gamma |
| `engine/obsidia_kernel/contract.py` | `proofs/V18_3_1/…` | SHA identique |
| `engine/obsidia_os2/metrics.py` | `proofs/V18_3_1/…` | Patch P56B gamma |
| `engine/os0/contract.py` | `proofs/V18_3_1/…` | SHA identique |
| `engine/os1/x108.py` | `proofs/V18_3_1/…` | SHA identique |
| `engine/os3/metrics.py` | `proofs/V18_3_1/…` | SHA identique |

---

## LOT 6 — PRIVATE_UI_EXCLUSION

Les chemins suivants sont **définitivement exclus** de tout import. Surface : `PRIVATE_UI_IGNORE`.

- `src/lib/banking/gemini.ts` — Gemini
- `src/pages/BankingModule.tsx` — BankWorld domain
- `os4-integration/canonical_components/canonical/AgentConstellationPanel.tsx` — UI privée
- `os4-integration/pages_v2/App_v2.tsx` — UI privée
- Tous les chemins `os4-integration/**/*.tsx` et `src/**/*.tsx` — même règle

### RESPONSE_TEMPLATE_READONLY

- `f36_user_scenario_controlled_response.py` → jamais classé `DECISION_KERNEL`
- `f37_multi_domain_user_scenarios_readonly.py` → jamais classé `DECISION_KERNEL`

Ces fichiers, s'ils sont rencontrés, n'ont **aucune autorité décisionnelle**. Aucune mutation, aucun ACT.

---

## Règles strictes

- Aucune copie depuis `_tmp_core_import`
- Pas de modification de `sigma/`, `proofs/V18_3_1/`, `apps/obsidia_api/`, `runtime_wiring`
- Pas d'import groupé des 42 en une fois
- Pas de copie brute de `engine/bus/`
- UI privée jamais classée kernel
- `RESPONSE_TEMPLATE_READONLY` jamais classé `DECISION_KERNEL`
- `runtime_allowed_now = false`, `memory_write = false`, `graphiti_write = false`

---

## Prochaine étape

**P59 — SAFE_BATCH_1_IMPORT** : importer les 10 fichiers SAFE_BATCH_1 avec tests obligatoires.
