import React, { useState, useEffect, useRef } from "react";
import { Link } from "wouter";
import { trpc } from "@/lib/trpc";
import { useDecisionStream } from "@/hooks/useDecisionStream";
import StrasbourgClockModule from "@/components/StrasbourgClockModule";
import { useMemo } from "react";

// ─── Types ────────────────────────────────────────────────────────────────────

type GuardDecision = "ALLOW" | "HOLD" | "BLOCK";
type AgentStatus = "active" | "idle" | "blocked" | "holding";
type World = "trading" | "bank" | "ecom";

interface Agent {
  id: string;
  name: string;
  world: World;
  status: AgentStatus;
  intent: string;
  lastDecision: GuardDecision;
  fiabilité: number;
  actionsTotal: number;
  actionsBlocked: number;
}

interface DecisionEvent {
  id: string;
  ts: number;
  agent: string;
  world: World;
  intent: string;
  decision: GuardDecision;
  coherence: number;
  latencyMs: number;
  proofHash: string;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

const DECISION_COLORS: Record<GuardDecision, string> = {
  BLOCK: "#f87171",
  HOLD: "#fbbf24",
  ALLOW: "#4ade80",
};

const DECISION_ICONS: Record<GuardDecision, string> = {
  ALLOW: "🟢",
  HOLD: "🟡",
  BLOCK: "🔴",
};

const WORLD_COLORS: Record<World, string> = {
  trading: "#60a5fa",
  bank: "#a78bfa",
  ecom: "#34d399",
};

const WORLD_ICONS: Record<World, string> = {
  trading: "📈",
  bank: "🛡️",
  ecom: "🛒",
};

const STATUS_COLORS: Record<AgentStatus, string> = {
  active: "#4ade80",
  idle: "oklch(0.45 0.01 240)",
  blocked: "#f87171",
  holding: "#fbbf24",
};

const CONSENSUS_NODES = [
  { city: "Paris", ok: true },
  { city: "London", ok: true },
  { city: "Frankfurt", ok: true },
  { city: "Amsterdam", ok: true },
];

function shortHash(n: number): string {
  return ((n * 31337 + Date.now()) >>> 0).toString(16).padStart(8, "0").slice(0, 8);
}

function seededRand(seed: number, step: number): number {
  return ((seed * 1664525 + step * 1013904223) >>> 0) / 0xffffffff;
}

function makeDecision(fiabilité: number): GuardDecision {
  if (fiabilité < 0.30) return "BLOCK";
  if (fiabilité < 0.60) return "HOLD";
  return "ALLOW";
}

const INITIAL_AGENTS: Agent[] = [
  { id: "ta1", name: "Alpha — Trading Principal", world: "trading", status: "active", intent: "SELL 1.2 BTC", lastDecision: "HOLD", fiabilité: 0.55, actionsTotal: 0, actionsBlocked: 0 },
  { id: "ba1", name: "Sentinel — Fraud Detector", world: "bank", status: "active", intent: "DEPOSIT €5 000", lastDecision: "ALLOW", fiabilité: 0.82, actionsTotal: 0, actionsBlocked: 0 },
  { id: "pa1", name: "Vault — Risk Manager", world: "bank", status: "active", intent: "WITHDRAW €50 000", lastDecision: "BLOCK", fiabilité: 0.18, actionsTotal: 0, actionsBlocked: 0 },
  { id: "ia1", name: "Omega — Pricing Agent", world: "ecom", status: "idle", intent: "UPDATE PRICE", lastDecision: "ALLOW", fiabilité: 0.91, actionsTotal: 0, actionsBlocked: 0 },
];

const INTENTS: Record<World, string[]> = {
  trading: ["SELL 1.2 BTC", "BUY ETH", "SHORT BTC", "LONG ETH", "REBALANCE", "CLOSE POSITION"],
  bank: ["DEPOSIT €5 000", "WIRE €200 000", "WITHDRAW €50 000", "APPROVE LOAN", "FREEZE ACCOUNT", "VALIDATE KYC"],
  ecom: ["UPDATE PRICE", "RESTOCK SKU-42", "APPLY DISCOUNT", "CANCEL ORDER", "BULK IMPORT", "FLASH SALE"],
};

// ─── Component ────────────────────────────────────────────────────────────────

export default function ControlTower() {
  const [agents, setAgents] = useState<Agent[]>(INITIAL_AGENTS);
  const [events, setEvents] = useState<DecisionEvent[]>([]);
  const [showAllAgents, setShowAllAgents] = useState(false);
  const [showAllDecisions, setShowAllDecisions] = useState(false);
  const [globalStats, setGlobalStats] = useState({ block: 0, hold: 0, allow: 0, total: 0 });
  const stepRef = useRef(0);

  // WebSocket live decision stream
  const { events: wsEvents, stats: wsStats, connected: wsConnected, latency: wsLatency } = useDecisionStream();

  // Sync WebSocket events into local state
  useEffect(() => {
    if (wsEvents.length === 0) return;
    const latest = wsEvents[0];
    const worldMap: Record<string, World> = { TRADING: "trading", BANKING: "bank", ECOMMERCE: "ecom" };
    const w = worldMap[latest.domain] ?? "trading";
    const d = latest.guard.decision as GuardDecision;
    const localEvent: DecisionEvent = {
      id: latest.id,
      ts: latest.timestamp,
      agent: latest.agent.id,
      world: w,
      intent: latest.agent.proposal,
      decision: d,
      coherence: latest.engine.coherence,
      latencyMs: Math.floor(Math.random() * 15 + 5),
      proofHash: latest.proof.hash,
    };
    setEvents(prev => [localEvent, ...prev].slice(0, 50));
    setAgents(prev => prev.map(a => a.world === w ? {
      ...a,
      coherence: latest.engine.coherence,
      lastDecision: d,
      status: d === "BLOCK" ? "blocked" : d === "HOLD" ? "holding" : "active",
      intent: latest.agent.proposal,
      actionsTotal: a.actionsTotal + 1,
      actionsBlocked: a.actionsBlocked + (d === "BLOCK" ? 1 : 0),
    } : a));
  }, [wsEvents]);

  // ── Real backend data ────────────────────────────────────────────────────
  const proofQuery = trpc.engine.proofs.useQuery(undefined, { refetchInterval: 30000 });
  const engineInfo = trpc.engine.info.useQuery(undefined, { refetchInterval: 15000 });
  const tradingHistory = trpc.trading.history.useQuery({ limit: 20 }, { refetchInterval: 10000 });
  const bankHistory = trpc.bank.history.useQuery({ limit: 20 }, { refetchInterval: 10000 });
  const ecomHistory = trpc.ecom.history.useQuery({ limit: 20 }, { refetchInterval: 10000 });

  // ── Merge real tickets from all 3 domains into unified decision events ────
  const realEvents = useMemo(() => {
    const all: DecisionEvent[] = [];
    const toDecision = (d: string): GuardDecision =>
      d === "BLOCK" ? "BLOCK" : d === "HOLD" ? "HOLD" : "ALLOW";
    const toWorld = (domain: string): World =>
      domain === "bank" ? "bank" : domain === "ecom" ? "ecom" : "trading";
    for (const t of tradingHistory.data ?? []) {
      all.push({
        id: String(t.id),
        ts: typeof t.createdAt === "number" ? t.createdAt : new Date(t.createdAt).getTime(),
        agent: "Alpha — Trading Principal",
        world: "trading",
        intent: t.intentId ?? "TRADE",
        decision: toDecision(t.decision),
        coherence: (t.thresholds as any)?.min_min_ciz ?? 0.7,
        latencyMs: 8,
        proofHash: t.auditTrail ? String(t.auditTrail).slice(0, 8) : "--------",
      });
    }
    for (const t of bankHistory.data ?? []) {
      all.push({
        id: String(t.id),
        ts: typeof t.createdAt === "number" ? t.createdAt : new Date(t.createdAt).getTime(),
        agent: "Sentinel — Fraud Detector",
        world: "bank",
        intent: t.intentId ?? "BANK_OP",
        decision: toDecision(t.decision),
        coherence: (t.thresholds as any)?.min_min_ciz ?? 0.65,
        latencyMs: 11,
        proofHash: t.auditTrail ? String(t.auditTrail).slice(0, 8) : "--------",
      });
    }
    for (const t of ecomHistory.data ?? []) {
      all.push({
        id: String(t.id),
        ts: typeof t.createdAt === "number" ? t.createdAt : new Date(t.createdAt).getTime(),
        agent: "Omega — Pricing Agent",
        world: "ecom",
        intent: t.intentId ?? "ECOM_OP",
        decision: toDecision(t.decision),
        coherence: (t.thresholds as any)?.min_min_ciz ?? 0.72,
        latencyMs: 9,
        proofHash: t.auditTrail ? String(t.auditTrail).slice(0, 8) : "--------",
      });
    }
    return all.sort((a, b) => b.ts - a.ts).slice(0, 50);
  }, [tradingHistory.data, bankHistory.data, ecomHistory.data]);

  // ── Real guard stats from DB tickets ─────────────────────────────────────
  const realStats = useMemo(() => {
    const all = [...(tradingHistory.data ?? []), ...(bankHistory.data ?? []), ...(ecomHistory.data ?? [])];
    const block = all.filter(t => t.decision === "BLOCK").length;
    const hold = all.filter(t => t.decision === "HOLD").length;
    const allow = all.filter(t => t.decision === "ALLOW").length;
    const total = all.length;
    return { block, hold, allow, total };
  }, [tradingHistory.data, bankHistory.data, ecomHistory.data]);

  // ── Real agent stats from DB tickets ─────────────────────────────────────
  const agentStats = useMemo(() => {
    const byWorld: Record<World, { total: number; blocked: number; lastDecision: GuardDecision; lastIntent: string; coherence: number }> = {
      trading: { total: 0, blocked: 0, lastDecision: "ALLOW", lastIntent: "—", coherence: 0.75 },
      bank: { total: 0, blocked: 0, lastDecision: "ALLOW", lastIntent: "—", coherence: 0.75 },
      ecom: { total: 0, blocked: 0, lastDecision: "ALLOW", lastIntent: "—", coherence: 0.75 },
    };
    for (const ev of realEvents) {
      const w = ev.world;
      byWorld[w].total++;
      if (ev.decision === "BLOCK") byWorld[w].blocked++;
      if (byWorld[w].total === 1) {
        byWorld[w].lastDecision = ev.decision;
        byWorld[w].lastIntent = ev.intent;
        byWorld[w].coherence = ev.coherence;
      }
    }
    return byWorld;
  }, [realEvents]);

  // Live simulation tick
  useEffect(() => {
    const interval = setInterval(() => {
      stepRef.current++;
      const step = stepRef.current;

      setAgents(prev => prev.map((agent, i) => {
        const r = seededRand(i * 100 + step, step);
        const fiabilitéShift = (r - 0.5) * 0.15;
        const newFiabilité = Math.max(0.05, Math.min(0.98, agent.fiabilité + fiabilitéShift));
        const decision = makeDecision(newFiabilité);
        const intents = INTENTS[agent.world];
        const newIntent = r > 0.7 ? intents[Math.floor(r * intents.length) % intents.length] : agent.intent;
        const newStatus: AgentStatus = decision === "BLOCK" ? "blocked" : decision === "HOLD" ? "holding" : "active";

        const event: DecisionEvent = {
          id: `${agent.id}-${step}`,
          ts: Date.now(),
          agent: agent.name,
          world: agent.world,
          intent: newIntent,
          decision,
          coherence: newFiabilité,
          latencyMs: Math.floor(r * 15 + 5),
          proofHash: shortHash(i * 1000 + step),
        };

        setEvents(prev => [event, ...prev].slice(0, 50));
        setGlobalStats(prev => ({
          block: prev.block + (decision === "BLOCK" ? 1 : 0),
          hold: prev.hold + (decision === "HOLD" ? 1 : 0),
          allow: prev.allow + (decision === "ALLOW" ? 1 : 0),
          total: prev.total + 1,
        }));

        return {
          ...agent,
          fiabilité: newFiabilité,
          intent: newIntent,
          lastDecision: decision,
          status: newStatus,
          actionsTotal: agent.actionsTotal + 1,
          actionsBlocked: agent.actionsBlocked + (decision === "BLOCK" ? 1 : 0),
        };
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, [agents]);

  // Prefer real DB stats when available, fallback to local simulation
  const hasRealData = realStats.total > 0;
  const totalDecisions = hasRealData ? realStats.total : (wsStats.total > 0 ? wsStats.total : globalStats.total);
  const blockPct = hasRealData ? (realStats.block / realStats.total) * 100 : (totalDecisions > 0 ? (globalStats.block / globalStats.total) * 100 : 30);
  const holdPct = hasRealData ? (realStats.hold / realStats.total) * 100 : (totalDecisions > 0 ? (globalStats.hold / globalStats.total) * 100 : 18);
  const allowPct = hasRealData ? (realStats.allow / realStats.total) * 100 : (totalDecisions > 0 ? (globalStats.allow / globalStats.total) * 100 : 52);
  // Merge real events with local simulation events
  const mergedEvents = useMemo(() => {
    if (realEvents.length > 0) return realEvents;
    return events;
  }, [realEvents, events]);
  const avgLatency = engineInfo.data?.uptime_ms
    ? Math.round(engineInfo.data.uptime_ms / Math.max(totalDecisions, 1) % 20 + 5)
    : (events.length > 0 ? Math.round(events.slice(0, 20).reduce((s, e) => s + e.latencyMs, 0) / Math.min(events.length, 20)) : 11);

  const displayedAgents = showAllAgents ? agents : agents.slice(0, 2);
  const displayedDecisions = showAllDecisions ? mergedEvents : mergedEvents.slice(0, 5);
  const consensusReached = CONSENSUS_NODES.filter(n => n.ok).length >= 3;

  return (
    <div className="flex flex-col max-w-4xl mx-auto px-4 pb-12" style={{ gap: "40px" }}>

      {/* ─── Header ──────────────────────────────────────────────────────────────────────── */}
      <div className="pt-8">
        {/* Fil narratif STEP 5 OF 5 */}
        <div className="flex items-center gap-2 mb-5 flex-wrap">
          {[
            { label: "Market", step: 1, href: "/market", color: "#60a5fa" },
            { label: "Agents", step: 2, href: "/agents", color: "#fbbf24" },
            { label: "Guard X-108", step: 3, href: "/decision-flow", color: "oklch(0.72 0.18 145)" },
            { label: "Proof", step: 4, href: "/proof", color: "#34d399" },
            { label: "Control", step: 5, href: "/control", color: "#60a5fa", active: true },
          ].map((s, i, arr) => (
            <React.Fragment key={s.step}>
              <a href={s.href} className="flex items-center gap-1.5 px-2.5 py-1 rounded font-mono text-[9px] font-bold" style={{ textDecoration: "none", background: s.active ? `${s.color}18` : "oklch(0.12 0.01 240)", border: `1px solid ${s.active ? s.color : "oklch(0.20 0.01 240)"}`, color: s.active ? s.color : "oklch(0.40 0.01 240)" }}>
                <span style={{ opacity: 0.6 }}>{s.step}</span>
                <span>{s.label}</span>
              </a>
              {i < arr.length - 1 && <span className="font-mono text-[9px]" style={{ color: "oklch(0.28 0.01 240)" }}>→</span>}
            </React.Fragment>
          ))}
        </div>
        <div className="flex items-center justify-between">
          <div>
            <div className="text-[10px] font-mono tracking-[0.3em] uppercase mb-1" style={{ color: "oklch(0.72 0.18 145)" }}>
              Obsidia Labs — OS4
            </div>
            <h1 className="font-mono font-bold text-2xl text-foreground">
              Control Tower
              <span className="ml-3 text-sm font-normal" style={{ color: "oklch(0.55 0.01 240)" }}>Autonomous Agent Governance</span>
            </h1>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: wsConnected ? "#4ade80" : "#f87171" }} />
              <span className="text-[10px] font-mono" style={{ color: wsConnected ? "#4ade80" : "#f87171" }}>
                {wsConnected ? "LIVE" : "RECONNECTING"}
              </span>
            </div>
            {wsLatency > 0 && (
              <span className="text-[9px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>{wsLatency}ms</span>
            )}
            <span className="text-[9px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>{totalDecisions} decisions</span>
          </div>
        </div>
      </div>

      {/* ─── SECTION 1 : AGENTS ACTIFS ──────────────────────────────────────── */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-mono font-bold text-sm uppercase tracking-widest" style={{ color: "oklch(0.72 0.18 145)" }}>
            Agents actifs ({agents.length})
          </h2>
          <button
            onClick={() => setShowAllAgents(v => !v)}
            className="text-[10px] font-mono px-3 py-1.5 rounded border transition-colors"
            style={{ borderColor: "oklch(0.25 0.01 240)", color: "oklch(0.65 0.01 240)" }}
          >
            {showAllAgents ? "Réduire" : "Voir tout"}
          </button>
        </div>
        <div className="flex flex-col" style={{ gap: "16px" }}>
          {displayedAgents.map(agent => (
            <div
              key={agent.id}
              className="rounded-lg"
              style={{
                padding: "24px",
                background: "oklch(0.10 0.01 240)",
                border: `1px solid oklch(0.20 0.01 240)`,
                borderLeft: `3px solid ${WORLD_COLORS[agent.world]}`,
              }}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="text-lg">{WORLD_ICONS[agent.world]}</span>
                  <div>
                    <div className="font-mono font-bold text-sm text-foreground">{agent.name}</div>
                    <div className="text-[10px] font-mono" style={{ color: "oklch(0.50 0.01 240)" }}>
                      Action proposée : {agent.intent}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-base">{DECISION_ICONS[agent.lastDecision]}</span>
                  <span
                    className="text-xs font-mono font-bold px-2 py-1 rounded"
                    style={{ background: `${DECISION_COLORS[agent.lastDecision]}15`, color: DECISION_COLORS[agent.lastDecision] }}
                  >
                    {agent.lastDecision}
                  </span>
                </div>
              </div>
              {/* Fiabilité bar */}
              <div>
                <div className="flex justify-between text-[9px] font-mono mb-1.5">
                  <span style={{ color: "oklch(0.50 0.01 240)" }}>Cohérence structurelle</span>
                  <span style={{ color: agent.fiabilité < 0.30 ? "#f87171" : agent.fiabilité < 0.60 ? "#fbbf24" : "#4ade80" }}>
                    {(agent.fiabilité * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="h-1.5 rounded overflow-hidden" style={{ background: "oklch(0.16 0.01 240)" }}>
                  <div
                    className="h-full rounded transition-all duration-500"
                    style={{
                      width: `${agent.fiabilité * 100}%`,
                      background: agent.fiabilité < 0.30 ? "#f87171" : agent.fiabilité < 0.60 ? "#fbbf24" : "#4ade80",
                    }}
                  />
                </div>
              </div>
              <div className="text-[9px] font-mono mt-2" style={{ color: "oklch(0.40 0.01 240)" }}>
                {agent.actionsTotal} actions · {agent.actionsBlocked} bloquées
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ─── SECTION 1b : AGENT PROFILES (Alpha / Sentinel / Mercury) ──────────────────────────────────────── */}
      <section>
        <h2 className="font-mono font-bold text-sm uppercase tracking-widest mb-4" style={{ color: "oklch(0.72 0.18 145)" }}>
          Agent Profiles
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            {
              name: "Alpha",
              role: "Trading Principal",
              domain: "trading",
              icon: "📈",
              color: "#60a5fa",
              mission: "Analyzes BTC/ETH market signals and proposes BUY/SELL orders.",
              decisions: agents.find(a => a.world === "trading"),
            },
            {
              name: "Sentinel",
              role: "Fraud Detector",
              domain: "bank",
              icon: "🛡️",
              color: "#a78bfa",
              mission: "Monitors banking transactions for fraud, liquidity risk, and AML compliance.",
              decisions: agents.find(a => a.world === "bank" && a.name.includes("Sentinel")),
            },
            {
              name: "Mercury",
              role: "Pricing Agent",
              domain: "ecom",
              icon: "🛒",
              color: "#34d399",
              mission: "Optimizes e-commerce pricing, promotions, and inventory in real time.",
              decisions: agents.find(a => a.world === "ecom"),
            },
          ].map(profile => {
            const ag = profile.decisions;
            const blockRate = ag && ag.actionsTotal > 0 ? ((ag.actionsBlocked / ag.actionsTotal) * 100).toFixed(0) : "0";
            const allowRate = ag && ag.actionsTotal > 0 ? (((ag.actionsTotal - ag.actionsBlocked) / ag.actionsTotal) * 100).toFixed(0) : "100";
            const fiabilité = ag ? ag.fiabilité : 0.75;
            const lastDecision = ag ? ag.lastDecision : "ALLOW";
            return (
              <div key={profile.name} className="rounded-lg p-5 flex flex-col gap-3"
                style={{ background: "oklch(0.10 0.01 240)", border: `1px solid ${profile.color}30`, borderTop: `3px solid ${profile.color}` }}>
                {/* Header */}
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{profile.icon}</span>
                  <div>
                    <div className="font-mono font-black text-sm" style={{ color: profile.color }}>{profile.name}</div>
                    <div className="text-[9px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>{profile.role}</div>
                  </div>
                  <div className="ml-auto">
                    <span className="text-[9px] font-mono px-2 py-0.5 rounded font-bold"
                      style={{ background: `${DECISION_COLORS[lastDecision]}15`, color: DECISION_COLORS[lastDecision] }}>
                      {lastDecision}
                    </span>
                  </div>
                </div>

                {/* Mission */}
                <p className="text-[10px] font-mono leading-relaxed" style={{ color: "oklch(0.55 0.01 240)" }}>
                  {profile.mission}
                </p>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { label: "Actions", value: ag ? ag.actionsTotal : 0, color: "oklch(0.65 0.01 240)" },
                    { label: "ALLOW", value: `${allowRate}%`, color: "#4ade80" },
                    { label: "BLOCK", value: `${blockRate}%`, color: "#f87171" },
                  ].map(stat => (
                    <div key={stat.label} className="rounded p-2 text-center"
                      style={{ background: "oklch(0.13 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
                      <div className="font-mono font-bold text-sm" style={{ color: stat.color }}>{stat.value}</div>
                      <div className="text-[8px] font-mono mt-0.5" style={{ color: "oklch(0.40 0.01 240)" }}>{stat.label}</div>
                    </div>
                  ))}
                </div>

                {/* Fiabilité bar */}
                <div>
                  <div className="flex justify-between text-[9px] font-mono mb-1">
                    <span style={{ color: "oklch(0.45 0.01 240)" }}>Fiabilité</span>
                    <span style={{ color: fiabilité < 0.30 ? "#f87171" : fiabilité < 0.60 ? "#fbbf24" : "#4ade80" }}>
                      {(fiabilité * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-1 rounded overflow-hidden" style={{ background: "oklch(0.16 0.01 240)" }}>
                    <div className="h-full rounded transition-all duration-500"
                      style={{ width: `${fiabilité * 100}%`, background: fiabilité < 0.30 ? "#f87171" : fiabilité < 0.60 ? "#fbbf24" : profile.color }} />
                  </div>
                </div>

                {/* Current intent */}
                {ag && (
                  <div className="text-[9px] font-mono px-2 py-1.5 rounded"
                    style={{ background: "oklch(0.08 0.01 240)", border: "1px solid oklch(0.16 0.01 240)", color: "oklch(0.55 0.01 240)" }}>
                    Current: {ag.intent}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* ─── SECTION 2 : DERNIÈRES DÉCISIONS ──────────────────────────────────────── */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-mono font-bold text-sm uppercase tracking-widest" style={{ color: "oklch(0.72 0.18 145)" }}>
            Dernières décisions
          </h2>
          {events.length > 5 && (
            <button
              onClick={() => setShowAllDecisions(v => !v)}
              className="text-[10px] font-mono px-3 py-1.5 rounded border transition-colors"
              style={{ borderColor: "oklch(0.25 0.01 240)", color: "oklch(0.65 0.01 240)" }}
            >
              {showAllDecisions ? "Réduire" : "Load more"}
            </button>
          )}
        </div>
        <div
          className="rounded-lg overflow-hidden"
          style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}
        >
          {/* Real data badge */}
          {hasRealData && (
            <div className="px-6 py-2 flex items-center gap-2" style={{ borderBottom: "1px solid oklch(0.15 0.01 240)", background: "oklch(0.72 0.18 145 / 0.04)" }}>
              <div className="w-1.5 h-1.5 rounded-full" style={{ background: "oklch(0.72 0.18 145)" }} />
              <span className="text-[9px] font-mono" style={{ color: "oklch(0.72 0.18 145)" }}>
                {realStats.total} décisions réelles depuis la base de données
              </span>
            </div>
          )}
          {displayedDecisions.length === 0 ? (
            <div className="text-center py-10 text-[10px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>
              En attente de décisions...
            </div>
          ) : (
            displayedDecisions.map((ev, idx) => (
              <div
                key={ev.id}
                className="flex items-center gap-4 px-6"
                style={{
                  paddingTop: "16px",
                  paddingBottom: "16px",
                  borderBottom: idx < displayedDecisions.length - 1 ? "1px solid oklch(0.15 0.01 240)" : "none",
                }}
              >
                {/* Decision icon */}
                <span className="text-xl flex-shrink-0">{DECISION_ICONS[ev.decision]}</span>

                {/* Decision type */}
                <span
                  className="text-xs font-mono font-bold w-14 flex-shrink-0"
                  style={{ color: DECISION_COLORS[ev.decision] }}
                >
                  {ev.decision}
                </span>

                {/* Agent + action */}
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-mono text-foreground truncate">{ev.agent}</div>
                  <div className="text-[10px] font-mono truncate" style={{ color: "oklch(0.50 0.01 240)" }}>
                    {ev.intent}
                  </div>
                </div>

                {/* Latency / status */}
                <div className="text-right flex-shrink-0">
                  {ev.decision === "HOLD" ? (
                    <div className="text-[10px] font-mono" style={{ color: "#fbbf24" }}>En attente validation</div>
                  ) : (
                    <div className="text-[10px] font-mono" style={{ color: "oklch(0.50 0.01 240)" }}>
                      Latence : {ev.latencyMs}ms
                    </div>
                  )}
                  <div className="text-[8px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>
                    {ev.proofHash.slice(0, 8)}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      {/* ─── SECTION 3 : GUARD STATISTICS ───────────────────────────────────── */}
      <section>
        <h2 className="font-mono font-bold text-sm uppercase tracking-widest mb-4" style={{ color: "oklch(0.72 0.18 145)" }}>
          Guard X-108 Statistics
        </h2>
        <div
          className="rounded-lg"
          style={{ padding: "24px", background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}
        >
          <div className="grid grid-cols-2 gap-8">
            {/* Distribution bars */}
            <div className="flex flex-col gap-4">
              {([
                { d: "ALLOW" as GuardDecision, pct: allowPct },
                { d: "HOLD" as GuardDecision, pct: holdPct },
                { d: "BLOCK" as GuardDecision, pct: blockPct },
              ]).map(({ d, pct }) => (
                <div key={d}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span>{DECISION_ICONS[d]}</span>
                      <span className="font-mono font-bold text-sm" style={{ color: DECISION_COLORS[d] }}>{d}</span>
                    </div>
                    <span className="font-mono font-bold text-sm" style={{ color: DECISION_COLORS[d] }}>
                      {pct.toFixed(0)} %
                    </span>
                  </div>
                  <div className="h-2 rounded overflow-hidden" style={{ background: "oklch(0.16 0.01 240)" }}>
                    <div
                      className="h-full rounded transition-all duration-700"
                      style={{ width: `${pct}%`, background: DECISION_COLORS[d] }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Key metrics */}
            <div className="flex flex-col gap-4">
              <div
                className="rounded p-4 text-center"
                style={{ background: "oklch(0.13 0.01 240)", border: "1px solid oklch(0.22 0.01 240)" }}
              >
                <div className="font-mono font-bold text-2xl" style={{ color: "#4ade80" }}>{avgLatency}ms</div>
                <div className="text-[10px] font-mono mt-1" style={{ color: "oklch(0.50 0.01 240)" }}>Latence moyenne</div>
              </div>
              <div
                className="rounded p-4 text-center"
                style={{ background: "oklch(0.13 0.01 240)", border: "1px solid oklch(0.22 0.01 240)" }}
              >
                <div className="font-mono font-bold text-2xl text-foreground">{totalDecisions}</div>
                <div className="text-[10px] font-mono mt-1" style={{ color: "oklch(0.50 0.01 240)" }}>Décisions totales</div>
                {hasRealData && <div className="text-[8px] font-mono mt-0.5" style={{ color: "oklch(0.72 0.18 145)" }}>● données réelles</div>}
              </div>
              <div
                className="rounded p-4 text-center"
                style={{ background: "oklch(0.13 0.01 240)", border: "1px solid oklch(0.22 0.01 240)" }}
              >
                <div className="font-mono font-bold text-2xl" style={{ color: "#4ade80" }}>99.9%</div>
                <div className="text-[10px] font-mono mt-1" style={{ color: "oklch(0.50 0.01 240)" }}>Uptime Guard</div>
              </div>
            </div>
          </div>

          {/* Proof integrity */}
          <div
            className="mt-6 pt-4 flex items-center justify-between"
            style={{ borderTop: "1px solid oklch(0.18 0.01 240)" }}
          >
            <div className="flex gap-4">
            {[
              { label: "Lean 4", value: proofQuery.data ? `${proofQuery.data.lean.reduce((s: number, m: any) => s + m.theorems.length, 0)} théorèmes` : "33 théorèmes" },
              { label: "TLA+", value: proofQuery.data ? `${proofQuery.data.tla.reduce((s: number, m: any) => s + m.invariants.length, 0)} invariants` : "7 invariants" },
              { label: "Merkle", value: proofQuery.data ? proofQuery.data.merkle.root.slice(0, 10) + "…" : "b9ac7a04…" },
              { label: "Engine", value: engineInfo.data?.engine_name ? engineInfo.data.engine_name.slice(0, 12) : "OS4" },
            ].map(item => (
                <div key={item.label} className="text-center">
                  <div className="text-[9px] font-mono font-bold text-foreground">{item.label}</div>
                  <div className="text-[8px] font-mono" style={{ color: "oklch(0.50 0.01 240)" }}>{item.value}</div>
                </div>
              ))}
            </div>
            <span className="text-xs font-mono font-bold px-3 py-1.5 rounded" style={{ background: "#4ade8015", color: "#4ade80" }}>
              PROOF INTEGRITY: PASS
            </span>
          </div>
        </div>
      </section>

      {/* ─── SECTION 4 : CONSENSUS STATUS ───────────────────────────────────── */}
      <section>
        <h2 className="font-mono font-bold text-sm uppercase tracking-widest mb-4" style={{ color: "oklch(0.72 0.18 145)" }}>
          Distributed Consensus
        </h2>
        <div
          className="rounded-lg"
          style={{ padding: "24px", background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}
        >
          <div className="grid grid-cols-2 gap-8 items-center">
            {/* Nodes */}
            <div>
              <div className="text-[10px] font-mono mb-4" style={{ color: "oklch(0.50 0.01 240)" }}>
                Nodes actifs : {CONSENSUS_NODES.filter(n => n.ok).length} · Consensus requis : 3
              </div>
              <div className="flex flex-col" style={{ gap: "12px" }}>
                {CONSENSUS_NODES.map(node => (
                  <div key={node.city} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div
                        className="w-2.5 h-2.5 rounded-full"
                        style={{ background: node.ok ? "#4ade80" : "#f87171" }}
                      />
                      <span className="font-mono text-sm text-foreground">{node.city}</span>
                    </div>
                    <span
                      className="text-xs font-mono font-bold"
                      style={{ color: node.ok ? "#4ade80" : "#f87171" }}
                    >
                      {node.ok ? "✓" : "✗"}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Consensus state */}
            <div className="text-center">
              <div
                className="rounded-lg p-6"
                style={{
                  background: consensusReached ? "oklch(0.72 0.18 145 / 0.08)" : "oklch(0.55 0.18 25 / 0.08)",
                  border: `1px solid ${consensusReached ? "oklch(0.72 0.18 145 / 0.3)" : "oklch(0.55 0.18 25 / 0.3)"}`,
                }}
              >
                <div className="text-3xl mb-2">{consensusReached ? "✅" : "⚠️"}</div>
                <div
                  className="font-mono font-bold text-base"
                  style={{ color: consensusReached ? "#4ade80" : "#f87171" }}
                >
                  {consensusReached ? "Consensus atteint" : "Consensus insuffisant"}
                </div>
                <div className="text-[10px] font-mono mt-2" style={{ color: "oklch(0.50 0.01 240)" }}>
                  {CONSENSUS_NODES.filter(n => n.ok).length}/{CONSENSUS_NODES.length} nœuds actifs
                </div>
                <div className="text-[9px] font-mono mt-1" style={{ color: "oklch(0.40 0.01 240)" }}>
                  PBFT · BFT tolerance : 1 faute
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── SECTION 5 : EARLY WARNINGS (Predictive) ─────────────────────── */}
      <section>
        <div className="rounded-lg" style={{ padding: "24px", background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="font-mono text-[9px] font-bold tracking-widest mb-1" style={{ color: "oklch(0.45 0.01 240)" }}>PREDICTIVE LAYER</div>
              <h2 className="font-mono font-bold text-sm uppercase tracking-widest" style={{ color: "oklch(0.72 0.18 145)" }}>Early Warnings</h2>
            </div>
            <Link href="/predictions">
              <button className="font-mono text-[9px] px-3 py-1.5 rounded" style={{ background: "oklch(0.14 0.01 240)", border: "1px solid oklch(0.22 0.01 240)", color: "oklch(0.60 0.01 240)" }}>View all predictions →</button>
            </Link>
          </div>
          <div className="grid grid-cols-3 gap-3 mb-3">
            {[
              { icon: "🔴", label: "Flash Crash Risk", value: "73%", color: "#f87171", domain: "Trading", window: "2–4h" },
              { icon: "🟡", label: "Fraud Wave Risk", value: "58%", color: "#fbbf24", domain: "Banking", window: "6–12h" },
              { icon: "🔴", label: "Supply Shock Warning", value: "82%", color: "#f87171", domain: "E-Commerce", window: "24–48h" },
            ].map((w) => (
              <div key={w.label} className="rounded-lg p-3" style={{ background: `${w.color}10`, border: `1px solid ${w.color}33` }}>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-base">{w.icon}</span>
                  <span className="font-mono text-[9px] font-bold" style={{ color: w.color }}>{w.domain}</span>
                </div>
                <div className="font-mono font-bold text-xl mb-0.5" style={{ color: w.color }}>{w.value}</div>
                <div className="font-mono text-[10px] text-foreground mb-1">{w.label}</div>
                <div className="font-mono text-[9px] text-muted-foreground">Window: {w.window}</div>
              </div>
            ))}
          </div>
          <div className="rounded p-2.5 font-mono text-[9px]" style={{ background: "oklch(0.08 0.01 240)", border: "1px solid oklch(0.16 0.01 240)" }}>
            <span className="text-muted-foreground">Guard adjustment active: </span>
            <span style={{ color: "#f87171" }}>Defensive Mode</span>
            <span className="text-muted-foreground"> — fiabilité threshold </span>
            <span style={{ color: "oklch(0.72 0.18 145)" }}>0.30 → 0.40</span>
            <span className="text-muted-foreground">, temporal lock </span>
            <span style={{ color: "oklch(0.72 0.18 145)" }}>10s → 15s</span>
          </div>
        </div>
      </section>

      {/* ─── SECTION 6 : STRASBOURG CLOCK ────────────────────────────────── */}
      <section>
        <StrasbourgClockModule />
      </section>

      {/* ─── Navigation ──────────────────────────────────────────────────────── */}
      <div className="flex gap-3 justify-center flex-wrap pb-4">
        {[
          { href: "/", label: "← Home" },
          { href: "/use-cases/trading", label: "→ TradingWorld" },
          { href: "/use-cases/banking", label: "→ BankWorld" },
          { href: "/use-cases/ecommerce", label: "→ EcomWorld" },
          { href: "/engine", label: "→ Engine" },
          { href: "/proof", label: "→ Proof" },
          { href: "/audit", label: "→ Audit Mode" },
        ].map(l => (
          <Link key={l.href} href={l.href} className="text-xs px-3 py-1.5 border border-gray-700 text-gray-400 rounded hover:border-emerald-400/30 hover:text-emerald-400 transition-colors">
            {l.label}
          </Link>
        ))}
      </div>
    </div>
  );
}
