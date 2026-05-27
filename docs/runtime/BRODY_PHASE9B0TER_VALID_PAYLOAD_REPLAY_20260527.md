# BRODY_PHASE9B0TER_VALID_PAYLOAD_REPLAY_20260527

Status: DIAGNOSTIC_ONLY

## Scope
Replay Phase 9B-0 routes that previously returned 422 using payloads derived from OpenAPI schemas.

## Result
- pass_count = 7
- total = 7

## Replay results
- context_build: path=/api/periphery/context/build status=OK code=200 length=588 preview={"readonly":true,"advisory_only":true,"emits_act":false,"emits_verdict":false,"decision_authority":"KX108_ONLY","memory_write":false,"kernel_mutation":false,"real_action":false,"source":"REAL_BACKEND","timestamp":"2026-05-27T05:53:33.009197+00:00","packet_id":"2a89e92f7bd442ebaf9cdd555492f302","acti
- context_ingress: path=/api/periphery/context/ingress status=OK code=200 length=379 preview={"readonly":true,"advisory_only":true,"emits_act":false,"emits_verdict":false,"decision_authority":"KX108_ONLY","memory_write":false,"kernel_mutation":false,"real_action":false,"source":"REAL_BACKEND","timestamp":"2026-05-27T05:53:33.019338+00:00","action_id":"phase9b0ter","context_accepted":false,"
- brody_language_route: path=/api/periphery/brody/language-route status=OK code=200 length=352 preview={"readonly":true,"advisory_only":true,"emits_act":false,"emits_verdict":false,"decision_authority":"KX108_ONLY","memory_write":false,"kernel_mutation":false,"real_action":false,"source":"REAL_BACKEND","timestamp":"2026-05-27T05:53:33.028356+00:00","query_id":"phase9b0ter_lang","detected_language":"f
- brody_context_query: path=/api/periphery/brody/context-query status=OK code=200 length=440 preview={"readonly":true,"advisory_only":true,"emits_act":false,"emits_verdict":false,"decision_authority":"KX108_ONLY","memory_write":false,"kernel_mutation":false,"real_action":false,"source":"REAL_BACKEND","timestamp":"2026-05-27T05:53:33.038960+00:00","query_id":"phase9b0ter_context","query_text":"OS Tr
- brody_double_brain: path=/api/periphery/brody/double-brain-route status=OK code=200 length=386 preview={"readonly":true,"advisory_only":true,"emits_act":false,"emits_verdict":false,"decision_authority":"KX108_ONLY","memory_write":false,"kernel_mutation":false,"real_action":false,"source":"REAL_BACKEND","timestamp":"2026-05-27T05:53:33.050391+00:00","route_id":"phase9b0ter_bdf","mode":"BALANCED","syst
- brody_diffusion_mix: path=/api/periphery/brody/diffusion-mix status=OK code=200 length=378 preview={"readonly":true,"advisory_only":true,"emits_act":false,"emits_verdict":false,"decision_authority":"KX108_ONLY","memory_write":false,"kernel_mutation":false,"real_action":false,"source":"REAL_BACKEND","timestamp":"2026-05-27T05:53:33.060465+00:00","mix_id":"phase9b0ter_diffusion","llm_weight":0.8,"d
- graphiti_context_adapt: path=/api/periphery/graphiti/context-adapt status=OK code=200 length=426 preview={"readonly":true,"advisory_only":true,"emits_act":false,"emits_verdict":false,"decision_authority":"KX108_ONLY","memory_write":false,"kernel_mutation":false,"real_action":false,"source":"REAL_BACKEND","timestamp":"2026-05-27T05:53:33.070684+00:00","adapter_id":"phase9b0ter_graphiti","source_query_id

## Interpretation
- HTTP 200 means route is live with valid payload.
- HTTP 422 after schema correction means deeper model mismatch.
- HTTP 404 means missing route.
- These routes are supporting surfaces for Phase 9B binding, not decision authorities.

## Boundary
- Diagnostic only.
- No source patch.
- No kernel mutation.
- No X108 mutation.
- No Graphiti write requested.
- No memory write requested.
- KX108_ONLY remains sole decision authority.