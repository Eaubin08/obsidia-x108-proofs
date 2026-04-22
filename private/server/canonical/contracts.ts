export type Domain = "bank" | "trading" | "ecom";
export type X108Gate = "ALLOW" | "HOLD" | "BLOCK";
export type Severity = "S0" | "S1" | "S2" | "S3" | "S4";

export interface CanonicalDecisionEnvelope {
  domain: Domain;
  market_verdict: string;
  x108_gate: X108Gate;
  reason_code: string;
  violation_code?: string | null;
  severity: Severity;
  decision_id: string;
  trace_id: string;
  ticket_required: boolean;
  ticket_id?: string | null;
  attestation_ref?: string | null;
  metrics: Record<string, unknown>;
  raw_engine?: Record<string, unknown> | null;
}
