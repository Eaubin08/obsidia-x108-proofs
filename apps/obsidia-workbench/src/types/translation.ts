import type { DetectedLanguage } from '../lib/language'

export interface AlphabetUnit {
  symbol: string
  label: string
  role: 'INTENT' | 'ENTITY' | 'CONSTRAINT' | 'QUALIFIER' | 'UNKNOWN'
  confidence: number
  source_span: string
}

export interface IRCandidate {
  ir_id: string
  intent_type: string
  entities: string[]
  constraints: string[]
  unknowns: string[]
  risk_flags: string[]
  contradictions: string[]
  reversible: boolean
  irreversible: false
  action_candidate: boolean
  readonly: true
  allowed_to_decide: false
  allowed_to_act: false
  memory_write: false
  kernel_mutation: false
  decision_authority: 'X108_ONLY'
}

export interface TranslationTrace {
  trace_id: string
  user_input: string
  detected_language: DetectedLanguage
  response_language: DetectedLanguage
  os_trad_status: 'PARSED' | 'AMBIGUOUS' | 'BLOCKED' | 'MOCK'
  alphabet_units: AlphabetUnit[]
  ir_candidate: IRCandidate
  context_packet_id: string
  os_reverse_projection: string
  x108_boundary_status: 'READONLY' | 'BLOCKED' | 'PENDING'
  readonly: true
  allowed_to_decide: false
  allowed_to_act: false
  memory_write: false
  kernel_mutation: false
  source: 'LIVE' | 'MOCK' | 'STUB'
  mode: 'LIVE' | 'MOCK' | 'STUB'
}
