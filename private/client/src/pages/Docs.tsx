import { Link } from "wouter";

const DOC_SECTIONS = [
  {
    icon: "🚀",
    title: "Quick Start",
    color: "oklch(0.72 0.18 145)",
    items: [
      { label: "What is Obsidia?", desc: "Overview of the governance kernel and its purpose", href: "/what-is-obsidia" },
      { label: "How it Works", desc: "Step-by-step walkthrough of the decision pipeline", href: "/how-it-works" },
      { label: "30-Second Demo", desc: "Watch a Flash Crash scenario from start to proof", href: "/" },
    ],
  },
  {
    icon: "🏗",
    title: "Architecture",
    color: "oklch(0.60 0.12 200)",
    items: [
      { label: "System Architecture", desc: "OS0 → OS4 stack, layer responsibilities, data flow", href: "/technology" },
      { label: "Guard X-108", desc: "Safety gate specification: coherence, invariants, temporal lock", href: "/governance" },
      { label: "Decision Lifecycle", desc: "From intent to proof — every step explained", href: "/decision-lifecycle" },
    ],
  },
  {
    icon: "🧪",
    title: "Simulations",
    color: "oklch(0.65 0.18 240)",
    items: [
      { label: "Trading Simulation", desc: "Flash crash, pump & dump, algo war scenarios", href: "/use-cases/trading" },
      { label: "Banking Safety", desc: "Bank run, CBDC crisis, fraud wave scenarios", href: "/use-cases/banking" },
      { label: "E-commerce Automation", desc: "Bot traffic, viral demand, supply crisis scenarios", href: "/use-cases/ecommerce" },
      { label: "Scenario Engine", desc: "Run and compare all scenarios with metrics", href: "/scenario-engine" },
    ],
  },
  {
    icon: "📐",
    title: "Formal Proofs",
    color: "oklch(0.72 0.18 145)",
    items: [
      { label: "Lean 4 Theorems", desc: "33 formally proven safety invariants", href: "/proof" },
      { label: "TLA+ Specification", desc: "Temporal logic model of the decision pipeline", href: "/proof" },
      { label: "Merkle Anchoring", desc: "Cryptographic audit trail construction", href: "/proof" },
      { label: "Bank Adversarial Tests", desc: "20 adversarial scenarios with formal guarantees", href: "/proof" },
    ],
  },
  {
    icon: "⚙️",
    title: "Expert Tools",
    color: "oklch(0.55 0.01 240)",
    items: [
      { label: "Control Tower", desc: "Multi-agent surveillance dashboard", href: "/control" },
      { label: "Decision Stream", desc: "Live governance reactor — all worlds", href: "/stream" },
      { label: "Engine Dashboard", desc: "Kernel metrics, coherence, decision rate", href: "/engine" },
      { label: "Stress Lab", desc: "25 adversarial scenarios with stress testing", href: "/stress" },
      { label: "Mirror Mode", desc: "Parallel agent comparison and divergence analysis", href: "/mirror" },
      { label: "Audit Mode", desc: "Institutional audit trail and export", href: "/audit" },
    ],
  },
];

export default function Docs() {
  return (
    <div className="flex flex-col gap-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="pt-6 pb-2">
        <div className="text-[9px] font-mono tracking-[0.3em] uppercase mb-2" style={{ color: "oklch(0.65 0.18 240)" }}>
          Documentation
        </div>
        <h1 className="font-mono font-bold text-3xl text-foreground mb-3">
          Obsidia OS4 — Technical Documentation
        </h1>
        <p className="font-mono text-sm text-muted-foreground max-w-2xl leading-relaxed">
          Complete reference for the Obsidia governance platform. Start with Quick Start if you are new,
          or jump directly to the section you need.
        </p>
      </div>

      {/* Search hint */}
      <div className="p-4 rounded flex items-center gap-3"
        style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
        <span className="text-muted-foreground font-mono text-sm">🔍</span>
        <span className="font-mono text-sm text-muted-foreground">
          Use the navigation menu to access any section directly. Expert tools are available via the{" "}
          <span style={{ color: "oklch(0.60 0.12 200)" }}>⚙ EXPERT</span> toggle in the top-right corner.
        </span>
      </div>

      {/* Doc sections */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {DOC_SECTIONS.map(section => (
          <div key={section.title} className="p-5 rounded flex flex-col gap-4"
            style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
            <div className="flex items-center gap-3">
              <span className="text-2xl">{section.icon}</span>
              <h2 className="font-mono font-bold text-base" style={{ color: section.color }}>{section.title}</h2>
            </div>
            <div className="flex flex-col gap-2">
              {section.items.map(item => (
                <Link key={item.label} href={item.href}
                  className="flex flex-col gap-0.5 p-2.5 rounded transition-colors cursor-pointer"
                  style={{ background: "oklch(0.09 0.01 240)", border: "1px solid oklch(0.15 0.01 240)" }}>
                  <div className="font-mono text-xs font-bold" style={{ color: "oklch(0.80 0.01 240)" }}>
                    {item.label} →
                  </div>
                  <div className="text-[10px] text-muted-foreground">{item.desc}</div>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* GitHub link */}
      <div className="p-5 rounded flex items-center justify-between"
        style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
        <div>
          <div className="font-mono text-sm font-bold text-foreground mb-1">Source Code</div>
          <div className="text-[10px] text-muted-foreground">
            Lean 4 proofs, TLA+ specifications, and full platform source on GitHub.
          </div>
        </div>
        <a href="https://github.com/Eaubin08/Obsidia-lab-trad" target="_blank" rel="noopener noreferrer"
          className="px-5 py-2.5 rounded font-mono text-sm font-bold border flex-shrink-0"
          style={{ background: "transparent", color: "oklch(0.65 0.01 240)", borderColor: "oklch(0.25 0.01 240)" }}>
          GitHub →
        </a>
      </div>
    </div>
  );
}
