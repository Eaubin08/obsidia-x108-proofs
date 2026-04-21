/**
 * Sigma Real Adapter — Branchement RÉEL sur obsidia_sigma_v130.py
 * Observation-only : ne modifie jamais le verdict.
 */

import { spawnSync } from "child_process";
import path from "path";
import fs from "fs";
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

function findObsidiaRepoRoot(): string | null {
  const candidates = [
    process.cwd(),
    path.join(process.cwd(), "obsidia-engine-proof-core"),
    path.join(process.cwd(), "upstream", "obsidia-engine-proof-core"),
    path.resolve(process.cwd(), "..", "obsidia-engine-proof-core"),
    path.resolve(process.cwd(), "..", "..", "obsidia-engine-proof-core"),
    path.resolve(process.cwd(), "..", "..", "..", "obsidia-engine-proof-core"),
  ];

  for (const candidate of candidates) {
    try {
      const agentsPath = path.join(candidate, "agents", "obsidia_sigma_v130.py");
      if (fs.existsSync(agentsPath)) {
        return candidate;
      }
    } catch {
      // ignore
    }
  }

  return null;
}

export function callRealSigma(envelope: CanonicalEnvelope): SigmaRealObservation {
  const observed_at = Date.now();

  try {
    const repoRoot = findObsidiaRepoRoot();
    if (!repoRoot) {
      return {
        stability: "unknown",
        metrics: {},
        alerts: ["SIGMA_REPO_NOT_FOUND"],
        observed_at,
        confidence: null,
        source: "incomplete",
        status: "incomplete",
      };
    }

    const pyCode = [
      "import sys, json",
      `sys.path.insert(0, r'''${repoRoot}''')`,
      "from agents.obsidia_sigma_v130 import ObsidiaSigmaMonitor",
      "monitor = ObsidiaSigmaMonitor()",
      `envelope = json.loads(r'''${JSON.stringify(envelope)}''')`,
      "monitor.evaluate_step(",
      "  severity=envelope.get('severity', 'S2'),",
      "  risks=envelope.get('risk_flags', []),",
      "  contras=envelope.get('contradictions', [])",
      ")",
      "report = monitor.export_to_proofkit()",
      "sigma = report.get('V18_9_sigma_stability', {})",
      "out = {",
      "  'stability': 'unstable' if not sigma.get('pass', False) else 'stable',",
      "  'metrics': sigma.get('metrics', {}),",
      "  'alerts': sigma.get('violation_types', []),",
      "  'confidence': None",
      "}",
      "print(json.dumps(out))",
    ].join("\n");

    const result = spawnSync("py", ["-3", "-c", pyCode], {
      cwd: repoRoot,
      encoding: "utf-8",
      timeout: 10000,
      maxBuffer: 10 * 1024 * 1024,
    });

    if (result.error) {
      return {
        stability: "unknown",
        metrics: {},
        alerts: ["SIGMA_PYTHON_ERROR", result.error.message],
        observed_at,
        confidence: null,
        source: "incomplete",
        status: "failed",
      };
    }

    if (result.status !== 0) {
      return {
        stability: "unknown",
        metrics: {},
        alerts: ["SIGMA_PYTHON_FAILED", (result.stderr || "").trim()],
        observed_at,
        confidence: null,
        source: "incomplete",
        status: "failed",
      };
    }

    const stdout = (result.stdout || "").trim();
    if (!stdout) {
      return {
        stability: "unknown",
        metrics: {},
        alerts: ["SIGMA_NO_OUTPUT"],
        observed_at,
        confidence: null,
        source: "incomplete",
        status: "incomplete",
      };
    }

    const parsed = JSON.parse(stdout);

    return {
      stability: parsed.stability === "stable" || parsed.stability === "unstable" ? parsed.stability : "unknown",
      metrics: parsed.metrics && typeof parsed.metrics === "object" ? parsed.metrics : {},
      alerts: Array.isArray(parsed.alerts) ? parsed.alerts : [],
      observed_at,
      confidence: parsed.confidence ?? null,
      source: "obsidia_sigma_v130",
      status: "ok",
    };
  } catch (err) {
    return {
      stability: "unknown",
      metrics: {},
      alerts: ["SIGMA_EXCEPTION", String(err)],
      observed_at,
      confidence: null,
      source: "incomplete",
      status: "failed",
    };
  }
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
