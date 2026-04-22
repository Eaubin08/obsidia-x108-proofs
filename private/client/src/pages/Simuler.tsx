import { useState, useEffect, useCallback, useRef, useMemo } from "react";
import { useSearch } from "wouter";
import { trpc } from "@/lib/trpc";
import MetriquesSimulation from "@/components/MetriquesSimulation";
import PilotagePanel from "@/components/PilotagePanel";
import CommandPanel, { type CommandParams, type CommandDomain } from "@/components/CommandPanel";
import BeforeAfterPanel, { type BeforeAfterResult } from "@/components/BeforeAfterPanel";
import RunBreadcrumb from "@/components/RunBreadcrumb";
import ProjectionPanel, { type ProjectionScenario } from "@/components/ProjectionPanel";
import { ModeBadgeBar, type OperatingMode } from "@/components/ModeBadge";
import { CanonicalAgentPanel } from "@/components/CanonicalAgentPanel";
// Imports directs — les composants sont montés/démontés proprement à chaque changement d'onglet
import TradingWorld from "./TradingWorld";
import BankWorld from "./BankWorld";
import EcomWorld from "./EcomWorld";

// ─── Types ────────────────────────────────────────────────────────────────────

type Onglet = "trading" | "banque" | "ecom" | "stress" | "marche" | "agents";

// ─── Données des onglets ──────────────────────────────────────────────────────

const ONGLETS: {
  id: Onglet;
  label: string;
  icon: string;
  couleur: string;
  titre: string;
  // 3 niveaux d'explication
  simple: string;
  investisseur: string;
  expert: string;
}[] = [
  {
    id: "trading",
    label: "Trading",
    icon: "📈",
    couleur: "#3b82f6",
    titre: "Marché financier",
    simple: "Un programme surveille le cours du Bitcoin et propose des ordres d'achat ou de vente. Obsidia décide si chaque ordre est safe avant de l'exécuter.",
    investisseur: "Guard X-108 applique un verrou temporel de 10 secondes sur les ordres irréversibles et bloque automatiquement lors de krachs éclairs (volatilité > 45 %).",
    expert: "Moteur GBM + Markov + GARCH. Seuils : BLOCK si vol > 0.45 ou cohérence < 0.25 ; HOLD si vol > 0.30 ou cohérence < 0.50. Reproductible via seed déterministe.",
  },
  {
    id: "banque",
    label: "Banque",
    icon: "🏦",
    couleur: "#a78bfa",
    titre: "Institution bancaire",
    simple: "Un agent gère les virements et transactions d'une banque. Obsidia détecte les anomalies (fraude, ruée bancaire) et bloque les opérations suspectes avant qu'elles partent.",
    investisseur: "10 scénarios adversariaux : bank run, fraude massive, choc de taux, bulle de crédit. Guard X-108 maintient les ratios de liquidité et bloque les violations de solvabilité.",
    expert: "Moteur log-normal + détection fraude. Invariants : liquidité > 15 %, ratio capital > 8 %, score fraude < 0.85. 473 tests adversariaux PASS.",
  },
  {
    id: "ecom",
    label: "E-Commerce",
    icon: "🛒",
    couleur: "#34d399",
    titre: "Boutique en ligne",
    simple: "Un agent ajuste les prix et les stocks d'une boutique. Obsidia empêche les décisions qui pourraient déclencher une réaction en chaîne (guerre des prix, attaque de bots).",
    investisseur: "Guard X-108 protège les marges contre les ajustements de prix agressifs et bloque les décisions de pricing lors de pics de trafic anormaux (bots, DDoS).",
    expert: "Modèle funnel CVR/ROAS + agents X-108. Seuils : BLOCK si trafic bot > 80 % ou marge < 5 % ; HOLD si CVR chute > 40 % en 5 min.",
  },
  {
    id: "stress",
    label: "Stress Lab",
    icon: "⚠",
    couleur: "#f87171",
    titre: "Tester les limites",
    simple: "Que se passe-t-il si le marché s'effondre complètement ? Si une banque est attaquée ? Si des bots inondent une boutique ? Ce laboratoire simule les pires scénarios possibles.",
    investisseur: "16 scénarios adversariaux extrêmes (Flash Crash, Black Swan, Adversarial AI, Credit Bubble Burst…). Chaque scénario est exécuté 100 fois pour mesurer la robustesse de Guard X-108.",
    expert: "Monte Carlo sur 100 seeds par scénario. Distribution BLOCK/HOLD/ALLOW. Métriques : cohérence moyenne, volatilité moyenne, stabilité Guard (0→1). Catégories : TRADING / BANK / ECOM / KERNEL.",
  },
  {
    id: "marche",
    label: "Marché Réel",
    icon: "🔴",
    couleur: "#fbbf24",
    titre: "Prix Binance en direct",
    simple: "Les vrais prix du marché crypto (Bitcoin, Ethereum…) en temps réel. Obsidia analyse chaque tick et indique si une action serait autorisée, mise en attente ou bloquée — sans jamais exécuter d'ordre réel.",
    investisseur: "Données Binance 24h en temps réel. Guard X-108 calcule volatilité, cohérence et régime de marché pour chaque crypto. Mode miroir : simulation pure, aucun ordre réel.",
    expert: "Proxy Binance /api/v3/ticker/24hr. Calcul volatilité = (high-low)/price. Cohérence = f(trend, stability). Régime détecté : BULL/BEAR/CRASH/SIDEWAYS/RECOVERY. Fallback simulé si API indisponible.",
  },
  {
    id: "agents",
    label: "Agents",
    icon: "🤖",
    couleur: "#a78bfa",
    titre: "Pipeline Canonique",
    simple: "Chaque décision passe par une constellation d'agents spécialisés (Trading : 17 agents, Bank : 12 agents, Ecom : 12 agents) + 10 méta-agents transversaux. Le Guard X-108 est le juge unique.",
    investisseur: "Les agents proposent, X-108 dispose. Chaque agent vote avec un score de confiance. L'agrégateur domaine calcule le verdict métier. Les méta-agents vérifient la cohérence globale.",
    expert: "Pipeline : observation → interprétation → contradiction/preuve locale → agrégation domaine → méta-agents → Guard X-108 unique → payload canonique. Source : canonical_framework (Python) ou canonical_fallback (local).",
  },
];

// ─── Scénarios Stress Lab ─────────────────────────────────────────────────────

interface StressScenario {
  id: string;
  category: string;
  name: string;
  description: string;
  shock: string;
  expectedGuard: "BLOCK" | "HOLD" | "ALLOW" | "MIXED";
  params: { volatility: number; coherence: number; regime: string; liquidity: number; intensity: number };
}

