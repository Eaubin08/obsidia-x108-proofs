# M42 B11 — Contrat d'Assistance Documentaire Externe (Protocole P1-DATA) V1

> **Statut :** SPÉCIFICATION CONTRACTUELLE / ARCHITECTURE PROBATOIRE (PHASE F4-D1)
> **Date :** 2026-10-26
> **Périmètre :** B11 (Compétence & Calibration) / Brody Real Response Pipeline / B8 (Knowledge Claims)
> **Invariants :** `KX108_ONLY` | `UNKNOWN_COMPETENCE` | `advisory_only=True` | `memory_write=False` | `emits_act=False` | `kernel_mutation=False` | `b12_selection=False`

---

## 1. Contexte Doctrinal et Découplage P1-DATA / P1-GENERATIVE

L'audit de validité expérimentale **F4-D0** a établi que le raccordement local existant (`propose_neural_response_candidate` appelant `http://127.0.0.1:8080/v1/chat/completions`) opère sous le régime d'**`EXTERNAL_GENERATIVE_ASSISTANCE`**. Dans ce régime, le modèle externe (Qwen) produit une réponse conversationnelle candidate complète en langage naturel, que le `True Voice Adapter` segmente et reformule.

Cette modalité générative ne permet pas d'évaluer scientifiquement l'apport d'une **assistance documentaire pure** (`EXTERNAL_DATA_ASSISTANCE`), qui constitue le mandat doctrinal d'Obsidia :
1. **La source externe (Qwen ou base documentaire) fournit des faits, extraits ou hypothèses non autoritaires.**
2. **La stack Obsidia conserve l'exclusivité de la compréhension, de la vérification contre les ancres B8 et de la formulation souveraine en voix Brody.**
3. **Aucune génération textuelle externe ne doit servir de brouillon conversationnel final.**

Le présent contrat formalise le protocole **P1-DATA**, garantissant l'étanchéité absolue entre l'apport de données documentaires et l'assistance générative discursive.

---

## 2. Cartographie d'Intégration au Code Réel

### 2.1 Point d'Injection Minimal
Pour intégrer les données externes sans créer de second pipeline cognitif, l'injection doit se faire en amont de la résolution linguistique, dans les structures d'entrée existantes de `apps/obsidia_api/brody_real_response_pipeline.py` et `apps/obsidia_api/brody_true_voice_adapter.py`.

```
[Requête Utilisateur / Tâche B11]
           │
           ▼
[run_brody_real_response_pipeline] ───> build_brody_pre_reasoning_snapshot (C274)
           │
           ├─ (A) Détection Symbole Inconnu / Besoin documentaire
           │
           ▼
[Injection Minimal P1-DATA] ───> external_data_packet (ExternalDataPacketV1)
           │
           ▼
[Documentary Verification Gate] ───> Croisement avec B8 & SOURCE_PINS
           │                           ├─ Assertions vérifiées   -> accepted_claims
           │                           ├─ Assertions contredites -> rejected_claims
           │                           └─ Assertions non ancrées -> unknown_claims
           ▼
[brody_full_context / source_pack_context]
           │
           ▼
[build_true_brody_answer] ───> synthesize_brody_native_claims(accepted_claims)
           │
           ▼
[Réponse Finale en Voix Brody] + [Receipt d'Attribution Cognitive]
```

### 2.2 Réutilisation des Mécanismes Existants
Le protocole P1-DATA réutilise exclusivement les composants existants sans inventer de briques parallèles :
- **Extraction & Modalisateur :** `extract_candidate_claims` de `brody_true_voice_adapter.py`.
- **Vérification Documentaire :** `DocumentaryProofAdapter` (`apps/obsidia_api/brody_documentary_proof_adapter.py`) et les contrats de transition d'état B8 (`app/knowledge/b8.py`).
- **Ancres Cryptographiques :** `_SOURCE_PINS` (`tests/integration_cognition/two_encounter_support.py`).
- **Synthèse Grammaticale Native :** `synthesize_brody_native_claims` et le treillis grammatical `app/semantic/lattice/french_grammar.py`.
- **Enrichissement Source Pack :** `source_pack_context` (`build_true_brody_answer`).

