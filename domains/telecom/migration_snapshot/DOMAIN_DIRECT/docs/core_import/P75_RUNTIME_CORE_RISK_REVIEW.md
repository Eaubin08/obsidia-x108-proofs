# P75 — Runtime Core Risk Review

**Audit ID :** P75  
**Statut :** `P75_RUNTIME_CORE_RISK_REVIEW_READY`  
**Mode :** `AUDIT_ONLY` — aucun patch, aucun import, aucune modification  
**Branche :** `p75-runtime-core-risk-review`  
**Date :** 2026-06-07

---

## 1. Verdict court

| Métrique | Valeur |
|---|---:|
| Fichiers runtime scannés | 33 |
| BLOCK_RUNTIME_IMPORT | 13 |
| BLOCK_UNTIL_FORMAL_REVIEW | 1 |
| KEEP_PROOF_VERSION | 2 |
| ADAPT_READONLY_LATER | 6 |
| ADAPT_DRY_RUN_LATER | 3 |
| IMPORT_TEST_ONLY_LATER | 2 |
| IMPORT_DOC_ONLY_LATER | 2 |
| DO_NOT_IMPORT_DUPLICATE | 4 |
| runtime_decision | **NO_RUNTIME_IMPORT** |
| runtime modifié | NON |
| sigma modifié | NON |
| ACT activé | NON |

**Pourquoi NO_RUNTIME_IMPORT :**  
L'intégralité des composants du moteur core (`engine/`) est soit bloquée (kernel triangle, émetteurs ACT, writes non-gatés, réseau), soit déjà couverte par les preuves existantes (sigma/guard.py, runtime_wiring/x108_admission_stub.py), soit candidate pour un palier futur dédié (os0 readonly, os3 métriques). Aucun import direct n'est possible sans violer les invariants P72 ou les verrous P56D.

---

## 2. Modèle Runtime — catégories de risque

| Catégorie | Description |
|---|---|
| `RUNTIME_KERNEL_MUTATION_BLOCKED` | Kernel d'exécution (run_final, ObsidiaKernel, run_obsidia) — BLOCK PERMANENT |
| `RUNTIME_ACTION_RISK_BLOCKED` | Émetteurs ACT (os1/os1.py, orchestrator, pipeline, api_server/main.py, run_api.sh) |
| `RUNTIME_WRITE_RISK_BLOCKED` | Writes filesystem non-gatés (audit_log, signing, run_attestation, os3/svg) |
| `RUNTIME_NETWORK_RISK_BLOCKED` | Réseau externe boto3 S3 (worm_uploader) |
| `RUNTIME_REQUIRES_FORMAL_REVIEW` | Manipulation sys.path + sys.modules.pop (core_full/adapter.py) |
| `RUNTIME_ALREADY_COVERED_BY_PROOF` | Déjà couverts par sigma/ ou runtime_wiring/ (os1/x108.py, os0/ir.py) |
| `RUNTIME_ADAPTER_CANDIDATE_READONLY` | Logique pure sans side-effect — candidat palier futur readonly |
| `RUNTIME_ADAPTER_CANDIDATE_DRY_RUN` | Logique utile avec DRY_RUN_ONLY — candidat palier futur dry-run |
| `RUNTIME_TEST_ONLY_CANDIDATE` | Tests unitaires OS0 — candidat tests de régression architecturale |
| `RUNTIME_DOC_ONLY_CANDIDATE` | Référence documentaire uniquement (demo, types kernel contract) |
| `RUNTIME_DUPLICATE_OLD_CORE` | Copies vendored (vendor/obsidia_os0/, vendor/obsidia_os1/, vendor/proof/, engine_runtime.py) |

---

## 3. Verrous absolus — P75 AUDIT_ONLY

**VERROU ABSOLU :** Si action/write/network/kernel mutation → `BLOCK_RUNTIME_IMPORT`

