# M42 B11 Compétence & Calibration — Spécification de Caractérisation Empirique V1

## 1. Statut, périmètre et frontière doctrinale

- **Chapitre :** M42 — B11 Compétence et Calibration (Étage 3 : Caractérisation descriptive des observations empiriques Rail A).
- **Couche :** Cognition / Pré-forge / Gouvernance périphérique (`app/cognition/b11/`).
- **Composant cible :** `characterize_empirical_observations`.
- **Mode d'autorité :** Purement consultatif, lecture seule stricte (`B11_EFFECTS` : `memory_write=False`, `emits_act=False`, `kernel_mutation=False`, `decision_authority="KX108_ONLY"`, `advisory_only=True`, `b12_selection=False`).
- **Arbitrage doctrinal V1 (HOLD formel sur inférence & calibration) :**
  1. **Description pure vs Inférence :** La tranche V1 se limite exclusivement à la **caractérisation descriptive** rigoureuse d'observations d'exécution réelles et vérifiées du Rail A (`tooling_build`).
  2. **HOLD sur toute promotion de compétence :** Tout profil `ContextualCompetenceProfile` émis ou projeté à l'issue de cette caractérisation demeure impérativement sous `CompetenceRegime.UNKNOWN_COMPETENCE`, avec `confidence_score = 0.0`, `reliability_score = None`, `calibration_metric = None` et `b12_selection = False`.
  3. **Rejet des seuils universels arbitraires ($N_{\min}$) :** Aucun seuil statistique ($N_{\min}$) n'est activé en dur pour déclencher une promotion automatique de compétence.
  4. **Rejet de l'inférence Bayésienne automatique :** Le prior $\text{Beta}(1, 1)$ reste une hypothèse de modélisation théorique et ne doit pas injecter de score a priori sans preuve.
  5. **Rejet de l'assimilation Wilson $\to$ fiabilité :** Une borne de Wilson est un intervalle descriptif d'incertitude d'échantillon ; elle ne devient pas automatiquement un `reliability_score`.
  6. **Rejet de la calibration prédictive sur `kxpre.confidence` :** `kxpre.pre_governance_integrity_confidence` est une métrique d'intégrité de pré-gouvernance, en aucun cas une probabilité prédictive de succès du test. Aucune métrique de calibration (ECE, Brier) n'est calculée sans prédictions ex-ante scellées.
  7. **Déduplication technique $\neq$ Indépendance statistique :** La déduplication d'identifiants physiques `(batch_id, child_id)` n'établit pas l'indépendance statistique entre exécutions.

---

## 2. Contrat de Données Empiriques : `EmpiricalContextualCharacterization`

La structure intermédiaire `EmpiricalContextualCharacterization` est immuable (`frozen`) et encapsule la caractérisation descriptive des observations :