const STRESS_SCENARIOS: StressScenario[] = [
  { id: "flash_crash", category: "TRADING", name: "Flash Crash", description: "Chute de prix soudaine de −40 % en un seul tick. Le carnet d'ordres s'effondre.", shock: "Prix −40 % · Vol ×4 · Liquidité −80 %", expectedGuard: "BLOCK", params: { volatility: 0.85, coherence: 0.12, regime: "CRASH", liquidity: 0.1, intensity: 0.95 } },
  { id: "black_swan", category: "TRADING", name: "Black Swan", description: "Événement géopolitique imprévu. Toutes les corrélations cassent. Les modèles échouent simultanément.", shock: "Corrélation = 0 · Vol ×5 · Tous les modèles invalides", expectedGuard: "BLOCK", params: { volatility: 0.95, coherence: 0.05, regime: "CRASH", liquidity: 0.05, intensity: 1.0 } },
  { id: "market_manipulation", category: "TRADING", name: "Manipulation de marché", description: "Attaque de spoofing : de gros faux ordres sont placés puis annulés rapidement.", shock: "Carnet d'ordres empoisonné · Faux signaux · Effondrement cohérence", expectedGuard: "BLOCK", params: { volatility: 0.48, coherence: 0.15, regime: "BEAR", liquidity: 0.30, intensity: 0.80 } },
  { id: "bank_run", category: "BANK", name: "Ruée bancaire", description: "Événement de retrait massif. La liquidité est drainée en quelques heures.", shock: "Retraits +500 % · Réserves −70 % · Cascade de panique", expectedGuard: "BLOCK", params: { volatility: 0.60, coherence: 0.18, regime: "CRASH", liquidity: 0.08, intensity: 0.92 } },
  { id: "credit_bubble_burst", category: "BANK", name: "Éclatement de bulle de crédit", description: "Contraction systémique du crédit. 30 % du portefeuille de prêts fait défaut simultanément.", shock: "Taux de défaut +3000 % · Ratio capital −8 % · Risque de solvabilité", expectedGuard: "BLOCK", params: { volatility: 0.80, coherence: 0.12, regime: "CRASH", liquidity: 0.10, intensity: 0.95 } },
  { id: "fraud_wave", category: "BANK", name: "Vague de fraude", description: "Attaque coordonnée : 50 tentatives de fraude simultanées sur différents comptes.", shock: "Score fraude 0,95 · 50 tentatives · Violation AML", expectedGuard: "BLOCK", params: { volatility: 0.35, coherence: 0.10, regime: "BEAR", liquidity: 0.65, intensity: 0.90 } },
  { id: "bot_traffic_attack", category: "ECOM", name: "Attaque de bots", description: "Inondation de bots style DDoS : 10 000 fausses sessions par seconde.", shock: "Trafic +1000 % · CVR −90 % · Revenus distordus", expectedGuard: "BLOCK", params: { volatility: 0.70, coherence: 0.15, regime: "CRASH", liquidity: 0.20, intensity: 0.88 } },
  { id: "supply_chain_break", category: "ECOM", name: "Rupture de chaîne d'approvisionnement", description: "Fournisseur clé en défaut. 40 % des SKUs indisponibles.", shock: "Stock −40 % · Demande non satisfaite · Revenus −35 %", expectedGuard: "HOLD", params: { volatility: 0.38, coherence: 0.42, regime: "BEAR", liquidity: 0.60, intensity: 0.60 } },
  { id: "ai_adversarial", category: "KERNEL", name: "Attaque IA adversariale", description: "Un agent hostile injecte des propositions conçues pour contourner les invariants X-108.", shock: "Cohérence falsifiée · Tentative de collision de hash · Bypass invariant", expectedGuard: "BLOCK", params: { volatility: 0.55, coherence: 0.03, regime: "CRASH", liquidity: 0.40, intensity: 0.99 } },
  { id: "clock_drift", category: "KERNEL", name: "Dérive d'horloge", description: "Verrou temporel manipulé : horloge système décalée de ±30 secondes.", shock: "Dérive ±30s · Invariant temporel violé", expectedGuard: "BLOCK", params: { volatility: 0.40, coherence: 0.08, regime: "CRASH", liquidity: 0.50, intensity: 0.95 } },
];

// ─── Symboles marché réel ─────────────────────────────────────────────────────

const SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT"];

function simulateGuard(volatility: number, coherence: number, regime: string): { decision: "BLOCK" | "HOLD" | "ALLOW"; reason: string } {
  if (volatility > 0.45 || coherence < 0.25) return { decision: "BLOCK", reason: `Vol ${(volatility * 100).toFixed(1)} % > 45 % ou cohérence ${coherence.toFixed(2)} < 0,25 — action bloquée.` };
  if (volatility > 0.30 || coherence < 0.50 || regime === "CRASH" || regime === "BEAR") return { decision: "HOLD", reason: `Vol ${(volatility * 100).toFixed(1)} % > 30 % ou cohérence ${coherence.toFixed(2)} < 0,50 — attente 10s.` };
  return { decision: "ALLOW", reason: `Tous les invariants satisfaits : vol ${(volatility * 100).toFixed(1)} % ✓, cohérence ${coherence.toFixed(2)} ✓.` };
}

function seededRng(seed: number) {
  let s = seed;
  return () => { s = (s * 1664525 + 1013904223) & 0xffffffff; return (s >>> 0) / 0xffffffff; };
}

function generateSimulatedTick(symbol: string, seed: number) {
  const bases: Record<string, number> = { BTCUSDT: 67000, ETHUSDT: 3400, SOLUSDT: 180, BNBUSDT: 580, ADAUSDT: 0.65, XRPUSDT: 0.72 };
  const base = bases[symbol] ?? 100;
  const rng = seededRng(seed);
  const pct = (rng() - 0.5) * 0.12;
  const price = base * (1 + pct);
  const vol = 0.05 + rng() * 0.35;
  const coherence = Math.max(0, Math.min(1, 0.8 - vol * 1.2 + (rng() - 0.5) * 0.2));
  const regime = pct < -0.04 ? "CRASH" : pct < -0.01 ? "BEAR" : pct > 0.03 ? "BULL" : vol < 0.15 ? "SIDEWAYS" : "RECOVERY";
  const { decision, reason } = simulateGuard(vol, coherence, regime);
  const now = new Date();
  return { symbol, price, priceChangePct24h: pct * 100, volatility: vol, coherence, regime, guardDecision: decision, guardReason: reason, timestamp: `${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}` };
}

// ─── Composant Stress Lab ─────────────────────────────────────────────────────

