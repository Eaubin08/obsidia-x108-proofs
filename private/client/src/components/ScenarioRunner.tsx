import React, { useState, useRef } from "react";
import { trpc } from "@/lib/trpc";

// ─── Types ────────────────────────────────────────────────────────────────────

type ScenarioId = "flash_crash" | "bank_run" | "fraud_attack" | "traffic_spike";
type GuardDecision = "ALLOW" | "HOLD" | "BLOCK";

interface ScenarioStep {
  step: number;
  timestamp: number;
  world: string;
  event: string;
  agentProposal: string;
  coherence: number;
  volatility: number;
  guardDecision: GuardDecision;
  holdDuration?: number;
  capitalImpact: number;
  proofHash: string;
  explanation: string;
}

interface ScenarioResult {
  scenarioId: string;
  scenarioName: string;
  world: string;
  seed: number;
  totalSteps: number;
  steps: ScenarioStep[];
  summary: {
    totalBlock: number;
    totalHold: number;
    totalAllow: number;
    capitalSaved: number;
    capitalExposed: number;
    avgCoherence: number;
    minCoherence: number;
    maxCoherence: number;
    blockRate: number;
    holdRate: number;
    allowRate: number;
  };
  verdict: "SAFE" | "DEGRADED" | "CRITICAL";
  verdictReason: string;
}

interface BatchResult {
  scenarioId: string;
  seeds: number[];
  results: ScenarioResult[];
  aggregated: {
    avgBlockRate: number;
    avgHoldRate: number;
    avgAllowRate: number;
    avgCapitalSaved: number;
    safeCount: number;
    degradedCount: number;
    criticalCount: number;
  };
}

// ─── Scenario Metadata ────────────────────────────────────────────────────────

const SCENARIOS: { id: ScenarioId; label: string; world: string; icon: string; color: string; desc: string }[] = [
  {
    id: "flash_crash",
    label: "Flash Crash",
    world: "Trading",
    icon: "📉",
    color: "#f87171",
    desc: "Effondrement stochastique du marché — GBM + régime Markov + GARCH. 60 steps. Guard X-108 protège contre les ordres irréversibles pendant le crash.",
  },
  {
    id: "bank_run",
    label: "Bank Run",
    world: "Bank",
    icon: "🏃",
    color: "#fbbf24",
    desc: "Crise de liquidité bancaire — retraits massifs en cascade. 55 steps. Guard X-108 bloque les transactions irréversibles qui épuiseraient la liquidité.",
  },
  {
    id: "fraud_attack",
    label: "Fraud Attack",
    world: "Bank",
    icon: "🚨",
    color: "#a78bfa",
    desc: "Attaque multi-vecteurs (phishing, SIM swap, IBAN spoofing). 50 steps. Guard X-108 détecte et bloque les transactions frauduleuses via TSG/DTS.",
  },
  {
    id: "traffic_spike",
    label: "Traffic Spike",
    world: "E-Com",
    icon: "📈",
    color: "#60a5fa",
    desc: "Surge de trafic x50 (Black Friday) — risque de destruction de marge. 52 steps. Guard X-108 bloque les actions commerciales destructrices de valeur.",
  },
];

// ─── Helpers ──────────────────────────────────────────────────────────────────

const decisionColor = (d: GuardDecision) => d === "BLOCK" ? "#f87171" : d === "HOLD" ? "#fbbf24" : "#4ade80";
const verdictColor = (v: string) => v === "SAFE" ? "#4ade80" : v === "DEGRADED" ? "#fbbf24" : "#f87171";
const verdictBg = (v: string) => v === "SAFE" ? "oklch(0.72 0.18 145 / 0.12)" : v === "DEGRADED" ? "oklch(0.75 0.18 75 / 0.12)" : "oklch(0.60 0.20 25 / 0.12)";

// ─── Component ────────────────────────────────────────────────────────────────

