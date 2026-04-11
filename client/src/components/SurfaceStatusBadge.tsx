/**
 * SurfaceStatusBadge — badge de statut de surface OS4
 * Affiche REAL / PARTIAL / LOCAL_ONLY / SCAFFOLD
 * avec la source de la valeur (python, db_real, ws_real, os4_local_fallback, preview_local)
 */
import React from "react";

export type SurfaceStatus = "REAL" | "PARTIAL" | "LOCAL_ONLY" | "SCAFFOLD" | "LOADING" | "ERROR";
export type DataSource =
  | "python"
  | "db_real"
  | "ws_real"
  | "os4_local_fallback"
  | "preview_local";

const STATUS_CONFIG: Record<
  SurfaceStatus,
  { label: string; color: string; bg: string; border: string; dot: string }
> = {
  REAL: {
    label: "REAL",
    color: "oklch(0.72 0.18 145)",
    bg: "oklch(0.13 0.06 145 / 0.35)",
    border: "oklch(0.72 0.18 145 / 0.4)",
    dot: "oklch(0.72 0.18 145)",
  },
  PARTIAL: {
    label: "PARTIAL",
    color: "oklch(0.75 0.18 75)",
    bg: "oklch(0.13 0.06 75 / 0.35)",
    border: "oklch(0.75 0.18 75 / 0.4)",
    dot: "oklch(0.75 0.18 75)",
  },
  LOCAL_ONLY: {
    label: "LOCAL",
    color: "oklch(0.65 0.12 240)",
    bg: "oklch(0.13 0.02 240 / 0.35)",
    border: "oklch(0.45 0.05 240 / 0.4)",
    dot: "oklch(0.55 0.05 240)",
  },
  SCAFFOLD: {
    label: "SCAFFOLD",
    color: "oklch(0.55 0.05 240)",
    bg: "oklch(0.11 0.01 240 / 0.35)",
    border: "oklch(0.30 0.01 240 / 0.4)",
    dot: "oklch(0.40 0.01 240)",
  },
  LOADING: {
    label: "...",
    color: "oklch(0.55 0.05 240)",
    bg: "oklch(0.11 0.01 240 / 0.35)",
    border: "oklch(0.25 0.01 240 / 0.4)",
    dot: "oklch(0.40 0.01 240)",
  },
  ERROR: {
    label: "ERROR",
    color: "oklch(0.65 0.20 25)",
    bg: "oklch(0.13 0.08 25 / 0.35)",
    border: "oklch(0.65 0.20 25 / 0.4)",
    dot: "oklch(0.65 0.20 25)",
  },
};

const SOURCE_CONFIG: Record<
  DataSource,
  { label: string; color: string; icon: string }
> = {
  python: {
    label: "python",
    color: "oklch(0.72 0.18 145)",
    icon: "⬡",
  },
  db_real: {
    label: "db_real",
    color: "oklch(0.65 0.18 220)",
    icon: "◈",
  },
  ws_real: {
    label: "ws_real",
    color: "oklch(0.70 0.15 180)",
    icon: "◉",
  },
  os4_local_fallback: {
    label: "os4_fallback",
    color: "oklch(0.75 0.18 75)",
    icon: "⚠",
  },
  preview_local: {
    label: "preview",
    color: "oklch(0.55 0.05 240)",
    icon: "○",
  },
};

interface SurfaceStatusBadgeProps {
  status: SurfaceStatus;
  source?: DataSource;
  /** Afficher en mode compact (badge seul, sans source) */
  compact?: boolean;
  className?: string;
}

export default function SurfaceStatusBadge({
  status,
  source,
  compact = false,
  className = "",
}: SurfaceStatusBadgeProps) {
  const sc = STATUS_CONFIG[status];
  const src = source ? SOURCE_CONFIG[source] : null;

  return (
    <div
      className={`inline-flex items-center gap-1.5 font-mono ${className}`}
      style={{ fontSize: "10px" }}
    >
      {/* Status badge */}
      <span
        className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded"
        style={{
          background: sc.bg,
          border: `1px solid ${sc.border}`,
          color: sc.color,
        }}
      >
        <span
          className="w-1.5 h-1.5 rounded-full inline-block"
          style={{ background: sc.dot }}
        />
        {sc.label}
      </span>

      {/* Source badge */}
      {!compact && src && (
        <span
          className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded"
          style={{
            background: "oklch(0.10 0.01 240 / 0.5)",
            border: "1px solid oklch(0.20 0.01 240 / 0.5)",
            color: src.color,
          }}
        >
          <span>{src.icon}</span>
          <span>{src.label}</span>
        </span>
      )}
    </div>
  );
}

/**
 * SourceTag — affiche uniquement la source d'une valeur individuelle
 * Utiliser inline à côté d'une valeur pour indiquer sa provenance
 */
export function SourceTag({
  source,
  className = "",
}: {
  source: DataSource;
  className?: string;
}) {
  const src = SOURCE_CONFIG[source];
  return (
    <span
      className={`inline-flex items-center gap-0.5 font-mono px-1 py-0.5 rounded ${className}`}
      style={{
        fontSize: "9px",
        background: "oklch(0.10 0.01 240 / 0.5)",
        border: "1px solid oklch(0.20 0.01 240 / 0.4)",
        color: src.color,
      }}
    >
      {src.icon} {src.label}
    </span>
  );
}

/**
 * CanonicalFieldRow — affiche un champ canonique avec sa source
 */
export function CanonicalFieldRow({
  label,
  value,
  source,
  mono = true,
  highlight = false,
}: {
  label: string;
  value: React.ReactNode;
  source?: DataSource;
  mono?: boolean;
  highlight?: boolean;
}) {
  return (
    <div className="flex items-start justify-between gap-2 py-0.5">
      <span
        className="text-[10px] shrink-0"
        style={{ color: "oklch(0.45 0.01 240)", fontFamily: mono ? "monospace" : undefined }}
      >
        {label}
      </span>
      <div className="flex items-center gap-1.5 min-w-0">
        <span
          className={`text-[10px] break-all ${mono ? "font-mono" : ""}`}
          style={{
            color: highlight ? "oklch(0.72 0.18 145)" : "oklch(0.75 0.02 240)",
          }}
        >
          {value ?? "—"}
        </span>
        {source && <SourceTag source={source} />}
      </div>
    </div>
  );
}