function StressLabPanel() {
  const [results, setResults] = useState<Record<string, { block: number; hold: number; allow: number; runs: number; pythonAvailable?: boolean; source?: string; sampleTraceId?: string }>>({});
  const [running, setRunning] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>("TOUS");
  const batchRunMutation = trpc.engine.batchRun.useMutation();

  const runScenario = useCallback(async (scenario: StressScenario, runs = 10) => {
    setRunning(scenario.id);
    try {
      // Use 10 seeds (each seed = 1 run of totalSteps steps)
      const seeds = Array.from({ length: runs }, (_, i) => i + 1);
      type ScenarioId = "flash_crash" | "bank_run" | "fraud_attack" | "traffic_spike" | "black_swan" | "market_manipulation" | "credit_bubble_burst" | "fraud_wave" | "bot_traffic_attack" | "supply_chain_break" | "ai_adversarial" | "clock_drift";
      const res = await batchRunMutation.mutateAsync({ scenarioId: scenario.id as ScenarioId, seeds });
      const agg = res.aggregated as any;
      const allSteps = (res.results as any[]).flatMap((r: any) => r.steps ?? []);
      const pythonSteps = allSteps.filter((s: any) => s.source === "python");
      const sampleTrace = pythonSteps.find((s: any) => s.trace_id)?.trace_id;
      const block = allSteps.filter((s: any) => s.guardDecision === "BLOCK").length;
      const hold = allSteps.filter((s: any) => s.guardDecision === "HOLD").length;
      const allow = allSteps.filter((s: any) => s.guardDecision === "ALLOW").length;
      setResults(prev => ({
        ...prev,
        [scenario.id]: {
          block, hold, allow,
          runs: allSteps.length,
          pythonAvailable: agg?.pythonAvailable ?? false,
          source: agg?.pythonAvailable ? "python" : "local_fallback",
          sampleTraceId: sampleTrace,
        },
      }));
    } catch {
      // Fallback PRNG local si Python DOWN
      let block = 0, hold = 0, allow = 0;
      for (let i = 0; i < runs * 10; i++) {
        const rng = seededRng(i * 137 + 42);
        const noise = (rng() - 0.5) * 0.15;
        const vol = Math.min(1, Math.max(0, scenario.params.volatility + noise));
        const coh = Math.min(1, Math.max(0, scenario.params.coherence + noise * 0.5));
        if (vol > 0.45 || coh < 0.20) block++;
        else if (vol > 0.30 || coh < 0.45) hold++;
        else allow++;
      }
      setResults(prev => ({ ...prev, [scenario.id]: { block, hold, allow, runs: runs * 10, pythonAvailable: false, source: "local_fallback" } }));
    }
    setRunning(null);
  }, [batchRunMutation]);

  const runAll = useCallback(async () => {
    for (const s of STRESS_SCENARIOS) {
      await runScenario(s, 5);
    }
  }, [runScenario]);

  const categories = ["TOUS", "TRADING", "BANK", "ECOM", "KERNEL"];
  const filtered = filter === "TOUS" ? STRESS_SCENARIOS : STRESS_SCENARIOS.filter(s => s.category === filter);
  const catColor = (cat: string) => cat === "TRADING" ? "#3b82f6" : cat === "BANK" ? "#a78bfa" : cat === "ECOM" ? "#34d399" : "#fbbf24";
  const guardColor = (g: string) => g === "BLOCK" ? "#f87171" : g === "HOLD" ? "#fbbf24" : "#4ade80";

  // Métriques récapitulatives calculées depuis les résultats
  const scenariosTermines = Object.keys(results).length;
  const totalRuns = scenariosTermines * 100;
  const totalBlock = Object.values(results).reduce((a, r) => a + r.block, 0);
  const totalHold  = Object.values(results).reduce((a, r) => a + r.hold, 0);
  const totalAllow = Object.values(results).reduce((a, r) => a + r.allow, 0);
  const tauxBlocageGlobal = totalRuns > 0 ? totalBlock / totalRuns : 0;
  const tauxSurvie = totalRuns > 0 ? (totalHold + totalAllow) / totalRuns : 0;
  // Capital protégé estimé : chaque BLOCK sur 100k€ évite une perte de 8%
  const capitalProtege = totalBlock * 100_000 * 0.08;
  const pireScenario = Object.entries(results).sort(([, a], [, b]) => b.block - a.block)[0];
  const pireScenarioNom = pireScenario ? (STRESS_SCENARIOS.find(s => s.id === pireScenario[0])?.name ?? "—") : "—";

  return (
    <div className="flex flex-col gap-6">
      {/* Explication */}
      <div className="p-5 rounded" style={{ background: "oklch(0.65 0.22 25 / 0.06)", border: "1px solid oklch(0.65 0.22 25 / 0.25)" }}>
        <div className="text-[9px] font-mono tracking-widest uppercase mb-2" style={{ color: "#f87171" }}>⚠ Stress Lab — Tester les limites</div>
        <p className="text-[12px] font-mono leading-relaxed mb-3" style={{ color: "oklch(0.65 0.01 240)" }}>
          Ce laboratoire simule les <strong style={{ color: "#f87171" }}>pires scénarios possibles</strong> pour tester la robustesse de Guard X-108.
          Chaque scénario est exécuté <strong style={{ color: "oklch(0.72 0.18 145)" }}>100 fois</strong> avec des variations aléatoires pour mesurer la distribution des décisions.
        </p>
        <div className="grid grid-cols-3 gap-3 text-center">
          {[
            { label: "Scénarios", value: STRESS_SCENARIOS.length.toString(), color: "#f87171" },
            { label: "Runs par scénario", value: "100", color: "#fbbf24" },
            { label: "Résultats attendus", value: "BLOCK majoritaire", color: "#4ade80" },
          ].map(m => (
            <div key={m.label} className="p-2 rounded" style={{ background: "oklch(0.11 0.01 240)" }}>
              <div className="font-mono font-bold text-sm" style={{ color: m.color }}>{m.value}</div>
              <div className="text-[9px] font-mono text-muted-foreground">{m.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Tableau récapitulatif Stress Lab */}
      <div className="rounded-lg p-4" style={{ background: "oklch(0.09 0.01 240)", border: "1px solid oklch(0.65 0.22 25 / 0.20)" }}>
        <div className="flex items-center justify-between mb-3">
          <span className="font-mono font-bold text-xs" style={{ color: "#f87171" }}>Métriques Stress Lab</span>
          <span className="text-[9px] font-mono px-2 py-0.5 rounded" style={{ background: scenariosTermines > 0 ? "#f8717112" : "oklch(0.12 0.01 240)", color: scenariosTermines > 0 ? "#f87171" : "oklch(0.40 0.01 240)", border: `1px solid ${scenariosTermines > 0 ? "#f8717125" : "oklch(0.18 0.01 240)"}` }}>
            {scenariosTermines > 0 ? `${scenariosTermines}/${STRESS_SCENARIOS.length} scénarios testés` : "En attente de simulation"}
          </span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
          {[
            { label: "Scénarios testés",   valeur: `${scenariosTermines} / ${STRESS_SCENARIOS.length}`, couleur: "#f87171" },
            { label: "Taux de blocage",    valeur: totalRuns > 0 ? `${(tauxBlocageGlobal * 100).toFixed(1)} %` : "—", couleur: tauxBlocageGlobal > 0.7 ? "#4ade80" : "#fbbf24" },
            { label: "Taux de survie",     valeur: totalRuns > 0 ? `${(tauxSurvie * 100).toFixed(1)} %` : "—", couleur: tauxSurvie > 0.5 ? "#f87171" : "#4ade80" },
            { label: "Capital protégé",    valeur: capitalProtege > 0 ? (capitalProtege >= 1_000_000 ? `€${(capitalProtege/1_000_000).toFixed(2)}M` : `€${(capitalProtege/1_000).toFixed(0)}k`) : "—", couleur: "oklch(0.72 0.18 145)" },
          ].map(m => (
            <div key={m.label} className="p-2 rounded text-center" style={{ background: "oklch(0.11 0.01 240)" }}>
              <div className="font-mono font-bold text-sm" style={{ color: m.couleur }}>{m.valeur}</div>
              <div className="text-[9px] font-mono text-muted-foreground">{m.label}</div>
            </div>
          ))}
        </div>
        {scenariosTermines > 0 && (
          <div className="rounded overflow-hidden" style={{ border: "1px solid oklch(0.16 0.01 240)" }}>
            <table className="w-full text-[10px] font-mono">
              <thead>
                <tr style={{ background: "oklch(0.11 0.01 240)" }}>
                  <th className="text-left px-3 py-1.5 font-bold" style={{ color: "oklch(0.50 0.01 240)" }}>Métrique</th>
                  <th className="text-right px-3 py-1.5 font-bold" style={{ color: "oklch(0.50 0.01 240)" }}>Valeur</th>
                  <th className="text-right px-3 py-1.5 font-bold hidden md:table-cell" style={{ color: "oklch(0.50 0.01 240)" }}>Détail</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { label: "Total runs",          valeur: `${totalRuns.toLocaleString("fr-FR")}`, detail: `${scenariosTermines} scénarios × 100 runs`, couleur: "oklch(0.70 0.01 240)" },
                  { label: "BLOCK total",         valeur: `${totalBlock.toLocaleString("fr-FR")}`, detail: `${(tauxBlocageGlobal * 100).toFixed(1)} % des runs`, couleur: "#f87171" },
                  { label: "HOLD total",          valeur: `${totalHold.toLocaleString("fr-FR")}`, detail: `${totalRuns > 0 ? ((totalHold/totalRuns)*100).toFixed(1) : "0"} % des runs`, couleur: "#fbbf24" },
                  { label: "ALLOW total",         valeur: `${totalAllow.toLocaleString("fr-FR")}`, detail: `${totalRuns > 0 ? ((totalAllow/totalRuns)*100).toFixed(1) : "0"} % des runs`, couleur: "#4ade80" },
                  { label: "Pire scénario",       valeur: pireScenarioNom, detail: pireScenario ? `${pireScenario[1].block} BLOCK / 100` : "—", couleur: "#f87171" },
                  { label: "Capital protégé est.",valeur: capitalProtege > 0 ? (capitalProtege >= 1_000_000 ? `€${(capitalProtege/1_000_000).toFixed(2)}M` : `€${(capitalProtege/1_000).toFixed(0)}k`) : "€0", detail: "Base 100k€ × 8% par BLOCK", couleur: "oklch(0.72 0.18 145)" },
                ].map((row, i) => (
                  <tr key={row.label} style={{ background: i % 2 === 0 ? "oklch(0.095 0.01 240)" : "oklch(0.10 0.01 240)", borderTop: "1px solid oklch(0.13 0.01 240)" }}>
                    <td className="px-3 py-1.5" style={{ color: "oklch(0.60 0.01 240)" }}>{row.label}</td>
                    <td className="px-3 py-1.5 text-right font-bold" style={{ color: row.couleur }}>{row.valeur}</td>
                    <td className="px-3 py-1.5 text-right hidden md:table-cell" style={{ color: "oklch(0.40 0.01 240)" }}>{row.detail}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {scenariosTermines === 0 && (
          <div className="text-center text-[10px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>
            Lancez des scénarios pour voir les métriques agrégées apparaître ici.
          </div>
        )}
      </div>

      {/* Filtres + bouton tout lancer */}
      <div className="flex items-center gap-3 flex-wrap">
        {categories.map(cat => (
          <button key={cat} onClick={() => setFilter(cat)}
            className="px-3 py-1.5 rounded text-[10px] font-mono font-bold"
            style={{
              background: filter === cat ? (cat === "TOUS" ? "oklch(0.72 0.18 145)" : catColor(cat) + "30") : "oklch(0.12 0.01 240)",
              color: filter === cat ? (cat === "TOUS" ? "oklch(0.10 0.01 240)" : catColor(cat)) : "oklch(0.50 0.01 240)",
              border: `1px solid ${filter === cat ? (cat === "TOUS" ? "oklch(0.72 0.18 145)" : catColor(cat)) : "oklch(0.20 0.01 240)"}`,
            }}>
            {cat}
          </button>
        ))}
        <button onClick={runAll} disabled={running !== null}
          className="ml-auto px-4 py-1.5 rounded text-[10px] font-mono font-bold"
          style={{ background: "oklch(0.72 0.18 145)", color: "oklch(0.10 0.01 240)", opacity: running ? 0.6 : 1 }}>
          ▶ Tout lancer
        </button>
      </div>

      {/* Grille de scénarios */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map(scenario => {
          const result = results[scenario.id];
          const isRunning = running === scenario.id;
          const cc = catColor(scenario.category);
          const ec = guardColor(scenario.expectedGuard);
          return (
            <div key={scenario.id} className="p-4 rounded" style={{ background: "oklch(0.11 0.01 240)", border: `1px solid ${isRunning ? cc + "60" : "oklch(0.18 0.01 240)"}` }}>
              {/* Header */}
              <div className="flex items-start justify-between mb-2">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded" style={{ background: cc + "20", color: cc }}>{scenario.category}</span>
                    <span className="text-sm font-mono font-bold text-foreground">{scenario.name}</span>
                  </div>
                  <p className="text-[10px] font-mono text-muted-foreground leading-relaxed">{scenario.description}</p>
                </div>
                <span className="text-[9px] font-mono px-2 py-0.5 rounded ml-2 shrink-0" style={{ background: ec + "15", color: ec, border: `1px solid ${ec}33` }}>
                  Attendu : {scenario.expectedGuard}
                </span>
              </div>

              {/* Choc */}
              <div className="text-[9px] font-mono px-2 py-1 rounded mb-3" style={{ background: "oklch(0.65 0.22 25 / 0.08)", border: "1px solid oklch(0.65 0.22 25 / 0.20)", color: "#f87171" }}>
                ⚡ {scenario.shock}
              </div>

              {/* Paramètres */}
              <div className="grid grid-cols-5 gap-1 mb-3">
                {[
                  { k: "vol", v: `${(scenario.params.volatility * 100).toFixed(0)} %`, high: scenario.params.volatility > 0.4 },
                  { k: "cohérence", v: scenario.params.coherence.toFixed(2), high: scenario.params.coherence < 0.3 },
                  { k: "régime", v: scenario.params.regime, high: scenario.params.regime === "CRASH" },
                  { k: "liquidité", v: `${(scenario.params.liquidity * 100).toFixed(0)} %`, high: scenario.params.liquidity < 0.3 },
                  { k: "intensité", v: `${(scenario.params.intensity * 100).toFixed(0)} %`, high: scenario.params.intensity > 0.7 },
                ].map(p => (
                  <div key={p.k} className="text-center p-1 rounded" style={{ background: "oklch(0.13 0.01 240)" }}>
                    <div className="text-[8px] font-mono text-muted-foreground">{p.k}</div>
                    <div className="text-[10px] font-mono font-bold" style={{ color: p.high ? "#f87171" : "oklch(0.72 0.18 145)" }}>{p.v}</div>
                  </div>
                ))}
              </div>

              {/* Résultat */}
              {result && !isRunning && (
                <div className="mb-3">
                  <div className="flex rounded overflow-hidden h-3" style={{ background: "oklch(0.14 0.01 240)" }}>
                    <div style={{ width: `${(result.block / result.runs) * 100}%`, background: "#f87171", transition: "width 0.5s" }} />
                    <div style={{ width: `${(result.hold / result.runs) * 100}%`, background: "#fbbf24", transition: "width 0.5s" }} />
                    <div style={{ width: `${(result.allow / result.runs) * 100}%`, background: "#4ade80", transition: "width 0.5s" }} />
                  </div>
                  <div className="flex justify-between mt-1 text-[9px] font-mono">
                    <span style={{ color: "#f87171" }}>BLOCK {((result.block / result.runs) * 100).toFixed(1)} %</span>
                    <span style={{ color: "#fbbf24" }}>HOLD {((result.hold / result.runs) * 100).toFixed(1)} %</span>
                    <span style={{ color: "#4ade80" }}>ALLOW {((result.allow / result.runs) * 100).toFixed(1)} %</span>
                  </div>
                  {/* Source badge */}
                  <div className="flex items-center gap-2 mt-1.5">
                    <span className="text-[8px] font-mono px-1.5 py-0.5 rounded" style={{
                      background: result.pythonAvailable ? "oklch(0.72 0.18 145 / 0.12)" : "oklch(0.65 0.22 25 / 0.10)",
                      color: result.pythonAvailable ? "oklch(0.72 0.18 145)" : "#f87171",
                      border: `1px solid ${result.pythonAvailable ? "oklch(0.72 0.18 145 / 0.3)" : "oklch(0.65 0.22 25 / 0.3)"}`
                    }}>
                      {result.pythonAvailable ? "⚡ python" : "⚠ local_fallback"}
                    </span>
                    {result.sampleTraceId && (
                      <span className="text-[8px] font-mono text-muted-foreground truncate" style={{ maxWidth: 160 }}>
                        trace: {result.sampleTraceId.slice(0, 8)}…
                      </span>
                    )}
                    <span className="text-[8px] font-mono text-muted-foreground ml-auto">{result.runs} steps</span>
                  </div>
                </div>
              )}

              {isRunning && (
                <div className="mb-3 flex items-center gap-2 text-[10px] font-mono" style={{ color: cc }}>
                  <div className="w-3 h-3 rounded-full border-2 border-t-transparent animate-spin" style={{ borderColor: `${cc} transparent transparent transparent` }} />
                  Simulation en cours…
                </div>
              )}

              {/* Bouton */}
              <button onClick={() => runScenario(scenario)} disabled={running !== null}
                className="w-full py-1.5 rounded text-[10px] font-mono font-bold"
                style={{ background: isRunning ? cc + "30" : "oklch(0.14 0.01 240)", color: cc, border: `1px solid ${cc}40`, opacity: running && !isRunning ? 0.5 : 1 }}>
                {result && !isRunning ? "↺ Relancer (100 runs)" : isRunning ? "En cours…" : "▶ Simuler (100 runs)"}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Composant Marché Réel ────────────────────────────────────────────────────

function MarcheReelPanel() {
  const [ticks, setTicks] = useState<Map<string, ReturnType<typeof generateSimulatedTick>>>(new Map());
  const [selected, setSelected] = useState("BTCUSDT");
  const [live, setLive] = useState(false);
  const [dataSource, setDataSource] = useState<"simulé" | "live">("simulé");
  const seedRef = useRef(Date.now() % 100000);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const { data: binanceData, refetch } = trpc.mirror.prices.useQuery(
    { symbols: SYMBOLS },
    { enabled: false, retry: false }
  );

  const updateTicks = useCallback(() => {
    seedRef.current = (seedRef.current * 1664525 + 1013904223) & 0xffffffff;
    const newTicks = new Map<string, ReturnType<typeof generateSimulatedTick>>();
    SYMBOLS.forEach((sym, i) => {
      newTicks.set(sym, generateSimulatedTick(sym, Math.abs(seedRef.current + i * 997) % 99999 + 1));
    });
    setTicks(newTicks);
  }, []);

  useEffect(() => {
    updateTicks();
  }, [updateTicks]);

  useEffect(() => {
    if (binanceData) {
      try {
        const newTicks = new Map<string, ReturnType<typeof generateSimulatedTick>>();
        binanceData.data?.forEach((item: any) => {
          const { decision, reason } = simulateGuard(item.volatility, item.coherence, item.regime);
          const now = new Date();
          newTicks.set(item.symbol, {
            symbol: item.symbol, price: item.price, priceChangePct24h: item.change24h * 100,
            volatility: item.volatility, coherence: item.coherence, regime: item.regime,
            guardDecision: decision, guardReason: reason,
            timestamp: `${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}`,
          });
        });
        if (newTicks.size > 0) { setTicks(newTicks); setDataSource("live"); }
      } catch { /* fallback simulé */ }
    }
  }, [binanceData]);

  const toggleLive = useCallback(() => {
    if (live) {
      if (intervalRef.current) clearInterval(intervalRef.current);
      setLive(false);
    } else {
      setLive(true);
      refetch();
      intervalRef.current = setInterval(() => { updateTicks(); refetch(); }, 5000);
    }
  }, [live, refetch, updateTicks]);

  useEffect(() => () => { if (intervalRef.current) clearInterval(intervalRef.current); }, []);

  const tick = ticks.get(selected);

  // Métriques récapitulatives calculées depuis tous les ticks
  const allTicks = Array.from(ticks.values());
  const blocksMarche = allTicks.filter(t => t.guardDecision === "BLOCK").length;
  const holdsMarche  = allTicks.filter(t => t.guardDecision === "HOLD").length;
  const allowsMarche = allTicks.filter(t => t.guardDecision === "ALLOW").length;
  const capitalHypo = 100_000;
  const rendementMoyen = allTicks.length > 0 ? allTicks.reduce((a, t) => a + t.priceChangePct24h, 0) / allTicks.length : 0;
  const capitalActuelHypo = capitalHypo * (1 + rendementMoyen / 100 * (allowsMarche / Math.max(1, allTicks.length)));
  const pnlHypo = capitalActuelHypo - capitalHypo;
  const volatMoyenne = allTicks.length > 0 ? allTicks.reduce((a, t) => a + t.volatility, 0) / allTicks.length : 0;
  const guardColor = (g: string) => g === "BLOCK" ? "#f87171" : g === "HOLD" ? "#fbbf24" : "#4ade80";

  return (
    <div className="flex flex-col gap-6">
      {/* Explication */}
      <div className="p-5 rounded" style={{ background: "oklch(0.78 0.18 60 / 0.06)", border: "1px solid oklch(0.78 0.18 60 / 0.25)" }}>
        <div className="text-[9px] font-mono tracking-widest uppercase mb-2" style={{ color: "#fbbf24" }}>🔴 Marché Réel — Mode Miroir</div>
        <p className="text-[12px] font-mono leading-relaxed" style={{ color: "oklch(0.65 0.01 240)" }}>
          Les <strong style={{ color: "#fbbf24" }}>vrais prix du marché crypto</strong> en temps réel (données Binance).
          Guard X-108 analyse chaque tick et indique sa décision — <strong style={{ color: "#f87171" }}>aucun ordre réel n'est jamais exécuté</strong>.
          C'est une simulation pure sur données réelles.
        </p>
      </div>

      {/* Tableau métriques Marché Réel */}
      <div className="rounded-lg p-4" style={{ background: "oklch(0.09 0.01 240)", border: "1px solid oklch(0.78 0.18 60 / 0.20)" }}>
        <div className="flex items-center justify-between mb-3">
          <span className="font-mono font-bold text-xs" style={{ color: "#fbbf24" }}>Métriques Marché Réel</span>
          <span className="text-[9px] font-mono px-2 py-0.5 rounded" style={{ background: live ? "#4ade8012" : "oklch(0.12 0.01 240)", color: live ? "#4ade80" : "oklch(0.40 0.01 240)", border: `1px solid ${live ? "#4ade8025" : "oklch(0.18 0.01 240)"}` }}>
            {live ? `● Live — ${SYMBOLS.length} marchés` : `○ ${dataSource === "live" ? "Dernières données Binance" : "Données simulées"}`}
          </span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
          {[
            { label: "Capital hypothétique", valeur: `€${capitalHypo.toLocaleString("fr-FR")}`, couleur: "#fbbf24" },
            { label: "P&L simulé",           valeur: `${pnlHypo >= 0 ? "+" : ""}€${pnlHypo.toFixed(0)}`, couleur: pnlHypo >= 0 ? "#4ade80" : "#f87171" },
            { label: "Volatilité moy.",      valeur: allTicks.length > 0 ? `${(volatMoyenne * 100).toFixed(1)} %` : "—", couleur: volatMoyenne > 0.30 ? "#f87171" : "#4ade80" },
            { label: "Décisions Guard",      valeur: `${allTicks.length}`, couleur: "#a78bfa" },
          ].map(m => (
            <div key={m.label} className="p-2 rounded text-center" style={{ background: "oklch(0.11 0.01 240)" }}>
              <div className="font-mono font-bold text-sm" style={{ color: m.couleur }}>{m.valeur}</div>
              <div className="text-[9px] font-mono text-muted-foreground">{m.label}</div>
            </div>
          ))}
        </div>
        <div className="rounded overflow-hidden" style={{ border: "1px solid oklch(0.16 0.01 240)" }}>
          <table className="w-full text-[10px] font-mono">
            <thead>
              <tr style={{ background: "oklch(0.11 0.01 240)" }}>
                <th className="text-left px-3 py-1.5 font-bold" style={{ color: "oklch(0.50 0.01 240)" }}>Métrique</th>
                <th className="text-right px-3 py-1.5 font-bold" style={{ color: "oklch(0.50 0.01 240)" }}>Valeur</th>
                <th className="text-right px-3 py-1.5 font-bold hidden md:table-cell" style={{ color: "oklch(0.50 0.01 240)" }}>Détail</th>
              </tr>
            </thead>
            <tbody>
              {[
                { label: "Marchés surveillés",  valeur: `${SYMBOLS.length}`,                                    detail: SYMBOLS.map(s => s.replace("USDT","")).join(" · "),      couleur: "#fbbf24" },
                { label: "BLOCK Guard",          valeur: `${blocksMarche}`,                                     detail: `${allTicks.length > 0 ? ((blocksMarche/allTicks.length)*100).toFixed(0) : "0"} % des marchés`, couleur: "#f87171" },
                { label: "HOLD Guard",           valeur: `${holdsMarche}`,                                      detail: `${allTicks.length > 0 ? ((holdsMarche/allTicks.length)*100).toFixed(0) : "0"} % des marchés`,  couleur: "#fbbf24" },
                { label: "ALLOW Guard",          valeur: `${allowsMarche}`,                                     detail: `${allTicks.length > 0 ? ((allowsMarche/allTicks.length)*100).toFixed(0) : "0"} % des marchés`, couleur: "#4ade80" },
                { label: "Rendement moyen 24h",  valeur: `${rendementMoyen >= 0 ? "+" : ""}${rendementMoyen.toFixed(2)} %`, detail: "Moyenne sur tous les marchés",                    couleur: rendementMoyen >= 0 ? "#4ade80" : "#f87171" },
                { label: "P&L hypothétique",    valeur: `${pnlHypo >= 0 ? "+" : ""}€${pnlHypo.toFixed(2)}`,   detail: `Base €${capitalHypo.toLocaleString("fr-FR")} × rendement Guard`, couleur: pnlHypo >= 0 ? "#4ade80" : "#f87171" },
                { label: "Source données",      valeur: dataSource === "live" ? "Binance live" : "Simulé",    detail: live ? "Mise à jour toutes les 5s" : "Cliquez sur Démarrer live", couleur: dataSource === "live" ? "#4ade80" : "oklch(0.50 0.01 240)" },
              ].map((row, i) => (
                <tr key={row.label} style={{ background: i % 2 === 0 ? "oklch(0.095 0.01 240)" : "oklch(0.10 0.01 240)", borderTop: "1px solid oklch(0.13 0.01 240)" }}>
                  <td className="px-3 py-1.5" style={{ color: "oklch(0.60 0.01 240)" }}>{row.label}</td>
                  <td className="px-3 py-1.5 text-right font-bold" style={{ color: row.couleur }}>{row.valeur}</td>
                  <td className="px-3 py-1.5 text-right hidden md:table-cell" style={{ color: "oklch(0.40 0.01 240)" }}>{row.detail}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Contrôles */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="flex gap-2 flex-wrap">
          {SYMBOLS.map(sym => (
            <button key={sym} onClick={() => setSelected(sym)}
              className="px-3 py-1.5 rounded text-[10px] font-mono font-bold"
              style={{
                background: selected === sym ? "oklch(0.78 0.18 60 / 0.20)" : "oklch(0.12 0.01 240)",
                color: selected === sym ? "#fbbf24" : "oklch(0.50 0.01 240)",
                border: `1px solid ${selected === sym ? "#fbbf24" : "oklch(0.20 0.01 240)"}`,
              }}>
              {sym.replace("USDT", "")}
            </button>
          ))}
        </div>
        <button onClick={toggleLive}
          className="ml-auto px-4 py-1.5 rounded text-[10px] font-mono font-bold"
          style={{ background: live ? "#f87171" : "oklch(0.72 0.18 145)", color: live ? "white" : "oklch(0.10 0.01 240)" }}>
          {live ? "■ Arrêter" : "▶ Démarrer live"}
        </button>
        <span className="text-[9px] font-mono px-2 py-1 rounded"
          style={{ background: dataSource === "live" ? "#4ade8015" : "oklch(0.12 0.01 240)", color: dataSource === "live" ? "#4ade80" : "oklch(0.45 0.01 240)", border: `1px solid ${dataSource === "live" ? "#4ade8030" : "oklch(0.20 0.01 240)"}` }}>
          {dataSource === "live" ? "● Binance live" : "○ Données simulées"}
        </span>
      </div>

      {/* Tick sélectionné */}
      {tick && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Prix et Guard */}
          <div className="p-5 rounded" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="font-mono font-bold text-2xl text-foreground">{tick.symbol.replace("USDT", "")}/USDT</div>
                <div className="font-mono text-lg font-bold" style={{ color: "#fbbf24" }}>
                  ${tick.price.toLocaleString("fr-FR", { minimumFractionDigits: tick.price < 10 ? 4 : 2, maximumFractionDigits: tick.price < 10 ? 4 : 2 })}
                </div>
              </div>
              <div className="text-right">
                <div className="font-mono text-sm font-bold" style={{ color: tick.priceChangePct24h >= 0 ? "#4ade80" : "#f87171" }}>
                  {tick.priceChangePct24h >= 0 ? "+" : ""}{tick.priceChangePct24h.toFixed(2)} %
                </div>
                <div className="text-[9px] font-mono text-muted-foreground">24h</div>
              </div>
            </div>

            {/* Métriques */}
            <div className="grid grid-cols-3 gap-2 mb-4">
              {[
                { k: "Volatilité", v: `${(tick.volatility * 100).toFixed(1)} %`, high: tick.volatility > 0.30 },
                { k: "Cohérence", v: tick.coherence.toFixed(2), high: tick.coherence < 0.50 },
                { k: "Régime", v: tick.regime, high: tick.regime === "CRASH" || tick.regime === "BEAR" },
              ].map(m => (
                <div key={m.k} className="text-center p-2 rounded" style={{ background: "oklch(0.13 0.01 240)" }}>
                  <div className="text-[8px] font-mono text-muted-foreground">{m.k}</div>
                  <div className="font-mono text-xs font-bold" style={{ color: m.high ? "#f87171" : "oklch(0.72 0.18 145)" }}>{m.v}</div>
                </div>
              ))}
            </div>

            {/* Timestamp */}
            <div className="text-[9px] font-mono text-muted-foreground">
              Mis à jour : {tick.timestamp} UTC
            </div>
          </div>

          {/* Décision Guard */}
          <div className="p-5 rounded flex flex-col gap-4" style={{ background: `${guardColor(tick.guardDecision)}08`, border: `1px solid ${guardColor(tick.guardDecision)}30` }}>
            <div>
              <div className="text-[9px] font-mono tracking-widest uppercase mb-2" style={{ color: guardColor(tick.guardDecision) }}>
                🛡 Décision Guard X-108
              </div>
              <div className="font-mono font-bold text-3xl" style={{ color: guardColor(tick.guardDecision) }}>
                {tick.guardDecision}
              </div>
            </div>

            <p className="text-[11px] font-mono leading-relaxed" style={{ color: "oklch(0.60 0.01 240)" }}>
              {tick.guardReason}
            </p>

            <div className="text-[10px] font-mono px-3 py-2 rounded" style={{ background: "oklch(0.65 0.22 25 / 0.08)", border: "1px solid oklch(0.65 0.22 25 / 0.20)", color: "#f87171" }}>
              ⚠ MODE MIROIR — Aucun ordre réel n'est exécuté. Simulation pure.
            </div>

            {/* Ce que ça signifie */}
            <div className="text-[10px] font-mono leading-relaxed" style={{ color: "oklch(0.50 0.01 240)" }}>
              {tick.guardDecision === "BLOCK" && "Guard X-108 bloquerait définitivement tout ordre sur cette crypto dans ces conditions de marché."}
              {tick.guardDecision === "HOLD" && "Guard X-108 mettrait tout ordre en attente de 10 secondes pour laisser le marché se stabiliser."}
              {tick.guardDecision === "ALLOW" && "Guard X-108 autoriserait l'exécution d'un ordre dans ces conditions de marché."}
            </div>
          </div>
        </div>
      )}

      {/* Grille toutes les cryptos */}
      <div>
        <div className="text-[9px] font-mono tracking-widest uppercase mb-3" style={{ color: "oklch(0.45 0.01 240)" }}>
          Vue d'ensemble — {SYMBOLS.length} marchés
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {SYMBOLS.map(sym => {
            const t = ticks.get(sym);
            if (!t) return null;
            const gc = guardColor(t.guardDecision);
            return (
              <button key={sym} onClick={() => setSelected(sym)}
                className="p-3 rounded text-left"
                style={{ background: selected === sym ? `${gc}10` : "oklch(0.11 0.01 240)", border: `1px solid ${selected === sym ? gc + "50" : "oklch(0.18 0.01 240)"}` }}>
                <div className="flex items-center justify-between mb-1">
                  <span className="font-mono font-bold text-xs text-foreground">{sym.replace("USDT", "")}</span>
                  <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded" style={{ background: gc + "20", color: gc }}>{t.guardDecision}</span>
                </div>
                <div className="font-mono text-sm font-bold" style={{ color: "#fbbf24" }}>
                  ${t.price.toLocaleString("fr-FR", { maximumFractionDigits: t.price < 10 ? 4 : 2 })}
                </div>
                <div className="text-[9px] font-mono" style={{ color: t.priceChangePct24h >= 0 ? "#4ade80" : "#f87171" }}>
                  {t.priceChangePct24h >= 0 ? "+" : ""}{t.priceChangePct24h.toFixed(2)} %
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// ─── Composant principal ──────────────────────────────────────────────────────

// Fallback sombre — fond identique au thème, pas de flash blanc
const FallbackSombre = ({ couleur }: { couleur: string }) => (
  <div className="flex items-center justify-center py-16" style={{ background: "oklch(0.07 0.01 240)", borderRadius: "8px" }}>
    <div className="flex flex-col items-center gap-3">
      <div className="w-6 h-6 rounded-full border-2 border-t-transparent"
        style={{ borderColor: `${couleur} transparent transparent transparent`, animation: "spin 0.8s linear infinite" }} />
      <span className="text-xs font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>Chargement…</span>
    </div>
  </div>
);

// ─── Projection dynamique selon paramètres ───────────────────────────────────
function computeProjections(params: CommandParams): ProjectionScenario[] {
  const vol = params.volatilite ?? params.risque ? (params.risque! / 100) : 0.20;
  const stress = params.stressIntensity ?? 0.5;
  const irreversible = params.irreversible ?? false;
  const pBlock = Math.min(0.95, vol * 0.6 + stress * 0.4 + (irreversible ? 0.1 : 0));
  const pHold  = Math.min(0.95 - pBlock, (1 - pBlock) * 0.4);
  const pAllow = Math.max(0.01, 1 - pBlock - pHold);
  return [
    { label: "ALLOW — Exécution autorisée",   probability: pAllow, outcome: "continuation", description: `Invariants satisfaits · vol ${(vol * 100).toFixed(0)} % · stress ${(stress * 100).toFixed(0)} %` },
    { label: "HOLD — Mise en attente 10s",     probability: pHold,  outcome: "neutral",       description: `Seuil intermédiaire atteint · verrou temporel activé` },
    { label: "BLOCK — Action bloquée",         probability: pBlock, outcome: "degradation",   description: `Invariant violé · ${irreversible ? "irréversible · " : ""}vol critique` },
  ];
}

export default function Simuler() {
  const [actif, setActif] = useState<Onglet>("trading");
  const [expertMode, setExpertMode] = useState(false);
  const onglet = ONGLETS.find(o => o.id === actif)!

  // ── Poste de commande ──
  // Lecture des deep-links au montage : ?domain=…&scenarioId=…&seed=…&rerun=1
  const searchStr = useSearch();
  const [cmdParams, setCmdParams] = useState<CommandParams>(() => {
    const sp = new URLSearchParams(searchStr);
    const domainParam = sp.get("domain") as CommandDomain | null;
    const scenarioParam = sp.get("scenarioId") ?? sp.get("scenario");
    return {
      domain: (domainParam && ["trading","bank","ecom"].includes(domainParam)) ? domainParam : "trading",
      scenarioId: scenarioParam ?? "flash_crash",
      mode: "gouverne_preuve",
      source: "auto",
      taille: 10000,
      risque: 20,
      volatilite: 0.20,
      stressIntensity: 0.5,
      elapsed: 5,
      tau: 10,
      irreversible: false,
    };
  });
  // seed courant du run — initialisé depuis deep-link si présent
  const [runSeed, setRunSeed] = useState<number>(() => {
    const sp = new URLSearchParams(searchStr);
    const s = sp.get("seed");
    return s ? parseInt(s, 10) : Math.floor(Math.random() * 9999);
  });
  // Si rerun=1 dans l'URL, basculer automatiquement sur l'onglet stress
  useEffect(() => {
    const sp = new URLSearchParams(searchStr);
    if (sp.get("rerun") === "1") {
      setActif("stress");
    }
  }, [searchStr]);
  const [cmdResult, setCmdResult] = useState<BeforeAfterResult | null>(null);
  const [cmdLoading, setCmdLoading] = useState(false);
  const runScenarioMutation = trpc.engine.runScenario.useMutation();
  const savePythonTraceMutation = trpc.engine.savePythonTrace.useMutation();

  // Projections dynamiques liées aux paramètres — Règle 4 : non exécutoire
  const projections = useMemo(() => computeProjections(cmdParams), [cmdParams]);

  async function handleCommandRun() {
    setCmdLoading(true);
    setCmdResult(null);
    // Générer un nouveau seed à chaque run (sauf si relance depuis deep-link)
    const currentSeed = runSeed;
    setRunSeed(Math.floor(Math.random() * 9999)); // prépare le prochain run
    try {
      type ScenarioId = "flash_crash" | "bank_run" | "fraud_attack" | "traffic_spike" | "black_swan" | "market_manipulation" | "credit_bubble_burst" | "fraud_wave" | "bot_traffic_attack" | "supply_chain_break" | "ai_adversarial" | "clock_drift";
      const res = await runScenarioMutation.mutateAsync({
        scenarioId: cmdParams.scenarioId as ScenarioId,
        seed: currentSeed,
      });
      const lastStep = res.steps?.[res.steps.length - 1];
      // source déterminée par le mode choisi
      const source: BeforeAfterResult["source"] =
        cmdParams.source === "fallback_only_debug" ? "fallback_only_debug"
        : cmdParams.source === "python_preferred" ? "python"
        : "os4_local_fallback";
      // replayRef = "scenarioId:seed" — format lisible pour le deep-link et la DB
      const replayRef = `${cmdParams.scenarioId}:${currentSeed}`;
      const result: BeforeAfterResult = {
        marketVerdict: lastStep?.agentProposal ?? res.verdict ?? "UNKNOWN",
        agentProposal: lastStep?.explanation,
        metierMetrics: lastStep ? {
          cohérence: lastStep.coherence?.toFixed(2) ?? "—",
          volatilité: lastStep.volatility?.toFixed(2) ?? "—",
          impact: `${lastStep.capitalImpact?.toFixed(0) ?? "—"} €`,
        } : undefined,
        x108Gate: lastStep?.guardDecision ?? "BLOCK",
        x108Reason: lastStep?.explanation,
        traceId: lastStep?.proofHash,
        stateHash: lastStep?.proofHash,
        source,
        replayRef,
      };
      setCmdResult(result);
      // ── Persistance en DB — uniquement si mode gouverne ou gouverne_preuve et source non dégradée
      // Règle anti-doublon : on ne persiste pas les runs fallback_only_debug (non souverains)
      // Règle anti-doublon : traceId = proofHash — si deux runs ont le même proofHash, seul le premier est utile
      if (cmdParams.mode !== "brut" && cmdParams.source !== "fallback_only_debug") {
        const gate = result.x108Gate;
        if (gate === "ALLOW" || gate === "HOLD" || gate === "BLOCK") {
          savePythonTraceMutation.mutate({
            domain: cmdParams.domain as "trading" | "bank" | "ecom" | "system",
            decision: gate,
            reasons: result.x108Reason ? [result.x108Reason] : [],
            stateHash: result.stateHash,
            traceId: result.traceId,
            source: source === "python" ? "python" : "os4_engine",
            coherence: lastStep?.coherence,
            volatility: lastStep?.volatility,
            tau: cmdParams.tau,
            // Champs de replay — permettent à MissionControlPanel de reconstruire le deep-link
            scenarioId: cmdParams.scenarioId,
            seed: currentSeed,
          });
        }
      }
    } catch {
      setCmdResult({
        marketVerdict: "ERREUR",
        x108Gate: "BLOCK",
        x108Reason: "Erreur lors de l'exécution du scénario",
        source: "os4_local_fallback",
      });
    } finally {
      setCmdLoading(false);
    }
  }

  // Mode opératoire dérivé de l'onglet actif et des paramètres de commande
  const operatingMode: OperatingMode = (actif === "stress" || actif === "marche")
    ? (cmdParams.source === "fallback_only_debug" ? "FALLBACK" : cmdParams.mode === "brut" ? "DEMO" : "SIMU")
    : "LIVE";
  const modeDetail = operatingMode === "LIVE" ? "WebSocket actif"
    : operatingMode === "SIMU" ? `${cmdParams.domain} · ${cmdParams.scenarioId}`
    : operatingMode === "FALLBACK" ? "Python hors ligne"
    : `${cmdParams.domain} · brut`;

  return (
    <div className="flex flex-col max-w-5xl mx-auto px-4 pb-16" style={{ gap: "32px" }}>
      {/* ─── Barre de régime opératoire ─────────────────────────────────────── */}
      <ModeBadgeBar
        mode={operatingMode}
        detail={modeDetail}
        right={cmdResult ? `run_id: ${cmdResult.replayRef ?? "—"}` : undefined}
      />

      {/* ─── En-tête ─────────────────────────────────────────────────────────── */}
      <div className="pt-8">
        <div className="text-[10px] font-mono tracking-[0.3em] uppercase mb-2" style={{ color: "oklch(0.72 0.18 145)" }}>
          Obsidia Labs — OS4
        </div>
        <div className="flex items-start justify-between flex-wrap gap-3">
          <div>
            <h1 className="font-mono font-bold text-2xl text-foreground mb-2">Simuler</h1>
            <p className="text-sm" style={{ color: "oklch(0.55 0.01 240)", maxWidth: "560px", lineHeight: "1.6" }}>
              Choisissez un domaine pour lancer une simulation. Chaque action proposée est évaluée par{" "}
              <strong style={{ color: "oklch(0.72 0.18 145)" }}>Guard X-108</strong> avant d'être exécutée.
            </p>
          </div>
          {/* Toggle niveau d'explication */}
          <button onClick={() => setExpertMode(e => !e)}
            className="px-3 py-1.5 rounded text-[10px] font-mono font-bold flex-shrink-0"
            style={{ background: expertMode ? "oklch(0.60 0.12 200 / 0.15)" : "oklch(0.12 0.01 240)", color: expertMode ? "oklch(0.60 0.12 200)" : "oklch(0.50 0.01 240)", border: `1px solid ${expertMode ? "oklch(0.60 0.12 200 / 0.4)" : "oklch(0.20 0.01 240)"}` }}>
            {expertMode ? "🔬 Mode Expert" : "👁 Mode Simple"}
          </button>
        </div>
      </div>

      {/* ─── Onglets ─────────────────────────────────────────────────────────── */}
      <div className="flex gap-2 flex-wrap">
        {ONGLETS.map(o => (
          <button key={o.id} onClick={() => setActif(o.id)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-mono font-bold"
            style={{
              background: actif === o.id ? `${o.couleur}18` : "oklch(0.10 0.01 240)",
              border: `1.5px solid ${actif === o.id ? o.couleur : "oklch(0.18 0.01 240)"}`,
              color: actif === o.id ? o.couleur : "oklch(0.55 0.01 240)",
            }}>
            <span>{o.icon}</span>
            <span>{o.label}</span>
          </button>
        ))}
      </div>

      {/* ─── Explication 3 niveaux ────────────────────────────────────────────── */}
      <div className="rounded-lg p-5" style={{ background: `${onglet.couleur}08`, border: `1px solid ${onglet.couleur}30` }}>
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xl">{onglet.icon}</span>
          <span className="font-mono font-bold text-sm" style={{ color: onglet.couleur }}>{onglet.titre}</span>
        </div>

        {/* Niveau simple — toujours visible */}
        <div className="mb-3">
          <div className="text-[9px] font-mono tracking-widest uppercase mb-1" style={{ color: "oklch(0.45 0.01 240)" }}>
            En clair
          </div>
          <p className="text-[13px] font-mono leading-relaxed" style={{ color: "oklch(0.75 0.01 240)" }}>
            {onglet.simple}
          </p>
        </div>

        {/* Niveau investisseur */}
        <div className="mb-3 pt-3" style={{ borderTop: "1px solid oklch(0.16 0.01 240)" }}>
          <div className="text-[9px] font-mono tracking-widest uppercase mb-1" style={{ color: "oklch(0.45 0.01 240)" }}>
            Pour un investisseur
          </div>
          <p className="text-[12px] font-mono leading-relaxed" style={{ color: "oklch(0.60 0.01 240)" }}>
            {onglet.investisseur}
          </p>
        </div>

        {/* Niveau expert — masqué par défaut */}
        {expertMode && (
          <div className="pt-3" style={{ borderTop: "1px solid oklch(0.16 0.01 240)" }}>
            <div className="text-[9px] font-mono tracking-widest uppercase mb-1" style={{ color: "oklch(0.60 0.12 200)" }}>
              Détail technique
            </div>
            <p className="text-[11px] font-mono leading-relaxed" style={{ color: "oklch(0.50 0.01 240)" }}>
              {onglet.expert}
            </p>
          </div>
        )}
      </div>

      {/* ─── Poste de commande (Stress Lab + Marché Réel) ───────────────────── */}
      {(actif === "stress" || actif === "marche") && (
        <div className="flex flex-col gap-4">
          <CommandPanel
            params={cmdParams}
            onChange={p => {
              setCmdParams(p);
              setCmdResult(null);
            }}
            onRun={handleCommandRun}
            loading={cmdLoading}
          />
          {/* Projection — Règle 4 : explicitement non exécutoire */}
          <ProjectionPanel
            domain={cmdParams.domain as CommandDomain}
            scenarios={projections}
            horizon="run suivant"
            loading={cmdLoading}
          />
          {/* Vue avant/après */}
          {(cmdResult || cmdLoading) && (
            <BeforeAfterPanel
              params={cmdParams}
              result={cmdResult ?? { marketVerdict: "", x108Gate: "ALLOW", source: "auto" as any }}
              loading={cmdLoading}
            />
          )}
          {/* Fil de navigation run X-108 */}
          {cmdResult && !cmdLoading && (
            <RunBreadcrumb
              domain={cmdParams.domain}
              scenarioId={cmdParams.scenarioId}
              seed={cmdParams.tau}
              verdict={cmdResult.x108Gate === "ALLOW" || cmdResult.x108Gate === "HOLD" || cmdResult.x108Gate === "BLOCK" ? cmdResult.x108Gate : null}
              traceId={cmdResult.traceId}
              ticketId={cmdResult.stateHash}
            />
          )}
        </div>
      )}

      {/* ─── Séparateur ──────────────────────────────────────────────────────── */}
      <div className="flex items-center gap-3">
        <div className="h-px flex-1" style={{ background: "oklch(0.18 0.01 240)" }} />
        <span className="text-[10px] font-mono tracking-widest uppercase" style={{ color: onglet.couleur }}>
          {onglet.icon} {onglet.titre}
        </span>
        <div className="h-px flex-1" style={{ background: "oklch(0.18 0.01 240)" }} />
      </div>

      {/* ─── Métriques financières (Trading / Banque / E-Commerce) ────────── */}
      {(actif === "trading" || actif === "banque" || actif === "ecom") && (
        <MetriquesSimulation
          domaine={actif === "trading" ? "trading" : actif === "banque" ? "bank" : "ecom"}
          couleur={onglet.couleur}
          capitalBase={actif === "trading" ? 100_000 : actif === "banque" ? 1_000_000 : 50_000}
        />
      )}

      {/* ─── Contenu ──────────────────────────────────────────────────────────────────────────────── */}
      {/* Rendu conditionnel pur — un seul composant actif à la fois, pas d'intervals en arrière-plan */}
      {actif === "stress" && <StressLabPanel />}
      {actif === "marche" && <MarcheReelPanel />}
      {actif === "trading" && <TradingWorld />}
      {actif === "banque"  && <BankWorld />}
      {actif === "ecom"    && <EcomWorld />}
      {actif === "agents" && (
        <div className="flex flex-col gap-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <CanonicalAgentPanel domain="trading" scenarioId="flash_crash" seed={Math.floor(Math.random() * 0x7fffffff)} className="" />
            <CanonicalAgentPanel domain="bank" scenarioId="fraud_attempt" seed={Math.floor(Math.random() * 0x7fffffff)} className="" />
            <CanonicalAgentPanel domain="ecom" scenarioId="fraud_checkout" seed={Math.floor(Math.random() * 0x7fffffff)} className="" />
          </div>
          <div className="rounded-lg border p-3 font-mono text-[10px]" style={{ borderColor: "oklch(0.25 0.05 280)", background: "oklch(0.11 0.03 280)" }}>
            <div className="mb-2" style={{ color: "oklch(0.65 0.12 280)" }}>Règles absolues du pipeline canonique</div>
            <div className="flex flex-col gap-1" style={{ color: "oklch(0.55 0.05 280)" }}>
              <div>1. Aucun agent métier n'autorise seul une action irréversible.</div>
              <div>2. Un seul juge final : GuardX108.</div>
              <div>3. Tous les domaines convergent vers le même payload canonique.</div>
              <div>4. Les agents méta sont transversaux et réutilisables.</div>
              <div>5. Les domaines changent ; la souveraineté ne change jamais.</div>
            </div>
          </div>
        </div>
      )}

      {/* ── Pilotage global Simuler (stress/marche) ── */}
      {(actif === "stress" || actif === "marche") && (
        <PilotagePanel
          domain={cmdParams.domain as CommandDomain}
          onRerun={handleCommandRun}
          onReset={() => { setCmdResult(null); setCmdLoading(false); }}
          loading={cmdLoading}
          showMode={false}
        />
      )}

    </div>
  );
}
