/**
 * ReplayPanel — panneau de replay d'un run OS4 V2
 * Permet de rejouer un run passé dans Future avec les mêmes paramètres
 * Utilisé dans Past (détail run) et Future (compare)
 */
import React, { useState } from "react";
import { Link } from "wouter";
import type { CanonicalEnvelope } from "./DecisionEnvelopeCard";

export interface RunRecord {
  run_id: string;
  domain: "trading" | "bank" | "ecom";
  scenario_name: string;
  timestamp: number;
  duration_ms?: number;
  envelope?: CanonicalEnvelope;
  agent_count?: number;
  proof_complete: boolean;
  tags?: string[];
}

interface ReplayPanelProps {
  run: RunRecord;
  onReplay?: (run: RunRecord) => void;
  onCompare?: (run: RunRecord) => void;
  futureLink?: string;
  className?: string;
}

const DOMAIN_CFG = {
  trading: { icon: "📈", accent: "oklch(0.72 0.18 145)" },
  bank:    { icon: "🏦", accent: "oklch(0.65 0.18 240)" },
  ecom:    { icon: "🛒", accent: "oklch(0.72 0.18 45)"  },
};

export default function ReplayPanel({ run, onReplay, onCompare, futureLink, className = "" }: ReplayPanelProps) {
  const [expanded, setExpanded] = useState(false);
  const dom = DOMAIN_CFG[run.domain];
  const date = new Date(run.timestamp);
  const dateStr = date.toLocaleDateString("fr-FR", { day: "2-digit", month: "short" });
  const timeStr = date.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
  const gate = run.envelope?.x108_gate;
  const gateColor = gate === "ALLOW" ? "oklch(0.72 0.18 145)" : gate === "HOLD" ? "oklch(0.72 0.18 45)" : gate === "BLOCK" ? "oklch(0.65 0.25 25)" : "oklch(0.40 0.01 240)";

  return (
    <div className={`rounded overflow-hidden ${className}`}
      style={{ background: "oklch(0.115 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
      {/* Header */}
      <button
        onClick={() => setExpanded(v => !v)}
        className="w-full flex items-center gap-2 px-3 py-2 text-left"
      >
        <span className="text-[10px]">{dom.icon}</span>
        <div className="flex-1 min-w-0">
          <div className="text-[10px] font-mono font-bold truncate" style={{ color: "oklch(0.80 0.01 240)" }}>
            {run.scenario_name}
          </div>
          <div className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>
            {dateStr} {timeStr} · {run.domain}
            {run.duration_ms && ` · ${run.duration_ms}ms`}
          </div>
        </div>
        {gate && (
          <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded shrink-0"
            style={{ background: `${gateColor}15`, border: `1px solid ${gateColor}40`, color: gateColor }}>
            {gate}
          </span>
        )}
        <span className="text-[9px] font-mono shrink-0"
          style={{ color: run.proof_complete ? "oklch(0.72 0.18 145)" : "oklch(0.65 0.25 25)" }}>
          {run.proof_complete ? "✓" : "⚠"}
        </span>
        <span className="text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>{expanded ? "▲" : "▼"}</span>
      </button>

      {/* Tags */}
      {run.tags && run.tags.length > 0 && (
        <div className="px-3 pb-1.5 flex gap-1 flex-wrap">
          {run.tags.map(t => (
            <span key={t} className="text-[8px] font-mono px-1 rounded"
              style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.50 0.01 240)" }}>{t}</span>
          ))}
        </div>
      )}

      {/* Expanded */}
      {expanded && (
        <div className="px-3 pb-3 flex flex-col gap-2" style={{ borderTop: "1px solid oklch(0.16 0.01 240)" }}>
          {/* Envelope summary */}
          {run.envelope && (
            <div className="pt-2 grid grid-cols-2 gap-1 text-[8px] font-mono">
              {[
                { k: "verdict",    v: run.envelope.market_verdict },
                { k: "confidence", v: `${Math.round(run.envelope.confidence * 100)}%` },
                { k: "contradictions", v: String(run.envelope.contradictions) },
                { k: "unknowns",   v: String(run.envelope.unknowns) },
                { k: "reason",     v: run.envelope.reason_code },
                { k: "agents",     v: String(run.agent_count ?? "—") },
              ].map(({ k, v }) => (
                <div key={k}>
                  <span style={{ color: "oklch(0.40 0.01 240)" }}>{k} </span>
                  <span style={{ color: "oklch(0.65 0.01 240)" }}>{v}</span>
                </div>
              ))}
            </div>
          )}
          {/* run_id */}
          <div className="text-[8px] font-mono" style={{ color: "oklch(0.38 0.01 240)" }}>
            run_id : {run.run_id.slice(0, 20)}…
          </div>
          {/* Actions */}
          <div className="flex gap-2 flex-wrap mt-1">
            {onReplay && (
              <button
                onClick={() => onReplay(run)}
                className="px-2 py-1 rounded text-[9px] font-mono font-bold"
                style={{ background: dom.accent + "18", border: `1px solid ${dom.accent}40`, color: dom.accent }}>
                ▶ Replay dans Future
              </button>
            )}
            {onCompare && (
              <button
                onClick={() => onCompare(run)}
                className="px-2 py-1 rounded text-[9px] font-mono"
                style={{ background: "oklch(0.14 0.01 240)", border: "1px solid oklch(0.22 0.01 240)", color: "oklch(0.60 0.01 240)" }}>
                Compare
              </button>
            )}
            {futureLink && (
              <Link href={futureLink}>
                <button className="px-2 py-1 rounded text-[9px] font-mono"
                  style={{ background: "oklch(0.14 0.01 240)", border: "1px solid oklch(0.22 0.01 240)", color: "oklch(0.60 0.01 240)" }}>
                  Open in Future
                </button>
              </Link>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
