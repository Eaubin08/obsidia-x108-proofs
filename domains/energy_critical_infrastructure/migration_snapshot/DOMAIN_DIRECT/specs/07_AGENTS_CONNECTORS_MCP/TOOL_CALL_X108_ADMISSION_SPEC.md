# TOOL_CALL_X108_ADMISSION_SPEC
Status: SOURCE_ORGANIZED
Authority: KX108_ONLY
Source Paths:
- periphery/mcp/mcp_permission_matrix.py
Source Status: SOURCE_ORGANIZED
Scope: Admission de tool-call via X108.
Allowed:
- Tool-call critique → X108 gate obligatoire
Forbidden:
- Tool-call sans X108 pour action irréversible
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
