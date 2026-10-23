# M42 B11 Compétence & Calibration — Spécification Brody Cognitive Evidence Bundle V1

## 1. Statut, rôle et frontières doctrinales

- **Chapitre :** M42 — B11 Compétence et Calibration (Étage 5 : Preuves cognitives rejouables et scellement d'évidence).
- **Couche :** Cognition / Gouvernance consultative (`app/cognition/b11/`).
- **Composant cible futur :** `app.cognition.b11.brody_evidence_store` (`BrodyCognitiveEvidenceBundleV1`, `publish_brody_evidence_bundle`, `load_and_verify_brody_evidence_bundle`, `B11CognitiveEvidenceReader`, `project_b11_bundle_competence_profile`).
- **Route architecturale retenue :** Option B — Adaptateur de preuve cognitive spécialisé et léger, réutilisant strictement les primitives matérielles de publication atomique exclusive d'Obsidia (`os.link`, flush, fsync hors dépôt).
- **Règle absolue de non-contamination :** Aucune réutilisation des schémas de fichiers du Rail A (`target_path`, `pre_write_sha256`, `SealedRollbackEvidence`). Un cycle cognitif ne modifie aucun fichier de code source (`memory_write=False`, `kernel_mutation=False`).
- **Invariance de gouvernance B11_EFFECTS :** Toute observation, vérification ou rejeu dans B11 est strictement consultatif (`decision_authority="KX108_ONLY"`, `memory_write=False`, `emits_act=False`, `advisory_only=True`, `b12_selection=False`).
- **Maintien impératif sous UNKNOWN_COMPETENCE :** Tant que les seuils statistiques $N_{\min}$ et protocoles de répétition ne sont pas complétés, tout profil projeté conserve `confidence_score = 0.0`, `reliability_score = None`, `calibration_metric = None` et `b12_selection = False`.
- **Politique V1 à schéma fermé :** Aucun champ non déclaré n'est toléré dans le bundle V1 (`EXTRA_FIELDS_REJECTED`). Tout snapshot de données doit être structurellement typé et normalisé en structures récursivement immuables.

---

## 2. Séparation formelle des responsabilités (3 Rôles)

La doctrine Obsidia impose la dissociation hermétique des acteurs intervenant sur le cycle de vie de la preuve :

```
+-------------------------------------------------------------------------------+
| 1. CognitiveEvidencePublisher (infrastructure de publication hors B11)         |
|    - Valide et normalise le payload sous schéma fermé V1                      |
|    - Applique la politique de rejet des secrets et données sensibles (PII)    |
|    - Ignore ou rejette tout seal_status="STORE_SEALED" injecté en amont       |
|    - Écrit en fichier temporaire .tmp frère, flush() + os.fsync()             |
|    - Publie atomiquement via os.link (PUBLICATION_ATOMIC) vers le store local |
+-------------------------------------------------------------------------------+
                                      |
                                      v [Magasin scellé local append-only]
+-------------------------------------------------------------------------------+
| 2. CognitiveEvidenceVerifier (utilitaire passif de lecture et validation)     |
|    - Relit les octets scellés depuis le disque à chaque accès                |
|    - Recalcule le SHA-256 canonique et compare bit-à-bit (INTEGRITY_VERIFIED) |
|    - Détecte toute altération matérielle (IMMUTABILITY_VIOLATION)            |
|    - Qualifie l'origine en ORIGIN_UNESTABLISHED sans attestation externe      |
|    - Aucune écriture disque, aucune modification d'état                       |
+-------------------------------------------------------------------------------+
                                      |
                                      v [Bundle intègre certifié]
+-------------------------------------------------------------------------------+
| 3. B11CognitiveEvidenceReader (consommateur purement consultatif B11)         |
|    - Décode le bundle en BrodyCognitiveObservationV1                          |
|    - Confronte la sortie aux oracles de test indépendants                     |
|    - Zéro écriture matérielle : interdiction absolue de publier un bundle     |
|    - Maintient B11_EFFECTS (zéro I/O disque, zéro décision, zéro ACT)        |
|    - Projette le profil sous CompetenceRegime.UNKNOWN_COMPETENCE              |
+-------------------------------------------------------------------------------+
```

### Règles d'herméticité des rôles :
1. `evaluate_brody_cognitive_observation`, `project_b11_competence_profile` et les lecteurs B11 ne possèdent aucune capacité d'écriture et ne doivent **jamais** appeler `publish_brody_evidence_bundle`.
2. Même si le code réside dans `app.cognition.b11.brody_evidence_store`, la séparation fonctionnelle entre publication (`CognitiveEvidencePublisher`), vérification (`CognitiveEvidenceVerifier`) et lecture B11 (`B11CognitiveEvidenceReader`) est absolue.
3. Les tests vérifient l'absence matérielle d'écriture (surveillance effective du système de fichiers) lors de toute invocation de lecture.

---

## 3. Contrat de Données : `BrodyCognitiveEvidenceBundleV1`

Le bundle est une structure à **schéma fermé** et à **immuabilité transitive (deep immutability)**.

### 3.1 Normalisation et deep immutability
- Une `dataclass(frozen=True)` ne protégeant que les références de premier niveau, tous les conteneurs internes (`dict`, `list`) sont récursivement normalisés à la construction en structures immuables (`tuple` de paires clef-valeur ou `MappingProxyType`).
- Toute tentative de mutation interne sur `external_provider_trace`, `replay_dependencies` ou `evaluation_reference` lève une exception `TypeError`.
- Les objets dynamiques arbitraires (instances de classes non déclarées, lambdas, générateurs) sont formellement exclus à la validation d'entrée.

### 3.2 Définition des champs liés (Schéma Fermé)

| Champ | Type | Qualification | Rôle dans l'intégrité | Données interdites & Garde-fous |
|---|---|---|---|---|
| `contract_version` | `int` | **OBSERVED** | Version du schéma (`1`). | Version entière strictement positive (`1`). Tout autre entier est rejeté. |
| `bundle_id` | `str` | **DERIVED** | Identifiant unique canonique (`bceb-<32 hex>`). | Doit être strictement dérivé de l'empreinte `integrity_digest`. |
| `execution_id` | `str` | **OBSERVED** | Identifiant technique du cycle (`exec-<12 hex>` ou session). | Ne garantit pas l'unicité globale (collision possible). |
| `mechanism_ref` | `str` | **OBSERVED** | Identité du mécanisme (`"brody:cognitive_resolution"`). | Interdiction formelle d'indiquer un mécanisme Rail A (`"rail_a:*"`). |
| `mechanism_version` | `str` | **OBSERVED** | Version attestée (`"REAL_COGNITIVE_JOIN_C1_V1"`). | Ne doit pas être altéré par l'appelant. |
| `execution_timestamp_utc`| `str` | **OBSERVED** | Horodatage ISO 8601 UTC de l'exécution. | Format strict `YYYY-MM-DDTHH:MM:SSZ`. |
| `input_context_digest` | `str` | **OBSERVED** | SHA-256 (64 hex) du message d'entrée et contexte initial. | Atteste de l'empreinte du prompt ; n'établit pas l'origine légitime. |
| `documentary_refs` | `tuple[str, ...]` | **OBSERVED** | Identifiants de claims B8 (`fixture:...` ou `b8claim_*`). | Références aux claims documentaires admissibles uniquement. |
| `symbolic_context_refs` | `tuple[str, ...]` | **OBSERVED** | Identifiants d'état B7 (`sens:frame`) et M41 (`set_id`). | Doit pointer vers des structures symboliques canoniques. |
| `external_provider_trace` | `Mapping[str, Any]`| **OBSERVED** | Traces d'appel modèle distant (`called`, `model`, `calls`).| Tracé factuel sans inférence causale d'intelligence ou d'autorité. |
| `observable_response_digest`| `str` | **OBSERVED** | SHA-256 (64 hex) de la réponse émise ou snapshot de sortie. | Permet la vérification bit-à-bit sans fuite de texte secret. |
| `observable_response_text`| `str \| None` | **OBSERVED** | Texte final émis ou `None` si expurgé. | Aucune donnée personnelle, mot de passe ou secret d'authentification. |
| `evaluation_reference` | `Mapping[str, Any] \| None` | **DERIVED** | Référence d'oracle de test (`locator`, `statement`, `world_fact`).| Rejet absolu de tout oracle circulaire issu de Brody (`source="SELF"`). |
| `replay_dependencies` | `Mapping[str, Any]`| **DERIVED** | Métadonnées de rejeu (`replay_mode`, `pinned_document_digests`).| Doit spécifier le mode de rejeu sans présumer de reproduction bit-exacte. |
| `privacy_classification`| `str` | **DERIVED** | Qualification de confidentialité (`"SYNTHETIC_REDACTED"`).| `"CONTAINS_PII_REJECTED"` entraîne le blocage immédiat de publication. |
| `publication_mode` | `str` | **DERIVED** | Mode de publication atomique (`"PUBLICATION_ATOMIC"`). | Qualifie la mécanique de publication locale exclusive via `os.link`. |
| `seal_status` | `str` | **DERIVED** | Statut matériel (`"EPHEMERAL_IN_MEMORY"` ou `"STORE_SEALED"`).| Ignoré si fourni en entrée. Attribué exclusivement après scellement disque. |
| `provenance_status` | `str` | **DERIVED** | Statut d'origine (`"ORIGIN_UNESTABLISHED"`). | Atteste qu'aucune signature cryptographique externe n'est établie. |
| `integrity_digest` | `str` | **DERIVED** | SHA-256 complet sur l'ensemble des champs normalisés UTF-8. | Re-calculé à la lecture et comparé bit-à-bit. |

Tout champ supplémentaire présent dans le payload d'entrée est rejeté (`EXTRA_FIELDS_REJECTED`).

---

## 4. Échelle Épistémique et Séparation des Garanties

Il est formellement interdit de confondre les garanties suivantes :

### 4.1 Intégrité vs Origine vs Publication (BCE-F01)
1. **`INTEGRITY_VERIFIED` :** Les octets relus sur le disque ont une empreinte SHA-256 strictement identique à `integrity_digest`. Prouve mathématiquement la non-corruption du fichier par rapport à son empreinte ; ne prouve **pas** l'origine historique ou l'authenticité de l'auteur.
2. **`ORIGIN_UNESTABLISHED` :** Le bundle provient d'un environnement applicatif local sans clé de signature asymétrique externe (RFC3161 ou PKI de grand livre). L'origine de l'appelant n'est donc **pas établie** par le hachage.
3. **`PUBLICATION_ATOMIC` :** L'écriture a suivi la séquence staging temporaire + `flush()` + `os.fsync()` + liaison dure `os.link`. Garantit l'absence d'écriture partielle et la détection d'écrasement concurrent, mais ne confère **aucune impossibilité de remplacement** par un acteur système privilégié disposant des droits administrateur sur le disque.
4. **`STORE_SEALED` :** Qualifie un scellement applicatif local sur disque par lien dur exclusif, et **non une attestation externe infalsifiable**. L'intégrité doit être systématiquement **revérifiée à chaque lecture**.

### 4.2 Rejouabilité : Niveaux formellement disjoints (BCE-F03)
1. **`TRACE_REPLAYABLE` :** Relecture cohérente et vérification hors-ligne de la séquence des artefacts enregistrés (entrées, traces d'appels, sorties intermédiaires, réponse stockée). N'implique aucune réexécution de calcul.
2. **`SYMBOLIC_REEXECUTION` :** Réexécution déterministe des modules logiques/symboliques (B7 résolution de coréférence, M41 hypothèses, B8 validation de claims) lorsque leurs dépendances et documents épinglés sont présents.
3. **`NEURAL_REEXECUTION` :** Nouvelle inférence par un modèle de langage (ex. Qwen). Dépend impérativement de l'environnement matériel, des pilotes GPU/CUDA, de la quantification et des graines. Stochastique par nature, elle ne garantit **jamais** une identité bit-à-bit.
4. **`BIT_EXACT_REPLAY_VERIFIED` :** Identité bit-à-bit effectivement constatée par comparaison directe des sorties générées lors d'un rejeu. Elle n'est **jamais présumée a priori**, même en présence de graines aléatoires et de condensats de poids de modèles.

---

## 5. Politique de Confidentialité V1 (BCE-F02)

1. **Schéma fermé et données synthétiques :** Seuls les champs explicitement autorisés au §3.2 sont admis. Aucun champ dynamique brut ne peut être injecté. Les harnais de test utilisent exclusivement des données synthétiques.
2. **Rejet des secrets et motifs sensibles :** Le publisher vérifie l'absence de motifs reconnaissables de secrets (clés d'API, tokens de type `sk-...`, jetons d'autorisation `Bearer`, identifiants d'accès, numéros de sécurité sociale ou bancaires). La détection d'un secret déclenche le rejet immédiat (`PRIVACY_VIOLATION_REJECTED` / `CONTAINS_PII_REJECTED`) et bloque toute écriture sur disque.
3. **Absence de prétention à la détection universelle :** Le système V1 **ne prétend pas résoudre la détection universelle des données personnelles (PII)** en langage naturel non structuré. Les filtres constituent une défense en profondeur, non une certification d'anonymat.
4. **Digests et identifiants corrélables :** Les empreintes SHA-256 (`input_context_digest`, `observable_response_digest`) et les identifiants techniques sont potentiellement corrélables (attaques par dictionnaire sur messages courts, analyse fréquentielle). Ils constituent une **pseudonymisation technique locale**, et ne doivent pas être assimilés à une **anonymisation absolue**.
5. **Aucun raccordement à des conversations réelles :** L'adaptateur de bundle V1 est strictement interdit de raccordement à des flux d'utilisateurs réels ou des logs de production.
6. **Interdiction de rétention en production :** Aucune persistance à long terme en production n'est autorisée tant qu'une politique de cycle de vie, de rétention maximale et de purge n'a pas été formellement spécifiée et approuvée.

---

## 6. Matrice des Scénarios RED (BCE-01 à BCE-12)

| Code | Scénario | Conditions & Entrée | Comportement attendu |
|---|---|---|---|
| **BCE-01** | Publication atomique et vérification conforme | Bundle synthétique complet sous schéma fermé V1 | Publication `STORED`, `PUBLICATION_ATOMIC` ; rechargement avec `INTEGRITY_VERIFIED`, `STORE_SEALED`, `ORIGIN_UNESTABLISHED` sans confusion des statuts. |
| **BCE-02** | Altération matérielle d'artefact sur disque | Modification d'un octet dans le fichier scellé | Détection obligatoire à la lecture sous `INTEGRITY_MISMATCH` / `IMMUTABILITY_VIOLATION` ; l'intégrité n'est jamais présumée. |
| **BCE-03** | Référence croisée manquante | Bundle référençant un document B8 absent du registre local | Rejet fail-closed en `REPLAY_DEPENDENCY_MISSING` / `INVALID_CROSS_REFERENCE`. |
| **BCE-04** | Bundle forgé ou auto-attesté | Payload injecté contenant `evaluation_outcome="PASS"` ou un `seal_status="STORE_SEALED"` falsifié | Rejet strict sous `FORGED_BUNDLE_REJECTED` ; statut d'origine maintenu `ORIGIN_UNESTABLISHED` sans promotion d'autorité. |
| **BCE-05** | Dépendance de replay symbolique absente | Métadonnées de rejeu sans documents épinglés | Qualification explicite en `REPLAY_INPUTS_INCOMPLETE` ; refus de qualification de rejeu symbolique déterministe. |
| **BCE-06** | Snapshot de sortie neuronale présent | Bundle contenant un snapshot textuel de Qwen | Qualifié strictement `TRACE_REPLAYABLE` ; refus formel de `BIT_EXACT_REPLAY_VERIFIED` ou de rejeu déterministe présumé. |
| **BCE-07** | Oracle circulaire ou auto-référentiel | Référence d'évaluation pointant vers `bundle_id` ou la réponse Brody | Rejet strict sous `CIRCULAR_SELF_REFERENTIAL` / `TAUTOLOGICAL_ORACLE_REJECTED`. |
| **BCE-08** | Évaluation contre oracle indépendant | Confrontation à un document synthétique épinglé (`SOURCE_PINS`) | Évaluation `PASS` ou `FAIL` bornée au contrat de test, sans prétention à une vérité universelle (`world_fact=False`). |
| **BCE-09** | Détection de secrets et rejet de champs extra | Payload contenant un token d'API / secret, ou un champ non déclaré | Rejet fail-closed (`PRIVACY_VIOLATION_REJECTED` ou `EXTRA_FIELDS_REJECTED`) ; aucun fichier écrit sur le disque. |
| **BCE-10** | Traçabilité fournisseur externe | Appel modèle distant constaté (`model_calls > 0`) | `external_provider_called=True`, attribution `STACK_PLUS_EXTERNAL_MODEL`, causalité non inférée. |
| **BCE-11** | Invariance des effets B11 et zéro écriture | Lecture B11 (`B11CognitiveEvidenceReader`) sur store temporaire | `B11_EFFECTS` préservé ; absence matérielle confirmée d'écriture (répertoire de store strictement invariant). |
| **BCE-12** | Invariance UNKNOWN_COMPETENCE | Projection du profil de compétence B11 issu du bundle | Maintien absolu de `CompetenceRegime.UNKNOWN_COMPETENCE`, `confidence_score=0.0`, `b12_selection=False`. |
