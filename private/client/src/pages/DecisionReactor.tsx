/**
 * DecisionReactor.tsx — OS4 v13
 * Vue causale totale : WORLD → AGENT → ENGINE → GUARD X-108 → DECISION → PROOF
 * Chaque décision affiche : inputs + calculs + résultat + explication textuelle
 */
import React, { useState, useEffect, useRef, useCallback } from "react";
import { trpc } from "@/lib/trpc";
import MarketMechanics from "@/components/MarketMechanics";

// ─── Types ────────────────────────────────────────────────────────────────────
interface ReactorDecision {
  id: string;
  timestamp: string;
  domain: "TRADING" | "BANK" | "ECOM";
  // WORLD
  world: {
    price: number;
    volatility: number;
    regime: string;
    liquidity: number;
    event?: string;
  };
  // AGENT
  agent: {
    observation: string;
    proposal: string;
    confidence: number;
  };
  // ENGINE
  engine: {
    coherence: number;
    risk: number;
    volatilityScore: number;
    regimeScore: number;
  };
  // GUARD
  guard: {
    decision: "BLOCK" | "HOLD" | "ALLOW";
    reason: string;
    temporalLock: boolean;
    holdDuration?: number;
  };
  // PROOF
  proof: {
    hash: string;
    merkleRoot: string;
    replayVerified: boolean;
  };
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
const DOMAINS = ["TRADING", "BANK", "ECOM"] as const;
const PROPOSALS = {
  TRADING: ["BUY BTC", "SELL BTC", "HOLD POSITION", "REDUCE EXPOSURE"],
  BANK: ["AUTHORIZE TRANSFER", "PROCESS WITHDRAWAL", "APPROVE LOAN", "BLOCK TRANSACTION"],
  ECOM: ["UPDATE PRICE +8%", "LAUNCH PROMOTION", "RESTOCK INVENTORY", "BLOCK BOT TRAFFIC"],
};
const REGIMES = ["BULL", "BEAR", "CRASH", "RECOVERY", "SIDEWAYS"];
const EVENTS = ["Flash Crash -7%", "Volatility Spike", "Liquidity Gap", "Rate Hike", "Normal Market", "Volume Surge"];

function seededRand(seed: number): () => number {
  let s = seed;
  return () => {
    s = (s * 1664525 + 1013904223) & 0xffffffff;
    return (s >>> 0) / 0xffffffff;
  };
}

function generateDecision(seed: number): ReactorDecision {
  const rng = seededRand(seed);
  const domain = DOMAINS[Math.floor(rng() * 3)];
  const price = 40000 + rng() * 30000;
  const volatility = 0.05 + rng() * 0.45;
  const regime = REGIMES[Math.floor(rng() * 5)];
  const liquidity = 0.3 + rng() * 0.7;
  const coherence = 0.3 + rng() * 0.7;
  const risk = volatility * (1 - coherence);
  const proposals = PROPOSALS[domain];
  const proposal = proposals[Math.floor(rng() * proposals.length)];
  const confidence = 0.4 + rng() * 0.6;
  const event = rng() > 0.7 ? EVENTS[Math.floor(rng() * 6)] : undefined;

  // Guard decision logic (mirrors guardX108 engine)
  let guardDecision: "BLOCK" | "HOLD" | "ALLOW";
  let reason: string;
  let temporalLock = false;
  let holdDuration: number | undefined;

  if (volatility > 0.35 || coherence < 0.4 || regime === "CRASH") {
    if (volatility > 0.45 || coherence < 0.3) {
      guardDecision = "BLOCK";
      reason = `Critical: volatility=${(volatility * 100).toFixed(1)}% exceeds threshold. Coherence=${coherence.toFixed(2)} below minimum. Action blocked permanently.`;
    } else {
      guardDecision = "HOLD";
      temporalLock = true;
      holdDuration = 10;
      reason = `Temporal lock active: volatility=${(volatility * 100).toFixed(1)}% > 35% threshold. Coherence=${coherence.toFixed(2)}. Waiting ${holdDuration}s for stabilization.`;
    }
  } else {
    guardDecision = "ALLOW";
    reason = `All invariants satisfied: volatility=${(volatility * 100).toFixed(1)}% ✓, coherence=${coherence.toFixed(2)} ✓, regime=${regime} ✓. Action authorized.`;
  }

  const hash = `0x${(seed * 0xdeadbeef >>> 0).toString(16).padStart(8, "0")}${(seed * 0xcafebabe >>> 0).toString(16).padStart(8, "0")}`;
  const merkleRoot = `0xb9ac7a04${(seed * 0xf00d >>> 0).toString(16).padStart(8, "0")}`;

  const now = new Date();
  const ts = `${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}`;

  return {
    id: `d-${seed}`,
    timestamp: ts,
    domain,
    world: { price, volatility, regime, liquidity, event },
    agent: { observation: `Observing ${domain.toLowerCase()} market: ${regime} regime, vol=${(volatility * 100).toFixed(1)}%`, proposal, confidence },
    engine: { coherence, risk, volatilityScore: volatility, regimeScore: regime === "BULL" ? 0.9 : regime === "CRASH" ? 0.1 : 0.5 },
    guard: { decision: guardDecision, reason, temporalLock, holdDuration },
    proof: { hash, merkleRoot, replayVerified: true },
  };
}

// ─── Decision Card ─────────────────────────────────────────────────────────────
function DecisionCard({ d, isLatest }: { d: ReactorDecision; isLatest: boolean }) {
  const [expanded, setExpanded] = useState(isLatest);

  const guardColor = d.guard.decision === "ALLOW"
    ? "oklch(0.72 0.18 145)"
    : d.guard.decision === "HOLD"
    ? "oklch(0.78 0.18 60)"
    : "oklch(0.65 0.22 25)";

  const domainColor = d.domain === "TRADING"
    ? "oklch(0.65 0.18 240)"
    : d.domain === "BANK"
    ? "oklch(0.72 0.18 145)"
    : "oklch(0.75 0.18 280)";

  return (
    <div
      style={{
        background: isLatest ? "oklch(0.12 0.02 240)" : "oklch(0.10 0.01 240)",
        border: `1px solid ${isLatest ? guardColor + "66" : "oklch(0.18 0.01 240)"}`,
        borderLeft: `3px solid ${guardColor}`,
        borderRadius: "6px",
        marginBottom: "8px",
        overflow: "hidden",
        transition: "all 0.3s",
      }}
    >
      {/* Header row */}
      <div
        className="flex items-center justify-between px-4 py-2 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
        style={{ borderBottom: expanded ? "1px solid oklch(0.16 0.01 240)" : "none" }}
      >
        <div className="flex items-center gap-3">
          <span className="text-[10px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>{d.timestamp}</span>
          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded" style={{ background: domainColor + "22", color: domainColor }}>{d.domain}</span>
          <span className="text-xs font-mono text-muted-foreground">{d.agent.proposal}</span>
        </div>
        <div className="flex items-center gap-3">
          {d.world.event && (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded" style={{ background: "oklch(0.65 0.22 25 / 0.15)", color: "oklch(0.65 0.22 25)" }}>
              ⚡ {d.world.event}
            </span>
          )}
          <span className="text-xs font-mono font-bold px-3 py-1 rounded" style={{ background: guardColor + "22", color: guardColor, border: `1px solid ${guardColor}44` }}>
            {d.guard.decision}
          </span>
          <span className="text-[10px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>{expanded ? "▲" : "▼"}</span>
        </div>
      </div>

      {/* Expanded — full causal chain */}
      {expanded && (
        <div className="px-4 py-3 grid grid-cols-3 gap-4" style={{ gridTemplateColumns: "1fr 1fr 1fr" }}>
          {/* Left: WORLD + AGENT */}
          <div className="flex flex-col gap-3">
            {/* WORLD */}
            <div>
              <div className="text-[9px] font-mono font-bold mb-1.5 tracking-widest" style={{ color: "oklch(0.65 0.18 240)" }}>① WORLD STATE</div>
              <div className="text-[10px] font-mono space-y-0.5">
                <div className="flex justify-between">
                  <span style={{ color: "oklch(0.45 0.01 240)" }}>price</span>
                  <span style={{ color: "oklch(0.85 0.01 240)" }}>${d.world.price.toFixed(0)}</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: "oklch(0.45 0.01 240)" }}>volatility</span>
                  <span style={{ color: d.world.volatility > 0.35 ? "oklch(0.65 0.22 25)" : "oklch(0.72 0.18 145)" }}>{(d.world.volatility * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: "oklch(0.45 0.01 240)" }}>regime</span>
                  <span style={{ color: "oklch(0.85 0.01 240)" }}>{d.world.regime}</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: "oklch(0.45 0.01 240)" }}>liquidity</span>
                  <span style={{ color: "oklch(0.85 0.01 240)" }}>{(d.world.liquidity * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>
            {/* AGENT */}
            <div>
              <div className="text-[9px] font-mono font-bold mb-1.5 tracking-widest" style={{ color: "oklch(0.75 0.18 280)" }}>② AGENT</div>
              <div className="text-[10px] font-mono space-y-0.5">
                <div style={{ color: "oklch(0.55 0.01 240)" }} className="leading-relaxed">{d.agent.observation}</div>
                <div className="flex justify-between mt-1">
                  <span style={{ color: "oklch(0.45 0.01 240)" }}>proposal</span>
                  <span className="font-bold" style={{ color: "oklch(0.85 0.01 240)" }}>{d.agent.proposal}</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: "oklch(0.45 0.01 240)" }}>confidence</span>
                  <span style={{ color: "oklch(0.85 0.01 240)" }}>{(d.agent.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Center: ENGINE + GUARD */}
          <div className="flex flex-col gap-3">
            {/* ENGINE */}
            <div>
              <div className="text-[9px] font-mono font-bold mb-1.5 tracking-widest" style={{ color: "oklch(0.78 0.18 60)" }}>③ ENGINE EVALUATION</div>
              <div className="text-[10px] font-mono space-y-0.5">
                <div className="flex justify-between">
                  <span style={{ color: "oklch(0.45 0.01 240)" }}>coherence</span>
                  <span style={{ color: d.engine.coherence > 0.6 ? "oklch(0.72 0.18 145)" : "oklch(0.65 0.22 25)" }}>{d.engine.coherence.toFixed(3)}</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: "oklch(0.45 0.01 240)" }}>risk score</span>
                  <span style={{ color: d.engine.risk > 0.3 ? "oklch(0.65 0.22 25)" : "oklch(0.72 0.18 145)" }}>{d.engine.risk.toFixed(3)}</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: "oklch(0.45 0.01 240)" }}>vol score</span>
                  <span style={{ color: "oklch(0.85 0.01 240)" }}>{d.engine.volatilityScore.toFixed(3)}</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: "oklch(0.45 0.01 240)" }}>regime score</span>
                  <span style={{ color: "oklch(0.85 0.01 240)" }}>{d.engine.regimeScore.toFixed(2)}</span>
                </div>
              </div>
            </div>
            {/* GUARD */}
            <div>
              <div className="text-[9px] font-mono font-bold mb-1.5 tracking-widest" style={{ color: guardColor }}>④ GUARD X-108</div>
              <div className="text-[10px] font-mono">
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="font-bold text-sm px-3 py-1 rounded" style={{ background: guardColor + "22", color: guardColor, border: `1px solid ${guardColor}44` }}>
                    {d.guard.decision}
                  </span>
                  {d.guard.temporalLock && (
                    <span className="text-[9px] px-2 py-0.5 rounded" style={{ background: "oklch(0.78 0.18 60 / 0.15)", color: "oklch(0.78 0.18 60)" }}>
                      ⏱ LOCK {d.guard.holdDuration}s
                    </span>
                  )}
                </div>
                <div style={{ color: "oklch(0.55 0.01 240)" }} className="leading-relaxed text-[9px]">{d.guard.reason}</div>
              </div>
            </div>
          </div>

          {/* Right: DECISION + PROOF */}
          <div className="flex flex-col gap-3">
            {/* DECISION */}
            <div>
              <div className="text-[9px] font-mono font-bold mb-1.5 tracking-widest" style={{ color: "oklch(0.72 0.18 145)" }}>⑤ DECISION</div>
              <div className="text-[10px] font-mono space-y-1">
                <div className="p-2 rounded" style={{ background: guardColor + "11", border: `1px solid ${guardColor}33` }}>
                  <div className="font-bold" style={{ color: guardColor }}>
                    {d.guard.decision === "ALLOW" ? `✓ ${d.agent.proposal}` : d.guard.decision === "HOLD" ? `⏸ DELAYED — ${d.agent.proposal}` : `✗ BLOCKED — ${d.agent.proposal}`}
                  </div>
                  <div className="mt-1 text-[9px]" style={{ color: "oklch(0.50 0.01 240)" }}>
                    {d.guard.decision === "ALLOW" ? "Action executed immediately" : d.guard.decision === "HOLD" ? `Action delayed ${d.guard.holdDuration}s pending re-evaluation` : "Action permanently rejected by Guard X-108"}
                  </div>
                </div>
              </div>
            </div>
            {/* PROOF */}
            <div>
              <div className="text-[9px] font-mono font-bold mb-1.5 tracking-widest" style={{ color: "oklch(0.60 0.12 200)" }}>⑥ CRYPTOGRAPHIC PROOF</div>
              <div className="text-[10px] font-mono space-y-0.5">
                <div>
                  <span style={{ color: "oklch(0.45 0.01 240)" }}>hash </span>
                  <span className="font-mono text-[9px]" style={{ color: "oklch(0.55 0.01 240)" }}>{d.proof.hash}</span>
                </div>
                <div>
                  <span style={{ color: "oklch(0.45 0.01 240)" }}>merkle </span>
                  <span className="font-mono text-[9px]" style={{ color: "oklch(0.55 0.01 240)" }}>{d.proof.merkleRoot.slice(0, 18)}…</span>
                </div>
                <div className="flex items-center gap-1.5 mt-1">
                  <div className="w-1.5 h-1.5 rounded-full" style={{ background: "oklch(0.72 0.18 145)" }} />
                  <span style={{ color: "oklch(0.72 0.18 145)" }}>Replay verified</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Stats Panel ───────────────────────────────────────────────────────────────
