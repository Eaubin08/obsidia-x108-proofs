/**
 * SimulationWorlds.tsx — OS4 v31 — Hub de simulation avec Decision Pipeline
 */
import React, { useState } from "react";
import { Link } from "wouter";
import { useViewMode } from "@/contexts/ViewModeContext";

const FLUX_STEPS = [
  { id: "market", label: "Market", icon: "📊", href: "/market" },
  { id: "simulation", label: "Simulation", icon: "🔬", href: "/simulation-worlds" },
  { id: "agents", label: "Agents", icon: "🤖", href: "/agents" },
  { id: "decision", label: "Decision", icon: "⚖", href: "/stream" },
  { id: "guard", label: "Guard X-108", icon: "🛡", href: "/engine" },
  { id: "proof", label: "Proof", icon: "⛓", href: "/proof-center" },
];

function FluxBar({ active }: { active: string }) {
  return (
    <div className="flex items-center justify-center gap-0 mb-8 flex-wrap">
      {FLUX_STEPS.map((step, i) => (
        <React.Fragment key={step.id}>
          <Link href={step.href}>
            <div className="flex items-center gap-1.5 px-3 py-2 rounded font-mono text-[10px] font-bold cursor-pointer"
              style={{ background: step.id === active ? "oklch(0.72 0.18 145 / 0.15)" : "oklch(0.12 0.01 240)", border: `1px solid ${step.id === active ? "oklch(0.72 0.18 145)" : "oklch(0.20 0.01 240)"}`, color: step.id === active ? "oklch(0.72 0.18 145)" : "oklch(0.45 0.01 240)" }}>
              <span>{step.icon}</span><span>{step.label}</span>
            </div>
          </Link>
          {i < FLUX_STEPS.length - 1 && <div className="px-1.5 font-mono text-[10px]" style={{ color: "oklch(0.30 0.01 240)" }}>→</div>}
        </React.Fragment>
      ))}
    </div>
  );
}

type Domain = "trading" | "bank" | "ecom";
type PipelineStatus = "pending" | "running" | "completed" | "blocked";

interface Scenario {
  id: string; label: string; description: string; descriptionSimple: string;
  agent: string; agentAction: string; agentConfidence: number;
  guardDecision: "ALLOW" | "HOLD" | "BLOCK"; guardReason: string;
  temporalLock: number; consensusVotes: number; consensusTotal: number;
  proofHash: string; href: string;
}

