# Spec 13 — Violation Taxonomy & Severity Matrix (P114-P120) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** Violation Taxonomy & Severity Matrix

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
13) SPEC — Violation Taxonomy & Severity Matrix
(classification officielle des violations Obsidia)
13.0 Objectif
Créer une taxonomie fermée, exhaustive, permettant :
qualification immédiate d’un incident,
décision automatique (halt / degrade / log),
audit OS3 déterministe,
lecture politique / juridique claire.
👉 Aucune violation hors taxonomy n’est autorisée.
13.1 Structure canonique
violation_taxonomy.json
{
  "version": "1.0",
  "levels": {
    "INFO":    { "severity": 1, "action": "LOG" },
    "WARN":    { "severity": 2, "action": "LOG" },
    "BLOCK":   { "severity": 3, "action": "DENY" },
    "CRITICAL":{ "severity": 4, "action": "HALT" }
  },
  "violations": {
    "TOOL_NOT_ALLOWED": {
      "level": "BLOCK",
      "description": "Tool not permitted by policy or registry"
    },
    "WRITE_FORBIDDEN": {
      "level": "BLOCK",
      "description": "Write operation attempted under no_write policy"
    },
    "POLICY_LIMIT_EXCEEDED": {
      "level": "BLOCK",
      "description": "Cost / call / time budget exceeded"
    },
    "MCP_ATTESTATION_FAILED": {
      "level": "CRITICAL",
      "description": "Untrusted MCP server"
    },
    "SIGNATURE_INVALID": {
      "level": "CRITICAL",
      "description": "Invalid cryptographic signature"
    },
    "TRACE_HASH_MISMATCH": {
      "level": "CRITICAL",
      "description": "Trace integrity violation"
    },
    "REPLAY_DIVERGENCE": {
      "level": "CRITICAL",
      "description": "Replay does not match expected trace"
    }
  }
}
13.2 Matrice de décision (runtime)
👉 CRITICAL = arrêt dur + rapport automatique OS3
13.3 Invariants
Toute violation est typée
Toute violation est signée
Toute violation est rejouable
Aucune “erreur libre”
