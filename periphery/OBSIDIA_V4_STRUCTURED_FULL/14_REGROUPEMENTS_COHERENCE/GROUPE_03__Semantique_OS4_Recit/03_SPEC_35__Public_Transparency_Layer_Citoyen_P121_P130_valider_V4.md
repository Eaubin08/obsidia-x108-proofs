# Spec 35 — Public Transparency Layer Citoyen (P121-P130) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** Public Transparency Layer (Citoyen)

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
35) SPEC — Public Transparency Layer (Citoyen)
35.0 Objectif
Rendre Obsidia lisible par le citoyen, sans exposition de données ni de complexité technique.
35.1 Principe
La transparence ne donne pas accès au système.
Elle donne accès à sa vérité structurelle.
35.2 Contenu exposé publiquement
✓ Constitution hashée
✓ Nombre d’audits
✓ Nombre de vetos humains
✓ Nombre de violations
✓ État de conformité global
❌ Jamais exposé :
données
logs
policies détaillées
clés
35.3 Interface
[ Tableau public ]
- statut : conforme / non conforme
- dernière vérification
- périmètre couvert
35.4 Effet politique
Responsabilité visible
Pas de boîte noire
Confiance mesurable
Débat démocratique possible
35.5 Garantie clé
Un citoyen peut vérifier qu’aucune IA ne décide pour lui.
