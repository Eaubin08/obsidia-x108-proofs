import type { IRCandidate } from '../types/translation'
import type { DetectedLanguage } from './language'

const FR: Record<string, string> = {
  authority_escalation_request:
    "Je lis une demande d'autorisation ou d'escalade. Brody ne peut pas émettre d'ACT, de HOLD ou de BLOCK. L'autorité de décision est exclusivement X-108. Je peux structurer cette intention en IRCandidate pour passage contrôlé via SovereignTicket.",
  action_execution_request:
    "Je détecte une intention d'exécution. Cette action ne peut pas être initiée depuis Brody. Je peux préparer un ActionCandidate et un ContextPacket pour soumission à X-108.",
  permission_request:
    "Une demande de permission est détectée. Brody ne peut pas l'accorder — la décision appartient à X-108. Je peux documenter l'intention dans un ContextPacket.",
  decision_delegation_request:
    "Je ne peux pas prendre cette décision — c'est le périmètre exclusif de X-108. Je peux analyser l'intention et préparer un signal consultatif.",
  creation_request:
    "Une demande de création est détectée. Brody est readonly — aucune création directe. Je peux préparer une proposition structurée pour X-108.",
  write_request:
    "Une écriture est demandée. Brody n'écrit pas en mémoire — aucune mutation possible. Je peux générer un candidat mémoire pour révision humaine.",
  deletion_request:
    "Une suppression est demandée. Brody ne peut pas supprimer — aucune action irréversible depuis ce niveau.",
  general_action_request:
    "Je détecte une intention d'action. Sans ticket X-108 valide, aucune action réelle ne peut être exécutée. Je peux préparer le contexte.",
  general_query:
    "Je lis ta demande dans le contexte Obsidia. Je peux analyser, structurer, contextualiser — mais je ne décide pas. Dis-moi ce que tu cherches à comprendre ou à préparer.",
}

const EN: Record<string, string> = {
  authority_escalation_request:
    "I read an authorization or escalation request. Brody cannot emit ACT, HOLD, or BLOCK. Decision authority is exclusively X-108. I can structure this intent as an IRCandidate for controlled passage via SovereignTicket.",
  action_execution_request:
    "I detect an execution intent. This action cannot be initiated from Brody. I can prepare an ActionCandidate and ContextPacket for submission to X-108.",
  permission_request:
    "A permission request is detected. Brody cannot grant it — the decision belongs to X-108. I can document the intent in a ContextPacket.",
  decision_delegation_request:
    "I cannot make this decision — it is the exclusive scope of X-108. I can analyze the intent and prepare an advisory signal.",
  creation_request:
    "A creation request is detected. Brody is readonly — no direct creation. I can prepare a structured proposal for X-108.",
  write_request:
    "A write is requested. Brody does not write to memory — no mutation possible. I can generate a memory candidate for human review.",
  deletion_request:
    "A deletion is requested. Brody cannot delete — no irreversible action from this layer.",
  general_action_request:
    "I detect an action intent. Without a valid X-108 ticket, no real action can be executed. I can prepare the context.",
  general_query:
    "I read your request in the Obsidia context. I can analyze, structure, contextualize — but I do not decide. Tell me what you want to understand or prepare.",
}

export function buildOSReverseProjection(
  ir: IRCandidate,
  language: DetectedLanguage,
): string {
  const pool = language === 'en' ? EN : FR
  return pool[ir.intent_type] ?? pool['general_query']
}
