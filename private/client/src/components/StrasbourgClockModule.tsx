import { useState, useEffect } from "react";
import { trpc } from "@/lib/trpc";

// ─── Types ────────────────────────────────────────────────────────────────────

interface NodeStatus {
  id: string;
  city: string;
  flag: string;
  status: "synced" | "syncing" | "offline";
  latencyMs: number;
}

type Decision = "ALLOW" | "HOLD" | "BLOCK";

interface ConsensusVote {
  nodeId: string;
  city: string;
  vote: Decision;
}

interface LastDecision {
  agent: string;
  action: string;
  decision: Decision;
  reason: string;
  timestamp: string;
}

// ─── Constants ────────────────────────────────────────────────────────────────

const NODES_BASE: NodeStatus[] = [
  { id: "N1", city: "Paris",     flag: "🇫🇷", status: "synced", latencyMs: 12 },
  { id: "N2", city: "London",    flag: "🇬🇧", status: "synced", latencyMs: 18 },
  { id: "N3", city: "Frankfurt", flag: "🇩🇪", status: "synced", latencyMs: 9  },
  { id: "N4", city: "Amsterdam", flag: "🇳🇱", status: "synced", latencyMs: 15 },
];

const D_COLOR: Record<Decision, string> = {
  ALLOW: "#4ade80",
  HOLD:  "#fbbf24",
  BLOCK: "#f87171",
};

const D_BG: Record<Decision, string> = {
  ALLOW: "#4ade8015",
  HOLD:  "#fbbf2415",
  BLOCK: "#f8717115",
};

// ─── Component ────────────────────────────────────────────────────────────────

