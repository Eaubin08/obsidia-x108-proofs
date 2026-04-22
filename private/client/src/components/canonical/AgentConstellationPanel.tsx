/**
 * AgentConstellationPanel — vue constellation agentique OS4 V2
 * Organise les agents par couche canonique : Observation → Interpretation → Contradiction → Aggregation → Governance → Proof
 * Règle UX : jamais une liste brute — toujours par rôle fonctionnel
 */
import React, { useState } from "react";

// ─── Types ────────────────────────────────────────────────────────────────────

export type AgentLayer = "Observation" | "Interpretation" | "Contradiction" | "Aggregation" | "Governance" | "Proof";

export interface AgentData {
  name: string;
  layer: AgentLayer;
  claim?: string;
  confidence?: number;
  severity_hint?: "S1" | "S2" | "S3" | "S4";
  proposed_verdict?: string;
  contradictions?: number;
  unknowns?: number;
  risk_flags?: string[];
  evidence_count?: number;
  status?: "active" | "silent" | "anomalous" | "low-confidence";
  trace_covered?: boolean;
}

export interface AggregationData {
  market_verdict: string;
  confidence: number;
  contradictions_count: number;
  unknowns_count: number;
  risk_flags: string[];
  evidence_refs: number;
  dominant_contributors: string[];
}

interface AgentConstellationPanelProps {
  agents: AgentData[];
  aggregation?: AggregationData;
  domain: "trading" | "bank" | "ecom";
  /** Vue compacte (résumé par couche) ou développée (chaque agent) */
  defaultExpanded?: boolean;
  className?: string;
}

// ─── Config couches ───────────────────────────────────────────────────────────

const LAYER_CFG: Record<AgentLayer, { icon: string; color: string; question: string }> = {
  Observation:    { icon: "👁", color: "oklch(0.65 0.18 240)", question: "Que voit-on ?" },
  Interpretation: { icon: "🧠", color: "oklch(0.72 0.18 145)", question: "Comment lire la situation ?" },
  Contradiction:  { icon: "⚡", color: "oklch(0.72 0.18 45)",  question: "Est-ce cohérent ?" },
  Aggregation:    { icon: "🔗", color: "#a78bfa",               question: "Quelle voix unique ?" },
  Governance:     { icon: "🛡️", color: "oklch(0.72 0.18 145)", question: "Que tranche X-108 ?" },
  Proof:          { icon: "🔐", color: "oklch(0.60 0.15 290)",  question: "Est-ce traçable ?" },
};

const LAYER_ORDER: AgentLayer[] = ["Observation", "Interpretation", "Contradiction", "Aggregation", "Governance", "Proof"];

// ─── AgentRow ─────────────────────────────────────────────────────────────────

function AgentRow({ agent }: { agent: AgentData }) {
  const cfg = LAYER_CFG[agent.layer];
  const confPct = agent.confidence !== undefined ? Math.round(agent.confidence * 100) : null;
  const statusColor = {
    active:         "oklch(0.72 0.18 145)",
    silent:         "oklch(0.45 0.01 240)",
    anomalous:      "oklch(0.65 0.25 25)",
    "low-confidence": "oklch(0.72 0.18 45)",
  }[agent.status ?? "active"];

  return (
    <div className="flex items-start gap-2 px-3 py-1.5 rounded"
      style={{ background: "oklch(0.115 0.01 240)", border: "1px solid oklch(0.16 0.01 240)" }}>
      {/* Statut dot */}
      <div className="w-1.5 h-1.5 rounded-full mt-1.5 shrink-0" style={{ background: statusColor }} />
      {/* Contenu */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-[10px] font-mono font-bold" style={{ color: cfg.color }}>{agent.name}</span>
          {agent.proposed_verdict && (
            <span className="text-[9px] font-mono px-1 py-0.5 rounded"
              style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.65 0.01 240)" }}>
              {agent.proposed_verdict}
            </span>
          )}
          {confPct !== null && (
            <span className="text-[9px] font-mono" style={{ color: confPct >= 70 ? "oklch(0.72 0.18 145)" : confPct >= 50 ? "oklch(0.72 0.18 45)" : "oklch(0.65 0.25 25)" }}>
              {confPct}%
            </span>
          )}
          {agent.severity_hint && (
            <span className="text-[8px] font-mono" style={{ color: "oklch(0.55 0.01 240)" }}>{agent.severity_hint}</span>
          )}
        </div>
        {agent.claim && (
          <div className="text-[8px] font-mono mt-0.5 truncate" style={{ color: "oklch(0.50 0.01 240)" }}>{agent.claim}</div>
        )}
        {/* Flags */}
        {((agent.contradictions ?? 0) > 0 || (agent.unknowns ?? 0) > 0 || (agent.risk_flags?.length ?? 0) > 0) && (
          <div className="flex gap-1.5 mt-0.5 flex-wrap">
            {(agent.contradictions ?? 0) > 0 && (
              <span className="text-[8px] font-mono" style={{ color: "oklch(0.72 0.18 45)" }}>⚠ {agent.contradictions} contr.</span>
            )}
            {(agent.unknowns ?? 0) > 0 && (
              <span className="text-[8px] font-mono" style={{ color: "oklch(0.65 0.18 240)" }}>? {agent.unknowns} unk.</span>
            )}
            {agent.risk_flags?.slice(0, 2).map(f => (
              <span key={f} className="text-[8px] font-mono px-1 rounded"
                style={{ background: "oklch(0.65 0.25 25 / 0.12)", color: "oklch(0.65 0.25 25)" }}>{f}</span>
            ))}
          </div>
        )}
      </div>
      {/* Evidence count */}
      {agent.evidence_count !== undefined && (
        <span className="text-[8px] font-mono shrink-0" style={{ color: "oklch(0.40 0.01 240)" }}>
          {agent.evidence_count} ev.
        </span>
      )}
    </div>
  );
}

