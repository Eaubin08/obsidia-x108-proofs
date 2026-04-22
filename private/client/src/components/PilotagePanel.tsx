import React from "react";

interface PilotagePanelProps {
  domain: "trading" | "bank" | "ecom";
  onRerun?: () => void;
  onReset?: () => void;
  onCompare?: () => void;
  loading?: boolean;
  pythonAvailable?: boolean;
  mode?: "real" | "fallback";
  showMode?: boolean;
  showCompare?: boolean;
  compareActive?: boolean;
  extraControls?: React.ReactNode;
  scenarioLabel?: string;
}

const DOMAIN_COLOR: Record<string, string> = {
  trading: "oklch(0.65 0.18 220)",
  bank:    "oklch(0.75 0.18 75)",
  ecom:    "oklch(0.72 0.18 145)",
};

export default function PilotagePanel({
  domain,
  onRerun,
  onReset,
  onCompare,
  loading,
  pythonAvailable,
  mode,
  showMode = true,
  showCompare = false,
  compareActive = false,
  extraControls,
  scenarioLabel,
}: PilotagePanelProps) {
  const accent = DOMAIN_COLOR[domain] ?? "oklch(0.65 0.18 220)";

  return (
    <div className="rounded p-3" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] font-mono uppercase tracking-widest" style={{ color: accent }}>
          Pilotage
        </span>
        {scenarioLabel && (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded" style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.55 0.01 240)", border: "1px solid oklch(0.22 0.01 240)" }}>
            {scenarioLabel}
          </span>
        )}
      </div>

      <div className="flex items-center gap-2 flex-wrap">
        {/* Rerun */}
        {onRerun && (
          <button
            onClick={onRerun}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded font-mono text-xs font-bold transition-all"
            style={{ background: loading ? "oklch(0.14 0.01 240)" : `${accent}22`, border: `1px solid ${accent}55`, color: loading ? "oklch(0.45 0.01 240)" : accent }}
          >
            {loading ? "⟳ En cours…" : "⟳ Relancer"}
          </button>
        )}

        {/* Reset */}
        {onReset && (
          <button
            onClick={onReset}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded font-mono text-xs transition-all"
            style={{ background: "oklch(0.14 0.01 240)", border: "1px solid oklch(0.22 0.01 240)", color: "oklch(0.55 0.01 240)" }}
          >
            ↺ Reset
          </button>
        )}

        {/* Compare */}
        {showCompare && onCompare && (
          <button
            onClick={onCompare}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded font-mono text-xs transition-all"
            style={{
              background: compareActive ? "oklch(0.65 0.18 220 / 0.15)" : "oklch(0.14 0.01 240)",
              border: `1px solid ${compareActive ? "oklch(0.65 0.18 220 / 0.5)" : "oklch(0.22 0.01 240)"}`,
              color: compareActive ? "oklch(0.65 0.18 220)" : "oklch(0.55 0.01 240)",
            }}
          >
            ⇄ Comparer
          </button>
        )}

        {/* Contrôles supplémentaires */}
        {extraControls}

        {/* Mode Python / Fallback */}
        {showMode && (
          <div className="ml-auto flex items-center gap-1.5">
            <div
              className="w-1.5 h-1.5 rounded-full"
              style={{ background: pythonAvailable ? "#4ade80" : "oklch(0.75 0.18 75)" }}
            />
            <span className="text-[10px] font-mono" style={{ color: pythonAvailable ? "#4ade80" : "oklch(0.75 0.18 75)" }}>
              {pythonAvailable === undefined ? "…" : pythonAvailable ? "Python UP" : "Fallback local"}
            </span>
          </div>
        )}
      </div>

      {/* Mode brut vs gouverné */}
      {mode && (
        <div className="mt-2 flex items-center gap-2">
          <span className="text-[10px] text-muted-foreground font-mono">Mode :</span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded font-bold" style={{
            background: mode === "real" ? "oklch(0.72 0.18 145 / 0.15)" : "oklch(0.75 0.18 75 / 0.15)",
            color: mode === "real" ? "#4ade80" : "oklch(0.75 0.18 75)",
            border: `1px solid ${mode === "real" ? "oklch(0.72 0.18 145 / 0.4)" : "oklch(0.75 0.18 75 / 0.4)"}`,
          }}>
            {mode === "real" ? "⚡ Réel (Python)" : "⚠ Fallback (local)"}
          </span>
        </div>
      )}
    </div>
  );
}
