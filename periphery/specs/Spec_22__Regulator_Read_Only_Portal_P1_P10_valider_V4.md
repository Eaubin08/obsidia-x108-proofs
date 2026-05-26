# Spec 22 — Regulator Read-Only Portal (P1-P10) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** Regulator Read-Only Portal

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
22) SPEC — Regulator Read-Only Portal
22.0 Objectif
Fournir à une autorité externe (CNIL, ANSSI, Cour des comptes, Commission UE, inspection ministérielle) un accès strictement en lecture, cryptographiquement borné, non interactif, au système Obsidia.
👉 Ce portail ne permet aucune action, aucune configuration, aucune requête libre.
22.1 Principes non négociables
READ-ONLY absolu
Accès temporellement borné
Aucune dépendance au runtime actif
Données pré-scellées
Zéro accès aux outils / agents / policies actives
22.2 Mode d’accès
A) Accès par session régulatrice
Regulator Session:
- Session ID
- Scope = READ_ONLY
- Time Window = [T_start, T_end]
- Data Snapshot Hash
- Signature Authority
➡️ Généré hors runtime, à partir d’OS3.
B) Authentification
Certificat institutionnel (X.509 ou équivalent)
Session token signé (usage unique)
Expiration automatique
❌ Aucun login utilisateur classique
❌ Aucun compte persistant
22.3 Données accessibles
✓ Audit reports (HTML / PDF)
✓ Replay packs (ZIP)
✓ Policy snapshots (compiled)
✓ Violation logs
✓ Merkle roots
✓ Incident reports
✓ Governance timeline
❌ Pas de :
prompt
modèle
agent
tool call en direct
policy modifiable
22.4 Interface (textuelle)
[HEADER]
Regulatory Portal – OBSIDIA
Jurisdiction: EU / FR
Audit Window: T1 → T2
Snapshot Hash
[MENU]
- Executive Summary
- Policies (compiled)
- Violations
- Replays
- Incidents
- Exports
[MAIN]
(read-only tables)
[FOOTER]
Merkle Root
Global Signature
22.5 Garantie juridique fournie
Aucun biais d’observation
Aucune manipulation possible
Preuve de non-intervention humaine
👉 Le portail montre ce qui a existé, pas ce qui existe maintenant.
