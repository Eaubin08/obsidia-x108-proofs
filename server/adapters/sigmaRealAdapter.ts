/**
 * Sigma Real Adapter — Branchement RÉEL sur obsidia_sigma_v130.py
 * 
 * Appelle le VRAI ObsidiaSigmaMonitor avec enveloppe complète
 * Observation-only : ne modifie JAMAIS le verdict
 */

import { spawnSync } from "child_process";
import path from "path";
import type { CanonicalEnvelope } from "../canonical/canonicalPipeline";

export interface SigmaRealObservation {
  stability: "stable" | "unstable" | "unknown";
  metrics: Record<string, number>;
  alerts: string[];
  observed_at: number;
  confidence: number | null;
  source: "obsidia_sigma_v130" | "incomplete";
  status: "ok" | "incomplete" | "failed";
}

/**
 * Appelle le VRAI Sigma Python avec enveloppe complète
 * 
 * IMPORTANT : Sigma est observation-only. Ne modifie JAMAIS le verdict.
 * Prend l'enveloppe complète, pas heuristiques locales.
 */
export function callRealSigma(envelope: CanonicalEnvelope): SigmaRealObservation {
  try {
    // Détection dynamique du repo
    const repoRoot = findObsidiaRepoRoot();
    if (!repoRoot) {
      return {
        stability: "unknown",
        metrics: {},
        alerts: ["SIGMA_REPO_NOT_FOUND"],
        observed_at: Date.now(),
        confidence: null,
        source: "incomplete",
        status: "incomplete",
      };
    }
    
    // Appeler le script Python avec enveloppe complète
    const result = spawnSync("python3", [
      "-c",
      `
import sys
sys.path.insert(0, '${repoRoot}')
from agents.obsidia_sigma_v130 import ObsidiaSigmaMonitor
import json

monitor = ObsidiaSigmaMonitor()
envelope = ${JSON.stringify(envelope)}

# Passer enveloppe complète au monitor
monitor.evaluate_step(
  severity=envelope.get('severity', 'S2'),
  risks=envelope.get('risk_flags', []),
  contras=envelope.get('contradictions', [])
)
report = monitor.export_to_proofkit()
print(json.dumps(report))
      `,
    ], {
      encoding: "utf-8",
      maxBuffer: 10 * 1024 * 1024,
      timeout: 5000,
    });
    
    if (result.error || result.status !== 0) {
      return {
        stability: "unknown",
        metrics: {},
        alerts: ["SIGMA_PYTHON_FAILED", result.stderr || ""],
        observed_at: Date.now(),
        confidence: null,
        source: "incomplete",
        status: "failed",
      };
    }
    
    const output = result.stdout?.trim();
    if (!output) {
      return {
        stability: "unknown",
        metrics: {},
        alerts: ["SIGMA_NO_OUTPUT"],
        observed_at: Date.now(),
        confidence: null,
        source: "incomplete",
        status: "incomplete",
      };
    }
    
    const report = JSON.parse(output);
    
    return {
      stability: report.stability || "unknown",
      metrics: report.metrics || {},
      alerts: report.alerts || [],
      observed_at: Date.now(),
      confidence: report.confidence ?? null,
      source: "obsidia_sigma_v130",
      status: "ok",
    };
  } catch (err) {
    return {
      stability: "unknown",
      metrics: {},
      alerts: ["SIGMA_EXCEPTION", String(err)],
      observed_at: Date.now(),
      confidence: null,
      source: "incomplete",
      status: "failed",
    };
  }
}

function findObsidiaRepoRoot(): string | null {
  // Chercher le repo dans les chemins courants
  const possiblePaths = [
    "/home/ubuntu/obsidia-engine-proof-core",
    "../../../obsidia-engine-proof-core",
    "../../obsidia-engine-proof-core",
  ];
  
  for (const p of possiblePaths) {
    try {
      const resolved = path.resolve(p);
      const agentsPath = path.join(resolved, "agents", "obsidia_sigma_v130.py");
      const fs = require("fs");
      if (fs.existsSync(agentsPath)) {
        return resolved;
      }
    } catch (err) {
      // Continuer
    }
  }
  
  return null;
}

export function validateSigmaObservationOnly(
  verdictBefore: string,
  verdictAfter: string
): { valid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  if (verdictBefore !== verdictAfter) {
    errors.push("Sigma modified verdict: not observation-only");
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
}
