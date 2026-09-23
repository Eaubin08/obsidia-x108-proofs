# COGNITIVE_BOUNDARY_ENFORCEMENT

Boundary: COGNITIVE_REINTEGRATION_ADVISORY_ONLY  
Authority: KX108_ONLY  

## Required fields

All future Cognitive-derived packets must include:

- source_status
- claim_scope
- advisory_only=true
- readonly=true
- emits_act=false
- emits_verdict=false
- decision_authority=KX108_ONLY
- runtime_allowed_now=false

## Enforcement rules

1. Cognitive output attempting ACT → fail_closed.
2. Cognitive output attempting ALLOW/HOLD/BLOCK → fail_closed.
3. Cognitive output attempting memory write → fail_closed.
4. Cognitive output claiming consciousness proof → fail_closed.
5. Cognitive output claiming autonomous authority → fail_closed.
6. Cognitive output attempting X108 override → fail_closed.
7. Cognitive output importing .py runtime → fail_closed.
8. Cognitive output using source pack as active module → fail_closed.