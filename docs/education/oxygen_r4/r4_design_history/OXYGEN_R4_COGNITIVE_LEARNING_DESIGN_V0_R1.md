# Oxygen — conception R4 « apprentissage cognitif » V0 — révision R1 (conception seule)

R1 intègre la relecture indépendante (APPROVE_WITH_CHANGES) : B1 corrigé (clé de concept), NB1, NB2, NB4, NB5 et NB6 intégrés. NB3 est **contesté avec preuve** : `PredicateUnit.objects: tuple[Argument, ...]` existe (`app/semantic/lattice/primitives.py:157`). R0 est conservée à côté.

**Date :** 2026-10-22 · **Auteur :** Claude, **contaminé** (a lu les examens de développement ; ne les relit pas ici) · **Statut :** conception de recherche, **non canonique, non FREEZE**, aucun code.
**Base :** réconciliation V0.1 (auditée PASS_WITH_NB, sha256 `ffe3262e…`). V0 figé (`dfef4f98`). Prospective V0 en HOLD_INDEPENDENCE.

**Garde-fous :**
- aucune règle propre à F1–F7 ;
- aucun examen ;
- aucune donnée d'examen utilisée pour concevoir ou régler.

Les sens F1–F7 n'apparaissent ici que comme **étiquettes opaques** fournies par l'enseignant.

## 0. Nouveaux constats (sondes en lecture seule sur les données d'enseignement)

| # | Sonde | Résultat | Conséquence |
|---|---|---|---|
| N1 | SENS `parse_utterance` sur les 18 phrases d'enseignement de « force » | **2 phrases sur 18** produisent une unité de prédicat ; 0 ambiguïté signalée | SENS est construit pour des énoncés de gouvernance (lexique fermé de verbes à poids d'autorité). **Ce n'est pas une représentation exploitable des phrases pédagogiques** sans extension. |
| N2 | OS Trad `calibrate_lexical_knownness` sur une phrase d'enseignement | `known_concept_ids = []` ; tous les mots sont en `unknowns` ; source `REVERSE_OS_INTERLANGUAGE_CANON_V1` (vocabulaire IR / gouvernance) | **Correction de V0.1 §1** : ce calibrateur **ne sert pas** de signal « mot connu » pour le français courant. |
| N3 | corpus lexical `periphery/language/lexical_corpus.py` | base de 530 Mo : 663 134 lemmes, 307 892 sens (Littré, OEWN, thésaurus, gloses bilingues). **54 sur 54** mots de contenu de l'enseignement sont connus (mots de contenu = `tests/education_pilot/_bench.content_words`, liste `STOP` du banc, hors mot cible ; avec une autre liste de mots vides, le relecteur trouve 57 sur 57). 17 entrées de sens ou de synonymes pour « force » | c'est la **seule ressource existante** qui apporte une connaissance lexicale préalable. Elle répond directement à la limite principale de V0 (mots inconnus des leçons). |

N3 change la **nature** de ce qui serait démontré. Avec le corpus, l'élève n'apprend plus « à partir de rien ». Il apprend à **relier** l'enseignement à un lexique préalable. Ce choix est cohérent avec un apprenant humain, qui a déjà un vocabulaire, mais c'est une **décision du fondateur** (voir §8).

## A. Représentation du sens

Une occurrence du mot cible est représentée par un **enregistrement stratifié**. Chaque couche porte un **statut épistémique** :

| Statut | Signification |
|---|---|
| OBSERVATION | extrait du texte |
| HYPOTHÈSE | inférée par l'élève |
| VALIDÉ_ENSEIGNANT | étiquette ou correction reçue |

Rien n'est jamais promu au-delà de cette mémoire locale.

