/**
 * CausalPipeline.tsx — OS4 v13
 * Composant réutilisable : boucle complète WORLD→AGENT→ENGINE→GUARD→DECISION→PROOF
 * Chaque page doit répondre aux 6 questions fondamentales.
 * Adapté par domaine : TRADING / BANK / ECOM
 */
import React from "react";

export type PipelineDomain = "TRADING" | "BANK" | "ECOM";

interface CausalPipelineProps {
  domain: PipelineDomain;
  /** Live metrics injected from the parent page */
  metrics?: {
    volatility?: number;
    coherence?: number;
    regime?: string;
    guardDecision?: "BLOCK" | "HOLD" | "ALLOW";
    guardReason?: string;
    proposal?: string;
    proofHash?: string;
  };
  compact?: boolean;
}

const DOMAIN_CONFIG: Record<PipelineDomain, {
  worldLabel: string;
  worldItems: string[];
  agentLabel: string;
  agentItems: string[];
  engineItems: string[];
  decisionItems: string[];
}> = {
  TRADING: {
    worldLabel: "Financial Market",
    worldItems: ["price · volatility · regime", "order book · liquidity", "funding rate · volume"],
    agentLabel: "Trading Agent",
    agentItems: ["observes price trend", "evaluates volatility", "proposes BUY / SELL / HOLD"],
    engineItems: ["coherence score", "volatility analysis", "regime classification", "risk evaluation"],
    decisionItems: ["order allowed", "order blocked", "order delayed (HOLD)"],
  },
  BANK: {
    worldLabel: "Banking System",
    worldItems: ["accounts · transactions", "liquidity · reserves", "IR · CIZ · DTS · TSG"],
    agentLabel: "Banking Agent",
    agentItems: ["analyzes transfer intent", "evaluates counterparty risk", "proposes AUTHORIZE / BLOCK"],
    engineItems: ["IR — integrity ratio", "CIZ — coherence integrity zone", "DTS — decision time score", "TSG — temporal safety gate"],
    decisionItems: ["transfer authorized", "transfer blocked", "transfer delayed (HOLD)"],
  },
  ECOM: {
    worldLabel: "Marketplace",
    worldItems: ["traffic · demand · price", "inventory · conversion rate", "competitor pricing · ROAS"],
    agentLabel: "Pricing Agent",
    agentItems: ["observes demand signals", "evaluates price elasticity", "proposes PRICE UPDATE / PROMOTION"],
    engineItems: ["demand coherence", "price elasticity score", "inventory risk", "revenue impact"],
    decisionItems: ["price update allowed", "promotion blocked", "action delayed (HOLD)"],
  },
};

