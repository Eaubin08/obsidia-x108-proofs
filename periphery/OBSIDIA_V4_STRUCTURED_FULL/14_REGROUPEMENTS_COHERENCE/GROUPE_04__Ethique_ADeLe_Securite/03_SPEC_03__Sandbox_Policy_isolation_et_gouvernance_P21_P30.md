# Spec 03 — Sandbox Policy (isolation et gouvernance, P21-P30)

**Statut V4 :** VALIDÉ
**Titre source détaillé :** Sandbox Policy (Isolation & Gouvernance)

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
3) SPEC — Sandbox Policy (Isolation & Gouvernance)
3.0 Définition
Une sandbox Obsidia est un environnement d’exécution contraint, gouverné par policy explicite, jamais implicite.
3.1 Objectifs
Tester sans impacter le réel
Garantir absence d’effet de bord
Permettre audit complet
Rendre toute violation détectable
3.2 Schéma SandboxPolicy
{
  "policy_id": "uuid",
  "sandbox_mode": true,
  "no_write": true,
  "allowed_tools": ["read_api", "compute", "simulate"],
  "forbidden_tools": ["filesystem", "network_write", "db_write"],
  "max_cost": 5,
  "max_duration_sec": 60,
  "max_calls": 10,
  "memory_limit_mb": 512,
  "external_network": false,
  "export_allowed": false,
  "trace_level": "FULL"
}
3.3 Contraintes standard (canon)
3.4 Violations sandbox (codes)
Chaque violation :
génère un VIOLATION_EVENT
déclenche audit OS3 possible
peut invalider le ticket
3.5 Interaction Sandbox ↔ Ticket
La sandbox lit les constraints du ticket
Elle refuse toute action non listée
Elle trace chaque tentative, même refusée
3.6 Garantie système
Une sandbox Obsidia ne peut pas faire plus que ce qui est explicitement autorisé, et ne peut pas faire moins sans laisser de trace.
🔒 Résumé verrouillage
Trace = preuve
Ticket = autorisation unique
Sandbox policy = périmètre dur
Si tu veux la suite logique :
spec du schéma de violation
spec du replay OS3 (matching attendu / observé)
spec cryptographique (keys, rotation, trust chain)
Parfait. Voilà les 3 SPEC en mode contrat (implémentable, auditable, sans flou) :
