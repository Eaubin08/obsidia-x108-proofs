# Spec 01 — Event Schema Obsidia (format canonique JSON, P1-P10)

**Statut V4 :** VALIDÉ
**Titre source détaillé :** Formats de trace (Event Schema Obsidia)

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
1) SPEC — Formats de trace (Event Schema Obsidia)
1.0 Principe fondamental
Une trace Obsidia n’est pas un log applicatif.
C’est :
une preuve temporelle
une brique de comptabilité totale
un élément de rejouabilité déterministe
une unité audit OS3
👉 Toute action, décision, tentative ou refus DOIT produire une trace.
1.1 Invariants de trace (non négociables)
1.2 Event Obsidia — Schéma canon (JSON)
{
  "event_id": "uuid-v7",
  "event_type": "REQUEST | DECISION | EXECUTION | AUDIT | VIOLATION | REFUSAL",
  "layer": "OS0 | OS1 | OS3 | OS4 | CORTEX | AGENT | SANDBOX",
  "timestamp": "2026-03-21T14:32:08.456Z",
  "actor": {
    "type": "HUMAN | AGENT | SYSTEM",
    "id": "user_id | agent_id | service_id"
  },
  "session_id": "uuid",
  "request_id": "uuid",
  "scope": "PRIVATE | PUBLIC_SANDBOX | INTERNAL",
  "intent": "string (normalisé)",
  "payload_hash": "sha256",
  "payload_ref": "uri | null",
  "decision_ticket_id": "uuid | null",
  "policy_id": "policy_uuid | null",
  "risk_class": "LOW | MEDIUM | HIGH",
  "result": "ALLOW | DENY | HOLD | EXECUTED | FAILED | AUDITED",
  "parent_event_hash": "sha256 | null",
  "event_hash": "sha256",
  "signature": "ed25519 | null"
}
1.3 Chaînage des événements
Chaque événement calcule :
event_hash = HASH(
  event_id +
  timestamp +
  payload_hash +
  parent_event_hash
)
parent_event_hash = hash du dernier événement valide
Toute rupture = VIOLATION
1.4 Typologie des événements
1.5 Stockage minimal requis
Append-only
Lecture séquentielle
Export JSON brut
Aucun overwrite possible
Snapshot périodique signé
