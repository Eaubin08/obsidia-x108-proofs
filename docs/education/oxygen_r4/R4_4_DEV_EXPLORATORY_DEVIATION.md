# R4.4 DEV-EXPLORATORY — Déviation documentée (Premier incrément P5-L2)

**Statut :** DEV_EXPLORATORY — PREMIER_INCREMENT_P5L2
**Date :** 2026-10-23
**Commit de base :** bde60c37 (pré-enregistrement V1 + addendum A1)
**Autorisation :** DEV_EXPLORATORY_PHASE_1=GO (message utilisateur du 2026-10-23)

---

## 1. Périmètre de cet incrément

Ce document consigne, avant toute modification du moteur, les déviations introduites dans
`r4_core_student.py` pour le premier incrément cohérent de P5-L2.

**Ce qui est implémenté dans cet incrément :**
- Suivi de la provenance réelle par événement pédagogique (révision source).
- Identité de l'événement source par item (`_source_event`).
- Vérification de l'indépendance au niveau de l'événement (pas seulement de l'item).
- Prévention du double comptage : deux observations issues du même appel `learn()` ne
  comptent pas comme deux confirmations indépendantes.
- Détection de la paire de dispositifs (constructions + exemplaires) avec argmax distincts
  et événements sources disjoints → CORROBORATION_NIVEAU_2 (`_p5l2_satisfied`).

**Ce qui est intentionnellement omis de cet incrément :**
- Déviations C1-D1/D2 (seuils P3 par classe) : spécification uniquement, non implémentée.
- P5-L3 (triple-concordance K1/K3/K5) : HOLD — dépend de P_ALIGN (K1).
- G5b (K4 confiance) : HOLD — sans objet sous option C.
- Calibration R4.4 et ajustement de seuils : CALIBRATION_TUNING=NO.
- RED V0.3 : PRIVATE_RED_ACCESS=NO.

---

## 2. Contrats modifiés

### 2.1 `_evidence` — signature étendue

**Avant :** retourne `(classes, labels, active)` (3-tuple)
**Après :** retourne `(classes, labels, active, event_classes)` (4-tuple)

`event_classes` = `{nom_de_classe: {L: frozenset({révision_de_l'argmax})}}`

Justification : sans la révision de l'argmax, il est impossible de détecter si
constructions et exemplaires désignent le même événement pédagogique.

### 2.2 `_independent_pair` — paramètre `event_of` optionnel

**Avant :** vérifie uniquement la disjonction des identifiants d'item (provenance item-level).
**Après :** si `event_of` fourni, vérifie aussi la disjonction des révisions sources.

Impact sur le comportement : deux items distincts issus du même appel `learn()` ne
satisfont plus le critère d'indépendance si `event_of` est passé.

### 2.3 Nouveau : `_source_event(d, item_id)`

Retourne la révision de l'événement ayant introduit `item_id` dans le dérivé `d`.
Source : `d["items"][item_id]["revision"]`.

### 2.4 Nouveau : `_p5l2_satisfied(conc, classes, event_classes)`

Itère sur les étiquettes concordantes. Pour chaque étiquette L :
1. Vérifie que "constructions" ET "exemplaires" sont tous deux concordants sur L.
2. Vérifie que leurs argmax sont des items distincts (prov_c ∩ prov_e = ∅).
3. Vérifie que leurs événements sources sont disjoints (ev_c ∩ ev_e = ∅).

Si toutes les conditions sont satisfaites : retourne `(L, entrées)`.
Sinon : retourne `(None, [])`.

### 2.5 `answer` — nouveau chemin CORROBORATION_NIVEAU_2

Après le check CONFLIT (inchangé), et avant PREUVE_INSUFFISANTE :
appel de `_p5l2_satisfied`. Si satisfait, émet une réponse avec `origin =
"CORROBORATION_NIVEAU_2"` et `exploratory = True`.

L'indépendance dans le chemin existant (`indep`) est renforcée : `event_of` est passé
à `_independent_pair`, ce qui renforce (sans changer la sémantique contractuelle) le
critère d'indépendance.

---

## 3. Conditions d'émission CORROBORATION_NIVEAU_2

Une réponse `CORROBORATION_NIVEAU_2` est émise si et seulement si :
1. Pas de CONFLIT (inchangé).
2. Constructions concordantes sur L (voices[L] ≥ TAU, argmax unique).
3. Exemplaires concordants sur L (voices[L] ≥ TAU, argmax unique).
4. Argmax constructions ≠ argmax exemplaires (items distincts).
5. Révision source argmax constructions ≠ révision source argmax exemplaires.

**Ce qui n'est pas vérifié dans cet incrément (limitations) :**
- C2 (contre-preuve formelle F(t,¬L) ≥ 2) : non implémenté.
  La mécanique des contrastes existante filtre les cas les plus évidents, mais pas
  tous. C2 complet nécessiterait une table de fréquences par trait et par étiquette.
- Filtrage D1/D2 des traits non diagnostiques (C1 déviation).

---

## 4. Invariants préservés

- Les 27 tests existants (HEAD bde60c37) restent valides.
  Le seul test affecté en signature est `test_b4_contested_sentence_never_feeds_any_evidence_class`
  (décompactage 3→4 valeurs), sans changement de logique.
- P_ALIGN = HOLD : `_p5l2_satisfied` ne consulte jamais le lexique d'alignement.
- PRIVATE_RED_ACCESS = NO : aucun fichier RED V0.3 n'est lu.
- AGY_MUTATION = NO : aucune frontière d'autorité ni contrat KX108 modifié.
- PUSH=0 / MERGE=0 : commit local uniquement.

---

## 5. Traçabilité

| Élément | Valeur |
|---|---|
| Commit base | `bde60c37` |
| Branche | `feat/claude-linguistic-repair-m42-v0` |
| Pré-enregistrement | `docs/education/oxygen_r4/R4_4_PREREGISTRATION.md` (commit `0698b838` + A1 `bde60c37`) |
| Autorisation | Message utilisateur DEV_EXPLORATORY_PHASE_1=GO (2026-10-23) |
| Version de cet incrément | INCREMENT_P5L2_V1 |

---

*Ce document est figé avant toute modification du moteur. Il consigne les intentions,
non les résultats. La vérification a posteriori passe par les tests.*

---

## ADDENDUM V1.1 — 2026-10-24 (correctif après audit FAIL)

**Base :** `796cf371` (V1). **Audit :** `R4_4_P5L2_V1_CODE_AUDIT.md` (hors dépôt, SHA-256 `533a2914…8707`), verdict FAIL.
**Autorisation :** M1 à M5 = GO ; P5_L2_NEW_RESPONSE_AUTHORITY = NO.
Le texte V1 ci-dessus est conservé tel quel ; cet addendum le corrige.

### A.1 Omissions du document V1 relevées par l’audit

- Condition A1.1-2 du pré-enregistrement (témoins aveugles figés) non remplie lors du build V1 : la piste DEV-EXPLORATORY a été ouverte par décision opérateur, sans que ce document le consigne.
- Conditions §3.2 non vérifiées par V1 : 4–5 (P2, N_c/TP_c), 6 (contre-preuve), 7 (P3). STOP_CORROBORATION (§7) et RAPPEL (§3.8) absents. V1 émettait pourtant le code contractuel CORROBORATION_NIVEAU_2.
- V1 court-circuitait la porte historique (seuil agrégé TAU, marge DELTA, sélection TOP).
- V1 rendait l’origine ACQUIS_LECON inatteignable ; la §2.5 affirmait à tort « sans changer la sémantique contractuelle ».
- §1 : D1/D2 sont des déviations du filtre C1 (§3.6 du pré-enregistrement), et non des « seuils P3 par classe ».
- Message du commit V1 : « 27 baseline unchanged » est inexact (une ligne de `test_b4` modifiée ; 102 lignes du fichier de tests normalisées en CRLF).

### A.2 Corrections V1.1

| # | Changement | Effet |
|---|---|---|
| M1 | Suppression de la voie d’émission P5-L2 dans `answer()` ; schéma de réponse historique restauré (plus de clé `exploratory`) | P5-L2 n’a plus aucune autorité de réponse |
| M2 | `_evidence` : la provenance d’une classe devient l’ensemble des items ex æquo au maximum (plus de départage par identifiant) ; ses événements sont les révisions de cet ensemble | aucune réponse ne dépend de l’ordre des identifiants |
| M3 | `_device_dependency` : causes de dépendance de la paire constructions/exemplaires (ITEM_COMMUN, EVENEMENT_COMMUN, MEME_DOMAINE, MEME_REGISTRE, OBSERVATION_DERIVEE, SOURCE_AUTEUR_INCONNUS) ; une métadonnée absente compte comme partagée | la paire n’est jamais déclarée indépendante |
| M4 | `_p5l2_status` : statut interne provisoire à quatre niveaux (hypothèse, candidat, admissible, autorité de réponse) ; `admissible` et `response_authority` restent faux | CORROBORATION_NIVEAU_2 n’est plus utilisé |
| M5 | Cet addendum ; deux tests inexacts corrigés ; test positif V1 retiré | traçabilité |

### A.3 Effet annoncé sur la voie historique

- Le schéma des items ne porte ni auteur ni source : STOP_CORROBORATION ne peut jamais être exclu. En application de la règle « information manquante ⇒ pas d’indépendance », la paire constructions/exemplaires ne peut plus autoriser aucune réponse, ni par P5-L2 ni par la porte historique.
- Conséquence : `ACQUIS_LECON` est inatteignable ; `TRANSFERE` et `CORRIGE` restent atteignables par les paires incluant les contrastes, dont le comportement est inchangé.
- Contrôle par injection (graine 108, 20 000 tirages, items réels) : V1.1 ne répond jamais là où `bde60c37` s’abstient (0) ; quand les deux répondent, sens, origine et provenance sont identiques (0 écart). Réponses `bde60c37` perdues : ACQUIS_LECON 121 et TRANSFERE 107, toutes fondées sur la seule paire constructions/exemplaires. CORRIGE : 1 637/1 637 conservées.
- Données d’enseignement V0 (LOO structurel, transitions seulement) : 18/18 HOLD avant et après, en lot comme item par item.

### A.4 Points NOT_COVERED (contrat insuffisant pour trancher)

| Point | Comportement V1.1 | Décision requise |
|---|---|---|
| Auteur / source des items | absents du schéma → dépendance non résolue | contrat de provenance des items |
| Granularité d’événement (une leçon livrée en plusieurs `learn()`) | bloquée uniquement par la source inconnue | identifiant de leçon fourni par l’appelant, ou révision |
| Répétition d’un indice lexical entre dispositifs | jetons partagés exposés (`shared_cue_tokens`), sans règle de décision | règle de séparation des dispositifs |
| RAPPEL §3.8 | non implémenté ; un rappel n’est jamais corroboré (ensembles ex æquo) | implémentation à autoriser |
| Ré-enseignement d’un item sous le même identifiant | ignoré silencieusement (`setdefault`, préexistant) | règle de révision des items |
| Événement source des contrastes | non suivi ; contrôle d’événement vacant pour les paires avec contrastes | hors périmètre V1.1 |
| P2 (N_c/TP_c), contre-preuve, P3 | absents ; listés dans `missing_conditions` | incréments futurs |

### A.5 Tests

- V1 : 36/36 au commit `796cf371` (résultat conservé dans l’historique Git).
- V1.1 : 50 tests = 27 historiques inchangés depuis V1 + 6 tests V1 inchangés + 2 tests V1 corrigés et renommés + 15 tests V1.1 ; 1 test V1 retiré (il encodait comme attendue une configuration interdite par STOP_CORROBORATION).
- RED sur le moteur V1 : 15 échecs (10 comportementaux, 5 dus à l’API absente). GREEN après correctif : 50/50.
- Ces tests sont des tests de développement dérivés de scénarios consommés ; ils ne démontrent ni la conformité P5-L2 ni une calibration.

---

## ADDENDUM V1.2 — 2026-10-24 (provenance pédagogique et périmètre de M3)

**Base :** `da78b5c7`. **Décision :** PEDAGOGICAL_PROVENANCE = GO ; NEW_RESPONSE_AUTHORITY = NO ; M3 = correction de périmètre.

### B.1 Cause des 228 réponses historiques perdues (injection graine 108, sans vérité terrain)

| Condition appliquée à la voie historique | Introduite par | ACQUIS_LECON | TRANSFERE | Nature |
|---|---|---|---|---|
| même appel `learn()` (EVENEMENT_COMMUN) | V1 `796cf371` | 98 | 82 | règle de sécurité intentionnelle (V1 §2.2), plus stricte que K3 |
| `SOURCE_AUTEUR_INCONNUS` | V1.1 `da78b5c7` | 23 | 25 | changement de contrat : condition d’indépendance de source absente de K3 |

- Dans les 228 cas, l’ancien moteur répondait par la seule paire constructions/exemplaires, à items disjoints : K3 était satisfait au sens de R4.2.2.
- CORRIGE : 1 637 réponses identiques tirage par tirage, car les paires avec contraste ne sont jugées que par K3 (disjonction d’identifiants).
- La justesse des réponses perdues n’est pas établie (injection synthétique). Sur les données V0, aucune version ne répond : aucune perte réelle.

### B.2 Contrats relus

- K3 (R4.2.2) : indépendance = ensembles de provenance (items, corrections, groupes) disjoints ; aucune clause d’événement ni de source. Son exemple admet une provenance à plusieurs items, ce qui est cohérent avec M2.
- R4.4, contrat d’évidence §2.3 : le biais commun (même registre, auteur, domaine) est « impossible à détecter par la règle seule » ; il relève du contrôle de diversité à la rédaction du curriculum.
- R4.4 Niveau 2 (proposition C.6) déclare « même curriculum, même auteur » comme limite admise, alors que STOP_CORROBORATION (§7) en fait un arrêt : ambiguïté non tranchée.
- `it[4]` (domaine) est le domaine thématique du sens (constant par sens dans V0) et `it[5]` un registre de langue : aucun n’identifie une source.

### B.3 Carte des données de provenance

| Notion | Donnée réelle | Statut |
|---|---|---|
| observation | item `(id, mot, phrase, étiquette, domaine, registre)` ou correction `(id, exercice, texte)` | présente |
| événement d’enseignement | révision d’un appel `learn()` ou `apply_correction()` ; le banc livre un ensemble entier en un seul `learn()` | présente |
| trait dérivé | traits POS/NG/DET/SURF et lemmes, recalculés à la demande depuis la phrase | présente (non stockée) |
| dérivation explicite | correction → exercice ; contraste → {correction, exercice} | présente |
| leçon (regroupement) | aucun identifiant distinct de l’appel `learn()` | absente |
| source, auteur, enseignant, curriculum | aucun champ ; les ensembles `E` / `CONC` n’existent que côté banc | absente |
| leçon d’origine d’un exercice | non déclarée | absente |
| rappel (RAPPEL §3.8) | non implémenté ; `answer`, `retrieve` et `history` n’écrivent aucun événement | absent |

### B.4 Représentation interne V1.2 (aucune autorité nouvelle)

- `_observation_provenance` : observation_id, teaching_event_id, teaching_event_kind, lesson_id (`None`), source_id (`None`), derived_from (l’exercice pour une correction, `None` sinon). Aucune valeur n’est inventée.
- `_pair_relation` :
  - SAME_EVENT : item, événement ou parent connu partagés ;
  - UNKNOWN_DEPENDENCY : exercice reçu avec une correction, dont la leçon d’origine n’est pas déclarée ;
  - VERIFIED_INDEPENDENT_SOURCES : sources connues et disjointes ; jamais atteint, aucun source_id n’existe ;
  - DISTINCT_PEDAGOGICAL_EVENTS sinon : réplication pédagogique interne, pas indépendance.
- `_device_pair_is_independent` : prédicat unique de la porte historique pour la paire constructions/exemplaires ; politique active = VERIFIED_INDEPENDENT_SOURCES seulement.
- `_p5l2_status` expose `evidence_status`. Les causes STOP_CORROBORATION (`_device_dependency`) restent des diagnostics P5-L2 : la porte historique ne les lit plus.
- Réponses : identiques à V1.1 (20 000/20 000 tirages sur deux campagnes, 16 scénarios, données V0).

### B.5 Deux comportements côte à côte — décision HOLD

| | S (actif) | H (compatible K3, HOLD, simulé hors dépôt) |
|---|---|---|
| paire constructions/exemplaires | jamais indépendante sans source vérifiée | indépendante si DISTINCT_PEDAGOGICAL_EVENTS |
| paires avec contraste | K3 | K3 |
| injection cohérente (graine 108) | 3 503 réponses | 3 718 réponses = `bde60c37` (0 nouvelle, 0 différente) |
| ACQUIS_LECON | inatteignable | atteignable |
| scénarios réels qui répondent de nouveau | — | A2, C, C2, D, G2 (fausses corroborations relevées par l’audit V1) |
| scénarios qui restent HOLD | A, B, B2, H3, F, I, J, G-TAU, observation dérivée | idem |
| CORRIGE réel (paire avec contraste) | répond | répond |

H revient à accepter la réplication pédagogique interne comme indépendance K3. C’est une dérogation au contrat de sécurité V1.1 : elle n’est pas appliquée.

### B.6 Tests

- Les 50 tests V1.1 sont conservés sans modification ; 11 tests V1.2 ajoutés → 61/61.
- RED sur V1.1 : 11 échecs (10 dus à l’API absente ; 1 comportemental : la porte historique de V1.1 lisait les causes P5-L2).
- Régressions locales sans examens : 22/22.
