/*
 * Orchestrator Real — Patch cible
 * Flux réel minimal :
 * pipeline -> audit -> sigma -> merkle -> rfc -> tla export -> output
 */

import fs from "fs";
import os from "os";
import path from "path";
import { spawnSync } from "child_process";

import { runCanonicalPipeline, CanonicalEnvelope, DomainState } from "../canonical/canonicalPipeline";
import { getAuditLog, AuditLogEntry } from "../audit/auditLog";
import { callRealSigma, SigmaRealObservation } from "../adapters/sigmaRealAdapter";
import { callRealMerkleVerify, callRealVerifyAll, MerkleRealAttestation } from "../adapters/merkleRealAdapter";
import { callRealRFC3161TSA, RFC3161Token } from "../adapters/rfc3161RealAdapter";
import { generateDecisionIds } from "../canonical/idFactory";
import { defaultTradingState, defaultBankState, defaultEcomState } from "../canonical/canonicalPipeline";

export { defaultTradingState, defaultBankState, defaultEcomState };

export interface OrchestrationRealOutput {
  success: boolean;
  envelope?: CanonicalEnvelope;
  audit_entry?: AuditLogEntry;
  sigma?: SigmaRealObservation;
  attestation?: MerkleRealAttestation;
  rfc3161?: RFC3161Token | null;
  tla_export?: Record<string, unknown> | null;
  verify_all?: {
    success: boolean;
    output: string;
    errors: string[];
  };
  timestamps?: {
    started_at: number;
    pipeline_at: number;
    audit_at: number;
    sigma_at: number;
    merkle_at: number;
    rfc3161_at?: number;
    tla_at?: number;
    completed_at: number;
  };
  errors: string[];
  warnings?: string[];
}

export interface OrchestrationRealInput {
  domain: "trading" | "bank" | "ecom";
  state: DomainState;
}

