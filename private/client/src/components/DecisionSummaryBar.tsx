import React from "react";

export type GateVerdict = "ALLOW" | "HOLD" | "BLOCK" | null;

interface DecisionSummaryBarProps {
  gate: GateVerdict;
  verdict?: string;        // verdict métier ex: "PRICE_ADJUST", "RISK_HOLD"
  source?: string;         // "python" | "os4_local_fallback" | "db_real"
  severity?: string;       // "S0" | "S1" | "S2" | "S3" | "S4"
  reason?: string;         // raison principale
  loading?: boolean;
  domain?: string;
}

const GATE_CONFIG: Record<NonNullable<GateVerdict>, { label: string; bg: string; border: string; color: string; icon: string }> = {
  ALLOW: { label: "AUTORISÉ", bg: "oklch(0.12 0.04 145)", border: "oklch(0.72 0.18 145 / 0.5)", color: "#4ade80", icon: "✓" },
  HOLD:  { label: "EN ATTENTE", bg: "oklch(0.14 0.06 75)", border: "oklch(0.75 0.18 75 / 0.5)", color: "oklch(0.75 0.18 75)", icon: "⏸" },
  BLOCK: { label: "BLOQUÉ", bg: "oklch(0.14 0.06 25)", border: "oklch(0.55 0.18 25 / 0.5)", color: "#f87171", icon: "✕" },
};

const SOURCE_LABEL: Record<string, { label: string; color: string }> = {
  python:             { label: "⚡ python", color: "oklch(0.65 0.18 220)" },
  os4_local_fallback: { label: "⚠ fallback", color: "oklch(0.75 0.18 75)" },
  db_real:            { label: "◉ db", color: "#4ade80" },
  ws_real:            { label: "◉ live", color: "#4ade80" },
  local_sim:          { label: "○ sim", color: "oklch(0.50 0.01 240)" },
};

export default function DecisionSummaryBar({ gate, verdict, source, severity, reason, loading, domain }: DecisionSummaryBarProps) {
  if (loading) {
    return (
      <div className="rounded p-3 flex items-center gap-3 animate-pulse" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
        <div className="w-20 h-8 rounded" style={{ background: "oklch(0.18 0.01 240)" }} />
        <div className="flex-1 h-4 rounded" style={{ background: "oklch(0.18 0.01 240)" }} />
      </div>
    );
  }

  if (!gate) {
    return (
      <div className="rounded p-3 flex items-center gap-3" style={{ background: "oklch(0.10 0.01 240)", border: "1px dashed oklch(0.25 0.01 240)" }}>
        <span className="text-xs font-mono text-muted-foreground">En attente d'une décision…</span>
        {domain && <span className="text-[10px] font-mono px-2 py-0.5 rounded" style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.55 0.01 240)" }}>{domain.toUpperCase()}</span>}
      </div>
    );
  }

  const cfg = GATE_CONFIG[gate];
  const srcCfg = source ? (SOURCE_LABEL[source] ?? { label: source, color: "oklch(0.55 0.01 240)" }) : null;

  return (
    <div className="rounded p-3 flex items-center gap-3 flex-wrap" style={{ background: cfg.bg, border: `1px solid ${cfg.border}` }}>
      {/* Gate principal */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <span className="font-mono font-bold text-xl" style={{ color: cfg.color }}>{cfg.icon}</span>
        <div>
          <div className="font-mono font-bold text-sm leading-tight" style={{ color: cfg.color }}>X-108 {cfg.label}</div>
          {verdict && <div className="text-[10px] font-mono" style={{ color: cfg.color + "99" }}>{verdict}</div>}
        </div>
      </div>

      {/* Séparateur */}
      <div className="w-px h-8 flex-shrink-0" style={{ background: cfg.border }} />

      {/* Raison */}
      {reason && (
        <div className="flex-1 min-w-0">
          <div className="text-[10px] text-muted-foreground font-mono mb-0.5">Raison</div>
          <div className="text-xs font-mono truncate" style={{ color: "oklch(0.75 0.01 240)" }}>{reason}</div>
        </div>
      )}

      {/* Badges droite */}
      <div className="flex items-center gap-2 flex-shrink-0 ml-auto">
        {severity && severity !== "S0" && (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded font-bold" style={{ background: "oklch(0.55 0.18 25 / 0.15)", color: "#f87171", border: "1px solid oklch(0.55 0.18 25 / 0.3)" }}>
            {severity}
          </span>
        )}
        {srcCfg && (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded" style={{ background: "oklch(0.14 0.01 240)", color: srcCfg.color, border: "1px solid oklch(0.22 0.01 240)" }}>
            {srcCfg.label}
          </span>
        )}
        {domain && (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded" style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.55 0.01 240)", border: "1px solid oklch(0.22 0.01 240)" }}>
            {domain.toUpperCase()}
          </span>
        )}
      </div>
    </div>
  );
}
