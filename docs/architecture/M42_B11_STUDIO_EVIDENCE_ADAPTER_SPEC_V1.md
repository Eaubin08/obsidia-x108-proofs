# Spécification Architecture — M42/B11 — Studio Evidence Adapter V1

**Statut :** CANDIDATE / SPEC REVISED (Correction F-F3-01) / NON IMPLEMENTED  
**Mode :** READ_ONLY APPLIED / ZERO RUNTIME MUTATION  
**Autorité :** KX108_ONLY  
**Couche :** CONNECTORS / B11 COGNITION  
**Contrat cible :** `app/cognition/b11/studio_evidence_adapter.py`  

---

## 1. Contexte et Objectifs

L'intégration M42/B11 a établi :
1. Le scellement cryptographique des faisceaux de preuves cognitives (`BrodyCognitiveEvidenceBundleV1`, BCE V1) sous schéma fermé à 19 champs ;
2. Le pont d'assemblage et de réexécution symbolique déterministe B8 (`BrodyCognitiveEvidenceBridgeV1`) ;
3. L'évaluateur cognitif indépendant (`CognitiveIndependentEvaluatorV1`, E3).

Parallèlement, le dépôt **Brody Studio** (`C:\Users\User\obsidia-studio`, HEAD `637dd86`) a formalisé et testé en offline les contrats de consommation E11/B6 et d'admission éditoriale V1 et V2 (`studio_e11_contract.py`, `studio_native_editorial.py`), validés sur des fixtures canoniques réelles (`public_fixture_False.json`, `public_fixture_V2_False.json`).

L'objectif de cette spécification est de définir le contrat d'un adaptateur de frontière pur :
```text
Studio Real Receipt (E11 / V1 / V2) ──> [studio_evidence_adapter] ──> BCE V1 Payload (19 champs) ──> E3 Evaluator
```
Sans muter ni le noyau de calcul Brody, ni le client Studio, ni usurper le scellement ou l'autorité de vérification.

---

## 2. Matrice Champ par Champ : Provenance et Dérivation BCE V1

### 2.1 Classification des Statuts de Preuve
- **ORIGINAL :** Donnée présente directement dans le reçu Studio ou C1.
- **DERIVED :** Calcul déterministe pur (ex. SHA-256) sans injection de sémantique non prouvée.
- **REFERENCED :** Référence transmise pour traçabilité, non réexécutée localement.
- **MISSING :** Donnée absente du flux source.
- **UNATTESTED :** Donnée mentionnée mais dont l'origine cryptographique ou la conformité n'est pas vérifiable.

### 2.2 Matrice Complète Réconciliée des 19 Champs Canoniques BCE V1