export function orchestrateReal(
  input: OrchestrationRealInput | "trading" | "bank" | "ecom",
  state?: DomainState
): OrchestrationRealOutput {
  let domain: "trading" | "bank" | "ecom";
  let domainState: DomainState;

  if (typeof input === "object" && "domain" in input) {
    domain = input.domain;
    domainState = input.state;
  } else {
    domain = input;
    if (!state) {
      return { success: false, errors: ["state is required"] };
    }
    domainState = state;
  }

  const startedAt = Date.now();
  const errors: string[] = [];
  const warnings: string[] = [];

  try {
    // 1) Pipeline réel
    const rawEnvelope = runCanonicalPipeline(domain, domainState);
    const pipelineAt = Date.now();

    // 2) IDs : on garde ceux du pipeline s'ils existent, sinon on les complète
    const ids = (!rawEnvelope.decision_id || !rawEnvelope.trace_id)
      ? generateDecisionIds(domain, domainState as unknown as Record<string, unknown>, false)
      : null;

    const kernelVerdict = extractKernelVerdict(rawEnvelope);
    const consensusVerdict = extractConsensusVerdict(rawEnvelope);
    const x108 = extractX108(rawEnvelope);

    const reasons = extractReasons(rawEnvelope);
    const theoremRefs = extractTheoremRefs(rawEnvelope);
    const evidenceRefs = [...(rawEnvelope.evidence_refs ?? [])];

    const envelope: CanonicalEnvelope = {
      ...rawEnvelope,
      decision_id: rawEnvelope.decision_id || ids!.decision_id,
      trace_id: rawEnvelope.trace_id || ids!.trace_id,
      ticket_id: rawEnvelope.ticket_id ?? (ids ? ids.ticket_id : null),

      kernel_verdict: kernelVerdict as "ALLOW" | "HOLD" | "BLOCK" | undefined,
      consensus_verdict: consensusVerdict as "ALLOW" | "HOLD" | "BLOCK" | undefined,
      x108_gate: rawEnvelope.x108_gate ?? consensusVerdict,

      x108: {
        elapsed: x108.elapsed,
        tau: x108.tau,
        irr: x108.irr,
      },

      reasons,
      theorem_refs: theoremRefs,
      evidence_refs: evidenceRefs,

      timestamps: rawEnvelope.timestamps || {
        created_at: startedAt,
        kernel_at: pipelineAt,
        consensus_at: pipelineAt,
      },
    };

    if (!rawEnvelope.python_available) {
      warnings.push("python pipeline unavailable or degraded");
    }

    // 3) Audit log réel
    const auditLog = getAuditLog();
    const auditEntry = auditLog.append(
      envelope.decision_id,
      envelope.trace_id,
      envelope.ticket_id,
      domain,
      envelope.kernel_verdict || "HOLD",
      envelope.consensus_verdict || "HOLD",
      envelope.x108_gate,
      envelope.confidence,
      envelope.severity,
      envelope.reasons || [],
      envelope.evidence_refs || [],
      envelope.timestamps!.created_at,
      envelope.timestamps!.kernel_at,
      envelope.timestamps!.consensus_at
    );
    const auditAt = Date.now();
    envelope.evidence_refs = [...envelope.evidence_refs, `audit:${auditEntry.hash}`];

    // 4) Sigma réel avec enveloppe complète (pas heuristiques locales)
    const sigma = callRealSigma(envelope);
    const sigmaAt = Date.now();
    envelope.sigma = sigma;
    if (envelope.timestamps) envelope.timestamps.sigma_at = sigmaAt;

    // 5) Merkle / verify_all réels
    const attestation = callRealMerkleVerify(envelope.decision_id);
    const verifyAll = callRealVerifyAll();
    const merkleAt = Date.now();

    envelope.attestation = {
      attestation_id: attestation.attestation_id,
      merkle_root: attestation.merkle_root,
      seal: attestation.seal,
      verified: attestation.verified,
    };
    if (envelope.timestamps) envelope.timestamps.attestation_at = merkleAt;

    if (attestation.merkle_root && attestation.status === "verified") {
      envelope.evidence_refs.push(`merkle:${attestation.merkle_root}`);
    } else if (attestation.status === "incomplete") {
      warnings.push("merkle root incomplete: no real artefact");
    } else if (attestation.status === "failed") {
      warnings.push("merkle root failed");
    }

    // 6) RFC3161 honnête
    let rfc3161: RFC3161Token | null = null;
    if (attestation.merkle_root && attestation.status === "verified") {
      rfc3161 = callRealRFC3161TSA(envelope.decision_id, attestation.merkle_root);
      envelope.rfc3161 = {
        token: rfc3161?.token ?? null,
        timestamp: rfc3161?.timestamp ?? null,
        verified: rfc3161?.verified ?? false,
        status: rfc3161?.status ?? "incomplete",
      };
      if (envelope.timestamps) envelope.timestamps.rfc3161_at = Date.now();

      if (rfc3161 && rfc3161.status !== "verified") {
        warnings.push(`rfc3161 status=${rfc3161.status}`);
      }
    } else {
      warnings.push("rfc3161 skipped: no real merkle root");
    }
    const rfc3161At = Date.now();

    // 7) Export TLA réel depuis l'enveloppe
    const tlaExport = exportTLAFromEnvelope(envelope);
    const tlaAt = Date.now();

    // Ajouter TLA evidence_refs si export réussi
    if (tlaExport && typeof tlaExport === "object" && "status" in tlaExport && tlaExport.status === "exported") {
      if ("output_trace_path" in tlaExport && tlaExport.output_trace_path) {
        envelope.evidence_refs.push(`tla:${tlaExport.output_trace_path}`);
      }
      if ("vars_path" in tlaExport && tlaExport.vars_path) {
        envelope.evidence_refs.push(`tla_vars:${tlaExport.vars_path}`);
      }
    }

    return {
      success: errors.length === 0,
      envelope,
      audit_entry: auditEntry,
      sigma,
      attestation,
      rfc3161,
      tla_export: tlaExport,
      verify_all: verifyAll,
      timestamps: {
        started_at: startedAt,
        pipeline_at: pipelineAt,
        audit_at: auditAt,
        sigma_at: sigmaAt,
        merkle_at: merkleAt,
        rfc3161_at: rfc3161At,
        tla_at: tlaAt,
        completed_at: Date.now(),
      },
      errors,
      warnings,
    };
  } catch (err) {
    errors.push(err instanceof Error ? err.message : String(err));
    return { success: false, errors };
  }
}

