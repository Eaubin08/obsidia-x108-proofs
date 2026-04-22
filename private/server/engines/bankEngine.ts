/**
 * BankWorld Engine v2
 * Realistic cash flow model: log-normal deposits + proportional withdrawals
 * + fraud injection + IR/CIZ/DTS/TSG metrics + savings governance
 * Deterministic with seed-based replay (Mulberry32 PRNG)
 */

import { computeMerkleRoot, sha256 } from "./guardX108.js";

// ─── Seeded PRNG ──────────────────────────────────────────────────────────────
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

export interface BankParams {
  seed: number;
  steps: number;
  initialBalance: number;
  mu: number;          // log-normal mean for daily deposits (e.g. 0.0 → ~100€/day)
  sigma: number;       // log-normal volatility for deposits (e.g. 0.3)
  withdrawalRate: number; // fraction of deposits spent per day (e.g. 0.7 = 70%)
  fraudRate: number;   // probability of fraud per step
  fraudAmount: number; // mean fraud amount
  fraudDetectionCapacity?: number; // probability of detecting a fraud attempt (0..1, default 0.8)
  interestRate: number; // annual interest rate
  savingsGoal: number; // target savings balance
  reserveRatio: number; // minimum reserve ratio
}

export interface Transaction {
  t: number;
  amount: number;
  type: "credit" | "debit" | "fraud" | "interest" | "fee";
  balance: number;
  flagged: boolean;
}

export interface BankStep {
  t: number;
  balance: number;
  deposit: number;
  withdrawal: number;
  fraudDetected: boolean;
  fraudAmount: number;
  interestEarned: number;
  reserveRatio: number;
  transactions: Transaction[];
}

export interface BankMetrics {
  finalBalance: number;
  totalDeposits: number;
  totalWithdrawals: number;
  totalFraudLoss: number;
  fraudCount: number;
  fraudDetectionRate: number;
  /**
   * IR — Investment Return (annualized)
   * = (finalBalance - initialBalance) / initialBalance × (365 / steps)
   * Positive if balance grew, negative if it shrank.
   */
  ir: number;
  /**
   * CIZ — Capital Integrity Zone
   * = finalBalance / initialBalance
   * > 1 : balance grew (healthy), < 1 : balance shrank (warning)
   */
  ciz: number;
  /**
   * DTS — Debt-to-Savings ratio
   * = totalWithdrawals / totalDeposits
   * < 1 : spending less than earning (healthy), > 1 : over-spending
   */
  dts: number;
  /**
   * TSG — Target Savings Gap
   * = (savingsGoal - finalBalance) / savingsGoal
   * < 0 : goal exceeded, 0–1 : gap remaining, > 1 : balance below 0
   */
  tsg: number;
  savingsGoalMet: boolean;
  reserveCompliance: number;
  stateHash: string;
  merkleRoot: string;
}

export interface BankResult {
  params: BankParams;
  steps: BankStep[];
  metrics: BankMetrics;
}

// ─── Engine ───────────────────────────────────────────────────────────────────

