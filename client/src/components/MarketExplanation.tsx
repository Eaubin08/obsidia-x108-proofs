import React, { useState } from "react";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface MarketExplanationProps {
  domain: "trading" | "bank" | "ecom";
}

// ─── Data per domain ──────────────────────────────────────────────────────────

const DOMAIN_DATA = {
  trading: {
    title: "Trading World — Market Simulation",
    subtitle: "Stochastic Financial Market",
    worldDesc: "This trading world simulates a financial market. The price dynamics follow a stochastic model combining Geometric Brownian Motion for long-term drift, Markov regime switching for bull / bear / crash conditions, GARCH volatility clustering, and jump diffusion for sudden shocks. The goal is to test whether the Obsidia governance kernel can protect autonomous trading agents during unstable markets.",
    worldIcon: "📈",
    agentDesc: "The autonomous trading agent perceives market state (price, volatility, regime, coherence) and proposes irreversible actions: BUY, SELL, or HOLD. Each proposal is submitted to the Guard X-108 before execution.",
    engineDesc: "The OS4 engine evaluates the agent's proposal against 4 invariants: coherence threshold (≥0.60), volatility gate, temporal lock (τ=10s), and risk killswitch (max drawdown 20%). The engine computes a coherence score from market features.",
    guardDesc: "Guard X-108 applies the BLOCK > HOLD > ALLOW hierarchy. During a flash crash (coherence < 0.30), it BLOCKs the trade. During high volatility (coherence 0.30–0.60), it HOLDs for τ=10s. Only when coherence ≥ 0.60 does it ALLOW execution.",
    proofDesc: "Every decision is cryptographically anchored: Merkle root (tamper-evident log), RFC3161 timestamp (Strasbourg Clock), Lean4 theorem X108-2 (no irreversible action before τ), TLA+ invariant TemporalSafety.",
    layers: [
      { key: "WORLD", label: "Market World", color: "#60a5fa", icon: "🌍" },
      { key: "AGENT", label: "Trading Agent", color: "#a78bfa", icon: "🤖" },
      { key: "ENGINE", label: "OS4 Engine", color: "#fbbf24", icon: "⚙️" },
      { key: "GUARD", label: "Guard X-108", color: "#f87171", icon: "🛡️" },
      { key: "PROOF", label: "Cryptographic Proof", color: "#4ade80", icon: "🔐" },
    ],
  },
  bank: {
    title: "Bank World — Financial Institution Simulation",
    subtitle: "Log-Normal Cash Flow Model",
    worldDesc: "This banking world simulates a financial institution managing cash flows, credit risk, and fraud detection. Cash flows follow a log-normal distribution. The model tracks four risk indicators: IR (Integrity Ratio), CIZ (Cash Integrity Zone), DTS (Decision Temporal Score), and TSG (Trust Score Guard). The goal is to test whether the Obsidia kernel can detect and block fraudulent transactions before they execute.",
    worldIcon: "🏦",
    agentDesc: "The banking agent processes transactions (transfers, withdrawals, credit operations) and proposes irreversible financial actions. Each transaction is scored against the 4 risk indicators before being submitted to Guard X-108.",
    engineDesc: "The OS4 engine evaluates each transaction against business invariants: IR < 0.85 triggers BLOCK, CIZ anomaly triggers HOLD, DTS < 0.70 triggers HOLD, TSG < 0.50 triggers BLOCK. The engine computes a composite coherence score from all 4 indicators.",
    guardDesc: "Guard X-108 applies the BLOCK > HOLD > ALLOW hierarchy. A fraud attempt (IR=0.95) is immediately BLOCKed. A suspicious transaction (CIZ anomaly) is HOLDed for τ=10s for recomputation. Only clean transactions (all 4 indicators green) are ALLOWed.",
    proofDesc: "Every banking decision is cryptographically anchored: Merkle root (tamper-evident audit trail), RFC3161 timestamp, Lean4 theorem IG-1 (integrity gate invariant), TLA+ invariant FailClosed (system fails safe on ambiguity).",
    layers: [
      { key: "WORLD", label: "Bank World", color: "#60a5fa", icon: "🌍" },
      { key: "AGENT", label: "Banking Agent", color: "#a78bfa", icon: "🤖" },
      { key: "ENGINE", label: "OS4 Engine", color: "#fbbf24", icon: "⚙️" },
      { key: "GUARD", label: "Guard X-108", color: "#f87171", icon: "🛡️" },
      { key: "PROOF", label: "Cryptographic Proof", color: "#4ade80", icon: "🔐" },
    ],
  },
  ecom: {
    title: "E-Commerce World — Marketplace Simulation",
    subtitle: "Traffic Funnel & Agent Coordination",
    worldDesc: "This e-commerce world simulates a marketplace with autonomous agents managing inventory, pricing, and order fulfillment. The model tracks CTR (Click-Through Rate), CVR (Conversion Rate), ROAS (Return on Ad Spend), and margin. Agents can trigger irreversible actions: flash sales, bulk orders, price changes. The goal is to test whether the Obsidia kernel can prevent agents from executing harmful commercial decisions.",
    worldIcon: "🛒",
    agentDesc: "Multiple autonomous agents (pricing agent, inventory agent, campaign agent) perceive marketplace state and propose irreversible commercial actions. Each proposal is scored for coherence before being submitted to Guard X-108.",
    engineDesc: "The OS4 engine evaluates each commercial action against business invariants: margin < 5% triggers BLOCK, ROAS < 1.0 triggers HOLD, CVR anomaly triggers HOLD, inventory depletion risk triggers BLOCK. The engine computes a coherence score from funnel metrics.",
    guardDesc: "Guard X-108 applies the BLOCK > HOLD > ALLOW hierarchy. A flash sale that would destroy margin (coherence < 0.30) is BLOCKed. A bulk order during low inventory (coherence 0.30–0.60) is HOLDed for τ=10s. Only profitable actions (coherence ≥ 0.60) are ALLOWed.",
    proofDesc: "Every commercial decision is cryptographically anchored: Merkle root (tamper-evident order log), RFC3161 timestamp, Lean4 theorem C-1 (coherence invariant), TLA+ invariant BlockPriority (BLOCK always overrides ALLOW).",
    layers: [
      { key: "WORLD", label: "E-Commerce World", color: "#60a5fa", icon: "🌍" },
      { key: "AGENT", label: "Commerce Agent", color: "#a78bfa", icon: "🤖" },
      { key: "ENGINE", label: "OS4 Engine", color: "#fbbf24", icon: "⚙️" },
      { key: "GUARD", label: "Guard X-108", color: "#f87171", icon: "🛡️" },
      { key: "PROOF", label: "Cryptographic Proof", color: "#4ade80", icon: "🔐" },
    ],
  },
};

