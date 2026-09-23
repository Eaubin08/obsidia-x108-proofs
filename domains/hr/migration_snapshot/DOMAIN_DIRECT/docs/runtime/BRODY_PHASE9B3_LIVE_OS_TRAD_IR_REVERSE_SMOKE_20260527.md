# BRODY_PHASE9B3_LIVE_OS_TRAD_IR_REVERSE_SMOKE_20260527

Status: DIAGNOSTIC_ONLY

## Scope
Live smoke test for Phase 9B2 backend OS Trad / IR / OS Reverse routes on 8012.

## OpenAPI routes
- route=/api/os-trad/translate exists=True
- route=/api/ir/candidate exists=True
- route=/api/os-reverse/project exists=True
- route=/api/brody/chat exists=True

## Live POST results
- name=os_trad_translate path=/api/os-trad/translate status=OK code=200 readonly=True advisory_only=True emits_act=False emits_verdict=False decision_authority=KX108_ONLY memory_write=False graphiti_write=False kernel_mutation=False x108_mutation=False source=REAL_BACKEND length=1624
- name=ir_candidate path=/api/ir/candidate status=OK code=200 readonly=True advisory_only=True emits_act=False emits_verdict=False decision_authority=KX108_ONLY memory_write=False graphiti_write=False kernel_mutation=False x108_mutation=False source=REAL_BACKEND length=1265
- name=os_reverse_project path=/api/os-reverse/project status=OK code=200 readonly=True advisory_only=True emits_act=False emits_verdict=False decision_authority=KX108_ONLY memory_write=False graphiti_write=False kernel_mutation=False x108_mutation=False source=REAL_BACKEND length=1781

## Result
- openapi_route_pass_count = 4 / 4
- live_post_boundary_pass_count = 3 / 3

## Boundary
- Live smoke only.
- No source patch.
- No kernel mutation.
- No X108 mutation.
- No memory write requested.
- No Graphiti write requested.
- KX108_ONLY remains sole decision authority.