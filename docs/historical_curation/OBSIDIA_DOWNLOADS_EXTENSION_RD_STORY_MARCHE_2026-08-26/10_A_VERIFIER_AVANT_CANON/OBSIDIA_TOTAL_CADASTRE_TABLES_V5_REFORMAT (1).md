# OBSIDIA — CADASTRE TABLES V5 REFORMAT

## 0. Master counts

| Bloc | Count | Lecture | Statut |
|---|---:|---|---|
| GitHub F77 officiel | 4506 | runtime/docs/tests/proofs stabilisés | officiel / pushé |
| Local pré-freeze | 340 | specs/contracts/source matter | non tracké / en build |
| Zips sources uniques | 2842 | Atlas, Cognitive, RSSI, NPL, External Signals | source base |
| V4 corps historique | 2606 références composant | Brody memory, pépites, arbres, agents, modules, guards | non dédupliqué |
| Total brut utile avant dédup | 7688 | GitHub + local + zips sources | cadastre utile |
| Full filesystem audit | 24430 | inclut audits locaux massifs | trop large / non canon |
| FastAPI routes détectées | 151 | surface API | runtime map |

## 1. Corpus GitHub F77 officiel — regroupement canonique

| Groupe | Count | Composition | Action |
|---|---:|---|---|
| `40_RUNTIME_APPS` | 149 | API runtime, routes, bus, Brody adapters, Graphiti client, Workbench | `SPLIT_REQUIRED` |
| `41_RUNTIME_PERIPHERY` | 2599 | corps historique : Brody memory, pépites, arbres, agents, modules, guards | `SPLIT_REQUIRED` |
| `42_RUNTIME_SIGMA` | 78 | Sigma registry/dispatcher/packets/connectors/domains | `KEEP_RUNTIME` |
| `43_DOCS_ARCHITECTURE` | 777 | docs architecture/runtime/audit/release/demo/risk | `SPLIT_REQUIRED` |
| `44_TESTS` | 264 | tests api/sigma/brody/bus/periphery/non-sovereignty | `SPLIT_REQUIRED` |
| `45_PROOFS` | 185 | proof artifacts / replay / formal-adjacent | `KEEP_PROOF` |
| `46_SCRIPTS` | 147 | scripts audit/test/freeze/hardening | `KEEP_PROOF` |
| `47_EXTERNAL_PACK` | 11 | review pack public F77 | `KEEP_PUBLIC_PACK` |

### 1.1 `apps/` — split utile

| Sous-groupe apps | Count | Lecture | Action |
|---|---:|---|---|
| `WORKBENCH_UI` | 69 | UI / workbench / frontend + rapports locaux | `KEEP_RUNTIME` |
| `API_ROUTES` | 19 | routes FastAPI | `KEEP_RUNTIME` |
| `BUS_RUNTIME` | 5 | apps/obsidia_api/bus | `KEEP_RUNTIME` |
| `GRAPHITI_CLIENT` | 2 | graphiti_env_loader + graphiti_v20_readonly_client | `KEEP_RUNTIME` |
| `CORE_API_SPINE` | 4 | main.py, auth.py, safe_response.py, output_envelope.py | `KEEP_RUNTIME` |
| `BRODY_RUNTIME_ADAPTERS` | 50 | Brody response, memory, tree, thermo, gencoin, domain raccord, lifecycle | `KEEP_RUNTIME / SPLIT_LATER` |

### 1.2 `periphery/` — corps historique / cognitif V4

