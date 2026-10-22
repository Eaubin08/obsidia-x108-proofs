# Oxygen — pilote « force » : pré-enregistrement GREEN V0 et protocole du jeu indépendant

**Statut :** pré-enregistrement **expérimental**. Ce n'est **pas** un FREEZE canonique Obsidia, et il n'engage aucune fondation scellée.
**Base :** banc RED V0.3, commit `00cc85fc`. Conception `OXYGEN_GREEN_DESIGN_V0.md`, révision R3.
**Aucun code GREEN n'existe à la date du verrouillage.**

## 1. Objet verrouillé

Le document de conception R3 fait foi **intégralement**. Son empreinte est :

| Fichier | Révision | SHA-256 (fichier UTF-8, fins de ligne LF) |
|---|---|---|
| `OXYGEN_GREEN_DESIGN_V0.md` | R3 (verrouillée) | `01df067f1b0075db17cc0d86de1a81b844c6e670a4cbcfaef42e3a56e19632d5` |
| `green_design_history/OXYGEN_GREEN_DESIGN_V0_R2.md` | R2 (historique) | `e26e24fe1c16a5e0e9fba9adacdb0e8a71dd3fe667e6aef8461937dbeca99e83` |
| `green_design_history/OXYGEN_GREEN_DESIGN_V0_R1.md` | R1 (historique) | `258aa698c2877928969a7bc65d1ce9d838a11926d078e2064c336416e61417e7` |

Éléments verrouillés, tous définis dans R3 :

| Élément | Référence R3 | Contenu verrouillé |
|---|---|---|
| Algorithme | §1.3 | Naive Bayes (Laplace) sur traits, plus vote k-NN (Jaccard pondéré), plus bonus de cue ; distribution normalisée |
| Paramètres | §1.3, tableau | τ = 0,5 ; δ = 0,15 ; k = 3 ; poids d'un exercice corrigé ×2 ; bonus de cue +2,0 (log) ; poids des traits 1,0 / 1,0 / 0,5 / 0,3 ; Laplace 1,0 |
| Traits contextuels | §1.2 | fenêtre ±3 positionnelle (`P±n`), n-grammes contenant la cible, forme de surface, déterminant ou possessif précédent, mots pleins, n-grammes de caractères (3) ; **identiques pour tout mot** |
| Abstention | §1.3 | HOLD si p < τ, ou écart < δ, ou aucun trait contextuel de la cible vu à l'enseignement, ou mot jamais enseigné |
| Corrections | §1.3 (B3) | sens = `ex[3]` ; segment « » extrait comme cue ; aucun sens lu dans le texte ; retrait sans effacement ; C-X jamais cité dans une provenance d'`answer` |
| Mémoire | §1.4 | révision 0 = état vide, un appel = une révision ; `history.content` = `retrieve(as_of_revision)` ; fichier unique canonique ; `StateIntegrityError` |
| Limites | §5, §8 | pronostics et revendications maximales tels qu'écrits |
| Arrêt | §7 | STOP_LEAK, STOP_CIRCULAR, STOP_PROTOCOL, STOP_OVERFIT (indicatif), budget de 2 itérations |

**Règle de déviation.** Toute modification d'un élément verrouillé après le gel exige :
- une nouvelle révision (R4…) avec son empreinte ;
- une justification écrite ;
- une nouvelle relecture indépendante.

Les résultats obtenus avant la déviation sont rapportés séparément. Une déviation décidée **après** avoir vu un résultat d'examen rend ce résultat **non probant** pour la version déviée.

## 2. Contrôle de contamination

- **Déclaration :** l'auteur (Claude, cette session) a lu les examens privés RED V0.1 à V0.3. Les auditeurs V0.2 et V0.3 aussi. Le relecteur de la clôture R3 aussi, pour vérifier l'absence de règles calquées (§5).
- **Garde-fou dans le code :** le futur test unitaire vérifie que le source de l'élève ne contient aucun identifiant de sens comme jeton (`\b(F[1-7]|C[12]|R[12]|T1)\b`), aucun mot indice, aucun import du banc ni de `app`.
- **Garde-fou expérimental :** seul le jeu indépendant (§3) décontamine. Aucun de ces agents ne peut le rédiger, ni en voir les items ou les clés.

