/**
 * HealthMatrix — matrice de santé système OS4 V2
 * Affiche les 4 dimensions : Agent Health / Proof Coverage / Decision Quality / Risk Exposure
 * Utilisée dans Control
 */
import React from "react";

export interface HealthDimension {
  label: string;
  score: number; // 0-100
  trend: "up" | "down" | "stable";
  details?: string;
  critical?: boolean;
}

export interface HealthMatrixData {
  agent_health: HealthDimension;
  proof_coverage: HealthDimension;
  decision_quality: HealthDimension;
  risk_exposure: HealthDimension;
  domain: "trading" | "bank" | "ecom";
  last_updated?: number;
}

interface HealthMatrixProps {
  data: HealthMatrixData;
  className?: string;
}

const DOMAIN_ACCENT = {
  trading: "oklch(0.72 0.18 145)",
  bank:    "oklch(0.65 0.18 240)",
  ecom:    "oklch(0.72 0.18 45)",
};

function scoreColor(score: number, invert = false): string {
  const s = invert ? 100 - score : score;
  if (s >= 80) return "oklch(0.72 0.18 145)";
  if (s >= 60) return "oklch(0.72 0.18 45)";
  if (s >= 40) return "oklch(0.65 0.25 25)";
  return "oklch(0.60 0.30 15)";
}

function ScoreBar({ score, invert = false }: { score: number; invert?: boolean }) {
  const color = scoreColor(score, invert);
  return (
    <div className="w-full h-1 rounded-full overflow-hidden" style={{ background: "oklch(0.18 0.01 240)" }}>
      <div className="h-full rounded-full transition-all" style={{ width: `${score}%`, background: color }} />
    </div>
  );
}

function DimensionCard({ dim, invert = false }: { dim: HealthDimension; invert?: boolean }) {
  const color = scoreColor(dim.score, invert);
  const trendIcon = dim.trend === "up" ? "↑" : dim.trend === "down" ? "↓" : "→";
  const trendColor = dim.trend === "up" ? "oklch(0.72 0.18 145)" : dim.trend === "down" ? "oklch(0.65 0.25 25)" : "oklch(0.50 0.01 240)";

  return (
    <div className="rounded p-3" style={{
      background: dim.critical ? "oklch(0.65 0.25 25 / 0.08)" : "oklch(0.12 0.01 240)",
      border: `1px solid ${dim.critical ? "oklch(0.65 0.25 25 / 0.30)" : "oklch(0.18 0.01 240)"}`,
    }}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-[9px] font-mono" style={{ color: "oklch(0.55 0.01 240)" }}>{dim.label}</span>
        <div className="flex items-center gap-1">
          <span className="text-[9px] font-mono" style={{ color: trendColor }}>{trendIcon}</span>
          <span className="text-[13px] font-mono font-bold" style={{ color }}>{dim.score}</span>
        </div>
      </div>
      <ScoreBar score={dim.score} invert={invert} />
      {dim.details && (
        <div className="mt-1.5 text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>{dim.details}</div>
      )}
      {dim.critical && (
        <div className="mt-1 text-[8px] font-mono font-bold" style={{ color: "oklch(0.65 0.25 25)" }}>⚠ Attention requise</div>
      )}
    </div>
  );
}

export default function HealthMatrix({ data, className = "" }: HealthMatrixProps) {
  const accent = DOMAIN_ACCENT[data.domain];
  const dimensions = [
    { dim: data.agent_health,     invert: false },
    { dim: data.proof_coverage,   invert: false },
    { dim: data.decision_quality, invert: false },
    { dim: data.risk_exposure,    invert: true  },
  ];

  const overallScore = Math.round(
    (data.agent_health.score + data.proof_coverage.score + data.decision_quality.score + (100 - data.risk_exposure.score)) / 4
  );

  return (
    <div className={`rounded overflow-hidden ${className}`}
      style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2"
        style={{ borderBottom: "1px solid oklch(0.16 0.01 240)", background: "oklch(0.12 0.01 240)" }}>
        <span className="text-[10px] font-mono font-bold" style={{ color: accent }}>
          Health Matrix — {data.domain.charAt(0).toUpperCase() + data.domain.slice(1)}
        </span>
        <div className="flex items-center gap-2">
          <span className="text-[9px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>Overall</span>
          <span className="text-[13px] font-mono font-bold" style={{ color: scoreColor(overallScore) }}>{overallScore}</span>
          {data.last_updated && (
            <span className="text-[8px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>
              {new Date(data.last_updated).toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>
      {/* Grid 2x2 */}
      <div className="grid grid-cols-2 gap-2 p-3">
        {dimensions.map(({ dim, invert }) => (
          <DimensionCard key={dim.label} dim={dim} invert={invert} />
        ))}
      </div>

      {/* ─── Phrase d'interprétation (spec : titre métier + phrase + statut + action) ──────────────────────────── */}
      {(() => {
        const status = overallScore >= 80 ? "normal" : overallScore >= 60 ? "watch" : "critical";
        const statusColor = status === "normal" ? "oklch(0.72 0.18 145)" : status === "watch" ? "oklch(0.72 0.18 45)" : "oklch(0.65 0.25 25)";
        const statusLabel = status === "normal" ? "Système stable" : status === "watch" ? "Surveillance requise" : "Intervention requise";
        const criticalDims = dimensions.filter(({ dim, invert }) => {
          const s = invert ? 100 - dim.score : dim.score;
          return s < 60;
        });
        const phrase = criticalDims.length === 0
          ? `Health à ${overallScore}% — tous les indicateurs dans les normes, aucune action immédiate.`
          : `Health à ${overallScore}% — ${criticalDims.map(d => d.dim.label).join(", ")} sous le seuil critique. Vérification recommandée.`;
        const action = criticalDims.length === 0
          ? "Continuer la surveillance normale"
          : `Inspecter ${criticalDims[0].dim.label} dans Control`;
        return (
          <div className="px-3 pb-3">
            <div className="rounded p-2" style={{ background: `${statusColor}0a`, border: `1px solid ${statusColor}33` }}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-[8px] font-mono font-bold" style={{ color: statusColor }}>{statusLabel}</span>
                <span className="text-[7px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>Overall {overallScore}/100</span>
              </div>
              <div className="text-[8px] font-mono" style={{ color: "oklch(0.55 0.01 240)" }}>{phrase}</div>
              <div className="mt-1 text-[7px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>→ {action}</div>
            </div>
          </div>
        );
      })()}
    </div>
  );
}
