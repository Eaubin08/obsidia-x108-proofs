# Spec 11 — Policy Compile (compilation règles, P101-P110) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** Policy Compile

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
11) SPEC — Policy Compile
(policy.json → table runtime ultra rapide)
11.0 Objectif
Transformer une policy déclarative en structure runtime O(1) :
sans parsing JSON à chaque call,
sans logique conditionnelle lourde,
déterministe.
11.1 Entrée
policy.json
{
  "policy_id": "sandbox_public_v1",
  "no_write": true,
  "allowed_scopes": ["READ_ONLY", "AUDIT"],
  "allowed_tools": ["http.get", "maps.geocode"],
  "max_cost": 5,
  "max_calls": 20,
  "time_budget_ms": 10000
}
11.2 Sortie compilée
policy.compiled.bin (ou .json compact)
{
  "policy_id": "sandbox_public_v1",
  "flags": {
    "NO_WRITE": true
  },
  "scope_mask": 0b0011,
  "tool_bitmap": {
    "http.get": 1,
    "maps.geocode": 1,
    "http.post": 0
  },
  "limits": {
    "max_cost": 5,
    "max_calls": 20,
    "time_budget_ms": 10000
  }
}
11.3 Tables runtime
Chargées au démarrage du moteur :
tool_bitmap[tool_id] → allow/deny
scope_mask & tool.scope_bit → ok/deny
flags.NO_WRITE && tool.write → deny
👉 Aucun JSON.parse dans le chemin critique.
11.4 Processus de compilation
Valider policy vs tool_registry.json
Convertir scopes → bits
Générer bitmap tools
Calculer policy_hash
Signer (ASK)
11.5 Invariants
Même input → même compiled output
Toute policy compilée est hashée + signée
Policy non compilée = invalide en runtime