const SCENARIOS: Record<Domain, Scenario[]> = {
  trading: [
    { id: "market-crash", label: "Market Crash", description: "BTC drops 20% in 4 hours. Volatility spikes to 0.08. Agent Alpha generates SELL signal.", descriptionSimple: "The market crashes. The agent wants to sell. The Guard pauses to verify.", agent: "Agent Alpha", agentAction: "SELL 1.5 BTC", agentConfidence: 0.41, guardDecision: "HOLD", guardReason: "Coherence threshold not met (0.18 < 0.45)", temporalLock: 10, consensusVotes: 3, consensusTotal: 4, proofHash: "a3f8c2d1e9b7...", href: "/simulation-worlds/trading" },
    { id: "flash-pump", label: "Flash Pump", description: "BTC surges +15% in 30 minutes. High liquidity, coherence 0.82. Agent Alpha buys.", descriptionSimple: "The market spikes up. The agent wants to buy. The Guard validates.", agent: "Agent Alpha", agentAction: "BUY 0.5 BTC", agentConfidence: 0.82, guardDecision: "ALLOW", guardReason: "Coherence 0.82 — within safe threshold", temporalLock: 10, consensusVotes: 4, consensusTotal: 4, proofHash: "b7e1a4f2c8d3...", href: "/simulation-worlds/trading" },
    { id: "liquidity-drain", label: "Liquidity Drain", description: "Market depth collapses. Slippage exceeds 3%. Agent Alpha proposes large sell order.", descriptionSimple: "Very low liquidity. The agent wants to sell but the Guard blocks it.", agent: "Agent Alpha", agentAction: "SELL 2.0 BTC", agentConfidence: 0.29, guardDecision: "BLOCK", guardReason: "Slippage > 3% — execution risk too high", temporalLock: 10, consensusVotes: 1, consensusTotal: 4, proofHash: "c2d5f8a1b3e7...", href: "/simulation-worlds/trading" },
  ],
  bank: [
    { id: "fraud-detection", label: "Fraud Detection", description: "€48,000 wire to unknown IBAN at 3am. Risk score 0.89. Sentinel flags as fraud.", descriptionSimple: "A suspicious transfer is detected. The agent flags it. The Guard blocks it.", agent: "Agent Sentinel", agentAction: "FLAG TRANSFER €48,000", agentConfidence: 0.89, guardDecision: "BLOCK", guardReason: "Risk score 0.89 — fraud threshold exceeded", temporalLock: 10, consensusVotes: 4, consensusTotal: 4, proofHash: "d4e9b2c7f1a8...", href: "/simulation-worlds/bank" },
    { id: "large-transfer", label: "Large Transfer", description: "€50,000 transfer to known business partner. Risk score 0.72. Sentinel requests review.", descriptionSimple: "A large transfer is initiated. The agent is uncertain. The Guard pauses for review.", agent: "Agent Sentinel", agentAction: "REVIEW TRANSFER €50,000", agentConfidence: 0.61, guardDecision: "HOLD", guardReason: "Amount exceeds threshold — manual review required", temporalLock: 10, consensusVotes: 2, consensusTotal: 4, proofHash: "e8f3a6d2c1b9...", href: "/simulation-worlds/bank" },
    { id: "aml-check", label: "AML Check", description: "Regular €5,000 payment to verified merchant. Risk score 0.08. Sentinel approves.", descriptionSimple: "A normal payment is verified. The agent approves it. The Guard allows.", agent: "Agent Sentinel", agentAction: "APPROVE PAYMENT €5,000", agentConfidence: 0.94, guardDecision: "ALLOW", guardReason: "Risk score 0.08 — within safe threshold", temporalLock: 10, consensusVotes: 4, consensusTotal: 4, proofHash: "f1b7e4c9a2d5...", href: "/simulation-worlds/bank" },
  ],
  ecom: [
    { id: "demand-spike", label: "Demand Spike", description: "Product demand +300% in 2 hours. Stock critically low. Mercury proposes price adjustment.", descriptionSimple: "A product goes viral. The agent wants to raise the price. The Guard validates.", agent: "Agent Mercury", agentAction: "RAISE PRICE +25%", agentConfidence: 0.77, guardDecision: "ALLOW", guardReason: "Demand signal coherent — price adjustment validated", temporalLock: 10, consensusVotes: 4, consensusTotal: 4, proofHash: "a9c3f7b2e1d6...", href: "/simulation-worlds/ecom" },
    { id: "price-war", label: "Price War", description: "Competitor drops price 40%. Mercury proposes aggressive counter-discount.", descriptionSimple: "A competitor cuts prices. The agent wants to match. The Guard pauses to check margins.", agent: "Agent Mercury", agentAction: "DISCOUNT −35%", agentConfidence: 0.52, guardDecision: "HOLD", guardReason: "Margin impact unclear — coherence 0.52", temporalLock: 10, consensusVotes: 2, consensusTotal: 4, proofHash: "b4d8f2a6c9e3...", href: "/simulation-worlds/ecom" },
    { id: "inventory-shock", label: "Inventory Shock", description: "Stock = 0. Mercury proposes flash sale. Guard blocks — no inventory.", descriptionSimple: "The product is out of stock. The agent wants a sale. The Guard blocks it.", agent: "Agent Mercury", agentAction: "FLASH SALE −30%", agentConfidence: 0.31, guardDecision: "BLOCK", guardReason: "Stock = 0 — execution impossible", temporalLock: 10, consensusVotes: 0, consensusTotal: 4, proofHash: "c7e1b5f9a3d2...", href: "/simulation-worlds/ecom" },
  ],
};