| Corpus | Sous-groupe | Count | Action | Lecture |
|---|---|---:|---|---|
| `BRODY_MEMORY_READONLY` | `BRODY_MEMORY_ALL` | 498 | `KEEP_RUNTIME` | Mémoire Brody / Graphiti readonly / adapters mémoire |
| `OBSIDIA_V4_STRUCTURED_FULL` | `REGROUPEMENTS_COHERENCE` | 450 | `REGROUP_CANON` | Regroupements de cohérence du vieux corps V4 |
| `MMONDE_REVERSE_OS_34ARBRES` | `ARBRES_34_TENSOR_MATRIX` | 428 | `REGROUP_CANON` | 34 arbres / matrice tensorielle / Tree34 |
| `OBSIDIA_V4_STRUCTURED_FULL` | `PREUVES_LEAN_TLA` | 233 | `KEEP_PROOF` | Preuves Lean/TLA/formal/proofs |
| `OBSIDIA_V4_STRUCTURED_FULL` | `PEPITES_161` | 162 | `REGROUP_CANON` | Pépites sémantiques historiques |
| `CORE_AUTHORITY` | `X108_KX108` | 133 | `KEEP_CANON` | Surface X108/KX108 + specs authority |
| `SIGMA_LAYER` | `SIGMA_RUNTIME` | 88 | `KEEP_RUNTIME` | Sigma registry / dispatcher / packets / tests / route |
| `TESTS_PERIPHERY` | `PERIPHERY_TESTS` | 81 | `KEEP_PROOF` | Tests périphériques |
| `APPS_WORKBENCH` | `WORKBENCH_UI` | 69 | `KEEP_RUNTIME` | Workbench UI |
| `MMONDE_REVERSE_OS_34ARBRES` | `AGENTS_52` | 65 | `REGROUP_CANON` | 52 agents |
| `OBSIDIA_V4_STRUCTURED_FULL` | `MODULES_A1_A24` | 50 | `DEDUP_AND_REGROUP` | Modules A1→A24 |
| `WORKFLOW_GOVERNANCE` | `WORKFLOW_GOVERNANCE_READONLY` | 46 | `KEEP_RUNTIME` | Workflow governance readonly |
| `OBSIDIA_V4_STRUCTURED_FULL` | `AGENTS_ROLES` | 44 | `DEDUP_AND_REGROUP` | Agents et rôles V4 |
| `OBSIDIA_V4_STRUCTURED_FULL` | `SPECS_40` | 41 | `DEDUP_WITH_SPECS` | Anciennes specs V4 à réconcilier avec specs/ |
| `TESTS_NON_SOVEREIGNTY` | `NON_SOVEREIGNTY_TESTS` | 35 | `KEEP_PROOF` | Tests non-souveraineté |
| `OBSIDIA_V4_STRUCTURED_FULL` | `GARDIENS_T1_T12` | 26 | `DEDUP_AND_REGROUP` | Gardiens T1→T12 |
| `MMONDE_REVERSE_OS_34ARBRES` | `CONSTITUTION_LOIS_OBSIDIENNES` | 20 | `REGROUP_CANON` | Lois obsidiennes / constitution |
| `MMONDE_REVERSE_OS_34ARBRES` | `REVERSE_OS_SSR_JARVIS` | 20 | `KEEP_AND_DEDUP` | Reverse OS / SSR / Jarvis |
| `MMONDE_REVERSE_OS_34ARBRES` | `MEMOIRE_MONDE_COSMOS_REFLEX` | 20 | `REGROUP_CANON` | Mémoire monde / cosmos / réflexe |
| `MMONDE_REVERSE_OS_34ARBRES` | `MCP_BRIDGE_OBSIDIA_IR` | 19 | `REGROUP_CANON` | MCP bridge / Obsidia IR |
| `OBSIDIA_V4_STRUCTURED_FULL` | `BLOCS_17` | 18 | `REGROUP_CANON` | 17 blocs fondateurs |
| `MMONDE_REVERSE_OS_34ARBRES` | `GRAPHES_NUAGE_POINTS` | 12 | `REGROUP_CANON` | Graphes / nuage / points |
| `MMONDE_REVERSE_OS_34ARBRES` | `FRICTION_AVDR_CONTINUUM` | 11 | `REGROUP_CANON` | Friction / AVDR / continuum |
| `BUS_LAYER` | `BUS_RUNTIME` | 10 | `KEEP_RUNTIME` | Bus runtime |
| `MMONDE_REVERSE_OS_34ARBRES` | `HEXAFLUX_LTCU_MUTATIONS` | 9 | `REGROUP_CANON` | Hexaflux / LTCU / mutations |
| `MMONDE_REVERSE_OS_34ARBRES` | `BDF_DOUBLE_CERVEAU` | 9 | `REGROUP_CANON` | BDF double cerveau |
| `MMONDE_REVERSE_OS_34ARBRES` | `SHAZAM_COGNITIF` | 9 | `REGROUP_CANON` | Shazam cognitif |

