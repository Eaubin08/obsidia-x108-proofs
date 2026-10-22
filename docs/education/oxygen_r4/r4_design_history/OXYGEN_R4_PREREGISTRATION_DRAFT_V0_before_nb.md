# Oxygen — R4 : pré-enregistrement expérimental (BROUILLON, non verrouillé)

**Statut :** brouillon. **Pas de FREEZE canonique Obsidia.** Le verrouillage n'interviendra qu'après la vérification indépendante de la conception R2 et le contrôle de contamination du corpus.
**Décision fondateur :** `LEXIQUE_PREALABLE=YES`. Aucun build, aucun runtime, aucune écriture mémoire.
**Conception :** `OXYGEN_R4_COGNITIVE_LEARNING_DESIGN_V0.md`, R2 (sha256 `0983a60c…`, à confirmer après vérification).

## 1. Décisions architecturales

- **Option C**, hybride. Les classes de preuve sont les suivantes :
  - constructions ;
  - exemplaires ;
  - alignement de la cible sur le corpus ;
  - proximité lexicale pondérée des voisins, **conditionnelle à P-LEX** ;
  - contrastes issus des corrections.
- **Option A** (V0) est la référence figée.
- SENS n'est pas utilisé dans R4 V0 : sa couverture est de 2 / 18 sur les phrases pédagogiques. Une éventuelle copie vendorisée relèverait d'une décision ultérieure.
- OS Trad, AVDR, Continuum, Native Memory, MMonde et les 34 arbres ne sont pas utilisés : leur utilité au sens lexical n'est pas démontrée. Aucun moteur parallèle n'est créé.
- La mémoire est locale (`/state`), le corpus est en lecture seule, l'autorité reste `KX108_ONLY`, et aucune promotion n'a lieu.

## 2. Classes de preuve, poids et abstention (fixés a priori)

| Classe | Voix | Poids |
|---|---|---|
| Constructions (schéma autour de la cible, sans morceaux de mots comme preuve) | ≤ 1 | 1 |
| Exemplaires (similarité de constructions et de lemmes) | ≤ 1 | 1 |
| Alignement de la cible (groupes de sens du corpus pour le lemme cible, reliés aux étiquettes enseignées) | ≤ 1 | 1 |
| Proximité lexicale des voisins (garde-fous (a)–(f), seuil 0,2) | ≤ 1 | 1, **ou 0 si P-LEX échoue** |
| Contrastes (« A, pas B ») | ≤ 1 | 1 |

Chaque voix est normalisée dans [0, 1]. Le score d'un sens est la moyenne pondérée des voix. La confiance d'un sens subit un **rétrécissement** n / (n + 2), où n est le nombre d'exemplaires du sens.

**Réponse** seulement si les quatre conditions sont réunies :
1. au moins **deux classes indépendantes** concordent sur le même sens ;
2. le score du premier sens est ≥ 0,5 ;
3. l'écart avec le second sens est ≥ 0,15 ;
4. aucun voisin déterminant n'est inconnu du corpus.

**Sinon HOLD, avec un motif :** `MOT_INCONNU`, `PREUVE_INSUFFISANTE` ou `CONFLIT`. Un mot jamais enseigné donne HOLD.

**Origine de chaque preuve :** `PREALABLE`, `INTERPRETE_CORPUS`, `ACQUIS_LECON`, `CORRIGE`, `TRANSFERE` ou `INCERTAIN`, journalisée dans la provenance.

## 3. Configurations comparées (même jeu, un passage chacune)

| Config | Code | Corpus | Leçons et corrections | Rôle |
|---|---|---|---|---|
| **A** | V0 figé (`dfef4f98`) | non | oui | référence historique |
| **B** | R4 | **non** (classes corpus à 0) | oui | apport des leçons seules dans l'architecture R4 |
| **C** | R4 | oui | **non** (aucun `learn`, aucune correction) | savoir lexical initial ; l'élève ne connaît pas les étiquettes enseignées, donc il répond HOLD sur les items étiquetés, sauf les mesures listées ci-dessous |
| **D** | R4 | oui | oui | configuration complète |

**Mesures par configuration :**
- exactitude et abstention T0 (avant enseignement) et T1 à T4 ;
- gain T1 − T0 ;
- calibration : HOLD approprié et injustifié, erreurs non abstenues ;
- provenance par origine ;
- part des réponses justes appuyées sur `TRANSFERE`.

