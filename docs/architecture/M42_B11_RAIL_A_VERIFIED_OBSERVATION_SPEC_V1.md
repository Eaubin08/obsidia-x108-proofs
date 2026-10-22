# M42 B11 Compétence & Calibration — Spécification de l'Adaptateur d'Observations Vérifiées Rail A (`tooling_build`) V1

## 1. Statut, périmètre et frontière doctrinale

- **Chapitre :** M42 — B11 Compétence et Calibration (Étage 1 : Acquisition d'observations d'exécution vérifiées).
- **Couche :** Cognition / Pré-forge / Gouvernance périphérique (`app/cognition/b11/`).
- **Rail couvert :** Rail A (`tooling_build` — remédiation gouvernée `C1 -> C2 -> D1 -> D2`). Le Rail B (`AGENT_PRE_EXECUTION`) demeure en `HOLD` en l'absence de reçu post-exécution scellé.
- **Mode d'autorité :** Lecture seule stricte, non-souverain, consultatif (`B11_EFFECTS` : `memory_write=False`, `emits_act=False`, `kernel_mutation=False`, `decision_authority="KX108_ONLY"`, `advisory_only=True`, `b12_selection=False`).
- **Frontière doctrinale de la tranche V1 :**
  - Cet adaptateur établit uniquement qu'une **observation d'exécution** du domaine `tooling_build` est cryptographiquement intègre, cohérente sur toute sa chaîne d'artefacts et chargée depuis des stores contrôlés.
  - **Aucune formule de score de fiabilité, aucune formule de confiance de compétence, aucun seuil $N_{\min}$, aucune calibration empirique (`calibration_metric`) et aucune promotion en `EVIDENCED_COMPETENCE` ou `EVIDENCED_INCOMPETENCE` ne sont activés dans cette tranche.**
  - Tant que ces paramètres doctrinaux ne sont pas approuvés, `evaluate_contextual_competence` conserve impérativement `CompetenceRegime.UNKNOWN_COMPETENCE` avec `confidence_score=0.0`, `reliability_score=None` et `calibration_metric=None`.

---

## 2. Modèle d'entrée et résolution depuis les stores contrôlés

1. **Interdiction des payloads auto-déclarés :**
   L'adaptateur n'accepte jamais un dictionnaire ou un objet fourni en mémoire déclarant `is_verified=True` ou `is_authenticated=True` (règle `FC-02`).
2. **Résolution par identifiant racine et chemins de stores explicites :**
   L'entrée de `load_and_verify_rail_a_observation` est exclusivement un identifiant de décision post-exécution `kxpost_decision_record_id: str` (préfixe `kxpost-`) accompagné des chemins explicites des répertoires de stores :
   - `kx108_decision_dir: Path`
   - `pre_execution_context_dir: Path`
   - `sealed_receipt_dir: Path`
   - `sealed_rollback_evidence_dir: Path`
   - `test_contract_results_dir: Path`
   - Optionnellement : `closure_id: str | None = None` et `execution_closures_dir: Path | None = None`.
3. **Déréférencement en lecture seule des 6 artefacts canoniques :**
   - `kxpost` est chargé depuis `kx108_decision_dir` via `load_kx108_decision_record`.
   - Depuis `kxpost`, l'adaptateur extrait et charge :
     - `kxpre` (`kxpost["kx108_pre_decision_record_id"]`) depuis `kx108_decision_dir` via `load_kx108_decision_record` ;
     - `sar` (`kxpost["sealed_apply_receipt_id"]`) depuis `sealed_receipt_dir` via `load_sealed_apply_receipt` ;
     - `sre` (`kxpost["sealed_rollback_evidence_id"]`) depuis `sealed_rollback_evidence_dir` via `load_sealed_rollback_evidence` ;
     - `tcr` (`kxpost["test_result_id"]`) depuis `test_contract_results_dir` via `load_test_contract_result`.
   - Depuis `kxpre`, l'adaptateur extrait et charge :
     - `pec` (`kxpre["pre_execution_context_id"]`) depuis `pre_execution_context_dir` via `load_pre_execution_context_record`.
   - Si `closure_id` est fourni, `clo` est chargé depuis `execution_closures_dir` via `load_execution_closure_record`.

