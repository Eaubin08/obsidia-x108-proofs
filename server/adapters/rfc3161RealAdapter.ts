/**
 * RFC3161 Real Adapter
 * Branchement rÃ©el sur un serveur TSA
 */

import { spawnSync } from "child_process";
import { getRFC3161Config } from "../config/rfc3161";
import path from "path";

export interface RFC3161Token {
  decision_id: string;
  source: "obsidia_rfc3161";
  status: "verified" | "pending" | "incomplete" | "failed";
  verified: boolean;
  token: string | null;
  timestamp: number | null;
  tsa_url: string | null;
  artifact_path: string | null;
  command: string | null;
  stdout: string;
  stderr: string;
  reason: string | null;
}

export function callRealRFC3161TSA(
  decision_id: string,
  merkle_root: string
): RFC3161Token {
  const config = getRFC3161Config();

  // Si RFC3161 est dÃ©sactivÃ©, retourner incomplete honnÃªtement
  if (!config.enabled) {
    return {
      decision_id,
      source: "obsidia_rfc3161",
      status: "incomplete",
      verified: false,
      token: null,
      timestamp: null,
      tsa_url: null,
      artifact_path: null,
      command: null,
      stdout: "",
      stderr: "",
      reason: "RFC3161 disabled (OBSIDIA_RFC3161_ENABLED not set)",
    };
  }

  // Si pas de TSA URL, retourner incomplete
  if (!config.tsa_url) {
    return {
      decision_id,
      source: "obsidia_rfc3161",
      status: "incomplete",
      verified: false,
      token: null,
      timestamp: null,
      tsa_url: null,
      artifact_path: null,
      command: null,
      stdout: "",
      stderr: "",
      reason: "No TSA URL configured (OBSIDIA_TSA_URL)",
    };
  }

  // Appeler le script Python rÃ©el
  try {
    const scriptPath = path.join(
      process.cwd(),
      "server/python_agents/verify_rfc3161.py"
    );

    const result = spawnSync("py", ["-3", scriptPath, decision_id, merkle_root, config.tsa_url], {
      timeout: config.timeout,
      encoding: "utf-8",
    });

    if (result.error) {
      return {
        decision_id,
        source: "obsidia_rfc3161",
        status: "failed",
        verified: false,
        token: null,
        timestamp: null,
        tsa_url: config.tsa_url,
        artifact_path: null,
        command: `py -3 ${scriptPath}`,
        stdout: "",
        stderr: result.error.message,
        reason: `Script execution failed: ${result.error.message}`,
      };
    }

    // Parser la sortie JSON du script
    try {
      const output = JSON.parse(result.stdout);
      return output as RFC3161Token;
    } catch (e) {
      return {
        decision_id,
        source: "obsidia_rfc3161",
        status: "failed",
        verified: false,
        token: null,
        timestamp: null,
        tsa_url: config.tsa_url,
        artifact_path: null,
        command: `py -3 ${scriptPath}`,
        stdout: result.stdout,
        stderr: result.stderr || "",
        reason: `Failed to parse script output: ${e}`,
      };
    }
  } catch (e) {
    return {
      decision_id,
      source: "obsidia_rfc3161",
      status: "failed",
      verified: false,
      token: null,
      timestamp: null,
      tsa_url: config.tsa_url,
      artifact_path: null,
      command: null,
      stdout: "",
      stderr: String(e),
      reason: `Adapter error: ${e}`,
    };
  }
}




