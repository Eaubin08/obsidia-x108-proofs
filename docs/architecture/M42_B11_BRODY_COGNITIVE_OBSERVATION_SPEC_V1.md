# M42 B11 Compétence & Calibration — Spécification d'Observation Cognitive Brody V1

## 1. Statut, périmètre et frontière doctrinale

- **Chapitre :** M42 — B11 Compétence et Calibration (Étage 4 : Observation cognitive consultative de Brody).
- **Couche :** Cognition / Gouvernance consultative (`app/cognition/b11/`).
- **Composant cible :** `app.cognition.b11.brody_observation_adapter` (`BrodyCognitiveObservationV1`, `load_and_verify_brody_observation`, `evaluate_brody_cognitive_observation`).
- **Mode d'autorité :** Purement consultatif, lecture seule stricte (`B11_EFFECTS` : `memory_write=False`, `emits_act=False`, `kernel_mutation=False`, `decision_authority="KX108_ONLY"`, `advisory_only=True`, `b12_selection=False`).
- **Séparation absolue des mécanismes :** Brody (`brody:cognitive_resolution`) est un mécanisme cognitif/symbolique distinct et orthogonal au mécanisme déterministe de mutation Rail A (`rail_a:governed_content_apply`). Aucune observation Rail A ne peut être attribuée à Brody (`CAUSAL_ATTRIBUTION_MISMATCH`), et inversement.
- **HOLD formel sur toute promotion de compétence :** Tout profil projeté demeure sous `CompetenceRegime.UNKNOWN_COMPETENCE` avec `confidence_score = 0.0`, `reliability_score = None`, `calibration_metric = None` et `b12_selection = False`.

---

## 2. Contrat de Données : `BrodyCognitiveObservationV1`

La structure `BrodyCognitiveObservationV1` est immuable (`frozen`) et encapsule l'observation unitaire d'un cycle cognitif de Brody.

### 2.1 Champs et Qualifications Épistémiques

