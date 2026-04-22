/**
 * Canonical Envelope — Contrat de l'enveloppe canonique backend
 * 
 * Aligné avec Python contracts.py CanonicalDecisionEnvelope
 * Utilisé par le flux d'orchestration réel
 */

export interface CanonicalEnvelope {
  // IDs uniques
  decision_id: string;
  trace_id: string;
  ticket_id: string | null;
  
  // Domaine et mode
  domain: "trading" | "bank" | "ecom";
  mode: "live" | "simu" | "fallback" | "demo";
  
  // Entrée
  input_ref: string;
  
  // Verdicts
  kernel_verdict: "ALLOW" | "HOLD" | "BLOCK";
  consensus_verdict: "ALLOW" | "HOLD" | "BLOCK";
  x108_gate: "ALLOW" | "HOLD" | "BLOCK";
  
  // Métriques X108
  x108: {
    elapsed: number;
    tau: number;
    irr: number | boolean | null;
  };
  
  // Raisons et références
  reason_code: string;
  reasons: string[];
  theorem_refs: string[];
  evidence_refs: string[];
  
  // Confiance et sévérité
  confidence: number;
  severity: "S0" | "S1" | "S2" | "S3" | "S4";
  
  // Observations
  contradictions: string[];
  unknowns: string[];
  risk_flags: string[];
  
  // Sigma observation (optionnel — rempli par adapter)
  sigma?: {
    stability: "stable" | "unstable" | "unknown";
    metrics: Record<string, number>;
    alerts: string[];
    confidence: number;
  };
  
  // Attestation Merkle (optionnel — rempli par adapter)
  attestation?: {
    attestation_id: string;
    merkle_root: string | null;
    seal: string | null;
    verified: boolean;
  };
  
  // RFC3161 (optionnel — rempli par adapter)
  rfc3161?: {
    token: string | null;
    timestamp: number | null;
    verified: boolean;
  };
  
  // Timestamps (REQUIS — créé par pipeline, enrichi par orchestrateur)
  timestamps: {
    created_at: number;
    kernel_at: number;
    consensus_at: number;
    sigma_at?: number;
    attestation_at?: number;
    rfc3161_at?: number;
  };
  
  // Source et métadonnées
  source?: "canonical_framework" | "canonical_fallback";
  metadata?: Record<string, unknown>;
  
  // Python pipeline status
  python_available?: boolean;
}

export function validateCanonicalEnvelope(envelope: CanonicalEnvelope): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];
  
  if (!envelope.decision_id) errors.push("decision_id is required");
  if (!envelope.trace_id) errors.push("trace_id is required");
  if (!["ALLOW", "HOLD", "BLOCK"].includes(envelope.kernel_verdict)) {
    errors.push("Invalid kernel_verdict");
  }
  if (envelope.confidence < 0 || envelope.confidence > 1) {
    errors.push("confidence must be between 0 and 1");
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
}
