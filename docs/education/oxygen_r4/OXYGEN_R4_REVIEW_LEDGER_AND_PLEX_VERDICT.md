# Oxygen R4 — registre des revues et verdict P-LEX

**Statut :** archive documentaire, **expérimentale et non canonique**. Aucun build, aucun export du corpus.

## 1. Généalogie de la conception

| Révision | Fichier | Revue indépendante | Verdict | Cause principale |
|---|---|---|---|---|
| Recherche R4 V0 | `OXYGEN_R4_RESEARCH_V0.md` | non relue isolément | — | contenait des erreurs (OS Trad dit « introuvable », AVDR et Continuum sous-estimés, diagnostic V0 mal mesuré) |
| Réconciliation V0.1 | `OXYGEN_R4_RESEARCH_V0_1_SOURCE_RECONCILIATION.md` | oui | **PASS_WITH_NB** | corrige E1 à E5 de la recherche V0 |
| Conception R0 | `r4_design_history/…_R0.md` | oui | **APPROVE_WITH_CHANGES** | B1 : les `sense_id` sont propres au lemme, donc aucun transfert entre mots |
| Conception R1 | `r4_design_history/…_R1.md` | oui | **FAIL** | recouvrement de synonymes non pondéré : **23 faux rapprochements sur 26** sur l'enseignement |
| Conception R2 | `r4_design_history/…_R2.md` | oui | **PASS_WITH_NB** | garde-fous (a)–(f) ; 5 remarques (formule sous-spécifiée, support P-LEX, explication des comptes, métrique principale, capacité 3) |
| Conception R3 | `r4_design_history/…_R3.md` | indirecte (audit de clôture) | — | remarques de R2 intégrées ; lemmatisation ambiguë non spécifiée |
| Conception R4 | `r4_design_history/…_R4_audited.md` | oui (clôture) | **PASS_WITH_NB** | résultat P-LEX enregistré ; remarques NB1 à NB6 (départage du script, support absent du §A, restes anciens, double sens de « C », robustesse, antériorité des seuils) |
| **Conception R4.1** | `OXYGEN_R4_COGNITIVE_LEARNING_DESIGN_V0.md` | contre-vérification finale : voir §4 | — | corrections rédactionnelles seulement |

Aucun PASS_WITH_NB n'est requalifié en PASS. Toutes les réserves restent en vigueur.

## 2. Verdict P-LEX

| Champ | Valeur |
|---|---|
| **P_LEX** | **HOLD**, couche **désactivée** |
| RETAINED_PAIRS | **5** |
| MIN_PAIRS | 10 |
| PRECISION | **0,40** |
| MIN_PRECISION | 0,50 |
| Détail | TP / FP / FN / TN = 2 / 3 / 111 / 963 ; rappel 0,018 ; rapport de discrimination 5,7 (sur 5 paires) ; 152 paires indécidables ; 191 ambiguës écartées |
| Robustesse | lemmatisation stricte : 2 retenues ; ambiguës réintégrées : 8 retenues, précision 0,25 ; même verdict |
| Reproductibilité | `plex_measure_r4.py` (sha256 consigné dans la conception R4.1) ; base `lexicon.db` `0a58bdb4…16a` en lecture seule ; **recalcul indépendant identique** lors de l'audit de clôture |
| Limite chronologique | l'antériorité des seuils (0,2 ; 0,5 ; 3 depuis R2 ; support ≥ 10 depuis R3) **n'est établie que par la généalogie des fichiers** hors dépôt, sans horodatage externe. Ce commit en est la première trace git. |

**Règles pour le futur build :**
- la proximité lexicale entre concepts est **désactivée** (poids 0) ;
- elle ne peut être **réactivée** ni implicitement ni explicitement sans une nouvelle révision relue, une nouvelle mesure P-LEX et des seuils inchangés ;
- le corpus lexical préalable reste **autorisé** (décision du fondateur), mais son apport est séparé de celui des leçons par les configurations B, C et D et par la métrique principale D − C hors `PREALABLE`.

## 3. Limites de provenance du corpus

- `MANIFEST.json` liste 6 sources, alors que la base en a 8. UniMorph français et les exceptions WordNet sont attribués seulement dans la table `sources` et dans `INGESTION_REPORT.json`. UniMorph français est **exclu** du futur export jusqu'à correction du manifeste.
- `total_lemmas` = 843 969 est la somme des imports. La table `lemmas` a 663 134 lignes, dont 616 326 triplets distincts.
- Les `sense_id` du thésaurus sont des numéros d'import, instables d'une version à l'autre.
- Les droits paraissent compatibles avec un usage interne de recherche, avec attribution, sans redistribution. **Ce n'est pas un avis juridique.**
- Contamination : un contrôleur indépendant n'a trouvé aucune phrase d'examen ni séquence de 6 tokens ou plus. Les recoupements de 4 tokens viennent uniquement du Littré, qui est exclu de l'export.
- **Export : non exécuté.**

## 4. Contre-vérification finale de R4.1

Vérificateur indépendant, sur la version finale. Verdict : **PASS_WITH_NB**.

- Empreintes conformes : conception `a27b3bc2…f0ccd`, pré-enregistrement `8406dcf1…df74`. L'empreinte citée dans le pré-enregistrement est l'empreinte réelle.
- Le diff entre R4 auditée et R4.1 est **uniquement rédactionnel**. Aucun seuil (0,2 ; 0,5 ; 3 ; 10), poids, mécanisme ou hypothèse n'a changé.
- La proximité lexicale est désactivée partout.
- Le registre est fidèle ; aucun PASS_WITH_NB n'est requalifié.

**Remarque restante (NB4 partiellement appliquée) — erratum.** La conception R4.1 n'est pas réécrite, pour garder son empreinte. La lecture suivante **fait foi** :

| Ligne de la conception R4.1 | Texte | Lire |
|---|---|---|
| 119 | « l'option C se réduit… » | « l'architecture **ARCH-C** se réduit… » |
| 214 | « C est le plus coûteux) : C est le seul… » | « **ARCH-C** est la plus coûteuse) : **ARCH-C** est la seule… » |
| 223 | « si C ne dépasse pas A » | « si la configuration **D (ARCH-C complète)** ne dépasse pas la configuration **A (V0)**, ni **ARCH-A** » |
| 260 | « mécanisme de transfert de C » | « mécanisme de transfert d'**ARCH-C** » |
| 269 | « conditionne C… A ou B » | « conditionne **ARCH-C**… **ARCH-A** ou **ARCH-B** » |

Partout ailleurs, A, B, C et D désignent les **configurations** du pré-enregistrement.
