# PERIPHERY_TO_KERNEL_PASSAGE_RULES
Status: SOURCE_ORGANIZED
Authority: KX108_ONLY
Source Paths:
- periphery/x108_ingress/readonly_context_ingress.py\n- periphery/export_for_x108.py
Source Status: SOURCE_ORGANIZED
Scope: Règles de passage périphérie → kernel.
Allowed:
- export_for_x108.py = seul chemin vers le kernel\n- readonly_context_ingress = gate d'entrée
Forbidden:
- Passage direct sans gate\n- Bypass readonly_context_ingress
Inputs: Domain sources
Outputs: Spec contractuelle
Metrics: N/A
Invariants: KX108_ONLY pour toute décision
X108 Boundary: KX108_ONLY
Tests Required: À définir en Plan 3
Proof Expected: Python test
Runtime Status: RUNTIME_CODE
Claim-Scope Notes: Voir 00_SCOPE_DISCIPLINE/
Open Questions: À préciser en Plan 3
