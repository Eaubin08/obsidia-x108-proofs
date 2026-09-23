# HIDDEN_TRANSCRIPT_PACKET_SPEC

Status: SPEC_CANDIDATE
Authority: KX108_ONLY

Source Paths:
- USER_PROVIDED_SOURCE_ONLY
- Recepteurs Obsidia (voir NPL_SOURCE_TO_SPEC_MAPPING.md)

Source Status: SPEC_CANDIDATE

Scope: Spec NPL — HIDDEN_TRANSCRIPT_PACKET_SPEC

Allowed:
- Signal probabiliste avec provenance_uncertainty
- CONTEXT_ONLY — NON_SOVEREIGN

Forbidden:
- NO_ACT — NO_VERDICT_FINAL — NO_MEMORY_WRITE sans gate
- Claim de certitude ou de diagnostic

Inputs: Signaux contextuels + sources utilisateur
Outputs: Packet NPL avec score in [0,1] + uncertainty
Metrics: provenance_confidence, provenance_uncertainty, manipulation_risk_signal
Invariants: PERIPHERAL_READONLY; KX108_ONLY
X108 Boundary: NPL produit contexte — KX108 decide
Tests Required: test_npl_no_decision; test_packet_schema
Proof Expected: Python test
Runtime Status: SPEC_CANDIDATE
Claim-Scope Notes: Voir NPL_CLAIM_SCOPE_LIMITS.md
Open Questions: Preciser en Plan 3
