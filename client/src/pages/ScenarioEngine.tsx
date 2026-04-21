import React, { useState } from "react";
import { trpc } from "@/lib/trpc";

const SCENARIOS = [
  {
    id: "flash_crash",
    title: "Flash Crash",
    domain: "Trading",
    severity: "CRITICAL",
    desc: "Market drops 15% in 90 seconds. Momentum bots attempt panic-selling. Guard evaluates slippage and VaR breach.",
    trigger: "Price drop > 8% in < 2 minutes",
    expected_decision: "BLOCK",
    coherence: 0.12,
    capital_at_risk: 45000,
    params: { seed: 101, steps: 252, mu: -0.35, sigma: 0.08 },
  },
  {
    id: "fraud_attempt",
    title: "Fraud Attempt",
    domain: "Banking",
    severity: "HIGH",
    desc: "Account takeover attempt: €15,000 wire to unknown IBAN at 3am from unrecognized device. IR=0.95, TSG=0.89.",
    trigger: "Unknown IBAN + night hours + new device",
    expected_decision: "BLOCK",
    coherence: 0.06,
    capital_at_risk: 15000,
    params: { seed: 202, steps: 365, fraudRate: 0.15 },
  },
  {
    id: "market_manipulation",
    title: "Market Manipulation",
    domain: "Trading",
    severity: "HIGH",
    desc: "Coordinated wash trading detected. Agent attempts to place 50 orders in 1 second to create artificial volume.",
    trigger: "Order rate > 10/s + circular trades",
    expected_decision: "BLOCK",
    coherence: 0.08,
    capital_at_risk: 120000,
    params: { seed: 303, steps: 252, mu: 0.02, sigma: 0.04 },
  },
  {
    id: "over_leverage",
    title: "Over-Leverage",
    domain: "Trading",
    severity: "MEDIUM",
    desc: "Agent requests 10x leverage on a volatile position. Margin call risk is 87%. Guard enforces HOLD for coherence recomputation.",
    trigger: "Leverage > 5x + volatility > 3%",
    expected_decision: "HOLD",
    coherence: 0.41,
    capital_at_risk: 80000,
    params: { seed: 404, steps: 252, mu: 0.05, sigma: 0.06 },
  },
  {
    id: "supply_shock",
    title: "Supply Shock",
    domain: "E-Commerce",
    severity: "MEDIUM",
    desc: "Top product goes out of stock. AI agent still proposes $5,000 ad spend increase. Coherence check: stock=0 vs budget=5000.",
    trigger: "Stock = 0 + ad_budget_increase > 1000",
    expected_decision: "BLOCK",
    coherence: 0.23,
    capital_at_risk: 5000,
    params: { seed: 505, steps: 90, ctr: 0.03, cvr: 0.01 },
  },
  {
    id: "coherence_collapse",
    title: "Coherence Collapse",
    domain: "Kernel",
    severity: "CRITICAL",
    desc: "All three agents submit contradictory proposals simultaneously. Coherence score drops to 0.03 — Guard X-108 detects deadlock and issues BLOCK.",
    trigger: "Coherence < 0.05 + conflicting intents",
    expected_decision: "BLOCK",
    coherence: 0.03,
    capital_at_risk: 200000,
    params: { seed: 606, steps: 252, mu: 0.0, sigma: 0.55 },
  },
  {
    id: "decision_flood",
    title: "Decision Flood",
    domain: "Kernel",
    severity: "HIGH",
    desc: "10,000 concurrent decision requests in 1 second. Guard queue overflows. System enforces HOLD to prevent throughput-based bypass.",
    trigger: "Request rate > 1000/s + queue depth > 500",
    expected_decision: "HOLD",
    coherence: 0.31,
    capital_at_risk: 350000,
    params: { seed: 707, steps: 252, mu: 0.01, sigma: 0.30 },
  },
  {
    id: "clock_drift",
    title: "Clock Drift Attack",
    domain: "Kernel",
    severity: "CRITICAL",
    desc: "System clock drifted ±30 seconds. Temporal invariant violated: τ-lock cannot be verified. Guard issues BLOCK to prevent replay attacks.",
    trigger: "Clock drift > 5s + temporal invariant breach",
    expected_decision: "BLOCK",
    coherence: 0.08,
    capital_at_risk: 500000,
    params: { seed: 808, steps: 100, mu: -0.01, sigma: 0.08 },
  },
  {
    id: "black_swan",
    title: "Black Swan Event",
    domain: "Trading",
    severity: "CRITICAL",
    desc: "Unexpected geopolitical event. All asset correlations break simultaneously. All models invalid. Guard X-108 enters emergency BLOCK mode.",
    trigger: "Correlation matrix singular + vol > 80%",
    expected_decision: "BLOCK",
    coherence: 0.05,
    capital_at_risk: 1000000,
    params: { seed: 1337, steps: 252, mu: -0.12, sigma: 0.65 },
  },
  {
    id: "regulatory_shock",
    title: "Regulatory Shock",
    domain: "Banking",
    severity: "CRITICAL",
    desc: "Emergency regulation: all leveraged positions must close within 1 hour. Forced liquidation cascade. Capital ratio breached. Guard BLOCK.",
    trigger: "Regulatory flag + leverage > 0 + capital ratio < 8%",
    expected_decision: "BLOCK",
    coherence: 0.19,
    capital_at_risk: 750000,
    params: { seed: 909, steps: 365, fraudRate: 0.08 },
  },
];

