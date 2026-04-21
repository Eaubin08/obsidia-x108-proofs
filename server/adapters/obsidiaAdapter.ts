/**
 * ObsidiaAdapter — Connecteur vers les moteurs réels OS4
 * Structure : call engine → guard evaluation → execute → return decision
 */

import { runTradingSimulation } from "../engines/tradingEngine";
import { runBankSimulation } from "../engines/bankEngine";
import { runEcomSimulation } from "../engines/ecomEngine";
import { runGuard, computeMerkleRoot, type GuardInput } from "../engines/guardX108";

// ─── Types ────────────────────────────────────────────────────────────────────

export type SimulationMode = "quick" | "advanced" | "stress" | "replay";
export type VerticalType = "trading" | "bank" | "ecom";

export interface ObsidiaRequest {
  vertical: VerticalType;
  mode: SimulationMode;
  seed?: number;
  params?: {
    volatility?: number;
    risk?: number;
    fraudProbability?: number;
    marketRegime?: "bull" | "bear" | "crash";
    traffic?: number;
    steps?: number;
  };
}

export interface ObsidiaDecision {
  verdict: "BLOCK" | "HOLD" | "ALLOW";
  holdDuration?: number;
  coherenceScore: number;
  irreversibilityScore: number;
  reason: string;
  hash: string;
  timestamp: number;
}

export interface ObsidiaResult {
  vertical: VerticalType;
  mode: SimulationMode;
  seed: number;
  decision: ObsidiaDecision;
  metrics: Record<string, number | string | boolean>;
  series: number[];
  proofHash: string;
  executionTimeMs: number;
  guardPassed: boolean;
}

// ─── Mode Configs ─────────────────────────────────────────────────────────────

function getModeConfig(mode: SimulationMode, params?: ObsidiaRequest["params"]) {
  switch (mode) {
    case "quick":
      return { steps: 30, mu: 0.08, sigma: 0.15, seed: 42, fraudProbability: 0.03 };
    case "advanced":
      return {
        steps: 252,
        mu: 0.08,
        sigma: params?.volatility ?? 0.2,
        seed: Math.floor(Math.random() * 9999),
        fraudProbability: params?.fraudProbability ?? 0.05,
      };
    case "stress":
      return {
        steps: 100,
        mu: -0.25,
        sigma: 0.6,
        seed: 1337,
        fraudProbability: 0.3,
      };
    case "replay":
      return {
        steps: 252,
        mu: 0.08,
        sigma: 0.2,
        seed: params?.steps ?? 42,
        fraudProbability: 0.05,
      };
    default:
      return { steps: 252, mu: 0.08, sigma: 0.2, seed: 42, fraudProbability: 0.05 };
  }
}

// ─── Main Adapter ─────────────────────────────────────────────────────────────