const DOMAIN_CONFIG = {
  trading: { label: "Trading", icon: "📈", color: "oklch(0.72 0.18 145)", agent: "Agent Alpha" },
  bank: { label: "Bank", icon: "🏦", color: "oklch(0.60 0.12 200)", agent: "Agent Sentinel" },
  ecom: { label: "E-Commerce", icon: "🛒", color: "#f59e0b", agent: "Agent Mercury" },
};

function DecisionPipeline({ scenario, isSimple }: { scenario: Scenario; isSimple: boolean }) {
  const DC: Record<string, string> = { ALLOW: "oklch(0.72 0.18 145)", HOLD: "#f59e0b", BLOCK: "#f87171" };
  const steps: Array<{ id: string; label: string; icon: string; status: PipelineStatus; detail: string; detailSimple: string }> = [
    { id: "scenario", label: "Scenario", icon: "🔬", status: "completed", detail: scenario.description, detailSimple: scenario.descriptionSimple },
    { id: "agent", label: "Agent Signal", icon: "🤖", status: "completed", detail: `${scenario.agent} → ${scenario.agentAction} (confidence: ${scenario.agentConfidence.toFixed(2)})`, detailSimple: `${scenario.agent} proposes: ${scenario.agentAction}` },
    { id: "guard", label: "Guard X-108", icon: "🛡", status: scenario.guardDecision === "BLOCK" ? "blocked" : "completed", detail: `Decision: ${scenario.guardDecision} — ${scenario.guardReason}`, detailSimple: `Guard says: ${scenario.guardDecision} — ${scenario.guardReason}` },
    { id: "temporal", label: "Temporal Lock", icon: "⏱", status: scenario.guardDecision === "BLOCK" ? "blocked" : "completed", detail: `X-108 temporal gate: ${scenario.temporalLock}s hold window applied`, detailSimple: `The system waits ${scenario.temporalLock} seconds before executing` },
    { id: "consensus", label: "Consensus", icon: "🗳", status: scenario.guardDecision === "BLOCK" ? "blocked" : scenario.consensusVotes >= 3 ? "completed" : "running", detail: `${scenario.consensusVotes}/${scenario.consensusTotal} nodes voted`, detailSimple: `${scenario.consensusVotes} out of ${scenario.consensusTotal} nodes agreed` },
    { id: "proof", label: "Proof", icon: "⛓", status: scenario.guardDecision === "BLOCK" ? "blocked" : scenario.consensusVotes >= 3 ? "completed" : "pending", detail: `Merkle anchor — hash: ${scenario.proofHash}`, detailSimple: "The decision is cryptographically recorded" },
  ];
  const SC: Record<PipelineStatus, string> = { pending: "oklch(0.35 0.01 240)", running: "#f59e0b", completed: "oklch(0.72 0.18 145)", blocked: "#f87171" };
  const SB: Record<PipelineStatus, string> = { pending: "oklch(0.14 0.01 240)", running: "#f59e0b22", completed: "oklch(0.72 0.18 145 / 0.12)", blocked: "#f8717122" };
  const SL: Record<PipelineStatus, string> = { pending: "PENDING", running: "RUNNING", completed: "COMPLETED", blocked: "BLOCKED" };
  return (
    <div className="rounded-lg overflow-hidden" style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
      <div className="p-4" style={{ borderBottom: "1px solid oklch(0.18 0.01 240)" }}>
        <div className="font-mono text-[9px] font-bold tracking-widest" style={{ color: "oklch(0.45 0.01 240)" }}>DECISION PIPELINE — {scenario.label.toUpperCase()}</div>
      </div>
      <div className="p-4">
        {steps.map((step, i) => (
          <div key={step.id} className="flex gap-4">
            <div className="flex flex-col items-center">
              <div className="w-8 h-8 rounded-full flex items-center justify-center text-sm flex-shrink-0" style={{ background: SB[step.status], border: `1px solid ${SC[step.status]}` }}>{step.icon}</div>
              {i < steps.length - 1 && <div className="w-px flex-1 my-1" style={{ background: `${SC[step.status]}44`, minHeight: "20px" }} />}
            </div>
            <div className="pb-4 flex-1" style={{ minHeight: i < steps.length - 1 ? "52px" : "auto" }}>
              <div className="flex items-center gap-2 mb-1">
                <span className="font-mono font-bold text-xs text-foreground">{step.label}</span>
                <span className="font-mono text-[8px] px-1.5 py-0.5 rounded" style={{ background: SB[step.status], color: SC[step.status], border: `1px solid ${SC[step.status]}44` }}>{SL[step.status]}</span>
                {step.id === "guard" && <span className="font-mono text-[8px] px-1.5 py-0.5 rounded font-bold" style={{ background: `${DC[scenario.guardDecision]}22`, color: DC[scenario.guardDecision], border: `1px solid ${DC[scenario.guardDecision]}44` }}>{scenario.guardDecision}</span>}
              </div>
              <p className="font-mono text-[10px] leading-relaxed" style={{ color: "oklch(0.50 0.01 240)" }}>{isSimple ? step.detailSimple : step.detail}</p>
            </div>
          </div>
        ))}
      </div>
      <div className="p-4 pt-0">
        <Link href={scenario.href}>
          <button className="w-full py-2.5 rounded font-mono text-xs font-bold" style={{ background: "oklch(0.72 0.18 145)", color: "oklch(0.10 0.01 240)" }}>Run Full Simulation →</button>
        </Link>
      </div>
    </div>
  );
}


