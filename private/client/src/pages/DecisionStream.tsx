/**
 * DecisionStream.tsx — OS4 v18
 * Governance Reactor — live decision stream from all worlds.
 * Displays: timestamp | world | agent proposal | engine metrics | X-108 decision | proof hash
 * Powered by WebSocket /ws/decisions — real-time, no polling.
 */
import React, { useState, useRef, useEffect } from "react";
import { Link } from "wouter";
import { useDecisionStream } from "@/hooks/useDecisionStream";
import type { LiveDecisionEvent } from "@/hooks/useDecisionStream";

// ─── Constants ────────────────────────────────────────────────────────────────
const DECISION_COLORS = {
  BLOCK: { bg: "oklch(0.18 0.06 15)", text: "#f87171", border: "oklch(0.35 0.12 15 / 0.6)" },
  HOLD:  { bg: "oklch(0.18 0.06 60)", text: "#fbbf24", border: "oklch(0.35 0.12 60 / 0.6)" },
  ALLOW: { bg: "oklch(0.14 0.04 145)", text: "#4ade80", border: "oklch(0.35 0.10 145 / 0.6)" },
};

const DOMAIN_COLORS: Record<string, string> = {
  TRADING: "#60a5fa",
  BANKING: "#a78bfa",
  ECOMMERCE: "#34d399",
};

const REGIME_COLORS: Record<string, string> = {
  CRISIS: "#f87171",
  VOLATILE: "#fbbf24",
  BULL: "#4ade80",
  NEUTRAL: "oklch(0.55 0.01 240)",
};

