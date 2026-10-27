# Spec 15 — End-to-End Example (P131-P140) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** End-to-End Example

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
15) SPEC — End-to-End Example
(1 appel MCP tracé, audité et rejoué de A à Z)
15.1 Contexte
Couche : SANDBOX_PUBLIC
Policy : sandbox_public_v1
Tool : maps.geocode
MCP server : maps_mcp
15.2 Étape 1 — Demande d’action
{
  "intent": "geocode",
  "tool": "maps.geocode",
  "input": "Charleville-Mézières"
}
15.3 Étape 2 — Policy Gate
Checks effectués :
tool autorisé ✔
no_write = true, tool.write = false ✔
scope READ_ONLY ✔
coût cumulé ≤ max_cost ✔
MCP attesté ✔
→ ALLOW
15.4 Étape 3 — MCP Call
{
  "mcp_server": "maps_mcp",
  "request": {
    "address": "Charleville-Mézières"
  }
}
15.5 Étape 4 — Trace générée
{
  "event_type": "TOOL_CALL",
  "tool": "maps.geocode",
  "policy_hash": "abc123",
  "input_hash": "def456",
  "output_hash": "ghi789",
  "timestamp": "2026-03-21T10:00:00Z",
  "signature": "ed25519:XYZ"
}
15.6 Étape 5 — OS3 Audit
Vérifications :
hash trace OK
signature OK
policy_hash connu
tool ∈ registry
MCP attesté
→ AUDIT_PASS
15.7 Étape 6 — Replay OS3
Input rejoué :
"Charleville-Mézières"
Résultat attendu :
lat: 49.773,
lon: 4.720
Comparaison :
output_hash attendu == output_hash observé ✔
→ REPLAY_MATCH
15.8 Rapport final
{
  "status": "PASS",
  "violations": [],
  "policy_hash": "abc123",
  "trace_root": "merkle_root_xyz",
  "signed_by": "OS3_ROOT"
}
15.9 Ce que ça prouve (pour investisseurs / institutions)
Aucun appel non gouverné
Aucun effet de bord
Auditabilité totale
Rejouabilité parfaite
MCP utilisé sans perte de souveraineté
🔒 Verrou final
À ce stade, Obsidia dispose de :
un langage de violation officiel
un hot-reload sûr
une chaîne complète action → audit → replay
👉 C’est un OS cognitif gouvernable, pas un agent bricolé.
Si tu veux, prochaine brique logique :
spec “Governance dashboard (policy / violations / replay)”
spec “Legal-grade audit export (ZIP + signatures)”
spec “Incident response protocol”
Parfait. On continue au même niveau canonique, sans extrapoler, sans marketing, directement spécifiable / implémentable / auditable.
