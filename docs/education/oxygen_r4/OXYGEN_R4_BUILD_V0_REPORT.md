# Oxygen R4 — build isolé V0 : rapport (export réalisé, élève en HOLD_CONTRACT)

**Date :** 2026-10-22 · **Auteur :** Claude (contaminé par les examens de développement) · **Base :** `1e2ef216` (conception R4.1 `a27b3bc2…`, pré-enregistrement `8406dcf1…`).
**Statut :** expérimental, non canonique. Aucun élève R4 écrit, aucune évaluation de développement, aucune prospective, aucune intégration.

## 1. Phase 0 : préflight

HEAD `1e2ef216`, arbre propre. `SHA256SUMS.txt` de `docs/education/oxygen_r4/` vérifié. V0 inchangé (`exemplar_student.py` `aebbc335…`, `features.py` `91b8dec5…`). Banc RED V0.3 inchangé depuis `00cc85fc`. Corpus inchangé (`lexicon.db` `0a58bdb4…`, `MANIFEST.json` intact). Examens non lus.

## 2. Phase 1 : export lexical minimal (réalisé)

**Outil :** `tests/education_pilot/r4_lexicon_export.py`.
- Sélection **par règle** (pré-enregistrement §7) : `thes_fr` (FR) et Morphalou (FR, `DISTINCT surface_form, lemma, pos`).
- Exclus : Littré, UniMorph français, OEWN, FreeDict, UniMorph anglais, exceptions WordNet.
- Base ouverte en `mode=ro&immutable=1`, et son empreinte est vérifiée avant l'export (HOLD si elle diffère).
- Écriture **refusée** dans le dépôt.

