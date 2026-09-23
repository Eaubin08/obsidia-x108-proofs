# BUV_MASTER_SPEC

Status: SOURCE_FOUND_UNDER_DIFFERENT_NAME
Authority: KX108_ONLY

Source Paths:
- `docs/gencoin/sandbox_pre_freeze/BALANCE_CANON.md`
- `periphery/gencoin_sandbox/balance_operator.py`
- `docs/gencoin/sandbox_pre_freeze/LIMITS_AND_STATUS.md`

Source Status: RUNTIME_CODE (sandbox) + DOC_ONLY

Scope:
Spec master de la Balance Obsidienne (BUV = terme conceptuel de l'audio).

Allowed:
- "BUV correspond à BALANCE_CANON.md + balance_operator.py"
- "La balance calcule un score multi-facteur — pas une décision ALLOW/HOLD/BLOCK"
- "Balance = signal de pondération pour X108"

Forbidden:
- "buv_master_spec.md existe dans le repo" (ABSENT_UNDER_THIS_NAME — cette spec remplace)
- "La Balance décide"
- "BUV = token"
- "Balance → ALLOW automatique"

Inputs:
- Scores périphériques (utility, coherence, stability, cost, risk)

Outputs:
- balance_score ∈ [0,1] — signal pour X108

Metrics:
- utility : valeur utilitaire de l'action
- coherence : cohérence avec le système
- stability : impact sur la stabilité
- cost : coût thermodynamique
- risk : niveau de risque

Invariants:
- Balance pèse — BUV filtre — X108 décide
- Balance ne produit pas ALLOW/HOLD/BLOCK
- Balance ne produit pas vérité finale

X108 Boundary:
- Balance = entrée pour X108 — KX108 décide

Tests Required:
- test_balance_no_verdict
- test_balance_score_range

Proof Expected: Python test

Runtime Status: RUNTIME_CODE (sandbox)

Claim-Scope Notes:
"Balance ≠ décision finale" — résultat d'une évaluation multi-facteur.

Open Questions:
- La balance sandbox sera-t-elle connectée au runtime principal en Plan 3 ?
