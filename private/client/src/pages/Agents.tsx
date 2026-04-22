/**
 * Agents.tsx — OS4 v31
 * Page Agents : Alpha (trading), Sentinel (fraud), Mercury (inventory)
 * Flux : Market → Agents → Decision → Guard X-108 → Proof
 */
import React, { useState, useEffect } from "react";
import { Link } from "wouter";
import { trpc } from "@/lib/trpc";
import { useViewMode } from "@/contexts/ViewModeContext";

// ─── Flux visuel ─────────────────────────────────────────────────────────────
const FLUX_STEPS = [
  { id: "market", label: "Market", icon: "📊", href: "/market" },
  { id: "agents", label: "Agents", icon: "🤖", href: "/agents" },
  { id: "decision", label: "Decision", icon: "⚖", href: "/stream" },
  { id: "guard", label: "Guard X-108", icon: "🛡", href: "/engine" },
  { id: "proof", label: "Proof", icon: "⛓", href: "/proof-center" },
];

function FluxBar({ active }: { active: string }) {
  return (
    <div className="flex items-center justify-center gap-0 mb-8 flex-wrap">
      {FLUX_STEPS.map((step, i) => (
        <React.Fragment key={step.id}>
          <Link href={step.href}>
            <div
              className="flex items-center gap-1.5 px-3 py-2 rounded font-mono text-[10px] font-bold cursor-pointer"
              style={{
                background: step.id === active ? "oklch(0.72 0.18 145 / 0.15)" : "oklch(0.12 0.01 240)",
                border: `1px solid ${step.id === active ? "oklch(0.72 0.18 145)" : "oklch(0.20 0.01 240)"}`,
                color: step.id === active ? "oklch(0.72 0.18 145)" : "oklch(0.45 0.01 240)",
              }}
            >
              <span>{step.icon}</span>
              <span>{step.label}</span>
            </div>
          </Link>
          {i < FLUX_STEPS.length - 1 && (
            <div className="px-1.5 font-mono text-[10px]" style={{ color: "oklch(0.30 0.01 240)" }}>→</div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
}

// ─── Définition des agents ────────────────────────────────────────────────────
const AGENTS = [
  {
    id: "alpha",
    name: "Agent Alpha",
    role: "Trading Agent",
    domain: "TRADING",
    domainLabel: "Trading",
    domainColor: "oklch(0.72 0.18 145)",
    icon: "📈",
    description: "Analyses market signals, volatility patterns, and price action to generate buy/sell proposals.",
    descriptionSimple: "Watches the crypto market and proposes buy or sell actions based on price and volatility.",
    capabilities: ["Price analysis", "Volatility detection", "Regime classification", "Signal generation"],
    streamId: "agent_trading",
  },
  {
    id: "sentinel",
    name: "Agent Sentinel",
    role: "Fraud Detector",
    domain: "BANKING",
    domainLabel: "Bank",
    domainColor: "oklch(0.60 0.12 200)",
    icon: "🔍",
    description: "Monitors transaction flows, detects anomalies, and flags suspicious patterns using risk scoring.",
    descriptionSimple: "Monitors bank transactions and flags suspicious ones before they are executed.",
    capabilities: ["Transaction monitoring", "Risk scoring", "AML detection", "Fraud pattern matching"],
    streamId: "agent_banking",
  },
  {
    id: "mercury",
    name: "Agent Mercury",
    role: "Inventory Manager",
    domain: "ECOMMERCE",
    domainLabel: "E-Commerce",
    domainColor: "#f59e0b",
    icon: "🛒",
    description: "Tracks demand signals, stock levels, and pricing dynamics to propose optimal inventory actions.",
    descriptionSimple: "Monitors product demand and stock levels, and proposes price adjustments when needed.",
    capabilities: ["Demand forecasting", "Stock monitoring", "Price optimization", "Flash sale detection"],
    streamId: "agent_ecommerce",
  },
];

// ─── Composant AgentCard ──────────────────────────────────────────────────────
function AgentCard({ agent, isSimple, events }: {
  agent: typeof AGENTS[0];
  isSimple: boolean;
  events: Array<{ id: string; timestamp: number; agent: { id: string; proposal: string }; guard: { decision: string; reason: string }; domain: string }>;
}) {
  const agentEvents = events.filter(e =>
    e.domain === agent.domain
  ).slice(0, 5);

  const allowCount = agentEvents.filter(e => e.guard.decision === "ALLOW").length;
  const holdCount = agentEvents.filter(e => e.guard.decision === "HOLD").length;
  const blockCount = agentEvents.filter(e => e.guard.decision === "BLOCK").length;
  const total = agentEvents.length || 1;
  const blockRate = Math.round((blockCount / total) * 100);

  const lastEvent = agentEvents[0];
  const DECISION_COLOR: Record<string, string> = {
    ALLOW: "oklch(0.72 0.18 145)",
    HOLD: "#f59e0b",
    BLOCK: "#f87171",
  };

  return (
    <div className="rounded-lg overflow-hidden" style={{ background: "oklch(0.10 0.01 240)", border: `1px solid ${agent.domainColor}33` }}>
      {/* Header */}
      <div className="p-5" style={{ borderBottom: "1px solid oklch(0.18 0.01 240)" }}>
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg flex items-center justify-center text-xl" style={{ background: `${agent.domainColor}22`, border: `1px solid ${agent.domainColor}44` }}>
              {agent.icon}
            </div>
            <div>
              <div className="font-mono font-bold text-base text-foreground">{agent.name}</div>
              <div className="font-mono text-[10px]" style={{ color: agent.domainColor }}>{agent.role}</div>
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: "oklch(0.72 0.18 145)" }} />
            <span className="font-mono text-[9px]" style={{ color: "oklch(0.45 0.01 240)" }}>ACTIVE</span>
          </div>
        </div>
        <p className="font-mono text-[11px] leading-relaxed" style={{ color: "oklch(0.55 0.01 240)" }}>
          {isSimple ? agent.descriptionSimple : agent.description}
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-0" style={{ borderBottom: "1px solid oklch(0.18 0.01 240)" }}>
        {[
          { label: "ALLOW", count: allowCount, color: "oklch(0.72 0.18 145)" },
          { label: "HOLD", count: holdCount, color: "#f59e0b" },
          { label: "BLOCK", count: blockCount, color: "#f87171" },
        ].map((stat, i) => (
          <div key={stat.label} className="p-3 text-center" style={{ borderRight: i < 2 ? "1px solid oklch(0.18 0.01 240)" : "none" }}>
            <div className="font-mono font-bold text-lg" style={{ color: stat.color }}>{stat.count}</div>
            <div className="font-mono text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Signal + Confidence + Last action */}
      {lastEvent && (
        <div className="p-4" style={{ borderBottom: "1px solid oklch(0.18 0.01 240)" }}>
          {/* Signal row */}
          <div className="flex items-center justify-between mb-2">
            <div>
              <div className="font-mono text-[9px] font-bold tracking-widest mb-0.5" style={{ color: "oklch(0.40 0.01 240)" }}>SIGNAL</div>
              <div className="font-mono text-xs font-bold text-foreground">{lastEvent.agent.proposal}</div>
            </div>
            <div className="text-right">
              <div className="font-mono text-[9px] font-bold tracking-widest mb-0.5" style={{ color: "oklch(0.40 0.01 240)" }}>CONFIDENCE</div>
              {(() => {
                const conf = (() => {
                  const match = lastEvent.guard.reason?.match(/([0-9]+\.?[0-9]*)/);
                  if (match) {
                    const v = parseFloat(match[1]);
                    return v > 1 ? v / 100 : v;
                  }
                  return 0.5;
                })();
                const pct = Math.round(conf * 100);
                const color = conf >= 0.6 ? "oklch(0.72 0.18 145)" : conf >= 0.35 ? "#f59e0b" : "#f87171";
                return (
                  <div className="flex items-center gap-1.5">
                    <div className="w-12 h-1.5 rounded-full overflow-hidden" style={{ background: "oklch(0.18 0.01 240)" }}>
                      <div className="h-full rounded-full" style={{ width: `${pct}%`, background: color }} />
                    </div>
                    <span className="font-mono text-[10px] font-bold" style={{ color }}>{pct}%</span>
                  </div>
                );
              })()}
            </div>
          </div>
          {/* Guard verdict */}
          <div className="flex items-center justify-between">
            <div className="font-mono text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>
              {lastEvent.guard.reason}
            </div>
            <span className="font-mono text-[9px] font-bold px-2 py-0.5 rounded ml-2 shrink-0" style={{ background: `${DECISION_COLOR[lastEvent.guard.decision]}22`, color: DECISION_COLOR[lastEvent.guard.decision], border: `1px solid ${DECISION_COLOR[lastEvent.guard.decision]}44` }}>
              {lastEvent.guard.decision}
            </span>
          </div>
        </div>
      )}

      {/* Capabilities (Expert only) */}
      {!isSimple && (
        <div className="p-4" style={{ borderBottom: "1px solid oklch(0.18 0.01 240)" }}>
          <div className="font-mono text-[9px] font-bold tracking-widest mb-2" style={{ color: "oklch(0.40 0.01 240)" }}>CAPABILITIES</div>
          <div className="flex flex-wrap gap-1.5">
            {agent.capabilities.map(cap => (
              <span key={cap} className="font-mono text-[9px] px-2 py-0.5 rounded" style={{ background: `${agent.domainColor}15`, color: agent.domainColor, border: `1px solid ${agent.domainColor}33` }}>
                {cap}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Block rate */}
      <div className="p-4">
        <div className="flex items-center justify-between mb-1.5">
          <span className="font-mono text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>Guard block rate</span>
          <span className="font-mono text-[9px] font-bold" style={{ color: blockRate > 30 ? "#f87171" : "oklch(0.72 0.18 145)" }}>{blockRate}%</span>
        </div>
        <div className="h-1 rounded-full overflow-hidden" style={{ background: "oklch(0.18 0.01 240)" }}>
          <div className="h-full rounded-full" style={{ width: `${blockRate}%`, background: blockRate > 30 ? "#f87171" : "oklch(0.72 0.18 145)" }} />
        </div>
        {isSimple && (
          <div className="font-mono text-[9px] mt-2" style={{ color: "oklch(0.40 0.01 240)" }}>
            {blockRate > 30
              ? `⚠ ${blockRate}% of proposals blocked — high-risk domain`
              : `✓ ${blockRate}% block rate — system operating normally`}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Page principale ──────────────────────────────────────────────────────────
// ─── Export helpers ─────────────────────────────────────────────────────────
function exportCSV(events: Array<{ id: string; timestamp: number; domain: string; agent: { id: string; proposal: string }; guard: { decision: string; reason: string } }>) {
  const header = "id,timestamp,domain,proposal,decision,reason\n";
  const rows = events.map(e =>
    `${e.id},${new Date(e.timestamp).toISOString()},${e.domain},"${e.agent.proposal}",${e.guard.decision},"${e.guard.reason}"`
  ).join("\n");
  const blob = new Blob([header + rows], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a"); a.href = url; a.download = "agents_decisions.csv"; a.click();
  URL.revokeObjectURL(url);
}

function exportJSON(events: Array<{ id: string; timestamp: number; domain: string; agent: { id: string; proposal: string }; guard: { decision: string; reason: string } }>) {
  const blob = new Blob([JSON.stringify(events, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a"); a.href = url; a.download = "agents_decisions.json"; a.click();
  URL.revokeObjectURL(url);
}

export default function Agents() {
  const { isSimple } = useViewMode();
  // Flux live — refresh every 3 seconds
  const { data: streamData, dataUpdatedAt } = trpc.stream.getEvents.useQuery(
    { limit: 50 },
    { refetchInterval: 3000 }
  );

  const events = (streamData ?? []) as Array<{
    id: string;
    timestamp: number;
    domain: string;
    agent: { id: string; proposal: string };
    guard: { decision: string; reason: string };
  }>;

  return (
    <div className="max-w-5xl mx-auto" style={{ color: "oklch(0.90 0.01 240)", paddingTop: "24px" }}>

      {/* Header */}
      <div className="mb-6 rounded p-5" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.72 0.18 145 / 0.20)" }}>
        <div className="font-mono text-[9px] font-bold tracking-[0.3em] uppercase mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>
          OBSIDIA OS4 — STEP 2 OF 5
        </div>
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <h1 className="font-mono font-bold text-3xl text-foreground mb-2">Agents</h1>
            <p className="font-mono text-sm mb-2" style={{ color: "oklch(0.72 0.18 145)" }}>
              Agents observe the world. They propose. Guard X-108 judges.
            </p>
            <p className="font-mono text-xs max-w-2xl leading-relaxed mb-4" style={{ color: "oklch(0.55 0.01 240)" }}>
              {isSimple
                ? "Three autonomous agents monitor the market and propose actions. Each proposal is evaluated by the Guard X-108 before execution."
                : "Three specialized agents operate across trading, banking, and e-commerce domains. Each agent generates proposals that enter the governance pipeline for X-108 validation."}
            </p>
            {/* Pipeline narrative */}
            <div className="flex items-center gap-1 flex-wrap">
              {[
                { label: "WORLD",       color: "#60a5fa", active: false },
                { label: "AGENT",       color: "#a78bfa", active: true },
                { label: "GUARD X-108", color: "#34d399", active: false },
                { label: "VERDICT",     color: "#a78bfa", active: false },
                { label: "PROOF",       color: "#34d399", active: false },
              ].map((item, i, arr) => (
                <React.Fragment key={item.label}>
                  <div
                    className="px-2 py-1 rounded font-mono text-[9px] font-bold"
                    style={{
                      background: item.active ? `${item.color}20` : "oklch(0.09 0.01 240)",
                      border: `1px solid ${item.active ? item.color : "oklch(0.18 0.01 240)"}`,
                      color: item.active ? item.color : "oklch(0.35 0.01 240)",
                    }}
                  >
                    {item.active && <span className="mr-1">▶</span>}{item.label}
                  </div>
                  {i < arr.length - 1 && <span className="font-mono text-[9px]" style={{ color: "oklch(0.28 0.01 240)" }}>→</span>}
                </React.Fragment>
              ))}
            </div>
          </div>
          {/* Live indicator + export */}
          <div className="flex flex-col items-end gap-2">
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: "oklch(0.72 0.18 145)" }} />
              <span className="font-mono text-[9px]" style={{ color: "oklch(0.72 0.18 145)" }}>LIVE</span>
              <span className="font-mono text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>
                {dataUpdatedAt ? new Date(dataUpdatedAt).toLocaleTimeString() : ""}
              </span>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => exportCSV(events)}
                disabled={events.length === 0}
                className="font-mono text-[9px] px-3 py-1.5 rounded"
                style={{ background: "oklch(0.72 0.18 145 / 0.12)", border: "1px solid oklch(0.72 0.18 145 / 0.4)", color: "oklch(0.72 0.18 145)", opacity: events.length === 0 ? 0.4 : 1 }}
              >
                ↓ Export CSV
              </button>
              <button
                onClick={() => exportJSON(events)}
                disabled={events.length === 0}
                className="font-mono text-[9px] px-3 py-1.5 rounded"
                style={{ background: "oklch(0.60 0.12 200 / 0.12)", border: "1px solid oklch(0.60 0.12 200 / 0.4)", color: "oklch(0.60 0.12 200)", opacity: events.length === 0 ? 0.4 : 1 }}
              >
                ↓ Export JSON
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Flux visuel */}
      <FluxBar active="agents" />

      {/* Agents grid */}
      <div className="grid grid-cols-1 gap-6 mb-8" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))" }}>
        {AGENTS.map(agent => (
          <AgentCard key={agent.id} agent={agent} isSimple={isSimple} events={events} />
        ))}
      </div>

      {/* Recent decisions table */}
      <div className="rounded-lg overflow-hidden mb-8" style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
        <div className="p-4 flex items-center justify-between" style={{ borderBottom: "1px solid oklch(0.18 0.01 240)" }}>
          <div className="font-mono text-[9px] font-bold tracking-widest" style={{ color: "oklch(0.45 0.01 240)" }}>
            RECENT DECISIONS — ALL AGENTS ({events.length} events)
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: "oklch(0.72 0.18 145)" }} />
            <span className="font-mono text-[9px]" style={{ color: "oklch(0.72 0.18 145)" }}>live · 3s refresh</span>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full font-mono text-[10px]">
            <thead>
              <tr style={{ borderBottom: "1px solid oklch(0.18 0.01 240)" }}>
                {["Time", "Domain", "Proposal", "Guard", "Reason"].map(h => (
                  <th key={h} className="px-4 py-2 text-left font-bold" style={{ color: "oklch(0.40 0.01 240)" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {events.slice(0, 8).map(ev => {
                const DECISION_COLOR: Record<string, string> = { ALLOW: "oklch(0.72 0.18 145)", HOLD: "#f59e0b", BLOCK: "#f87171" };
                const DOMAIN_COLOR: Record<string, string> = { TRADING: "oklch(0.72 0.18 145)", BANKING: "oklch(0.60 0.12 200)", ECOMMERCE: "#f59e0b" };
                return (
                  <tr key={ev.id} style={{ borderBottom: "1px solid oklch(0.14 0.01 240)" }}>
                    <td className="px-4 py-2" style={{ color: "oklch(0.40 0.01 240)" }}>
                      {new Date(ev.timestamp).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                    </td>
                    <td className="px-4 py-2">
                      <span className="px-1.5 py-0.5 rounded text-[9px]" style={{ background: `${DOMAIN_COLOR[ev.domain] ?? "#888"}22`, color: DOMAIN_COLOR[ev.domain] ?? "#888" }}>
                        {ev.domain}
                      </span>
                    </td>
                    <td className="px-4 py-2 font-bold text-foreground">{ev.agent.proposal}</td>
                    <td className="px-4 py-2">
                      <span className="font-bold" style={{ color: DECISION_COLOR[ev.guard.decision] ?? "#888" }}>{ev.guard.decision}</span>
                    </td>
                    <td className="px-4 py-2" style={{ color: "oklch(0.45 0.01 240)", maxWidth: "200px" }}>
                      <span className="truncate block">{ev.guard.reason}</span>
                    </td>
                  </tr>
                );
              })}
              {events.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-6 text-center" style={{ color: "oklch(0.40 0.01 240)" }}>
                    Loading agent decisions...
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="rounded-lg p-5" style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
        <div className="font-mono text-[9px] font-bold tracking-widest mb-3" style={{ color: "oklch(0.45 0.01 240)" }}>NEXT STEPS IN THE PIPELINE</div>
        <div className="flex flex-wrap gap-3">
          <Link href="/stream">
            <button className="px-4 py-2 rounded font-mono text-xs font-bold" style={{ background: "oklch(0.60 0.12 200 / 0.15)", color: "oklch(0.60 0.12 200)", border: "1px solid oklch(0.60 0.12 200 / 0.4)" }}>
              ⚖ Decision Stream →
            </button>
          </Link>
          <Link href="/control">
            <button className="px-4 py-2 rounded font-mono text-xs font-bold" style={{ background: "oklch(0.72 0.18 145 / 0.15)", color: "oklch(0.72 0.18 145)", border: "1px solid oklch(0.72 0.18 145 / 0.4)" }}>
              🤖 Control Tower →
            </button>
          </Link>
          <Link href="/simulation-worlds">
            <button className="px-4 py-2 rounded font-mono text-xs font-bold" style={{ background: "oklch(0.72 0.18 145)", color: "oklch(0.10 0.01 240)" }}>
              ▶ Run Simulation →
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
}