### 1.3 `docs/` — split visible / logique

| Sous-groupe docs | Count | Source / lecture |
|---|---:|---|
| `GENCOIN_SANDBOX_PRE_FREEZE` | 23 | docs/gencoin/sandbox_pre_freeze |
| `F12B_QUALITY_PARITY` | 19 | docs/runtime/f12b_quality_parity |
| `RUNTIME_ARCHIVE` | 17 | docs/runtime/archive |
| `BRODY_RIGHTS_AUTHORITY_FREEZE` | 7 | docs/freeze/BRODY_RIGHTS_AUTHORITY |
| `API_SAMPLES_PHASE12F` | 4 | docs/runtime/phase12f_a_api_samples |
| `ENV_CONTRACTS` | 2 | docs/contracts/env |
| `FULL_TEST_MATRIX_RECONCILIATION` | 2 | docs/freeze/FULL_TEST_MATRIX_RECONCILIATION |
| `RUNTIME_SINGLE_REPORTS` | reste | nombreux rapports runtime isolés F4→F77 |

### 1.4 `tests/` — familles de tests

| Famille tests | Count | Lecture |
|---|---:|---|
| `NON_SOVEREIGNTY_TESTS` | 35 | no ACT, no decision, no write, no mint, no bypass |
| `PERIPHERY_TESTS` | 81 | balance, tree, entropy, reverse OS, token policy, periphery validation |
| `SIGMA_TESTS` | F60-F73 | registry, dispatcher, packets, connectors, orchestrator, graphiti bridge, trees |
| `API_TESTS` | présent | Brody, Bus, Sigma endpoints, OS Trad, security, F76B |
| `LEGACY_ROOT_TESTS` | 3 | tests/legacy_root/gate_engine_v4 |

## 2. Local pré-freeze — 340 fichiers

### 2.1 Specs locales — 212 fichiers

| Sous-corpus specs | Count | Lecture |
|---|---:|---|
| `00_SCOPE_DISCIPLINE` | 9 | claim discipline / dry-run / public proof |
| `01_X108_AUTHORITY` | 7 | KX108 / no bypass / temporal gate |
| `02_INTERLAYER_CONSTITUTION` | 8 | constitution inter-couches |
| `03_ENTROPY_DISCIPLINE` | 11 | entropy / semantic heat / Lyapunov |
| `04_AGI_TREE34_FLUX` | 5 | Tree34 / AGI flux |
| `05_BALANCE_BUV_GEOMETRIES` | 9 | BUV / balance / geometries |
| `06_HIGH_PERIPHERY_SYSTEMS` | 7 | double brain / Reverse OS / Shazam |
| `07_AGENTS_CONNECTORS_MCP` | 10 | agents / tools / MCP |
| `08_MEMORY_BRODY_GRAPHITI` | 7 | mémoire / Brody / Graphiti |
| `09_CRITICAL_WORLDS` | 14 | bank / trading / GPS / aviation |
| `10_VALUE_GENCOIN_JCOIN` | 11 | value / Gencoin / Jcoin |
| `11_PROOF_REPLAY_OS3` | 9 | OS3 / proof / replay |
| `12_NARRATIVE_PROVENANCE_LAYER` | 34 | NPL / culture / récit / mémoire |
| `external_signals` | 39 | Timeverse / temporal sidecar |
| `_imports_readonly` | 17 | imports sources readonly |
| `_source_index` | 7 | source → spec/runtime/claim maps |
| `_invariant_graph` | 2 | invariant graph / Lean delta |
| `root specs` | 6 | index / registry / guides |

