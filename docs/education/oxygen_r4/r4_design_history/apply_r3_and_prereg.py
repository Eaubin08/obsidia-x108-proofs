import pathlib, shutil
d = pathlib.Path(__file__).parent
des = d / "OXYGEN_R4_COGNITIVE_LEARNING_DESIGN_V0.md"
pre = d / "OXYGEN_R4_PREREGISTRATION_DRAFT_V0.md"
shutil.copy(des, d / "OXYGEN_R4_COGNITIVE_LEARNING_DESIGN_V0_R2.md")
shutil.copy(pre, d / "OXYGEN_R4_PREREGISTRATION_DRAFT_V0_before_nb.md")
s = des.read_text(encoding="utf-8")


def R(a, b):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, 1)


R("— révision R2 (conception seule)", "— révision R3 (conception seule)")
R("R2 intègre la relecture indépendante de R1 (**FAIL**)",
  "R3 intègre la vérification de R2 (**PASS_WITH_NB**) : formule de proximité entièrement spécifiée, capacité 3 requalifiée. R2 intègre la relecture indépendante de R1 (**FAIL**)")
R("| (a) Pondération | proximité = Σ des poids IDF des lemmes pivots communs, normalisée par la taille des deux voisinages. Poids IDF d'un lemme pivot = log(N / nombre de voisinages qui le contiennent), N et effectifs calculés **sur l'export figé**, jamais sur les données d'enseignement ou d'examen. |",
  "| (a) Pondération | **voisinage** V(l) d'un lemme l = union, sur **toutes** ses entrées `thes_fr` de l'export, des lemmes listés, plus l. **N** = nombre de lemmes distincts ayant au moins une entrée `thes_fr` dans l'export ; **df(p)** = nombre de ces voisinages contenant p ; **idf(p) = ln(N / df(p))** (logarithme naturel). **Proximité(a, b) = Σ_{p ∈ V(a) ∩ V(b)} idf(p) / √(Σ_{p ∈ V(a)} idf(p) · Σ_{p ∈ V(b)} idf(p))** : un cosinus pondéré, dans [0, 1], symétrique. Tout est calculé **sur l'export figé seulement**. |")
R("| 3. Distinguer des sens proches | **contrastes** :", "| 3. Distinguer des sens proches | **contrastes** :")
old = "par une **règle générique de négation**, figée et testée unitairement (réouverture explicite de la règle B3 de V0) | **compréhension** |"
R(old, "par une **règle générique de négation**, figée et testée unitairement (réouverture explicite de la règle B3 de V0) | **visée**, à démontrer par H4 |")
des.write_text(s, encoding="utf-8", newline="\n")

s = pre.read_text(encoding="utf-8")
R("(BROUILLON, non verrouillé)", "(PRÊT À VERROUILLER, non verrouillé)")
R("**Conception :** `OXYGEN_R4_COGNITIVE_LEARNING_DESIGN_V0.md`, R2 (sha256 `0983a60c…`, à confirmer après vérification).",
  "**Conception :** `OXYGEN_R4_COGNITIVE_LEARNING_DESIGN_V0.md`, **R3** (empreinte au §8). R2 vérifiée PASS_WITH_NB ; les cinq remarques sont intégrées.")
R("| P-LEX | la proximité pondérée discrimine les étiquettes | enseignement seul : précision ≥ 0,5 et rapport ≥ 3 | classe désactivée |",
  "| P-LEX | la proximité pondérée discrimine les étiquettes | enseignement seul, paires de voisins de leçons différentes, proximité ≥ 0,2 : **au moins 10 paires retenues**, précision ≥ 0,5 et rapport ≥ 3. Si le taux entre étiquettes différentes vaut 0, le rapport est jugé satisfait seulement si au moins 10 paires de même étiquette sont retenues. | classe désactivée (y compris en cas de support insuffisant) |")
R("**Gain propre à l'enseignement :** D − C.",
  "**Gain propre à l'enseignement, métrique principale (H2, H3) :** exactitude de D comptée **en excluant** les réponses dont toutes les preuves sont d'origine `PREALABLE`, moins celle de C comptée de la même façon. D − C brut est rapporté **en secondaire**.")
R("| **M-CIBLE** | masquer dans l'export toutes les entrées du **lemme cible** (« force », « chemin », « corriger ») **et** ses occurrences dans les listes de synonymes des autres lemmes ; toutes les autres relations restent |",
  "| **M-CIBLE** | masquer dans l'export toutes les entrées du **lemme cible** (« force », « chemin », « corriger ») **et** ses occurrences dans les listes de synonymes des autres lemmes, **y compris ses formes fléchies** (toute forme que l'export lemmatise vers le lemme cible) ; toutes les autres relations restent |")
R("- `metadata.total_lemmas` vaut 843 969, alors que la table `lemmas` en compte 663 134 (écart de comptage : formes UniMorph français sans lemme) ;",
  "- `metadata.total_lemmas` vaut 843 969, alors que la table `lemmas` en compte 663 134 : 843 969 est la **somme des `lemmas_imported` par source, doublons compris** (159 182 + 427 464 + 135 909 + 36 452 + 76 488 + 8 474), et non un décompte de la table ;")
R("| Conception R2 | `0983a60c…`, après vérification |", "| Conception R3 | __DES_SHA__ |")
pre.write_text(s, encoding="utf-8", newline="\n")
print("ok")
