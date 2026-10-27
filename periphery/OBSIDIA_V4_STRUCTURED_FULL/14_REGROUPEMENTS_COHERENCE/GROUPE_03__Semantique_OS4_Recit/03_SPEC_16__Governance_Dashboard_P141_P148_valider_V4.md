# Spec 16 — Governance Dashboard (P141-P148) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** Governance Dashboard

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
16) SPEC — Governance Dashboard
(policy / violations / replay)
16.0 Objectif
Fournir une interface de gouvernance souveraine permettant à un humain (dirigeant, auditeur, institution) de :
voir ce qui est autorisé
voir ce qui a été violé
rejouer ce qui s’est réellement passé
sans jamais agir sur le système en direct
👉 Le dashboard ne décide rien, n’exécute rien, n’écrit rien.
16.1 Principes fondamentaux
Read-only absolu
Aucune action destructive
Vue déterministe (ce qui est affiché = ce qui est dans les traces)
Séparation stricte :
gouvernance ≠ exécution
lecture ≠ contrôle
16.2 Architecture logique
OS3 (Audit)
 ├─ traces/
 ├─ violations/
 ├─ policies/
 ├─ replays/
 └─ reports/
Governance Dashboard
 ├─ Policy Viewer
 ├─ Violation Monitor
 ├─ Replay Inspector
 ├─ Timeline / Merkle Tree
 └─ Export Center (read-only)
16.3 Modules du dashboard
A) Policy Viewer
Affiche :
policy_id
policy_hash
version
date d’activation
scopes autorisés
limites (cost, tools, write)
Fonctions :
comparaison policy vN / vN+1
affichage policy compilée, jamais la source
B) Violation Monitor
Table temps réel (ou différé) :
Filtres :
par couche
par sévérité
par policy
par MCP server
C) Replay Inspector
Sélection d’un trace_id :
Affiche :
input attendu
output observé
output rejoué
hash match / mismatch
divergence (si existante)
👉 Aucun replay ne modifie l’état système
D) Timeline & Merkle Tree
Vue chronologique :
t0 ─ policy_loaded
t1 ─ tool_call
t2 ─ output_received
t3 ─ audit_pass
t4 ─ replay_match
racine Merkle globale pour vérification externe
E) Export Center
Export ZIP audit
Export PDF signé
Export JSON brut
16.4 Accès & rôles
