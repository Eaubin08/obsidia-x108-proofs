import React from "react";

export interface ProjectionScenario {
  label: string;
  probability: number;   // 0–1
  outcome: "continuation" | "degradation" | "recovery" | "neutral";
  description: string;
}

interface ProjectionPanelProps {
  domain: "trading" | "bank" | "ecom";
  scenarios?: ProjectionScenario[];
  horizon?: string;   // ex: "5 min", "24h", "7j"
  loading?: boolean;
}

const OUTCOME_CONFIG = {
  continuation: { color: "#4ade80", label: "Continuation", icon: "→" },
  degradation:  { color: "#f87171", label: "Dégradation",  icon: "↘" },
  recovery:     { color: "oklch(0.75 0.18 75)", label: "Récupération", icon: "↗" },
  neutral:      { color: "oklch(0.55 0.01 240)", label: "Neutre", icon: "—" },
};

const DOMAIN_COLOR: Record<string, string> = {
  trading: "oklch(0.65 0.18 220)",
  bank:    "oklch(0.75 0.18 75)",
  ecom:    "oklch(0.72 0.18 145)",
};

const DEFAULT_SCENARIOS: Record<string, ProjectionScenario[]> = {
  trading: [
    { label: "Tendance maintenue", probability: 0.55, outcome: "continuation", description: "Momentum actuel conservé, volatilité stable" },
    { label: "Correction technique", probability: 0.30, outcome: "degradation", description: "Retour vers moyenne mobile 20 périodes" },
    { label: "Rebond rapide", probability: 0.15, outcome: "recovery", description: "Acheteurs institutionnels entrent en jeu" },
  ],
  bank: [
    { label: "Transaction validée", probability: 0.65, outcome: "continuation", description: "Contreparties vérifiées, limites respectées" },
    { label: "Délai réglementaire", probability: 0.25, outcome: "neutral", description: "Validation KYC/AML en attente" },
    { label: "Risque de contrepartie", probability: 0.10, outcome: "degradation", description: "Score de crédit dégradé détecté" },
  ],
  ecom: [
    { label: "Conversion optimale", probability: 0.60, outcome: "continuation", description: "Panier moyen stable, taux de rebond faible" },
    { label: "Friction checkout", probability: 0.25, outcome: "degradation", description: "Abandon panier probable si délai > 3s" },
    { label: "Upsell activé", probability: 0.15, outcome: "recovery", description: "Recommandation moteur active" },
  ],
};

export default function ProjectionPanel({ domain, scenarios, horizon, loading }: ProjectionPanelProps) {
  const accent = DOMAIN_COLOR[domain] ?? "oklch(0.65 0.18 220)";
  const items = scenarios ?? DEFAULT_SCENARIOS[domain] ?? [];

  return (
    <div className="rounded p-3" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-[10px] font-mono uppercase tracking-widest" style={{ color: accent }}>
          Projection — Futur
        </span>
        {horizon && (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded" style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.55 0.01 240)", border: "1px solid oklch(0.22 0.01 240)" }}>
            Horizon : {horizon}
          </span>
        )}
      </div>

      {loading ? (
        <div className="space-y-2 animate-pulse">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-10 rounded" style={{ background: "oklch(0.14 0.01 240)" }} />
          ))}
        </div>
      ) : (
        <div className="space-y-2">
          {items.map((sc, i) => {
            const cfg = OUTCOME_CONFIG[sc.outcome];
            const pct = Math.round(sc.probability * 100);
            return (
              <div key={i} className="rounded p-2 relative overflow-hidden" style={{ background: "oklch(0.13 0.01 240)", border: `1px solid ${cfg.color}22` }}>
                {/* Barre de probabilité */}
                <div
                  className="absolute left-0 top-0 bottom-0 rounded-l"
                  style={{ width: `${pct}%`, background: `${cfg.color}12`, transition: "width 0.5s ease" }}
                />
                <div className="relative flex items-center gap-2">
                  <span className="font-mono text-sm font-bold flex-shrink-0" style={{ color: cfg.color }}>{cfg.icon}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-bold" style={{ color: cfg.color }}>{sc.label}</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded ml-auto flex-shrink-0" style={{ background: `${cfg.color}20`, color: cfg.color }}>
                        {pct}%
                      </span>
                    </div>
                    <div className="text-[10px] text-muted-foreground font-mono mt-0.5 truncate">{sc.description}</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      <div className="mt-2 text-[9px] text-muted-foreground font-mono text-right">
        Projection probabiliste · non contractuelle
      </div>
    </div>
  );
}
