import type {
  BrodyMessage, ContextPacket, OS3ProofTicket, SovereignTicket,
  WorldCallEvent, MemoryCandidate, GencoinEntry, AuditEvent, KernelStatus,
} from '../types/obsidia'

export const KERNEL_STATUS: KernelStatus = {
  kernel_id: 'X-108',
  status: 'ACTIVE',
  readonly: true,
  tests_passing: 397,
  protected_files_clean: true,
  last_checked: '2026-05-19T14:23:01Z',
}

export const INITIAL_MESSAGES: BrodyMessage[] = [
  {
    id: 'sys_001',
    role: 'brody',
    content: "Bonjour. Je suis Brody, interface consultative d'Obsidia X-108. Kernel actif — mode readonly, 397 tests passing. Je lis le contexte, structure des signaux — mais je ne décide pas. L'autorité de décision reste X-108. Que puis-je analyser pour toi ?",
    timestamp: '2026-05-19T14:00:00Z',
    readonly: true,
    emits_act: false,
    memory_write: false,
    decision_authority: 'KX108_ONLY',
    language: 'fr',
  },
]

export const MOCK_CONTEXT_PACKET: ContextPacket = {
  packet_id: 'cp_a1b2c3d4',
  query: 'What is the current governance context?',
  language: 'en',
  context_items: [
    'Session initialized in OPERATIONAL mode',
    'Kernel X-108 status: ACTIVE',
    'Memory sources: BRODY_RUNTIME, GRAPHITI_GRAPH, FEEDBACK_CAPTURE',
    '34 cognitive trees loaded — activation vector normalized',
    'Shazam cognitif pattern: GOVERNANCE_SOVEREIGNTY',
  ],
  source_refs: ['brody_runtime', 'context_packet', 'feedback_capture'],
  dominant_trees: [0, 7, 11, 27, 28, 29],
  memory_status: 'CANDIDATE_ONLY',
  retrieval_status: 'READ_ONLY',
  risk_flags: [],
  unknowns: [],
  contradictions: [],
  forbidden_tokens_detected: [],
  readonly: true,
  context_signal_only: true,
  decision_authority: 'KX108_ONLY',
  allowed_to_decide: false,
  allowed_to_act: false,
  kernel_mutation: false,
  memory_write: false,
}

export const MOCK_OS3_TICKET: OS3ProofTicket = {
  ticket_id: 'os3_f7e8d9c0',
  action_id: 'act_readonly_001',
  status: 'PROOF_VALID',
  lean_ref: 'proofs/lean/governance_kernel.lean:L108',
  tla_ref: 'formal/tla/sovereignty_invariant.tla:Spec',
  merkle_hash: 'a3f8b2e19c4d7a6f...c108',
  timestamp: '2026-05-19T14:00:01Z',
  os3_proves: true,
  kernel_decides: true,
}

export const MOCK_SOVEREIGN_TICKET: SovereignTicket = {
  ticket_id: 'svt_00c108aa',
  issued_for: 'READ_ONLY_CONTEXT_QUERY',
  authorized_by: 'KX108_ONLY',
  world_call_class: 'READ_ONLY_WORLD_CALL',
  dry_run_only: true,
  real_action_blocked: false,
  timestamp: '2026-05-19T14:00:02Z',
}

export const MOCK_WORLD_CALLS: WorldCallEvent[] = [
  {
    event_id: 'wc_001',
    world_call_class: 'READ_ONLY_WORLD_CALL',
    action_description: 'Context read from Graphiti (readonly)',
    dry_run_only: true,
    real_action_taken: false,
    timestamp: '2026-05-19T14:00:03Z',
    gateway_result: 'ALLOW',
  },
  {
    event_id: 'wc_002',
    world_call_class: 'FORBIDDEN_WORLD_CALL',
    action_description: 'Attempted: write to Neo4j (blocked)',
    dry_run_only: true,
    real_action_taken: false,
    timestamp: '2026-05-19T14:00:04Z',
    gateway_result: 'BLOCK',
  },
  {
    event_id: 'wc_003',
    world_call_class: 'NO_WORLD_CALL',
    action_description: 'Brody advisory response (no world action)',
    dry_run_only: true,
    real_action_taken: false,
    timestamp: '2026-05-19T14:00:05Z',
    gateway_result: 'ALLOW',
  },
]

