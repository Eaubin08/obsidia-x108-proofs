import React from "react";

interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  trend?: "up" | "down" | "neutral";
  size?: "sm" | "md" | "lg";
  className?: string;
  mono?: boolean;
}

export function MetricCard({
  label,
  value,
  unit,
  trend,
  size = "md",
  className = "",
  mono = true,
}: MetricCardProps) {
  const trendColor =
    trend === "up"
      ? "text-positive"
      : trend === "down"
      ? "text-negative"
      : "text-foreground";

  const valueSize =
    size === "lg"
      ? "text-3xl"
      : size === "sm"
      ? "text-base"
      : "text-xl";

  return (
    <div className={`panel p-3 ${className}`}>
      <div className="metric-label mb-1">{label}</div>
      <div className={`font-bold ${valueSize} ${trendColor} ${mono ? "font-mono" : ""} leading-tight`}>
        {typeof value === "number" ? value.toLocaleString("en-US", { maximumFractionDigits: 4 }) : value}
        {unit && <span className="text-muted-foreground text-sm ml-1">{unit}</span>}
      </div>
    </div>
  );
}

interface DecisionBadgeProps {
  decision: "ALLOW" | "HOLD" | "BLOCK";
  className?: string;
}

export function DecisionBadge({ decision, className = "" }: DecisionBadgeProps) {
  const cls =
    decision === "ALLOW"
      ? "badge-allow"
      : decision === "HOLD"
      ? "badge-hold"
      : "badge-block";
  return (
    <span className={`${cls} ${className} inline-flex items-center gap-1`}>
      <span className="w-1.5 h-1.5 rounded-full inline-block" style={{
        background: decision === "ALLOW" ? "oklch(0.72 0.18 145)" : decision === "HOLD" ? "oklch(0.78 0.18 75)" : "oklch(0.62 0.22 25)"
      }} />
      {decision}
    </span>
  );
}

interface HashDisplayProps {
  label: string;
  hash: string;
  truncate?: boolean;
}

export function HashDisplay({ label, hash, truncate = true }: HashDisplayProps) {
  const display = truncate ? `${hash.slice(0, 8)}…${hash.slice(-6)}` : hash;
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="text-muted-foreground uppercase tracking-wider" style={{ fontSize: "0.65rem" }}>{label}</span>
      <span className="os4-hash font-mono">{display}</span>
    </div>
  );
}

interface X108GateProps {
  tau: number;
  elapsed: number;
  irr: boolean;
  gateActive: boolean;
}

export function X108Gate({ tau, elapsed, irr, gateActive }: X108GateProps) {
  const remaining = Math.max(0, tau - elapsed);
  return (
    <div className={`panel p-2 flex items-center gap-3 text-xs ${gateActive ? "border-warning" : "border-positive"}`}>
      <div className={`w-2 h-2 rounded-full flex-shrink-0 ${gateActive ? "bg-warning-subtle glow-amber" : "bg-positive-subtle glow-green"}`}
           style={{ background: gateActive ? "oklch(0.78 0.18 75)" : "oklch(0.72 0.18 145)" }} />
      <div>
        <div className="font-mono font-bold" style={{ color: gateActive ? "oklch(0.78 0.18 75)" : "oklch(0.72 0.18 145)" }}>
          X-108 {gateActive ? `HOLD — ${remaining.toFixed(1)}s` : "CLEAR"}
        </div>
        <div className="text-muted-foreground" style={{ fontSize: "0.6rem" }}>
          τ={tau}s · elapsed={elapsed.toFixed(1)}s · irr={irr ? "true" : "false"}
        </div>
      </div>
    </div>
  );
}
