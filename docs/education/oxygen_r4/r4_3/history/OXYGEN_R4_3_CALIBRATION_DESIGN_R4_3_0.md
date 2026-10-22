# Oxygen R4.3 — conception de la calibration (conception seule, non verrouillée)

**Base :** `c9a3d861` (R4-Core figé). Conservés sans modification : V0, R4-Core, banc RED V0.3, export V1, contrats R4.2.2, historiques. **Auteur contaminé** (examens de développement lus autrefois) ; **aucun examen relu ici**. Les analyses utilisent uniquement les 18 items d'enseignement de « force » et des phrases **synthétiques**.

**État de départ :**

| Indicateur | Valeur |
|---|---|
| Tests unitaires | 17 / 17 |
| Critères d'acquisition | 0 / 10 |
| HOLD | 60 / 60 |
| P_LEX | HOLD |
| P_ALIGN | HOLD |

## 1. Faisabilité mathématique de R4-Core

**Règle en vigueur :**
- voix(L) = s_max(L) × n_L / (n_L + 2), où s_max(L) est la similarité de Jaccard **maximale** entre la question et un exemplaire de L ;
- concordance si voix ≥ τ = 0,5 (K3 / K4 / K6) ;
- d'où la condition s_max ≥ **(n + 2) / (2n)**.

| n (exemples du sens) | s_max requise | Atteignable ? |
|---|---|---|
| 1 | 1,50 | **jamais** (Jaccard ≤ 1) |
| 2 | 1,00 | seulement pour une phrase identique |
| 3 | 0,833 | quasi-identique |
| 4 | 0,75 | — |
| 5 | 0,70 | — |
| 10 | 0,60 | — |
| ∞ | → 0,50 | — |

**Mesures sur l'enseignement seul :**

| Classe | Même sens (15 paires) | Sens différents (138 paires) | Plus proche voisin, leave-one-out |
|---|---|---|---|
| Constructions | moyenne 0,19, maximum **0,538** | moyenne 0,085, maximum 0,538 | 6 / 18 (hasard : 1/7) |
| Lemmes (export V1) | moyenne 0,017, maximum 0,25 | **toujours 0** | 3 / 18 (souvent muet) |

Avec s_max ≤ 0,538, il faudrait **n ≥ 27** exemples par sens pour que la règle actuelle puisse répondre : 0,538 ≥ (n + 2)/(2n) ⇔ n ≥ 26,3. Enrichir le curriculum sans changer les règles (option D seule) est donc **pratiquement impossible**.

**Cause racine, en trois parties :**
1. **Erreur de catégorie.** Le rétrécissement n/(n+2) est un estimateur de **fréquence** (une proportion avec un a priori Beta). Il est appliqué ici à une **similarité maximale**, qui n'est pas une proportion et ne gagne rien à l'augmentation de n.
2. **Échelle non calibrée.** τ = 0,5 est une probabilité, alors qu'un indice de Jaccard entre phrases différentes vit sur une autre échelle (moyenne 0,19 même entre phrases de même sens).
3. **Indépendance stricte.** K3 exige deux classes à provenances disjointes, alors qu'il ne reste que trois classes. La classe lemmes est rarement active, et les contrastes ne concernent que 3 paires corrigées.

**Distinctions demandées :**

| Notion | Rôle |
|---|---|
| similarité brute | signal |
| quantité d'enseignement | n |
| dépendance des preuves | K3 |
| qualité des preuves | précision de la classe |
| rétrécissement | où l'appliquer |
| seuil | τ, δ |
| abstention justifiée | quand le risque estimé est réellement supérieur à 0,5 |

## 2. Options (aucune implémentée)

### A — Seuil fonction du nombre de preuves indépendantes
- **Formule :** τ_k = 0,5 pour k ≥ 2 classes indépendantes, 0,75 pour k = 1.
- **Hypothèse :** les voix sont déjà des probabilités. **Fausse ici**, puisque ce sont des similarités.
- **n faible :** inchangé, toujours bloqué par le rétrécissement. **Surconfiance :** faible ; abstention excessive : **élevée**.
- **Statut :** modifie K3 et la condition 1. **Insuffisante seule.**

### B — Rétrécissement adapté au très petit n
- **Formule :** voix = s_max × (n + c)/(n + 2 + c), avec c > 0, ou bien aucun rétrécissement pour n ≤ 3.
- **Effet :** déplace la borne. À n = 2, sans rétrécissement, il faut encore s_max ≥ 0,5, ce qui reste rare (2 paires de même sens sur 15 au-dessus de 0,5) et **non sélectif** (le maximum entre sens différents vaut aussi 0,538).
- **Surconfiance :** **élevée** (des similarités moyennes deviennent des réponses). **Rejetée** : elle produit des réponses sans fiabilité démontrée.

### C — Séparation fiabilité / classification / décision *(recommandée)*
1. **Classification par classe :** étiquette du **plus proche exemplaire**, uniquement si la similarité est ≥ **s_min = 0,2** (seuil déjà pré-enregistré, réutilisé) ; égalité entre étiquettes différentes → classe muette.
2. **Fiabilité par classe, auto-estimée par l'élève :** leave-one-out sur **ses propres exemples enseignés actifs** (jamais sur un examen) : r_c = (TP_c + 1) / (N_c + 2), soit un **a priori Beta(1,1)**. C'est l'endroit correct pour n/(n+2) : il s'applique à des **comptes de réussites**.
3. **Décision :**
   - **(a)** deux classes indiquent L, provenances disjointes (K3), et p = 1 − ∏(1 − r_c) ≥ τ = 0,5 ;
   - **ou (b)** une seule classe active, sans voix contraire, avec r_c ≥ **0,75** (seuil fixé ici, avant toute mesure) ;
   - et aucune classe ne désigne une autre étiquette (sinon `CONFLIT`, K9).
