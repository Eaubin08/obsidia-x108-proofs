import pathlib, shutil, re
d = pathlib.Path(__file__).parent
des = d / "OXYGEN_R4_COGNITIVE_LEARNING_DESIGN_V0.md"
pre = d / "OXYGEN_R4_PREREGISTRATION_DRAFT_V0.md"
shutil.copy(des, d / "OXYGEN_R4_COGNITIVE_LEARNING_DESIGN_V0_R4_audited.md")
shutil.copy(pre, d / "OXYGEN_R4_PREREGISTRATION_DRAFT_V0_R4_audited.md")

s = des.read_text(encoding="utf-8")


def R(a, b, count=1):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, count)


R("— révision R4 (conception seule)", "— révision R4.1 (conception seule)")
R("R4 enregistre le **résultat P-LEX",
  "R4.1 applique les corrections **rédactionnelles** de l'audit de clôture (PASS_WITH_NB) : NB1 à NB4, plus NB5 et NB6 consignés. Aucun paramètre, seuil ou mécanisme n'est modifié. **Nomenclature (NB4) :** les architectures s'appellent désormais **ARCH-A / ARCH-B / ARCH-C** ; les lettres **A / B / C / D** sont réservées aux configurations du pré-enregistrement. R4 enregistre le **résultat P-LEX")
R("**Critère de réfutation chiffré P-LEX, préalable à tout build de cette classe :** sur les données d'enseignement seules, par paires de voisins de leçons différentes,",
  "**Critère de réfutation chiffré P-LEX, préalable à tout build de cette classe :** sur les données d'enseignement seules, par paires de voisins de leçons différentes, avec un **support minimal de 10 paires retenues** (NB2),")
R("| 2. Relier plusieurs exemples à un concept | profils agrégés ; **proximité lexicale pondérée** entre voisins d'exemplaires (modèle ci-dessous), comme **preuve faible** |",
  "| 2. Relier plusieurs exemples à un concept | profils agrégés de constructions et de lemmes (Jaccard sur les ensembles de lemmes candidats). **(R4.1)** La proximité lexicale pondérée est **désactivée** (P-LEX en échec). |")
R("| (iv) | **ablations obligatoires** : C sans corpus (≈ B), C sans contrastes, C sans SENS |",
  "| (iv) | **ablations obligatoires** : celles du pré-enregistrement §4 (M-CIBLE, SANS-CONTRASTE, SANS-CUE-CIBLE) et la configuration B (sans corpus). « Sans SENS » est retiré, puisque SENS n'est pas utilisé. |")
R("| H2 | C dépasse la meilleure ligne de base", "| H2 | la configuration D (ARCH-C complète) dépasse la meilleure ligne de base")
R("| H3 | le gain vient du lexique préalable | ablation C sans corpus sur le même jeu | si C sans corpus ≈ C, le corpus est inutile |",
  "| H3 | le gain vient du lexique préalable | configuration B (sans corpus) contre D, sur le même jeu | si D − B ≤ 0, le corpus est inutile |")
s = s.replace("**Candidat préféré : C**", "**Candidat préféré : ARCH-C**")
s = s.replace("| Critère | A. V0 amélioré", "| Critère | ARCH-A. V0 amélioré").replace("| B. Relationnelle et compositionnelle", "| ARCH-B. Relationnelle et compositionnelle").replace("| C. Hybride :", "| ARCH-C. Hybride :")
R("Mesure, **sur les données d'enseignement seulement**,", "Mesure, **sur les données d'enseignement seulement**,")
R("**Limite déclarée :** les 191 paires",
  """**Précisions de l'audit de clôture :**
- **(NB1) Départage du script :** `plex_measure_r4.py` contient un départage non prévu par la conception. Une forme qui est elle-même un lemme du thésaurus l'emporte sur l'ambiguïté. Sans ce départage, en lemmatisation stricte, il ne reste que **2** paires retenues. Avec les 191 paires ambiguës réintégrées (maximum sur les lemmes candidats), on obtient **8** paires retenues et une précision de **0,25**. Le verdict ÉCHEC tient dans les trois cas. La règle de R4 (ensemble de lemmes candidats) fait foi pour le futur build.
- **(NB5) Robustesse :** l'un des 2 vrais positifs est une paire de lemmes identiques, donc un cas trivial. La base de comptage (1 422 paires d'occurrences, 18 items avec exercices, toutes les paires d'occurrences) diffère des 853 paires de la relecture de R1 (leçons E seules). Le rapport de 5,7 repose sur 5 paires.
- **(NB6) Antériorité des seuils :** elle n'est établie que par la généalogie des fichiers (`_R2`, `_R3`, scripts `apply_*`), sans horodatage externe. Le verrouillage par commit fournira une trace git.

**Limite déclarée :** les 191 paires""")
des.write_text(s, encoding="utf-8", newline="\n")

# section C class list (NB3): add contrasts if missing
s = des.read_text(encoding="utf-8")
m = re.search(r"Le score est un \*\*vote de preuves par classe\*\* : ([^.]*)\.", s)
if m and "contrastes" not in m.group(1):
    s = s.replace(m.group(0), m.group(0).replace(m.group(1), m.group(1) + ", contrastes"), 1)
    des.write_text(s, encoding="utf-8", newline="\n")

s = pre.read_text(encoding="utf-8")
R("Le verrouillage n'interviendra qu'après la vérification indépendante de la conception R2 et le c",
  "Audit de clôture de la conception R4 et de ce pré-enregistrement : **PASS_WITH_NB** ; corrections rédactionnelles appliquées en R4.1. Le verrouillage interviendra par le commit documentaire autorisé, après la vérification indépendante et le c")
R("**R4** (empreinte au §8).", "**R4.1** (empreinte au §8). Nomenclature : configurations **A / B / C / D** ; architectures **ARCH-A / ARCH-B / ARCH-C** (la configuration D est ARCH-C complète).")
R("| Conception R4 |", "| Conception R4.1 |")
pre.write_text(s, encoding="utf-8", newline="\n")
print("ok")
