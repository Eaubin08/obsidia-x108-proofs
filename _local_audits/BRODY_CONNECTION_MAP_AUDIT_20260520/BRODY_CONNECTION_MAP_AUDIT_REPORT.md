# BRODY CONNECTION MAP AUDIT — 2026-05-20

## Scope
READONLY audit. No patches, no runtime changes, no Neo4j connection.

## Live Status
- /api/brody/chat: 7/7 cases return HTTP 200
- All responses: KX108_ONLY, emits_act=false, memory_write=false
- Memory chain: ERROR — NEO4J_PASSWORD_NOT_SET (expected, Neo4j not configured)
- Tool call candidate: ABSENT (no layer exists)
- Graphiti: BLOCKED (port 7688 closed)
- Source: REAL_BRODY_RUNTIME_NO_GRAPHITI

## What's Bound
| Layer | Status |
|---|---|
| project_memory_snapshot | API BOUND |
| session_memory_snapshot | API BOUND |
| true_response_structure | API BOUND |
| brody_full_context | API BOUND |
| true_voice_snapshot | API BOUND |
| freeze_metrics_snapshot | API BOUND |
| authority_snapshot | API BOUND |
| automation_snapshot | API BOUND |
| semantic_query_router | API BOUND |
| memory_response_chain | API BOUND (Neo4j-dependent) |

## What Exists But Is Not API-Bound
- operator_loop (7 modules freeze-sourced, not in payload)
- command_gate (freeze-sourced, not in payload)
- graphiti_candidate_pipeline (6 modules, not wired)
- external_access_bridge (16 API bridge modules, freeze-only)

## Blockers
1. **tool_call_candidate adapter** — MISSING, blocks BFCL V2
2. **Neo4j live** — NEO4J_PASSWORD not set in API process

## Next Priority
P1: tool_call_candidate readonly adapter
P2: Neo4j live memory chain activation
P3: operator_loop API binding