| Groupe | Attribut | Type | Qualification | Définition & Règle d'invariance |
|---|---|---|---|---|
| **A. Identité** | `observation_id` | `str` | **OBSERVED** | Identifiant unique de l'observation cognitive (`brody-cogo-<hash>`). |
| | `execution_id` | `str` | **OBSERVED** | Identifiant technique du cycle (`signal_id` ou request session ID). |
| | `task_family` | `str` | **OBSERVED** | Famille cognitive (`"AMBIGUITY_RESOLUTION"`, `"DOCUMENTARY_VERIFICATION"`, `"LEXICAL_QUALIFICATION"`, `"COGNITIVE_SYNTHESIS"`). |
| | `task_ref` | `str` | **OBSERVED** | Tâche d'évaluation (ex. `"COGNITIVE_RESOLUTION"`). |
| | `mechanism_ref` | `str` | **OBSERVED** | Référence canonique (`"brody:cognitive_resolution:V1"`, `"brody:real_cognitive_join:C1_V1"`). |
| | `mechanism_version` | `str` | **OBSERVED** | Version attestée (`"REAL_COGNITIVE_JOIN_C1_V1"`). |
| | `input_context_digest` | `str` | **OBSERVED** | Empreinte SHA-256 (64 hex) du prompt d'entrée et contexte initial. |
| **B. Observation** | `observable_response` | `str \| None` | **OBSERVED** | Réponse textuelle finale émise ou `None` en cas de hold/blocage. |
| | `expressed_uncertainty_status` | `str` | **OBSERVED** | Statut d'incertitude (`"RESOLVED"`, `"AMBIGUOUS_COEXISTING_HYPOTHESES"`, `"UNRESOLVED_UNKNOWN"`, `"CLARIFICATION_HOLD"`, `"EXPLICIT_ABSTENTION"`). |
| | `components_health_status` | `dict[str, str]` | **OBSERVED** | Dictionnaire des statuts réels des composants (`"READY"`, `"DEGRADED"`, etc.). |
| | `documentary_refs` | `tuple[str, ...]` | **OBSERVED** | Références de reçus B8 (`resolution_refs`, `provenance_refs`). |
| | `documentary_status` | `str` | **OBSERVED** | Statut documentaire B8 (`"CORROBORATED"`, `"CONTRADICTED"`, `"UNVERIFIED"`, `"ABSENT"`). |
| | `external_provider_called` | `bool` | **OBSERVED** | `True` si un appel modèle distant/local (Qwen) a été émis (`model_calls > 0`). |
| | `external_provider_model` | `str \| None` | **OBSERVED** | Nom du fournisseur ou modèle externe si appelé, sinon `None`. |
| | `governance_compliance` | `bool` | **OBSERVED** | `True` si et seulement si `readonly=True`, `decision_authority="KX108_ONLY"` et `emits_act=False`. |
| **C. Garanties** | `structural_validation_status` | `str` | **DERIVED** | `"VALID"` si le reçu runtime est bien formé, sinon `"INVALID"`. |
| | `replay_status` | `str` | **DERIVED** | `"REPLAYABLE_DETERMINISTIC"` si entrées et graines sont épinglées, sinon `"NOT_REPLAYABLE"`. |
| | `integrity_verification_status` | `str` | **DERIVED** | `"STORE_SEALED"` si persisté sous ancre scellée, sinon `"EPHEMERAL_UNSEALED"`. |
| | `ground_truth_status` | `str` | **DERIVED** | `"INDEPENDENT_ORACLE_PINNED"`, `"CIRCULAR_SELF_REFERENTIAL"`, ou `"MISSING"`. |
| | `provenance_status` | `str` | **DERIVED** | `"PROVENANCE_UNESTABLISHED"` (par défaut sans grand livre certifié). |
| | `attribution_status` | `str` | **DERIVED** | `"STACK_ONLY"`, `"STACK_PLUS_EXTERNAL_MODEL"`, ou `"EXTERNAL_MODEL_RAW"`. |
| **D. Évaluation** | `evaluation_outcome` | `str` | **DERIVED** | Résultat formel : `"PASS"`, `"FAIL"`, `"ERROR"`, `"ABSTAIN_CORRECT"`, `"INDETERMINATE"`. |
| | `evaluation_notes` | `str` | **DERIVED** | Diagnostic explicatif de l'évaluation cognitive. |

Tout champ dont la preuve n'est pas établie doit porter explicitement `None`, `"MISSING"` ou `"UNESTABLISHED"`.

---

## 3. Frontières de Preuve et Garde-Fous Épistémiques

1. **`signal_id` $\neq$ identifiant d'exécution unique :** `signal_id` étant dérivé de `sha256(message + session_id)`, plusieurs requêtes identiques dans la même session partagent le même `signal_id`. L'identité d'exécution requiert un horodatage ou nonce distinct.
2. **Hash d'entrée $\neq$ origine de la donnée :** Un hachage SHA-256 atteste de l'intégrité du texte soumis, jamais de son authenticité historique ou de sa provenance légitime.
3. **Statut `READY` $\neq$ exactitude factuelle :** Un reçu portant `status="READY_SHADOW_READONLY"` prouve uniquement la terminaison sans exception non gérée du pipeline logiciel ; il ne garantit en rien la véracité cognitive de la réponse.
4. **Contrôle B8 $\neq$ vérité universelle du monde :** La validation B8 atteste de la fidélité d'un claim par rapport à un document source épinglé (`SOURCE_PINS`). Elle ne prouve pas que le document source décrit un fait physique réel.
5. **Réponse pure $\neq$ compétence générale :** L'absence d'hallucination ou de fuite de mémoire (`data_purity_agent_result["is_pure"] == True`) atteste de la conformité du filtre, pas de la compétence du modèle à résoudre des tâches inconnues.
6. **Abstention $\neq$ échec :** Une abstention explicite (`CLARIFICATION_HOLD`, `STILL_UNRESOLVED`) face à des prémisses insuffisantes ou ambiguës est un comportement rigoureux. Elle ne devient `ABSTAIN_CORRECT` que si un oracle indépendant confirme que la tâche exigeait l'abstention. En l'absence d'oracle, le résultat est `INDETERMINATE`, jamais `FAIL`.
7. **Reçu éphémère $\neq$ historique vérifié :** Un reçu circulant en mémoire dans un payload HTTP relève de `TRACE_EPHEMERAL` ; il ne peut être qualifié d'observation historique scellée (`INTEGRITY_VERIFIED`).
8. **Reçu scellé $\neq$ réponse exacte :** La persistance scellée garantit l'invariance des octets consignés, pas la véracité cognitive de leur contenu.
9. **Indépendance stricte de l'oracle :** Un oracle de test n'est indépendant que s'il est épinglé isolément avant l'exécution. Tout oracle dérivé de la sortie de Brody ou du transport modèle est rejeté pour circularité (`CIRCULAR_SELF_REFERENTIAL`).

