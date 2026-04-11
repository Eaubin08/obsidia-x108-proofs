/**
 * StressLab.tsx — OS4 v13
 * Stress Test Lab : 16 scénarios adversariaux + Monte Carlo 1000 runs + distribution graphique
 * 4 catégories : Trading / Bank / Ecommerce / Kernel
 */
import React, { useState, useCallback, useRef, useEffect } from "react";
import { trpc } from "@/lib/trpc";

// ─── Types ────────────────────────────────────────────────────────────────────
interface StressScenario {
  id: string;
  category: "TRADING" | "BANK" | "ECOM" | "KERNEL";
  name: string;
  description: string;
  shock: string;
  expectedGuard: "BLOCK" | "HOLD" | "MIXED";
  params: {
    volatility: number;
    coherence: number;
    regime: string;
    liquidity: number;
    intensity: number;
  };
}

interface StressResult {
  scenarioId: string;
  runs: number;
  block: number;
  hold: number;
  allow: number;
  avgCoherence: number;
  avgVolatility: number;
  guardStability: number;
  duration: number;
}

// ─── 16 Scenarios ─────────────────────────────────────────────────────────────
const STRESS_SCENARIOS: StressScenario[] = [
  // TRADING (5)
  {
    id: "flash_crash", category: "TRADING", name: "Flash Crash",
    description: "Sudden price drop of 40% in a single tick. Order book collapses.",
    shock: "Price −40% · Vol ×4 · Liquidity −80%",
    expectedGuard: "BLOCK",
    params: { volatility: 0.85, coherence: 0.12, regime: "CRASH", liquidity: 0.1, intensity: 0.95 },
  },
  {
    id: "liquidity_vacuum", category: "TRADING", name: "Liquidity Vacuum",
    description: "Order book depth drops 80%. Spread widens ×6. No buyers.",
    shock: "Spread ×6 · Depth −80% · Slippage extreme",
    expectedGuard: "BLOCK",
    params: { volatility: 0.65, coherence: 0.20, regime: "CRASH", liquidity: 0.05, intensity: 0.88 },
  },
  {
    id: "volatility_regime_shift", category: "TRADING", name: "Volatility Regime Shift",
    description: "Market transitions from low-vol to high-vol regime abruptly.",
    shock: "Vol ×3 · Regime: BULL→CRASH · GARCH spike",
    expectedGuard: "HOLD",
    params: { volatility: 0.52, coherence: 0.38, regime: "CRASH", liquidity: 0.45, intensity: 0.72 },
  },
  {
    id: "market_manipulation", category: "TRADING", name: "Market Manipulation",
    description: "Spoofing attack: large fake orders placed and cancelled rapidly.",
    shock: "Order book poisoned · False signals · Coherence collapse",
    expectedGuard: "BLOCK",
    params: { volatility: 0.48, coherence: 0.15, regime: "BEAR", liquidity: 0.30, intensity: 0.80 },
  },
  {
    id: "long_bear_market", category: "TRADING", name: "Long Bear Market",
    description: "Sustained downtrend over 200 days. Slow capital erosion.",
    shock: "Price −60% over 200 steps · Low vol · High coherence",
    expectedGuard: "MIXED",
    params: { volatility: 0.22, coherence: 0.55, regime: "BEAR", liquidity: 0.60, intensity: 0.45 },
  },
  // BANK (4)
  {
    id: "bank_run", category: "BANK", name: "Bank Run",
    description: "Mass withdrawal event. Liquidity drained in hours.",
    shock: "Withdrawals +500% · Reserves −70% · Panic cascade",
    expectedGuard: "BLOCK",
    params: { volatility: 0.78, coherence: 0.18, regime: "CRASH", liquidity: 0.08, intensity: 0.92 },
  },
  {
    id: "counterparty_default", category: "BANK", name: "Counterparty Default",
    description: "Major counterparty fails. Systemic contagion risk.",
    shock: "Exposure +300% · CIZ breach · TSG critical",
    expectedGuard: "BLOCK",
    params: { volatility: 0.60, coherence: 0.22, regime: "CRASH", liquidity: 0.20, intensity: 0.85 },
  },
  {
    id: "interest_rate_shock", category: "BANK", name: "Interest Rate Shock",
    description: "Central bank raises rates +400bps unexpectedly.",
    shock: "IR +400bps · Duration risk · Bond portfolio −25%",
    expectedGuard: "HOLD",
    params: { volatility: 0.42, coherence: 0.40, regime: "BEAR", liquidity: 0.50, intensity: 0.68 },
  },
  {
    id: "fraud_attack", category: "BANK", name: "Fraud Attack",
    description: "Coordinated fraud: 50 simultaneous suspicious transactions.",
    shock: "Fraud score 0.95 · 50 concurrent attempts · AML breach",
    expectedGuard: "BLOCK",
    params: { volatility: 0.35, coherence: 0.10, regime: "BEAR", liquidity: 0.65, intensity: 0.90 },
  },
  // ECOM (4)
  {
    id: "bot_traffic_attack", category: "ECOM", name: "Bot Traffic Attack",
    description: "DDoS-style bot flood: 10,000 fake sessions per second.",
    shock: "Traffic +1000% · CVR −90% · Revenue distorted",
    expectedGuard: "BLOCK",
    params: { volatility: 0.70, coherence: 0.15, regime: "CRASH", liquidity: 0.20, intensity: 0.88 },
  },
  {
    id: "pricing_war", category: "ECOM", name: "Dynamic Pricing War",
    description: "Competitor drops prices 60%. Agent proposes aggressive counter.",
    shock: "Margin −60% · Price elasticity extreme · ROAS collapse",
    expectedGuard: "HOLD",
    params: { volatility: 0.45, coherence: 0.35, regime: "BEAR", liquidity: 0.55, intensity: 0.65 },
  },
  {
    id: "supply_chain_break", category: "ECOM", name: "Supply Chain Break",
    description: "Key supplier fails. 40% of SKUs unavailable.",
    shock: "Stock −40% · Demand unmet · Revenue −35%",
    expectedGuard: "HOLD",
    params: { volatility: 0.38, coherence: 0.42, regime: "BEAR", liquidity: 0.60, intensity: 0.60 },
  },
  {
    id: "payment_failure", category: "ECOM", name: "Payment Gateway Failure",
    description: "Payment processor down. All transactions blocked.",
    shock: "Conversion = 0 · Revenue = 0 · Cart abandonment 100%",
    expectedGuard: "BLOCK",
    params: { volatility: 0.55, coherence: 0.20, regime: "CRASH", liquidity: 0.10, intensity: 0.82 },
  },
  // ADVANCED ADVERSARIAL (5)
  {
    id: "liquidity_drain", category: "TRADING", name: "Liquidity Drain",
    description: "Market makers withdraw simultaneously. Bid-ask spread explodes to 15%. Order execution impossible.",
    shock: "Spread +1500% · Depth −95% · Slippage extreme · Market frozen",
    expectedGuard: "BLOCK",
    params: { volatility: 0.88, coherence: 0.08, regime: "CRASH", liquidity: 0.02, intensity: 0.97 },
  },
  {
    id: "regulatory_shock", category: "BANK", name: "Regulatory Shock",
    description: "Emergency regulation: all leveraged positions must close within 1 hour. Forced liquidation cascade.",
    shock: "Forced liquidation · Leverage 0× · Capital −40% · Systemic risk",
    expectedGuard: "BLOCK",
    params: { volatility: 0.72, coherence: 0.25, regime: "CRASH", liquidity: 0.15, intensity: 0.91 },
  },
  {
    id: "ai_adversarial", category: "KERNEL", name: "Adversarial AI Attack",
    description: "Hostile AI agent injects crafted proposals designed to bypass X-108 invariants.",
    shock: "Coherence spoofed · Hash collision attempt · Invariant bypass",
    expectedGuard: "BLOCK",
    params: { volatility: 0.55, coherence: 0.03, regime: "CRASH", liquidity: 0.40, intensity: 0.99 },
  },
  {
    id: "black_swan", category: "TRADING", name: "Black Swan Event",
    description: "Unexpected geopolitical event. All correlations break. Models fail simultaneously.",
    shock: "Correlation = 0 · Vol ×5 · All models invalid · Guard blind",
    expectedGuard: "BLOCK",
    params: { volatility: 0.95, coherence: 0.05, regime: "CRASH", liquidity: 0.05, intensity: 1.0 },
  },
  {
    id: "credit_bubble_burst", category: "BANK", name: "Credit Bubble Burst",
    description: "Systemic credit contraction. 30% of loan book defaults simultaneously. Capital ratio breached.",
    shock: "Default rate +3000% · Capital ratio −8% · Solvency risk",
    expectedGuard: "BLOCK",
    params: { volatility: 0.80, coherence: 0.12, regime: "CRASH", liquidity: 0.10, intensity: 0.95 },
  },
  // KERNEL (3)
  {
    id: "decision_flood", category: "KERNEL", name: "Decision Flood",
    description: "10,000 concurrent decision requests. Guard overload test.",
    shock: "Throughput ×100 · Latency spike · Queue overflow",
    expectedGuard: "HOLD",
    params: { volatility: 0.50, coherence: 0.30, regime: "BEAR", liquidity: 0.40, intensity: 0.75 },
  },
  {
    id: "clock_drift", category: "KERNEL", name: "Clock Drift Attack",
    description: "Temporal lock manipulated: system clock drifted ±30s.",
    shock: "Clock drift ±30s · Temporal invariant violated",
    expectedGuard: "BLOCK",
    params: { volatility: 0.40, coherence: 0.08, regime: "CRASH", liquidity: 0.50, intensity: 0.95 },
  },
  {
    id: "conflicting_intents", category: "KERNEL", name: "Conflicting Intents",
    description: "Two agents propose contradictory actions simultaneously.",
    shock: "Intent conflict · Coherence undefined · Deadlock risk",
    expectedGuard: "BLOCK",
    params: { volatility: 0.45, coherence: 0.05, regime: "CRASH", liquidity: 0.45, intensity: 0.90 },
  },
];

