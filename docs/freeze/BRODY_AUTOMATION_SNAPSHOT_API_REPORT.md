# BRODY AUTOMATION SNAPSHOT API REPORT
# Date: 2026-05-20
# Status: API_BRODY_AUTOMATION_SNAPSHOT_PASS

---

## /api/brody/chat payload — automation_snapshot field

Added to response payload:
  automation_snapshot: {
    session_ledger: { enabled, status, event_candidate_created, event_hash, sequence, memory_write: false }
    presave_buffer: { enabled, status, presave_candidate, manual_validation_required: true }
    auto_triage: { enabled, zone, memory_candidate, review_candidate, axes, reasons, memory_intake: false }
    memory_candidate_pipeline: { candidate_created, needs_review, review_gate_status, gates_passing, gates_total, graphiti_write: false, neo4j_write: false }
    operator_loop: { human_command_packet_ready, command_gate_classification, execution_allowed_for_brody: false, human_operator_required }
    next_allowed_steps: [...]
    blocked_steps: [...]
    request_type: ...
    created_at: ...
    readonly: true
    emits_act: false
    graphiti_write: false
    neo4j_write: false
    decision_authority: KX108_ONLY
  }

## Route change (apps/obsidia_api/routes/brody.py)

1. Import run_brody_automation_layer + enrich_final_answer_with_automation
2. After v1412a: extract authority_snapshot.request_type
3. Call run_brody_automation_layer(session_id, message, language, request_type, authority_snapshot, context_packet, response_md)
4. Call enrich_final_answer_with_automation(raw_answer, automation_snapshot, language)
5. Add automation_snapshot to safe_backend_response payload

## Boundary invariants in payload

All automation_snapshot fields are readonly.
graphiti_write=false at all levels.
neo4j_write=false at all levels.
emits_act=false.
decision_authority=KX108_ONLY.
No runtime mutation.

Result: API_BRODY_AUTOMATION_SNAPSHOT_PASS