| Couche | Contenu | Source | Statut |
|---|---|---|---|
| Forme | lemme, forme, nombre et genre, catégorie | `lexical_corpus.lookup_surface_form` (analyses morphologiques) | OBSERVATION |
| Construction | schéma autour de la cible : préposition gouvernante (`de N`, `à N de`), déterminant, quantification, complément de nom, place dans la phrase | extracteur générique (comme V0, sans morceaux de mots comme trait principal) | OBSERVATION |
| Concepts voisins | pour chaque mot plein voisin : son **voisinage lexical** = l'ensemble des **lemmes** cités dans ses entrées `synonym_group` du corpus, plus le lemme lui-même (**clé de concept, B1**). Les `sense_id` sont propres à chaque lemme et **ne servent pas** de clé partagée. | corpus | OBSERVATION, avec la mention « ressource externe, `verified_fact = False` » |
| Sens candidats de la cible | groupes de sens du corpus pour le lemme cible | corpus | HYPOTHÈSE, jamais une réponse |
| Relations | relations typées et génériques cible ↔ voisins : `gouverne`, `quantifié_par`, `complément_de` ; nombre et détermination de la cible comme **traits de forme**, non comme relation nommée (NB2 : la relation `agent_collectif` de R0 est retirée, trop proche d'un motif de leçon) ; polarité | extracteur ; **SENS** quand il produit une unité (2 / 18 : optionnel, jamais requis) | OBSERVATION |
| Domaine | étiquette de domaine reçue avec la leçon ; aucune inférence de domaine sans preuve | enseignant | VALIDÉ_ENSEIGNANT |
| Temporalité | **deux axes distincts** : révision d'apprentissage (quand l'élève l'a appris) et intervalle de validité (quand c'est vrai, concept de B8 `ValidTimeInterval`) ; aucune horloge universelle | élève | — |
| Contradiction | paires « A, pas B » issues des corrections ; statut `CONTESTÉ` / `REMPLACÉ` (vocabulaire des états B8) | corrections | VALIDÉ_ENSEIGNANT |
| Provenance | identifiants des items enseignés et des concepts du corpus mobilisés | élève | — |
| Incertitude | probabilité **calibrée**, plus un **motif** d'abstention (`MOT_INCONNU`, `PREUVE_INSUFFISANTE`, `CONFLIT`) | §C | — |