// ─── AgentRoleGroup ───────────────────────────────────────────────────────────

function AgentRoleGroup({ layer, agents, expanded, onToggle }: {
  layer: AgentLayer;
  agents: AgentData[];
  expanded: boolean;
  onToggle: () => void;
}) {
  const cfg = LAYER_CFG[layer];
  const active = agents.filter(a => a.status !== "silent").length;
  const avgConf = agents.length > 0
    ? agents.reduce((s, a) => s + (a.confidence ?? 0), 0) / agents.length
    : 0;
  const hasConflict = agents.some(a => (a.contradictions ?? 0) > 0);
  const topFlags = Array.from(new Set(agents.flatMap(a => a.risk_flags ?? []))).slice(0, 2);

  return (
    <div className="rounded overflow-hidden" style={{ border: "1px solid oklch(0.16 0.01 240)" }}>
      {/* Header couche */}
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-2 px-3 py-2 text-left"
        style={{ background: "oklch(0.12 0.01 240)" }}
      >
        <span className="text-[11px]">{cfg.icon}</span>
        <span className="text-[10px] font-mono font-bold" style={{ color: cfg.color }}>{layer}</span>
        <span className="text-[9px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>({agents.length})</span>
        {/* Stats compactes */}
        <div className="flex items-center gap-2 ml-auto text-[8px] font-mono">
          <span style={{ color: "oklch(0.55 0.01 240)" }}>
            {active}/{agents.length} actifs
          </span>
          {avgConf > 0 && (
            <span style={{ color: avgConf >= 0.7 ? "oklch(0.72 0.18 145)" : avgConf >= 0.5 ? "oklch(0.72 0.18 45)" : "oklch(0.65 0.25 25)" }}>
              avg {Math.round(avgConf * 100)}%
            </span>
          )}
          {hasConflict && <span style={{ color: "oklch(0.72 0.18 45)" }}>⚠ conflit</span>}
          {topFlags.map(f => (
            <span key={f} className="px-1 rounded" style={{ background: "oklch(0.65 0.25 25 / 0.12)", color: "oklch(0.65 0.25 25)" }}>{f}</span>
          ))}
        </div>
        <span className="text-[9px] ml-2" style={{ color: "oklch(0.40 0.01 240)" }}>{expanded ? "▲" : "▼"}</span>
      </button>
      {/* Question */}
      {!expanded && (
        <div className="px-3 py-1 text-[8px] font-mono" style={{ color: "oklch(0.38 0.01 240)", background: "oklch(0.105 0.01 240)" }}>
          {cfg.question}
        </div>
      )}
      {/* Agents développés */}
      {expanded && (
        <div className="p-2 flex flex-col gap-1" style={{ background: "oklch(0.10 0.01 240)" }}>
          {agents.length === 0 ? (
            <div className="text-[9px] font-mono text-center py-2" style={{ color: "oklch(0.35 0.01 240)" }}>
              Aucun agent dans cette couche
            </div>
          ) : (
            agents.map(a => <AgentRow key={a.name} agent={a} />)
          )}
        </div>
      )}
    </div>
  );
}

// ─── AggregationSummaryBlock ──────────────────────────────────────────────────