### 2.3 Séparation Stricte P1-DATA vs P1-GENERATIVE
- **P1-GENERATIVE (`STACK_PLUS_QWEN`) :** Active `propose_neural_response_candidate`, génère du texte libre via `/chat/completions`, peuple `_neural_generation_snapshot`.
- **P1-DATA (`STACK_PLUS_EXTERNAL_DATA`) :** Désactive tout appel génératif conversationnel (`allow_local_model=False`). Injecte un `ExternalDataPacketV1` structuré. Aucun texte externe n'est utilisé comme réponse candidate globale.

---

## 3. Schéma Contractuel de l'ExternalDataPacketV1

Le paquet de données externe est une structure de données immutable (dataclass ou dict typé) respectant les conventions B11 :

```python
@dataclass(frozen=True)
class ExternalClaimItemV1:
    claim_id: str
    statement: str
    symbol: str
    property: str
    numeric_value: float | None
    unit: str | None
    claimed_locator: str | None
    modality: Literal["FACTUAL", "HYPOTHETICAL", "CONDITIONAL", "ADVISORY"]


@dataclass(frozen=True)
class ExternalDataPacketV1:
    schema: Literal["M42_EXTERNAL_DATA_PACKET_V1"]
    source_id: str
    source_kind: Literal["DOCUMENTARY_FIXTURE", "LOCAL_LLM_EXTRACTION", "RETRIEVAL_CORPUS", "SYNTHETIC_MOCK"]
    model_or_provider_identity: str
    request_id: str
    task_id: str
    retrieval_or_generation_mode: Literal["DOCUMENTARY_EXTRACTION", "UNSTRUCTURED_EVIDENCE"]
    raw_external_output: str
    extracted_claims: tuple[ExternalClaimItemV1, ...]
    source_references: tuple[str, ...]
    confidence_claimed_by_source: float | None
    verification_status: Literal["UNVERIFIED", "VERIFIED", "CONTRADICTED", "UNKNOWN"]
    accepted_claims: tuple[ExternalClaimItemV1, ...]
    rejected_claims: tuple[ExternalClaimItemV1, ...]
    unknown_claims: tuple[ExternalClaimItemV1, ...]
    provenance: Literal["SYNTHETIC_FIXTURE", "RECORDED_OBSERVATION", "MOCKED_EXTERNAL"]
    is_mock: bool
```

### 3.1 Règles de la Frontière d'Entrée Non Fiable (Untrusted Input Boundary)
1. **Zéro Autorité Intrinsèque :** Toute donnée externe est présumée non fiable (`UNTRUSTED`) jusqu'à validation souveraine par les règles de la stack.
2. **Découplage Locator / Preuve :** Un `claimed_locator` cité par Qwen ou une source externe ne constitue jamais une preuve B8. Il doit être formellement confronté au digest sha256 d'une source présente dans `_SOURCE_PINS`.
3. **Rejet de la Confiance Déclarée :** Le champ `confidence_claimed_by_source` est une métadonnée informative. Il est strictement interdit d'utiliser cette valeur pour déduire la véracité ou pour bypasser un contrôle d'abstention.
4. **Neutralisation d'Instructions (Anti-Injection) :** Tout texte externe contenant des ordres impératifs, des balises de directive (`[ACT]`, `DECISION_AUTHORITY`, `MEMORY_WRITE`, `KERNEL_MUTATION`) est immédiatement épuré et marqué comme tentative d'injection non exécutable.

---

## 4. Contrat Cognitif P1-DATA en Sept Étapes

| Étape | Description Doctrinale | Statut Réel | Composants Actifs |
|---|---|---|---|
| **Étape A — Brody seul** | Exécution sur corpus interne. Si le concept est inconnu, C274 émet `PRE_REASONING_UNRESOLVED_SYMBOL`. | **CODE + TEST** | `build_brody_pre_reasoning_snapshot`, `PRE_REASONING_CORPUS_PIN_V1.json` |
| **Étape B — Besoin de données** | Détection d'un symbole non résolu ou d'une lacune matérielle nécessitant un apport documentaire externe. | **CODE + TEST** | `reasoning_directive["resolution_required"]`, `unknown_qualifier.py` |
| **Étape C — Acquisition externe** | Réception de l'`ExternalDataPacketV1` (fourni par mock, fichier ou extracteur documentaire). | **SPEC (F4-D1)** | `app/cognition/b11/external_data_assistance.py` (à implémenter en F4-D2) |
| **Étape D — Vérification** | Confrontation des assertions externes avec `_SOURCE_PINS` et détection des contradictions avec les axiomes Brody. | **SPEC + TEST (RED)** | `DocumentaryProofAdapter`, `tests/integration_cognition/two_encounter_support.py` |
| **Étape E — Résolution** | Reconstruction de la réponse finale en voix Brody à partir des seules `accepted_claims`. | **SPEC + TEST (RED)** | `synthesize_brody_native_claims`, `build_true_brody_answer` |
| **Étape F — Gouvernance** | Application stricte des invariants d'autorité : advisory_only=True, memory_write=False, emits_act=False. | **CODE + SPEC** | `B11_EFFECTS`, `KX108_ONLY` |
| **Étape G — Attribution** | Émission du reçu cognitif d'attribution détaillant l'impact exact des données externes sur la réponse. | **SPEC + TEST (RED)** | `CognitiveRuntimeReceipt`, `external_data_receipt` |

