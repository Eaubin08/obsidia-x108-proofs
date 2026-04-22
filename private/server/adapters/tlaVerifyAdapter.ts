/**
 * TLA Verify Adapter
 * Branchement rÃ©el sur vÃ©rification TLA externe
 */

import { spawnSync } from "child_process";
import { getTLAConfig } from "../config/tla";
import path from "path";

export interface TLAVerificationResult {
  decision_id: string;
  target: "X108.tla" | "ObsidiaDistX108A12.tla";
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
  target: "X108.tla" | "ObsidiaDistX108A12.tla" = "X108.tla"
): TLAVerificationResult {
  const config = getTLAConfig();

  // Si TLA est dÃ©sactivÃ©, retourner incomplete honnÃªtement
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

  // Appeler le script Python rÃ©el
  try {
    const scriptPath = path.join(
      process.cwd(),
      "server/python_agents/verify_tla.py"
    );

    const result = spawnSync("py", ["-3", scriptPath, decision_id, trace_path, vars_path, target], {
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
        command: `py -3 ${scriptPath}`,
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
        command: `py -3 ${scriptPath}`,
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




