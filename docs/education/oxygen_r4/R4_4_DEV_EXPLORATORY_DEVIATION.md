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

---

## ADDENDUM V1.3 — 2026-10-24 (réception facultative de la provenance pédagogique)

**Base :** `a70e0efb`. **Décision fondateur :** S_STRICT conservé comme politique de réponse provisoire ; H_HISTORICAL = référence seulement ; PEDAGOGICAL_PROVENANCE_INCREMENT = GO ; aucune autorité de réponse nouvelle.

### C.1 Points d’entrée audités

| Étape | Identifiants | Création, conservation, perte |
|---|---|---|
| curriculum (`_pilot_data`, côté hôte) | item, correction, exercice visé ; ensembles `E` / `CONC` | aucune leçon, source ni auteur |
| banc (`Teacher.teach`, `Teacher.correct`) | items, corrections | un ensemble entier part en un seul `learn()` (14 leçons + 4 exercices) ; perte du nom d’ensemble et de tout regroupement en leçons |
| protocole (`runner.py`, `SandboxStudent`) | items, correction, exercice | commun à tous les élèves ; aucune métadonnée transportée |
| élève : `_add` | révision, type d’événement | la révision identifie une livraison, pas une leçon |
| élève : `_derive` | items et corrections par id | la première occurrence gagne ; les livraisons suivantes d’un même id étaient invisibles (désormais listées dans `occurrences`) |
| mémoire et inférence | ids d’items et de corrections, révisions | `retrieve`, `history`, journal et provenance de réponse inchangés |
| persistance | état complet | JSON canonique + SHA-256 ; replay = rederivation depuis les événements |

### C.2 Contrat de provenance pédagogique

| Champ | Sens | Origine |
|---|---|---|
| item_id | contenu enseigné (`it[0]`) ; pour une correction, l’exercice visé | données |
| observation_id | preuve : l’item (à sa première occurrence) ou la correction | données |
| teaching_event_id | révision de la première occurrence | événements |
| occurrences | toutes les livraisons de l’id ; une répétition n’ajoute ni observation ni source | événements |
| lesson_id | leçon logique | attestée par l’appelant ; jamais déduite d’un appel `learn()` ni d’un identifiant |
| source_id, author_id | source pédagogique, auteur | attestés seulement ; leur égalité est un diagnostic, leur différence ne prouve rien |
| derived_from | filiation déclarée (exercice → item source) ; correction → exercice | attestée ou données ; parcourue de façon transitive |
| evidence_status | relation entre deux ensembles de preuves | calculée |

Statuts :
- SAME_EVENT : identifiant, filiation ou leçon partagés ; ou même livraison sans que les deux côtés attestent des leçons distinctes ;
- UNKNOWN_DEPENDENCY : exercice reçu avec une correction, sans origine déclarée ;
- DISTINCT_PEDAGOGICAL_EVENTS : leçons attestées distinctes, ou livraisons distinctes sans lien connu (réplication pédagogique interne, pas indépendance) ;
- VERIFIED_INDEPENDENT_SOURCES : exige une attestation d’indépendance que le contrat ne définit pas ; jamais retourné.

Distinctions : l’identité d’une leçon est `lesson_id` ; une occurrence est la livraison d’un item ; une répétition est une nouvelle occurrence du même item (aucune observation nouvelle) ou un nouvel item de la même leçon (SAME_EVENT) ; une nouvelle leçon pédagogiquement distincte porte un `lesson_id` distinct attesté ; une source extérieure indépendante vérifiée n’est pas représentable aujourd’hui.

### C.3 Interface et sérialisation

