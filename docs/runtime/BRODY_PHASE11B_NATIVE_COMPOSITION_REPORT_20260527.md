# BRODY_PHASE11B_NATIVE_COMPOSITION_REPORT_20260527

Status: PASS

## Scope

Phase 11B adds native Brody machination composition inside /api/brody/chat without changing X108 authority.

## Added

- apps/obsidia_api/brody_contracts_packet.py
- apps/obsidia_api/brody_machination_composer.py
- tests/api/test_brody_native_machination_packet.py

## Patched

- apps/obsidia_api/routes/brody.py

## Native fields added to /api/brody/chat

- contracts
- authority_contract
- permission_matrix
- kernel_contract
- boundary_contract
- signal_contract
- forbidden_output_contract
- machination_packet
- support_routes
- support_summary

## Final live validation

After restarting 8011 / 8012 / 5173 and launching 8012 with NEO4J_PASSWORD from graphiti-lab\.env.graphiti.local:

- graphiti_v20_status=OK
- graphiti_v20_context=OK
- brody_openapi=OK
- brody_graphiti_status=OK
- source=REAL_BRODY_GRAPHITI_LIVE
- graphiti_status=GRAPHITI_LIVE_READONLY_PASS
- graphiti_blocker=
- neo4j_status=LIVE_READONLY
- contracts=True
- machination_packet=True
- support_routes=True
- support_summary=True
- support_boundary=KX108_ONLY

## Boundary

Preserved:

- readonly=true
- advisory_only=true
- context_signal_only=true
- allowed_to_decide=false
- allowed_to_act=false
- emits_act=false
- emits_verdict=false
- memory_write=false
- graphiti_write=false
- neo4j_write=false
- kernel_mutation=false
- x108_mutation=false
- decision_authority=KX108_ONLY

## Tests

- py_compile passed
- targeted pytest passed: 65 passed, 2 pre-existing duplicate OpenAPI operation ID warnings
- live payload recheck passed after restarting 8012 with NEO4J_PASSWORD
- Graphiti V20 frozen endpoints live on 8011
- Workbench UI live on 5173

## Decision

Phase 11B validates native Brody machination composition.

Current state:

/api/brody/chat =
Brody primary voice
+ Graphiti live readonly
+ Neo4j live readonly
+ contracts
+ permission matrix
+ kernel contract
+ boundary contract
+ signal contract
+ forbidden output contract
+ machination packet
+ support routes
+ support summary
+ KX108_ONLY authority.
