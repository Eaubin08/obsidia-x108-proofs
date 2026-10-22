# M42 B11 Compétence & Calibration — Spécification du Pont Contextuel d'Observations Rail A V1

## 1. Statut, périmètre et frontière doctrinale

- **Chapitre :** M42 — B11 Compétence et Calibration (Étage 2 : Raccordement contextuel des observations Rail A vers `ContextualCompetenceProfile`).
- **Couche :** Cognition / Pré-forge / Gouvernance périphérique (`app/cognition/b11/`).
- **Composant cible :** `evaluate_rail_a_contextual_competence`.
- **Mode d'autorité :** Lecture seule stricte, non-souverain, consultatif (`B11_EFFECTS` : `memory_write=False`, `emits_act=False`, `kernel_mutation=False`, `decision_authority="KX108_ONLY"`, `advisory_only=True`, `b12_selection=False`).
- **Frontière doctrinale de la tranche V1 :**
  - Le pont effectue la projection contextuelle d'observations d'exécution réelles du Rail A (`tooling_build`) vérifiées depuis les stores contrôlés vers un profil `ContextualCompetenceProfile`.
  - **Tant que les seuils statistiques $N_{\min}$, les règles d'échantillonnage et les formules de calibration empirique de M42 ne sont pas arrêtés et approuvés, tout profil émis demeure impérativement sous `CompetenceRegime.UNKNOWN_COMPETENCE` avec `confidence_score=0.0`, `reliability_score=None` et `calibration_metric=None`.**
  - Les observations vérifiées pertinentes sont consignées dans `evidence_refs` (traçabilité), et les motifs de maintien sous régime inconnu sont documentés dans `unknowns`.
  - **Aucune attribution cognitive :** Les observations du Rail A représentent exclusivement des exécutions du mécanisme déterministe pré-forge `rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE`. Elles ne sont en aucun cas attribuées à Brody, à un modèle neuronal ou à un agent cognitif.

---

## 2. Contrat d'entrée et frontière de consommation

### 2.1 Signature cible

```python
evaluate_rail_a_contextual_competence(
    evaluation_id: str,
    domain: str,
    task_ref: str,
    target_resources: Sequence[str],
    conditions: Sequence[str] = (),
    *,
    kxpost_decision_record_ids: Sequence[Any] = (),
    kx108_decision_dir: Path,
    pre_execution_context_dir: Path,
    sealed_receipt_dir: Path,
    sealed_rollback_evidence_dir: Path,
    test_contract_results_dir: Path,
) -> ContextualCompetenceProfile
```

### 2.2 Règles de résolution et sécurité passive

1. **Interdiction des instances en mémoire non vérifiées :**
   Le pont n'accepte aucun objet ou dictionnaire auto-déclaré (`is_verified=True`, objet forgé mimant `RailAVerifiedObservation`). L'acquisition d'observations passe obligatoirement par `load_and_verify_rail_a_observations_batch` à partir des identifiants `kxpost_decision_record_ids` et des répertoires de stores explicites.
2. **Défense passive sur les arguments d'entrée :**
   - `evaluation_id`, `domain`, `task_ref` doivent être des chaînes non vides.
   - `target_resources` et `conditions` doivent être des conteneurs natifs séquentiels (`tuple`, `list`) de chaînes non vides.
   - Les objets hostiles surchargeant `__str__`, `__eq__` ou `__iter__` sont rejetés en mode fail-closed sans exécution de méthode dynamique dangereuse.

---

## 3. Matrice de projection contextuelle

Pour chaque observation issue de `load_and_verify_rail_a_observations_batch`, le pont vérifie sa correspondance exacte avec la requête d'évaluation :

| Dimension d'évaluation | Attribut `RailAVerifiedObservation` | Règle de correspondance / Conséquence en cas de divergence |
|---|---|---|
| **Domaine** | `obs.domain` (`"tooling_build"`) | `obs.domain == domain`. Si divergence : observation exclue du contexte demandé, signalée par `CONTEXT_MISMATCH:DOMAIN` dans `risk_indicators`. |
| **Tâche** | `obs.task_ref` (`"UPDATE_TARGET_FROM_SOURCE"`) | `obs.task_ref == task_ref`. Si divergence : observation exclue, signalée par `CONTEXT_MISMATCH:TASK` dans `risk_indicators`. |
| **Ressource cible** | `obs.executing_mechanism_ref` (`"rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE"`) | `target_resources` doit contenir le mécanisme exécutant réel. **Interdiction de fournir `mutated_target_path` comme ressource exécutante** : si `target_resources` référence le fichier modifié au lieu du mécanisme, l'observation est rejetée avec `MUTATED_PATH_NOT_AN_EXECUTING_MECHANISM`. |
| **Cible mutée** | `obs.mutated_target_path` | Dimension de contexte explicite. Si `conditions` exige un `mutated_target_path:<path>`, l'observation doit porter exactement ce chemin. |
| **Contrat de test** | `obs.test_contract_hash` | Si `conditions` exige un `test_contract_hash:<hash>`, l'observation doit porter exactement ce hash. |
| **Conditions d'isolation** | `obs.conditions` | Les exigences contextuelles (`worktree_isolated:True`, `branch_isolated:True`, etc.) doivent être satisfaites par l'observation. |

