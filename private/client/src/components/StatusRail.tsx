/**
 * StatusRail — barre de statut système persistante (topbar OS4 V2)
 * Affiche : Monde | Mode | Source | X-108 Gate | Fraîcheur | Last Decision ID | Proof Status
 * Règle UX : toujours visible, jamais mensonger sur le mode réel
 */
import React, { useState, useEffect } from "react";
import { useWorld, DOMAIN_COLORS, MODE_COLORS, GATE_COLORS, type WorldDomain, type OperatingMode } from "@/contexts/WorldContext";

// ─── Helpers ─────────────────────────────────────────────────────────────────
function formatAge(ts: number | null): string {
  if (!ts) return "";
  const diff = Date.now() - ts;
  if (diff < 5000)   return "à l'instant";
  if (diff < 60000)  return `il y a ${Math.floor(diff / 1000)}s`;
  if (diff < 3600000) return `il y a ${Math.floor(diff / 60000)}min`;
  return `il y a ${Math.floor(diff / 3600000)}h`;
}

// ─── WorldFilter ─────────────────────────────────────────────────────────────
function WorldFilter() {
  const { domain, setDomain } = useWorld();
  const domains: { key: WorldDomain; label: string; icon: string }[] = [
    { key: "trading", label: "Trading", icon: "📈" },
    { key: "bank",    label: "Bank",    icon: "🏦" },
    { key: "ecom",    label: "Ecom",    icon: "🛒" },
  ];
  return (
    <div className="flex items-center gap-0.5">
      {domains.map(d => {
        const active = domain === d.key;
        const colors = DOMAIN_COLORS[d.key];
        return (
          <button
            key={d.key}
            onClick={() => setDomain(d.key)}
            className="flex items-center gap-1 px-2 py-0.5 rounded text-[9px] font-mono font-bold transition-all"
            style={{
              background: active ? colors.bg : "transparent",
              border: `1px solid ${active ? colors.border : "transparent"}`,
              color: active ? colors.accent : "oklch(0.45 0.01 240)",
            }}
          >
            <span>{d.icon}</span>
            <span className="hidden sm:inline">{d.label}</span>
          </button>
        );
      })}
    </div>
  );
}

// ─── ModePill ────────────────────────────────────────────────────────────────
function ModePill({ mode }: { mode: OperatingMode }) {
  const m = MODE_COLORS[mode];
  return (
    <div className="flex items-center gap-1 px-2 py-0.5 rounded text-[9px] font-mono font-bold"
      style={{ background: m.bg, border: `1px solid ${m.color}40`, color: m.color }}>
      {mode === "LIVE" && <span className="w-1.5 h-1.5 rounded-full animate-pulse inline-block" style={{ background: m.color }} />}
      {m.label}
    </div>
  );
}

// ─── GatePill avec indicateur de fraîcheur ───────────────────────────────────
function GatePill({ gate, updatedAt }: { gate: "ALLOW" | "HOLD" | "BLOCK" | null; updatedAt: number | null }) {
  const [age, setAge] = useState<string>("");

  useEffect(() => {
    if (!updatedAt) { setAge(""); return; }
    setAge(formatAge(updatedAt));
    const interval = setInterval(() => setAge(formatAge(updatedAt)), 5000);
    return () => clearInterval(interval);
  }, [updatedAt]);

  if (!gate) return (
    <span className="text-[9px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>X-108 —</span>
  );
  const g = GATE_COLORS[gate];
  return (
    <div className="flex items-center gap-1.5">
      <div className="flex items-center gap-1 px-2 py-0.5 rounded text-[9px] font-mono font-bold"
        style={{ background: g.bg, border: `1px solid ${g.color}40`, color: g.color }}>
        <span>X-108</span>
        <span>{gate}</span>
      </div>
      {age && (
        <span className="text-[8px] font-mono hidden md:inline"
          style={{ color: "oklch(0.38 0.01 240)" }}>
          · {age}
        </span>
      )}
    </div>
  );
}

// ─── ProofPill ───────────────────────────────────────────────────────────────
function ProofPill({ status }: { status: "COMPLETE" | "PARTIAL" | "MISSING" | null }) {
  if (!status) return (
    <span className="text-[9px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>Proof —</span>
  );
  const cfg = {
    COMPLETE: { color: "oklch(0.72 0.18 145)", label: "✓ Proof" },
    PARTIAL:  { color: "oklch(0.72 0.18 45)",  label: "⚠ Proof" },
    MISSING:  { color: "oklch(0.65 0.25 25)",  label: "✗ Proof" },
  }[status];
  return (
    <span className="text-[9px] font-mono font-bold" style={{ color: cfg.color }}>{cfg.label}</span>
  );
}

// ─── StatusRail ──────────────────────────────────────────────────────────────
export default function StatusRail() {
  const { mode, source, x108Gate, lastDecisionId, proofStatus, gateUpdatedAt } = useWorld();

  return (
    <div
      className="flex items-center justify-between px-4 py-1 gap-2 overflow-x-auto"
      style={{
        background: "oklch(0.085 0.01 240)",
        borderBottom: "1px solid oklch(0.16 0.01 240)",
        minHeight: "28px",
      }}
    >
      {/* Gauche : filtre monde */}
      <WorldFilter />

      {/* Centre : mode + source */}
      <div className="flex items-center gap-2">
        <ModePill mode={mode} />
        <span className="text-[9px] font-mono hidden md:inline" style={{ color: "oklch(0.40 0.01 240)" }}>
          {source}
        </span>
      </div>

      {/* Droite : X-108 + fraîcheur + Last Decision + Proof */}
      <div className="flex items-center gap-2">
        <GatePill gate={x108Gate} updatedAt={gateUpdatedAt} />
        {lastDecisionId && (
          <span className="text-[9px] font-mono hidden lg:inline" style={{ color: "oklch(0.45 0.01 240)" }}>
            #{lastDecisionId.slice(0, 8)}
          </span>
        )}
        <ProofPill status={proofStatus} />
      </div>
    </div>
  );
}
