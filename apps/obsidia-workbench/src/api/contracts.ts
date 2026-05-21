/**
 * API contracts — mirrors ObsidiaShell (port 8011) + Engine API (port 8000) response shapes.
 * Read-only. No mutation types defined.
 */

export interface ApiHealthResponse {
  status: 'healthy' | 'degraded' | 'error'
  gateway: string
  version: string
  timestamp: string
  services?: Record<string, { status: string; error?: string }>
}

export interface GraphitiStatusResponse {
  status: 'healthy' | 'degraded' | 'not_loaded'
  frozen: boolean
  run_id?: string
  entity_count?: number
  relation_count?: number
  episode_count?: number
  timestamp?: string
}

export interface GraphitiContextResponse {
  q: string
  results: Array<{
    uuid?: string
    name?: string
    summary?: string
    fact?: string
    episodes?: string[]
    score?: number
  }>
  count: number
  readonly: true
}

export interface GraphitiReadinessResponse {
  ready: boolean
  missing: string[]
  warnings: string[]
  timestamp?: string
}

export interface GraphitiMetricsResponse {
  entity_count: number
  relation_count: number
  episode_count: number
  run_id?: string
  version?: string
}

export interface AuditChainResponse {
  chain: Array<{
    trace_id: string
    timestamp: string
    action?: string
    result?: string
    verdict?: string
  }>
}

/** Automation layer snapshot — from brody_automation_orchestrator.py */
export interface AutomationSnapshot {
  request_type?: string
  created_at?: string
  readonly: true
  advisory_only: true
  memory_write: false
  graphiti_write: false
  neo4j_write: false
  emits_act: false
  decision_authority: 'KX108_ONLY'
  session_ledger?: {
    enabled: boolean
    status: string
    event_candidate_created: boolean
    event_hash?: string
    sequence?: number
    memory_write: false
  }
  presave_buffer?: {
    enabled: boolean
    status: string
    presave_candidate: Record<string, unknown> | null
    manual_validation_required: true
  }
  auto_triage?: {
    enabled: boolean
    zone: 'CRISTAL' | 'TRANSITION' | 'NEANT' | 'NOT_RUN'
    memory_candidate?: boolean
    review_candidate?: boolean
    axes?: string[]
    reasons?: string[]
    reflex_status?: string
    memory_intake: false
    status: string
  }
  memory_candidate_pipeline?: {
    candidate_created: boolean
    needs_review: boolean
    review_gate_status: string
    gates_passing: number
    gates_total: number
    graphiti_write: false
    neo4j_write: false
  }
  operator_loop?: {
    human_command_packet_ready: boolean
    command_gate_classification: string
    execution_allowed_for_brody: false
    human_operator_required: boolean
    packet_status?: string
  }
  next_allowed_steps?: string[]
  blocked_steps?: string[]
}

/** Freeze metrics snapshot — from brody_freeze_metrics_snapshot.py */
export interface FreezeMetricsSnapshot {
  source_mode: 'FREEZE_SOURCED_ONLY'
  status: string
  created_at: string
  workspace_root: string
  pointer_file_count: number
  context_packet_chain: {
    status: string
    query: string
    consumer: string
    engine: string
    hydration: string
    chain_source: string
    neo4j_role: string
  }
  memory_pipeline: {
    status: string
    session_ledger: string
    presave_buffer: string
    auto_triage: string
    graphiti_candidate_prep: string
    graphiti_review_gate: string
    graphiti_import_apply: string
    memory_write: boolean
    graphiti_write: boolean
    neo4j_write: boolean
    source: string
  }
  operator_loop: {
    status: string
    command_gate: string
    human_command_packet: string
    control_loop: string
    execution_line: string
    execution_receipt: string
    handoff_line: string
    final_baseline: string
    brody_execute_allowed: boolean
    human_operator_required: boolean
    receipt_schema_only: boolean
    actual_execution_receipt_present: boolean
    source: string
  }
  x108_boundary: {
    decision_authority: string
    emits_act: boolean
    emits_verdict: boolean
    kernel_mutation: boolean
    x108_runtime_binding: boolean
    x108_merge: boolean
    source: string
  }
  runtime_llm: {
    brody_llm_obsidien: boolean
    runtime_freeze: boolean
    terminal_native_run: boolean
    boundary_ok: boolean
    detector_ok: boolean
    source: string
  }
  x108_proof_state: {
    status: string
    checked_pointer_count: string
    dry_run: boolean
    source: string
  }
  not_found_in_freeze_sources: Record<string, string>
  readonly: true
  memory_write: false
  graphiti_write: false
  neo4j_write: false
  emits_act: false
  emits_verdict: false
  kernel_mutation: false
  decision_authority: 'KX108_ONLY'
  source_files_scanned: string[]
}

/** Structured response engine snapshot — from brody_structured_response_engine_adapter.py */
export interface StructuredResponseSnapshot {
  status: string
  query_stage: 'PASS' | 'PARTIAL' | 'FAILED' | 'UNAVAILABLE'
  consumer_stage: 'PASS' | 'PARTIAL' | 'FAILED' | 'UNAVAILABLE'
  engine_stage: 'PASS' | 'PARTIAL' | 'TERMINAL_FALLBACK' | 'FAILED' | 'UNAVAILABLE'
  context_items_count: number
  text_material_status: 'HAS_MATERIAL' | 'PARTIAL_MATERIAL' | 'LOW_MATERIAL' | 'NO_MATERIAL' | 'CHAIN_UNAVAILABLE'
  response_md: string
  memory_query?: string
  graphiti_status?: string
  graphiti_blocker?: string
  neo4j_status?: string
  selected_items?: unknown[]
  tag_counts?: Record<string, number>
  chain_source?: string
  source_doc_refs?: string[]
  created_at?: string
  readonly: true
  memory_write: false
  graphiti_write: false
  neo4j_write: false
  emits_act: false
  decision_authority: 'KX108_ONLY'
}