export async function callObsidiaEngine(req: ObsidiaRequest): Promise<ObsidiaResult> {
  const startTime = Date.now();
  const config = getModeConfig(req.mode, req.params);
  const seed = req.seed ?? config.seed ?? 42;

  let series: number[] = [];
  let metrics: Record<string, number | string | boolean> = {};
  let guardInput: {
    action: string;
    irreversibilityScore: number;
    coherenceScore: number;
    amount?: number;
    volatility?: number;
  };

  // ── Step 1: Call the real engine ──────────────────────────────────────────
  switch (req.vertical) {
    case "trading": {
      const result = runTradingSimulation({
        seed,
        steps: config.steps,
        S0: 100,
        mu: config.mu,
        sigma: config.sigma,
        dt: 1 / 252,
        regimes: 3,
        jumpLambda: req.mode === "stress" ? 0.1 : 0.02,
        jumpMu: -0.05,
        jumpSigma: 0.08,
        garchAlpha: 0.1,
        garchBeta: 0.85,
        garchOmega: 0.00001,
        frictionBps: 5,
      });
      series = result.steps.map((s) => s.price);
      metrics = {
        finalPrice: result.metrics.finalPrice,
        totalReturn: result.metrics.totalReturn,
        sharpe: result.metrics.sharpe,
        maxDrawdown: result.metrics.maxDrawdown,
        var95: result.metrics.var95,
        es95: result.metrics.es95,
        annualizedVol: result.metrics.annualizedVol,
        stateHash: result.metrics.stateHash,
      };
      guardInput = {
        action: "EXECUTE_TRADE",
        irreversibilityScore: Math.abs(result.metrics.totalReturn) > 0.15 ? 0.85 : 0.4,
        coherenceScore: result.metrics.sharpe > 0.5 ? 0.8 : 0.45,
        volatility: result.metrics.annualizedVol,
      };
      break;
    }

    case "bank": {
      const result = runBankSimulation({
        seed,
        steps: config.steps,
        initialBalance: 50000,
        mu: 0.0,
        sigma: 0.3,
        withdrawalRate: 0.7,
        fraudRate: config.fraudProbability,
        fraudAmount: 2500,
        interestRate: 0.03,
        savingsGoal: 60000,
        reserveRatio: 0.1,
      });
      series = result.steps.map((s) => s.balance);
      metrics = {
        finalBalance: result.metrics.finalBalance,
        totalDeposits: result.metrics.totalDeposits,
        totalWithdrawals: result.metrics.totalWithdrawals,
        totalFraudLoss: result.metrics.totalFraudLoss,
        fraudCount: result.metrics.fraudCount,
        fraudDetectionRate: result.metrics.fraudDetectionRate,
        ir: result.metrics.ir,
        ciz: result.metrics.ciz,
        dts: result.metrics.dts,
        tsg: result.metrics.tsg,
        savingsGoalMet: result.metrics.savingsGoalMet,
        reserveCompliance: result.metrics.reserveCompliance,
        stateHash: result.metrics.stateHash,
      };
      guardInput = {
        action: "EXECUTE_TRANSFER",
        irreversibilityScore: result.metrics.ir,
        coherenceScore: result.metrics.ciz,
        amount: result.metrics.totalWithdrawals,
      };
      break;
    }

    case "ecom": {
      const result = runEcomSimulation({
        seed,
        steps: config.steps,
        impressions: req.params?.traffic ?? 10000,
        baseCTR: 0.04,
        baseCVR: 0.025,
        basePrice: 85,
        baseCOGS: 42,
        adSpend: 500,
        aiAgentEnabled: true,
        aiHoldSeconds: 10,
        priceElasticity: 1.2,
      });
      series = result.steps.map((s) => s.revenue ?? 0);
      metrics = {
        totalRevenue: result.metrics.totalRevenue,
        totalCOGS: result.metrics.totalCOGS,
        totalMargin: result.metrics.totalMargin,
        totalAdSpend: result.metrics.totalAdSpend,
        totalConversions: result.metrics.totalConversions,
        avgCTR: result.metrics.avgCTR,
        avgCVR: result.metrics.avgCVR,
        avgROAS: result.metrics.avgROAS,
        avgMarginRate: result.metrics.avgMarginRate,
        agentActionsTotal: result.metrics.agentActionsTotal,
        agentHoldCount: result.metrics.agentHoldCount,
        agentBlockCount: result.metrics.agentBlockCount,
        agentAllowCount: result.metrics.agentAllowCount,
        x108ComplianceRate: result.metrics.x108ComplianceRate,
        stateHash: result.metrics.stateHash,
      };
      guardInput = {
        action: "APPROVE_AGENT_PURCHASE",
        irreversibilityScore: result.metrics.avgROAS < 1.5 ? 0.8 : 0.35,
        coherenceScore: result.metrics.avgMarginRate > 0.2 ? 0.75 : 0.42,
        amount: result.metrics.totalRevenue,
      };
      break;
    }
  }

  // ── Step 2: Guard X-108 evaluation ───────────────────────────────────────
  const guardPayload: GuardInput = {
    intent_id: `${req.vertical}-${req.mode}-${seed}-${Date.now()}`,
    domain: req.vertical,
    metrics: {
      irreversibilityScore: guardInput.irreversibilityScore,
      coherenceScore: guardInput.coherenceScore,
      amount: guardInput.amount ?? 0,
      volatility: guardInput.volatility ?? 0,
    },
    thresholds: {
      irr_block: 0.9,
      irr_hold: 0.7,
      coh_block: 0.3,
      coh_hold: 0.5,
    },
    tau: 10,
    elapsed: req.mode === "stress" ? 0 : 15, // stress mode triggers HOLD
    irr: guardInput.irreversibilityScore > 0.7,
    replay_ref: `seed:${seed}`,
  };
  const guardResult = runGuard(guardPayload);

  // ── Step 3: Build Merkle proof ────────────────────────────────────────────
  const leaves = series.slice(0, 8).map((v) => v.toFixed(6));
  const proofHash = computeMerkleRoot(leaves);

  const executionTimeMs = Date.now() - startTime;

  return {
    vertical: req.vertical,
    mode: req.mode,
    seed,
    decision: {
      verdict: guardResult.decision,
      holdDuration: guardResult.x108.gate_active ? guardResult.x108.tau : undefined,
      coherenceScore: guardInput.coherenceScore,
      irreversibilityScore: guardInput.irreversibilityScore,
      reason: guardResult.reasons.join(" | "),
      hash: guardResult.audit.hash_now,
      timestamp: Date.now(),
    },
    metrics,
    series,
    proofHash,
    executionTimeMs,
    guardPassed: guardResult.decision !== "BLOCK",
  };
}
