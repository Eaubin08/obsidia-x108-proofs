# ANTI_FAKE_WORK_REPLAY_ATTACK_SPEC
Status: SOURCE_ORGANIZED
Authority: KX108_ONLY
Source Paths:
- periphery/os3_ticket.py (merkle_root, replay_status)\n- periphery/gencoin.py
Source Status: SOURCE_ORGANIZED
Scope: Protection contre faux travail et attaque replay.
Allowed:
- merkle_root = protection intégrité\n- replay_status = NOT_RUN (futur Plan 3)
Forbidden:
- Replay non vérifiable\n- Faux travail non détectable
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
