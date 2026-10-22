# Oxygen — recherche R4 : réconciliation des sources V0.1 (correctif de V0)

**Date :** 2026-10-22 · **Auteur :** Claude (contaminé par les examens de développement ; non relus ici) · **Statut :** correctif documentaire, **non canonique, non FREEZE**. Il corrige `OXYGEN_R4_RESEARCH_V0.md` (sha256 `2e12992a…`) sans l'effacer : V0 reste en l'état, et ce document fait foi là où il le contredit.
**Worktree :** `dfef4f98`, propre, lu sans modification. Aucun R4, aucun RED V0.4, aucune évaluation.

## 0. Erreurs de V0 corrigées

| # | Affirmation de V0 | Correction | Cause |
|---|---|---|---|
| E1 | « OS Trad est introuvable dans le code » | **faux** : routes, adaptateur, tests, code vendor et appels sur le chemin Brody existent (§1) | ma recherche `git grep "OS.?Trad"` était **sensible à la casse** et limitée à `*.py` / `*.md` ; elle a manqué `os_trad` |
| E2 | « AVDR = 2 lignes » | **incomplet** : un mappeur de phases testé, une route API, deux fichiers Lean qui compilent, un canon, des schémas (§2) | j'ai lu le seul `periphery/avdr.py` |
| E3 | « Continuum = ébauche de 10 lignes » | **incomplet** : le registre le déclare couvert par deux snapshots réellement appelés par la route Brody ; la couverture est **partielle** (§3) | même cause |
| E4 | « NB 1,51 contre k-NN 0,53 » | **comparaison invalide** : 1,51 était l'écart du score **total**, 0,53 la contribution **totale** du k-NN. Mesure correcte au §5 : écart NB 1,42 contre écart k-NN 0,11. | méthode |
| E5 | « traits presque tous bruités (sacs de mots, n-grammes de caractères) » | les **n-grammes de caractères** dominent (médiane 11 sur ~26 traits) ; les sacs de mots ne valent que 3 | lecture non mesurée |

**Effet de bord à signaler :** en vérifiant AVDR, j'ai lancé `lean` hors du répertoire `proofs/lean`. elan a alors tenté de télécharger une chaîne v4.35, arrêtée au bout du délai. Il reste des fichiers partiels `~\.elan\toolchains\leanprover--lean4---v4.35.lock` et `…v4.35.tmp`. Aucun dépôt n'a été touché. Le nettoyage relève de votre décision.

## 1. OS Trad

