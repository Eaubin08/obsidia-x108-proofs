/**
 * OS4 Canonical Pipeline Bridge
 * Appelle les agents Python canoniques (Trading/Bank/Ecom + Guard X-108 + méta-agents)
 * via child_process.spawnSync sur run_pipeline.py
 *
 * Contrat de sortie : CanonicalDecisionEnvelope (aligné avec Python contracts.py)
 * Source : "canonical_framework" si Python OK, "canonical_fallback" si Python DOWN
 */
import { spawnSync } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BRIDGE_SCRIPT = path.resolve(__dirname, "../python_agents/run_pipeline.py");
const PYTHON_BIN = "python3.11";

// ─── Contrat canonique enrichi (aligné avec Python CanonicalDecisionEnvelope) ─
export interface CanonicalEnvelope {
  domain: "trading" | "bank" | "ecom";
  market_verdict: string;
  confidence: number;
  contradictions: string[];
  unknowns: string[];
  risk_flags: string[];
  x108_gate: "ALLOW" | "HOLD" | "BLOCK";
  reason_code: string;
  severity: "S0" | "S1" | "S2" | "S3" | "S4";
  decision_id: string;
  trace_id: string;
  ticket_required: boolean;
  ticket_id: string | null;
  attestation_ref: string | null;
  source: string;
  evidence_refs: string[];
  metrics: Record<string, unknown>;
  raw_engine: Record<string, unknown>;
  // Champs ajoutés côté TS pour traçabilité
  python_available: boolean;
  elapsed_ms: number;
  // Per-agent vote map: { agent_id -> { confidence, layer, claim, proposed_verdict, risk_flags, severity } }
  agent_votes?: Record<string, {
    confidence: number;
    layer: string;
    claim: string;
    proposed_verdict: string;
    risk_flags: string[];
    severity: string;
    contradictions: string[];
    unknowns: string[];
  }>;
  // Champs enrichis par orchestrateur (optionnels)
  kernel_verdict?: "ALLOW" | "HOLD" | "BLOCK";
  consensus_verdict?: "ALLOW" | "HOLD" | "BLOCK";
  x108?: {
    elapsed: number;
    tau: number;
    irr: number | boolean | null;
  };
  reasons?: string[];
  theorem_refs?: string[];
  sigma?: {
    stability: "stable" | "unstable" | "unknown";
    metrics: Record<string, number>;
    alerts: string[];
    confidence: number | null;
    status?: "ok" | "incomplete" | "failed";
    source?: "obsidia_sigma_v130" | "incomplete";
  };
  attestation?: {
    attestation_id?: string;
    merkle_root?: string | null;
    seal?: string | null;
    verified?: boolean;
    status?: "verified" | "incomplete" | "failed";
  };
  rfc3161?: {
    token?: string | null;
    timestamp?: number | null;
    verified?: boolean;
    status?: "verified" | "pending" | "failed" | "incomplete";
  };
  timestamps?: {
    created_at: number;
    kernel_at: number;
    consensus_at: number;
    sigma_at?: number;
    attestation_at?: number;
    rfc3161_at?: number;
  };
}

// ─── États par défaut pour chaque domaine ─────────────────────────────────────
export interface TradingState {
  symbol: string;
  prices: number[];
  highs: number[];
  lows: number[];
  volumes: number[];
  spreads_bps: number[];
  sentiment_scores: number[];
  event_risk_scores: number[];
  btc_reference_prices: number[];
  exposure?: number;
  drawdown?: number;
  order_book_imbalance?: number;
  order_book_depth?: number;
  slippage_bps?: number;
}

export interface BankState {
  transaction_type: string;
  amount: number;
  channel: string;
  counterparty_known: boolean;
  counterparty_age_days: number;
  account_balance: number;
  available_cash: number;
  historical_avg_amount: number;
  behavior_shift_score: number;
  fraud_score: number;
  policy_limit: number;
  affordability_score: number;
  urgency_score: number;
  identity_mismatch_score: number;
  narrative_conflict_score: number;
  device_trust_score?: number;
  recent_failed_attempts?: number;
  elapsed_s?: number;
  min_required_elapsed_s?: number;
}

export interface EcomState {
  session_id: string;
  traffic_quality: number;
  basket_intent_score: number;
  stock_ok: boolean;
  margin_rate: number;
  roas: number;
  conversion_readiness: number;
  fulfillment_risk: number;
  customer_trust: number;
  intent_conflict_score: number;
  checkout_friction_score: number;
  merchant_policy_score: number;
  basket_value: number;
  ad_spend: number;
  order_value: number;
  x108_compliance_rate: number;
}

export type DomainState = TradingState | BankState | EcomState;

