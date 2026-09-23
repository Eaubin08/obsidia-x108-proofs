# KX108_ONLY_AUTHORITY_SPEC

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- `periphery/action_lifecycle.py` (X108_EVALUATED step)
- `periphery/os3_ticket.py` (x108_gate field)
- `periphery/export_for_x108.py`
- `periphery/x108_ingress/readonly_context_ingress.py`
- `docs/PROOF_SCOPE.md`

Source Status: RUNTIME_CODE + SOURCE_CANON

Scope:
Définir et verrouiller l'autorité exclusive de KX108 sur toutes les décisions du système Obsidia.

Allowed:
- "Seul X-108 émet ALLOW / HOLD / BLOCK"
- "X108_EVALUATED est l'étape centrale du cycle d'action"
- "Tous les composants périphériques fournissent du contexte — KX108 décide"

Forbidden:
- Tout agent, LLM, Brody, Graphiti, Tree34, NPL, Balance, Gencoin, GPS ne décide
- Aucun bypass de X108 pour des actions irréversibles
- Aucun composant n'émet ALLOW/HOLD/BLOCK à la place de KX108

Inputs:
- Context packets de tous les modules périphériques
- OS3ProofTicket (après évaluation)

Outputs:
- x108_gate : ALLOW | HOLD | BLOCK
- reason_code, severity

Metrics: N/A

Invariants:
- BLOCK > HOLD > ALLOW (priorité absolue)
- Toute action irréversible passe par X108
- Toute écriture mémoire critique passe par gate
- Tout tool-call critique passe par gate
- `can_emit_act=False` pour TOUS les composants périphériques

X108 Boundary:
- X108 EST la boundary — il est l'autorité finale

Tests Required:
- test_no_bypass_x108 — aucun composant ne peut contourner X108
- test_block_priority — BLOCK > HOLD > ALLOW

Proof Expected: LEAN_PROVEN pour noyau X108 temporel

Runtime Status: RUNTIME_CODE (kernel)

Claim-Scope Notes:
"KX108_ONLY" = formulation contractuelle — toujours présente dans chaque spec.

Open Questions: Aucune — règle absolue
