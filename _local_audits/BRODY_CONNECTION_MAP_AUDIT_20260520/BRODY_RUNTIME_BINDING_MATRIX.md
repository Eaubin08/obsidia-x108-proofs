# Brody Runtime Binding Matrix
**Audit date**: 2026-05-20
**Source**: Live TestClient audit of /api/brody/chat × 7 messages + file inventory

Legend: Y=yes, N=no, P=partial, ?=unknown

| Component | Exists | Freeze | Runtime | API Bound | UI Bound | Tested | Write Risk | Current Status | Next Action |
|-----------|--------|--------|---------|-----------|----------|--------|------------|----------------|-------------|
| project_memory_snapshot | Y | Y | Y | Y | Y | Y | N | READY — local sources, graphiti live BLOCKED | Expose graphiti live when Neo4j set |
| session_memory_snapshot | Y | Y | Y | Y | Y | Y | N | READY — session ledger JSONL, strict followup | None |
| true_response_structure_snapshot | Y | Y | Y | Y | N | Y | N | READY — terminal dialogue identity | None |
| brody_full_context | Y | Y | Y | Y | N | Y | N | READY — unifies all foundations | None |
| true_voice_snapshot | Y | Y | Y | Y | Y | Y | N | READY — synthesizes final_answer | Local index synthesis added |
| authority_snapshot | Y | Y | Y | Y | Y | Y | N | READY | None |
| automation_snapshot | Y | Y | Y | Y | Y | Y | N | READY — structure present; operator_loop status empty | Activate operator_loop status (P2) |
| structured_response_snapshot | Y | Y | Y | Y | Y | Y | N | READY — stages: QUERY/CONSUMER/ENGINE | None |
| freeze_metrics_snapshot | Y | Y | Y | Y | Y | Y | N | READY — pointer files read | None |
| memory_response_chain_snapshot | Y | Y | Y | Y | Y | Y | N | READY — LOCAL_GRAPHITI_INDEX_FALLBACK active | Wire Neo4j when available |
| semantic_query_snapshot | Y | N | Y | Y | Y | Y | N | READY — topic+primary_query+fallbacks | None |
| context_packet_query | Y | N | Y | P | N | N | N | READY periphery module — bypassed when Neo4j offline | Use when Neo4j set |
| context_packet_consumer | Y | N | Y | P | N | N | N | READY periphery module — used by structured_response_adapter | None |
| local_response_engine | Y | N | Y | P | N | N | N | READY periphery module — called from chain adapter | None |
| terminal_structural_dialogue | Y | Y | Y | P | N | Y | N | READY — Foundation C identity source | None |
| language routing / OS Trad | Y | Y | Y | Y | Y | Y | N | READY — translation_trace in API | None |
| IR candidate | Y | Y | Y | Y | N | P | N | READY — ir_candidate present in all API calls | None |
| translation_trace | Y | Y | Y | Y | N | P | N | READY — translation_trace_snapshot in API | None |
| x108_boundary | Y | Y | Y | Y | Y | Y | N | READY — decision_authority=KX108_ONLY in all calls | None |
| rights / authority matrix | Y | Y | Y | Y | Y | Y | N | READY — request_type classification working | None |
| operator_loop | Y | Y | P | P | N | N | N | PARTIAL — field present in automation_snapshot; status empty | P2: activate status reporting |
| local_command_gate | Y | N | N | N | N | N | N | UNBOUND — periphery module exists | P2: bind to automation_snapshot |
| human_command_packet | Y | N | N | N | N | N | N | UNBOUND — periphery module exists | P2: bind to operator loop |
| execution_receipt | Y | N | N | N | N | N | N | UNBOUND — periphery validator exists | P2: bind to operator loop |
| handoff_line | N | N | N | N | N | N | N | MISSING — no dedicated module found | P3: research |
| session_ledger | Y | Y | Y | P | N | Y | N | READY — writes locally; exposed via session_memory | None |
| presave_buffer | Y | Y | Y | P | N | N | N | READY — stages candidates; in automation_snapshot | None |
| auto_triage | Y | N | Y | P | N | N | N | READY — in automation_snapshot | None |
| memory_candidate_pipeline | Y | N | Y | Y | N | N | N | PRESENT in automation_snapshot field | None |
| graphiti_candidate_prep | Y | N | N | N | N | N | N | UNBOUND — full pipeline in periphery | P6: after Neo4j |
| graphiti_review_gate | Y | N | N | N | N | N | N | UNBOUND — manual only | P6: after Neo4j |
| graphiti_import_apply | Y | N | N | N | N | N | LOW | UNBOUND — manual only; guarded | P6: after Neo4j — human approval required |
| Graphiti V20 readonly index | Y | Y | Y | P | Y | Y | N | READY — 3267 records loaded; local path only | Use live Neo4j index when available |
| Neo4j guide bridge | Y | N | N | N | N | N | N | UNBOUND — blocked by NEO4J_PASSWORD_NOT_SET | Requires env var + running Neo4j |
| BrodyMemoryDoc | Y | N | N | N | N | N | N | EXISTS in periphery context_packet_query; Neo4j offline | Requires Neo4j |
| Mmonde / 34 arbres | Y | Y | P | P | N | Y | N | PARTIAL — tree_policy bound; Mmonde world source unbound | P3 |
| tree_policy | Y | Y | Y | Y | N | Y | N | READY | None |
| tool_call_candidate | N | N | N | N | N | N | N | MISSING — no module produces structured tool-call | P1: build tool_call_candidate readonly adapter |
| ActionCandidate | P | N | N | N | N | N | N | PARTIAL — ir_candidate exists; no structured ActionCandidate output | P3 |
| BFCL V1 | Y | Y | N | N | N | Y | N | FROZEN_PASS — offline path only | Do not touch |
| BFCL V2 | Y | Y | P | P | N | N | N | BLOCKED — runtime callable; no candidate output | P1: needs tool_call_candidate layer |
| SWE-bench | P | Y | N | N | N | N | N | SMOKE_ONLY — WSL Docker; Brody not yet integrated | P5: deferred |
| Terminal-Bench | Y | Y | N | N | N | N | N | SMOKE_ONLY (oracle) — Brody not yet integrated | P5: deferred |

---

## Key Observation

**14 snapshot fields confirmed in /api/brody/chat response** (all 7 test messages):
`final_answer`, `brody_full_context`, `true_voice_snapshot`, `project_memory_snapshot`,
`session_memory_snapshot`, `true_response_structure_snapshot`, `authority_snapshot`,
`automation_snapshot`, `structured_response_snapshot`, `freeze_metrics_snapshot`,
`memory_response_chain_snapshot`, `semantic_query_snapshot`, `ir_candidate`, `translation_trace`

**Absent from API response** (confirmed None/missing in live calls):
`tool_call_candidate` — blocking BFCL V2 PASS
