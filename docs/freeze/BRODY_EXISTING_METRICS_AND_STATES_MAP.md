# BRODY EXISTING METRICS AND STATES MAP
# Date: 2026-05-20
# Status: BRODY_EXISTING_METRICS_AND_STATES_MAP_PASS

Scanning rule: a field is valid only if found in an actual module, pointer, or manifest file.
If not found: NOT_FOUND_IN_EXISTING_SOURCES.

---

## A. Session Memory Ledger
Source: CURRENT_BRODY_SESSION_MEMORY_LEDGER_READONLY.txt
        periphery/brody_memory_readonly/session_memory_ledger_readonly/BRODY_SESSION_MEMORY_LEDGER_READONLY_MANIFEST.json
        brody_session_memory_ledger_readonly_v2.py

FIELD_SOURCE_MAP:
  status                  = "BRODY_SESSION_MEMORY_LEDGER_READONLY_V2_READY"
  memory_role             = "GUIDE_CONTEXT_NAVIGATION_ONLY"
  memory_decision         = false
  allowed_to_decide       = false
  emits_act               = false
  emits_allow_hold_block  = false
  emits_verdict           = false
  decision_authority      = "KX108_ONLY"
  kernel_mutation         = false
  x108_mutation           = false
  x108_runtime_binding    = false
  x108_merge              = false
  neo4j_role              = "LIVE_GRAPH_MEMORY_SURFACE_ONLY"
  brody_role              = "SESSION_MEMORY_LEDGER_READONLY"
  auto_triage             = false
  memory_intake           = false
  graphiti_index_write    = false
  readonly                = true
  response_only           = true
  real_llm_connected      = false
  model_provider_bound    = false

build_record() returns:
  status                  = "BRODY_SESSION_MEMORY_LEDGER_READONLY_V2_PASS"
  session_id              = <str>
  session_dir             = <path>
  sequence                = <int>
  event_hash              = <sha256-hex>
  previous_event_hash     = <sha256-hex>
  record_json             = <path>
  record_md               = <path>
  session_index           = <path>
  session_ledger_jsonl    = <path>
  memory_query            = <str>
  packet_results_count    = <int>
  triage_status           = "NOT_APPLIED_NEXT_PALIER"
  memory_intake_status    = "TRACE_ONLY_NOT_INDEXED"

NOT_FOUND_IN_EXISTING_SOURCES (invented, forbidden in runtime):
  confidence              = NOT_FOUND_IN_EXISTING_SOURCES
  risk_level              = NOT_FOUND_IN_EXISTING_SOURCES
  automation_score        = NOT_FOUND_IN_EXISTING_SOURCES

---

## B. Session Presave Buffer
Source: periphery/brody_memory_readonly/session_presave_buffer_readonly/BRODY_SESSION_PRESAVE_BUFFER_READONLY_MANIFEST.json
        brody_session_presave_buffer_readonly_v1.py

FIELD_SOURCE_MAP:
  presave_buffer          = true
  manual_validation_required = true
  graphiti_index_write    = false
  memory_intake           = false
  memory_decision         = false
  allowed_to_decide       = false
  emits_act               = false
  emits_verdict           = false
  kernel_mutation         = false
  x108_runtime_binding    = false
  x108_merge              = false
  decision_authority      = "KX108_ONLY"
  brody_role              = "SESSION_PRESAVE_BUFFER_READONLY"
  memory_role             = "GUIDE_CONTEXT_NAVIGATION_ONLY"
  readonly                = true
  response_only           = true

---

## C. Auto Triage Memory Intake
Source: periphery/brody_memory_readonly/auto_triage_memory_intake_readonly/BRODY_AUTO_TRIAGE_MEMORY_INTAKE_READONLY_MANIFEST.json
        brody_auto_triage_memory_intake_readonly_v1.py

FIELD_SOURCE_MAP (boundary):
  auto_triage             = true
  memory_intake           = false
  graphiti_index_write    = false
  memory_decision         = false
  allowed_to_decide       = false
  emits_act               = false
  emits_allow_hold_block  = false
  emits_verdict           = false
  kernel_mutation         = false
  x108_mutation           = false
  x108_runtime_binding    = false
  x108_merge              = false
  decision_authority      = "KX108_ONLY"
  brody_role              = "AUTO_TRIAGE_MEMORY_INTAKE_READONLY"
  memory_role             = "GUIDE_CONTEXT_NAVIGATION_ONLY"
  readonly                = true
  response_only           = true
  status                  = "BRODY_AUTO_TRIAGE_MEMORY_INTAKE_READONLY_PASS"

ALLOWED ZONE VALUES (from adapted_rules in manifest):
  "CRISTAL"               = "memory_candidate_only_not_canon"
  "TRANSITION"            = "review_candidate_only"
  "NEANT"                 = "reject_candidate_only_no_delete"

  BLOCK_IMMEDIATE         = FORBIDDEN (replaced by REFLEX_ALERT_ONLY)

ALLOWED REFLEX STATUSES (from ReflexReducer in module):
  "REFLEX_ALERT_ONLY"
  "PROCEED_CONTEXT_ONLY"

classify_record() output fields (REAL):
  zone                    = "CRISTAL" | "TRANSITION" | "NEANT"
  memory_candidate        = true | false
  review_candidate        = true | false
  reject_candidate        = true | false
  axes                    = [str...]     (x108, memory, graphiti, tree34, kernel, proof, boundary, triage)
  reasons                 = [str...]
  friction.heat           = float
  friction.stable_hint    = bool
  resonance.resonance_hint = bool
  resonance.signature_mod_49 = int
  reflex.status           = "REFLEX_ALERT_ONLY" | "PROCEED_CONTEXT_ONLY"
  reflex.alerts           = [str...]
  event_hash              = <sha256-hex>

