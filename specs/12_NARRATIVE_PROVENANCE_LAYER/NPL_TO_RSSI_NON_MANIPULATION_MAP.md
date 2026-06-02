# NPL_TO_RSSI_NON_MANIPULATION_MAP
Status: SPEC_CANDIDATE
Authority: KX108_ONLY
Source Paths:
- periphery/bias/bias_gate.py + bias_trace.py — manipulation_risk_signal obligatoire
Scope: Map NPL vers recepteur Obsidia.
Allowed:
- NPL enrichit le recepteur Obsidia avec signaux contextuels
Forbidden:
- NPL ecrit dans le recepteur sans gate
- NPL prend decision via le recepteur
Invariants: Recepteur = readonly par defaut — gate humain pour ecriture
X108 Boundary: KX108_ONLY
Runtime Status: SPEC_CANDIDATE
Claim-Scope Notes: Map = lecture seule — voir NPL_CLAIM_SCOPE_LIMITS.md