---

## 4. Attribution des Contributions et Séparation des Mécanismes

1. **Stack Brody seule (`STACK_ONLY`) :** Résolution interne via corpus lexical, détection B7, validation documentaire B8 et True Voice, sans émission de requêtes vers un modèle externe (`model_calls == 0`).
2. **Stack Brody + Modèle externe (`STACK_PLUS_EXTERNAL_MODEL`) :** Propositions textuelles générées par Qwen, filtrées, bornées et contraintes par B8 et True Voice. La présence d'un appel externe ne prouve pas que le succès ou l'échec est causé par le modèle externe.
3. **Fournisseur externe seul (`EXTERNAL_MODEL_RAW`) :** Évaluation isolée du texte brut émis par le modèle externe dans un protocole de comparaison séparé, hors pipeline Brody.
4. **Non-attribution à Qwen :** Qwen est un fournisseur externe passif d'échantillons textuels bruts. Aucune direction, cognition supérieure ou autorité n'est attribuée à Qwen.
5. **Non-attribution Rail A $\leftrightarrow$ Brody :** Séparation causale stricte. Une réussite de compilation ou de patch Rail A n'apporte aucune preuve sur Brody.

---

## 5. Contrats d'Évaluation par Famille de Tâches

| Famille | Tâche évaluable | Référence de vérité | `PASS` | `FAIL` | `ABSTAIN_CORRECT` |
|---|---|---|---|---|---|
| **A. B7/M41** | Résolution d'ambiguïté | Oracle d'ambiguïté annoté | Ambiguïté détectée, hypothèses maintenues sans gagnant forcé | Sélection arbitraire d'hypothèse ou ambiguïté manquée | Abstention explicite (`STILL_UNRESOLVED`) sous preuve incomplète |
| **B. B8** | Corroboration documentaire | Document source épinglé (`SOURCE_PINS`) | Claim corroboré conforme au document source | Claim faux admis ou claim valide rejeté | Contradiction détectée (`DOCUMENT_ASSERTION_CONTRADICTED`) et rejetée |
| **C. Lexique** | Qualification d'inconnues | Base lexicale épinglée (`lexicon.db`) | Inconnues réelles correctement isolées et typées | Terme inconnu admis comme canonique ou inverse | N/A (classification binaire) |
| **D. Synthèse** | Réponse True Voice | Contrat de pureté et claims B8 | Réponse pure, sourcée, exempte d'hallucinations | Injection de faits non prouvés ou fuite de mémoire | `CLARIFICATION_HOLD` légitime face à un manque d'information |

---

## 6. Échelle des 6 Niveaux de Preuve Cognitive

