# Spécification M42/B11 — Protocole Expérimental et Comparaison Empirique V1

**Statut :** CANDIDATE / SPEC ONLY / ZERO RUNTIME  
**Autorité :** KX108_ONLY  
**Couche :** CONNECTORS / B11 COGNITION  
**Contrat cible :** `app/cognition/b11/empirical_comparison.py`  
**Régime de compétence :** UNKNOWN_COMPETENCE  
**Délégation autorité :** NONE (Qwen consultatif ou témoin externe exclusif)  

---

## 1. Objectif et Portée

Le présent document formalise le protocole d'évaluation comparative entre trois conditions d'exécution de Brody / Obsidia :

- **Condition A — `STACK_ONLY` :** Brody / Obsidia résout la requête uniquement avec ses composants cognitifs, symboliques et son registre documentaire B8, sans consultation de modèle externe.
- **Condition B — `STACK_PLUS_QWEN` :** Brody / Obsidia résout la requête avec accès à un modèle local auxiliaire (Qwen), ce dernier étant strictement restreint à la fourniture de données, indices et hypothèses non autoritaires (`advisory_only=True`).
- **Condition C — `QWEN_ONLY` :** Réponse brute du modèle externe seul sur la même tâche, sans le système de contrôle, de pré-raisonnement ou de validation documentaire d'Obsidia, servant de baseline témoin.

Cette spécification définit les structures de données, les règles de comparaison appariée, les métriques statistiques admissibles et la chaîne d'attribution causale.

---

## 2. Invariants et Niveaux Doctrinaires

### 2.1 Hiérarchie des niveaux de preuve

Il est formellement interdit de déduire un niveau supérieur à partir d'un niveau inférieur :

1. **Niveau 1 — `HARNESS_VALIDATED` :**  
   Le protocole est vérifié syntaxiquement et sémantiquement sur des fixtures contrôlées (mockées ou synthétiques).
2. **Niveau 2 — `EMPIRICAL_OBSERVATIONS_AVAILABLE` :**  
   Des essais appariés réels ont été exécutés sur des données effectives avec traçabilité complète de l'inférence.
3. **Niveau 3 — `STATISTICAL_CALIBRATION_SUPPORTED` :**  
   Un volume d'échantillon suffisant avec intervalles de confiance et oracles indépendants permet d'estimer une calibration empirique.

Le régime demeure impérativement `UNKNOWN_COMPETENCE` tout au long de la phase F1.

### 2.2 Invariants Kernel & B11

- `decision_authority = "KX108_ONLY"`
- `advisory_only = True`
- `memory_write = False`
- `emits_act = False`
- `kernel_mutation = False`
- `b12_selection = False`
- Zéro écriture sur les registres de production.

---

## 3. Schémas de Données du Contrat

Le futur module `app/cognition/b11/empirical_comparison.py` exposera les classes suivantes :

### 3.1 `EmpiricalTaskV1`

Définit une tâche d'évaluation unitaire :
```python
@dataclass(frozen=True)
class EmpiricalTaskV1:
    task_id: str
    prompt: str
    task_category: str  # e.g. FACT_KNOWN, CONTRADICTION, KNOWLEDGE_GAP, AMBIGUITY, JUSTIFIED_ABSTENTION, UNJUSTIFIED_ABSTENTION, SOURCE_CONFLICT, EXTERNAL_DATA_USEFUL, EXTERNAL_DATA_MISLEADING, EXTERNAL_DATA_NEUTRAL
    oracle_reference: dict[str, Any]  # locator B8, assertion attendue, ground_truth_provenance, etc.
    metadata: dict[str, Any] = field(default_factory=dict)
```

Règle d'or : `oracle_reference` doit être indépendant de toute sortie générée par les conditions A, B ou C. Tout oracle auto-référentiel ou dérivé de la réponse évaluée est rejeté avec `INVALID_CIRCULAR_ORACLE`.

### 3.2 `EmpiricalConditionV1`

```python
EmpiricalConditionV1 = Literal["STACK_ONLY", "STACK_PLUS_QWEN", "QWEN_ONLY"]
```

### 3.3 `EmpiricalTrialReceiptV1`

Reçu d'exécution d'un essai unitaire :
```python
@dataclass(frozen=True)
class EmpiricalTrialReceiptV1:
    trial_id: str
    task_id: str
    condition: EmpiricalConditionV1
    system_version: str
    observable_response_text: str
    abstained: bool
    abstention_reason: str | None
    external_telemetry: dict[str, Any]
    evaluation_result: dict[str, Any] | None
    is_mock: bool
    timestamp_iso: str
```

