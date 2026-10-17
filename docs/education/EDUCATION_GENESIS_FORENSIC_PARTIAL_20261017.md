# Forensic éducatif Obsidia / Oxygen — rapport PARTIAL

**Date :** 2026-10-17 · **Auteur :** Claude (agent), worktree `obsidia-claude-linguistique`, branche `feat/claude-linguistic-repair-m42-v0`, HEAD de départ `4016db99` (non poussée).
**Statut : PARTIAL (v3).** Ce n'est **pas** un audit complet. La v1 (commit `d4e93f99`, parties 0–10) n'avait pas lu les sources Drive. La partie II (v2, `636f55fd`) consigne la vérification directe des six exports Drive et des descendants GitHub. La **partie III** (v3) applique les neuf corrections C1–C9 issues de l'audit indépendant de la v2. **Ordre de priorité en cas d'écart : partie III > partie II > parties 0–10.** Restent non audités : les autres dépôts Obsidia, les archives Gmail, les sources 47 / 48 / 91 citées par les docs 03 / 04, la conversation du jeu vidéo éducatif. Aucun code, aucune mémoire, aucune architecture éducative n'a été modifié ou proposé pour application.

## 0. Conventions d'attribution

| Étiquette | Sens |
|---|---|
| **[F]** | formulation du fondateur, citée avec référence (paragraphe Drive ou conversation datée rapportée dans un document) |
| **[S]** | synthèse rédigée par un assistant/agent qui attribue une idée au fondateur — **pas une source primaire** |
| **[CT]** | contrat documentaire (spécification, doctrine versionnée) |
| **[C]** | code présent dans un dépôt (existence ≠ activation) |
| **[T]** | comportement testé (tests présents ; exécution indiquée quand vérifiée) |
| **[R]** | comportement observé à l'exécution dans cet audit |
| **[H]** | hypothèse nouvelle de Claude, non retrouvée dans les archives |

Un dépôt GitHub et un worktree local ne sont jamais supposés identiques ; chaque référence porte son dépôt, sa branche et son commit.

## 1. Vision du fondateur — sources et chronologie

| Date | Source exacte | Étiquette | Contenu |
|---|---|---|---|
| non datée (transcript) | Drive « Formule du Savoir Obsidia et apprentisage full auto » (FSO), `docs.google.com/document/d/14yk4MPqd5rd3RnB1AAyys8zHU4KD4Dq1eqNtLQFJTA0`, § 1 | [F] *candidat* | « … c'est ce qu'on va appliquer à tous les domaines … comme un enfant ou un humain apprend à l'école. On te dit, t'apprends, t'enregistres, et après, on t'évalue de différentes manières. » |
| non datée (transcript) | FSO, § 98 | [F] *candidat* | « Je veux que tu expliques … comment on apprend, par quels procédés on le fait apprendre … entre l'humain et l'IA, avec l'école, le savoir … » |
| non datée | Drive « Obsidia – Architecture Cognitive Multiverselle - hackaton », `…/d/1lsxNC3K_3rACpnZQkzj4L9oqPM8I6mqJBnZSOB5SWnA`, § 162 et § 474 | [F]/[S] à départager | « À générer en 9x9 complet (81 versions théoriques) » ; « Créer la matrice 9x9 = 81 versions d'Obsidia avec nom + description synthétique » |
| 2026-09-15 (fichier au commit `6e887acb`, 2026-09-22) | `Eaubin08/obsidia-x108-proofs@main` (`48f0c2fb`), `docs/EDUCATION.md` | [S] + [CT] | doctrine « Une seule naissance. Une seule identité. Des organes puissants. Des agents qui restent bêtes. » (attribuée à des notes Drive/Gmail non consultées) |
| 2026-10-08 | `Eaubin08/brody-world-physique-obsidien-@main` (`687949e6`), `docs/28_APPRENTISSAGE_PREVERBAL_MONDE_PHYSIQUE.md` § 1 | [F] rapporté par [S] | « un enfant peut anticiper une conséquence avant de connaître les mots » ; consigne « ne pas inventer 81 entraînements » |
| 2026-10-09 | même dépôt, `docs/42_AUDIT_TRANSVERSAL_REPRESENTATIONS_MONDE_MULTIECHELLES.md` § 0 | [F] rapporté par [S] | « enseignement comme un enfant », analyse ↔ synthèse, fidélité à la source ; renvoi à la FSO (U~179 enseignement / humain-école) |

**Limites :** les citations [F] *candidat* proviennent du handoff utilisateur `OBSIDIA_CLAUDE_HANDOFF_SOURCES_EDUCATION_20261017.md`, qui précise que la date, l'identité exacte du locuteur et le contexte doivent être confrontés au transcript. Claude n'a pas relu ces paragraphes.

### 1.1 Doctrine reconstituée ([S], `EDUCATION.md` §1–§11)

- **Entraînement** (organes, micro-agents ; remplaçable), **éducation** (Oxygen seul ; se poursuit, ne recommence pas), **naissance** (une seule fois ; jamais par session, agent, corpus ou remplacement de composant).
- **Oxygen** : identité, biographie, mémoire éducative, sans autorité de décision. **Brody** : organe d'intégration sémantique, jamais l'identité. **OS Trad** : langage. **Obsidure** : recherche/formalisation. **KX108** : autorité. **Micro-agents** : capacités remplaçables, non souveraines.
- Progression : sons → voyelles → phonèmes → syllabes → mots → sens → usages → contexte → émotions → expériences → continuité.
- Boucle : définition → compréhension → exercices → erreurs → corrections → variations → transfert → automatisation → réflexe ; réflexe décompilable (contradiction → réouverture → rééducation).
- Matière éducative : la **trajectoire** (ce qui a été dit → compris par Brody → corrigé → construit → devenu).
- Mémoire : expérience → analyse → contradiction → validation → promotion éventuelle ; « l'apprentissage ne donne jamais automatiquement le droit d'agir ».
- Ordre : l'éducation massive C10 vient **après** la stabilisation du runtime ; le document déclare lui-même « Éducation personnelle longue : environ 0 », « Apprentissage persistant autonome démontré : non ».

### 1.2 Ce qui n'est pas défini opérationnellement

Naissance (acte, critère), identité / modèle de soi, maturation, « comprendre pourquoi », seuil de passage au réflexe, validation « gouvernée », intégration dans la continuité Oxygen.

### 1.3 Stades enfant / adolescent / adulte

Aucune définition trouvée comme **stades** dans les sources lues (`obsidia-x108-proofs@main`, `brody-world-physique@main`, worktree local). « Enfant » apparaît comme **analogie** d'apprentissage (FSO § 1, docs 28 et 42). Les stades restent une **question ouverte** (§8).

