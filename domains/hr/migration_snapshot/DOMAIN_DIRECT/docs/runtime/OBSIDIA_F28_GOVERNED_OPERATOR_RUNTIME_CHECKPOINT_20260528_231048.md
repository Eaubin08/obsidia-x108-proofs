# OBSIDIA F28 — GOVERNED OPERATOR RUNTIME CHECKPOINT

Mode: GOVERNED_OPERATOR_RUNTIME_CHECKPOINT  
Patch runtime: YES  
Commit candidate: YES  
Tag candidate: YES  

## Covered phases

- F28.0 — Next Review Audit
- F28.1 — Governed Operator Runtime Audit
- F28.2 — Governed Operator Runtime Route
- F28.3 — Runtime Smoke

## Result

``text
GOVERNED_OPERATOR_RUNTIME_V1 created
/api/periphery/operator/governed-runtime route added
Runtime context now carries tree_signal_packet_snapshot
Operator runtime aggregates:
- domain_sigma_envelope
- tree_signal_packet
- operator_view_packet
- runtime_context
Validation
py_compile = PASS
pytest = PASS
git diff --check = PASS
runtime smoke = PASS
Runtime smoke
status=200
version=GOVERNED_OPERATOR_RUNTIME_V1
mode=READONLY_GOVERNED_OPERATOR_RUNTIME
operator_domain_sigma=OK
operator_tree_signal=OK
runtime_domain_sigma_ready=True
runtime_tree_signal_ready=True
decision_authority=KX108_ONLY
readonly=True
can_decide=False
can_emit_act=False
emits_act=False
F28_3_GOVERNED_OPERATOR_RUNTIME_SMOKE_OK
Boundary
DECISION_AUTHORITY=KX108_ONLY
readonly=true
advisory_only=true
context_signal_only=true
can_decide=false
can_emit_act=false
emits_act=false
emits_verdict=false
memory_write=false
graphiti_write=false
neo4j_write=false
kernel_mutation=false
x108_mutation=false
Open state

No confirmed danger.
No ACT emission.
No kernel/X108 mutation.

Next

F29_MEMORY_GRAPHITI_RECONCILIATION_AUDIT_OR_F30_WORKFLOW_SOP_ENGINE_AUDIT
