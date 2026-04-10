# Limites et Périmètre du Système Obsidia

La transparence est la base de la confiance. Obsidia est un système de gouvernance déterministe puissant, mais il possède des limites structurelles assumées. Ce document détaille ce que le système **ne fait pas**, et les cas où son utilisation est inappropriée.

## 1. Ce qu'Obsidia ne fait pas

### 1.1. Pas de raisonnement sémantique dans le Noyau
Le Noyau Déterministe (Governance Core) ne "comprend" pas le texte, les images ou les concepts humains. Il évalue des invariants mathématiques (Lean 4) et des règles logiques strictes. Si une IA générative propose une action poétique mais qui viole une règle de risque financier, le noyau bloquera l'action sans tenir compte du contexte poétique.

### 1.2. Pas de génération de contenu direct
Obsidia n'est pas un LLM. Il ne génère pas de texte, de code ou d'images. Il se positionne **après** la génération (par un système tiers comme OpenAI, Anthropic, ou un modèle local) pour valider ou bloquer l'action qui en découle.

### 1.3. Pas de réparation automatique de l'IA
Si une IA connectée à Obsidia se met à halluciner en boucle et propose 10 000 actions illégales, Obsidia bloquera les 10 000 actions (taux de blocage de 100%). Cependant, Obsidia ne "réparera" pas l'IA source pour l'empêcher d'halluciner. Il protège le système cible, il ne soigne pas le système source.

## 2. Limites Structurelles (Trade-offs)

### 2.1. Le compromis Latence / Complexité
Le Protocole Reflex garantit une latence d'interception inférieure à 5ms. Cependant, cette vitesse extrême nécessite que les règles (invariants) soient évaluables en temps constant. Les règles nécessitant des appels API externes complexes ou des calculs probabilistes lourds ne peuvent pas être exécutées dans la couche Reflex (elles doivent être évaluées en amont dans l'Espace Latent).

### 2.2. Rigidité Déterministe (Le "Faux Positif" assumé)
Obsidia préférera toujours un faux positif (bloquer une action légitime mais ambiguë) à un faux négatif (laisser passer une action dangereuse). Si les paramètres de la requête frôlent les limites de l'invariant sans les dépasser clairement, le système appliquera un `HOLD` (mise en attente) ou un `BLOCK`. Il n'y a pas de "tolérance exceptionnelle" dans le noyau.

### 2.3. Dépendance à la qualité des Invariants
Obsidia garantit que les règles définies ne seront jamais violées. Cependant, si les règles définies par l'opérateur humain sont intrinsèquement mauvaises, obsolètes ou incomplètes, Obsidia exécutera ces mauvaises règles avec une précision absolue. Le système est mathématiquement prouvé, mais la pertinence métier des règles reste la responsabilité de l'intégrateur.

## 3. Vecteurs d'Attaque Non Couverts

### 3.1. Compromission Physique du Serveur (Hardware)
Les preuves Lean 4 et les spécifications TLA+ prouvent la logique logicielle. Elles ne protègent pas contre un acteur malveillant ayant un accès physique ou root au serveur exécutant le noyau, qui pourrait altérer la RAM ou modifier les binaires compilés (bien que l'ancrage Merkle détecterait l'anomalie a posteriori).

### 3.2. Attaques Sybil sur les sources de données (Oracles)
Si une règle déterministe dépend d'une source de données externe (ex: le prix du Bitcoin sur un exchange), et que cet exchange est piraté pour envoyer de fausses données, Obsidia prendra une décision déterministe basée sur ces fausses données. La sécurisation des oracles externes est hors du périmètre du noyau.

---
*Ce document est mis à jour à chaque itération majeure du protocole X-108.*
