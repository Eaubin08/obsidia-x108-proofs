# Spec 07 — Replay Pack Format (bundle standard, P64-P70) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** Replay Pack Format (Bundle standard)

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
7) SPEC — Replay Pack Format (Bundle standard)
7.0 But
Un Replay Pack = un artefact portable et offline, suffisant pour :
rejouer (OS3)
auditer (preuve)
vérifier (hash-chain + tickets + policy)
signer (root hashes + manifest)
👉 Un Replay Pack doit être auto-suffisant : aucune dépendance réseau.
7.1 Structure de dossier (canon)
replay_pack/
  manifest.json
  roots.json
  policy.json
  tickets/
    ticket_0001.json
    ticket_0002.json
  traces/
    events_0001.jsonl
    events_0002.jsonl
  artifacts/
    inputs/...
    outputs/...
  keys/
    certs.json
    revocations.json
  signatures/
    manifest.sig
    roots.sig
Contrainte
events_*.jsonl = JSON Lines (1 event par ligne, ordre strict)
Tout fichier listé dans manifest.json doit avoir un hash.
7.2 manifest.json (index maître)
{
  "pack_id": "uuid-v7",
  "version": "1.0",
  "created_at": "2026-03-21T14:40:00Z",
  "context": {
    "project": "Obsidia",
    "layer_scope": "PUBLIC_SANDBOX",
    "session_id": "uuid",
    "request_id": "uuid"
  },
  "files": [
    { "path": "roots.json", "sha256": "..." },
    { "path": "policy.json", "sha256": "..." },
    { "path": "tickets/ticket_0001.json", "sha256": "..." },
    { "path": "traces/events_0001.jsonl", "sha256": "..." },
    { "path": "keys/certs.json", "sha256": "..." },
    { "path": "keys/revocations.json", "sha256": "..." }
  ],
  "claims": {
    "hash_chain_intact": true,
    "ticket_required_for_execution": true,
    "no_write": true
  },
  "signing": {
    "manifest_signed_by": "ASK | TSK | ROOT",
    "signature_file": "signatures/manifest.sig"
  }
}
Règles
manifest.json est signé (manifest.sig)
si un fichier est ajouté/supprimé → nouveau manifest + nouvelle signature.
7.3 roots.json (hash racines)
{
  "pack_id": "uuid-v7",
  "trace_root_hash": "sha256(all events hashes in order)",
  "first_event_hash": "sha256",
  "last_event_hash": "sha256",
  "tickets_root_hash": "sha256(all tickets hashes sorted)",
  "policy_hash": "sha256(policy.json)",
  "certs_hash": "sha256(keys/certs.json)",
  "revocations_hash": "sha256(keys/revocations.json)",
  "created_at": "timestamp"
}
Règles
roots.json est signé (roots.sig) par ASK (OS3) ou ROOT (si scellage fort).
trace_root_hash = racine déterministe (voir 7.6).
7.4 policy.json (Sandbox Policy utilisée)
Contient le document canon de policy (cf spec sandbox policy) :
no_write
allowed_tools
max_cost
max_calls
time_budget_ms
allowed_scopes
export_rules
7.5 Tickets (tickets/ticket_*.json)
Contient les tickets signés utilisés dans la session.
Règle : chaque ticket référencé dans un event EXECUTION doit être présent.
7.6 Traces (events_*.jsonl)
Chaque ligne = EVENT canon (votre event schema).
Règles de base
Ordre strict par timestamp puis seq
parent_hash obligatoire (sauf premier)
event_hash recalculable = sha256(canonical_json(event_without_sig)+parent_hash)
7.7 Certs / Revocations
keys/certs.json : certificats de clés valides
keys/revocations.json : clés révoquées
Règle : OS3 doit rejeter toute signature provenant d’une clé révoquée au timestamp concerné.
7.8 Signatures
signatures/manifest.sig : signature ed25519 du sha256(manifest.json canonical)
signatures/roots.sig : signature ed25519 du sha256(roots.json canonical)
