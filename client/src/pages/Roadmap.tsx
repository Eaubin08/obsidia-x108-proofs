import { Link } from "wouter";

// ─── Data ─────────────────────────────────────────────────────────────────────

const REPO = "https://github.com/Eaubin08/Obsidia-lab-trad";

interface Phase {
  number: number;
  title: string;
  description: string;
  status: "completed" | "current" | "upcoming";
  highlights?: string[];
  link?: string;
}

const PHASES: Phase[] = [
  {
    number: 1,
    title: "Core Guard Engine",
    description: "Implémentation du moteur de garde X-108 — évaluation de cohérence structurelle, décision ALLOW/HOLD/BLOCK.",
    status: "completed",
    highlights: ["Cohérence structurelle", "Décision ternaire", "Latence < 15ms"],
    link: `${REPO}/tree/main/core`,
  },
  {
    number: 3,
    title: "Merkle Integrity",
    description: "Chaîne de hachage Merkle sur toutes les décisions. Toute modification d'une décision passée est détectable.",
    status: "completed",
    highlights: ["Merkle tree SHA-256", "711 fichiers suivis", "Seal V18.3.1"],
    link: `${REPO}/tree/main/lean/Obsidia/Merkle.lean`,
  },
  {
    number: 5,
    title: "Temporal Gate X-108",
    description: "Verrou temporel de 10 secondes sur les actions irréversibles. Aucune exécution prématurée possible.",
    status: "completed",
    highlights: ["Fenêtre τ = 10s", "Prouvé en Lean 4", "Invariant TLA+"],
    link: `${REPO}/tree/main/lean/Obsidia/TemporalX108.lean`,
  },
  {
    number: 9,
    title: "Distributed Consensus",
    description: "Consensus PBFT distribué sur 4 nœuds (Paris, London, Frankfurt, Amsterdam). Tolérance aux fautes byzantines f=1.",
    status: "completed",
    highlights: ["PBFT 3/4", "4 nœuds géographiques", "Latence < 20ms"],
    link: `${REPO}/tree/main/tla/DistributedX108.tla`,
  },
  {
    number: 11,
    title: "RFC 3161 Anchoring",
    description: "Ancrage cryptographique des décisions via horodatage RFC 3161 (FreeTSA) et Bitcoin OTS. Preuve légalement opposable.",
    status: "completed",
    highlights: ["RFC 3161 · FreeTSA", "Bitcoin OTS Block #876,234", "SHA-256"],
    link: `${REPO}/blob/main/rfc3161_anchor.json`,
  },
  {
    number: 14,
    title: "Deterministic Reproducibility",
    description: "Reproductibilité déterministe complète : même seed, même résultat. Audit et replay possibles sur n'importe quelle décision passée.",
    status: "completed",
    highlights: ["Seed-based replay", "State hash verification", "Prouvé formellement"],
    link: `${REPO}/tree/main/lean/Obsidia/Basic.lean`,
  },
  {
    number: 18,
    title: "Bank Adversarial Suite",
    description: "Suite de 473 tests adversariaux : flash crash, bank run, fraude, injection de bruit. 0 violation détectée.",
    status: "completed",
    highlights: ["473 tests PASS", "Flash crash 8000 steps", "0 violation"],
    link: `${REPO}/tree/main/bank-proof`,
  },
  {
    number: 20,
    title: "Temporal X-108 Refinement",
    description: "Raffinement du protocole X-108 : ajustement dynamique de τ selon la volatilité du marché, multi-domaine (trading/bank/ecom).",
    status: "completed",
    highlights: ["τ adaptatif", "3 domaines", "Cohérence multi-agent"],
    link: `${REPO}/tree/main/tla/X108.tla`,
  },
  {
    number: 24,
    title: "TLA+ Formal Specifications",
    description: "Spécifications TLA+ complètes : 7 invariants vérifiés sur toutes les traces d'exécution. TypeOK, Safety, GateCorrectness, DistributedSafety.",
    status: "completed",
    highlights: ["7 invariants", "TypeOK + Safety", "DistributedSafety"],
    link: `${REPO}/tree/main/tla`,
  },
  {
    number: 28,
    title: "X108 STD v1.0 — Current",
    description: "Version stable du moteur Obsidia X-108. Démonstrateur complet : moteur visible, preuves formelles, tests adversariaux, gouvernance temporelle, audit exportable.",
    status: "current",
    highlights: ["33 théorèmes Lean 4", "473 tests PASS", "Export Proof Package"],
    link: REPO,
  },
  {
    number: 32,
    title: "Multi-Agent Coordination",
    description: "Coordination entre agents spécialisés (trading, bank, ecom) avec consensus inter-domaine et propagation des décisions.",
    status: "upcoming",
    highlights: ["Consensus inter-domaine", "Agent mesh", "Propagation décisions"],
  },
  {
    number: 36,
    title: "On-Chain Anchoring",
    description: "Ancrage des décisions directement sur la blockchain Ethereum via smart contract. Auditabilité publique et immuable.",
    status: "upcoming",
    highlights: ["Smart contract Solidity", "Ethereum mainnet", "Preuve publique"],
  },
];