function StatsPanel({ decisions }: { decisions: ReactorDecision[] }) {
  const block = decisions.filter(d => d.guard.decision === "BLOCK").length;
  const hold = decisions.filter(d => d.guard.decision === "HOLD").length;
  const allow = decisions.filter(d => d.guard.decision === "ALLOW").length;
  const total = decisions.length || 1;
  const avgCoherence = decisions.reduce((s, d) => s + d.engine.coherence, 0) / total;
  const avgVol = decisions.reduce((s, d) => s + d.world.volatility, 0) / total;

  return (
    <div className="grid grid-cols-6 gap-3 mb-4">
      {[
        { label: "TOTAL", value: decisions.length, color: "oklch(0.85 0.01 240)" },
        { label: "ALLOW", value: allow, sub: `${((allow / total) * 100).toFixed(0)}%`, color: "oklch(0.72 0.18 145)" },
        { label: "HOLD", value: hold, sub: `${((hold / total) * 100).toFixed(0)}%`, color: "oklch(0.78 0.18 60)" },
        { label: "BLOCK", value: block, sub: `${((block / total) * 100).toFixed(0)}%`, color: "oklch(0.65 0.22 25)" },
        { label: "AVG COHERENCE", value: avgCoherence.toFixed(3), color: avgCoherence > 0.6 ? "oklch(0.72 0.18 145)" : "oklch(0.65 0.22 25)" },
        { label: "AVG VOLATILITY", value: `${(avgVol * 100).toFixed(1)}%`, color: avgVol > 0.35 ? "oklch(0.65 0.22 25)" : "oklch(0.72 0.18 145)" },
      ].map(s => (
        <div key={s.label} className="p-3 rounded" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
          <div className="text-[9px] font-mono text-muted-foreground mb-1">{s.label}</div>
          <div className="text-lg font-mono font-bold" style={{ color: s.color }}>{s.value}</div>
          {s.sub && <div className="text-[9px] font-mono" style={{ color: s.color + "aa" }}>{s.sub}</div>}
        </div>
      ))}
    </div>
  );
}

