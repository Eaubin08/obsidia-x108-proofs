import React, { useState } from "react";
import { Link } from "wouter";

const LIFECYCLE_STEPS = [
  {
    id: "world_state",
    step: 1,
    title: "World State",
    layer: "OS4",
    desc: "The simulation world captures the current state: market prices, account balances, cart contents, agent positions.",
    details: [
      "Price series from GBM + Markov regime model",
      "Account balance, transaction history",
      "Cart state, inventory, ad budget",
      "Agent portfolio positions",
    ],
    code: "world_state = { price: 142.50, volatility: 0.023, regime: 'BULL', timestamp: 1709654400 }",
    color: "oklch(0.65 0.18 220)",
  },
  {
    id: "agent_observation",
    step: 2,
    title: "Agent Observation",
    layer: "OS1 + OS2",
    desc: "The agent observes the world state and generates a strategy. It proposes an action based on its objective function.",
    details: [
      "Agent reads world state snapshot",
      "Computes expected value of each action",
      "Selects action with highest utility",
      "Packages action proposal with metadata",
    ],
    code: "action = { type: 'SELL_ALL', amount: 10000, urgency: 0.95, agent: 'momentum_bot_v2' }",
    color: "oklch(0.65 0.18 220)",
  },
  {
    id: "guard_evaluation",
    step: 3,
    title: "Guard X-108 Evaluation",
    layer: "X-108",
    desc: "The guard intercepts the action. It checks irreversibility, coherence score, and temporal constraints.",
    details: [
      "Check: is this action irreversible?",
      "Compute coherence score (0.0 → 1.0)",
      "Evaluate temporal constraint (τ=10s)",
      "Run domain-specific invariant checks",
    ],
    code: "guard_eval = { irreversible: true, coherence: 0.23, tau_elapsed: 0, invariants: [FAIL, FAIL, PASS] }",
    color: "oklch(0.72 0.18 145)",
    highlight: true,
  },
  {
    id: "decision_state",
    step: 4,
    title: "Decision State",
    layer: "X-108 → OS2",
    desc: "The guard emits a decision: BLOCK, HOLD, or ALLOW. This decision is final and cryptographically signed.",
    details: [
      "BLOCK: invariant violated, action rejected",
      "HOLD: τ=10s wait, coherence recomputed",
      "ALLOW: all invariants satisfied, proceed",
      "Decision signed with SHA-256 hash",
    ],
    code: "decision = { result: 'BLOCK', reason: 'coherence_below_threshold', hash: 'a3f2...', timestamp: 1709654410 }",
    color: "oklch(0.72 0.18 145)",
    highlight: true,
  },
  {
    id: "execution",
    step: 5,
    title: "Execution",
    layer: "OS2",
    desc: "If ALLOW, the action is executed. If BLOCK, it is discarded. If HOLD, it waits τ seconds then re-evaluates.",
    details: [
      "ALLOW: action applied to world state",
      "BLOCK: action discarded, agent notified",
      "HOLD: action queued for τ=10s, then re-evaluated",
      "World state updated with execution result",
    ],
    code: "execution = { status: 'BLOCKED', world_state_unchanged: true, capital_saved: 15000 }",
    color: "oklch(0.65 0.18 220)",
  },
  {
    id: "proof",
    step: 6,
    title: "Proof & Audit",
    layer: "OS3",
    desc: "Every decision is logged, hashed, and added to the Merkle tree. The chain is tamper-evident and replayable.",
    details: [
      "Log entry: timestamp + world_state_hash + decision",
      "Hash chain: H(n) = SHA256(H(n-1) || entry)",
      "Merkle root updated with new leaf",
      "Replay verifier can reproduce decision from seed",
    ],
    code: "proof = { log_hash: 'b7c1...', merkle_root: 'd4e9...', replay_verified: true, lean4_theorem: 'T_017' }",
    color: "oklch(0.65 0.18 220)",
  },
];