---

## 3. Matrice des vérificateurs canoniques réutilisés

Chaque artefact chargé doit passer son vérificateur canonique de production (`(True, None)`) avant tout contrôle de liaison croisée :

| Artefact | Module source | Vérificateur appelé | Garantie établie par le vérificateur |
|---|---|---|---|
| `pec` (`pec-*`) | `scripts/obsidia_pre_execution_context.py` | `verify_pre_execution_context_record(pec)` | Schéma V1/V2 supporté, champs liés présents, `decision_authority == "KX108_ONLY"`, `context_record_hash` exact, et en V2 recalcul autonome de `manifest_sha256` depuis `pec["manifest"]`. |
| `kxpre` (`kxpre-*`) | `scripts/obsidia_kx108_decision_store.py` | `verify_kx108_decision_record(kxpre)` | Schéma V1, champs `_PRE_RECORD_BOUND_FIELDS` présents, `decision_authority == "KX108_ONLY"`, `x108_gate` valide, `decision_record_hash` exact. |
| `sre` (`sre-*`) | `scripts/obsidia_sealed_evidence_v0.py` | `verify_sealed_rollback_evidence(sre)` | `sealed is True`, `operation_type == "UPDATE_TARGET_FROM_SOURCE"`, décodage base64 strict de `pre_write_bytes_b64`, `sha256(preimage) == pre_write_sha256`, taille exacte, `sealed_rollback_evidence_hash` exact. |
| `sar` (`sar-*`) | `scripts/obsidia_sealed_evidence_v0.py` | `verify_sealed_apply_receipt(sar)` | `sealed is True`, `status == "CONTENT_APPLIED"`, `target_post_sha256 == source_content_sha256` (64-hex), `sealed_apply_receipt_hash` exact. |
| `tcr` (`tcr-*`) | `scripts/obsidia_test_contract.py` | `verify_test_contract_result_artifact(tcr)` | Schéma V1, champs `_RESULT_BOUND_FIELDS` présents, `result_record_hash` exact. |
| `kxpost` (`kxpost-*`) | `scripts/obsidia_kx108_decision_store.py` | `verify_kx108_decision_record(kxpost)` | Schéma V1, champs `_POST_PRE_LINKED_SEALED_RECORD_BOUND_FIELDS` présents, `decision_authority == "KX108_ONLY"`, `x108_gate` valide, `decision_record_hash` exact. |
| `clo` (`clo-*`, opt.) | `scripts/obsidia_execution_closure.py` | `verify_execution_closure_record(clo)` | Schéma V1, champs `_CLOSURE_BOUND_FIELDS` présents, `decision_authority == "KX108_ONLY"`, `closure_record_hash` exact. |

---

## 4. Contrôles complémentaires et 18 invariants de liaison croisée

Outre les 6 vérificateurs individuels, l'adaptateur applique en mode fail-closed les contrôles suivants :

1. **Phases, domaine et autorité :**
   - `kxpost.get("decision_phase") == "POST_EXECUTION"` et `kxpost["decision_record_id"].startswith("kxpost-")`. Tout enregistrement `kxd-*` (legacy 1-phase sans scellé C2) ou `kxagent-*` (`AGENT_PRE_EXECUTION`) est rejeté (`UNSUPPORTED_DECISION_PHASE_OR_LEGACY_RECORD`).
   - `kxpre.get("decision_phase") == "PRE_EXECUTION"` et `kxpre["decision_record_id"].startswith("kxpre-")`.
   - `kxpre.get("domain") == "tooling_build"` et `kxpost.get("domain") == "tooling_build"`.
   - `kxpre.get("x108_gate") == "ALLOW"` (aucune exécution légitime sans `ALLOW` pré-exécution).
   - `tcr.get("decision_authority") == "KX108_ONLY"`.

