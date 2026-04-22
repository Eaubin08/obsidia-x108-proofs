import React, { useState, useEffect, useCallback, useRef } from "react";
import { Link } from "wouter";

// ─── Types ────────────────────────────────────────────────────────────────────

type Verdict = "ALLOW" | "HOLD" | "BLOCK";
type ScenarioId = "flash_crash" | "fraud_wave" | "supply_shock";

interface PipelineStep {
  stage: string;
  icon: string;
  color: string;
  title: string;
  label: string;
  detail: string;
  verdict?: Verdict;
}

interface Scenario {
  id: ScenarioId;
  title: string;
  subtitle: string;
  domain: string;
  domainColor: string;
  agent: string;
  verdict: Verdict;
  threat: string;
  steps: PipelineStep[];
  stats: { label: string; value: string; color?: string }[];
}

// ─── Scenarios ────────────────────────────────────────────────────────────────

const SCENARIOS: Scenario[] = [
  {
    id: "flash_crash",
    title: "Flash Crash",
    subtitle: "BTC volatility spike — Agent Alpha proposes SELL",
    domain: "Trading",
    domainColor: "#3b82f6",
    agent: "Alpha",
    verdict: "BLOCK",
    threat: "HIGH RISK",
    steps: [
      { stage: "market",  icon: "🌍", color: "#60a5fa", title: "Market Event",       label: "BTC volatility spike detected",       detail: "Volatility: 0.81 · Trend: downward · Volume: +220% · Window: 2–4h" },
      { stage: "agent",   icon: "🤖", color: "#a78bfa", title: "Agent Alpha",         label: "Signal: SELL BTC",                    detail: "Confidence: 0.41 · Risk score: 0.73 · Strategy: momentum · Proposal: SELL 2.4 BTC" },
      { stage: "predict", icon: "📡", color: "#f59e0b", title: "Prediction Engine",   label: "Flash crash probability: 63%",        detail: "Model: temporal LSTM · Window: 2h · Guard thresholds adjusted · HIGH RISK" },
      { stage: "guard",   icon: "🛡", color: "#34d399", title: "Guard X-108",         label: "Coherence 0.41 — threshold 0.18 ✓",  detail: "Risk score 0.73 exceeds limit 0.60 · Consensus: 4/4 · Temporal lock: 10s" },
      { stage: "verdict", icon: "⚖️", color: "#f87171", title: "Verdict",             label: "BLOCK",                               detail: "Action rejected — risk score exceeds threshold · Capital protected: $18,400", verdict: "BLOCK" },
      { stage: "proof",   icon: "🔐", color: "#34d399", title: "Proof Generated",     label: "Merkle anchor: a3f8c2d1…",            detail: "Root: a3f8c2d1e9b4 · Timestamp immutable · Lean invariant: BLOCK_VALID ✓" },
    ],
    stats: [
      { label: "Capital Protected", value: "$18,400", color: "#34d399" },
      { label: "Risk Score",        value: "0.73",    color: "#f87171" },
      { label: "Confidence",        value: "0.41",    color: "#f59e0b" },
      { label: "Verdict",           value: "BLOCK",   color: "#f87171" },
    ],
  },
  {
    id: "fraud_wave",
    title: "Fraud Wave",
    subtitle: "Suspicious transfer €50k — Agent Sentinel evaluates",
    domain: "Banking",
    domainColor: "#22c55e",
    agent: "Sentinel",
    verdict: "ALLOW",
    threat: "LOW RISK",
    steps: [
      { stage: "market",  icon: "🌍", color: "#60a5fa", title: "Market Event",       label: "Large transfer request €50k",         detail: "Amount: €50,000 · Recipient: external · Fraud score: 0.12 · KYC: verified" },
      { stage: "agent",   icon: "🤖", color: "#a78bfa", title: "Agent Sentinel",      label: "Signal: ALLOW transfer",              detail: "Confidence: 0.88 · Risk score: 0.12 · Strategy: compliance · All checks passed" },
      { stage: "predict", icon: "📡", color: "#f59e0b", title: "Prediction Engine",   label: "Fraud probability: 8%",               detail: "Model: anomaly detection · Window: immediate · Thresholds nominal · LOW RISK" },
      { stage: "guard",   icon: "🛡", color: "#34d399", title: "Guard X-108",         label: "Coherence 0.88 — threshold 0.18 ✓",  detail: "Risk score 0.12 within limits · Consensus: 4/4 · Temporal lock: expired" },
      { stage: "verdict", icon: "⚖️", color: "#4ade80", title: "Verdict",             label: "ALLOW",                               detail: "Action executed immediately — all criteria met · Transfer authorized", verdict: "ALLOW" },
      { stage: "proof",   icon: "🔐", color: "#34d399", title: "Proof Generated",     label: "Merkle anchor: b7e2f9a3…",            detail: "Root: b7e2f9a3c1d8 · Timestamp immutable · Lean invariant: ALLOW_VALID ✓" },
    ],
    stats: [
      { label: "Transfer Amount",   value: "€50,000", color: "#4ade80" },
      { label: "Fraud Score",       value: "0.12",    color: "#4ade80" },
      { label: "Confidence",        value: "0.88",    color: "#4ade80" },
      { label: "Verdict",           value: "ALLOW",   color: "#4ade80" },
    ],
  },
  {
    id: "supply_shock",
    title: "Supply Shock",
    subtitle: "Traffic surge +340% — Agent Mercury proposes PROMOTE",
    domain: "E-Commerce",
    domainColor: "#a855f7",
    agent: "Mercury",
    verdict: "HOLD",
    threat: "MEDIUM RISK",
    steps: [
      { stage: "market",  icon: "🌍", color: "#60a5fa", title: "Market Event",       label: "Traffic surge +340% detected",        detail: "Impressions: +340% · CVR: 0.04 · ROAS: 2.1 · Competitor price drop: -18%" },
      { stage: "agent",   icon: "🤖", color: "#a78bfa", title: "Agent Mercury",       label: "Signal: PROMOTE — flash sale",        detail: "Confidence: 0.67 · Risk score: 0.31 · Strategy: growth · Margin risk: medium" },
      { stage: "predict", icon: "📡", color: "#f59e0b", title: "Prediction Engine",   label: "Revenue uplift probability: 71%",     detail: "Model: demand forecast · Window: 24h · Margin risk detected · MEDIUM" },
      { stage: "guard",   icon: "🛡", color: "#34d399", title: "Guard X-108",         label: "Coherence 0.67 — threshold 0.18 ✓",  detail: "Risk score 0.31 within limits · Temporal lock: 10s remaining · Waiting..." },
      { stage: "verdict", icon: "⚖️", color: "#fbbf24", title: "Verdict",             label: "HOLD",                                detail: "Action valid — verrou temporel active · Executing in 10s · Margin protected", verdict: "HOLD" },
      { stage: "proof",   icon: "🔐", color: "#34d399", title: "Proof Generated",     label: "Merkle anchor: c9d4a1e7…",            detail: "Root: c9d4a1e7f2b5 · Timestamp immutable · Lean invariant: HOLD_VALID ✓" },
    ],
    stats: [
      { label: "Revenue Uplift",    value: "+71%",    color: "#fbbf24" },
      { label: "Risk Score",        value: "0.31",    color: "#fbbf24" },
      { label: "Confidence",        value: "0.67",    color: "#a78bfa" },
      { label: "Verdict",           value: "HOLD",    color: "#fbbf24" },
    ],
  },
];

