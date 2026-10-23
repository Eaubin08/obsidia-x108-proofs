# M42 B11 Compétence & Calibration — Spécification Bridge Cognitif & Replay Symbolique V1

## 1. Statut, rôle et frontières doctrinales

- **Chapitre :** M42 — B11 Compétence et Calibration (Étage 5 : Preuves cognitives rejouables et pont d'assemblage).
- **Couche :** Cognition / Gouvernance consultative (`app/cognition/b11/`).
- **Composant cible futur :** `app.cognition.b11.brody_evidence_bridge` (`build_evidence_bundle_payload_from_receipt`, `reexecute_symbolic_bundle`, `SymbolicReexecutionReportV1`).
- **Rôle du module :**
  1. Fonction pure d'assemblage canonique transformant un reçu d'exécution cognitive réel (`run_real_cognitive_join` / `two_encounter_support`) et son observation B11 en payload structuré pour `publish_brody_evidence_bundle`.
  2. Moteur de réexécution symbolique déterministe hors-ligne vérifiant bit-à-bit les dépendances logiques B7/M41/B8 sans ré-exécution du modèle de langage distant (Qwen).
- **Invariance absolue de gouvernance :** Le bridge est une fonction pure : zéro écriture disque, zéro transport réseau, zéro décision souveraine (`decision_authority="KX108_ONLY"`), maintien impératif sous `CompetenceRegime.UNKNOWN_COMPETENCE`.

---

## 2. Contrat d'Assemblage : `build_evidence_bundle_payload_from_receipt`

### 2.1 Signature formelle
```python
def build_evidence_bundle_payload_from_receipt(
    cognitive_receipt: Mapping[str, Any],
    observation: BrodyCognitiveObservationV1 | None = None,
    evaluation_reference: Mapping[str, Any] | None = None,
    replay_mode: str = "DETERMINISTIC_OFFLINE",
    hypothesis_set: Any | None = None,
    knowledge_claims: Sequence[Any] = (),
) -> dict[str, Any]:
    ...
```

### 2.2 Règles de transformation et préservation
1. **Extraction depuis le reçu réel :**
   - `execution_id` : extrait de `cognitive_receipt["signal_id"]`.
   - `mechanism_ref` : `"brody:cognitive_resolution"`.
   - `mechanism_version` : extrait de `cognitive_receipt.get("version", "REAL_COGNITIVE_JOIN_C1_V1")`.
   - `execution_timestamp_utc` : extrait de `cognitive_receipt.get("created_at")` ou horodatage UTC canonique.
   - `input_context_digest` : SHA-256 du message d'entrée original.
   - `external_provider_trace` : extrait fidèlement des composants (ex. `W4B_LOCAL_MODEL_EVIDENCE`, `model_evidence_snapshot`).
2. **Rattachement symbolique et documentaire réel :**
   - `documentary_refs` : tuples des `claim_id` extraits de `knowledge_claims` (instances réelles `b8.KnowledgeClaim`).
   - `symbolic_context_refs` : tuples des identifiants d'état B7 (`sens:frame`) et M41 (`set_id` issu de `WorldHypothesisSet`).
   - `observable_response_text` et `observable_response_digest` : issus de l'observation ou du texte synthétisé.
3. **Dépendances de replay :**
   - `pinned_document_digests` : condensats SHA-256 des documents B8 sous-jacents aux claims.
   - `replay_mode` : `"DETERMINISTIC_OFFLINE"` ou `"TRACE_REPLAYABLE_ONLY"`.
4. **Garde-fous de schéma et vérité :**
   - Génère exclusivement les 19 champs autorisés par le schéma fermé V1.
   - Initialise `seal_status = "EPHEMERAL_IN_MEMORY"` (le statut `STORE_SEALED` est réservé à la publication matérielle effective).
   - Initialise `provenance_status = "ORIGIN_UNESTABLISHED"` (le reçu local ne constitue pas une attestation cryptographique externe).
   - Calcule l'empreinte `integrity_digest` et dérive `bundle_id = f"bceb-{integrity_digest[:32]}"`.

---

## 3. Contrat de Replay Symbolique : `reexecute_symbolic_bundle`

### 3.1 Signature formelle
```python
def reexecute_symbolic_bundle(
    bundle_id: str,
    store_dir: Path | str | None = None,
    isolated_source_pins: Mapping[str, Any] | None = None,
) -> SymbolicReexecutionReportV1:
    ...
```

### 3.2 Protocole de réexécution déterministe
1. **Relecture et vérification préliminaire :**
   - Invoque `CognitiveEvidenceVerifier.load_and_verify(bundle_id, store_dir)`.
   - Si l'intégrité est compromise ou l'identifiant malformé, arrêt immédiat en `FAIL_CLOSED`.
2. **Validation des dépendances :**
   - Vérifie la présence des condensats documentaires dans `isolated_source_pins` (par défaut `SOURCE_PINS`).
   - Si un document épinglé manque : statut `DEPENDENCY_MISSING`.
3. **Réexécution symbolique effective :**
   - **Couche B8 :** Pour chaque claim documenté, ré-évalue les transitions formelles via `b8.evaluate_transition` sur un `SlotSnapshot` vierge jusqu'à `ClaimState.VERIFIED`.
   - **Couche M41 :** Reconstitue les hypothèses `WorldStateHypothesis` du set et ré-évalue les invariants de sélection/coexistence.
   - **Couche B7 :** Re-valide la résolution de coréférence lexicale sans accès réseau.
4. **Comparaison et confrontation :**
   - Confronte les sorties symboliques recalculées aux condensats archivés dans le bundle.
   - En cas d'identité totale : `SYMBOLIC_REEXECUTION_MATCHED`.
   - En cas de divergence d'un seul attribut : `SYMBOLIC_REEXECUTION_DIVERGED` explicite.
5. **Herméticité neuronale :**
   - Aucune invocation de modèle distant (Qwen). La réexécution symbolique teste exclusivement la chaîne logique déterministe.
   - Refus formel de promouvoir le bundle en `BIT_EXACT_REPLAY_VERIFIED` pour la partie générative.

---

## 4. Frontières Épistémiques et Séparation des Preuves

| Statut Épistémique | Définition & Règle d'Attribution | Interdiction Doctrinale |
|---|---|---|
| **`BUNDLE_INTEGRITY_VERIFIED`** | Les octets du bundle sur disque correspondent bit-à-bit à l'empreinte SHA-256 canonique. | Ne prouve pas l'authenticité historique de l'appelant. |
| **`RECEIPT_ORIGIN_UNESTABLISHED`**| Le reçu provient d'une boucle locale sans signature asymétrique externe (RFC3161/HSM). | Interdiction formelle de promouvoir en origine certifiée. |
| **`TRACE_REPLAY_VERIFIED`** | La trace d'exécution enregistrée est structurellement cohérente et rejouable passivement. | Ne constitue pas une réexécution des calculs. |
| **`SYMBOLIC_REEXECUTION_PERFORMED`** | Les modules déterministes B7/M41/B8 ont été effectivement ré-invoqués en mémoire isolée. | Ne peut pas être accordé par simple lecture de snapshots. |
| **`SYMBOLIC_REEXECUTION_MATCHED`** | Les états symboliques recalculés sont strictement identiques aux références archivées. | Ne prouve aucune compétence du modèle de langage. |
| **`NEURAL_REEXECUTION_NOT_PERFORMED`** | Le modèle neuronal externe n'a pas été réexécuté (mode hors-ligne hermétique). | Interdiction de présumer de l'invariance stochastique de Qwen. |
| **`INDEPENDENT_ORACLE_BOUNDED`** | La réponse est confrontée à un oracle synthétique indépendant (`SOURCE_PINS`). | Prouve la conformité au test, jamais une vérité physique universelle. |

---

## 5. Matrice des Scénarios RED (E2-01 à E2-08)

| Code | Scénario | Conditions & Entrée | Comportement attendu |
|---|---|---|---|
| **E2-01** | Assemblage conforme depuis reçu réel | Reçu authentique issu de `run_real_cognitive_join` | Payload valide sous schéma fermé V1, 19 champs, `seal_status="EPHEMERAL_IN_MEMORY"`, `ORIGIN_UNESTABLISHED`. |
| **E2-02** | Extraction des claims B8 réels | Claims réels issus de `two_encounter_support.acquire` | `documentary_refs` et `pinned_document_digests` fidèlement rattachés sans perte d'attributs. |
| **E2-03** | Sérialisation des hypothèses M41 | `WorldHypothesisSet` réel avec hypothèses coexistant | Préservation intégrale de l'ambiguïté sans sélection canonique arbitraire. |
| **E2-04** | Publication et TRACE_REPLAY complet | Payload issu de l'assemblage réel publié via `brody_evidence_store` | Publication `STORED`, intégrité vérifiée, relecture passive conforme. |
| **E2-05** | Réexécution symbolique déterministe effective | Invocation de `reexecute_symbolic_bundle` sur bundle valide | Exécution réelle de B8/M41/B7, résultat `SYMBOLIC_REEXECUTION_MATCHED`. |
| **E2-06** | Dépendance altérée ou divergence | Falsification d'une assertion dans le document épinglé sous-jacent | Détection immédiate sous `SYMBOLIC_REEXECUTION_DIVERGED` ou `REPLAY_DEPENDENCY_MISSING`. |
| **E2-07** | Herméticité neuronale et refus de BIT_EXACT | Bundle portant un snapshot de sortie neuronale Qwen | Réexécution symbolique réussie, réexécution neuronale ignorée, `bit_exact_replay_verified=False`. |
| **E2-08** | Invariance B11 et pureté du bridge | Exécution de l'assemblage et du rejeu sous surveillance FS | `memory_write=False`, zéro fichier résiduel, maintien sous `UNKNOWN_COMPETENCE`. |