2. **Identité d'exécution uniforme sur `(kxpre, sre, sar, tcr, kxpost)` :**
   - Même `batch_execution_id` (chaîne non vide).
   - Même `child_execution_id` (chaîne non vide).
   - Même `execution_authority_hash` (SHA-256 64-hex valide).
   - Même `approval_id` (chaîne non vide).

3. **Continuité cryptographique des paires `(id, hash 64-hex)` :**
   - `kxpre["pre_execution_context_id"] == pec["context_id"]` et `kxpre["pre_execution_context_record_hash"] == pec["context_record_hash"]`.
   - `sre["kx108_pre_decision_record_id"] == kxpre["decision_record_id"]` et `sre["kx108_pre_decision_record_hash"] == kxpre["decision_record_hash"]`.
   - `sar["kx108_pre_decision_record_id"] == kxpre["decision_record_id"]` et `sar["kx108_pre_decision_record_hash"] == kxpre["decision_record_hash"]`.
   - `sar["sealed_rollback_evidence_id"] == sre["sealed_rollback_evidence_id"]` et `sar["sealed_rollback_evidence_hash"] == sre["sealed_rollback_evidence_hash"]`.
   - `kxpost["kx108_pre_decision_record_id"] == kxpre["decision_record_id"]` et `kxpost["kx108_pre_decision_record_hash"] == kxpre["decision_record_hash"]`.
   - `kxpost["sealed_apply_receipt_id"] == sar["sealed_apply_receipt_id"]` et `kxpost["sealed_apply_receipt_hash"] == sar["sealed_apply_receipt_hash"]`.
   - `kxpost["sealed_rollback_evidence_id"] == sre["sealed_rollback_evidence_id"]` et `kxpost["sealed_rollback_evidence_hash"] == sre["sealed_rollback_evidence_hash"]`.
   - `kxpost["test_result_id"] == tcr["result_id"]` et `kxpost["test_result_record_hash"] == tcr["result_record_hash"]`.

4. **Continuité du contrat de test (`test_contract_hash`) et limite PEC V1 vs PEC V2 :**
   - `kxpre["test_contract_hash"] == tcr["test_contract_hash"] == kxpost["test_contract_hash"]` (SHA-256 64-hex).
   - En schéma PEC V2 (`context_schema_version == 2`), `pec["manifest"]` est persisté de manière auto-contenue et son `test_contract_hash` est vérifié contre `tcr["test_contract_hash"]`. En schéma PEC V1 historique (`context_schema_version == 1`), `manifest` n'étant pas persisté dans `pec`, la liaison de `test_contract_hash` repose uniquement sur `(kxpre, tcr, kxpost)` sans la garantie auto-contenue du manifeste V2.

5. **Continuité physique de la cible, de la source et de l'isolation :**
   - `pec["target_path"] == sre["target_path"] == sar["target_path"]` et `pec["target_path"] in (pec.get("approved_scope") or [])`.
   - `pec["target_pre_sha256"] == sre["pre_write_sha256"] == sar["target_pre_sha256"]`.
   - `pec["source_sha256"] == sre["source_content_sha256"] == sar["source_content_sha256"] == sar["target_post_sha256"]`.
   - `pec.get("worktree_isolated") is True`, `pec.get("branch_isolated") is True`, `pec.get("protected_scope_status") == "CLEAN"`.