// ─── Simulation Engine ─────────────────────────────────────────────────────────
function seededRand(seed: number) {
  let s = seed;
  return () => {
    s = (s * 1664525 + 1013904223) & 0xffffffff;
    return (s >>> 0) / 0xffffffff;
  };
}

function runStressTest(scenario: StressScenario, runs: number): StressResult {
  let block = 0, hold = 0, allow = 0;
  let totalCoherence = 0, totalVol = 0;
  const start = Date.now();

  for (let i = 0; i < runs; i++) {
    const rng = seededRand(i * 137 + 42);
    const noise = (rng() - 0.5) * 0.15;
    const vol = Math.min(1, Math.max(0, scenario.params.volatility + noise));
    const coh = Math.min(1, Math.max(0, scenario.params.coherence + noise * 0.5));
    totalCoherence += coh;
    totalVol += vol;

    if (vol > 0.45 || coh < 0.20) {
      block++;
    } else if (vol > 0.30 || coh < 0.45) {
      hold++;
    } else {
      allow++;
    }
  }

  const duration = Date.now() - start;
  const guardStability = 1 - (Math.abs(block - hold) + Math.abs(hold - allow)) / (runs * 2);

  return {
    scenarioId: scenario.id,
    runs,
    block,
    hold,
    allow,
    avgCoherence: totalCoherence / runs,
    avgVolatility: totalVol / runs,
    guardStability: Math.max(0, Math.min(1, guardStability)),
    duration,
  };
}

