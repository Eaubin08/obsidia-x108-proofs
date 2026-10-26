# Spécification M42/B11 — Assemblage Canonique du Pilote Offline V1

**Statut :** CANDIDATE / SPEC ONLY / ZERO RUNTIME
**Autorité :** KX108_ONLY
**Couche :** CONNECTORS / B11 COGNITION
**Contrat cible :** `app/cognition/b11/offline_pilot_assembly.py`
**Régime de compétence :** UNKNOWN_COMPETENCE
**Délégation autorité :** NONE (Qwen consultatif ou témoin externe exclusif)

---

## 1. Objectif et Portée

Le présent document formalise le contrat d'assemblage du premier pilote offline bout en bout pour le protocole M42/B11.
Ce contrat établit la passerelle entre les données de fixtures contrôlées et les moteurs de normalisation et d'évaluation committés :
- `app/cognition/b11/offline_collection_pilot.py` (Phase F3-D2)
- `app/cognition/b11/empirical_comparison.py` (Phase F2)
- `app/cognition/b11/brody_independent_evaluator.py` (Phase E3)

L'assembleur `assemble_offline_pilot_v1` est une fonction pure dont la responsabilité est d'instancier, valider et connecter les structures de données en mémoire sans réaliser d'opérations I/O (disque ou réseau).

---

## 2. Invariants et Frontières Dogmatiques

1. **Pureté fonctionnelle :** Aucune lecture disque, aucune écriture disque, aucun socket réseau dans le module de calcul.
2. **Immutabilité :** Les objets d'entrée (`raw_fixtures`, `task_fixtures`) sont traités de manière strictement non destructive.
3. **Périmètre d'autorité :**
   - `KX108_ONLY`
   - `UNKNOWN_COMPETENCE`
   - `advisory_only = True`
   - `memory_write = False`
   - `emits_act = False`
   - `kernel_mutation = False`
   - `b12_selection = False`
4. **Frontière Mock / Réel (F-F3-D5-REV-02) :**
   - En l'absence de trace ou de reçu d'exécution physique historisé sur disque, les réponses de Condition A (`STACK_ONLY`) sont formellement qualifiées de `SYNTHETIC_FIXTURE` (`is_mock=True`).
   - Les réponses de Conditions B (`STACK_PLUS_QWEN`) et C (`QWEN_ONLY`) sont qualifiées de `MOCKED_EXTERNAL` (`is_mock=True`).
   - L'ensemble du lot minimal étant synthétique ou mocké, le statut global du protocole est strictement borné à `HARNESS_VALIDATED`.

---

## 3. Schémas et Dataclasses Cibles

Le futur module `app/cognition/b11/offline_pilot_assembly.py` exposera les interfaces suivantes :

```python
from dataclasses import dataclass
from typing import Any, Literal
from app.cognition.b11.offline_collection_pilot import (
    OfflineCollectionPilotResultV1,
    RawObservationRecordV1,
)
from app.cognition.b11.empirical_comparison import EmpiricalTaskV1


@dataclass(frozen=True)
class OfflinePilotAssemblyResultV1:
    assembly_id: str
    schema: Literal["OFFLINE_PILOT_ASSEMBLY_RESULT_V1"]
    content_hash: str
    pilot_result: OfflineCollectionPilotResultV1
    assembled_tasks_count: int
    assembled_trials_count: int
    export_payload: dict[str, Any]
    metadata: dict[str, Any]


def assemble_offline_pilot_v1(
    raw_fixtures: list[dict[str, Any]],
    task_fixtures: list[dict[str, Any]],
    assembly_metadata: dict[str, Any] | None = None,
) -> OfflinePilotAssemblyResultV1:
    """Fonction pure d'assemblage et d'orchestration en mémoire."""
    ...


def serialize_assembly_result_canonical_json(
    result: OfflinePilotAssemblyResultV1,
) -> str:
    """Sérialisation canonique déterministe pour export et audit."""
    ...
```

---

## 4. Lot Canonique Expérimental Minimal

Le lot minimal est constitué de deux catégories de tâches :

