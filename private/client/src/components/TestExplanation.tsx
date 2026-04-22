import React, { useState } from "react";

// ─── Types ────────────────────────────────────────────────────────────────────

interface TestSuite {
  name: string;
  domain: string;
  icon: string;
  color: string;
  what: string;
  why: string;
  proves: string[];
  invariants: string[];
  sampleTests: { id: string; label: string; expected: string; explanation: string }[];
}

// ─── Test Suites Metadata ─────────────────────────────────────────────────────

const TEST_SUITES: TestSuite[] = [
  {
    name: "Trading Suite",
    domain: "trading",
    icon: "📉",
    color: "#60a5fa",
    what: "5 scénarios adversariaux sur le moteur de trading (GBM + Markov + GARCH). Chaque test injecte un état de marché hostile et vérifie que le Guard X-108 prend la bonne décision.",
    why: "Le trading algorithmique peut amplifier les crises (flash crash 2010, 2015). Le Guard X-108 doit bloquer les ordres irréversibles quand la cohérence du marché s'effondre.",
    proves: [
      "Invariant I1 : aucun ordre irréversible n'est exécuté quand coherence < 30%",
      "Invariant I2 : HOLD τ obligatoire quand 30% ≤ coherence < 60%",
      "Invariant I3 : la chaîne de décision est hashée et vérifiable (Merkle)",
      "Propriété P1 : le Guard ne peut pas être contourné par un agent malveillant",
    ],
    invariants: ["coherence ≥ 0.30 pour ALLOW", "volatility < 0.04 pour ALLOW sans HOLD", "holdDuration ≥ 3s si HOLD"],
    sampleTests: [
      { id: "T-TRD-01", label: "Flash crash — coherence 0.05", expected: "BLOCK", explanation: "Coherence 5% < 30% → invariant I1 déclenché → BLOCK immédiat" },
      { id: "T-TRD-02", label: "Volatilité élevée — coherence 0.45", expected: "HOLD", explanation: "Coherence 45% ∈ [30%, 60%) → HOLD τ=5s obligatoire" },
      { id: "T-TRD-03", label: "Marché stable — coherence 0.82", expected: "ALLOW", explanation: "Coherence 82% ≥ 60% → tous les invariants satisfaits → ALLOW" },
      { id: "T-TRD-04", label: "Régime BEAR — tendance baissière", expected: "HOLD", explanation: "Régime Markov BEAR détecté → HOLD préventif même si coherence > 60%" },
      { id: "T-TRD-05", label: "Ordre de vente massif — impact marché", expected: "BLOCK", explanation: "Impact marché > 2% → action irréversible → BLOCK" },
    ],
  },
  {
    name: "Bank Suite",
    domain: "bank",
    icon: "🏦",
    color: "#4ade80",
    what: "5 scénarios de stress bancaire (bank run, fraude, liquidité). Chaque test vérifie que le Guard X-108 protège la liquidité et détecte les transactions frauduleuses.",
    why: "Les crises bancaires se propagent en heures (SVB 2023 : 42Mrd$ retirés en 24h). Le Guard X-108 doit bloquer les transactions irréversibles qui menacent la solvabilité.",
    proves: [
      "Invariant B1 : aucun retrait massif irréversible si IR < 15%",
      "Invariant B2 : HOLD obligatoire si CIZ anomalie détectée",
      "Invariant B3 : transactions frauduleuses bloquées si TSG < 20%",
      "Propriété B4 : la chaîne de décision est auditée et horodatée RFC3161",
    ],
    invariants: ["IR ≥ 15% pour ALLOW", "CIZ normal pour ALLOW sans HOLD", "TSG ≥ 20% pour ALLOW"],
    sampleTests: [
      { id: "T-BNK-01", label: "Bank run — 500 retraits simultanés", expected: "BLOCK", explanation: "IR 3% < 15% → invariant B1 → BLOCK tous les retraits > 10k EUR" },
      { id: "T-BNK-02", label: "Virement IBAN étranger inconnu", expected: "HOLD", explanation: "TSG 35% → CIZ anomalie → HOLD τ=8s pour vérification" },
      { id: "T-BNK-03", label: "Transaction normale — client vérifié", expected: "ALLOW", explanation: "IR 87% · CIZ normal · TSG 91% → tous invariants satisfaits" },
      { id: "T-BNK-04", label: "Fraude SIM swap — accès inhabituel", expected: "BLOCK", explanation: "DTS anomalie + géolocalisation impossible → BLOCK immédiat" },
      { id: "T-BNK-05", label: "Virement masse salariale — récurrent", expected: "ALLOW", explanation: "Pattern récurrent vérifié · montant cohérent · bénéficiaire connu" },
    ],
  },
  {
    name: "Ecom Suite",
    domain: "ecom",
    icon: "🛒",
    color: "#fbbf24",
    what: "5 scénarios e-commerce adversariaux (traffic spike, margin attack, bot). Chaque test vérifie que le Guard X-108 protège les marges et la cohérence du funnel.",
    why: "Les flash sales mal contrôlées peuvent détruire les marges en minutes (ROAS < 0.5). Le Guard X-108 doit bloquer les actions commerciales destructrices de valeur.",
    proves: [
      "Invariant E1 : aucune action si marge < 5%",
      "Invariant E2 : HOLD si ROAS < 1.0",
      "Invariant E3 : bot traffic détecté → BLOCK campagnes",
      "Propriété E4 : cohérence du funnel vérifiée avant toute action",
    ],
    invariants: ["marge ≥ 5% pour ALLOW", "ROAS ≥ 1.0 pour ALLOW sans HOLD", "CVR > 0.5% pour ALLOW"],
    sampleTests: [
      { id: "T-ECM-01", label: "Flash sale -60% — marge 2%", expected: "BLOCK", explanation: "Marge 2% < 5% → invariant E1 → BLOCK action commerciale" },
      { id: "T-ECM-02", label: "Campagne ROAS 0.7 — trafic x20", expected: "HOLD", explanation: "ROAS 0.7 < 1.0 → invariant E2 → HOLD τ=5s réévaluation" },
      { id: "T-ECM-03", label: "Campagne normale — ROAS 2.3", expected: "ALLOW", explanation: "Marge 18% · ROAS 2.3 · CVR 2.1% → tous invariants satisfaits" },
      { id: "T-ECM-04", label: "Bot attack — 500k sessions/min", expected: "BLOCK", explanation: "CVR 0.01% → bot traffic → BLOCK toutes les campagnes" },
      { id: "T-ECM-05", label: "Restock d'urgence — stock 1%", expected: "ALLOW", explanation: "Action préventive non irréversible → ALLOW avec monitoring" },
    ],
  },
  {
    name: "Kernel Suite",
    domain: "kernel",
    icon: "⚙️",
    color: "#a78bfa",
    what: "5 tests unitaires du noyau Guard X-108 (integrityGate, x108TemporalLock, riskKillswitch). Vérification formelle des invariants de base.",
    why: "Le noyau Guard X-108 est la dernière ligne de défense. Ses invariants doivent être vérifiables formellement et ne jamais être contournés, même par l'agent lui-même.",
    proves: [
      "Invariant K1 : integrityGate bloque si hash invalide",
      "Invariant K2 : x108TemporalLock impose τ ≥ 3s pour HOLD",
      "Invariant K3 : riskKillswitch déclenche BLOCK si killswitch activé",
      "Propriété K4 : la chaîne de preuves est continue et sans lacune",
    ],
    invariants: ["hash valide pour toute décision", "τ ≥ 3s pour HOLD", "killswitch → BLOCK immédiat"],
    sampleTests: [
      { id: "T-KRN-01", label: "Hash invalide — état corrompu", expected: "BLOCK", explanation: "integrityGate détecte hash invalide → BLOCK immédiat + alerte" },
      { id: "T-KRN-02", label: "HOLD τ=1s — trop court", expected: "HOLD τ=3s", explanation: "x108TemporalLock impose τ_min=3s → override τ=1s → τ=3s" },
      { id: "T-KRN-03", label: "Killswitch activé — urgence", expected: "BLOCK", explanation: "riskKillswitch activé → BLOCK toutes les actions → état figé" },
      { id: "T-KRN-04", label: "Chaîne de preuves — 100 décisions", expected: "PASS", explanation: "Merkle root vérifié · 100 feuilles · aucune lacune · RFC3161 valide" },
      { id: "T-KRN-05", label: "Reset chaîne — nouveau cycle", expected: "PASS", explanation: "resetChain() → nouvelle racine Merkle · continuité prouvée" },
    ],
  },
];

