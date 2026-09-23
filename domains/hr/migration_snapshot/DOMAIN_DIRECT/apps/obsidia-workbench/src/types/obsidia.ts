export type GateResult = 'ALLOW' | 'HOLD' | 'BLOCK' | 'DRY_RUN_ONLY'

export interface BrodyMessage {
  id: string
  role: 'user' | 'brody'
  content: string
  timestamp: string
  readonly: boolean
  emits_act: boolean
  memory_write: boolean
  decision_authority: 'KX108_ONLY'
  language: string
  source?: 'REAL_BRODY_GRAPHITI_LIVE' | 'REAL_BRODY_LOCAL_ENGINE_ONLY' | 'REAL_BRODY_LLM_AUTHORIZED_READONLY' | 'REAL_BRODY_RUNTIME_NO_GRAPHITI' | 'REAL_BACKEND' | 'BACKEND_STUB' | 'FRONTEND_MOCK' | 'MEMORY_RESPONSE_CHAIN' | 'API_ERROR' | string
  backendPayload?: Record<string, unknown>
}

export interface ContextPacket {
  packet_id: string
  query: string
  language: string
  context_items: string[]
  source_refs: string[]
  dominant_trees: number[]
  memory_status: string
  retrieval_status: string
  risk_flags: string[]
  unknowns: string[]
  contradictions: string[]
  forbidden_tokens_detected: string[]
  readonly: true
  context_signal_only: true
  decision_authority: 'KX108_ONLY'
  allowed_to_decide: false
  allowed_to_act: false
  kernel_mutation: false
  memory_write: false
}

export interface OS3ProofTicket {
  ticket_id: string
  action_id: string
  status: 'PROOF_VALID' | 'PROOF_PENDING' | 'PROOF_INVALID'
  lean_ref: string
  tla_ref: string
  merkle_hash: string
  timestamp: string
  os3_proves: true
  kernel_decides: true
}

export interface SovereignTicket {
  ticket_id: string
  issued_for: string
  authorized_by: 'KX108_ONLY'
  world_call_class: 'READ_ONLY_WORLD_CALL' | 'REVERSIBLE_WORLD_CALL' | 'IRREVERSIBLE_WORLD_CALL' | 'CRITICAL_WORLD_CALL' | 'FORBIDDEN_WORLD_CALL' | 'NO_WORLD_CALL'
  dry_run_only: boolean
  real_action_blocked: boolean
  timestamp: string
}

export interface WorldCallEvent {
  event_id: string
  world_call_class: SovereignTicket['world_call_class']
  action_description: string
  dry_run_only: true
  real_action_taken: false
  timestamp: string
  gateway_result: GateResult
}

export interface MemoryCandidate {
  candidate_id: string
  source_type: 'BRODY_RUNTIME' | 'GRAPHITI_GRAPH' | 'FEEDBACK_CAPTURE' | 'CONTEXT_PACKET'
  content_summary: string
  status: 'CANDIDATE_ONLY' | 'NEEDS_REVIEW' | 'PROMOTION_READY' | 'REJECTED' | 'FROZEN'
  memory_write_allowed: false
  auto_promotion_allowed: false
  created_at: string
}

export interface GencoinEntry {
  entry_id: string
  proof_ref: string
  amount_symbolic: number
  ledger_only: true
  is_real_token: false
  post_proof_only: true
  timestamp: string
  description: string
}

export interface AuditEvent {
  event_id: string
  type: 'context_read' | 'brody_response' | 'memory_candidate' | 'governance_check' | 'world_call' | 'gencoin_entry'
  description: string
  result: 'OK' | 'BLOCKED' | 'DRY_RUN' | 'HOLD'
  timestamp: string
}

export interface KernelStatus {
  kernel_id: 'X-108'
  status: 'ACTIVE' | 'FROZEN' | 'DEGRADED'
  readonly: true
  tests_passing: number
  protected_files_clean: true
  last_checked: string
}