- `learn(items, provenance=None)` et `apply_correction(correction, exercise, provenance=None)` : argument nommé facultatif, `provenance = {id: {lesson_id, source_id, author_id, derived_from}}`. Les clés sont limitées aux ids de l’événement ; la validation a lieu à la frontière (`ValueError`) ; `None` signifie inconnu.
- Stockage : clé facultative `provenance` dans l’événement, absente quand rien n’est attesté. Les états historiques restent identiques octet pour octet ; un état V1.3 est relu par V1.2 sans écart d’observation (clé ignorée).
- La provenance attestée à la première occurrence gouverne ; une attestation ultérieure pour un id déjà reçu reste dans le journal des événements sans être appliquée (même règle que pour le contenu).
- `runner.py` et `SandboxStudent` sont inchangés : dans le chemin du banc, aucune métadonnée n’atteint l’élève et toutes les observations restent inconnues. L’extension du protocole est proposée, non appliquée : le runner est commun à tous les élèves et `EmptyStudent.learn(items)` n’accepte aucun argument supplémentaire.
- Lecture interne : `_provenance_record` (contrat complet), `_observation_provenance` (vue V1.2 à clés stables), `_lineage`. La sortie publique de `retrieve` est inchangée.

### C.4 Effets vérifiés

- Réponses sous S : identiques à `a70e0efb` sur 16 scénarios (dont 7 avec métadonnées), sur 2 × 20 000 tirages à métadonnées synthétiques (graine 108) et sur les données V0. CORRIGE conservé.
- La branche automatique VERIFIED de V1.2 (sources connues et disjointes) est retirée : avec la réception des métadonnées, deux `source_id` distincts seraient devenus une preuve d’indépendance et, par S, une autorité de réponse.
- P5-L2 : `candidate` suit `evidence_status` (même leçon ⇒ non candidat). `SOURCE_AUTEUR_INCONNUS` est émis tant que source ou auteur manque ; MEME_LECON, MEME_SOURCE et MEME_AUTEUR le sont quand ces champs sont attestés et partagés. Toujours non admissible, sans autorité de réponse.
- Référence H (inactive) : les métadonnées la rendent plus stricte pour une même leçon répétée (M1 ; injection en quatre `learn()` : −46 réponses) et plus permissive pour deux leçons attestées dans un même appel (injection en un seul `learn()` : +6). Résidu : la porte historique conserve la règle de livraison V1 (`event_of`), inactive sous S, qui bloque encore M2 sous H.

### C.5 Restes NOT_COVERED

- Transport des métadonnées par le protocole du banc.
- Attestation d’indépendance des sources (qui vérifie, avec quel registre).
- Conflit entre attestations successives pour un même id : non signalé.
- Ré-enseignement sous le même id avec une autre étiquette (G2) : toujours ignoré.
- RAPPEL, P2 et P3 : non traités dans cette passe.

### C.6 Tests

- Les 61 tests existants sont conservés sans modification ; 12 tests V1.3 ajoutés → 73/73.
- RED sur V1.2 : 12 échecs, tous dus à l’API absente.
- Régressions locales sans examens : 22/22.

---

## ADDENDUM V1.4 — 2026-10-24 (transport de la provenance déclarée)

**Base :** `00f7a8f6`. **Décision :** PROVENANCE_TRANSPORT = GO ; BACKWARD_COMPATIBILITY = MANDATORY ; S actif ; H = référence ; aucune autorité de réponse nouvelle.

### D.1 Où la provenance se perdait

| Étape | Avant V1.4 | V1.4 |
|---|---|---|
| curriculum (`_pilot_data`) | aucune métadonnée | inchangé : aucune métadonnée réelle n’existe, aucune n’est créée |
| `Teacher.teach` / `Teacher.correct` | aucun paramètre de provenance | `provenance=None` facultatif, transmis seulement s’il est présent ; `correct` ne transmet à chaque correction que les entrées de cette correction et de son exercice |
| `SandboxStudent.learn` / `apply_correction` | messages `{op, items}` / `{op, correction, exercise}` | clé `provenance` ajoutée seulement si présente ; `provenance_delivered` exposé après chaque appel |
| `runner.py` (partagé) | n’appelait que `learn(items)` / `apply_correction(c, e)` | `_deliver` : la provenance n’est passée qu’à une méthode dont la signature déclare `provenance`, sinon l’appel historique est inchangé ; la réponse gagne `provenance_delivered` seulement si la requête portait une provenance |
| élève R4-Core | réception facultative (V1.3) | inchangé |