// ============================================================================
// Script resolution
// ============================================================================

function resolveExportTLAScript(): string | null {
  // Détection dynamique principale
  const candidates = [
    path.join(process.cwd(), "server", "python_agents", "export_tla.py"),
    path.join(__dirname, "..", "python_agents", "export_tla.py"),
  ];

  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }

  // Fallback secondaire seulement
  const fallback = path.join("/home/ubuntu/obsidia-engine-proof-core", "agents", "export_tla.py");
  if (fs.existsSync(fallback)) {
    return fallback;
  }

  return null;
}

// ============================================================================
// Extraction helpers
// ============================================================================

function extractKernelVerdict(envelope: CanonicalEnvelope): string {
  return envelope.kernel_verdict || envelope.x108_gate || "HOLD";
}

function extractConsensusVerdict(envelope: CanonicalEnvelope): string {
  return envelope.consensus_verdict || envelope.x108_gate || "HOLD";
}

function extractX108(envelope: CanonicalEnvelope): { elapsed: number; tau: number; irr: number | boolean | null } {
  const x108 = envelope.x108 || { elapsed: 0, tau: 0, irr: null };
  return {
    elapsed: x108?.elapsed ?? 0,
    tau: x108?.tau ?? 0,
    irr: (x108?.irr ?? null) as number | boolean | null,
  };
}

function extractReasons(envelope: CanonicalEnvelope): string[] {
  if (envelope.reasons && Array.isArray(envelope.reasons)) {
    return envelope.reasons;
  }
  if (envelope.reason_code) {
    return [envelope.reason_code];
  }
  return [];
}

function extractTheoremRefs(envelope: CanonicalEnvelope): string[] {
  return envelope.theorem_refs || [];
}

// ============================================================================
// TLA Export
// ============================================================================

function exportTLAFromEnvelope(envelope: CanonicalEnvelope): Record<string, unknown> | null {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "obsidia-tla-"));
  const inputPath = path.join(tmpDir, `${envelope.decision_id}.json`);
  const outputTracePath = path.join(tmpDir, `tla_trace_${envelope.decision_id}.json`);

  fs.writeFileSync(inputPath, JSON.stringify(envelope, null, 2), "utf-8");

  const scriptPath = resolveExportTLAScript();
  if (!scriptPath) {
    return {
      status: "incomplete",
      reason: "export_tla.py not found",
      input_path: inputPath,
      output_trace_path: outputTracePath,
      tla_targets: ["X108.tla", "DistributedX108.tla"],
    };
  }

  const res = spawnSync("python3", [scriptPath, inputPath, outputTracePath], {
    encoding: "utf-8",
    maxBuffer: 10 * 1024 * 1024,
    timeout: 5000,
  });

  const varsPath = outputTracePath.replace(/\.json$/, "_vars.json");

  if (res.status !== 0) {
    return {
      status: "failed",
      reason: res.stderr || "export_tla.py failed",
      input_path: inputPath,
      output_trace_path: outputTracePath,
      vars_path: varsPath,
      stdout: res.stdout ?? "",
      stderr: res.stderr ?? "",
      tla_targets: ["X108.tla", "DistributedX108.tla"],
    };
  }

  let trace = null;
  let vars = null;

  if (fs.existsSync(outputTracePath)) {
    trace = JSON.parse(fs.readFileSync(outputTracePath, "utf-8"));
  }
  if (fs.existsSync(varsPath)) {
    vars = JSON.parse(fs.readFileSync(varsPath, "utf-8"));
  }

  return {
    status: "exported",
    input_path: inputPath,
    output_trace_path: outputTracePath,
    vars_path: varsPath,
    trace,
    vars,
    tla_targets: ["X108.tla", "DistributedX108.tla"],
    stdout: res.stdout ?? "",
    stderr: res.stderr ?? "",
  };
}

