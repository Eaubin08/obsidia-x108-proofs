# Comment circule la donnée dans Obsidia

> Guide rédigé le 2026-09-15. Chaque étape renvoie au fichier qui l'exécute. Les principes sont cités depuis le [README](../README.md) ; le reste est lu dans le code.
>
> **Branche de référence.** La mémoire native, MEMZUM, le cœur cognitif de Brody et la couche langage vivent sur la branche [`integration/harness-runtime-binder-v1`](https://github.com/Eaubin08/obsidia-x108-proofs/tree/integration/harness-runtime-binder-v1), qui n'est pas encore fusionnée dans `main`. Les liens marqués **(H)** pointent vers cette branche.

À lire avant : [Comprendre Obsidia](COMPRENDRE_OBSIDIA.md). À lire après : [Entraînement, éducation, naissance](EDUCATION.md) et [Sécurité](SECURITE.md).

Obsidia fait circuler l'information sur **trois trajets** qui se croisent :

| Trajet | Question | Nature |
|---|---|---|
| [1. La cognition](#1-le-trajet-de-la-cognition--comment-brody-répond) | Comment une demande devient une réponse ? | aller simple, en lecture seule |
| [2. Le savoir](#2-le-trajet-du-savoir--comment-une-information-devient-mémoire) | Comment une information devient mémoire fiable ? | boucle lente, validée par un humain |
| [3. L'action](#3-le-trajet-de-laction--comment-une-proposition-touche-le-réel) | Comment une proposition peut toucher le réel ? | passe obligatoirement par X-108 |

Puis : [4. OS Trad, le langage commun](#4-os-trad--le-langage-commun) et [5. Pourquoi ça fonctionne sans entraînement](#5-pourquoi-ça-fonctionne-sans-entraînement).

```text
                 ┌───────────── 2. SAVOIR (boucle lente, validée par l'humain) ─────────────┐
                 │                                                                            ▼
 demande ─▶ 1. COGNITION ─▶ réponse          capture ─▶ tri ─▶ validation humaine ─▶ mémoire native
   │             ▲    │                                                                       │
   │             │    └──▶ 3. ACTION ─▶ frontière ─▶ X-108 : ACT | HOLD | BLOCK                 │
   │             └──────────────── relecture de la mémoire validée ◀─────────────────────────┘
   └─▶ 4. OS TRAD traduit à l'entrée et reprojette à la sortie (humain ↔ IR ↔ lisible par le noyau)
```

---

## 1. Le trajet de la cognition — comment Brody répond

Point d'entrée : la route `/api/brody/chat` ([`routes/brody.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/apps/obsidia_api/routes/brody.py) **(H)**). Brody n'est pas un modèle de langage : c'est un **moteur de contexte**. À chaque appel, il **assemble** une réponse à partir de signaux calculés et de sources locales. **Tout le trajet est en lecture seule** : aucune écriture en mémoire, aucun ACT, autorité `KX108_ONLY`.

### 1.1 Vue d'ensemble

```text
message
 │
 ├─0─ filtre de secrets ─────────────────────────────── (bloque si clé privée / secret)
 │
 ├─1─ CŒUR COGNITIF   micro-core (14 signaux) → balance engine (11 balances) → point cloud 21D
 │                    = qu'est-ce que cette demande, quels risques, quelles couches activer, quel budget
 │
 ├─2─ PRÉ-RAISONNEMENT   requête sémantique → projection Reverse OS / IR → calibration C265→C274
 │
 ├─3─ FASTPATH   demande reconnue ? → réponse structurée immédiate (sans LLM)
 │
 ├─4─ JONCTION COGNITIVE   ContextPacketV2 enrichi (Sigma, arbres, agents) — en ombre, sans autorité
 │
 ├─5─ MÉMOIRE   MEMZUM : « faut-il de la mémoire ? » → si oui : mémoire native locale → moteur de réponse local
 │
 ├─6─ SOURCES   source packs → porte X-108 → contexte
 │
 ├─7─ RÉPONSE « TRUE VOICE »   construite à partir des structures (mémoire, session, sources)
 │
 ├─8─ MESURES   Sigma → anti-mismatch → Sigma final → Thermo → Gencoin (ombre) → arbres → garde mémoire
 │
 └─9─ nettoyage final des secrets → Terminal / Workbench
```

### 1.2 Les étapes en détail

| # | Étape | Ce qui se passe | Fichier |
|---|---|---|---|
| 0 | **Filtre de secrets** | Si le message contient une clé privée ou un secret, le traitement s'arrête et la réponse est nettoyée. | [`brody_secret_scrubber.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/apps/obsidia_api/brody_secret_scrubber.py) **(H)** |
| 1a | **Micro-core** | Calcule **14 signaux permanents** en moins de 20 ms : autorité, CIC, invariant, réversibilité, réflexe, instinct, bio-animal (cohérence), mémoire non souveraine, pertinence mémoire, projection non-prédiction, symbolique, fractal, OS reverse, réciprocité. Il **détecte aussi les tentatives de contournement** (« bypass », « ignore X108 », « écris en mémoire canonique »…) et les **actions irréversibles** (« supprime définitivement », « reset --hard », « drop table »…). | [`brody_cognitive_micro_core.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/apps/obsidia_api/brody_cognitive_micro_core.py) **(H)** |
| 1b | **Balance engine** | Pèse **11 tensions** : réversibilité, risque, exponentielle, cohérence, coût énergétique, terrain bio, mémoire, causalité, signal faible, symbolique, projection. Chaque tension a une priorité : P0 = absolu/HOLD, P1 = danger, P2 = cohérence, P3 = énergie, P4 = mémoire, P5 = signal faible, P6 = symbolique/projection. Un seuil dépassé amplifie le signal. **Il pèse, il ne décide pas.** | [`brody_balance_engine.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/apps/obsidia_api/brody_balance_engine.py) **(H)** |
| 1c | **Point cloud 21D** | Transforme la demande en **vecteur à 21 axes** (domaine, autorité, réversibilité, pression, preuve, temporalité, fiabilité de la source, ressource, trajectoire, comportement, projection, mémoire, symbolique, fractal, OS reverse…). Il choisit **au plus 6 couches actives** parmi 18 (bank, trading, GPS, mémoire, preuve, langage universel, réflexe…) et un **budget** de 8 192 octets. Les couches *autorité* et *CIC* sont **toujours actives**. | [`brody_point_cloud_21d_selector.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/apps/obsidia_api/brody_point_cloud_21d_selector.py) **(H)** |
| 2 | **Pré-raisonnement** | Requête sémantique, puis projection par le **Reverse OS** existant (IR, traduction), puis calibration lexicale et **calibration avant raisonnement** en 4 temps : C265 (sens → intégration symbolique), C266 (alignement symbolique), C273 (détection de divergence), C274 (calibration). Voir [§ 4 OS Trad](#4-os-trad--le-langage-commun). | [`brody_pre_reasoning_adapter.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/apps/obsidia_api/brody_pre_reasoning_adapter.py) **(H)** |
| 3 | **Fastpath** | Si la demande est reconnue (règles CIC, GPS irréversible, tentative adversariale…), elle reçoit une **réponse structurée immédiate**, **sans LLM, sans accès disque, sans ACT**. | [`brody_v3_fastpath_response.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/apps/obsidia_api/brody_v3_fastpath_response.py) **(H)** |
| 4 | **Jonction cognitive** | Construit un **ContextPacketV2** : éléments de contexte, références et empreintes des sources, arbres dominants, inconnues, contradictions, drapeaux de risque. Il est enrichi par le signal Sigma, le signal des arbres et le résultat des agents. Le paquet **refuse les mots d'autorité** (ALLOW, HOLD, BLOCK, ACT, DECIDE, VERDICT, EXECUTE…). Il est superposé en ombre (`SHADOW_READONLY_SUPERPOSED`). | [`brody_real_cognitive_join.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/apps/obsidia_api/brody_real_cognitive_join.py), [`context_packet_builder_v2.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/periphery/context/context_packet_builder_v2.py) **(H)** |
| 5a | **MEMZUM : faut-il de la mémoire ?** | MEMZUM **ne cherche rien**. Il consolide des signaux déjà calculés (`point_cloud.memory_packet_required`, pertinence mémoire du micro-core, tension *mémoire* de la balance, axe 13 du point cloud, domaine, intention, état adversarial) en **une seule réponse : oui ou non**. Il ignore quel stockage existe (« provider-neutral »). | [`brody_memzum_activation_adapter.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/apps/obsidia_api/brody_memzum_activation_adapter.py) **(H)** |
| 5b | **Mémoire native** | Si MEMZUM dit oui : recherche **locale, sans réseau, sans service externe** dans l'index natif Obsidia (3 267 enregistrements), puis **moteur de réponse local**, puis instantané de réponse. | [`brody_obsidia_native_memory.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/apps/obsidia_api/brody_obsidia_native_memory.py), [`brody_native_memory_response_adapter.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/apps/obsidia_api/brody_native_memory_response_adapter.py) **(H)** |
| 6 | **Sources** | Les *source packs* (corpus du projet) sont sélectionnés par le routeur de capacités, hydratés, **passés par la porte X-108**, puis résumés. | [`brody_source_context_bridge.py`](../runtime_wiring/source_runtime/brody_source_context_bridge.py), [`capability_path_router.py`](../runtime_wiring/source_runtime/capability_path_router.py) |
| 7 | **Réponse « True Voice »** | La réponse finale est **construite à partir des structures existantes** : mémoire projet, session, sources, avec une priorité au moteur de réponse local. Le code impose : *« Always use true_voice for final answer — never raw response_md »*. | [`brody_true_voice_adapter.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/apps/obsidia_api/brody_true_voice_adapter.py), [`brody_real_response_pipeline.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/apps/obsidia_api/brody_real_response_pipeline.py) **(H)** |
| 8 | **Mesures en ombre** | Sigma initial → **anti-mismatch** (écart entre ce qui est dit et ce qui est vrai) → Sigma final → **Thermo** → valeur Gencoin fictive → signal des arbres → **garde de promotion mémoire** → vue opérateur. Tout est calculé et affiché, **rien ne décide** (`SHADOW_READONLY`). | [`brody_anti_mismatch_signal.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/apps/obsidia_api/brody_anti_mismatch_signal.py), [`brody_memory_promotion_guard.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/apps/obsidia_api/brody_memory_promotion_guard.py) **(H)** |
| 9 | **Sortie** | Nettoyage profond des secrets sur toute la réponse (texte, paquets, traces), puis envoi au Terminal ou au Workbench. | [`routes/brody.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/apps/obsidia_api/routes/brody.py) **(H)** |

### 1.3 À retenir

- **Brody calcule avant de parler.** Il sait quel type de demande il reçoit, quel risque elle porte, quelles couches mobiliser et combien de place allouer, **avant** de chercher quoi que ce soit.
- **Brody ne décide pas et n'écrit pas.** Les mesures éclairent la réponse, elles n'ont jamais d'autorité.
- **Chaque organe a une seule question.** MEMZUM dit *s'il faut* de la mémoire, la mémoire native dit *ce qu'elle contient*, le moteur local *formule*.

Couches : [10 · Cognition](couches/10_COGNITIVE_SYSTEM.md), [11 · Sigma](couches/11_HIGH_PERIPHERY_MACHINERY.md), [12 · Langage](couches/12_LANGUAGE_OS_TRAD_IR.md), [14 · Mémoire](couches/14_CONTEXT_MEMORY_EDUCATION.md).

---

## 2. Le trajet du savoir — comment une information devient mémoire

Principe (README § 10.4) :

```text
BRUT → candidat → triage → provenance → fraîcheur → validation → promotion canonique
```

> *« La mémoire n'est pas la vérité. Une trace doit franchir des contrôles avant de devenir canonique. »* — README § 9

### 2.1 La mémoire est native Obsidia

La mémoire de Brody est **ta propre stack**, et non plus Graphiti ni Neo4j :

- **Index natif** : [`_obsidia_native_memory/OBSIDIA_NATIVE_MEMORY_INDEX_V1/`](https://github.com/Eaubin08/obsidia-x108-proofs/tree/integration/harness-runtime-binder-v1/_obsidia_native_memory/OBSIDIA_NATIVE_MEMORY_INDEX_V1) **(H)**, un fichier JSONL de **3 267 enregistrements** au schéma `OBSIDIA_NATIVE_MEMORY_RECORD_V1`.
- **Migration** (C2B-M4A1, 2026-09-07) : l'ancien index Graphiti a été converti par [`migrate_legacy_memory_index_to_obsidia_native_v1.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/scripts/memory/migrate_legacy_memory_index_to_obsidia_native_v1.py) **(H)**. Résultat : **parité 3 267 / 3 267**, **0 étiquette graphiti ou neo4j restante**, ancienne source ni modifiée ni supprimée, empreintes SHA-256 source et cible enregistrées, statut `PASS`.
- **Lecture** : locale, sans réseau, sans service externe, sans écriture ni auto-promotion.
- **Activation** : décidée en amont par **MEMZUM**, qui ne connaît aucun fournisseur de stockage. Changer de stockage ne change donc pas la cognition.

### 2.2 Le parcours d'une information

Chaque étape est un module séparé de [`periphery/brody_memory_readonly/`](../periphery/brody_memory_readonly/) :

| # | Étape | Ce qui se passe | Module |
|---|---|---|---|
| 1 | **Capture** | Chaque échange est journalisé ; ce qui concerne le projet est mis en attente. | `session_memory_ledger_readonly`, `project_intake_capture_buffer_readonly`, `session_presave_buffer_readonly` |
| 2 | **Tri automatique** | Les éléments bruts deviennent des **candidats**, jamais des vérités. | `auto_triage_memory_intake_readonly`, [`memory_candidate_ledger.py`](../periphery/memory/memory_candidate_ledger.py) |
| 3 | **Validation humaine** | En fin de session, **l'humain valide** ce qui mérite d'être gardé, puis le tri est refait. | `session_close_human_validation_gate_readonly`, `post_human_review_memory_triage_readonly` |
| 4 | **Préparation et essai à blanc** | Les candidats validés sont préparés, importés **à blanc**, puis passent une **porte de revue**. | `…_candidate_prep_…`, `…_candidate_import_dry_run_readonly`, `…_candidate_review_gate_readonly` |
| 5 | **Écriture gardée, manuelle uniquement** | L'écriture ne se fait qu'**à la main**, à partir d'une décision de revue. | `…_guarded_manual_apply_…`, `…_import_apply_guarded_manual_only` |
| 6 | **Vérification** | On vérifie ce qui a été appliqué et on rejoue les requêtes pour détecter une régression. | `post_…_apply_verify_readonly`, `memory_replay_query_regression_readonly` |
| 7 | **Relecture** | La mémoire validée est servie en **paquets de contexte** au moteur de réponse local, puis à Brody (trajet 1, étape 5). | `context_packet_query_readonly`, `context_packet_consumer_readonly`, `local_response_engine_readonly` |

*Les noms de modules des étapes 4 à 6 contiennent encore le mot « graphiti » : c'est un héritage de l'ancienne cible. La lecture se fait aujourd'hui sur la mémoire native (§ 2.1).*

**La boucle :** ce qui est validé aujourd'hui est relu par Brody demain. **Le système apprend en accumulant de la mémoire validée, pas en modifiant un modèle.**

**La protection :** pendant une conversation, la garde de promotion mémoire impose `memory_write=false`, `canon_promotion=false` et `memory_promotion=false`. Une conversation ne peut pas s'auto-promouvoir en vérité.

**Les autres sources de savoir**, lues au même titre que la mémoire :
- les **source packs** ([`_source_packs/`](../_source_packs/)) et le registre des sources ([`runtime_wiring/source_registry/`](../runtime_wiring/source_registry/)) ;
- le **corpus mathématique** (134 éléments, tous rattachés à Lean) ; voir [Entraînement, éducation, naissance § 7.2](EDUCATION.md) ;
- le **pack éducatif Brody V1** ; voir [Entraînement, éducation, naissance § 8.1](EDUCATION.md) ;
- les **spécifications** ([`specs/`](../specs/)), les **contrats** ([`runtime_contracts/`](../runtime_contracts/)) et les **preuves** ([couche 24](couches/24_FORMAL_METHODS.md), [couche 25](couches/25_OS3_PROOF_REPLAY_ATTESTATION.md)).

---

## 3. Le trajet de l'action — comment une proposition touche le réel

Principe (README § 10.3) :

```text
possible → admissible → autorisé → réel
```

1. Un organe (Brody, Obsidure, un domaine) produit une **proposition**. C'est le *possible*.
2. Les preuves et les mesures disent si elle tient debout. C'est l'*admissible* : tests, Lean, replay, Sigma.
3. La **frontière d'ingress** vérifie qu'un envelope valide atteint le noyau ([`periphery/x108_ingress/`](../periphery/x108_ingress/), [couche 17](couches/17_BOUNDARIES_ACTION_INGRESS.md)).
4. **X-108 juge avant l'exécution** : `ACT`, `HOLD` ou `BLOCK`. C'est l'*autorisé* ([`KERNEL_OVERVIEW.md`](KERNEL_OVERVIEW.md), [couche 16](couches/16_X108_AUTHORITY_KERNEL.md)).
5. Seul un `ACT` passe au *réel*, par une frontière bornée, et l'action est scellée et rejouable ([couche 25](couches/25_OS3_PROOF_REPLAY_ATTESTATION.md)).

Dans la route Brody, cette chaîne ne s'exerce aujourd'hui qu'en **sandbox** : passerelle HOLD/BLOCK (P54) et bus d'action en dry-run (P53). **Brody n'émet jamais d'ACT.**

---

## 4. OS Trad — le langage commun

### 4.1 Ce que c'est

OS Trad (et son sens retour, **Reverse OS**) n'est pas un simple traducteur de langues. C'est une **couche d'interlangage multidirectionnelle** :

```text
Humain ↔ Chinois / glyphe ↔ Géométrie ↔ Math ↔ Code ↔ IR ↔ Lisible par le noyau ↔ Sortie adaptée au public
```

Source : [`interlanguage_transduction_v1.md`](../_source_packs/REVERSE_OS_INTERLANGUAGE_CANON_V1/evidence/interlanguage_transduction_v1.md) (statut `CANON_RUNTIME_BOUNDARY`).

### 4.2 La règle centrale : la vérité n'est dans aucune langue

> La source de vérité n'est jamais le chinois, le français, l'anglais, la géométrie, le totem, le symbole ou la narration.
> **La source de vérité est `IR_L2 + CONTRAT_COGNITIF_L2_5`.**

- Le **chinois / hanzi** sert de **projection compacte** : compresser un concept, accélérer la navigation symbolique, créer des glyphes combinables. Il ne sert **ni à décider, ni à prouver, ni à remplacer l'IR**.
- **Tout glyphe doit pouvoir être reprojeté** dans la langue de l'utilisateur, en math, en IR ou en explication pour un public donné. Sinon, il est refusé.

### 4.3 Le pipeline

Recommandé par l'audit [F72](architecture/F72_OS_TRAD_IR_REVERSE_DEEP_PIPELINE_AUDIT.md) :

```text
entrée → traduction OS Trad → candidat IR → projection Reverse → projection audience → réponse readonly
```

| Étape | Rôle | Où |
|---|---|---|
| **Détection et routage de langue** | 10 langues (fr, en, es, de, it, pt, nl, ar, zh, ja). Les marqueurs d'autorité usurpée (`admin:`, `root:`, `system:`, `kernel:`, `sudo:`, `override:`) sont repérés. | [`periphery/language/language_router.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/periphery/language/language_router.py) **(H)** |
| **Qualification des inconnues** | Les mots inconnus sont conservés, séparés des mots de surface, et résolus seulement s'il existe une route sémantique canonique. | [`unknown_qualifier.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/periphery/language/unknown_qualifier.py) **(H)** |
| **Traduction et candidat IR** | Routes `/api/os-trad/translate`, `/api/ir/candidate`, `/api/os-reverse/project`. | [`routes/os_trad_ir_reverse.py`](../apps/obsidia_api/routes/os_trad_ir_reverse.py) |
| **Projection Reverse OS** | Reprojection de l'IR vers une action lisible, un format et un public (audience). | [`brody_existing_reverse_os_bridge.py`](../apps/obsidia_api/brody_existing_reverse_os_bridge.py), `periphery/reverse_os/` |
| **Calibration cognitive** | C265 → C266 → C273 → C274 avant le raisonnement ; **C275** vérifie que la réponse candidate respecte cette calibration ; **C277** (*final sense halo*) consolide le sens final ; **C278** vérifie que l'action projetée garde le même sens (`action_meaning_validator`). | [`periphery/language/`](https://github.com/Eaubin08/obsidia-x108-proofs/tree/integration/harness-runtime-binder-v1/periphery/language) **(H)** |
| **Adaptateur de build** | `os_trad_propose` produit une **proposition à blanc** (`DRY_RUN_ONLY`) : aucune spec `.os` n'est compilée, les intentions `ACTION` sont refusées. | [`os_adapters/os_trad_adapter.py`](../apps/obsidia_api/os_adapters/os_trad_adapter.py) |

### 4.4 Où OS Trad intervient dans Brody

- À l'**étape 2** (pré-raisonnement), Brody projette le message par le Reverse OS et produit une trace de traduction (`translation_trace`) et un candidat IR (`ir_candidate`).
- Le **composeur de machination** agrège Brody et les preuves OS Trad / IR / Reverse en une seule réponse native ([`brody_machination_composer.py`](../apps/obsidia_api/brody_machination_composer.py)).
- Le **Workbench** affiche le pipeline ([`osTradPipeline.ts`](../apps/obsidia-workbench/src/lib/osTradPipeline.ts)).

Couche : [12 · Langage, OS Trad, IR](couches/12_LANGUAGE_OS_TRAD_IR.md).

---

## 5. Pourquoi ça fonctionne sans entraînement

Obsidia n'est pas un modèle qu'on entraîne. C'est une **architecture qui organise du savoir écrit et validé et des règles prouvées**.

> **Brody ne progresse pas parce qu'on entraîne ses poids. Brody progresse par stabilisation de ses chemins.** Le LLM classique porte le contexte dans une fenêtre ; Brody le porte dans une architecture et **réduit l'espace possible avant de répondre**.

Attention au vocabulaire : l'**entraînement** donne des capacités aux organes ; l'**éducation** et la **naissance** appartiennent à **Oxygen**, l'unique entité éduquée *(vision, pas encore lancée)*. Détails dans [Entraînement, éducation, naissance](EDUCATION.md).

Six raisons, toutes vérifiables :

### 5.1 C'est une règle du projet, pas un accident

Le pack éducatif de Brody l'écrit en toutes lettres (règles D1 et D2 de `BRODY_V1_FORBIDDEN_BELIEFS.md`) :

> **D1** — *« Brody n'est pas un modèle fine-tuné sur des données Obsidia. Son contexte est assemblé à chaque appel depuis des sources locales readonly. »*
> **D2** — *« Chaque appel Brody est stateless sur le plan de l'apprentissage. Le contexte de chaque appel est assemblé depuis le CIC. »*

### 5.2 Le savoir est dans des fichiers, pas dans des poids

Obsidia sait ce qui est **écrit et validé** : mémoire native (3 267 enregistrements), source packs, corpus math, pack éducatif, spécifications, preuves. Pour qu'il sache une chose nouvelle, **on l'ajoute et on la valide** (trajet 2). Il n'y a rien à réentraîner.

> *« Le modèle peut évoluer ou être remplacé. La continuité cognitive reste dans Obsidia. »* — README § 6.12

### 5.3 Le raisonnement est calculé, pas appris

Le micro-core, les 11 balances, le point cloud 21D, MEMZUM et la calibration C265 → C278 sont du **code déterministe** : motifs, seuils, priorités, axes. Ils donnent la même réponse à la même entrée, et on peut les lire, les tester et les corriger. Il n'y a pas de poids opaques à ajuster.

### 5.4 La structure passe avant l'inférence

```text
forme du problème → intention → domaine → risque → capacité → preuve attendue → inférence éventuelle
```

L'inférence n'arrive qu'**à la fin, et seulement si nécessaire** (README § 10.1).

### 5.5 Obsidia se demande d'abord s'il faut appeler un modèle

> *« Un modèle doit-il réellement être appelé ? »* — README § 8.4

- Le **fastpath** répond sans LLM.
- La mémoire et la réponse sont **« provider-neutral »** : le moteur de réponse local est prioritaire.
- Dans l'orchestrateur, le fournisseur de modèle vaut **`NOT_REQUESTED`** par défaut, et **`DISABLED_BY_POLICY`** même s'il est demandé ([`brody_full_runtime_orchestrator.py`](../apps/obsidia_api/brody_full_runtime_orchestrator.py)).
- Le benchmark [OIE V0.7](audits/OBSIDIA_OIE_OBSIDIA_VS_GEMINI_POWER_METRICS_V0_7.md) mesure 4 appels de modèle évités sur 7 familles de tâches. *C'est un dry-run sur des valeurs figées.*

### 5.6 La décision est déterministe et prouvée

Le noyau X-108 **n'utilise aucune IA générative**. Il applique des invariants vérifiés en Lean 4 et en TLA+. Une règle prouvée n'a pas à apprendre : elle doit rester **la même**. Le corpus math qui nourrit les réponses est lui aussi fermé côté Lean (134/134) ; voir [Entraînement, éducation, naissance § 7.2](EDUCATION.md).

### Attribuer chaque résultat

Quand une réponse est bonne, il faut savoir d'où elle vient : `corpus ≠ retrieval ≠ Obsidure ≠ Brody ≠ LLM ≠ calcul ≠ template ≠ preuve`.

### Ce que ça ne veut pas dire

- **Un LLM peut être branché**, mais comme un organe parmi d'autres, jamais comme le cerveau ni comme l'autorité (README § 8.1).
- **État réel au 14 septembre 2026** : entraînement durable de Brody = 0, fine-tuning = 0, apprentissage persistant autonome non démontré. Le progrès vient de la machinerie, des routes, du corpus, des règles et des contextes réinjectés (voir le § 9 d'[Entraînement, éducation, naissance](EDUCATION.md)).
- **La qualité dépend de ce qui est écrit et validé.** Pour une question sur un sujet que ni la mémoire, ni les sources, ni le corpus ne contiennent, Brody n'invente pas : il répond avec ce qu'il a et signale les inconnues.
- La stack est en **reconstruction canonique** ; la V0.1 n'est pas publiée (README, « État du projet »).
