# Oxygen R4.2 — registre des déviations par rapport à R4.1 et au pré-enregistrement

Toutes les déviations sont décidées **avant toute ligne de code de l'élève** et **sans consulter d'examen**. R4.1 (`a27b3bc2…`), le pré-enregistrement (`8406dcf1…`), le registre des revues, l'erratum et l'export V1 restent inchangés.

| # | Élément | R4.1 / pré-enregistrement | R4.2 | Nature | Justification |
|---|---|---|---|---|---|
| D1 | Classe « alignement de la cible » (K1) | nommée, non définie | évocation par **appartenance directe** aux groupes, liaison **exclusive** apprise, voix = part des groupes évoqués liés | **nouvelle décision architecturale** | contrat absent ; mécanisme choisi sans voisinage, pour respecter P-LEX = HOLD |
| D2 | **Porte P-ALIGN** | inexistante | leave-one-out sur l'enseignement : au moins 6 items non muets et précision ≥ 0,5, sinon classe désactivée | **nouvelle porte de réfutation** | même discipline que P-LEX ; seuils fixés avant toute mesure |
| D3 | Règle de négation (K2) | « règle générique », non définie | marqueurs fermés ; segments positif et négatif ; étiquettes reconnues seulement parmi celles déjà apprises ; `ex[3]` prioritaire ; cas `CONTESTÉ` et `MALFORMÉ` | **réouverture explicite de B3**, prévue par R4.1 | contrat absent |
| D4 | Indépendance (K3) | « deux classes indépendantes » | indépendance = **provenances disjointes** ; la classe corpus compte pour une | précision | empêche le double comptage de preuves corrélées |
| D5 | Rétrécissement (K4) | « par exemple n / (n + 2) » ; point d'application non dit | n_L / (n_L + 2) **sur chaque voix**, avant la concordance et les seuils | précision | « par exemple » levé ; point d'application fixé |
| D6 | Voisin déterminant (K5) | non défini | mots pleins dans ±3 tokens ; inconnu = ni forme Morphalou ni lemme `thes_fr` ; non applicable en B | précision | fenêtre reprise de V0 |
| D7 | Voix des constructions, exemplaires et contrastes (K6) | non définies | Jaccard maximal par étiquette ; constructions sans sacs de mots ni morceaux de mots ; contraste via le seuil **0,2 réutilisé** | précision (aucun nouveau paramètre) | — |
| D8 | Score d'un sens | « moyenne pondérée des voix » | moyenne sur les classes **non muettes et activées** | précision | une classe muette n'est pas une preuve contre |
| D9 | Origine `TRANSFERE` (K7) | définie via `INTERPRETE_CORPUS` (proximité) | Jaccard nul entre la question et les items de L, avec une classe concordante | **redéfinition** imposée par l'échec de P-LEX | — |
| D10 | `PREALABLE` | « réponse dont toutes les preuves sont `PREALABLE` » exclue de D | `PREALABLE` qualifie les **hypothèses non étiquetées** ; le savoir antérieur est mesuré par **C_mappée** | précision de la métrique | une réponse étiquetée suppose toujours une leçon |
| D11 | Critère de risque (K8) | conception §C : « risque sous le seuil » ; absent du pré-enregistrement | risque = 1 − score, équivalent à la condition 2 | réconciliation | aucun nouveau critère |
| D12 | Motifs d'abstention (K9) | trois motifs, sans règle | précédence `MOT_INCONNU` > `CONFLIT` > `PREUVE_INSUFFISANTE`, règles quantifiées | précision | libellés de R4.1 conservés |
| D13 | Configuration C et métrique principale (K10) | « D − C hors `PREALABLE` » | **D − C_mappée**, avec une table **groupe → étiquette** établie et figée par un **contrôleur séparé** avant tout passage ; D − C brut en secondaire | **nouvelle décision de protocole** | sans table, la métrique principale est en METRIC_HOLD |
| D14 | Configuration B | « classes corpus à 0 » | plus : condition 4 non applicable, exemplaires sur formes repliées | précision | pas de lemmatisation sans corpus |
| D15 | M-CIBLE | lemme, formes et entrées | **plus les expressions en plusieurs mots** contenant la cible (3) | changement de règle d'export | il exige un **export V2** et une nouvelle autorisation ; V1 n'est pas touché |
| D16 | Sortie de l'élève | `{sense, provenance}` | plus un champ facultatif `corpus_hypotheses` (groupes évoqués), ignoré par le banc RED et lu par le seul harnais d'évaluation de l'opérateur | extension compatible | le protocole RED V0.3 n'est pas modifié |

**Déviations substantielles, à ne pas présenter comme rédactionnelles :** D1, D2, D3, D9, D13, D15.

**Conséquences connues d'avance, déclarées :**
- la classe corpus **ne peut pas** séparer les sens de « chemin » et de « corriger » (un seul groupe chacun) ;
- si P-ALIGN échoue, ARCH-C n'a plus de preuve tirée du corpus et H3 est très probablement réfutée ;
- le rétrécissement et la règle des provenances disjointes rendront l'élève **prudent** : HOLD fréquent possible, et H5 (HOLD injustifié ≤ 0,2) peut échouer.

## Ajouts R4.2.1

| # | Élément | R4.2.1 | Nature |
|---|---|---|---|
| D17 | Statuts `CONTESTÉ`, `MALFORMÉ`, `NON_INTERPRÉTÉ` et leurs effets (B4) | `CONTESTÉ` exclu des voix et de n_L, conservé en mémoire ; `NON_INTERPRÉTÉ` sans effet | **nouveauté** (vocabulaire des états B8, sans import) |
| D18 | Classification par item : savoir antérieur, apprentissage nouveau, transfert ; métrique d'interaction (D − B) − C_mappée | ajoutées au protocole d'évaluation (K10) | **nouveauté de protocole** |
| D19 | Poids 1/k, appariement multi-mots, égalités, leave-one-out sans fuite, attribution des gloses, vote de C_mappée (B1, B2, B3, B5) | précisés | précisions bloquantes levées |
| D15 (corrigé) | M-CIBLE V2 | **2** expressions en plusieurs mots en plus (et non 3) | changement de règle d'export, qui exige V2 |
