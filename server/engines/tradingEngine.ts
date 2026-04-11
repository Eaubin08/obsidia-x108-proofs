/**
 * TradingWorld Engine
 * Composite price model: GBM + Markov regimes + Jump diffusion + GARCH volatility
 * Deterministic with seed-based replay
 */

// ─── Seeded PRNG (Mulberry32) ─────────────────────────────────────────────────
function mulberry32(seed: number) {
  let s = seed >>> 0;
  return function () {
    s |= 0;
    s = (s + 0x6d2b79f5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function boxMuller(rand: () => number): number {
  const u = rand();
  const v = rand();
  return Math.sqrt(-2 * Math.log(u + 1e-15)) * Math.cos(2 * Math.PI * v);
}

// ─── Types ────────────────────────────────────────────────────────────────────

export interface TradingParams {
  seed: number;
  steps: number;
  S0: number;         // initial price
  mu: number;         // drift
  sigma: number;      // base volatility
  dt: number;         // time step (e.g. 1/252)
  jumpLambda: number; // Poisson intensity
  jumpMu: number;     // mean jump size
  jumpSigma: number;  // jump size std
  garchAlpha: number; // GARCH(1,1) alpha
  garchBeta: number;  // GARCH(1,1) beta
  garchOmega: number; // GARCH(1,1) omega
  regimes: number;    // number of Markov regimes
  frictionBps: number; // transaction cost in bps
}

export interface TradingStep {
  t: number;
  price: number;
  returns: number;
  volatility: number;
  regime: number;
  jump: boolean;
  volume: number;
}

export interface TradingMetrics {
  finalPrice: number;
  totalReturn: number;
  annualizedVol: number;
  maxDrawdown: number;
  var95: number;       // 95% VaR
  es95: number;        // 95% Expected Shortfall
  sharpe: number;
  stateHash: string;
  merkleRoot: string;
}

export interface TradingResult {
  params: TradingParams;
  steps: TradingStep[];
  metrics: TradingMetrics;
}

// ─── Engine ───────────────────────────────────────────────────────────────────

import crypto from "crypto";
import { computeMerkleRoot, sha256 } from "./guardX108.js";

export function runTradingSimulation(params: TradingParams): TradingResult {
  const rand = mulberry32(params.seed);

  // Markov regime transition matrix (simplified)
  const regimeTransition = buildRegimeMatrix(params.regimes, rand);
  const regimeMu = Array.from({ length: params.regimes }, (_, i) =>
    params.mu * (1 + (i - params.regimes / 2) * 0.5)
  );
  const regimeSigma = Array.from({ length: params.regimes }, (_, i) =>
    params.sigma * (1 + i * 0.3)
  );

  const steps: TradingStep[] = [];
  let price = params.S0;
  let regime = 0;
  let garchVar = params.sigma * params.sigma;
  const returns: number[] = [];

  for (let t = 0; t < params.steps; t++) {
    // 1. Regime transition
    const transRow = regimeTransition[regime];
    const u = rand();
    let cumP = 0;
    for (let r = 0; r < params.regimes; r++) {
      cumP += transRow[r];
      if (u < cumP) {
        regime = r;
        break;
      }
    }

    // 2. GARCH volatility update
    const prevReturn = returns.length > 0 ? returns[returns.length - 1] : 0;
    garchVar =
      params.garchOmega +
      params.garchAlpha * prevReturn * prevReturn +
      params.garchBeta * garchVar;
    const garchSigma = Math.sqrt(Math.max(garchVar, 1e-8));

    // 3. GBM with regime-dependent parameters
    const mu_r = regimeMu[regime];
    const sigma_r = regimeSigma[regime] * garchSigma / params.sigma;
    const z = boxMuller(rand);
    const gbmReturn = (mu_r - 0.5 * sigma_r * sigma_r) * params.dt + sigma_r * Math.sqrt(params.dt) * z;

    // 4. Jump diffusion (Merton)
    let jumpReturn = 0;
    let jumped = false;
    const jumpProb = params.jumpLambda * params.dt;
    if (rand() < jumpProb) {
      jumped = true;
      const jz = boxMuller(rand);
      jumpReturn = params.jumpMu + params.jumpSigma * jz;
    }

    // 5. Friction
    const frictionCost = params.frictionBps / 10000 * (jumped ? 2 : 1);

    const totalReturn = gbmReturn + jumpReturn - frictionCost;
    price = price * Math.exp(totalReturn);

    // 6. Volume (log-normal)
    const vol = Math.exp(10 + 0.5 * boxMuller(rand));

    returns.push(totalReturn);
    steps.push({
      t,
      price: Math.max(price, 0.01),
      returns: totalReturn,
      volatility: garchSigma,
      regime,
      jump: jumped,
      volume: vol,
    });
  }

  const metrics = computeTradingMetrics(steps, params, returns);
  return { params, steps, metrics };
}

function buildRegimeMatrix(n: number, rand: () => number): number[][] {
  const matrix: number[][] = [];
  for (let i = 0; i < n; i++) {
    const row: number[] = [];
    let sum = 0;
    for (let j = 0; j < n; j++) {
      const v = rand() + (i === j ? n : 0.1); // self-transition more likely
      row.push(v);
      sum += v;
    }
    matrix.push(row.map((v) => v / sum));
  }
  return matrix;
}

function computeTradingMetrics(
  steps: TradingStep[],
  params: TradingParams,
  returns: number[]
): TradingMetrics {
  const finalPrice = steps[steps.length - 1]?.price ?? params.S0;
  const totalReturn = (finalPrice - params.S0) / params.S0;

  // Annualized volatility
  const mean = returns.reduce((a, b) => a + b, 0) / returns.length;
  const variance = returns.reduce((a, r) => a + (r - mean) ** 2, 0) / returns.length;
  const annualizedVol = Math.sqrt(variance / params.dt);

  // Max drawdown
  let peak = params.S0;
  let maxDD = 0;
  for (const s of steps) {
    if (s.price > peak) peak = s.price;
    const dd = (peak - s.price) / peak;
    if (dd > maxDD) maxDD = dd;
  }

  // VaR and ES (historical simulation)
  const sortedReturns = [...returns].sort((a, b) => a - b);
  const varIdx = Math.floor(0.05 * sortedReturns.length);
  const var95 = -sortedReturns[varIdx];
  const es95 = -(sortedReturns.slice(0, varIdx).reduce((a, b) => a + b, 0) / (varIdx || 1));

  // Sharpe (annualized, risk-free = 0)
  const annualReturn = totalReturn / (params.steps * params.dt);
  const sharpe = annualReturn / (annualizedVol + 1e-8);

  // State hash
  const stateStr = steps.map((s) => `${s.t}:${s.price.toFixed(6)}:${s.regime}`).join("|");
  const stateHash = sha256(stateStr);

  // Merkle root over price hashes
  const priceHashes = steps.map((s) => sha256(s.price.toFixed(6)));
  const merkleRoot = computeMerkleRoot(priceHashes);

  return {
    finalPrice,
    totalReturn,
    annualizedVol,
    maxDrawdown: maxDD,
    var95,
    es95,
    sharpe,
    stateHash,
    merkleRoot,
  };
}