| Attribut | Type | Définition & Règle d'invariance |
|---|---|---|
| `characterization_id` | `str` | Identifiant technique non vide de la caractérisation. |
| `target_mechanism_ref` | `str` | Référence du mécanisme gouverné (`"rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE"`). |
| `domain` | `str` | Domaine d'évaluation (`"tooling_build"`). |
| `task_ref` | `str` | Tâche d'évaluation (`"UPDATE_TARGET_FROM_SOURCE"`). |
| `conditions` | `tuple[str, ...]` | Conditions contextuelles d'isolation demandées. |
| `evidence_refs` | `tuple[str, ...]` | Références des observations vérifiées retenues dans le contexte (`kxpost:*`). |
| `data_provenance_type` | `str` | `"PROVENANCE_UNESTABLISHED"`, `"CANONICAL_FIXTURE_STORE"`, `"HISTORICAL_PRODUCTION_STORE"` ou `"UNAUTHENTICATED"`. |
| `raw_observation_count` | `int` | Nombre total d'identifiants d'observation soumis ($N_{raw} \ge 0$). |
| `distinct_execution_count` | `int` | Nombre d'exécutions physiques distinctes après déduplication technique ($N_{distinct} \ge 0$). |
| `retained_in_context_count` | `int` | Nombre d'observations vérifiées satisfaisant exactement le contexte d'évaluation ($N_{retained} \ge 0$). |
| `pass_count` | `int` | Nombre d'observations retenues portant `ALL_REQUIRED_PASS` ($k_{pass} \ge 0$). |
| `fail_count` | `int` | Nombre d'observations retenues portant `REQUIRED_TEST_FAILED` ($k_{fail} \ge 0$). |
| `error_count` | `int` | Nombre d'observations présentant une erreur d'exécution ou corruption ($k_{err} \ge 0$). |
| `excluded_count` | `int` | Nombre d'observations soumises exclues pour divergence contextuelle ou rejet ($k_{excl} \ge 0$). |
| `observed_success_rate` | `float \| None` | Proportion observée $\frac{k_{pass}}{N_{retained}}$ si $N_{retained} > 0$, sinon `None`. |
| `context_group_keys` | `tuple[str, ...]` | Clés de dépendance contextuelle `(mechanism, task_ref, target_path, contract_hash)`. |
| `context_group_count` | `int` | Nombre de groupes contextuels observés ($\text{len}(context\_group\_keys)$). |
| `statistical_independence_status` | `str` | Statut d'indépendance : `"NOT_ESTABLISHED"`, `"MONO_CONTEXT_INDEPENDENCE_UNESTABLISHED"`, `"INDEPENDENCE_NOT_ASSUMED"`. |
| `predictive_data_status` | `str` | `"PREDICTIVE_DATA_ABSENT"` (aucune prévision probabiliste scellée ex-ante). |
| `descriptive_admissibility_status` | `str` | `"NO_DATA"`, `"INSUFFICIENT_DATA"`, `"ADMISSIBLE_DESCRIPTIVE_ONLY"`, `"EXCLUDED_MISMATCH"`. |
| `diagnostic_codes` | `tuple[str, ...]` | Codes diagnostiques et avertissements (ex. `EMPIRICAL_VARIABILITY_OBSERVED`, `CORRELATION_DETECTED`). |
| `unknowns` | `tuple[str, ...]` | Lacunes explicites (ex. `NO_HISTORICAL_EVIDENCE`, `PREDICTIVE_CALIBRATION_UNAVAILABLE`). |

---

## 3. Règles de Caractérisation Statistique et Descriptive

1. **Dénominateur et taux descriptif :**
   - $N_{retained} = k_{pass} + k_{fail} + k_{error}$.
   - Si $N_{retained} = 0$ : `observed_success_rate = None`.
   - Si $N_{retained} > 0$ : `observed_success_rate = float(pass_count / retained_in_context_count)`.
   - Ce taux est une pure statistique descriptive de l'échantillon collecté, sans extrapolation prédictive.