### D.2 Consommateurs du runner partagé

| Élève | Signatures | Effet de V1.4 |
|---|---|---|
| `EmptyStudent` | `learn(items)`, `apply_correction(correction, exercise)` | aucun : provenance non transmise, accusé `false` |
| `ExemplarSenseStudent` | idem | idem |
| `R4CoreStudent` | idem + `provenance=None` | reçoit la provenance, accusé `true` |
| `Probe` (généré par `test_pilot_force_controls`) | `probe()` seulement | aucun |
| `Sink` (hôte, `test_pilot_force_controls`) | `learn(items)`, `apply_correction(c, e)` | aucun : `Teacher` n’ajoute rien sans provenance |

Aucun élève n’est modifié.

### D.3 Contrat de transport

- Transportés, par id d’item ou de correction : lesson_id, source_id, author_id, derived_from (item_id = `it[0]` est déjà dans l’item).
- Calculés par l’élève, jamais transportés : teaching_event_id, occurrences, evidence_status.
- Trois niveaux distincts : métadonnée déclarée (seul niveau transporté) ; métadonnée vérifiée (aucun mécanisme) ; indépendance scientifiquement attestée (SOURCE_ATTESTATION = NOT_IMPLEMENTED).
- L’inconnu est préservé : aucun champ absent n’est complété ; lesson_id n’est jamais déduit d’un appel `learn()`.
- Aucun rattrapage de `TypeError` : une erreur interne d’un élève remonte telle quelle.

### D.4 Vérifications

- Protocole : transcriptions historiques identiques octet pour octet entre l’ancien et le nouveau runner pour les trois élèves ; avec provenance, seul l’accusé diffère.
- Chemin réel du banc (conteneur Docker, image épinglée, sans réseau), fixture synthétique : deux leçons dans un même appel, deux livraisons d’une même leçon, items sans provenance, correction avec filiation, deux source_id déclarés sans attestation. Les métadonnées sont retrouvées après sauvegarde, rechargement côté hôte et redémarrage du conteneur ; TP-A1 n’est compté qu’une fois (occurrences [1, 2]) ; aucune relation VERIFIED ; réponses identiques à la même fixture sans métadonnées.
- Curriculum pilote sans métadonnées : événements sans clé `provenance`, toutes les observations inconnues.
- CORRIGE conservé, avec ou sans métadonnées.
- Tests : 73 R4-Core + 22 régressions locales + 8 tests de transport → 103/103.

### D.5 Limites

- Aucune provenance réellement attestée n’existe dans le curriculum : la fixture est synthétique et ses métadonnées sont déclarées par le test.
- Les tests de bout en bout n’utilisent pas la fixture `new_student`, qui tue tous les conteneurs étiquetés ; ils sont ignorés si Docker est indisponible.
- Les tests pilotes du banc (`test_pilot_force_*`) ne sont pas exécutés (examens privés ou attente RED) ; leurs appels sans provenance sont inchangés.
- G2, RAPPEL, P2, P3 et l’attestation des sources restent hors périmètre.

---

## ADDENDUM V1.5 — 2026-10-24 (provenance réelle du curriculum historique V0)

**Base :** `91bbc626`. **Décision :** V15_REAL_PROVENANCE = GO ; source = V0 historique ; V0 non modifié ; S actif ; aucune autorité de réponse nouvelle.

### E.1 Source canonique V0