/** Memory response chain snapshot — from brody_memory_response_chain_adapter.py */
export interface MemoryResponseChainSnapshot {
  status: string
  source_mode: string
  material_quality: string
  response_md: string
  response_md_length: number
  effective_query: string | null
  primary_query: string
  attempted_queries: Array<{ query: string; results_count: number }>
  graphiti_live: boolean
  neo4j_status: string
  local_index_records_total: number
  hydration_module_used: boolean
  local_response_engine_used: boolean
  final_answer_uses_response_md: boolean
  selected_items?: unknown[]
  readonly: true
  memory_write: false
  decision_authority: 'KX108_ONLY'
}

/** Project memory snapshot — from brody_project_memory_adapter.py */
export interface ProjectMemorySnapshot {
  status: string
  source_mode: string
  local_records_count: number
  text_excerpt_records_count: number
  usable_material: boolean
  cache_enabled: boolean
  graphiti_index_item_count: number
  candidate_ledger_count: number
  contextual_material_status: string
  source_file_used: string
  readonly: true
  memory_write: false
  decision_authority: 'KX108_ONLY'
}

/** Candidate memory snapshot */
export interface CandidateMemorySnapshot {
  status: string
  presave_buffer_found: boolean
  auto_triage_found: boolean
  candidate_only: true
  memory_write: false
  graphiti_write: false
  can_prepare_candidate: boolean
  can_commit_memory: false
  requires_human_gate: true
  decision_authority: 'KX108_ONLY'
}

/** Operator loop snapshot */
export interface OperatorLoopSnapshot {
  status: string
  command_gate: Record<string, unknown>
  operator_required: boolean
  brody_execute_allowed: false
  can_prepare_action_candidate: boolean
  emits_act: false
  memory_write: false
  decision_authority: 'KX108_ONLY'
}

/** Tree policy snapshot */
export interface TreePolicySnapshot {
  status: string
  safe_trees: number
  blocked_action: number
  blocked_memory: number
  blocked_agi: number
  total_trees: number
  readonly: true
  decision_authority: 'KX108_ONLY'
}

/** Temporal context snapshot */
export interface TemporalContextSnapshot {
  status: string
  past_context: Record<string, unknown>
  present_context: Record<string, unknown>
  future_context: Record<string, unknown>
  control_proof_context: Record<string, unknown>
  readonly: true
  decision_authority: 'KX108_ONLY'
}

/** Cognitive modules snapshot */
export interface CognitiveModulesSnapshot {
  status: string
  total_known: number
  modules_found: number
  modules_active: string[]
  modules: Record<string, unknown>
  readonly: true
  decision_authority: 'KX108_ONLY'
}

/** Runtime context — top-level envelope of all snapshots */
export interface RuntimeContext {
  status: string
  created_at: string
  semantic_query_snapshot: Record<string, unknown>
  authority_snapshot: Record<string, unknown>
  session_memory_snapshot: Record<string, unknown>
  project_memory_snapshot: ProjectMemorySnapshot
  memory_response_chain_snapshot: MemoryResponseChainSnapshot
  freeze_metrics_snapshot: Record<string, unknown>
  automation_snapshot: Record<string, unknown>
  candidate_memory_snapshot: CandidateMemorySnapshot
  operator_loop_snapshot: OperatorLoopSnapshot
  tree_policy_snapshot: TreePolicySnapshot
  temporal_context_snapshot: TemporalContextSnapshot
  cognitive_modules_snapshot: CognitiveModulesSnapshot
  brody_full_context: Record<string, unknown>
  true_voice_snapshot: Record<string, unknown>
  memory_chain_pass: boolean
  memory_material_quality: string
  local_records_count: number
  text_excerpt_records_count: number
  voice_source: string
  topic: string
  request_type: string
  readonly: true
  memory_write: false
  decision_authority: 'KX108_ONLY'
}

/** Full /api/brody/chat response */
export interface BrodyChatResponse {
  final_answer: string
  response: string
  decision_authority: 'KX108_ONLY'
  emits_act: false
  memory_write: false
  voice_runtime: string
  source: string
  authority_snapshot: Record<string, unknown>
  semantic_query_snapshot: Record<string, unknown>
  session_memory_snapshot: Record<string, unknown>
  project_memory_snapshot: ProjectMemorySnapshot
  memory_response_chain_snapshot: MemoryResponseChainSnapshot
  freeze_metrics_snapshot: Record<string, unknown>
  automation_snapshot: Record<string, unknown>
  candidate_memory_snapshot: CandidateMemorySnapshot
  operator_loop_snapshot: OperatorLoopSnapshot
  tree_policy_snapshot: TreePolicySnapshot
  temporal_context_snapshot: TemporalContextSnapshot
  cognitive_modules_snapshot: CognitiveModulesSnapshot
  runtime_context: RuntimeContext
  brody_full_context: Record<string, unknown>
  true_voice_snapshot: Record<string, unknown>
}

/** Source tag attached to every resolved value */
export type DataSource = 'api' | 'mock'
export interface Resolved<T> {
  data: T
  source: DataSource
}
