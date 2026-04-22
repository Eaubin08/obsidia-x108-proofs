/**
 * Predictions — Predictive Dashboard
 * Affiche les signaux faibles détectés par le système avant que les agents agissent.
 * Flux : Market → Prediction → Simulation → Agents → Decision → X-108 → Proof
 */
import React, { useState, useEffect } from "react";
import { Link, useLocation } from "wouter";
import { useViewMode } from "@/contexts/ViewModeContext";
import { trpc } from "@/lib/trpc";
import ProbabilityChart, { SimulationMarker } from "@/components/ProbabilityChart";

// ─── Types ────────────────────────────────────────────────────────────────────

type RiskLevel = "high" | "medium" | "low";
type Domain = "trading" | "bank" | "ecom";

interface Prediction {
  id: string;
  domain: Domain;
  level: RiskLevel;
  title: string;
  titleSimple: string;
  probability: number;
  window: string;
  indicators: string[];
  actions: string[];
  simulationRoute?: string;  // route vers /simulation-worlds ou /use-cases/*
  guardAdjustment?: {
    label: string;
    normalCoherence: number;
    defensiveCoherence: number;
    normalLock: number;
    defensiveLock: number;
  };
}

// ─── Static prediction data ───────────────────────────────────────────────────

const PREDICTIONS: Prediction[] = [
  // HIGH RISK
  {
    id: "flash-crash",
    domain: "trading",
    level: "high",
    title: "Flash Crash Risk",
    titleSimple: "Risque d'effondrement rapide du marché",
    probability: 73,
    window: "2–4 hours",
    indicators: [
      "Volatility clustering detected",
      "Order book thinning (depth -42%)",
      "Fear & Greed Index drop (28 → 14)",
      "Historical similarity to 2010 Flash Crash (87%)",
    ],
    actions: [
      "Reduce exposure to high-beta assets",
      "Enable defensive mode (coherence +0.10)",
      "Increase guard thresholds",
      "Prepare stop-loss orders",
    ],
    simulationRoute: "/use-cases/trading",
    guardAdjustment: {
      label: "Defensive Mode",
      normalCoherence: 0.30,
      defensiveCoherence: 0.40,
      normalLock: 10,
      defensiveLock: 15,
    },
  },
  {
    id: "supply-shock",
    domain: "ecom",
    level: "high",
    title: "Supply Shock Warning",
    titleSimple: "Rupture de stock imminente",
    probability: 82,
    window: "24–48 hours",
    indicators: [
      "Supplier disruption signals (3 suppliers)",
      "Inventory depletion rate +180%",
      "Competitor price increase +23%",
      "Logistics delay index elevated",
    ],
    actions: [
      "Prepare alternative suppliers immediately",
      "Adjust pricing strategy",
      "Reserve critical stock",
      "Notify customers of potential delays",
    ],
    simulationRoute: "/use-cases/ecommerce",
    guardAdjustment: {
      label: "Supply Guard",
      normalCoherence: 0.30,
      defensiveCoherence: 0.45,
      normalLock: 10,
      defensiveLock: 20,
    },
  },
  // MEDIUM RISK
  {
    id: "fraud-wave",
    domain: "bank",
    level: "medium",
    title: "Fraud Wave Risk",
    titleSimple: "Vague de fraude probable",
    probability: 58,
    window: "6–12 hours",
    indicators: [
      "Suspicious login patterns (+340%)",
      "Failed login spike (last 2h)",
      "Attack pattern similarity to Jan 2024 wave",
      "Unusual geographic distribution",
    ],
    actions: [
      "Enable enhanced monitoring",
      "Require 2FA for large withdrawals",
      "Increase Sentinel sensitivity",
      "Prepare fraud response team",
    ],
    simulationRoute: "/use-cases/banking",
    guardAdjustment: {
      label: "Sentinel Alert",
      normalCoherence: 0.30,
      defensiveCoherence: 0.38,
      normalLock: 10,
      defensiveLock: 12,
    },
  },
  {
    id: "market-regime",
    domain: "trading",
    level: "medium",
    title: "Regime Shift Signal",
    titleSimple: "Changement de tendance de marché",
    probability: 61,
    window: "4–8 hours",
    indicators: [
      "Bull/Bear transition probability elevated",
      "GARCH volatility clustering (σ² +2.3×)",
      "Markov regime probability: Crisis 61%",
      "Correlation breakdown across assets",
    ],
    actions: [
      "Rebalance portfolio toward defensive assets",
      "Reduce leverage",
      "Monitor VaR breach thresholds",
      "Activate scenario-based guard rules",
    ],
    simulationRoute: "/use-cases/trading",
  },
  // LOW RISK
  {
    id: "liquidity-pressure",
    domain: "bank",
    level: "low",
    title: "Liquidity Pressure",
    titleSimple: "Pression sur les liquidités",
    probability: 34,
    window: "48–72 hours",
    indicators: [
      "Withdrawal rate slightly elevated (+12%)",
      "Interbank rate uptick",
      "Deposit growth slowing",
    ],
    actions: [
      "Monitor liquidity ratios",
      "Prepare contingency funding",
      "Review loan portfolio",
    ],
  },
  {
    id: "ctr-drop",
    domain: "ecom",
    level: "low",
    title: "CTR Degradation Signal",
    titleSimple: "Baisse de performance publicitaire",
    probability: 28,
    window: "72–96 hours",
    indicators: [
      "CTR declining trend (-8% over 3 days)",
      "Ad fatigue indicators",
      "Competitor spend increase",
    ],
    actions: [
      "Refresh ad creatives",
      "Review targeting parameters",
      "Prepare budget reallocation",
    ],
  },
];

