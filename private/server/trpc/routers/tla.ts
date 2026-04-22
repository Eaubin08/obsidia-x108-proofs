/**
 * TLA Router
 * Endpoint tRPC pour vérification TLA
 */

import { z } from "zod";
import { publicProcedure, router } from "../index";
import { callRealTLAVerify } from "../../adapters/tlaVerifyAdapter";
import path from "path";
import fs from "fs";

type ResolvedPaths = {
  trace_path: string | null;
  vars_path: string | null;
};

function getStableTLAPaths(decision_id: string): { dir: string; trace_path: string; vars_path: string } {
  const dir = path.join(process.cwd(), "traces", "tla", decision_id);
  return {
    dir,
    trace_path: path.join(dir, "trace.json"),
    vars_path: path.join(dir, "vars.json"),
  };
}

function recoverTLAPathsFromEnvelope(decision_id: string): ResolvedPaths {
  const envelopePath = path.join(process.cwd(), "traces", "canonical", `${decision_id}.envelope.json`);

  if (!fs.existsSync(envelopePath)) {
    return { trace_path: null, vars_path: null };
  }

  try {
    const raw = fs.readFileSync(envelopePath, "utf-8");
    const envelope = JSON.parse(raw);

    const refs = Array.isArray(envelope?.evidence_refs) ? envelope.evidence_refs : [];

    const traceRef = refs.find((x: unknown) => typeof x === "string" && x.startsWith("tla:")) as string | undefined;
    const varsRef = refs.find((x: unknown) => typeof x === "string" && x.startsWith("tla_vars:")) as string | undefined;

    const trace_path =
      (typeof envelope?.tla_export?.output_trace_path === "string" ? envelope.tla_export.output_trace_path : null) ??
      (traceRef ? traceRef.slice("tla:".length) : null);

    const vars_path =
      (typeof envelope?.tla_export?.vars_path === "string" ? envelope.tla_export.vars_path : null) ??
      (varsRef ? varsRef.slice("tla_vars:".length) : null);

    return { trace_path, vars_path };
  } catch {
    return { trace_path: null, vars_path: null };
  }
}

function ensureStableArtifacts(decision_id: string): ResolvedPaths {
  const stable = getStableTLAPaths(decision_id);

  const stableTraceExists = fs.existsSync(stable.trace_path);
  const stableVarsExists = fs.existsSync(stable.vars_path);

  if (stableTraceExists && stableVarsExists) {
    return {
      trace_path: stable.trace_path,
      vars_path: stable.vars_path,
    };
  }

  const recovered = recoverTLAPathsFromEnvelope(decision_id);

  if (!recovered.trace_path || !recovered.vars_path) {
    return {
      trace_path: stableTraceExists ? stable.trace_path : null,
      vars_path: stableVarsExists ? stable.vars_path : null,
    };
  }

  try {
    fs.mkdirSync(stable.dir, { recursive: true });

    if (!stableTraceExists && fs.existsSync(recovered.trace_path)) {
      fs.copyFileSync(recovered.trace_path, stable.trace_path);
    }

    if (!stableVarsExists && fs.existsSync(recovered.vars_path)) {
      fs.copyFileSync(recovered.vars_path, stable.vars_path);
    }
  } catch {
    // on retombe honnêtement sur les chemins récupérés
  }

  const finalTrace = fs.existsSync(stable.trace_path) ? stable.trace_path : recovered.trace_path;
  const finalVars = fs.existsSync(stable.vars_path) ? stable.vars_path : recovered.vars_path;

  return {
    trace_path: fs.existsSync(finalTrace) ? finalTrace : null,
    vars_path: fs.existsSync(finalVars) ? finalVars : null,
  };
}

export const tlaRouter = router({
  byDecision: publicProcedure
    .input(
      z.object({
        decision_id: z.string(),
        target: z.enum(["X108.tla", "ObsidiaDistX108A12.tla"]).optional(),
      })
    )
    .query(({ input }) => {
      try {
        const target = input.target || "X108.tla";
        const resolved = ensureStableArtifacts(input.decision_id);

        if (!resolved.trace_path || !resolved.vars_path) {
          return {
            decision_id: input.decision_id,
            target,
            status: "incomplete",
            verified: false,
            trace_path: resolved.trace_path,
            vars_path: resolved.vars_path,
            reason: "Trace or vars file not found",
          };
        }

        return callRealTLAVerify(
          input.decision_id,
          resolved.trace_path,
          resolved.vars_path,
          target
        );
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