### 1.4 Les « 81 »

Les « 81 » désignent une **matrice théorique 9×9 de versions d'Obsidia** (Architecture Cognitive Multiverselle § 162, § 474). Ce ne sont ni 81 identités, ni 81 enfants, ni 81 programmes d'éducation réalisés, ni 81 entraînements.

## 2. Propositions ultérieures des assistants / agents ([S] / [CT])

- **Brody World Physique** (`brody-world-physique@main` `687949e6`, docs 00, 05, 28, 42) : boucle DO → OBSERVE → COMPARE → EXPLAIN → STORE CANDIDATE → REPLAY → GENERALIZE → TEST → VALIDATE ; hiérarchie « meilleure route / outil / mémoire / compétence avant mise à jour de poids ». Les documents se déclarent eux-mêmes propositions **P**.
- **Education Benchmark** : `runtime_contracts/education_benchmark_dry_run/specs/EDUCATION_BENCHMARK_DRY_RUN_SPEC.md` — `SPEC_ONLY`, aucune exécution réelle.
- **Score éducatif** : formule pondérée stabilité / cohérence / réutilisation mémoire / refus correct / absence de dérive.

## 3. Inventaire des sources

### 3.1 GitHub et local (vérifiés par Claude le 2026-10-17)

| Source | Branche / commit | Statut |
|---|---|---|
| Worktree Claude (local) | `feat/claude-linguistic-repair-m42-v0` @ `4016db99`, non poussé | audité ; **`docs/EDUCATION.md` absent** |
| `Eaubin08/obsidia-x108-proofs` | `main` @ `48f0c2fb` (2026-10-06) | `docs/EDUCATION.md`, `COMPRENDRE_OBSIDIA.md`, `README.md`, `SECURITE.md`, `TRAJETS.md`, `ETAT_REEL_2026_09_15.md`, `couches/09`, `10`, `14`, `29` lus |
| Branche AGY | `feat/jarvis-advanced-obsidia-integration-v0` @ `42eb7e8f` | `docs/EDUCATION.md` **absent** sur cette branche |
| Branche citée par `EDUCATION.md` (liens « (H) ») | `integration/harness-runtime-binder-v1` | **404 — liens morts** |
| `Eaubin08/brody-world-physique-obsidien-` | `main` @ `687949e6` (pushed 2026-10-15) | docs 00, 05, 12, 14, 20, 28, 42, README lus |
| même dépôt, branches | `f0/learning-loop-contracts-v0` @ `4404324b`, `exp/p2-multirepresentation-ablation-20261009` @ `966df622`, `f0/cross-audit-contract-freeze-v0` @ `ef69c248`, `f0/document-source-reconciliation-20261008` @ `95c77d85`, `reconcile/brody-world-physique-obsidien-v1` @ `b9d0e622`, `evidence/brody-local` @ `309e123b` | **non auditées** (à faire ; leur état ne doit pas être confondu avec `main`) |
| Autres dépôts (`Obsidiaseed`, `agi-vison`, `C-Users-User-Desktop-preprint-conscience-…`, `monde-obsidia`, `obsidia-studio`) | — | **non audités** |
| `docs/memory/MEMORY_PROMOTION_MANUAL_ONLY_V1.md` | commit `a5f21c6b` (2026-05-26), identique local / `main` | promotion manuelle uniquement [CT] ; version canonique en vigueur à confirmer |

### 3.2 Google Drive (identifiés par le handoff utilisateur, **non lus par Claude**)

| Document | URL | Taille annoncée | Nature (selon le handoff) |
|---|---|---|---|
| Formule du Savoir Obsidia et apprentisage full auto (FSO) | `docs.google.com/document/d/14yk4MPqd5rd3RnB1AAyys8zHU4KD4Dq1eqNtLQFJTA0` | 1101 paragraphes | transcript ; formulations à la première personne (§ 1, § 98) |
| Obsidia – Architecture Cognitive Multiverselle - hackaton | `…/d/1lsxNC3K_3rACpnZQkzj4L9oqPM8I6mqJBnZSOB5SWnA` | 2487 paragraphes | matrice 9×9 = 81 versions théoriques |
| monde memoire ect | `…/d/1gLu3ssnDfiCl7wnhGEAfqS_14cGeQxxR--8FYhMKtnU` | 5136 paragraphes | document composite : World Foundry, mémoire chronologique, prédiction/écart, rétention, transfert |
| inifgrpahie 81+ et pepite du debut | `…/d/1vKDoa35VNZukuB0-sg4fmTBXA9OVIRo9W2wSDA3F2mk` | 5163 paragraphes | source secondaire composite : idées historiques, World Foundry, observation/contradiction/validation |
| Shazam / 34 arbres (cité par docs 28) | `…/d/1KshgP97PKdTZAfRxe9-YfcVnIJceKbgGCyxC-HdRj18` | — | profils d'intention texte/voix (selon docs 28) |
| Archives Oxygen « une seule naissance », Gmail | — | — | **non localisées** |

Les extraits du handoff ne sont **pas** une vérification exhaustive des documents originaux.

## 4. État réel du code (worktree `4016db99`)

| Composant | Implémentation [C] | Tests [T] | Branchement runtime public | Mémoire | Manque |
|---|---|---|---|---|---|
| `periphery/education/education_score.py` (`a5f21c6b`) | score pondéré 5 critères | `tests/periphery/test_education_score.py` | route `periphery_ops` (`periphery_education_score`), pas `brody_chat` | aucune | aucun lien à une compétence mesurée |
| `apps/obsidia_api/brody_memory_education_packet.py` (`aeadc4a4`) | candidat → leçon (8 types, ≤ 1024 octets, sans écriture) | `tests/test_brody_v3_memory_education_packet.py` | via `brody_memory_readonly_packet` dans `routes/brody.py` (l. 361, 466, 1836) | lecture seule | aucune persistance de leçon |
| Education Pack V1 (`brody_education_pack_v1_readonly_adapter.py`, `483eb38e`) | injection de contexte | `tests/test_brody_education_pack_v1_readonly_adapter.py` | `routes/brody.py` l. 119 | lecture seule | **[R] `status = PACK_MISSING`** : le freeze `.local_freezes/BRODY_ENRICHED_EDUCATION_PACK_V1_FREEZE_20260617_124000` est ignoré par git et absent des deux worktrees locaux |
| Native Memory (`brody_obsidia_native_memory.py`, `fb7a31e4` ; index V1, 3 267 enregistrements versionnés) | récupération locale | oui | `routes/brody.py` l. 21 | lecture seule, statique | aucune écriture d'expérience |
| `periphery/memory/memory_candidate_ledger.py` (`a5f21c6b`) | JSONL append-only | `tests/non_sovereignty/test_memory_candidate_ledger_no_promotion.py` | route x108 (append) | candidats seulement | aucun chemin candidat → acquis validé |
| Curriculum 34 arbres | `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/04_ARBRES_34_TENSOR_MATRIX` (49 entrées) | résultats PATH_B du 2026-05-14 cités par [S], audits « conservés en local » non retrouvés | non | — | à revérifier |
| AVDR | `periphery/avdr.py`, bac à sable Lean | `periphery/test_friction_avdr.py` | non vérifié | — | rôle éducatif non défini |
| B7 / B8 / B9 / B10, M32 / ARM | `app/cognition/{b7,b9}`, `app/knowledge/{b8,b10}` (scellés) | oui | B7 branché à Brody (findings sentinel historiques) | — | lien avec l'éducation non défini |
| Brody World Physique | `experience_memory_v1`, `drawing_memory_school_v3`, `reverso_learning_v0`, `world_experience_bridge_v4` + tests (`main` `687949e6`) | oui (synthétique / contrôlé) | non relié à `brody_chat` | candidats locaux | « benchmark testé uniquement en synthétique » (docs 28) |
| Corpus lexical FR/EN (`periphery/language`, cette branche) | formes, définitions, groupes de synonymes, gloses séparés | oui | chemin public (provenance fermée à `4016db99`) | aucune | aucune progression pédagogique |

