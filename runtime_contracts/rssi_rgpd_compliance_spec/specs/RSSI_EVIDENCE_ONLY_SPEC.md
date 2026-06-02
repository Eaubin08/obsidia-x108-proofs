# RSSI_EVIDENCE_ONLY_SPEC

Boundary: RSSI_EVIDENCE_ONLY
Authority: KX108_ONLY
Runtime active: false

RSSI materials can be used as evidence references, checklist context, risk-control advisory labels, and future OS3 evidence inputs.

RSSI materials cannot:

- certify security
- block automatically
- authorize runtime decisions
- produce ALLOW/HOLD/BLOCK
- produce ACT
- replace X108
- replace human security review

Required claim-scope:

- evidence_only=true
- advisory_only=true
- certification_claim_allowed=false
- runtime_allowed_now=false
- decision_authority=KX108_ONLY