export default function SimulationWorlds() {
  const [domain, setDomain] = useState<Domain>("trading");
  const [selectedScenario, setSelectedScenario] = useState<string>("market-crash");
  const { isSimple } = useViewMode();
  const scenarios = SCENARIOS[domain];
  const scenario = scenarios.find(s => s.id === selectedScenario) ?? scenarios[0];
  const domainConfig = DOMAIN_CONFIG[domain];
  const handleDomainChange = (d: Domain) => { setDomain(d); setSelectedScenario(SCENARIOS[d][0].id); };
  const TABS: { id: Domain; label: string; icon: string; color: string }[] = [
    { id: "trading", label: "Trading", icon: "📈", color: "oklch(0.72 0.18 145)" },
    { id: "bank", label: "Bank", icon: "🏦", color: "oklch(0.60 0.12 200)" },
    { id: "ecom", label: "E-Commerce", icon: "🛒", color: "#f59e0b" },
  ];
  const DC: Record<string, string> = { ALLOW: "oklch(0.72 0.18 145)", HOLD: "#f59e0b", BLOCK: "#f87171" };

  return (
    <div className="max-w-5xl mx-auto" style={{ color: "oklch(0.90 0.01 240)", paddingTop: "24px" }}>
      {/* Header */}
      <div className="mb-8">
        <div className="font-mono text-[9px] font-bold tracking-[0.3em] uppercase mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>OBSIDIA LABS — SIMULATION LAYER</div>
        <h1 className="font-mono font-bold text-3xl text-foreground mb-3">Simulation</h1>
        <p className="font-mono text-sm max-w-2xl leading-relaxed" style={{ color: "oklch(0.55 0.01 240)" }}>
          {isSimple
            ? "Choose a domain and a scenario to see how the system reacts. Each scenario shows the full decision pipeline from market signal to cryptographic proof."
            : "Select a domain and scenario to observe the complete governance pipeline: agent signal → X-108 evaluation → temporal lock → distributed consensus → Merkle proof."}
        </p>
      </div>

      {/* Flux visuel */}
      <FluxBar active="simulation" />

      <div className="grid gap-6" style={{ gridTemplateColumns: "1fr 1.4fr" }}>
        {/* Left: domain + scenario selection */}
        <div>
          <div className="font-mono text-[9px] font-bold tracking-widest mb-3" style={{ color: "oklch(0.45 0.01 240)" }}>SELECT DOMAIN</div>
          <div className="flex gap-2 mb-6">
            {TABS.map(tab => (
              <button key={tab.id} onClick={() => handleDomainChange(tab.id)}
                className="flex items-center gap-1.5 px-3 py-2 rounded font-mono text-xs font-bold flex-1 justify-center"
                style={{ background: domain === tab.id ? `${tab.color}20` : "oklch(0.12 0.01 240)", border: `1px solid ${domain === tab.id ? tab.color : "oklch(0.20 0.01 240)"}`, color: domain === tab.id ? tab.color : "oklch(0.45 0.01 240)" }}>
                <span>{tab.icon}</span><span>{tab.label}</span>
              </button>
            ))}
          </div>

          <div className="font-mono text-[9px] font-bold tracking-widest mb-3" style={{ color: "oklch(0.45 0.01 240)" }}>SELECT SCENARIO</div>
          <div className="space-y-2 mb-6">
            {scenarios.map(sc => {
              const isSelected = sc.id === scenario.id;
              return (
                <button key={sc.id} onClick={() => setSelectedScenario(sc.id)} className="w-full text-left p-3 rounded-lg"
                  style={{ background: isSelected ? "oklch(0.14 0.01 240)" : "oklch(0.11 0.01 240)", border: `1px solid ${isSelected ? domainConfig.color : "oklch(0.18 0.01 240)"}` }}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono font-bold text-xs" style={{ color: isSelected ? domainConfig.color : "oklch(0.70 0.01 240)" }}>{sc.label}</span>
                    <span className="font-mono text-[9px] font-bold px-1.5 py-0.5 rounded" style={{ background: `${DC[sc.guardDecision]}22`, color: DC[sc.guardDecision] }}>{sc.guardDecision}</span>
                  </div>
                  <p className="font-mono text-[9px] leading-relaxed" style={{ color: "oklch(0.45 0.01 240)" }}>{isSimple ? sc.descriptionSimple : sc.description}</p>
                </button>
              );
            })}
          </div>

          {/* Agent info */}
          <div className="rounded-lg p-4" style={{ background: "oklch(0.10 0.01 240)", border: `1px solid ${domainConfig.color}33` }}>
            <div className="font-mono text-[9px] font-bold tracking-widest mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>ASSIGNED AGENT</div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center text-base" style={{ background: `${domainConfig.color}22`, border: `1px solid ${domainConfig.color}44` }}>{domainConfig.icon}</div>
              <div>
                <div className="font-mono font-bold text-sm text-foreground">{domainConfig.agent}</div>
                <div className="font-mono text-[9px]" style={{ color: domainConfig.color }}>{domainConfig.label} domain</div>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Decision Pipeline */}
        <div>
          <div className="font-mono text-[9px] font-bold tracking-widest mb-3" style={{ color: "oklch(0.45 0.01 240)" }}>DECISION PIPELINE</div>
          <DecisionPipeline scenario={scenario} isSimple={isSimple} />
        </div>
      </div>

      {/* Bottom: world cards */}
      <div className="mt-10">
        <div className="font-mono text-[9px] font-bold tracking-widest mb-4" style={{ color: "oklch(0.45 0.01 240)" }}>FULL SIMULATION ENVIRONMENTS</div>
        <div className="grid grid-cols-3 gap-4">
          {[
            { id: "trading", label: "TradingWorld", icon: "📈", color: "oklch(0.72 0.18 145)", desc: "GBM + Markov regimes + GARCH volatility", href: "/simulation-worlds/trading" },
            { id: "bank", label: "BankWorld", icon: "🏦", color: "oklch(0.60 0.12 200)", desc: "Log-normal cash flows + 4 fraud gauges", href: "/simulation-worlds/bank" },
            { id: "ecom", label: "EcomWorld", icon: "🛒", color: "#f59e0b", desc: "CTR/CVR/ROAS funnel + 3 AI agents", href: "/simulation-worlds/ecom" },
          ].map(world => (
            <Link key={world.id} href={world.href}>
              <div className="rounded-lg p-4 cursor-pointer" style={{ background: "oklch(0.10 0.01 240)", border: `1px solid ${world.color}33` }}>
                <div className="text-2xl mb-2">{world.icon}</div>
                <div className="font-mono font-bold text-sm mb-1" style={{ color: world.color }}>{world.label}</div>
                <p className="font-mono text-[9px]" style={{ color: "oklch(0.45 0.01 240)" }}>{world.desc}</p>
                <div className="font-mono text-[9px] mt-3" style={{ color: world.color }}>Launch →</div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