// ─── Component ────────────────────────────────────────────────────────────────

export default function Roadmap() {
  const completedCount = PHASES.filter(p => p.status === "completed").length;
  const currentPhase = PHASES.find(p => p.status === "current");

  return (
    <div className="flex flex-col max-w-4xl mx-auto px-4 pb-16" style={{ gap: "48px" }}>

      {/* ─── Header ─────────────────────────────────────────────────────────── */}
      <div className="pt-8">
        <div className="text-[10px] font-mono tracking-[0.3em] uppercase mb-1" style={{ color: "oklch(0.72 0.18 145)" }}>
          Obsidia Labs — OS4
        </div>
        <h1 className="font-mono font-bold text-2xl text-foreground mb-2">
          Roadmap
        </h1>
        <p className="text-sm" style={{ color: "oklch(0.55 0.01 240)", maxWidth: "560px" }}>
          L'évolution du moteur Obsidia X-108 depuis les premiers prototypes jusqu'à la version stable actuelle.
          Chaque phase correspond à un aspect fondamental du système.
        </p>

        {/* Current status banner */}
        <div
          className="mt-6 inline-flex items-center gap-3 px-4 py-2 rounded-lg"
          style={{ background: "oklch(0.72 0.18 145 / 0.10)", border: "1px solid oklch(0.72 0.18 145 / 0.30)" }}
        >
          <div className="w-2 h-2 rounded-full" style={{ background: "oklch(0.72 0.18 145)" }} />
          <span className="font-mono text-xs font-bold" style={{ color: "oklch(0.72 0.18 145)" }}>
            Phase actuelle : {currentPhase?.title ?? "X108 STD v1.0"}
          </span>
          <span className="font-mono text-[9px]" style={{ color: "oklch(0.45 0.01 240)" }}>
            {completedCount} phases complétées
          </span>
        </div>
      </div>

      {/* ─── Timeline ───────────────────────────────────────────────────────── */}
      <section>
        <h2 className="font-mono font-bold text-sm uppercase tracking-widest mb-8" style={{ color: "oklch(0.72 0.18 145)" }}>
          Development Timeline
        </h2>

        <div className="relative">
          {/* Vertical line */}
          <div
            className="absolute left-[19px] top-0 bottom-0 w-px"
            style={{ background: "oklch(0.22 0.01 240)" }}
          />

          <div className="flex flex-col" style={{ gap: "0" }}>
            {PHASES.map((phase, idx) => {
              const isCompleted = phase.status === "completed";
              const isCurrent = phase.status === "current";
              const isUpcoming = phase.status === "upcoming";

              const dotColor = isCurrent
                ? "oklch(0.72 0.18 145)"
                : isCompleted
                  ? "oklch(0.60 0.12 200)"
                  : "oklch(0.30 0.01 240)";

              const borderColor = isCurrent
                ? "oklch(0.72 0.18 145 / 0.5)"
                : isCompleted
                  ? "oklch(0.60 0.12 200 / 0.25)"
                  : "oklch(0.20 0.01 240)";

              const bgColor = isCurrent
                ? "oklch(0.72 0.18 145 / 0.07)"
                : isCompleted
                  ? "oklch(0.10 0.01 240)"
                  : "oklch(0.08 0.01 240)";

              return (
                <div key={phase.number} className="flex items-start gap-6" style={{ paddingBottom: idx < PHASES.length - 1 ? "32px" : "0" }}>
                  {/* Dot */}
                  <div className="relative flex-shrink-0 flex items-center justify-center" style={{ width: "40px", paddingTop: "20px" }}>
                    <div
                      className="w-4 h-4 rounded-full z-10 flex items-center justify-center"
                      style={{ background: dotColor, boxShadow: isCurrent ? `0 0 12px ${dotColor}` : "none" }}
                    >
                      {isCompleted && (
                        <svg width="8" height="8" viewBox="0 0 8 8" fill="none">
                          <path d="M1.5 4L3 5.5L6.5 2" stroke="white" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      )}
                      {isCurrent && (
                        <div className="w-2 h-2 rounded-full" style={{ background: "white" }} />
                      )}
                    </div>
                  </div>

                  {/* Card */}
                  <div
                    className="flex-1 rounded-lg"
                    style={{
                      padding: "20px 24px",
                      background: bgColor,
                      border: `1px solid ${borderColor}`,
                      opacity: isUpcoming ? 0.6 : 1,
                    }}
                  >
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span
                            className="font-mono text-[9px] font-bold px-1.5 py-0.5 rounded"
                            style={{
                              background: isCurrent ? "oklch(0.72 0.18 145 / 0.20)" : isCompleted ? "oklch(0.60 0.12 200 / 0.15)" : "oklch(0.18 0.01 240)",
                              color: isCurrent ? "oklch(0.72 0.18 145)" : isCompleted ? "oklch(0.60 0.12 200)" : "oklch(0.40 0.01 240)",
                            }}
                          >
                            Phase {phase.number}
                          </span>
                          {isCurrent && (
                            <span className="font-mono text-[9px] font-bold px-1.5 py-0.5 rounded" style={{ background: "oklch(0.72 0.18 145 / 0.15)", color: "oklch(0.72 0.18 145)" }}>
                              ● CURRENT
                            </span>
                          )}
                          {isUpcoming && (
                            <span className="font-mono text-[9px] px-1.5 py-0.5 rounded" style={{ background: "oklch(0.16 0.01 240)", color: "oklch(0.40 0.01 240)" }}>
                              UPCOMING
                            </span>
                          )}
                        </div>
                        <h3 className="font-mono font-bold text-sm text-foreground">{phase.title}</h3>
                      </div>
                      {phase.link && (
                        <a
                          href={phase.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-mono text-[9px] flex-shrink-0"
                          style={{ color: "oklch(0.45 0.01 240)" }}
                        >
                          GitHub ↗
                        </a>
                      )}
                    </div>

                    <p className="text-[11px] mb-3" style={{ color: "oklch(0.50 0.01 240)" }}>
                      {phase.description}
                    </p>

                    {phase.highlights && (
                      <div className="flex flex-wrap gap-2">
                        {phase.highlights.map(h => (
                          <span
                            key={h}
                            className="font-mono text-[9px] px-2 py-0.5 rounded"
                            style={{
                              background: "oklch(0.14 0.01 240)",
                              color: "oklch(0.45 0.01 240)",
                              border: "1px solid oklch(0.20 0.01 240)",
                            }}
                          >
                            {h}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ─── Links ──────────────────────────────────────────────────────────── */}
      <section>
        <h2 className="font-mono font-bold text-sm uppercase tracking-widest mb-4" style={{ color: "oklch(0.72 0.18 145)" }}>
          Explorer le projet
        </h2>
        <div className="grid grid-cols-2 gap-4">
          {[
            { label: "Repository GitHub", desc: "Code source complet", href: REPO, icon: "⬡" },
            { label: "Proof Center", desc: "Preuves formelles + tests", href: "/proof-center", icon: "📐", internal: true },
            { label: "Control Tower", desc: "Supervision live", href: "/control-tower", icon: "🗼", internal: true },
            { label: "Evidence", desc: "Traces Strasbourg Clock", href: "/evidence", icon: "⛓️", internal: true },
          ].map(item => (
            item.internal ? (
              <Link key={item.label} href={item.href}>
                <div
                  className="rounded-lg cursor-pointer"
                  style={{ padding: "16px 20px", background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span>{item.icon}</span>
                    <span className="font-mono font-bold text-xs text-foreground">{item.label}</span>
                  </div>
                  <p className="text-[10px]" style={{ color: "oklch(0.45 0.01 240)" }}>{item.desc}</p>
                </div>
              </Link>
            ) : (
              <a key={item.label} href={item.href} target="_blank" rel="noopener noreferrer" style={{ textDecoration: "none" }}>
                <div
                  className="rounded-lg"
                  style={{ padding: "16px 20px", background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span>{item.icon}</span>
                    <span className="font-mono font-bold text-xs text-foreground">{item.label}</span>
                  </div>
                  <p className="text-[10px]" style={{ color: "oklch(0.45 0.01 240)" }}>{item.desc}</p>
                </div>
              </a>
            )
          ))}
        </div>
      </section>

    </div>
  );
}
