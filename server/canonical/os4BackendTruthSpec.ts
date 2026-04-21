/**
 * OS4 Backend Truth Spec — Vérité backend unique pour OS4
 * 
 * Définit la réponse backend finale exploitable par le frontend OS4.
 * Une seule source de vérité pour chaque décision.
 */

import { CanonicalEnvelope } from "./canonicalEnvelope";
import { AuditLogEntry } from "../audit/auditLog";
import { SigmaRealObservation } from "../adapters/sigmaRealAdapter";
import { MerkleRealAttestation } from "../adapters/merkleRealAdapter";
import { RFC3161Token } from "../adapters/rfc3161RealAdapter";

export interface OS4BackendTruth {
  // Identifiants
  decision_id: string;
  trace_id: string;
  ticket_id: string | null;
  
  // Verdict final (source de vérité unique)
  verdict: "ALLOW" | "HOLD" | "BLOCK";
  confidence: number;
  severity: "S0" | "S1" | "S2" | "S3" | "S4";
  
  // Domaine et contexte
  domain: "trading" | "bank" | "ecom";
  mode: "live" | "simu" | "fallback" | "demo";
  
  // Raisons et preuves
  reasons: string[];
  theorem_refs: string[];
  evidence_refs: string[];
  
  // Observations (Sigma)
  sigma?: {
    stability: "stable" | "unstable" | "unknown";
    alerts: string[];
    confidence: number | null;
  };
  
  // Attestation (Merkle)
  attestation?: {
    merkle_root: string | null;
    seal: string | null;
    verified: boolean;
  };
  
  // RFC3161
  rfc3161?: {
    token: string | null;
    timestamp: number | null;
    verified: boolean;
  };
  
  // Timestamps
  created_at: number;
  kernel_at: number;
  consensus_at: number;
  
  // Audit log entry
  audit_entry?: AuditLogEntry;
  
  // Métadonnées
  source: "canonical_framework" | "canonical_fallback";
  metadata: Record<string, unknown>;
}

/**
 * Construit la vérité backend unique depuis les composants
 */
export function buildOS4BackendTruth(
  envelope: CanonicalEnvelope,
  auditEntry: AuditLogEntry,
  sigma?: SigmaRealObservation,
  attestation?: MerkleRealAttestation,
  rfc3161?: RFC3161Token
): OS4BackendTruth {
  return {
    decision_id: envelope.decision_id,
    trace_id: envelope.trace_id,
    ticket_id: envelope.ticket_id,
    
    // Verdict final unique
    verdict: envelope.x108_gate,
    confidence: envelope.confidence,
    severity: envelope.severity,
    
    domain: envelope.domain,
    mode: envelope.mode,
    
    reasons: envelope.reasons,
    theorem_refs: envelope.theorem_refs,
    evidence_refs: envelope.evidence_refs,
    
    sigma: sigma ? {
      stability: sigma.stability,
      alerts: sigma.alerts,
      confidence: sigma.confidence || null,
    } : undefined,
    
    attestation: attestation ? {
      merkle_root: attestation.merkle_root || null,
      seal: attestation.seal || null,
      verified: attestation.verified,
    } : undefined,
    
    rfc3161: rfc3161 ? {
      token: rfc3161.token,
      timestamp: rfc3161.timestamp,
      verified: rfc3161.verified,
    } : undefined,
    
    created_at: envelope.timestamps.created_at,
    kernel_at: envelope.timestamps.kernel_at,
    consensus_at: envelope.timestamps.consensus_at,
    
    audit_entry: auditEntry,
    
    source: envelope.source || "canonical_framework",
    metadata: envelope.metadata || {},
  };
}

/**
 * Valide la vérité backend
 */
export function validateOS4BackendTruth(truth: OS4BackendTruth): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];
  
  if (!truth.decision_id) errors.push("decision_id is required");
  if (!truth.trace_id) errors.push("trace_id is required");
  if (!["ALLOW", "HOLD", "BLOCK"].includes(truth.verdict)) {
    errors.push("Invalid verdict");
  }
  if (truth.confidence < 0 || truth.confidence > 1) {
    errors.push("confidence must be between 0 and 1");
  }
  if (!truth.created_at) errors.push("created_at is required");
  
  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Pages OS4 à recâbler avec cette vérité backend
 */
export const OS4_PAGES_TO_RECABLE = [
  {
    page: "decisions_list",
    needs: ["decision_id", "verdict", "confidence", "severity", "created_at"],
    endpoint: "/api/trpc/os4.decisions.list",
  },
  {
    page: "decision_detail",
    needs: ["full OS4BackendTruth"],
    endpoint: "/api/trpc/os4.decisions.detail",
  },
  {
    page: "audit_log",
    needs: ["audit_entry"],
    endpoint: "/api/trpc/os4.audit.list",
  },
  {
    page: "sigma_observations",
    needs: ["sigma"],
    endpoint: "/api/trpc/os4.sigma.observations",
  },
  {
    page: "attestations",
    needs: ["attestation", "rfc3161"],
    endpoint: "/api/trpc/os4.attestations.list",
  },
  {
    page: "backend_truth",
    needs: ["full OS4BackendTruth"],
    endpoint: "/api/trpc/os4.backend.truth",
  },
];
