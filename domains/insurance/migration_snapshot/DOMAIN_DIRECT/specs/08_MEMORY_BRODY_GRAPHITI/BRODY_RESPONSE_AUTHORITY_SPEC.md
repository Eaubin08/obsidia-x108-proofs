# BRODY_RESPONSE_AUTHORITY_SPEC

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- `periphery/brody/brody_runtime_readonly.py`
- `periphery/brody/brody_response_contract.py`
- `docs/freeze/BRODY_RIGHTS_AUTHORITY_MATRIX_REPORT.md`

Source Status: RUNTIME_CODE + SOURCE_CANON

Scope: Définir l'autorité (limitée) de Brody et ses gardes de non-souveraineté.

Allowed:
- "Brody produit des réponses readonly et contextuelles"
- "Brody peut contextualiser mais pas décider"
- "Brody est advisory_only + non-souverain"

Forbidden:
- "Brody décide"
- "Brody émet ALLOW/HOLD/BLOCK"
- "Brody écrit mémoire sans gate humain"
- "Brody = autorité décisionnelle"

Inputs: Queries + context packets
Outputs: Réponses readonly + signal contextuel

Metrics: N/A

Invariants:
- `memory_write=False` dans BrodyLanguageRoute
- Brody ↛ ACT
- Brody non souverain ≠ Brody inutile — signal contextuel précieux

X108 Boundary: KX108_ONLY — Brody fournit contexte

Tests Required:
- `tests/api/test_brody_chat_readonly.py` (existant)
- `test_brody_no_decision_authority`

Proof Expected: Python test (existants dans tests/api/)

Runtime Status: RUNTIME_CODE + READONLY

Claim-Scope Notes:
"Brody non souverain ≠ Brody inutile" — signal contextuel de haute valeur.

Open Questions:
- Quand Brody pourra-t-il écrire mémoire (avec gate) ?
