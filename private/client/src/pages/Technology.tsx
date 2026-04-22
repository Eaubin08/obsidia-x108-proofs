import { Link } from "wouter";

const PIPELINE = [
  { id: "WORLD", label: "World State", desc: "Market data, transactions, user actions, environmental signals", color: "oklch(0.65 0.18 240)" },
  { id: "AGENT", label: "Agent", desc: "Perception, strategy generation, action proposal with intent metadata", color: "oklch(0.65 0.18 240)" },
  { id: "INTENT", label: "Intent", desc: "Structured action request: type, parameters, reversibility flag, risk estimate", color: "oklch(0.60 0.12 200)" },
  { id: "X-108", label: "Guard X-108", desc: "Coherence check · Invariant validation · Temporal lock τ=10s · Risk scoring", color: "oklch(0.72 0.18 145)", highlight: true },
  { id: "DECISION", label: "Decision", desc: "BLOCK / HOLD / ALLOW — with cryptographic signature and reason code", color: "oklch(0.72 0.18 145)" },
];

const TECH_SECTIONS = [
  {
    id: "architecture",
    icon: "🏗",
    title: "Architecture",
    color: "oklch(0.65 0.18 240)",
    content: [
      { label: "OS0 — Invariants / IR", desc: "Contract validation, hash invariants, formal specification layer" },
      { label: "OS1 — Registry / Agents", desc: "Agent registry, world adapters, capability declarations" },
      { label: "OS2 — Runtime Engine", desc: "Decision pipeline, strategy generation, coherence computation" },
      { label: "X-108 — Safety Gate", desc: "Temporal safety gate, BLOCK/HOLD/ALLOW with τ=10s lock", highlight: true },
      { label: "OS3 — Audit / Proof", desc: "Hash logs, Merkle tree construction, replay verifier" },
      { label: "OS4 — Interface / Worlds", desc: "TradingWorld, BankWorld, EcomWorld — simulation environments" },
    ],
  },
  {
    id: "guard",
    icon: "🛡",
    title: "Guard X-108",
    color: "oklch(0.72 0.18 145)",
    content: [
      { label: "Coherence threshold", desc: "Actions are blocked when coherence score < 0.30 (configurable per domain)" },
      { label: "Temporal lock τ=10s", desc: "Irreversible actions wait 10 seconds for coherence recomputation" },
      { label: "Invariant validation", desc: "Every action is checked against formal invariants defined in Lean 4" },
      { label: "Risk scoring", desc: "Multi-factor risk model: volatility, liquidity, counterparty, regulatory" },
      { label: "Deterministic output", desc: "Same seed + same state → same decision, every time. Fully reproducible." },
    ],
  },
  {
    id: "engine",
    icon: "⚙️",
    title: "Deterministic Engine",
    color: "oklch(0.60 0.12 200)",
    content: [
      { label: "Seeded PRNG", desc: "All randomness is seeded — simulations are fully reproducible from any checkpoint" },
      { label: "State machine", desc: "Each world is a deterministic state machine with explicit transition rules" },
      { label: "Coherence computation", desc: "Coherence is computed from volatility, trend consistency, and agent history" },
      { label: "Hash chain", desc: "Every state transition is hashed and chained — tamper detection is automatic" },
      { label: "Replay verification", desc: "Any decision can be replayed from its seed to verify the output independently" },
    ],
  },
  {
    id: "consensus",
    icon: "🔗",
    title: "Distributed Consensus",
    color: "oklch(0.65 0.01 240)",
    content: [
      { label: "Multi-agent agreement", desc: "When multiple agents propose conflicting actions, consensus protocol resolves conflicts" },
      { label: "Merkle anchoring", desc: "Decision trees are anchored in a Merkle structure for tamper-proof audit" },
      { label: "RFC3161 timestamps", desc: "Cryptographic timestamps anchor decisions to an external time authority" },
      { label: "Proof of non-action", desc: "BLOCK decisions are also recorded — the absence of action is provable" },
    ],
  },
];

