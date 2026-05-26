# Spec 10 — Tool Registry Canonical (registre outils, P91-P100) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** Tool Registry Canonical

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
10) SPEC — Tool Registry Canonical
(liste des tools autorisés par couche + mapping scopes)
10.0 Objectif
Définir l’inventaire autorisé des outils par couche Obsidia, avec :
scopes,
permissions d’écriture,
ticket requis ou non,
classes de coût.
👉 Source de vérité unique pour le Policy Gate et l’Adapter MCP.
10.1 Fichier canon
tool_registry.json
{
  "version": "1.0",
  "updated_at": "2026-03-21T00:00:00Z",
  "layers": {
    "OS0_OS1": ["crypto.verify", "hash.sha256"],
    "OS3_AUDIT": ["trace.read", "trace.verify", "report.render"],
    "OS4_JARVIS": ["ui.render", "ui.input"],
    "CORTEX_MCP": ["mcp.call"],
    "SANDBOX_PUBLIC": ["http.get", "maps.geocode"],
    "AGENTS_EXEC": ["http.get", "http.post"]
  },
  "tools": {
    "http.get": {
      "scope": "READ_ONLY",
      "write": false,
      "cost_class": "LOW",
      "ticket_required": false
    },
    "http.post": {
      "scope": "WRITE",
      "write": true,
      "cost_class": "MED",
      "ticket_required": true
    },
    "filesystem.write": {
      "scope": "WRITE",
      "write": true,
      "cost_class": "LOW",
      "ticket_required": true
    },
    "payments.send": {
      "scope": "IRREVERSIBLE",
      "write": true,
      "cost_class": "HIGH",
      "ticket_required": true
    },
    "trace.verify": {
      "scope": "AUDIT",
      "write": false,
      "cost_class": "LOW",
      "ticket_required": false
    }
  }
}
10.2 Règles d’évaluation
Tool ∉ layer.tools → DENY
Tool ∉ registry.tools → DENY
no_write = true && write = true → DENY
ticket_required = true sans ticket valide → DENY
Scope tool ∉ policy.allowed_scopes → DENY
👉 Aucune exception runtime.
Toute modification = nouvelle version + hash.
10.3 Hash & signature
tool_registry.json → sha256
référencé dans policy_hash et roots.json
signé par ROOT ou ASK selon scope
