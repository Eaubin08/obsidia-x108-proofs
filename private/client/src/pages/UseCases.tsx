import { Link } from "wouter";

const USE_CASES = [
  {
    href: "/use-cases/trading",
    icon: "📈",
    title: "Trading Simulation",
    subtitle: "Financial markets · AI trading agents",
    description:
      "This simulation shows how an AI trading agent interacts with the market. Every proposed trade passes through Guard X-108 before execution. If the action is unsafe — flash crash, pump & dump, liquidity drain — the system blocks it before it happens.",
    scenarios: ["Flash Crash", "Pump & Dump", "Algo War", "Black Swan", "Liquidity Drain", "Bear Market"],
    color: "oklch(0.72 0.18 145)",
    bg: "oklch(0.72 0.18 145 / 0.06)",
    border: "oklch(0.72 0.18 145 / 0.25)",
  },
  {
    href: "/use-cases/banking",
    icon: "🏦",
    title: "Banking Safety Layer",
    subtitle: "Financial institutions · Autonomous transactions",
    description:
      "Banking agents can trigger irreversible transfers, approve large loans, and execute complex financial operations. Guard X-108 evaluates every action against coherence thresholds, risk invariants, and regulatory constraints before authorization.",
    scenarios: ["Bank Run", "CBDC Crisis", "Bail-in", "Fraud Wave", "Liquidity Drain", "Counterparty Default"],
    color: "oklch(0.60 0.12 200)",
    bg: "oklch(0.60 0.12 200 / 0.06)",
    border: "oklch(0.60 0.12 200 / 0.25)",
  },
  {
    href: "/use-cases/ecommerce",
    icon: "🛒",
    title: "E-commerce Automation",
    subtitle: "Commerce agents · Pricing & inventory",
    description:
      "Autonomous commerce agents manage pricing, inventory, fulfillment, and marketing. Without governance, a pricing agent can collapse margins in seconds. Guard X-108 ensures every automated decision respects business invariants and safety constraints.",
    scenarios: ["Traffic Spike", "Inventory Shortage", "Fake Reviews Attack", "Flash Sale", "Bot Traffic", "Regulatory Shock"],
    color: "oklch(0.65 0.18 240)",
    bg: "oklch(0.65 0.18 240 / 0.06)",
    border: "oklch(0.65 0.18 240 / 0.25)",
  },
];

export default function UseCases() {
  return (
    <div className="flex flex-col gap-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="pt-6 pb-2">
        <div className="text-[9px] font-mono tracking-[0.3em] uppercase mb-2" style={{ color: "oklch(0.65 0.18 240)" }}>
          Use Cases
        </div>
        <h1 className="font-mono font-bold text-3xl text-foreground mb-3">
          Guard X-108 across industries
        </h1>
        <p className="font-mono text-sm text-muted-foreground max-w-2xl leading-relaxed">
          Obsidia applies the same governance kernel to three different domains.
          In each case, the pipeline is identical: agent proposes an action, Guard X-108 evaluates it, the decision is recorded with a cryptographic proof.
        </p>
      </div>

      {/* Use case cards */}
      <div className="flex flex-col gap-6">
        {USE_CASES.map((uc) => (
          <div key={uc.href} className="rounded-lg overflow-hidden" style={{ background: uc.bg, border: `1px solid ${uc.border}` }}>
            <div className="p-6">
              <div className="flex items-start gap-5">
                <div className="text-4xl flex-shrink-0 mt-1">{uc.icon}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-1">
                    <h2 className="font-mono font-bold text-xl" style={{ color: uc.color }}>{uc.title}</h2>
                  </div>
                  <div className="text-[10px] font-mono text-muted-foreground mb-3">{uc.subtitle}</div>
                  <p className="font-mono text-sm text-muted-foreground leading-relaxed mb-4">
                    {uc.description}
                  </p>
                  {/* Scenarios */}
                  <div className="flex flex-wrap gap-2 mb-5">
                    {uc.scenarios.map(s => (
                      <span key={s} className="text-[10px] font-mono px-2 py-0.5 rounded"
                        style={{ background: "oklch(0.12 0.01 240)", color: "oklch(0.55 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
                        {s}
                      </span>
                    ))}
                  </div>
                  <Link href={uc.href}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded font-mono text-sm font-bold"
                    style={{ background: uc.color, color: "oklch(0.10 0.01 240)" }}>
                    Open Simulation →
                  </Link>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pipeline reminder */}
      <div className="p-5 rounded" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
        <div className="text-[9px] font-mono tracking-[0.3em] uppercase mb-3 text-muted-foreground">
          Common Pipeline — All Use Cases
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {["World State", "Agent Proposal", "Guard X-108", "Decision", "Cryptographic Proof"].map((step, i) => (
            <span key={step} className="flex items-center gap-2">
              <span className="font-mono text-xs px-2.5 py-1 rounded"
                style={{
                  background: step === "Guard X-108" ? "oklch(0.72 0.18 145 / 0.12)" : "oklch(0.14 0.01 240)",
                  color: step === "Guard X-108" ? "oklch(0.72 0.18 145)" : "oklch(0.65 0.01 240)",
                  border: step === "Guard X-108" ? "1px solid oklch(0.72 0.18 145 / 0.40)" : "1px solid oklch(0.20 0.01 240)",
                  fontWeight: step === "Guard X-108" ? "bold" : "normal",
                }}>
                {step}
              </span>
              {i < 4 && <span style={{ color: "oklch(0.30 0.01 240)" }}>→</span>}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