2. **Indépendance statistique non établie :**
   - Même si $N_{distinct} > 1$, la déduplication technique ne garantit pas l'indépendance statistique.
   - Si toutes les observations partagent la même cible et le même contrat (`context_group_count == 1`), `statistical_independence_status` vaut `"MONO_CONTEXT_INDEPENDENCE_UNESTABLISHED"`.
   - Si les contextes diffèrent (`context_group_count > 1`), `statistical_independence_status` vaut `"INDEPENDENCE_NOT_ASSUMED"` (aucune règle de transférabilité trans-contextuelle n'est activée).
3. **Variabilité observée vs Contradiction :**
   - La coexistence de `pass_count > 0` et `fail_count > 0` au sein d'un échantillon reflète une variabilité empirique observée (`EMPIRICAL_VARIABILITY_OBSERVED`).
   - Elle ne constitue pas une contradiction logique d'invariant (`CONTRADICTION`) sans démonstration d'un fait contradictoire sous conditions strictement identiques.
4. **Distinction échec fonctionnel vs erreur d'exécution :**
   - `fail_count` : contrat de test canonique exécuté et rapportant un échec (`REQUIRED_TEST_FAILED`).
   - `error_count` : anomalie d'exécution, d'artefact manquant ou d'intégrité.
5. **Absence de calibration prédictive :**
   - En l'absence de prédictions probabilistes ex-ante scellées dans les artefacts d'observation, `predictive_data_status = "PREDICTIVE_DATA_ABSENT"`.
   - `calibration_metric` dans le profil projeté vaut impérativement `None`.
6. **Non-attribution causale :**
   - Les observations Rail A sont strictement imputées à `rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE`.
   - Toute tentative d'évaluer Brody, Qwen ou un agent neuronal à partir d'observations Rail A déclenche un rejet d'attribution (`CAUSAL_ATTRIBUTION_MISMATCH` ou `CONTEXT_MISMATCH:TARGET_RESOURCE`), avec exclusion totale des observations (`retained_in_context_count = 0`).
7. **Provenance non inférée :**
   - La validation de l'intégrité cryptographique locale des artefacts n'établit pas leur provenance d'origine historique ou de fixture.
   - Sans preuve indépendante d'origine, `data_provenance_type` vaut `PROVENANCE_UNESTABLISHED` (ou `UNAUTHENTICATED` si aucune observation retenue), tandis que `LOCAL_INTEGRITY_VERIFIED` documente la réussite de la vérification locale.

---

## 4. Matrice des Scénarios RED (REC-01 à REC-08)

| Code | Scénario | Entrées & Préconditions | Attendu Caractérisation | Attendu Profil B11 |
|---|---|---|---|---|
| **REC-01** | Absence d'observation | Aucun ID d'observation soumis ($N_{raw} = 0$). | `raw=0`, `distinct=0`, `retained=0`, `observed_success_rate=None`, `status="NO_DATA"`. | `UNKNOWN_COMPETENCE`, `confidence=0.0`, `reliability=None`, `NO_HISTORICAL_EVIDENCE`. |
| **REC-02** | Deux succès distincts | 2 observations distinctes vérifiées avec contrat `ALL_REQUIRED_PASS`. | `raw=2`, `distinct=2`, `retained=2`, `pass=2`, `fail=0`, `observed_success_rate=1.0`, `status="ADMISSIBLE_DESCRIPTIVE_ONLY"`. | `UNKNOWN_COMPETENCE`, `confidence=0.0`, `reliability=None`, aucun $N_{\min}$ arbitraire. |
| **REC-03** | 20 exécutions corrélées sur même cible | 20 observations distinctes sur la même cible mutée (`src/target.py`) et même contrat. | `distinct=20`, `context_group_count=1`, `statistical_independence_status="MONO_CONTEXT_INDEPENDENCE_UNESTABLISHED"`. | `UNKNOWN_COMPETENCE`, `confidence=0.0`, `reliability=None`, aucune promotion par volume. |
| **REC-04** | 4 PASS et 4 FAIL vérifiés | 4 observations PASS et 4 observations FAIL vérifiées. | `retained=8`, `pass=4`, `fail=4`, `observed_success_rate=0.5`, diagnostic `EMPIRICAL_VARIABILITY_OBSERVED`. | `UNKNOWN_COMPETENCE`, aucune contradiction erronée posée. |
| **REC-05** | 6 FAIL vérifiés | 6 observations distinctes avec contrat `REQUIRED_TEST_FAILED`. | `retained=6`, `pass=0`, `fail=6`, `observed_success_rate=0.0`. | `UNKNOWN_COMPETENCE`, `reliability=None` (aucune incompétence définitive décrétée). |
| **REC-06** | 10 PASS sur cibles distinctes | 10 observations distinctes sur 10 cibles mutées distinctes (`src/target_0.py` ... `target_9.py`). | `retained=10`, `pass=10`, `context_group_count=10`, `statistical_independence_status="INDEPENDENCE_NOT_ASSUMED"`. | `UNKNOWN_COMPETENCE`, contextes préservés, aucun regroupement transcontextuel inférentiel. |
| **REC-07** | 4 PASS et 1 FAIL sans prédiction ex-ante | 5 observations distinctes (4 PASS, 1 FAIL) sans probabilité prédictive scellée. | `retained=5`, `pass=4`, `fail=1`, `observed_success_rate=0.8`, `predictive_data_status="PREDICTIVE_DATA_ABSENT"`. | `UNKNOWN_COMPETENCE`, `calibration_metric=None`, `PREDICTIVE_CALIBRATION_UNAVAILABLE`. |
| **REC-08** | Non-attribution Rail A $\to$ Brody | Observations Rail A présentées pour évaluer `target_resources=("brody:cognitive_resolution",)`. | `retained=0`, `excluded=N`, rejet d'attribution `CAUSAL_ATTRIBUTION_MISMATCH`, evidence_refs vide. | `UNKNOWN_COMPETENCE`, `B11_EFFECTS` préservé, stores intacts. |
