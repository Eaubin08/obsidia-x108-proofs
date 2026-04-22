/**
 * Orchestration Router
 * Endpoint tRPC pour orchestration réelle
 */

import { z } from "zod";
import { publicProcedure, router } from "../index";
import { orchestrateReal, defaultTradingState, defaultBankState, defaultEcomState } from "../../orchestration/orchestratorReal";

export const orchestrationRouter = router({
  real: publicProcedure
    .input(
      z.object({
        domain: z.enum(["trading", "bank", "ecom"]),
        state: z.any().optional().nullable(),
      })
    )
    .mutation(({ input }) => {
      const state = input.state || 
        (input.domain === "trading" ? defaultTradingState() :
         input.domain === "bank" ? defaultBankState() :
         defaultEcomState());
      return orchestrateReal({ domain: input.domain, state: state as any });
    }),
});