// ─── Fallback local si Python DOWN ────────────────────────────────────────────
function buildFallbackEnvelope(
  domain: "trading" | "bank" | "ecom",
  elapsed_ms: number
): CanonicalEnvelope {
  return {
    domain,
    market_verdict: "UNAVAILABLE",
    confidence: 0,
    contradictions: ["PYTHON_ENGINE_OFFLINE"],
    unknowns: ["CANONICAL_PIPELINE_UNAVAILABLE"],
    risk_flags: ["FALLBACK_MODE"],
    x108_gate: "HOLD",
    reason_code: "PYTHON_ENGINE_OFFLINE",
    severity: "S2",
    decision_id: `${domain}-fallback-${Date.now()}`,
    trace_id: `fallback-${Date.now()}`,
    ticket_required: false,
    ticket_id: null,
    attestation_ref: null,
    source: "canonical_fallback",
    evidence_refs: [],
    metrics: { fallback: true },
    raw_engine: { fallback: true },
    python_available: false,
    elapsed_ms,
  };
}

// ─── Appel principal du pipeline canonique ────────────────────────────────────
export function runCanonicalPipeline(
  domain: "trading" | "bank" | "ecom",
  state: DomainState
): CanonicalEnvelope {
  const t0 = Date.now();

  try {
    const result = spawnSync(
      PYTHON_BIN,
      [BRIDGE_SCRIPT, domain, JSON.stringify(state)],
      {
        encoding: "utf8",
        timeout: 10_000, // 10s max
        cwd: path.resolve(__dirname, "../.."),
      }
    );

    const elapsed_ms = Date.now() - t0;

    if (result.error || result.status !== 0) {
      console.warn(
        `[canonical] Python pipeline failed for ${domain}:`,
        result.stderr || result.error?.message
      );
      return buildFallbackEnvelope(domain, elapsed_ms);
    }

    const stdout = result.stdout?.trim();
    if (!stdout) {
      return buildFallbackEnvelope(domain, elapsed_ms);
    }

    const parsed = JSON.parse(stdout) as Omit<CanonicalEnvelope, "python_available" | "elapsed_ms">;

    if ("error" in parsed) {
      console.warn(`[canonical] Python pipeline error for ${domain}:`, (parsed as { error: string }).error);
      return buildFallbackEnvelope(domain, elapsed_ms);
    }

    return {
      ...parsed,
      python_available: true,
      elapsed_ms,
    };
  } catch (err) {
    const elapsed_ms = Date.now() - t0;
    console.warn(`[canonical] Exception calling Python pipeline for ${domain}:`, err);
    return buildFallbackEnvelope(domain, elapsed_ms);
  }
}

// ─── Générateur pseudo-aléatoire déterministe (LCG) ─────────────────────────
function makeLCG(seed: number) {
  let s = (seed ^ 0xdeadbeef) >>> 0;
  return () => {
    s = Math.imul(1664525, s) + 1013904223;
    return (s >>> 0) / 0xffffffff;
  };
}

// ─── États dynamiques — chaque appel produit un état différent ───────────────
export function defaultTradingState(seed?: number): TradingState {
  const rng = makeLCG(seed ?? Date.now());
  const n = 21;
  // Régime aléatoire : bull / bear / range / volatile
  const regime = Math.floor(rng() * 4); // 0=range, 1=bull, 2=bear, 3=volatile
  const base = 80 + rng() * 120;        // prix de base entre 80 et 200
  const trend = regime === 1 ? 1.5 + rng() * 2 : regime === 2 ? -(1 + rng() * 2.5) : (rng() - 0.5) * 0.8;
  const vol = regime === 3 ? 4 + rng() * 6 : 0.5 + rng() * 2;
  const sentiment = regime === 1 ? 0.4 + rng() * 0.5 : regime === 2 ? -0.5 + rng() * 0.3 : (rng() - 0.5) * 0.6;
  const eventRisk = regime === 3 ? 0.5 + rng() * 0.4 : regime === 2 ? 0.3 + rng() * 0.3 : rng() * 0.3;
  return {
    symbol: "BTCUSDT",
    prices: Array.from({ length: n }, (_, i) => Math.max(1, base + i * trend + (rng() - 0.5) * vol * 2)),
    highs: Array.from({ length: n }, (_, i) => Math.max(1, base + i * trend + vol + rng() * vol)),
    lows: Array.from({ length: n }, (_, i) => Math.max(1, base + i * trend - vol - rng() * vol)),
    volumes: Array.from({ length: n }, (_, i) => 500 + rng() * 8000),
    spreads_bps: Array.from({ length: n }, () => regime === 3 ? 10 + rng() * 20 : 2 + rng() * 6),
    sentiment_scores: Array.from({ length: n }, () => Math.min(1, Math.max(-1, sentiment + (rng() - 0.5) * 0.3))),
    event_risk_scores: Array.from({ length: n }, () => Math.min(1, Math.max(0, eventRisk + (rng() - 0.5) * 0.15))),
    btc_reference_prices: Array.from({ length: n }, (_, i) => Math.max(1, base + i * trend)),
    exposure: Math.min(0.95, Math.max(0.01, 0.1 + rng() * 0.7)),
    drawdown: Math.min(0.4, Math.max(0, rng() * (regime === 2 ? 0.35 : 0.1))),
    order_book_imbalance: Math.min(0.9, Math.max(0, (rng() - 0.5) * 1.2 + 0.15)),
    order_book_depth: Math.min(3, Math.max(0.1, 0.3 + rng() * 2.5)),
    slippage_bps: regime === 3 ? 10 + rng() * 25 : 1 + rng() * 8,
  };
}

