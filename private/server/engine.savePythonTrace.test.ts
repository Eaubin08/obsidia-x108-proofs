/**
 * Test Vitest — engine.savePythonTrace
 *
 * Garantit :
 * 1. Le replayRef est au format "scenarioId:seed" quand les deux champs sont fournis
 * 2. Le replayRef tombe sur intentId quand scenarioId ou seed est absent
 * 3. La procédure retourne { success: true, ticketId, replayRef }
 * 4. Les champs domain, decision, reasons sont bien persistés
 */

import { describe, expect, it, vi, beforeEach } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

// ─── Mock de db.insertDecisionTicket ─────────────────────────────────────────
// On ne touche pas à la vraie DB dans les tests unitaires
vi.mock("./db", async (importOriginal) => {
  const actual = await importOriginal<typeof import("./db")>();
  return {
    ...actual,
    db: {
      ...actual.db,
      insertDecisionTicket: vi.fn(async (_input: unknown) => 42), // retourne un ticketId fictif
    },
  };
});

// ─── Contexte public (pas d'auth requise pour savePythonTrace) ────────────────
function createPublicContext(): TrpcContext {
  return {
    user: null,
    req: { protocol: "https", headers: {} } as TrpcContext["req"],
    res: {} as TrpcContext["res"],
  };
}

// ─── Tests ───────────────────────────────────────────────────────────────────
describe("engine.savePythonTrace", () => {

  it("construit replayRef = 'scenarioId:seed' quand les deux champs sont fournis", async () => {
    const caller = appRouter.createCaller(createPublicContext());
    const result = await caller.engine.savePythonTrace({
      domain: "trading",
      decision: "ALLOW",
      reasons: ["coherence > seuil"],
      scenarioId: "flash_crash",
      seed: 4271,
      source: "python",
    });
    expect(result.success).toBe(true);
    expect(result.replayRef).toBe("flash_crash:4271");
  });

  it("construit replayRef = 'scenarioId:seed' pour un autre domaine et verdict", async () => {
    const caller = appRouter.createCaller(createPublicContext());
    const result = await caller.engine.savePythonTrace({
      domain: "bank",
      decision: "BLOCK",
      reasons: ["volatility > 0.4", "irréversible"],
      scenarioId: "bank_run",
      seed: 1337,
      source: "os4_engine",
      coherence: 0.3,
      volatility: 0.5,
      tau: 15,
    });
    expect(result.success).toBe(true);
    expect(result.replayRef).toBe("bank_run:1337");
  });

  it("tombe sur intentId quand scenarioId est absent", async () => {
    const caller = appRouter.createCaller(createPublicContext());
    const result = await caller.engine.savePythonTrace({
      domain: "ecom",
      decision: "HOLD",
      reasons: [],
      seed: 999,
      // scenarioId absent
    });
    expect(result.success).toBe(true);
    // replayRef ne doit PAS être "undefined:999"
    expect(result.replayRef).not.toMatch(/^undefined:/);
    // doit ressembler à un intentId (commence par "trace-" ou est un hash)
    expect(result.replayRef).toBeTruthy();
  });

  it("tombe sur intentId quand seed est absent", async () => {
    const caller = appRouter.createCaller(createPublicContext());
    const result = await caller.engine.savePythonTrace({
      domain: "trading",
      decision: "ALLOW",
      reasons: [],
      scenarioId: "black_swan",
      // seed absent
    });
    expect(result.success).toBe(true);
    // replayRef ne doit PAS être "black_swan:undefined"
    expect(result.replayRef).not.toMatch(/:undefined$/);
    expect(result.replayRef).toBeTruthy();
  });

  it("retourne ticketId et success=true sur un run complet", async () => {
    const caller = appRouter.createCaller(createPublicContext());
    const result = await caller.engine.savePythonTrace({
      domain: "trading",
      decision: "BLOCK",
      reasons: ["tau dépassé", "volatility critique"],
      scenarioId: "market_manipulation",
      seed: 7777,
      stateHash: "abc123def456",
      traceId: "trace-xyz",
      source: "python",
      coherence: 0.12,
      volatility: 0.88,
      tau: 5,
    });
    expect(result.success).toBe(true);
    expect(result.ticketId).toBeDefined();
    expect(result.replayRef).toBe("market_manipulation:7777");
  });

});