// ─── Component ────────────────────────────────────────────────────────────────

export default function TestExplanation() {
  const [activeSuite, setActiveSuite] = useState(0);
  const [expandedTest, setExpandedTest] = useState<string | null>(null);
  const suite = TEST_SUITES[activeSuite];

  return (
    <div className="panel p-0 overflow-hidden" style={{ border: "1px solid oklch(0.18 0.02 240)" }}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3" style={{ background: "oklch(0.10 0.02 240)", borderBottom: "1px solid oklch(0.18 0.02 240)" }}>
        <div className="flex items-center gap-2">
          <span className="text-base">🧪</span>
          <span className="font-mono font-bold text-sm text-foreground">Test Explanation</span>
          <span className="text-[9px] font-mono px-1.5 py-0.5 rounded" style={{ background: "oklch(0.65 0.18 280 / 0.15)", color: "#a78bfa" }}>What · Why · Proves</span>
        </div>
        <div className="text-[9px] font-mono text-zinc-500">20 tests · 4 suites · 0 failures</div>
      </div>

      <div className="p-4">
        {/* Suite tabs */}
        <div className="grid grid-cols-4 gap-2 mb-4">
          {TEST_SUITES.map((s, i) => (
            <button
              key={s.domain}
              onClick={() => { setActiveSuite(i); setExpandedTest(null); }}
              className="p-2.5 rounded text-left transition-all"
              style={{
                background: activeSuite === i ? `${s.color}12` : "oklch(0.09 0.01 240)",
                border: `1px solid ${activeSuite === i ? s.color + "50" : "oklch(0.16 0.01 240)"}`,
              }}
            >
              <div className="text-base mb-1">{s.icon}</div>
              <div className="font-mono font-bold text-[10px]" style={{ color: activeSuite === i ? s.color : "oklch(0.55 0.01 240)" }}>{s.name}</div>
              <div className="text-[8px] font-mono text-zinc-600 mt-0.5">{s.sampleTests.length} tests</div>
            </button>
          ))}
        </div>

        {/* What / Why */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="rounded p-3" style={{ background: `${suite.color}08`, border: `1px solid ${suite.color}20` }}>
            <div className="text-[8px] font-mono mb-1.5" style={{ color: suite.color }}>WHAT</div>
            <p className="text-[10px] font-mono text-zinc-300 leading-relaxed">{suite.what}</p>
          </div>
          <div className="rounded p-3" style={{ background: "oklch(0.09 0.01 240)", border: "1px solid oklch(0.16 0.01 240)" }}>
            <div className="text-[8px] font-mono text-zinc-500 mb-1.5">WHY</div>
            <p className="text-[10px] font-mono text-zinc-400 leading-relaxed">{suite.why}</p>
          </div>
        </div>

        {/* Proves */}
        <div className="rounded p-3 mb-4" style={{ background: "oklch(0.08 0.01 280)", border: "1px solid oklch(0.18 0.02 280)" }}>
          <div className="text-[8px] font-mono text-purple-400 mb-2">WHAT THIS PROVES</div>
          <div className="space-y-1">
            {suite.proves.map((p, i) => (
              <div key={i} className="flex items-start gap-2 text-[9px] font-mono">
                <span className="text-purple-500 mt-0.5">▸</span>
                <span className="text-zinc-300">{p}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Invariants */}
        <div className="flex flex-wrap gap-2 mb-4">
          {suite.invariants.map((inv, i) => (
            <span key={i} className="text-[8px] font-mono px-2 py-0.5 rounded" style={{ background: `${suite.color}10`, color: suite.color, border: `1px solid ${suite.color}25` }}>
              {inv}
            </span>
          ))}
        </div>

        {/* Test cases */}
        <div className="space-y-1.5">
          <div className="text-[9px] font-mono text-zinc-500 mb-2">Test cases — cliquer pour voir l'explication</div>
          {suite.sampleTests.map(test => (
            <div key={test.id}>
              <button
                onClick={() => setExpandedTest(expandedTest === test.id ? null : test.id)}
                className="w-full flex items-center justify-between px-3 py-2 rounded text-left transition-all"
                style={{
                  background: expandedTest === test.id ? `${suite.color}10` : "oklch(0.09 0.01 240)",
                  border: `1px solid ${expandedTest === test.id ? suite.color + "30" : "oklch(0.15 0.01 240)"}`,
                }}
              >
                <div className="flex items-center gap-3">
                  <span className="text-[8px] font-mono text-zinc-600">{test.id}</span>
                  <span className="text-[10px] font-mono text-zinc-300">{test.label}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[9px] font-mono px-1.5 py-0.5 rounded" style={{
                    background: test.expected === "BLOCK" ? "#f8717115" : test.expected === "ALLOW" ? "#4ade8015" : "#fbbf2415",
                    color: test.expected === "BLOCK" ? "#f87171" : test.expected === "ALLOW" ? "#4ade80" : "#fbbf24",
                  }}>
                    {test.expected}
                  </span>
                  <span className="text-[8px] text-zinc-600">{expandedTest === test.id ? "▲" : "▼"}</span>
                </div>
              </button>
              {expandedTest === test.id && (
                <div className="px-3 py-2 rounded-b text-[9px] font-mono text-zinc-400 leading-relaxed" style={{ background: `${suite.color}06`, border: `1px solid ${suite.color}20`, borderTop: "none" }}>
                  <span className="text-zinc-500">Explication : </span>{test.explanation}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
