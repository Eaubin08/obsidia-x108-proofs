/**
 * Provenance Router
 * Endpoint tRPC pour vérification provenance avec les bons arguments
 */

import { z } from "zod";
import { publicProcedure, router } from "../index";
import { spawnSync } from "child_process";
import path from "path";
import fs from "fs";
import { getAuditLog } from "../../audit/auditLog";

export const provenanceRouter = router({
  verify: publicProcedure
    .input(z.object({ decision_id: z.string() }))
    .query(({ input }) => {
      try {
        // Résoudre les chemins réels des artefacts
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
        
        // Chemins réels
        const auditLogPath = path.join(process.cwd(), "traces/audit/audit.jsonl");
        const envelopePath = path.join(process.cwd(), "traces/canonical", `${input.decision_id}.envelope.json`);
        
        // Vérifier que les fichiers existent
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
        
        const scriptPath = path.join(
          process.cwd(),
          "server/python_agents/verify_provenance.py"
        );
        
        // Appeler le script avec les bons arguments
        const result = spawnSync("python3", [scriptPath, auditLogPath, envelopePath], {
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
