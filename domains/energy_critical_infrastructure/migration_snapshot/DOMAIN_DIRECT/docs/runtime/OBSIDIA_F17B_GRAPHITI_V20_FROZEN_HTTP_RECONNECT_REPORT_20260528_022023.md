# OBSIDIA F17B — GRAPHITI V20 FROZEN HTTP RECONNECT REPORT

Date: 20260528_022023
CHECKPOINT: F17B_GRAPHITI_V20_FROZEN_HTTP_RECONNECT
MODE: PATCH
STATUS: PASS_LOCAL_AWAITING_COMMIT

## ROOT CAUSE FROM F17A

8000 had Graphiti blocked because NEO4J_PASSWORD was not set.
8011 Graphiti V20 frozen was available and readonly.
The memory chain jumped to local JSONL before trying 8011 when Neo4j credentials were missing.

## PATCH IMPLEMENTED

Source order after patch:

1. Neo4j live when credentials + port are available.
2. Graphiti V20 frozen HTTP via 8011 when Neo4j is unavailable.
3. Local JSONL index fallback only if 8011 is empty/unavailable.

## FILES TOUCHED

- apps/obsidia_api/brody_memory_response_chain_adapter.py
- apps/obsidia_api/brody_real_response_pipeline.py
- apps/obsidia_api/brody_full_runtime_orchestrator.py
- tests/api/test_f17b_graphiti_v20_frozen_reconnect.py
- scripts/f17b_runtime_payload_assert.py
- docs/runtime/F17B_TERMINAL_GRAPHITI_V20_RECONNECT.txt
- docs/runtime/F17B_8000_BRODY_GRAPHITI_RECONNECT_PAYLOAD.json

## BOUNDARY CHECK

KX108_ONLY=true
readonly=true
graphiti_write=false
memory_write=false
emits_act=false
emits_verdict=false
kernel_mutation=false
x108_mutation=false
execution_allowed=false

## NEXT STEP

Commit/tag/push after user validation.
