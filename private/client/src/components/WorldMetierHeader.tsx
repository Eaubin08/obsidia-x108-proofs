import { useState } from "react";
import { useLocation } from "wouter";

// ─── Types ────────────────────────────────────────────────────────────────────

export type WorldMode = "LAB" | "LIVE";

export interface WorldVerdictMetier {
  label: string;        // ex. "Capital protégé", "Ordres bloqués", "Clients protégés"
  value: string | number; // ex. "€ 0 perdu", "3 bloqués", "2 protégés"
  color: string;        // couleur oklch
  icon: string;         // emoji
}

export interface WorldSlider {
  key: string;
  label: string;
  min: number;
  max: number;
  step: number;
  value: number;
  unit: string;
  color: string;
}

export interface WorldMetierHeaderProps {
  domain: "trading" | "bank" | "ecom";
  mode: WorldMode;
  onModeChange?: (mode: WorldMode) => void;
  x108Status: "ONLINE" | "OFFLINE" | "DEGRADED";
  verdicts: WorldVerdictMetier[];
  sliders?: WorldSlider[];
  onSliderChange?: (key: string, value: number) => void;
  lastDecision?: "ALLOW" | "HOLD" | "BLOCK" | null;
  decisionCount?: number;
  className?: string;
}

// ─── Config par domaine ───────────────────────────────────────────────────────

const DOMAIN_CONFIG = {
  trading: {
    label: "Trading",
    icon: "📈",
    accent: "oklch(0.72 0.18 145)",
    bg: "oklch(0.72 0.18 145 / 0.08)",
    border: "oklch(0.72 0.18 145 / 0.25)",
  },
  bank: {
    label: "Banque",
    icon: "🏦",
    accent: "oklch(0.65 0.18 240)",
    bg: "oklch(0.65 0.18 240 / 0.08)",
    border: "oklch(0.65 0.18 240 / 0.25)",
  },
  ecom: {
    label: "E-Commerce",
    icon: "🛒",
    accent: "oklch(0.72 0.18 45)",
    bg: "oklch(0.72 0.18 45 / 0.08)",
    border: "oklch(0.72 0.18 45 / 0.25)",
  },
};

const DECISION_META = {
  ALLOW: { label: "ALLOW", color: "oklch(0.72 0.18 145)", bg: "oklch(0.72 0.18 145 / 0.12)" },
  HOLD:  { label: "HOLD",  color: "oklch(0.72 0.18 45)",  bg: "oklch(0.72 0.18 45 / 0.12)"  },
  BLOCK: { label: "BLOCK", color: "oklch(0.65 0.25 25)",  bg: "oklch(0.65 0.25 25 / 0.12)"  },
};

const X108_META = {
  ONLINE:   { label: "X-108 ONLINE",   color: "oklch(0.72 0.18 145)", dot: "#4ade80" },
  OFFLINE:  { label: "X-108 OFFLINE",  color: "oklch(0.65 0.25 25)",  dot: "#f87171" },
  DEGRADED: { label: "X-108 DÉGRADÉ",  color: "oklch(0.72 0.18 45)",  dot: "#fbbf24" },
};

// ─── Composant ────────────────────────────────────────────────────────────────

