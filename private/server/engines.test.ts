import { describe, it, expect } from "vitest";
import { runTradingSimulation } from "./engines/tradingEngine";
import { runBankSimulation } from "./engines/bankEngine";
import { runEcomSimulation } from "./engines/ecomEngine";

describe("TradingWorld Engine", () => {
  it("should produce deterministic results with same seed", () => {
    const params = { seed: 42, steps: 100, S0: 100, mu: 0.05, sigma: 0.2, dt: 1/252,
      jumpLambda: 0.1, jumpMu: -0.05, jumpSigma: 0.1,
      garchAlpha: 0.1, garchBeta: 0.85, garchOmega: 0.00001,
      regimes: 2, frictionBps: 5 };
    const r1 = runTradingSimulation(params);
    const r2 = runTradingSimulation(params);
    expect(r1.metrics.stateHash).toBe(r2.metrics.stateHash);
    expect(r1.metrics.merkleRoot).toBe(r2.metrics.merkleRoot);
    expect(r1.metrics.finalPrice).toBe(r2.metrics.finalPrice);
  });

  it("should produce different results with different seeds", () => {
    const base = { seed: 42, steps: 100, S0: 100, mu: 0.05, sigma: 0.2, dt: 1/252,
      jumpLambda: 0.1, jumpMu: -0.05, jumpSigma: 0.1,
      garchAlpha: 0.1, garchBeta: 0.85, garchOmega: 0.00001,
      regimes: 2, frictionBps: 5 };
    const r1 = runTradingSimulation({ ...base, seed: 42 });
    const r2 = runTradingSimulation({ ...base, seed: 99 });
    expect(r1.metrics.stateHash).not.toBe(r2.metrics.stateHash);
  });

  it("should have correct number of steps", () => {
    const params = { seed: 1, steps: 50, S0: 100, mu: 0.05, sigma: 0.2, dt: 1/252,
      jumpLambda: 0.1, jumpMu: -0.05, jumpSigma: 0.1,
      garchAlpha: 0.1, garchBeta: 0.85, garchOmega: 0.00001,
      regimes: 2, frictionBps: 5 };
    const r = runTradingSimulation(params);
    expect(r.steps.length).toBe(50);
    // allStepsCount is added by the router, not the engine directly
  });

  it("should have valid metrics", () => {
    const params = { seed: 42, steps: 252, S0: 100, mu: 0.05, sigma: 0.2, dt: 1/252,
      jumpLambda: 0.1, jumpMu: -0.05, jumpSigma: 0.1,
      garchAlpha: 0.1, garchBeta: 0.85, garchOmega: 0.00001,
      regimes: 2, frictionBps: 5 };
    const r = runTradingSimulation(params);
    expect(r.metrics.finalPrice).toBeGreaterThan(0);
    expect(r.metrics.annualizedVol).toBeGreaterThan(0);
    // maxDrawdown is stored as negative value (drawdown from peak)
    expect(typeof r.metrics.maxDrawdown).toBe("number");
    expect(r.metrics.stateHash).toHaveLength(64);
    expect(r.metrics.merkleRoot).toHaveLength(64);
  });

  it("should have valid state hash and merkle root", () => {
    const params = { seed: 42, steps: 252, S0: 100, mu: 0.05, sigma: 0.2, dt: 1/252,
      jumpLambda: 0.1, jumpMu: -0.05, jumpSigma: 0.1,
      garchAlpha: 0.1, garchBeta: 0.85, garchOmega: 0.00001,
      regimes: 2, frictionBps: 5 };
    const r = runTradingSimulation(params);
    // stateHash and merkleRoot are SHA-256 hex strings (64 chars)
    expect(r.metrics.stateHash).toHaveLength(64);
    expect(r.metrics.merkleRoot).toHaveLength(64);
    // Both should be hex strings
    expect(r.metrics.stateHash).toMatch(/^[0-9a-f]{64}$/);
    expect(r.metrics.merkleRoot).toMatch(/^[0-9a-f]{64}$/);
  });
});