| # | Champ BCE V1 | Source Studio / C1 | Transformation Admissible | Statut Preuve | Nature dans BCE V1 |
|---|---|---|---|---|---|
| 1 | `contract_version` | Règle `CognitiveEvidencePublisher` | Entier `1` (`int = 1`) | DERIVED | Attendu payload final (int) |
| 2 | `execution_id` | `receipt.signal_id` | `str(receipt["signal_id"])` | ORIGINAL | Natif Studio |
| 3 | `mechanism_ref` | `final_answer_source` | `"brody:studio_editorial"` ou source certifiée | DERIVED | Attendu payload final |
| 4 | `mechanism_version` | `receipt.version` / en-tête V1/V2 | `str(receipt.get("version", "REAL_COGNITIVE_JOIN_C1_V1"))` | ORIGINAL | Natif Studio |
| 5 | `execution_timestamp_utc` | `receipt.created_at` | Format ISO-8601 UTC certifié | ORIGINAL | Natif Studio |
| 6 | `input_context_digest` | `pre_reasoning_snapshot.user_message` | `hashlib.sha256(msg.encode("utf-8")).hexdigest()` | DERIVED | Calcul déterministe |
| 7 | `documentary_refs` | `source_file_refs` / `entries` E11 | Tuple ou liste normalisée de locators | ORIGINAL / REFERENCED | Natif Studio |
| 8 | `symbolic_context_refs` | `cognition_shadow_memory.entries` | Identifiants d'état et étiquettes B6 | ORIGINAL / REFERENCED | Natif Studio |
| 9 | `external_provider_trace` | `local_model_evidence_snapshot` | Normalisation dict (`causal_contribution_verified=False`) | ORIGINAL / DERIVED | Natif Studio |
| 10 | `observable_response_digest` | `editorial_artifact.draft.text` | `hashlib.sha256(text.encode("utf-8")).hexdigest()` | DERIVED | Calcul déterministe |
| 11 | `observable_response_text` | `editorial_artifact.draft.text` | Extraction de la chaîne textuelle `<POST>` | ORIGINAL | Natif Studio |
| 12 | `evaluation_reference` | Paramètre oracle externe | Transmission de l'oracle E3 ou `{}` | REFERENCED | Externe indépendant |
| 13 | `replay_dependencies` | Pins et hashes de composants | Dictionnaire de hashes validés | DERIVED / REFERENCED | Calcul déterministe |
| 14 | `privacy_classification` | En-têtes Studio | `"INTERNAL_AUDIT_ONLY"` ou `"PUBLIC_SAFE"` | DERIVED | Attendu payload final |
| 15 | `publication_mode` | `publication_permitted` | `"DRAFT_ONLY"` (`False` -> `"DRAFT_ONLY"`) | DERIVED | Attendu payload final |
| 16 | `seal_status` | Adaptateur de frontière | `"UNSEALED_ADAPTER_PAYLOAD"` ou `"EPHEMERAL_IN_MEMORY"` | DERIVED | Attendu (non scellé store) |
| 17 | `provenance_status` | Adaptateur de frontière | `"STUDIO_E11_ADAPTED"` | DERIVED | Attendu payload final |
| 18 | `integrity_digest` | Payload canonique JSON pré-scellement | SHA-256 de `json.dumps(payload_sans_hash, sort_keys=True)` | DERIVED | Calcul déterministe BCE |
| 19 | `bundle_id` | `integrity_digest` dérivé | `f"bceb-{integrity_digest[:32]}"` | DERIVED | Calcul déterministe BCE |

> **Règle de Scellement Réconciliée (Section 4) :**
> L'algorithme de calcul de `integrity_digest` et de `bundle_id` réutilise strictement la règle canonique de `CognitiveEvidencePublisher` :
> ```python
> data_for_hash = {k: v for k, v in payload.items() if k not in ("integrity_digest", "bundle_id")}
> norm_bytes = json.dumps(data_for_hash, sort_keys=True, ensure_ascii=False).encode("utf-8")
> integrity_digest = hashlib.sha256(norm_bytes).hexdigest()
> bundle_id = f"bceb-{integrity_digest[:32]}"
> ```

---

## 3. Frontières et Interdictions Strictes

### 3.1 Frontière B6 (Omission Contexte) ↔ M41 (Ambiguïté Ontologique)
- **Interdiction Formelle :** Une omission de contexte B6 (`B6_OMISSIONS`, `B6_UNKNOWNS`) dans un reçu Studio ne prouve PAS l'existence d'une pluralité d'hypothèses M41 concurrentes.
- **Règle :** L'adaptateur ne synthétise aucun `WorldHypothesisSet` artificiel. Si M41 n'est pas instancié dans le reçu original, le champ reste absent ou marqué `M41_COVERAGE_UNATTESTED`.
- **Comportement E3 :** Si un test d'abstention requiert une ambiguïté M41 non prouvée dans le bundle, le verdict de l'évaluateur E3 doit obligatoirement être `INDETERMINATE`.