| Élément | Valeur |
|---|---|
| fichier | `tests/education_pilot/_pilot_data.py` |
| SHA-256 | `9dc3b41fc18326b102344a22e1f209e21ae0639993e7bab0b8c95b16953dbbac` (4 694 octets, LF) |
| historique | un seul commit, `00cc85fc` (2026-10-22, auteur Git Etienne Aubin) ; inchangé depuis |
| structure | `(item_id, word, sentence, expected, domain, register)` |
| contenu | 14 leçons, 4 exercices, 4 corrections, 4 leçons concurrentes, 1 contradiction ; ensembles `E` et `CONC` |
| usage par le banc | `Teacher.teach(E_LESSONS + E_EXERCISES)` en un seul appel, puis `Teacher.correct` (4 corrections) |

### E.2 Faits et affirmations

| Nature | Contenu | Preuve |
|---|---|---|
| fait du fichier | données expérimentales, non canoniques | `_pilot_data.py:1` |
| fait du fichier | inventaire des sens provisoire, à valider par un auteur humain ; aucun contenu de dictionnaire propriétaire | `_pilot_data.py:3-4` |
| fait du fichier | corrections dérivées uniquement d’exercices de E ; chaque correction cite son exercice | `_pilot_data.py:8`, `:53-58`, `:74` |
| fait du fichier | exercices tirés de l’ensemble E, sans parent au niveau de la leçon | `_pilot_data.py:45` |
| fait du fichier | aucun champ de leçon, de source ni d’auteur | `_pilot_data.py:10` |
| document tiers | E = « leçons du professeur » : un rôle, pas une identité | spec pilote V0, ligne 51 |
| document tiers | désignation des auteurs des leçons : décision à prendre ; aucune désignation consignée | spec pilote V0, ligne 144 |
| document tiers, non vérifié, non utilisé | gloses de correction écrites par l’auteur du contrat R4.2 (Claude) | contrat R4.2, ligne 72 |
| métadonnée Git | l’auteur du commit est l’auteur du dépôt de l’artefact, non attesté comme auteur pédagogique | `git 00cc85fc` |

### E.3 Manifeste

- `tests/education_pilot/pilot_v0_provenance_manifest.json` (SHA-256 `1de0beb2ae5260efb6092e6dee977e71ec2522773efaa10a7e970068405a5ca5`), généré à partir de V0 sans le modifier.
- L’identité de l’artefact (chemin, empreinte, commit) est tenue à part de la source pédagogique (source_id et author_id : UNKNOWN).
- Regroupements attestés : les cinq listes et les ensembles `E` / `CONC` ; un ensemble d’enseignement n’est pas une leçon.
- 27 observations : lesson_id, source_id et author_id inconnus partout ; derived_from attesté seulement pour les 5 corrections (exercice cité), avec la ligne exacte.
- Inconnues explicites avec leur motif ; affirmations non utilisées listées ; source_independence = NOT_ATTESTED.
- `tests/education_pilot/_pilot_provenance.py` : `load_manifest` refuse le manifeste si l’empreinte du curriculum diffère ; `declared_provenance` ne transmet que les champs attestés non nuls.

### E.4 Raccordement et vérifications

- Seul champ effectivement transporté : derived_from des 4 corrections enseignées (le lien porté par chaque correction, désormais déclaré par le manifeste). Aucun champ n’est transmis pour les items.
- Chemin réel du banc (conteneur Docker), V0 avec et sans manifeste :
  - réponses identiques (18 PREUVE_INSUFFISANTE + 4 MOT_INCONNU), y compris après redémarrage ;
  - accusé `true` sur les corrections ;
  - observations à leçon, source et auteur inconnus ;
  - teaching_event_id = 1 pour les 18 items : une livraison observée, pas une leçon ;
  - EX-F1 compté une seule fois (occurrences [1, 2]) ;
  - deux items de V0 sont SAME_EVENT par leur livraison commune, leur leçon restant inconnue ;
  - aucune autorité P5-L2.
- Leave-one-out sur V0 (18 items, en lot et item par item) : 0 divergence sur 36.
- Tests : 73 + 22 + 8 + 5 = 108/108.