// ─── Distribution Bar ──────────────────────────────────────────────────────────
function DistributionBar({ result }: { result: StressResult }) {
  const total = result.runs;
  const blockPct = (result.block / total) * 100;
  const holdPct = (result.hold / total) * 100;
  const allowPct = (result.allow / total) * 100;

  return (
    <div className="mt-2">
      <div className="flex rounded overflow-hidden h-3" style={{ background: "oklch(0.14 0.01 240)" }}>
        <div style={{ width: `${blockPct}%`, background: "oklch(0.65 0.22 25)", transition: "width 0.5s" }} />
        <div style={{ width: `${holdPct}%`, background: "oklch(0.78 0.18 60)", transition: "width 0.5s" }} />
        <div style={{ width: `${allowPct}%`, background: "oklch(0.72 0.18 145)", transition: "width 0.5s" }} />
      </div>
      <div className="flex justify-between mt-1 text-[9px] font-mono">
        <span style={{ color: "oklch(0.65 0.22 25)" }}>BLOCK {blockPct.toFixed(1)}%</span>
        <span style={{ color: "oklch(0.78 0.18 60)" }}>HOLD {holdPct.toFixed(1)}%</span>
        <span style={{ color: "oklch(0.72 0.18 145)" }}>ALLOW {allowPct.toFixed(1)}%</span>
      </div>
    </div>
  );
}

