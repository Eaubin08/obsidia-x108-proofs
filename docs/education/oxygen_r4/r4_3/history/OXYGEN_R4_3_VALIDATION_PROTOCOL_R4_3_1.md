# Oxygen R4.3 — protocole de validation (à figer avant tout build)

**Principe :** la faisabilité se vérifie sur les **données d'enseignement**, des **exemples synthétiques**, des **contrôles adversariaux** et des **tests d'état**, jamais sur les réponses des examens. Le RED V0.3 reste un banc de **développement**, contaminé.

## 1. Tests unitaires obligatoires (avant tout banc)

| Famille | Tests | Attendu |
|---|---|---|
| Positifs synthétiques | **T-POS-n** : 2 sens, constructions et vocabulaire distinctifs, n = 2, 3, 5 leçons par sens ; 8 questions **différentes de toute leçon** (générateur sans répétition) | au moins une réponse dès n = 3 ; précision 1,0 sur les réponses |
| Négatifs synthétiques | **T-NEG-UNREL** : contexte sans rapport ; **T-NEG-MIX** : contexte mêlant deux sens ; **T-NEG-NEWWORD** : mot jamais enseigné | HOLD (`PREUVE_INSUFFISANTE`, `CONFLIT`, `MOT_INCONNU`) |
| Rappel | **T-RAPPEL** : phrase identique à une leçon active | réponse d'origine `RAPPEL`, exclue des métriques d'acquisition ; phrase contestée → HOLD |
| Fiabilité | **T-BETA** ; **T-SELF-LOO** : la fiabilité est recalculée sur les seuls exemplaires actifs, sans lire la question | valeurs exactes ; aucune dépendance à la question |
| Pertinence | **T-REL** : un trait présent dans ≥ 50 % des exemplaires est ignoré | le témoin « contexte sans rapport » ne répond pas |
| Contradiction | **T-CONTRA** : exercice contesté | exclu de la fiabilité et des classes ; réponses qui s'y appuyaient → HOLD |
| Conformité | T-NEG-MARK, T-CONTENT, T-RETRIEVE-STATUS, T-JOURNAL, T-GLOSE, T-K9-1/2/3 | voir les écarts de conformité |
| Hérités | les 17 tests de R4-Core (ordre, état, intégrité), adaptés seulement là où C change la définition des voix | identiques |

## 2. Porte de faisabilité **P-CAL** (enseignement seul, seuils fixés ici)

Leave-one-out sur les 18 items de « force », avec la règle C complète (fiabilité auto-estimée **sans** l'item retenu, ses corrections ni la contradiction qui le visent, comme dans la règle B2 de P-ALIGN).

**P-CAL est satisfait si les trois conditions suivantes sont réunies :**
- **couverture ≥ 0,20**, soit au moins 4 réponses hors `RAPPEL` ;
- **précision ≥ 0,60** ;
- **aucun** témoin négatif synthétique n'est violé.

**Prévision déclarée d'avance :** sur l'enseignement actuel, la couverture sera **probablement d'environ 0** (projection : 0 / 18). P-CAL échouera alors, ce qui exprimera que **le matériau d'enseignement est insuffisant**, et non un défaut de la règle. Dans ce cas :
- il n'y a **pas** de build R4.3 sur le RED V0.3 ;
- la suite est un **curriculum enrichi** (RED V0.4, décision séparée, au moins 5 leçons par sens, rédigé par une personne qui n'a pas lu les examens), sur lequel P-CAL serait remesuré ;
- **aucun seuil n'est modifié** pour faire passer P-CAL.

## 3. Comparaison future (après une éventuelle porte P-CAL satisfaite)

Configurations, sur le **même** jeu et en un seul passage chacune :

| Configuration | Description |
|---|---|
| A | V0 figé |
| R4-Core figé | B et D |
| R4.3 | B (sans lemmatisation) et D (avec lemmatisation) |

**Rapports séparés :**
- couverture, précision, HOLD approprié et injustifié ;
- réponses `RAPPEL` (exclues des métriques d'acquisition) ;
- origines (`ACQUIS_LECON`, `CORRIGE`, `TRANSFERE`) ;
- effet de la lemmatisation (D − B).

**Statut de chaque passage :**

| Banc | Statut |
|---|---|
| RED V0.3 | **exploratoire, déclaré** |
| RED V0.4 éventuel | développement |
| Prospective | **seule preuve** ; elle exige un nouveau jeu indépendant et un opérateur humain (HOLD_INDEPENDENCE persistant) |

## 4. Risques de contamination du protocole

- **Auteur contaminé :** les paramètres nouveaux (0,75 et 50 %) sont fixés **avant** toute mesure, justifiés par la théorie (§1 de la conception) et par les témoins **synthétiques**, sans aucun score du RED.
- Le prototype jetable a vu les données d'enseignement : ce sont des données autorisées.
- Le témoin négatif qui a motivé le filtre de pertinence est **synthétique**.
- Une relecture technique sous le même compte est une **contre-vérification**, pas une indépendance expérimentale.

## 5. Critères d'arrêt

| Code | Situation |
|---|---|
| STOP_PCAL | P-CAL échoue → curriculum, pas de build |
| STOP_NEG | un témoin négatif répond → règle réfutée |
| STOP_TUNE | toute modification de seuil après une mesure → la mesure n'est plus probante, et la révision doit être relue |
| Budget | 2 itérations de build R4.3 au plus |

---

# Révision R4.3.1 — liste figée des témoins synthétiques (NB5)

Le mot cible est inventé (« zorp »), avec 2 sens opaques Z1 et Z2. Le générateur **ne répète jamais** une phrase de leçon.

| Id | Contenu | Attendu |
|---|---|---|
| POS-1 | n = 3 ; Z1 : contextes marins et construction « sur le … » ; Z2 : contextes de cuisine et construction « dans la … » ; question Z1 inédite, même construction et vocabulaire marin non vu | Z1 ou HOLD ; **jamais Z2** |
| POS-2 | symétrique pour Z2 | Z2 ou HOLD ; jamais Z1 |
| POS-COV | 8 questions inédites (4 Z1, 4 Z2) avec n = 5 | au moins 1 réponse, précision 1,0 |
| NEG-UNREL-1 | « Le zorp surgit sans prévenir. » | HOLD |
| NEG-UNREL-2 | « Un zorp passait par là hier. » | HOLD |
| NEG-MIX-BAL | autant d'indices Z1 que Z2 | HOLD (`CONFLIT` ou `PREUVE_INSUFFISANTE`) |
| NEG-MIX-UNBAL | **mêlé déséquilibré** (un indice marin et deux de cuisine, constructions mêlées) | **HOLD** ; une réponse déclenche STOP_NEG |
| NEG-NEWWORD | mot jamais enseigné | `MOT_INCONNU` |
| CONTRA | exercice Z1 contesté vers Z2 | exclu de la fiabilité ; aucune réponse fondée sur lui |
| RAPPEL | question identique à une leçon active | origine `RAPPEL`, exclue des métriques |

**Le contenu exact des phrases est écrit dans le futur fichier de tests et figé par empreinte avant toute exécution.**
