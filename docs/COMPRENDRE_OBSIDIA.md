# Comprendre Obsidia

> Récit d'entrée, tiré du [README](../README.md) du projet. C'est la page à lire en premier. Ensuite : [Trajets de la donnée](TRAJETS.md) · [Entraînement, éducation, naissance](EDUCATION.md) · [Sécurité](SECURITE.md) · [État réel 2026-09-15](ETAT_REEL_2026_09_15.md) · [Guide des couches](README.md).

---

## Obsidia en une phrase

> **Obsidia est un système d'exploitation cognitif gouverné qui aide une organisation à comprendre sa propre structure, mobiliser plusieurs formes d'intelligence, proposer des transformations, les tester et les prouver avant de contrôler leur passage au réel.**

```text
Intelligence distribuée + mémoire gouvernée + preuve + autorité isolée + action bornée
```

Obsidia ne repose pas sur un modèle unique chargé de tout comprendre et de tout décider. L'intelligence est répartie entre des organes spécialisés, et **l'autorité reste isolée** dans un seul noyau : `KX108_ONLY`.

L'état réel du 2026-09-15 précise le point important de la reprise : le runtime le plus avancé pour la mémoire n'est plus le chemin historique Graphiti/Neo4j. Il est dans le cutover **Native Memory Obsidia** du worktree M4D4 (`obsidia-main-direct-20260914`, `5d27d003 + index staged`). Graphiti et Neo4j ne doivent plus être racontés comme mémoire active sans callsite runtime démontré.

---

## D'où vient Obsidia

Obsidia n'est pas né d'un prompt, d'un hackathon ou d'une spécification écrite à l'avance. Il est né **à la rencontre de deux recherches**.

**La première portait sur la cohérence.** Comment une structure acquiert-elle du sens ? Qu'est-ce qui la rend cohérente ? Comment vérifier qu'elle tient dans le temps ? À quel moment un système doit-il refuser ? Une chaîne s'en est dégagée :

```text
Sens → Organisation → Cohérence → Temps → Constance → Mémoire → Stabilisation
```

**La seconde était une confrontation quotidienne avec les limites des modèles de langage** : oubli d'une contrainte déjà donnée, glissement du sens, zones inconnues remplies au lieu d'être signalées, réponse fluide mais structurellement fausse, proposition transformée trop vite en action.

Ces échecs n'ont pas été traités comme des problèmes de formulation. À chaque friction, une question : *quelle couche manque ? quelle loi ? quel verrou ? quelle mémoire ? quelle preuve ? quel refus ?* Chaque réponse est devenue une pièce du système :

| Faille observée | Pièce d'Obsidia qui y répond |
|---|---|
| l'oubli | une mémoire externe et gouvernée |
| le glissement du sens | des invariants et un noyau |
| la surinterprétation | des frontières et la lecture seule |
| la réponse trop libre | des contrats de sortie et une validation |
| l'action trop rapide | HOLD et la temporalité |
| le contexte confus | la traduction, les arbres et le routage |
| l'hallucination | la provenance, la preuve et le replay |
| la désobéissance subtile | des droits, des non-droits et une boucle opérateur |

> Obsidia n'est pas né contre les LLM. Il est né dans l'interstice entre **la puissance de l'intelligence probabiliste** et **son incapacité à rester fidèle et gouvernée dans le temps**.

Le projet est porté par **Étienne Aubin**, entrepreneur et architecte, dans les Ardennes. Il a été construit avec une méthode particulière : formuler une intention, poser des concepts et des frontières, faire générer par des agents IA, auditer, corriger les trahisons de sens, prouver, puis intégrer sous gouvernance. **Sans jamais déléguer à l'IA la direction conceptuelle ni l'autorité finale.**

---

## La question à laquelle Obsidia répond

La plupart des systèmes agentiques se demandent : **comment rendre un agent plus capable ?**

Obsidia se pose une autre question :

> **Dans quel système une intelligence peut-elle comprendre, apprendre et progresser sans que sa puissance lui donne automatiquement le droit d'agir ?**

Une intelligence peut être rapide, convaincante et bien outillée, et rester dangereuse si son passage au réel n'est pas gouverné. Obsidia sépare donc ce que les autres confondent :

```text
comprendre ≠ proposer ≠ simuler ≠ prouver ≠ autoriser ≠ exécuter
```

