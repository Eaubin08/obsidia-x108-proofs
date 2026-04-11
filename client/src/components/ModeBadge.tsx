/**
 * ModeBadge — signalisation systématique du régime opératoire
 *
 * 4 modes :
 *  - DEMO     : données simulées, non persistées (Flash Crash, Stress Lab démo)
 *  - SIMU     : run Simuler gouverné, persisté en DB, non exécutoire
 *  - LIVE     : décisions WebSocket réelles (TradingWorld / BankWorld / EcomWorld)
 *  - FALLBACK : Python hors ligne, moteur local actif
 *
 * Usage :
 *   <ModeBadge mode="SIMU" />
 *   <ModeBadge mode="LIVE" detail="WebSocket actif" />
 *   <ModeBadge mode="FALLBACK" detail="Python hors ligne" />
 */

import React from "react";

export type OperatingMode = "DEMO" | "SIMU" | "LIVE" | "FALLBACK";

interface ModeBadgeProps {
  mode: OperatingMode;
  detail?: string;
  /** Affichage compact (sans label texte) — pour les espaces restreints */
  compact?: boolean;
}

const MODE_CONFIG: Record<OperatingMode, {
  label: string;
  color: string;
  bg: string;
  border: string;
  dot: string;
  pulse?: boolean;
}> = {
  LIVE: {
    label: "LIVE",
    color: "#4ade80",
    bg: "oklch(0.10 0.04 145 / 0.6)",
    border: "#4ade8044",
    dot: "#4ade80",
    pulse: true,
  },
  SIMU: {
    label: "SIMU",
    color: "oklch(0.65 0.18 220)",
    bg: "oklch(0.10 0.04 220 / 0.6)",
    border: "oklch(0.65 0.18 220 / 0.3)",
    dot: "oklch(0.65 0.18 220)",
  },
  DEMO: {
    label: "DEMO",
    color: "oklch(0.75 0.18 75)",
    bg: "oklch(0.10 0.04 75 / 0.6)",
    border: "oklch(0.75 0.18 75 / 0.3)",
    dot: "oklch(0.75 0.18 75)",
  },
  FALLBACK: {
    label: "FALLBACK",
    color: "#f87171",
    bg: "oklch(0.10 0.04 25 / 0.6)",
    border: "#f8717144",
    dot: "#f87171",
    pulse: true,
  },
};

export default function ModeBadge({ mode, detail, compact = false }: ModeBadgeProps) {
  const cfg = MODE_CONFIG[mode];

  return (
    <div
      className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded font-mono"
      style={{
        background: cfg.bg,
        border: `1px solid ${cfg.border}`,
        fontSize: "10px",
        letterSpacing: "0.08em",
      }}
    >
      {/* Point de statut */}
      <span
        style={{
          display: "inline-block",
          width: 6,
          height: 6,
          borderRadius: "50%",
          background: cfg.dot,
          flexShrink: 0,
          boxShadow: cfg.pulse ? `0 0 6px ${cfg.dot}` : "none",
        }}
      />

      {/* Label */}
      <span className="font-bold" style={{ color: cfg.color }}>
        MODE : {cfg.label}
      </span>

      {/* Détail optionnel */}
      {!compact && detail && (
        <span style={{ color: "oklch(0.45 0.01 240)", marginLeft: 2 }}>
          — {detail}
        </span>
      )}
    </div>
  );
}

/**
 * ModeBadgeBar — barre de badges utilisée en haut de page
 * Affiche le mode principal + un contexte optionnel (version moteur, domaine, etc.)
 */
export function ModeBadgeBar({
  mode,
  detail,
  right,
}: {
  mode: OperatingMode;
  detail?: string;
  right?: React.ReactNode;
}) {
  return (
    <div
      className="flex items-center justify-between px-4 py-1.5"
      style={{
        background: "oklch(0.08 0.01 240)",
        borderBottom: "1px solid oklch(0.14 0.01 240)",
        minHeight: 32,
      }}
    >
      <ModeBadge mode={mode} detail={detail} />
      {right && (
        <div className="text-[9px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>
          {right}
        </div>
      )}
    </div>
  );
}
