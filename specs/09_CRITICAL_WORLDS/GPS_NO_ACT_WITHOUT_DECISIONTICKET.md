# GPS_NO_ACT_WITHOUT_DECISIONTICKET
Status: SOURCE_ORGANIZED
Authority: KX108_ONLY
Source Paths:
- connectors/aviation_robo.py\n- periphery/adapters/gps_adapter.py
Source Status: SOURCE_ORGANIZED
Scope: GPS ne peut pas agir sans DecisionTicket.
Allowed:
- Aucune trajectoire réelle sans DecisionTicket X108
Forbidden:
- GPS émet action physique sans ticket
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