> *« Le système ne fait pas confiance à une intelligence uniquement parce qu'elle produit une bonne réponse. Il fait confiance au chemin contrôlé qu'elle est obligée d'emprunter. »*

---

## Les problèmes qu'Obsidia résout

| Problème courant | Réponse d'Obsidia |
|---|---|
| **Le modèle reste le centre implicite.** Même avec RAG, agents et outils, un modèle peut être laissé au centre de la compréhension, du choix, de la décision et parfois de l'action. | Obsidia sépare ces responsabilités : dans le chemin Brody/M4D4 audité, la réponse est produite par génération structurelle locale. Tout chemin utilisant réellement un modèle doit être documenté séparément, avec callsite prouvé, et ne doit pas expliquer causalement M4D4. |
| **On confond présence et fonctionnement** : documenté, installé, appelé, testé, utilisé… | Obsidia distingue ces états, pour éviter doublons, composants orphelins et faux sentiment de sécurité. |
| **La mémoire est traitée comme une vérité.** | Une information ne devient pas vraie parce qu'elle a été mémorisée : elle passe par tri, provenance, validation humaine ([trajet du savoir](TRAJETS.md#2-le-trajet-du-savoir--comment-une-information-devient-mémoire)). |
| **L'inférence est appelée trop tôt.** | Avant « quel modèle appeler ? », Obsidia se demande **« faut-il appeler un modèle ? »** ([pourquoi ça marche sans entraînement](TRAJETS.md#7-pourquoi-ça-fonctionne-sans-entraînement)). |
| **Les agents confondent proposition et transformation.** | Une chaîne stricte : proposer, simuler, tester, prouver, valider, puis seulement agir. |

---

## La philosophie en six phrases

```text
Noyau souverain fermé · Périphérie spécialisée ouverte · Exploration autorisée · Souveraineté jamais déléguée
```

- **L'intelligence n'est pas l'autorité.** Comprendre ou résoudre ne donne pas le droit d'agir.
- **La mémoire n'est pas la vérité.** Une trace doit franchir des contrôles avant de devenir canonique.
- **La preuve n'est pas l'autorisation.** Une preuve confirme une propriété ; elle ne décide pas d'agir.
- **Le refus peut être productif.** Un refus structuré montre une frontière et ce qui manque.
- **Le système doit apprendre sans absorber la pollution.** Une attaque devient une leçon, pas une contamination.
- **L'humain reste l'opérateur de souveraineté.** Il garde la direction, la validation et le refus.

---

## Qui fait quoi, en une image

```text
Oxygen porte l'identité et l'éducation — une seule naissance (vision).
Les domaines comprennent leur terrain.
OS Trad reçoit la langue vivante et la stabilise en IR — la vérité est dans l'IR, jamais dans une langue.
La mémoire native conserve sous gouvernance.
Brody comprend et coordonne — sans décider, sans écrire, sans porter l'identité.
Obsidure recherche et formalise — sans commit, sans push, sans souveraineté concurrente.
Les micro-agents savent faire — ils restent bêtes.
Sigma surveille, retrouve, guide et explique — sans trancher.
Lean prouve dans un périmètre défini.
KX108 autorise et tranche : ACT, HOLD ou BLOCK.
Le Terminal rend le système utilisable.
```

Le détail de chaque organe est dans le [guide des couches](README.md), et leur fonctionnement concret dans les [trajets de la donnée](TRAJETS.md).

Dans le chemin M4D4 audité, cela a une conséquence simple : la réponse de Brody est expliquée par la stack locale. Elle assemble une compréhension depuis Native Memory, les corpus, le contexte de session, les règles, les scores, le micro-core, les balances, le point cloud 21D, MEMZUM, les domaines, les adapters, le moteur local et True Voice.

---

## Comment Étienne obtient concrètement ces résultats

La réponse courte est : Étienne n'a pas seulement demandé a une IA de répondre mieux. Il a construit un système ou chaque résultat doit passer par une suite de transformations explicites.

Une question humaine arrive avec ses mots, ses sous-entendus et ses risques. Obsidia ne la traite pas comme une phrase libre qui part directement vers une réponse. Le système commence par la situer : qui demande, sur quoi, avec quelle intention possible, quel niveau de risque, quelles inconnues, quelles sources disponibles.

Ensuite, plusieurs organes se relaient :

