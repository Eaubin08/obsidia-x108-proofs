# Spec 09 — Tool Adapter MCP → Policy Gate (mapping tools/scopes, P81-P90) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** Tool Adapter MCP → Obsidia Policy Gate (mapping tools/scopes/cost)

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
9) SPEC — Tool Adapter MCP → Obsidia Policy Gate (mapping tools/scopes/cost)
9.0 But
MCP = transport/outillage.
Obsidia = souveraineté/décision.
👉 L’adapter impose que toute action MCP passe par :
mapping (tool → scope)
policy evaluation
ticket check (si action exécutante)
trace event (avant/après)
enforcement (allow/deny)
9.1 Position dans l’architecture
Chemin canon :
Agent/OS4 -> MCP Client -> Tool Adapter -> Policy Gate -> Tool Execution
Le Tool Adapter n’exécute rien sans Policy Gate.
9.2 Objet d’entrée (MCP Call Envelope)
{
  "mcp": {
    "server": "maps_mcp",
    "tool": "maps.geocode",
    "args": { "q": "Paris" }
  },
  "context": {
    "session_id": "uuid",
    "request_id": "uuid",
    "actor_id": "agent_exec_17",
    "scope": "PUBLIC_SANDBOX"
  }
}
9.3 Mapping Tool → Scope + Cost Class
Table canon tool_map.json
{
  "maps.geocode": {
    "scope": "READ_ONLY",
    "cost_class": "LOW",
    "write": false
  },
  "filesystem.write": {
    "scope": "WRITE",
    "cost_class": "LOW",
    "write": true
  },
  "payments.send": {
    "scope": "IRREVERSIBLE",
    "cost_class": "HIGH",
    "write": true,
    "ticket_required": true
  }
}
9.4 Cost model (canon)
Le gate a besoin d’un coût “prévisible”.
cost_class → cost units
LOW = 0.1
MED = 1
HIGH = 5
EXTREME = 20
coût dynamique optionnel :
estimated_tokens
estimated_latency_ms
data_volume_kb
Formule canon :
cost = base(cost_class) + 0.001*tokens + 0.0001*latency_ms + 0.0005*kb
9.5 Policy evaluation (règles)
Entrées :
policy sandbox
tool_map entry
remaining budgets
Checks :
no_write && tool.write => DENY + violation SANDBOX_WRITE_ATTEMPT
tool not in allowed_tools => DENY + TOOL_NOT_ALLOWED
scope not in allowed_scopes => DENY + SCOPE_NOT_ALLOWED
cost + spent_cost > max_cost => DENY + COST_LIMIT_EXCEEDED
calls + 1 > max_calls => DENY + MAX_CALLS_EXCEEDED
si ticket_required => ticket valid + constraints match
9.6 Trace events (avant/après)
Chaque call produit 2 events :
TOOL_CALL_INTENT
TOOL_CALL_RESULT
INTENT (avant execution)
tool
args_hash (pas les args en clair si sensible)
cost_estimate
policy_id
decision (ALLOW/DENY)
RESULT (après execution, si allow)
status ok/fail
result_hash
cost_spent
latency_ms
9.7 Enforcement (deny = pas d’appel MCP)
Si DENY :
aucun call vers MCP server
event enregistré
violation enregistrée (selon code)
9.8 Sortie adapter
{
  "decision": "ALLOW | DENY",
  "reason": "TOOL_NOT_ALLOWED",
  "cost_estimate": 1.2,
  "remaining": {
    "max_cost": 5,
    "spent_cost": 3.9,
    "max_calls": 20,
    "calls": 12
  }
}
Si tu veux, prochaine brique logique (et ça verrouille tout) :
spec “Tool registry canonical” (liste tools autorisés par couche + mapping scopes)
spec “Policy compile” (policy.json → table runtime ultra rapide)
spec “MCP server attestation” (option : vérifier que le serveur MCP est celui attendu via hash/cert)
Parfait. Voici les 3 SPEC canoniques, prêtes à implémenter sans ambiguïté.
