# Oxygen R4.2 — spécification des contrats K1 à K10 (conception seule, non verrouillée)

**Base :** `87ac3190`. Conception R4.1 `a27b3bc2…` et pré-enregistrement `8406dcf1…` **conservés et non modifiés** ; R4.2 est un **amendement** distinct. Export V1 figé, inchangé.
**Auteur :** Claude, **contaminé** (a lu les examens de développement). Aucune règle de ce document n'a été choisie ou réglée sur un examen. Les seules données consultées sont l'enseignement (`_pilot_data.py`) et l'export V1. Les exemples sont **synthétiques** : X désigne un mot cible, L1 et L2 des étiquettes opaques, g1 et g2 des groupes du corpus.
**Statut :** non canonique, non FREEZE. Aucun code d'élève.

**Faits consultés (enseignement et export seulement) :**
- « force » a **15** groupes dans le thésaurus (5 à 21 synonymes chacun) ;
- « chemin » et « corriger » n'en ont **qu'un** chacun (63 et 107 synonymes), qui mélange leurs sens ;
- ~~3~~ **2** synonymes en plusieurs mots contiennent une forme d'un mot cible (« chemin de fer », « force de la nature » ; correction R4.2.1/R4.2.2) ;
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
  6. **Gloses :** les **tokens** pleins du segment positif (lemmatisés à l'évocation) vont à la glose de `ex[3]` ; ceux du segment négatif à la glose de N (B3). Le segment entre « » est conservé comme cue de construction, comme en V0.
- **Sorties :** contrastes (P, N, traits de construction de l'exercice, provenance `C-n`), gloses, statut.
- **Cas de refus ou cas dégradés :**

| Cas | Traitement |
|---|---|
| aucun marqueur de négation | aucun contraste ; glose positive seulement |
| P absent | P := `ex[3]` |
| **P ≠ `ex[3]` sans négation** (cas d'une révision) | l'exemplaire existant passe à `CONTESTÉ` ; l'étiquette textuelle est journalisée comme **alternative non apprise** ; aucun contraste |
| P ≠ `ex[3]` avec négation | statut `MALFORMÉ` ; rien n'est appris du texte |
| ~~étiquette inconnue de 𝓛~~ | ~~ignorée et journalisée~~ — **supprimé en R4.2.2** (aucune détection hors 𝓛) |
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

---

# Révision R4.2.1 — précisions contractuelles (relecture technique : HOLD → corrections)

Ces règles **complètent et priment** sur le texte ci-dessus. Aucune mesure n'a été faite entre R4.2.0 et R4.2.1. P-ALIGN n'a pas été exécuté.

## B1 — K1 : usage du poids 1/k

- **Support** (liaison) : binaire. Un item compte dès qu'au moins un de ses mots évoque g_j, quel que soit k.
- **Poids d'évocation d'un groupe par une question :** w(g_j) = **max**, sur les mots de la question qui évoquent g_j, de 1/k, où k est le nombre de lemmes candidats du mot (k = 1 pour un mot non ambigu).
- **Voix :** voix(L) = Σ_{g ∈ E ∩ liens(L)} w(g) / Σ_{g ∈ E} w(g).
- **Égalités :** une égalité en tête n'est pas un maximum strict ; la classe ne concorde alors sur aucune étiquette (K3).
- **Appariement token ↔ synonyme :** comparaison après repli des accents et passage en minuscules. Un synonyme en plusieurs mots n'est évoqué que si **tous** ses tokens apparaissent **consécutivement** dans le texte.

## B2 — K1 : leave-one-out de P-ALIGN sans fuite

Pour retenir un item i, on retire de l'apprentissage :
- l'item i lui-même ;
- **toute correction dont l'exercice est i**, avec ses gloses et ses contrastes ;
- la **contradiction** si elle porte sur i.

**Égalité en tête de la voix :** l'item compte comme **muet** pour P-ALIGN, ni juste ni faux. La porte compte les items non muets (au moins 6) et la précision de l'étiquette en tête strictement maximale (≥ 0,5).

## B3 — K1 et K2 : attribution des gloses

- Les lemmes du **segment positif** décrivent `ex[3]` : ce sont des gloses **de `ex[3]`**.
- Les lemmes du **segment négatif** décrivent **N** (« pas de courage (N) » décrit N) : ce sont des gloses **de N**, et non contre N.
- Pour la liaison comme pour l'exclusivité, une glose compte comme un **item d'enseignement de l'étiquette qu'elle décrit**.
- **Exclusivité :** g_j est `AMBIGU` dès qu'il est évoqué par des items, phrases ou gloses, d'au moins **deux** étiquettes.
- **Mots métalinguistiques** (« parle », « marque », « désigne », « exprime »…) : **aucun filtrage**, pour ne pas introduire de liste ad hoc. Le risque de faux liens est déclaré ; l'exclusivité le limite.

## B4 — Statut `CONTESTÉ` (K2, K4, K6)

**Un exemplaire `CONTESTÉ` :**
- reste en mémoire, dans `retrieve` (avec son champ de statut) et dans `history` ;
- est **exclu** des exemplaires actifs : il ne compte pas dans n_L (K4) et ne fournit aucune voix (K6) ;
- n'alimente aucune glose : l'étape 6 de K2 ne s'applique **pas** au texte qui conteste.

**Ordre :** si l'étiquette textuelle d'une révision n'est **pas encore** dans 𝓛, ~~statut `NON_INTERPRÉTÉ`~~ — **remplacé en R4.2.2 par `NON_RECONNU`** (voir « Reconnaissance des étiquettes »).

## B5 — K10 : vote de C_mappée

- Les groupes évoqués associés à « **aucune** » dans la table sont **ignorés**.
- C_mappée = L si **au moins un** groupe évoqué est associé à une étiquette et que **tous** ces groupes renvoient à la même étiquette L. Sinon HOLD.

**Règle de la table, imposée d'avance au contrôleur :**
- un groupe dont les synonymes recouvrent plusieurs sens pédagogiques reçoit « **aucune** » ;
- c'est le cas, d'avance, de l'unique groupe de « chemin » et de celui de « corriger ».

**Contrôleur :**
- désigné par le fondateur ;
- il n'a lu **ni les examens ni les liens appris** par l'élève ;
- il reçoit seulement les listes de synonymes des groupes cibles de l'export V1 et l'inventaire des sens.

**Biais déclaré :** C_mappée mesure le savoir préalable **plus l'expertise du contrôleur**. D − C_mappée est donc **conservateur**, et non exempt de biais.

## Remarques non bloquantes intégrées

| Remarque | Règle R4.2.1 |
|---|---|
| NB1 M-CIBLE | les expressions en plusieurs mots contenant une forme du lemme cible sont **2** (« chemin de fer », « force de la nature ») ; « travaux forcés » relève de *forcer* et **n'est pas** masqué |
| NB2 K2 | plusieurs étiquettes dans le segment positif → `MALFORMÉ` ; tokenisation : découpage sur l'apostrophe (« l'intensité » → « l », « intensité ») ; « pas » est **toujours** un marqueur, et le risque de « pas » nom est déclaré |
| NB3 K6 / K7 | plusieurs contrastes pour un même P : **maximum** ; la classe contrastes est **une** classe pour K3, de provenance {`C-n`, exercice} ; K7 : Jaccard sur les **phrases** d'enseignement seulement, gloses exclues |
| NB4 K3 + K4 | il est attendu que la condition 1 soit **rarement** satisfaite, avec un HOLD massif possible et H5 en péril. Ce n'est **pas chiffré**, pour ne pas mesurer avant le verrouillage : c'est une limite déclarée |
| NB5 registre | nouveautés ajoutées au registre (D17 à D19) |
| NB6 ex aequo P-ALIGN | voir B2 |

---

# Révision R4.2.2 — `CONTESTÉ`, ordre et reconnaissance des étiquettes

Ces règles complètent et priment sur R4.2.0 et R4.2.1. Aucune mesure n'a été faite entre-temps.

## F-A — Effet de `CONTESTÉ` et indépendance de l'ordre (choix explicite : **suspension**)

1. **Règle d'état** (calculée sur l'**ensemble** des corrections reçues pour un exercice e, et non sur leur ordre) : si **au moins une** correction a placé e en `CONTESTÉ`, alors **tous** les contrastes et **toutes** les gloses issus de **toute** correction portant sur e sont **SUSPENDUS**.
2. **Effet de la suspension :**
   - exclus des voix de la classe contrastes (K6), des liaisons et de l'exclusivité de K1, et de n_L (K4, via B4) ;
   - **conservés** dans la mémoire, dans `history` et dans `retrieve`, avec le statut `SUSPENDU` ;
   - jamais effacés.
3. **Ordre :** une correction qui arrive sur un exercice déjà `CONTESTÉ` est enregistrée et suspendue aussitôt. Une contestation qui arrive après des corrections suspend rétroactivement leurs effets. **L'état final dépend donc seulement de l'ensemble des corrections**, pas de leur ordre.
4. **Cas réel, connu d'avance :** C-4 (sur EX-F6) suivi de C-X (sur EX-F6), ou l'inverse, donne le **même** état final. EX-F6 est `CONTESTÉ`. Le contraste (F6, F5) et les gloses de C-4 sont `SUSPENDUS`. n_F6 vaut 2 et non 3. L'alternative F5 est journalisée.

## Reconnaissance des étiquettes (remplace `NON_INTERPRÉTÉ`)

- **Seules** les étiquettes de 𝓛 sont reconnues. Il n'existe **aucune** détection d'étiquette hors 𝓛, donc aucun paramètre caché.
- **Une correction n'apprend quelque chose de son texte que si son segment positif contient une étiquette reconnue P :**

| Cas | Traitement |
|---|---|
| P = `ex[3]` | gloses et contrastes appris (règles K2 et B3) |
| P ≠ `ex[3]`, sans négation | `CONTESTÉ` (B4) |
| P ≠ `ex[3]`, avec négation | `MALFORMÉ` |
| **aucune étiquette reconnue** dans le segment positif | **texte ignoré et journalisé** (`NON_RECONNU`) : aucune glose, aucun contraste, aucune contestation |

- L'exemplaire de l'exercice reste toujours enregistré avec `ex[3]` (règle B3).
- Ce tableau **remplace** le cas « P absent → P := `ex[3]` » de K2 et le cas `NON_INTERPRÉTÉ` de B4.

## Contenu des gloses et évocation en plusieurs mots

- Les gloses **excluent** les tokens d'étiquette et le segment entre « ». Ce segment reste un cue de construction, comme en V0.
- Une glose est conservée comme **séquence ordonnée** de tokens, comme une phrase, ce qui permet l'appariement consécutif de B1.
- Un synonyme en plusieurs mots s'apparie sur les **tokens repliés de surface**, sans lemmatisation. Il reçoit donc **k = 1**.

## Corrections de texte du corps de la spécification

- La section **M-CIBLE** du corps et la ligne d'origine **D15** indiquent « 3 » expressions : **lire 2** (« chemin de fer », « force de la nature »), conformément à R4.2.1 NB1 et à la vérification empirique de la relecture.

## Tests unitaires obligatoires ajoutés

| Test | Attendu |
|---|---|
| T-ORDRE-1 | séquence correction normale → contestation sur le même exercice : contraste et gloses `SUSPENDUS`, exemplaire `CONTESTÉ`, n_L diminué |
| T-ORDRE-2 | séquence inverse : état **identique** (même contenu de `retrieve`, mêmes voix pour toute question synthétique) |
| T-NON-RECONNU | texte sans étiquette reconnue : aucun effet hormis le journal |
| T-GLOSE | les gloses ne contiennent ni étiquettes ni segment entre « » |
| T-MULTI | un synonyme en plusieurs mots n'est évoqué que par une suite consécutive exacte, avec k = 1 |

## Finalisation R4.2.2 (remarques de la relecture : PASS_WITH_NB)

- **NB-1, ordre entre leçons et corrections : choix du recalcul.** L'interprétation de **chaque** correction (étiquettes reconnues, P, contrastes, gloses, contestation) est **recalculée** à partir de l'ensemble 𝓛 **courant**, à chaque mise à jour de l'état. L'état de l'élève est donc une **fonction de l'ensemble** des leçons et corrections reçues, indépendante de leur ordre. Le journal conserve chaque interprétation successive, sans effacement. Test ajouté **T-ORDRE-3** : une contestation reçue avant la leçon de l'étiquette contestataire donne, une fois cette leçon apprise, le même état que dans l'ordre inverse.
- **NB-2, phrase d'un exercice `CONTESTÉ` :** elle est exclue de **toutes** les preuves (n_L, K6, liaison **et** exclusivité de K1, Jaccard de K7), et conservée en mémoire et dans `history`.
- **NB-3 :** la ligne de K2 « étiquette inconnue de 𝓛 : ignorée et journalisée » est **supprimée** (aucune détection hors 𝓛). Dans le registre, la mention `NON_INTERPRÉTÉ` de D17 est **remplacée** par `NON_RECONNU` (D21).
- **NB-4, formulations :**
  - F-A §2 : les contrastes et gloses suspendus n'entrent **jamais** dans n_L ; seul l'exemplaire `CONTESTÉ` en sort (B4) ;
  - les gloses sont stockées comme **séquences de tokens** ; la lemmatisation intervient **à l'évocation** (K1), comme pour les phrases ;
  - « 3 » expressions dans le corps : **lire 2**.

**Statut final des contrats :** K1 à K10 et M-CIBLE sont **spécifiés**. Aucun ne reste en HOLD_CONTRACT.


## Clôture R4.2.2 (contre-vérification finale : PASS_WITH_NB, tour 4)

**Textes contradictoires barrés sur place (NB-D)** : la ligne K2 « étiquette inconnue de 𝓛 », `NON_INTERPRÉTÉ` en B4, « 3 » synonymes et « lemmes du segment ». La primauté des sections finales reste la règle.

**Définition de 𝓛 (NB-E)** : 𝓛 = ensemble des étiquettes de **tous les items étiquetés reçus**, leçons **et** exercices (`ex[3]`). Une étiquette n'entre jamais dans 𝓛 par un texte de correction.

**Exclusivité et phrase contestée (NB-B, substantiel, D23)** : la phrase d'un exercice `CONTESTÉ` est exclue de la **liaison** de K1, mais elle **reste comptée dans l'exclusivité**, pour son étiquette `ex[3]` **et** pour l'étiquette contestataire. Une phrase disputée garde son **veto** : ses groupes deviennent `AMBIGU`. Cette règle remplace, pour l'exclusivité seulement, la Finalisation NB-2.

**Biais de transfert déclaré (NB-C)** : comme la phrase contestée sort de la réunion de K7, `TRANSFERE` est plus facile pour une question proche de cette phrase. Le gain de transfert peut donc être **surévalué** sur ce voisinage. Le rapport d'évaluation devra isoler les réponses `TRANSFERE` dont la question a un Jaccard > 0 avec une phrase contestée.

**Journal des réinterprétations (NB-F)** : chaque mise à jour de l'état ajoute une entrée {révision, item ou correction déclencheur, interprétations modifiées (correction → ancien statut → nouveau statut), éléments suspendus ou réactivés}. Les entrées sont uniquement ajoutées, jamais effacées.

**Tests obligatoires ajoutés (NB-A)** :
- **T-ORDRE-3** : contestation reçue avant la leçon de l'étiquette contestataire → état final identique à l'ordre inverse ;
- **T-ORDRE-REEL** : la séquence réelle C-X → leçons F5 → C-4 et toutes ses permutations donnent le même état ;
- **T-VETO** : une phrase contestée rend `AMBIGU` un groupe qu'elle évoque.