export default function Technology() {
  return (
    <div className="flex flex-col gap-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="pt-6 pb-2">
        <div className="text-[9px] font-mono tracking-[0.3em] uppercase mb-2" style={{ color: "oklch(0.60 0.12 200)" }}>
          Technology
        </div>
        <h1 className="font-mono font-bold text-3xl text-foreground mb-3">
          How the engine works
        </h1>
        <p className="font-mono text-sm text-muted-foreground max-w-2xl leading-relaxed">
          Obsidia is built on a deterministic, formally verified decision engine.
          Every component is designed to be auditable, reproducible, and provably safe.
        </p>
      </div>

      {/* Intent pipeline */}
      <div className="p-6 rounded" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
        <div className="text-[9px] font-mono tracking-[0.3em] uppercase mb-5 text-muted-foreground">
          Intent Pipeline
        </div>
        <div className="flex flex-col gap-0 max-w-lg">
          {PIPELINE.map((step, i) => (
            <div key={step.id} className="flex items-start gap-0">
              <div className="flex flex-col items-center mr-4">
                <div className="w-10 h-10 rounded-full flex items-center justify-center font-mono text-xs font-bold flex-shrink-0"
                  style={{
                    background: step.highlight ? "oklch(0.72 0.18 145 / 0.15)" : "oklch(0.14 0.01 240)",
                    border: `2px solid ${step.highlight ? "oklch(0.72 0.18 145 / 0.60)" : "oklch(0.22 0.01 240)"}`,
                    color: step.color,
                  }}>
                  {step.id.slice(0, 2)}
                </div>
                {i < PIPELINE.length - 1 && (
                  <div className="w-0.5 h-6" style={{ background: "oklch(0.20 0.01 240)" }} />
                )}
              </div>
              <div className="flex-1 pb-4 pt-1.5">
                <div className="font-mono text-sm font-bold mb-0.5" style={{ color: step.color }}>{step.label}</div>
                <div className="text-[10px] text-muted-foreground leading-relaxed">{step.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tech sections */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {TECH_SECTIONS.map(section => (
          <div key={section.id} className="p-5 rounded flex flex-col gap-4"
            style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
            <div className="flex items-center gap-3">
              <span className="text-2xl">{section.icon}</span>
              <h2 className="font-mono font-bold text-base" style={{ color: section.color }}>{section.title}</h2>
            </div>
            <div className="flex flex-col gap-2.5">
              {section.content.map(item => (
                <div key={item.label} className="flex flex-col gap-0.5">
                  <div className="font-mono text-xs font-bold"
                    style={{ color: (item as { highlight?: boolean }).highlight ? "oklch(0.72 0.18 145)" : "oklch(0.75 0.01 240)" }}>
                    {item.label}
                  </div>
                  <div className="text-[10px] text-muted-foreground leading-relaxed">{item.desc}</div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Links */}
      <div className="flex gap-3 flex-wrap pb-4">
        <Link href="/proof" className="px-5 py-2.5 rounded font-mono text-sm font-bold"
          style={{ background: "oklch(0.72 0.18 145)", color: "oklch(0.10 0.01 240)" }}>
          View formal proofs →
        </Link>
        <Link href="/engine" className="px-5 py-2.5 rounded font-mono text-sm font-bold border"
          style={{ background: "transparent", color: "oklch(0.60 0.12 200)", borderColor: "oklch(0.60 0.12 200 / 0.50)" }}>
          Live Engine Dashboard →
        </Link>
        <a href="https://github.com/Eaubin08/Obsidia-lab-trad" target="_blank" rel="noopener noreferrer"
          className="px-5 py-2.5 rounded font-mono text-sm font-bold border"
          style={{ background: "transparent", color: "oklch(0.55 0.01 240)", borderColor: "oklch(0.25 0.01 240)" }}>
          Source code →
        </a>
      </div>
    </div>
  );
}