Contenu requis de `external_telemetry` :
- `external_called: bool`
- `external_received: bool`
- `external_admitted: bool`
- `provenance: Literal["MOCKED_EXTERNAL", "REAL_EXTERNAL", "NONE"]`
- `model_calls: int`
- `prompt_tokens: int`
- `completion_tokens: int`
- `latency_ms: float`

### 3.4 `EmpiricalComparisonReportV1`

Rapport consolidé d'une campagne de comparaison :
```python
@dataclass(frozen=True)
class EmpiricalComparisonReportV1:
    report_id: str
    schema: Literal["EMPIRICAL_COMPARISON_REPORT_V1"]
    protocol_level: Literal["HARNESS_VALIDATED", "EMPIRICAL_OBSERVATIONS_AVAILABLE", "STATISTICAL_CALIBRATION_SUPPORTED"]
    competence_regime: Literal["UNKNOWN_COMPETENCE"]
    decision_authority: Literal["KX108_ONLY"]
    advisory_only: bool
    total_tasks: int
    total_trials: int
    contains_mocked_data: bool
    metrics_by_condition: dict[str, dict[str, Any]]
    pairwise_comparisons: dict[str, dict[str, Any]]
    causal_attribution: dict[str, Any]
    limitations: list[str]
    hold_reasons: list[str]
```

---

## 4. Chaîne d'Attribution Causale Qwen

Pour évaluer si l'apport de Qwen dans la condition B a un effet réel, l'analyseur vérifie strictement la séquence ordonnée :

1. `EXTERNAL_CALLED` : Un appel au modèle local a été émis (`model_calls > 0`).
2. `EXTERNAL_DATA_RECEIVED` : Une réponse HTTP valide a été reçue (`external_received is True`).
3. `EXTERNAL_DATA_ADMITTED` : Les données ont franchi les contrôles de consistance et de format (`external_admitted is True`).
4. `ANSWER_CHANGED` : La réponse observable en condition B diffère de celle obtenue en condition A pour la même tâche.
5. `PERFORMANCE_DIFFERENCE_OBSERVED` : Le statut d'évaluation E3 s'est modifié (ex. passage de `INDETERMINATE` ou `FAIL` à `PASS`).
6. `CAUSAL_EFFECT_SUPPORTED` : L'amélioration est formellement imputable aux données externes sous variation contrôlée sans facteur confondant.

**Interdiction formelle :** `EXTERNAL_CALLED` ou `model_calls > 0` n'implique en aucun cas `CAUSAL_EFFECT_SUPPORTED`.

---

## 5. Méthodologie Statistique et Comparaison Appariée

### 5.1 Unité d'analyse

L'unité d'analyse statistique est la **tâche unique (`task_id`)**.
Si une même tâche est répétée $K$ fois (ex. pour tester la variance du décodage), ces répétitions ne constituent pas $K$ tâches indépendantes. Le dénominateur $N$ pour les tests d'hypothèse reste le nombre de tâches distinctes.

### 5.2 Intervalles de confiance

Pour chaque condition, les proportions binaires (taux de succès, taux d'abstention) doivent être encadrées par des **intervalles de score de Wilson à 95 %** :
$$w = \frac{p + \frac{z^2}{2N} \pm z \sqrt{\frac{p(1-p)}{N} + \frac{z^2}{4N^2}}}{1 + \frac{z^2}{N}}$$
avec $z = 1.96$.

### 5.3 Comparaison appariée (A vs B, B vs C, A vs C)

La comparaison de performances sur les mêmes tâches requiert un test pour données appariées :
- Pour les sorties dichotomiques (Succès vs Échec), utilisation du **test exact de McNemar** (ou test binomial des désaccords si $b+c < 25$).
- Rejet de toute comparaison non appariée ou présentant des tâches incompatibles (`UNPAIRED_TASK`, `INCOMPATIBLE_ORACLE_CONDITIONS`).

---

## 6. Préservation des Limites Cognitives B11

- `F-F3-03` : L'évaluation automatique reste strictement circonscrite aux faits scalaires et typés vérifiés par E3. Aucune validation rhétorique ou éditoriale n'est requise ni assimilée à une preuve cognitive.
- `F-F3-04` : L'extracteur scalaire isole le premier fait numérique sans analyse syntaxique multi-sujets.
- Preuves causales logicielles : Le chantier `oracle_freshness_gate` demeure en **HOLD documentaire** et ne constitue pas une attestation B8.