### 2.2 Runtime contracts — 46 fichiers

| Sous-corpus contracts | Count | Lecture |
|---|---:|---|
| `boundaries` | 13 | boundaries runtime |
| `contracts` | 7 | contrats markdown |
| `schemas` | 7 | schemas JSON |
| `dry_run` | 4 | dry-run général |
| `external_signals_dry_run` | 8 | signaux externes dry-run |
| `reports/index/other` | 7 | rapports / README / compléments |

### 2.3 Source provenance / backlog

| Bloc local | Count | Lecture | Action |
|---|---:|---|---|
| `_source_discovery` | 36 | audits source/provenance | KEEP_SOURCE_ONLY |
| `_source_packs` | 16 | backlog source strict pattern | KEEP_SOURCE_ONLY |
| `docs/source_packs` | 4 | docs de source packs | KEEP_SOURCE_ONLY |
| `.local_audits` | 22 | audit temporaire | EXCLUDE_TEMP |

## 3. Zips sources uniques — 2842 fichiers

| Corpus zip | Count | Lecture |
|---|---:|---|
| `ATLAS_CORPUS` | 1738 | `OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS.zip` |
| `COGNITIVE_REINTEGRATION_CORPUS` | 513 | `OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL(1).zip` |
| `NPL_CORPUS` | 103 | `OBSIDIA_NARRATIVE_PROVENANCE_LAYER_SPEC_PACK_V1_MAX.zip` |
| `EXTERNAL_SIGNALS_CORPUS` | 41 | `OBSIDIA_RSSI_EXTERNAL_SIGNALS_PATCH_V1.zip` |
| `RSSI_RGPD_ISO_CORPUS` | 280 | `OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2.zip` |
| `RSSI_SECURITY_PRESENTATION_CORPUS` | 167 | `OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1.zip` |

### 3.x ATLAS_CORPUS — 1738 fichiers

Zip: `OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS.zip`

#### Groupes internes

| Groupe interne | Count |
|---|---:|
| `docs` | 1639 |
| `periphery` | 28 |
| `.runtime_freezes` | 24 |
| `registry` | 7 |
| `.pytest_cache` | 5 |
| `tests` | 4 |
| `COMPLETION_AUDIT_V0_3.json` | 1 |
| `COMPLETION_AUDIT_V0_3.md` | 1 |
| `DEEP_FINAL_AUDIT_V0_5.json` | 1 |
| `DEEP_FINAL_AUDIT_V0_5.md` | 1 |
| `FILE_INDEX_COMPLETE.md` | 1 |
| `FINAL_NO_MISSING_CHECK_V0_3.json` | 1 |
| `FINAL_PASS_AUDIT_V0_6.json` | 1 |
| `FINAL_PASS_AUDIT_V0_6.md` | 1 |
| `FINAL_PASS_AUDIT_V0_7.json` | 1 |
| `FINAL_PASS_AUDIT_V0_7.md` | 1 |
| `FINAL_SELF_CHECK_V0_5.json` | 1 |
| `GAP_REPORT_V0_TO_V0_1.md` | 1 |
| `MANIFEST_SHA256_ALL_FILES.json` | 1 |
| `MANIFEST_SHA256_ALL_FILES_V0_1.json` | 1 |
| `MANIFEST_SHA256_ALL_FILES_V0_1_VERIFIED.json` | 1 |
| `MANIFEST_SHA256_ALL_FILES_V0_2_METRICS_FILLED.json` | 1 |
| `MANIFEST_SHA256_ALL_FILES_V0_3_COMPLETION_AUDIT.json` | 1 |
| `MANIFEST_SHA256_ALL_FILES_V0_4_SPECIFIC_METRICS.json` | 1 |
| `MANIFEST_SHA256_ALL_FILES_V0_5_DEEP_FINAL_AUDIT.json` | 1 |
| `MANIFEST_SHA256_ALL_FILES_V0_6_FINAL_PASS.json` | 1 |
| `MANIFEST_SHA256_ALL_FILES_V0_7_FINAL_PASS.json` | 1 |
| `NO_REPO_MUTATION_NOTICE.md` | 1 |
| `README.md` | 1 |
| `TEST_OUTPUT.txt` | 1 |
| `TEST_OUTPUT_V0_1.txt` | 1 |
| `TEST_OUTPUT_V0_2.txt` | 1 |
| `TEST_OUTPUT_V0_3.txt` | 1 |
| `TEST_OUTPUT_V0_4.txt` | 1 |
| `VERIFICATION_REPORT_V0_1.json` | 1 |
| `VERIFICATION_REPORT_V0_1.md` | 1 |
| `patches` | 1 |

