# M42 B11 Compétence & Calibration — Spécification Évaluation Cognitive Indépendante V1

## 1. Statut, Rôle et Frontières Doctrinales

- **Chapitre :** M42 — B11 Compétence et Calibration (Étage 6 : Évaluation cognitive indépendante et attribution causale).
- **Couche :** Cognition / Gouvernance consultative (`app/cognition/b11/`).
- **Composant cible :** `app.cognition.b11.brody_independent_evaluator` (`evaluate_brody_cognitive_evidence_bundle`, `CognitiveEvaluationReportV1`, `project_b11_evaluator_competence_profile`).
- **Rôle du module :**
  1. Évaluer de manière strictement indépendante les réponses cognitives issues de bundles scellés (`BrodyCognitiveEvidenceBundleV1`), sans dépendre de l'implémentation interne de Brody (qu'il s'agisse de la variante partagée SENS/Cognition ou du développement Studio).
  2. Séparer rigoureusement la **recevabilité d'un oracle documentaire** de la **correction sémantique et factuelle d'une réponse**.
  3. Qualifier de manière univoque les statuts `PASS`, `FAIL`, `ABSTAIN_CORRECT`, `ABSTAIN_UNJUSTIFIED`, et `INDETERMINATE`.
  4. Délimiter l'attribution causale entre la stack symbolique native Obsidia et les modèles externes (Qwen).
- **Invariance absolue de gouvernance :**
  - Zéro I/O d'écriture non contrôlée (`memory_write=False`).
  - Zéro émission d'action (`emits_act=False`).
  - Zéro mutation du noyau (`kernel_mutation=False`).
  - Autorité décisionnelle exclusive `KX108_ONLY`.
  - Maintien impératif sous `CompetenceRegime.UNKNOWN_COMPETENCE` (`confidence_score=0.0`, `reliability_score=None`, `calibration_metric=None`).

---

## 2. Découplage Fondamental : Recevabilité vs Correction

### 2.1 Limite du Placeholder BCE V1
Dans l'implémentation historique de `brody_evidence_store.py` (Phase BCE V1), la présence d'un oracle dans `_SOURCE_PINS` (`locator in _SOURCE_PINS`) suffisait à qualifier le champ `evaluation_outcome="PASS"`.
> [!WARNING]
> Un document épinglé recevable (`SOURCE_PINS`) atteste uniquement de l'existence et de l'intégrité de la référence dans le banc d'essai. Il ne constitue en aucun cas la preuve que la réponse formulée par Brody est exacte ou conforme à cette référence.

### 2.2 Règle de Réconciliation E3
L'évaluateur indépendant V1 produit son propre verdict souverain (`CognitiveEvaluationReportV1.verdict`), découplé de la métadonnée d'intégrité du bundle :
- `ground_truth_status` qualifie la recevabilité de l'oracle (`INDEPENDENT_ORACLE_PINNED`, `CIRCULAR_SELF_REFERENTIAL`, `ORACLE_UNPINNED`, `ORACLE_CORRUPTED`, `MISSING`).
- `verdict` qualifie la justesse cognitive de la réponse confrontée à l'assertion attendue (`PASS`, `FAIL`, `ABSTAIN_CORRECT`, `ABSTAIN_UNJUSTIFIED`, `INDETERMINATE`, `ERROR`).

---

## 3. Contrat d'Évaluation : `evaluate_brody_cognitive_evidence_bundle`

### 3.1 Signature Formelle
```python
def evaluate_brody_cognitive_evidence_bundle(
    bundle: BrodyCognitiveEvidenceBundleV1 | Mapping[str, Any],
    oracle: Mapping[str, Any],
    *,
    store_dir: Path | str | None = None,
    evaluation_id: str | None = None,
    isolated_source_pins: Mapping[str, Any] | None = None,
) -> CognitiveEvaluationReportV1:
    ...
```

### 3.2 Structure de Résultat : `CognitiveEvaluationReportV1`
La structure de rapport est immuable (`frozen=True`) et certifie :
- `evaluation_id` : identifiant canonique d'évaluation (`eval-bie-...`).
- `bundle_id` : identifiant du bundle évalué (`bceb-...`).
- `observation_id` : identifiant de l'observation cognitive associée.
- `oracle_ref` : identifiant de l'oracle indépendant.
- `oracle_digest` : empreinte SHA-256 du document de référence préétabli.
- `verdict` : verdict parmi `PASS`, `FAIL`, `ABSTAIN_CORRECT`, `ABSTAIN_UNJUSTIFIED`, `INDETERMINATE`, `ERROR`.
- `ground_truth_status` : statut de l'oracle (`INDEPENDENT_ORACLE_PINNED`, `CIRCULAR_SELF_REFERENTIAL`, etc.).
- `expected_assertion` : dictionnaire typé de l'assertion de référence attendue.
- `observed_assertion` : dictionnaire typé extrait de la réponse observable.
- `observable_response_text` : texte brut de la réponse évaluée.
- `justification` : raisonnement déterministe menant au verdict.
- `attribution_status` : `STACK_ONLY`, `STACK_PLUS_EXTERNAL_MODEL`, ou `EXTERNAL_MODEL_ONLY`.
- `causal_contribution_verified` : booléen (`False` par défaut, requiert discrimination comparative).
- `evaluation_timestamp_utc` : horodatage UTC certifié.

