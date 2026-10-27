# Spec 23 — Cross-Territory Audit Federation (P11-P20) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** Cross-Territory Audit Federation

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
23) SPEC — Cross-Territory Audit Federation
23.0 Objectif
Permettre à plusieurs territoires / institutions d’auditer le même système, sans partager :
runtime
données internes
gouvernance locale
23.1 Problème traité
Systèmes transfrontaliers
Exigences divergentes (UE, FR, région, organisme)
Besoin de cohérence sans centralisation
23.2 Principe fondamental
Chaque territoire conserve sa souveraineté, mais les preuves sont compatibles.
23.3 Architecture fédérée
Territory A (FR)
- OS3 instance
- Audit artifacts
Territory B (EU)
- OS3 instance
- Audit artifacts
Shared:
- Merkle root compatibility
- Policy hash alignment
❌ Aucun runtime partagé
❌ Aucun accès croisé direct
23.4 Fédération par preuves
Artefacts échangés
- Merkle roots
- Policy hashes
- Replay summary
- Violation summary
➡️ Jamais les traces brutes complètes sauf demande formelle.
23.5 Vérification croisée
Chaque autorité peut vérifier :
- même policy_hash ?
- même replay outcome ?
- même violation count ?
Si divergence → signal d’alerte formel
23.6 Cas d’usage typiques
Région vs État
État vs UE
Ministère vs Autorité indépendante
Collectivité vs Cour des comptes
👉 Obsidia devient audit-compatible multi-souverain, sans être centralisé.
