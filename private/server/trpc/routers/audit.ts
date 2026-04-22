/**
 * Audit Router
 * Endpoint tRPC pour audit log réel
 */

import { z } from "zod";
import { publicProcedure, router } from "../index";
import { getAuditLog } from "../../audit/auditLog";

export const auditRouter = router({
  byDecision: publicProcedure
    .input(z.object({ decision_id: z.string() }))
    .query(({ input }) => {
      const auditLog = getAuditLog();
      const entry = auditLog.getByDecisionId(input.decision_id);
      
      if (!entry) {
        return { found: false, entry: null };
      }
      
      return { found: true, entry };
    }),
});
