# Oxygen R4.2 — spécification des contrats K1 à K10 (conception seule, non verrouillée)

**Base :** `87ac3190`. Conception R4.1 `a27b3bc2…` et pré-enregistrement `8406dcf1…` **conservés et non modifiés** ; R4.2 est un **amendement** distinct. Export V1 figé, inchangé.
**Auteur :** Claude, **contaminé** (a lu les examens de développement). Aucune règle de ce document n'a été choisie ou réglée sur un examen. Les seules données consultées sont l'enseignement (`_pilot_data.py`) et l'export V1. Les exemples sont **synthétiques** : X désigne un mot cible, L1 et L2 des étiquettes opaques, g1 et g2 des groupes du corpus.
**Statut :** non canonique, non FREEZE. Aucun code d'élève.

**Faits consultés (enseignement et export seulement) :**
- « force » a **15** groupes dans le thésaurus (5 à 21 synonymes chacun) ;
- « chemin » et « corriger » n'en ont **qu'un** chacun (63 et 107 synonymes), qui mélange leurs sens ;
- **3** synonymes en plusieurs mots contiennent un mot cible ;
- les textes de correction citent les étiquettes, avec ou sans parenthèses (« … (F1), pas de courage (F2) » ; « lecture F5 admise »).

**Paramètres déjà pré-enregistrés, inchangés :** τ 0,5 ; δ 0,15 ; seuil 0,2 ; poids égaux ; rétrécissement n / (n + 2) ; « deux classes indépendantes » ; P-LEX désactivé.

---

## Classement des contrats

| Contrat | Nature |
|---|---|
| K3, K4, K5, K6, K8, K9 | **précision** d'un élément déjà prévu par R4.1 (aucun nouveau mécanisme) |
| K2 | **réouverture explicite** de la règle B3 de V0, prévue par R4.1 (capacité 3), désormais définie |
| K7 | **redéfinition** imposée par l'échec de P-LEX |
| **K1** | **nouvelle décision architecturale** : mécanisme d'alignement, plus une **porte de réfutation P-ALIGN** |
| **K10** | **nouvelle décision de protocole** : correspondance externe des groupes du corpus vers les étiquettes, établie par un contrôleur séparé |

---

## K1 — Alignement corpus ↔ sens enseignés

- **Problème exact :** R4.1 nomme la classe « alignement de la cible » (« groupes de sens du corpus pour le lemme cible, reliés aux étiquettes enseignées ») sans dire comment se fait la liaison, ni comment on en tire une voix.
- **Source :** pré-enregistrement §2, ligne « Alignement de la cible » ; conception §B, élément 3, capacité 7.
- **Entrées autorisées :**
  - les groupes `thes_fr` du lemme cible t, c'est-à-dire G_t = {g_j, chacun avec un ensemble de synonymes S_j} ;
  - les items d'enseignement reçus (phrase, étiquette) ;
  - les **gloses** positives et négatives extraites des corrections par K2 ;
  - la lemmatisation Morphalou de l'export.
  - **Interdits :** les `sense_id` comme clés partagées, toute table codée, les examens.