function AggregationSummaryBlock({ agg }: { agg: AggregationData }) {
  return (
    <div className="rounded p-3" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
      <div className="text-[9px] font-mono font-bold mb-2" style={{ color: "#a78bfa" }}>
        🔗 Aggregation — voix unique du domaine
      </div>
      <div className="flex flex-wrap gap-3 text-[9px] font-mono">
        <div>
          <span style={{ color: "oklch(0.45 0.01 240)" }}>verdict </span>
          <span style={{ color: "oklch(0.80 0.01 240)" }}>{agg.market_verdict}</span>
        </div>
        <div>
          <span style={{ color: "oklch(0.45 0.01 240)" }}>conf </span>
          <span style={{ color: agg.confidence >= 0.7 ? "oklch(0.72 0.18 145)" : "oklch(0.72 0.18 45)" }}>
            {Math.round(agg.confidence * 100)}%
          </span>
        </div>
        {agg.contradictions_count > 0 && (
          <div>
            <span style={{ color: "oklch(0.45 0.01 240)" }}>contradictions </span>
            <span style={{ color: "oklch(0.72 0.18 45)" }}>{agg.contradictions_count}</span>
          </div>
        )}
        {agg.unknowns_count > 0 && (
          <div>
            <span style={{ color: "oklch(0.45 0.01 240)" }}>unknowns </span>
            <span style={{ color: "oklch(0.65 0.18 240)" }}>{agg.unknowns_count}</span>
          </div>
        )}
        <div>
          <span style={{ color: "oklch(0.45 0.01 240)" }}>evidence </span>
          <span style={{ color: "oklch(0.55 0.01 240)" }}>{agg.evidence_refs}</span>
        </div>
      </div>
      {agg.dominant_contributors.length > 0 && (
        <div className="mt-2 text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>
          Top contributors : {agg.dominant_contributors.slice(0, 3).join(", ")}
        </div>
      )}
    </div>
  );
}

// ─── AgentConstellationPanel ──────────────────────────────────────────────────

export default function AgentConstellationPanel({
  agents,
  aggregation,
  domain,
  defaultExpanded = false,
  className = "",
}: AgentConstellationPanelProps) {
  const [expandedLayers, setExpandedLayers] = useState<Set<AgentLayer>>(
    defaultExpanded ? new Set(LAYER_ORDER) : new Set()
  );

  const toggleLayer = (layer: AgentLayer) => {
    setExpandedLayers(prev => {
      const next = new Set(prev);
      if (next.has(layer)) next.delete(layer);
      else next.add(layer);
      return next;
    });
  };

  const byLayer = (layer: AgentLayer) => agents.filter(a => a.layer === layer);

  // ─── Phrase d'interprétation constellation ─────────────────────────────────────────────────────
  const silentCount = agents.filter(a => a.status === "silent").length;
  const anomalousCount = agents.filter(a => a.status === "anomalous").length;
  const lowConfCount = agents.filter(a => a.status === "low-confidence").length;
  const activeCount = agents.filter(a => a.status !== "silent").length;
  const constellationStatus = anomalousCount > 0 ? "critical" : silentCount > agents.length * 0.3 ? "watch" : "normal";
  const constellationStatusColor = constellationStatus === "normal" ? "oklch(0.72 0.18 145)" : constellationStatus === "watch" ? "oklch(0.72 0.18 45)" : "oklch(0.65 0.25 25)";
  const constellationPhrase = anomalousCount > 0
    ? `${anomalousCount} agent(s) anomal(aux) détecté(s) — inspection immédiate recommandée.`
    : silentCount > 0
    ? `${silentCount} agent(s) silencieux sur ${agents.length} — couverture réduite.`
    : `${activeCount}/${agents.length} agents actifs — constellation opérationnelle.`;
  const constellationAction = anomalousCount > 0
    ? "Vérifier les agents anomaleux dans Control"
    : silentCount > 0
    ? "Investiguer les agents silencieux"
    : "Continuer la surveillance";

  return (
    <div className={`flex flex-col gap-1.5 ${className}`}>
      {LAYER_ORDER.map(layer => (
        <React.Fragment key={layer}>
          {layer === "Aggregation" && aggregation ? (
            <AggregationSummaryBlock agg={aggregation} />
          ) : (
            <AgentRoleGroup
              layer={layer}
              agents={byLayer(layer)}
              expanded={expandedLayers.has(layer)}
              onToggle={() => toggleLayer(layer)}
            />
          )}
        </React.Fragment>
      ))}

      {/* Phrase d'interprétation (spec : titre métier + phrase + statut + action) */}
      {agents.length > 0 && (
        <div className="rounded p-2 mt-1" style={{ background: `${constellationStatusColor}0a`, border: `1px solid ${constellationStatusColor}33` }}>
          <div className="flex items-center justify-between mb-1">
            <span className="text-[8px] font-mono font-bold" style={{ color: constellationStatusColor }}>
              {constellationStatus === "normal" ? "Constellation opérationnelle" : constellationStatus === "watch" ? "Surveillance requise" : "Anomalie détectée"}
            </span>
            <span className="text-[7px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>{activeCount}/{agents.length} actifs</span>
          </div>
          <div className="text-[8px] font-mono" style={{ color: "oklch(0.55 0.01 240)" }}>{constellationPhrase}</div>
          <div className="mt-1 text-[7px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>→ {constellationAction}</div>
        </div>
      )}
    </div>
  );
}

// ─── Exports nommés ───────────────────────────────────────────────────────────
export { AgentRow, AgentRoleGroup, AggregationSummaryBlock };
export type { AgentConstellationPanelProps };
