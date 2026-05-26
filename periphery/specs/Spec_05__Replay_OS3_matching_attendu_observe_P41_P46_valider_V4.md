# Spec 05 — Replay OS3 (matching attendu/observé, P41-P46) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** Replay OS3 (Matching attendu / observé)

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
5) SPEC — Replay OS3 (Matching attendu / observé)
5.0 Rôle
OS3 ne “réfléchit” pas.
OS3 rejoue.
Il prend :
un pack de traces (observé)
un modèle attendu (contrat)
et produit un rapport de matching + divergences.
5.1 Entrées / sorties
Input A — Trace Pack (observé)
liste ordonnée d’Event Obsidia (hash-chain intacte)
plus Decision Tickets associés (si présents)
plus SandboxPolicy appliquée
Input B — Expected Model (attendu)
Deux formes possibles (au choix) :
Expected Trace Skeleton (séquence attendue)
Expected Constraints (invariants à satisfaire)
Output — OS3 Audit Report
MATCH_SCORE
divergences classées
preuve de rejouabilité
signature OS3
5.2 Schéma EXPECTED_TRACE_SKELETON
{
  "expected_id": "uuid",
  "version": "1.0",
  "request_id": "uuid",
  "expected_sequence": [
    { "event_type": "REQUEST", "layer": "OS4" },
    { "event_type": "DECISION", "layer": "OS0" },
    { "event_type": "EXECUTION", "layer": "SANDBOX" },
    { "event_type": "AUDIT", "layer": "OS3" }
  ],
  "invariants": {
    "no_write": true,
    "allowed_tools": ["read_api", "compute", "simulate"],
    "ticket_required_for_execution": true,
    "hash_chain_intact": true
  }
}
5.3 Matching engine (règles strictes)
Matching minimal (hard constraints)
Si une seule échoue ⇒ FAIL direct :
chaîne de hash intacte
timestamps monotones
execution ⇒ ticket valide obligatoire
policy appliquée = policy attendue
aucune violation S3/S4 ignorée
Matching séquence (soft constraints)
Score calculé sur :
ordre des types d’événements
présence/absence d’événements attendus
“extra events” tolérés si marqués DEBUG (option)
5.4 Schéma OS3_REPLAY_REPORT
{
  "audit_id": "uuid-v7",
  "request_id": "uuid",
  "session_id": "uuid",
  "timestamp": "2026-03-21T14:35:55.000Z",
  "status": "PASS | FAIL",
  "match_score": 0.97,
  "hard_checks": {
    "hash_chain_intact": true,
    "ticket_valid": true,
    "policy_match": true,
    "no_write_respected": true
  },
  "sequence_checks": {
    "missing_events": [],
    "extra_events": ["uuid"],
    "order_violations": []
  },
  "divergences": [
    {
      "code": "REPLAY_EXTRA_EVENT",
      "severity": "S1",
      "expected": "none",
      "observed": "DEBUG_EVENT",
      "event_id": "uuid"
    }
  ],
  "evidence": {
    "trace_root_hash": "sha256",
    "first_event_hash": "sha256",
    "last_event_hash": "sha256"
  },
  "signature": "ed25519"
}
5.5 Divergences : classification