### 3.2 Statut `CONTEXT_LIMITED` ↔ Abstention Épistémique
- **Interdiction Formelle :** `CONTEXT_LIMITED` dans Studio est un statut d'observation consommateur, pas une démonstration d'abstention cognitive correcte.
- **Règle :** Pour qualifier un `ABSTAIN_CORRECT`, l'évaluateur E3 exige la conjonction :
  1. D'une exigence explicite d'abstention dans l'oracle (`requires_abstention=True`) ;
  2. D'une réserve réellement exprimée dans le texte observable ;
  3. D'une justification causale ou symbolique attestée.
  Sans cette conjonction, le statut reste `INDETERMINATE` ou `FAIL`.

### 3.3 Évaluation Éditoriale ↔ Évaluation Cognitive
- **Frontière Étanche :** La conformité éditoriale de Studio (structure en 4 paragraphes, absence de répétition lexicale, respect des balises `<POST>`) certifie la qualité de réalisation de forme.
- **Règle :** Cette conformité ne constitue **JAMAIS** une preuve de correction factuelle. L'adaptateur isole le texte observable pour l'évaluateur E3, qui juge exclusivement la conformité aux faits de l'oracle de référence.

### 3.4 Non-Usurpation du Scellement BCE
- L'adaptateur est un transformateur de données, **pas une autorité de scellement**.
- Il ne doit jamais émettre un `seal_status="STORE_SEALED"` ni un `provenance_status="ORIGIN_ESTABLISHED"`.
- Ces statuts sont réservés au `BrodyEvidenceStore` lors de l'écriture physique contrôlée. L'adaptateur retourne `seal_status="UNSEALED_ADAPTER_PAYLOAD"` ou `"EPHEMERAL_IN_MEMORY"`.

---

## 4. Contrat d'Oracle Réconcilié pour l'Évaluateur E3 (Résolution F-F3-01)

L'évaluateur `evaluate_brody_cognitive_evidence_bundle` valide en étape 4 la présence du document oracle dans `_SOURCE_PINS` via sa clé `locator`.

Pour qu'un test factuel (F3-03 / F3-04) soit recevable :
1. **Document source épinglé :** Le document associé doit être présent dans `_SOURCE_PINS` (ex. `locator="16b9d28ef7878084a353c4dbec94889efc6239016c7af01a3e8f17567ccc466b"`, énonçant `"La température de florvaxium est de 12 K."`).
2. **Assertion typée attendue :** L'oracle doit définir `expected_assertion={"symbol": "florvaxium", "property": "temperature", "numeric_value": 12.0, "unit": "K"}`.
3. **Discrimination PASS/FAIL pure :**
   - **Même oracle, même locator, même assertion attendue** pour F3-03 et F3-04.
   - En F3-03, la réponse observable énonce `"12 K"` -> Verdict `PASS`.
   - En F3-04, la réponse observable énonce `"99 K"` -> Verdict `FAIL` (motif `CONTRADICTION`).
   - La causalité du verdict repose exclusivement sur le contenu de la réponse observable.

---

## 5. Interface Candidate du Module futur

Fichier cible : `app/cognition/b11/studio_evidence_adapter.py`

```python
def adapt_studio_receipt_to_bundle_payload(
    studio_payload: Mapping[str, Any],
    evaluation_reference: Mapping[str, Any] | None = None,
    replay_mode: str = "DETERMINISTIC_OFFLINE",
) -> dict[str, Any]:
    """Transforme purement un reçu d'exécution Studio E11/V1/V2 en payload canonique BCE V1 (19 champs).

    Invariants :
    - Pureté : zéro écriture disque, zéro requête réseau, zéro mutation d'arguments.
    - Fail-closed : lève ValueError si les invariants Studio/KX108 sont violés.
    - Sceau : seal_status="UNSEALED_ADAPTER_PAYLOAD" ou "EPHEMERAL_IN_MEMORY" (jamais STORE_SEALED).
    - contract_version : int = 1.
    """
    ...
```