## 3. Protocole du nouveau jeu d'examen indépendant (évaluation prospective)

1. **Rédacteur.** Il est désigné par le fondateur : un humain, ou un agent lancé **sans aucun accès** au fichier `exams_v0.json`, aux rapports d'audit V0.2 et V0.3, ni à ce dossier de conception.
   - Il reçoit uniquement : les définitions F1–F7, C1–C2, R1–R2, T1 ; le format des items ; les règles de construction (point 2) ; et **les données d'enseignement**, uniquement pour garantir la disjonction.
2. **Construction.** Un jeu complet X0′, X1′, X1-far′, X2′, X3′, X4′, avec :
   - au moins 2 items par sens de « force » et par examen ;
   - au moins 2 items par sens de « chemin » / « corriger » dans X3′ ;
   - au moins 2 items HOLD par examen ;
   - des items « table » en X0′, X1′ et X3′ ;
   - X1-far′ sans mot plein commun avec l'enseignement ;
   - X4′ dans des domaines absents de l'enseignement ;
   - aucune quasi-copie d'une leçon ;
   - un canari propre.
3. **Stockage.** Le fichier est privé et **hors dépôt**, dans un répertoire distinct de celui de `exams_v0.json`. Il n'est jamais monté dans le conteneur élève, jamais lu par l'auteur.
4. **Recevabilité.** Le banc RED V0.3 est lancé **inchangé** avec `OXYGEN_PILOT_EXAMS=<jeu indépendant>` et `EmptyStudent` **avant tout passage du GREEN**.
   - Tous les contrôles doivent être verts : isolation, disjonction, quasi-copie, far, référence parfaite, discrimination, témoin, scan des fragments.
   - Sinon, le jeu est renvoyé au rédacteur. L'auteur ne voit que les noms des contrôles en échec, jamais les items.
5. **Empreinte.** Le rédacteur, ou l'opérateur, consigne le SHA-256 du fichier **avant** le premier passage du GREEN.
6. **Passage unique.** Le GREEN gelé est évalué **une seule fois** sur ce jeu. L'auteur reçoit uniquement les verdicts par critère (10 RED d'acquisition, 7 tests d'interface, l'invariant) et les exactitudes agrégées, **pas** les réponses par item.
7. **Ablation des cues (N5).** Elle n'a lieu que sur ce jeu, dans le même passage, sous forme d'une seconde configuration déclarée ici, avec le bonus de cue fixé à 0.
8. **Après publication.** Le jeu devient « vu » ; une nouvelle évaluation prospective exige un nouveau jeu.
9. **Opérateur d'exécution (clôture R3).** La recevabilité (point 4) et le passage (points 6 et 7) sont exécutés par un **opérateur désigné par le fondateur**. Cet opérateur n'est **pas l'auteur**, n'est aucun agent contaminé, et ne s'exécute pas dans la session de l'auteur. La sortie brute de pytest expose des items : messages d'assertion, identifiants, phrases, variables locales avec `-l` ou dans un traceback.
10. **Sortie filtrée.** L'auteur reçoit **uniquement** un résumé : nom de chaque contrôle ou critère, OK/KO, exactitudes agrégées par examen. Il ne reçoit **jamais** :
    - la sortie brute de pytest ;
    - les tracebacks ;
    - les journaux du conteneur ;
    - l'état `/state` de l'élève ;
    - le `ShownLog` ;
    - les réponses par item.

    Les noms transmis sont ceux des **critères et contrôles non paramétrés** (par exemple `t1_acquisition`) ; tout identifiant pytest paramétré est nettoyé par l'opérateur avant transmission.
11. **Artefacts.** Répertoires temporaires, états d'élève et journaux du passage sont **détruits** après la production du résumé, ou conservés seulement dans le stockage privé de l'opérateur, hors dépôt et hors de portée de l'auteur.