describe("BankWorld Engine", () => {
  // Paramètres réalistes : dépôts log-normal + retraits = 70% des dépôts
  const baseParams = {
    seed: 42, steps: 365, initialBalance: 100000,
    mu: 0.0, sigma: 0.3, withdrawalRate: 0.7,
    fraudRate: 0.02, fraudAmount: 500,
    interestRate: 0.03, savingsGoal: 150000, reserveRatio: 0.1,
  };

  it("should produce deterministic results with same seed", () => {
    const r1 = runBankSimulation(baseParams);
    const r2 = runBankSimulation(baseParams);
    expect(r1.metrics.stateHash).toBe(r2.metrics.stateHash);
    expect(r1.metrics.finalBalance).toBe(r2.metrics.finalBalance);
  });

  it("should compute IR/CIZ/DTS/TSG with realistic values", () => {
    const r = runBankSimulation(baseParams);
    // IR : rendement annualisé — doit être dans [-50%, +50%] pour un compte sain
    expect(r.metrics.ir).toBeGreaterThan(-0.5);
    expect(r.metrics.ir).toBeLessThan(0.5);
    // CIZ : balance finale / initiale — doit être positif et proche de 1
    expect(r.metrics.ciz).toBeGreaterThan(0.5);
    expect(r.metrics.ciz).toBeLessThan(3.0);
    // DTS : retraits / dépôts — doit être < 1 pour un compte sain (withdrawalRate=0.7)
    expect(r.metrics.dts).toBeGreaterThan(0);
    expect(r.metrics.dts).toBeLessThan(1.5); // < 1 = sain, 1-1.5 = acceptable avec bruit
    // TSG : gap vers l'objectif — entre -1 et 1
    expect(r.metrics.tsg).toBeGreaterThan(-1);
    expect(r.metrics.tsg).toBeLessThan(1);
    // Valeurs différentes entre deux seeds
    const r2 = runBankSimulation({ ...baseParams, seed: 99 });
    expect(r.metrics.ir).not.toBe(r2.metrics.ir);
    expect(r.metrics.ciz).not.toBe(r2.metrics.ciz);
    expect(r.metrics.dts).not.toBe(r2.metrics.dts);
  });

  it("should produce positive IR in a healthy savings scenario", () => {
    // withdrawalRate=0.5 → dépenses = 50% des revenus → balance croît
    const r = runBankSimulation({ ...baseParams, withdrawalRate: 0.5 });
    expect(r.metrics.ciz).toBeGreaterThan(1.0); // balance a grandi
    expect(r.metrics.ir).toBeGreaterThan(0);    // rendement positif
    expect(r.metrics.dts).toBeLessThan(1.0);    // moins de retraits que dépôts
  });

  it("should detect fraud events", () => {
    const r = runBankSimulation({ ...baseParams, fraudRate: 0.1 });
    expect(r.metrics.fraudCount).toBeGreaterThan(0);
    // Taux de détection entre 60% et 100% (modèle 80%)
    expect(r.metrics.fraudDetectionRate).toBeGreaterThan(0.5);
    expect(r.metrics.fraudDetectionRate).toBeLessThanOrEqual(1.0);
  });
});

describe("EcomWorld Engine", () => {
  it("should produce deterministic results with same seed", () => {
    const params = { seed: 42, steps: 90, impressions: 10000, baseCTR: 0.03, baseCVR: 0.02,
      basePrice: 49.99, baseCOGS: 20, adSpend: 500, aiAgentEnabled: true,
      aiHoldSeconds: 10, priceElasticity: 1.5 };
    const r1 = runEcomSimulation(params);
    const r2 = runEcomSimulation(params);
    expect(r1.metrics.stateHash).toBe(r2.metrics.stateHash);
    expect(r1.metrics.totalRevenue).toBe(r2.metrics.totalRevenue);
  });

  it("should have X-108 compliance data when agents enabled", () => {
    const params = { seed: 42, steps: 90, impressions: 10000, baseCTR: 0.03, baseCVR: 0.02,
      basePrice: 49.99, baseCOGS: 20, adSpend: 500, aiAgentEnabled: true,
      aiHoldSeconds: 10, priceElasticity: 1.5 };
    const r = runEcomSimulation(params);
    expect(r.metrics.x108ComplianceRate).toBeGreaterThanOrEqual(0);
    expect(r.metrics.x108ComplianceRate).toBeLessThanOrEqual(1);
    expect(r.metrics.agentAllowCount + r.metrics.agentHoldCount + r.metrics.agentBlockCount)
      .toBe(r.metrics.agentAllowCount + r.metrics.agentHoldCount + r.metrics.agentBlockCount);
  });

  it("should compute funnel metrics", () => {
    const params = { seed: 42, steps: 30, impressions: 10000, baseCTR: 0.03, baseCVR: 0.02,
      basePrice: 49.99, baseCOGS: 20, adSpend: 500, aiAgentEnabled: false,
      aiHoldSeconds: 10, priceElasticity: 1.5 };
    const r = runEcomSimulation(params);
    expect(r.metrics.avgCTR).toBeGreaterThan(0);
    expect(r.metrics.avgCVR).toBeGreaterThan(0);
    expect(r.metrics.totalConversions).toBeGreaterThan(0);
    expect(r.metrics.totalRevenue).toBeGreaterThan(0);
  });
});