const LAYER_CONTENT: Record<string, Record<string, string>> = {
  trading: {
    WORLD: "worldDesc",
    AGENT: "agentDesc",
    ENGINE: "engineDesc",
    GUARD: "guardDesc",
    PROOF: "proofDesc",
  },
  bank: {
    WORLD: "worldDesc",
    AGENT: "agentDesc",
    ENGINE: "engineDesc",
    GUARD: "guardDesc",
    PROOF: "proofDesc",
  },
  ecom: {
    WORLD: "worldDesc",
    AGENT: "agentDesc",
    ENGINE: "engineDesc",
    GUARD: "guardDesc",
    PROOF: "proofDesc",
  },
};

// ─── Component ────────────────────────────────────────────────────────────────

export default function MarketExplanation({ domain }: MarketExplanationProps) {
  const [activeLayer, setActiveLayer] = useState<string>("WORLD");
  const [expanded, setExpanded] = useState(true);

  const data = DOMAIN_DATA[domain];
  const activeLayerData = data.layers.find(l => l.key === activeLayer)!;
  const contentKey = LAYER_CONTENT[domain][activeLayer] as keyof typeof data;
  const activeContent = data[contentKey] as string;

  return (
    <div className="panel p-0 overflow-hidden" style={{ border: "1px solid oklch(0.18 0.02 240)" }}>
      {/* Header */}
      <div
        className="flex items-center justify-between px-5 py-3 cursor-pointer"
        style={{ background: "oklch(0.10 0.02 240)", borderBottom: expanded ? "1px solid oklch(0.18 0.02 240)" : "none" }}
        onClick={() => setExpanded(e => !e)}
      >
        <div className="flex items-center gap-3">
          <span className="text-lg">{data.worldIcon}</span>
          <div>
            <div className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">World Explained</div>
            <div className="font-mono font-bold text-sm text-foreground">{data.title}</div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[9px] font-mono px-2 py-0.5 rounded" style={{ background: "oklch(0.72 0.18 145 / 0.15)", color: "#4ade80", border: "1px solid oklch(0.72 0.18 145 / 0.3)" }}>
            {data.subtitle}
          </span>
          <span className="text-muted-foreground text-xs">{expanded ? "▲" : "▼"}</span>
        </div>
      </div>

      {expanded && (
        <div className="p-5">
          {/* Pipeline tabs */}
          <div className="flex items-center gap-0 mb-5">
            {data.layers.map((layer, idx) => (
              <React.Fragment key={layer.key}>
                <button
                  onClick={() => setActiveLayer(layer.key)}
                  className="flex items-center gap-1.5 px-3 py-2 rounded text-[10px] font-mono font-bold transition-all"
                  style={{
                    background: activeLayer === layer.key ? `${layer.color}20` : "transparent",
                    color: activeLayer === layer.key ? layer.color : "oklch(0.50 0.01 240)",
                    border: `1px solid ${activeLayer === layer.key ? layer.color + "60" : "oklch(0.20 0.01 240)"}`,
                  }}
                >
                  <span>{layer.icon}</span>
                  <span>{layer.key}</span>
                </button>
                {idx < data.layers.length - 1 && (
                  <div className="text-[10px] px-1" style={{ color: "oklch(0.30 0.01 240)" }}>→</div>
                )}
              </React.Fragment>
            ))}
          </div>

          {/* Active layer content */}
          <div className="rounded p-4" style={{ background: `${activeLayerData.color}08`, border: `1px solid ${activeLayerData.color}30` }}>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-base">{activeLayerData.icon}</span>
              <span className="font-mono font-bold text-sm" style={{ color: activeLayerData.color }}>{activeLayerData.label}</span>
            </div>
            <p className="text-sm text-muted-foreground font-mono leading-relaxed">{activeContent}</p>
          </div>

          {/* Quick summary row */}
          <div className="mt-4 grid grid-cols-5 gap-2">
            {data.layers.map(layer => (
              <div
                key={layer.key}
                className="text-center p-2 rounded cursor-pointer"
                style={{
                  background: activeLayer === layer.key ? `${layer.color}15` : "oklch(0.08 0.01 240)",
                  border: `1px solid ${activeLayer === layer.key ? layer.color + "40" : "oklch(0.15 0.01 240)"}`,
                }}
                onClick={() => setActiveLayer(layer.key)}
              >
                <div className="text-base">{layer.icon}</div>
                <div className="text-[8px] font-mono mt-1" style={{ color: activeLayer === layer.key ? layer.color : "oklch(0.40 0.01 240)" }}>{layer.key}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