1. `TRACE_EPHEMERAL` : Dictionnaire en mémoire vive (réponse HTTP / fastpath).
2. `STRUCTURALLY_VALIDATED` : Schéma validé passivement, invariants de gouvernance vérifiés.
3. `REPLAYABLE` : Paramètres d'entrée, graines et documents sources épinglés pour ré-exécution déterministe.
4. `INTEGRITY_VERIFIED` : Artefacts d'entrée/sortie persistés sous magasin scellé avec hachage SHA-256 croisé.
5. `INDEPENDENTLY_EVALUATED` : Sortie confrontée à un contrat d'évaluation cognitif et un oracle de vérité terrain indépendant.
6. `EMPIRICALLY_CHARACTERIZABLE` : Observation admise par le moteur B11, intégrée au profil descriptif sans extrapolation inductive.

---

## 7. Matrice des Scénarios RED (BRO-01 à BRO-12)

| Code | Scénario | Entrée & Conditions | Comportement attendu |
|---|---|---|---|
| **BRO-01** | Reçu valide mais éphémère | Reçu HTTP bien formé sans ancre de store scellé | Admis en `STRUCTURALLY_VALIDATED` ; rejeté pour caractérisation historique scellée (`EPHEMERAL_UNSEALED`). |
| **BRO-02** | Reçu forgé ou auto-attesté | Dictionnaire injecté manuellement avec `evaluation_outcome="PASS"` prétendu | Rejet fail-closed immédiat (`SELF_ATTESTATION_REJECTED`) ; aucune promotion de preuve. |
| **BRO-03** | Réponse exacte avec oracle indépendant | Réponse Brody corroborée par document source épinglé | Évalué `PASS`, borné strictement au contexte et au document testé. |
| **BRO-04** | Réponse conforme mais fausse | Réponse structurellement valide mais en contradiction avec l'oracle | Évalué `FAIL` cognitif ; conformité structurelle préservée séparément. |
| **BRO-05** | Ambiguïté B7/M41 maintenue | Entrée intrinsèquement ambiguë, oracle confirmant l'absence de solution unique | Hypothèses multiples préservées sans gagnant forcé ; évalué `ABSTAIN_CORRECT`. |
| **BRO-06** | Abstention sans référence indépendante | `CLARIFICATION_HOLD` émis en l'absence d'oracle indépendant de vérité terrain | Évalué `INDETERMINATE` ; refus de prononcer arbitrairement un `ABSTAIN_CORRECT` ou un `FAIL`. |
| **BRO-07** | Contradiction documentaire B8 | Entrée contradictoire avec le document source épinglé | Détection de `DOCUMENT_ASSERTION_CONTRADICTED` ; rejet de l'admission en mémoire. |
| **BRO-08** | Appel fournisseur externe traçable | Consultation avec $M=1$ round de modèle externe | `external_provider_called = True`, `attribution_status = "STACK_PLUS_EXTERNAL_MODEL"`, causalité non inférée. |
| **BRO-09** | Oracle auto-référent ou circulaire | Oracle dérivé de la réponse même de Brody ou non isolé | Détection de circularité (`CIRCULAR_SELF_REFERENTIAL`) ; rejet de l'évaluation indépendante. |
| **BRO-10** | Attribution croisée Rail A $\to$ Brody | Observation Rail A présentée pour évaluer le mécanisme Brody | Rejet strict `CAUSAL_ATTRIBUTION_MISMATCH` ; exclusion totale des observations ($N_{\text{retained}}=0$). |
| **BRO-11** | Contexte d'entrée non épinglé | Trace produite sans capture des graines ou documents d'entrée | `replay_status = "NOT_REPLAYABLE"` ; déclassement en `NON_REPLAYABLE_TRACE`. |
| **BRO-12** | Invariants de gouvernance et B11_EFFECTS | Exécution complète d'observation | Maintien absolu de `UNKNOWN_COMPETENCE`, `confidence_score=0.0`, `reliability_score=None`, `calibration_metric=None`, `B11_EFFECTS` scrupuleusement respecté. |
