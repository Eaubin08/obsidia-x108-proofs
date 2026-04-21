/**
 * TLA Verify Adapter
 * Branchement réel sur vérification TLA externe
 */

import { spawnSync } from "child_process";
import { getTLAConfig } from "../config/tla";
import path from "path";

export interface TLAVerificationResult {
  decision_id: string;
  target: "X108.tla" | "DistributedX108.tla";
  status: "verified" | "incomplete" | "failed";
  verified: boolean;
  trace_path: string | null;
  vars_path: string | null;
  stdout_path: string | null;
  stderr_path: string | null;
  command: string | null;
  stdout: string;
  stderr: string;
  reason: string | null;
}

export function callRealTLAVerify(
  decision_id: string,
  trace_path: string,
  vars_path: string,
  target: "X108.tla" | "DistributedX108.tla" = "X108.tla"
): TLAVerificationResult {
  const config = getTLAConfig();

  // Si TLA est désactivé, retourner incomplete honnêtement
  if (!config.enabled) {
    return {
      decision_id,
      target,
      status: "incomplete",
      verified: false,
      trace_path,
      vars_path,
      stdout_path: null,
      stderr_path: null,
      command: null,
      stdout: "",
      stderr: "",
      reason: "TLA verification disabled (OBSIDIA_TLA_ENABLED not set)",
    };
  }

  // Appeler le script Python réel
  try {
    const scriptPath = path.join(
      process.cwd(),
      "server/python_agents/verify_tla.py"
    );

    const result = spawnSync("python3", [scriptPath, decision_id, trace_path, vars_path, target], {
      timeout: config.timeout,
      encoding: "utf-8",
    });

    if (result.error) {
      return {
        decision_id,
        target,
        status: "failed",
        verified: false,
        trace_path,
        vars_path,
        stdout_path: null,
        stderr_path: null,
        command: `python3 ${scriptPath}`,
        stdout: "",
        stderr: result.error.message,
        reason: `Script execution failed: ${result.error.message}`,
      };
    }

    // Parser la sortie JSON du script
    try {
      const output = JSON.parse(result.stdout);
      return output as TLAVerificationResult;
    } catch (e) {
      return {
        decision_id,
        target,
        status: "failed",
        verified: false,
        trace_path,
        vars_path,
        stdout_path: null,
        stderr_path: null,
        command: `python3 ${scriptPath}`,
        stdout: result.stdout,
        stderr: result.stderr || "",
        reason: `Failed to parse script output: ${e}`,
      };
    }
  } catch (e) {
    return {
      decision_id,
      target,
      status: "failed",
      verified: false,
      trace_path,
      vars_path,
      stdout_path: null,
      stderr_path: null,
      command: null,
      stdout: "",
      stderr: String(e),
      reason: `Adapter error: ${e}`,
    };
  }
}
