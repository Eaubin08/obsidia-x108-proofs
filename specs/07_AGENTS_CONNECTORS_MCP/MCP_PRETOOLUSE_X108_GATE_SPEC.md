# MCP_PRETOOLUSE_X108_GATE_SPEC
Status: SOURCE_ORGANIZED
Authority: KX108_ONLY
Source Paths:
- periphery/mcp/mcp_permission_matrix.py\n- periphery/mcp_bridge.py
Source Status: SOURCE_ORGANIZED
Scope: Gate X108 avant tout tool-call MCP.
Allowed:
- Tool-call critique = X108 ALLOW requis\n- mcp_permission_matrix vérifie les permissions
Forbidden:
- Tool-call sans gate X108
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