### E.5 Limites

- V0 ne contient ni leçon, ni source, ni auteur attestés : aucune distinction leçon / livraison n’est démontrable sur V0 au-delà du repli par livraison.
- L’élève ignore de quel artefact viennent ses observations : la liaison artefact ↔ observations reste côté hôte (manifeste vérifié avant livraison) ; le contrat V1.3 n’a pas de champ d’artefact.
- La contradiction `C-X` figure au manifeste, mais `Teacher.correct` ne l’enseigne pas.
- Ni V0.4-DEV v1.2.1, ni RED V0.3, ni aucun examen n’ont été lus ou modifiés.

---

## ADDENDUM V1.6 — 2026-10-24 (RAPPEL)

**Base :** `f1391e52`. **Décision :** RAPPEL_V16 = GO ; S actif ; P5-L2 sans autorité ; P2, P3, P_ALIGN en HOLD ; auteur et source de V0 = UNKNOWN.

### F.1 Contrat appliqué

Sources : Option C §5 (`OXYGEN_R4_3_CALIBRATION_DESIGN.md`), `R4_4_CONTRACT_GAPS_CLOSURE.md` lacune 4 (TC-R1 à TC-R7), pré-enregistrement §3.8 et H4.

- Empreinte repliée : minuscules, accents repliés, espaces normalisés, ponctuation finale `. ! ?` retirée. La ponctuation interne est conservée (choix du contrat) ; aucune lemmatisation, donc la même empreinte en configurations B et D.
- Exemplaire actif : non CONTESTÉ. Une correction SUSPENDUE n’existe que sur un exercice contesté, qui est donc déjà exclu.
- Comportement : étiquette de l’exemplaire, origine `RAPPEL`, provenance = ids des exemplaires rappelés ; deux étiquettes pour la même empreinte → CONFLIT.
- Priorité sur P1–P5 et K9 : le RAPPEL est placé après « mot jamais enseigné » (incompatible avec un exemplaire actif) et avant le contrôle du déterminant inconnu.
- Non contributif : aucun événement, aucune observation, aucune voix modifiée (N_c et TP_c n’existent pas encore).

Constat de lecture : le RAPPEL émet une étiquette (TC-R1). C’est la seule émission nouvelle, autorisée par le contrat. Elle porte l’origine `RAPPEL` (mémoire), jamais une origine d’inférence, et la porte d’inférence (S, M1) est inchangée pour toute question non identique.

### F.2 Chemin de rappel

| Notion | Réalisation |
|---|---|
| observation originale | première occurrence d’un item ou d’une correction (teaching_event_id) |
| occurrence de lecture | `answer`, `retrieve`, `history`, `_recall` : aucun événement, aucun changement d’état |
| rappel | question à empreinte identique à un exemplaire actif : réponse RAPPEL |
| nouvel enseignement | appel `learn()` : observation nouvelle si l’id est nouveau, occurrence sinon |
| correction | `apply_correction` : observation de correction, occurrence de l’exercice |
| observation dérivée | exercice reçu avec une correction ; contraste issu d’une correction OK ; traits calculés |

`_recall(word, sentence, as_of=None)` renvoie le statut (RAPPEL, CONFLIT ou aucun), les étiquettes, les observations, la vue mémoire (statut, corrections) et les enregistrements de provenance V1.3. Il est en lecture seule et rejouable au passé.

### F.3 Invariants

