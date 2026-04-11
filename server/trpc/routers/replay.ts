/**
 * Replay Router
 * Endpoint tRPC pour vÃ©rification replay avec les bons arguments
 */

import { z } from "zod";
import { publicProcedure, router } from "../index";
import { spawnSync } from "child_process";

const isWin = process.platform === "win32";
const PYTHON_CMD = isWin ? "py" : "python3";
const pyArgs = (args: string[]) => (isWin ? ["-3.11", ...args] : args);
import path from "path";
import fs from "fs";
import { getAuditLog } from "../../audit/auditLog";

export const replayRouter = router({
  verify: publicProcedure
    .input(z.object({ decision_id: z.string() }))
    .query(({ input }) => {
      try {
        // RÃ©soudre les chemins rÃ©els des artefacts
        const auditLog = getAuditLog();
        const entry = auditLog.getByDecisionId(input.decision_id);
        
        if (!entry) {
          return {
            decision_id: input.decision_id,
            status: "failed",
            verified: false,
            reason: "Decision not found in audit log",
            stdout: "",
            stderr: "Decision not found",
          };
        }
        
        // Chemins rÃ©els
        const auditLogPath = path.join(process.cwd(), "traces", "audit", "audit.jsonl");
const canonicalDir = path.join(process.cwd(), "traces", "canonical");
        let envelopePath = path.join(canonicalDir, `${input.decision_id}.envelope.json`);
if (!fs.existsSync(envelopePath)) {
  const altEnvelopePath = path.join(canonicalDir, `${input.decision_id}.json`);
  if (fs.existsSync(altEnvelopePath)) {
    envelopePath = altEnvelopePath;
  }
}
        const traceTlaPath = path.join(process.cwd(), "traces/tla", input.decision_id, "trace.json");
        
        // VÃ©rifier que les fichiers existent
        if (!fs.existsSync(auditLogPath)) {
          return {
            decision_id: input.decision_id,
            status: "incomplete",
            verified: false,
            reason: "Audit log not found",
            stdout: "",
            stderr: `Audit log not found: ${auditLogPath}`,
          };
        }
        
        if (!fs.existsSync(envelopePath)) {
          return {
            decision_id: input.decision_id,
            status: "incomplete",
            verified: false,
            reason: "Envelope not found",
            stdout: "",
            stderr: `Envelope not found: ${envelopePath}`,
          };
        }
        
        // trace.json requis par verify_replay.py
if (!fs.existsSync(traceTlaPath)) {
  const envelopeJson = JSON.parse(fs.readFileSync(envelopePath, "utf-8"));
  fs.mkdirSync(path.dirname(traceTlaPath), { recursive: true });
  fs.writeFileSync(
    traceTlaPath,
    JSON.stringify({
      decision_id: input.decision_id,
      trace_id: envelopeJson.trace_id ?? null,
      kernel_verdict: envelopeJson.kernel_verdict ?? envelopeJson.x108_gate ?? null,
      consensus_verdict: envelopeJson.consensus_verdict ?? envelopeJson.x108_gate ?? null,
      x108_gate: envelopeJson.x108_gate ?? null,
      generated_by: "replay_router_fallback_aligned"
    }, null, 2),
    "utf-8"
  );
}
        const scriptPath = path.join(
          process.cwd(),
          "server/python_agents/verify_replay.py"
        );
        
        // Appeler le script avec les bons arguments
        const args = [scriptPath, auditLogPath, envelopePath, traceTlaPath];
                
        const result = spawnSync(PYTHON_CMD, pyArgs(args), {
          timeout: 30000,
          encoding: "utf-8",
        });
        
        if (result.error) {
          return {
            decision_id: input.decision_id,
            status: "failed",
            verified: false,
            reason: result.error.message,
            stdout: "",
            stderr: result.error.message,
          };
        }
        
        try {
          const output = JSON.parse(result.stdout);
          return output;
        } catch (e) {
          return {
            decision_id: input.decision_id,
            status: "failed",
            verified: false,
            reason: `Failed to parse script output: ${e}`,
            stdout: result.stdout,
            stderr: result.stderr || "",
          };
        }
      } catch (e) {
        return {
          decision_id: input.decision_id,
          status: "failed",
          verified: false,
          reason: String(e),
          stdout: "",
          stderr: String(e),
        };
      }
    }),
});




