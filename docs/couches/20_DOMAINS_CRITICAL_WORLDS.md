# 20 · Domaines critiques : GPS, Bank, Trading

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

Chaque domaine comprend son terrain (objets, règles, risques, preuves) et le traduit vers la gouvernance commune. Le domaine traduit, X-108 tranche.

## Où elle intervient dans le trajet d'une demande

- **Étape 4 · Organes spécialisés** : Brody comprend et formule, la mémoire rappelle, les domaines vérifient leur terrain, Obsidure prépare un candidat, Sigma et le Peripheral Mesh mesurent la cohérence, Tree34 et Thermo apportent leurs lectures. Ils proposent, ils ne décident pas.

Voir le trajet complet : [guide général](../README.md).

## Où est son code aujourd'hui

**Points d'entrée connus :**

- [connectors/](../../connectors) · connecteurs de domaines : bank, trading, gps_defense_aviation
- [runtime_terrain_bank_trading_gps/](../../runtime_terrain_bank_trading_gps) · terrain runtime Bank, Trading, GPS
- [hackathons/nativebuilder-gps-defense/](../../hackathons/nativebuilder-gps-defense) · GPS défense
- [tools/bank_robo_real/](../../tools/bank_robo_real) · outillage Bank
- [examples/](../../examples) · exemples d'entrées (bank_normal.json, bank_suspicious.json…)

D'après le registre de fonctionnalités V3, **112 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | 35 |
| `scripts/` | 16 |
| `tools/bank_robo_real/` | 11 |
| `specs/09_CRITICAL_WORLDS/` | 10 |
| `runtime_terrain_bank_trading_gps/` | 6 |
| `demos/local_flows/` | 3 |
| `domain_packets/` | 3 |
| `examples/` | 3 |
| `patches/bank_robo_real/` | 3 |
| `periphery/adapters/` | 3 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (54)

### Documents de référence — à lire en premier

- [BANK_TRADING_GPS_CALIBRATION_WORLDS_V0](../architecture/BANK_TRADING_GPS_CALIBRATION_WORLDS_V0.md) · `docs/architecture/BANK_TRADING_GPS_CALIBRATION_WORLDS_V0.md`
  <br>Bank = économie ; Trading = marché ; GPS = trajectoire/source/temps/énergie.
- [F60 — Sigma Registry Canonical Domains](../architecture/OBSIDIA_F60_SIGMA_REGISTRY_CANONICAL_DOMAINS.md) · `docs/architecture/OBSIDIA_F60_SIGMA_REGISTRY_CANONICAL_DOMAINS.md`
  <br>The Sigma registry exposes four canonical domains. Each domain contains runtime agent instances that evaluate observations and produce advisory votes. No domain decides. No…
- [DOMAIN STACK ONLY — RUNBOOK](../runtime_launchers/DOMAIN_STACK_ONLY_RUNBOOK.md) · `docs/runtime_launchers/DOMAIN_STACK_ONLY_RUNBOOK.md`
  <br>This launcher starts only the domain execution matrix:
- [BANK_ROBO_REAL_BOOT](../BANK_ROBO_REAL_BOOT.md) · `docs/BANK_ROBO_REAL_BOOT.md` *(référence probable)*
  <br>Ce document décrit le boot réel observable de bank-robo depuis server/core/index.ts.
- [BANK_ROBO_REAL_DB_PROBE](../BANK_ROBO_REAL_DB_PROBE.md) · `docs/BANK_ROBO_REAL_DB_PROBE.md` *(référence probable)*
  <br>Ce document sépare les niveaux de validation du raccord réel bank-robo.
- [BANK_ROBO_REAL_PATCH_DELTA](../BANK_ROBO_REAL_PATCH_DELTA.md) · `docs/BANK_ROBO_REAL_PATCH_DELTA.md` *(référence probable)*
  <br>Tracer les deltas locaux ajoutés côté proof-suite par rapport à l'upstream bank-robo.