**Contrastes :**

| Effet | Calcul |
|---|---|
| Avantage du corpus | D − B |
| Avantage des leçons | D − C |
| Interaction corpus × enseignement | (D − B) − (C − socle sans corpus ni leçons, ≡ HOLD partout) |
| Apport de R4 | D − A et B − A |

**Gain propre à l'enseignement :** D − C. Comme les étiquettes n'existent pas avant les leçons, C mesure ce que le corpus permet **sans** enseignement : connaissance des mots, détection de l'inconnu, abstention. Une réponse juste de D dont la seule preuve est d'origine `PREALABLE` n'est **pas** comptée comme apprentissage.

## 4. Ablations

| Ablation | Contenu | Question |
|---|---|---|
| **M-CIBLE** | masquer dans l'export toutes les entrées du **lemme cible** (« force », « chemin », « corriger ») **et** ses occurrences dans les listes de synonymes des autres lemmes ; toutes les autres relations restent | la réponse vient-elle de la récupération directe du sens de la cible, ou d'un transfert par les voisins ? |
| **SANS-PROX** | classe « proximité des voisins » à 0 | apport de la proximité lexicale (si P-LEX a été satisfait) |
| **SANS-CONTRASTE** | classe « contrastes » à 0 | apport des corrections contrastives (H4) |
| **SANS-CUE-CIBLE** | classe « alignement de la cible » à 0 | équivalent fonctionnel de M-CIBLE sans changer l'export |

Toutes les ablations sont des **configurations déclarées ici** et exécutées dans le même passage unique.

## 5. Hypothèses réfutables

| # | Hypothèse | Épreuve | Échec |
|---|---|---|---|
| P-LEX | la proximité pondérée discrimine les étiquettes | enseignement seul : précision ≥ 0,5 et rapport ≥ 3 | classe désactivée |
| H1 | le vote par classes réduit les erreurs assurées | leave-one-out sur l'enseignement : moins de 6 / 18 erreurs non abstenues, sans moins de 7 justes | calibration réfutée |
| H2 | D dépasse la meilleure ligne de base, avec la marge, sur T1 et X1-far | prospective indépendante | égalité ou moins |
| H3 | le gain vient du corpus | D − B > 0 | ≤ 0 |
| H3b | le gain n'est pas une simple récupération du sens de la cible | D sous M-CIBLE reste > B | effondrement vers B |
| H4 | les contrastes aident les sens proches | D − SANS-CONTRASTE > 0 sur les sens proches | ≤ 0 |
| H5 | l'abstention est calibrée | HOLD injustifié ≤ 0,2 et approprié ≥ 0,5 | dépassement |
| H6 | la mémoire et les révisions sont intactes | 7 tests d'interface | régression |

**Échantillons techniques :** aucune conclusion statistique. La campagne scientifique future exige au moins 20 items par sens.

## 6. Critères d'arrêt

- **STOP_LEAK** : un contrôle d'isolation ou de fragments est rouge.
- **STOP_CIRCULAR** : un identifiant de sens ou un mot indice apparaît dans le code de l'élève, ou une sélection du corpus a été faite à la main.
- **STOP_PROTOCOL** : un changement du banc ou des examens apparaît nécessaire.
- **STOP_CONTAMINATION** : le contrôleur indépendant trouve des fragments d'examen (≥ 6 tokens) dans l'export.
- **STOP_OVERFIT** : la différence entre développement et prospective est > 0,3. C'est indicatif, la prospective fait foi.
- **Budget :** 2 itérations de build, chacune suivie d'un audit.

## 7. Ressource : dépendances, export, droits

**Source :** `data/linguistic_corpus/lexicon.db`.

| Propriété | Valeur |
|---|---|
| sha256 | `0a58bdb4c9094f06aaa92f3c545a9c9ef411eeeb4daf52f06b54c191e2eca16a` |
| taille | 530 Mo |
| schéma | `BRODY_LINGUISTIC_CORPUS_V1` |
| créée le | 2026-10-17 08:46:06 UTC (horodatage de métadonnée) |
| suivi git | non suivie (ignorée par git) ; seuls `MANIFEST.json` et `INGESTION_REPORT.json` le sont |

**Sources utilisées par l'export minimal :**

