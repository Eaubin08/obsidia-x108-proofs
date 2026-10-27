# Spec 04 — Violation Schema (schéma violation, P31-P40) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** Schéma de violation (Violation Schema)

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
4) SPEC — Schéma de violation (Violation Schema)
4.0 Rôle
Une violation = un événement canonique, non discutable, qui signale :
tentative interdite
incohérence de chaîne
dépassement de limites
ticket invalide / réutilisé
divergence de replay OS3
👉 Toute violation DOIT produire :
un VIOLATION_EVENT (trace standard)
un VIOLATION_RECORD (objet enrichi)
optionnel : une ESCALATION (signal système)
4.1 Niveaux de gravité
4.2 Codes canon de violation
Tickets
TICKET_EXPIRED
TICKET_REUSED
TICKET_INVALID_SIGNATURE
TICKET_SCOPE_MISMATCH
TICKET_CONSTRAINTS_BROKEN
Sandbox / outils
SANDBOX_WRITE_ATTEMPT
TOOL_NOT_ALLOWED
NETWORK_WRITE_BLOCKED
EXPORT_FORBIDDEN
COST_LIMIT_EXCEEDED
TIMEOUT_EXCEEDED
MAX_CALLS_EXCEEDED
Chaîne / traces
TRACE_CHAIN_BREAK
HASH_MISMATCH
MISSING_PARENT_EVENT
NON_MONOTONIC_TIME
OS3 Replay
REPLAY_DIVERGENCE_EXPECTED_OBSERVED
REPLAY_MISSING_EVENT
REPLAY_EXTRA_EVENT
REPLAY_POLICY_MISMATCH
4.3 Schéma VIOLATION_RECORD (JSON)
{
  "violation_id": "uuid-v7",
  "violation_code": "TOOL_NOT_ALLOWED",
  "severity": "S2",
  "timestamp": "2026-03-21T14:33:01.123Z",
  "context": {
    "layer": "SANDBOX",
    "scope": "PUBLIC_SANDBOX",
    "session_id": "uuid",
    "request_id": "uuid",
    "ticket_id": "uuid | null",
    "policy_id": "uuid | null",
    "actor": { "type": "AGENT", "id": "agent_exec_17" }
  },
  "expected": {
    "allowed_tools": ["read_api", "compute", "simulate"],
    "no_write": true,
    "max_cost": 5
  },
  "observed": {
    "attempted_tool": "filesystem.write",
    "attempted_action": "WRITE_FILE",
    "cost_estimate": 0.2
  },
  "evidence": {
    "event_id": "uuid",
    "event_hash": "sha256",
    "parent_event_hash": "sha256",
    "payload_hash": "sha256",
    "log_ref": "uri | null"
  },
  "decision": {
    "result": "DENY",
    "reaction": "BLOCK | FREEZE | ESCALATE",
    "audit_required": true
  },
  "signature": "ed25519 | null"
}
4.4 Réactions système (policy-driven)
