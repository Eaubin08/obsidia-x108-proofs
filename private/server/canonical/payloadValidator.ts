import type { CanonicalDecisionEnvelope } from "./contracts";

const REQUIRED_FIELDS: (keyof CanonicalDecisionEnvelope)[] = [
  "domain","market_verdict","x108_gate","reason_code","severity","decision_id","trace_id","ticket_required","metrics"
];

export function validateCanonicalEnvelope(payload: Record<string, unknown>) {
  const missing = REQUIRED_FIELDS.filter((k) => !(k in payload));
  return { ok: missing.length === 0, missing };
}