6. **Cohérence interne du `TestContractResult` (`tcr`) :**
   - `tcr["checks"]` doit être une liste non vide de dictionnaires et `len(tcr["checks"]) == tcr["check_count"]`.
   - `required_checks = [c for c in tcr["checks"] if c.get("required", True)]` doit vérifier `len(required_checks) == tcr["required_check_count"]` et `tcr["required_check_count"] >= 1`.
   - Pour chaque check de `tcr["checks"]`, `c.get("result")` doit appartenir à `{"PASS", "FAIL", "ERROR"}` :
     - `SUBPROCESS_ARGV` (`expected_exit_code` / `exit_code`) : absent si `ERROR` ; `result == "PASS"` exige `exit_code == expected_exit_code`, `result == "FAIL"` exige `exit_code != expected_exit_code`.
     - `TARGET_POSTCONDITION_SHA256` (`expected_target_sha256` / `actual_target_sha256`) : absent si `ERROR` ; `result == "PASS"` exige `actual_target_sha256 == expected_target_sha256 == sar["target_post_sha256"]`, `result == "FAIL"` exige `actual_target_sha256 != expected_target_sha256`.
     - `DIFF_SCOPE_EXACT` (`expected_diff_paths` / `actual_diff_paths`) : absent si `ERROR`, listes de chaînes non vides triées canoniquement ; `result == "PASS"` exige `actual_diff_paths == expected_diff_paths`, `result == "FAIL"` exige `actual_diff_paths != expected_diff_paths`.
   - Le statut agrégé recalculé depuis `required_checks` (`"TEST_EXECUTION_ERROR"` si au moins un `"ERROR"`, sinon `"REQUIRED_TEST_FAILED"` si au moins un `"FAIL"`, sinon `"ALL_REQUIRED_PASS"`) doit être strictement égal à `tcr["aggregate_status"]`. Toute divergence est rejetée avec `TEST_RESULT_INTERNAL_INCONSISTENCY`.

---

## 5. Qualification sémantique : ressource, portée du test et confiance pré-exécution

1. **Séparation `executing_mechanism_ref` vs `mutated_target_path` :**
   - `sar["target_path"]` (ex. `"scripts/obsidia_branching_ledger.py"`) est le **fichier cible muté** (`mutated_target_path`), jamais l'identité d'un agent exécutant.
   - Le mécanisme exécutant réel est identifié par `executing_mechanism_ref = "rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE"`.

2. **Portée strictement bornée de `ALL_REQUIRED_PASS` :**
   - `tcr["aggregate_status"] == "ALL_REQUIRED_PASS"` prouve uniquement que le remplacement de `mutated_target_path` par `source_content_sha256` a satisfait les checks déterministes de `test_contract_hash`. Il ne prouve aucune compétence générale sur `tooling_build`.

3. **Exclusion de `clo.functional_status` :**
   - Dans `scripts/obsidia_execution_closure.py`, `functional_status = "PASS"` est codé en dur lors de la création d'un `ExecutionClosureRecord`. Si un `clo-*` est fourni et vérifié, son champ `functional_status` est ignoré pour qualifier le résultat d'exécution : seul `tcr["aggregate_status"]` fait foi pour le contrat de test.

4. **Non-éligibilité de la confiance pré-exécution à la calibration empirique :**
   - Dans `kxpre["canonical_envelope"]["confidence"]`, le pipeline `tooling_build` évalue l'état pré-action avec `tests_results="UNKNOWN"` et produit constamment `0.95` (`confidence_scope="integrity"`) pour toute enveloppe de gouvernance propre et isolée.
   - Cette valeur mesure l'intégrité structurelle de l'enveloppe de gouvernance et **non** une probabilité prédictive de succès du contrat de test. Elle est exposée sous `pre_governance_integrity_confidence` avec `is_predictive_outcome_probability = False`.

---

## 6. Contrat des structures et fonctions de l'adaptateur (`app/cognition/b11/rail_a_observation_adapter.py`)