Toute observation rejetée ou hors contexte n'est pas versée dans les `evidence_refs` du profil pour la compétence demandée.

---

## 4. Contrat de sortie B11 V1

1. **Régime épistémique et scores :**
   - `competence_regime = CompetenceRegime.UNKNOWN_COMPETENCE`
   - `confidence_score = 0.0`
   - `reliability_score = None`
   - `calibration_metric = None`
2. **Traçabilité des preuves (`evidence_refs`) :**
   - Seules les observations vérifiées qui satisfont **l'intégralité** de la projection contextuelle sont versées dans `evidence_refs`.
   - Format de référence : `obs.observation_id` accompagné de ses ancres cryptographiques.
3. **Consignation des limites et diagnostics (`unknowns`, `risk_indicators`) :**
   - En l'absence de formule statistique arrêtée, `unknowns` contient au minimum `M42_STATISTICAL_THRESHOLDS_PENDING` (garantissant l'invariant B11 `len(unknowns) >= 1` sous `UNKNOWN_COMPETENCE`).
   - Si aucune observation n'est fournie ou admissible : `NO_HISTORICAL_EVIDENCE` dans `unknowns`.
   - Les rejets de bundles, doublons (`DUPLICATE_EXECUTION_OBSERVATION_REJECTED`) ou divergences de contexte sont tracés dans `risk_indicators`.
4. **Distinction échec de test vs incompétence :**
   - Une observation portant `verified_execution_outcome == "VERIFIED_TEST_CONTRACT_FAILURE"` est une observation valide d'échec de contrat. Elle est tracée fidèlement dans `evidence_refs` et n'est pas promue en `EVIDENCED_INCOMPETENCE` tant que le seuil $N_{\min}$ n'est pas défini.

---

## 5. Matrice des scénarios RED (RAC-01 à RAC-10)

| Code | Scénario | Attendu |
|---|---|---|
| **RAC-01** | Bundle valide PASS (`ALL_REQUIRED_PASS` + `ALLOW`) sur contexte exact | `competence_regime == UNKNOWN_COMPETENCE`, `confidence_score == 0.0`, `reliability_score is None`, `evidence_refs` contient les références du bundle vérifié. |
| **RAC-02** | Bundle valide FAIL (`REQUIRED_TEST_FAILED` + `BLOCK`) sur contexte exact | Tracé fidèlement dans `evidence_refs`, profil maintenu en `UNKNOWN_COMPETENCE` (pas de promotion prématurée en `EVIDENCED_INCOMPETENCE`). |
| **RAC-03** | Domaine divergent (`domain="bank"` au lieu de `"tooling_build"`) | Observation exclue de `evidence_refs`, `risk_indicators` contient `CONTEXT_MISMATCH:DOMAIN`. |
| **RAC-04** | Tâche divergente (`task_ref="OTHER_TASK"`) | Observation exclue de `evidence_refs`, `risk_indicators` contient `CONTEXT_MISMATCH:TASK`. |
| **RAC-05** | Ressource cible divergente ou tentative de passer `mutated_target_path` comme mécanisme | Rejet de l'attribution, `MUTATED_PATH_NOT_AN_EXECUTING_MECHANISM` ou `CONTEXT_MISMATCH:TARGET_RESOURCE` dans `risk_indicators`. |
| **RAC-06** | Cible mutée, contrat de test ou condition d'isolation divergent dans `conditions` | Observation exclue du contexte spécifique, `CONTEXT_MISMATCH:CONDITIONS` dans `risk_indicators`. |
| **RAC-07** | Bundle manquant sur disque ou falsifié | Aucune preuve promue dans `evidence_refs`, `risk_indicators` rapporte `ARTIFACT_MISSING:*` ou `ARTIFACT_VERIFICATION_FAILED:*`. |
| **RAC-08** | Même exécution soumise deux fois sous des décisions distinctes | Dédoublonnage actif : une seule preuve retenue, `DUPLICATE_EXECUTION_OBSERVATION_REJECTED` consigné dans `risk_indicators`. |
| **RAC-09** | Entrée hostile (dict `is_verified=True`, objet forgé, dunder malveillant) | Rejet passif fail-closed sans exécution dunder, `SELF_ATTESTATION_REJECTED` ou `INVALID_RECORD_STRUCTURE_REJECTED` dans `risk_indicators`. |
| **RAC-10** | Aucune observation (liste vide) | Profil en `UNKNOWN_COMPETENCE`, `unknowns` contient `NO_HISTORICAL_EVIDENCE`, respect strict de `B11_EFFECTS` et zéro I/O disque. |