**Limite assumée :** à 2 items par sens, ce jeu reste **technique**. Il décontamine, mais il ne donne pas de puissance statistique.

## 4. Trois épreuves distinctes

| Épreuve | Rôle | Jeu | Ce qu'elle peut établir |
|---|---|---|---|
| RED V0.3 (`exams_v0.json`) | **banc de développement** | contaminé (vu par l'auteur et les auditeurs) | le GREEN est mécaniquement compatible avec le protocole ; aucune conclusion d'apprentissage |
| Jeu indépendant (§3) | **évaluation prospective** | rédigé après le gel par un tiers non contaminé | un signal d'apprentissage non ajusté sur un échantillon technique ; aucune conclusion statistique |
| Campagne scientifique future | **confirmation** | au moins 20 items par sens et par examen ; seuils et tests (par exemple binomial exact contre la meilleure ligne de base, correction de Holm) **pré-enregistrés** | une conclusion statistique, dans les limites du protocole ; elle exige une autorisation séparée |

## 5. Absence de règles calquées sur les examens privés

À vérifier par la relecture de clôture : aucun élément de R3 (exemple, trait, paramètre, règle) ne reproduit un item, un mot plein ni une structure propre aux examens privés, qui seraient absents des données d'enseignement. Le résultat est consigné au §7.

## 6. Historique des révisions de la conception

| Révision | SHA-256 | Changement |
|---|---|---|
| R1 | `258aa698c2877928969a7bc65d1ce9d838a11926d078e2064c336416e61417e7` | proposition initiale |
| R2 | `e26e24fe1c16a5e0e9fba9adacdb0e8a71dd3fe667e6aef8461937dbeca99e83` | relecture n°1 (APPROVE_WITH_CHANGES) : B1 `history.content` ; B2 fichier unique canonique ; B3 sens `ex[3]` ; N1 à N8 |
| R3 | `01df067f1b0075db17cc0d86de1a81b844c6e670a4cbcfaef42e3a56e19632d5` | relecture n°2 (APPROVE_WITH_CHANGES, rédaction) : hyperparamètres a priori partout ; positions `P±n` ; C-X hors `taught_senses()` |

R2 et R3 se reproduisent à l'octet près depuis R1 par des remplacements textuels documentés.

## 7. Relecture de clôture R3

Relecteur indépendant de clôture (contaminé volontairement pour cette vérification ; exclu de la rédaction du jeu indépendant). Verdict : **APPROVE_WITH_CHANGES**.

- **Empreintes et diff :** R1, R2, R3 conformes ; R3 = R2 + les trois corrections de rédaction seulement (6 blocs).
- **Corrections (a) hyperparamètres a priori, (b) positions `P±n`, (c) C-X hors provenance :** OK ; aucun nouveau défaut ; cohérent avec les tests d'interface.
- **Pré-enregistrement :** fidèle ; il n'est pas présenté comme FREEZE canonique ; les trois épreuves sont distinguées.
- **Changement requis :** le protocole n'indiquait ni qui exécute le banc ni comment sa sortie est filtrée. La sortie brute de pytest expose des items. **Corrigé** par les points 9 à 11 du §3.
- **NB contamination consignée :** au §1.2 de R3, la liste d'exemples de déterminants cite `sa`. « sa force » apparaît 8 fois dans les examens privés et **0 fois dans l'enseignement**. C'est très probablement un écho de la lecture des examens par l'auteur.
  - L'extracteur reste générique (« déterminant ou possessif précédent »). Ce n'est pas une règle, et le comportement de l'élève n'en dépend pas : tout déterminant précédent est capté, quel qu'il soit.
  - R3 est conservée telle quelle, pour garder l'empreinte verrouillée. Une R4 qui remplacerait `sa` par `les` ou `toutes ses` reste **optionnelle** et soumise à la règle de déviation (§1).
  - Ce cas confirme que seul le jeu indépendant décontamine.
- Les autres expressions citées dans R3 (« de force », « à force de », « forces de l' », « de toutes ses », « newtons », « corrigeait », « table ») figurent toutes dans l'enseignement.
