/**
 * IncidentCard — carte incident/alerte OS4 V2
 * Utilisée dans Control (alertes actives) et Past (incidents historiques)
 */
import React, { useState } from "react";
import { Link } from "wouter";

export interface IncidentData {
  id: string;
  title: string;
  domain: "trading" | "bank" | "ecom" | "system";
  severity: "S1" | "S2" | "S3" | "S4";
  status: "active" | "investigating" | "resolved" | "suppressed";
  trigger: string;
  x108_response?: "BLOCK" | "HOLD" | "ALLOW";
  decision_id?: string;
  timestamp: number;
  resolved_at?: number;
  description?: string;
  next_action?: string;
}

interface IncidentCardProps {
  incident: IncidentData;
  onAcknowledge?: (id: string) => void;
  pastLink?: string;
  className?: string;
}

const SEV_CFG = {
  S1: { color: "oklch(0.72 0.18 145)", bg: "oklch(0.72 0.18 145 / 0.08)", label: "S1 — Info" },
  S2: { color: "oklch(0.72 0.18 45)",  bg: "oklch(0.72 0.18 45 / 0.08)",  label: "S2 — Warn" },
  S3: { color: "oklch(0.65 0.25 25)",  bg: "oklch(0.65 0.25 25 / 0.08)",  label: "S3 — Error" },
  S4: { color: "oklch(0.60 0.30 15)",  bg: "oklch(0.60 0.30 15 / 0.12)",  label: "S4 — Critical" },
};

const STATUS_CFG = {
  active:        { color: "oklch(0.65 0.25 25)",  label: "ACTIVE" },
  investigating: { color: "oklch(0.72 0.18 45)",  label: "INVESTIGATING" },
  resolved:      { color: "oklch(0.72 0.18 145)", label: "RESOLVED" },
  suppressed:    { color: "oklch(0.40 0.01 240)", label: "SUPPRESSED" },
};

const DOMAIN_ICON = { trading: "📈", bank: "🏦", ecom: "🛒", system: "⚙️" };

export default function IncidentCard({ incident: inc, onAcknowledge, pastLink, className = "" }: IncidentCardProps) {
  const [expanded, setExpanded] = useState(false);
  const sev = SEV_CFG[inc.severity];
  const status = STATUS_CFG[inc.status];
  const elapsed = Date.now() - inc.timestamp;
  const elapsedStr = elapsed < 60000
    ? `${Math.round(elapsed / 1000)}s`
    : elapsed < 3600000
    ? `${Math.round(elapsed / 60000)}m`
    : `${Math.round(elapsed / 3600000)}h`;

  return (
    <div className={`rounded overflow-hidden ${className}`}
      style={{ background: sev.bg, border: `1px solid ${sev.color}30` }}>
      {/* Header */}
      <button
        onClick={() => setExpanded(v => !v)}
        className="w-full flex items-center gap-2 px-3 py-2 text-left"
      >
        <span className="text-[10px]">{DOMAIN_ICON[inc.domain]}</span>
        <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded"
          style={{ background: `${sev.color}20`, color: sev.color }}>{inc.severity}</span>
        <span className="text-[10px] font-mono font-bold flex-1 truncate" style={{ color: "oklch(0.85 0.01 240)" }}>
          {inc.title}
        </span>
        <span className="text-[9px] font-mono shrink-0" style={{ color: status.color }}>{status.label}</span>
        <span className="text-[8px] font-mono shrink-0" style={{ color: "oklch(0.40 0.01 240)" }}>{elapsedStr}</span>
        <span className="text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>{expanded ? "▲" : "▼"}</span>
      </button>

      {/* Trigger */}
      <div className="px-3 pb-1.5 text-[8px] font-mono" style={{ color: "oklch(0.50 0.01 240)" }}>
        Trigger : {inc.trigger}
        {inc.x108_response && (
          <span className="ml-2 font-bold" style={{ color: sev.color }}>→ X-108 {inc.x108_response}</span>
        )}
      </div>

      {/* Expanded */}
      {expanded && (
        <div className="px-3 pb-3 flex flex-col gap-2" style={{ borderTop: "1px solid oklch(0.16 0.01 240)" }}>
          {inc.description && (
            <p className="text-[9px] font-mono pt-2" style={{ color: "oklch(0.60 0.01 240)" }}>{inc.description}</p>
          )}
          {inc.next_action && (
            <div className="text-[9px] font-mono" style={{ color: "oklch(0.72 0.18 145)" }}>
              → {inc.next_action}
            </div>
          )}
          {inc.decision_id && (
            <div className="text-[8px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>
              decision_id : {inc.decision_id.slice(0, 16)}…
            </div>
          )}
          {/* Actions */}
          <div className="flex gap-2 flex-wrap mt-1">
            {inc.status === "active" && onAcknowledge && (
              <button
                onClick={() => onAcknowledge(inc.id)}
                className="px-2 py-1 rounded text-[9px] font-mono font-bold"
                style={{ background: sev.color + "20", border: `1px solid ${sev.color}50`, color: sev.color }}>
                Acknowledge
              </button>
            )}
            {pastLink && (
              <Link href={pastLink}>
                <button className="px-2 py-1 rounded text-[9px] font-mono"
                  style={{ background: "oklch(0.14 0.01 240)", border: "1px solid oklch(0.22 0.01 240)", color: "oklch(0.60 0.01 240)" }}>
                  View in Past
                </button>
              </Link>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