4. **Pertinence (correctif du témoin négatif) :**
   - les traits de construction présents dans **au moins 50 %** des exemplaires enseignés du mot sont ignorés : ils ne discriminent rien ;
   - s_min s'applique après ce filtrage.
5. **Rappel exact `RAPPEL`, nouvelle origine :** une question identique (même empreinte repliée) à une phrase enseignée active reçoit l'étiquette de cette phrase. Cette réponse est **exclue** des métriques d'acquisition et de transfert : la ligne de base « memorizer » du banc la couvre déjà.

- **n faible :** la fiabilité reste basse tant que l'élève n'a pas vérifié lui-même sa classe, donc il s'abstient ; elle croît avec les réussites internes.
- **Surconfiance :** contenue par le leave-one-out et l'a priori Beta, mais N_c est petit, donc r_c instable (déclaré).
- **Statut :** **déviations substantielles** de K4 (point d'application), K6 (voix = fiabilité, pas similarité), condition 1 (voie b) et K7 (origine `RAPPEL`).

### D — Enrichissement du curriculum sans changer les seuils
- **Formule :** inchangée.
- **Effet :** il faudrait au moins 27 exemples par sens (§1). C'est **inutile seul**, mais **nécessaire avec C** : sur l'enseignement actuel, C ne répond à **aucun** item (§3).
- **Statut :** c'est une modification du **banc** (RED V0.4, nouvel enseignement), donc une **décision séparée** du fondateur.

### E — Une classe forte et des signaux consultatifs
- **Forme :** la classe lemmes, de haute précision (0 recouvrement entre sens différents sur l'enseignement), décide seule ; les constructions et les contrastes ne servent qu'à départager ou à signaler un conflit.
- **Risque :** couverture très faible ; lemmes muets sur les phrases éloignées (X1-far, sans mot plein commun par construction).
- **Statut :** cas particulier de C(b).

## 3. Projections (enseignement et synthétique, sans examen)

| Situation | Résultat de l'option C (règle prototype) |
|---|---|
| **Enseignement actuel**, leave-one-out imbriqué | **0 réponse sur 18.** Fiabilités observées : lemmes 0,75, mais classe presque toujours muette ; constructions 0,35 à 0,47. **L'abstention est justifiée** : répondre par constructions donnerait environ 2 erreurs sur 3. |
| Synthétique, 2 sens, constructions et vocabulaire distinctifs, n = 1 / 2 / 3 / 5 | répond 0 / 2 / 4 / 4 questions sur 8, **toutes justes** |
| Synthétique, contexte mêlant les deux sens | **HOLD** (correct) |
| Synthétique, contexte sans rapport (« Le mot surgit sans prévenir. ») | **réponse L1 (faux positif)** avec le prototype **sans** le filtre de pertinence (point 4) ; ce filtre a été ajouté **à cause** de ce témoin |
| Synthétique, phrase identique à une leçon | HOLD en R4-Core (K3), ce qui motive `RAPPEL` (point 5) |

Ces projections viennent d'un **prototype jetable**, hors dépôt. Elles n'engagent aucun paramètre.

## 4. Recommandation

**C (avec les points 4 et 5) + D**, à décider ensemble :
- C corrige l'erreur de catégorie (rétrécissement sur des comptes, voix = fiabilité), garde τ = 0,5, δ = 0,15 et s_min = 0,2, et ajoute un seul seuil nouveau (0,75 pour la voie à une classe) ;
- **sur l'enseignement actuel, C ne répondra quasiment jamais**, et c'est le comportement correct ;
- R4.3 ne produira de réponses vérifiables qu'avec un curriculum enrichi (D), donc un RED V0.4 avec plus de leçons par sens, rédigé sans examen.

**Coûts :** calcul du leave-one-out interne à chaque mise à jour (18 à 50 items : négligeable) ; nouveaux tests (voir le protocole).

**Risques :** fiabilité estimée sur de très petits N ; faux positifs de construction si le filtre de pertinence ne suffit pas ; `RAPPEL` mal interprété comme apprentissage.

**Réfutation :**
- si, sur l'enseignement actuel, C répond avec une précision < 0,5, C est réfutée ;
- si elle répond à un témoin négatif synthétique, C est réfutée ;
- si un curriculum enrichi ne fait monter ni la couverture ni la précision, l'hypothèse « le goulot est le curriculum » est réfutée.

**En cas d'échec :** R4 est clos comme résultat négatif documenté ; V0 reste la référence.

## 5. Frontières

- Aucun raccordement à Brody, SENS, OS Trad, Native Memory, M42, B11 ou KX108.
- La fiabilité locale ne remplace ni Thermo ni Sigma ; Sigma reste consultatif, GuardX108 garde la frontière de gouvernance, et l'autorité reste **KX108_ONLY**.
- R4.3 n'est pas la naissance d'Oxygen.

## 6. Paramètres proposés, à figer après relecture

| Paramètre | Valeur | Origine |
|---|---|---|
| τ | 0,5 | inchangé |
| δ | 0,15 | inchangé |
| s_min | 0,2 | seuil pré-enregistré, réutilisé |
| A priori de fiabilité | Beta(1, 1) | nouveau |
| τ_1 (voie à une classe) | **0,75** | **nouveau** |
| Filtre de pertinence | traits présents dans ≥ 50 % des exemplaires du mot | **nouveau** |
| Proximité K1 | désactivée | inchangé |
| P-LEX, P-ALIGN | HOLD | inchangé |
