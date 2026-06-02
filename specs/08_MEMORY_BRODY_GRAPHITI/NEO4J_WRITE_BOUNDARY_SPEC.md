# NEO4J_WRITE_BOUNDARY_SPEC
Status: SOURCE_ORGANIZED
Authority: KX108_ONLY
Source Paths:
- sigma/graphiti_readonly_bridge.py\n- docs/freeze/BRODY_RIGHTS_AUTHORITY_MATRIX_REPORT.md
Source Status: SOURCE_ORGANIZED
Scope: Boundary neo4j write.
Allowed:
- neo4j_write = gate humain obligatoire\n- Lecture neo4j = toujours autorisée
Forbidden:
- neo4j_write sans gate\n- neo4j_write sans X108 ALLOW
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