export function runBankSimulation(params: BankParams): BankResult {
  const rand = mulberry32(params.seed);
  const steps: BankStep[] = [];
  let balance = params.initialBalance;
  let totalDeposits = 0;
  let totalWithdrawals = 0;
  let totalFraudLoss = 0;
  let fraudCount = 0;
  let fraudDetected = 0;
  let reserveCompliantSteps = 0;

  const dailyRate = params.interestRate / 365;
  // Base daily deposit: scale initialBalance so deposits are meaningful
  // e.g. initialBalance=100000 → baseDeposit ≈ 300€/day (≈ 9000€/month salary)
  const baseDeposit = params.initialBalance * 0.003;

  for (let t = 0; t < params.steps; t++) {
    const transactions: Transaction[] = [];

    // 1. Log-normal deposit (always positive — income/salary)
    const z1 = boxMuller(rand);
    const deposit = baseDeposit * Math.exp(params.mu + params.sigma * z1);
    totalDeposits += deposit;
    balance += deposit;
    transactions.push({ t, amount: deposit, type: "credit", balance, flagged: false });

    // 2. Proportional withdrawal (spending = withdrawalRate × deposit, with noise)
    const z2 = boxMuller(rand);
    const withdrawalBase = deposit * params.withdrawalRate;
    const withdrawal = Math.max(0, withdrawalBase * Math.exp(0.2 * z2));
    totalWithdrawals += withdrawal;
    balance -= withdrawal;
    transactions.push({ t, amount: -withdrawal, type: "debit", balance, flagged: false });

    // 3. Interest accrual
    const interest = Math.max(balance, 0) * dailyRate;
    balance += interest;
    transactions.push({ t, amount: interest, type: "interest", balance, flagged: false });

    // 4. Fraud injection
    let fraudAmt = 0;
    let fraudFlag = false;
    if (rand() < params.fraudRate) {
      fraudCount++;
      const fz = boxMuller(rand);
      fraudAmt = params.fraudAmount * Math.exp(0.3 * fz);
      // Detection model: parameterized detection rate (default 80%)
      const detected = rand() < (params.fraudDetectionCapacity ?? 0.8);
      if (detected) {
        fraudDetected++;
        fraudFlag = true;
        // Fraud blocked — no balance change
        transactions.push({ t, amount: -fraudAmt, type: "fraud", balance, flagged: true });
      } else {
        totalFraudLoss += fraudAmt;
        balance -= fraudAmt;
        transactions.push({ t, amount: -fraudAmt, type: "fraud", balance, flagged: false });
      }
    }

    // 5. Reserve check
    const reserveRatio = balance / Math.max(params.initialBalance, 1);
    if (reserveRatio >= params.reserveRatio) reserveCompliantSteps++;

    // 6. Fee (small operational cost)
    const fee = balance * 0.0001;
    balance -= fee;
    transactions.push({ t, amount: -fee, type: "fee", balance, flagged: false });

    steps.push({
      t,
      balance: Math.max(balance, 0),
      deposit,
      withdrawal,
      fraudDetected: fraudFlag,
      fraudAmount: fraudAmt,
      interestEarned: interest,
      reserveRatio,
      transactions,
    });
  }

  const metrics = computeBankMetrics(steps, params, {
    totalDeposits,
    totalWithdrawals,
    totalFraudLoss,
    fraudCount,
    fraudDetected,
    reserveCompliantSteps,
  });

  return { params, steps, metrics };
}

function computeBankMetrics(
  steps: BankStep[],
  params: BankParams,
  agg: {
    totalDeposits: number;
    totalWithdrawals: number;
    totalFraudLoss: number;
    fraudCount: number;
    fraudDetected: number;
    reserveCompliantSteps: number;
  }
): BankMetrics {
  const finalBalance = steps[steps.length - 1]?.balance ?? params.initialBalance;

  // IR: annualized return on initial balance
  const ir = ((finalBalance - params.initialBalance) / params.initialBalance) * (365 / params.steps);

  // CIZ: Capital Integrity Zone — > 1 means balance grew
  const ciz = finalBalance / params.initialBalance;

  // DTS: Debt-to-Savings — < 1 means spending less than earning (healthy)
  const dts = agg.totalDeposits > 0 ? agg.totalWithdrawals / agg.totalDeposits : 0;

  // TSG: Target Savings Gap — < 0 means goal exceeded
  const tsg = (params.savingsGoal - finalBalance) / params.savingsGoal;

  const fraudDetectionRate = agg.fraudCount > 0 ? agg.fraudDetected / agg.fraudCount : 1;
  const reserveCompliance = steps.length > 0 ? agg.reserveCompliantSteps / steps.length : 1;

  // State hash
  const stateStr = steps.map((s) => `${s.t}:${s.balance.toFixed(2)}:${s.fraudDetected ? 1 : 0}`).join("|");
  const stateHash = sha256(stateStr);

  // Merkle root
  const balanceHashes = steps.map((s) => sha256(s.balance.toFixed(2)));
  const merkleRoot = computeMerkleRoot(balanceHashes);

  return {
    finalBalance,
    totalDeposits: agg.totalDeposits,
    totalWithdrawals: agg.totalWithdrawals,
    totalFraudLoss: agg.totalFraudLoss,
    fraudCount: agg.fraudCount,
    fraudDetectionRate,
    ir,
    ciz,
    dts,
    tsg,
    savingsGoalMet: finalBalance >= params.savingsGoal,
    reserveCompliance,
    stateHash,
    merkleRoot,
  };
}