| Source | Version | Licence | Usage dans R4 |
|---|---|---|---|
| Dicollecte / LibreOffice `thes_fr` | 7.0 | MPL 2.0 / LGPL 3.0 / GPL 3.0 | groupes de synonymes (37 205 entrées) |
| Morphalou | 3.1 (06/2016) | LGPL-LR (ATILF CNRS / ORTOLANG) | lemmatisation (976 427 formes FR) |
| UniMorph français | 4.0 | CC-BY-SA 4.0 | lemmatisation (261 309 formes FR) |

**Sources non exportées :** XMLittré (CC-BY-SA 3.0, définitions jusqu'à 400 caractères, qui peuvent contenir des citations), OEWN (anglais), FreeDict, UniMorph anglais, exceptions WordNet.

**Export minimal, déterministe et reproductible.** Il est **défini par règle**, jamais par liste de mots :
1. `senses WHERE source_id='thes_fr' AND lang='fr'`, colonnes `lemma`, `pos`, `sense_id`, `synonyms` ;
2. `inflections WHERE lang='fr'`, colonnes distinctes `surface_form`, `lemma`, `pos` ;
3. tri lexicographique complet, sérialisation canonique (SQLite reconstruite par insertions triées, ou JSONL trié en UTF-8), et empreinte sha256 consignée **avant** la rédaction de tout jeu prospectif R4 ;
4. variante **M-CIBLE** produite par la même règle, plus le masquage du §4, avec sa propre empreinte.

**Métadonnées à signaler :**
- `MANIFEST.json` liste 6 sources, alors que la base et `INGESTION_REPORT.json` en ont 8 (UniMorph français et les exceptions WordNet n'y figurent pas) ;
- `metadata.total_lemmas` vaut 843 969, alors que la table `lemmas` en compte 663 134 (écart de comptage : formes UniMorph français sans lemme) ;
- les `sense_id` du thésaurus sont des numéros séquentiels d'import (`thes_fr_N`), qui ne sont **pas** des identifiants stables d'une version à l'autre.

**Droits :** l'usage interne de recherche, sans redistribution, est compatible avec les licences déclarées, à condition d'attribuer les sources (ATILF CNRS / ORTOLANG, Dicollecte / LibreOffice, UniMorph). L'export reste **privé**, hors dépôt, et ne doit pas être publié. Toute redistribution, y compris dans un dépôt public, exige une revue de licence : LGPL-LR, MPL / LGPL / GPL et CC-BY-SA, avec obligations de partage à l'identique pour les œuvres dérivées. **Ce n'est pas un avis juridique.**

**Contamination :** le contrôle par un contrôleur indépendant (contaminé volontairement, exclu de toute rédaction d'examen) porte sur la présence de fragments des épreuves de développement dans le corpus. Il rapporte uniquement des comptes agrégés. Résultat : voir le §9. Le même contrôle sera refait par l'opérateur sur le futur jeu indépendant.

## 8. Empreintes à verrouiller

| Objet | Empreinte |
|---|---|
| Conception R2 | `0983a60c…`, après vérification |
| Ce pré-enregistrement | à calculer au verrouillage |
| Export du corpus et variante M-CIBLE | à calculer **au début du build**, par l'outil d'export, puis consignées avant tout passage d'examen |
| Base source | `0a58bdb4…16a` |

## 9. Contrôle de contamination du corpus

Contrôleur indépendant, sur la base complète ouverte en lecture seule (`mode=ro&immutable=1`), sur 64 phrases d'examen de développement et 22 phrases d'enseignement. Il n'a rapporté que des comptes :

| Mesure | Examens | Enseignement |
|---|---|---|
| Phrase entière contenue dans un champ | 0 | 0 |
| Séquence commune ≥ 6 tokens | 0 | 0 |
| Séquence commune ≥ 4 tokens | 13 / 64, **uniquement XMLittré** | 8 / 22, uniquement XMLittré |
| Canari | absent | — |

**Verdict : `CORPUS_EXAM_FRAGMENTS = INCIDENTAL`.** Il s'agit de tournures françaises courantes. Les examens en recoupent proportionnellement moins que l'enseignement.

**XMLittré est exclu de l'export minimal** : l'export n'utilise que `thes_fr` et les formes morphologiques. Les seuls recoupements observés sont donc écartés par construction. Le contrôle sera refait par l'opérateur sur le futur jeu indépendant.
