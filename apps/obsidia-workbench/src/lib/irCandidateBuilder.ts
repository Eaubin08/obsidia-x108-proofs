import type { IRCandidate, AlphabetUnit } from '../types/translation'

const INTENT_MAP: Record<string, string> = {
  autorise: 'authority_escalation_request',
  autoriser: 'authority_escalation_request',
  autorisez: 'authority_escalation_request',
  authorize: 'authority_escalation_request',
  execute: 'action_execution_request',
  executer: 'action_execution_request',
  run: 'action_execution_request',
  lancer: 'action_execution_request',
  start: 'action_execution_request',
  allow: 'permission_request',
  permit: 'permission_request',
  permets: 'permission_request',
  décide: 'decision_delegation_request',
  décider: 'decision_delegation_request',
  decide: 'decision_delegation_request',
  créer: 'creation_request',
  create: 'creation_request',
  write: 'write_request',
  écrire: 'write_request',
  delete: 'deletion_request',
  supprimer: 'deletion_request',
  faire: 'general_action_request',
  fais: 'general_action_request',
  do: 'general_action_request',
  go: 'general_action_request',
  fonce: 'general_action_request',
  agis: 'general_action_request',
}

export function buildIRCandidate(text: string, alphabetUnits: AlphabetUnit[]): IRCandidate {
  const t = text.toLowerCase()
  const intentUnits = alphabetUnits.filter(u => u.role === 'INTENT')
  const entityUnits = alphabetUnits.filter(u => u.role === 'ENTITY')
  const unknownUnits = alphabetUnits.filter(u => u.role === 'UNKNOWN')

  const riskFlags: string[] = []
  const contradictions: string[] = []

  if (/\b(autorise[rz]?|authorize?|allow|permit|permets?)\b/i.test(t)) {
    riskFlags.push('AUTHORITY_ESCALATION')
  }
  if (/\b(execute?r?|run|lancer|start|fonce|agis)\b/i.test(t)) {
    riskFlags.push('ACTION_REQUEST')
  }
  if (/\b(write|écrire|modify|modifier|create?r?|créer?|delete|supprimer)\b/i.test(t)) {
    riskFlags.push('WRITE_REQUEST')
  }
  if (/\b(créateur|creator|je t'ai|i made you|i built you|i am your)\b/i.test(t)) {
    riskFlags.push('AUTHORITY_CLAIM')
  }
  if (/\b(act\b|acte)\b/i.test(t) && !/readonly|lecture/i.test(t)) {
    riskFlags.push('ACT_TOKEN_DETECTED')
  }
  if (
    /\b(gencoin|token|wallet|blockchain|chain)\b/i.test(t) &&
    /\b(send|envoyer|transfer|transférer|buy|acheter|sell|vendre|mint)\b/i.test(t)
  ) {
    riskFlags.push('CHAIN_ACTION_ATTEMPT')
  }

  if (riskFlags.includes('AUTHORITY_ESCALATION') || riskFlags.includes('AUTHORITY_CLAIM')) {
    contradictions.push('BRODY_CANNOT_AUTHORIZE_ACT')
    contradictions.push('DECISION_AUTHORITY_IS_X108_ONLY')
  }
  if (riskFlags.includes('WRITE_REQUEST')) {
    contradictions.push('MEMORY_WRITE_FORBIDDEN_BRODY_READONLY')
  }
  if (riskFlags.includes('ACT_TOKEN_DETECTED')) {
    contradictions.push('EMITS_ACT_FALSE')
  }
  if (riskFlags.includes('CHAIN_ACTION_ATTEMPT')) {
    contradictions.push('NO_REAL_CHAIN_ACTION_FROM_BRODY')
  }

  const firstIntent = intentUnits[0]?.label.toLowerCase()
  const intentType: string = (firstIntent && INTENT_MAP[firstIntent])
    ? INTENT_MAP[firstIntent]
    : riskFlags.length > 0
    ? 'authority_escalation_request'
    : 'general_query'

  return {
    ir_id: `ir_${Date.now().toString(36)}`,
    intent_type: intentType,
    entities: entityUnits.map(u => u.label),
    constraints: alphabetUnits.filter(u => u.role === 'CONSTRAINT').map(u => u.label),
    unknowns: unknownUnits.map(u => u.label),
    risk_flags: riskFlags,
    contradictions,
    reversible: !riskFlags.includes('ACTION_REQUEST') && !riskFlags.includes('WRITE_REQUEST'),
    irreversible: false,
    action_candidate: riskFlags.length > 0,
    readonly: true,
    allowed_to_decide: false,
    allowed_to_act: false,
    memory_write: false,
    kernel_mutation: false,
    decision_authority: 'X108_ONLY',
  }
}