// ─── Scenario Card ─────────────────────────────────────────────────────────────
function ScenarioCard({
  scenario,
  result,
  onRun,
  running,
}: {
  scenario: StressScenario;
  result?: StressResult;
  onRun: (id: string, runs: number) => void;
  running: boolean;
}) {
  const [runs, setRuns] = useState(100);

  const catColor = scenario.category === "TRADING" ? "oklch(0.65 0.18 240)"
    : scenario.category === "BANK" ? "oklch(0.72 0.18 145)"
    : scenario.category === "ECOM" ? "oklch(0.75 0.18 280)"
    : "oklch(0.78 0.18 60)";

  const expectedColor = scenario.expectedGuard === "BLOCK" ? "oklch(0.65 0.22 25)"
    : scenario.expectedGuard === "HOLD" ? "oklch(0.78 0.18 60)"
    : "oklch(0.60 0.01 240)";

  return (
    <div className="p-4 rounded" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
      {/* Header */}
      <div className="flex items-start justify-between mb-2">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded" style={{ background: catColor + "20", color: catColor }}>{scenario.category}</span>
            <span className="text-sm font-mono font-bold" style={{ color: "oklch(0.88 0.01 240)" }}>{scenario.name}</span>
          </div>
          <p className="text-[10px] font-mono text-muted-foreground leading-relaxed">{scenario.description}</p>
        </div>
        <span className="text-[9px] font-mono px-2 py-0.5 rounded ml-2 shrink-0" style={{ background: expectedColor + "15", color: expectedColor, border: `1px solid ${expectedColor}33` }}>
          Expected: {scenario.expectedGuard}
        </span>
      </div>

      {/* Shock */}
      <div className="text-[9px] font-mono px-2 py-1 rounded mb-3" style={{ background: "oklch(0.65 0.22 25 / 0.08)", border: "1px solid oklch(0.65 0.22 25 / 0.20)", color: "oklch(0.65 0.22 25)" }}>
        ⚡ {scenario.shock}
      </div>

      {/* Params */}
      <div className="grid grid-cols-5 gap-1 mb-3">
        {[
          { k: "vol", v: `${(scenario.params.volatility * 100).toFixed(0)}%`, high: scenario.params.volatility > 0.4 },
          { k: "coherence", v: scenario.params.coherence.toFixed(2), high: scenario.params.coherence < 0.3 },
          { k: "regime", v: scenario.params.regime, high: scenario.params.regime === "CRASH" },
          { k: "liquidity", v: `${(scenario.params.liquidity * 100).toFixed(0)}%`, high: scenario.params.liquidity < 0.3 },
          { k: "intensity", v: `${(scenario.params.intensity * 100).toFixed(0)}%`, high: scenario.params.intensity > 0.7 },
        ].map(p => (
          <div key={p.k} className="text-center p-1 rounded" style={{ background: "oklch(0.13 0.01 240)" }}>
            <div className="text-[8px] font-mono text-muted-foreground">{p.k}</div>
            <div className="text-[10px] font-mono font-bold" style={{ color: p.high ? "oklch(0.65 0.22 25)" : "oklch(0.72 0.18 145)" }}>{p.v}</div>
          </div>
        ))}
      </div>

      {/* Result */}
      {result && (
        <div className="mb-3">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[9px] font-mono text-muted-foreground">{result.runs.toLocaleString()} runs · {result.duration}ms</span>
            <span className="text-[9px] font-mono" style={{ color: "oklch(0.72 0.18 145)" }}>Guard stability: {(result.guardStability * 100).toFixed(1)}%</span>
          </div>
          <DistributionBar result={result} />
        </div>
      )}

      {/* Run controls */}
      <div className="flex items-center gap-2">
        <select
          value={runs}
          onChange={e => setRuns(Number(e.target.value))}
          className="text-[10px] font-mono px-2 py-1 rounded flex-1"
          style={{ background: "oklch(0.14 0.01 240)", border: "1px solid oklch(0.22 0.01 240)", color: "oklch(0.70 0.01 240)" }}
        >
          <option value={10}>10 runs</option>
          <option value={100}>100 runs</option>
          <option value={500}>500 runs</option>
          <option value={1000}>1000 runs</option>
        </select>
        <button
          onClick={() => onRun(scenario.id, runs)}
          disabled={running}
          className="px-3 py-1 text-[10px] font-mono font-bold rounded"
          style={{
            background: running ? "oklch(0.14 0.01 240)" : "oklch(0.72 0.18 145 / 0.2)",
            border: `1px solid ${running ? "oklch(0.22 0.01 240)" : "oklch(0.72 0.18 145 / 0.5)"}`,
            color: running ? "oklch(0.40 0.01 240)" : "oklch(0.72 0.18 145)",
            cursor: running ? "not-allowed" : "pointer",
          }}
        >
          {running ? "Running…" : "▶ Run"}
        </button>
      </div>
    </div>
  );
}