| Contrainte | Statut P75 |
|---|:---:|
| Ne pas patcher | RESPECTÉ |
| Ne pas importer | RESPECTÉ |
| Ne pas modifier runtime_wiring | RESPECTÉ |
| Ne pas modifier sigma | RESPECTÉ |
| Ne pas modifier routes | RESPECTÉ |
| Ne pas activer ACT | RESPECTÉ |
| Ne pas lancer serveur | RESPECTÉ |
| Ne pas exécuter runtime core | RESPECTÉ |
| Ne pas appeler réseau | RESPECTÉ |

---

## 4. Composants bloqués — analyse détaillée

### 4.1 Triangle Kernel (RUNTIME_KERNEL_MUTATION_BLOCKED)

| Fichier | Composant | Raison |
|---|---|---|
| `engine/obsidia_kernel/kernel.py` | `ObsidiaKernel.run()` | Kernel central, appelle run_obsidia() → ACT/HOLD/BLOCK |
| `engine/core_full/entrypoint.py` | `run_obsidia()` | Entrypoint kernel, lance run_final(**payload) |
| `engine/obsidia_runtime/engine_final.py` | `run_final()` | Moteur complet OS2+OS1, produit FinalResult(decision=ACT) |

Ces trois composants forment un triangle indissociable. Import brut = exécution du kernel complet. **BLOCK_RUNTIME_IMPORT PERMANENT.** GuardX108 (sigma/guard.py) reste l'autorité finale — Lean-proven `GUARD_X108_FINAL_AUTHORITY`.

### 4.2 Émetteurs ACT (RUNTIME_ACTION_RISK_BLOCKED)

| Fichier | Risque |
|---|---|
| `engine/os1/os1.py` | `OS1Decision(decision='ACT')` hors pipeline sigma/GuardX108 |
| `engine/unified/orchestrator.py` | `_kernel = ObsidiaKernel()` s'exécute à l'**import** (side-effect critique) |
| `engine/unified/pipeline.py` | Délègue à orchestrator.py — mêmes risques par transitivité |
| `engine/api_server/main.py` | FastAPI live + write par requête + route `/v1/decision` |
| `engine/api_server/run_api.sh` | Lance uvicorn — serveur live |

**P75-F2 (critique) :** `orchestrator.py` crée `ObsidiaKernel()` et `build_default_router()` au chargement du module — pas à l'intérieur d'une fonction. Impossible à importer sans lancer le kernel.

### 4.3 Writes non-gatés (RUNTIME_WRITE_RISK_BLOCKED)

| Fichier | Write non-gaté |
|---|---|
| `engine/api_server/audit_log.py` | `open(AUDIT_LOG, 'a')` + `makedirs` à l'import |
| `engine/api_server/signing.py` | `KEY_DIR.mkdir()` + `write_text(priv_pem/pub_pem)` à l'import |
| `engine/api_server/run_attestation.py` | `write_attestation()` + génération clés |
| `engine/os3/svg.py` | `render_core_svg(out_path)` — write SVG non gaté |

P72 invariant `NO_MEMORY_WRITE_WITHOUT_GATE` : tout write requiert un gate explicite.

### 4.4 Réseau externe (RUNTIME_NETWORK_RISK_BLOCKED)

`engine/api_server/worm_uploader.py` : boto3 S3 (`upload_file`, `put_object`, `create_bucket`). Variables d'environnement `OBSIDIA_WORM_ENDPOINT`, `OBSIDIA_WORM_ACCESS_KEY`. P70 invariant `NETWORK_EGRESS_REVIEW_REQUIRED`.

### 4.5 Revue formelle requise (RUNTIME_REQUIRES_FORMAL_REVIEW)

`engine/core_full/modules/os_trad/adapter.py` : `sys.path.insert(0, VENDOR_DIR)` + `sys.modules.pop(k)` pour obsidia_os0, obsidia_os1, proof. Risque d'interférence directe avec sigma/ si importé dans le même process. `BLOCK_UNTIL_FORMAL_REVIEW`.

---

## 5. Candidats pour paliers futurs

### 5.1 ADAPT_READONLY_LATER (6 composants)