export function defaultBankState(seed?: number): BankState {
  const rng = makeLCG(seed ?? Date.now());
  // Profil aléatoire : normal / suspect / fraude / gros virement
  const profile = Math.floor(rng() * 4); // 0=normal, 1=suspect, 2=fraude, 3=gros
  const isFraud = profile === 2;
  const isSuspect = profile === 1;
  const isLarge = profile === 3;
  const channels = ["mobile", "web", "branch", "api"] as const;
  return {
    transaction_type: isLarge ? "WIRE" : ["TRANSFER", "PAYMENT", "WITHDRAWAL"][Math.floor(rng() * 3)],
    amount: isLarge ? 5000 + rng() * 15000 : isFraud ? 800 + rng() * 3000 : 200 + rng() * 2000,
    channel: channels[Math.floor(rng() * channels.length)],
    counterparty_known: isFraud ? rng() < 0.2 : rng() > 0.3,
    counterparty_age_days: isFraud ? Math.floor(rng() * 10) : Math.floor(30 + rng() * 500),
    account_balance: 3000 + rng() * 50000,
    available_cash: 1000 + rng() * 30000,
    historical_avg_amount: 100 + rng() * 1500,
    behavior_shift_score: isFraud ? 0.6 + rng() * 0.4 : isSuspect ? 0.4 + rng() * 0.3 : rng() * 0.35,
    fraud_score: isFraud ? 0.65 + rng() * 0.35 : isSuspect ? 0.3 + rng() * 0.3 : rng() * 0.25,
    policy_limit: 3000 + rng() * 10000,
    affordability_score: isFraud ? rng() * 0.5 : 0.5 + rng() * 0.5,
    urgency_score: isFraud ? 0.6 + rng() * 0.4 : rng() * 0.5,
    identity_mismatch_score: isFraud ? 0.5 + rng() * 0.5 : rng() * 0.3,
    narrative_conflict_score: isFraud ? 0.4 + rng() * 0.5 : rng() * 0.3,
    device_trust_score: isFraud ? rng() * 0.4 : 0.6 + rng() * 0.4,
    recent_failed_attempts: isFraud ? Math.floor(rng() * 5) : Math.floor(rng() * 2),
    elapsed_s: 50 + rng() * 300,
    min_required_elapsed_s: 108,
  };
}

export function defaultEcomState(seed?: number): EcomState {
  const rng = makeLCG(seed ?? Date.now());
  // Profil aléatoire : conversion / abandon / fraude / promo
  const profile = Math.floor(rng() * 4); // 0=normal, 1=abandon, 2=fraude, 3=promo
  const isFraud = profile === 2;
  const isAbandonment = profile === 1;
  const isPromo = profile === 3;
  return {
    session_id: `sess-${Date.now()}-${Math.floor(rng() * 9999)}`,
    traffic_quality: isFraud ? rng() * 0.35 : 0.45 + rng() * 0.55,
    basket_intent_score: isAbandonment ? rng() * 0.4 : isPromo ? 0.8 + rng() * 0.2 : 0.4 + rng() * 0.55,
    stock_ok: rng() > (isAbandonment ? 0.4 : 0.1),
    margin_rate: isPromo ? 0.02 + rng() * 0.08 : 0.1 + rng() * 0.3,
    roas: isPromo ? 3 + rng() * 3 : 1 + rng() * 3.5,
    conversion_readiness: isAbandonment ? rng() * 0.4 : 0.4 + rng() * 0.55,
    fulfillment_risk: isFraud ? 0.5 + rng() * 0.5 : rng() * 0.5,
    customer_trust: isFraud ? rng() * 0.3 : 0.4 + rng() * 0.6,
    intent_conflict_score: isFraud ? 0.6 + rng() * 0.4 : rng() * 0.4,
    checkout_friction_score: isAbandonment ? 0.5 + rng() * 0.5 : rng() * 0.45,
    merchant_policy_score: isFraud ? rng() * 0.5 : 0.5 + rng() * 0.5,
    basket_value: 20 + rng() * 500,
    ad_spend: 5 + rng() * 100,
    order_value: 20 + rng() * 500,
    x108_compliance_rate: isFraud ? rng() * 0.4 : 0.6 + rng() * 0.4,
  };
}

