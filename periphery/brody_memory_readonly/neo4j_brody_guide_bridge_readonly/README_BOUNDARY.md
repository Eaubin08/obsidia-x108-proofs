# BRODY NEO4J GUIDE BRIDGE READONLY

- status: BRODY_NEO4J_GUIDE_BRIDGE_READONLY_READY
- memory_role: GUIDE_CONTEXT_NAVIGATION_ONLY
- neo4j_role: LIVE_GRAPH_MEMORY_SURFACE_ONLY
- brody_role: CONTEXT_CONSUMER

## Boundary

MEMORY_DECISION=false
ALLOWED_TO_DECIDE=false
EMITS_ACT=false
DECISION_AUTHORITY=KX108_ONLY
KERNEL_MUTATION=false
X108_RUNTIME_BINDING=false
X108_MERGE=false

This bridge imports / queries memory records for Brody guidance only.
It must not influence X108 verdicts.