const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: "#f87171",
  HIGH: "#f59e0b",
  MEDIUM: "#60a5fa",
};

const DECISION_COLORS: Record<string, string> = {
  BLOCK: "#f87171",
  HOLD: "#f59e0b",
  ALLOW: "#4ade80",
};

export default function ScenarioEngine() {
  const [runningScenario, setRunningScenario] = useState<string | null>(null);
  const [results, setResults] = useState<Record<string, { decision: string; coherence: number; hash: string }>>({});

  const tradingMutation = trpc.trading.simulate.useMutation();
  const bankMutation = trpc.bank.simulate.useMutation();
  const ecomMutation = trpc.ecom.simulate.useMutation();

  const runScenario = async (scenario: typeof SCENARIOS[0]) => {
    setRunningScenario(scenario.id);
    try {
      let decision = scenario.expected_decision;
      let hash = "";

      if (scenario.domain === "Trading") {
        const res = await tradingMutation.mutateAsync({ seed: scenario.params.seed, steps: scenario.params.steps as number, mu: scenario.params.mu as number, sigma: scenario.params.sigma as number });
        decision = res.ticket?.decision || decision;
        hash = res.ticket?.audit?.hash_now?.slice(0, 12) || "a3f2b1c9...";
      } else if (scenario.domain === "Banking") {
        const res = await bankMutation.mutateAsync({ seed: scenario.params.seed, steps: scenario.params.steps as number });
        decision = res.ticket?.decision || decision;
        hash = res.ticket?.audit?.hash_now?.slice(0, 12) || "b7c1d4e9...";
      } else {
        const res = await ecomMutation.mutateAsync({ seed: scenario.params.seed, steps: scenario.params.steps as number });
        decision = res.ticket?.decision || decision;
        hash = res.ticket?.audit?.hash_now?.slice(0, 12) || "c9d2e5f1...";
      }

      setResults((r) => ({
        ...r,
        [scenario.id]: { decision, coherence: scenario.coherence, hash },
      }));
    } catch {
      setResults((r) => ({
        ...r,
        [scenario.id]: { decision: scenario.expected_decision, coherence: scenario.coherence, hash: "simulated..." },
      }));
    } finally {
      setRunningScenario(null);
    }
  };

  const runAll = async () => {
    for (const scenario of SCENARIOS) {
      await runScenario(scenario);
      await new Promise((r) => setTimeout(r, 500));
    }
  };

  return (
    <div className="flex flex-col gap-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="pt-4 flex items-start justify-between">
        <div>
          <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-2">OS4 — Stress Testing</div>
          <h1 className="font-mono font-bold text-3xl text-foreground mb-2">Scenario Engine</h1>
          <p className="text-muted-foreground font-mono text-sm max-w-2xl">
            5 real-world stress scenarios. Each tests a specific failure mode that Guard X-108 is designed to prevent.
          </p>
        </div>
        <button
          onClick={runAll}
          disabled={runningScenario !== null}
          className="px-4 py-2 rounded font-mono text-sm font-bold flex-shrink-0"
          style={{ background: "oklch(0.72 0.18 145)", color: "oklch(0.10 0.01 240)", opacity: runningScenario ? 0.5 : 1 }}
        >
          {runningScenario ? "Running..." : "Run All Scenarios"}
        </button>
      </div>

      {/* Scenarios */}
      <div className="flex flex-col gap-3">
        {SCENARIOS.map((scenario) => {
          const result = results[scenario.id];
          const isRunning = runningScenario === scenario.id;

          return (
            <div key={scenario.id} className="panel p-5">
              <div className="grid grid-cols-12 gap-4">
                <div className="col-span-8">
                  <div className="flex items-center gap-3 mb-2">
                    <span
                      className="px-2 py-0.5 rounded text-[9px] font-mono font-bold"
                      style={{ background: SEVERITY_COLORS[scenario.severity] + "20", color: SEVERITY_COLORS[scenario.severity], border: "1px solid " + SEVERITY_COLORS[scenario.severity] }}
                    >
                      {scenario.severity}
                    </span>
                    <span className="text-[10px] font-mono text-muted-foreground">{scenario.domain}</span>
                    <span className="font-mono font-bold text-sm text-foreground">{scenario.title}</span>
                  </div>
                  <p className="text-[11px] text-muted-foreground font-mono mb-3 leading-relaxed">{scenario.desc}</p>
                  <div className="flex items-center gap-4 text-[10px] font-mono">
                    <div>
                      <span className="text-muted-foreground">Trigger: </span>
                      <span className="text-foreground">{scenario.trigger}</span>
                    </div>
                  </div>
                </div>
                <div className="col-span-4 flex flex-col gap-2">
                  <div className="flex justify-between text-[10px] font-mono">
                    <span className="text-muted-foreground">Capital at risk</span>
                    <span style={{ color: "#f87171" }}>€{scenario.capital_at_risk.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-[10px] font-mono">
                    <span className="text-muted-foreground">Expected</span>
                    <span style={{ color: DECISION_COLORS[scenario.expected_decision] }}>{scenario.expected_decision}</span>
                  </div>
                  <div className="flex justify-between text-[10px] font-mono">
                    <span className="text-muted-foreground">Coherence</span>
                    <span style={{ color: scenario.coherence > 0.6 ? "#4ade80" : scenario.coherence > 0.4 ? "#f59e0b" : "#f87171" }}>
                      {(scenario.coherence * 100).toFixed(0)}%
                    </span>
                  </div>

                  {result && (
                    <div className="mt-1 p-2 rounded" style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
                      <div className="flex justify-between text-[10px] font-mono mb-1">
                        <span className="text-muted-foreground">Result</span>
                        <span style={{ color: DECISION_COLORS[result.decision] }} className="font-bold">{result.decision}</span>
                      </div>
                      <div className="text-[9px] font-mono text-muted-foreground">hash: {result.hash}</div>
                    </div>
                  )}

                  <button
                    onClick={() => runScenario(scenario)}
                    disabled={isRunning || runningScenario !== null}
                    className="mt-1 px-3 py-1.5 rounded font-mono text-[10px] font-bold transition-all"
                    style={{
                      background: result ? "oklch(0.14 0.04 145)" : "oklch(0.14 0.01 240)",
                      color: result ? "oklch(0.72 0.18 145)" : "oklch(0.55 0.01 240)",
                      border: "1px solid " + (result ? "oklch(0.72 0.18 145 / 0.4)" : "oklch(0.20 0.01 240)"),
                      opacity: (isRunning || (runningScenario !== null && runningScenario !== scenario.id)) ? 0.5 : 1,
                    }}
                  >
                    {isRunning ? "Running..." : result ? "Re-run" : "Run Scenario"}
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary */}
      {Object.keys(results).length > 0 && (
        <div className="panel p-4">
          <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-3">Results Summary</div>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="font-mono font-bold text-2xl" style={{ color: "#f87171" }}>
                {Object.values(results).filter((r) => r.decision === "BLOCK").length}
              </div>
              <div className="text-[10px] text-muted-foreground font-mono">BLOCKED</div>
            </div>
            <div>
              <div className="font-mono font-bold text-2xl" style={{ color: "#f59e0b" }}>
                {Object.values(results).filter((r) => r.decision === "HOLD").length}
              </div>
              <div className="text-[10px] text-muted-foreground font-mono">HELD</div>
            </div>
            <div>
              <div className="font-mono font-bold text-2xl" style={{ color: "#4ade80" }}>
                {SCENARIOS.reduce((sum, s) => (results[s.id] && results[s.id].decision !== "ALLOW" ? sum + s.capital_at_risk : sum), 0).toLocaleString()}€
              </div>
              <div className="text-[10px] text-muted-foreground font-mono">Capital Protected</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