// ─── Scénarios prédéfinis par domaine ─────────────────────────────────────────
export type ScenarioId =
  | "flash_crash" | "bull_run" | "range_bound" | "high_volatility"
  | "large_transfer" | "fraud_attempt" | "normal_payment" | "limit_breach"
  | "high_roas" | "low_margin" | "cart_abandonment" | "fraud_checkout";

export function buildStateFromScenario(
  domain: "trading" | "bank" | "ecom",
  scenarioId: ScenarioId,
  seed: number
): DomainState {
  // Déterministe via seed (simple LCG pour variation)
  const rng = (n: number) => ((seed * 1664525 + n * 1013904223) & 0xffffffff) / 0xffffffff;

  if (domain === "trading") {
    const isFlashCrash = scenarioId === "flash_crash";
    const isBull = scenarioId === "bull_run";
    const isHighVol = scenarioId === "high_volatility";
    const n = 21;
    const base = 100 + rng(1) * 50;
    const trend = isFlashCrash ? -3 : isBull ? 2 : 0.5;
    const noise = isHighVol ? 5 : 1;
    return {
      symbol: "BTCUSDT",
      prices: Array.from({ length: n }, (_, i) => Math.max(1, base + i * trend + (rng(i) - 0.5) * noise * 2)),
      highs: Array.from({ length: n }, (_, i) => Math.max(1, base + i * trend + noise + rng(i + 100) * noise)),
      lows: Array.from({ length: n }, (_, i) => Math.max(1, base + i * trend - noise - rng(i + 200) * noise)),
      volumes: Array.from({ length: n }, (_, i) => 1000 + rng(i + 300) * 5000),
      spreads_bps: Array(n).fill(isHighVol ? 15 : 4),
      sentiment_scores: Array(n).fill(isFlashCrash ? -0.5 : isBull ? 0.7 : 0.2),
      event_risk_scores: Array(n).fill(isFlashCrash ? 0.8 : 0.15),
      btc_reference_prices: Array.from({ length: n }, (_, i) => Math.max(1, base + i * trend)),
      exposure: isFlashCrash ? 0.8 : 0.2,
      drawdown: isFlashCrash ? 0.15 : 0.01,
      order_book_imbalance: isFlashCrash ? 0.7 : 0.15,
      order_book_depth: isFlashCrash ? 0.3 : 1.2,
      slippage_bps: isHighVol ? 20 : 2,
    } as TradingState;
  }

  if (domain === "bank") {
    const isFraud = scenarioId === "fraud_attempt";
    const isLarge = scenarioId === "large_transfer";
    const isLimit = scenarioId === "limit_breach";
    return {
      transaction_type: isLarge ? "WIRE" : "TRANSFER",
      amount: isLarge ? 8000 : isLimit ? 5500 : 1200,
      channel: "mobile",
      counterparty_known: !isFraud,
      counterparty_age_days: isFraud ? 2 : 120,
      account_balance: 10000,
      available_cash: 8500,
      historical_avg_amount: 300,
      behavior_shift_score: isFraud ? 0.85 : 0.25,
      fraud_score: isFraud ? 0.9 : 0.10,
      policy_limit: 5000,
      affordability_score: isLarge ? 0.4 : 0.9,
      urgency_score: isFraud ? 0.9 : 0.2,
      identity_mismatch_score: isFraud ? 0.8 : 0.1,
      narrative_conflict_score: isFraud ? 0.7 : 0.1,
      device_trust_score: isFraud ? 0.2 : 0.95,
      recent_failed_attempts: isFraud ? 3 : 0,
      elapsed_s: 140,
      min_required_elapsed_s: 108,
    } as BankState;
  }

  // ecom
  const isHighRoas = scenarioId === "high_roas";
  const isLowMargin = scenarioId === "low_margin";
  const isFraudCheckout = scenarioId === "fraud_checkout";
  return {
    session_id: `sess-${seed}`,
    traffic_quality: isFraudCheckout ? 0.2 : 0.8,
    basket_intent_score: isHighRoas ? 0.95 : 0.76,
    stock_ok: true,
    margin_rate: isLowMargin ? 0.02 : 0.22,
    roas: isHighRoas ? 4.5 : 2.4,
    conversion_readiness: isHighRoas ? 0.92 : 0.77,
    fulfillment_risk: 0.22,
    customer_trust: isFraudCheckout ? 0.1 : 0.85,
    intent_conflict_score: isFraudCheckout ? 0.9 : 0.1,
    checkout_friction_score: 0.2,
    merchant_policy_score: 0.9,
    basket_value: 140,
    ad_spend: 20,
    order_value: 140,
    x108_compliance_rate: isFraudCheckout ? 0.2 : 0.95,
  } as EcomState;
}
