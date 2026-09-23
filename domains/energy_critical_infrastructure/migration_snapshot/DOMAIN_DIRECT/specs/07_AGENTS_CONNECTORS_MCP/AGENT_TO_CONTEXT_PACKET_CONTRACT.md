# AGENT_TO_CONTEXT_PACKET_CONTRACT
Status: RUNTIME_CODE
Authority: KX108_ONLY
Source Paths:
- periphery/context/context_packet_builder_v2.py\n- periphery/agent_contracts.py
Source Status: RUNTIME_CODE
Scope: Contrat agent → context packet.
Allowed:
- Agent produit un ContextPacket avec can_decide=False
Forbidden:
- Agent bypasse ContextPacket
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