| Niveau | Constat | Preuve |
|---|---|---|
| **Source historique** | prototype vendor « obsidia_os0 / os1 » : IR, traduction, déterminisme, bac à sable. `translate.py` traduit un **sous-ensemble minuscule de pseudo-Python** vers l'IR et encapsule le texte libre comme `EVENT` | `proofs/V18_3_1/engine_buildable_0_9_3_1/modules/os_trad/vendor/obsidia_os0/*` |
| **Pack source** | `OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_P0P1_FIXED.zip` recommandé comme 8e famille source (P31), statut `OS_TRAD_REVERSE_OS_CANDIDATE_NOT_YET_ACTIVE` à cette date | `docs/source_packs/OS_TRAD_REVERSE_OS_SOURCE_CANDIDATE.md` ; P32, P33D (`P33D_OS_TRAD_EVIDENCE_RECONCILED`) |
| **Spec / docs** | workbench OS Trad → IR, projection reverse, alphabet symbolique ; audit F72 du pipeline ; contrats de route 9B1 | `docs/translation/*`, `docs/architecture/F72_*`, `docs/runtime/BRODY_PHASE9B*` |
| **Code** | `apps/obsidia_api/routes/os_trad_ir_reverse.py` (412 lignes), trois routes : `/api/os-trad/translate`, `/api/ir/candidate`, `/api/os-reverse/project` ; `os_adapters/os_trad_adapter.py` (P65, **DRY_RUN_ONLY**, n'appelle jamais `proof.runner.build`), enregistré dans `bus/registry.py` | lecture du code |
| **Tests** | une vingtaine de fichiers, dont `tests/api/test_os_trad_ir_reverse_routes.py`, `test_f72_os_trad_ir_reverse_pipeline_audit.py`, `test_os_trad_reverse_preview_p32.py` | `git grep` (non relancés ici) |
| **Runtime** | les routes sont **montées** (`main.py:137,158`). Sur le chemin Brody, `brody_real_response_pipeline.py:407` importe et **appelle** `_risk_flags` et `_intent` d'OS Trad sur chaque message ; `brody_code_intent_adapter.py` et `brody_machination_composer.py` les réutilisent aussi | lecture **statique** ; aucune trace dynamique dans cette passe |
| **Effet observable** | sur Brody : drapeaux de risque (`authority_claim`, `action_request`, `mutation_request`, `write_request`, `code_debug`) et intention (`question`, `analysis`…). Sur les routes : « unités d'alphabet » (langue, frontière, drapeaux, forme), contraintes READONLY, calibrage de connaissance lexicale (`calibrate_lexical_knownness`) | code |
| **Limites** | les classifieurs procèdent par **mots-clés et expressions régulières** ; aucun sens lexical, aucune désambiguïsation ; `os_trad_authority: TRANSLATION_ONLY` ; l'adaptateur de build reste en dry-run. Une route montée **ne prouve pas** un branchement cognitif : l'effet sur Brody se limite à l'intention et au risque. | — |
| **Variantes ailleurs** | copies dans `obsidia-clean-wt`, `obsidia-g16-*`, `obsidia-f7-*`, `obsidia-engine-proof-core` (dont `obsidia-x108-proofs_REMOTE_A5F21C6B`, 1 265 chemins correspondant à os_trad / avdr / continuum, surtout `_doc_curation` et `.local_audits`) | **SOURCE_NOT_VERIFIED** : il faudrait comparer par empreinte ces copies avec le worktree, et lire `_doc_curation` pour l'historique |
| Notes `.deepseek/pastes` | synthèses d'assistant [AF], jamais citées comme paroles du fondateur | non lues |

**Utilité pour R4 :** `calibrate_lexical_knownness` (mot connu ou inconnu) peut servir de signal d'**abstention** (famille 7). Les classifieurs d'intention et de risque ne servent pas au sens lexical.

## 2. AVDR

| Niveau | Constat |
|---|---|
| **Canon** | `docs/gencoin/sandbox_pre_freeze/AVDR_CANON.md` : **Accueil → Vibration → Déploiement → Résolution**, un « protocole de lecture et de transformation vivante d'un état cognitif », fusionné avec ADeLe / A2DR (mesure) et la Balance (pesée non linéaire) |
| **Code** | `periphery/gencoin_sandbox/avdr_phase_mapper.py` (49 lignes) : il attribue une phase à partir de deux nombres (`truth_score`, `sigma_score`) par seuils fixes (0,4 / 0,3, 0,65 / 0,55, 0,85 / 0,75) ; `periphery/avdr.py` (2 lignes) : retourne `AVDR_CONTEXT_ONLY` |
| **Tests** | `tests/periphery/test_avdr_phase_mapper.py` : **5 / 5** relancés ici ; `periphery/test_friction_avdr.py` et pack `17_TESTS/test_friction_avdr.py` non relancés |
| **Runtime** | route API `periphery_ops.py:789` (`map_avdr_phase`). Le registre Brody le déclare `EXACT_FOUND`, `active: False`, et le classe en module « futur ». Le snapshot temporel indique `avdr_phase_available: False`. **Il n'est pas appelé sur Brody.** |
| **Friction / OBAN** | pack `12_FRICTION_AVDR_CONTINUUM` : `friction_symbolique.py` = `abs(logique − diffusif)` (2 lignes) ; `oban_rollback.py` = **placeholder** ; schémas JSON AVDR, FrictionSymbolique, OBAN |
| **Lean** | `periphery/lean_sandbox/AVDR.lean` (176 lignes) et `AVDR_Light.lean` (46 lignes) **compilent** avec la chaîne du projet (v4.28.0), sans `sorry`, sans `axiom`. Les théorèmes sont **définitionnels** : `rfl` sur la succession des étapes, enregistrement des variantes, introduction et élimination d'une conjonction de 7 prédicats. Ils prouvent la **cohérence des définitions**, aucune propriété dynamique ni sémantique. Ces fichiers sont dans `periphery/lean_sandbox`, **hors** du `lakefile` de `proofs/lean` : ils ne sont pas couverts par la construction de la bibliothèque de preuves. |
| **Divergence** | le Lean nomme les étapes classiques **audit → validate → deduce → resonate** (plus trace, filtre instable, sortie stable), avec des variantes classique, développementale, cosmique et légère. Le canon dit **Accueil → Vibration → Déploiement → Résolution**. Ce sont **deux lectures** différentes de l'acronyme, à réconcilier. |

**Ce qui est réellement représenté :**

| Notion demandée | Représentation réelle |
|---|---|
| Phases | deux nomenclatures (canon ; Lean) ; seul le mappeur à seuils est exécutable |
| Friction | une différence absolue de deux nombres (pack), sans usage runtime |
| Validation | un prédicat `validation_ok` en Lean (définitionnel) |
| Transformation, trajectoires, corrections | **non implémentées** (OBAN rollback est un placeholder) |
| Invariants testés | seuils du mappeur (pytest) ; cohérence définitionnelle (Lean) |

## 3. Continuum

| Aspect | Couvert ? | Par quoi | Appelé sur Brody ? |
|---|---|---|---|
| **État temporel** | partiellement | `brody_temporal_context_adapter.build_temporal_context_snapshot` : un résumé passé / présent / futur dérivé d'autres snapshots (sujet précédent, nombre d'enregistrements, état de la chaîne mémoire, candidats) | oui (`routes/brody.py:1234`), statique |
| **Continuité de session** | partiellement | `brody_session_memory_adapter` : lit le ledger JSONL de session (dernier message, sujet, `followup_supported`) | oui (`routes/brody.py:176`), statique |
| **Historique des chemins** | non | B9 (chemins cognitifs) isolé | non |
| **Reprise après interruption** | partiellement | le ledger de session persiste entre requêtes (lecture seule par l'adaptateur) ; pas de mécanisme de reprise d'un raisonnement interrompu | — |
| **Conservation des transformations** | non | — | — |
| **Provenance des connaissances** | non (dans Continuum) | B8 `EvidenceRef`, candidats (`source_id`), isolés | non |
| **Connexions entre branches** | non | `NodeContinuum` (dataclass : `event_ids`, `divergence`) jamais utilisée | non |

**Verdict Continuum :** l'étiquette `COVERED_BY_EXISTING_MODULE` signifie **couverture partielle**, par la continuité de session et un résumé temporel. Ce n'est **pas** une implémentation de Continuum comme mémoire des transformations et des branches.

## 4. Crosswalk mémoire et recherche par le sens (mise à jour)

Ces éléments ne forment **pas** un moteur intégré. Chacun a son propre statut.

| Élément | Statut réel | Contrat réutilisable pour R4, **sans raccordement runtime** |
|---|---|---|
| Frise humaine / chronologie éducative | absente ; Native Memory sans dates | aucun ; à concevoir |
| 34 arbres | signal R^34 à chaque requête Brody, « never a decision » | vecteur de phrase pré-calculé hors conteneur, comme trait, en ablation |
| Domaines spécialisés | `memory_world_mapper` avec contrat de domaine | étiquette de domaine comme trait ou filtre |
| Mot / sens / contexte | corpus lexical (formes, gloses, synonymes) ; SENS (cadres, ambiguïtés, scellé) ; **OS Trad : intention, risque, `calibrate_lexical_knownness`** | classes sémantiques depuis un export figé du corpus ; « mot connu ou inconnu » pour l'abstention |
| Graphes / nuages | point cloud 21D ; Graphiti chargé, retrait déclaré | aucun démontré |
| Relations calibrées | Balance, sigma, `truth_score` (entrées du mappeur AVDR) | à étudier ; aucun lien avec le sens |
| Continuum | partiel (§3) | modèle de journal de session, en lecture |
| Native Memory | 3 267 enregistrements en lecture seule, sans dates | aucun pour l'élève (risque de source cachée) |
| B8 / B9 / B10 | isolés, testés | B8 : états et temps de validité (concepts) ; B10 : requête « à la révision r » (concept, déjà reproduite par V0) |
| SENS | scellé, appelé sur Brody | traits de cadre pré-calculés, en ablation |
| OS Trad | §1 | signal lexical d'abstention |
| AVDR | §2 | **aucun** pour l'apprentissage du sens. Une lecture « phase d'apprentissage » d'un élève resterait une analogie non démontrée. |

## 5. Diagnostic V0 : méthode vérifiée

**Méthode :** leave-one-out sur les 18 items d'enseignement de « force » (14 leçons et 4 exercices), **sans corrections** (le bonus de cue est donc absent). Pour chaque item, on décompose le score de l'élève figé en part bayésienne (score total moins vote k-NN) et part k-NN. Code figé `aebbc335…`, aucun examen lu, aucun paramètre modifié.

| Mesure | Valeur | Remarque |
|---|---|---|
| Traits par phrase | médiane 26,5 (min 8, max 40) | composition médiane : n-grammes de caractères 11, positions 4, n-grammes cible 4, mots pleins 3, surface 1, déterminant 1 |
| Écart entre les deux premiers sens, part bayésienne | médiane **1,42** | corrige E4 |
| Écart entre les deux premiers sens, part k-NN | médiane **0,11** | |
| Réponse finale = choix du bayésien seul | **13 / 13** réponses non HOLD | le k-NN ne change jamais la décision |
| Bayésien seul correct / k-NN seul correct | 7 / 18 et 6 / 18 | |
| Résultat final | 7 justes, **6 fausses**, 5 HOLD (dont 2 « aucun trait non trivial vu », 3 par τ/δ) | |
| Abstention | HOLD si mot non enseigné, si aucun trait de position ou de n-gramme cible connu, si p1 ≤ 0,5, ou si p1 − p2 ≤ 0,15 | |

**Portée :** 18 items, avec 1 à 2 exemples restants par sens en leave-one-out. Ce sont des **constats descriptifs sur ce jeu**, pas une conclusion statistique.

**Séparation des causes :**

| Cause | Indice | Confiance |
|---|---|---|
| Faiblesse algorithmique | bayésien dominant (13 / 13), k-NN inerte | élevée sur ce jeu |
| Mauvaise calibration | softmax sur sommes de ~26 log-probabilités ; 6 erreurs non abstenues | moyenne |
| Défaut de représentation du sens | les morceaux de mots dominent ; aucune notion de classe sémantique | moyenne |
| Limites d'une mémoire d'exemples | 1 à 3 exemples par sens ; le k-NN ne départage pas | moyenne |
| Manque de données d'enseignement | 2 à 3 phrases par sens ; 1 pour « chemin » / « corriger » | élevée |
| Faiblesse des examens | X1-far sans mot plein commun par construction ; abstention binaire (1 HOLD) | élevée, pour la mesure ; le banc est néanmoins valide (référence parfaite) |

## 6. Les sept familles R4 (conservées, précisées)

| Famille | Capacité recherchée | Réutilisable (concept ou export, sans runtime) | Non démontré | Dépendances | Contamination | Épreuve de réfutation | Vision Oxygen |
|---|---|---|---|---|---|---|---|
| 1 Exemplaires et relations | départager les sens par constructions reliées | B10 (révisions, concept) | que des relations aident à n = 2 ou 3 | aucune | faible | ablation avec et sans relations sur le jeu indépendant | apprendre de quelques exemples |
| 2 Concepts et composition | généraliser aux mots inconnus | corpus `periphery/language` (export figé), SENS (traits), 34 arbres (vecteur) | que ces ressources portent l'information de sens utile | décision sur la ressource externe | **élevée** (choix de la ressource) | ressource figée **avant** le jeu ; ablation | relier les mots aux concepts |
| 3 Correction d'hypothèses | utiliser les contrastes « A, pas B » | aucun mécanisme existant ; une règle générique de négation à créer | qu'une règle générique soit fiable | réouverture explicite de B3 | moyenne | tests unitaires de la règle et ablation | apprendre de ses erreurs |
| 4 Cumul sans effacement | réviser sans réécrire | états B8 (concepts) ; journal V0 | — (déjà partiellement en V0) | aucune | nulle | tests d'interface existants | historique éducatif |
| 5 Récupération multi-axes | sens, domaine, contexte, temps d'apprentissage et de validité | B8 `ValidTimeInterval`, B10 `at_or_before` (concepts) | utilité pour l'acquisition | aucune | nulle | nouveaux tests d'interface (non probants pour l'apprentissage) | frise éducative locale |
| 6 Erreurs et provenance | garder les erreurs comme exemples négatifs | B8 `EvidenceRef` (concept) | gain sur l'acquisition | 3 | faible | ablation | « on apprend aussi de ses fautes » |
| 7 Calibration et abstention | moins d'erreurs assurées, HOLD justifié | OS Trad `calibrate_lexical_knownness` (signal mot connu ou inconnu) | que le signal lexical réduise les erreurs | décision ressource | moyenne | HOLD injustifié et erreurs sur le jeu indépendant | savoir dire « je ne sais pas » |

