# FAIL_CLOSED_PRIORITY_SPEC

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- `periphery/action_lifecycle.py`
- `periphery/os3_ticket.py`
- `periphery/blockchain/signature_boundary.py`

Source Status: RUNTIME_CODE

Scope:
Verrouiller la règle de priorité BLOCK > HOLD > ALLOW et le comportement fail-closed.

Allowed:
- "En cas d'ambiguïté ou d'erreur, X108 retourne HOLD ou BLOCK — jamais ALLOW par défaut"
- "BLOCK est prioritaire sur tout autre verdict"

Forbidden:
- "En cas d'erreur, le système continue normalement"
- "ALLOW par défaut si incertain"

Inputs: Context packets + OS3ProofTicket

Outputs: gate = BLOCK si incertitude critique

Metrics: N/A

Invariants:
- BLOCK = arrêt immédiat
- HOLD = attente de résolution humaine
- ALLOW = conditions toutes vérifiées
- Fail-closed = BLOCK si critères incomplets

X108 Boundary: KX108_ONLY

Tests Required:
- test_fail_closed_on_unknown_domain
- test_block_on_incomplete_ticket

Proof Expected: Python test

Runtime Status: RUNTIME_CODE

Claim-Scope Notes: Le comportement fail-closed est une garantie de sécurité — pas une fonctionnalité optionnelle.

Open Questions: Y a-t-il des cas où HOLD déclenche une action automatique ?