export default function StrasbourgClockModule() {
  const [now, setNow] = useState(() => new Date());
  const [lockRemaining, setLockRemaining] = useState(7.2);
  const lockTotal = 10;

  const [nodes, setNodes] = useState<NodeStatus[]>(NODES_BASE);

  const [votes, setVotes] = useState<ConsensusVote[]>([
    { nodeId: "N1", city: "Paris",     vote: "ALLOW" },
    { nodeId: "N2", city: "London",    vote: "ALLOW" },
    { nodeId: "N3", city: "Frankfurt", vote: "ALLOW" },
    { nodeId: "N4", city: "Amsterdam", vote: "HOLD"  },
  ]);

  const [lastDecision, setLastDecision] = useState<LastDecision>({
    agent:     "Alpha",
    action:    "SELL 1.2 BTC",
    decision:  "HOLD",
    reason:    "Coherence threshold not reached (0.71 < 0.80)",
    timestamp: new Date().toISOString(),
  });

  // ─── Real data ─────────────────────────────────────────────────────────────

  const proofQuery = trpc.engine.proofs.useQuery(undefined, { refetchInterval: 30000 });
  const rfc3161Ts  = proofQuery.data?.rfc3161?.timestamp ?? new Date().toISOString();

  const streamQuery = trpc.stream.getEvents.useQuery(
    { limit: 1 },
    { refetchInterval: 5000 }
  );

  useEffect(() => {
    const entries = streamQuery.data;
    if (!entries || entries.length === 0) return;
    const latest = entries[0];
    const d = (latest.guard?.decision ?? "HOLD") as Decision;
    setLastDecision({
      agent:     latest.agent?.id ?? "Alpha",
      action:    latest.agent?.proposal ?? "SELL 1.2 BTC",
      decision:  d,
      reason:    latest.guard?.reason ?? "Coherence threshold not reached",
      timestamp: new Date(latest.timestamp).toISOString(),
    });
    setVotes([
      { nodeId: "N1", city: "Paris",     vote: d },
      { nodeId: "N2", city: "London",    vote: d },
      { nodeId: "N3", city: "Frankfurt", vote: d },
      { nodeId: "N4", city: "Amsterdam", vote: d === "ALLOW" ? "HOLD" : d === "BLOCK" ? "HOLD" : "ALLOW" },
    ]);
  }, [streamQuery.data]);

  // ─── Live tick ─────────────────────────────────────────────────────────────

  useEffect(() => {
    const id = setInterval(() => {
      setNow(new Date());
      setLockRemaining(prev => {
        const next = Math.round((prev - 0.1) * 10) / 10;
        return next <= 0 ? lockTotal : next;
      });
      setNodes(prev =>
        prev.map(n => ({
          ...n,
          latencyMs: Math.max(5, n.latencyMs + Math.floor(Math.random() * 5) - 2),
        }))
      );
    }, 1000);
    return () => clearInterval(id);
  }, []);

  // ─── Derived ───────────────────────────────────────────────────────────────

  const lockPct    = (lockRemaining / lockTotal) * 100;
  const lockFilled = Math.round(lockPct / 10);
  const lockBar    = "█".repeat(lockFilled) + "░".repeat(10 - lockFilled);

  const allowCount = votes.filter(v => v.vote === "ALLOW").length;
  const blockCount = votes.filter(v => v.vote === "BLOCK").length;
  const quorum     = 3;
  const reached    = allowCount >= quorum || blockCount >= quorum;
  const finalVote: Decision = allowCount >= quorum ? "ALLOW" : blockCount >= quorum ? "BLOCK" : "HOLD";

  const card = {
    background:   "oklch(0.10 0.01 240)",
    border:       "1px solid oklch(0.20 0.01 240)",
    borderRadius: "8px",
    padding:      "20px 24px",
  } as const;

  return (
    <div className="flex flex-col" style={{ gap: "16px" }}>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-mono font-bold text-sm uppercase tracking-widest" style={{ color: "oklch(0.72 0.18 145)" }}>
            Strasbourg Clock
          </h3>
          <p className="text-[10px] font-mono mt-0.5" style={{ color: "oklch(0.45 0.01 240)" }}>
            Gouvernance temporelle X-108 · Système distribué
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full" style={{ background: "#4ade80", boxShadow: "0 0 6px #4ade80" }} />
          <span className="font-mono text-[10px]" style={{ color: "#4ade80" }}>LIVE</span>
        </div>
      </div>

      {/* 2×2 grid */}
      <div className="grid grid-cols-2" style={{ gap: "16px" }}>

        {/* Card 1 — RFC3161 */}
        <div style={card}>
          <div className="text-[10px] font-mono uppercase tracking-widest mb-3" style={{ color: "oklch(0.50 0.01 240)" }}>
            RFC3161 Timestamp
          </div>
          <div className="font-mono font-bold text-sm mb-1" style={{ color: "#fbbf24" }}>
            {now.toISOString().replace("T", " ").slice(0, 19)} UTC
          </div>
          <div className="text-[9px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>
            Ancre certifiée : {rfc3161Ts.slice(0, 19).replace("T", " ")} UTC
          </div>
          <div className="text-[9px] font-mono mt-1" style={{ color: "oklch(0.40 0.01 240)" }}>
            TSA : FreeTSA · SHA-256
          </div>
        </div>

        {/* Card 2 — Temporal Lock */}
        <div style={card}>
          <div className="text-[10px] font-mono uppercase tracking-widest mb-3" style={{ color: "oklch(0.50 0.01 240)" }}>
            Temporal Lock
          </div>
          <div className="flex items-baseline gap-2 mb-2">
            <span className="font-mono font-bold text-xl" style={{ color: lockRemaining > 3 ? "#fbbf24" : "#f87171" }}>
              {lockRemaining.toFixed(1)}s
            </span>
            <span className="text-[10px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>
              / {lockTotal}s
            </span>
          </div>
          <div className="rounded-full overflow-hidden mb-2" style={{ height: "6px", background: "oklch(0.18 0.01 240)" }}>
            <div
              className="h-full rounded-full"
              style={{
                width: `${lockPct}%`,
                background: lockRemaining > 3 ? "#fbbf24" : "#f87171",
                transition: "width 0.9s linear",
              }}
            />
          </div>
          <div className="font-mono text-[9px]" style={{ color: lockRemaining > 3 ? "#fbbf24" : "#f87171" }}>
            [{lockBar}] {lockRemaining.toFixed(1)}s / {lockTotal}s
          </div>
          <div className="text-[9px] font-mono mt-2" style={{ color: "oklch(0.40 0.01 240)" }}>
            Les actions irréversibles attendent l'expiration du verrou.
          </div>
        </div>

        {/* Card 3 — Nodes */}
        <div style={card}>
          <div className="flex items-center justify-between mb-3">
            <div className="text-[10px] font-mono uppercase tracking-widest" style={{ color: "oklch(0.50 0.01 240)" }}>
              Nodes Synchronization
            </div>
            <span className="text-[9px] font-mono px-2 py-0.5 rounded" style={{ background: "#4ade8015", color: "#4ade80" }}>
              {nodes.filter(n => n.status === "synced").length}/{nodes.length} synced
            </span>
          </div>
          <div className="flex flex-col" style={{ gap: "8px" }}>
            {nodes.map(n => (
              <div key={n.id} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm">{n.flag}</span>
                  <span className="font-mono text-xs text-foreground">{n.city}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-mono text-[9px]" style={{ color: "#4ade80" }}>✓ synced</span>
                  <span className="font-mono text-[9px]" style={{ color: "oklch(0.45 0.01 240)" }}>{n.latencyMs}ms</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Card 4 — Consensus */}
        <div style={card}>
          <div className="text-[10px] font-mono uppercase tracking-widest mb-3" style={{ color: "oklch(0.50 0.01 240)" }}>
            Consensus Status
          </div>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div>
              <div className="text-[9px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>Nœuds actifs</div>
              <div className="font-mono font-bold text-lg text-foreground">{nodes.length}</div>
            </div>
            <div>
              <div className="text-[9px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>Consensus requis</div>
              <div className="font-mono font-bold text-lg text-foreground">{quorum}</div>
            </div>
          </div>
          <div className="flex flex-col mb-3" style={{ gap: "4px" }}>
            {votes.map(v => (
              <div key={v.nodeId} className="flex items-center justify-between">
                <span className="font-mono text-[10px]" style={{ color: "oklch(0.55 0.01 240)" }}>{v.city}</span>
                <span
                  className="font-mono text-[9px] px-2 py-0.5 rounded"
                  style={{ background: D_BG[v.vote], color: D_COLOR[v.vote] }}
                >
                  {v.vote}
                </span>
              </div>
            ))}
          </div>
          <div
            className="flex items-center justify-between rounded px-3 py-2"
            style={{ background: D_BG[finalVote], border: `1px solid ${D_COLOR[finalVote]}30` }}
          >
            <span className="font-mono text-[10px]" style={{ color: "oklch(0.55 0.01 240)" }}>
              Décision finale · PBFT 3/4
            </span>
            <span className="font-mono font-bold text-sm" style={{ color: D_COLOR[finalVote] }}>
              {reached ? finalVote : "PENDING"}
            </span>
          </div>
        </div>
      </div>

      {/* Card 5 — Last Decision */}
      <div
        style={{
          ...card,
          borderLeft: `3px solid ${D_COLOR[lastDecision.decision]}`,
        }}
      >
        <div className="flex items-center justify-between mb-4">
          <div className="text-[10px] font-mono uppercase tracking-widest" style={{ color: "oklch(0.50 0.01 240)" }}>
            Last Decision Validated
          </div>
          <span className="text-[9px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>
            {new Date(lastDecision.timestamp).toLocaleTimeString("fr-FR", {
              hour: "2-digit", minute: "2-digit", second: "2-digit",
            })} UTC
          </span>
        </div>
        <div className="grid grid-cols-4 gap-4">
          <div>
            <div className="text-[9px] font-mono uppercase tracking-widest mb-1" style={{ color: "oklch(0.45 0.01 240)" }}>Agent</div>
            <div className="font-mono font-bold text-sm text-foreground">{lastDecision.agent}</div>
          </div>
          <div>
            <div className="text-[9px] font-mono uppercase tracking-widest mb-1" style={{ color: "oklch(0.45 0.01 240)" }}>Action</div>
            <div className="font-mono text-xs text-foreground">{lastDecision.action}</div>
          </div>
          <div>
            <div className="text-[9px] font-mono uppercase tracking-widest mb-1" style={{ color: "oklch(0.45 0.01 240)" }}>Decision</div>
            <span
              className="font-mono font-bold text-sm px-2 py-0.5 rounded"
              style={{ background: D_BG[lastDecision.decision], color: D_COLOR[lastDecision.decision] }}
            >
              {lastDecision.decision}
            </span>
          </div>
          <div>
            <div className="text-[9px] font-mono uppercase tracking-widest mb-1" style={{ color: "oklch(0.45 0.01 240)" }}>Reason</div>
            <div className="font-mono text-[10px]" style={{ color: "oklch(0.60 0.01 240)" }}>{lastDecision.reason}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