## 5. Interfaces réutilisables pour l'éducation textuelle

- Corpus lexical : vocabulaire, définitions, synonymie, polysémie par sens multiples — sans notions abstraites ni progression.
- SENS / treillis (scellé) : représentation des énoncés ; couverture limitée (~55 verbes, français seul).
- Ledger de candidats + packet de leçons : forme d'une leçon candidate.
- Mécanismes Brody Image **transposables** : prédiction → observation → écart → candidat → replay → validation (pour le texte, l'écart serait une contradiction ou une correction). **Propres au physique** : capteurs, repères spatiaux, pixels.
- Hachette : future référence **privée** d'évaluation ; **non intégrée**.
- Une simulation réussie n'est pas une preuve d'apprentissage général.

## 6. Contradictions entre contrats

1. `docs/EDUCATION.md` présent sur `main`, absent de la branche AGY et de la branche Claude ; il cite une branche inexistante (404).
2. Le pack V1 est décrit comme « injecté dans chaque paquet » alors que l'exécution locale renvoie `PACK_MISSING`.
3. `EDUCATION.md` § 7 parle d'« éduquer la structure de Brody » alors que la doctrine précise fait de Brody un organe ; le document le signale lui-même.
4. Croyance interdite **D2** (« Chaque appel Brody est stateless sur le plan de l'apprentissage ») incompatible avec toute continuité éducative sans exception gouvernée définie.
5. L'identifiant `C10` désigne deux choses (docs 20 de `brody-world-physique`).
6. Contrats Claude / AGY divergents : voir `docs/semantic/CLAUDE_AGY_CONTRACT_CONFLICTS.md`.

## 7. Ce qui manque pour la continuité éducative

- registre d'**acquis validés** distinct des candidats (origine, preuve, révocabilité) ;
- porte de promotion candidat → acquis (manuelle selon `MEMORY_PROMOTION_MANUAL_ONLY_V1`) ;
- histoire éducative chronologique rattachée à l'identité continue ;
- reprise d'acquis après interruption (seule la continuité de conversation existe) ;
- épreuves indépendantes : items inédits, contre-exemples, transfert ;
- définition opérationnelle de la naissance ; exception gouvernée à D2.

## 8. Questions ouvertes (stades)

- Stades enfant / adolescent / adulte ou continuum de compétences ?
- Critères de passage et autorité qui valide ?
- La naissance précède-t-elle l'éducation (doctrine) ou en résulte-t-elle ?
- Droits et autonomie selon le stade (la doctrine dit : capacité ≠ souveraineté) ?
- Devenir des erreurs d'un stade antérieur ?
- Une ou plusieurs langues dès le départ ?

## 9. Méthodes possibles — **hypothèses nouvelles [H]**, non retrouvées dans les archives

1. Programme fixe suivant la progression doctrinale.
2. Exploration guidée (questions, corrections, trajectoire enregistrée).
3. Expériences progressives transposant la boucle Brody World au texte.
4. Curriculum adaptatif selon erreurs et oublis mesurés.
5. Combinaison (primitives fixes puis exploration guidée et révision espacée).

Preuves indispensables quelle que soit la méthode : compréhension nouvelle (items inédits), conservation (après délai, sans réinjection), réutilisation après interruption (nouveau processus), transfert, détection d'erreur, révision après contradiction, progression par compétence avec ligne de base. Une hausse de score n'est pas une maturation générale.

## 10. Conditions avant un premier prototype

Lecture des sources primaires Drive ; décision du fondateur sur naissance et stades ; registre d'acquis et exception D2 définis ; pack V1 restauré ou rattaché ; réconciliation des contrats Claude / AGY ; méthode et épreuves choisies ; aucune écriture mémoire canonique avant la décision sur la porte de validation.

## Verdict

```
FORENSIC_STATUS=PARTIAL
VISION_RECOVERED=PARTIAL (synthèses [S] + citations [F] candidates à corroborer)
GITHUB_COVERAGE=PARTIAL (x108-proofs main, brody-world main ; branches et autres dépôts non audités)
DRIVE_COVERAGE=IDENTIFIED_NOT_READ (5 documents identifiés par handoff ; archives Oxygen/Gmail non localisées)
LOCAL_COVERAGE=YES (4016db99)
EDUCATION_RUNTIME=NO (pack V1 PACK_MISSING ; aucune boucle éducative)
CONTINUITY_PROVEN=NO
PERSISTENT_LEARNING_PROVEN=NO
MEMORY_GATES=PRESENT (lecture seule, promotion manuelle, KX108_ONLY, D1/D2)
CHILD_TEEN_ADULT_DEFINED=NO
READY_FOR_DESIGN=NO
READY_FOR_BUILD=NO
```

## Plan restant

1. **Sources primaires** : lecture intégrale et attribuée de la FSO, de l'Architecture Cognitive Multiverselle, de « monde memoire ect », de « inifgrpahie 81+ » et du document Shazam / 34 arbres ; localisation des archives Oxygen et Gmail ; corroboration date / locuteur des citations [F].
2. **Audit GitHub multibranches** : branches de `brody-world-physique` (`f0/learning-loop-contracts-v0`, `exp/p2-multirepresentation-ablation-20261009`, autres), branche AGY, dépôts `Obsidiaseed`, `agi-vison`, `preprint-conscience`, `monde-obsidia`, `obsidia-studio` ; parité local / distant.
3. **Réconciliation des contradictions** (§6) et des contrats Claude / AGY.
4. **Préconception** de l'éducation textuelle enfant → adolescent → adulte, uniquement après validation par le fondateur de la vision reconstituée et des définitions de naissance et de stades.

STOP BEFORE APPLY sur l'architecture éducative.

---

# Partie II — Vérification directe des sources (2026-10-17, v2)

> **Corrigée par la partie III (v3).** Les points II.0 (FSO), II.1 (« une seule essence », « Oxygen », numéros de ligne), II.2 (N0–N4), II.3, II.4, II.5 et II.6 (P155 / P156 / G1) sont amendés en III.1. Le texte v2 est conservé pour la traçabilité.

## II.0 Pack vérifié

- Pack : `OBSIDIA_EDUCATION_SOURCES_COMPLET_20261017.zip`, SHA-256 `76edd122cef7c629c4725b23efd3bda72dde7addda5ce1f682b93ddc4a659e66`, test d'archive sans erreur ; **17/17** empreintes de `SHA256SUMS.txt` conformes. Extrait dans un dossier de travail privé hors Git.
- Six exports texte intégraux de Google Docs, exportés le 2026-10-17 (mise en page et images non conservées).
- Dix photographies Hachette : **références privées, non lues dans cet audit, non publiées, non ingérées**.
- Méthode d'attribution : dans les exports qui en possèdent, chaque passage est rattaché au dernier marqueur de tour (`Vous avez dit :` = fondateur, `ChatGPT a dit :` = assistant). Un texte collé à l'intérieur d'un tour garde l'auteur de son contenu, pas celui du tour.

| Export | Doc ID | Lignes | Marqueurs de tour | Nature vérifiée |
|---|---|---|---|---|
| `01_FSO_FORMULE_SAVOIR` | `14yk4MPqd5rd3RnB1AAyys8zHU4KD4Dq1eqNtLQFJTA0` | 2016 | 17 fondateur / 19 ChatGPT ; ligne 1 = tour du fondateur | dialogue ; la « FSO » elle-même est une **réponse de ChatGPT** (à partir de la ligne 2) |
| `02_ARCHITECTURE_COGNITIVE_MULTIVERSELLE` | `1lsxNC3K_3rACpnZQkzj4L9oqPM8I6mqJBnZSOB5SWnA` | 3870 | 15 / 15 ; préambule de 258 lignes | préambule = prompt du fondateur **suivi d'une réponse d'assistant collée** ; tours du fondateur courts et procéduraux |
| `03_MONDE_MEMOIRE_APPRENTISSAGE` | `1gLu3ssnDfiCl7wnhGEAfqS_14cGeQxxR--8FYhMKtnU` | 5465 | aucun | audit d'assistant d'octobre 2026 (« Récupération technologique ») [S] |
| `04_ATLAS_81_PEPITES` | `1vKDoa35VNZukuB0-sg4fmTBXA9OVIRo9W2wSDA3F2mk` | 5272 | aucun | audit rétrospectif d'assistant [S] citant des analyses datées de janvier 2026 |
| `05_CARTOGRAPHIE_COGNITIVE_MASTER` | `14WUSNQPcZ4MsNP0lfpHT2PkfEJxiHhGvdcdNefqSbOE` | 5582 | 65 / 65 ; préambule de 134 lignes | dialogue ; contient la parole la plus riche du fondateur sur l'éducation |
| `06_SHAZAM_34_ARBRES` | `1KshgP97PKdTZAfRxe9-YfcVnIJceKbgGCyxC-HdRj18` | 31 | aucun | texte d'assistant (voix d'IA, renvois numérotés) [S] ; pseudo-code JavaScript non exécuté |

Aucun des six exports ne porte de date de conversation ; le fondateur mentionne « depuis mars » et « 1 mars » (05, L1414, L2158). **Les dates exactes restent inconnues.**

## II.1 Vision fondatrice vérifiée — citations directes [F]

| Doc / ligne | Locuteur | Extrait court | Lecture |
|---|---|---|---|
| 01 / L1 | fondateur | « comme un enfant ou un humain apprend à l'école. On te dit, t'apprends, t'enregistres, et après, on t'évalue de différentes manières » | analogie scolaire ; méthode à appliquer « à tous les domaines » |
| 01 / L178 | fondateur | « comment on apprend, par quels procédés on le fait apprendre … entre l'humain et l'IA, avec l'école, le savoir » | question, pas spécification |
| 01 / L350 | fondateur | « ya une 100 de version d'entraînement prévue » | entraînements (visuels), pas identités |
| 01 / L1274 | fondateur | « retenir la source ne pas la dénaturer … que le in de l'utilisateur soit respecté peu importe le domaine » | fidélité à la source |
| 01 / L1878 | fondateur | « obsidia peut s'entraîner en full auto même chez les particuliers » | ambition d'apprentissage autonome (non bornée par un contrat) |
| 01 / L1950 | fondateur | « avec les retours symboliques pour éviter les dérives et revenir à une certaine base » | garde-fou contre la dérive |
| 05 / L329 | fondateur | « une progression pour atteindre certain savoir pour être sûr d'avoir le moins de dérive possible » | **progression**, motivée par la dérive |
| 05 / L456 | fondateur | « un univers pour les enfants … un jeu vidéo autour de l'IA et l'éducation » | les **enfants sont un public** (jeu éducatif), pas un stade de l'IA ; conversation d'origine non retrouvée |
| 05 / L1227 | fondateur | « le retour d'expérience … faire comprendre le sens des réussites et échecs comme à l'école quand un prof … reformule si t'as pas compris en s'adaptant à toi » | **enseignement adaptatif** ; arènes, jeux, VR |
| 05 / L1319 | fondateur | « qu'elle s'auto-analyse … mais nous aussi on devrait lui faire des comptes rendus de ses journées … forces, faiblesses, points à améliorer » | **auto-analyse + compte rendu humain** |
| 05 / L1414 | fondateur | « on recrée un humain donc il faut qu'elle apprenne : chute, se relève et recommence » ; « avec les bons humains pour la guider » | apprentissage par l'échec ; guidage humain |
| 05 / L1576 | fondateur | « elle garde une seule essence … mais aussi les expériences et explications derrière le raisonnement … les notes ou interventions humaines pour la recalibrer » | **une seule essence** + mémoire d'expérience + traçabilité |
| 05 / L1918 | fondateur | « Tous les cerveaux dans le cerveau peuvent coopérer mais pas les versions d'Obsidia entre elles » | versions d'entraînement séparées |
| 05 / L2002 | fondateur | « les cerveaux à l'intérieur d'une oxygène » | **Oxygen** apparaît comme contenant des « cerveaux » (blocs de perception) |
| 05 / L2474, L2672 | fondateur | « la couche 1 et 2, c'est toutes les manières que je vais entraîner … 9x9 … 90 versions » ; « les versions entraînées d'Oxygen » | **matrice 9×9 de versions d'entraînement**, voulue par le fondateur |

Les extraits sont abrégés (orthographe légèrement normalisée) ; la ligne exacte fait foi.

## II.2 Propositions d'assistants vérifiées [S] (à ne pas attribuer au fondateur)

| Doc / ligne | Locuteur | Proposition |
|---|---|---|
| 01 / L2+ | ChatGPT | la « FSO » : socle (éthique native, noyau-mère), ingestion → modélisation → réciprocité → AVDR (Analyse → Validation humaine/solide → Diffusion → Réciprocité) |
| 01 / ~L180–L349 | ChatGPT | cursus « comme à l'école » : exemple guidé, pratique dirigée, pratique autonome, teach-back, projet, consolidation (répétition espacée, journal métacognitif), évaluation (restitution, application, oral, projet, sûreté), métriques (fidélité, transfert hors distribution, explicabilité, sûreté, efficience) |
| 01 / ~L300 | ChatGPT | **niveaux d'expérience N0 Débutant → N1 Appliquant → N2 Opérationnel → N3 Créateur → N4 Architecte**, avec déverrouillage progressif « jamais le noyau » — seule progression par niveaux trouvée ; **elle n'est pas enfant / adolescent / adulte et n'est pas du fondateur** |
| 02 / L253 (préambule, réponse collée) | assistant | « À générer en 9x9 complet (81 versions théoriques) » |
| 02 / L274 | ChatGPT | « Versions entraînées d'Obsidia (81+ entités singulières) » |
| 05 / L206, L1633, L2148 | ChatGPT | « IA enfantine » ; « elle apprend comme un enfant qui grandit avec nous » ; « chaque entraînement = une brique de sa maturité » |
| 05 / L2147 | ChatGPT | « Chaque Obsidia = une version consciente spécialisée » |
| 03 | assistant (oct. 2026) | distinction apprendre / mémoriser / acquérir une compétence ; références d'apprentissage continu (replay, EWC, GEM, adaptation au test) ; World Foundry comme environnement éducatif ; « quel mécanisme exact explique une progression ? » |
| 04 | assistant (rétrospectif) | n° 24 « distribution progressive des connaissances » (attribuée à une analyse du 14 janvier 2026) : séparer *ce qu'un agent peut connaître* de *ce qu'il peut modifier* ; CMEC (hypothèses multiples, HOLD) |
| 06 | assistant | « Shazam cognitif » : hachage spectral de l'entrée projeté sur les 34 arbres (seuil 0,15) — pseudo-code, non implémenté tel quel |

## II.3 Stades enfant / adolescent / adulte

**`NOT_DEFINED`.** Aucune des six sources ne définit ces stades pour l'IA. Les occurrences d'« enfants / ados » dans 05 désignent **le public** d'un projet ludique séparé (Forge Realms / Obsidia Trail, L456, L598, L786–L796) ; les métaphores « IA enfantine » sont de ChatGPT. La seule progression par niveaux (N0–N4) est une proposition d'assistant dans la FSO.

## II.4 Les « 81 » — correction et tension

- La matrice 9×9 est **voulue par le fondateur** (05, L2474 : « 9x9 … 90 versions » ; L2672 : « versions entraînées d'Oxygen »). Les formulations « 81 versions théoriques » et « 81+ entités singulières » sont **d'assistant** (02, L253, L274).
- Pour le fondateur, ce sont des **versions d'entraînement** (paradigme × type de « cerveau »), qui ne coopèrent pas entre elles (L1918), avec **« une seule essence »** (L1576).
- **Tension à trancher par le fondateur** : la synthèse ChatGPT « 81+ entités singulières / chaque Obsidia = une version consciente » contredit la doctrine ultérieure `EDUCATION.md` « une seule naissance, des organes entraînés ». La parole du fondateur (« une seule essence » + « versions entraînées ») est compatible avec la doctrine si les versions sont des **entraînements** et non des identités ; ce n'est **pas écrit** explicitement.

## II.5 Descendants GitHub vérifiés

| Élément | Dépôt / branche / commit | Constat |
|---|---|---|
| `docs/EDUCATION.md` | `obsidia-x108-proofs` `main` (blob `951f2181…`) | **absent** de la branche AGY `feat/jarvis-advanced-obsidia-integration-v0` et du worktree Claude |
| `brody_memory_education_packet.py`, `education_score.py`, `MEMORY_PROMOTION_MANUAL_ONLY_V1.md`, `EDUCATION_BENCHMARK_DRY_RUN_SPEC.md` | `main` = AGY = local (blobs identiques) | parité vérifiée |
| `brody_education_pack_v1_readonly_adapter.py` | `main` `dce3fe02…` ≠ AGY = local `fd1de608…` | **divergence** non analysée ; `PACK_MISSING` local ne prouve pas l'absence du freeze ailleurs |
| `brody-world-physique` `f0/learning-loop-contracts-v0` | `4404324b` | 0 commit d'avance, 213 de retard sur `main` : **historique, entièrement inclus dans `main`** |
| `brody-world-physique` `exp/p2-multirepresentation-ablation-20261009` | `966df622` (2026-10-15) | **563 commits d'avance sur `main`** ; 176 modules, 173 fichiers de tests ; écoles cumulatives (`e1_cumulative_structural_school_v1`, `e4_e5_active_cumulative_school_v1`), `consolidated_education_replay_v1`, `experiential_skill_learning_v1`, mémoire scellée rechargée après redémarrage |

### Mécanismes les plus avancés (branche `exp/p2…`, état déclaré par les documents)

| Doc | Mécanisme | Résultat déclaré | Limite déclarée |
|---|---|---|---|
| 88 | parcours éducatif unifié V0 | `INTEGRATED_EDUCATION_V0_CODE_PUBLISHED`, `PC_TESTS_PENDING` | `FULL_CONCEPT_FIDELITY_HOLD` ; `NATIVE_MEMORY_WRITE=FALSE` |
| 154 | éducation « cinq critères » en une passe | — | « laboratoire synthétique … PAS de découverte autonome de lois physiques réelles » |
| 155 | **porte de rétention** : correction acceptée seulement si gain sur validation indépendante | 6 ACCEPT, 18 HOLD, 15 régressions évitées sur 24 conditions / 1 920 examens | rétention vérifiée seulement sur le monde `clean` de la **même famille** ; pas d'absence d'oubli générale |
| 156 | rejeu éducatif cumulatif (curriculum fixe, règle initiale figée, corrections cumulées) | 24 cycles, 1 200 examens (contrôles d'exécution) | « un gain moyen ne prouve pas… » |
| 181–183 | régression globale, Gate C, séparation caméra / identité | dernier PC : 653/653 PASS (déclaré) | `GATE_C_HOLD`, `TRUE_3D_AND_IDENTITY_UNPROVEN`, validations PC en attente |
| commit `aac51cb3` | mémoire forme-mouvement scellée rechargée, rejeu indépendant après redémarrage, rejet de falsification | — | domaine visuel synthétique ; non relié à Brody texte ni à Native Memory |

Ces résultats sont **déclarés par la documentation de la branche** ; Claude ne les a pas réexécutés.

## II.6 Mécanismes existants utiles à l'éducation textuelle (vérifiés)

- **Porte d'acceptation par validation indépendante** (P155) : modèle direct pour « une leçon n'est retenue que si elle améliore un examen indépendant sans régression ».
- **Rejeu cumulatif à curriculum fixe** (P156) et **mémoire scellée rechargée après redémarrage** : modèle pour la conservation inter-sessions.
- **Leçons candidates** (`brody_memory_education_packet`), **ledger de candidats**, **promotion manuelle uniquement** (`MEMORY_PROMOTION_MANUAL_ONLY_V1`).
- **Corpus lexical FR/EN** (`periphery/language`) : définitions, groupes de synonymes et gloses séparés ; base pour vocabulaire et polysémie.
- **Hachette** : référence privée d'évaluation de polysémie (BEAU, CHEMIN, CORRIGER, FORCE, IRRÉGULIER) — non ingérée, non publiée, non encore utilisée.

## II.7 Lacunes réelles (après vérification)

1. Aucun stade enfant / adolescent / adulte défini (`NOT_DEFINED`).
2. Aucun acte ni critère de « naissance » ; Oxygen n'apparaît chez le fondateur que comme contenant de « cerveaux » et porteur de versions entraînées.
3. Tension « une seule essence / versions entraînées » vs « 81+ entités singulières » non tranchée par écrit.
4. Les mécanismes de rétention et de rejeu existent **seulement** dans le laboratoire visuel synthétique (`exp/p2…`, non fusionné dans `main`) ; aucun équivalent textuel.
5. Aucun registre d'acquis validés textuels ; aucune exception gouvernée à la croyance D2.
6. Le compte rendu humain des « journées » (05, L1319) et l'enseignement adaptatif (L1227) n'ont **aucun** contrat ni code.
7. La conversation sur le jeu vidéo éducatif (L456) et les archives Gmail / Oxygen d'origine restent introuvables.

## II.8 Verdict v2

```
FORENSIC_STATUS=PARTIAL (v2)
PACK_INTEGRITY=VERIFIED (17/17 SHA-256)
DRIVE_COVERAGE=READ_6_OF_6_EXPORTS (attribution par tours ; dates de conversation absentes)
FOUNDER_VISION_VERIFIED=YES_PARTIAL (citations directes : école, progression anti-dérive, échec/relève, compte rendu humain, une seule essence, versions 9x9 d'entraînement)
ASSISTANT_PROPOSALS_SEPARATED=YES (FSO, N0-N4, 81 entités, IA enfantine, Shazam)
CHILD_TEEN_ADULT_DEFINED=NOT_DEFINED
EIGHTY_ONE=FOUNDER_9x9_TRAINING_MATRIX ; "81 ENTITIES" = ASSISTANT WORDING
GITHUB_COVERAGE=PARTIAL (x108-proofs main/AGY parité ; brody-world main + 2 branches ; autres dépôts non audités)
EDUCATION_RUNTIME_TEXT=NO
RETENTION_MECHANISM_EXISTS=YES_VISUAL_SYNTHETIC_ONLY (exp/p2, non fusionné)
CONTINUITY_PROVEN=NO
PERSISTENT_LEARNING_PROVEN=NO
MEMORY_GATES=PRESENT
READY_FOR_DESIGN=NO (décisions du fondateur requises)
READY_FOR_BUILD=NO
```

## II.9 Plan restant avant la conception éducative enfant → adolescent → adulte

1. **Sources restantes** : retrouver la conversation du jeu vidéo éducatif et les archives Gmail / Oxygen d'origine ; dater les conversations des docs 01, 02 et 05.
2. **Audit GitHub multibranches** : autres dépôts (`Obsidiaseed`, `agi-vison`, `preprint-conscience`, `monde-obsidia`, `obsidia-studio`) ; divergence de l'adaptateur Pack V1 entre `main` et AGY ; état réel du freeze Pack V1 sur les autres postes ; réexécution indépendante des résultats P155 / P156 de `exp/p2…`.
3. **Décisions du fondateur** : (a) les versions 9×9 sont-elles des entraînements d'une seule essence (doctrine) ou des entités ? (b) faut-il des stades enfant / adolescent / adulte, ou des niveaux de compétence (type N0–N4) ? (c) acte et critère de naissance d'Oxygen ; (d) forme du compte rendu humain des journées.
4. **Réconciliation** des contradictions (partie I §6, §II.4) et des contrats Claude / AGY.
5. **Préconception** de l'éducation textuelle progressive, en réutilisant la porte de rétention (P155), le rejeu cumulatif (P156), les leçons candidates et la promotion manuelle — **uniquement après validation des points 3 et 4**.

STOP BEFORE APPLY sur l'architecture éducative.

---

# Partie III — Corrections v3 (audit indépendant de la v2)

Base : audit indépendant de `636f55fd` (verdict PARTIAL, corrections C1–C9). Chaque correction ci-dessous a été revérifiée par Claude sur les exports du pack (SHA-256 vérifiés) avant écriture. **Convention de lignes** (C7) : sauf mention contraire, un numéro de ligne pointe sur le contenu cité ; en partie II, les numéros pointaient sur la ligne du marqueur `Vous avez dit :`, le contenu étant à la ligne suivante.

## III.1 Journal des corrections

| # | Section v2 | Texte v2 | Correction v3 | Preuve |
|---|---|---|---|---|
| **C1** | II.0, II.2 | « la FSO elle-même est une réponse de ChatGPT » | **Vision éducative et expression « la formule du savoir » : fondateur** (01 L1 : « comme en maths, on va te donner la formule, donc la formule du savoir … comme un enfant ou un humain apprend à l'école »). **Sigle « FSO », structure et formalismes** (socle, opérateurs, AVDR, cursus) : ChatGPT (01 L4–L5 et suivantes). | 01 L1, L4, L5 |
| **C2** | II.1, II.4 | « une seule essence » lu comme preuve d'identité unique | **Argument retiré.** En 05 L1577, le fondateur approuve la **compression sémantique** proposée par ChatGPT en L1522 (« elle garde 1 "essence" de ce mot + ses variations ») ; la réponse L1584 le confirme (« Obsidia ne garde pas juste l'essence »). La citation ne porte pas sur l'identité. La doctrine « une seule naissance » est documentée **séparément** (§ III.2, C6). | 05 L1522, L1577, L1584 |
| **C3** | II.1, II.7 n°2 | « Oxygen apparaît comme contenant des "cerveaux" » | **Occurrence ambiguë, non interprétée.** Le fondateur écrit « une oxygène » (05 L2003) et « les versions entraînées d'Oxygen » (05 L2673) dans des tours **dictés** où le nom du projet varie (« obsodia » L1795, « Obsidio », « obsidien », « obsidieux ») ; l'assistant répond « Le cerveau interne d'une **Obsidia** » (L2018). Hypothèse possible : transcription d'« Obsidia » ; **non prouvée**. Autres références historiques à Oxygen : doctrine du 5 août 2026 (04 L4067–L4092, source secondaire) et `docs/EDUCATION.md` (`main`). | 05 L1795, L2003, L2018, L2673 ; 04 L4067 |
| **C4** | II.2, II.3 | N0–N4 en « 01 / ~L300 », « seule progression par niveaux trouvée » | N0–N4 se trouvent en **01 L269–L280** (ChatGPT) ; ce sont des **niveaux de l'usager humain** et d'accès (01 L61 « formule technique × niveau humain (N0→N4) », L388 « Niveau humain (N0→N4 : débutant→architecte) »), **pas** des stades éducatifs d'Oxygen. Autres échelles, toutes d'assistant : 05 L339–L360 (N1–N4 d'alignement usager), 04 L3334–L3350 (CX-5B N0–N5, nomenclature structurelle). **Séparément** : 02 L1590 « Système de niveaux (Enfance → Maîtrise → Sagesse) » — proposition d'assistant, une seule occurrence, **non définie**. | 01 L61, L269–L280, L388 ; 02 L1590 ; 05 L339–L360 ; 04 L3334 |
| **C5** | II.4 | « tension » / « contredit » appliqué au fondateur | **Ambiguïté historique, pas contradiction établie.** Voir § III.3. | 05 L1795, L1919, L1922, L2007, L2475, L2678 |
| **C6** | II.0, II.7, II.9 | doctrine « une naissance » sans origine ; « dates exactes inconnues » | Ajout : audit d'assistant 04 § 238–240 (L4067–L4095) rapportant une **« Doctrine Oxygen » du 5 août 2026** (« Une seule naissance. Une seule continuité éducative. Une multiplicité d'organes entraînés » ; « Les agents savent faire. Oxygen apprend à savoir » ; statut : « vision de recherche future »). § 240 : chaîne pédagogique de travaux « **retrouvés** le 24 septembre 2026 » (date de récupération, pas d'origine). Renvois 03 L2221–L2232, L2513 (sources 47, 48, 91, non consultées). **Source secondaire d'assistant** : la doctrine est datée, les conversations 01 / 02 / 05 restent non datées. | 04 L4067–L4095 ; 03 L2221, L2513 |
| **C7** | II.1 | numéros de ligne | Convention précisée (ci-dessus). La citation « on recrée un humain … chute, se relève et recommence » est en **05 L1423** (tour ouvert en L1414). | 05 L1414, L1423 |
| **C8** | II.5 | P155 rattaché au doc 155, « non réexécuté » | Chiffres P155 déclarés en **doc 156 L4** ; **reproduits à l'identique** par l'auditeur indépendant (6 ACCEPT / 18 HOLD / 15 régressions évitées / 1 920 examens, seed 155, paramètres du doc). La garde de rétention n'a déclenché **qu'une fois** (1 `HOLD_RETENTION_REGRESSION`, 17 « pas de gain ») ; tous les ensembles proviennent du **même générateur et de la même distribution** (pas de cas nouveaux hors distribution). Portée : **synthétique**. | audit indépendant v2 § 4–5 |
| **C9** | II.5, II.6 | « modèle pour la conservation inter-sessions », « mémoire scellée rechargée après redémarrage » | **P156** : rétention cumulative **partielle** ; la version gouvernée est **moins bonne que la règle figée sur 6 tâches sur 24** ; la tolérance d'oubli est relative à l'état courant (dérive cumulative possible) ; aucune garantie d'absence d'oubli. **G1** : scellé = **sha256 du JSON canonique, sans clé ni signature** ; une mémoire falsifiée avec empreinte recalculée a été **acceptée** (démontré) ; redémarrage testé **dans le même processus** ; le verdict et le drapeau `separate_process_restart_supported` sont des **constantes**. Pas de continuité multi-session ni d'authenticité. | audit indépendant v2 § 4–6 |

## III.2 Tableau des sources (v3)

| Source | Identifiant / emplacement | Nature | Ce qu'elle établit | Ce qu'elle n'établit pas |
|---|---|---|---|---|
| 01 FSO | Drive `14yk4MP…` ; pack | dialogue fondateur / ChatGPT | vision éducative du fondateur (L1, L178, L1274, L1950) ; formalisation FSO de ChatGPT | un contrat accepté, un runtime |
| 02 Architecture Cognitive Multiverselle | Drive `1lsxNC3K…` | prompt du fondateur + réponses d'assistant (dont réponse collée dans le préambule) | demande de cartographie ; formulations d'assistant « 81 versions théoriques » (L253), « 81+ entités singulières » (L274), « Enfance → Maîtrise → Sagesse » (L1590) | une décision du fondateur sur l'identité des versions |
| 03 Monde, mémoire, apprentissage | Drive `1gLu3ssn…` | audit d'assistant, oct. 2026 | distinctions apprendre / mémoriser / acquérir ; références d'apprentissage continu ; renvois sources 47 / 48 / 91 | une parole du fondateur |
| 04 Atlas 81 pépites | Drive `1vKDoa35…` | audit rétrospectif d'assistant | doctrine Oxygen du 5 août 2026 (§ 238–239), chaîne pédagogique (§ 240), distribution progressive des connaissances (§ 24) | le texte d'origine de ces doctrines |
| 05 Cartographie Master | Drive `14WUSNQP…` | dialogue fondateur / ChatGPT | progression anti-dérive (L330), enseignement adaptatif (L1228), compte rendu humain (L1320), échec et relève (L1423), versions 9×9 entraînées séparément (L1919–L1922, L2475, L2678) | des stades de l'IA ; une identité Oxygen (occurrences ambiguës, C3) |
| 06 Shazam 34 arbres | Drive `1KshgP97…` | texte d'assistant | pseudo-code de hachage spectral | une implémentation |
| `docs/EDUCATION.md` | `obsidia-x108-proofs@main` `48f0c2fb` | synthèse d'assistant (2026-09-15) | doctrine « une seule naissance », entraînement ≠ éducation | une preuve de runtime éducatif |
| Branche `exp/p2-multirepresentation-ablation-20261009` | `brody-world-physique` `966df622` | code + docs expérimentaux | P155 reproduit ; P156 contrôles reproduits ; G1 tests 3/3 | apprentissage persistant, transfert, authenticité, multi-session |

## III.3 Versions 9×9 — distinctions (C5)

| Notion | Ce que disent les sources | Attribution |
|---|---|---|
| **Paradigmes d'entraînement** (couche 1) et **modes de traitement / « cerveaux »** (couche 2 : token, diffusif, quantique, symbolique…) | « la couche 1 et 2, c'est toutes les manières que je vais entraîner » | fondateur, 05 L2475 |
| **Versions expérimentales entraînées** (couche 3) | « 9x9 … 90 versions d'Obsidio » ; « ils vont apprendre de tout et de chaque mode … plus de 90 versions » | fondateur, 05 L2475, L2678 |
| **Non-coopération entre versions** | « Tous les cerveaux dans le cerveau peuvent coopérer mais pas les versions d'Obsidia entre elles » ; « j'entraîne les différentes versions … avec des versions de cerveau différent » | fondateur, 05 L1919, L1922 (correction explicite à l'assistant) |
| Vocabulaire d'identité | « une entité ces token cerveau » (une occurrence) | fondateur, 05 L1795 — ambigu |
| « Entité Obsidienne distincte », « plusieurs Obsidia séparées », « version consciente spécialisée », « 81+ entités singulières » | — | **ChatGPT**, 05 L2022, L2059, L2147 ; 02 L274 |
| **Continuité identitaire** (une seule naissance) | « Une seule naissance. Une seule continuité éducative. Une multiplicité d'organes entraînés » | audit d'assistant rapportant une doctrine du 5 août 2026 (04 L4071) ; `EDUCATION.md` |

**Lecture v3 :** chez le fondateur, les versions sont des configurations entraînées séparément, sans coopération ; il ne dit ni qu'elles sont des identités, ni qu'elles sont de simples configurations d'une identité unique. **Ambiguïté historique**, à trancher par le fondateur. La seule opposition nette est entre le vocabulaire de ChatGPT (« entités », « consciente ») et la doctrine ultérieure « une seule naissance ».

## III.4 Constatations vérifiées

- Intégrité du pack : zip et 17 empreintes conformes (vérifié deux fois, dont par l'auditeur).
- Vision éducative du fondateur : école, évaluation, progression anti-dérive, apprentissage par l'échec, enseignement adaptatif, auto-analyse et compte rendu humain, fidélité à la source, garde-fous symboliques contre la dérive.
- Stades enfant / adolescent / adulte : **`NOT_DEFINED`** pour l'IA ou Oxygen, chez le fondateur comme chez l'assistant ; « enfants » chez le fondateur = public d'un jeu (05 L457).
- Parité GitHub / local : conforme au tableau II.5 (cinq artefacts identiques `main` = AGY = local ; adaptateur Pack V1 divergent ; `EDUCATION.md` seulement sur `main`).
- Conflits de contrats Claude / AGY : 6/6 confirmés.

## III.5 Limites scientifiques

| Élément | Statut v3 |
|---|---|
| P155 | `RESULTS_REPRODUCED=YES` ; `SCOPE=SYNTHETIC` ; même distribution pour cours, retour, validation et examen ; garde de rétention active une seule fois |
| P156 | `CUMULATIVE_RETENTION=PARTIAL` ; `FROZEN_BASELINE_WINS_ON_6_OF_24_TASKS=YES` ; `NO_FORGETTING_GUARANTEE=NO` |
| G1 | `CONTENT_HASH=YES` ; `AUTHENTICITY_PROVEN=NO` ; `INDEPENDENT_PROCESS_RESTART_PROVEN=NO` ; `MULTI_DAY_CONTINUITY_PROVEN=NO` |
| `KX108_ONLY` dans les artefacts | **étiquette littérale** ; ne prouve pas un passage effectif par le noyau |
| Mémoire | candidate expérimentale (scalaires synthétiques) ≠ acquis validé ≠ capacité transférable (non prouvée) ≠ continuité éducative (non prouvée) ≠ promotion canonique (absente) ≠ autorité (KX108) |

Niveaux à ne pas confondre : reconstitution historique ≠ formalisation pédagogique ≠ prototype expérimental ≠ intégration runtime ≠ apprentissage persistant démontré ≠ capacité ≠ autorité.

## III.6 Questions encore ouvertes

1. Les occurrences « oxygène / Oxygen » de 05 L2003 et L2673 désignent-elles Oxygen ou sont-elles une transcription d'« Obsidia » ?
2. Les versions 9×9 sont-elles des entraînements d'une même continuité, ou des entités distinctes ?
3. Faut-il des stades enfant / adolescent / adulte, des niveaux de compétence, ou autre chose ? (« Enfance → Maîtrise → Sagesse » n'est qu'une mention d'assistant.)
4. Quel acte et quel critère pour la « naissance » d'Oxygen ?
5. Quelle forme pour le compte rendu humain des « journées » (05 L1320) ?
6. Où sont la conversation du jeu éducatif, les archives Gmail et les sources 47 / 48 / 91 ?

## III.7 Statut de préconception

```
REPORT_VERSION=V3
FORENSIC_STATUS=PARTIAL
C1_C9_CORRECTED=YES
FSO_ORIGIN=FOUNDER_VISION / ASSISTANT_FORMALIZATION_AND_ACRONYM
OXYGEN_OCCURRENCES_IN_05=AMBIGUOUS
NINE_BY_NINE=HISTORICAL_AMBIGUITY (versions entraînées séparément ; identité non tranchée)
CHILD_TEEN_ADULT=NOT_DEFINED
P155=REPRODUCED / SYNTHETIC
P156=PARTIAL_RETENTION / FROZEN_WINS_6_OF_24
G1=CONTENT_HASH_ONLY / NO_AUTHENTICITY / NO_INDEPENDENT_RESTART / NO_MULTI_DAY
PERSISTENT_LEARNING_PROVEN=NO
READY_FOR_CONCEPTUAL_PRECONCEPTION=NO (questions III.6 à trancher par le fondateur)
READY_FOR_RUNTIME_INTEGRATION=NO
```

STOP BEFORE APPLY sur l'architecture éducative.
