# Spec 02 — Decision Ticket Obsidia (schéma ticket signé, P11-P20)

**Statut V4 :** VALIDÉ
**Titre source détaillé :** Ticket signé (Decision Ticket Obsidia)

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
2) SPEC — Ticket signé (Decision Ticket Obsidia)
2.0 Rôle
Le Decision Ticket est le seul objet autorisant une exécution.
Sans ticket valide :
❌ aucun agent
❌ aucune action
❌ aucune sandbox
2.1 Propriétés fondamentales
2.2 Schéma du ticket signé
{
  "ticket_id": "uuid-v7",
  "request_id": "uuid",
  "session_id": "uuid",
  "issued_at": "timestamp",
  "expires_at": "timestamp",
  "decision": "ALLOW | DENY | HOLD",
  "scope": "PRIVATE | PUBLIC_SANDBOX | INTERNAL",
  "constraints": {
    "sandbox": true,
    "no_write": true,
    "max_cost": 5,
    "allowed_tools": ["tool_a", "tool_b"],
    "time_limit_sec": 30
  },
  "reason_code": "string canonique",
  "core_hash": "sha256",
  "signature": "ed25519"
}
2.3 Règles d’exécution
Un ticket est INVALIDE si :
expiré
scope incohérent
signature invalide
constraints violées
request_id déjà consommé
2.4 Cycle de vie
ISSUED → CONSUMED → ARCHIVED
Un ticket ne peut être consommé qu’une seule fois
Toute tentative de réutilisation = VIOLATION
2.5 Vérification minimale avant exécution
if not verify_signature(ticket):
  reject
if now > ticket.expires_at:
  reject
if ticket.consumed:
  reject
if not constraints_respected:
  reject