---

## 4. Règles de Comparaison Structurée et Typée

La comparaison ne repose pas sur une simple égalité de chaînes textuelles, mais sur des faits typés déterministes :
1. **Extraction de faits typés :** Extraction de clés scalaires canoniques (ex. `{"temperature": 12, "unit": "K", "subject": "florvaxium"}`).
2. **Tolérance zéro sur discordance factuelle :** Si la réponse affirme une valeur différente de la référence (ex. `99 K` vs `12 K`), le verdict est strictement `FAIL`.
3. **Traitement de l'abstention :**
   - Si la réponse formule une abstention explicite (ex. refus de trancher en présence d'ambiguïté M41 sans discriminant) et que le bundle contient un `WorldHypothesisSet` non résolu $\rightarrow$ `ABSTAIN_CORRECT`.
   - Si la réponse formule une abstention alors qu'un `b8.KnowledgeClaim` vérifié et non ambigu est disponible $\rightarrow$ `ABSTAIN_UNJUSTIFIED`.
4. **Rejet de circularité :** Si `oracle["source"]` appartient à `{"BRODY_PREVIOUS_OUTPUT", "SELF", "MODEL_PREVIOUS_TURN", "TAUTOLOGICAL"}` $\rightarrow$ rejet immédiat en `CIRCULAR_SELF_REFERENTIAL`, verdict `INDETERMINATE` ou `ERROR`, jamais `PASS`.
5. **Pré-engagement temporel :** Le document oracle doit être préexistant et horodaté antérieurement à l'exécution cognitive du bundle.

---

## 5. Protocole Comparatif Tripartite (Stack vs Qwen)

Pour isoler la contribution causale des composants, trois conditions expérimentales étanches sont formalisées :

| Condition | Configuration | Rôle Épistémique |
|---|---|---|
| **A. Stack Seule** | `called=False`, zéro appel LLM distant | Baseline symbolique pure (B7 lattice + M41 hypothèses + B8 documents). Démontre l'autonomie formelle d'Obsidia. |
| **B. Stack + Qwen** | `called=True`, 1 appel indice | Qwen est utilisé comme fournisseur d'indices non autoritaire, filtré par l'admission B8. Évalue le gain d'extraction sans perte de souveraineté. |
| **C. Qwen Seul** | Modèle externe seul, zéro filtre | Baseline comparative passive externe. Ne dispose d'aucune autorité décisionnelle dans Obsidia. |

> [!IMPORTANT]
> Un compteur `model_calls > 0` démontre un contact réseau/inférence, mais ne prouve aucunement une contribution causale à l'exactitude de la réponse. La contribution causale ne peut être validée que par divergence entre la Condition A et la Condition B face à un même oracle indépendant.

---

## 6. Matrice des 10 Scénarios RED (E3-01 à E3-10)

| Code | Scénario | Conditions & Entrée | Comportement Attendu |
|---|---|---|---|
| **E3-01** | `PASS` Conforme | Réponse affirmant 12 K face à oracle indépendant 12 K | `verdict="PASS"`, `ground_truth_status="INDEPENDENT_ORACLE_PINNED"` |
| **E3-02** | `FAIL` Contradiction | Réponse affirmant 99 K face à oracle indépendant 12 K | `verdict="FAIL"`, motif explicite de discordance de valeur |
| **E3-03** | `ABSTAIN_CORRECT` | Abstention justifiée par 2 hypothèses M41 coexistant | `verdict="ABSTAIN_CORRECT"`, conservation de l'ambiguïté |
| **E3-04** | `ABSTAIN_UNJUSTIFIED` | Abstention injustifiée alors qu'un claim B8 est vérifié | `verdict="ABSTAIN_UNJUSTIFIED"`, preuve d'incompétence d'exploitation |
| **E3-05** | Oracle Circulaire | Source oracle auto-référentielle (`BRODY_PREVIOUS_OUTPUT`) | `ground_truth_status="CIRCULAR_SELF_REFERENTIAL"`, refus de PASS |
| **E3-06** | Oracle Manquant | Oracle non trouvé dans les pins indépendants | `ground_truth_status="ORACLE_UNPINNED"`, `verdict="INDETERMINATE"` |
| **E3-07** | Source Altérée | Document oracle discordant avec le condensat épinglé | `ground_truth_status="ORACLE_CORRUPTED"`, `verdict="ERROR"` |
| **E3-08** | Attribution Externe | Trace avec `model_calls=1` sans preuve de causalité | `attribution_status="STACK_PLUS_EXTERNAL_MODEL"`, `causal_contribution_verified=False` |
| **E3-09** | Invariance Compétence | Évaluation ponctuelle sans agrégat statistique $N$ | `UNKNOWN_COMPETENCE` strict, `confidence=0.0`, aucun score dérivé |
| **E3-10** | Pureté B11 | Surveillance de l'environnement matériel et des effets | Zéro écriture disque, zéro ACT, `decision_authority="KX108_ONLY"` |
