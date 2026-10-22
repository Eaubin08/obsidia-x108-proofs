import pathlib, shutil
d = pathlib.Path(__file__).parent
p = d / "OXYGEN_R4_COGNITIVE_LEARNING_DESIGN_V0.md"
shutil.copy(p, d / "OXYGEN_R4_COGNITIVE_LEARNING_DESIGN_V0_R0.md")
s = p.read_text(encoding="utf-8")


def R(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)


R("# Oxygen — conception R4 « apprentissage cognitif » V0 (conception seule)",
  "# Oxygen — conception R4 « apprentissage cognitif » V0 — révision R1 (conception seule)\n\n"
  "R1 intègre la relecture indépendante (APPROVE_WITH_CHANGES) : B1 corrigé (clé de concept), NB1, NB2, NB4, NB5 et NB6 intégrés. NB3 est **contesté avec preuve** : `PredicateUnit.objects: tuple[Argument, ...]` existe (`app/semantic/lattice/primitives.py:157`). R0 est conservée à côté.")
R("54 sur 54** mots de contenu de l'enseignement sont connus.",
  "54 sur 54** mots de contenu de l'enseignement sont connus (mots de contenu = `tests/education_pilot/_bench.content_words`, liste `STOP` du banc, hors mot cible ; avec une autre liste de mots vides, le relecteur trouve 57 sur 57).")
R("| Concepts voisins | pour chaque mot plein voisin : ensemble d'identifiants de **groupes de sens ou synonymes** du corpus (concept ids = `sense_id`) | corpus | OBSERVATION, avec la mention « ressource externe, `verified_fact = False` » |",
  "| Concepts voisins | pour chaque mot plein voisin : son **voisinage lexical** = l'ensemble des **lemmes** cités dans ses entrées `synonym_group` du corpus, plus le lemme lui-même (**clé de concept, B1**). Les `sense_id` sont propres à chaque lemme et **ne servent pas** de clé partagée. | corpus | OBSERVATION, avec la mention « ressource externe, `verified_fact = False` » |")
R("| Relations | relations typées et génériques cible ↔ voisins : `gouverne`, `quantifié_par`, `complément_de`, `agent_collectif` (pluriel + déterminant défini) ; polarité |",
  "| Relations | relations typées et génériques cible ↔ voisins : `gouverne`, `quantifié_par`, `complément_de` ; nombre et détermination de la cible comme **traits de forme**, non comme relation nommée (NB2 : la relation `agent_collectif` de R0 est retirée, trop proche d'un motif de leçon) ; polarité |")
R("**Exemple sans règle propre à un sens :** pour une phrase contenant « force » suivi de « de » et d'une quantité avec unité, l'élève observe la construction `force de <quantité> <unité>`. Il observe aussi que l'unité appartient, dans le corpus, à des groupes de concepts « mesure ». Il relie cette configuration à l'étiquette que l'enseignant a donnée aux leçons qui avaient la même construction et des voisins de concepts proches. Ni « newton » ni aucun sens n'est codé.",
  "**Exemple sans règle propre à un sens (NB1, remplace l'exemple de R0, calqué sur une leçon et faux sur le corpus) :** soit un mot cible X, une leçon « … X … voisin *v1* … » étiquetée L, et une question « … X … voisin *v2* … », où *v2* n'apparaît dans aucune leçon. Si les voisinages lexicaux de *v1* et *v2* se recouvrent dans le corpus (un lemme commun dans leurs groupes de synonymes), la question reçoit une preuve en faveur de L, citée en provenance (*v1*, *v2*, lemme commun). Sinon, cette classe de preuve est muette. Aucun mot ni sens n'est codé.")
R("| Corpus lexical | `lookup_surface_form(form, lang) → LinguisticAnalysis[]` ; `get_senses_and_synonyms(lemma, lang) → SenseDefinition[]` (`sense_id`, `kind`, `synonyms`, `definition`, `verified_fact = False`) ; `is_known_lexical_item(word, lang)` ; base SQLite `data/linguistic_corpus/lexicon.db` | monter un **export figé** (sous-ensemble ou base entière, 530 Mo) en lecture seule dans `/extra`, avec empreinte. Le banc RED le permet déjà (`OXYGEN_PILOT_STUDENT_PATH`) **sans changer le protocole** : l'examinateur n'envoie toujours que `(mot, phrase)`. |",
  "| Corpus lexical | `lookup_surface_form(form, lang) → LinguisticAnalysis[]` ; `get_senses_and_synonyms(lemma, lang) → SenseDefinition[]` (`sense_id`, `kind`, `synonyms`, `definition`, `verified_fact = False`) ; `is_known_lexical_item(word, lang)` ; base SQLite `data/linguistic_corpus/lexicon.db` (`DB_PATH` relatif au dépôt, `lexical_corpus.py:31`) | monter un **export figé** (base entière, ou sous-ensemble produit par **règle mécanique** : par exemple les entrées de tous les lemmes d'un dictionnaire de formes, jamais une liste choisie à la main) en lecture seule dans `/extra`, avec empreinte. **Lecteur (NB5)** : un lecteur propre à l'élève, en bibliothèque standard, qui ouvre la base en SQLite `file:…?mode=ro&immutable=1` (le module du dépôt n'est pas importable dans le conteneur, et son `DB_PATH` y est invalide). Le banc RED le permet déjà (`OXYGEN_PILOT_STUDENT_PATH`) **sans changer le protocole** : l'examinateur n'envoie toujours que `(mot, phrase)`. |")
R("| 2. Relier plusieurs exemples à un concept | profils agrégés ; concepts du corpus **partagés** entre exemplaires (deux leçons différentes dont les voisins sont synonymes) | **compréhension** : regroupement au-delà de la surface |",
  "| 2. Relier plusieurs exemples à un concept | profils agrégés ; **voisinages lexicaux qui se recouvrent** entre exemplaires (deux leçons différentes dont les voisins partagent un lemme de synonymes, règle mécanique figée) | **compréhension** : regroupement au-delà de la surface |")
R("| 7. Transférer vers un contexte inédit | les profils d'alignement portent sur des **concepts du corpus**, pas sur des mots : un voisin jamais vu en leçon mais synonyme ou co-classé dans le corpus transmet le signal | **compréhension**, si l'ablation le confirme |",
  "| 7. Transférer vers un contexte inédit | les profils portent sur des **voisinages lexicaux**, pas sur des mots : un voisin jamais vu en leçon mais dont le voisinage recouvre celui d'un voisin enseigné transmet le signal. **Non démontré** : la densité réelle des recouvrements est à mesurer sur l'enseignement seul (test unitaire), avant tout RED | **compréhension**, si l'ablation le confirme |")
R("| Corpus lexical | CODE, RUNTIME (Brody, selon le crosswalk) | 663 k lemmes, 307 k sens | oui |",
  "| Corpus lexical | CODE ; **RUNTIME non tracé** (NB4 : seul appelant dans `app` + `periphery` : `periphery/language/native_realization.py`) | 663 k lemmes, 307 k sens | non démontré |")
R("1. Le corpus porte-t-il réellement l'information utile ? C'est non démontré ; H3 le testera.",
  "1. Le corpus porte-t-il réellement l'information utile ? C'est non démontré ; H3 le testera. **Avant tout RED**, un test unitaire sur l'enseignement seul mesurera combien de paires de voisins de leçons ont des voisinages lexicaux qui se recouvrent. Si c'est quasi nul, le mécanisme de transfert de C est réfuté d'avance.")
p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
