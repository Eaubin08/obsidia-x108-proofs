# CONNECTOR_TO_INTENT_ENVELOPE_SPEC
Status: RUNTIME_CODE
Authority: KX108_ONLY
Source Paths:
- connectors/aviation_robo.py\n- periphery/adapters/gps_adapter.py
Source Status: RUNTIME_CODE
Scope: Connector → intent envelope spec.
Allowed:
- Connector produit intent = proposed_verdict\n- Intent ≠ DecisionTicket
Forbidden:
- Connector émet action directe
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
