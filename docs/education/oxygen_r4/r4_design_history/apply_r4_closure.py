import pathlib, shutil
d = pathlib.Path(__file__).parent
des = d / "OXYGEN_R4_COGNITIVE_LEARNING_DESIGN_V0.md"
pre = d / "OXYGEN_R4_PREREGISTRATION_DRAFT_V0.md"
shutil.copy(des, d / "OXYGEN_R4_COGNITIVE_LEARNING_DESIGN_V0_R3.md")
shutil.copy(pre, d / "OXYGEN_R4_PREREGISTRATION_DRAFT_V0_R3.md")
s = des.read_text(encoding="utf-8")


def R(a, b):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, 1)


R("— révision R3 (conception seule)", "— révision R4 (conception seule)")
R("R3 intègre la vérification de R2",
  "R4 enregistre le **résultat P-LEX mesuré sur l'enseignement (échec : classe « proximité des voisins » désactivée, conformément à la règle pré-enregistrée)** et spécifie la **lemmatisation ambiguë**, que R3 laissait ouverte. R3 intègre la vérification de R2")
R("**Critère de réfutation chiffré P-LEX, préalable à tout build de cette classe :**",
  """**Lemmatisation ambiguë (R4) :** une forme dont l'export propose plusieurs lemmes est représentée par l'**ensemble** de ses lemmes candidats, sans en choisir un. Les classes qui comparent des lemmes (exemplaires) utilisent l'indice de Jaccard sur ces ensembles. Le lemme **cible** n'est jamais ambigu : c'est le mot fourni par la question. Une forme sans lemme n'a pas de voisinage et ne compte dans aucune classe lexicale.

**Résultat P-LEX (mesuré le 2026-10-22, enseignement seul, formule R3, seuils inchangés)** — 18 items de « force », 55 occurrences de mots pleins, paires de voisins de leçons différentes :

| Mesure | Valeur |
|---|---|
| TP / FP / FN / TN | 2 / 3 / 111 / 963 |
| Paires retenues (≥ 0,2) | **5** (minimum exigé : 10) |
| Précision | **0,40** (exigé : ≥ 0,5) |
| Rappel | 0,018 |
| Rapport de discrimination | 5,7 (calculé sur 5 paires) |
| Paires indécidables (au moins un mot sans voisinage) | 152 |
| Paires à lemmatisation ambiguë (écartées dans cette mesure) | 191 |

**Verdict P-LEX : échec** (support insuffisant et précision < 0,5). La classe « proximité des voisins » est **désactivée** (poids 0). La capacité 7 (transfert par voisinage lexical) est **réfutée sur l'enseignement** pour cette formule. Les autres classes ne sont pas affectées. Toute nouvelle formule exigerait une révision relue et une nouvelle mesure P-LEX, **sans** changer les seuils.

**Critère de réfutation chiffré P-LEX, préalable à tout build de cette classe :**""")
R("| 7. Transférer vers un contexte inédit | proximité lexicale pondérée entre un voisin inédit et des voisins enseignés, **un seul saut, sans transitivité** | **non démontré** : réfuté d'avance si P-LEX échoue (voir ci-dessous) |",
  "| 7. Transférer vers un contexte inédit | **(R4) P-LEX a échoué : la proximité des voisins est désactivée.** Le transfert ne repose plus que sur les constructions et l'alignement de la cible sur le corpus. | **non démontré** ; le transfert lexical par voisinage est réfuté sur l'enseignement |")
des.write_text(s, encoding="utf-8", newline="\n")

s = pre.read_text(encoding="utf-8")
R("**Conception :** `OXYGEN_R4_COGNITIVE_LEARNING_DESIGN_V0.md`, **R3** (empreinte au §8).",
  "**Conception :** `OXYGEN_R4_COGNITIVE_LEARNING_DESIGN_V0.md`, **R4** (empreinte au §8).")