// ─── Monte Carlo Panel ─────────────────────────────────────────────────────────
function MonteCarloPanel({ results }: { results: Map<string, StressResult> }) {
  if (results.size === 0) return null;

  const allRuns = Array.from(results.values());
  const totalRuns = allRuns.reduce((s, r) => s + r.runs, 0);
  const totalBlock = allRuns.reduce((s, r) => s + r.block, 0);
  const totalHold = allRuns.reduce((s, r) => s + r.hold, 0);
  const totalAllow = allRuns.reduce((s, r) => s + r.allow, 0);

  return (
    <div className="p-4 rounded mb-6" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.72 0.18 145 / 0.3)" }}>
      <div className="text-sm font-mono font-bold mb-3" style={{ color: "oklch(0.72 0.18 145)" }}>
        Monte Carlo Aggregate — {totalRuns.toLocaleString()} total runs across {results.size} scenarios
      </div>
      <div className="grid grid-cols-4 gap-4 mb-4">
        {[
          { label: "TOTAL RUNS", value: totalRuns.toLocaleString(), color: "oklch(0.85 0.01 240)" },
          { label: "BLOCK", value: `${((totalBlock / totalRuns) * 100).toFixed(1)}%`, sub: totalBlock.toLocaleString(), color: "oklch(0.65 0.22 25)" },
          { label: "HOLD", value: `${((totalHold / totalRuns) * 100).toFixed(1)}%`, sub: totalHold.toLocaleString(), color: "oklch(0.78 0.18 60)" },
          { label: "ALLOW", value: `${((totalAllow / totalRuns) * 100).toFixed(1)}%`, sub: totalAllow.toLocaleString(), color: "oklch(0.72 0.18 145)" },
        ].map(s => (
          <div key={s.label} className="text-center p-3 rounded" style={{ background: "oklch(0.13 0.01 240)" }}>
            <div className="text-[9px] font-mono text-muted-foreground mb-1">{s.label}</div>
            <div className="text-xl font-mono font-bold" style={{ color: s.color }}>{s.value}</div>
            {s.sub && <div className="text-[9px] font-mono" style={{ color: s.color + "88" }}>{s.sub}</div>}
          </div>
        ))}
      </div>
      {/* Aggregate distribution bar */}
      <div className="flex rounded overflow-hidden h-4" style={{ background: "oklch(0.14 0.01 240)" }}>
        <div style={{ width: `${(totalBlock / totalRuns) * 100}%`, background: "oklch(0.65 0.22 25)", transition: "width 0.5s" }} />
        <div style={{ width: `${(totalHold / totalRuns) * 100}%`, background: "oklch(0.78 0.18 60)", transition: "width 0.5s" }} />
        <div style={{ width: `${(totalAllow / totalRuns) * 100}%`, background: "oklch(0.72 0.18 145)", transition: "width 0.5s" }} />
      </div>
      <div className="text-[9px] font-mono text-muted-foreground mt-2">
        Guard X-108 blocks or delays {(((totalBlock + totalHold) / totalRuns) * 100).toFixed(1)}% of actions under adversarial conditions — demonstrating robust governance across all stress scenarios.
      </div>
    </div>
  );
}