**Sortie privée, hors dépôt :** `C:\Users\User\Documents\OBSIDIA_HANDOFF\oxygen_r4_lexicon_export\v1\` (65 Mo au lieu de 530).

| Fichier | Lignes | sha256 |
|---|---|---|
| `thes_fr.jsonl` | 37 205 | `378e4809508a1ac6cc4e6bfb7ea840125606410b16c69adf72bc22ff531188de` |
| `morphalou_fr.jsonl` | 812 825 (triplets distincts) | `9e6e60da4b771bb8726838a877a227e5d2ebd7778f6e3ec6fe10d0adc31fdee6` |
| `thes_fr_mcible.jsonl` (variante M-CIBLE) | 37 188 | `9b2f4d82e0845bd0d51215d91973c66e4bd2db35a3d93b32bd7dacbd3d46331a` |
| `MANIFEST.json` | — | `4ef57e9ac3bd6f033c6d3de9bb443a3b6dc4e90b61a11e853ff5db44fac8b285` |

**Détails de l'export :**
- Formes à lemmes multiples conservées : **45 457**. Toutes les lignes candidates sont gardées ; aucun choix n'est fait à l'export.
- M-CIBLE : cibles = les mots enseignés, dérivés des données d'enseignement par règle, soit `chemin`, `corriger` et `force` (« table » n'est jamais enseigné). Les entrées de ces lemmes sont retirées (17 entrées), ainsi que leurs **43 formes** des listes de synonymes ; les autres relations restent.
- **Stabilité :** deux générations indépendantes donnent des empreintes identiques.
- **Tests :** `tests/education_pilot/test_r4_lexicon_export.py`, **6 / 6**. Ils couvrent le refus d'écrire dans le dépôt, la régénération identique, les sources et règles, le tri canonique, la conservation des lemmes ambigus et le masquage M-CIBLE.
- Contamination : le contrôle indépendant antérieur (pré-enregistrement §9) a trouvé des recoupements uniquement dans le Littré, qui est exclu. Aucun nouveau contrôle n'est requis tant que l'export ne contient ni Littré ni définitions.

## 3. Phase 2 et 3 : élève R4, **HOLD_CONTRACT**

À la lecture intégrale, la conception R4.1 et le pré-enregistrement **ne définissent pas** plusieurs mécanismes que l'élève doit implémenter. Les définir maintenant reviendrait à faire des choix de conception **après** avoir été exposé aux examens de développement, et sans relecture, ce que la consigne interdit (« ne pas improviser : HOLD avec le contrat concerné »).

| # | Contrat manquant | Référence | Pourquoi c'est matériel |
|---|---|---|---|
| **K1** | **Calcul de la classe « alignement de la cible »** : comment un groupe de sens du corpus pour le lemme cible est relié à une étiquette enseignée, et comment on en tire une voix pour une question | pré-enregistrement §2, ligne 26 ; conception §B, élément 3, et capacité 7 | c'est la **seule classe fondée sur le corpus** encore active depuis l'échec de P-LEX. Elle porte les configurations C et D, H3, H3b et M-CIBLE. |
| **K2** | **Règle générique de négation** des contrastes (« A, pas B ») et passage de la correction à une voix | conception §B, capacité 3 ; lacune 3 | les textes de correction contiennent les identifiants de sens ; la règle détermine ce qui est appris |
| **K3** | **Concordance** de « deux classes indépendantes » (même sens en tête ? voix au-dessus d'un seuil ?) | pré-enregistrement §2, condition 1 | elle décide de toute réponse ou de toute abstention |
| **K4** | **Application du rétrécissement** n / (n + 2) : sur la voix des exemplaires, sur le score final avant les seuils 0,5 et 0,15, ou sur une « confiance » distincte | pré-enregistrement §2 ; conception §C (« par exemple ») | elle déplace l'abstention |
| **K5** | Définition d'un **« voisin déterminant »** (condition 4, `MOT_INCONNU`) | pré-enregistrement §2, condition 4 ; capacité 5 | elle décide de l'abstention `MOT_INCONNU` |
| **K6** | Formules des voix **constructions** et **exemplaires** (similarité, normalisation dans [0, 1]) | pré-enregistrement §2 | elles constituent le cœur du score |
| **K7** | Attribution de l'origine **`TRANSFERE`** maintenant que la proximité (`INTERPRETE_CORPUS`) est désactivée | doctrine, origines | elle détermine la métrique principale (D − C hors `PREALABLE`) |

**Contrats supplémentaires relevés par l'audit** (à fixer aussi en R4.2) :

| # | Contrat manquant | Référence |
|---|---|---|
| **K8** | la conception §C exige que « le risque estimé [soit] sous le seuil », alors que le pré-enregistrement §2 ne reprend pas ce critère : incohérence à trancher | conception §C ; pré-enregistrement §2 |
| **K9** | règle quantifiée distinguant `CONFLIT` de `PREUVE_INSUFFISANTE` | conception §B, capacité 5 |
| **K10** | comportement de la configuration C (corpus sans leçons) : quelles mesures autres que HOLD peut-elle produire ? | pré-enregistrement §3 |

**Conséquences :**
- l'invariant P-LEX (test qui échoue si la proximité est réactivée) dépend du code de l'élève ; il est **reporté** avec lui ;
- les configurations A, B, C et D, les ablations et les tests d'interface ne sont **pas exécutés**.

**Pour lever le HOLD :** une révision **R4.2**, purement contractuelle, doit fixer K1 à K7 a priori. Elle doit être :
- rédigée sans consulter les examens et justifiée par l'enseignement et des principes génériques ;
- **relue par un relecteur non contaminé** ;
- verrouillée par empreinte avant toute ligne de code de l'élève.

Les seuils et poids déjà pré-enregistrés restent inchangés.

## 4. Audit indépendant : **PASS_WITH_NB**

- L'export est conforme au §7, régénéré **à l'octet près** par l'auditeur (y compris `MANIFEST.json`), avec les empreintes réelles déclarées.
- Le HOLD_CONTRACT est **justifié** : K1 à K7 ne sont réellement pas spécifiés, et les implémenter aurait relevé de STOP_CIRCULAR. Ce n'est pas un arrêt prématuré.
- Aucune mutation constatée.

**Remarques non bloquantes :**
- **NB1 :** M-CIBLE masque les formes exactes de la cible, mais pas les synonymes **en plusieurs mots** qui la contiennent (par exemple « chemin de fer »). C'est conforme à la lettre du §4, mais discutable pour H3b : **à trancher en R4.2**.
- **NB2 :** `morphalou_fr.jsonl` sert aux deux variantes ; les formes des cibles y restent. C'est voulu, puisque la cible est fournie par la question et n'est jamais lemmatisée.
- **NB3 :** le test de régénération compare désormais aussi `MANIFEST.json` (corrigé, sans toucher à l'outil).
- **NB4 :**
  - le test « pas de définitions » ne lit que les 10 000 premiers caractères, mais il est doublé par le test sur les clés exactes ;
  - les cibles M-CIBLE dépendent de `_pilot_data`, donc tout ajout de leçon changerait la variante (l'empreinte est figée).
- **NB5 :** le refus d'écrire dans le dépôt ne résout pas `ROOT` lui-même ; il serait fragile si le dépôt était atteint par un lien symbolique. L'outil n'est pas modifié dans cette passe, pour ne pas changer `tool_sha256` du manifeste.

## 4. Mutations

**Dans le dépôt** (non commité avant audit) :
- `tests/education_pilot/r4_lexicon_export.py` ;
- `tests/education_pilot/test_r4_lexicon_export.py` ;
- ce rapport.

**Hors dépôt :** l'export privé (`OBSIDIA_HANDOFF\oxygen_r4_lexicon_export\v1`).

**Non touchés :** V0, le banc RED, les examens, le corpus, AGY, B8, B9, B10, SENS, Brody.