NOT_FOUND_IN_EXISTING_SOURCES (forbidden in runtime):
  confidence              = NOT_FOUND_IN_EXISTING_SOURCES
  triage_score            = NOT_FOUND_IN_EXISTING_SOURCES
  risk_level              = NOT_FOUND_IN_EXISTING_SOURCES

---

## D. Human Command Packet
Source: CURRENT_BRODY_HUMAN_COMMAND_PACKET_READONLY.txt
        periphery/brody_memory_readonly/brody_human_command_packet_readonly/BRODY_HUMAN_COMMAND_PACKET_READONLY_MANIFEST.json
        brody_human_command_packet_readonly_v1.py

build_human_command_packet() returns:
  status                       = "BRODY_HUMAN_COMMAND_PACKET_READONLY_V1_PACKETIZED"
  packet_kind                  = "HUMAN_OPERATOR_COMMAND_PACKET"
  classification               = <str from gate>
  operator_action              = "MANUAL_REVIEW_AND_MANUAL_EXECUTION_ONLY"
  brody_execute_allowed        = false
  brody_authorize_allowed      = false
  executed                     = false
  requires_human_operator      = true
  readonly_analysis_only       = true
  network_executed             = false
  filesystem_mutation_executed = false
  git_mutation_executed        = false
  graphiti_write               = false
  graphiti_index_write         = false
  neo4j_write_executed         = false
  memory_intake                = false
  memory_decision              = false
  allowed_to_decide            = false
  emits_act                    = false
  emits_verdict                = false
  decision_authority           = "KX108_ONLY"
  kernel_mutation              = false
  x108_runtime_binding         = false
  x108_merge                   = false

---

## E. Writable Memory Protocol
Source: _local_audits/brody_memory_pipeline_commit_now_20260514/
        BRODY_WRITABLE_MEMORY_PROTOCOL_CANDIDATE_READONLY_20260514_003129/
        WRITABLE_MEMORY_ACTIVATION_CHECKLIST.md

FIELD_SOURCE_MAP:
  writable_memory_active  = false
  protocol_state          = "PROTOCOL_CANDIDATE_ONLY"
  gates_passing           = "0/6"
  operator_approval       = false
  real_import_ready       = false

Gate IDs (real, from checklist):
  GATE_001  = "HUMAN_OPERATOR_GATE"           status=BLOCKED
  GATE_002  = "KX108_BOUNDARY_GATE"           status=BLOCKED
  GATE_003  = "GRAPHITI_IMPORT_SCOPE_GATE"    status=BLOCKED
  GATE_004  = "NEO4J_WRITE_SCOPE_GATE"        status=BLOCKED
  GATE_005  = "ROLLBACK_GATE"                 status=BLOCKED
  GATE_006  = "POST_IMPORT_AUDIT_GATE"        status=BLOCKED

---

## F. Tree Policy
Source: brody_rights_authority_matrix.py — _TREE_POLICY
        (sourced from T13_T34_SIGNAL_DISCOVERY_READONLY_20260514_025500)

  safe_trees              = ["T13","T14","T15","T16","T17","T18","T19","T23","T25","T26","T27","T28","T29"]
  safe_count              = 13
  safe_docs               = 117
  blocked_action          = ["T20","T21","T22"]
  blocked_action_reason   = "BLOCKED_ACTION_TRIGGER — V_ACTION_TRANSFORMATION"
  blocked_memory          = ["T24"]
  blocked_memory_reason   = "BLOCKED_DIRECT_MEMORY_WRITE — T24 Arbre de la Memoire"
  blocked_agi             = ["T30","T31","T32","T33","T34"]
  blocked_agi_reason      = "BLOCKED_AGI_LAYER — VIII_OBSIDIA_AGI"
  signal_method           = "PATH_SLUG"

---

## G. X108 / Root Boundary
Source: safe_response.py, brody_rights_authority_matrix.py, all manifests

Correct value:  decision_authority = "KX108_ONLY"
Bug found:      safe_response.py has "X108_ONLY" — requires correction to "KX108_ONLY"

---

## H. Token Masking Policy (strip_forbidden_tokens)
Source: apps/obsidia_api/safe_response.py

Current: masks ALL occurrences of ACT/HOLD/BLOCK/ALLOW/DECIDE/VERDICT in text
Correct: mask ONLY sovereign-emission patterns (Brody actively claiming to emit a verdict)
         Allow conceptual mention: "Brody ne peut pas autoriser ACT"

---

## I. Complete NOT_FOUND_IN_EXISTING_SOURCES Registry

Fields that MUST NOT appear as real values in runtime outputs:

  confidence              = NOT_FOUND_IN_EXISTING_SOURCES
  triage_score            = NOT_FOUND_IN_EXISTING_SOURCES
  risk_level              = NOT_FOUND_IN_EXISTING_SOURCES
  automation_score        = NOT_FOUND_IN_EXISTING_SOURCES
  memory_state            = NOT_FOUND_IN_EXISTING_SOURCES (use protocol_state from checklist)
  automation_state        = NOT_FOUND_IN_EXISTING_SOURCES

If a placeholder is needed:  use "NOT_AVAILABLE_FROM_EXISTING_RUNTIME"

---

Result: BRODY_EXISTING_METRICS_AND_STATES_MAP_PASS