#### Catégories internes

| Catégorie | Count |
|---|---:|
| `DOCS` | 1620 |
| `REGISTRY` | 25 |
| `PERIPHERY` | 18 |
| `TESTS` | 17 |
| `FREEZE` | 17 |
| `AUDIT` | 17 |
| `OTHER` | 13 |
| `METRICS` | 8 |
| `PACKETS` | 3 |

#### Extensions

| Extension | Count |
|---|---:|
| `.md` | 1241 |
| `.json` | 453 |
| `.py` | 18 |
| `.pyc` | 15 |
| `.txt` | 7 |
| `[none]` | 3 |
| `.tag` | 1 |

### 3.x COGNITIVE_REINTEGRATION_CORPUS — 513 fichiers

Zip: `OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL(1).zip`

#### Groupes internes

| Groupe interne | Count |
|---|---:|
| `component_specs` | 458 |
| `family_specs` | 25 |
| `schemas` | 8 |
| `packets` | 5 |
| `11_AUTHORITY_MODEL.md` | 1 |
| `proof` | 1 |
| `tests` | 1 |
| `09_FORMULA_DICTIONARY.md` | 1 |
| `10_INVARIANTS.md` | 1 |
| `05_LEGACY_TO_KERNEL_BOUNDARY.md` | 1 |
| `06_COMPONENT_INDEX.csv` | 1 |
| `08_METRIC_DICTIONARY.yaml` | 1 |
| `53_IMPLEMENTATION_ROADMAP.md` | 1 |
| `54_FREEZE_MANIFEST.yaml` | 1 |
| `01_README.md` | 1 |
| `55_HASHES.sha256` | 1 |
| `02_SCOPE_AND_DECISION.md` | 1 |
| `03_SOURCE_INVENTORY.md` | 1 |
| `12_QUARANTINE_REGISTRY.md` | 1 |
| `04_CANON_MAP.md` | 1 |
| `07_COMPONENT_SPEC_MATRIX.csv` | 1 |

#### Catégories internes

| Catégorie | Count |
|---|---:|
| `COMPONENT_SPECS` | 458 |
| `FAMILY_SPECS` | 25 |
| `OTHER` | 10 |
| `PACKETS` | 6 |
| `SCHEMAS` | 4 |
| `TESTS` | 2 |
| `BOUNDARY_INVARIANT` | 2 |
| `METRICS` | 2 |
| `REGISTRY` | 2 |
| `PROOF` | 1 |
| `FREEZE` | 1 |

#### Extensions

| Extension | Count |
|---|---:|
| `.yaml` | 490 |
| `.md` | 12 |
| `.json` | 8 |
| `.csv` | 2 |
| `.sha256` | 1 |

### 3.x NPL_CORPUS — 103 fichiers

Zip: `OBSIDIA_NARRATIVE_PROVENANCE_LAYER_SPEC_PACK_V1_MAX.zip`

#### Groupes internes

