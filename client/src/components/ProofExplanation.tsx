import React, { useState } from "react";

// ─── Proof Modules Metadata ───────────────────────────────────────────────────

const PROOF_MODULES = [
  {
    id: "lean4",
    name: "Lean 4 — Théorèmes Formels",
    icon: "∀",
    color: "#a78bfa",
    what: "33 théorèmes formellement prouvés en Lean 4 sur le comportement du Guard X-108. Chaque théorème est une preuve mathématique vérifiable par un assistant de preuve indépendant.",
    why: "Les preuves formelles sont la seule garantie absolue qu'un système ne peut pas violer ses invariants. Contrairement aux tests (qui ne peuvent pas couvrir tous les cas), une preuve formelle couvre l'espace infini des états possibles.",
    proves: [
      "Théorème 1 : BLOCK est irréversible — une fois décidé, il ne peut pas être annulé",
      "Théorème 2 : HOLD respecte τ_min — la durée minimale est toujours respectée",
      "Théorème 3 : Cohérence monotone — la cohérence ne peut pas augmenter pendant un crash",
      "Théorème 4 : Déterminisme — même seed + même état → même décision (toujours)",
      "Théorème 5 : Sécurité absolue — aucune action irréversible ne passe si coherence < 30%",
    ],
    techDetails: "Lean 4 · 8 modules · 33 théorèmes · vérifiés par lake build · tag x108-std-v1.0",
    files: ["lean/Obsidia/GuardX108.lean", "lean/Obsidia/Invariants.lean", "lean/Obsidia/TemporalLock.lean"],
  },
  {
    id: "tla",
    name: "TLA+ — Invariants Temporels",
    icon: "□",
    color: "#60a5fa",
    what: "7 invariants temporels spécifiés en TLA+ (Temporal Logic of Actions). TLA+ permet de vérifier des propriétés sur des séquences infinies d'états, couvrant tous les comportements possibles du système.",
    why: "Les systèmes distribués et les agents autonomes ont des comportements temporels complexes (deadlocks, livelocks, starvation). TLA+ prouve que ces comportements indésirables ne peuvent pas se produire.",
    proves: [
      "Invariant TLA-1 : Safety — le Guard ne peut jamais autoriser une action irréversible dans un état incohérent",
      "Invariant TLA-2 : Liveness — chaque HOLD se termine en temps fini (pas de deadlock)",
      "Invariant TLA-3 : Fairness — chaque agent reçoit une décision en temps borné",
      "Invariant TLA-4 : Non-interference — deux agents ne peuvent pas interférer sur la même décision",
      "Invariant TLA-5 : Auditabilité — chaque décision est tracée et non-répudiable",
    ],
    techDetails: "TLA+ · 7 modules · vérifiés par TLC model checker · 10^6 états explorés",
    files: ["tla/GuardX108.tla", "tla/TemporalLock.tla", "tla/InvariantChecker.tla"],
  },
  {
    id: "merkle",
    name: "Merkle Tree — Intégrité des Preuves",
    icon: "⬡",
    color: "#4ade80",
    what: "Chaque décision du Guard X-108 est hashée et insérée dans un arbre de Merkle. La racine de l'arbre est publiée et vérifiable indépendamment. Toute modification d'une décision passée invalide la racine.",
    why: "Un système de gouvernance doit être auditable. Le Merkle tree garantit que l'historique des décisions est tamper-evident — impossible à modifier sans être détecté. C'est la même technologie que Bitcoin et Ethereum.",
    proves: [
      "Propriété M1 : Tamper-evidence — toute modification d'une décision passée est détectée",
      "Propriété M2 : Completeness — aucune décision ne peut être supprimée de l'historique",
      "Propriété M3 : Vérifiabilité — n'importe qui peut vérifier l'intégrité sans accès complet",
      "Propriété M4 : Continuité — la chaîne de preuves est sans lacune depuis la genèse",
    ],
    techDetails: "SHA-256 · arbre binaire · racine publiée · vérifiable en O(log n)",
    files: ["core/engine/merkle.ts", "evidence/os4/merkle_root.json", "evidence/os4/strasbourg_clock/"],
  },
  {
    id: "rfc3161",
    name: "RFC 3161 — Horodatage Légal",
    icon: "⏱",
    color: "#fbbf24",
    what: "Chaque racine Merkle est horodatée par une autorité de confiance (RFC 3161 — Internet X.509 PKI Timestamp Protocol). L'horodatage prouve que les preuves existaient à un instant précis, avant tout litige.",
    why: "Dans un contexte légal ou réglementaire (MiCA, DORA, PSD2), il faut pouvoir prouver que le système était conforme à un instant donné. L'horodatage RFC 3161 est reconnu légalement dans l'UE (eIDAS).",
    proves: [
      "Propriété R1 : Antériorité — les preuves existaient avant la date d'horodatage",
      "Propriété R2 : Non-répudiation — l'horodatage est signé par une TSA (Time Stamping Authority)",
      "Propriété R3 : Conformité eIDAS — valeur légale dans l'Union Européenne",
      "Propriété R4 : Chaîne de confiance — vérifiable jusqu'à la racine de confiance de l'UE",
    ],
    techDetails: "RFC 3161 · TSA DigiCert · SHA-256 · valeur légale eIDAS · Strasbourg Clock",
    files: ["evidence/os4/strasbourg_clock/rfc3161_anchor.json", "evidence/os4/strasbourg_clock/proof_bundle.json"],
  },
];

