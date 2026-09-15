# Comment circule la donnée dans Obsidia

> Guide rédigé le 2026-09-15 à partir de `main` (5d27d003). Chaque étape renvoie au fichier qui l'exécute réellement. Les principes sont cités depuis le [README](../README.md) ; le reste est lu dans le code.

Obsidia fait circuler l'information sur **trois trajets** qui se croisent :

| Trajet | Question à laquelle il répond | Sens |
|---|---|---|
| [1. La cognition](#1-le-trajet-de-la-cognition--ce-qui-se-passe-quand-on-parle-à-brody) | Comment une demande devient une réponse ? | aller simple, en lecture seule |
| [2. Le savoir](#2-le-trajet-du-savoir--comment-une-information-devient-mémoire) | Comment une information devient mémoire fiable ? | boucle lente, validée par un humain |
| [3. L'action](#3-le-trajet-de-laction--comment-une-proposition-touche-le-réel) | Comment une proposition peut toucher le réel ? | passe obligatoirement par X-108 |

Puis : [4. Pourquoi ça fonctionne déjà sans entraînement](#4-pourquoi-ça-fonctionne-déjà-sans-entraînement).

```text
                ┌──────────── 2. SAVOIR (boucle lente, validée) ─────────────┐
                │                                                             ▼
 demande ─▶ 1. COGNITION ─▶ réponse          capture ─▶ tri ─▶ validation humaine ─▶ Graphiti
                ▲    │                                                             │
                │    └──▶ 3. ACTION ─▶ frontière ─▶ X-108 : ACT | HOLD | BLOCK       │
                └────────────── relecture de la mémoire validée ◀──────────────────┘
```

---

## 1. Le trajet de la cognition — ce qui se passe quand on parle à Brody

Point d'entrée : la route [`/brody/chat`](../apps/obsidia_api/routes/brody.py). Les étapes ci-dessous suivent l'ordre du code. **Tout ce trajet est en lecture seule** : aucune écriture en mémoire, aucun ACT, autorité `KX108_ONLY`.

| # | Étape | Ce qui se passe | Fichier |
|---|---|---|---|
| 0 | **Filtre de secrets** | Si le message contient une clé privée ou un secret, la réponse est bloquée et nettoyée avant tout traitement. | [`routes/brody.py`](../apps/obsidia_api/routes/brody.py) (vers la ligne 218) |
| 1 | **Fastpath** | Les demandes connues (règles CIC, GPS irréversible, tentatives de contournement du type « bypass X108 ») sont reconnues par motifs et reçoivent tout de suite une réponse structurée. **Pas de LLM, pas d'accès disque, pas d'ACT.** | [`brody_v3_fastpath_response.py`](../apps/obsidia_api/brody_v3_fastpath_response.py) |
| 2 | **Compréhension** | Normalisation du texte, garde d'intention en lecture seule, requête sémantique, détection de l'intention (demande d'action, revendication d'autorité…). | [`routes/brody.py`](../apps/obsidia_api/routes/brody.py) (vers les lignes 387 à 420) |
| 3 | **Rappel du contexte** | Brody assemble ce qu'il sait déjà : la **mémoire de session** (échanges précédents), la **mémoire projet** (index Graphiti et ledger des candidats), la **mémoire candidate**, le contexte temporel, les modules cognitifs et les arbres. | [`brody_session_memory_adapter.py`](../apps/obsidia_api/brody_session_memory_adapter.py), [`brody_project_memory_adapter.py`](../apps/obsidia_api/brody_project_memory_adapter.py), [`brody_candidate_memory_adapter.py`](../apps/obsidia_api/brody_candidate_memory_adapter.py) |
| 4 | **Sources** | Les *source packs* (corpus du projet) sont interrogés, hydratés, **passés par la porte X-108**, puis résumés en contexte. Le routeur de capacités choisit les familles de sources utiles. | [`brody_source_context_bridge.py`](../runtime_wiring/source_runtime/brody_source_context_bridge.py), [`capability_path_router.py`](../runtime_wiring/source_runtime/capability_path_router.py) |
| 5 | **Activations en lecture seule** | Mémoire Graphiti/Neo4j en lecture (P52), bus d'action du monde en dry-run (P53), passerelle d'action HOLD/BLOCK en sandbox (P54). | [`routes/brody.py`](../apps/obsidia_api/routes/brody.py) (blocs P51 à P54) |
| 6 | **Mesures** | Sigma initial → signal **anti-mismatch** (écart entre ce qui est dit et ce qui est vrai) → Sigma final → **Thermo** → valeur Gencoin fictive → signal Tree → **garde de promotion mémoire** → vue opérateur. Tout est calculé et affiché, rien ne décide (`SHADOW_READONLY`). | [`brody_anti_mismatch_signal.py`](../apps/obsidia_api/brody_anti_mismatch_signal.py), [`brody_memory_promotion_guard.py`](../apps/obsidia_api/brody_memory_promotion_guard.py) |
| 7 | **Réponse « True Voice »** | La réponse finale est **construite à partir des structures existantes** : mémoire projet, session et source packs. Le code impose : *« Always use true_voice for final answer — never raw response_md »*. | [`brody_true_voice_adapter.py`](../apps/obsidia_api/brody_true_voice_adapter.py) |
| 8 | **Sortie** | Nouveau nettoyage des secrets sur toute la réponse, puis renvoi au Terminal ou au Workbench. | [`routes/brody.py`](../apps/obsidia_api/routes/brody.py) (vers la ligne 1101) |

**À retenir :** Brody **relie et formule**, il ne décide pas et n'écrit pas. Les mesures (Sigma, anti-mismatch, Thermo) éclairent la réponse sans jamais avoir d'autorité. Voir les couches [10 · Cognition](couches/10_COGNITIVE_SYSTEM.md), [11 · Sigma](couches/11_HIGH_PERIPHERY_MACHINERY.md) et [14 · Mémoire](couches/14_CONTEXT_MEMORY_EDUCATION.md).

---

## 2. Le trajet du savoir — comment une information devient mémoire

Principe (README § 10.4, « Mémoire gouvernée ») :

```text
BRUT → candidat → triage → provenance → fraîcheur → validation → promotion canonique
```

> *« La mémoire n'est pas la vérité. Une trace doit franchir des contrôles avant de devenir canonique. »* — README § 9

Dans le code, chaque étape est un module séparé de [`periphery/brody_memory_readonly/`](../periphery/brody_memory_readonly/) :

| # | Étape | Ce qui se passe | Module |
|---|---|---|---|
| 1 | **Capture** | Chaque échange est journalisé ; ce qui concerne le projet est mis en attente. | `session_memory_ledger_readonly`, `project_intake_capture_buffer_readonly`, `session_presave_buffer_readonly` |
| 2 | **Tri automatique** | Les éléments bruts sont classés et deviennent des **candidats**, jamais des vérités. | `auto_triage_memory_intake_readonly`, [`memory_candidate_ledger.py`](../periphery/memory/memory_candidate_ledger.py) |
| 3 | **Validation humaine** | En fin de session, **l'humain valide** ce qui mérite d'être gardé, puis le tri est refait après sa revue. | `session_close_human_validation_gate_readonly`, `post_human_review_memory_triage_readonly` |
| 4 | **Préparation et essai à blanc** | Les candidats validés sont préparés pour Graphiti, importés **à blanc** (dry-run), puis passent une **porte de revue**. | `graphiti_candidate_prep_from_post_human_triage_readonly`, `graphiti_candidate_import_dry_run_readonly`, `graphiti_candidate_review_gate_readonly` |
| 5 | **Écriture gardée, manuelle uniquement** | L'écriture dans Graphiti ne se fait qu'**à la main**, à partir d'une décision de revue. | `graphiti_guarded_manual_apply_from_review_decision_readonly_memory_only`, `graphiti_import_apply_guarded_manual_only` |
| 6 | **Vérification** | Après l'écriture, on vérifie ce qui a été appliqué et on rejoue les requêtes pour détecter une régression. | `post_graphiti_apply_verify_readonly`, `memory_replay_query_regression_readonly` |
| 7 | **Relecture** | La mémoire validée est lue sous forme d'index, puis servie en **paquets de contexte** au moteur de réponse et à Brody (étape 3 du trajet 1). | [`_graphiti_readonly_indexes/`](../_graphiti_readonly_indexes/), `context_packet_query_readonly`, `context_packet_consumer_readonly`, `local_response_engine_readonly` |

**La boucle :** ce qui est validé aujourd'hui est relu par Brody demain. Le système **apprend en accumulant de la mémoire validée**, pas en modifiant un modèle.

**La protection :** pendant une conversation, la garde de promotion mémoire impose `memory_write=false`, `graphiti_write=false` et `canon_promotion=false` ([`brody_memory_promotion_guard.py`](../apps/obsidia_api/brody_memory_promotion_guard.py)). Une conversation ne peut donc pas s'auto-promouvoir en vérité.

**Les autres sources de savoir**, lues au même titre que la mémoire :
- les **source packs** ([`_source_packs/`](../_source_packs/)) et le registre des sources ([`runtime_wiring/source_registry/`](../runtime_wiring/source_registry/)) ;
- les **spécifications** ([`specs/`](../specs/)) et les **contrats** ([`runtime_contracts/`](../runtime_contracts/)) ;
- les **preuves** : Lean, TLA+, receipts ; voir la [couche 24](couches/24_FORMAL_METHODS.md) et la [couche 25](couches/25_OS3_PROOF_REPLAY_ATTESTATION.md).

---

## 3. Le trajet de l'action — comment une proposition touche le réel

Principe (README § 10.3, « Autorité isolée ») :

```text
possible → admissible → autorisé → réel
```

1. Un organe (Brody, Obsidure, un domaine) produit une **proposition**. C'est le *possible*.
2. Les preuves et les mesures disent si elle tient debout. C'est l'*admissible* : tests, Lean, replay, Sigma.
3. La **frontière d'ingress** vérifie qu'un envelope valide atteint le noyau ([`periphery/x108_ingress/`](../periphery/x108_ingress/), [couche 17](couches/17_BOUNDARIES_ACTION_INGRESS.md)).
4. **X-108 juge avant l'exécution** : `ACT`, `HOLD` ou `BLOCK`. C'est l'*autorisé* ([`docs/KERNEL_OVERVIEW.md`](KERNEL_OVERVIEW.md), [couche 16](couches/16_X108_AUTHORITY_KERNEL.md)).
5. Seul un `ACT` passe au *réel*, par une frontière bornée, et l'action est scellée et rejouable ([couche 25](couches/25_OS3_PROOF_REPLAY_ATTESTATION.md)).

Dans la route Brody, cette chaîne ne s'exerce aujourd'hui qu'en **sandbox** : la passerelle HOLD/BLOCK (P54) et le bus d'action en dry-run (P53). Brody n'émet jamais d'ACT.

---

## 4. Pourquoi ça fonctionne déjà sans entraînement

Obsidia n'est pas un modèle qu'on entraîne. C'est une **architecture qui organise du savoir déjà écrit et des règles déjà prouvées**. Cinq raisons, toutes vérifiables dans le dépôt :

### 4.1 Le savoir est dans des fichiers, pas dans des poids

Un LLM « sait » ce qu'il a absorbé pendant son entraînement. Obsidia sait ce qui est **écrit et validé** : ledgers de session (JSONL), index Graphiti, source packs, registres, spécifications et preuves. Pour qu'il sache une chose nouvelle, **il suffit de l'ajouter et de la valider** (trajet 2). Il n'y a rien à réentraîner.

> *« Les apprentissages ne devront pas appartenir uniquement au modèle qui les a produits. Ils devront être conservés dans l'architecture Obsidia. […] Le modèle peut évoluer ou être remplacé. La continuité cognitive reste dans Obsidia. »* — README § 6.12

### 4.2 La structure passe avant l'inférence

Avant toute « intelligence », la demande est découpée :

```text
forme du problème → intention → domaine → risque → capacité → preuve attendue → inférence éventuelle
```

L'inférence n'arrive qu'**à la fin, et seulement si nécessaire** (README § 10.1). Beaucoup de demandes sont résolues par la structure seule.

### 4.3 Obsidia se demande d'abord s'il faut appeler un modèle

> *« Obsidia ajoute une question précédente : un modèle doit-il réellement être appelé ? »* — README § 8.4

C'est visible dans le code :
- le **fastpath** répond aux demandes connues **sans LLM** (étape 1 du trajet 1) ;
- dans l'orchestrateur, le fournisseur de modèle vaut **`NOT_REQUESTED`** par défaut, et **`DISABLED_BY_POLICY`** même s'il est demandé ([`brody_full_runtime_orchestrator.py`](../apps/obsidia_api/brody_full_runtime_orchestrator.py), vers la ligne 265) ;
- la réponse finale vient de **True Voice**, construite à partir des structures, et non du texte brut d'un modèle (étape 7).

Le benchmark [OIE V0.7](audits/OBSIDIA_OIE_OBSIDIA_VS_GEMINI_POWER_METRICS_V0_7.md) mesure cette « puissance d'évitement » : 4 appels de modèle évités sur 7 familles de tâches. *Attention : c'est un dry-run sur des valeurs figées, pas encore un run réel.*

### 4.4 La décision est déterministe et prouvée

Le noyau X-108 **n'utilise aucune IA générative** (voir le [GLOSSAIRE](GLOSSAIRE.md)). Il applique des invariants vérifiés en Lean 4 et en TLA+. Une règle prouvée n'a pas besoin d'apprendre : elle doit rester **la même**, et c'est justement ce qui la rend fiable.

### 4.5 Grandir, c'est ajouter des organes, pas réentraîner

> *« L'extension d'Obsidia ne consiste pas à entraîner un modèle différent pour chaque entreprise. Elle consiste à construire les organes, les contrats, les preuves et les traductions. »* — README § 18.14

Un nouveau domaine s'ajoute avec ses objets, ses règles, ses risques et ses preuves (README § 18.3). Il n'y a pas de nouveau modèle à entraîner.

### Ce que ça ne veut pas dire

- **Un LLM peut être branché**, mais comme un organe parmi d'autres, pour reformuler par exemple, jamais comme le cerveau ni comme l'autorité (README § 8.1). Le code prévoit ce chemin de reformulation, mais la réponse finale reste celle de True Voice.
- **La qualité des réponses dépend de ce qui est écrit et validé.** Le fastpath ne couvre que les demandes qu'il reconnaît. Pour une question libre sur un sujet que la mémoire et les sources ne contiennent pas, Brody n'invente pas : il répond avec ce qu'il a.
- La stack est encore en **reconstruction canonique** : la V0.1 n'est pas publiée (README, « État du projet »).