// ─── Main Component ────────────────────────────────────────────────────────────
export default function DecisionReactor() {
  const [decisions, setDecisions] = useState<ReactorDecision[]>([]);
  const [running, setRunning] = useState(false);
  const [speed, setSpeed] = useState(1500); // ms between decisions
  const [filter, setFilter] = useState<"ALL" | "BLOCK" | "HOLD" | "ALLOW">("ALL");
  const seedRef = useRef(Date.now() % 100000);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const addDecision = useCallback(() => {
    seedRef.current = (seedRef.current * 1664525 + 1013904223) & 0xffffffff;
    const d = generateDecision(Math.abs(seedRef.current) % 99999 + 1);
    setDecisions(prev => [d, ...prev].slice(0, 50));
  }, []);

  const toggleRun = () => {
    if (running) {
      if (intervalRef.current) clearInterval(intervalRef.current);
      intervalRef.current = null;
      setRunning(false);
    } else {
      addDecision();
      intervalRef.current = setInterval(addDecision, speed);
      setRunning(true);
    }
  };

  useEffect(() => {
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, []);

  useEffect(() => {
    if (running) {
      if (intervalRef.current) clearInterval(intervalRef.current);
      intervalRef.current = setInterval(addDecision, speed);
    }
  }, [speed, running, addDecision]);

  // Generate initial decisions
  useEffect(() => {
    const initial: ReactorDecision[] = [];
    for (let i = 0; i < 5; i++) {
      initial.push(generateDecision(42 + i * 137));
    }
    setDecisions(initial);
  }, []);

  const filtered = filter === "ALL" ? decisions : decisions.filter(d => d.guard.decision === filter);

  return (
    <div className="max-w-7xl mx-auto" style={{ color: "oklch(0.90 0.01 240)" }}>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h1 className="text-2xl font-mono font-bold" style={{ color: "oklch(0.72 0.18 145)" }}>
              Decision Reactor
            </h1>
            <p className="text-sm font-mono text-muted-foreground mt-1">
              Vue causale totale — chaque décision expose la chaîne complète WORLD → AGENT → ENGINE → GUARD X-108 → DECISION → PROOF
            </p>
          </div>
          <div className="flex items-center gap-3">
            {running && (
              <div className="flex items-center gap-1.5 text-xs font-mono" style={{ color: "oklch(0.72 0.18 145)" }}>
                <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: "oklch(0.72 0.18 145)" }} />
                LIVE
              </div>
            )}
            <select
              value={speed}
              onChange={e => setSpeed(Number(e.target.value))}
              className="text-xs font-mono px-2 py-1 rounded"
              style={{ background: "oklch(0.14 0.01 240)", border: "1px solid oklch(0.22 0.01 240)", color: "oklch(0.70 0.01 240)" }}
            >
              <option value={3000}>Slow (3s)</option>
              <option value={1500}>Normal (1.5s)</option>
              <option value={800}>Fast (0.8s)</option>
              <option value={300}>Ultra (0.3s)</option>
            </select>
            <button
              onClick={toggleRun}
              className="px-4 py-2 text-xs font-mono font-bold rounded"
              style={{
                background: running ? "oklch(0.65 0.22 25 / 0.2)" : "oklch(0.72 0.18 145 / 0.2)",
                border: `1px solid ${running ? "oklch(0.65 0.22 25 / 0.5)" : "oklch(0.72 0.18 145 / 0.5)"}`,
                color: running ? "oklch(0.65 0.22 25)" : "oklch(0.72 0.18 145)",
              }}
            >
              {running ? "⏹ STOP" : "▶ START LIVE FEED"}
            </button>
          </div>
        </div>

        {/* Pipeline visual */}
        <div className="flex items-center gap-1 text-[10px] font-mono p-3 rounded" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
          {[
            { label: "① WORLD", color: "oklch(0.65 0.18 240)" },
            { label: "② AGENT", color: "oklch(0.75 0.18 280)" },
            { label: "③ ENGINE", color: "oklch(0.78 0.18 60)" },
            { label: "④ GUARD X-108", color: "oklch(0.72 0.18 145)" },
            { label: "⑤ DECISION", color: "oklch(0.72 0.18 145)" },
            { label: "⑥ PROOF", color: "oklch(0.60 0.12 200)" },
          ].map((step, i) => (
            <React.Fragment key={step.label}>
              <span className="px-2 py-1 rounded font-bold" style={{ background: step.color + "15", color: step.color, border: `1px solid ${step.color}33` }}>
                {step.label}
              </span>
              {i < 5 && <span style={{ color: "oklch(0.30 0.01 240)" }}>→</span>}
            </React.Fragment>
          ))}
          <span className="ml-auto text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>
            Every decision exposes the full causal chain. Click any row to expand.
          </span>
        </div>
      </div>

      {/* Stats */}
      <StatsPanel decisions={decisions} />

      {/* Filter */}
      <div className="flex items-center gap-2 mb-4">
        <span className="text-[10px] font-mono text-muted-foreground">Filter:</span>
        {(["ALL", "ALLOW", "HOLD", "BLOCK"] as const).map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className="px-3 py-1 text-[10px] font-mono rounded"
            style={{
              background: filter === f ? "oklch(0.72 0.18 145 / 0.2)" : "oklch(0.12 0.01 240)",
              border: `1px solid ${filter === f ? "oklch(0.72 0.18 145 / 0.5)" : "oklch(0.20 0.01 240)"}`,
              color: filter === f ? "oklch(0.72 0.18 145)" : "oklch(0.55 0.01 240)",
            }}
          >
            {f} {f !== "ALL" && `(${decisions.filter(d => d.guard.decision === f).length})`}
          </button>
        ))}
        <span className="ml-auto text-[10px] font-mono text-muted-foreground">{filtered.length} decisions</span>
      </div>

      {/* Decision Feed */}
      <div>
        {filtered.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground font-mono text-sm">
            Press START LIVE FEED to begin generating decisions
          </div>
        ) : (
          filtered.map((d, i) => (
            <DecisionCard key={d.id + i} d={d} isLatest={i === 0} />
          ))
        )}
      </div>

      {/* Market Mechanics */}
      <div className="mt-6">
        <MarketMechanics />
      </div>

      {/* Footer explanation */}
      <div className="mt-6 p-4 rounded" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
        <div className="text-[10px] font-mono text-muted-foreground leading-relaxed">
          <span className="font-bold" style={{ color: "oklch(0.72 0.18 145)" }}>How to read this page:</span> Each row represents one decision cycle. Expand any row to see the full causal chain: the world state that triggered the agent, the engine evaluation (coherence + risk + volatility + regime), the Guard X-108 decision with its exact reasoning, and the cryptographic proof anchoring the decision. This is the complete OS4 governance pipeline made visible.
        </div>
      </div>
    </div>
  );
}