const EXAMPLE_SCENARIOS = [
  { id: "flash_crash", label: "Flash Crash", decision: "BLOCK", coherence: 0.12 },
  { id: "normal_trade", label: "Normal Trade", decision: "ALLOW", coherence: 0.87 },
  { id: "large_transfer", label: "Large Transfer", decision: "HOLD", coherence: 0.54 },
];

export default function DecisionLifecycle() {
  const [activeStep, setActiveStep] = useState(0);
  const [activeScenario, setActiveScenario] = useState("flash_crash");

  const step = LIFECYCLE_STEPS[activeStep];
  const scenario = EXAMPLE_SCENARIOS.find((s) => s.id === activeScenario)!;

  return (
    <div className="flex flex-col gap-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="pt-4">
        <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-2">OS4 — Core Mechanism</div>
        <h1 className="font-mono font-bold text-3xl text-foreground mb-2">Decision Lifecycle</h1>
        <p className="text-muted-foreground font-mono text-sm">
          Every decision in OS4 follows the same 6-step pipeline. Click each step to explore.
        </p>
      </div>

      {/* Scenario selector */}
      <div className="flex items-center gap-3">
        <span className="text-[10px] font-mono text-muted-foreground uppercase">Scenario:</span>
        {EXAMPLE_SCENARIOS.map((s) => (
          <button
            key={s.id}
            onClick={() => setActiveScenario(s.id)}
            className="px-3 py-1 rounded text-[10px] font-mono font-bold transition-all"
            style={{
              background: activeScenario === s.id ? (s.decision === "BLOCK" ? "#f8717120" : s.decision === "HOLD" ? "#f59e0b20" : "#4ade8020") : "oklch(0.14 0.01 240)",
              color: s.decision === "BLOCK" ? "#f87171" : s.decision === "HOLD" ? "#f59e0b" : "#4ade80",
              border: "1px solid " + (activeScenario === s.id ? (s.decision === "BLOCK" ? "#f87171" : s.decision === "HOLD" ? "#f59e0b" : "#4ade80") : "oklch(0.20 0.01 240)"),
            }}
          >
            {s.label} → {s.decision}
          </button>
        ))}
      </div>

      {/* Pipeline steps */}
      <div className="grid grid-cols-12 gap-4">
        {/* Step list */}
        <div className="col-span-4 flex flex-col gap-1">
          {LIFECYCLE_STEPS.map((s, i) => (
            <button
              key={s.id}
              onClick={() => setActiveStep(i)}
              className="flex items-center gap-3 px-3 py-2.5 rounded text-left transition-all"
              style={{
                background: activeStep === i ? (s.highlight ? "oklch(0.14 0.04 145)" : "oklch(0.15 0.02 220)") : "oklch(0.12 0.01 240)",
                border: "1px solid " + (activeStep === i ? (s.highlight ? "oklch(0.72 0.18 145 / 0.5)" : "oklch(0.65 0.18 220 / 0.4)") : "oklch(0.18 0.01 240)"),
              }}
            >
              <div
                className="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-mono font-bold flex-shrink-0"
                style={{
                  background: activeStep === i ? (s.highlight ? "oklch(0.72 0.18 145)" : "oklch(0.65 0.18 220)") : "oklch(0.18 0.01 240)",
                  color: activeStep === i ? "oklch(0.10 0.01 240)" : "oklch(0.40 0.01 240)",
                }}
              >
                {s.step}
              </div>
              <div>
                <div className="text-[10px] font-mono font-bold" style={{ color: s.highlight ? "oklch(0.72 0.18 145)" : "oklch(0.65 0.01 240)" }}>
                  {s.title}
                </div>
                <div className="text-[9px] text-muted-foreground">{s.layer}</div>
              </div>
            </button>
          ))}
        </div>

        {/* Step detail */}
        <div className="col-span-8 flex flex-col gap-3">
          <div
            className="panel p-5"
            style={{ borderColor: step.highlight ? "oklch(0.72 0.18 145 / 0.4)" : "oklch(0.20 0.01 240)" }}
          >
            <div className="flex items-center justify-between mb-3">
              <div>
                <div className="font-mono font-bold text-lg" style={{ color: step.highlight ? "oklch(0.72 0.18 145)" : "oklch(0.65 0.18 220)" }}>
                  Step {step.step} — {step.title}
                </div>
                <div className="text-[10px] font-mono text-muted-foreground">{step.layer}</div>
              </div>
              {step.highlight && (
                <div className="px-2 py-1 rounded text-[9px] font-mono font-bold" style={{ background: "oklch(0.14 0.04 145)", color: "oklch(0.72 0.18 145)", border: "1px solid oklch(0.72 0.18 145 / 0.4)" }}>
                  GUARD X-108
                </div>
              )}
            </div>
            <p className="text-sm text-muted-foreground font-mono mb-4">{step.desc}</p>
            <div className="flex flex-col gap-1.5 mb-4">
              {step.details.map((d) => (
                <div key={d} className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground">
                  <div className="w-1 h-1 rounded-full flex-shrink-0" style={{ background: step.highlight ? "oklch(0.72 0.18 145)" : "oklch(0.65 0.18 220)" }} />
                  {d}
                </div>
              ))}
            </div>
            <div className="rounded p-3 text-[10px] font-mono overflow-x-auto" style={{ background: "oklch(0.08 0.01 240)", color: "oklch(0.72 0.18 145)", border: "1px solid oklch(0.18 0.01 240)" }}>
              {step.code}
            </div>
          </div>

          {/* Coherence meter for guard step */}
          {(activeStep === 2 || activeStep === 3) && (
            <div className="panel p-4">
              <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-3">Coherence Score — {scenario.label}</div>
              <div className="flex items-center gap-3">
                <div className="flex-1 h-3 rounded-full overflow-hidden" style={{ background: "oklch(0.14 0.01 240)" }}>
                  <div
                    className="h-full rounded-full transition-all duration-700"
                    style={{
                      width: `${scenario.coherence * 100}%`,
                      background: scenario.coherence > 0.6 ? "#4ade80" : scenario.coherence > 0.4 ? "#f59e0b" : "#f87171",
                    }}
                  />
                </div>
                <div className="font-mono text-sm font-bold w-12" style={{ color: scenario.coherence > 0.6 ? "#4ade80" : scenario.coherence > 0.4 ? "#f59e0b" : "#f87171" }}>
                  {(scenario.coherence * 100).toFixed(0)}%
                </div>
                <div
                  className="px-2 py-1 rounded text-[10px] font-mono font-bold"
                  style={{
                    background: scenario.decision === "BLOCK" ? "#f8717120" : scenario.decision === "HOLD" ? "#f59e0b20" : "#4ade8020",
                    color: scenario.decision === "BLOCK" ? "#f87171" : scenario.decision === "HOLD" ? "#f59e0b" : "#4ade80",
                    border: "1px solid " + (scenario.decision === "BLOCK" ? "#f87171" : scenario.decision === "HOLD" ? "#f59e0b" : "#4ade80"),
                  }}
                >
                  {scenario.decision}
                </div>
              </div>
              <div className="text-[9px] text-muted-foreground font-mono mt-2">
                Threshold: 0.60 — Below threshold → BLOCK or HOLD
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Nav */}
      <div className="flex gap-3 pb-4">
        <Link href="/simulation-worlds" className="px-4 py-2 rounded font-mono text-sm font-bold" style={{ background: "oklch(0.72 0.18 145)", color: "oklch(0.10 0.01 240)" }}>
            See it in action →
          </Link>
        <Link href="/scenario-engine" className="px-4 py-2 rounded font-mono text-sm border" style={{ background: "transparent", color: "oklch(0.72 0.18 145)", borderColor: "oklch(0.72 0.18 145 / 0.5)" }}>
            Run stress scenarios →
          </Link>
      </div>
    </div>
  );
}
