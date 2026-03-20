# Le Sigma Engine

## 1. Qu'est-ce que le Sigma Engine ?

Le **Sigma Engine** est le composant de validation et d'orchestration qui fait le pont entre le Noyau Déterministe (Obsidia Kernel) et le monde réel. 

Si le noyau X-108 est le "juge" qui évalue les règles mathématiques, le Sigma Engine est "l'huissier" qui s'assure que :
1. Les données entrantes sont bien formées avant d'être jugées.
2. La décision du juge est correctement ancrée cryptographiquement (Merkle Tree).
3. L'exécution finale respecte strictement la décision rendue.

## 2. Rôle dans l'Architecture

Dans l'architecture globale, le Sigma Engine se situe entre les agents périphériques et le noyau déterministe :

`Agents Cognitifs (Espace Latent) -> SIGMA ENGINE -> Noyau Déterministe (X-108)`

Il a trois responsabilités principales :

### A. Formatage Canonique
Il reçoit les intentions brutes des agents IA (ex: "Je veux acheter pour 10 millions de BTC") et les convertit dans le format canonique exigé par le protocole X-108 (payload JSON strict avec métriques de volatilité, de friction et de régime de marché).

### B. Validation des Invariants Locaux
Avant même de solliciter le noyau, le Sigma Engine vérifie les invariants de base (ex: est-ce que le montant est positif ? est-ce que l'agent est autorisé à parler ?). S'il y a une erreur grossière, il rejette la requête immédiatement sans consommer de ressources de preuve.

### C. Ancrage et Traçabilité
Une fois la décision rendue par le noyau (`ALLOW`, `HOLD`, `BLOCK`), le Sigma Engine génère l'identifiant unique de la décision (`decision_id`), la trace (`trace_id`), et met à jour l'arbre de Merkle pour garantir l'auditabilité parfaite de l'événement.

## 3. Preuves de fonctionnement

Le bon fonctionnement du Sigma Engine est prouvé par la batterie de tests continus (v1.3.0) :
- **Tests unitaires (pytest) :** 100% PASS (22/22)
- **Tests d'intégration (vitest) :** 100% PASS (39/39)
- **Batteries adversariales :** Plus de 1 million de cas testés sans faille.

*Note : Le code source du Sigma Engine fait partie du moteur de production propriétaire et n'est pas inclus dans ce dépôt public.*
