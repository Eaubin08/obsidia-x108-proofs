# LLM_ADVISORY_ONLY_BOUNDARY
Status: SOURCE_ORGANIZED
Authority: KX108_ONLY
Source Paths:
- periphery/brody/brody_runtime_readonly.py\n- periphery/context/context_packet_builder_v2.py
Source Status: SOURCE_ORGANIZED
Scope: LLM = advisory only — boundary spec.
Allowed:
- LLM produit contexte / réponse / suggestion\n- LLM ne décide jamais
Forbidden:
- LLM = autorité décisionnelle\n- LLM émet ALLOW/HOLD/BLOCK
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