- [BANK_ROBO_REAL_ROBUSTNESS_PLAN](../BANK_ROBO_REAL_ROBUSTNESS_PLAN.md) · `docs/BANK_ROBO_REAL_ROBUSTNESS_PLAN.md` *(référence probable)*
  <br>Passer de la preuve de raccord à la preuve de robustesse bank sur :
- [Bank Scenarios](../BANK_SCENARIOS.md) · `docs/BANK_SCENARIOS.md` *(référence probable)*
  <br>This file defines the canonical P2 Bank scenarios using the current public bank schema.
- [GPS Reality Authenticity Gate - Activation Note](../investor/GPS_REALITY_AUTHENTICITY_GATE_ACTIVATION_NOTE.md) · `docs/investor/GPS_REALITY_AUTHENTICITY_GATE_ACTIVATION_NOTE.md` *(référence probable)*
  <br>The activation of the Reality Authenticity Gate for the GPS / defense /
- [Obsidia GPS / Defense / Aviation V0.1 - State Matrix](../investor/GPS_V01_STATE_MATRIX.md) · `docs/investor/GPS_V01_STATE_MATRIX.md` *(référence probable)*
  <br>Status date: 2026-08-02
- [GPS_ADAPTER_MAPPING_V0](../periphery/GPS_ADAPTER_MAPPING_V0.md) · `docs/periphery/GPS_ADAPTER_MAPPING_V0.md` *(référence probable)*
  <br>Bloc périphérique non souverain. Sortie attendue : PeripheralSignalPacket.

<details><summary><b>Rapports, audits et preuves d'exécution</b> (21)</summary>

**`docs/`**

- [BANK_OUTPUTS.md](../BANK_OUTPUTS.md) — Bank Outputs
- [BANK_ROBO_REAL_BATCH1000_CONSISTENCY_VALIDATION.md](../BANK_ROBO_REAL_BATCH1000_CONSISTENCY_VALIDATION.md) — BANK_ROBO_REAL_BATCH1000_CONSISTENCY_VALIDATION
- [BANK_ROBO_REAL_BATCH1000_EXISTING_SERVER_RECENT50_VALIDATION.md](../BANK_ROBO_REAL_BATCH1000_EXISTING_SERVER_RECENT50_VALIDATION.md) — BANK_ROBO_REAL_BATCH1000_EXISTING_SERVER_RECENT50_VALIDATION
- [BANK_ROBO_REAL_BATCH1000_PROCESS_ONLY_VALIDATION.md](../BANK_ROBO_REAL_BATCH1000_PROCESS_ONLY_VALIDATION.md) — BANK_ROBO_REAL_BATCH1000_PROCESS_ONLY_VALIDATION
- [BANK_ROBO_REAL_BATCH100_CLIENT_VALIDATION.md](../BANK_ROBO_REAL_BATCH100_CLIENT_VALIDATION.md)
- [BANK_ROBO_REAL_E2E_VALIDATION.md](../BANK_ROBO_REAL_E2E_VALIDATION.md) — BANK_ROBO_REAL_E2E_VALIDATION
- [P2_BANK_CORRECTION_CANONICAL_REPORT.md](../P2_BANK_CORRECTION_CANONICAL_REPORT.md) — P2 BANK - COMPTE-RENDU CANONIQUE DE CORRECTION
- [P2_BANK_SCALE_RESULTS.md](../P2_BANK_SCALE_RESULTS.md) — P2 Bank Scale Results

**`docs/core_import/`** · *dossier lu par du code : ne pas déplacer*

- [P56C_D_ALL_DOMAINS_CORE_RIGOR_AUDIT.json](../core_import/P56C_D_ALL_DOMAINS_CORE_RIGOR_AUDIT.json)
- [P76_GPS_TERRAIN_PORTABLE_RECONCILIATION.json](../core_import/P76_GPS_TERRAIN_PORTABLE_RECONCILIATION.json)
- [P76_GPS_TERRAIN_PORTABLE_RECONCILIATION.md](../core_import/P76_GPS_TERRAIN_PORTABLE_RECONCILIATION.md) — P76 — GPS Terrain Portable Reconciliation

