import React, { useState, useCallback } from "react";
import { trpc } from "@/lib/trpc";

// ─── Types ────────────────────────────────────────────────────────────────────

type ScenarioId = "flash_crash" | "bank_run" | "fraud_attack" | "traffic_spike";

interface SeedSummary {
  seed: number;
  verdict: "SAFE" | "DEGRADED" | "CRITICAL";
  blockRate: number;
  holdRate: number;
  allowRate: number;
  avgCoherence: number;
  capitalSaved: number;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

const VERDICT_COLOR: Record<string, string> = {
  SAFE: "#4ade80",
  DEGRADED: "#fbbf24",
  CRITICAL: "#f87171",
};

const SCENARIO_LABELS: Record<ScenarioId, { label: string; icon: string; domain: string }> = {
  flash_crash: { label: "Flash Crash", icon: "📉", domain: "trading" },
  bank_run: { label: "Bank Run", icon: "🏦", domain: "bank" },
  fraud_attack: { label: "Fraud Attack", icon: "🚨", domain: "bank" },
  traffic_spike: { label: "Traffic Spike", icon: "🛒", domain: "ecom" },
};

// ─── Component ────────────────────────────────────────────────────────────────

export default function EngineTransparency() {
  const [scenarioId, setScenarioId] = useState<ScenarioId>("flash_crash");
  const [seedSummaries, setSeedSummaries] = useState<SeedSummary[]>([]);
  const [aggregated, setAggregated] = useState<{
    avgBlockRate: number;
    avgHoldRate: number;
    avgAllowRate: number;
    avgCapitalSaved: number;
    safeCount: number;
    degradedCount: number;
    criticalCount: number;
  } | null>(null);
  const [running, setRunning] = useState(false);
  const [expandedSeed, setExpandedSeed] = useState<number | null>(null);

  const batchRunMutation = trpc.engine.batchRun.useMutation();

  const runBatch = useCallback(async () => {
    setRunning(true);
    setSeedSummaries([]);
    setAggregated(null);
    try {
      const seeds = [1, 7, 13, 21, 42, 77, 100, 137, 256, 999];
      const result = await batchRunMutation.mutateAsync({ scenarioId, seeds });
      // Map ScenarioResult[] → SeedSummary[]
      const summaries: SeedSummary[] = result.results.map(r => ({
        seed: r.seed,
        verdict: r.verdict,
        blockRate: r.summary.blockRate,
        holdRate: r.summary.holdRate,
        allowRate: r.summary.allowRate,
        avgCoherence: r.summary.avgCoherence,
        capitalSaved: r.summary.capitalSaved,
      }));
      setSeedSummaries(summaries);
      setAggregated(result.aggregated);
    } catch (err) {
      console.error("batchRun error:", err);
    } finally {
      setRunning(false);
    }
  }, [scenarioId, batchRunMutation]);

  const meta = SCENARIO_LABELS[scenarioId];

  return (
    <div className="panel p-0 overflow-hidden" style={{ border: "1px solid oklch(0.18 0.02 240)" }}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3" style={{ background: "oklch(0.10 0.02 240)", borderBottom: "1px solid oklch(0.18 0.02 240)" }}>
        <div className="flex items-center gap-2">
          <span className="text-base">🔭</span>
          <span className="font-mono font-bold text-sm text-foreground">Engine Transparency</span>
          <span className="text-[9px] font-mono px-1.5 py-0.5 rounded" style={{ background: "oklch(0.65 0.18 145 / 0.15)", color: "#4ade80" }}>Batch Run · 10 seeds</span>
        </div>
        <div className="text-[9px] font-mono text-zinc-500">Robustesse statistique du Guard X-108</div>
      </div>

      <div className="p-4">
        {/* Scenario selector + Run button */}
        <div className="flex items-center gap-2 mb-4 flex-wrap">
          <div className="text-[9px] font-mono text-zinc-500">Scénario :</div>
          {(Object.entries(SCENARIO_LABELS) as [ScenarioId, typeof SCENARIO_LABELS[ScenarioId]][]).map(([id, m]) => (
            <button
              key={id}
              onClick={() => setScenarioId(id)}
              className="px-2.5 py-1 rounded font-mono text-[9px] font-bold transition-all flex items-center gap-1"
              style={{
                background: scenarioId === id ? "oklch(0.65 0.18 145 / 0.2)" : "oklch(0.09 0.01 240)",
                border: `1px solid ${scenarioId === id ? "oklch(0.65 0.18 145 / 0.5)" : "oklch(0.16 0.01 240)"}`,
                color: scenarioId === id ? "#4ade80" : "oklch(0.55 0.01 240)",
              }}
            >
              <span>{m.icon}</span>
              <span>{m.label}</span>
            </button>
          ))}
          <button
            onClick={runBatch}
            disabled={running}
            className="ml-auto px-4 py-1.5 rounded font-mono text-[10px] font-bold transition-all"
            style={{
              background: running ? "oklch(0.15 0.01 240)" : "oklch(0.65 0.18 145)",
              color: running ? "oklch(0.55 0.01 240)" : "oklch(0.10 0.01 240)",
              cursor: running ? "not-allowed" : "pointer",
            }}
          >
            {running ? "Running..." : `▶ Run 10 Seeds — ${meta.icon} ${meta.label}`}
          </button>
        </div>

        {/* Aggregated stats */}
        {aggregated && (
          <div className="grid grid-cols-5 gap-2 mb-4">
            {[
              { label: "SAFE", value: aggregated.safeCount, color: "#4ade80" },
              { label: "DEGRADED", value: aggregated.degradedCount, color: "#fbbf24" },
              { label: "CRITICAL", value: aggregated.criticalCount, color: "#f87171" },
              { label: "AVG BLOCK", value: `${(aggregated.avgBlockRate * 100).toFixed(1)}%`, color: "#f87171" },
              { label: "CAPITAL SAVED", value: `${(aggregated.avgCapitalSaved / 1000).toFixed(0)}k`, color: "#60a5fa" },
            ].map(m => (
              <div key={m.label} className="rounded p-2 text-center" style={{ background: "oklch(0.09 0.01 240)", border: "1px solid oklch(0.16 0.01 240)" }}>
                <div className="font-mono font-bold text-lg" style={{ color: m.color }}>{m.value}</div>
                <div className="text-[8px] font-mono text-zinc-500 mt-0.5">{m.label}</div>
              </div>
            ))}
          </div>
        )}

        {/* Distribution bar */}
        {aggregated && (
          <div className="mb-4">
            <div className="text-[8px] font-mono text-zinc-500 mb-1.5">Distribution SAFE/DEGRADED/CRITICAL sur 10 seeds</div>
            <div className="h-4 rounded overflow-hidden flex">
              {aggregated.safeCount > 0 && (
                <div className="h-full flex items-center justify-center text-[7px] font-mono font-bold" style={{ width: `${aggregated.safeCount * 10}%`, background: "#4ade8030", color: "#4ade80", borderRight: "1px solid oklch(0.12 0.01 240)" }}>
                  {aggregated.safeCount > 1 ? `${aggregated.safeCount}×` : ""}
                </div>
              )}
              {aggregated.degradedCount > 0 && (
                <div className="h-full flex items-center justify-center text-[7px] font-mono font-bold" style={{ width: `${aggregated.degradedCount * 10}%`, background: "#fbbf2430", color: "#fbbf24", borderRight: "1px solid oklch(0.12 0.01 240)" }}>
                  {aggregated.degradedCount > 1 ? `${aggregated.degradedCount}×` : ""}
                </div>
              )}
              {aggregated.criticalCount > 0 && (
                <div className="h-full flex items-center justify-center text-[7px] font-mono font-bold" style={{ width: `${aggregated.criticalCount * 10}%`, background: "#f8717130", color: "#f87171" }}>
                  {aggregated.criticalCount > 1 ? `${aggregated.criticalCount}×` : ""}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Seed results */}
        {seedSummaries.length > 0 && (
          <div>
            <div className="text-[9px] font-mono text-zinc-500 mb-2">Résultats par seed — cliquer pour voir les détails</div>
            <div className="space-y-1">
              {seedSummaries.map(r => (
                <div key={r.seed}>
                  <button
                    onClick={() => setExpandedSeed(expandedSeed === r.seed ? null : r.seed)}
                    className="w-full flex items-center gap-3 px-3 py-2 rounded text-left transition-all"
                    style={{
                      background: expandedSeed === r.seed ? `${VERDICT_COLOR[r.verdict]}10` : "oklch(0.09 0.01 240)",
                      border: `1px solid ${expandedSeed === r.seed ? VERDICT_COLOR[r.verdict] + "30" : "oklch(0.15 0.01 240)"}`,
                    }}
                  >
                    <span className="text-[8px] font-mono text-zinc-600 w-16">seed={r.seed}</span>
                    <span className="text-[9px] font-mono px-1.5 py-0.5 rounded font-bold" style={{ background: `${VERDICT_COLOR[r.verdict]}15`, color: VERDICT_COLOR[r.verdict] }}>
                      {r.verdict}
                    </span>
                    <span className="text-[9px] font-mono text-zinc-400">block={`${(r.blockRate * 100).toFixed(1)}%`}</span>
                    <span className="text-[9px] font-mono text-zinc-500">coh={`${(r.avgCoherence * 100).toFixed(1)}%`}</span>
                    <span className="text-[8px] font-mono text-zinc-600 ml-auto">{expandedSeed === r.seed ? "▲" : "▼"}</span>
                  </button>
                  {expandedSeed === r.seed && (
                    <div className="px-3 py-2 rounded-b space-y-1" style={{ background: `${VERDICT_COLOR[r.verdict]}06`, border: `1px solid ${VERDICT_COLOR[r.verdict]}20`, borderTop: "none" }}>
                      <div className="grid grid-cols-3 gap-2 text-[9px] font-mono">
                        <div><span className="text-zinc-500">Verdict : </span><span style={{ color: VERDICT_COLOR[r.verdict] }}>{r.verdict}</span></div>
                        <div><span className="text-zinc-500">BLOCK : </span><span className="text-red-400">{(r.blockRate * 100).toFixed(1)}%</span></div>
                        <div><span className="text-zinc-500">HOLD : </span><span className="text-amber-400">{(r.holdRate * 100).toFixed(1)}%</span></div>
                        <div><span className="text-zinc-500">ALLOW : </span><span className="text-emerald-400">{(r.allowRate * 100).toFixed(1)}%</span></div>
                        <div><span className="text-zinc-500">Cohérence moy. : </span><span className="text-blue-400">{(r.avgCoherence * 100).toFixed(2)}%</span></div>
                        <div><span className="text-zinc-500">Capital sauvé : </span><span className="text-purple-400">{r.capitalSaved.toLocaleString()}</span></div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty state */}
        {seedSummaries.length === 0 && !running && (
          <div className="text-center py-8">
            <div className="text-3xl mb-3">🔭</div>
            <div className="font-mono text-sm text-zinc-400 mb-1">Aucun résultat</div>
            <div className="text-[10px] font-mono text-zinc-600">Sélectionnez un scénario et cliquez sur "Run 10 Seeds" pour tester la robustesse statistique du Guard X-108</div>
          </div>
        )}
      </div>
    </div>
  );
}
