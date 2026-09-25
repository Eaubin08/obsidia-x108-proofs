# Convergence langage / mémoire / causalité / chronologie (V0)

Question de recherche (utilisateur) : LANGAGE, MÉMOIRE, CAUSALITÉ,
CHRONOLOGIE DES CONNAISSANCES, MODÈLE DU MONDE et REPRÉSENTATION SYMBOLIQUE
sont-ils des systèmes séparés, ou des **projections** d'un même substrat
cognitif multidimensionnel ?

Réponse de cet audit : **substrat partagé pour un petit noyau de primitives,
sémantiques distinctes au-dessus**. On ne doit ni tout fusionner, ni tout
dupliquer. Détail ci-dessous.

## 1. L'hypothèse « multivers cognitif » est déjà dans les sources

Sources extraites Obsidia (`01_SOURCES/extracted_text_all.md`) :
- l.38-39 : « un Graphe Multidimensionnel … Chaque donnée entrante (un Nœud
  Continuum) n'appartient pas à un seul arbre, mais possède un vecteur
  d'appartenance à plusieurs arbres simultanément » ;
- l.529 : les 34 arbres « forment un bloc multidimensionnel où chaque donnée
  est traitée simultanément à travers plusieurs » ;
- l.1784-1809 (CALIBRATION_PROCEDURALE) : liens typés (CAUSAL / STRUCTUREL /
  ANALOGIQUE / TEMPOREL / HYPOTHÉTIQUE), directionnalité (DIRECT / INDIRECT /
  BIDIRECTIONNEL), force ; « un lien analogique n'est pas un lien causal » ;
  « un lien trop général (tout → tout) est un lien nul » ;
- l.2425 : « la mémoire comme état causal, pas stockage brut ».

Mais la couche relationnelle correspondante est **vide dans le code** (M0 :
`relation_graph.build_graph → {}`, `path_finder.find_path → []`,
`Link.schema.json` sans propriétés). L'hypothèse est donc **documentée, non
réfutée, non implémentée**.

## 2. Modèle retenu : un objet, plusieurs projections, liens typés

```
                 ┌──────────── projection GRAMMATICALE (forme, mode, négateur)
                 ├──────────── projection SÉMANTIQUE  (prédicat, arguments)
                 ├──────────── projection TEMPORELLE  (temps/aspect, réalisé ?, déixis)
   UN OBJET ─────┼──────────── projection CAUSALE     (relations CAUSES/CONDITIONS)
 (PredicateUnit) ├──────────── projection ÉPISTÉMIQUE (asserté, ouï-dire, croyance…)
                 ├──────────── projection PRAGMATIQUE (requis, interdit, rapporté…)
                 ├──────────── projection PROVENANCE  (span dans le brut, analyseur)
                 ├──────────── projection MONDE       (besoin de preuve courante)
                 ├──────────── projection AUTORITÉ    (toujours : aucune ; gate requise ?)
                 └──────────── projection CONFIANCE   (confiance, ambiguïtés)
```

Les projections sont des **vues calculées** sur l'unique objet
(`app/semantic/lattice/projections.py::project`), pas des copies : elles ne
peuvent pas diverger. C'est le point exact où la notion de « superposition »
des 34 arbres devient vérifiable : un vecteur d'appartenance = une projection.

### Types de connexion distingués (`ConnectionKind`)

| Type | Définition opérationnelle |
|---|---|
| `DIRECT_RELATION` | arête typée entre A et B (hors temps et provenance) |
| `TEMPORAL_RELATION` | arête `PRECEDES` / `FOLLOWS` entre A et B |
| `PROVENANCE_RELATION` | arête `REPORTS` (B est connu *par* A) |
| `SHARED_CAUSE` | ∃ C : `CAUSES(C→A)` et `CAUSES(C→B)` |
| `SHARED_ANCESTOR` | A et B enchâssés sous le même prédicat (rapport, crainte, condition) |
| `INDIRECT_PATH` | chemin de longueur ≥ 2 (chemin renvoyé) |
| `SEMANTIC_SIMILARITY` | même prédicat canonique **sans** chemin — explicitement *pas* une relation |
| `NO_PROVEN_CONNECTION` | aucun des cas précédents — **l'absence est représentée** |

