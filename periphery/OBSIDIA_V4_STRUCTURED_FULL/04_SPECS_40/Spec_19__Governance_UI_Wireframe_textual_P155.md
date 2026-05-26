# Spec 19 — Governance UI Wireframe textual (P155)

**Statut V4 :** À_FORMALISER_OU_À_PROUVER
**Titre source détaillé :** Governance UI Wireframe (textual)

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
19) SPEC — Governance UI Wireframe (textual)
(lecture humaine, gouvernance souveraine)
19.0 Objectif
Définir la structure textuelle (non graphique) de l’interface de gouvernance Obsidia.
👉 Ce wireframe est :
implémentable en HTML simple
lisible en PDF
projetable en interface institutionnelle
indépendant de toute techno front
19.1 Règles UI fondamentales
Zéro action destructive
Zéro bouton “execute / approve / override”
Navigation par lecture uniquement
Toutes les données sont issues d’OS3
Chaque vue est horodatée et signée
19.2 Layout global (texte)
[HEADER]
- System: OBSIDIA
- Mode: GOVERNANCE / READ-ONLY
- Policy Hash: <hash>
- Audit Window: <start> → <end>
[LEFT NAV]
- Overview
- Policies
- Violations
- Replays
- Timeline
- Exports
- Incidents
[MAIN PANEL]
(dynamic)
[FOOTER]
- Merkle Root
- Signature Status
- Timestamp
19.3 Pages détaillées
A) Overview
System Status: STABLE
Active Policy: POLICY_2026_03 (hash)
Total Traces: 12,482
Violations: 3 (0 critical)
Replays Verified: 100%
B) Policies
Policy ID | Version | Hash | Active Since | Status
--------------------------------------------------
POL-01    | v3      | abc… | 2026-03-01   | ACTIVE
Click → Policy Detail (compiled)
Scopes:
- tools.allowed = [read, compute]
- write = false
- max_cost = 0.05
Policy hash: xyz
C) Violations
Timestamp | Session | Code | Severity | Outcome
------------------------------------------------
t1        | S-01    | COST_LIMIT | MEDIUM | BLOCK
Click → Violation Detail
policy rule violated
trace reference
automatic action taken
D) Replays
Trace ID | Expected Hash | Observed Hash | Match
------------------------------------------------
T-991    | h1            | h1            | YES
Click → Replay Detail
diff (if any)
replay engine version
E) Timeline
t0 policy_loaded
t1 tool_call
t2 audit_pass
t3 replay_match
F) Exports
Available:
- Audit ZIP
- Signed PDF
- Raw JSON
(No action except download)
G) Incidents
Incident ID | Opened | Severity | Status
----------------------------------------
INC-03      | t2     | HIGH     | CLOSED