R("| Proximité lexicale des voisins (garde-fous (a)–(f), seuil 0,2) | ≤ 1 | 1, **ou 0 si P-LEX échoue** |",
  "| Proximité lexicale des voisins (garde-fous (a)–(f), seuil 0,2) | — | **0 : désactivée** (P-LEX en échec, mesure du 2026-10-22, conception R4) |")
R("| **SANS-PROX** | classe « proximité des voisins » à 0 | apport de la proximité lexicale (si P-LEX a été satisfait) |",
  "| **SANS-PROX** | **sans objet** : la classe est déjà désactivée | — |")
R("**Gain propre à l'enseignement, métrique principale (H2, H3) :**", """**Limites d'interprétation :**
- **B − A** compare deux architectures différentes (V0 : bayésien naïf, k-NN et traits ; R4 : vote par classes). Un écart mesure l'architecture **et** son usage des leçons, sans pouvoir les séparer.
- **D − C** isole l'apport des leçons à ressource égale. Ce n'est **pas** à lui seul une preuve de compréhension causale : il faut aussi les ablations, la provenance par origine et la prospective indépendante.
- Pour chaque item, on journalise : la réponse avant enseignement (T0 de D, et C), la réponse après, et si elle **a été modifiée par les leçons**. On publie la part des réponses justes **déjà disponibles avant apprentissage** et la part **réellement modifiées** par les leçons.

**Gain propre à l'enseignement, métrique principale (H2, H3) :**""")
R("| P-LEX | la proximité pondérée discrimine les étiquettes |", "| P-LEX (**ÉCHEC mesuré, R4**) | la proximité pondérée discrimine les étiquettes |")
R("**Sources utilisées par l'export minimal :**", """**Réconciliation de la provenance :**

| Fait | Explication |
|---|---|
| `MANIFEST.json` : 6 jeux de données ; table `sources` : 8 | les deux en plus sont **UniMorph français** (formes FR, CC-BY-SA 4.0, somme de contrôle `4760fc36…`) et les **exceptions WordNet 3.0** (anglais, licence de type BSD, `cbda5ea6…`). Ils sont présents dans `sources` et dans `INGESTION_REPORT.json`, absents du manifeste. |
| `total_lemmas` = 843 969 | somme des `lemmas_imported` des 8 sources (Morphalou 159 182 ; UniMorph anglais 427 464 ; OEWN 135 909 ; thes_fr 36 452 ; XMLittré 76 488 ; FreeDict 8 474 ; UniMorph français et WordNet 0). Ce n'est pas un décompte de table. |
| Table `lemmas` : 663 134 lignes | seules 3 sources y écrivent (Morphalou, UniMorph anglais, XMLittré). Les lemmes d'OEWN, de thes_fr et de FreeDict ne vivent que dans `senses`. **616 326** triplets distincts (lemme, langue, catégorie) : des doublons existent **entre** sources. La formulation de R3, « lemmes effectivement distincts : 663 134 », est **corrigée**. |
| Formes : 2 002 724 importées contre 1 892 839 en table | déduplication par la contrainte `UNIQUE` d'`inflections` (UniMorph français 367 732 importées → 261 309 conservées ; WordNet 5 945 → 3 012 ; Morphalou 976 570 → 976 427 ; UniMorph anglais 652 477 → 652 091) |

**Sources utilisées par l'export minimal :**""")
R("| UniMorph français | 4.0 | CC-BY-SA 4.0 | lemmatisation (261 309 formes FR) |",
  "| ~~UniMorph français~~ | 4.0 | CC-BY-SA 4.0 | **exclu** de l'export tant que le manifeste ne l'attribue pas (attribution présente seulement dans `sources` et le rapport d'ingestion). Décision prise **avant** l'export et sans regard aux examens. |")
R("2. `inflections WHERE lang='fr'`, colonnes distinctes `surface_form`, `lemma`, `pos` ;",
  "2. `inflections WHERE lang='fr' AND source_id='morphalou_3_1'`, colonnes distinctes `surface_form`, `lemma`, `pos` ;")
R("| Conception R3 |", "| Conception R4 |")
pre.write_text(s, encoding="utf-8", newline="\n")
print("ok")
