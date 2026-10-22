# Oxygen — pilote « force » : recherche R4 (conception uniquement)

**Date :** 2026-10-22 · **Auteur :** Claude (contaminé : a lu les examens de développement) · **Statut :** proposition de recherche, **non canonique**, distincte de V0. Aucun élève R4, aucun examen, aucun seuil modifié.
**Base :** V0 figé en `dfef4f98` ; conception R3 `01df067f…`. Prospective V0 : **HOLD_INDEPENDENCE**.

## 1. Préservation de V0

| Élément | État vérifié |
|---|---|
| HEAD / worktree | `dfef4f98`, propre |
| `exemplar_student.py` / `features.py` | `aebbc335…` / `91b8dec5…` inchangés |
| Conception R3 | `01df067f…` inchangée |
| Banc RED V0.3 | aucune différence depuis `00cc85fc` |
| Dossier de passation | `C:\Users\User\Documents\OBSIDIA_HANDOFF\oxygen_prospective_v0\` conservé (README `1407a7b3…`, protocole `01f33151…`, script `a11d88f3…`, consignes `162bb015…`) |

**Points du script opérateur à faire vérifier indépendamment avant l'examen** (le script a été écrit par l'auteur du modèle) :

1. **Empreintes** : les valeurs attendues (`EXPECTED`) doivent être recalculées par l'opérateur lui-même, à partir de `git show dfef4f98:…`.
2. **Filtrage de sortie** (`pytest_names`, `summarize`) : seuls des noms, OK/KO et des agrégats sont affichés ; aucun `print` d'item, de phrase, d'identifiant ou de message d'exception.
3. **`campaign`** : la séquence doit être identique à la fixture du banc (`test_pilot_force_red.py::campaign`). Il faut vérifier qu'elle n'envoie à l'élève que `(mot, phrase)`, via `_bench.Examiner`, sans contourner le mélange.
4. **Ablation** : le module écrit dans `/extra` ne fait que mettre `CUE_BONUS` à 0, sans autre changement.
5. **Garde du passage unique** : le fichier `ONESHOT_DONE` dépend du répertoire privé. Un opérateur pourrait la contourner en changeant de répertoire. C'est une **discipline de l'opérateur**, pas une garantie technique.
6. **Journaux privés** : les fichiers `*_raw.txt` contiennent les sorties pytest complètes, donc des items possibles. Ils doivent rester hors de portée de Claude.
7. **Environnement** : `OXYGEN_PILOT_EXAMS` est transmis par l'environnement du processus hôte. La sonde d'isolation du banc vérifie qu'il n'atteint pas le conteneur.

## 2. Diagnostic des limites de V0

**Sources :**
- les agrégats du banc de développement, déjà publiés ;
- une analyse **sur l'enseignement seul** : leave-one-out sur les 18 items, décomposition du score.

Aucun nouvel examen n'a été consulté, et rien n'a été optimisé.

**Mesures sur l'enseignement :**
- LOO : 7 justes, 6 **fausses**, 2 HOLD faute de trait connu, 3 HOLD par τ/δ ;
- écart médian entre les deux premiers scores : 1,51 ;
- contribution médiane du vote k-NN : 0,53 ;
- environ 26 traits par phrase, pour 2 à 3 phrases d'enseignement par sens de « force » et **1 par sens** de « chemin » / « corriger ».

| Capacité | Constat V0 | Limite intrinsèque de l'algorithme | Insuffisance du jeu expérimental |
|---|---|---|---|
| **Acquisition lexicale** | 0 → 0,57 en T1 ; 4 sens sur 7 à 100 % | aucune connaissance préalable des mots pleins : un mot jamais vu n'apporte rien | 2 à 3 phrases par sens, trop peu pour estimer 26 traits |
| **Désambiguïsation par contexte** | égale le trigramme, sans le dépasser | le bayésien naïf **somme ~26 log-probabilités** de traits presque tous bruités (sacs de mots, n-grammes de caractères). Le score domine le k-NN, et la softmax rend des probabilités extrêmes. Résultat : des erreurs **assurées** (6 sur 18 en LOO) plutôt que des HOLD. | — |
| **Apprentissage concurrent** | « chemin » 0,00, « corriger » 0,25 | traits indépendants du mot, mais rien ne transfère d'un mot à l'autre | **1 leçon par sens** : apprentissage quasi impossible pour tout apprenant sans connaissance préalable (déjà signalé comme NB3 de l'audit) |
| **Abstention** | HOLD approprié 1,00 ; HOLD injustifié de 0,14 à 0,50 | le seuil porte sur des probabilités mal calibrées ; « trait non trivial vu » est trop permissif, puisque les mots-outils suffisent | 1 seul item HOLD par examen, donc une mesure binaire |
| **Mémoire et révisions** | 7 / 7 en interface ; `history` = `retrieve(as_of)` | cues jamais retirés ; la contradiction n'est pas interprétée (règle `ex[3]`) | — |
| **Conservation après redémarrage** | rechargement exact (tests unitaires) ; X2 = 0,43 | aucune ; X2 mesure aussi la généralisation sur d'autres phrases | X2 mélange rétention et généralisation |
| **Généralisation** | X1-far 0,50 ; X4 0,29 | **limite principale** : sans représentation des mots pleins inconnus, seules les constructions (« de force », « à force de ») transfèrent | X1-far exclut **par construction** tout mot plein de l'enseignement, ce qui teste une connaissance que les leçons ne donnent pas |

**Conclusion du diagnostic :**
1. Trois limites viennent de l'algorithme : calibration, domination du bayésien naïf sur des traits bruités, et absence de connaissance lexicale préalable.
2. Deux limites viennent du dispositif : trop peu de leçons par sens, surtout pour « chemin » et « corriger », et des mesures binaires pour l'abstention.

Un R4 qui ne traiterait que les premières resterait borné par les secondes. Changer l'enseignement serait une **nouvelle version du banc** (RED V0.4), soumise à une décision séparée.

## 3. Pistes R4, par famille (conception seulement)

| # | Famille | Idée | Manque de V0 visé | Risque |
|---|---|---|---|---|
| 1 | **Exemplaires et relations** | des exemplaires reliés entre eux : même construction, même domaine, contraste explicite (« X, pas Y ») ; vote par relations plutôt que par sacs de traits ; poids appris par fiabilité en LOO | domination du bayésien naïf ; traits bruités | surapprentissage sur 18 items |
| 2 | **Représentation conceptuelle et composition** | un sens = prototype + **classes sémantiques** des voisins (« agent collectif », « phénomène naturel », « grandeur mesurée »), dérivées d'une **ressource lexicale extérieure aux examens**, par exemple le corpus `periphery/language` (gloses, synonymes) | généralisation vers les mots inconnus (X1-far, X4) | **contamination** si la ressource ou ses classes sont choisies en connaissant les examens ; il faut une ressource figée **avant** et sélectionnée par un tiers |
| 3 | **Correction d'hypothèses** | lire les corrections comme des contrastes (« (Fa), pas (Fb) ») par une règle générique de négation, testée unitairement ; chaque correction réduit la confiance de la paire confondue | V0 ignore délibérément le sens nié (B3) | la règle doit être générique et figée ; c'est une réouverture explicite de B3 |
| 4 | **Apprentissage cumulatif sans effacement** | conserver le journal par révision de V0 ; ajouter un **statut** par exemplaire (actif, contesté, remplacé) sur le modèle des états B8 (`SUPERSEDED`, `CONTESTED`) ; ne jamais réécrire le passé | contradiction non interprétée ; cues jamais retirés | confusion entre état local et état B8 ; aucune écriture B8 réelle |
| 5 | **Récupération par sens, domaine, contexte et temporalité** | deux axes temporels distincts, **temps d'apprentissage** (révision) et **temps de validité** (B8 `ValidTimeInterval`), sans horloge universelle | V0 n'a que la révision | aucun |
| 6 | **Erreurs, provenance, historique éducatif** | conserver les **erreurs de l'élève** comme exemples négatifs datés par révision, avec leur correction ; c'est l'historique éducatif local | les erreurs d'exercice sont aujourd'hui remplacées par la correction | ne pas confondre avec la continuité éducative d'Oxygen |
| 7 | **Calibration de l'abstention** (transversale) | probabilités calibrées en LOO sur l'enseignement (température unique), seuil exprimé en *risque d'erreur* | HOLD injustifié élevé, erreurs assurées | calibrage sur 18 items, donc instable |

**Contamination de ce document :** l'auteur a lu les examens de développement. Les exemples de classes de la famille 2 (« agent collectif », « phénomène naturel », « grandeur mesurée ») peuvent en être un écho. Ils sont **illustratifs seulement**. Les classes réelles doivent venir d'une ressource figée et choisie par un tiers. Deux mots propres aux examens, cités par erreur dans un premier brouillon, ont été retirés.

**Ce qui vise une compréhension contextuelle plutôt qu'une mémorisation de phrases :** les familles 2 (classes sémantiques des voisins, qui permettent de généraliser aux mots inconnus), 3 (contrastes explicites entre sens proches) et 1 (constructions reliées). Les familles 4 à 6 concernent la **mémoire** et l'honnêteté de l'historique. Elles ne prouveront aucune compréhension.

## 4. Matrice des mécanismes existants

Statuts tirés du crosswalk `OXYGEN_MEMORY_SEMANTIC_CROSSWALK_V0.md` et d'une lecture rapide du code. **Aucun n'est branché au pilote.**

| Mécanisme | Capacité démontrée | Limite | Réutilisation possible pour R4 | Nouveau contrat éventuel | Risque de contamination | Épreuve future |
|---|---|---|---|---|---|---|
| **SENS** (scellé) | cadres d'énoncés, ambiguïtés, appelé sur Brody | scellé : aucune modification ; ne donne pas l'inventaire des sens de « force » | lecture seule d'analyses de cadre comme trait, **si** elle est exportable sans import runtime dans le conteneur | adaptateur hors conteneur qui pré-calcule des traits SENS pour les leçons **et** les questions, contrat de non-fuite (l'adaptateur ne voit que la phrase) | faible si appliqué identiquement ; moyen si choisi parce qu'il « marche » sur les examens vus | ablation avec et sans SENS sur le jeu indépendant |
| **Corpus lexical** (`periphery/language`) | formes, définitions, synonymes, gloses ; appelé sur Brody | un groupe de synonymes n'est pas un sens ; il n'y a pas de niveau concept | source de **classes sémantiques** pour la famille 2 | export figé et versionné du corpus, monté en lecture seule dans `/extra`, avec empreinte | **élevé** : il faut vérifier que le corpus ne contient pas les phrases d'examen (contrôle de fragments étendu) et figer l'extraction avant de connaître le jeu prospectif | contrôle de fragments sur l'export ; ablation |
| **OS Trad** | **introuvable dans le code** : mentionné seulement dans des notes d'assistant (`.deepseek/pastes`, non lues, [AF]) | aucune | aucune avant d'avoir localisé une implémentation | — | — | localisation, sinon abandon |
| **B8** (isolé) | états de claim (`CANDIDATE`, `SUPERSEDED`, `CONTESTED`…), temps de validité, supersession ; tests | isolé ; importé seulement par B10 | **vocabulaire et modèle** d'états pour la famille 4 ; temps de validité pour la famille 5 | aucun appel : copie de concepts uniquement | nul | tests unitaires de l'élève R4 |
| **B9** (isolé) | chemins cognitifs | isolé, non raccordé | inspiration éventuelle pour tracer un raisonnement de réponse | — | nul | — |
| **B10** (isolé) | révisions par slot, `get_artifacts_at_or_before`, historique | authenticité absente (invariant rouge) | modèle de requête « à la révision r », que V0 reproduit déjà | aucun ; l'invariant reste séparé | nul | — |
| **Native Memory** | 3 267 enregistrements en lecture seule, snapshot de récupération sur Brody | **pas de champ de date** ; pas de sens lexical | aucune pour l'élève ; elle ne doit pas être une source d'apprentissage cachée | — | élevé si elle contient des phrases proches des examens | — |
| **MMonde** (M41) | modèle du monde, périmètre V1 clos, chargé à la demande | non intégré, non prouvé en Lean | inspiration pour des classes d'entités ou de phénomènes (famille 2), **sans import** | décision du fondateur requise (Option A : pas d'import MMonde/F12) | moyen | — |
| **34 arbres** (R^34) | signal d'activation à chaque requête Brody | « jamais une décision » ; aucun lien avec le sens lexical ; réduction 34 → 8 inactive | un vecteur R^34 de la phrase comme **trait supplémentaire**, en expérience séparée | adaptateur hors conteneur qui pré-calcule R^34 identiquement pour leçons et questions | moyen | ablation R^34 contre sans, sur un jeu indépendant |
| **Continuum** | `periphery/continuum_node.py` : une **ébauche de dataclass** de 10 lignes ; l'adaptateur Brody le déclare « couvert » par les snapshots de session et temporels | aucune mécanique d'apprentissage | aucune démontrée | — | nul | — |
| **AVDR** | `periphery/avdr.py` : **2 lignes**, retourne `AVDR_CONTEXT_ONLY`, `non_decision` | ébauche | aucune | — | nul | — |

**Ne rien reconstruire sans preuve d'un manque.** Les manques démontrés par V0 sont la calibration, la généralisation aux mots inconnus, l'interprétation des contrastes et la quantité d'enseignement. Aucun ne prouve qu'il faille reconstruire B8, B10, Native Memory, MMonde ou les arbres.

**Crosswalk :** il reste documentaire. La mémoire multidimensionnelle (arbres, nuages, graphes, frise) **n'est pas branchée** au pilote, et cette proposition ne le prétend pas.

## 5. Exigences d'indépendance pour R4

1. **Conception :** relue par un relecteur indépendant **non contaminé**, puis verrouillée par empreinte avant tout code (même schéma que R3).
2. **Ressources externes :** toute ressource (export du corpus, traits SENS, R^34) est **choisie et figée avant** la rédaction du jeu prospectif R4, puis passe le contrôle de fragments d'examen.
3. **Évaluation :**
   - un **nouveau** jeu indépendant, rédigé par un humain non contaminé, distinct du jeu prospectif V0 ;
   - un opérateur humain, avec la même transmission filtrée ;
   - V0 et R4 évalués sur **le même** jeu, chacun en un seul passage, pour la comparaison.
4. **Banc de développement :** les examens V0.3 sont contaminés. Ils ne servent qu'à vérifier la mécanique, jamais à conclure ni à régler.
5. **Préalable :** tant que la prospective V0 est en HOLD_INDEPENDENCE, R4 ne peut pas être évalué de façon probante non plus. **La désignation de personnes indépendantes est le préalable commun.**

## 6. Questions ouvertes pour le fondateur

1. Désigner un rédacteur et un opérateur humains (préalable commun V0 / R4).
2. Autoriser ou non un **RED V0.4** avec un enseignement enrichi (au moins 5 leçons par sens, au moins 3 par sens concurrent) : c'est une décision distincte de R4.
3. Choisir les familles R4 à concevoir. Recommandation de recherche, **non canonique** : 7 + 3 + 2, puis 4 à 6 ensuite.
4. Autoriser ou non l'usage d'une ressource lexicale externe (corpus `periphery/language`), avec ses garde-fous de contamination.