### 6.1 `RailAVerifiedObservation` (classe immuable `__slots__`)
- `observation_id: str` (`"b11-railo-<32hex>"`)
- `domain: str` (`"tooling_build"`)
- `task_ref: str` (`"UPDATE_TARGET_FROM_SOURCE"`)
- `executing_mechanism_ref: str` (`"rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE"`)
- `mutated_target_path: str`
- `conditions: tuple[str, ...]`
- `batch_execution_id: str`
- `child_execution_id: str`
- `execution_authority_hash: str`
- `approval_id: str`
- `test_contract_hash: str`
- `target_pre_sha256: str`
- `target_post_sha256: str`
- `source_content_sha256: str`
- `test_aggregate_status: str` (`"ALL_REQUIRED_PASS"` | `"REQUIRED_TEST_FAILED"` | `"TEST_EXECUTION_ERROR"`)
- `required_check_count: int`
- `passed_required_check_count: int`
- `kx108_pre_gate: str` (`"ALLOW"`)
- `kx108_post_gate: str` (`"ALLOW"` | `"HOLD"` | `"BLOCK"`)
- `verified_execution_outcome: str` (`"VERIFIED_TEST_CONTRACT_PASS"` | `"VERIFIED_TEST_CONTRACT_FAILURE"` | `"VERIFIED_GOVERNANCE_POST_HOLD_OR_BLOCK"`)
- `pre_governance_integrity_confidence: float`
- `is_predictive_outcome_probability: bool` (`False`)
- `anchor_refs: tuple[str, ...]` (paires `"<type>:<id>:sha256:<hash>"` pour `pec`, `kxpre`, `sre`, `sar`, `tcr`, `kxpost`)
- `provenance_store_verified: bool` (`True`)

### 6.2 `RailABundleVerificationResult` (classe immuable `__slots__`)
- `verified: bool`
- `observation: RailAVerifiedObservation | None`
- `rejection_code: str | None`
- `evidence_refs: tuple[str, ...]`
- `unknowns: tuple[str, ...]`
- `risk_indicators: tuple[str, ...]`

### 6.3 Fonctions publiques
- `load_and_verify_rail_a_observation(kxpost_decision_record_id, *, kx108_decision_dir, pre_execution_context_dir, sealed_receipt_dir, sealed_rollback_evidence_dir, test_contract_results_dir, closure_id=None, execution_closures_dir=None) -> RailABundleVerificationResult`
- `load_and_verify_rail_a_observations_batch(kxpost_decision_record_ids, *, kx108_decision_dir, pre_execution_context_dir, sealed_receipt_dir, sealed_rollback_evidence_dir, test_contract_results_dir) -> tuple[tuple[RailAVerifiedObservation, ...], tuple[str, ...], tuple[str, ...]]`
  - Détecte et rejette tout doublon de `kxpost_decision_record_id`, de reçu scellé (`sar-*`) **et** tout doublon d'exécution unitaire partageant le même couple `(batch_execution_id, child_execution_id)` ou `child_execution_id` (`DUPLICATE_EXECUTION_OBSERVATION_REJECTED`), sans assimiler l'identité d'autorité de lot (`execution_authority_hash`) à l'identité d'exécution d'un enfant.

---

## 7. Limite de confiance des stores (Trust Boundary)

La validation par `load_and_verify_rail_a_observation` établit :
1. L'**intégrité cryptographique interne** de chaque artefact (SHA-256 64-hex recalculé sur les champs liés et preimage base64 redécodée) ;
2. La **cohérence topologique et causale** des 6 artefacts entre eux ;
3. La **provenance depuis les répertoires de stores contrôlés** fournis à l'adaptateur, par opposition à un payload non vérifié injecté par l'appelant.

**Limite explicite :** Les stores du Rail A reposant sur des fichiers JSON locaux scellés par `os.link` et SHA-256 sans signature asymétrique matérielle (HSM/TPM) ni horodatage externe RFC3161 par exécution, cette vérification ne prouve pas une origine matériellement incontestable face à un adversaire privilégié capable de réécrire intégralement les répertoires de stores sur le disque local.

---

