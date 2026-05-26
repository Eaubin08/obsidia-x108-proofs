import type { TranslationTrace } from '../types/translation'
import type { DetectedLanguage } from './language'
import { detectUserLanguage } from './language'
import { buildAlphabetUnits } from './symbolicAlphabet'
import { buildIRCandidate } from './irCandidateBuilder'
import { buildOSReverseProjection } from './osReverseProjection'

function traceId(): string {
  return `tr_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 5)}`
}

function packetId(): string {
  return `cp_${Date.now().toString(36)}`
}

export function runOSTradPipeline(
  userInput: string,
  sessionLanguage: DetectedLanguage = 'fr',
): TranslationTrace {
  const detectedLanguage = detectUserLanguage(userInput)
  const responseLang: DetectedLanguage =
    detectedLanguage === 'unknown' || detectedLanguage === 'mixed'
      ? sessionLanguage
      : detectedLanguage

  const alphabetUnits = buildAlphabetUnits(userInput)
  const irCandidate   = buildIRCandidate(userInput, alphabetUnits)
  const reverseProj   = buildOSReverseProjection(irCandidate, responseLang)

  const hasForbidden =
    irCandidate.risk_flags.length > 0 &&
    (irCandidate.risk_flags.includes('AUTHORITY_ESCALATION') ||
      irCandidate.risk_flags.includes('ACT_TOKEN_DETECTED'))

  return {
    trace_id:            traceId(),
    user_input:          userInput,
    detected_language:   detectedLanguage,
    response_language:   responseLang,
    os_trad_status:      hasForbidden ? 'BLOCKED' : 'PARSED',
    alphabet_units:      alphabetUnits,
    ir_candidate:        irCandidate,
    context_packet_id:   packetId(),
    os_reverse_projection: reverseProj,
    x108_boundary_status: 'READONLY',
    readonly:            true,
    allowed_to_decide:   false,
    allowed_to_act:      false,
    memory_write:        false,
    kernel_mutation:     false,
    source:              'MOCK',
    mode:                'MOCK',
  }
}
