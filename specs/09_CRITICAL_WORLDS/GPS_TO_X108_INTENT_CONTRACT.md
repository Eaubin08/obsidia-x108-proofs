# GPS_TO_X108_INTENT_CONTRACT
Status: RUNTIME_CODE
Authority: KX108_ONLY
Source Paths:
- periphery/adapters/gps_adapter.py\n- sigma/domains/gps_defense_aviation_agents.py
Source Status: RUNTIME_CODE
Scope: Contrat GPS → X108 via intent.
Allowed:
- GPS produit intent trajectory_integrity_review\n- Scores: drift/conflict/time_skew/brownout
Forbidden:
- GPS produit DecisionTicket directement\n- GPS émet action sans X108
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
