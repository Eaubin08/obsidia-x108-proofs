# NPL_TO_GRAPHITI_MAP
Status: SPEC_CANDIDATE
Authority: KX108_ONLY
Source Paths:
- sigma/graphiti_readonly_bridge.py — NO_GRAPHITI_WRITE sans gate
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
