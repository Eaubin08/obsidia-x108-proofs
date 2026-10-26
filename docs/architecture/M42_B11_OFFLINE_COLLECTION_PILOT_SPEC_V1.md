# Spécification M42/B11 — Pilote Offline de Collecte Comparative V1

**Statut :** CANDIDATE / SPEC ONLY / ZERO RUNTIME  
**Autorité :** KX108_ONLY  
**Couche :** CONNECTORS / B11 COGNITION  
**Contrat cible :** `app/cognition/b11/offline_collection_pilot.py`  
**Régime de compétence :** UNKNOWN_COMPETENCE  
**Délégation autorité :** NONE (Qwen consultatif ou témoin externe exclusif)  

---

## 1. Objectif et Périmètre

Le présent document formalise les contrats de frontière d'un collecteur offline pour la phase M42/F3.
Ce collecteur a pour unique mission de :

1. Recevoir des observations brutes ou constituées pour les conditions `STACK_ONLY`, `STACK_PLUS_QWEN` et `QWEN_ONLY`.
2. Normaliser ces observations en structures typées `EmpiricalTrialReceiptV1` conformes au moteur `EmpiricalComparisonV1`.
3. Préserver rigoureusement la provenance réelle des données en distinguant trois natures : `RECORDED_OBSERVATION`, `SYNTHETIC_FIXTURE` et `MOCKED_EXTERNAL`.
4. Qualifier la source de chaque champ (`OBSERVED`, `DERIVED`, `DECLARED`, `UNAVAILABLE`) pour proscrire toute interpolation de télémétrie absente.
5. Vérifier les contraintes d'appariement sur les tâches et versions d'oracles.
6. Transmettre les essais validés à `compare_empirical_trials` et consolider un rapport de pilote consultatif.

**Interdictions formelles :**
- Aucun appel réseau, aucun serveur de modèle démarré.
- Aucune écriture dans les bases ou stores de production (`memory_write=False`).
- Aucune inférence de compétence statistique globale (`UNKNOWN_COMPETENCE`).
- Aucun élargissement d'oracle B8 ni contournement de `_SOURCE_PINS`.

---

## 2. Natures de Données et Provenance

Chaque observation reçue doit impérativement déclarer sa nature :

| Nature | Définition doctinaire | Statut de preuve autorisé |
|---|---|---|
| **`RECORDED_OBSERVATION`** | Sortie d'exécution enregistrée traçable (code, hash et environnement identifiables). | Éligible à l'analyse descriptive réelle. |
| **`SYNTHETIC_FIXTURE`** | Cas d'école ou fixture forgée pour valider le comportement structurel du protocole. | Borne impérativement le rapport à `HARNESS_VALIDATED`. |
| **`MOCKED_EXTERNAL`** | Réponse simulée d'un tiers externe (ex. mock HTTP de Qwen). | Ne constitue aucune preuve de performance empirique de Qwen. |

Un reçu d'observation et son empreinte SHA-256 ne constituent jamais une attestation externe B8 par leur simple présence.

---

## 3. Qualification des Champs de Télémétrie

Pour chaque champ d'un reçu, le collecteur associe une étiquette de traçabilité :

- **`OBSERVED` :** Donnée effectivement mesurée ou issue du flux (ex. tokens reçus, texte de réponse, latence mesurée).
- **`DERIVED` :** Donnée calculée par fonction déterministe à partir d'observations (ex. hash SHA-256, statut E3).
- **`DECLARED` :** Paramètre de configuration fixé par le protocole (ex. version du système, température 0.0).
- **`UNAVAILABLE` :** Donnée non collectée ou non instrumentée (ex. coût financier en dollars/euros absent).

*Règle :* Il est formellement interdit d'inventer un coût financier ou une latence si elle n'a pas été mesurée.

---

## 4. Schémas de Données du Futur Module

Le futur module `app/cognition/b11/offline_collection_pilot.py` définira :

### 4.1 Types et Dataclasses

