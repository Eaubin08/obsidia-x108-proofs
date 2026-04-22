import { useState, useEffect, useRef } from "react";
import { Link } from "wouter";

// ─── Types ────────────────────────────────────────────────────────────────────

type ViewMode = "investor" | "technical";

interface PipelineStep {
  id: string;
  icon: string;
  label: string;
  sublabel: string;
  color: string;
  investorDesc: string;
  technicalDesc: string;
}

// ─── Data ─────────────────────────────────────────────────────────────────────

const PIPELINE_STEPS: PipelineStep[] = [
  {
    id: "market",
    icon: "🌍",
    label: "Market Context",
    sublabel: "World state",
    color: "#60a5fa",
    investorDesc: "The system monitors real-time market conditions: price movements, volatility, transaction volumes, and risk signals.",
    technicalDesc: "MarketFeed ingests tick data and computes coherence score Ω = f(volatility, spread, depth). Threshold: Ω < 0.30 triggers defensive mode.",
  },
  {
    id: "agent",
    icon: "🤖",
    label: "Agent Signal",
    sublabel: "Proposal",
    color: "#fbbf24",
    investorDesc: "An AI agent analyzes the situation and proposes an action — a trade, a transfer, a price change — with its confidence level.",
    technicalDesc: "Agent emits Intent(action, confidence, seed). Alpha uses LSTM-based signal with confidence ∈ [0,1]. Proposal is serialized and passed to Guard.",
  },
  {
    id: "guard",
    icon: "🛡",
    label: "Guard X-108",
    sublabel: "Evaluation",
    color: "oklch(0.72 0.18 145)",
    investorDesc: "The Guard evaluates the proposal against safety rules. It checks coherence, risk thresholds, and applies a cooldown period for irreversible actions.",
    technicalDesc: "Guard evaluates: (1) coherence check Ω vs threshold, (2) Lean 4 invariant verification, (3) temporal lock τ=10s for irreversible actions. O(1) deterministic.",
  },
  {
    id: "decision",
    icon: "⚡",
    label: "Decision",
    sublabel: "ALLOW / HOLD / BLOCK",
    color: "#a78bfa",
    investorDesc: "The Guard issues one of three verdicts: ALLOW (execute), HOLD (wait for validation), or BLOCK (reject — too risky).",
    technicalDesc: "Decision ∈ {ALLOW, HOLD, BLOCK}. ALLOW: Ω ≥ 0.60. HOLD: 0.30 ≤ Ω < 0.60 or temporal lock active. BLOCK: Ω < 0.30 or invariant violated.",
  },
  {
    id: "proof",
    icon: "🔗",
    label: "Proof",
    sublabel: "Cryptographic record",
    color: "#34d399",
    investorDesc: "Every decision — whether approved or blocked — generates a cryptographic proof. This creates a tamper-proof audit trail for regulators and auditors.",
    technicalDesc: "SHA-256 hash of (intent, decision, timestamp, seed). Merkle root updated. RFC3161 timestamp anchored. Théorème formel: ∀ decision, ∃ verifiable proof.",
  },
];

const LIVE_EXAMPLE = {
  event: { label: "Market Event", value: "BTC/USD drops -18.4% in 3 minutes", color: "#f87171", icon: "📉" },
  agent: { label: "Agent Alpha", value: "Proposes SELL 100% BTC — $125,000", color: "#fbbf24", icon: "🤖" },
  guard: { label: "Guard X-108", value: "Coherence 0.12 < threshold 0.30 · Invariant violated", color: "#f87171", icon: "🛡" },
  decision: { label: "Decision", value: "BLOCK — Irreversible action refused", color: "#f87171", icon: "⚡" },
  proof: { label: "Proof", value: "Hash b9ac7a04 · Empreinte cryptographiqueed · RFC3161 timestamp", color: "#34d399", icon: "🔗" },
  result: { label: "Capital Protected", value: "$125,000 saved from catastrophic loss", color: "#4ade80", icon: "✅" },
};