const VERDICT_META: Record<Verdict, { color: string; bg: string; icon: string; desc: string }> = {
  ALLOW: { color: "#4ade80", bg: "rgba(74,222,128,0.12)",  icon: "✅", desc: "Action executed immediately" },
  HOLD:  { color: "#fbbf24", bg: "rgba(251,191,36,0.12)",  icon: "⏳", desc: "Action valid — verrou temporel active" },
  BLOCK: { color: "#f87171", bg: "rgba(248,113,113,0.12)", icon: "⛔", desc: "Action rejected — risk exceeded" },
};

// ─── Main Component ───────────────────────────────────────────────────────────

export default function DemoPage() {
  const [scenarioIdx, setScenarioIdx] = useState(0);
  const [activeStep, setActiveStep] = useState(0);
  const [running, setRunning] = useState(false);
  const [loop, setLoop] = useState(true);
  const [completedCount, setCompletedCount] = useState(0);
  const [history, setHistory] = useState<Array<{ scenario: ScenarioId; verdict: Verdict; ts: string }>>([]);
  const intervalRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const scenario = SCENARIOS[scenarioIdx];

  const startScenario = useCallback((idx: number) => {
    setScenarioIdx(idx);
    setActiveStep(0);
    setRunning(true);
  }, []);

  // Step animation
  useEffect(() => {
    if (!running) return;
    if (activeStep >= scenario.steps.length) {
      setRunning(false);
      setCompletedCount(c => c + 1);
      setHistory(h => [
        { scenario: scenario.id, verdict: scenario.verdict, ts: new Date().toLocaleTimeString("fr-FR") },
        ...h.slice(0, 11),
      ]);
      if (loop) {
        intervalRef.current = setTimeout(() => {
          startScenario((scenarioIdx + 1) % SCENARIOS.length);
        }, 2500);
      }
      return;
    }
    const t = setTimeout(() => setActiveStep(s => s + 1), 700);
    return () => clearTimeout(t);
  }, [running, activeStep, scenario, loop, scenarioIdx, startScenario]);

  // Cleanup
  useEffect(() => () => { if (intervalRef.current) clearTimeout(intervalRef.current); }, []);

  // Auto-start on mount
  useEffect(() => { startScenario(0); }, [startScenario]);

  const vMeta = VERDICT_META[scenario.verdict];
  const progress = Math.round((activeStep / scenario.steps.length) * 100);

  return (
    <div className="max-w-6xl mx-auto py-6 px-4 flex flex-col gap-6">

      {/* Header */}
      <div className="rounded p-5" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.72 0.18 145 / 0.25)" }}>
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <div className="font-mono text-[9px] font-bold tracking-widest mb-1" style={{ color: "oklch(0.45 0.01 240)" }}>
              OBSIDIA OS4 — DEMO MODE
            </div>
            <h1 className="font-mono text-2xl font-bold mb-1" style={{ color: "oklch(0.90 0.01 240)" }}>
              Live Decision Engine
            </h1>
            <p className="font-mono text-xs" style={{ color: "oklch(0.55 0.01 240)" }}>
              Autonomous scenarios — Flash Crash · Fraud Wave · Supply Shock
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded font-mono text-[10px] font-bold"
              style={{ background: "oklch(0.72 0.18 145 / 0.10)", border: "1px solid oklch(0.72 0.18 145 / 0.4)", color: "oklch(0.72 0.18 145)" }}>
              <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: "oklch(0.72 0.18 145)" }} />
              LIVE
            </div>
            <div className="font-mono text-[10px]" style={{ color: "oklch(0.50 0.01 240)" }}>
              {completedCount} decisions
            </div>
            <button
              onClick={() => setLoop(l => !l)}
              className="px-3 py-1.5 rounded font-mono text-[10px] font-bold"
              style={{
                background: loop ? "oklch(0.60 0.12 200 / 0.15)" : "oklch(0.12 0.01 240)",
                border: `1px solid ${loop ? "oklch(0.60 0.12 200 / 0.5)" : "oklch(0.22 0.01 240)"}`,
                color: loop ? "oklch(0.60 0.12 200)" : "oklch(0.50 0.01 240)",
              }}
            >
              {loop ? "⟳ Loop ON" : "⟳ Loop OFF"}
            </button>
          </div>
        </div>

        {/* Scenario selector */}
        <div className="flex gap-2 mt-4 flex-wrap">
          {SCENARIOS.map((s, i) => (
            <button
              key={s.id}
              onClick={() => startScenario(i)}
              className="flex items-center gap-2 px-3 py-2 rounded font-mono text-xs font-bold"
              style={{
                background: scenarioIdx === i ? `${s.domainColor}18` : "oklch(0.09 0.01 240)",
                border: `1px solid ${scenarioIdx === i ? s.domainColor : "oklch(0.20 0.01 240)"}`,
                color: scenarioIdx === i ? s.domainColor : "oklch(0.55 0.01 240)",
              }}
            >
              <span style={{ color: s.domainColor }}>●</span>
              {s.title}
              <span className="font-normal text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>{s.domain}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

        {/* Left: current scenario info */}
        <div className="flex flex-col gap-4">

          {/* Scenario card */}
          <div className="rounded p-4" style={{ background: "oklch(0.11 0.01 240)", border: `1px solid ${scenario.domainColor}44` }}>
            <div className="font-mono text-[9px] font-bold tracking-widest mb-2" style={{ color: scenario.domainColor }}>
              {scenario.domain.toUpperCase()} — AGENT {scenario.agent.toUpperCase()}
            </div>
            <div className="font-mono text-sm font-bold mb-1" style={{ color: "oklch(0.90 0.01 240)" }}>
              {scenario.title}
            </div>
            <div className="font-mono text-[10px] mb-3" style={{ color: "oklch(0.55 0.01 240)" }}>
              {scenario.subtitle}
            </div>
            {/* Threat level */}
            <div className="inline-flex items-center gap-1.5 px-2 py-1 rounded font-mono text-[9px] font-bold mb-3"
              style={{
                background: scenario.verdict === "BLOCK" ? "rgba(248,113,113,0.12)" : scenario.verdict === "HOLD" ? "rgba(251,191,36,0.12)" : "rgba(74,222,128,0.12)",
                color: scenario.verdict === "BLOCK" ? "#f87171" : scenario.verdict === "HOLD" ? "#fbbf24" : "#4ade80",
                border: `1px solid ${scenario.verdict === "BLOCK" ? "#f8717144" : scenario.verdict === "HOLD" ? "#fbbf2444" : "#4ade8044"}`,
              }}>
              ⚠ {scenario.threat}
            </div>
            {/* Stats */}
            <div className="grid grid-cols-2 gap-2">
              {scenario.stats.map(stat => (
                <div key={stat.label} className="rounded p-2" style={{ background: "oklch(0.09 0.01 240)", border: "1px solid oklch(0.16 0.01 240)" }}>
                  <div className="font-mono text-[8px] text-muted-foreground mb-0.5">{stat.label}</div>
                  <div className="font-mono text-sm font-bold" style={{ color: stat.color ?? "oklch(0.90 0.01 240)" }}>{stat.value}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Progress */}
          <div className="rounded p-3" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
            <div className="flex items-center justify-between mb-2 font-mono text-[9px]" style={{ color: "oklch(0.45 0.01 240)" }}>
              <span>PIPELINE PROGRESS</span>
              <span>{progress}%</span>
            </div>
            <div className="h-1.5 rounded-full overflow-hidden" style={{ background: "oklch(0.16 0.01 240)" }}>
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{ width: `${progress}%`, background: "oklch(0.72 0.18 145)" }}
              />
            </div>
            <div className="flex items-center justify-between mt-2 font-mono text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>
              <span>Step {Math.min(activeStep, scenario.steps.length)}/{scenario.steps.length}</span>
              <span>{running ? "▶ Running..." : activeStep >= scenario.steps.length ? "✓ Complete" : "⏸ Paused"}</span>
            </div>
          </div>

          {/* Decision history */}
          {history.length > 0 && (
            <div className="rounded p-3" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
              <div className="font-mono text-[9px] font-bold tracking-widest mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>
                VERDICT HISTORY
              </div>
              <div className="flex flex-col gap-1">
                {history.slice(0, 6).map((h, i) => {
                  const vm = VERDICT_META[h.verdict];
                  const sc = SCENARIOS.find(s => s.id === h.scenario);
                  return (
                    <div key={i} className="flex items-center gap-2 font-mono text-[9px]">
                      <span style={{ color: "oklch(0.35 0.01 240)" }}>{h.ts}</span>
                      <span style={{ color: sc?.domainColor ?? "oklch(0.55 0.01 240)" }}>{sc?.domain}</span>
                      <span className="px-1.5 py-0.5 rounded font-bold" style={{ background: vm.bg, color: vm.color }}>
                        {h.verdict}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Links */}
          <div className="rounded p-3" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
            <div className="font-mono text-[9px] font-bold tracking-widest mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>EXPLORE</div>
            <div className="flex flex-col gap-1">
              {[
                { href: "/market",        label: "Market",   color: "#60a5fa" },
                { href: "/agents",        label: "Agents",   color: "#a78bfa" },
                { href: "/decision-flow", label: "Decision", color: "#34d399" },
                { href: "/proof-center",  label: "Proof",    color: "#34d399" },
                { href: "/control",       label: "Control",  color: "#94a3b8" },
              ].map(item => (
                <Link key={item.href} href={item.href}>
                  <span className="block px-2 py-1 rounded font-mono text-[10px] font-bold" style={{ color: item.color }}>
                    {item.label} →
                  </span>
                </Link>
              ))}
            </div>
          </div>
        </div>

        {/* Right: pipeline animation */}
        <div className="lg:col-span-2 flex flex-col gap-3">

          {/* Pipeline steps */}
          {scenario.steps.map((step, i) => {
            const isActive = i < activeStep;
            const isCurrent = i === activeStep - 1;
            const vm = step.verdict ? VERDICT_META[step.verdict] : null;

            return (
              <div key={step.stage} className="flex gap-3">
                {/* Timeline */}
                <div className="flex flex-col items-center" style={{ minWidth: "36px" }}>
                  <div
                    className="w-9 h-9 rounded-full flex items-center justify-center text-base font-bold flex-shrink-0 transition-all duration-500"
                    style={{
                      background: isActive ? `${step.color}18` : "oklch(0.12 0.01 240)",
                      border: `2px solid ${isActive ? step.color : "oklch(0.22 0.01 240)"}`,
                      color: isActive ? step.color : "oklch(0.35 0.01 240)",
                      boxShadow: isCurrent ? `0 0 12px ${step.color}66` : "none",
                    }}
                  >
                    {step.icon}
                  </div>
                  {i < scenario.steps.length - 1 && (
                    <div className="w-px flex-1 mt-1 transition-all duration-500"
                      style={{ background: isActive ? `${step.color}44` : "oklch(0.18 0.01 240)", minHeight: "20px" }} />
                  )}
                </div>

                {/* Card */}
                <div
                  className="flex-1 rounded p-3 mb-2 transition-all duration-500"
                  style={{
                    background: isActive ? `${step.color}0a` : "oklch(0.10 0.01 240)",
                    border: `1px solid ${isActive ? `${step.color}44` : "oklch(0.16 0.01 240)"}`,
                    opacity: isActive ? 1 : 0.45,
                  }}
                >
                  <div className="flex items-center justify-between mb-1">
                    <div className="font-mono text-[9px] font-bold tracking-widest" style={{ color: isActive ? step.color : "oklch(0.35 0.01 240)" }}>
                      {step.title.toUpperCase()}
                    </div>
                    {isCurrent && (
                      <div className="flex items-center gap-1 font-mono text-[8px]" style={{ color: "oklch(0.72 0.18 145)" }}>
                        <div className="w-1 h-1 rounded-full animate-pulse" style={{ background: "oklch(0.72 0.18 145)" }} />
                        PROCESSING
                      </div>
                    )}
                  </div>
                  <div className="font-mono text-xs font-bold mb-1" style={{ color: isActive ? "oklch(0.90 0.01 240)" : "oklch(0.45 0.01 240)" }}>
                    {step.label}
                  </div>
                  {isActive && (
                    <div className="font-mono text-[10px]" style={{ color: "oklch(0.50 0.01 240)" }}>
                      {step.detail}
                    </div>
                  )}
                  {vm && isActive && (
                    <div
                      className="mt-2 inline-flex items-center gap-2 px-3 py-1.5 rounded font-mono text-sm font-bold"
                      style={{ background: vm.bg, color: vm.color, border: `1px solid ${vm.color}44` }}
                    >
                      {vm.icon} {step.verdict}
                      <span className="font-normal text-[10px]">— {vm.desc}</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {/* Completion banner */}
          {activeStep >= scenario.steps.length && (
            <div
              className="rounded p-4 text-center font-mono"
              style={{ background: `${vMeta.color}0a`, border: `1px solid ${vMeta.color}44` }}
            >
              <div className="text-lg font-bold mb-1" style={{ color: vMeta.color }}>
                {vMeta.icon} Verdict: {scenario.verdict}
              </div>
              <div className="text-xs" style={{ color: "oklch(0.55 0.01 240)" }}>
                {vMeta.desc} · Merkle proof generated · Lean invariant verified
              </div>
              {loop && (
                <div className="mt-2 text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>
                  Next scenario in 2.5s…
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Bottom: pipeline summary */}
      <div className="rounded p-4" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
        <div className="font-mono text-[9px] font-bold tracking-widest mb-3" style={{ color: "oklch(0.45 0.01 240)" }}>
          GOVERNANCE PIPELINE — OBSIDIA OS4
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {[
            { label: "WORLD",      color: "#60a5fa", desc: "Market provides context" },
            { label: "AGENT",      color: "#a78bfa", desc: "Agent proposes action" },
            { label: "GUARD X-108",color: "#34d399", desc: "The judge evaluates" },
            { label: "VERDICT",    color: "#a78bfa", desc: "ALLOW / HOLD / BLOCK" },
            { label: "PROOF",      color: "#34d399", desc: "Cryptographic evidence" },
          ].map((item, i, arr) => (
            <React.Fragment key={item.label}>
              <div className="flex flex-col items-center gap-1">
                <div className="px-2 py-1 rounded font-mono text-[9px] font-bold"
                  style={{ background: `${item.color}12`, color: item.color, border: `1px solid ${item.color}44` }}>
                  {item.label}
                </div>
                <div className="font-mono text-[8px] text-center" style={{ color: "oklch(0.40 0.01 240)", maxWidth: "80px" }}>
                  {item.desc}
                </div>
              </div>
              {i < arr.length - 1 && (
                <span className="font-mono text-sm" style={{ color: "oklch(0.30 0.01 240)", marginBottom: "14px" }}>→</span>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
}