| # | Invariant | Vérification |
|---|---|---|
| 1, 2 | un rappel, même répété, ne crée ni observation ni preuve | état canonique et `_evidence` identiques après rappels répétés |
| 3 | N_c / TP_c intacts | aucun état modifié ; N_c / TP_c non implémentés |
| 4 | CONTESTÉ / SUSPENDU non rappelés | exercice contesté, correction suspendue : pas de RAPPEL, inférence normale |
| 5 | filiation des corrections conservée | correction → exercice et exercice → item source déclaré inchangés |
| 6 | contradiction conservée | après la contradiction pilote, EX-F6 n’est plus rappelé ; rappel au passé et journal conservés ; double étiquette → CONFLIT |
| 7, 8 | UNKNOWN reste UNKNOWN ; aucune indépendance | provenance rappelée identique, relation inchangée |
| 9 | pas de contournement de la porte | 0 question non identique modifiée ; origine RAPPEL distincte des origines d’inférence |
| 10 | replay | rappel identique après sauvegarde / rechargement ; `as_of` reproduit le passé |

### F.4 Différentiel V1.5 → V1.6

- Questions non identiques : 0 changement sur 14 scénarios ; injection 2 × 20 000 tirages identiques ; leave-one-out V0 : 0 divergence sur 36.
- Questions identiques à un exemplaire : 81 HOLD/PREUVE_INSUFFISANTE → RAPPEL avec l’étiquette enseignée ; 1 CONFLIT et 2 exemplaires contestés inchangés ; 1 réponse `L1/CORRIGE` d’inférence portant sur une phrase enseignée devient `L1/RAPPEL` (même sens, origine mémoire au lieu d’inférence, conformément à H4).
- V0 complet : les 18 phrases enseignées répondent RAPPEL avec leur étiquette ; 4 MOT_INCONNU inchangés ; après la contradiction, EX-F6 n’est plus rappelé.
- États sauvegardés identiques octet pour octet ; seuils inchangés.

### F.5 Tests

- Base de 108 tests : 107 inchangés ; 1 assertion mise à jour (`test_v11_recall_of_a_lesson_sentence_is_not_corroborated` : HOLD → RAPPEL ; son commentaire documentait le RAPPEL comme NOT_COVERED).
- 14 tests RAPPEL ajoutés → 122/122.
- RED sur V1.5 : 14 échecs (10 comportementaux, 4 dus à l’API absente) ; le test d’invariant sur le rappel répété passait déjà.

### F.6 NOT_COVERED

- TC-R2 (exclusion des métriques) : aucun calcul de métriques P-CAL n’existe, et le score du banc RED ne distingue pas RAPPEL. Les examens sont disjoints de l’enseignement par construction, mais le contrôle `check_unseen` du banc (minuscules et espaces) est plus faible que l’empreinte RAPPEL (accents, ponctuation finale).
- Orthogonalité RAPPEL / LOO-CAL : LOO-CAL n’est pas implémenté (P2).
- Lecture à confirmer : l’invariant 9 et « ne pas autoriser une nouvelle réponse » sont lus comme portant sur l’inférence. Si le RAPPEL devait rester purement informatif, ce serait une déviation de TC-R1 à décider.
- L’addendum V1.5 (« 18 PREUVE_INSUFFISANTE ») décrit V1.5 : sous V1.6, ces sondes identiques aux phrases enseignées répondent RAPPEL.

---

## ADDENDUM V1.7 — 2026-10-24 (P2 / LOO-CAL : blocage contractuel ; précondition RAPPEL / unseen)

**Base :** `fcaae848`. **Décision :** RAPPEL accepté (réponse de mémoire, exclue de P-CAL) ; P2 et LOO-CAL = GO ; LOO-ALIGN = HOLD ; P3 et C1 non autorisés ; S actif.

### G.1 Contrats relus

| Source | N_c / TP_c | Classe muette | Égalité | Voix |
|---|---|---|---|---|
| R4.3.1 NB1 / NB2 (calibration design) | items actifs non muets en LOO / étiquette juste | similarité < s_min 0,2 ou marge < δ 0,15, après filtre de pertinence | entre étiquettes différentes → muette | similarité brute (rétrécissement porté sur les comptes) |
| R4.4, fermeture des lacunes, lacune 1 | items actifs non muets / argmax juste | aucune voix > 0 | comptée dans N_c, pas dans TP_c | voix de la classe |
| R4.4, lacune 3 et pré-enregistrement §3.4 / §3.6 | itérations LOO non muettes / justes | aucun trait P3 actif ; C1 puis P3 recalculés à chaque itération | — | voix sur traits filtrés |

