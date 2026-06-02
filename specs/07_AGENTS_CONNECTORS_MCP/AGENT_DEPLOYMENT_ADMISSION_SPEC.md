# AGENT_DEPLOYMENT_ADMISSION_SPEC
Status: DOC_ONLY
Authority: KX108_ONLY
Source Paths:
- periphery/OBSIDIA_MMONDE_.../10_AGENTS_52/agents_52.registry.json\n- docs/status/PERIPHERY_PUBLIC_INDEX.md
Source Status: DOC_ONLY
Scope: Conditions d'admission d'un agent en déploiement.
Allowed:
- Agent doit avoir spec contractuelle\n- Agent doit avoir test de non-souveraineté
Forbidden:
- Déployer agent sans spec\n- Déployer agent sans test non-décision
Inputs: Domain sources
Outputs: Spec contractuelle
Metrics: N/A
Invariants: KX108_ONLY pour toute décision
X108 Boundary: KX108_ONLY
Tests Required: À définir en Plan 3
Proof Expected: Python test
Runtime Status: DOC_ONLY
Claim-Scope Notes: Voir 00_SCOPE_DISCIPLINE/
Open Questions: À préciser en Plan 3
