# Obsidia

## Comprendre et transformer une organisation sans abandonner l’autorité à l’intelligence

> **État du projet au 17 juillet 2026**
>
> Obsidia possède déjà un noyau, des preuves, des runtimes, des mémoires, des domaines et plusieurs organes fonctionnels. La première version produit, **Obsidia V0.1**, n’est pas encore publiée. Le travail actuel consiste à reconstruire une version canonique, connectée, testée et explicable de la stack locale maximale.

## Sommaire

1. [Obsidia en une phrase](#1-obsidia-en-une-phrase)
2. [L’origine du projet](#2-lorigine-du-projet)
3. [Qui porte Obsidia](#3-qui-porte-obsidia)
4. [La question fondatrice](#4-la-question-fondatrice)
5. [Le premier produit : Obsidia V0.1](#5-le-premier-produit--obsidia-v01)
6. [Ce que la V0.1 permettra concrètement](#6-ce-que-la-v01-permettra-concrètement)
7. [À qui s’adresse Obsidia](#7-à-qui-sadresse-obsidia)
8. [Les problèmes auxquels Obsidia répond](#8-les-problèmes-auxquels-obsidia-répond)
9. [La philosophie du projet](#9-la-philosophie-du-projet)
10. [Les changements de paradigme](#10-les-changements-de-paradigme)
11. [L’état réel de la stack locale](#11-létat-réel-de-la-stack-locale)
12. [Ce qui est déjà stabilisé](#12-ce-qui-est-déjà-stabilisé)
13. [Ce qui existe mais doit encore être consolidé](#13-ce-qui-existe-mais-doit-encore-être-consolidé)
14. [Le build maximal local](#14-le-build-maximal-local)
15. [La reconstruction canonique actuelle](#15-la-reconstruction-canonique-actuelle)
16. [L’architecture générale](#16-larchitecture-générale)
17. [Les principaux organes](#17-les-principaux-organes)
18. [Les domaines et les possibilités d’extension](#18-les-domaines-et-les-possibilités-dextension)
19. [Ce que contient ce dépôt public](#19-ce-que-contient-ce-dépôt-public)
20. [Ce que ce dépôt ne prétend pas encore](#20-ce-que-ce-dépôt-ne-prétend-pas-encore)
21. [La route vers la V0.1](#21-la-route-vers-la-v01)
22. [La vision à long terme](#22-la-vision-à-long-terme)

## 1. Obsidia en une phrase

**Obsidia est un système d’exploitation cognitif gouverné qui aide une organisation à comprendre sa propre structure, mobiliser plusieurs formes d’intelligence, proposer des transformations, les tester et les prouver avant de contrôler leur passage au réel.**

Obsidia ne repose pas sur un modèle unique chargé de tout comprendre et de tout décider. L’intelligence est distribuée entre plusieurs organes spécialisés. L’autorité reste isolée.

```text
Intelligence distribuée
+
mémoire gouvernée
+
preuve
+
autorité isolée
+
action bornée
```

La chaîne générale est :

```text
Cognition
→ Intention
→ Décision
→ Action
→ Preuve
```

La règle d’autorité centrale est :

```text
KX108_ONLY
```

Aucun modèle, agent, domaine, système de mémoire, moteur de preuve ou couche d’optimisation ne devient souverain.

## 2. L’origine du projet

Obsidia n’est pas né d’un seul prompt, d’un hackathon ou d’une spécification écrite à l’avance.

Le projet s’est construit progressivement, à la rencontre de deux recherches.

### Une recherche sur les conditions de cohérence

Avant de devenir une stack logicielle, Obsidia était déjà une recherche sur plusieurs questions :

- comment une structure acquiert-elle du sens ?
- comment ce sens est-il organisé ?
- qu’est-ce qui rend une structure cohérente ?
- comment vérifier qu’elle tient dans le temps ?
- comment distinguer mémoire, continuité et stabilisation ?
- à quel moment un système doit-il refuser ?
- comment protéger le passage d’une possibilité vers une action réelle ?
- comment construire une intelligence qui conserve son orientation sans devenir figée ?

Une première chaîne s’est dégagée :

```text
Sens
→ Organisation
→ Cohérence
→ Temps
→ Constance
→ Mémoire
→ Stabilisation
```

Le sens donne une direction. L’organisation agence les éléments. La cohérence vérifie que la structure tient dans son cadre. Le temps éprouve cette structure. La constance mesure sa capacité à conserver une orientation sous perturbation. La mémoire accumule ce qui a réellement tenu. La stabilisation émerge ensuite.

### Une confrontation directe avec les limites des LLM

En parallèle, l’usage intensif des modèles de langage a fait apparaître des limites répétées :

- oubli d’une contrainte déjà donnée ;
- glissement progressif du sens ;
- reformulation d’un concept pourtant figé ;
- confusion entre contexte et intention ;
- remplissage des zones inconnues ;
- surinterprétation ;
- simplification excessive ;
- réponse fluide mais structurellement fausse ;
- volonté d’aider au lieu de respecter le cadre ;
- proposition transformée trop vite en action.

Ces échecs n’ont pas été traités comme de simples problèmes de formulation. À chaque friction, la question est devenue :

```text
Quelle couche manque ?
Quelle loi manque ?
Quel verrou manque ?
Quelle mémoire manque ?
Quelle preuve manque ?
Quel receipt manque ?
Quel refus manque ?
```

Progressivement :

```text
oubli → mémoire externe et gouvernée
glissement → invariants et kernel
surinterprétation → frontières et readonly
réponse trop libre → contrats de sortie et validation
action trop rapide → HOLD et temporalité
contexte confus → traduction, arbres et routage
hallucination → provenance, preuve et replay
désobéissance subtile → droits, non-droits et boucle opérateur
```

Obsidia n’est donc pas né contre les LLM. Il est né dans l’interstice entre :

```text
la puissance de l’intelligence probabiliste
↔
son incapacité à rester fidèle et gouvernée dans le temps
```

Chaque faille a révélé une loi manquante. Chaque friction a produit une couche. Chaque dérive a justifié un verrou.

## 3. Qui porte Obsidia

Obsidia est porté par **Étienne Aubin**, entrepreneur et architecte du projet, basé dans les Ardennes en France.

Le projet n’est pas né dans un laboratoire traditionnel ni au sein d’une grande équipe de recherche. Il a été construit par une méthode particulière :

- formulation d’intentions ;
- création de concepts et de frontières ;
- assemblage de disciplines différentes ;
- utilisation d’agents et d’outils IA pour l’implémentation ;
- audits successifs ;
- formalisation ;
- tests ;
- correction des trahisons de sens ;
- conservation des étapes et des preuves.

Le rôle du fondateur n’est pas d’être l’unique développeur de chaque fichier. Il consiste à porter le fil global : définir ce que le système doit devenir, préserver les distinctions entre les organes, identifier les incohérences, décider ce qui peut être intégré et faire transformer une intention en composants testables.

```text
Intention
→ architecture
→ contraintes
→ génération
→ audit
→ correction
→ preuve
→ intégration gouvernée
```

Obsidia est aussi une expérimentation sur une nouvelle manière de construire des systèmes complexes avec l’IA, sans lui déléguer la direction conceptuelle ni l’autorité finale.

## 4. La question fondatrice

La plupart des systèmes agentiques partent de cette question :

> **Comment rendre un agent plus capable ?**

Ils améliorent son raisonnement, ses outils, sa mémoire, son autonomie, son accès aux données et sa capacité à planifier.

Obsidia part d’une question différente :

> **Dans quel système une intelligence peut-elle comprendre, apprendre et progresser sans que sa puissance lui donne automatiquement le droit d’agir ?**

Une intelligence peut être rapide, cohérente localement, bien outillée, convaincante, capable de générer du code ou de trouver un chemin, et rester dangereuse si son passage au réel n’est pas gouverné.

```text
comprendre
≠ proposer
≠ simuler
≠ prouver
≠ autoriser
≠ exécuter
```

Le système ne fait pas confiance à une intelligence uniquement parce qu’elle produit une bonne réponse. Il fait confiance au chemin contrôlé qu’elle est obligée d’emprunter.

## 5. Le premier produit : Obsidia V0.1

La première mise au monde d’Obsidia sera **Obsidia V0.1**.

La V0.1 sera le premier produit capable de rendre la stack utilisable comme un ensemble cohérent. Elle prendra la forme d’une interface unifiée permettant de connecter progressivement une organisation à Obsidia.

Son rôle ne sera pas seulement de répondre à des questions. Elle devra permettre de :

- observer une organisation ;
- reconstruire sa structure réelle ;
- comprendre ses composants ;
- comparer ce qui est déclaré et ce qui fonctionne ;
- identifier les dépendances et les contradictions ;
- proposer des transformations ;
- les simuler ;
- les tester ;
- les prouver ;
- demander une validation ;
- mesurer leur effet ;
- intégrer ce qui a été appris.

```text
connecter
→ observer
→ structurer
→ comprendre
→ prouver
→ proposer
→ simuler
→ qualifier
→ déléguer
→ mesurer
→ apprendre
→ reprojecter
```

La V0.1 doit devenir simultanément un cockpit, une interface conversationnelle, un système de compréhension organisationnelle, une forge de transformation, un environnement de simulation, une surface de preuve, un système de gouvernance et une mémoire structurée du fonctionnement réel.

## 6. Ce que la V0.1 permettra concrètement

Obsidia V0.1 sera la première interface permettant à une organisation de rendre son fonctionnement progressivement lisible par toute la stack Obsidia.

Elle ne sera pas seulement un assistant auquel on pose des questions. Elle devra permettre de passer de ressources dispersées à une représentation structurée, puis de cette représentation à des transformations contrôlées.

### 6.1 Connecter l’organisation

Une organisation pourra connecter progressivement :

- ses dépôts de code ;
- ses documents ;
- ses procédures ;
- ses règles métier ;
- ses bases de connaissances ;
- ses APIs ;
- ses outils internes ;
- ses tickets ;
- ses historiques d’incidents ;
- ses flux opérationnels ;
- ses systèmes de mesure ;
- ses preuves et rapports existants.

La V0.1 ne considérera pas immédiatement ces éléments comme vrais, actuels ou canoniques. Ils entreront d’abord comme sources à analyser.

```text
Sources de l’organisation
→ tri
→ provenance
→ fraîcheur
→ traduction
→ représentation structurée
```

### 6.2 Reconstruire ce qui existe réellement

La V0.1 devra différencier :

- ce qui est uniquement décrit dans un document ;
- ce qui existe sous forme de fichier ou de composant ;
- ce qui peut être importé ;
- ce qui est réellement appelé ;
- ce qui influence réellement un résultat ;
- ce qui a été testé ;
- ce qui est encore utilisé ;
- ce qui est obsolète ;
- ce qui est dupliqué ;
- ce qui est considéré comme stable sans preuve actuelle.

```text
Concept
→ artefact
→ import
→ route runtime
→ dépendances
→ test composant
→ test d’intégration
→ test E2E
→ effet causal
→ preuve
→ freeze
```

L’utilisateur ne devra plus parcourir seul des milliers de fichiers pour comprendre l’état de son système. Obsidia devra pouvoir répondre à des questions telles que : quels composants existent réellement, lesquels sont branchés, quelles routes les utilisent, quelles preuves sont encore valides, quelles dépendances sont manquantes et pourquoi une règle existe.

### 6.3 Comprendre l’organisation comme un système

Obsidia ne devra pas seulement indexer des documents. La V0.1 devra reconstruire les relations entre les personnes, les composants, les règles, les procédures, les outils, les risques, les décisions, les preuves, les responsabilités et les actions possibles.

```text
objets
+
relations
+
règles
+
risques
+
actions
+
preuves
+
responsabilités
+
temporalité
```

Cette représentation permettra de comprendre non seulement ce que l’organisation possède, mais comment elle fonctionne.

### 6.4 Transformer une demande humaine en mission gouvernée

L’utilisateur pourra dialoguer naturellement avec le Terminal.

> Audite la mémoire, vérifie ce qui est réellement branché, crée une branche séparée et propose uniquement les reconnexions sûres sans toucher au kernel.

La demande devra être traduite par l’OS IR en éléments opérationnels : intention, cible, contexte, composants concernés, exclusions, droits accordés, niveau de risque, preuves attendues, tests requis, conditions de HOLD et autorité nécessaire.

```text
Langage naturel
→ OS IR
→ intention canonique
→ plan actif
→ graphe de capacités
→ mission gouvernée
```

Brody interprète la langue vivante. L’OS IR la transforme en langage opérationnel stable. Le Terminal expose le déroulement de la mission.

### 6.5 Mobiliser uniquement les capacités nécessaires

La V0.1 ne devra pas appeler tous les organes pour chaque demande. Elle devra sélectionner les capacités utiles parmi Brody, la mémoire, les domaines, les outils, Sigma, Obsidure, Path Compute, Thermo, OIE, Lean, ProofKit, les registres et les couches de provenance ou de causalité.

```text
Besoin qualifié
→ capacités nécessaires
→ organes sélectionnés
→ exécution bornée
```

Une demande simple pourra être résolue localement. Une demande documentaire pourra rester readonly. Une demande de transformation pourra ouvrir une mission complète. Une action critique devra franchir les frontières d’autorité nécessaires.

### 6.6 Proposer une transformation sans l’imposer

Lorsqu’une amélioration est identifiée, la V0.1 devra produire une proposition structurée contenant le problème constaté, la cause probable, les composants concernés, le changement proposé, les risques, les dépendances, les tests nécessaires, les preuves disponibles, les effets attendus et les conditions de rollback.

```text
Compréhension
→ proposition
→ sandbox
→ tests
→ preuves
→ checkpoint
→ validation
→ promotion
```

Obsidure pourra construire la transformation. Sigma pourra détecter les contradictions et les manques. Lean pourra prouver certaines propriétés. X-108 et l’opérateur humain gouverneront le passage au réel.

### 6.7 Simuler avant d’agir

La V0.1 devra comparer l’état actuel, l’état proposé, les effets attendus, les effets secondaires possibles, le coût de l’action, le coût de l’inaction, les alternatives et le risque d’un rollback impossible.

Selon les cas, la simulation pourra prendre la forme d’un dry-run, d’une sandbox, d’un worktree isolé, d’un scénario métier, d’un replay, d’un test de charge, d’un fuzzing, d’une comparaison de trajectoires ou d’une exécution sur données synthétiques.

Le but est de rendre l’action réelle plus rare, plus explicable et plus facilement réversible.

### 6.8 Prouver ce qui peut réellement être prouvé

Chaque transformation devra être accompagnée de preuves correspondant à son périmètre réel : tests unitaires, tests d’intégration, tests E2E, rapports d’audit, traces, replay, receipts, vérifications Lean, contrôles de frontières et mesure de l’effet causal.

```text
propriété mathématique
≠ conformité du code
≠ fonctionnement runtime
≠ validité métier
≠ autorisation d’action
```

Une preuve ne devra jamais être étendue au-delà de ce qu’elle démontre.

### 6.9 Expliquer les refus et les blocages

Lorsqu’une mission ne peut pas continuer, la V0.1 devra expliquer quelle couche bloque, quelle contradiction a été détectée, quelle preuve manque, quelle information est trop ancienne, quelle source est incertaine, quelle permission n’a pas été accordée, quelle action serait irréversible et quelle prochaine étape reste possible.

```text
Refus
→ diagnostic de frontière
→ élément manquant
→ prochaine action sûre
```

Le refus devient une boussole plutôt qu’une sortie morte.

### 6.10 Mesurer l’effet réel d’une transformation

Après validation et exécution, la V0.1 devra mesurer si le changement a réellement été appliqué, si le comportement attendu apparaît, si les tests restent verts, si une nouvelle contradiction est apparue, si le coût a augmenté ou diminué, si une inférence distante a été évitée, si le système est devenu plus stable et si le rollback reste possible.

Le résultat devra être rattaché à la mission, la version, la date, la décision, la preuve, l’opérateur, l’état avant et l’état après.

### 6.11 Apprendre sans transformer toute expérience en vérité

Chaque mission pourra produire un apprentissage. Mais l’expérience brute ne devra pas automatiquement entrer dans la mémoire canonique.

Une donnée pourra rester brute, candidate, isolée, neutralisée, contestée ou en attente de validation. Dans le cas d’une attaque, d’une erreur ou d’un contenu polluant, Obsidia devra conserver la faiblesse révélée, la couche visée, l’effet causal, la défense efficace, la frontière à renforcer et le test à ajouter, sans nécessairement conserver le contenu dangereux comme connaissance réutilisable.

```text
Expérience
→ leçon neutralisée
→ candidat mémoire
→ triage
→ validation
→ mémoire collective
```

> **Extraire l’immunité, retirer la contagion.**

### 6.12 Construire une continuité indépendante du modèle utilisé

Les apprentissages ne devront pas appartenir uniquement au modèle qui les a produits. Ils devront être conservés dans l’architecture Obsidia : langage uni, OS IR, mémoire collective, registres, preuves, règles, compétences et raisons architecturales.

Brody pourra consulter et utiliser cette intelligence collective. Mais Brody ne la possédera pas.

```text
Le modèle peut évoluer ou être remplacé.
La continuité cognitive reste dans Obsidia.
```

### 6.13 Ce que verra l’utilisateur

Pour chaque mission, la V0.1 devra montrer simplement :

- la demande comprise ;
- le plan actif ;
- les capacités mobilisées ;
- les sources consultées ;
- les composants concernés ;
- les preuves disponibles ;
- les inconnues ;
- les contradictions ;
- les propositions ;
- les tests ;
- les décisions ;
- les validations humaines ;
- le résultat réel ;
- le receipt final.

L’objectif est que l’utilisateur comprenne le système sans avoir besoin de connaître toute son architecture interne.

## 7. À qui s’adresse Obsidia

Obsidia s’adresse aux organisations qui possèdent des systèmes complexes, plusieurs outils, des règles internes, des procédures, des actions sensibles, des données dispersées, des besoins de traçabilité et des transformations à gouverner.

Cela peut concerner une entreprise technologique, une PME, une banque, une industrie, un laboratoire, une administration, un acteur du transport, une entreprise e-commerce, une organisation de défense, une équipe de recherche ou une structure utilisant plusieurs agents IA.

Une organisation peut devenir progressivement un domaine Obsidia dès lors que son fonctionnement peut être décrit à travers :

```text
objets
+
règles
+
risques
+
actions
+
preuves
+
flux
+
responsabilités
```

Obsidia ne remplace pas le métier. Il construit les organes permettant au métier de devenir compréhensible, vérifiable et gouvernable.

## 8. Les problèmes auxquels Obsidia répond

### 8.1 Le modèle reste souvent le centre implicite

Même avec du RAG, des agents, une mémoire et des outils, le modèle reste souvent chargé de comprendre, choisir, raisonner, décider, expliquer et parfois agir. Obsidia sépare ces responsabilités. Le LLM devient un organe du système, pas son cerveau souverain.

### 8.2 Les organisations confondent présence et fonctionnement

Dans un système complexe, les états documenté, installé, importable, appelé, testé, utilisé, influent et stable sont souvent mélangés. Cette confusion produit doublons, composants orphelins, dépendances invisibles, faux sentiment de sécurité et erreurs de décision.

### 8.3 La mémoire est traitée comme une vérité

Une mémoire peut être brute, ancienne, contextuelle, contradictoire, non sourcée, polluée, candidate ou canonique. Obsidia refuse qu’une information devienne une vérité seulement parce qu’elle a été mémorisée.

### 8.4 L’inférence est appelée trop tôt

La plupart des architectures cherchent à optimiser : **quel modèle faut-il appeler ?** Obsidia ajoute une question précédente : **un modèle doit-il réellement être appelé ?**

Une demande connue peut parfois être reconnue, routée, vérifiée, résolue localement, refusée ou bornée sans réveiller un grand modèle distant.

### 8.5 Les agents de code confondent proposition et transformation

```text
idée
→ code
→ modification réelle
```

Obsidia impose une chaîne plus stricte :

```text
intention
→ proposition
→ sandbox
→ tests
→ preuves
→ validation
→ promotion
```

### 8.6 Une preuve est souvent étendue au-delà de son périmètre

Un théorème, un test ou un benchmark ne prouve jamais plus que ce qu’il mesure réellement. Obsidia cherche à attacher chaque preuve à son composant, son commit, sa version, ses hypothèses, sa date, son périmètre et son effet revendiqué.

### 8.7 Les refus sont peu informatifs

Obsidia vise un refus qui indique la frontière rencontrée, la contradiction, le contexte manquant, la preuve absente, la prochaine recherche utile et la couche à relancer.

## 9. La philosophie du projet

```text
Noyau souverain fermé
Périphérie spécialisée ouverte
Exploration autorisée
Souveraineté jamais déléguée
```

- **L’intelligence n’est pas l’autorité.** Une capacité à comprendre ou résoudre ne crée pas un droit d’agir.
- **La mémoire n’est pas la vérité.** Une trace doit franchir des contrôles avant de devenir canonique.
- **La preuve n’est pas l’autorisation.** Une preuve confirme une propriété ; elle ne décide pas qu’une action réelle doit être exécutée.
- **Le refus peut être productif.** Un refus structuré révèle une frontière et indique ce qui manque.
- **Le système doit apprendre sans absorber la pollution.** Une expérience hostile peut révéler une vulnérabilité, un lien causal, une défense efficace et une frontière à renforcer.
- **L’humain reste un opérateur de souveraineté.** L’utilisateur conserve la direction, la validation et la capacité de refus.

## 10. Les changements de paradigme

### 10.1 Structure avant inférence

```text
forme du problème
→ intention
→ domaine
→ risque
→ capacité
→ preuve attendue
→ inférence éventuelle
```

### 10.2 Intelligence distribuée

L’intelligence circule entre domaines, mémoire, outils, règles, preuves, Brody, Sigma, Obsidure et couches de calcul.

### 10.3 Autorité isolée

```text
possible
→ admissible
→ autorisé
→ réel
```

### 10.4 Mémoire gouvernée

```text
BRUT
→ candidat
→ triage
→ provenance
→ fraîcheur
→ validation
→ promotion canonique
```

### 10.5 Refus comme boussole

Le refus devient une information structurée sur la limite rencontrée.

### 10.6 Preuve attachée au runtime

Chaque affirmation importante doit pouvoir être reliée à une exécution, un test, une trace ou un modèle formel.

### 10.7 Économie d’inférence

Le système cherche à éviter les appels inutiles avant de chercher uniquement à réduire leur prix.

### 10.8 Entreprise comme système traduisible

Une entreprise devient une architecture composée d’objets, de flux, de règles, de risques, de preuves et d’actions.

## 11. L’état réel de la stack locale

Obsidia n’est plus principalement un concept. Mais Obsidia V0.1 n’est pas encore une version produit consolidée.

La stack locale actuelle est un système très large construit sur plusieurs mois. Elle est répartie entre la branche publique historique, des branches de construction, des tags, des freezes, des worktrees, des fichiers non suivis, des sauvegardes, des composants générés, des packs d’audit, des modules branchés, des modules présents mais non appelés et des composants historiques à requalifier.

Le travail actuel ne consiste pas à inventer la stack depuis zéro. Il consiste à déterminer précisément :

```text
ce qui existe
→ ce qui fonctionne
→ ce qui est réellement connecté
→ ce qui influence le résultat
→ ce qui est prouvé
→ ce qui peut être publié
```

### État synthétique au 17 juillet 2026

| Sous-système | Ce qui existe réellement | État actuel |
|---|---|---|
| X-108 / Kernel | Invariants, décisions bornées, HOLD/BLOCK, tests, preuves, receipts et replay | Fondation la plus stabilisée |
| Brody | Routes conversationnelles, contexte, mémoire, protections, vues opérateur et liens avec Sigma | Réel, intégration globale à reconfirmer |
| Mémoire / Graphiti | Lectures readonly, mémoire de projet et de session, candidats, sas BRUT/RAW | Réel, certains flux doivent être reconnectés |
| Sigma | Monitoring, dispatcher, registry multidomaine, bridges, rapports et intégrations API | Réel, Peripheral Mesh inégalement fermé |
| Obsidure | Cycle AVDR, propositions de code, sandbox, tests et attente de validation humaine | Réel, forge V0.1 encore incomplète |
| Lean / ProofKit | Corpus formel, manifests, rapports, contrôles et preuves | Réel, mapping preuve-runtime à renforcer |
| Domaines | Banque, Trading, E-commerce, GPS, Aviation, Défense et autres extensions | Réels à des niveaux de maturité différents |
| Terminal / Cockpit | Interface readonly, statuts, audits et panneaux techniques | V0 réelle, produit unifié non terminé |
| Router Track 1 | Routage avant inférence et résolution locale dans un dépôt séparé | Démonstrateur public réel |
| Obsidia V0.1 | Architecture produit, composants et boucle générale | Assemblage et fermeture en cours |

## 12. Ce qui est déjà stabilisé

### X-108 et la doctrine d’autorité

La séparation entre intelligence et autorité est stabilisée.

```text
KX108_ONLY
no bypass
no implicit ACT
HOLD before uncertainty
BLOCK on forbidden structure
```

Le kernel ne doit pas comprendre tout le monde réel. Les domaines traduisent leur réalité vers son alphabet.

### Plusieurs périmètres de preuve

Le projet possède déjà des tests Python, des preuves Lean, des modèles formels, des rapports ProofKit, des contrôles de frontières, des receipts, du replay, des freezes historiques et des contrôles d’intégrité.

### Des surfaces readonly réelles

Plusieurs composants ont été fermés historiquement en readonly ou dry-run : Brody, Graphiti, mémoire, World Action Bus, domaines, Sigma et Terminal.

### Plusieurs domaines démontrables

Banque, Trading, E-commerce et certaines familles GPS/Aviation/Défense ont déjà été utilisées comme terrains de validation de l’architecture.

### Routage avant inférence

Le dépôt séparé `obsidia-router` démontre déjà qu’une partie des demandes peut être reconnue, routée, résolue localement et vérifiée avant tout appel distant. Il expose un principe d’Obsidia sans représenter toute la stack.

## 13. Ce qui existe mais doit encore être consolidé

- **Brody complet :** de nombreuses briques existent, mais toutes les routes ne sont pas encore uniformément reliées à la stack maximale.
- **Mémoire unifiée :** les lectures et candidats existent ; la promotion canonique complète et la réconciliation globale doivent encore être fermées.
- **Peripheral Mesh :** provenance, fraîcheur, causalité, signaux physiques, Path Compute, Timeverse, Thermo, OIE, scénarios combinatoires, intégration de domaines et Anti-Mismatch existent à des niveaux de connexion et de preuve différents.
- **Obsidure comme constructeur général :** le cycle de proposition existe ; checkpoints, capacités, journalisation, promotion et rollback restent à fermer.
- **Terminal unifié :** le cockpit actuel est réel ; le Terminal cible doit devenir l’interface centrale des missions, plans, composants, preuves, validations et transformations.
- **Relation preuve-runtime :** chaque preuve importante doit encore être liée explicitement au composant, au commit et à la propriété runtime soutenue.

## 14. Le build maximal local

Le dépôt public `main` ne représente pas actuellement toute la surface construite localement.

```text
main public
→ base historique de preuve

build maximal local
→ plusieurs centaines de commits supplémentaires
```

Le snapshot maximal préservé est associé à :

```text
freeze/a-20260716-build-maximal
```

et au commit :

```text
a20e6aca8e78e53b0cce7c562dd8cb06437bdf7c
```

Au moment de la comparaison, ce build était :

```text
391 commits devant main
3 commits derrière main
```

Il contient une surface beaucoup plus large autour de Brody, Sigma, Obsidure, mémoire, domaines, OIE, Thermo, Lean, bus, Terminal, outils, intégrations et spécifications.

Le mot `freeze` signifie ici que l’état maximal a été préservé. Il ne signifie pas qu’il a été validé comme release. Les exécutions CI liées à cet état ont échoué pendant la suite complète de tests.

```text
build maximal préservé
≠ freeze vert
≠ release
≠ V0.1 terminée
```

Cet état doit être considéré comme un snapshot de reconstruction contenant la plus grande surface connue du projet.

Les inventaires font apparaître plusieurs milliers de fichiers et artefacts, des sauvegardes, des doublons, des composants historiques, des composants générés, des éléments audités mais pas connectés et environ deux cents composants supplémentaires à statuer précisément.

```text
préserver
→ inventorier
→ comprendre
→ classifier
→ reconnecter
→ tester
→ prouver
→ geler
```

## 15. La reconstruction canonique actuelle

Le chantier actuel vise à transformer le build maximal en une version canonique. Il faut notamment préserver les états locaux et distants, identifier la provenance de chaque composant, distinguer sauvegarde, legacy, candidat et canon, reconnecter les composants isolés, vérifier les imports et routes runtime, mesurer les effets causaux, rétablir les tests globaux, obtenir une CI verte, créer un registre permanent et produire un nouveau freeze.

Chaque composant doit recevoir un statut explicite :

```text
CONCEPT_ONLY
ARTEFACT_PRESENT
IMPORTABLE
RUNTIME_CALLED
COMPONENT_TESTED
INTEGRATION_TESTED
E2E_TESTED
CAUSAL_EFFECT_PROVED
FROZEN_GREEN
PUBLICLY_CLAIMABLE
```

Ordre structurel de reconstruction :

```text
Kernel
→ contrats et frontières
→ bus et traduction
→ mémoire
→ domaines
→ Sigma et Peripheral Mesh
→ Obsidure
→ Brody
→ Terminal
→ V0.1
```

## 16. L’architecture générale

```text
ENTRÉES DE L’ORGANISATION
│
├─ code
├─ documents
├─ procédures
├─ données
├─ outils
├─ événements
└─ demandes humaines
        │
        ▼
TRADUCTION ET COMPRÉHENSION
│
├─ OS Trad
├─ Unified Input IR
├─ compréhension du besoin
├─ contexte
└─ routage
        │
        ▼
PLAN ET CAPACITÉS
│
├─ Active Plan
├─ Capability Graph
├─ Corpus Resolver
└─ sélection des organes
        │
        ▼
ORGANES SPÉCIALISÉS
│
├─ Brody
├─ Mémoire / Graphiti
├─ Domaines
├─ Obsidure
├─ Sigma
├─ Path Compute
├─ Thermo
├─ OIE
└─ outils
        │
        ▼
PREUVES ET GOUVERNANCE
│
├─ tests
├─ replay
├─ Lean
├─ ProofKit
├─ receipts
└─ checkpoints
        │
        ▼
X-108
│
├─ HOLD
├─ BLOCK
└─ permission bornée
        │
        ▼
ACTION CONTRÔLÉE
│
├─ exécution
├─ mesure
├─ apprentissage
└─ re-projection
```

Toutes les demandes ne parcourent pas toute la chaîne. Une tâche simple peut être résolue localement. Une consultation readonly peut s’arrêter avant X-108. Une action critique doit franchir les frontières nécessaires.

## 17. Les principaux organes

### X-108

X-108 est la frontière d’autorité. Il protège le passage entre candidat, décision et action réelle. Il ne remplace pas les autres organes ; il juge les structures qu’ils lui transmettent.

### Brody

Brody est le moteur conversationnel et cognitif propriétaire d’Obsidia. Il peut comprendre, relier, reformuler, synthétiser, expliquer, consulter la mémoire et utiliser des outils bornés. Brody n’est pas la mémoire. Brody ne décide pas.

### Mémoire / Graphiti

La mémoire assure la continuité. Elle conserve sessions, projets, relations, traces, candidats, événements et contextes. Une mémoire n’est jamais automatiquement une vérité canonique.

### Sigma

Sigma surveille la cohérence dynamique de la stack. Il détecte contradictions, dérives, flips, collapses, incohérences inter-couches, preuves manquantes et blocages. Il peut retrouver, guider et expliquer. Il ne tranche pas à la place de X-108.

- **Sigma Core :** surveillance de cohérence et de trajectoire.
- **Sigma Guidance :** transformation d’une alerte en recommandation exploitable.
- **Sigma Introspective Search :** recherche interne dans les preuves, corpus, traces, registres et composants.
- **Couche de stabilisation :** lecture plus large de la tenue d’une trajectoire dans le temps. Sigma participe à la stabilisation ; il ne représente pas toute la stabilisation.

### Peripheral Mesh

Le Peripheral Mesh regroupe les organes spécialisés qui ne doivent pas être absorbés dans Sigma : Data Gate, Provenance Gate, Oracle Freshness, Physical Signal Periphery, Causal Trace Layer, Meta/Coordination, Path Compute, Timeverse/GPC, Thermo, OIE, OCS, Domain Integration et Combinatorial Scenario Lab.

Les couches produisent des rapports spécialisés. Sigma en surveille la cohérence globale.

### Obsidure

Obsidure est le constructeur gouverné. Il peut inspecter, proposer, générer un patch candidat, travailler en sandbox, tester, produire une preuve et attendre une validation. Il ne doit ni commit, ni push, ni promouvoir automatiquement une transformation.

### Lean et ProofKit

Lean prouve des propriétés dans un cadre formel. ProofKit produit et organise des artefacts de vérification. Ils ne prennent aucune décision métier.

### Terminal

Le Terminal doit devenir la surface unifiée permettant de comprendre et piloter toute la stack. Il doit montrer le plan actif, les capacités mobilisées, les couches consultées, les preuves, les contradictions, les décisions, les checkpoints, les receipts et les statuts réels des composants.

## 18. Les domaines et les possibilités d’extension

Obsidia n’est pas conçu pour un secteur unique. Banque, Trading, E-commerce, GPS, Aviation ou Défense sont des terrains déjà explorés dans le projet. Ils ne constituent pas les limites du système : ils montrent qu’une même architecture de gouvernance peut être appliquée à des réalités différentes.

### 18.1 Ce qu’est un domaine dans Obsidia

Un domaine est une couche spécialisée capable de comprendre une partie précise du réel. Il possède ses objets, son vocabulaire, ses règles, ses risques, ses actions, ses contraintes, ses sources, ses preuves, ses temporalités et ses responsabilités.

Dans un dépôt logiciel, les objets peuvent être fichiers, fonctions, branches, tests, dépendances, services et déploiements. Dans une banque, ils peuvent être comptes, transactions, limites, clients, alertes, autorisations et obligations réglementaires. Dans une usine, ils peuvent être machines, capteurs, procédures, opérateurs, incidents, ordres de maintenance et arrêts de production.

```text
Le domaine traduit.
X-108 tranche.
```

### 18.2 Une entreprise peut contenir plusieurs domaines

Une organisation ne devient pas un domaine monolithique. Elle peut être découpée en plusieurs Domain Packs :

```text
Entreprise
│
├─ logiciel
├─ finance
├─ ressources humaines
├─ conformité
├─ sécurité
├─ production
├─ logistique
├─ vente
├─ support client
└─ recherche
```

Chaque domaine conserve son propre langage et ses propres règles. Obsidia construit les ponts nécessaires entre eux.

```text
Support client → détecte un problème récurrent
Logistique → confirme une rupture
Finance → mesure le coût
Conformité → identifie une obligation
Path Compute → propose plusieurs trajectoires
Sigma → détecte les contradictions
X-108 → gouverne l’action critique
```

L’objectif n’est pas de fusionner tous les métiers dans un modèle généraliste, mais de permettre à plusieurs organes spécialisés de coopérer sans perdre leurs frontières.

### 18.3 Comment un nouveau domaine est créé

Domain Integration Layer doit permettre de transformer progressivement une réalité métier en Domain Pack.

```text
Réalité métier
→ objets
→ relations
→ règles
→ risques
→ actions
→ preuves
→ traduction vers le langage Obsidia
```

La construction d’un domaine peut comprendre :

1. l’inventaire des objets métier ;
2. la définition du vocabulaire canonique ;
3. la cartographie des flux ;
4. l’identification des actions sensibles ;
5. l’identification des risques ;
6. la définition des preuves nécessaires ;
7. la création des traducteurs ;
8. la création des contrats ;
9. la création des agents spécialisés ;
10. la création des tests et scénarios ;
11. la connexion readonly ;
12. la validation avant toute action réelle.

Le domaine ne crée pas sa propre loi. Il apprend à traduire son réel vers la gouvernance existante.

### 18.4 Développement logiciel et systèmes numériques

Obsidia pourra aider à cartographier les dépôts, retrouver les composants canoniques, distinguer code mort, legacy, backup et runtime, comprendre les dépendances, vérifier les routes réelles, identifier les composants orphelins, détecter les duplications, relier les tests aux composants, proposer des corrections, exécuter en sandbox, produire des checkpoints, gouverner les promotions et conserver un historique vérifiable.

> Identifie les composants mémoire présents mais non appelés, vérifie leurs dépendances, propose les reconnexions sûres dans un worktree isolé et arrête-toi avant toute promotion.

### 18.5 Opérations et procédures

Dans une organisation reposant sur des procédures, Obsidia pourra lire les SOP, reconstruire les étapes réelles, détecter les divergences entre procédure écrite et pratique, identifier les actions critiques, relier les preuves nécessaires, détecter les responsabilités manquantes, simuler une nouvelle procédure et mesurer l’effet d’un changement.

Cela peut concerner l’industrie, la santé, le transport, la logistique, l’administration, la maintenance, la qualité ou la sécurité.

### 18.6 Finance, banque et assurance

Obsidia pourra être appliqué à des environnements où l’action doit être fortement gouvernée : opérations financières, limites, fraude, conformité, scoring, contrôle des risques, justification des décisions, détection de contradictions, replay d’un dossier et séparation entre recommandation et autorisation.

Les moteurs métier pourront produire des signaux. Ils ne devront jamais devenir l’autorité finale.

### 18.7 Industrie et infrastructures physiques

Dans une industrie, Obsidia pourra relier machines, capteurs, procédures, maintenance, historiques de panne, opérateurs, contraintes de sécurité, coûts d’arrêt et trajectoires de production.

Physical Signal Periphery pourra lire les signaux. Causal Trace Layer pourra reconstruire les événements. Path Compute pourra comparer plusieurs réponses. Thermo pourra mesurer les coûts et dissipations. Sigma pourra détecter une incohérence globale. X-108 pourra protéger l’action critique.

### 18.8 Mobilité, aviation, spatial et défense

Ces domaines contiennent souvent des sources multiples, des informations contradictoires, des contraintes temporelles, des trajectoires, des décisions irréversibles, du fonctionnement dégradé et des exigences fail-closed.

Obsidia peut y apporter traduction de signaux, provenance, fraîcheur, cohérence spatiale et temporelle, simulation de trajectoires, détection de contradiction, replay, preuve et séparation entre calcul et autorisation.

Le système ne prétend pas remplacer les logiciels certifiés existants. Il vise à devenir une couche de compréhension, de preuve et de gouvernance autour de leurs décisions et transformations.

### 18.9 E-commerce, commerce et relation client

Dans un environnement commercial, plusieurs domaines peuvent coopérer : catalogue, prix, commandes, fraude, logistique, marketing, support, finance et conformité.

Obsidia pourra comprendre une anomalie de commande, vérifier le catalogue et la logistique, consulter les règles commerciales, détecter une contradiction, proposer une compensation, vérifier les droits, produire une réponse client et demander validation pour une action financière.

Brody pourra comprendre et formuler. Les domaines vérifieront leur terrain. X-108 gouvernera les actions sensibles.

### 18.10 Recherche, science et connaissance

Dans un laboratoire ou une équipe de recherche, Obsidia pourra organiser un corpus, suivre la provenance, vérifier la fraîcheur, séparer faits, hypothèses et spéculations, retrouver des contradictions, construire des cartes causales, relier les expériences, conserver les résultats négatifs, produire des preuves et reconstruire l’histoire d’une conclusion.

Sigma Introspective Search pourra rechercher ce que le système possède déjà. La mémoire pourra préserver les apprentissages. Brody pourra relier et expliquer. Aucune convergence ne devra être présentée comme vérité sans preuve adaptée.

### 18.11 Conformité, audit et gouvernance

Obsidia pourra retrouver les obligations, identifier les responsabilités, relier une règle à son application, détecter des preuves manquantes, vérifier la traçabilité, reconstruire un incident, produire un rapport, mesurer l’écart entre politique et runtime et conserver un receipt de validation.

Il ne remplacera pas l’autorité juridique ou réglementaire. Il fournira une structure plus vérifiable à l’organisation.

### 18.12 Ressources humaines et fonctionnement interne

Un domaine RH pourrait être limité à des fonctions gouvernées comme la cartographie des rôles, les procédures d’onboarding, les compétences, les accès, les responsabilités, les formations, les obligations et les workflows internes.

Les données humaines sensibles devront rester soumises à des politiques strictes de consentement, minimisation, confidentialité et non-discrimination. La possibilité technique d’analyser une donnée ne constitue jamais une autorisation de l’utiliser.

### 18.13 Le principe commun à tous les domaines

```text
Le domaine comprend son terrain.
L’OS IR traduit.
La mémoire conserve sous gouvernance.
Brody relie et formule.
Les couches spécialisées mesurent.
Sigma surveille et guide.
Lean et ProofKit produisent des preuves bornées.
X-108 gouverne le passage au réel.
```

L’extension d’Obsidia ne consiste pas à entraîner un modèle différent pour chaque entreprise. Elle consiste à construire les organes, les contrats, les preuves et les traductions permettant à chaque organisation de parler à la même architecture de gouvernance.

### 18.14 La possibilité à long terme

À terme, une organisation pourra construire progressivement son propre système cognitif gouverné :

```text
Mémoire de l’organisation
+
langage métier
+
domaines spécialisés
+
outils
+
preuves
+
règles
+
histoire des décisions
+
frontière d’autorité
```

Le modèle conversationnel pourra évoluer. Les outils pourront être remplacés. Les domaines pourront être enrichis. La continuité restera dans l’architecture, les mémoires, les contrats, les preuves et les chemins gouvernés d’Obsidia.

## 19. Ce que contient ce dépôt public

`obsidia-x108-proofs` constitue le périmètre public de preuve et de vérification de l’écosystème Obsidia.

Selon les branches et paliers, il contient notamment le kernel X-108, des contrats, des invariants, des modèles Lean, des modèles TLA+/TLC, des vérificateurs Python, des tests, Sigma, ProofKit, des rapports, des mécanismes de replay, des receipts, des composants readonly, des domaines, des composants périphériques, des routes API, des outils d’audit, des spécifications du Terminal et des snapshots expérimentaux.

Le dépôt public doit permettre de comprendre ce qu’Obsidia défend, comment l’autorité est séparée, quels éléments existent réellement, ce qui est prouvé, ce qui reste expérimental et où en est la construction du produit.

### Dépôt complémentaire

`obsidia-router` présente séparément une démonstration de routage avant inférence. Cette démonstration ne doit pas être confondue avec la stack Obsidia complète.

## 20. Ce que ce dépôt ne prétend pas encore

Ce dépôt ne prétend pas que :

- la V0.1 est terminée ;
- la stack maximale est actuellement verte ;
- chaque fichier est actif ;
- tous les composants sont connectés ;
- chaque domaine est prêt pour la production ;
- chaque théorème Lean prouve le runtime complet ;
- Sigma garantit toutes les décisions ;
- Brody possède une autorité ;
- Obsidure peut modifier librement le projet ;
- le système agit actuellement de manière autonome ;
- Obsidia constitue déjà une AGI ;
- les recherches sur la conscience démontrent une conscience artificielle.

```text
présent ≠ connecté
connecté ≠ causalement utile
testé ≠ prouvé globalement
préservé ≠ gelé vert
ambition ≠ capacité actuelle
```

## 21. La route vers la V0.1

La fermeture de la V0.1 nécessite encore plusieurs capacités structurelles.

### Registre canonique permanent

Chaque composant doit posséder une fiche :

```text
component_id
canonical_name
aliases
path
origin
role
dependencies
imports
runtime_status
proof_status
last_test
canonical_or_legacy
destination
```

### Runtime Supervisor

```text
CONFIG_PRESENT
PROCESS_PRESENT
PORT_OPEN
ENDPOINT_RESPONDS
COMPONENT_TESTED
INTEGRATION_TESTED
E2E_TESTED
```

### Moteur de checkpoints

```text
proposition
→ autorisation
→ exécution bornée
→ checkpoint
→ acceptation / correction / rollback
```

### Journal événementiel append-only

```text
MISSION_CREATED
BASELINE_CAPTURED
TOOL_REQUESTED
TOOL_AUTHORIZED
TOOL_EXECUTED
PATCH_PROPOSED
TEST_COMPLETED
KERNEL_VERDICT
HUMAN_DECISION
PROMOTION_COMPLETED
MISSION_CLOSED
```

### Capability and Credential Broker

Les agents doivent recevoir des capacités temporaires plutôt que des secrets permanents.

### Sandbox complète

Elle doit assurer isolation, réseau désactivé par défaut, quotas, absence de secrets, idempotence, interruption, gestion des échecs partiels, rollback et destruction vérifiée.

### Registre de versions

Les contrats entre OS Langage, IR, outils, mémoire, domaines, kernel et receipts doivent être versionnés ensemble.

### Mapping preuve-runtime

Chaque propriété formelle doit être rattachée à la version du composant qu’elle soutient.

### Self-hosting gouverné

```text
mission
→ analyse du Terminal
→ proposition
→ sandbox
→ tests
→ X-108
→ validation humaine
→ promotion
→ receipt
```

### Freeze global

La V0.1 ne pourra être déclarée fermée qu’après reconstruction canonique, tests globaux verts, CI verte, routes E2E, statuts explicites, preuves attachées, documentation réalignée et freeze reproductible.

## 22. La vision à long terme

L’histoire de l’IA a successivement cherché à faire raisonner la machine, apprendre depuis les données, produire du langage général, reconnecter les modèles au savoir, donner des outils aux agents et augmenter leur autonomie.

Obsidia ajoute une question :

> **Comment gouverner le chemin entre savoir, compréhension, réponse et action ?**

Le projet ne cherche pas à nier les avancées précédentes. Il cherche à réunir la logique du symbolique, l’apprentissage statistique, la puissance des LLM, la mémoire externe, les graphes, les outils, les agents, la preuve formelle, le logiciel critique, l’opérateur humain, le refus et la traçabilité sans reprendre leurs angles morts.

La différence ne repose pas sur une brique magique. Elle repose sur leur assemblage sous contrainte.

```text
Les domaines comprennent leur terrain.
La mémoire conserve sous gouvernance.
Brody comprend et formule.
Obsidure construit et propose.
Lean prouve dans un périmètre défini.
Sigma surveille, retrouve, guide et explique.
X-108 tranche.
Le Terminal rend le système utilisable.
```

L’ambition d’Obsidia n’est pas de concentrer toujours plus d’intelligence dans un modèle unique. Elle est de construire un environnement dans lequel plusieurs formes d’intelligence peuvent progresser, coopérer et apprendre sans devenir souveraines.

```text
La Big Tech a principalement travaillé sur :

modèle
→ réponse

Obsidia travaille sur :

source
→ tri
→ mémoire
→ compréhension
→ proposition
→ preuve
→ refus possible
→ décision gouvernée
→ action
→ replay
```

La première étape de cette vision sera Obsidia V0.1 :

> **Un système capable de connecter une organisation, d’en reconstruire le fonctionnement réel, de proposer des transformations, de les simuler, de les prouver et de gouverner leur passage au réel.**