### G.2 Point bloquant

N_c et TP_c sont définis sur des voix filtrées par C1 puis P3, recalculées à chaque itération. P3 et C1 ne sont pas implémentés et ne sont pas autorisés dans cette passe. Sans eux :

- TC-L4 (un exemplaire par étiquette, N_c = 0 attendu) donne N_c = 2 pour la classe constructions ;
- sur V0, classe constructions : N/TP = 18/6 selon la lacune 1, 5/5 selon R4.3.1, soit r_c = 0,35 ou 0,86 ; classe exemplaires : 2/2 ou 0/0.

Les lectures divergent jusqu’à la qualification même des classes (P2). Aucun N_c ni TP_c n’est donc calculé : ce serait choisir une formule non contractuelle. Sur les égalités, R4.3.1 (classe muette) et R4.4 (comptée dans N_c) divergent ; R4.4 étant postérieur, sa règle prime, à confirmer.

### G.3 Ce qui est implémenté (indépendant de P3 et C1)

`_loo_cal_plan(word, as_of=None)`, en lecture seule :

- unité = exemplaire actif ; retrait B2 = l’item et toutes les corrections qui le visent, contradiction comprise ;
- exclusions : CONTESTÉ ; RAPPEL (un autre exemplaire actif a la même empreinte, donc la question serait un rappel) ;
- répétitions : un identifiant livré plusieurs fois = une seule unité ;
- `remaining` : exemplaires actifs restants par étiquette ;
- `declared_descendants` : observations dérivées déclarées, signalées et non retirées (B2 ne les couvre pas) ;
- `votes = NOT_COMPUTED`, `missing = [P3_FILTER, C1_FILTER]`.

Sur V0 : 17 unités ; EX-F6 exclu (contesté par la contradiction).

### G.4 Précondition RAPPEL / unseen

- Constat : `check_unseen` (minuscules et espaces seulement) déclarait inédites les variantes d’une phrase enseignée par les accents ou la ponctuation finale (3 variantes sur 5 dans le test), alors que l’élève y répond RAPPEL.
- Correctif : `teaching_fingerprint`, identique à l’empreinte RAPPEL de l’élève, est enregistré par `ShownLog` ; `check_unseen` signale un item si son hachage ou son empreinte a déjà été montré. Le contrôle ne peut que signaler davantage d’items comme vus ; `sentence_hash` et la baseline memorizer sont inchangés ; aucune donnée et aucun examen ne sont touchés.
- Effet sur les campagnes RED : un item d’examen qui serait une variante d’une leçon ferait désormais échouer les contrôles d’unseen ; ce n’est pas vérifiable ici (examens privés).

### G.5 Non-régression et tests

- V1.6 → V1.7 : réponses identiques (24 sondes V0 avec contradiction ; leave-one-out 36/36) ; états sauvegardés identiques ; seuils inchangés ; RAPPEL et CORRIGE inchangés.
- Tests : 122 de base inchangés + 13 LOO-CAL + 4 unseen = 139/139.
- RED sur V1.6 : 15 échecs (13 dus à l’API LOO-CAL absente, 1 comportemental sur `check_unseen`, 1 dû à l’empreinte absente du banc).

### G.6 NOT_COVERED

- Calcul de N_c, TP_c et r_c : bloqué sur P3 et C1.
- Classe contrastes : la lacune 2 ne calibre que constructions et exemplaires.
- Descendants déclarés : signalés, non retirés ; leur retrait relèverait d’une extension de B2.
- Le contrôle de disjonction des ensembles de `test_pilot_force_controls` utilise encore `sentence_hash`.
- Aucune métrique P-CAL n’existe encore pour en exclure RAPPEL.