function fmtTime(ts: number): string {
  return new Date(ts).toLocaleTimeString("en-US", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function fmtMs(ts: number): string {
  return new Date(ts).toLocaleTimeString("en-US", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit", fractionalSecondDigits: 3 });
}

// ─── Single Event Row ─────────────────────────────────────────────────────────
function EventRow({ event, index }: { event: LiveDecisionEvent; index: number }) {
  const dc = DECISION_COLORS[event.guard.decision];
  const domainColor = DOMAIN_COLORS[event.domain] ?? "#888";
  const regimeColor = REGIME_COLORS[event.world.regime] ?? "oklch(0.55 0.01 240)";
  const isNew = index === 0;

  return (
    <div
      className="grid font-mono text-[11px] py-2 px-3 border-b"
      style={{
        gridTemplateColumns: "90px 80px 1fr 160px 90px 100px",
        gap: "8px",
        alignItems: "center",
        borderColor: "oklch(0.16 0.01 240)",
        background: isNew ? "oklch(0.13 0.02 145 / 0.15)" : "transparent",
        transition: "background 0.5s ease",
      }}
    >
      {/* Timestamp */}
      <div style={{ color: "oklch(0.40 0.01 240)" }}>{fmtTime(event.timestamp)}</div>

      {/* World / Domain */}
      <div className="flex items-center gap-1.5">
        <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ background: domainColor }} />
        <span style={{ color: domainColor }}>{event.domain.slice(0, 5)}</span>
      </div>

      {/* Agent Proposal */}
      <div className="truncate" style={{ color: "oklch(0.80 0.01 240)" }}>
        <span style={{ color: "oklch(0.45 0.01 240)" }}>{event.agent.id.split("_").slice(0, 2).join("_")} </span>
        <span className="font-bold">{event.agent.proposal}</span>
      </div>

      {/* Engine Metrics */}
      <div className="flex items-center gap-2">
        <span style={{ color: "oklch(0.45 0.01 240)" }}>coh</span>
        <span style={{ color: event.engine.coherence < 0.30 ? "#f87171" : event.engine.coherence < 0.60 ? "#fbbf24" : "#4ade80" }}>
          {event.engine.coherence.toFixed(2)}
        </span>
        <span style={{ color: "oklch(0.45 0.01 240)" }}>vol</span>
        <span style={{ color: event.world.volatility > 0.45 ? "#f87171" : event.world.volatility > 0.30 ? "#fbbf24" : "oklch(0.55 0.01 240)" }}>
          {(event.world.volatility * 100).toFixed(0)}%
        </span>
        <span style={{ color: regimeColor, fontSize: "9px" }}>{event.world.regime}</span>
      </div>

      {/* X-108 Decision */}
      <div
        className="flex items-center justify-center rounded px-2 py-0.5 font-bold text-[10px]"
        style={{ background: dc.bg, color: dc.text, border: `1px solid ${dc.border}` }}
      >
        {event.guard.decision}
      </div>

      {/* Proof Hash */}
      <div className="text-right" style={{ color: "oklch(0.35 0.01 240)", fontFamily: "monospace" }}>
        0x{event.proof.hash.slice(0, 8)}
      </div>
    </div>
  );
}

// ─── Stats Bar ────────────────────────────────────────────────────────────────
function StatsBar({ stats, connected, latency }: {
  stats: { total: number; block: number; hold: number; allow: number; blockRate: number; holdRate: number; allowRate: number };
  connected: boolean;
  latency: number;
}) {
  return (
    <div className="flex items-center gap-6 px-4 py-3 border-b font-mono text-xs" style={{ borderColor: "oklch(0.20 0.01 240)", background: "oklch(0.11 0.01 240)" }}>
      {/* WS Status */}
      <div className="flex items-center gap-1.5">
        <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: connected ? "#4ade80" : "#f87171" }} />
        <span style={{ color: connected ? "#4ade80" : "#f87171" }}>{connected ? "LIVE" : "RECONNECTING"}</span>
        {connected && latency > 0 && <span style={{ color: "oklch(0.40 0.01 240)" }}>{latency}ms</span>}
      </div>

      <div className="w-px h-4" style={{ background: "oklch(0.20 0.01 240)" }} />

      {/* Total */}
      <div>
        <span style={{ color: "oklch(0.45 0.01 240)" }}>total </span>
        <span className="font-bold text-foreground">{stats.total}</span>
      </div>

      {/* Block */}
      <div>
        <span style={{ color: "oklch(0.45 0.01 240)" }}>block </span>
        <span className="font-bold" style={{ color: "#f87171" }}>{stats.block}</span>
        <span style={{ color: "oklch(0.35 0.01 240)" }}> ({(stats.blockRate * 100).toFixed(1)}%)</span>
      </div>

      {/* Hold */}
      <div>
        <span style={{ color: "oklch(0.45 0.01 240)" }}>hold </span>
        <span className="font-bold" style={{ color: "#fbbf24" }}>{stats.hold}</span>
        <span style={{ color: "oklch(0.35 0.01 240)" }}> ({(stats.holdRate * 100).toFixed(1)}%)</span>
      </div>

      {/* Allow */}
      <div>
        <span style={{ color: "oklch(0.45 0.01 240)" }}>allow </span>
        <span className="font-bold" style={{ color: "#4ade80" }}>{stats.allow}</span>
        <span style={{ color: "oklch(0.35 0.01 240)" }}> ({(stats.allowRate * 100).toFixed(1)}%)</span>
      </div>

      {/* Rate bar */}
      <div className="flex-1 flex items-center gap-1 ml-2">
        <div className="flex-1 h-1.5 rounded-full overflow-hidden flex" style={{ background: "oklch(0.16 0.01 240)" }}>
          <div style={{ width: `${stats.blockRate * 100}%`, background: "#f87171" }} />
          <div style={{ width: `${stats.holdRate * 100}%`, background: "#fbbf24" }} />
          <div style={{ width: `${stats.allowRate * 100}%`, background: "#4ade80" }} />
        </div>
      </div>
    </div>
  );
}

