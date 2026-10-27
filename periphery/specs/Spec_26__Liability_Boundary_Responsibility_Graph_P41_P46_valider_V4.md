# Spec 26 — Liability Boundary & Responsibility Graph (P41-P46) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** Liability Boundary & Responsibility Graph

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
26) SPEC — Liability Boundary & Responsibility Graph
26.0 Objectif
Définir qui est responsable de quoi, à quel niveau, et jusqu’où, de façon :
explicite,
non ambiguë,
prouvable.
26.1 Principe clé
Obsidia ne dilue jamais la responsabilité.
26.2 Graphe de responsabilité (conceptuel)
Human Operator
   ↓ (veto signé)
Governance Layer
   ↓ (policy compile)
OS3 Audit Layer
   ↓ (execution trace)
Agents / Tools
26.3 Frontières de responsabilité
A) Humain
Responsable de :
l’intention
le veto
l’autorisation finale
❌ Jamais responsable d’une exécution technique non autorisée
B) Obsidia (système)
Responsable de :
l’application stricte des policies
la traçabilité
l’audit
la non-exécution sans veto
C) Outils / MCP / agents
Responsables de :
leur comportement interne
leur conformité déclarée
❌ Jamais décisionnaires
26.4 Encodage dans les traces
Chaque événement porte :
responsibility:
- actor_type (human / system / tool)
- actor_id
- authority_scope
26.5 Cas de litige
L’audit permet de répondre formellement à :
Qui a permis l’action ?
Qui l’a exécutée ?
Qui ne pouvait pas l’empêcher ?
Où la chaîne s’arrête ?
👉 Pas de zone grise, pas de “responsabilité diffuse”.