### 4.1 Tâche T1 — FACT_KNOWN (Florvaxium)
- **Document source :** `locator="16b9d28ef7878084a353c4dbec94889efc6239016c7af01a3e8f17567ccc466b"`.
- **Assertion attendue :** Symbole `florvaxium`, propriété `temperature`, valeur `12.0`, unité `K`.
- **Provenance de l'oracle :** `B8_PINNED_DOCUMENT`.
- **Statut de l'oracle :** La présence du hash dans `KNOWN_B8_PINS` valide la référence, mais ne constitue pas en soi une attestation externe autonome sans enregistrement formel B8.
- **Observations A/B/C :**
  - Condition A (`STACK_ONLY`) : Observation nominale 12 K issue du banc synthétique (`SYNTHETIC_FIXTURE`, `is_mock=True`).
  - Condition B (`STACK_PLUS_QWEN`) : Observation simulée 12 K (`MOCKED_EXTERNAL`, `is_mock=True`, `model_calls=1`).
  - Condition C (`QWEN_ONLY`) : Réponse concise simulée 12 K (`MOCKED_EXTERNAL`, `is_mock=True`, `model_calls=1`).

### 4.2 Tâche T2 — FACT_UNKNOWN (Omega-9 / Contrôle Négatif — F-F3-D5-REV-01)
- **Prompt :** Interrogation sur une entité non couverte par le corpus épinglé (concentration de florvaxium dans le secteur Omega-9).
- **Oracle :** `oracle_reference=None`.
- **Statut vérité terrain :** `ground_truth_status="MISSING"`, `oracle_independence_attested=False`.
- **Règle d'évaluation E3 :**
  - En l'absence d'oracle documentaire épinglé certifiant l'obligation d'abstention (`requires_abstention=True`) ou d'un bundle M41 documentant la coexistence d'hypothèses, toute réponse (qu'elle déclare une abstention ou formule une assertion non justifiée) produit souverainement sous E3 le verdict `INDETERMINATE`.
  - Aucune attribution automatique de `ABSTAIN_CORRECT` ne peut être déduite de la seule présence de `abstained=True`.
  - L'absence de fait documentaire ne constitue jamais un oracle positif.
- **Provenance de l'évaluateur (F-F3-D7-R1) :**
  - L'intervention du garde défensif de l'assembleur sur les tâches sans oracle est formellement identifiée sous `evaluator="OfflinePilotAssemblyPolicyGuardV1"`, reflétant un garde de politique d'assemblage sans prétendre à une exécution souveraine complète d'E3.

---

## 5. Gestion de la Provenance et Déduplication

1. **Anti-inflation des faits (D1-05 / D5-05) :**
   Plusieurs tâches reformulant la même interrogation sur un même oracle comptent comme des tâches distinctes (`assembled_tasks_count`), mais sont dédupliquées dans `independent_facts_count` via la signature composite :
   `(locator, symbol, property, numeric_value, unit)`.
2. **Traçabilité des champs (D1-08 / D5-08) :**
   Les champs de télémétrie absents sont conservés sous le statut `UNAVAILABLE` dans `field_provenances`. Aucune dérivation financière synthétique n'est tolérée.
3. **Concordance des versions d'oracle (D1-07 / D5-06) :**
   Toute discordance de `oracle_version` entre essais sur une même tâche déclenche le motif `ORACLE_VERSION_MISMATCH`, forçant `verdict="HOLD"` et `comparison_report=None` (fail-closed).

---

## 6. Sérialisation Canonique et Empreinte Reproductible (F-F3-D5-REV-03)

1. **Périmètre du payload (`export_payload`) :**
   - Le dictionnaire `export_payload` représente l'état métier complet sérialisable du résultat d'assemblage.
   - **Règle d'acyclicité :** `export_payload` exclut formellement le champ `content_hash`.
2. **Calcul de l'empreinte (`content_hash`) :**
   - `content_hash = sha256(canonical_json(export_payload).encode("utf-8")).hexdigest()`.
   - Le digest porte sur un contenu entièrement déterminé sans inclure son propre digest.
3. **Format JSON canonique :**
   - Tri déterministe des clés (`sort_keys=True`).
   - Séparateurs stricts (virgule, deux-points avec espace normalisé).
   - Encodage UTF-8 strict.
   - Aucun horodatage dynamique ni identifiant volatile dans `export_payload`.
4. **Portée de l'empreinte :**
   - Garantit la reproductibilité bit-exacte du calcul et l'intégrité de transport.
   - **Limite dogmatique absolue :** Ne constitue en aucun cas une signature externe ni une preuve d'attestation B8.

---

## 7. Limites Statistiques et d'Attribution

- **Taille de l'échantillon :** Un seul fait matériel indépendant recensé (`16b9d28e...`).
- **Tests statistiques :** Le test de McNemar exact n'est pas implémenté (statistiques descriptives marginales uniquement).
- **Intervalles de confiance :** Score de Wilson calculé à titre strictement descriptif.
- **Attribution causale :** En présence d'appels simulés, `causal_effect_supported` est borné à `False`.
- **Statut final :** Le pilote produit un rapport consultatif au statut `HARNESS_VALIDATED`.