- **Comportement attendu :**
  1. **Évocation.** Un texte T évoque le groupe g_j de t si au moins un **lemme candidat** d'un mot plein de T (hors cible) **appartient directement** à S_j. C'est une appartenance directe, sans voisinage de synonymes ni transitivité, donc sans rien qui ressemble à P-LEX. Une forme ambiguë à k lemmes candidats contribue avec un poids 1/k.
  2. **Liaison** (apprise, statut HYPOTHÈSE, origine `INTERPRETE_CORPUS`). Pour chaque étiquette L : support(L, g_j) = nombre d'**items d'enseignement distincts** de L dont la phrase ou la glose positive évoque g_j. Le lien L → g_j est **accepté** si les deux conditions suivantes sont réunies :
     - support ≥ 1 ;
     - g_j n'est évoqué par **aucun item d'une autre étiquette**, gloses négatives comprises. C'est l'**exclusivité**.

     Sinon g_j est marqué `AMBIGU` et **jamais utilisé**. Chaque lien conserve sa provenance : items, lemmes évocateurs, identifiant local du groupe (valable pour l'export V1 seulement).
  3. **Voix pour une question.** Soit E l'ensemble des groupes de t évoqués par la question. Pour chaque étiquette L, la voix vaut |E ∩ liens(L)| / |E|. La classe est **muette** si E ne contient aucun groupe lié.
- **Sorties :** une voix par étiquette dans [0, 1] et la provenance ; plus, **sans étiquette**, la liste E des groupes évoqués (origine `PREALABLE`), utilisée par K10.
- **Cas de refus :**
  - aucun mot plein lemmatisable → muette ;
  - groupes seulement `AMBIGU` → muette ;
  - cible à un seul groupe (cas de « chemin » et « corriger ») → la classe **ne peut pas** séparer leurs sens. C'est un **constat déclaré d'avance**.
- **Invariants :**
  - P-LEX reste désactivé : aucun voisinage, aucune proximité, aucune chaîne ;
  - aucun lien sans au moins un item d'enseignement en provenance ;
  - le lien n'est jamais une identité : un groupe n'est **pas** un sens enseigné.
- **Porte de réfutation P-ALIGN** (nouvelle, **préalable au build** de cette classe), mesurée **sur l'enseignement seul**, par leave-one-out sur les 18 items de « force » (liens appris sans l'item retenu) :
  - on retient les items pour lesquels la classe est **non muette** ;
  - support exigé : **au moins 6** items non muets ;
  - précision exigée : l'étiquette en tête de la voix est juste dans **au moins 50 %** des cas ;
  - **sinon la classe est désactivée**, comme P-LEX.

  Seuils fixés ici, **avant** toute mesure. Conséquence déclarée d'avance : si P-ALIGN échoue, ARCH-C n'a plus aucune classe de preuve fondée sur le corpus. Le corpus ne sert alors qu'à la lemmatisation et à `MOT_INCONNU`, et H3 sera très probablement réfutée.
- **Exemple générique :** une leçon L1 « … X … *a* … » et une glose de correction « … *b* … ». *b* ∈ S_1 et aucun item de L2 n'évoque g1, donc L1 → g1 est accepté. Une question « … X … *b* … » évoque g1 et donne la voix L1 = 1. Une question « … X … *c* … » avec *c* hors de tout S_j laisse la classe muette.
- **Tests unitaires possibles** (synthétiques) :
  - évocation par appartenance directe ;
  - poids 1/k des formes ambiguës ;
  - refus d'un groupe évoqué par deux étiquettes ;
  - aucune voix sans lien ;
  - aucune utilisation de `sense_id` comme clé entre lemmes ;
  - détection d'un mécanisme de voisinage réintroduit (invariant P-LEX) ;
  - leave-one-out de P-ALIGN reproductible.
- **Contamination :** **moyenne**. Les gloses de correction ont été écrites par l'auteur contaminé, mais elles font partie du banc figé (RED V0.3, `_pilot_data.py`) et sont donc légitimes comme enseignement. P-ALIGN ne lit aucun examen.

## K2 — Lecture des corrections (règle générique de négation)

- **Problème exact :** R4.1 annonce une « règle générique de négation » sans la définir. V0 (règle B3) ignorait le texte, à l'exception du segment entre guillemets.
- **Source :** conception §B, capacité 3 ; lacune 3.
- **Entrées :** le texte de correction, l'exercice corrigé `ex` et l'ensemble 𝓛 des **étiquettes déjà apprises**. Le code ne contient aucun littéral d'étiquette.
- **Comportement :**
  1. On découpe le texte en tokens après repli des accents. Les **marqueurs de négation** forment une liste fermée et générique : `pas`, `non`, `plutôt que`, `au lieu de`, `ne … pas`, `ne … plus`.
  2. Le **segment positif** va du début au premier marqueur ; le **segment négatif** va du premier marqueur jusqu'à la fin de la phrase.
  3. Les étiquettes citées sont les tokens égaux à un membre de 𝓛, avec ou sans parenthèses.
  4. **Sens de l'exemplaire = `ex[3]`** (la règle B3 reste prioritaire). Étiquette positive textuelle P = étiquette de 𝓛 du segment positif.
  5. **Contraste** (P, N) enregistré pour chaque N ∈ 𝓛 cité dans le segment négatif, si N ≠ P.
  6. **Gloses :** les lemmes pleins du segment positif vont à la glose de `ex[3]` ; ceux du segment négatif à la glose négative de N. Le segment entre « » est conservé comme cue de construction, comme en V0.
