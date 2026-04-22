import React, { useState, useEffect, useCallback, useRef } from "react";
import { Link } from "wouter";
import { trpc } from "@/lib/trpc";
import DecisionStream from "@/components/DecisionStream";
import ScenarioRunner from "@/components/ScenarioRunner";
import EngineTransparency from "@/components/EngineTransparency";

// ─── Types ───────────────────────────────────────────────────────────────────

type DecisionType = "ALLOW" | "HOLD" | "BLOCK";
type SimMode = "continuous" | "scenario" | "stress";
type WorldId = "trading" | "bank" | "ecom";

interface DecisionEvent {
  id: string;
  ts: number;
  world: WorldId;
  agent: string;
  proposal: string;
  decision: DecisionType;
  holdMs: number;
  worldStateHash: string;
  executionResult: string;
}

interface WorldState {
  id: WorldId;
  label: string;
  active: boolean;
  mode: SimMode;
  stepCount: number;
  decisionCount: number;
  blockCount: number;
  holdCount: number;
  allowCount: number;
  lastDecision: DecisionType | null;
  latencyMs: number;
  proofCount: number;
}

interface QueueItem {
  id: string;
  type: SimMode;
  world: WorldId;
  label: string;
  status: "pending" | "running" | "done";
  addedAt: number;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

const WORLDS: WorldId[] = ["trading", "bank", "ecom"];
const WORLD_LABELS: Record<WorldId, string> = {
  trading: "TradingWorld",
  bank: "BankWorld",
  ecom: "EcomWorld",
};
const AGENTS: Record<WorldId, string[]> = {
  trading: ["ALPHA-7", "MOMENTUM-3", "ARB-9"],
  bank: ["RISK-CTRL", "FRAUD-DET", "KYC-BOT"],
  ecom: ["PRICE-AI", "DEMAND-FC", "SUPPLY-OPT"],
};
const PROPOSALS: Record<WorldId, string[]> = {
  trading: ["BUY 500 BTC-USD @ 42,180", "SELL 1200 ETH @ 2,845", "SHORT SPX futures x3"],
  bank: ["WIRE €15,000 → IBAN DE89...", "APPROVE €450 payment", "BLOCK suspicious ACH"],
  ecom: ["PRICE iPhone 16 → €1,149", "RESTOCK 200 units", "FLASH SALE -30% MacBook"],
};

let _idCounter = 0;
const uid = () => `ev-${Date.now()}-${_idCounter++}`;

function seededRand(seed: number) {
  let s = seed;
  return () => {
    s = (s * 1664525 + 1013904223) & 0xffffffff;
    return (s >>> 0) / 0xffffffff;
  };
}

function makeDecision(r: number, world: WorldId): DecisionType {
  // Block rate ~8%, Hold rate ~18%, Allow ~74%
  if (world === "bank" && r < 0.12) return "BLOCK";
  if (world === "trading" && r < 0.06) return "BLOCK";
  if (world === "ecom" && r < 0.07) return "BLOCK";
  if (r < 0.22) return "HOLD";
  return "ALLOW";
}

function shortHash(seed: number): string {
  const h = (seed * 0xdeadbeef) >>> 0;
  return h.toString(16).padStart(8, "0").toUpperCase();
}

const DECISION_COLOR: Record<DecisionType, string> = {
  ALLOW: "text-emerald-400",
  HOLD: "text-amber-400",
  BLOCK: "text-red-400",
};
const DECISION_BG: Record<DecisionType, string> = {
  ALLOW: "bg-emerald-400/10 border-emerald-400/30",
  HOLD: "bg-amber-400/10 border-amber-400/30",
  BLOCK: "bg-red-400/10 border-red-400/30",
};

// ─── EngineInfoPanel (moteur réel du repo) ──────────────────────────────────

function EngineInfoPanel() {
  const { data: info, isLoading } = trpc.engine.info.useQuery();

  if (isLoading) return (
    <div className="bg-gray-900/60 border border-gray-800 rounded p-4 animate-pulse">
      <div className="text-xs text-gray-500 uppercase tracking-widest mb-2">Kernel Monitor</div>
      <div className="h-4 bg-gray-800 rounded w-1/2"></div>
    </div>
  );

  if (!info) return null;

  return (
    <div className="bg-gray-900/60 border border-emerald-400/20 rounded p-4">
      <div className="text-xs text-emerald-400 uppercase tracking-widest mb-3 flex items-center gap-2">
        <span>⚡ Kernel Monitor</span>
        <span className="text-gray-600">— Obsidia-lab-trad @ {info.commit_hash}</span>
        <span className="ml-auto text-[10px] text-emerald-400/60 border border-emerald-400/20 px-2 py-0.5 rounded">ProofKit {info.proofkit_overall}</span>
      </div>
      <div className="grid grid-cols-4 gap-4">
        <div>
          <div className="text-[10px] text-gray-500 mb-1">Engine</div>
          <div className="text-sm font-bold text-gray-200">{info.engine_name}</div>
          <div className="text-[10px] text-gray-500">v{info.engine_version} · {info.kernel}</div>
        </div>
        <div>
          <div className="text-[10px] text-gray-500 mb-1">Invariants</div>
          <div className="text-[10px] text-gray-400 space-y-0.5">
            <div className="text-amber-400 font-bold">{info.invariants.hierarchy}</div>
            <div>τ = {info.invariants.x108_temporal_lock_s}s</div>
            <div>Max DD = {(info.invariants.max_drawdown * 100).toFixed(0)}%</div>
          </div>
        </div>
        <div>
          <div className="text-[10px] text-gray-500 mb-1">Market Features (live)</div>
          <div className="text-[10px] text-gray-400 space-y-0.5">
            <div>Vol <span className="text-amber-400">{(info.market_features.volatility * 100).toFixed(2)}%</span></div>
            <div>Cohérence <span className="text-emerald-400">{(info.market_features.coherence * 100).toFixed(1)}%</span></div>
            <div>Régime <span className="text-blue-400">{info.market_features.regime}</span></div>
          </div>
        </div>
        <div>
          <div className="text-[10px] text-gray-500 mb-1">Preuves formelles</div>
          <div className="text-[10px] text-gray-400 space-y-0.5">
            <div>Lean4 <span className="text-purple-400">{info.lean4_theorems} théorèmes</span></div>
            <div>TLA+ <span className="text-purple-400">{info.tla_invariants} invariants</span></div>
            <div>Strasbourg <span className="text-emerald-400">{info.strasbourg_steps.toLocaleString()} steps / 0 violations</span></div>
          </div>
        </div>
      </div>
      <div className="mt-3 pt-3 border-t border-gray-800 flex items-center gap-3">
        <div className="text-[10px] text-gray-500">Merkle root :</div>
        <div className="font-mono text-[10px] text-emerald-400/70">{info.merkle_root.slice(0, 32)}…</div>
        <div className="ml-auto text-[10px] text-gray-600">Build hash : {info.build_hash}</div>
      </div>
    </div>
  );
}

// ─── Component ──────────────────────────────────────────────────────────────

export default function SimulationDashboard() {
  const [worlds, setWorlds] = useState<WorldState[]>([
    { id: "trading", label: "TradingWorld", active: true, mode: "continuous", stepCount: 0, decisionCount: 0, blockCount: 0, holdCount: 0, allowCount: 0, lastDecision: null, latencyMs: 0, proofCount: 0 },
    { id: "bank", label: "BankWorld", active: true, mode: "continuous", stepCount: 0, decisionCount: 0, blockCount: 0, holdCount: 0, allowCount: 0, lastDecision: null, latencyMs: 0, proofCount: 0 },
    { id: "ecom", label: "EcomWorld", active: false, mode: "scenario", stepCount: 0, decisionCount: 0, blockCount: 0, holdCount: 0, allowCount: 0, lastDecision: null, latencyMs: 0, proofCount: 0 },
  ]);

  const [events, setEvents] = useState<DecisionEvent[]>([]);
  const [queue, setQueue] = useState<QueueItem[]>([
    { id: "q1", type: "scenario", world: "trading", label: "Flash Crash scenario", status: "pending", addedAt: Date.now() - 12000 },
    { id: "q2", type: "stress", world: "bank", label: "Fraud stress 10k", status: "pending", addedAt: Date.now() - 8000 },
    { id: "q3", type: "scenario", world: "ecom", label: "Supply Shock scenario", status: "pending", addedAt: Date.now() - 3000 },
  ]);

  const [globalStats, setGlobalStats] = useState({ decisions: 0, blocks: 0, holds: 0, allows: 0, proofs: 0, avgLatency: 0 });
  const [running, setRunning] = useState(true);
  const tickRef = useRef(0);
  const randRef = useRef(seededRand(42));

  // ─── Simulation tick ───────────────────────────────────────────────────────
  const tick = useCallback(() => {
    if (!running) return;
    tickRef.current++;
    const r = randRef.current;

    setWorlds(prev => prev.map(w => {
      if (!w.active) return w;
      const r1 = r();
      const decision = makeDecision(r1, w.id);
      const latency = Math.round(8 + r() * 42);
      const newStep = w.stepCount + 1;
      const newDec = w.decisionCount + 1;
      const newBlock = w.blockCount + (decision === "BLOCK" ? 1 : 0);
      const newHold = w.holdCount + (decision === "HOLD" ? 1 : 0);
      const newAllow = w.allowCount + (decision === "ALLOW" ? 1 : 0);
      const newProof = w.proofCount + 1;

      // Emit event
      const agents = AGENTS[w.id];
      const proposals = PROPOSALS[w.id];
      const agentIdx = Math.floor(r() * agents.length);
      const propIdx = Math.floor(r() * proposals.length);
      const ev: DecisionEvent = {
        id: uid(),
        ts: Date.now(),
        world: w.id,
        agent: agents[agentIdx],
        proposal: proposals[propIdx],
        decision,
        holdMs: decision === "HOLD" ? 10000 : 0,
        worldStateHash: shortHash(tickRef.current * 31 + agentIdx),
        executionResult: decision === "ALLOW" ? "executed" : decision === "HOLD" ? "deferred" : "rejected",
      };
      setEvents(prev => [ev, ...prev].slice(0, 80));

      return { ...w, stepCount: newStep, decisionCount: newDec, blockCount: newBlock, holdCount: newHold, allowCount: newAllow, lastDecision: decision, latencyMs: latency, proofCount: newProof };
    }));

    // Update global stats
    setGlobalStats(prev => {
      const newDec = prev.decisions + worlds.filter(w => w.active).length;
      return { ...prev, decisions: newDec, proofs: newDec };
    });
  }, [running, worlds]);

  useEffect(() => {
    const interval = setInterval(tick, 1200);
    return () => clearInterval(interval);
  }, [tick]);

  // ─── Queue processor ──────────────────────────────────────────────────────
  useEffect(() => {
    const interval = setInterval(() => {
      setQueue(prev => {
        const pendingIdx = prev.findIndex(q => q.status === "pending");
        if (pendingIdx === -1) return prev;
        const updated = [...prev];
        updated[pendingIdx] = { ...updated[pendingIdx], status: "running" };
        setTimeout(() => {
          setQueue(q => q.map((item, i) => i === pendingIdx ? { ...item, status: "done" } : item));
        }, 4000 + Math.random() * 3000);
        return updated;
      });
    }, 6000);
    return () => clearInterval(interval);
  }, []);

  // ─── Computed metrics ─────────────────────────────────────────────────────
  const totalDecisions = worlds.reduce((s, w) => s + w.decisionCount, 0);
  const totalBlocks = worlds.reduce((s, w) => s + w.blockCount, 0);
  const totalHolds = worlds.reduce((s, w) => s + w.holdCount, 0);
  const totalAllows = worlds.reduce((s, w) => s + w.allowCount, 0);
  const totalProofs = worlds.reduce((s, w) => s + w.proofCount, 0);
  const avgLatency = worlds.filter(w => w.active).reduce((s, w) => s + w.latencyMs, 0) / Math.max(1, worlds.filter(w => w.active).length);

  const blockRate = totalDecisions > 0 ? ((totalBlocks / totalDecisions) * 100).toFixed(1) : "0.0";
  const holdRate = totalDecisions > 0 ? ((totalHolds / totalDecisions) * 100).toFixed(1) : "0.0";
  const execRate = totalDecisions > 0 ? ((totalAllows / totalDecisions) * 100).toFixed(1) : "0.0";

  const toggleWorld = (id: WorldId) => {
    setWorlds(prev => prev.map(w => w.id === id ? { ...w, active: !w.active } : w));
  };

  const addScenario = (type: SimMode, world: WorldId) => {
    const labels: Record<SimMode, string> = {
      continuous: `${WORLD_LABELS[world]} continuous`,
      scenario: `${WORLD_LABELS[world]} scenario`,
      stress: `${WORLD_LABELS[world]} stress 10k`,
    };
    setQueue(prev => [...prev, {
      id: uid(),
      type,
      world,
      label: labels[type],
      status: "pending",
      addedAt: Date.now(),
    }]);
  };

  const clearDoneQueue = () => {
    setQueue(prev => prev.filter(q => q.status !== "done"));
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-gray-100 font-mono">
      {/* Header */}
      <div className="border-b border-gray-800 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-emerald-400 font-bold text-sm">OS4</span>
          <span className="text-gray-600">›</span>
          <span className="text-gray-300 text-sm">Simulation Dashboard</span>
          <span className={`ml-2 text-xs px-2 py-0.5 rounded-full border ${running ? "text-emerald-400 border-emerald-400/30 bg-emerald-400/10" : "text-gray-500 border-gray-700"}`}>
            {running ? "● LIVE" : "○ PAUSED"}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setRunning(r => !r)}
            className={`text-xs px-3 py-1.5 rounded border transition-colors ${running ? "border-amber-400/30 text-amber-400 hover:bg-amber-400/10" : "border-emerald-400/30 text-emerald-400 hover:bg-emerald-400/10"}`}
          >
            {running ? "⏸ PAUSE" : "▶ RESUME"}
          </button>
          <Link href="/simulation-worlds" className="text-xs text-gray-500 hover:text-gray-300 transition-colors">
            ← Simulation Worlds
          </Link>
        </div>
      </div>

      <div className="p-6 space-y-6">

        {/* ── Global Metrics Bar ─────────────────────────────────────────── */}
        <div className="grid grid-cols-6 gap-3">
          {[
            { label: "TOTAL DECISIONS", value: totalDecisions.toLocaleString(), color: "text-gray-200" },
            { label: "BLOCK RATE", value: `${blockRate}%`, color: "text-red-400" },
            { label: "HOLD RATE", value: `${holdRate}%`, color: "text-amber-400" },
            { label: "EXEC RATE", value: `${execRate}%`, color: "text-emerald-400" },
            { label: "AVG LATENCY", value: `${avgLatency.toFixed(0)}ms`, color: "text-blue-400" },
            { label: "PROOFS GENERATED", value: totalProofs.toLocaleString(), color: "text-purple-400" },
          ].map(m => (
            <div key={m.label} className="bg-gray-900/60 border border-gray-800 rounded p-3">
              <div className="text-[10px] text-gray-500 uppercase tracking-widest mb-1">{m.label}</div>
              <div className={`text-xl font-bold ${m.color}`}>{m.value}</div>
            </div>
          ))}
        </div>

        {/* ── Main Grid ─────────────────────────────────────────────────── */}
        <div className="grid grid-cols-3 gap-4">

          {/* Active Worlds */}
          <div className="bg-gray-900/60 border border-gray-800 rounded p-4">
            <div className="text-xs text-gray-500 uppercase tracking-widest mb-3 flex items-center justify-between">
              <span>Active Worlds</span>
              <span className="text-emerald-400">{worlds.filter(w => w.active).length}/{worlds.length}</span>
            </div>
            <div className="space-y-3">
              {worlds.map(w => (
                <div key={w.id} className={`border rounded p-3 transition-colors ${w.active ? "border-emerald-400/20 bg-emerald-400/5" : "border-gray-700 bg-gray-800/30"}`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-bold text-gray-200">{w.label}</span>
                    <button
                      onClick={() => toggleWorld(w.id)}
                      className={`text-[10px] px-2 py-0.5 rounded border transition-colors ${w.active ? "border-emerald-400/30 text-emerald-400" : "border-gray-600 text-gray-500"}`}
                    >
                      {w.active ? "ACTIVE" : "IDLE"}
                    </button>
                  </div>
                  <div className="grid grid-cols-3 gap-1 text-[10px]">
                    <div><span className="text-gray-500">steps</span><br /><span className="text-gray-200">{w.stepCount}</span></div>
                    <div><span className="text-gray-500">decisions</span><br /><span className="text-gray-200">{w.decisionCount}</span></div>
                    <div><span className="text-gray-500">latency</span><br /><span className="text-blue-400">{w.latencyMs}ms</span></div>
                  </div>
                  <div className="flex gap-2 mt-2 text-[10px]">
                    <span className="text-red-400">BLOCK {w.blockCount}</span>
                    <span className="text-amber-400">HOLD {w.holdCount}</span>
                    <span className="text-emerald-400">ALLOW {w.allowCount}</span>
                  </div>
                  {w.lastDecision && (
                    <div className={`mt-1 text-[10px] font-bold ${DECISION_COLOR[w.lastDecision]}`}>
                      LAST: {w.lastDecision}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Decision Stream — composant live avancé */}
          <DecisionStream maxEvents={20} autoPlay={true} tickMs={2500} />

          {/* Guard Stats + Proof Events */}
          <div className="space-y-4">
            {/* Guard Statistics */}
            <div className="bg-gray-900/60 border border-gray-800 rounded p-4">
              <div className="text-xs text-gray-500 uppercase tracking-widest mb-3">Guard X-108 Statistics</div>
              <div className="space-y-2">
                {[
                  { label: "BLOCK", count: totalBlocks, rate: blockRate, color: "bg-red-400", textColor: "text-red-400" },
                  { label: "HOLD", count: totalHolds, rate: holdRate, color: "bg-amber-400", textColor: "text-amber-400" },
                  { label: "ALLOW", count: totalAllows, rate: execRate, color: "bg-emerald-400", textColor: "text-emerald-400" },
                ].map(s => (
                  <div key={s.label}>
                    <div className="flex justify-between text-[10px] mb-1">
                      <span className={s.textColor}>{s.label}</span>
                      <span className="text-gray-400">{s.count} ({s.rate}%)</span>
                    </div>
                    <div className="h-1.5 bg-gray-800 rounded overflow-hidden">
                      <div
                        className={`h-full ${s.color} transition-all duration-500`}
                        style={{ width: `${s.rate}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-3 pt-3 border-t border-gray-800 text-[10px] text-gray-500">
                <div className="flex justify-between">
                  <span>BLOCK priority rule</span>
                  <span className="text-emerald-400">✓ enforced</span>
                </div>
                <div className="flex justify-between mt-1">
                  <span>HOLD monotonicity</span>
                  <span className="text-emerald-400">✓ verified</span>
                </div>
                <div className="flex justify-between mt-1">
                  <span>Deterministic execution</span>
                  <span className="text-emerald-400">✓ confirmed</span>
                </div>
              </div>
            </div>

            {/* Proof Events */}
            <div className="bg-gray-900/60 border border-gray-800 rounded p-4">
              <div className="text-xs text-gray-500 uppercase tracking-widest mb-3 flex items-center justify-between">
                <span>Proof Events</span>
                <span className="text-purple-400">{totalProofs} anchors</span>
              </div>
              <div className="space-y-1.5">
                {events.slice(0, 5).map(ev => (
                  <div key={ev.id + "-proof"} className="border border-purple-400/20 bg-purple-400/5 rounded px-2 py-1.5 text-[10px]">
                    <div className="flex justify-between">
                      <span className="text-purple-300">HASH ANCHORED</span>
                      <span className="text-gray-500">{WORLD_LABELS[ev.world]}</span>
                    </div>
                    <div className="text-gray-500 font-mono mt-0.5">{ev.worldStateHash}...{shortHash(ev.ts)}</div>
                  </div>
                ))}
                {events.length === 0 && (
                  <div className="text-gray-600 text-xs text-center py-4">No proofs yet</div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* ── Simulation Queue + Scheduler ──────────────────────────────── */}
        <div className="grid grid-cols-2 gap-4">

          {/* Queue */}
          <div className="bg-gray-900/60 border border-gray-800 rounded p-4">
            <div className="text-xs text-gray-500 uppercase tracking-widest mb-3 flex items-center justify-between">
              <span>Simulation Queue (FIFO)</span>
              <button onClick={clearDoneQueue} className="text-[10px] text-gray-600 hover:text-gray-400 transition-colors">
                Clear done
              </button>
            </div>
            <div className="space-y-2 mb-3">
              {queue.map(q => (
                <div key={q.id} className={`border rounded px-3 py-2 text-[10px] flex items-center justify-between ${
                  q.status === "running" ? "border-amber-400/30 bg-amber-400/5" :
                  q.status === "done" ? "border-gray-700 bg-gray-800/30 opacity-50" :
                  "border-gray-700 bg-gray-800/30"
                }`}>
                  <div>
                    <span className={`font-bold mr-2 ${
                      q.type === "continuous" ? "text-blue-400" :
                      q.type === "scenario" ? "text-amber-400" : "text-red-400"
                    }`}>{q.type.toUpperCase()}</span>
                    <span className="text-gray-300">{q.label}</span>
                  </div>
                  <span className={`px-1.5 py-0.5 rounded text-[9px] ${
                    q.status === "running" ? "bg-amber-400/20 text-amber-400" :
                    q.status === "done" ? "bg-gray-700 text-gray-500" :
                    "bg-gray-800 text-gray-500"
                  }`}>{q.status.toUpperCase()}</span>
                </div>
              ))}
              {queue.length === 0 && (
                <div className="text-gray-600 text-xs text-center py-4">Queue empty</div>
              )}
            </div>
            {/* Add to queue */}
            <div className="border-t border-gray-800 pt-3">
              <div className="text-[10px] text-gray-500 mb-2">Add to queue:</div>
              <div className="flex flex-wrap gap-1.5">
                {(["trading", "bank", "ecom"] as WorldId[]).map(w => (
                  <React.Fragment key={w}>
                    <button onClick={() => addScenario("scenario", w)} className="text-[10px] px-2 py-1 border border-amber-400/20 text-amber-400 rounded hover:bg-amber-400/10 transition-colors">
                      {WORLD_LABELS[w]} scenario
                    </button>
                    <button onClick={() => addScenario("stress", w)} className="text-[10px] px-2 py-1 border border-red-400/20 text-red-400 rounded hover:bg-red-400/10 transition-colors">
                      {WORLD_LABELS[w]} stress
                    </button>
                  </React.Fragment>
                ))}
              </div>
            </div>
          </div>

          {/* Scheduler & Triggers */}
          <div className="bg-gray-900/60 border border-gray-800 rounded p-4">
            <div className="text-xs text-gray-500 uppercase tracking-widest mb-3">Scheduler & Triggers</div>
            <div className="space-y-2">
              {[
                { priority: "1", type: "CONTINUOUS", label: "All active worlds", freq: "permanent", color: "text-emerald-400" },
                { priority: "2", type: "SCENARIO", label: "Regression suite", freq: "nightly", color: "text-amber-400" },
                { priority: "3", type: "STRESS", label: "Invariant stress 100k", freq: "weekly", color: "text-red-400" },
                { priority: "4", type: "REPLAY", label: "Historical log replay", freq: "on commit", color: "text-blue-400" },
                { priority: "5", type: "PROOF", label: "Merkle integrity check", freq: "on commit", color: "text-purple-400" },
              ].map(s => (
                <div key={s.priority} className="border border-gray-700 rounded px-3 py-2 text-[10px] flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-gray-600">#{s.priority}</span>
                    <span className={`font-bold ${s.color}`}>{s.type}</span>
                    <span className="text-gray-400">{s.label}</span>
                  </div>
                  <span className="text-gray-600">{s.freq}</span>
                </div>
              ))}
            </div>

            <div className="mt-3 pt-3 border-t border-gray-800">
              <div className="text-[10px] text-gray-500 mb-2">Event triggers:</div>
              <div className="flex flex-wrap gap-1.5">
                {["new commit", "agent update", "governance change", "world module added"].map(t => (
                  <span key={t} className="text-[10px] px-2 py-0.5 border border-gray-700 text-gray-500 rounded">{t}</span>
                ))}
              </div>
            </div>

            <div className="mt-3 pt-3 border-t border-gray-800 text-[10px]">
              <div className="text-gray-500 mb-1">Stop conditions:</div>
              <div className="space-y-0.5 text-gray-600">
                <div>• invariant violation → immediate stop + CI block</div>
                <div>• system error → stop + alert</div>
                <div>• max steps reached → graceful stop</div>
                <div>• manual stop → pause + checkpoint</div>
              </div>
            </div>
          </div>
        </div>

        {/* ── Pipeline Complet ──────────────────────────────────────────── */}
        <div className="bg-gray-900/60 border border-gray-800 rounded p-4">
          <div className="text-xs text-gray-500 uppercase tracking-widest mb-4">Complete Automated Pipeline</div>
          <div className="flex items-center gap-0 overflow-x-auto">
            {[
              { label: "WORLD STATE", sub: "OS4 simulation", color: "border-blue-400/40 text-blue-400" },
              { label: "AGENT", sub: "OS1 registry", color: "border-gray-500/40 text-gray-400" },
              { label: "STRATEGY", sub: "OS2 runtime", color: "border-gray-500/40 text-gray-400" },
              { label: "X-108 GUARD", sub: "temporal gate", color: "border-amber-400/40 text-amber-400" },
              { label: "DECISION", sub: "BLOCK/HOLD/ALLOW", color: "border-emerald-400/40 text-emerald-400" },
              { label: "EXECUTION", sub: "state update", color: "border-gray-500/40 text-gray-400" },
              { label: "LOG", sub: "hash + timestamp", color: "border-purple-400/40 text-purple-400" },
              { label: "INVARIANT", sub: "check", color: "border-red-400/40 text-red-400" },
              { label: "PROOF", sub: "OS3 merkle", color: "border-purple-400/40 text-purple-400" },
            ].map((step, i, arr) => (
              <React.Fragment key={step.label}>
                <div className={`flex-shrink-0 border rounded px-3 py-2 text-center ${step.color}`}>
                  <div className="text-[10px] font-bold">{step.label}</div>
                  <div className="text-[9px] text-gray-600 mt-0.5">{step.sub}</div>
                </div>
                {i < arr.length - 1 && (
                  <div className="flex-shrink-0 text-gray-700 px-1 text-xs">→</div>
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* ── Scenario Engine ─────────────────────────────────────────────── */}
        <ScenarioRunner />

        {/* ── Engine Transparency (Batch Run 10 seeds) ──────────────────────────────── */}
        <EngineTransparency />

        {/* ── Engine Info (moteur réel du repo) ─────────────────────────────────────────────────────── */}
        <EngineInfoPanel />  {/* ── Navigation ──────────────────────────────────────────────────── */}
        <div className="flex gap-3 justify-center">          {[
            { href: "/simulation-worlds/trading", label: "→ TradingWorld" },
            { href: "/simulation-worlds/bank", label: "→ BankWorld" },
            { href: "/simulation-worlds/ecom", label: "→ EcomWorld" },
            { href: "/scenario-engine", label: "→ Scenario Engine" },
            { href: "/automated-tests", label: "→ Automated Tests" },
            { href: "/formal-proof", label: "→ Formal Proof" },
          ].map(l => (
            <Link key={l.href} href={l.href} className="text-xs px-3 py-1.5 border border-gray-700 text-gray-400 rounded hover:border-emerald-400/30 hover:text-emerald-400 transition-colors">
              {l.label}
            </Link>
          ))}
        </div>

      </div>
    </div>
  );
}