export default function WorldMetierHeader({
  domain,
  mode,
  onModeChange,
  x108Status,
  verdicts,
  sliders,
  onSliderChange,
  lastDecision,
  decisionCount,
  className = "",
}: WorldMetierHeaderProps) {
  const [showSliders, setShowSliders] = useState(false);
  const [, navigate] = useLocation();
  const cfg = DOMAIN_CONFIG[domain];
  const x108 = X108_META[x108Status];

  return (
    <div
      className={`rounded-xl px-5 py-4 ${className}`}
      style={{ background: cfg.bg, border: `1px solid ${cfg.border}` }}
    >
      {/* ── Ligne 1 : Identité + Mode + X-108 ── */}
      <div className="flex items-center gap-3 flex-wrap">
        <span className="text-lg">{cfg.icon}</span>
        <span className="font-mono font-bold text-sm" style={{ color: cfg.accent }}>
          {cfg.label}
        </span>

        {/* Mode LAB / LIVE */}
        <div className="flex items-center gap-1 rounded-full px-1 py-0.5" style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
          {(["LAB", "LIVE"] as WorldMode[]).map(m => (
            <button
              key={m}
              onClick={() => onModeChange?.(m)}
              className="px-2.5 py-0.5 rounded-full text-[9px] font-mono font-bold transition-all"
              style={{
                background: mode === m ? (m === "LIVE" ? cfg.accent : "oklch(0.20 0.01 240)") : "transparent",
                color: mode === m ? (m === "LIVE" ? "oklch(0.08 0.01 240)" : "oklch(0.75 0.01 240)") : "oklch(0.40 0.01 240)",
              }}
            >
              {m}
            </button>
          ))}
        </div>

        {/* X-108 statut */}
        <div className="flex items-center gap-1.5 ml-auto">
          <span className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ background: x108.dot }} />
          <span className="text-[9px] font-mono" style={{ color: x108.color }}>{x108.label}</span>
        </div>

        {/* Dernière décision */}
        {lastDecision && (
          <div
            className="px-2 py-0.5 rounded text-[9px] font-mono font-bold"
            style={{ background: DECISION_META[lastDecision].bg, color: DECISION_META[lastDecision].color }}
          >
            {DECISION_META[lastDecision].label}
          </div>
        )}

        {/* Nb décisions */}
        {decisionCount !== undefined && (
          <span className="text-[9px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>
            {decisionCount} décision{decisionCount > 1 ? "s" : ""}
          </span>
        )}
      </div>

      {/* ── Ligne 2 : Verdicts métier ── */}
      {verdicts.length > 0 && (
        <div className="flex flex-wrap gap-3 mt-3">
          {verdicts.map((v, i) => (
            <div key={i} className="flex items-center gap-2 px-3 py-1.5 rounded-lg" style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.16 0.01 240)" }}>
              <span className="text-sm">{v.icon}</span>
              <div>
                <div className="text-[8px] font-mono uppercase tracking-wider" style={{ color: "oklch(0.40 0.01 240)" }}>{v.label}</div>
                <div className="text-[11px] font-mono font-bold" style={{ color: v.color }}>{v.value}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── Ligne 3 : Sliders (dépliables) ── */}
      {sliders && sliders.length > 0 && (
        <div className="mt-3">
          <button
            onClick={() => setShowSliders(s => !s)}
            className="text-[9px] font-mono flex items-center gap-1"
            style={{ color: "oklch(0.45 0.01 240)" }}
          >
            <span>{showSliders ? "▲" : "▼"}</span>
            <span>Paramètres ({sliders.length})</span>
          </button>

          {showSliders && (
            <div className="grid grid-cols-1 gap-2 mt-2 md:grid-cols-2">
              {sliders.map(s => (
                <div key={s.key} className="flex flex-col gap-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[9px] font-mono" style={{ color: "oklch(0.50 0.01 240)" }}>{s.label}</span>
                    <span className="text-[9px] font-mono font-bold" style={{ color: s.color }}>
                      {typeof s.value === "number" && s.step < 1 ? s.value.toFixed(2) : s.value}{s.unit}
                    </span>
                  </div>
                  <input
                    type="range"
                    min={s.min}
                    max={s.max}
                    step={s.step}
                    value={s.value}
                    onChange={e => onSliderChange?.(s.key, parseFloat(e.target.value))}
                    className="w-full h-1 rounded appearance-none cursor-pointer"
                    style={{ accentColor: s.color }}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Ligne 4 : Actions rapides ── */}
      <div className="flex gap-2 mt-3 pt-3 flex-wrap" style={{ borderTop: "1px solid oklch(0.14 0.01 240)" }}>
        <button
          onClick={() => navigate(`/simuler?domain=${domain}&rerun=1`)}
          className="px-2.5 py-1 rounded text-[9px] font-mono font-bold"
          style={{ background: `${cfg.accent}18`, color: cfg.accent, border: `1px solid ${cfg.accent}35` }}
        >
          ↺ Simuler
        </button>
        <button
          onClick={() => navigate("/decision")}
          className="px-2.5 py-1 rounded text-[9px] font-mono font-bold"
          style={{ background: "oklch(0.65 0.18 240 / 0.10)", color: "oklch(0.65 0.18 240)", border: "1px solid oklch(0.65 0.18 240 / 0.30)" }}
        >
          ⚖ Décisions
        </button>
        <button
          onClick={() => navigate("/controle")}
          className="px-2.5 py-1 rounded text-[9px] font-mono font-bold"
          style={{ background: "oklch(0.55 0.12 280 / 0.10)", color: "oklch(0.55 0.12 280)", border: "1px solid oklch(0.55 0.12 280 / 0.30)" }}
        >
          🛡️ Mission Control
        </button>
      </div>
    </div>
  );
}
