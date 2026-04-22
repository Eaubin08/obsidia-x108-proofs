import React, { useState, useEffect } from "react";
import { Link, useLocation } from "wouter";
import { ConceptTooltip } from "@/components/ConceptTooltip";

// ─── Types ────────────────────────────────────────────────────────────────────

interface AgentStatus {
  name: string;
  domain: "trading" | "banking" | "ecom";
  icon: string;
  color: string;
  status: "ALLOW" | "HOLD" | "BLOCK" | "En attente";
  action: string;
  path: string;
}

// ─── Live agent status simulation ────────────────────────────────────────────

function generateAgentStatus(domain: "trading" | "banking" | "ecom"): { status: "ALLOW" | "HOLD" | "BLOCK" | "En attente"; action: string } {
  const r = Math.random();
  if (domain === "trading") {
    if (r < 0.15) return { status: "BLOCK", action: "SELL BTC — Flash crash risk" };
    if (r < 0.35) return { status: "HOLD", action: "BUY ETH — τ=10s lock" };
    return { status: "ALLOW", action: `${r > 0.6 ? "BUY" : "SELL"} BTC — Coherence OK` };
  }
  if (domain === "banking") {
    if (r < 0.10) return { status: "BLOCK", action: "Transfer €50k — Fraud risk" };
    if (r < 0.25) return { status: "HOLD", action: "Invest €20k — Liquidity check" };
    return { status: "ALLOW", action: "Deposit €5k — Normal" };
  }
  if (r < 0.12) return { status: "BLOCK", action: "Discount 40% — Margin collapse" };
  if (r < 0.28) return { status: "HOLD", action: "Ad spend +200% — τ=10s" };
  return { status: "ALLOW", action: "Promo +15% — ROAS OK" };
}

const STATUS_META: Record<string, { color: string; bg: string; icon: string }> = {
  ALLOW: { color: "#4ade80", bg: "rgba(74,222,128,0.12)", icon: "✅" },
  HOLD:  { color: "#fbbf24", bg: "rgba(251,191,36,0.12)",  icon: "⏳" },
  BLOCK: { color: "#f87171", bg: "rgba(248,113,113,0.12)", icon: "⛔" },
  "En attente":  { color: "#6b7280", bg: "rgba(107,114,128,0.10)", icon: "○" },
};

const AGENTS: AgentStatus[] = [
  { name: "Alpha",    domain: "trading", icon: "📈", color: "#3b82f6", status: "En attente", action: "Monitoring BTC/ETH", path: "/market/trading" },
  { name: "Sentinel", domain: "banking", icon: "🏦", color: "#22c55e", status: "En attente", action: "Monitoring transfers", path: "/market/banking" },
  { name: "Mercury",  domain: "ecom",    icon: "🛒", color: "#a855f7", status: "En attente", action: "Monitoring promotions", path: "/market/ecommerce" },
];

// ─── LiveModeBadge ────────────────────────────────────────────────────────────

export function LiveModeBadge({ mode, onChange }: { mode: "LIVE" | "DEMO"; onChange?: (m: "LIVE" | "DEMO") => void }) {
  return (
    <div className="flex items-center rounded overflow-hidden" style={{ border: "1px solid oklch(0.22 0.01 240)" }}>
      <button
        onClick={() => onChange?.("LIVE")}
        className="flex items-center gap-1 px-2 py-1 font-mono text-[9px] font-bold transition-all"
        style={{
          background: mode === "LIVE" ? "rgba(74,222,128,0.15)" : "oklch(0.12 0.01 240)",
          color: mode === "LIVE" ? "#4ade80" : "oklch(0.40 0.01 240)",
          borderRight: "1px solid oklch(0.22 0.01 240)",
        }}
      >
        {mode === "LIVE" && <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: "#4ade80", flexShrink: 0 }} />}
        LIVE
      </button>
      <button
        onClick={() => onChange?.("DEMO")}
        className="flex items-center gap-1 px-2 py-1 font-mono text-[9px] font-bold transition-all"
        style={{
          background: mode === "DEMO" ? "rgba(96,165,250,0.15)" : "oklch(0.12 0.01 240)",
          color: mode === "DEMO" ? "#60a5fa" : "oklch(0.40 0.01 240)",
        }}
      >
        DEMO
      </button>
    </div>
  );
}

