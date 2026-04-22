/**
 * ID Factory — Génération d'IDs uniques et déterministes
 * 
 * Utilisé par le pipeline réel pour générer :
 * - decision_id : identifiant unique de la décision
 * - trace_id : identifiant unique de la trace d'exécution
 * - ticket_id : identifiant du ticket si ticket_required
 */

import crypto from "crypto";

export interface IDFactoryConfig {
  domain: "trading" | "bank" | "ecom" | "meta";
  timestamp: number;
  stateHash: string;
}

/**
 * Génère un decision_id unique et déterministe
 * Format : {domain}-{timestamp}-{hash}
 */
export function generateDecisionId(config: IDFactoryConfig): string {
  const { domain, timestamp, stateHash } = config;
  const hash = crypto
    .createHash("sha256")
    .update(`${domain}:${timestamp}:${stateHash}`)
    .digest("hex")
    .substring(0, 12);
  
  return `${domain}-${timestamp}-${hash}`;
}

/**
 * Génère un trace_id unique (UUID-like)
 * Format : {timestamp}-{random}
 */
export function generateTraceId(): string {
  const timestamp = Date.now();
  const random = crypto.randomBytes(8).toString("hex");
  return `${timestamp}-${random}`;
}

/**
 * Génère un ticket_id unique (16 chars hex)
 * Utilisé si ticket_required = true
 */
export function generateTicketId(): string {
  return crypto.randomBytes(8).toString("hex");
}

/**
 * Calcule le hash d'un état pour la génération d'IDs déterministes
 */
export function hashState(state: Record<string, unknown>): string {
  const json = JSON.stringify(state, Object.keys(state).sort());
  return crypto.createHash("sha256").update(json).digest("hex");
}

/**
 * Génère tous les IDs pour une décision
 */
export function generateDecisionIds(
  domain: "trading" | "bank" | "ecom" | "meta",
  state: Record<string, unknown>,
  ticketRequired: boolean
): {
  decision_id: string;
  trace_id: string;
  ticket_id: string | null;
} {
  const timestamp = Date.now();
  const stateHash = hashState(state);
  
  return {
    decision_id: generateDecisionId({ domain, timestamp, stateHash }),
    trace_id: generateTraceId(),
    ticket_id: ticketRequired ? generateTicketId() : null,
  };
}

/**
 * Valide que les IDs sont bien formés
 */
export function validateIds(ids: {
  decision_id: string;
  trace_id: string;
  ticket_id: string | null;
}): { valid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  // decision_id : {domain}-{timestamp}-{hash}
  if (!ids.decision_id.match(/^(trading|bank|ecom|meta)-\d+-[a-f0-9]{12}$/)) {
    errors.push(`Invalid decision_id format: ${ids.decision_id}`);
  }
  
  // trace_id : {timestamp}-{random}
  if (!ids.trace_id.match(/^\d+-[a-f0-9]{16}$/)) {
    errors.push(`Invalid trace_id format: ${ids.trace_id}`);
  }
  
  // ticket_id : null ou 16 chars hex
  if (ids.ticket_id !== null && !ids.ticket_id.match(/^[a-f0-9]{16}$/)) {
    errors.push(`Invalid ticket_id format: ${ids.ticket_id}`);
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
}