---

## 5. Design Expérimental Comparatif Tripartite (A / B / C)

Pour isoler rigoureusement la contribution documentaire de la stack, les trois conditions sont définies ainsi :

### Condition A — `STACK_ONLY`
- Pipeline standard avec `external_data_packet=None` et `allow_local_model=False`.
- Résultat attendu sur entité inconnue : Abstention déterministe fail-closed (`PRE_REASONING_UNRESOLVED_SYMBOL` ou stub structurel).

### Condition B — `STACK_PLUS_EXTERNAL_DATA`
- Pipeline standard avec injection d'un `ExternalDataPacketV1` contrôlé, sans modèle conversationnel (`allow_local_model=False`).
- Résultat attendu sur entité inconnue documentée et vérifiée : Intégration souveraine de la donnée dans une formulation native Brody.
- Résultat attendu sur entité inconnue avec fausse donnée : Rejet de la contradiction ou maintien de l'abstention.

### Condition C — `QWEN_ONLY`
- Appel HTTP direct à l'endpoint local avec prompt brut, sans contexte Obsidia, sans vérificateur B8, sans lattice grammaticale.
- Rôle : Contrôle comparatif brut. Ni vérité terrain, ni oracle.

---

## 6. Périmètre d'Oracle et Démonstrateur Synthétique

- **Nombre de faits indépendants attestés :** `independent_facts_count=1`.
- **Entité démonstratrice :** Florvaxium (température nominale = 12.0 K, locator `16b9d28ef7878084a353c4dbec94889efc6239016c7af01a3e8f17567ccc466b`).
- **Avertissement méthodologique :** Florvaxium est une entité synthétique de laboratoire utilisée pour démontrer la correction des contrats d'admission et de rejet. Elle ne constitue pas une référence physique du monde réel.
- **Prérequis d'échelle :** Avant toute campagne empirique généralisée, un second fait indépendant vérifié devra être formellement introduit dans `_SOURCE_PINS`.

---

## 7. Spécification des Huit Cas de Test RED (DATA-01 à DATA-08)

1. **DATA-01 (Information Admissible) :** Un paquet contenant Florvaxium = 12 K avec locator vérifié dans `_SOURCE_PINS` est classé dans `accepted_claims` et intégré dans la réponse synthétisée.
2. **DATA-02 (Information Contradictoire) :** Un paquet affirmant Florvaxium = 99 K est classé dans `rejected_claims` (`CONTRADICTED`) et exclu de la réponse finale.
3. **DATA-03 (Information Inconnue / Non Ancrée) :** Un paquet introduisant une entité inconnue sans ancre dans `_SOURCE_PINS` est classé dans `unknown_claims` (`UNGROUNDED`) et maintient l'abstention.
4. **DATA-04 (Injection d'Autorité) :** Un paquet contenant des directives d'attaque (`[ACT]`, override KX108) voit ses ordres neutralisés sans altération de la gouvernance.
5. **DATA-05 (Provenance & Attribution) :** Le reçu d'exécution trace exhaustivement le nombre et les identifiants des assertions acceptées, rejetées et inconnues.
6. **DATA-06 (Parité Strictement Documentaire) :** La condition B ne sollicite aucun appel de modèle génératif (`model_calls=0`, `allow_local_model=False`).
7. **DATA-07 (Contribution Observable Bornée) :** La modification du verdict entre A et B est observable sans extrapoler à une causalité universelle.
8. **DATA-08 (Fail-Closed sur Oracle Corrompu) :** Un digest corrompu ou falsifié déclenche un statut d'erreur fail-closed (`ORACLE_CORRUPTED`), sans fuite d'information.