**Exemple sans règle propre à un sens (NB1, remplace l'exemple de R0, calqué sur une leçon et faux sur le corpus) :** soit un mot cible X, une leçon « … X … voisin *v1* … » étiquetée L, et une question « … X … voisin *v2* … », où *v2* n'apparaît dans aucune leçon. Si les voisinages lexicaux de *v1* et *v2* se recouvrent dans le corpus (un lemme commun dans leurs groupes de synonymes), la question reçoit une preuve en faveur de L, citée en provenance (*v1*, *v2*, lemme commun). Sinon, cette classe de preuve est muette. Aucun mot ni sens n'est codé.

**Contrats existants, sans supposer leur compatibilité :**

| Composant | Contrat exact | Adaptation nécessaire |
|---|---|---|
| SENS | `parse_utterance(raw) → UtteranceFrame` (`units: PredicateUnit[]` avec `predicate`, `lemma`, `polarity`, `objects: Argument[]` ; `ambiguities`, `contradictions`, `evidence_needs`) ; `SemanticFrame` (`entities`, `relations` avec `polarity`, `unknowns`, `contradictions`). **Scellé.** | aucune modification possible. Usage : (a) **schéma d'inspiration** pour la couche relations (sujet, prédicat, objet, polarité), (b) trait optionnel quand une unité existe. Exécution : le conteneur ne voit pas `app/`. Il faudrait une **copie vendorisée en lecture seule**, montée dans `/extra` avec empreinte, ce qui demande une décision (code scellé copié, non modifié). |
| Corpus lexical | `lookup_surface_form(form, lang) → LinguisticAnalysis[]` ; `get_senses_and_synonyms(lemma, lang) → SenseDefinition[]` (`sense_id`, `kind`, `synonyms`, `definition`, `verified_fact = False`) ; `is_known_lexical_item(word, lang)` ; base SQLite `data/linguistic_corpus/lexicon.db` (`DB_PATH` relatif au dépôt, `lexical_corpus.py:31`) | monter un **export figé** (base entière, ou sous-ensemble produit par **règle mécanique** : par exemple les entrées de tous les lemmes d'un dictionnaire de formes, jamais une liste choisie à la main) en lecture seule dans `/extra`, avec empreinte. **Lecteur (NB5)** : un lecteur propre à l'élève, en bibliothèque standard, qui ouvre la base en SQLite `file:…?mode=ro&immutable=1` (le module du dépôt n'est pas importable dans le conteneur, et son `DB_PATH` y est invalide). Le banc RED le permet déjà (`OXYGEN_PILOT_STUDENT_PATH`) **sans changer le protocole** : l'examinateur n'envoie toujours que `(mot, phrase)`. |
| OS Trad | `_risk_flags`, `_intent` (mots-clés de gouvernance) ; `calibrate_lexical_knownness` (vocabulaire IR) | **non réutilisable** pour le sens lexical (N2) |

## B. Apprentissage et correction

**Modèle :** un « concept enseigné » est l'étiquette opaque de l'enseignant. Il est relié à trois éléments :
1. ses **exemplaires** (comme V0) ;
2. un **profil de constructions** ;
3. un **profil d'alignement** sur les concepts du corpus, pour la cible et pour les voisins.

| Capacité | Mécanisme | Compréhension ou mémoire |
|---|---|---|
| 1. Acquérir un sens à partir d'exemples | créer le concept à la première leçon étiquetée ; profils initialisés par l'exemplaire | mémoire et début de compréhension |
| 2. Relier plusieurs exemples à un concept | profils agrégés ; **voisinages lexicaux qui se recouvrent** entre exemplaires (deux leçons différentes dont les voisins partagent un lemme de synonymes, règle mécanique figée) | **compréhension** : regroupement au-delà de la surface |
| 3. Distinguer des sens proches | **contrastes** : chaque correction « A, pas B » renforce les traits qui séparent A de B (apprentissage discriminant par paires), par une **règle générique de négation**, figée et testée unitairement (réouverture explicite de la règle B3 de V0) | **compréhension** |
| 4. Corriger sans effacer | journal en ajout seul ; statuts `ACTIF` / `CONTESTÉ` / `REMPLACÉ` ; `history` = `retrieve(as_of)` (V0) | mémoire |
| 5. Reconnaître une situation hors connaissance | motifs d'abstention typés ; `MOT_INCONNU` si un voisin déterminant est inconnu **du corpus**, `PREUVE_INSUFFISANTE` si le support est trop faible, `CONFLIT` si deux concepts sont soutenus par des preuves indépendantes | **compréhension de ses limites** |
| 6. Conserver après redémarrage | état canonique en fichier unique, sha256 (V0), plus l'empreinte de la ressource externe | mémoire |
| 7. Transférer vers un contexte inédit | les profils portent sur des **voisinages lexicaux**, pas sur des mots : un voisin jamais vu en leçon mais dont le voisinage recouvre celui d'un voisin enseigné transmet le signal. **Non démontré** : la densité réelle des recouvrements est à mesurer sur l'enseignement seul (test unitaire), avant tout RED | **compréhension**, si l'ablation le confirme |

**Les sept familles de recherche conservées :**

| Famille | Statut |
|---|---|
| 1 Exemplaires et relations | intégrée (exemplaires + relations typées) |
| 2 Concepts | intégrée (alignement sur le corpus) |
| 3 Correction | intégrée (contrastes) |
| 4 Cumul | intégrée (statuts) |
| 5 Récupération multi-axes | intégrée (deux axes temporels) |
| 6 Erreurs | intégrée : les erreurs de l'élève en exercice sont gardées comme **exemples négatifs** de la paire confondue |
| 7 Calibration | §C |

## C. Calibration (sans aucune réponse d'examen)

| Limite de V0 | Mécanisme R4 |
|---|---|
| Dominance bayésienne (écart 1,42 contre 0,11) | **pas de somme de log-probabilités par trait**. Le score est un **vote de preuves par classe** : construction, concepts voisins, alignement de la cible, exemplaires. Chaque classe produit au plus **une** voix, normalisée dans [0, 1], et les classes sont combinées avec des poids **fixés a priori** et égaux. Aucune classe ne peut écraser les autres par son nombre de traits. |
| Traits bruyants (11 morceaux de mots sur ~26) | les morceaux de mots ne servent plus qu'à l'**appariement morphologique** (retrouver le lemme dans le corpus), pas comme preuve de sens |
| Peu d'exemples | **rétrécissement** vers l'incertitude : la confiance d'un concept croît avec le nombre d'exemplaires et de classes concordantes (lissage fixé a priori, par exemple n / (n + 2)) |
| Erreurs assurées (6 / 18 en leave-one-out) | réponse seulement si **au moins deux classes indépendantes** concordent **et** si le risque estimé est sous le seuil |
| Abstentions excessives | abstention **typée** : distinguer « mot inconnu » de « conflit » permet de ne pas s'abstenir quand la construction seule est décisive (« à force de ») |
| Réglage | température ou seuil **fixés a priori**. Le leave-one-out sur l'enseignement est rapporté **en vérification seulement**, jamais pour régler (règle de R3). |

**Gouvernance :**
- la confiance de l'élève est une **mesure interne**, jamais une vérité du sens ;
- sigma reste consultatif ;
- GuardX108 garde sa frontière ;
- **KX108_ONLY** reste l'autorité de décision.

L'élève ne décide rien hors de sa mémoire expérimentale.

## D. Patrimoine Obsidia

Statut le plus avancé atteint par chaque mécanisme : VISION, SPEC, CODE, TEST, RUNTIME (appelé sur Brody) ou NON PROUVÉ (utile au sens lexical sans preuve).

| Mécanisme | Statut | Existe | Appelé | Réutilisable pour R4 | Raccord nécessaire | Manque réel |
|---|---|---|---|---|---|---|
| SENS | RUNTIME (Brody), TEST | frames, unités de prédicat, polarité, ambiguïtés, contradictions | oui (Brody) | schéma de relations ; trait optionnel (2 / 18) | copie vendorisée dans `/extra` (décision) | couverture des phrases non gouvernementales |
| OS Trad | RUNTIME partiel (intention et risque, mode par défaut), TEST | routes, classifieurs, calibrateur IR | oui (intention et risque) | **aucun** pour le sens (N2) | — | sens lexical |
| Corpus lexical | CODE ; **RUNTIME non tracé** (NB4 : seul appelant dans `app` + `periphery` : `periphery/language/native_realization.py`) | 663 k lemmes, 307 k sens | non démontré | **oui** : formes, concepts, connaissance des mots | export figé dans `/extra` | aucun lien sens ↔ leçon (à apprendre) |
| AVDR | CODE (mappeur), TEST, Lean définitionnel, VISION (canon) | phases à seuils | non (inactif) | **NON PROUVÉ** ; au mieux un vocabulaire de phases d'apprentissage | — | — |
| Continuum | partiel (session, résumé temporel) | snapshots | oui (Brody) | non (l'élève a son propre journal) | — | mémoire des transformations |
| Native Memory | RUNTIME, lecture seule, sans dates | 3 267 enregistrements | oui | **non** (risque de source cachée) | — | dimension temporelle |
| B8 | CODE, TEST, isolé | états, validité, supersession | non | **concepts** (statuts, validité) | aucun | — |
| B9 | CODE, TEST, isolé | chemins cognitifs | non | concept de trace de raisonnement (explication de réponse) | aucun | — |
| B10 | CODE, TEST, isolé | révisions par slot | non | concept « à la révision r » (déjà dans V0) | aucun | authenticité (invariant séparé) |
| 34 arbres | RUNTIME (signal R^34) | activation par requête | oui | **NON PROUVÉ** : un trait optionnel, à tester par ablation | copie vendorisée ou pré-calcul : un pré-calcul hôte des phrases d'examen **changerait le protocole**, donc vendorisation seulement | lien arbres ↔ sens |
| MMonde | CODE (M41 V1 clos), non intégré | modèle du monde | à la demande | non (Option A : pas d'import) | décision du fondateur | — |
| Frise historique humaine | VISION | — | — | non | — | **absente** |
| Chronologie éducative d'Oxygen | VISION | — | — | le journal par révisions de l'élève en est un **analogue local**, pas la chronologie d'Oxygen | — | absente |
| Domaines spécialisés | CODE (`memory_world_mapper`) | contrat de domaine | oui | l'étiquette de domaine reste fournie par l'enseignant | — | domaine ↔ sens |

**Ne pas confondre :**
- la frise **humaine** est le temps du monde ;
- la chronologie **éducative** est le temps d'apprentissage d'Oxygen ;
- les 34 **arbres** sont des axes cognitifs ;
- les **domaines** sont des champs d'application.

Une couverture documentaire n'est pas une intégration.

## E. Architectures candidates

| Critère | A. V0 amélioré (exemplaires + calibration) | B. Relationnelle et compositionnelle, sans ressource externe | C. Hybride : exemplaires + relations + alignement sur le corpus lexical (+ SENS optionnel) |
|---|---|---|---|
| Généralisation (mots inconnus des leçons) | faible : seule la construction transfère | moyenne : les relations transfèrent, pas le vocabulaire | **la meilleure attendue** : les concepts du corpus transfèrent |
| Peu d'exemples | moyenne | moyenne | **la meilleure attendue** : le lexique préalable compense |
| Correction | contrastes possibles | contrastes naturels | contrastes plus alignement |
| Rétention | identique (état canonique) | identique | identique, plus l'empreinte de la ressource |
| Abstention | calibrée | calibrée et typée | calibrée, typée, plus `MOT_INCONNU` fondé sur le corpus |
| Coût | faible | moyen | **élevé** : 530 Mo ou un sous-ensemble à figer, temps de démarrage du conteneur |
| Complexité | faible | moyenne | élevée |
| Réutilisation Obsidia | faible | faible (concepts B8) | **élevée** : corpus, SENS (option), concepts B8 / B10 |
| Traçabilité | bonne | bonne | bonne si chaque concept du corpus mobilisé figure dans la provenance |
| Risque de contamination | faible | faible | **élevé** : la ressource pourrait contenir des phrases d'examen (exemples Littré) ; sous-ensemble choisi par l'auteur contaminé |
| Ce qui serait démontré | meilleur usage des leçons | relations apprises | **usage des leçons pour s'aligner sur un lexique préalable** |

**Candidat préféré : C**, sous conditions. Le choix n'est pas motivé par la facilité (C est le plus coûteux) : C est le seul qui traite la limite principale démontrée, les mots inconnus des leçons.

| Condition | Contenu |
|---|---|
| (i) | décision du fondateur sur l'usage d'un lexique préalable (§8) |
| (ii) | ressource **entière ou sélectionnée par règle mécanique**, jamais à la main par l'auteur contaminé ; empreinte figée **avant** la rédaction de tout jeu prospectif |
| (iii) | **contrôle de fragments** : aucune phrase d'examen (jeu de développement **et** futur jeu indépendant) dans la ressource ; c'est l'opérateur qui le vérifie |
| (iv) | **ablations obligatoires** : C sans corpus (≈ B), C sans contrastes, C sans SENS |

**A** reste la **référence de contrôle** : si C ne dépasse pas A, le corpus n'apporte rien.

## F. Évaluation future (aucun examen fabriqué)

**Hypothèses réfutables :**

| # | Hypothèse | Épreuve | Échec honnête |
|---|---|---|---|
| H1 | le vote par classes réduit les erreurs assurées | leave-one-out sur l'**enseignement** (tests unitaires) : moins de 6 / 18 erreurs non abstenues, sans perte de justes | si les erreurs ne baissent pas, la calibration est réfutée |
| H2 | C dépasse la meilleure ligne de base avec la marge sur T1 et X1-far | prospective indépendante | égalité ou moins |
| H3 | le gain vient du lexique préalable | ablation C sans corpus sur le même jeu | si C sans corpus ≈ C, le corpus est inutile |
| H4 | les contrastes améliorent les sens proches | ablation sans contrastes | aucune différence |
| H5 | abstention : HOLD injustifié ≤ 0,2 et approprié ≥ 0,5 | prospective | dépassement |
| H6 | rétention et révisions intactes | tests d'interface existants (non probants pour l'apprentissage) | régression |

**Couches d'évaluation, toujours séparées :**
1. **tests unitaires** sur l'enseignement seul ;
2. **banc RED V0.3**, développement : il vérifie seulement la mécanique, puisque ses examens sont contaminés ;
3. **comparaison V0 / R4** sur le **même** jeu indépendant, chacun en un seul passage ;
4. **prospective indépendante** : rédacteur et opérateur humains ;
5. **campagne scientifique** : au moins 20 items par sens, statistiques pré-enregistrées.

V0 reste intact et sert de référence.

## G. Frontière mémoire

Identique à V0 : uniquement une mémoire expérimentale locale dans `/state`.

**Non concernés :**
- aucune mémoire candidate B8, aucune connaissance validée, aucune promotion ;
- aucune écriture Native Memory ;
- aucune écriture B10.

La ressource lexicale est montée **en lecture seule** et marquée `verified_fact = False` : elle sert de référence, pas de vérité. Sauvegarder un état d'élève n'est pas la naissance d'Oxygen.

## Lacunes de preuve

1. Le corpus porte-t-il réellement l'information utile ? C'est non démontré ; H3 le testera. **Avant tout RED**, un test unitaire sur l'enseignement seul mesurera combien de paires de voisins de leçons ont des voisinages lexicaux qui se recouvrent. Si c'est quasi nul, le mécanisme de transfert de C est réfuté d'avance.
2. Les phrases d'examen sont-elles absentes du corpus ? C'est non vérifié ; c'est le contrôle (iii), à la charge de l'opérateur.
3. Une règle générique de négation peut-elle lire les corrections de façon fiable ? C'est non démontré.
4. La couverture de SENS sur des phrases pédagogiques est de 2 / 18 : son apport est probablement négligeable.
5. Il faut une trace **dynamique** de Brody pour confirmer l'usage du corpus en runtime : le crosswalk dit qu'il y est appelé, sans trace dans cette passe.
6. Copies des sources dans d'autres dépôts : toujours SOURCE_NOT_VERIFIED.

## 8. Décisions du fondateur (une à la fois)

1. **Lexique préalable : oui ou non ?** C'est la décision qui conditionne C. Avec le corpus, Oxygen apprend à relier des leçons à un vocabulaire déjà présent. Sans lui, R4 se limite à A ou B.
2. Vendoriser une copie en lecture seule de SENS pour le conteneur, en option.
3. Désigner un rédacteur et un opérateur humains (préalable de toute prospective).