const TIMELINE = [
  { time: "08:23:14.000", event: "BTC/USD flash crash detected — volatility spike", color: "#f87171" },
  { time: "08:23:14.012", event: "Agent Alpha computes signal — confidence 0.41", color: "#fbbf24" },
  { time: "08:23:14.023", event: "Guard X-108 evaluates coherence Ω = 0.12", color: "oklch(0.72 0.18 145)" },
  { time: "08:23:14.031", event: "Decision: BLOCK — threshold violated", color: "#f87171" },
  { time: "08:23:14.032", event: "Proof generated — hash b9ac7a04 anchored", color: "#34d399" },
];

// ─── Component ────────────────────────────────────────────────────────────────

export default function HowItWorks() {
  const [viewMode, setViewMode] = useState<ViewMode>("investor");
  const [activeStep, setActiveStep] = useState<number | null>(null);
  const [liveStep, setLiveStep] = useState(-1);
  const [liveRunning, setLiveRunning] = useState(false);
  const liveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const runLiveExample = () => {
    setLiveStep(0);
    setLiveRunning(true);
  };

  useEffect(() => {
    if (!liveRunning) return;
    const liveKeys = Object.keys(LIVE_EXAMPLE);
    if (liveStep >= liveKeys.length) {
      setLiveRunning(false);
      return;
    }
    liveTimerRef.current = setTimeout(() => {
      setLiveStep(s => s + 1);
    }, 1200);
    return () => { if (liveTimerRef.current) clearTimeout(liveTimerRef.current); };
  }, [liveStep, liveRunning]);

  const liveKeys = Object.keys(LIVE_EXAMPLE) as (keyof typeof LIVE_EXAMPLE)[];

  return (
    <div className="flex flex-col gap-0 max-w-4xl mx-auto">

      {/* ─── HEADER ─────────────────────────────────────────────────────────── */}
      <div className="px-6 pt-10 pb-8 flex flex-col gap-4">
        <div className="text-[9px] font-mono tracking-[0.4em] uppercase" style={{ color: "oklch(0.72 0.18 145)" }}>
          Obsidia Labs — OS4
        </div>
        <h1 className="font-mono font-black text-3xl md:text-4xl text-foreground leading-tight">
          How Obsidia Works
        </h1>
        <p className="font-mono text-sm max-w-xl leading-relaxed" style={{ color: "oklch(0.60 0.01 240)" }}>
          Obsidia is a governance layer for autonomous agents.<br />
          It verifies decisions before execution and produces cryptographic proof.
        </p>

        {/* View mode toggle */}
        <div className="flex items-center gap-1 p-1 rounded self-start" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
          {(["investor", "technical"] as ViewMode[]).map(mode => (
            <button
              key={mode}
              onClick={() => setViewMode(mode)}
              className="px-4 py-1.5 rounded font-mono text-xs font-bold transition-all"
              style={{
                background: viewMode === mode ? "oklch(0.72 0.18 145)" : "transparent",
                color: viewMode === mode ? "oklch(0.10 0.01 240)" : "oklch(0.55 0.01 240)",
              }}
            >
              {mode === "investor" ? "For Investors" : "For Developers"}
            </button>
          ))}
        </div>
      </div>

      {/* ─── SECTION 1 — THE PROBLEM ────────────────────────────────────────── */}
      <section className="px-6 py-10" style={{ background: "oklch(0.09 0.01 240)", borderTop: "1px solid oklch(0.16 0.01 240)", borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
        <div className="text-[9px] font-mono tracking-[0.3em] uppercase mb-3" style={{ color: "#f87171" }}>
          Section 1 — The Problem
        </div>
        <h2 className="font-mono font-bold text-2xl text-foreground mb-3">
          Autonomous agents can execute irreversible actions instantly.
        </h2>
        <p className="font-mono text-sm mb-8 leading-relaxed" style={{ color: "oklch(0.60 0.01 240)" }}>
          AI agents act faster than humans can react. Once an action is executed, it is often too late to reverse.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {[
            { icon: "📉", domain: "Trading", event: "Flash Crash", desc: "A trading bot sells an entire portfolio in 80ms during a volatility spike." },
            { icon: "💸", domain: "Banking", event: "Fraud Wave", desc: "An automation agent triggers a $200,000 wire transfer without human confirmation." },
            { icon: "🛒", domain: "E-Commerce", event: "Supply Shock", desc: "A pricing agent drops all prices to $0 during a bot traffic attack." },
          ].map(item => (
            <div key={item.domain} className="p-5 rounded flex flex-col gap-3"
              style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.55 0.18 25 / 0.25)" }}>
              <div className="flex items-center gap-3">
                <span className="text-2xl">{item.icon}</span>
                <div>
                  <div className="font-mono text-xs font-bold" style={{ color: "#f87171" }}>{item.domain}</div>
                  <div className="text-[9px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>{item.event}</div>
                </div>
              </div>
              <p className="text-[11px] font-mono leading-relaxed" style={{ color: "oklch(0.55 0.01 240)" }}>{item.desc}</p>
            </div>
          ))}
        </div>
        <div className="p-4 rounded text-center"
          style={{ background: "oklch(0.55 0.18 25 / 0.08)", border: "1px solid oklch(0.55 0.18 25 / 0.30)" }}>
          <span className="font-mono text-sm font-bold" style={{ color: "#f87171" }}>
            Once the action is executed, it is often too late.
          </span>
        </div>
      </section>

      {/* ─── SECTION 2 — THE SOLUTION ───────────────────────────────────────── */}
      <section className="px-6 py-10">
        <div className="text-[9px] font-mono tracking-[0.3em] uppercase mb-3" style={{ color: "oklch(0.72 0.18 145)" }}>
          Section 2 — The Solution
        </div>
        <h2 className="font-mono font-bold text-2xl text-foreground mb-3">
          Obsidia adds a governance layer.
        </h2>
        <p className="font-mono text-sm mb-8 leading-relaxed" style={{ color: "oklch(0.60 0.01 240)" }}>
          Every action proposed by an agent is evaluated before execution.<br />
          The Guard X-108 sits between the agent and the real world.
        </p>
        <div className="grid grid-cols-2 gap-8 items-start">
          <div>
            <div className="text-[9px] font-mono mb-3 font-bold" style={{ color: "#f87171" }}>WITHOUT OBSIDIA</div>
            {["Agent proposes action", "Action executes immediately", "Damage occurs", "Verification happens later (too late)"].map((step, i) => (
              <div key={i} className="flex items-start gap-3 mb-3">
                <div className="w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-mono font-bold flex-shrink-0 mt-0.5"
                  style={{ background: "#f8717120", color: "#f87171", border: "1px solid #f8717140" }}>{i + 1}</div>
                <span className="font-mono text-xs" style={{ color: "oklch(0.55 0.01 240)" }}>{step}</span>
              </div>
            ))}
          </div>
          <div>
            <div className="text-[9px] font-mono mb-3 font-bold" style={{ color: "#4ade80" }}>WITH OBSIDIA</div>
            {["Agent proposes action", "Guard X-108 evaluates risk", "Decision: ALLOW / HOLD / BLOCK", "Action executes only if validated", "Cryptographic proof generated"].map((step, i) => (
              <div key={i} className="flex items-start gap-3 mb-3">
                <div className="w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-mono font-bold flex-shrink-0 mt-0.5"
                  style={{ background: "#4ade8020", color: "#4ade80", border: "1px solid #4ade8040" }}>{i + 1}</div>
                <span className="font-mono text-xs" style={{ color: "oklch(0.65 0.01 240)" }}>{step}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── SECTION 3 — THE DECISION PIPELINE ─────────────────────────────── */}
      <section className="px-6 py-10" style={{ background: "oklch(0.09 0.01 240)", borderTop: "1px solid oklch(0.16 0.01 240)", borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
        <div className="text-[9px] font-mono tracking-[0.3em] uppercase mb-3" style={{ color: "oklch(0.72 0.18 145)" }}>
          Section 3 — The Decision Pipeline
        </div>
        <h2 className="font-mono font-bold text-2xl text-foreground mb-2">
          Every decision follows the same path.
        </h2>
        <p className="font-mono text-sm mb-8 leading-relaxed" style={{ color: "oklch(0.60 0.01 240)" }}>
          Click a step to understand what happens at each stage.
        </p>

        {/* Pipeline horizontal */}
        <div className="flex items-center gap-0 mb-8 overflow-x-auto pb-2">
          {PIPELINE_STEPS.map((step, i) => (
            <div key={step.id} className="flex items-center" style={{ minWidth: 0 }}>
              <button
                onClick={() => setActiveStep(activeStep === i ? null : i)}
                className="flex flex-col items-center gap-2 px-3 py-3 rounded transition-all"
                style={{
                  background: activeStep === i ? `${step.color}15` : "transparent",
                  border: `1px solid ${activeStep === i ? step.color : "oklch(0.20 0.01 240)"}`,
                  minWidth: "90px",
                }}
              >
                <div className="w-10 h-10 rounded-full flex items-center justify-center text-lg"
                  style={{ background: `${step.color}20`, border: `2px solid ${step.color}60` }}>
                  {step.icon}
                </div>
                <div className="font-mono font-bold text-[10px] text-center" style={{ color: step.color }}>{step.label}</div>
                <div className="text-[8px] font-mono text-center" style={{ color: "oklch(0.40 0.01 240)" }}>{step.sublabel}</div>
              </button>
              {i < PIPELINE_STEPS.length - 1 && (
                <div className="flex items-center px-1">
                  <div className="w-6 h-0.5" style={{ background: "oklch(0.22 0.01 240)" }} />
                  <span className="text-[10px]" style={{ color: "oklch(0.35 0.01 240)" }}>→</span>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Active step detail */}
        {activeStep !== null && (
          <div className="rounded-lg p-5 transition-all"
            style={{ background: `${PIPELINE_STEPS[activeStep].color}08`, border: `1px solid ${PIPELINE_STEPS[activeStep].color}30` }}>
            <div className="flex items-center gap-3 mb-3">
              <span className="text-2xl">{PIPELINE_STEPS[activeStep].icon}</span>
              <div>
                <div className="font-mono font-bold text-sm" style={{ color: PIPELINE_STEPS[activeStep].color }}>
                  {PIPELINE_STEPS[activeStep].label}
                </div>
                <div className="text-[9px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>
                  {PIPELINE_STEPS[activeStep].sublabel}
                </div>
              </div>
            </div>
            <p className="font-mono text-xs leading-relaxed" style={{ color: "oklch(0.65 0.01 240)" }}>
              {viewMode === "investor" ? PIPELINE_STEPS[activeStep].investorDesc : PIPELINE_STEPS[activeStep].technicalDesc}
            </p>
          </div>
        )}

        {activeStep === null && (
          <div className="text-center py-4">
            <span className="text-[10px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>
              ↑ Click any step above to see details
            </span>
          </div>
        )}
      </section>

      {/* ─── SECTION 4 — LIVE EXAMPLE ───────────────────────────────────────── */}
      <section className="px-6 py-10">
        <div className="text-[9px] font-mono tracking-[0.3em] uppercase mb-3" style={{ color: "oklch(0.60 0.12 200)" }}>
          Section 4 — Live Example
        </div>
        <h2 className="font-mono font-bold text-2xl text-foreground mb-2">
          Flash Crash — one complete decision.
        </h2>
        <p className="font-mono text-sm mb-6 leading-relaxed" style={{ color: "oklch(0.60 0.01 240)" }}>
          BTC/USD drops -18.4% in 3 minutes. Watch the pipeline execute in real time.
        </p>

        <div className="flex gap-3 mb-6">
          <button
            onClick={runLiveExample}
            className="px-5 py-2 rounded font-mono text-xs font-bold"
            style={{ background: "oklch(0.72 0.18 145)", color: "oklch(0.10 0.01 240)" }}
          >
            ▶ Run Example
          </button>
          <button
            onClick={() => { setLiveStep(-1); setLiveRunning(false); }}
            className="px-5 py-2 rounded font-mono text-xs font-bold border"
            style={{ background: "transparent", color: "oklch(0.55 0.01 240)", borderColor: "oklch(0.22 0.01 240)" }}
          >
            ↺ Reset
          </button>
        </div>

        {/* Live steps */}
        <div className="flex flex-col gap-3">
          {liveKeys.map((key, i) => {
            const item = LIVE_EXAMPLE[key];
            const isVisible = liveStep > i || (!liveRunning && liveStep === -1);
            const isActive = liveStep === i && liveRunning;
            return (
              <div key={key}
                className="flex items-start gap-4 p-4 rounded transition-all duration-500"
                style={{
                  background: isActive ? `${item.color}10` : isVisible && liveStep > i ? "oklch(0.10 0.01 240)" : "oklch(0.08 0.01 240)",
                  border: `1px solid ${isActive ? item.color + "50" : "oklch(0.16 0.01 240)"}`,
                  opacity: liveStep === -1 ? 0.4 : liveStep > i ? 1 : isActive ? 1 : 0.3,
                }}>
                <span className="text-xl flex-shrink-0">{item.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="font-mono text-[10px] font-bold mb-1" style={{ color: "oklch(0.45 0.01 240)" }}>
                    {item.label}
                  </div>
                  <div className="font-mono text-xs font-bold" style={{ color: item.color }}>
                    {item.value}
                  </div>
                </div>
                {liveStep > i && (
                  <span className="text-[9px] font-mono px-2 py-0.5 rounded flex-shrink-0" style={{ background: "#4ade8015", color: "#4ade80" }}>✓</span>
                )}
              </div>
            );
          })}
        </div>

        {/* Timeline */}
        {liveStep >= liveKeys.length && (
          <div className="mt-6 rounded-lg p-4" style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
            <div className="text-[9px] font-mono font-bold mb-3" style={{ color: "oklch(0.45 0.01 240)" }}>EXECUTION TIMELINE</div>
            {TIMELINE.map((t, i) => (
              <div key={i} className="flex items-start gap-4 mb-2">
                <span className="font-mono text-[9px] flex-shrink-0" style={{ color: "oklch(0.40 0.01 240)" }}>{t.time}</span>
                <span className="font-mono text-[10px]" style={{ color: t.color }}>{t.event}</span>
              </div>
            ))}
            <div className="mt-3 pt-3 text-center font-mono text-xs font-bold" style={{ borderTop: "1px solid oklch(0.16 0.01 240)", color: "#4ade80" }}>
              Total latency: 32ms · Capital protected: $125,000
            </div>
          </div>
        )}
      </section>

      {/* ─── SECTION 5 — WHY THIS MATTERS ──────────────────────────────────── */}
      <section className="px-6 py-10" style={{ background: "oklch(0.09 0.01 240)", borderTop: "1px solid oklch(0.16 0.01 240)", borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
        <div className="text-[9px] font-mono tracking-[0.3em] uppercase mb-3" style={{ color: "oklch(0.65 0.18 240)" }}>
          Section 5 — Why This Matters
        </div>
        <h2 className="font-mono font-bold text-2xl text-foreground mb-8">
          Verification before execution, not after.
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-5 rounded" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.55 0.18 25 / 0.25)" }}>
            <div className="font-mono text-xs font-bold mb-4" style={{ color: "#f87171" }}>Traditional Systems</div>
            <div className="flex flex-col gap-3">
              {["Agent executes action immediately", "Verification happens after execution", "Damage is already done", "Audit trail is reconstructed post-hoc"].map((item, i) => (
                <div key={i} className="flex items-center gap-3">
                  <span className="text-[10px]" style={{ color: "#f87171" }}>✗</span>
                  <span className="font-mono text-xs" style={{ color: "oklch(0.55 0.01 240)" }}>{item}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="p-5 rounded" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.72 0.18 145 / 0.25)" }}>
            <div className="font-mono text-xs font-bold mb-4" style={{ color: "#4ade80" }}>Obsidia OS4</div>
            <div className="flex flex-col gap-3">
              {["Agent proposes action to Guard X-108", "Guard verifies before execution", "Action executes only if validated", "Cryptographic proof generated in real time"].map((item, i) => (
                <div key={i} className="flex items-center gap-3">
                  <span className="text-[10px]" style={{ color: "#4ade80" }}>✓</span>
                  <span className="font-mono text-xs" style={{ color: "oklch(0.65 0.01 240)" }}>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ─── SECTION 6 — PROOF ──────────────────────────────────────────────── */}
      <section className="px-6 py-10">
        <div className="text-[9px] font-mono tracking-[0.3em] uppercase mb-3" style={{ color: "oklch(0.60 0.12 200)" }}>
          Section 6 — Proof
        </div>
        <h2 className="font-mono font-bold text-2xl text-foreground mb-3">
          Every decision produces verifiable evidence.
        </h2>
        <p className="font-mono text-sm mb-8 leading-relaxed" style={{ color: "oklch(0.60 0.01 240)" }}>
          {viewMode === "investor"
            ? "Every decision — approved or blocked — is recorded and can be verified by anyone, at any time."
            : "Not just logs — mathematically proven guarantees."}
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {(viewMode === "investor" ? [
            { icon: "📋", title: "Audit trail", desc: "Every decision is recorded with timestamp, context, and outcome. Nothing is hidden." },
            { icon: "🔒", title: "Tamper-proof", desc: "Records cannot be altered after the fact. The system cannot lie about what happened." },
            { icon: "✅", title: "Regulators ready", desc: "Full audit trail exportable for compliance, legal review, or external audit." },
            { icon: "📊", title: "Capital protected", desc: "Each blocked action shows exactly how much capital was saved and why." },
          ] : [
            { icon: "📐", title: "33 Lean 4 Theorems", desc: "Every safety invariant is mathematically proven. Not tested — proven." },
            { icon: "🔧", title: "TLA+ Invariants", desc: "Temporal logic covers all concurrent execution paths." },
            { icon: "🔗", title: "Empreinte cryptographiques", desc: "Every decision is anchored in a hash chain. Tamper-proof." },
            { icon: "📋", title: "Evidence Logs", desc: "RFC3161 timestamps. Full audit trail for regulators." },
          ]).map(item => (
            <div key={item.title} className="p-4 rounded flex flex-col gap-2"
              style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
              <span className="text-2xl">{item.icon}</span>
              <div className="font-mono text-xs font-bold text-foreground">{item.title}</div>
              <div className="text-[10px] leading-relaxed" style={{ color: "oklch(0.50 0.01 240)" }}>{item.desc}</div>
            </div>
          ))}
        </div>
        <Link href="/proof"
          className="inline-block px-5 py-2.5 rounded font-mono text-sm font-bold"
          style={{ background: "oklch(0.60 0.12 200)", color: "oklch(0.95 0.01 240)" }}>
          View formal proofs →
        </Link>
      </section>

      {/* ─── SECTION 7 — SYSTEM OVERVIEW ────────────────────────────────────── */}
      <section className="px-6 py-10 pb-16" style={{ background: "oklch(0.09 0.01 240)", borderTop: "1px solid oklch(0.16 0.01 240)" }}>
        <div className="text-[9px] font-mono tracking-[0.3em] uppercase mb-3" style={{ color: "oklch(0.72 0.18 145)" }}>
          Section 7 — System Overview
        </div>
        <h2 className="font-mono font-bold text-2xl text-foreground mb-8">
          The complete Obsidia pipeline.
        </h2>
        <div className="flex flex-col items-center gap-0 max-w-sm mx-auto mb-10">
          {(viewMode === "investor" ? [
            { label: "Market", sub: "Something happens in the real world", color: "#60a5fa", icon: "🌍" },
            { label: "Agent", sub: "An AI proposes an action", color: "#fbbf24", icon: "🤖" },
            { label: "Guard X-108", sub: "Is this action safe?", color: "oklch(0.72 0.18 145)", icon: "🛡", highlight: true },
            { label: "Verdict", sub: "ALLOW — HOLD — BLOCK", color: "#a78bfa", icon: "⚡" },
            { label: "Proof", sub: "Record created — nothing can be hidden", color: "#34d399", icon: "🔗" },
            { label: "Control Tower", sub: "Humans monitor everything", color: "#60a5fa", icon: "🏗" },
          ] : [
            { label: "Market", sub: "Real-world events", color: "#60a5fa", icon: "🌍" },
            { label: "Agents", sub: "Alpha · Sentinel · Mercury", color: "#fbbf24", icon: "🤖" },
            { label: "Guard X-108", sub: "Coherence · Invariants · Temporal lock", color: "oklch(0.72 0.18 145)", icon: "🛡", highlight: true },
            { label: "Decision", sub: "ALLOW / HOLD / BLOCK", color: "#a78bfa", icon: "⚡" },
            { label: "Proof", sub: "Merkle · Lean · TLA+", color: "#34d399", icon: "🔗" },
            { label: "Control Tower", sub: "Monitoring · Audit · Governance", color: "#60a5fa", icon: "🏗" },
          ]).map((step, i, arr) => (
            <div key={step.label} className="flex flex-col items-center w-full">
              <div className="w-full p-4 rounded text-center"
                style={{
                  background: step.highlight ? `${step.color}15` : "oklch(0.11 0.01 240)",
                  border: `1px solid ${step.color}${step.highlight ? "60" : "30"}`,
                  transform: step.highlight ? "scale(1.04)" : "scale(1)",
                }}>
                <div className="flex items-center justify-center gap-3">
                  <span className="text-xl">{step.icon}</span>
                  <div className="text-left">
                    <div className="font-mono font-bold text-sm" style={{ color: step.color }}>{step.label}</div>
                    <div className="text-[9px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>{step.sub}</div>
                  </div>
                </div>
              </div>
              {i < arr.length - 1 && (
                <div className="flex flex-col items-center py-1">
                  <div className="w-0.5 h-5" style={{ background: "oklch(0.22 0.01 240)" }} />
                  <span className="text-[10px]" style={{ color: "oklch(0.35 0.01 240)" }}>↓</span>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* CTAs */}
        <div className="flex gap-3 flex-wrap justify-center">
          <Link href="/market" className="px-5 py-2.5 rounded font-mono text-sm font-bold"
            style={{ background: "oklch(0.72 0.18 145)", color: "oklch(0.10 0.01 240)" }}>
            Enter the System →
          </Link>
          <Link href="/decision-flow" className="px-5 py-2.5 rounded font-mono text-sm font-bold border"
            style={{ background: "transparent", color: "oklch(0.72 0.18 145)", borderColor: "oklch(0.72 0.18 145 / 0.5)" }}>
            Decision Flow →
          </Link>
          <Link href="/control" className="px-5 py-2.5 rounded font-mono text-sm font-bold border"
            style={{ background: "transparent", color: "oklch(0.65 0.01 240)", borderColor: "oklch(0.25 0.01 240)" }}>
            Control Tower →
          </Link>
        </div>
      </section>

    </div>
  );
}
