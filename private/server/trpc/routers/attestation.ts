/**
 * Attestation Router
 * Endpoint tRPC pour attestations Merkle + RFC3161
 */

import { z } from "zod";
import { publicProcedure, router } from "../index";
import { callRealMerkleVerify } from "../../adapters/merkleRealAdapter";
import { callRealRFC3161TSA } from "../../adapters/rfc3161RealAdapter";

export const attestationRouter = router({
  byDecision: publicProcedure
    .input(z.object({ decision_id: z.string() }))
    .query(({ input }) => {
      try {
        // Appeler Merkle réel
        const merkle = callRealMerkleVerify(input.decision_id);
        
        // Si Merkle réussi, appeler RFC3161 réel
        let rfc3161 = null;
        if (merkle.merkle_root && merkle.status === "verified") {
          rfc3161 = callRealRFC3161TSA(input.decision_id, merkle.merkle_root);
        }
        
        return {
          decision_id: input.decision_id,
          merkle: merkle as any,
          rfc3161: rfc3161 as any,
          combined_status: 
            merkle.status === "verified" && rfc3161?.status === "verified" ? "verified" :
            merkle.status === "incomplete" || rfc3161?.status === "incomplete" ? "incomplete" :
            "failed",
        } as any;
      } catch (e) {
        return {
          decision_id: input.decision_id,
          merkle: null,
          rfc3161: null,
          combined_status: "failed",
          error: String(e),
        };
      }
    }),
});