| Groupe interne | Count |
|---|---:|
| `05_METRICS` | 13 |
| `10_EXTERNAL_REFERENCES` | 11 |
| `03_SIGNALS` | 10 |
| `11_ADVANCED_PROVENANCE` | 10 |
| `06_OBSIDIA_BRANCHING` | 8 |
| `02_CORE_CONCEPTS` | 7 |
| `07_ADVERSARIAL_RISKS` | 7 |
| `08_TESTS_REQUIRED` | 7 |
| `00_INDEX` | 6 |
| `09_AUDIT` | 6 |
| `01_MASTER_SPEC` | 5 |
| `04_PACKET_SCHEMA` | 5 |
| `CLAIM_SCOPE_LIMITS.md` | 1 |
| `MANIFEST.md` | 1 |
| `MANIFEST_SHA256.json` | 1 |
| `PACK_STATUS.md` | 1 |
| `README.md` | 1 |
| `SOURCE_CONTEXT.md` | 1 |
| `VALIDATION_REPORT.md` | 1 |
| `VALIDATION_REPORT_TEMPLATE.md` | 1 |

#### Catégories internes

| Catégorie | Count |
|---|---:|
| `OTHER` | 59 |
| `METRICS` | 14 |
| `PACKETS` | 8 |
| `AUDIT` | 7 |
| `BOUNDARY_INVARIANT` | 6 |
| `TESTS` | 6 |
| `REGISTRY` | 3 |

#### Extensions

| Extension | Count |
|---|---:|
| `.md` | 102 |
| `.json` | 1 |

### 3.x EXTERNAL_SIGNALS_CORPUS — 41 fichiers

Zip: `OBSIDIA_RSSI_EXTERNAL_SIGNALS_PATCH_V1.zip`

#### Groupes internes

| Groupe interne | Count |
|---|---:|
| `component_specs` | 24 |
| `merge_appendices` | 5 |
| `family_specs` | 3 |
| `packets` | 3 |
| `MERGE_INSTRUCTIONS.md` | 1 |
| `README.md` | 1 |
| `SHA256SUMS.txt` | 1 |
| `VALIDATION_REPORT.yaml` | 1 |
| `proof` | 1 |
| `tests` | 1 |

#### Catégories internes

| Catégorie | Count |
|---|---:|
| `COMPONENT_SPECS` | 24 |
| `OTHER` | 7 |
| `FAMILY_SPECS` | 3 |
| `PACKETS` | 3 |
| `METRICS` | 1 |
| `BOUNDARY_INVARIANT` | 1 |
| `PROOF` | 1 |
| `TESTS` | 1 |

#### Extensions

| Extension | Count |
|---|---:|
| `.yaml` | 32 |
| `.md` | 6 |
| `.csv` | 2 |
| `.txt` | 1 |

### 3.x RSSI_RGPD_ISO_CORPUS — 280 fichiers

Zip: `OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2.zip`

#### Groupes internes

| Groupe interne | Count |
|---|---:|
| `docs` | 129 |
| `rssi` | 15 |
| `.runtime_freezes` | 14 |
| `rgpd` | 14 |
| `iso27001` | 13 |
| `tests` | 12 |
| `periphery` | 11 |
| `ai_security` | 11 |
| `security` | 10 |
| `data_governance` | 10 |
| `audit` | 9 |
| `registry` | 8 |
| `deployment` | 8 |
| `legal` | 8 |
| `README.md` | 1 |
| `FILE_INDEX_COMPLETE.md` | 1 |
| `MANIFEST_SHA256_ALL_FILES.json` | 1 |
| `FINAL_RSSI_AUDIT_REPORT.md` | 1 |
| `FINAL_RSSI_AUDIT_REPORT.json` | 1 |
| `FINAL_RSSI_SELF_CHECK.json` | 1 |
| `TEST_OUTPUT_RSSI_PACK_V1.txt` | 1 |
| `TEST_OUTPUT_RSSI_PACK_V2.txt` | 1 |

#### Catégories internes

| Catégorie | Count |
|---|---:|
| `DOCS` | 120 |
| `OTHER` | 87 |
| `AUDIT` | 25 |
| `TESTS` | 17 |
| `REGISTRY` | 15 |
| `PERIPHERY` | 7 |
| `FREEZE` | 6 |
| `METRICS` | 3 |