**`docs/investor/`** · *dossier lu par du code : ne pas déplacer*

- [GPS_V01_CLOSURE_REPORT.md](../investor/GPS_V01_CLOSURE_REPORT.md) — GPS V0.1 Closure Report

**`docs/runtime/`** · *dossier lu par du code : ne pas déplacer*

- [BRODY_PHASE12E5_POST_DOMAIN_FIRST_ADAPTIVE_REGRESSION_20260527.md](../runtime/BRODY_PHASE12E5_POST_DOMAIN_FIRST_ADAPTIVE_REGRESSION_20260527.md) — BRODY_PHASE12E5_POST_DOMAIN_FIRST_ADAPTIVE_REGRESSION_20260527
- [BRODY_PHASE12E6_OBSIDIAN_VOICE_DOMAIN_RACCORD_MANIFEST_20260527.json](../runtime/BRODY_PHASE12E6_OBSIDIAN_VOICE_DOMAIN_RACCORD_MANIFEST_20260527.json)
- [F12C_DOMAIN_RACCORD_ADAPTER_ZONE.txt](../runtime/F12C_DOMAIN_RACCORD_ADAPTER_ZONE.txt)
- [F12C_DOMAIN_RACCORD_PRIORITY_AUDIT.txt](../runtime/F12C_DOMAIN_RACCORD_PRIORITY_AUDIT.txt)
- [F37_MULTI_DOMAIN_PROOF_20260529_035506.json](../runtime/F37_MULTI_DOMAIN_PROOF_20260529_035506.json)
- [F38_MULTI_DOMAIN_LIVE_UVICORN_PROOF_20260529_040328.json](../runtime/F38_MULTI_DOMAIN_LIVE_UVICORN_PROOF_20260529_040328.json)
- [OBSIDIA_F12_DOMAIN_RACCORD_PRIORITY_TERMINAL_FREEZE_REPORT_20260527_232708.md](../runtime/OBSIDIA_F12_DOMAIN_RACCORD_PRIORITY_TERMINAL_FREEZE_REPORT_20260527_232708.md) — OBSIDIA F12 — DOMAIN RACCORD PRIORITY + TERMINAL VISIBILITY FREEZE REPORT
- [OBSIDIA_F38_1_MULTI_DOMAIN_LIVE_UVICORN_API_SMOKE_20260529_040328.md](../runtime/OBSIDIA_F38_1_MULTI_DOMAIN_LIVE_UVICORN_API_SMOKE_20260529_040328.md) — OBSIDIA F38 — Multi-Domain Live Uvicorn API Smoke

**`docs/runtime/phase12f_a_api_samples/`** · *dossier lu par du code : ne pas déplacer*

- [domain_friction.json](../runtime/phase12f_a_api_samples/domain_friction.json)

</details>

<details><summary><b>Rapports de phases passées</b> (21)</summary>

**`docs/`**