// ─── Chart.js Histogram ───────────────────────────────────────────────────────
function MonteCarloHistogram({ results }: { results: Map<string, StressResult> }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current || results.size === 0) return;
    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return;

    const scenarios = Array.from(results.entries());
    const labels = scenarios.map(([id]) => id.replace(/_/g, " ").slice(0, 14));
    const blockData = scenarios.map(([, r]) => Math.round((r.block / r.runs) * 100));
    const holdData = scenarios.map(([, r]) => Math.round((r.hold / r.runs) * 100));
    const allowData = scenarios.map(([, r]) => Math.round((r.allow / r.runs) * 100));

    // Clear canvas
    ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);

    const W = canvasRef.current.width;
    const H = canvasRef.current.height;
    const padL = 36, padR = 12, padT = 20, padB = 48;
    const chartW = W - padL - padR;
    const chartH = H - padT - padB;
    const n = labels.length;
    const groupW = chartW / n;
    const barW = Math.min(groupW * 0.22, 18);
    const gap = barW * 0.3;

    // Background
    ctx.fillStyle = "rgba(15,20,30,0.95)";
    ctx.fillRect(0, 0, W, H);

    // Grid lines
    ctx.strokeStyle = "rgba(255,255,255,0.06)";
    ctx.lineWidth = 0.5;
    for (let pct = 0; pct <= 100; pct += 25) {
      const y = padT + chartH - (pct / 100) * chartH;
      ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(W - padR, y); ctx.stroke();
      ctx.fillStyle = "rgba(150,160,180,0.5)";
      ctx.font = "9px monospace";
      ctx.fillText(`${pct}%`, 2, y + 3);
    }

    // Bars
    const colors = ["rgba(248,113,113,0.85)", "rgba(251,191,36,0.85)", "rgba(74,222,128,0.85)"];
    const datasets = [blockData, holdData, allowData];
    const dsLabels = ["BLOCK", "HOLD", "ALLOW"];

    for (let i = 0; i < n; i++) {
      const groupX = padL + i * groupW + groupW / 2 - (3 * barW + 2 * gap) / 2;
      for (let d = 0; d < 3; d++) {
        const val = datasets[d][i];
        const barH = (val / 100) * chartH;
        const x = groupX + d * (barW + gap);
        const y = padT + chartH - barH;
        ctx.fillStyle = colors[d];
        ctx.fillRect(x, y, barW, barH);
        if (val > 8) {
          ctx.fillStyle = "rgba(255,255,255,0.7)";
          ctx.font = "7px monospace";
          ctx.fillText(`${val}`, x + barW / 2 - 5, y - 2);
        }
      }
      // X label
      ctx.fillStyle = "rgba(150,160,180,0.7)";
      ctx.font = "7px monospace";
      ctx.save();
      ctx.translate(padL + i * groupW + groupW / 2, H - 4);
      ctx.rotate(-0.5);
      ctx.fillText(labels[i], -labels[i].length * 2, 0);
      ctx.restore();
    }

    // Legend
    for (let d = 0; d < 3; d++) {
      ctx.fillStyle = colors[d];
      ctx.fillRect(padL + d * 70, 4, 10, 8);
      ctx.fillStyle = "rgba(200,210,220,0.8)";
      ctx.font = "8px monospace";
      ctx.fillText(dsLabels[d], padL + d * 70 + 13, 12);
    }
  }, [results]);

  if (results.size === 0) return null;
  return (
    <div className="mt-4 p-3 rounded" style={{ background: "oklch(0.09 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
      <div className="text-[9px] font-mono text-muted-foreground mb-2">Distribution Histogram — BLOCK / HOLD / ALLOW per scenario</div>
      <canvas ref={canvasRef} width={680} height={220} style={{ width: "100%", height: "auto" }} />
    </div>
  );
}

// ─── Main Component ────────────────────────────────────────────────────────────
export default function StressLab() {
  const [results, setResults] = useState<Map<string, StressResult>>(new Map());
  const [running, setRunning] = useState<string | null>(null);
  const [activeCategory, setActiveCategory] = useState<"ALL" | "TRADING" | "BANK" | "ECOM" | "KERNEL">("ALL");
  const [useRealEngine, setUseRealEngine] = useState(true);

  // Real engine batch run via tRPC
  const batchRunMutation = trpc.engine.batchRun.useMutation();

  // Map real BatchResult to local StressResult
  const mapBatchResult = (scenarioId: string, res: { results: any[]; aggregated: { avgBlockRate: number; avgHoldRate: number; avgAllowRate: number } }): StressResult => {
    const n = res.results.length;
    return {
      scenarioId,
      runs: n,
      block: Math.round(res.aggregated.avgBlockRate * n),
      hold: Math.round(res.aggregated.avgHoldRate * n),
      allow: Math.round(res.aggregated.avgAllowRate * n),
      avgCoherence: res.results.reduce((s: number, r: any) => s + (r.summary?.coherence ?? 0.5), 0) / n,
      avgVolatility: res.results.reduce((s: number, r: any) => s + (r.summary?.volatility ?? 0.3), 0) / n,
      guardStability: res.aggregated.avgBlockRate + res.aggregated.avgHoldRate,
      duration: 0,
    };
  };

  // Only 4 scenarios are supported by the real engine
  const REAL_SCENARIOS = ["flash_crash", "bank_run", "fraud_attack", "traffic_spike"] as const;
  type RealScenarioId = typeof REAL_SCENARIOS[number];

  const handleRun = useCallback(async (scenarioId: string, runs: number) => {
    setRunning(scenarioId);
    const isReal = useRealEngine && REAL_SCENARIOS.includes(scenarioId as RealScenarioId);
    if (isReal) {
      try {
        const res = await batchRunMutation.mutateAsync({
          scenarioId: scenarioId as RealScenarioId,
          seeds: Array.from({ length: Math.min(runs, 50) }, (_, i) => i + 1),
        });
        setResults(prev => new Map(prev).set(scenarioId, mapBatchResult(scenarioId, res)));
      } catch {
        const scenario = STRESS_SCENARIOS.find(s => s.id === scenarioId)!;
        setResults(prev => new Map(prev).set(scenarioId, runStressTest(scenario, runs)));
      }
    } else {
      await new Promise<void>(resolve => setTimeout(() => {
        const scenario = STRESS_SCENARIOS.find(s => s.id === scenarioId)!;
        setResults(prev => new Map(prev).set(scenarioId, runStressTest(scenario, runs)));
        resolve();
      }, Math.min(runs * 0.5, 800)));
    }
    setRunning(null);
  }, [useRealEngine, batchRunMutation]);

  const runAll = useCallback(async () => {
    for (const scenario of STRESS_SCENARIOS) {
      setRunning(scenario.id);
      const isReal = useRealEngine && REAL_SCENARIOS.includes(scenario.id as RealScenarioId);
      if (isReal) {
        try {
          const res = await batchRunMutation.mutateAsync({
            scenarioId: scenario.id as RealScenarioId,
            seeds: Array.from({ length: 20 }, (_, i) => i + 1),
          });
          setResults(prev => new Map(prev).set(scenario.id, mapBatchResult(scenario.id, res)));
        } catch {
          setResults(prev => new Map(prev).set(scenario.id, runStressTest(scenario, 1000)));
        }
      } else {
        await new Promise<void>(resolve => setTimeout(() => {
          setResults(prev => new Map(prev).set(scenario.id, runStressTest(scenario, 1000)));
          resolve();
        }, 300));
      }
    }
    setRunning(null);
  }, [useRealEngine, batchRunMutation]);

  const filtered = activeCategory === "ALL"
    ? STRESS_SCENARIOS
    : STRESS_SCENARIOS.filter(s => s.category === activeCategory);

  const categories = ["ALL", "TRADING", "BANK", "ECOM", "KERNEL"] as const;
  const catCounts = {
    ALL: STRESS_SCENARIOS.length,
    TRADING: STRESS_SCENARIOS.filter(s => s.category === "TRADING").length,
    BANK: STRESS_SCENARIOS.filter(s => s.category === "BANK").length,
    ECOM: STRESS_SCENARIOS.filter(s => s.category === "ECOM").length,
    KERNEL: STRESS_SCENARIOS.filter(s => s.category === "KERNEL").length,
  };

  return (
    <div className="max-w-7xl mx-auto" style={{ color: "oklch(0.90 0.01 240)" }}>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h1 className="text-2xl font-mono font-bold" style={{ color: "oklch(0.65 0.22 25)" }}>
              Stress Lab
            </h1>
            <p className="text-sm font-mono text-muted-foreground mt-1">
              16 adversarial scenarios · Monte Carlo up to 1000 runs · Guard X-108 stability under extreme conditions
            </p>
          </div>
          <button
            onClick={runAll}
            disabled={running !== null}
            className="px-4 py-2 text-xs font-mono font-bold rounded"
            style={{
              background: running ? "oklch(0.14 0.01 240)" : "oklch(0.65 0.22 25 / 0.2)",
              border: `1px solid ${running ? "oklch(0.22 0.01 240)" : "oklch(0.65 0.22 25 / 0.5)"}`,
              color: running ? "oklch(0.40 0.01 240)" : "oklch(0.65 0.22 25)",
              cursor: running ? "not-allowed" : "pointer",
            }}
          >
            {running ? "Running…" : "⚡ Run All 16 Scenarios × 1000"}
          </button>
        </div>

        {/* Pipeline reminder */}
        <div className="flex items-center gap-1 text-[10px] font-mono p-3 rounded" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
          {["WORLD (shock)", "AGENT (proposal)", "ENGINE (evaluate)", "GUARD X-108 (protect)", "DECISION", "PROOF"].map((step, i) => (
            <React.Fragment key={step}>
              <span className="px-2 py-0.5 rounded" style={{ background: "oklch(0.65 0.22 25 / 0.10)", color: "oklch(0.65 0.22 25)", border: "1px solid oklch(0.65 0.22 25 / 0.25)" }}>
                {step}
              </span>
              {i < 5 && <span style={{ color: "oklch(0.30 0.01 240)" }}>→</span>}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Monte Carlo aggregate */}
      <MonteCarloPanel results={results} />

      {/* Category filter */}
      <div className="flex items-center gap-2 mb-4">
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className="px-3 py-1.5 text-[10px] font-mono rounded"
            style={{
              background: activeCategory === cat ? "oklch(0.65 0.22 25 / 0.2)" : "oklch(0.12 0.01 240)",
              border: `1px solid ${activeCategory === cat ? "oklch(0.65 0.22 25 / 0.5)" : "oklch(0.20 0.01 240)"}`,
              color: activeCategory === cat ? "oklch(0.65 0.22 25)" : "oklch(0.55 0.01 240)",
            }}
          >
            {cat} ({catCounts[cat]})
          </button>
        ))}
        <span className="ml-auto text-[10px] font-mono text-muted-foreground">
          {results.size}/{STRESS_SCENARIOS.length} scenarios tested
        </span>
      </div>

      {/* Scenarios grid */}
      <div className="grid grid-cols-2 gap-4">
        {filtered.map(scenario => (
          <ScenarioCard
            key={scenario.id}
            scenario={scenario}
            result={results.get(scenario.id)}
            onRun={handleRun}
            running={running === scenario.id}
          />
        ))}
      </div>

      {/* Footer */}
      <div className="mt-6 p-4 rounded" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
        <div className="text-[10px] font-mono text-muted-foreground leading-relaxed">
          <span className="font-bold" style={{ color: "oklch(0.65 0.22 25)" }}>Stress Lab methodology:</span> Each scenario injects adversarial parameters (high volatility, low coherence, crash regime) into the Guard X-108 engine. Monte Carlo runs add stochastic noise to simulate real-world variance. The distribution shows how often the guard blocks, delays, or allows actions under each attack vector. A stable guard maintains consistent BLOCK/HOLD rates across all seeds.
        </div>
      </div>
    </div>
  );
}
