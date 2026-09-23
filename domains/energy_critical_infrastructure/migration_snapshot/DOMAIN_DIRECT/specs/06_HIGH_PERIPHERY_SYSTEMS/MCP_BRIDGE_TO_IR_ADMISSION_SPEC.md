# MCP_BRIDGE_TO_IR_ADMISSION_SPEC

Status: RUNTIME_CODE
Authority: KX108_ONLY

Source Paths:
- periphery/mcp_bridge.py

Source Status: RUNTIME_CODE

Scope: MCP Bridge → IR — admission readonly.

Allowed:
- non_decision=True\n- policy_scope=READONLY_CONTEXT

Forbidden:
- MCP Bridge produit verdict\n- MCP Bridge write memory

Inputs: Domain sources
Outputs: Spec contractuelle
Metrics: N/A
Invariants: KX108_ONLY pour toute décision
X108 Boundary: KX108_ONLY
Tests Required: À définir en Plan 3
Proof Expected: Python test
Runtime Status: RUNTIME_CODE
Claim-Scope Notes: Voir 00_SCOPE_DISCIPLINE/ pour limites publiques
Open Questions: À préciser en Plan 3