// ─── Constants ────────────────────────────────────────────────────────────────

const LEVEL_CONFIG: Record<RiskLevel, { label: string; color: string; bg: string; border: string; icon: string }> = {
  high:   { label: "HIGH RISK",   color: "#f87171", bg: "#f8717115", border: "#f8717133", icon: "🔴" },
  medium: { label: "MEDIUM RISK", color: "#fbbf24", bg: "#fbbf2415", border: "#fbbf2433", icon: "🟡" },
  low:    { label: "LOW RISK",    color: "oklch(0.72 0.18 145)", bg: "oklch(0.72 0.18 145 / 0.08)", border: "oklch(0.72 0.18 145 / 0.25)", icon: "🟢" },
};

const DOMAIN_CONFIG: Record<Domain, { label: string; color: string; icon: string }> = {
  trading: { label: "Trading",    color: "oklch(0.72 0.18 145)", icon: "📈" },
  bank:    { label: "Banking",    color: "oklch(0.60 0.12 200)", icon: "🏦" },
  ecom:    { label: "E-Commerce", color: "#f59e0b",              icon: "🛒" },
};

const FLUX_STEPS = [
  { id: "market",     label: "Market",     active: false },
  { id: "prediction", label: "Prediction", active: true },
  { id: "simulation", label: "Simulation", active: false },
  { id: "agents",     label: "Agents",     active: false },
  { id: "decision",   label: "Decision",   active: false },
  { id: "x108",       label: "X-108",      active: false },
  { id: "proof",      label: "Proof",      active: false },
];

// ─── Components ───────────────────────────────────────────────────────────────

function ProbabilityBar({ value, color }: { value: number; color: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 rounded-full overflow-hidden" style={{ height: "6px", background: "oklch(0.18 0.01 240)" }}>
        <div className="h-full rounded-full" style={{ width: `${value}%`, background: color }} />
      </div>
      <span className="font-mono font-bold text-sm" style={{ color, minWidth: "36px", textAlign: "right" }}>{value}%</span>
    </div>
  );
}