AVDR, Continuum (au-delà de la session), MMonde, Native Memory et les ébauches de friction ou d'OBAN **n'ont pas démontré** de capacité utile à l'apprentissage du sens. Ils restent hors R4 tant qu'aucun manque précis ne les appelle.

## 7. Recherche encore nécessaire

1. Comparer par empreinte `obsidia-engine-proof-core/obsidia-x108-proofs_REMOTE_A5F21C6B` (`_doc_curation`, `.local_audits`) et les worktrees copies avec ce dépôt : **SOURCE_NOT_VERIFIED**.
2. Faire une trace **dynamique** d'un appel `brody_chat` qui confirme l'appel de `_risk_flags` / `_intent` d'OS Trad et des snapshots Continuum, dans un journal isolé, sans écriture.
3. Réconcilier les deux nomenclatures d'AVDR (canon contre Lean) : c'est une décision du fondateur.
4. Relancer les tests OS Trad et friction AVDR, non relancés ici.

## 8. Audit indépendant : PASS_WITH_NB (remarques intégrées ici, sans réécrire le texte audité)

- **NB1 :** l'appel d'OS Trad sur Brody a lieu pour une requête **par défaut** (`compact=False`). Les modes `compact` et `debug` sortent plus tôt (`routes/brody.py:390` → retour en :527) et ne l'appellent pas. Le §1 doit donc se lire « sur chaque message en mode par défaut ».
- **NB2 :** les deux écarts du §5 n'utilisent pas la même définition. Écart bayésien : entre les deux premiers sens du score final. Écart k-NN : entre ces **mêmes** deux sens (0,107). Mesuré sur les deux premiers sens propres au k-NN, il vaut 0,081. La conclusion (k-NN inerte) ne change pas.
- **NB3 :** `NodeContinuum` existe en deux versions : `periphery/continuum_node.py` (`event_ids`, `divergence`) et `periphery/common_types.py:90` (`events`, `description`). Aucune n'est utilisée dans le runtime.
- **NB4 :** « une vingtaine de fichiers de tests » se décompose en 7 fichiers dont le nom contient `os_trad` et 27 qui le mentionnent.
- **NB5 :** les tests de friction AVDR n'ont pas été relancés (point déjà déclaré au §7).
