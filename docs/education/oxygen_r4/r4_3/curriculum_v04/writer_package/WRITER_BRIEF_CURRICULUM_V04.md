# Consignes de rédaction — curriculum d'enseignement V0.4 (pilote « force »)

Ce document est le **seul** que vous recevez. Vous **n'avez pas** à connaître, et ne devez pas demander :
- d'anciens examens ou leurs réponses ;
- des résultats ou des scores ;
- le code d'un élève logiciel.

Vous ne transmettez **jamais** votre travail à Claude ni à un agent qui travaille pour lui. Vous le remettez à l'opérateur désigné par le fondateur.

## 1. Ce que vous rédigez

Un **curriculum d'enseignement**, c'est-à-dire des leçons, des exercices et des corrections pour un élève logiciel qui apprend les sens d'un mot polysémique. **Ce n'est pas un examen.** Vos phrases servent à **enseigner**. Un jeu d'évaluation sera rédigé plus tard, par une autre personne.

## 2. Inventaire des sens (provisoire)

**« force »**

| Code | Sens |
|---|---|
| F1 | vigueur physique d'un être |
| F2 | énergie morale, courage, volonté |
| F3 | contrainte, violence |
| F4 | groupe organisé, effectif (souvent au pluriel) |
| F5 | grandeur physique (mécanique) |
| F6 | intensité, degré |
| F7 | locution (« à force de », « de toutes ses forces », « en force ») |

**Mots de contrôle**

| Mot | Codes |
|---|---|
| « chemin » | C1 voie concrète ; C2 manière, parcours figuré |
| « corriger » | R1 rectifier une erreur ; R2 punir, châtier |

« table » n'est **jamais** enseigné. N'écrivez **aucune** phrase avec « table ».

## 3. Quantités minimales

| Contenu | Minimum |
|---|---|
| Leçons étiquetées par sens (F1–F7, C1, C2, R1, R2) | **au moins 5** |
| Exercices (phrases étiquetées, qui reçoivent une correction) | **au moins 2 par sens de « force »** |
| Corrections pédagogiques | une par exercice (format §5) |
| Paires « proches mais de sens différent » | **au moins 1 par paire de sens voisins** de « force » (au minimum F1/F2, F3/F6, F5/F6, F4/F7) |
| Cas de contexte **ambigu** | **au moins 3**, étiquetés `AMBIGU`, où le sens ne peut pas être décidé |

## 4. Qualités exigées

1. **Constructions variées** pour un même sens : position du mot, singulier ou pluriel, avec ou sans article, prépositions différentes.
2. **Contextes concrets différents** : sport, cuisine, mer, atelier, école, ville, nature, travail…
3. **Formulations lexicalement éloignées** : deux leçons d'un même sens partagent le moins possible de mots.
4. **Phrases originales**, écrites par vous ; n'en copiez aucune d'un dictionnaire, d'un manuel ou d'Internet.
5. **Difficulté progressive** : numérotez l'ordre pédagogique (champ `order`), du plus clair au plus subtil.
6. Le **mot cible est présent** dans chaque phrase (forme accordée ou conjuguée possible).
7. **Aucun indice artificiel** : n'écrivez pas le nom du sens dans la phrase.
8. **Provenance :** indiquez pour chaque phrase « rédigée par [rôle], date ».

## 5. Corrections

**Format :** `« segment clé » <explication> (CODE_juste), pas <explication> (CODE_confondu).`

Exemple de **forme** seulement, avec des codes et un mot fictifs : `« sur la rive » indique un lieu concret (X1), pas une manière d'agir (X2).`

L'explication décrit le sens juste avant « pas » et le sens confondu après « pas ». Utilisez exactement les codes du §2.

## 6. Format de remise

Un fichier JSON UTF-8 conforme au format décrit dans `CURRICULUM_V04_FORMAT.md` (joint).
1. Enregistrez-le **hors de tout dépôt git**.
2. Calculez son **SHA-256** et transmettez seulement cette empreinte et le chemin à l'opérateur.