// ============================================================================
// Validation
// ============================================================================

export function validateOrchestrationFlow(output: OrchestrationRealOutput): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  // 1) Envelope
  if (!output.envelope) {
    errors.push("envelope is missing");
    return { valid: false, errors };
  }
  const envelope = output.envelope;

  if (!envelope.decision_id) errors.push("envelope.decision_id is missing");
  if (!envelope.trace_id) errors.push("envelope.trace_id is missing");
  if (!envelope.kernel_verdict) errors.push("envelope.kernel_verdict is missing");
  if (!envelope.consensus_verdict) errors.push("envelope.consensus_verdict is missing");

  // 2) Audit entry
  if (!output.audit_entry) {
    errors.push("audit_entry is missing");
  } else {
    if (!output.audit_entry.hash) errors.push("audit_entry.hash is missing");
    if (!output.audit_entry.prev_hash) errors.push("audit_entry.prev_hash is missing");
  }

  // 3) Sigma non-décisionnel
  if (!output.sigma) {
    errors.push("sigma is missing");
  } else {
    if ("kernel_verdict" in output.sigma) errors.push("sigma should not contain kernel_verdict");
    if ("consensus_verdict" in output.sigma) errors.push("sigma should not contain consensus_verdict");
    if ("x108_gate" in output.sigma) errors.push("sigma should not contain x108_gate");
  }

  // 4) Attestation structurée
  if (!output.attestation) {
    errors.push("attestation is missing");
  } else {
    if (!output.attestation.attestation_id) errors.push("attestation.attestation_id is missing");
    if (!["verified", "incomplete", "failed"].includes(output.attestation.status ?? "")) {
      errors.push(`attestation.status has invalid value: ${output.attestation.status}`);
    }
  }

  // 5) RFC3161 status honnête
  if (output.rfc3161) {
    if (!["verified", "pending", "failed", "incomplete"].includes(output.rfc3161.status ?? "")) {
      errors.push(`rfc3161.status has invalid value: ${output.rfc3161.status}`);
    }
  }

  // 6) TLA export structuré
  if (output.tla_export) {
    if (typeof output.tla_export !== "object") {
      errors.push("tla_export is not an object");
    } else if ("status" in output.tla_export) {
      if (!["exported", "incomplete", "failed"].includes(output.tla_export.status as string)) {
        errors.push(`tla_export.status has invalid value: ${output.tla_export.status}`);
      }
    }
  }

  // 7) Verify all structuré
  if (!output.verify_all) {
    errors.push("verify_all is missing");
  } else {
    if (typeof output.verify_all.success !== "boolean") errors.push("verify_all.success is not a boolean");
    if (typeof output.verify_all.output !== "string") errors.push("verify_all.output is not a string");
    if (!Array.isArray(output.verify_all.errors)) errors.push("verify_all.errors is not an array");
  }

  // 8) Timestamps cohérents
  if (output.timestamps) {
    const t = output.timestamps;
    if (t.started_at > t.pipeline_at) errors.push("timestamps: started_at > pipeline_at");
    if (t.pipeline_at > t.audit_at) errors.push("timestamps: pipeline_at > audit_at");
    if (t.audit_at > t.sigma_at) errors.push("timestamps: audit_at > sigma_at");
    if (t.sigma_at > t.merkle_at) errors.push("timestamps: sigma_at > merkle_at");
    if (t.merkle_at > t.completed_at) errors.push("timestamps: merkle_at > completed_at");
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
