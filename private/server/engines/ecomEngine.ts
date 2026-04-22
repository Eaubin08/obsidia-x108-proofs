/**
 * EcomWorld Engine
 * Full funnel: CTR/CVR/ROAS + price/conversion/margin dynamics
 * AI agents with mandatory 10s HOLD (Guard X-108)
 * Deterministic with seed-based replay
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

export interface EcomParams {
  seed: number;
  steps: number;
  impressions: number;    // base impressions per step
  baseCTR: number;        // base click-through rate
  baseCVR: number;        // base conversion rate
  basePrice: number;      // base product price
  baseCOGS: number;       // cost of goods sold
  adSpend: number;        // ad spend per step
  aiAgentEnabled: boolean;
  aiHoldSeconds: number;  // X-108 mandatory hold (default: 10)
  priceElasticity: number; // price sensitivity
}

export interface AgentAction {
  t: number;
  agentId: string;
  action: "price_adjust" | "bid_adjust" | "inventory_reorder";
  proposed: number;
  applied: number;
  holdRequired: boolean;
  holdRemaining: number;
  x108Decision: "ALLOW" | "HOLD" | "BLOCK";
}

export interface EcomStep {
  t: number;
  impressions: number;
  clicks: number;
  conversions: number;
  revenue: number;
  cogs: number;
  margin: number;
  adSpend: number;
  ctr: number;
  cvr: number;
  roas: number;
  price: number;
  agentActions: AgentAction[];
}

export interface EcomMetrics {
  totalRevenue: number;
  totalCOGS: number;
  totalMargin: number;
  totalAdSpend: number;
  totalConversions: number;
  avgCTR: number;
  avgCVR: number;
  avgROAS: number;
  avgMarginRate: number;
  agentActionsTotal: number;
  agentHoldCount: number;
  agentBlockCount: number;
  agentAllowCount: number;
  x108ComplianceRate: number;
  stateHash: string;
  merkleRoot: string;
}

export interface EcomResult {
  params: EcomParams;
  steps: EcomStep[];
  metrics: EcomMetrics;
}

// ─── Agent state ──────────────────────────────────────────────────────────────

interface AgentState {
  id: string;
  lastActionTime: number;
  pendingAction: AgentAction | null;
}

// ─── Engine ───────────────────────────────────────────────────────────────────

export function runEcomSimulation(params: EcomParams): EcomResult {
  const rand = mulberry32(params.seed);
  const steps: EcomStep[] = [];

  // Initialize agents
  const agents: AgentState[] = params.aiAgentEnabled
    ? [
        { id: "agent-price-optimizer", lastActionTime: -999, pendingAction: null },
        { id: "agent-bid-manager", lastActionTime: -999, pendingAction: null },
        { id: "agent-inventory", lastActionTime: -999, pendingAction: null },
      ]
    : [];

  let price = params.basePrice;
  let totalRevenue = 0;
  let totalCOGS = 0;
  let totalAdSpend = 0;
  let totalConversions = 0;
  let agentActionsTotal = 0;
  let agentHoldCount = 0;
  let agentBlockCount = 0;
  let agentAllowCount = 0;

  // Seasonal/trend factors
  const trend = 1 + 0.001 * (rand() - 0.5); // slight upward/downward trend

  for (let t = 0; t < params.steps; t++) {
    const agentActions: AgentAction[] = [];

    // 1. AI Agent actions (with X-108 HOLD enforcement)
    if (params.aiAgentEnabled) {
      for (const agent of agents) {
        // Agent decides to act every ~10 steps
        if (rand() < 0.1) {
          const elapsed = t - agent.lastActionTime;
          const holdRequired = elapsed < params.aiHoldSeconds;
          const holdRemaining = Math.max(0, params.aiHoldSeconds - elapsed);

          let x108Decision: "ALLOW" | "HOLD" | "BLOCK" = "ALLOW";
          if (holdRequired) {
            x108Decision = "HOLD";
            agentHoldCount++;
          } else {
            agentAllowCount++;
          }

          const proposed = price * (1 + 0.05 * (rand() - 0.5));
          const applied = x108Decision === "ALLOW" ? proposed : price;

          if (x108Decision === "ALLOW") {
            price = applied;
            agent.lastActionTime = t;
          }

          const action: AgentAction = {
            t,
            agentId: agent.id,
            action: "price_adjust",
            proposed,
            applied,
            holdRequired,
            holdRemaining,
            x108Decision,
          };

          agentActions.push(action);
          agentActionsTotal++;
        }
      }
    }

    // 2. Funnel dynamics
    const seasonalFactor = 1 + 0.2 * Math.sin(2 * Math.PI * t / 30); // monthly cycle
    const trendFactor = Math.pow(trend, t);
    const priceEffect = Math.pow(price / params.basePrice, -params.priceElasticity);

    const ctr = Math.max(0.001, params.baseCTR * seasonalFactor * trendFactor * (1 + 0.1 * boxMuller(rand)));
    const cvr = Math.max(0.001, params.baseCVR * priceEffect * (1 + 0.05 * boxMuller(rand)));

    const impressions = Math.round(params.impressions * (1 + 0.2 * boxMuller(rand)));
    const clicks = Math.round(impressions * ctr);
    const conversions = Math.round(clicks * cvr);

    const revenue = conversions * price;
    const cogs = conversions * params.baseCOGS;
    const margin = revenue - cogs - params.adSpend;
    const roas = params.adSpend > 0 ? revenue / params.adSpend : 0;

    totalRevenue += revenue;
    totalCOGS += cogs;
    totalAdSpend += params.adSpend;
    totalConversions += conversions;

    steps.push({
      t,
      impressions,
      clicks,
      conversions,
      revenue,
      cogs,
      margin,
      adSpend: params.adSpend,
      ctr,
      cvr,
      roas,
      price,
      agentActions,
    });
  }

  const totalMargin = totalRevenue - totalCOGS - totalAdSpend;
  const avgCTR = steps.reduce((a, s) => a + s.ctr, 0) / steps.length;
  const avgCVR = steps.reduce((a, s) => a + s.cvr, 0) / steps.length;
  const avgROAS = totalAdSpend > 0 ? totalRevenue / totalAdSpend : 0;
  const avgMarginRate = totalRevenue > 0 ? totalMargin / totalRevenue : 0;

  const x108ComplianceRate =
    agentActionsTotal > 0
      ? (agentHoldCount + agentAllowCount) / agentActionsTotal
      : 1;

  // State hash
  const stateStr = steps.map((s) => `${s.t}:${s.revenue.toFixed(2)}:${s.conversions}`).join("|");
  const stateHash = sha256(stateStr);

  // Merkle root
  const revenueHashes = steps.map((s) => sha256(s.revenue.toFixed(2)));
  const merkleRoot = computeMerkleRoot(revenueHashes);

  const metrics: EcomMetrics = {
    totalRevenue,
    totalCOGS,
    totalMargin,
    totalAdSpend,
    totalConversions,
    avgCTR,
    avgCVR,
    avgROAS,
    avgMarginRate,
    agentActionsTotal,
    agentHoldCount,
    agentBlockCount,
    agentAllowCount,
    x108ComplianceRate,
    stateHash,
    merkleRoot,
  };

  return { params, steps, metrics };
}