| Fichier | Logique | Prérequis |
|---|---|---|
| `engine/os0/contract.py` | Validateur R1-R10 pur | Revue mapping R1-R10 vs P72, BOUNDARY complet |
| `engine/os0/determinism.py` | `canonical_hash()` SHA-256 pur | BOUNDARY complet |
| `engine/os3/metrics.py` | Métriques graphe, gamma=1.0 | Revue formelle OS2/OS3, palier dédié |
| `engine/os3/core_split.py` | Constantes CORE_1BASED/WORLD_1BASED | Dépend de metrics.py |
| `engine/api_server/security.py` | Auth HMAC/JWT (référence) | Import doc uniquement — apps/ a déjà son modèle auth (P68) |
| `engine/api_server/attestation.py` | `build_attestation()` / `sha256_file()` | Retirer makedirs au chargement + isoler write_attestation() |

### 5.2 ADAPT_DRY_RUN_LATER (3 composants)

| Fichier | Logique | Prérequis |
|---|---|---|
| `engine/os0/sandbox.py` | Executor IR déterministique, print=no-op | DRY_RUN_ONLY=True, revue output sémantique |
| `engine/os0/translate.py` | Traducteur python-like → IR (prototype) | DRY_RUN_ONLY=True, revue prototype incomplet |
| `engine/os1/parse_input.py` | AST → IR, ast.parse() standard | Sanitization input + DRY_RUN_ONLY=True |

---

## 6. Composants déjà couverts par les preuves

| Fichier | Couvert par |
|---|---|
| `engine/os1/x108.py` | `runtime_wiring/x108_admission_stub.py` + `sigma/guard.py` (P56D, Lean-proven) |
| `engine/os0/ir.py` | `sigma/contracts.py` (P56B) couvre le modèle de types ; architecture IR séparée |

Décision : `KEEP_PROOF_VERSION` — utiliser la version proof, ne pas réimporter.

---

## 7. Doublons vendored (DO_NOT_IMPORT_DUPLICATE)

| Répertoire | Contenu | Raison |
|---|---|---|
| `engine/core_full/modules/os_trad/vendor/obsidia_os0/` | 9 fichiers — copie exacte de engine/os0/ | Existe pour sys.path de adapter.py uniquement |
| `engine/core_full/modules/os_trad/vendor/obsidia_os1/` | 4 fichiers — copie exacte de engine/os1/ | Idem |
| `engine/core_full/modules/os_trad/vendor/proof/` | 3 fichiers (codegen, runner, Refusal) | Distinct des preuves formelles Lean/TLA du repo |
| `engine/obsidia_runtime/engine_runtime.py` | `assemble_minimal_engine()`, `os.walk('.')` | Couvert par sigma/registry.py (F60) |

---

## 8. Contraintes P72 appliquées

| Invariant P72 | Application P75 |
|---|---|
| `GUARD_X108_FINAL_AUTHORITY` | engine_final/kernel/orchestrator BLOQUÉS — GuardX108 reste l'autorité |
| `NO_ACT_BEFORE_TAU` | os1/os1.py et engine_final.py BLOQUÉS — émettent ACT sans respecter tau |
| `HOLD_BEFORE_TAU` | Pipeline OS1 exécute sans garantie temporelle — BLOQUÉ |
| `IRREVERSIBLE_ACTION_DELAY` | engine_final.py : `irreversible=True` sans tau garanti — BLOQUÉ |
| `NO_KERNEL_MUTATION_FROM_PERIPHERY` | kernel.py/entrypoint.py BLOQUÉS PERMANENT |
| `NO_MEMORY_WRITE_WITHOUT_GATE` | audit_log/signing/attestation/svg BLOQUÉS |
| `NETWORK_EGRESS_REVIEW_REQUIRED` | worm_uploader.py BLOQUÉ — boto3 S3 |
| `NO_PERIPHERY_DECISION_AUTHORITY` | os3/metrics.py `decision_act_hold()` = score advisory uniquement |
| `DETERMINISM` | os0/ir.py, os0/contract.py, os0/sandbox.py, os3/metrics.py — déterministes, candidats readonly |
| `ROUTE_AUTH_BOUNDARY` | api_server/main.py BLOQUÉ — serveur live double non autorisé (P68) |
| `DRY_RUN_ONLY_ADAPTERS` | Tout adapter futur (os0, os3) devra `DRY_RUN_ONLY=True` |
| `KX108_ONLY_DECISION_AUTHORITY` | Aucun composant core ne peut prendre de décision souveraine |