## 8. Matrice des scénarios RED obligatoires (RA-01 à RA-11)

| Code | Scénario | Attendu |
|---|---|---|
| **RA-01** | Bundle C2/D1 complet valide avec `ALL_REQUIRED_PASS` et `kxpost` `ALLOW` | `verified is True`, `verified_execution_outcome == "VERIFIED_TEST_CONTRACT_PASS"`, `executing_mechanism_ref != mutated_target_path`, `is_predictive_outcome_probability is False`, évaluation B11 maintenue en `UNKNOWN_COMPETENCE` (`conf=0.0`, `rel=None`). |
| **RA-02** | Bundle C2/D1 complet valide avec échec du contrat de test (`REQUIRED_TEST_FAILED`) et `kxpost` `BLOCK` | Produit par les vrais producteurs du dépôt (`run_and_persist_test_contract` + `run_and_persist_kx108_post_execution_decision`) ; `verified is True`, `verified_execution_outcome == "VERIFIED_TEST_CONTRACT_FAILURE"`. |
| **RA-03** | Omission d'un artefact (`pec`, `kxpre`, `sre`, `sar`, `tcr` ou `kxpost` absent sur disque) | `verified is False`, `observation is None`, `rejection_code` explicite (`ARTIFACT_MISSING:*`). |
| **RA-04** | Altération d'un artefact sur disque sans mise à jour valide de son empreinte | `verified is False`, `observation is None`, `ARTIFACT_VERIFICATION_FAILED:*` dans `risk_indicators`. |
| **RA-05** | Substitution croisée entre deux bundles $A$ et $B$ individuellement valides (`kxpost` re-haché pointant vers `tcr_B` ou `sar_B`) | `verified is False`, `observation is None`, `CROSS_LINK_MISMATCH:*` dans `risk_indicators`. |
| **RA-06** | Incohérence interne dans `tcr` (`aggregate_status="ALL_REQUIRED_PASS"` avec un check requis en `"FAIL"`), même après recalcul de `result_record_hash` | `verify_test_contract_result_artifact(tcr)` passe sur le hash recalculé, mais l'adaptateur rejette avec `TEST_RESULT_INTERNAL_INCONSISTENCY`. |
| **RA-07** | Soumission d'une décision legacy 1-phase `kxd-*` ou d'une décision agent `kxagent-*` | `verified is False`, `observation is None`, `rejection_code == "UNSUPPORTED_DECISION_PHASE_OR_LEGACY_RECORD"`. |
| **RA-08** | Soumission d'un dict auto-déclaré (`is_verified=True`) ou d'un objet forgé en mémoire imitant `RailAVerifiedObservation` | Rejet strict (`SELF_ATTESTATION_REJECTED` / `INVALID_RECORD_STRUCTURE_REJECTED` / `FORGED_OBSERVATION_OBJECT_REJECTED`), profil en `UNKNOWN_COMPETENCE`. |
| **RA-09** | Doublons dans un lot par `kxpost_decision_record_id` identique OU par deux `kxpost-*` distincts partageant le même `child_execution_id` | Le doublon est rejeté et consigné dans `risk_indicators` (`DUPLICATE_EXECUTION_OBSERVATION_REJECTED`). |
| **RA-10** | Bundle d'échec de test (`REQUIRED_TEST_FAILED`) accompagné d'un `ExecutionClosureRecord` (`clo-*`) portant `functional_status == "PASS"` | `verified_execution_outcome == "VERIFIED_TEST_CONTRACT_FAILURE"` : `clo.functional_status` n'est jamais assimilé à un succès de test. |
| **RA-11** | Invariants `B11_EFFECTS`, immutabilité de `RailAVerifiedObservation`, et absence totale d'écriture disque / B10 / mutation KX108 | `B11_EFFECTS` intacts, `AttributeError` sur tentative de mutation d'attribut, `0` fichier créé ou modifié dans les stores pendant la lecture. |