#### Extensions

| Extension | Count |
|---|---:|
| `.md` | 229 |
| `.json` | 26 |
| `.py` | 23 |
| `.txt` | 2 |

### 3.x RSSI_SECURITY_PRESENTATION_CORPUS — 167 fichiers

Zip: `OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1.zip`

#### Groupes internes

| Groupe interne | Count |
|---|---:|
| `docs` | 129 |
| `periphery` | 11 |
| `registry` | 8 |
| `.runtime_freezes` | 7 |
| `tests` | 5 |
| `FILE_INDEX_COMPLETE.md` | 1 |
| `FINAL_RSSI_AUDIT_REPORT.json` | 1 |
| `FINAL_RSSI_AUDIT_REPORT.md` | 1 |
| `FINAL_RSSI_SELF_CHECK.json` | 1 |
| `MANIFEST_SHA256_ALL_FILES.json` | 1 |
| `README.md` | 1 |
| `TEST_OUTPUT_RSSI_PACK_V1.txt` | 1 |

#### Catégories internes

| Catégorie | Count |
|---|---:|
| `DOCS` | 120 |
| `AUDIT` | 13 |
| `REGISTRY` | 12 |
| `PERIPHERY` | 7 |
| `TESTS` | 5 |
| `OTHER` | 4 |
| `FREEZE` | 3 |
| `METRICS` | 3 |

#### Extensions

| Extension | Count |
|---|---:|
| `.md` | 132 |
| `.json` | 18 |
| `.py` | 16 |
| `.txt` | 1 |

## 4. Source base fichiers racine

| Corpus racine | Count | Lecture |
|---|---:|---|
| `RAW_MARKDOWN_SOURCE` | 5 | fichier source racine |
| `ATLAS_CORPUS` | 1 | fichier source racine |
| `COGNITIVE_REINTEGRATION_CORPUS` | 1 | fichier source racine |
| `IMPLEMENTATION_PLAN_XLSX` | 1 | fichier source racine |
| `NPL_CORPUS` | 1 | fichier source racine |
| `EXTERNAL_SIGNALS_CORPUS` | 1 | fichier source racine |
| `RSSI_RGPD_ISO_CORPUS` | 1 | fichier source racine |
| `RSSI_SECURITY_PRESENTATION_CORPUS` | 1 | fichier source racine |
| `VALIDATION_REPORT` | 1 | fichier source racine |

### XLSX implementation plan

| Workbook | Sheets |
|---|---|
| `OBSIDIA_IMPLEMENTATION_PLAN_FILE_BY_FILE_V1.xlsx` | README, SUMMARY, IMPLEMENT_ORDER, FILE_PLAN_ALL, EXT_SIGNALS, RSSI_SECURITY, COGNITIVE, ATLAS, RGPD_ISO, ACTION_COUNTS |

## 5. Validations connues

| Bloc | Résultat |
|---|---|
| `F60_SIGMA_REGISTRY` | 110 passed |
| `F61_SIGMA_DISPATCHER` | 207 passed |
| `F62_SIGMA_PACKETS` | 205 passed |
| `F63_SIGMA_ENDPOINTS` | 195 passed |
| `F64_SIGMA_CONNECTORS` | 70 passed |
| `F65_SIGMA_BUS_BRIDGE` | 85 passed |
| `BUS_LAYER` | 103 passed |
| `F47_HARDENING` | sovereignty/sanitizer/nested scan PASS |

## 6. Lecture finale

```txt
GitHub F77 = base officielle stabilisée.
Local pré-freeze = specs/contracts/source matter en cours de canonisation.
Zips sources = minerai structuré à mapper/dédupliquer.
V4 corps historique = vraie matière cognitive/sémantique : pépites, arbres, agents, modules, gardiens, lois, mémoire.
V5 total = 7688 fichiers/instances utiles avant déduplication.
```