Aucun nœud n'est relié à tous les autres ; l'absence de chemin est un
résultat, pas une erreur.

## 3. Comparaison primitive par primitive

| Primitive | LANGAGE (UtteranceFrame) | MÉMOIRE (Obsidia) | Partagée ? | Pourquoi |
|---|---|---|---|---|
| Point / nœud | `PredicateUnit` (un prédicat dans un énoncé) | record natif / Nœud Continuum / Event | **Oui (forme)** | même besoin : identité stable + span/source + coordonnées multiples |
| Arête typée | `LatticeRelation(kind, source, target, confidence)` | `calibrated_links: List[Any]` (non typé), prompt de calibration | **Oui** | le vocabulaire de calibration (CAUSAL/TEMPOREL/…) et les connecteurs du discours se recouvrent ; la *force* est un attribut commun |
| Coordonnée temporelle | temps grammatical **relatif à l'énonciation** | date absolue d'un événement / d'une connaissance | **Non (sémantique différente)** | « a lancé » = antérieur à l'énonciation ; la mémoire a besoin de *deux* temps : temps de l'événement et temps d'acquisition (chronologie des connaissances). À relier par ancrage, pas à fusionner |
| Coordonnée causale | causalité **énoncée** (« car ») | causalité **procédurale** (`causal_chain.py`) et « mémoire de contraintes » | **Partielle** | la relation `CAUSES` est commune ; mais une causalité énoncée est une *assertion d'un locuteur* (épistémique), jamais un fait |
| Provenance | span dans le brut + analyseur | `source_sha256`, `text_sha256`, chemin, type de source | **Oui** | même contrat : tout est traçable au brut |
| Confiance | par unité, par relation | score de retrieval, `provenance_score` | **Oui (type)** | mais les échelles ne sont pas calibrées entre elles — ne pas comparer des nombres de systèmes différents |
| Contradiction | requis ∧ interdit sur le même référent | CONTRADICTION_HUNTER (vraie / tension / malentendu) | **Oui** | même règle de clôture : `closure_safe = not (unknowns or contradictions)` (déjà dans `closure.py`) |
| Référence non résolue | pronom sans antécédent | inconnue non qualifiée (`unresolved_unknowns`) | **Oui** | les deux sont de la **dette de clôture** |
| Voisinage sémantique | même prédicat canonique | similarité / nuage de points | **Oui, marqué faible** | toujours distingué d'une relation prouvée |
| Trajectoire / chemin | chemin dans le graphe de l'énoncé | parcours de graphe, `timeverse` | **Oui (algorithme)** | BFS borné identique |
| Consolidation | clôture sémantique d'un énoncé | promotion `CANDIDATE → PROMOTED_MANUAL_ONLY` | **Non** | la clôture d'un énoncé est automatique et locale ; la consolidation mémoire exige une revue humaine. Même mot, autorités différentes |
| Supersession / versions | n/a dans un énoncé isolé | absente (M0) | À concevoir | n'existe nulle part aujourd'hui |

## 4. Conclusion

- **Partager** : nœud identifié + span/provenance, arête typée avec force et
  confiance, contradiction, inconnue/référence non résolue, type de connexion,
  recherche de chemin bornée, projections comme vues.
- **Ne pas partager** : le temps (énonciatif ≠ chronologique ≠ temps
  d'acquisition), la causalité énoncée vs procédurale vs physique, la
  consolidation (automatique vs humaine), l'autorité (toujours externe :
  `KX108_ONLY`).
- Réponse à la question de recherche, en l'état des preuves : langage,
  mémoire et causalité **peuvent être des interfaces sur un substrat commun
  de nœuds typés multi-projetés**, à condition que chaque interface garde son
  propre système de coordonnées temporelles et épistémiques. Le code actuel ne
  permet pas de le démontrer au-delà du langage : la mémoire n'a encore ni
  arêtes ni temps.

## 5. Ce qui a été implémenté pour tester l'hypothèse

Uniquement côté langage (`app/semantic/lattice/`), avec des primitives
conçues pour être réutilisables par la mémoire sans y être branchées :
`PredicateUnit`, `LatticeRelation`, `UtteranceFrame`, `ProjectionAxis`,
`ConnectionKind`, `connection()`. Rien n'est écrit en mémoire ; rien n'est
importé depuis le dépôt Obsidia.
