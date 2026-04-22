import React, { useState } from "react";
import { DecisionBadge, HashDisplay, X108Gate } from "./MetricCard";

interface DecisionTicket {
  intent_id: string;
  domain: string;
  decision: "ALLOW" | "HOLD" | "BLOCK";
  reasons: string[];
  thresholds: Record<string, number>;
  x108: {
    tau: number;
    elapsed: number;
    irr: boolean;
    gate_active: boolean;
  };
  audit: {
    hash_prev: string;
    hash_now: string;
    merkle_root: string;
    anchor_ref?: string;
    ts_utc: string;
  };
  replay_ref?: string;
}

interface DecisionTicketPanelProps {
  ticket: DecisionTicket;
  className?: string;
}

export function DecisionTicketPanel({ ticket, className = "" }: DecisionTicketPanelProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className={`panel text-xs ${className}`}>
      {/* Header */}
      <div className="panel-header">
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground font-mono" style={{ fontSize: "0.65rem" }}>
            DECISION TICKET
          </span>
          <DecisionBadge decision={ticket.decision} />
          <span className="text-muted-foreground font-mono" style={{ fontSize: "0.6rem" }}>
            {ticket.domain.toUpperCase()}
          </span>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-muted-foreground hover:text-foreground transition-colors text-xs"
        >
          {expanded ? "▲" : "▼"}
        </button>
      </div>

      {/* Summary row */}
      <div className="p-2 flex flex-wrap gap-3 items-center">
        <X108Gate
          tau={ticket.x108.tau}
          elapsed={ticket.x108.elapsed}
          irr={ticket.x108.irr}
          gateActive={ticket.x108.gate_active}
        />
        <div className="flex flex-col gap-0.5">
          {ticket.reasons.map((r, i) => (
            <div key={i} className="text-muted-foreground" style={{ fontSize: "0.65rem" }}>
              {r}
            </div>
          ))}
        </div>
      </div>

      {/* Expanded audit trail */}
      {expanded && (
        <div className="border-t border-border p-2 space-y-1.5">
          <div className="text-muted-foreground uppercase tracking-wider mb-1" style={{ fontSize: "0.6rem" }}>
            Audit Trail
          </div>
          <HashDisplay label="hash_prev" hash={ticket.audit.hash_prev} />
          <HashDisplay label="hash_now" hash={ticket.audit.hash_now} />
          <HashDisplay label="merkle_root" hash={ticket.audit.merkle_root} />
          {ticket.audit.anchor_ref && (
            <div className="flex items-center gap-2 text-xs">
              <span className="text-muted-foreground uppercase tracking-wider" style={{ fontSize: "0.65rem" }}>anchor_ref</span>
              <span className="os4-hash font-mono">{ticket.audit.anchor_ref}</span>
            </div>
          )}
          <div className="flex items-center gap-2 text-xs">
            <span className="text-muted-foreground uppercase tracking-wider" style={{ fontSize: "0.65rem" }}>ts_utc</span>
            <span className="font-mono text-foreground">{ticket.audit.ts_utc}</span>
          </div>
          {ticket.replay_ref && (
            <div className="flex items-center gap-2 text-xs">
              <span className="text-muted-foreground uppercase tracking-wider" style={{ fontSize: "0.65rem" }}>replay_ref</span>
              <span className="font-mono text-foreground">{ticket.replay_ref}</span>
            </div>
          )}

          {/* Thresholds */}
          {Object.keys(ticket.thresholds).length > 0 && (
            <div>
              <div className="text-muted-foreground uppercase tracking-wider mb-1 mt-2" style={{ fontSize: "0.6rem" }}>
                Thresholds
              </div>
              <div className="grid grid-cols-2 gap-1">
                {Object.entries(ticket.thresholds).map(([k, v]) => (
                  <div key={k} className="flex justify-between gap-2">
                    <span className="text-muted-foreground font-mono" style={{ fontSize: "0.65rem" }}>{k}</span>
                    <span className="font-mono text-foreground" style={{ fontSize: "0.65rem" }}>{v}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex items-center gap-2 text-xs mt-1">
            <span className="text-muted-foreground uppercase tracking-wider" style={{ fontSize: "0.65rem" }}>intent_id</span>
            <span className="os4-hash font-mono">{ticket.intent_id}</span>
          </div>
        </div>
      )}
    </div>
  );
}
