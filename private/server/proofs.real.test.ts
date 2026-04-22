import fs from "fs";
import path from "path";
import { spawnSync } from "child_process";
import { describe, it, expect } from "vitest";
import { orchestrateReal, defaultBankState } from "./orchestration/orchestratorReal";

const PROJECT_ROOT = process.cwd();
const IS_WIN = process.platform === "win32";
const PYTHON_CMD = IS_WIN ? "py" : "python3";
const pyArgs = (args: string[]) => (IS_WIN ? ["-3", ...args] : args);

function stabilizeTlaArtifacts(decisionId: string, tlaExport: any) {
  const outDir = path.join(PROJECT_ROOT, "traces", "tla", decisionId);
  fs.mkdirSync(outDir, { recursive: true });

  const tracePath = path.join(outDir, "trace.json");
  const varsPath = path.join(outDir, "vars.json");

  fs.copyFileSync(tlaExport.output_trace_path, tracePath);
  fs.copyFileSync(tlaExport.vars_path, varsPath);

  return { tracePath, varsPath };
}

const hasRFC3161Env =
  process.env.OBSIDIA_RFC3161_ENABLED === "true" &&
  !!process.env.OBSIDIA_TSA_URL &&
  !!process.env.OBSIDIA_TSA_CHAIN_FILE &&
  !!process.env.OBSIDIA_TSA_CA_FILE;

const hasTlaEnv =
  process.env.OBSIDIA_TLA_ENABLED === "true" &&
  !!process.env.OBSIDIA_TLA_TLC_CMD &&
  !!process.env.OBSIDIA_TLA_ROOT;

const itRFC = hasRFC3161Env ? it : it.skip;
const itTLA = hasTlaEnv ? it : it.skip;

describe("proof locks — RFC3161 + Distributed A12", () => {
  itRFC("RFC3161 verified", () => {
    const output = orchestrateReal("bank", defaultBankState());

    expect(output.success).toBe(true);
    expect(output.attestation?.status).toBe("verified");

    const rfc = output.rfc3161 as any;
    expect(rfc?.status).toBe("verified");
    expect(rfc?.verified).toBe(true);
    expect(rfc?.artifact_path).toBeTruthy();
    expect(String(rfc?.stdout ?? "")).toContain("Verification: OK");
  }, 120000);

  itTLA("Distributed A12 verified", () => {
    const output = orchestrateReal("bank", defaultBankState());

    expect(output.success).toBe(true);
    expect(output.envelope?.decision_id).toBeTruthy();
    expect(output.tla_export).toBeTruthy();

    const tlaExport = output.tla_export as any;
    const decisionId = output.envelope!.decision_id;

    const { tracePath, varsPath } = stabilizeTlaArtifacts(decisionId, tlaExport);

    const script = path.join(PROJECT_ROOT, "server", "python_agents", "verify_tla.py");
    const res = spawnSync(
      PYTHON_CMD,
      pyArgs([script, decisionId, tracePath, varsPath, "ObsidiaDistX108A12.tla"]),
      {
        cwd: PROJECT_ROOT,
        encoding: "utf8",
        env: process.env,
      }
    );

    expect(res.status).toBe(0);
    expect(res.stdout).toBeTruthy();

    const parsed = JSON.parse(res.stdout);
    expect(parsed.target).toBe("ObsidiaDistX108A12.tla");
    expect(parsed.status).toBe("verified");
    expect(parsed.verified).toBe(true);
    expect(parsed.reason).toBe("TLC verification passed");
  }, 180000);
});
