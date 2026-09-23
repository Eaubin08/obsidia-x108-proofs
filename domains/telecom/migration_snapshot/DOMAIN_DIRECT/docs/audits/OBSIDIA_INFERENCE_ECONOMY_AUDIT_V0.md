# OBSIDIA_INFERENCE_ECONOMY_AUDIT_V0

## 1. Objet

Cet audit fige la couche Obsidia Inference Economy Layer.

Le constat central est le suivant : Obsidia ne réduit pas seulement le prix du token. Obsidia réduit la nécessité même du token et de l'inférence lourde.

La métrique principale n'est plus le coût par token, mais le coût par action admissible.

## 2. Principe

Le marché optimise souvent le prix de l'inférence : token moins cher, modèle plus petit, batching, cache, quantization, routing multi-model.

Obsidia attaque un étage plus profond : est-ce que l'inférence lourde doit être appelée au départ ?

Obsidia réduit le coût par :

- routage avant calcul lourd
- Fast Path
- domaines spécialisés
- mémoire ciblée
- preuve Lean locale
- kernel X108
- receipts
- replay
- suppression des chemins inutiles
- réduction des retries
- réduction des faux FAIL
- réduction du contexte large

## 3. Kernel et inférence

Le kernel X108 n'est pas le moteur d'inférence principal.

Il est l'autorité qui gouverne l'inférence.

Il décide ou contraint :

- quelle route a le droit d'exister
- quelle couche peut être activée
- quel domaine est admissible
- quelle preuve est requise
- quelle action est HOLD, BLOCK ou ACT
- quel coût est acceptable
- quelle sortie doit être rejouable ou auditée

Formule synthèse :

Le kernel gouverne l'action.
L'Inference Economy Layer gouverne le coût.
Brody gouverne l'interface cognitive.
Obsidure gouverne le code, la preuve et l'audit.
Les domaines gouvernent la traduction métier.
Les receipts prouvent le chemin.

## 4. Base de comparaison

Base unique : coût pour 1 million d'actions.

Les scénarios Big Tech utilisés sont des ordres de grandeur :

| Label | Description | Coût pour 1M actions |
|---|---|---:|
| BT-Energie basse | énergie inférence seule, scénario très conservateur | 102 EUR |
| BT-Energie lourde | énergie avec test-time compute / raisonnement long | 1 296 EUR |
| BT-API simple | petite requête API token | 5 500 EUR |
| BT-API normale | requête API normale avec contexte | 25 000 EUR |
| BT-Agentique | gros contexte, outils, retries, orchestration | 160 000 EUR+ |

## 5. Couches Obsidia mesurées

| Couche Obsidia | Description | Coût Obsidia pour 1M actions |
|---|---|---:|
| Fast Path | route ultra courte / cache / skip | 0,0015 EUR |
| Brody chat | couche conversationnelle/contextuelle gouvernée | 0,20 EUR |
| Bank | domaine financier gouverné | 0,70 EUR |
| Trading | domaine signaux / risque | 0,84 EUR |
| GPS / Aviation | domaine terrain critique | 0,91 EUR |
| Lean canon check | validation formelle moyenne | 13,29 EUR |
| Obsidure Lean ciblé | preuve ciblée Obsidure | 23,92 EUR |

## 6. Ratios face à une API frontier normale

Scénario : BT-API normale = 25 000 EUR / 1M actions.

| Couche Obsidia | Obsidia / 1M | BT-API normale / 1M | Ratio |
|---|---:|---:|---:|
| Fast Path | 0,0015 EUR | 25 000 EUR | 16 666 667x |
| Brody chat | 0,20 EUR | 25 000 EUR | 125 000x |
| Bank | 0,70 EUR | 25 000 EUR | 35 714x |
| Trading | 0,84 EUR | 25 000 EUR | 29 762x |
| GPS / Aviation | 0,91 EUR | 25 000 EUR | 27 473x |
| Lean canon check | 13,29 EUR | 25 000 EUR | 1 881x |
| Obsidure Lean ciblé | 23,92 EUR | 25 000 EUR | 1 045x |

## 7. Métriques agrégées

Les ratios ne doivent pas être additionnés brutalement.

Les métriques retenues sont :

| Métrique | Description | Résultat face à BT-API normale |
|---|---|---:|
| OSCA | Obsidia Structural Cost Advantage, moyenne géométrique des gains par couche | environ 36 000x à 38 000x |
| OAPI | Obsidia Action Portfolio Index, Fast Path + Brody + Bank + Trading + GPS | environ 47 000x |
| ODPI | Obsidia Domain Portfolio Index, Bank + Trading + GPS | environ 30 000x |

Lecture centrale :

Sur le panier mesuré, Obsidia montre un avantage économique moyen d'environ 36 000x à 38 000x face à une API frontier normale.

## 8. Interprétation

Un écart moyen de cet ordre ne doit pas être lu comme une simple optimisation de coût.

Il indique un changement de régime économique.

Obsidia ne gagne pas seulement en rendant le calcul moins cher.

Obsidia gagne en évitant que le calcul inutile soit déclenché.

Le coût évité devient plus important que le coût optimisé.

## 9. Principe stratégique

La Big Tech optimise le prix du token.

Obsidia optimise la nécessité du token.

La Big Tech facture l'inférence.

Obsidia réduit l'inférence inutile.

Le meilleur token n'est pas seulement le token moins cher.

Le meilleur token est celui qui n'a pas besoin d'être généré.

## 10. Industrialisation requise

Prochaine étape :

- refaire les mêmes tâches avec API externes réelles
- mesurer tokens input/output
- mesurer coût API réel
- mesurer latence
- mesurer retries
- mesurer outils appelés
- mesurer qualité de sortie
- mesurer preuve/replay
- comparer avec Obsidia sur PC / edge / P2P
- générer un cost receipt par action

## 11. Statut

Status : PROVISIONAL_METRICS_LOCKED_FOR_AUDIT

Ce document fige les hypothèses, les tableaux et la lecture stratégique.

Il ne prétend pas prouver une supériorité universelle sur toutes les tâches IA.

Il prouve que, sur le panier mesuré, Obsidia attaque le bon poste de coût : l'inférence inutile.
