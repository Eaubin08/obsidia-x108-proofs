/**
 * TLA Router
 * Endpoint tRPC pour vérification TLA
 */

import { z } from "zod";
import { publicProcedure, router } from "../index";
import { callRealTLAVerify } from "../../adapters/tlaVerifyAdapter";
import path from "path";
import fs from "fs";

export const tlaRouter = router({
  byDecision: publicProcedure
    .input(z.object({ 
      decision_id: z.string(),
      target: z.enum(["X108.tla", "DistributedX108.tla"]).optional(),
    }))
    .query(({ input }) => {
      try {
        const target = input.target || "X108.tla";
        
        // Chercher les fichiers trace et vars exportés
        const tracePath = path.join(process.cwd(), "traces", "tla", input.decision_id, "trace.json");
        const varsPath = path.join(process.cwd(), "traces", "tla", input.decision_id, "vars.json");
        
        // Si les fichiers n'existent pas, retourner incomplete
        if (!fs.existsSync(tracePath) || !fs.existsSync(varsPath)) {
          return {
            decision_id: input.decision_id,
            target: target,
            status: "incomplete",
            verified: false,
            trace_path: tracePath,
            vars_path: varsPath,
            reason: "Trace or vars file not found",
          };
        }
        
        // Appeler TLA verify réel
        const result = callRealTLAVerify(input.decision_id, tracePath, varsPath, target);
        
        return result;
      } catch (e) {
        return {
          decision_id: input.decision_id,
          target: input.target || "X108.tla",
          status: "failed",
          verified: false,
          trace_path: null,
          vars_path: null,
          reason: String(e),
        };
      }
    }),
});
