# Forensic éducatif Obsidia / Oxygen — rapport PARTIAL

**Date :** 2026-10-17 · **Auteur :** Claude (agent), worktree `obsidia-claude-linguistique`, branche `feat/claude-linguistic-repair-m42-v0`, HEAD de départ `4016db99` (non poussée).
**Statut : PARTIAL.** Ce n'est **pas** un audit complet. Les sources primaires Google Drive n'ont **pas** été lues directement par Claude ; elles sont seulement identifiées (§3.2, d'après un handoff utilisateur). Aucun code, aucune mémoire, aucune architecture éducative n'a été modifié ou proposé pour application.

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