- **Sorties :** contrastes (P, N, traits de construction de l'exercice, provenance `C-n`), gloses, statut.
- **Cas de refus ou cas dégradés :**

| Cas | Traitement |
|---|---|
| aucun marqueur de négation | aucun contraste ; glose positive seulement |
| P absent | P := `ex[3]` |
| **P ≠ `ex[3]` sans négation** (cas d'une révision) | l'exemplaire existant passe à `CONTESTÉ` ; l'étiquette textuelle est journalisée comme **alternative non apprise** ; aucun contraste |
| P ≠ `ex[3]` avec négation | statut `MALFORMÉ` ; rien n'est appris du texte |
| étiquette inconnue de 𝓛 | ignorée et journalisée |
| plusieurs négations | chaque N cité donne un contraste |

- **Invariants :**
  - aucune étiquette n'est créée depuis un texte de correction ;
  - le texte ne renverse jamais `ex[3]` ;
  - tout est journalisé, aucun effacement.
- **Exemple générique :** « « a b » exprime u (L1), pas v (L2). » avec `ex[3]` = L1 donne un contraste (L1, L2), u dans la glose de L1 et v dans la glose négative de L2. « Lecture L2 admise. » avec `ex[3]` = L1 et sans négation donne l'exemplaire CONTESTÉ et l'alternative L2 journalisée.
- **Tests possibles :** chaque ligne du tableau des cas, plus l'absence de littéral d'étiquette dans le code.
- **Contamination :** faible. La règle est générique et la liste de marqueurs est une classe grammaticale fermée.

## K3 — Concordance de deux classes indépendantes

- **Problème :** « au moins deux classes indépendantes concordent » n'est pas défini.
- **Source :** pré-enregistrement §2, condition 1 ; conception §C.
- **Comportement :**
  - une classe **concorde** sur L si sa voix rétrécie (K4) pour L est **≥ 0,5** et **strictement maximale** parmi les étiquettes de cette classe ;
  - deux classes concordantes sont **indépendantes** si leurs **ensembles de provenance** (identifiants d'items d'enseignement et de corrections, plus identifiants de groupes du corpus) sont **disjoints** ;
  - la condition 1 est satisfaite si au moins deux classes concordent sur le même L **et** forment au moins une paire indépendante.
- **Invariants :**
  - deux preuves tirées des mêmes items ou des mêmes groupes ne sont **jamais** comptées deux fois ;
  - la classe corpus (K1) compte pour **une seule** classe, quel que soit le nombre de groupes évoqués.
- **Exemple :** la classe constructions concorde sur L1 avec la provenance {i1, i2} ; la classe exemplaires concorde sur L1 avec {i2}. Elles ne sont pas indépendantes. La classe corpus concorde sur L1 avec {i3, g1} : elle est indépendante des deux précédentes.
- **Tests :** disjonction, non-disjonction, égalité de voix (pas de maximum strict, donc pas de concordance).
- **Contamination :** nulle.

## K4 — Rétrécissement n / (n + 2)

- **Comportement :** pour chaque classe et chaque étiquette L, voix'(L) = voix(L) × n_L / (n_L + 2), où n_L est le nombre d'**exemplaires actifs** de L (leçons et exercices non retirés ; un exemplaire corrigé compte une fois). Le rétrécissement s'applique **avant** la concordance (K3), le score et les seuils τ / δ.
- **Conséquence déclarée :** avec n_L = 2, il faut une voix brute de 1 pour atteindre 0,5 ; avec n_L = 3, une voix brute d'au moins 0,834.
- **Invariants :** déterministe ; n_L lu dans l'état ; jamais réglé.
- **Tests :** valeurs pour n = 0 (voix nulle), 1, 2, 3.
- **Contamination :** nulle.

## K5 — « Voisin déterminant »

- **Comportement :** les voisins déterminants sont les **mots pleins** (hors liste fermée de mots-outils de V0) situés dans la fenêtre **±3 tokens** autour de la première occurrence de la cible. Un voisin est **inconnu du corpus** si aucune forme Morphalou ne le lemmatise **et** s'il n'est pas lui-même un lemme `thes_fr`.
- **Configuration B** (sans corpus) : la condition 4 est **non applicable** (déclaré).
- **Tests :** fenêtre, mots-outils exclus, forme inconnue, configuration B.
- **Contamination :** faible. La taille de fenêtre est reprise de V0.

## K6 — Voix des classes constructions et exemplaires

**Constructions :**
- traits = classes `POS`, `NG`, `DET` et `SURF` de l'extracteur de V0, **sans** sacs de mots ni morceaux de mots ;
- voix(L) = max, sur les exemplaires actifs de L, de la similarité de Jaccard **pondérée** (poids 1) entre les traits de la question et ceux de l'exemplaire ;
- provenance : l'exemplaire qui réalise le maximum.

**Exemplaires :**
- traits = ensembles de **lemmes candidats** des mots pleins (hors cible), avec l'union pour les formes ambiguës (règle R4) ;
- en configuration B : formes repliées au lieu de lemmes (déclaré) ;
- voix(L) = max de Jaccard ; provenance : l'exemplaire du maximum.

**Contrastes (voix, K2) :**
- pour chaque contraste (P, N), si Jaccard(constructions de la question, constructions de l'exercice) ≥ **0,2** (seuil déjà pré-enregistré, réutilisé et non créé), alors voix(P) = cette similarité ;
- N ne reçoit **aucune** voix de cette classe ;
- provenance : `C-n` et l'exercice.

**Mutisme :** une classe est muette si toutes ses voix sont nulles.

**Score d'un sens :** moyenne des voix rétrécies sur les classes **non muettes et activées** dans la configuration. La classe proximité est toujours désactivée.

- **Tests :** bornes [0, 1], mutisme, absence de sacs de mots et de morceaux de mots dans les constructions, maximum et provenance.
- **Contamination :** faible. Les traits sont ceux de V0, déjà audités sans spécialisation.

## K7 — Origine `TRANSFERE`

- **Problème :** R4.1 définit `TRANSFERE` à partir de `INTERPRETE_CORPUS`, c'est-à-dire de la proximité, désormais désactivée.
- **Redéfinition :** une **réponse** pour L est d'origine `TRANSFERE` si les lemmes pleins de la question n'ont **aucun** lemme commun avec la réunion des lemmes des items d'enseignement de L (Jaccard = 0), alors que la réponse est soutenue par au moins une classe concordante d'origine `ACQUIS_LECON`, `CORRIGE` ou `INTERPRETE_CORPUS`.

**Origines des réponses (exclusives, dans l'ordre) :**

| Origine | Condition |
|---|---|
| `TRANSFERE` | condition ci-dessus |
| `CORRIGE` | un contraste ou une correction figure parmi les classes concordantes |
| `ACQUIS_LECON` | sinon, pour toute réponse étiquetée |
| `INCERTAIN` | HOLD |

`PREALABLE` qualifie les **hypothèses non étiquetées** (groupes évoqués, connaissance des mots), **jamais** une réponse étiquetée.
- **Tests :** chaque branche.
- **Contamination :** nulle.

## K8 — Critère de risque

- **Réconciliation :** le « risque estimé » de la conception §C est défini comme **1 − score rétréci du premier sens**. « Risque ≤ 0,5 » équivaut alors à la condition 2 (score ≥ τ = 0,5).
- **Aucun critère nouveau.** L'écart entre conception et pré-enregistrement est résolu en faveur du pré-enregistrement.

## K9 — Motifs d'abstention

Libellés **conservés** (R4.1) : `MOT_INCONNU` (= UNKNOWN_WORD), `PREUVE_INSUFFISANTE` (= INSUFFICIENT_EVIDENCE), `CONFLIT` (= CONFLICTING_EVIDENCE). La **précédence** les rend mutuellement exclusifs :

| Ordre | Motif | Condition |
|---|---|---|
| 1 | `MOT_INCONNU` | mot cible jamais enseigné, **ou** voisin déterminant inconnu du corpus (K5) |
| 2 | `CONFLIT` | au moins deux étiquettes différentes ont chacune au moins une classe concordante (K3), avec des provenances disjointes entre elles ; **ou** les deux premiers scores sont ≥ 0,5 avec un écart < 0,15 |
| 3 | `PREUVE_INSUFFISANTE` | toute autre condition 1 à 3 non satisfaite |

- **Tests :** un cas par motif, et l'ordre de précédence.
- **Contamination :** nulle.

## K10 — Configurations A, B, C, D et comparabilité

**Problème :** C (corpus sans leçons) ne connaît aucune étiquette. Lui donner 0 serait arbitraire ; lui donner HOLD ne mesure pas son savoir préalable.

| Config | Élève | Sortie étiquetée | Sortie non étiquetée (journal de l'évaluateur) |
|---|---|---|---|
| A | V0 figé | sens ou HOLD | — |
| B | R4 sans export (classe corpus et condition 4 inactives ; exemplaires sur formes repliées) | sens ou HOLD | — |
| C | R4 avec export, **sans** `learn` ni correction | toujours HOLD (`MOT_INCONNU` : cible non enseignée) | groupes de la cible évoqués par la question (K1, étape 1), origine `PREALABLE` |
| D | R4 complet | sens ou HOLD | idem C, plus liens appris |

**Correspondance externe (nouvelle composante du protocole) :**
- **Avant tout passage**, un **contrôleur séparé** établit une table **groupe du corpus → étiquette pédagogique** (ou « aucune ») pour chaque groupe des lemmes cibles de l'export V1.
- Il s'appuie **uniquement** sur les listes de synonymes et les définitions publiques des sens (inventaire F1–F7, C1–C2, R1–R2), **sans examen**.
- La table est **figée par empreinte** et **jamais** fournie à l'élève.
- C est alors évaluée par **C_mappée** : pour chaque item, l'étiquette obtenue en appliquant la table aux groupes évoqués, par vote unanime. Sinon HOLD.

**Métriques :**
- **principale : D − C_mappée**, sur les mêmes items. Elle mesure ce que les leçons ajoutent au-delà de ce qu'un usage **expert** du savoir préalable permettrait. C'est une estimation **conservatrice** du gain d'enseignement ;
- secondaires : D − C brut (C = HOLD), D − B (apport du corpus), B − A (avec réserve d'architecture) ;
- **interaction :** (D − B) − (C_mappée − 0).

**Apprentissage, savoir antérieur et transfert, par item :**
- **savoir antérieur** si C_mappée est juste ;
- **apprentissage nouveau** si D est juste alors que C_mappée est fausse ou HOLD ;
- **transfert** si la réponse de D est d'origine `TRANSFERE` (K7).

**Mots non enseignés mais présents dans le corpus :** on rapporte, par examen :
- la part des mots pleins des questions connus du corpus et absents de l'enseignement ;
- l'exactitude de D restreinte aux items qui en contiennent.

Le témoin « table » reste non enseigné et doit rester HOLD pour B, C et D.

**METRIC_HOLD ?** Non : D − C_mappée est définissable sans biais, **à condition** que la table de correspondance soit établie par un contrôleur séparé et figée avant le passage. Sans cette table, la métrique principale passe en **METRIC_HOLD**.

**Contamination :** **moyenne**. Le contrôleur ne doit pas être l'auteur. Une table rédigée par un agent du même compte est une contre-vérification technique, pas une indépendance expérimentale complète.

## M-CIBLE

- **Couverture décidée :** lemme, formes fléchies et entrées directes (déjà en V1), **plus** toute expression en plusieurs mots contenant une forme du lemme cible comme token, ce qui en retire 3.
- **Conséquence :** il faut un **export V2** distinct, avec sa propre empreinte et une **nouvelle autorisation**. V1 n'est pas modifié. M-CIBLE V1 reste disponible, marqué « couverture incomplète ».
- M-CIBLE est une **ablation** : elle n'est jamais une source d'enseignement fournie à l'élève.
