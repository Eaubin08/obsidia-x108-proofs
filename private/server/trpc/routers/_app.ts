/**
 * tRPC App Router
 * Assemblage de tous les routers
 */

import { router } from "../index";
import { orchestrationRouter } from "./orchestration";
import { auditRouter } from "./audit";
import { truthRouter } from "./truth";
import { systemRouter } from "./system";
import { attestationRouter } from "./attestation";
import { tlaRouter } from "./tla";
import { replayRouter } from "./replay";
import { provenanceRouter } from "./provenance";

export const appRouter = router({
  orchestration: orchestrationRouter,
  audit: auditRouter,
  truth: truthRouter,
  system: systemRouter,
  attestation: attestationRouter,
  tla: tlaRouter,
  replay: replayRouter,
  provenance: provenanceRouter,
});

export type AppRouter = typeof appRouter;