// ─── AgentsSidebar component ──────────────────────────────────────────────────

export default function AgentsSidebar() {
  const [location] = useLocation();
  const [agents, setAgents] = useState<AgentStatus[]>(AGENTS);
  const [collapsed, setCollapsed] = useState(false);

  // Simulate live status updates every 4s
  useEffect(() => {
    const interval = setInterval(() => {
      setAgents(prev => prev.map(a => {
        const live = generateAgentStatus(a.domain);
        return { ...a, status: live.status, action: live.action };
      }));
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  if (collapsed) {
    return (
      <div
        className="flex flex-col items-center gap-2 py-3 px-1.5 rounded"
        style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.18 0.01 240)", minWidth: "36px" }}
      >
        <button
          onClick={() => setCollapsed(false)}
          className="font-mono text-[9px] font-bold"
          style={{ color: "oklch(0.45 0.01 240)" }}
          title="Afficher les agents"
        >
          ▶
        </button>
        {agents.map(a => {
          const sm = STATUS_META[a.status];
          return (
            <Link key={a.name} href={a.path}>
              <span
                className="w-7 h-7 rounded-full flex items-center justify-center text-sm cursor-pointer"
                style={{ background: sm.bg, border: `1px solid ${sm.color}44` }}
                title={`${a.name} — ${a.status} — ${a.action}`}
              >
                {a.icon}
              </span>
            </Link>
          );
        })}
      </div>
    );
  }

  return (
    <div
      className="flex flex-col gap-2 py-3 px-2 rounded"
      style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.18 0.01 240)", minWidth: "180px", maxWidth: "200px" }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-1">
        <div className="font-mono text-[9px] font-bold tracking-widest" style={{ color: "oklch(0.45 0.01 240)" }}>
          ACTIVE AGENTS
        </div>
        <button
          onClick={() => setCollapsed(true)}
          className="font-mono text-[9px]"
          style={{ color: "oklch(0.35 0.01 240)" }}
          title="Réduire"
        >
          ◀
        </button>
      </div>

      {/* Agent cards */}
      {agents.map(a => {
        const sm = STATUS_META[a.status];
        const isCurrentDomain = location.includes(a.domain) || location.includes(a.path.replace("/market/", ""));
        return (
          <Link key={a.name} href={a.path}>
            <div
              className="rounded p-2 cursor-pointer"
              style={{
                background: isCurrentDomain ? `${a.color}12` : "oklch(0.12 0.01 240)",
                border: `1px solid ${isCurrentDomain ? `${a.color}44` : "oklch(0.18 0.01 240)"}`,
              }}
            >
              <div className="flex items-center gap-1.5 mb-1">
                <span className="text-sm">{a.icon}</span>
                <span className="font-mono text-[10px] font-bold" style={{ color: a.color }}>{a.name}</span>
                <span
                  className="ml-auto px-1 py-0.5 rounded font-mono text-[8px] font-bold"
                  style={{ background: sm.bg, color: sm.color, border: `1px solid ${sm.color}44` }}
                >
                  {sm.icon} {a.status}
                </span>
              </div>
              <div className="font-mono text-[9px] truncate" style={{ color: "oklch(0.50 0.01 240)" }}>
                {a.action}
              </div>
            </div>
          </Link>
        );
      })}

      {/* Footer: link to Decision Flow */}
      <div className="mt-1 pt-2" style={{ borderTop: "1px solid oklch(0.16 0.01 240)" }}>
        <Link href="/decision-flow">
          <span className="font-mono text-[9px] font-bold" style={{ color: "oklch(0.72 0.18 145)" }}>
            ⚡ Decision Flow →
          </span>
        </Link>
      </div>

      {/* Glossary hint */}
      <div className="font-mono text-[8px]" style={{ color: "oklch(0.35 0.01 240)" }}>
        <ConceptTooltip term="Guard X-108" showIcon>Guard X-108</ConceptTooltip> valide chaque action
      </div>
    </div>
  );
}