export default function ScenarioRunner() {
  const [activeScenario, setActiveScenario] = useState<ScenarioId>("flash_crash");
  const [seed, setSeed] = useState(42);
  const [result, setResult] = useState<ScenarioResult | null>(null);
  const [batchResult, setBatchResult] = useState<BatchResult | null>(null);
  const [mode, setMode] = useState<"single" | "batch">("single");
  const [replayStep, setReplayStep] = useState<number | null>(null);
  const [persistedStats, setPersistedStats] = useState<{ scenarioId: string; verdict: string; blockRate: number; capitalSaved: number; seed: number }[]>([]);
  const stepsRef = useRef<HTMLDivElement>(null);

  const runScenario = trpc.engine.runScenario.useMutation({
    onSuccess: (data) => {
      setResult(data as ScenarioResult);
      setBatchResult(null);
      setReplayStep(null);
      setPersistedStats(prev => [...prev.slice(-19), {
        scenarioId: data.scenarioId,
        verdict: data.verdict,
        blockRate: data.summary.blockRate,
        capitalSaved: data.summary.capitalSaved,
        seed,
      }]);
    },
  });

  const batchRun = trpc.engine.batchRun.useMutation({
    onSuccess: (data) => {
      setBatchResult(data as BatchResult);
      setResult(null);
      setReplayStep(null);
    },
  });

  const isLoading = runScenario.isPending || batchRun.isPending;
  const scenarioMeta = SCENARIOS.find(s => s.id === activeScenario)!;

  const handleRun = () => {
    if (mode === "single") {
      runScenario.mutate({ scenarioId: activeScenario, seed });
    } else {
      batchRun.mutate({ scenarioId: activeScenario, seeds: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] });
    }
  };

  const replayedStep = result && replayStep !== null ? result.steps[replayStep] : null;

  return (
    <div className="panel p-0 overflow-hidden" style={{ border: "1px solid oklch(0.18 0.02 240)" }}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3" style={{ background: "oklch(0.10 0.02 240)", borderBottom: "1px solid oklch(0.18 0.02 240)" }}>
        <div className="flex items-center gap-2">
          <span className="text-base">⚡</span>
          <span className="font-mono font-bold text-sm text-foreground">Scenario Engine</span>
          <span className="text-[9px] font-mono px-1.5 py-0.5 rounded" style={{ background: "oklch(0.65 0.18 220 / 0.15)", color: "#60a5fa" }}>OS4 v11</span>
        </div>
        <div className="flex items-center gap-2">
          {(["single", "batch"] as const).map(m => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className="text-[9px] font-mono px-2 py-0.5 rounded"
              style={{
                background: mode === m ? "oklch(0.65 0.18 220 / 0.20)" : "transparent",
                color: mode === m ? "#60a5fa" : "oklch(0.40 0.01 240)",
                border: `1px solid ${mode === m ? "oklch(0.65 0.18 220 / 0.40)" : "oklch(0.18 0.01 240)"}`,
              }}
            >
              {m === "single" ? "Single Run" : "Batch Run (10 seeds)"}
            </button>
          ))}
        </div>
      </div>

      <div className="p-4">
        {/* Scenario selector */}
        <div className="grid grid-cols-4 gap-2 mb-4">
          {SCENARIOS.map(sc => (
            <button
              key={sc.id}
              onClick={() => { setActiveScenario(sc.id); setResult(null); setBatchResult(null); setReplayStep(null); }}
              className="p-3 rounded text-left transition-all"
              style={{
                background: activeScenario === sc.id ? `${sc.color}12` : "oklch(0.09 0.01 240)",
                border: `1px solid ${activeScenario === sc.id ? sc.color + "50" : "oklch(0.16 0.01 240)"}`,
              }}
            >
              <div className="text-lg mb-1">{sc.icon}</div>
              <div className="font-mono font-bold text-[10px]" style={{ color: activeScenario === sc.id ? sc.color : "oklch(0.65 0.01 240)" }}>{sc.label}</div>
              <div className="text-[8px] font-mono text-zinc-600 mt-0.5">{sc.world}</div>
            </button>
          ))}
        </div>

        {/* Scenario description */}
        <div className="rounded p-3 mb-4 text-[10px] font-mono text-zinc-400" style={{ background: `${scenarioMeta.color}08`, border: `1px solid ${scenarioMeta.color}25` }}>
          <span className="font-bold" style={{ color: scenarioMeta.color }}>{scenarioMeta.icon} {scenarioMeta.label} — </span>
          {scenarioMeta.desc}
        </div>

        {/* Controls */}
        <div className="flex items-center gap-3 mb-4">
          {mode === "single" && (
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono text-zinc-500">Seed :</span>
              <input
                type="number"
                value={seed}
                onChange={e => setSeed(Number(e.target.value))}
                className="w-16 px-2 py-1 rounded text-[10px] font-mono text-center"
                style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.22 0.01 240)", color: "#e2e8f0" }}
              />
            </div>
          )}
          <button
            onClick={handleRun}
            disabled={isLoading}
            className="px-4 py-1.5 rounded font-mono font-bold text-xs transition-all"
            style={{
              background: isLoading ? "oklch(0.20 0.01 240)" : `${scenarioMeta.color}20`,
              color: isLoading ? "oklch(0.40 0.01 240)" : scenarioMeta.color,
              border: `1px solid ${isLoading ? "oklch(0.22 0.01 240)" : scenarioMeta.color + "50"}`,
            }}
          >
            {isLoading ? "⏳ Running..." : mode === "single" ? `▶ Run ${scenarioMeta.label}` : `▶ Batch Run × 10 seeds`}
          </button>
        </div>

        {/* Single result */}
        {result && (
          <div>
            {/* Verdict */}
            <div className="rounded p-3 mb-3 flex items-center justify-between" style={{ background: verdictBg(result.verdict), border: `1px solid ${verdictColor(result.verdict)}30` }}>
              <div>
                <span className="font-mono font-bold text-sm" style={{ color: verdictColor(result.verdict) }}>
                  {result.verdict === "SAFE" ? "✅" : result.verdict === "DEGRADED" ? "⚠️" : "🚨"} {result.verdict}
                </span>
                <p className="text-[10px] font-mono text-zinc-400 mt-0.5">{result.verdictReason}</p>
              </div>
              <div className="text-right">
                <div className="text-[9px] font-mono text-zinc-500">Seed {result.seed} · {result.totalSteps} steps</div>
                <div className="text-[9px] font-mono" style={{ color: "#4ade80" }}>Capital protégé : {result.summary.capitalSaved.toLocaleString()} EUR</div>
              </div>
            </div>

            {/* Summary stats */}
            <div className="grid grid-cols-3 gap-2 mb-3">
              {[
                { label: "BLOCK", value: result.summary.totalBlock, rate: result.summary.blockRate, color: "#f87171" },
                { label: "HOLD", value: result.summary.totalHold, rate: result.summary.holdRate, color: "#fbbf24" },
                { label: "ALLOW", value: result.summary.totalAllow, rate: result.summary.allowRate, color: "#4ade80" },
              ].map(s => (
                <div key={s.label} className="rounded p-2 text-center" style={{ background: `${s.color}10`, border: `1px solid ${s.color}25` }}>
                  <div className="font-mono font-bold text-lg" style={{ color: s.color }}>{s.value}</div>
                  <div className="text-[8px] font-mono" style={{ color: s.color }}>{s.label}</div>
                  <div className="text-[8px] font-mono text-zinc-600">{(s.rate * 100).toFixed(0)}%</div>
                </div>
              ))}
            </div>

            {/* Coherence bar */}
            <div className="flex items-center gap-2 mb-3">
              <span className="text-[9px] font-mono text-zinc-500 w-20">Avg coherence</span>
              <div className="flex-1 h-2 rounded-full bg-zinc-800">
                <div className="h-full rounded-full" style={{ width: `${result.summary.avgCoherence * 100}%`, background: result.summary.avgCoherence >= 0.6 ? "#4ade80" : result.summary.avgCoherence >= 0.3 ? "#fbbf24" : "#f87171" }} />
              </div>
              <span className="text-[9px] font-mono text-zinc-400">{(result.summary.avgCoherence * 100).toFixed(0)}%</span>
              <span className="text-[8px] font-mono text-zinc-600">min {(result.summary.minCoherence * 100).toFixed(0)}% · max {(result.summary.maxCoherence * 100).toFixed(0)}%</span>
            </div>

            {/* Steps timeline */}
            <div className="mb-3">
              <div className="text-[9px] font-mono text-zinc-500 mb-1.5 flex items-center justify-between">
                <span>Decision Timeline — cliquer pour Replay</span>
                {replayStep !== null && <button onClick={() => setReplayStep(null)} className="text-zinc-600 hover:text-zinc-400">✕ fermer replay</button>}
              </div>
              <div ref={stepsRef} className="flex gap-0.5 flex-wrap">
                {result.steps.map((s, i) => (
                  <button
                    key={s.step}
                    onClick={() => setReplayStep(replayStep === i ? null : i)}
                    title={`Step ${s.step}: ${s.guardDecision}`}
                    className="w-3 h-3 rounded-sm transition-all"
                    style={{
                      background: decisionColor(s.guardDecision),
                      opacity: replayStep === i ? 1 : 0.7,
                      transform: replayStep === i ? "scale(1.5)" : "scale(1)",
                      outline: replayStep === i ? `1px solid ${decisionColor(s.guardDecision)}` : "none",
                    }}
                  />
                ))}
              </div>
              <div className="flex gap-3 mt-1">
                {[{ label: "BLOCK", color: "#f87171" }, { label: "HOLD", color: "#fbbf24" }, { label: "ALLOW", color: "#4ade80" }].map(l => (
                  <span key={l.label} className="text-[8px] font-mono flex items-center gap-1" style={{ color: l.color }}>
                    <span className="w-2 h-2 rounded-sm inline-block" style={{ background: l.color }} /> {l.label}
                  </span>
                ))}
              </div>
            </div>

            {/* Replay panel */}
            {replayedStep && (
              <div className="rounded p-3 mb-3" style={{ background: `${decisionColor(replayedStep.guardDecision)}08`, border: `1px solid ${decisionColor(replayedStep.guardDecision)}30` }}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono font-bold text-[10px]" style={{ color: decisionColor(replayedStep.guardDecision) }}>
                    Step {replayedStep.step} — {replayedStep.guardDecision}
                  </span>
                  <span className="text-[8px] font-mono text-zinc-600">proof: {replayedStep.proofHash}</span>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <div className="text-[8px] font-mono text-zinc-500 mb-1">WHAT THE ENGINE SEES</div>
                    <div className="text-[9px] font-mono text-zinc-300">Event: {replayedStep.event}</div>
                    <div className="text-[9px] font-mono text-zinc-300">Proposal: {replayedStep.agentProposal}</div>
                    <div className="text-[9px] font-mono text-zinc-400">Coherence: {(replayedStep.coherence * 100).toFixed(0)}% · Volatility: {(replayedStep.volatility * 100).toFixed(0)}%</div>
                  </div>
                  <div>
                    <div className="text-[8px] font-mono text-zinc-500 mb-1">WHY THIS DECISION</div>
                    <div className="text-[9px] font-mono text-zinc-300 leading-relaxed">{replayedStep.explanation}</div>
                    {replayedStep.holdDuration && (
                      <div className="text-[8px] font-mono mt-1" style={{ color: "#fbbf24" }}>HOLD τ={replayedStep.holdDuration}s obligatoire</div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Batch result */}
        {batchResult && (
          <div>
            <div className="text-[10px] font-mono text-zinc-400 mb-3">
              Batch Run — {batchResult.seeds.length} seeds · Scénario : <span className="text-zinc-200">{batchResult.scenarioId}</span>
            </div>
            {/* Aggregated stats */}
            <div className="grid grid-cols-3 gap-2 mb-3">
              {[
                { label: "SAFE", value: batchResult.aggregated.safeCount, color: "#4ade80" },
                { label: "DEGRADED", value: batchResult.aggregated.degradedCount, color: "#fbbf24" },
                { label: "CRITICAL", value: batchResult.aggregated.criticalCount, color: "#f87171" },
              ].map(s => (
                <div key={s.label} className="rounded p-2 text-center" style={{ background: `${s.color}10`, border: `1px solid ${s.color}25` }}>
                  <div className="font-mono font-bold text-lg" style={{ color: s.color }}>{s.value}/10</div>
                  <div className="text-[8px] font-mono" style={{ color: s.color }}>{s.label}</div>
                </div>
              ))}
            </div>
            <div className="grid grid-cols-3 gap-2 mb-3">
              {[
                { label: "Avg BLOCK rate", value: `${(batchResult.aggregated.avgBlockRate * 100).toFixed(0)}%`, color: "#f87171" },
                { label: "Avg HOLD rate", value: `${(batchResult.aggregated.avgHoldRate * 100).toFixed(0)}%`, color: "#fbbf24" },
                { label: "Avg capital saved", value: `${Math.round(batchResult.aggregated.avgCapitalSaved).toLocaleString()} EUR`, color: "#4ade80" },
              ].map(s => (
                <div key={s.label} className="rounded p-2" style={{ background: "oklch(0.09 0.01 240)", border: "1px solid oklch(0.16 0.01 240)" }}>
                  <div className="text-[8px] font-mono text-zinc-500">{s.label}</div>
                  <div className="font-mono font-bold text-sm" style={{ color: s.color }}>{s.value}</div>
                </div>
              ))}
            </div>
            {/* Per-seed results */}
            <div className="space-y-1">
              {batchResult.results.map(r => (
                <div key={r.seed} className="flex items-center gap-3 px-2 py-1.5 rounded text-[9px] font-mono" style={{ background: "oklch(0.09 0.01 240)", border: "1px solid oklch(0.14 0.01 240)" }}>
                  <span className="text-zinc-500 w-10">seed {r.seed}</span>
                  <span className="font-bold" style={{ color: verdictColor(r.verdict) }}>{r.verdict}</span>
                  <span style={{ color: "#f87171" }}>B:{r.summary.totalBlock}</span>
                  <span style={{ color: "#fbbf24" }}>H:{r.summary.totalHold}</span>
                  <span style={{ color: "#4ade80" }}>A:{r.summary.totalAllow}</span>
                  <span className="ml-auto text-zinc-600">{r.summary.capitalSaved.toLocaleString()} EUR saved</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Persisted stats table */}
        {persistedStats.length > 0 && (
          <div className="mt-4">
            <div className="text-[9px] font-mono text-zinc-500 mb-1.5">Historique des runs (persisté)</div>
            <div className="overflow-x-auto">
              <table className="w-full text-[8px] font-mono">
                <thead>
                  <tr className="text-zinc-600">
                    <th className="text-left px-1 py-0.5">#</th>
                    <th className="text-left px-1 py-0.5">Scénario</th>
                    <th className="text-left px-1 py-0.5">Seed</th>
                    <th className="text-left px-1 py-0.5">Verdict</th>
                    <th className="text-right px-1 py-0.5">BLOCK%</th>
                    <th className="text-right px-1 py-0.5">Capital saved</th>
                  </tr>
                </thead>
                <tbody>
                  {persistedStats.map((s, i) => (
                    <tr key={i} className="border-t" style={{ borderColor: "oklch(0.12 0.01 240)" }}>
                      <td className="px-1 py-0.5 text-zinc-600">{i + 1}</td>
                      <td className="px-1 py-0.5 text-zinc-300">{s.scenarioId}</td>
                      <td className="px-1 py-0.5 text-zinc-500">{s.seed}</td>
                      <td className="px-1 py-0.5 font-bold" style={{ color: verdictColor(s.verdict) }}>{s.verdict}</td>
                      <td className="px-1 py-0.5 text-right" style={{ color: "#f87171" }}>{(s.blockRate * 100).toFixed(0)}%</td>
                      <td className="px-1 py-0.5 text-right" style={{ color: "#4ade80" }}>{s.capitalSaved.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