export default function CausalPipeline({ domain, metrics, compact = false }: CausalPipelineProps) {
  const cfg = DOMAIN_CONFIG[domain];

  const guardColor = !metrics?.guardDecision ? "oklch(0.60 0.01 240)"
    : metrics.guardDecision === "ALLOW" ? "oklch(0.72 0.18 145)"
    : metrics.guardDecision === "HOLD" ? "oklch(0.78 0.18 60)"
    : "oklch(0.65 0.22 25)";

  const steps = [
    {
      num: "①", label: "WORLD", sublabel: cfg.worldLabel,
      color: "oklch(0.65 0.18 240)",
      question: "What is the world?",
      items: cfg.worldItems,
      live: metrics?.regime ? `Regime: ${metrics.regime}` : undefined,
    },
    {
      num: "②", label: "AGENT", sublabel: cfg.agentLabel,
      color: "oklch(0.75 0.18 280)",
      question: "What does the agent try to do?",
      items: cfg.agentItems,
      live: metrics?.proposal ? `Proposal: ${metrics.proposal}` : undefined,
    },
    {
      num: "③", label: "ENGINE", sublabel: "Obsidia Kernel",
      color: "oklch(0.78 0.18 60)",
      question: "Why does the engine evaluate?",
      items: cfg.engineItems,
      live: metrics?.coherence !== undefined ? `Coherence: ${metrics.coherence.toFixed(3)} · Vol: ${metrics.volatility !== undefined ? (metrics.volatility * 100).toFixed(1) + "%" : "—"}` : undefined,
    },
    {
      num: "④", label: "GUARD X-108", sublabel: "Temporal Safety Gate",
      color: guardColor,
      question: "How does X-108 protect?",
      items: ["BLOCK — critical threshold exceeded", "HOLD — temporal lock active", "ALLOW — all invariants satisfied"],
      live: metrics?.guardDecision ? `Decision: ${metrics.guardDecision}` : undefined,
    },
    {
      num: "⑤", label: "DECISION", sublabel: "Authorized Action",
      color: "oklch(0.72 0.18 145)",
      question: "What decision is taken?",
      items: cfg.decisionItems,
      live: metrics?.guardDecision ? (metrics.guardDecision === "ALLOW" ? "✓ Action executed" : metrics.guardDecision === "HOLD" ? "⏸ Action delayed 10s" : "✗ Action rejected") : undefined,
    },
    {
      num: "⑥", label: "PROOF", sublabel: "Cryptographic Anchor",
      color: "oklch(0.60 0.12 200)",
      question: "What proof is produced?",
      items: ["decision hash (SHA-256)", "merkle root inclusion", "RFC3161 timestamp anchor", "replay verifiable"],
      live: metrics?.proofHash ? `Hash: ${metrics.proofHash.slice(0, 18)}…` : undefined,
    },
  ];

  if (compact) {
    // Compact horizontal pipeline bar
    return (
      <div className="p-3 rounded" style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.16 0.01 240)" }}>
        <div className="flex items-center gap-1 flex-wrap">
          {steps.map((step, i) => (
            <React.Fragment key={step.label}>
              <div className="flex flex-col items-center">
                <span className="text-[9px] font-mono font-bold px-2 py-1 rounded" style={{ background: step.color + "15", color: step.color, border: `1px solid ${step.color}30` }}>
                  {step.num} {step.label}
                </span>
                {step.live && (
                  <span className="text-[8px] font-mono mt-0.5" style={{ color: step.color + "cc" }}>{step.live}</span>
                )}
              </div>
              {i < 5 && <span className="text-[10px]" style={{ color: "oklch(0.28 0.01 240)" }}>→</span>}
            </React.Fragment>
          ))}
        </div>
      </div>
    );
  }

  // Full expanded pipeline
  return (
    <div className="p-4 rounded" style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.16 0.01 240)" }}>
      <div className="text-[10px] font-mono font-bold mb-3 tracking-widest" style={{ color: "oklch(0.50 0.01 240)" }}>
        DECISION LIFECYCLE — {domain} DOMAIN
      </div>
      <div className="grid grid-cols-3 gap-3">
        {steps.map(step => (
          <div key={step.label} className="p-3 rounded" style={{ background: "oklch(0.12 0.01 240)", border: `1px solid ${step.color}25` }}>
            {/* Step header */}
            <div className="flex items-center gap-2 mb-2">
              <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded" style={{ background: step.color + "18", color: step.color, border: `1px solid ${step.color}30` }}>
                {step.num} {step.label}
              </span>
            </div>
            {/* Question */}
            <div className="text-[9px] font-mono italic mb-2" style={{ color: "oklch(0.42 0.01 240)" }}>
              {step.question}
            </div>
            {/* Items */}
            <div className="space-y-0.5">
              {step.items.map(item => (
                <div key={item} className="text-[9px] font-mono flex items-start gap-1" style={{ color: "oklch(0.58 0.01 240)" }}>
                  <span style={{ color: step.color + "88" }}>·</span>
                  <span>{item}</span>
                </div>
              ))}
            </div>
            {/* Live metric */}
            {step.live && (
              <div className="mt-2 px-2 py-1 rounded text-[9px] font-mono font-bold" style={{ background: step.color + "12", color: step.color, border: `1px solid ${step.color}25` }}>
                {step.live}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