### Contraintes P74 sigma appliquées

| Contrainte P74 | Application P75 |
|---|---|
| `SIGMA_POST_GUARD_VETO_ONLY` | sigma/ non modifié — aucun composant core ne bypass `apply_sigma()` |
| `GUARD_X108_FINAL_AUTHORITY` | sigma/guard.py reste l'autorité finale — os1/x108.py `KEEP_PROOF_VERSION` |
| `NO_GAMMA_05` | os3/metrics.py gamma=1.0 par défaut — confirmé |
| `NO_KERNEL_MUTATION` | Aucun import core ne modifie sigma/guard.py, run_pipeline.py, obsidia_sigma_v130.py |

---

## 9. Findings

| ID | Type | Composant | Action |
|---|---|---|---|
| P75-F1 | CRITICAL_BLOCKED | kernel.py + entrypoint.py + engine_final.py | BLOCK_RUNTIME_IMPORT PERMANENT |
| P75-F2 | CRITICAL_BLOCKED | unified/orchestrator.py | BLOCK_RUNTIME_IMPORT (side-effect import) |
| P75-F3 | HIGH_BLOCKED | os1/os1.py | BLOCK_RUNTIME_IMPORT (émetteur ACT) |
| P75-F4 | VERIFIED_SAFE_FOR_LATER | os0/ (ir, contract, sandbox, determinism) | ADAPT_READONLY_LATER / ADAPT_DRY_RUN_LATER |
| P75-F5 | VERIFIED_SAFE_FOR_LATER | os3/metrics.py + os3/core_split.py | ADAPT_READONLY_LATER |
| P75-F6 | HIGH_BLOCKED | core_full/modules/os_trad/adapter.py | BLOCK_UNTIL_FORMAL_REVIEW |
| P75-F7 | AUDIT_CARRY_FORWARD | api_server/audit_log.py (logique hash chain) | ADAPT_READONLY_LATER (hash seul) |

**P75-F7 détail :** La logique de hash chain `h_i = sha256(h_{i-1} || json(event))` est architecturalement correcte et complémentaire des preuves RFC3161 du repo. L'implémentation courante écrit sans gate. La logique de hash seule est candidate ADAPT_READONLY_LATER dans un palier futur.

---

## 10. Décision

P75 conclut que **aucun composant runtime core ne peut être importé directement** dans le repo proof en l'état actuel.

**NO_RUNTIME_IMPORT — justification :**
- Triangle kernel (engine_final + entrypoint + ObsidiaKernel) : BLOCK PERMANENT.
- Émetteurs ACT (os1.py, orchestrator.py) : BLOCK jusqu'à preuve formelle.
- Writes non-gatés (audit_log, signing, attestation, svg) : P72 `NO_MEMORY_WRITE_WITHOUT_GATE`.
- Réseau externe (worm_uploader boto3) : P70 gate requis.
- sys.modules.pop (adapter.py) : BLOCK jusqu'à revue formelle d'interférence sigma/.
- Déjà couverts (os1/x108.py, os0/ir.py) : KEEP_PROOF_VERSION — pas de réimport.

**Candidats pour paliers futurs (sans import aujourd'hui) :**
- os0/ (contract, determinism, sandbox, translate, parse_input) — palier dédié requis.
- os3/ (metrics, core_split) — revue formelle OS2/OS3 requise.
- api_server/audit_log.py (hash logic only) — extraction isolée requise.

**sigma/ et runtime_wiring/ non modifiés.** GuardX108 reste l'autorité finale. gamma=1.0 confirmé.

**Prochain geste : P76 — GPS Terrain Portable Reconciliation.**

---

**Verdict :** `P75_RUNTIME_CORE_RISK_REVIEW_READY`