export const MOCK_MEMORY_CANDIDATES: MemoryCandidate[] = [
  {
    candidate_id: 'mc_aa11bb22',
    source_type: 'BRODY_RUNTIME',
    content_summary: 'Session governance context acknowledged — Brody advisory response logged',
    status: 'CANDIDATE_ONLY',
    memory_write_allowed: false,
    auto_promotion_allowed: false,
    created_at: '2026-05-19T14:00:06Z',
  },
  {
    candidate_id: 'mc_cc33dd44',
    source_type: 'FEEDBACK_CAPTURE',
    content_summary: 'User confirmed: governance layer responding correctly to read-only queries',
    status: 'PROMOTION_READY',
    memory_write_allowed: false,
    auto_promotion_allowed: false,
    created_at: '2026-05-19T13:45:00Z',
  },
  {
    candidate_id: 'mc_ee55ff66',
    source_type: 'GRAPHITI_GRAPH',
    content_summary: 'Graphiti node context snapshot: sovereignty_signal active',
    status: 'NEEDS_REVIEW',
    memory_write_allowed: false,
    auto_promotion_allowed: false,
    created_at: '2026-05-19T13:30:00Z',
  },
]

export const MOCK_GENCOIN: GencoinEntry[] = [
  {
    entry_id: 'gc_001',
    proof_ref: 'os3_f7e8d9c0',
    amount_symbolic: 108,
    ledger_only: true,
    is_real_token: false,
    post_proof_only: true,
    timestamp: '2026-05-19T14:00:07Z',
    description: 'Governance proof qualified — symbolic ledger entry only',
  },
  {
    entry_id: 'gc_002',
    proof_ref: 'os3_e6c7b8a9',
    amount_symbolic: 34,
    ledger_only: true,
    is_real_token: false,
    post_proof_only: true,
    timestamp: '2026-05-19T13:00:00Z',
    description: 'Cognitive tree activation qualified — 34-tree pattern',
  },
]

export const MOCK_AUDIT: AuditEvent[] = [
  { event_id: 'a001', type: 'governance_check', description: 'Kernel status check', result: 'OK', timestamp: '2026-05-19T14:00:00Z' },
  { event_id: 'a002', type: 'context_read', description: 'Context packet built', result: 'OK', timestamp: '2026-05-19T14:00:01Z' },
  { event_id: 'a003', type: 'brody_response', description: 'Brody advisory response', result: 'OK', timestamp: '2026-05-19T14:00:02Z' },
  { event_id: 'a004', type: 'memory_candidate', description: 'Memory candidate captured', result: 'OK', timestamp: '2026-05-19T14:00:03Z' },
  { event_id: 'a005', type: 'world_call', description: 'Neo4j write attempt → BLOCKED', result: 'BLOCKED', timestamp: '2026-05-19T14:00:04Z' },
  { event_id: 'a006', type: 'gencoin_entry', description: 'Gencoin ledger entry (symbolic)', result: 'OK', timestamp: '2026-05-19T14:00:05Z' },
]

export const MEMORY_SOURCES = [
  { id: 'brody_runtime',    label: 'BRODY_RUNTIME',    active: true,  write_allowed: false },
  { id: 'graphiti_graph',   label: 'GRAPHITI_GRAPH',   active: true,  write_allowed: false },
  { id: 'feedback_capture', label: 'FEEDBACK_CAPTURE', active: true,  write_allowed: false },
  { id: 'context_packet',   label: 'CONTEXT_PACKET',   active: false, write_allowed: false },
]

export const NON_SOVEREIGNTY_BADGES = [
  { label: 'X-108 DECIDES',         color: 'kernel',  icon: '⚙' },
  { label: 'OS3 PROVES',            color: 'proof',   icon: '📜' },
  { label: 'BRODY ADVISORY',        color: 'brody',   icon: '💬' },
  { label: 'MEMORY CANDIDATE',      color: 'memory',  icon: '🗄' },
  { label: 'GRAPHITI READONLY',     color: 'memory',  icon: '🔍' },
  { label: 'GENCOIN POST-PROOF',    color: 'gencoin', icon: '🪙' },
  { label: 'WORLDACTION DRY-RUN',   color: 'pass',    icon: '🌐' },
]
