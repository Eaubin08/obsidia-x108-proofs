# Spec 12 — MCP Server Attestation (intégrité serveur, P111-P113) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** MCP Server Attestation

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
12) SPEC — MCP Server Attestation
(vérifier que le serveur MCP est bien celui attendu)
12.0 Objectif
Empêcher :
serveurs MCP spoofés,
redirections silencieuses,
MITM sur tools critiques.
👉 Le Tool Adapter refuse tout MCP non attesté.
12.1 Fichier canon
mcp_servers.json
{
  "version": "1.0",
  "servers": {
    "maps_mcp": {
      "endpoint": "https://mcp.maps.example",
      "pubkey": "ed25519:ABCD...",
      "cert_sha256": "F1A9...",
      "allowed_tools": ["maps.geocode"],
      "valid_from": "2026-01-01",
      "valid_until": "2026-12-31"
    }
  }
}
12.2 Méthodes d’attestation (au moins une requise)
A) Signature de challenge
Adapter envoie nonce
MCP server signe nonce
Vérification via pubkey
B) Cert hash
TLS cert SHA256 == cert_sha256
C) Fingerprint runtime
hash(binaire MCP ou version API) si exposé
12.3 Check runtime (ordre strict)
server_id connu ?
now ∈ [valid_from, valid_until] ?
Attestation OK ?
Tool ∈ allowed_tools ?
→ sinon DENY + violation MCP_ATTESTATION_FAILED
12.4 Trace event obligatoire
Chaque attestation produit :
MCP_SERVER_ATTESTED ou MCP_SERVER_REJECTED
hash serveur
méthode utilisée (A/B/C)
12.5 Hash & trust chain
mcp_servers.json → hashé
inclus dans roots.json
clé de signature = ROOT (changement rare)
12.6 Fail-safe
Attestation impossible → pas de fallback
Aucun appel MCP sans attestation valide
🔒 Résumé verrouillage
Tool Registry = ce qui peut exister
Policy Compile = ce qui est autorisé maintenant
MCP Attestation = qui est digne de confiance
Si tu veux, prochaine étape logique :
spec “Violation taxonomy & severity matrix”
spec “Policy hot-reload (safe)”
spec “End-to-end example” (1 appel MCP tracé + audité + rejoué de A à Z)
Parfait. On continue au même niveau de rigueur, sans blabla, canonique, directement implémentable.