function GuardAdjustmentCard({ adj, color }: { adj: NonNullable<Prediction["guardAdjustment"]>; color: string }) {
  return (
    <div className="rounded-lg p-3 mt-3" style={{ background: "oklch(0.10 0.01 240)", border: `1px solid ${color}33` }}>
      <div className="font-mono text-[9px] font-bold tracking-widest mb-2" style={{ color }}>
        GUARD ADJUSTMENT — {adj.label.toUpperCase()}
      </div>
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
        <div className="rounded p-2" style={{ background: "oklch(0.13 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
          <div className="text-muted-foreground mb-1">Normal Mode</div>
          <div className="text-foreground">Coherence: <span style={{ color: "oklch(0.72 0.18 145)" }}>{adj.normalCoherence.toFixed(2)}</span></div>
          <div className="text-foreground">Lock: <span style={{ color: "oklch(0.72 0.18 145)" }}>{adj.normalLock}s</span></div>
        </div>
        <div className="rounded p-2" style={{ background: `${color}10`, border: `1px solid ${color}44` }}>
          <div className="mb-1" style={{ color }}>Defensive Mode</div>
          <div className="text-foreground">Coherence: <span style={{ color }}>+{adj.defensiveCoherence.toFixed(2)}</span></div>
          <div className="text-foreground">Lock: <span style={{ color }}>+{adj.defensiveLock}s</span></div>
        </div>
      </div>
    </div>
  );
}

function PredictionCard({ pred, isSimple }: { pred: Prediction; isSimple: boolean }) {
  const [expanded, setExpanded] = useState(false);
  const level = LEVEL_CONFIG[pred.level];
  const domain = DOMAIN_CONFIG[pred.domain];
  const [, navigate] = useLocation();

  return (
    <div className="rounded-lg overflow-hidden" style={{ border: `1px solid ${level.border}`, background: level.bg }}>
      {/* Header */}
      <button
        className="w-full text-left p-4"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-lg">{level.icon}</span>
            <div>
              <div className="font-mono font-bold text-sm text-foreground">
                {isSimple ? pred.titleSimple : pred.title}
              </div>
              <div className="flex items-center gap-2 mt-0.5">
                <span className="font-mono text-[9px] px-1.5 py-0.5 rounded font-bold" style={{ background: `${level.color}22`, color: level.color }}>{level.label}</span>
                <span className="font-mono text-[9px]" style={{ color: domain.color }}>{domain.icon} {domain.label}</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="font-mono font-bold text-xl" style={{ color: level.color }}>{pred.probability}%</div>
              <div className="font-mono text-[9px] text-muted-foreground">{pred.window}</div>
            </div>
            <span className="font-mono text-muted-foreground text-sm">{expanded ? "▲" : "▼"}</span>
          </div>
        </div>
        {/* Probability bar */}
        <div className="mt-3">
          <ProbabilityBar value={pred.probability} color={level.color} />
        </div>
      </button>

      {/* Expanded content */}
      {expanded && (
        <div className="px-4 pb-4 border-t" style={{ borderColor: level.border }}>
          <div className="grid grid-cols-2 gap-4 mt-4">
            {/* Indicators */}
            <div>
              <div className="font-mono text-[9px] font-bold tracking-widest mb-2 text-muted-foreground">TRIGGER INDICATORS</div>
              <div className="space-y-1.5">
                {pred.indicators.map((ind, i) => (
                  <div key={i} className="flex items-start gap-2 font-mono text-[10px] text-foreground">
                    <span style={{ color: level.color, flexShrink: 0 }}>▸</span>
                    <span>{ind}</span>
                  </div>
                ))}
              </div>
            </div>
            {/* Actions */}
            <div>
              <div className="font-mono text-[9px] font-bold tracking-widest mb-2 text-muted-foreground">RECOMMENDED ACTIONS</div>
              <div className="space-y-1.5">
                {pred.actions.map((act, i) => (
                  <div key={i} className="flex items-start gap-2 font-mono text-[10px] text-foreground">
                    <span style={{ color: "oklch(0.72 0.18 145)", flexShrink: 0 }}>→</span>
                    <span>{act}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
          {/* Guard adjustment */}
          {pred.guardAdjustment && (
            <GuardAdjustmentCard adj={pred.guardAdjustment} color={level.color} />
          )}

          {/* Simulate button */}
          {pred.simulationRoute && (
            <div className="mt-3 flex justify-end">
              <button
                onClick={(e) => { e.stopPropagation(); navigate(pred.simulationRoute!); }}
                className="flex items-center gap-2 px-4 py-2 rounded font-mono text-xs font-bold"
                style={{
                  background: level.color === "#f87171" ? "#f8717120" : level.color === "#fbbf24" ? "#fbbf2420" : "oklch(0.72 0.18 145 / 0.15)",
                  border: `1px solid ${level.color}44`,
                  color: level.color,
                }}
              >
                <span>▶</span>
                <span>Simuler ce scénario</span>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function Predictions() {
  const { isSimple } = useViewMode();
  const [domainFilter, setDomainFilter] = useState<Domain | "all">("all");
  const [levelFilter, setLevelFilter] = useState<RiskLevel | "all">("all");
  const [activeTab, setActiveTab] = useState<"live" | "history">("live");
  const [lastUpdated, setLastUpdated] = useState(new Date());

  // Live predictions from tRPC (probabilities computed from Binance data)
  const liveQuery = trpc.prediction.getLive.useQuery(undefined, {
    refetchInterval: 60000,
    staleTime: 30000,
  });
  const historyQuery = trpc.prediction.getHistory.useQuery(
    { limit: 20 },
    { enabled: activeTab === "history" }
  );

  // Simulation timestamps from portfolio_snapshots (last 24h) — for chart annotations
  const simTimestampsQuery = trpc.portfolio.getSimulationTimestamps.useQuery(
    { hours: 24 },
    { refetchInterval: 2 * 60 * 1000 } // refresh every 2 min
  );
  const simulationMarkers: SimulationMarker[] = simTimestampsQuery.data ?? [];

  // Merge live probabilities with static enriched data (indicators, titleSimple, guardAdjustment)
  const livePredictions: Prediction[] = liveQuery.data
    ? liveQuery.data.predictions.map((lp: { id: string; domain: Domain; level: RiskLevel; title: string; probability: number; window: string; triggers: string[]; actions: string[]; simulatePath?: string }) => {
        const staticMatch = PREDICTIONS.find(sp => sp.id === lp.id);
        return staticMatch
          ? { ...staticMatch, probability: lp.probability, level: lp.level }
          : {
              id: lp.id,
              domain: lp.domain,
              level: lp.level,
              title: lp.title,
              titleSimple: lp.title,
              probability: lp.probability,
              window: lp.window,
              indicators: lp.triggers,
              actions: lp.actions,
              simulationRoute: lp.simulatePath,
            };
      })
    : PREDICTIONS;

  useEffect(() => {
    if (liveQuery.data) setLastUpdated(new Date());
  }, [liveQuery.data]);

  const filtered = livePredictions
    .filter(p => domainFilter === "all" || p.domain === domainFilter)
    .filter(p => levelFilter === "all" || p.level === levelFilter);

  const highRisk   = filtered.filter(p => p.level === "high");
  const mediumRisk = filtered.filter(p => p.level === "medium");
  const lowRisk    = filtered.filter(p => p.level === "low");

  const totalHigh   = livePredictions.filter(p => p.level === "high").length;
  const totalMedium = livePredictions.filter(p => p.level === "medium").length;
  const totalLow    = livePredictions.filter(p => p.level === "low").length;

  const DOMAIN_TABS: { id: Domain | "all"; label: string; icon: string }[] = [
    { id: "all",     label: "All Domains", icon: "🌐" },
    { id: "trading", label: "Trading",     icon: "📈" },
    { id: "bank",    label: "Banking",     icon: "🏦" },
    { id: "ecom",    label: "E-Commerce",  icon: "🛒" },
  ];

  const LEVEL_TABS: { id: RiskLevel | "all"; label: string; color: string }[] = [
    { id: "all",    label: "All Levels", color: "oklch(0.55 0.01 240)" },
    { id: "high",   label: "High",       color: "#f87171" },
    { id: "medium", label: "Medium",     color: "#fbbf24" },
    { id: "low",    label: "Low",        color: "oklch(0.72 0.18 145)" },
  ];

  return (
    <div className="max-w-5xl mx-auto" style={{ color: "oklch(0.90 0.01 240)", paddingTop: "24px" }}>

      {/* Header */}
      <div className="mb-6">
        <div className="font-mono text-[9px] font-bold tracking-[0.3em] uppercase mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>OBSIDIA LABS — PREDICTIVE LAYER</div>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="font-mono font-bold text-3xl text-foreground">Predictions</h1>
              {liveQuery.isLoading && <span className="font-mono text-[9px] px-2 py-0.5 rounded" style={{ background: "oklch(0.72 0.18 145 / 0.15)", color: "oklch(0.72 0.18 145)" }}>FETCHING LIVE DATA...</span>}
            </div>
            <p className="font-mono text-sm max-w-2xl leading-relaxed" style={{ color: "oklch(0.55 0.01 240)" }}>
              {isSimple
                ? "Signaux d'alerte détectés avant que les agents agissent. La prédiction n'exécute rien — elle prépare le système."
                : "Weak signals detected upstream of agent execution. Predictions adjust guard thresholds without executing actions — governance remains intact."}
            </p>
          </div>
          <div className="text-right font-mono text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>
            <div className="flex items-center gap-1.5 justify-end">
              <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: "oklch(0.72 0.18 145)" }} />
              <span style={{ color: "oklch(0.72 0.18 145)" }}>LIVE</span>
            </div>
            <div className="mt-0.5">Updated {lastUpdated.toLocaleTimeString()}</div>
          </div>
        </div>
      </div>

      {/* Live / History tabs */}
      <div className="flex gap-2 mb-6">
        {(["live", "history"] as const).map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)}
            className="px-4 py-2 rounded font-mono text-xs font-bold"
            style={{
              background: activeTab === tab ? "oklch(0.72 0.18 145 / 0.15)" : "oklch(0.12 0.01 240)",
              border: `1px solid ${activeTab === tab ? "oklch(0.72 0.18 145)" : "oklch(0.20 0.01 240)"}`,
              color: activeTab === tab ? "oklch(0.72 0.18 145)" : "oklch(0.50 0.01 240)",
            }}>
            {tab === "live" ? "🔴 Live Predictions" : "📋 History"}
          </button>
        ))}
      </div>

      {/* Flux visuel */}
      <div className="rounded-lg p-3 mb-6 flex items-center gap-1 flex-wrap" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
        {FLUX_STEPS.map((step, i) => (
          <React.Fragment key={step.id}>
            <div className="px-2.5 py-1 rounded font-mono text-[9px] font-bold"
              style={{
                background: step.active ? "oklch(0.72 0.18 145 / 0.15)" : "oklch(0.14 0.01 240)",
                color: step.active ? "oklch(0.72 0.18 145)" : "oklch(0.45 0.01 240)",
                border: step.active ? "1px solid oklch(0.72 0.18 145 / 0.4)" : "1px solid oklch(0.20 0.01 240)",
              }}>
              {step.label}
            </div>
            {i < FLUX_STEPS.length - 1 && (
              <span className="font-mono text-[10px]" style={{ color: "oklch(0.30 0.01 240)" }}>→</span>
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          { level: "high" as RiskLevel, count: totalHigh, label: "High Risk Events" },
          { level: "medium" as RiskLevel, count: totalMedium, label: "Medium Risk Events" },
          { level: "low" as RiskLevel, count: totalLow, label: "Low Risk Signals" },
        ].map(({ level, count, label }) => {
          const cfg = LEVEL_CONFIG[level];
          return (
            <div key={level} className="rounded-lg p-4" style={{ background: cfg.bg, border: `1px solid ${cfg.border}` }}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">{cfg.icon}</span>
                <span className="font-mono text-[9px] font-bold tracking-widest" style={{ color: cfg.color }}>{cfg.label}</span>
              </div>
              <div className="font-mono font-bold text-3xl" style={{ color: cfg.color }}>{count}</div>
              <div className="font-mono text-[9px] text-muted-foreground mt-1">{label}</div>
            </div>
          );
        })}
      </div>

      {/* Filters row */}
      <div className="flex flex-wrap gap-4 mb-6">
        {/* Domain filter */}
        <div>
          <div className="font-mono text-[9px] font-bold tracking-widest mb-1.5" style={{ color: "oklch(0.40 0.01 240)" }}>DOMAIN</div>
          <div className="flex gap-1.5">
            {DOMAIN_TABS.map(tab => (
              <button key={tab.id} onClick={() => setDomainFilter(tab.id)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded font-mono text-xs font-bold"
                style={{
                  background: domainFilter === tab.id ? "oklch(0.72 0.18 145 / 0.15)" : "oklch(0.12 0.01 240)",
                  border: `1px solid ${domainFilter === tab.id ? "oklch(0.72 0.18 145)" : "oklch(0.20 0.01 240)"}`,
                  color: domainFilter === tab.id ? "oklch(0.72 0.18 145)" : "oklch(0.50 0.01 240)",
                }}>
                <span>{tab.icon}</span><span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
        {/* Level filter */}
        <div>
          <div className="font-mono text-[9px] font-bold tracking-widest mb-1.5" style={{ color: "oklch(0.40 0.01 240)" }}>RISK LEVEL</div>
          <div className="flex gap-1.5">
            {LEVEL_TABS.map(tab => (
              <button key={tab.id} onClick={() => setLevelFilter(tab.id)}
                className="px-3 py-1.5 rounded font-mono text-xs font-bold"
                style={{
                  background: levelFilter === tab.id ? `${tab.color}20` : "oklch(0.12 0.01 240)",
                  border: `1px solid ${levelFilter === tab.id ? tab.color : "oklch(0.20 0.01 240)"}`,
                  color: levelFilter === tab.id ? tab.color : "oklch(0.50 0.01 240)",
                }}>
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 24h Probability Trend Chart — visible only in Live tab */}
      {activeTab === "live" && (
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-base">📈</span>
            <span className="font-mono font-bold text-sm" style={{ color: "oklch(0.72 0.18 145)" }}>24H PROBABILITY TREND</span>
            <span className="font-mono text-[9px] px-2 py-0.5 rounded" style={{ background: "oklch(0.72 0.18 145 / 0.10)", color: "oklch(0.72 0.18 145)" }}>LIVE</span>
            {domainFilter !== "all" && (
              <span className="font-mono text-[9px] px-2 py-0.5 rounded" style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.50 0.01 240)" }}>
                {domainFilter.toUpperCase()}
              </span>
            )}
          </div>
          <ProbabilityChart
            activeDomain={domainFilter !== "all" ? domainFilter as "trading" | "bank" | "ecom" : undefined}
            height={260}
            simulationMarkers={simulationMarkers}
          />
        </div>
      )}

      {/* Predictions by level */}
      <div className="space-y-8">
        {/* High risk */}
        {highRisk.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-base">🔴</span>
              <span className="font-mono font-bold text-sm" style={{ color: "#f87171" }}>HIGH PROBABILITY EVENTS</span>
              <span className="font-mono text-[9px] px-2 py-0.5 rounded" style={{ background: "#f8717120", color: "#f87171" }}>{highRisk.length}</span>
            </div>
            <div className="space-y-3">
              {highRisk.map(pred => <PredictionCard key={pred.id} pred={pred} isSimple={isSimple} />)}
            </div>
          </div>
        )}

        {/* Medium risk */}
        {mediumRisk.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-base">🟡</span>
              <span className="font-mono font-bold text-sm" style={{ color: "#fbbf24" }}>MEDIUM PROBABILITY EVENTS</span>
              <span className="font-mono text-[9px] px-2 py-0.5 rounded" style={{ background: "#fbbf2420", color: "#fbbf24" }}>{mediumRisk.length}</span>
            </div>
            <div className="space-y-3">
              {mediumRisk.map(pred => <PredictionCard key={pred.id} pred={pred} isSimple={isSimple} />)}
            </div>
          </div>
        )}

        {/* Low risk */}
        {lowRisk.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-base">🟢</span>
              <span className="font-mono font-bold text-sm" style={{ color: "oklch(0.72 0.18 145)" }}>LOW RISK SIGNALS</span>
              <span className="font-mono text-[9px] px-2 py-0.5 rounded" style={{ background: "oklch(0.72 0.18 145 / 0.15)", color: "oklch(0.72 0.18 145)" }}>{lowRisk.length}</span>
            </div>
            <div className="space-y-3">
              {lowRisk.map(pred => <PredictionCard key={pred.id} pred={pred} isSimple={isSimple} />)}
            </div>
          </div>
        )}

        {filtered.length === 0 && (
          <div className="text-center py-12 font-mono text-muted-foreground">
            No predictions for this domain.
          </div>
        )}
      </div>

      {/* History tab content */}
      {activeTab === "history" && (
        <div className="space-y-3 mb-8">
          <div className="font-mono text-[9px] font-bold tracking-widest mb-4" style={{ color: "oklch(0.45 0.01 240)" }}>PREDICTION HISTORY — RESOLVED EVENTS</div>
          {historyQuery.isLoading && (
            <div className="text-center py-8 font-mono text-muted-foreground text-sm">Loading history...</div>
          )}
          {historyQuery.data && historyQuery.data.map((row: { id: number; predictionId: string; title: string; domain: string; level: string; probability: number; window: string; outcome: string; createdAt: Date | string; resolvedAt: Date | string | null }) => {
            const outcomeColor = row.outcome === "confirmed" ? "#f87171" : row.outcome === "refuted" ? "oklch(0.72 0.18 145)" : "#fbbf24";
            const outcomeIcon = row.outcome === "confirmed" ? "⚠️" : row.outcome === "refuted" ? "✅" : "⏳";
            const domainIcon = row.domain === "trading" ? "📈" : row.domain === "bank" ? "🏦" : "🛒";
            return (
              <div key={row.id} className="rounded-lg p-4 flex items-center justify-between" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
                <div className="flex items-center gap-3">
                  <span className="text-base">{outcomeIcon}</span>
                  <div>
                    <div className="font-mono font-bold text-sm text-foreground">{row.title}</div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="font-mono text-[9px]" style={{ color: "oklch(0.50 0.01 240)" }}>{domainIcon} {row.domain}</span>
                      <span className="font-mono text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>•</span>
                      <span className="font-mono text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>{new Date(row.createdAt).toLocaleDateString()}</span>
                      {row.resolvedAt && <><span className="font-mono text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>→</span><span className="font-mono text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>{new Date(row.resolvedAt).toLocaleDateString()}</span></>}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="font-mono font-bold text-lg" style={{ color: outcomeColor }}>{row.probability}%</div>
                    <div className="font-mono text-[9px] text-muted-foreground">{row.window}</div>
                  </div>
                  <div className="px-2.5 py-1 rounded font-mono text-[9px] font-bold" style={{ background: `${outcomeColor}20`, color: outcomeColor, border: `1px solid ${outcomeColor}44` }}>
                    {row.outcome.toUpperCase()}
                  </div>
                </div>
              </div>
            );
          })}
          {historyQuery.data && historyQuery.data.length === 0 && (
            <div className="text-center py-8 font-mono text-muted-foreground text-sm">No history yet.</div>
          )}
        </div>
      )}

      {/* Footer note */}
      <div className="mt-10 rounded-lg p-4" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
        <div className="font-mono text-[9px] font-bold tracking-widest mb-2 text-muted-foreground">PREDICTION ROLE — IMPORTANT</div>
        <div className="grid grid-cols-2 gap-4 font-mono text-[10px]">
          <div>
            <p className="text-foreground leading-relaxed">
              {isSimple
                ? "Les prédictions ne déclenchent aucune action. Elles ajustent uniquement les paramètres de surveillance du moteur X-108 pour le préparer à un événement probable."
                : "Predictions never execute actions directly. They modify the guard configuration context — adjusting coherence thresholds and temporal lock durations — so agents operate under stricter rules when risk is elevated."}
            </p>
          </div>
          <div className="space-y-1">
            <div className="flex justify-between"><span style={{ color: "oklch(0.72 0.18 145)" }}>Prediction</span><span className="text-muted-foreground">→ anticipates</span></div>
            <div className="flex justify-between"><span style={{ color: "oklch(0.60 0.12 200)" }}>Simulation</span><span className="text-muted-foreground">→ tests</span></div>
            <div className="flex justify-between"><span style={{ color: "#f59e0b" }}>Agents</span><span className="text-muted-foreground">→ propose</span></div>
            <div className="flex justify-between"><span style={{ color: "oklch(0.72 0.18 145)" }}>X-108</span><span className="text-muted-foreground">→ decides</span></div>
            <div className="flex justify-between"><span style={{ color: "oklch(0.65 0.01 240)" }}>Proof</span><span className="text-muted-foreground">→ proves</span></div>
          </div>
        </div>
      </div>
    </div>
  );
}
