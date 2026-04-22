import React, { useState, useEffect, useRef } from "react";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface StreamEvent {
  id: string;
  timestamp: number;
  world: "trading" | "bank" | "ecom";
  proposal: string;
  guardState: "EVALUATING" | "HOLD" | "BLOCK" | "ALLOW";
  holdRemaining?: number;
  coherence: number;
  decision: "PENDING" | "EXECUTED" | "BLOCKED" | "HELD";
  proofHash?: string;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

let _evId = 0;
function uid() { return `ev-${Date.now()}-${++_evId}`; }

function shortHash(): string {
  return Math.floor(Math.random() * 0xffffffff).toString(16).padStart(8, "0");
}

function randomCoherence(guardState: StreamEvent["guardState"]): number {
  if (guardState === "BLOCK") return 0.10 + Math.random() * 0.25;
  if (guardState === "HOLD") return 0.35 + Math.random() * 0.25;
  return 0.62 + Math.random() * 0.35;
}

const PROPOSALS: Record<StreamEvent["world"], string[]> = {
  trading: ["BUY BTC 0.5", "SELL ETH 2.0", "BUY SPX 100", "SELL AAPL 50", "BUY GOLD 10oz", "SELL EUR/USD 100k"],
  bank: ["TRANSFER 15,000 EUR", "WITHDRAWAL 8,500 EUR", "CREDIT 2,200 EUR", "TRANSFER 450 EUR", "PAYMENT 12,000 EUR"],
  ecom: ["FLASH SALE -30%", "BULK ORDER 500 units", "PRICE CHANGE +15%", "CAMPAIGN LAUNCH 10k€", "RESTOCK 200 units"],
};

function generateEvent(world: StreamEvent["world"]): StreamEvent {
  const proposals = PROPOSALS[world];
  const proposal = proposals[Math.floor(Math.random() * proposals.length)];
  const rand = Math.random();
  const guardState: StreamEvent["guardState"] = rand < 0.12 ? "BLOCK" : rand < 0.22 ? "HOLD" : "ALLOW";
  const coherence = randomCoherence(guardState);
  return {
    id: uid(),
    timestamp: Date.now(),
    world,
    proposal,
    guardState,
    holdRemaining: guardState === "HOLD" ? Math.floor(Math.random() * 9 + 1) : undefined,
    coherence,
    decision: guardState === "BLOCK" ? "BLOCKED" : guardState === "HOLD" ? "HELD" : "EXECUTED",
    proofHash: guardState === "ALLOW" ? shortHash() : undefined,
  };
}

// ─── Component ────────────────────────────────────────────────────────────────

interface DecisionStreamProps {
  maxEvents?: number;
  autoPlay?: boolean;
  tickMs?: number;
}

export default function DecisionStream({ maxEvents = 12, autoPlay = true, tickMs = 2000 }: DecisionStreamProps) {
  const [events, setEvents] = useState<StreamEvent[]>(() => {
    // Seed initial events
    const worlds: StreamEvent["world"][] = ["trading", "bank", "ecom"];
    return Array.from({ length: 6 }, (_, i) => {
      const ev = generateEvent(worlds[i % 3]);
      ev.timestamp = Date.now() - (6 - i) * 3000;
      return ev;
    });
  });
  const [paused, setPaused] = useState(!autoPlay);
  const [activeWorld, setActiveWorld] = useState<StreamEvent["world"] | "all">("all");
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (paused) return;
    const worlds: StreamEvent["world"][] = ["trading", "bank", "ecom"];
    const interval = setInterval(() => {
      const world = worlds[Math.floor(Math.random() * worlds.length)];
      const ev = generateEvent(world);
      setEvents(prev => [ev, ...prev.slice(0, maxEvents - 1)]);
    }, tickMs);
    return () => clearInterval(interval);
  }, [paused, maxEvents, tickMs]);

  const filtered = activeWorld === "all" ? events : events.filter(e => e.world === activeWorld);

  const decisionColor = (d: StreamEvent["decision"]) => {
    if (d === "BLOCKED") return "#f87171";
    if (d === "HELD") return "#fbbf24";
    return "#4ade80";
  };

  const guardColor = (g: StreamEvent["guardState"]) => {
    if (g === "BLOCK") return "#f87171";
    if (g === "HOLD") return "#fbbf24";
    if (g === "ALLOW") return "#4ade80";
    return "#60a5fa";
  };

  const worldColor = (w: StreamEvent["world"]) => {
    if (w === "trading") return "#60a5fa";
    if (w === "bank") return "#a78bfa";
    return "#fbbf24";
  };

  const worldIcon = (w: StreamEvent["world"]) => {
    if (w === "trading") return "📈";
    if (w === "bank") return "🏦";
    return "🛒";
  };

  return (
    <div className="panel p-0 overflow-hidden" style={{ border: "1px solid oklch(0.18 0.02 240)" }}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3" style={{ background: "oklch(0.10 0.02 240)", borderBottom: "1px solid oklch(0.18 0.02 240)" }}>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full" style={{ background: paused ? "#6b7280" : "#4ade80" }} />
          <span className="font-mono font-bold text-sm text-foreground">Decision Stream</span>
          <span className="text-[9px] font-mono px-1.5 py-0.5 rounded" style={{ background: "oklch(0.72 0.18 145 / 0.15)", color: "#4ade80" }}>LIVE</span>
        </div>
        <div className="flex items-center gap-2">
          {/* World filter */}
          {(["all", "trading", "bank", "ecom"] as const).map(w => (
            <button
              key={w}
              onClick={() => setActiveWorld(w)}
              className="text-[9px] font-mono px-2 py-0.5 rounded"
              style={{
                background: activeWorld === w ? (w === "all" ? "oklch(0.20 0.01 240)" : `${worldColor(w as StreamEvent["world"])}20`) : "transparent",
                color: activeWorld === w ? (w === "all" ? "#e2e8f0" : worldColor(w as StreamEvent["world"])) : "oklch(0.40 0.01 240)",
                border: `1px solid ${activeWorld === w ? (w === "all" ? "oklch(0.30 0.01 240)" : `${worldColor(w as StreamEvent["world"])}40`) : "oklch(0.18 0.01 240)"}`,
              }}
            >
              {w === "all" ? "ALL" : w.toUpperCase()}
            </button>
          ))}
          <button
            onClick={() => setPaused(p => !p)}
            className="text-[9px] font-mono px-2 py-0.5 rounded ml-1"
            style={{ background: paused ? "oklch(0.72 0.18 145 / 0.15)" : "oklch(0.20 0.01 240)", color: paused ? "#4ade80" : "#6b7280", border: "1px solid oklch(0.25 0.01 240)" }}
          >
            {paused ? "▶ PLAY" : "⏸ PAUSE"}
          </button>
        </div>
      </div>

      {/* Stream */}
      <div ref={listRef} className="overflow-y-auto" style={{ maxHeight: "380px", background: "oklch(0.07 0.01 240)" }}>
        {filtered.length === 0 && (
          <div className="text-center py-8 text-muted-foreground font-mono text-xs">No events yet — press PLAY</div>
        )}
        {filtered.map((ev, idx) => (
          <div
            key={ev.id}
            className="px-4 py-2.5 border-b"
            style={{
              borderColor: "oklch(0.12 0.01 240)",
              background: idx === 0 ? "oklch(0.10 0.02 240)" : "transparent",
              opacity: idx === 0 ? 1 : Math.max(0.4, 1 - idx * 0.06),
            }}
          >
            <div className="flex items-start gap-3">
              {/* Timestamp + world */}
              <div className="flex flex-col items-center gap-0.5 flex-shrink-0 w-16">
                <span className="text-[9px] font-mono text-zinc-500">
                  {new Date(ev.timestamp).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                </span>
                <span className="text-[8px]">{worldIcon(ev.world)}</span>
                <span className="text-[8px] font-mono" style={{ color: worldColor(ev.world) }}>{ev.world.toUpperCase()}</span>
              </div>

              {/* Main content */}
              <div className="flex-1 min-w-0">
                {/* Proposal */}
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[10px] font-mono font-bold text-zinc-200">{ev.proposal}</span>
                  <span className="text-[8px] font-mono px-1 py-0.5 rounded" style={{ background: `${guardColor(ev.guardState)}15`, color: guardColor(ev.guardState), border: `1px solid ${guardColor(ev.guardState)}30` }}>
                    Guard: {ev.guardState}{ev.holdRemaining ? ` (τ ${ev.holdRemaining}s)` : ""}
                  </span>
                </div>

                {/* Coherence bar */}
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[8px] font-mono text-zinc-500 w-16">coherence</span>
                  <div className="flex-1 h-1 rounded-full bg-zinc-800">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${ev.coherence * 100}%`,
                        background: ev.coherence >= 0.6 ? "#4ade80" : ev.coherence >= 0.3 ? "#fbbf24" : "#f87171",
                      }}
                    />
                  </div>
                  <span className="text-[8px] font-mono" style={{ color: ev.coherence >= 0.6 ? "#4ade80" : ev.coherence >= 0.3 ? "#fbbf24" : "#f87171" }}>
                    {(ev.coherence * 100).toFixed(0)}%
                  </span>
                </div>

                {/* Decision + proof */}
                <div className="flex items-center gap-3">
                  <span className="text-[9px] font-mono font-bold" style={{ color: decisionColor(ev.decision) }}>
                    → {ev.decision}
                  </span>
                  {ev.proofHash && (
                    <span className="text-[8px] font-mono text-zinc-600">
                      proof: {ev.proofHash}…
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer stats */}
      <div className="px-4 py-2 flex items-center gap-4 text-[9px] font-mono" style={{ background: "oklch(0.09 0.01 240)", borderTop: "1px solid oklch(0.14 0.01 240)" }}>
        {[
          { label: "BLOCK", color: "#f87171", count: events.filter(e => e.decision === "BLOCKED").length },
          { label: "HOLD", color: "#fbbf24", count: events.filter(e => e.decision === "HELD").length },
          { label: "ALLOW", color: "#4ade80", count: events.filter(e => e.decision === "EXECUTED").length },
        ].map(s => (
          <span key={s.label} style={{ color: s.color }}>
            ■ {s.label} {s.count}
          </span>
        ))}
        <span className="ml-auto text-zinc-600">{events.length} events total</span>
      </div>
    </div>
  );
}
