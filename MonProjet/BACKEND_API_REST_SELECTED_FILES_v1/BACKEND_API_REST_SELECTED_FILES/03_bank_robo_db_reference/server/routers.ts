import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router } from "./_core/trpc";
import { z } from "zod";

// Schema for transaction data sent from frontend session
const transactionDataSchema = z.object({
  decision: z.enum(["AUTORISER", "ANALYSER", "BLOQUER"]),
  reason: z.string(),
  geminiAnalysis: z.string(),
  metrics: z.object({
    ir: z.number(),
    ciz: z.number(),
    dts: z.number(),
    tsg: z.number(),
  }),
  ontologicalTests: z.object({
    timeIsLaw: z.number(),
    absoluteHoldGate: z.number(),
    zeroToleranceFlag: z.number(),
    irreversibilityIndex: z.number(),
    conflictZoneIsolation: z.number(),
    decisionTimeSensitivity: z.number(),
    totalSystemGuard: z.number(),
    negativeMemoryReflexes: z.number(),
    emergentBehaviorWatch: z.number(),
  }),
  roiContribution: z.number(),
});

export const appRouter = router({
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return { success: true } as const;
    }),
  }),

  // Banking Decision Robot API
  banking: router({
    // Process a single transaction
    processTransaction: publicProcedure
      .input(z.object({ scenarioName: z.string().optional() }))
      .mutation(async ({ input }) => {
        const { processTransaction } = await import("./bankingEngine");
        const { getRandomScenario, getScenarioByName } = await import("./scenarios");

        const scenario = input.scenarioName
          ? getScenarioByName(input.scenarioName)
          : getRandomScenario();

        if (!scenario) throw new Error("Scenario not found");

        const result = await processTransaction(scenario);

        // Save to database (background, don't block response)
        const db = await import("./db").then((m) => m.getDb());
        if (db) {
          const { transactions } = await import("../drizzle/schema");
          db.insert(transactions).values({
            scenarioName: scenario.name,
            decision: result.decision,
            reason: result.reason,
            ir: result.metrics.ir.toFixed(2),
            ciz: result.metrics.ciz.toFixed(2),
            dts: result.metrics.dts.toFixed(2),
            tsg: result.metrics.tsg.toFixed(2),
            timeIsLaw: result.ontologicalTests.timeIsLaw.toFixed(2),
            absoluteHoldGate: result.ontologicalTests.absoluteHoldGate.toFixed(2),
            zeroToleranceFlag: result.ontologicalTests.zeroToleranceFlag.toFixed(2),
            irreversibilityIndex: result.ontologicalTests.irreversibilityIndex.toFixed(2),
            conflictZoneIsolation: result.ontologicalTests.conflictZoneIsolation.toFixed(2),
            decisionTimeSensitivity: result.ontologicalTests.decisionTimeSensitivity.toFixed(2),
            totalSystemGuard: result.ontologicalTests.totalSystemGuard.toFixed(2),
            negativeMemoryReflexes: result.ontologicalTests.negativeMemoryReflexes.toFixed(2),
            emergentBehaviorWatch: result.ontologicalTests.emergentBehaviorWatch.toFixed(2),
            roiContribution: result.roiContribution,
          }).catch(err => console.error("[DB] Error saving transaction:", err));
        }

        return {
          scenario: {
            name: scenario.name,
            description: scenario.description,
            expectedDecision: scenario.expectedDecision,
          },
          ...result,
        };
      }),

    // Get all scenarios
    getScenarios: publicProcedure.query(async () => {
      const { SCENARIOS } = await import("./scenarios");
      return SCENARIOS.map((s) => ({
        name: s.name,
        expectedDecision: s.expectedDecision,
        description: s.description,
      }));
    }),

    // Get performance insights from SESSION data (sent by frontend)
    getPerformanceInsights: publicProcedure
      .input(z.object({
        sessionTransactions: z.array(transactionDataSchema),
        totalSessionCount: z.number(),
        avgResponseTimeMs: z.number(),
      }))
      .mutation(async ({ input }) => {
        const { generatePerformanceInsights } = await import("./bankingEngine");
        
        if (input.sessionTransactions.length < 10) {
          return {
            summary: `En attente de données (${input.totalSessionCount}/10 transactions de la session)`,
            trends: [],
            recommendations: [],
            metrics: {
              accuracyRate: 0,
              avgResponseTime: 0,
              geminiUsageRate: 0,
              confidenceScore: 0,
            },
          };
        }

        // Use last 20 transactions from session
        const recent = input.sessionTransactions.slice(-20);
        return generatePerformanceInsights(recent, input.totalSessionCount, input.avgResponseTimeMs);
      }),

    // Analyze continuous trends from SESSION data (sent by frontend)
    analyzeTrends: publicProcedure
      .input(z.object({
        recentTransactions: z.array(transactionDataSchema),
      }))
      .mutation(async ({ input }) => {
        const { analyzeContinuousTrends } = await import("./bankingEngine");
        
        if (input.recentTransactions.length < 5) {
          return ["Pas assez de données pour détecter des tendances"];
        }

        // Use last 10 transactions from session
        const recent = input.recentTransactions.slice(-10);
        return analyzeContinuousTrends(recent);
      }),

    // Generate detailed report from SESSION data (sent by frontend)
    generateReport: publicProcedure
      .input(z.object({
        sessionTransactions: z.array(transactionDataSchema),
        avgResponseTimeMs: z.number(),
      }))
      .mutation(async ({ input }) => {
        if (input.sessionTransactions.length === 0) {
          return "Aucune transaction dans la session pour générer un rapport";
        }

        const { generateDetailedReport } = await import("./bankingEngine");
        return generateDetailedReport(input.sessionTransactions, input.avgResponseTimeMs);
      }),
  }),
});

export type AppRouter = typeof appRouter;