```python
ObservationProvenanceKind = Literal["RECORDED_OBSERVATION", "SYNTHETIC_FIXTURE", "MOCKED_EXTERNAL"]
FieldProvenanceKind = Literal["OBSERVED", "DERIVED", "DECLARED", "UNAVAILABLE"]

@dataclass(frozen=True)
class RawObservationRecordV1:
    task_id: str
    trial_id: str
    condition: Literal["STACK_ONLY", "STACK_PLUS_QWEN", "QWEN_ONLY"]
    raw_response_text: str
    provenance_kind: ObservationProvenanceKind
    system_identity: str
    components: dict[str, str]  # nom du composant -> hash SHA-256
    external_telemetry: dict[str, Any]
    field_provenances: dict[str, FieldProvenanceKind]
    timestamp_iso: str
    abstained: bool = False
    abstention_reason: str | None = None
    oracle_version: str = "v1"

@dataclass(frozen=True)
class OfflineCollectionPilotResultV1:
    pilot_id: str
    schema: Literal["OFFLINE_COLLECTION_PILOT_RESULT_V1"]
    verdict: Literal["HARNESS_VALIDATED", "PILOT_WITH_GAPS", "HOLD"]
    competence_regime: Literal["UNKNOWN_COMPETENCE"]
    decision_authority: Literal["KX108_ONLY"]
    advisory_only: bool
    total_tasks_received: int
    unique_tasks_count: int
    independent_facts_count: int
    normalized_trials: list[EmpiricalTrialReceiptV1]
    comparison_report: EmpiricalComparisonReportV1 | None
    unpaired_tasks: list[str]
    hold_reasons: list[str]
    metadata: dict[str, Any]
```

### 4.2 Signature de la Fonction de Collecte

```python
def collect_and_compare_offline_pilot(
    observations: list[RawObservationRecordV1],
    tasks: list[EmpiricalTaskV1],
) -> OfflineCollectionPilotResultV1:
    """Collecte, normalise et consolide les observations offline en essais comparables."""
    ...
```

---

## 5. Règles d'Appariement et de Décompte

1. **Appariement :** Pour qu'une tâche soit appariée entre conditions, les observations doivent partager le même `task_id`, la même assertion attendue et la même version d'oracle. En cas de divergence, la tâche est rejetée avec `"UNPAIRED_TASK"` ou `"ORACLE_VERSION_MISMATCH"` consigné dans `hold_reasons`.
2. **Décompte des faits indépendants :** Plusieurs tâches reformulant la même interrogation sur un même oracle (ex. même locator `16b9d28e...`) comptent pour des tâches distinctes dans `unique_tasks_count`, mais doivent être dédupliquées dans `independent_facts_count` pour éviter toute illusion statistique.
3. **Absence d'auto-attestation d'oracle :** Un locator B8 syntaxiquement valide (`ORACLE_METADATA_ACCEPTED`) ne confère aucune certification d'indépendance documentaire externe (`oracle_independence_attested=False` sauf si explicitement corroboré par un ancrage B8 préexistant).
4. **Évaluation de l'abstention et étiquette de l'évaluateur (F-F3-D7-R1 / R2) :**
   - L'extracteur de normalisation du collecteur est étiqueté `evaluator="OfflineCollectionPilotV1"`, reflétant une extraction simplifiée sans prétendre à l'exécution souveraine d'`evaluate_brody_cognitive_evidence_bundle`.
   - Dans le collecteur simplifié, une réponse abstenue (`abstained=True`) évalue souverainement à `INDETERMINATE`. La seule présence d'un champ non vérifié `requires_abstention=True` dans un dictionnaire ou d'un locator non résolu ne permet pas de décerner `ABSTAIN_CORRECT` (qualification strictement réservée au chemin complet E3 avec preuves documentaires épinglées). L'indication déclarée de `requires_abstention` est conservée à titre consultatif dans les métadonnées `reasons`.
5. **Verdicts du pilote :**
   - **`HARNESS_VALIDATED` :** Structure et normalisation valides sur fixtures de contrôle.
   - **`PILOT_WITH_GAPS` :** Données incomplètes mais comparabilité partielle préservée.
   - **`HOLD` :** Tâches non appariables, collisions d'identifiants ou rupture de traçabilité.