| Organe | Ce qu'il reçoit | Ce qu'il transforme | Ce qu'il produit |
|---|---|---|---|
| OS Trad | langue vivante, termes ambigus, intention | mots en entités, relations, contraintes, unknowns | représentation interne exploitable |
| MEMZUM | signaux de besoin mémoire | indices de pertinence mémoire | oui/non : faut-il consulter la mémoire |
| Native Memory | requête locale et bornée | index validé, tags, fragments | contexte retrouvé avec provenance |
| Brody | représentation + contexte + règles | organisation cognitive de la réponse | réponse structurée et readonly |
| Domaines | objet métier ou physique | règles, risques, temporalité du domaine | contraintes et interprétation terrain |
| Sigma | sortie candidate et traces | contradictions, manques, dérives | signaux de cohérence |
| Obsidure | problème à explorer ou formaliser | hypothèses, patchs, preuves candidates | proposition ou chemin de preuve |
| KX108 | envelope admissible | règles d'autorité | `ACT`, `HOLD` ou `BLOCK` |

Ce mécanisme explique pourquoi le système donne parfois déjà des réponses solides : beaucoup de matière est déjà organisée avant la réponse finale. Le corpus math apporte des définitions et des statuts. La mémoire native retrouve des traces validées. Les règles réduisent les chemins possibles. Les domaines imposent leurs contraintes. Les preuves disent ce qui est seulement testé, prouvé, candidat ou inconnu.

Obsidia ne remplace donc pas le jugement humain par un automate souverain. Il construit un chemin ou la compréhension est séparée de l'autorisation. Une bonne réponse peut éclairer, proposer ou structurer ; elle ne devient pas automatiquement une action.

### La donnée devient progressivement autre chose

```text
document ou signal
-> source identifiée
-> fragment extrait
-> représentation
-> contexte
-> réponse ou proposition
-> preuve ou contradiction
-> décision gouvernée
-> trace vérifiable
```

Chaque flèche change le statut de l'objet. Un document reste un document tant qu'il n'est pas identifié, sourcé, découpé, indexé et rattaché a un statut. Une hypothèse reste une hypothèse tant qu'elle n'est pas testée. Un test reste un test tant qu'il ne prouve pas formellement le comportement global. Une mémoire reste un contexte tant qu'elle n'a pas franchi les portes de validation.

---

## Où va Obsidia

**Obsidia V0.1** sera la première « mise au monde » du système : une interface unifiée pour connecter une organisation, en reconstruire le fonctionnement réel, proposer des transformations, les simuler, les prouver et gouverner leur passage au réel.

À plus long terme, Obsidia ajoute une question à l'histoire de l'IA :

> **Comment gouverner le chemin entre savoir, compréhension, réponse et action ?**

```text
La Big Tech a surtout travaillé sur :   modèle → réponse
Obsidia travaille sur :                 source → tri → mémoire → compréhension → proposition
                                        → preuve → refus possible → décision gouvernée → action → replay
```

La formulation plus complète issue de la reprise est :

```text
monde réel → signal → observation située → provenance → représentation
→ savoir retrouvable → contexte → cognition → intention → capacité
→ décision gouvernée → action éventuelle → conséquence → vérification
→ expérience validée → éducation future d'Oxygen
```

L'ambition n'est pas de concentrer toujours plus d'intelligence dans un modèle unique. C'est de construire un environnement où **plusieurs formes d'intelligence peuvent progresser, coopérer et apprendre sans devenir souveraines**. Cette ambition porte un nom : **Oxygen**, l'unique entité née et éduquée. Brody, OS Trad et Obsidure sont ses organes ; les micro-agents sont des capacités entraînées.

> **Une seule naissance. Une seule identité. Des organes puissants. Des agents qui restent bêtes.**

> **L'AGI est une architecture de régulation, jamais un acteur incarné livré à lui-même.**

Oxygen est encore une vision : la phase C10 Éducation / Oxygen n'est pas lancée. Voir [Entraînement, éducation, naissance](EDUCATION.md).

---

## Ce qu'Obsidia ne prétend pas encore

Le projet est honnête sur son état : la V0.1 n'est pas terminée, tous les composants ne sont pas connectés, aucun domaine n'est prêt pour la production, les théorèmes Lean ne prouvent pas le runtime complet, Brody n'a aucune autorité, le système n'agit pas de manière autonome, et **Obsidia n'est pas une AGI**.

```text
présent ≠ connecté · connecté ≠ causalement utile · testé ≠ prouvé globalement · ambition ≠ capacité actuelle
```
