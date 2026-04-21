import React, { useState } from "react";

// ─── Glossaire Obsidia ────────────────────────────────────────────────────────

export const OBSIDIA_GLOSSARY: Record<string, { short: string; long: string; color?: string }> = {
  "Guard X-108": {
    short: "Moteur de décision qui valide chaque action proposée par un agent.",
    long: "Guard X-108 évalue la cohérence, le risque et les seuils de chaque signal agent. Il peut émettre ALLOW (exécution immédiate), HOLD (attente du temporal lock) ou BLOCK (rejet définitif). C'est le cœur de la gouvernance Obsidia.",
    color: "oklch(0.72 0.18 145)",
  },
  "Temporal Lock": {
    short: "Période de refroidissement empêchant des actions irréversibles trop rapides.",
    long: "Le Temporal Lock impose une durée d'attente (typiquement 10 secondes) avant qu'une action validée par Guard X-108 soit exécutée. Il protège contre les décisions en rafale et les erreurs de timing.",
    color: "oklch(0.60 0.12 200)",
  },
  "ALLOW": {
    short: "Action exécutée immédiatement.",
    long: "Guard X-108 a validé tous les critères : cohérence, risque, seuil. L'action est exécutée sans délai supplémentaire.",
    color: "#4ade80",
  },
  "HOLD": {
    short: "Action valide — en attente du temporal lock.",
    long: "L'action est correcte mais le temporal lock n'a pas encore expiré. Elle sera exécutée automatiquement à la fin de la période de refroidissement.",
    color: "#fbbf24",
  },
  "BLOCK": {
    short: "Action rejetée — risque ou incohérence détectée.",
    long: "Guard X-108 a détecté un risque ou une incohérence. L'action est annulée définitivement. Un audit trail est généré pour traçabilité.",
    color: "#f87171",
  },
  "Merkle Anchor": {
    short: "Empreinte cryptographique de la décision dans un arbre de Merkle.",
    long: "Chaque décision est hashée et ancrée dans un arbre de Merkle. Cela permet de prouver qu'une décision a eu lieu à un instant précis, sans en révéler le contenu. Fondement de la preuve cryptographique Obsidia.",
    color: "#34d399",
  },
  "Coherence": {
    short: "Score de cohérence de l'agent (0 à 1).",
    long: "Mesure la cohérence interne du signal d'un agent par rapport à son historique et aux autres agents. Doit dépasser le seuil minimum (défaut : 0.18) pour que l'action soit autorisée.",
    color: "#a78bfa",
  },
  "Confidence": {
    short: "Niveau de certitude de l'agent sur son signal (0 à 1).",
    long: "Plus la confiance est élevée, plus le signal est fiable. Une confiance faible (<0.3) peut déclencher un HOLD automatique même si la cohérence est suffisante.",
    color: "#f59e0b",
  },
  "Agent Alpha": {
    short: "Agent spécialisé dans le trading de cryptomonnaies.",
    long: "Agent Alpha surveille les marchés BTC/ETH en temps réel. Il génère des signaux BUY/SELL basés sur la volatilité, le volume et les indicateurs de momentum. Ses décisions passent systématiquement par Guard X-108.",
    color: "#3b82f6",
  },
  "Agent Sentinel": {
    short: "Agent spécialisé dans la sécurité bancaire.",
    long: "Agent Sentinel analyse les transactions bancaires pour détecter fraudes, anomalies de conformité et risques de liquidité. Il opère en mode temps réel avec un seuil de cohérence renforcé.",
    color: "#22c55e",
  },
  "Agent Mercury": {
    short: "Agent spécialisé dans l'optimisation e-commerce.",
    long: "Agent Mercury gère les promotions, les prix dynamiques et les alertes de stock. Il détecte les opportunités de demande et les risques de rupture, puis propose des actions validées par Guard X-108.",
    color: "#a855f7",
  },
};

// ─── Composant tooltip ────────────────────────────────────────────────────────

interface ConceptTooltipProps {
  term: string;
  children?: React.ReactNode;
  showIcon?: boolean;
}

export function ConceptTooltip({ term, children, showIcon = true }: ConceptTooltipProps) {
  const [open, setOpen] = useState(false);
  const def = OBSIDIA_GLOSSARY[term];
  const color = def?.color ?? "oklch(0.72 0.18 145)";

  if (!def) return <>{children ?? <span className="font-bold">{term}</span>}</>;

  return (
    <span className="relative inline-block">
      <button
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        className="inline-flex items-center gap-1 font-bold cursor-help"
        style={{ color }}
        aria-label={`Définition : ${term}`}
      >
        {children ?? term}
        {showIcon && (
          <span
            className="inline-flex items-center justify-center rounded-full text-[8px] font-bold"
            style={{
              width: "13px",
              height: "13px",
              background: `${color}22`,
              border: `1px solid ${color}66`,
              color,
              verticalAlign: "middle",
              flexShrink: 0,
            }}
          >
            ?
          </span>
        )}
      </button>
      {open && (
        <span
          className="absolute z-50 left-0 bottom-full mb-2 rounded px-3 py-2.5 shadow-xl"
          style={{
            background: "oklch(0.12 0.01 240)",
            border: `1px solid ${color}55`,
            minWidth: "260px",
            maxWidth: "340px",
            whiteSpace: "normal",
            pointerEvents: "none",
          }}
        >
          <span className="block font-mono font-bold text-xs mb-1" style={{ color }}>
            {term}
          </span>
          <span className="block font-mono text-[10px] mb-1.5" style={{ color: "oklch(0.80 0.01 240)" }}>
            {def.short}
          </span>
          <span className="block font-mono text-[9px]" style={{ color: "oklch(0.55 0.01 240)" }}>
            {def.long}
          </span>
        </span>
      )}
    </span>
  );
}

// ─── Barre de légende inline (pour les pages avec décisions) ─────────────────

export function DecisionLegend({ compact = false }: { compact?: boolean }) {
  const decisions = [
    { key: "ALLOW", color: "#4ade80", icon: "✅", desc: "Exécution immédiate" },
    { key: "HOLD",  color: "#fbbf24", icon: "⏳", desc: "Attente temporal lock" },
    { key: "BLOCK", color: "#f87171", icon: "⛔", desc: "Rejet définitif" },
  ];

  return (
    <div className={`flex items-center gap-${compact ? "3" : "4"} flex-wrap`}>
      {decisions.map(d => (
        <ConceptTooltip key={d.key} term={d.key as keyof typeof OBSIDIA_GLOSSARY} showIcon={false}>
          <span className={`flex items-center gap-1 font-mono font-bold ${compact ? "text-[9px]" : "text-[10px]"}`} style={{ color: d.color }}>
            <span>{d.icon}</span>
            <span>{d.key}</span>
            {!compact && <span className="font-normal" style={{ color: "oklch(0.50 0.01 240)" }}>— {d.desc}</span>}
          </span>
        </ConceptTooltip>
      ))}
      <ConceptTooltip term="Guard X-108" showIcon>
        <span className={`font-mono font-bold ${compact ? "text-[9px]" : "text-[10px]"}`} style={{ color: "oklch(0.72 0.18 145)" }}>
          Guard X-108
        </span>
      </ConceptTooltip>
      <ConceptTooltip term="Temporal Lock" showIcon>
        <span className={`font-mono font-bold ${compact ? "text-[9px]" : "text-[10px]"}`} style={{ color: "oklch(0.60 0.12 200)" }}>
          Temporal Lock
        </span>
      </ConceptTooltip>
    </div>
  );
}
