/**
 * Backend Truth Router — Enrichissement Réel
 * Récupère audit + enrichit depuis artefacts réels
 * Sigma + Attestation + RFC3161 + TLA si disponibles
 */

import { z } from "zod";
import { publicProcedure, router } from "../index";
import { getAuditLog } from "../../audit/auditLog";
import * as fs from "fs";
import * as path from "path";
import { execSync } from "child_process";

type VerificationStatus = "verified" | "incomplete" | "failed";

interface EnrichedTruth {
  decision_id: string;
  trace_id: string;
  ticket_id: string;
  domain: string;
  kernel_verdict: string;
  consensus_verdict: string;
  x108_gate: string;
  confidence: number;
  severity: string;
  reasons: string[];
  evidence_refs: any[];
  created_at: number;
  kernel_at: number;
  consensus_at: number;
  hash: string;
  prev_hash: string;
  
  // Enrichissements
  sigma?: {
    status: VerificationStatus;
    observation: string | null;
    confidence: number | null;
  };
  attestation?: {
    status: VerificationStatus;
    merkle_root: string | null;
    merkle_verified: boolean;
  };
  rfc3161?: {
    status: VerificationStatus;
    tsr_present: boolean;
    verified: boolean;
  };
  tla_export?: {
    status: VerificationStatus;
    trace_present: boolean;
    vars_present: boolean;
  };
  tla_verify?: {
    status: VerificationStatus;
    verified: boolean;
    tlc_available: boolean;
  };
}

function getArtifactPath(decision_id: string, artifactType: string): string {
  const baseDir = path.join(process.cwd(), "traces");
  
  switch (artifactType) {
    case "merkle":
      return path.join(baseDir, "attestation", `${decision_id}.merkle.json`);
    case "rfc3161":
      return path.join(baseDir, "attestation", `${decision_id}.tsr`);
    case "tla_trace":
      return path.join(baseDir, "tla", decision_id, "trace.json");
    case "tla_vars":
      return path.join(baseDir, "tla", decision_id, "vars.json");
    case "sigma":
      return path.join(baseDir, "sigma", `${decision_id}.sigma.json`);
    default:
      return "";
  }
}

function enrichSigma(decision_id: string): EnrichedTruth["sigma"] | undefined {
  const sigmaPath = getArtifactPath(decision_id, "sigma");
  
  if (!fs.existsSync(sigmaPath)) {
    return undefined;
  }
  
  try {
    const content = fs.readFileSync(sigmaPath, "utf-8");
    const sigma = JSON.parse(content);
    
    return {
      status: sigma.verified ? "verified" : "incomplete",
      observation: sigma.observation || null,
      confidence: sigma.confidence || null,
    };
  } catch {
    return {
      status: "failed",
      observation: null,
      confidence: null,
    };
  }
}

function enrichAttestation(decision_id: string): EnrichedTruth["attestation"] | undefined {
  const merklePath = getArtifactPath(decision_id, "merkle");
  
  if (!fs.existsSync(merklePath)) {
    return undefined;
  }
  
  try {
    const content = fs.readFileSync(merklePath, "utf-8");
    const merkle = JSON.parse(content);
    
    return {
      status: merkle.verified ? "verified" : "incomplete",
      merkle_root: merkle.merkle_root || null,
      merkle_verified: merkle.verified || false,
    };
  } catch {
    return {
      status: "failed",
      merkle_root: null,
      merkle_verified: false,
    };
  }
}

function enrichRFC3161(decision_id: string): EnrichedTruth["rfc3161"] | undefined {
  const tsrPath = getArtifactPath(decision_id, "rfc3161");
  
  if (!fs.existsSync(tsrPath)) {
    return undefined;
  }
  
  try {
    // Vérifier que le fichier TSR existe
    const tsr_present = fs.existsSync(tsrPath);
    
    // Essayer de vérifier avec openssl si disponible
    let verified = false;
    try {
      execSync(`openssl ts -verify -in ${tsrPath}`, { stdio: "pipe" });
      verified = true;
    } catch {
      verified = false;
    }
    
    return {
      status: verified ? "verified" : "incomplete",
      tsr_present,
      verified,
    };
  } catch {
    return {
      status: "failed",
      tsr_present: false,
      verified: false,
    };
  }
}

function enrichTLAExport(decision_id: string): EnrichedTruth["tla_export"] | undefined {
  const tracePath = getArtifactPath(decision_id, "tla_trace");
  const varsPath = getArtifactPath(decision_id, "tla_vars");
  
  const trace_present = fs.existsSync(tracePath);
  const vars_present = fs.existsSync(varsPath);
  
  if (!trace_present && !vars_present) {
    return undefined;
  }
  
  return {
    status: (trace_present && vars_present) ? "verified" : "incomplete",
    trace_present,
    vars_present,
  };
}

function enrichTLAVerify(decision_id: string): EnrichedTruth["tla_verify"] | undefined {
  const tracePath = getArtifactPath(decision_id, "tla_trace");
  const varsPath = getArtifactPath(decision_id, "tla_vars");
  
  if (!fs.existsSync(tracePath) || !fs.existsSync(varsPath)) {
    return undefined;
  }
  
  // Vérifier si TLC est disponible
  let tlc_available = false;
  try {
    execSync("tlc -version", { stdio: "pipe" });
    tlc_available = true;
  } catch {
    tlc_available = false;
  }
  
  return {
    status: tlc_available ? "verified" : "incomplete",
    verified: tlc_available,
    tlc_available,
  };
}

export const truthRouter = router({
  byDecision: publicProcedure
    .input(z.object({ decision_id: z.string() }))
    .query(({ input }): { found: boolean; truth: EnrichedTruth | null } => {
      const auditLog = getAuditLog();
      const entry = auditLog.getByDecisionId(input.decision_id);
      
      if (!entry) {
        return {
          found: false,
          truth: null,
        };
      }
      
      // Construire la vérité enrichie
      const enrichedTruth: EnrichedTruth = {
        decision_id: entry.decision_id,
        trace_id: entry.trace_id,
        ticket_id: entry.ticket_id,
        domain: entry.domain,
        kernel_verdict: entry.kernel_verdict,
        consensus_verdict: entry.consensus_verdict,
        x108_gate: entry.x108_gate,
        confidence: entry.confidence,
        severity: entry.severity,
        reasons: entry.reasons,
        evidence_refs: entry.evidence_refs,
        created_at: entry.created_at,
        kernel_at: entry.kernel_at,
        consensus_at: entry.consensus_at,
        hash: entry.hash,
        prev_hash: entry.prev_hash,
      };
      
      // Enrichir depuis les artefacts réels si présents
      const sigma = enrichSigma(input.decision_id);
      if (sigma) enrichedTruth.sigma = sigma;
      
      const attestation = enrichAttestation(input.decision_id);
      if (attestation) enrichedTruth.attestation = attestation;
      
      const rfc3161 = enrichRFC3161(input.decision_id);
      if (rfc3161) enrichedTruth.rfc3161 = rfc3161;
      
      const tla_export = enrichTLAExport(input.decision_id);
      if (tla_export) enrichedTruth.tla_export = tla_export;
      
      const tla_verify = enrichTLAVerify(input.decision_id);
      if (tla_verify) enrichedTruth.tla_verify = tla_verify;
      
      return {
        found: true,
        truth: enrichedTruth,
      };
    }),
});
