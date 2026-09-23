# CONTEXT_PACKET_READONLY_CONTRACT
Status: RUNTIME_CODE
Authority: KX108_ONLY
Source Paths:
- periphery/context/context_packet_builder_v2.py
Source Status: RUNTIME_CODE
Scope: ContextPacket = readonly contract.
Allowed:
- can_decide=False, allowed_to_act=False\n- kernel_mutation=False, memory_write=False
Forbidden:
- ContextPacket avec can_decide=True\n- ContextPacket avec memory_write=True
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
