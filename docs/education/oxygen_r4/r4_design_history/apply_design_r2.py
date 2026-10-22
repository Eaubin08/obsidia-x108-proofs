import pathlib, shutil
d = pathlib.Path(__file__).parent
p = d / "OXYGEN_R4_COGNITIVE_LEARNING_DESIGN_V0.md"
shutil.copy(p, d / "OXYGEN_R4_COGNITIVE_LEARNING_DESIGN_V0_R1.md")
lines = p.read_text(encoding="utf-8").split("\n")
s = "\n".join(lines)


def R(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)


R("— révision R1 (conception seule)", "— révision R2 (conception seule)")
R("R1 intègre la relecture indépendante",
  "R2 intègre la relecture indépendante de R1 (**FAIL**) : modèle d'identité de concept garde-fou (a)–(f), critère de réfutation chiffré, doctrine du lexique préalable (décision fondateur `LEXIQUE_PREALABLE=YES`). R1 intègre la relecture indépendante")
# line 41: concept neighbourhood with guardrails
old41 = lines[40]
R(old41, "| Concepts voisins | pour chaque mot plein voisin, **après lemmatisation obligatoire** (`lookup_surface_form` ; une forme sans lemme reste sans voisinage) : son **voisinage lexical** = lemmes de ses entrées `synonym_group`, plus le lemme. Les `sense_id` ne servent pas de clé partagée. **Le recouvrement est une preuve faible, jamais une identité de concept** (voir « Modèle de proximité lexicale » ci-dessous). | corpus | OBSERVATION, avec la mention « ressource externe, `verified_fact = False` » |")
old70 = lines[69]
R(old70, "| 2. Relier plusieurs exemples à un concept | profils agrégés ; **proximité lexicale pondérée** entre voisins d'exemplaires (modèle ci-dessous), comme **preuve faible** | **non démontré** : une proximité lexicale n'est pas un regroupement conceptuel ; elle ne compte comme compréhension que si le critère de précision P-LEX est satisfait |")
old75 = lines[74]
R(old75, "| 7. Transférer vers un contexte inédit | proximité lexicale pondérée entre un voisin inédit et des voisins enseignés, **un seul saut, sans transitivité** | **non démontré** : réfuté d'avance si P-LEX échoue (voir ci-dessous) |")
R("## B. Apprentissage et correction", """### Modèle de proximité lexicale (R2, garde-fous (a)–(f))

Mesure, **sur les données d'enseignement seulement**, par la relecture de R1 : sur 853 paires de voisins de leçons différentes, 26 recouvrements, dont **23 entre étiquettes différentes**. Taux de recouvrement de 4,5 % entre mêmes étiquettes contre 2,9 % entre étiquettes différentes. Une règle de recouvrement **non pondérée** pointe donc surtout vers une mauvaise étiquette. Les causes sont la polysémie (un voisin apporte les synonymes de tous ses sens) et des voisinages de taille très inégale (1 à 109 lemmes).

| Garde-fou | Règle (fixée a priori) |
|---|---|
| (a) Pondération | proximité = Σ des poids IDF des lemmes pivots communs, normalisée par la taille des deux voisinages. Poids IDF d'un lemme pivot = log(N / nombre de voisinages qui le contiennent), N et effectifs calculés **sur l'export figé**, jamais sur les données d'enseignement ou d'examen. |
| (b) Seuil et plafond | proximité retenue seulement au-dessus d'un seuil fixé a priori (0,2) ; **au plus une voix par paire de voisins**, et la classe « concepts voisins » vote au plus une fois par question, comme toute classe (§C) |
| (c) Aucune transitivité | un seul saut : voisin de la question ↔ voisin d'un exemplaire. Aucune fermeture, aucune chaîne A ≈ B ≈ C. |
| (d) Lemmatisation | obligatoire avant tout calcul ; formes non lemmatisables : pas de voisinage |
| (e) Statut | preuve **faible** et **observation**, jamais une identité de concept ni un sens partagé. Elle ne peut jamais, à elle seule, produire une réponse : il faut au moins une autre classe concordante (§C). |
| (f) Symétrie | proximité définie symétriquement (pivots communs, sans orientation). La symétrie des listes du corpus n'est pas supposée. |

**Critère de réfutation chiffré P-LEX, préalable à tout build de cette classe :** sur les données d'enseignement seules, par paires de voisins de leçons différentes, avec le modèle (a)–(f) :
- **précision** = part des paires retenues qui relient la même étiquette ;
- **rapport de discrimination** = taux de paires retenues entre même étiquette / taux entre étiquettes différentes.

**P-LEX est satisfait si la précision est ≥ 0,5 et le rapport ≥ 3.** Sinon, la classe « concepts voisins » est **désactivée** dans R4 : l'option C se réduit à constructions + exemplaires + alignement de la cible, et ce résultat est consigné. Ce critère est fixé **avant** de calculer le résultat. La mesure non pondérée de R1 (précision 3 / 26 ≈ 0,12, rapport ≈ 1,5) **échouerait**.

## B. Apprentissage et correction""")
old199_start = "1. Le corpus porte-t-il réellement l'information utile ? C'est non démontré ; H3 le testera."
R(old199_start, "1. Le corpus porte-t-il réellement l'information utile ? C'est non démontré ; **P-LEX** (précision et discrimination, pas seulement densité) puis H3 le testeront.")
R("## A. Représentation du sens", """## Doctrine du lexique préalable (décision fondateur 2026-10-22)

Oxygen peut commencer avec un vocabulaire préalable. Le corpus est une **source de connaissances lexicales consultative, en lecture seule**. Ce n'est ni un mécanisme de compréhension autonome ni une autorité. Chaque élément de preuve porte une **origine** :

| Origine | Signification |
|---|---|
| `PREALABLE` | présent dans le corpus avant tout enseignement |
| `INTERPRETE_CORPUS` | construit par l'élève à partir du corpus (proximité, lemmatisation) |
| `ACQUIS_LECON` | issu d'une leçon ou d'un exercice |
| `CORRIGE` | issu d'une correction ou d'une révision |
| `TRANSFERE` | réponse dans un contexte inédit, appuyée sur des preuves `ACQUIS_LECON` reliées par `INTERPRETE_CORPUS` |
| `INCERTAIN` | abstention ou preuve sous le seuil |

**Une réponse déjà directement disponible dans le corpus n'est pas comptée comme apprentissage.** La configuration « corpus sans leçons » (pré-enregistrement) mesure ce savoir initial, et le gain dû à l'enseignement se mesure par différence.

## A. Représentation du sens""")
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