// ─── Component ────────────────────────────────────────────────────────────────

export default function ProofExplanation() {
  const [activeModule, setActiveModule] = useState(0);
  const [expandedProof, setExpandedProof] = useState<number | null>(null);
  const mod = PROOF_MODULES[activeModule];

  return (
    <div className="panel p-0 overflow-hidden" style={{ border: "1px solid oklch(0.18 0.02 280)" }}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3" style={{ background: "oklch(0.10 0.02 280)", borderBottom: "1px solid oklch(0.18 0.02 280)" }}>
        <div className="flex items-center gap-2">
          <span className="text-base">🔬</span>
          <span className="font-mono font-bold text-sm text-foreground">Proof Explanation</span>
          <span className="text-[9px] font-mono px-1.5 py-0.5 rounded" style={{ background: "oklch(0.65 0.18 280 / 0.15)", color: "#a78bfa" }}>What · Why · Proves</span>
        </div>
        <div className="text-[9px] font-mono text-zinc-500">33 théorèmes · 7 invariants · Merkle · RFC3161</div>
      </div>

      <div className="p-4">
        {/* Module tabs */}
        <div className="grid grid-cols-4 gap-2 mb-4">
          {PROOF_MODULES.map((m, i) => (
            <button
              key={m.id}
              onClick={() => { setActiveModule(i); setExpandedProof(null); }}
              className="p-2.5 rounded text-left transition-all"
              style={{
                background: activeModule === i ? `${m.color}12` : "oklch(0.09 0.01 240)",
                border: `1px solid ${activeModule === i ? m.color + "50" : "oklch(0.16 0.01 240)"}`,
              }}
            >
              <div className="font-mono text-xl mb-1" style={{ color: activeModule === i ? m.color : "oklch(0.40 0.01 240)" }}>{m.icon}</div>
              <div className="font-mono font-bold text-[9px]" style={{ color: activeModule === i ? m.color : "oklch(0.55 0.01 240)" }}>{m.id.toUpperCase()}</div>
            </button>
          ))}
        </div>

        {/* Module name */}
        <div className="font-mono font-bold text-sm mb-3" style={{ color: mod.color }}>{mod.name}</div>

        {/* What / Why */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="rounded p-3" style={{ background: `${mod.color}08`, border: `1px solid ${mod.color}20` }}>
            <div className="text-[8px] font-mono mb-1.5" style={{ color: mod.color }}>WHAT</div>
            <p className="text-[10px] font-mono text-zinc-300 leading-relaxed">{mod.what}</p>
          </div>
          <div className="rounded p-3" style={{ background: "oklch(0.09 0.01 240)", border: "1px solid oklch(0.16 0.01 240)" }}>
            <div className="text-[8px] font-mono text-zinc-500 mb-1.5">WHY</div>
            <p className="text-[10px] font-mono text-zinc-400 leading-relaxed">{mod.why}</p>
          </div>
        </div>

        {/* What this proves */}
        <div className="rounded p-3 mb-4" style={{ background: "oklch(0.08 0.01 280)", border: "1px solid oklch(0.18 0.02 280)" }}>
          <div className="text-[8px] font-mono text-purple-400 mb-2">WHAT THIS PROVES</div>
          <div className="space-y-1.5">
            {mod.proves.map((p, i) => (
              <button
                key={i}
                onClick={() => setExpandedProof(expandedProof === i ? null : i)}
                className="w-full flex items-start gap-2 text-left"
              >
                <span className="text-purple-500 mt-0.5 flex-shrink-0 text-[9px]">▸</span>
                <span className="text-[9px] font-mono" style={{ color: expandedProof === i ? mod.color : "oklch(0.65 0.01 240)" }}>{p}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Tech details */}
        <div className="flex items-center justify-between">
          <div className="text-[8px] font-mono text-zinc-600">{mod.techDetails}</div>
          <div className="flex gap-2">
            {mod.files.map((f, i) => (
              <span key={i} className="text-[7px] font-mono px-1.5 py-0.5 rounded" style={{ background: `${mod.color}10`, color: mod.color, border: `1px solid ${mod.color}20` }}>
                {f.split("/").pop()}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