// ─── Detail Panel ─────────────────────────────────────────────────────────────
function DetailPanel({ event }: { event: LiveDecisionEvent | null }) {
  if (!event) {
    return (
      <div className="flex items-center justify-center h-full" style={{ color: "oklch(0.35 0.01 240)" }}>
        <span className="font-mono text-xs">Click an event to inspect</span>
      </div>
    );
  }

  const dc = DECISION_COLORS[event.guard.decision];

  return (
    <div className="p-4 font-mono text-xs flex flex-col gap-4 overflow-auto">
      {/* Header */}
      <div>
        <div className="text-[9px] uppercase tracking-widest mb-1" style={{ color: "oklch(0.45 0.01 240)" }}>Event ID</div>
        <div style={{ color: "oklch(0.60 0.01 240)" }}>{event.id}</div>
        <div className="mt-1" style={{ color: "oklch(0.40 0.01 240)" }}>{fmtMs(event.timestamp)}</div>
      </div>

      {/* World */}
      <div>
        <div className="text-[9px] uppercase tracking-widest mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>World State</div>
        <div className="grid grid-cols-2 gap-1">
          <span style={{ color: "oklch(0.45 0.01 240)" }}>domain</span>
          <span style={{ color: DOMAIN_COLORS[event.domain] ?? "#888" }}>{event.domain}</span>
          <span style={{ color: "oklch(0.45 0.01 240)" }}>regime</span>
          <span style={{ color: REGIME_COLORS[event.world.regime] ?? "oklch(0.55 0.01 240)" }}>{event.world.regime}</span>
          <span style={{ color: "oklch(0.45 0.01 240)" }}>volatility</span>
          <span style={{ color: event.world.volatility > 0.45 ? "#f87171" : "#fbbf24" }}>{(event.world.volatility * 100).toFixed(2)}%</span>
          <span style={{ color: "oklch(0.45 0.01 240)" }}>liquidity</span>
          <span style={{ color: event.world.liquidity > 0.6 ? "#4ade80" : "#fbbf24" }}>{(event.world.liquidity * 100).toFixed(1)}%</span>
          {event.world.price && <>
            <span style={{ color: "oklch(0.45 0.01 240)" }}>price</span>
            <span className="text-foreground">${event.world.price.toLocaleString()}</span>
          </>}
        </div>
      </div>

      {/* Agent */}
      <div>
        <div className="text-[9px] uppercase tracking-widest mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>Agent</div>
        <div className="grid grid-cols-2 gap-1">
          <span style={{ color: "oklch(0.45 0.01 240)" }}>id</span>
          <span className="text-foreground">{event.agent.id}</span>
          <span style={{ color: "oklch(0.45 0.01 240)" }}>proposal</span>
          <span className="font-bold text-foreground">{event.agent.proposal}</span>
          {event.agent.amount && <>
            <span style={{ color: "oklch(0.45 0.01 240)" }}>amount</span>
            <span className="text-foreground">${event.agent.amount.toLocaleString()}</span>
          </>}
        </div>
      </div>

      {/* Engine */}
      <div>
        <div className="text-[9px] uppercase tracking-widest mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>Engine Metrics</div>
        <div className="grid grid-cols-2 gap-1">
          <span style={{ color: "oklch(0.45 0.01 240)" }}>coherence</span>
          <span style={{ color: event.engine.coherence < 0.30 ? "#f87171" : event.engine.coherence < 0.60 ? "#fbbf24" : "#4ade80" }}>
            {event.engine.coherence.toFixed(4)}
          </span>
          <span style={{ color: "oklch(0.45 0.01 240)" }}>risk</span>
          <span style={{ color: event.engine.risk > 0.70 ? "#f87171" : "#fbbf24" }}>{event.engine.risk.toFixed(4)}</span>
          <span style={{ color: "oklch(0.45 0.01 240)" }}>state_ok</span>
          <span style={{ color: event.engine.stateConsistency ? "#4ade80" : "#f87171" }}>
            {event.engine.stateConsistency ? "true" : "false"}
          </span>
        </div>
      </div>

      {/* Guard X-108 */}
      <div>
        <div className="text-[9px] uppercase tracking-widest mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>Guard X-108</div>
        <div
          className="rounded px-3 py-2 mb-2 font-bold text-sm text-center"
          style={{ background: dc.bg, color: dc.text, border: `1px solid ${dc.border}` }}
        >
          {event.guard.decision}
        </div>
        <div style={{ color: "oklch(0.55 0.01 240)", lineHeight: "1.5" }}>{event.guard.reason}</div>
        {event.guard.holdDuration && (
          <div className="mt-1" style={{ color: "#fbbf24" }}>τ = {event.guard.holdDuration}s</div>
        )}
      </div>

      {/* Proof */}
      <div>
        <div className="text-[9px] uppercase tracking-widest mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>Proof</div>
        <div className="grid grid-cols-2 gap-1">
          <span style={{ color: "oklch(0.45 0.01 240)" }}>hash</span>
          <span style={{ color: "oklch(0.55 0.01 240)" }}>0x{event.proof.hash}</span>
          <span style={{ color: "oklch(0.45 0.01 240)" }}>lean4</span>
          <span style={{ color: event.proof.lean4 ? "#4ade80" : "#f87171" }}>{event.proof.lean4 ? "✓" : "✗"}</span>
          <span style={{ color: "oklch(0.45 0.01 240)" }}>tla+</span>
          <span style={{ color: event.proof.tlaPlus ? "#4ade80" : "#f87171" }}>{event.proof.tlaPlus ? "✓" : "✗"}</span>
          <span style={{ color: "oklch(0.45 0.01 240)" }}>merkle</span>
          <span style={{ color: "oklch(0.40 0.01 240)" }}>{event.proof.merkleLeaf.slice(0, 12)}…</span>
        </div>
      </div>
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────
export default function DecisionStreamPage() {
  const { events, stats, connected, latency } = useDecisionStream();
  const [selected, setSelected] = useState<LiveDecisionEvent | null>(null);
  const [filter, setFilter] = useState<"ALL" | "BLOCK" | "HOLD" | "ALLOW">("ALL");
  const [domainFilter, setDomainFilter] = useState<"ALL" | "TRADING" | "BANKING" | "ECOMMERCE">("ALL");
  const [paused, setPaused] = useState(false);
  const [frozenEvents, setFrozenEvents] = useState<LiveDecisionEvent[]>([]);
  const listRef = useRef<HTMLDivElement>(null);

  // Freeze/unfreeze stream
  useEffect(() => {
    if (!paused) {
      setFrozenEvents([]);
    }
  }, [paused]);

  const displayEvents = paused ? frozenEvents : events;

  const filtered = displayEvents.filter(e => {
    if (filter !== "ALL" && e.guard.decision !== filter) return false;
    if (domainFilter !== "ALL" && e.domain !== domainFilter) return false;
    return true;
  });

  const handlePause = () => {
    if (!paused) setFrozenEvents([...events]);
    setPaused(p => !p);
  };

  return (
    <div className="flex flex-col" style={{ height: "calc(100vh - 100px)" }}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b" style={{ borderColor: "oklch(0.20 0.01 240)" }}>
        <div>
          <div className="text-[9px] font-mono tracking-[0.3em] uppercase mb-0.5" style={{ color: "oklch(0.72 0.18 145)" }}>
            Obsidia Labs — OS4
          </div>
          <h1 className="font-mono font-bold text-lg text-foreground">
            Decision Stream
            <span className="ml-3 text-xs font-normal" style={{ color: "oklch(0.55 0.01 240)" }}>
              Governance Reactor — All Worlds
            </span>
          </h1>
        </div>

        <div className="flex items-center gap-3">
          {/* Domain filter */}
          {(["ALL", "TRADING", "BANKING", "ECOMMERCE"] as const).map(d => (
            <button
              key={d}
              onClick={() => setDomainFilter(d)}
              className="px-2 py-1 rounded font-mono text-[10px]"
              style={{
                background: domainFilter === d ? (d === "ALL" ? "oklch(0.20 0.01 240)" : `${DOMAIN_COLORS[d] ?? "#888"}22`) : "transparent",
                color: domainFilter === d ? (d === "ALL" ? "oklch(0.80 0.01 240)" : DOMAIN_COLORS[d]) : "oklch(0.40 0.01 240)",
                border: `1px solid ${domainFilter === d ? (d === "ALL" ? "oklch(0.30 0.01 240)" : `${DOMAIN_COLORS[d] ?? "#888"}44`) : "oklch(0.20 0.01 240)"}`,
              }}
            >
              {d.slice(0, 5)}
            </button>
          ))}

          <div className="w-px h-5" style={{ background: "oklch(0.20 0.01 240)" }} />

          {/* Decision filter */}
          {(["ALL", "BLOCK", "HOLD", "ALLOW"] as const).map(d => (
            <button
              key={d}
              onClick={() => setFilter(d)}
              className="px-2 py-1 rounded font-mono text-[10px]"
              style={{
                background: filter === d ? (d === "ALL" ? "oklch(0.20 0.01 240)" : DECISION_COLORS[d as keyof typeof DECISION_COLORS]?.bg ?? "transparent") : "transparent",
                color: filter === d ? (d === "ALL" ? "oklch(0.80 0.01 240)" : DECISION_COLORS[d as keyof typeof DECISION_COLORS]?.text ?? "#888") : "oklch(0.40 0.01 240)",
                border: `1px solid ${filter === d ? (d === "ALL" ? "oklch(0.30 0.01 240)" : DECISION_COLORS[d as keyof typeof DECISION_COLORS]?.border ?? "oklch(0.20 0.01 240)") : "oklch(0.20 0.01 240)"}`,
              }}
            >
              {d}
            </button>
          ))}

          <div className="w-px h-5" style={{ background: "oklch(0.20 0.01 240)" }} />

          {/* Pause */}
          <button
            onClick={handlePause}
            className="px-3 py-1 rounded font-mono text-[10px]"
            style={{
              background: paused ? "oklch(0.18 0.06 60)" : "oklch(0.14 0.01 240)",
              color: paused ? "#fbbf24" : "oklch(0.55 0.01 240)",
              border: `1px solid ${paused ? "oklch(0.35 0.12 60 / 0.5)" : "oklch(0.22 0.01 240)"}`,
            }}
          >
            {paused ? "▶ RESUME" : "⏸ PAUSE"}
          </button>

          <Link href="/control" className="font-mono text-[10px]" style={{ color: "oklch(0.45 0.01 240)" }}>
            ← Control Tower
          </Link>
        </div>
      </div>

      {/* Stats bar */}
      <StatsBar stats={stats} connected={connected} latency={latency} />

      {/* Column headers */}
      <div
        className="grid font-mono text-[9px] uppercase tracking-widest px-3 py-1.5 border-b"
        style={{
          gridTemplateColumns: "90px 80px 1fr 160px 90px 100px",
          gap: "8px",
          borderColor: "oklch(0.16 0.01 240)",
          background: "oklch(0.11 0.01 240)",
          color: "oklch(0.35 0.01 240)",
        }}
      >
        <div>Timestamp</div>
        <div>World</div>
        <div>Agent Proposal</div>
        <div>Engine Metrics</div>
        <div>X-108</div>
        <div className="text-right">Proof Hash</div>
      </div>

      {/* Main layout: stream + detail panel */}
      <div className="flex flex-1 overflow-hidden">
        {/* Event stream */}
        <div
          ref={listRef}
          className="flex-1 overflow-y-auto"
          style={{ minWidth: 0 }}
        >
          {filtered.length === 0 ? (
            <div className="flex items-center justify-center h-32">
              <span className="font-mono text-xs" style={{ color: "oklch(0.35 0.01 240)" }}>
                {connected ? "Waiting for events…" : "Connecting to WebSocket…"}
              </span>
            </div>
          ) : (
            filtered.map((event, i) => (
              <div
                key={event.id}
                onClick={() => setSelected(event)}
                style={{ cursor: "pointer", background: selected?.id === event.id ? "oklch(0.14 0.02 240)" : undefined }}
              >
                <EventRow event={event} index={i} />
              </div>
            ))
          )}
        </div>

        {/* Detail panel */}
        <div
          className="border-l overflow-y-auto"
          style={{
            width: "280px",
            flexShrink: 0,
            borderColor: "oklch(0.18 0.01 240)",
            background: "oklch(0.105 0.01 240)",
          }}
        >
          <div className="px-3 py-2 border-b font-mono text-[9px] uppercase tracking-widest" style={{ borderColor: "oklch(0.18 0.01 240)", color: "oklch(0.35 0.01 240)" }}>
            Event Inspector
          </div>
          <DetailPanel event={selected} />
        </div>
      </div>
    </div>
  );
}
