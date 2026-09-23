# ATLAS_READONLY_BOUNDARY_ENFORCEMENT

Boundary: ATLAS_READONLY_ADVISORY_ONLY
Authority: KX108_ONLY
Runtime active: false

Required fields for future Atlas-derived packets:

- source_status
- claim_scope
- advisory_only=true
- readonly=true
- emits_act=false
- emits_verdict=false
- reality_claim_allowed=false
- memory_write_allowed=false
- graph_write_allowed=false
- runtime_allowed_now=false
- decision_authority=KX108_ONLY

Enforcement:

1. Atlas output attempting ACT → fail_closed.
2. Atlas output attempting ALLOW/HOLD/BLOCK → fail_closed.
3. Atlas output claiming real-world truth → fail_closed.
4. Atlas output attempting memory write → fail_closed.
5. Atlas output attempting graph write → fail_closed.
6. Atlas output importing .py runtime → fail_closed.
7. Atlas output treating scenario as reality → fail_closed.
8. Atlas output bypassing X108 → fail_closed.