- [P2_BANK_ADVERSARIAL_SCOPE.md](../P2_BANK_ADVERSARIAL_SCOPE.md) — P2 Bank Adversarial Scope
- [P2_BANK_CONFUSION_MATRIX_SCOPE.md](../P2_BANK_CONFUSION_MATRIX_SCOPE.md) — P2 Bank Confusion Matrix Scope
- [P2_BANK_ENTERPRISE_SCOPE.md](../P2_BANK_ENTERPRISE_SCOPE.md) — P2 Bank Enterprise Scope
- [P2_BANK_FUZZ_SCALE_SCOPE.md](../P2_BANK_FUZZ_SCALE_SCOPE.md) — P2 Bank Fuzz Scale Scope
- [P2_BANK_HARDER_THAN_BUSINESS_CASES.md](../P2_BANK_HARDER_THAN_BUSINESS_CASES.md) — P2 Bank — Harder Than Business Cases
- [P2_BANK_OFFLINE_ERROR_ANALYSIS.md](../P2_BANK_OFFLINE_ERROR_ANALYSIS.md) — P2 Bank Offline Error Analysis
- [P2_BANK_REGULATORY_PROXY_SCOPE.md](../P2_BANK_REGULATORY_PROXY_SCOPE.md) — P2 Bank Regulatory Proxy Scope
- [P2_BANK_SCALE_SCOPE.md](../P2_BANK_SCALE_SCOPE.md) — P2 Bank Scale Scope
- [P2_BANK_SCENARIO_BENCHMARK_SCOPE.md](../P2_BANK_SCENARIO_BENCHMARK_SCOPE.md) — P2 Bank Scenario Benchmark Scope
- [P2_BANK_SCOPE.md](../P2_BANK_SCOPE.md) — P2 Bank Scope
- [P2_BANK_SECURITY_FUZZ_EXTENDED_FAILURES.md](../P2_BANK_SECURITY_FUZZ_EXTENDED_FAILURES.md) — P2 Bank — Security Fuzz Extended Failures
- [P2_BANK_SECURITY_FUZZ_EXTENDED_SCOPE.md](../P2_BANK_SECURITY_FUZZ_EXTENDED_SCOPE.md) — P2 Bank Security Fuzz Extended Scope
- [P2_BANK_SECURITY_FUZZ_SCOPE.md](../P2_BANK_SECURITY_FUZZ_SCOPE.md) — P2 Bank Security Fuzz Scope
- [P2_BANK_SHADOW_MODE_SCOPE.md](../P2_BANK_SHADOW_MODE_SCOPE.md) — P2 Bank Shadow Mode Scope
- [P2_BANK_TEST_SCOPE.md](../P2_BANK_TEST_SCOPE.md) — P2 Bank Test Scope
- [P2_BANK_TRANSPLANT_MAP.md](../P2_BANK_TRANSPLANT_MAP.md) — P2 Bank Transplant Map
- [P2_BANK_TRUTH_PROXY_SCOPE.md](../P2_BANK_TRUTH_PROXY_SCOPE.md) — P2 Bank Truth Proxy Scope

**`docs/runtime/`** · *dossier lu par du code : ne pas déplacer*

- [BRODY_PHASE12E4_B_DOMAIN_RACCORD_READONLY_PATCH_20260527.md](../runtime/BRODY_PHASE12E4_B_DOMAIN_RACCORD_READONLY_PATCH_20260527.md) — BRODY_PHASE12E4_B_DOMAIN_RACCORD_READONLY_PATCH_20260527
- [BRODY_PHASE12E4_C_DOMAIN_VOICE_PRIORITY_PATCH_20260527.md](../runtime/BRODY_PHASE12E4_C_DOMAIN_VOICE_PRIORITY_PATCH_20260527.md) — BRODY_PHASE12E4_C_DOMAIN_VOICE_PRIORITY_PATCH_20260527
- [BRODY_PHASE12E6_OBSIDIAN_VOICE_DOMAIN_RACCORD_FREEZE_20260527.md](../runtime/BRODY_PHASE12E6_OBSIDIAN_VOICE_DOMAIN_RACCORD_FREEZE_20260527.md) — BRODY_PHASE12E6_OBSIDIAN_VOICE_DOMAIN_RACCORD_FREEZE_20260527
- [OBSIDIA_F37_1_MULTI_DOMAIN_USER_SCENARIOS_READONLY_20260529_035506.md](../runtime/OBSIDIA_F37_1_MULTI_DOMAIN_USER_SCENARIOS_READONLY_20260529_035506.md) — OBSIDIA F37 — Multi-Domain User Scenarios Readonly

</details>

<details><summary><b>Archives</b> (1)</summary>

**`docs/runtime/archive/phase10_12_legacy_untracked_20260527/`** · *dossier lu par du code : ne pas déplacer*

- [BRODY_PHASE12E4_A2_DOMAIN_RACCORD_AUDIT_20260527.md](../runtime/archive/phase10_12_legacy_untracked_20260527/BRODY_PHASE12E4_A2_DOMAIN_RACCORD_AUDIT_20260527.md) — BRODY_PHASE12E4_A2_DOMAIN_RACCORD_AUDIT_20260527

</details>

## Fichiers liés au code

27 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
