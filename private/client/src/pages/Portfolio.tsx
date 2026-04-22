/**
 * Portfolio.tsx — OS4 v17
 * Personal financial laboratory — OAuth-linked persistent portfolio.
 * Shows wallet state, positions, P&L history, and Guard X-108 protection stats.
 */
import React, { useState, useEffect, useRef } from "react";
import { Chart, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler } from "chart.js";

Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler);
import { Line } from "react-chartjs-2";
import { Link } from "wouter";
import { trpc } from "@/lib/trpc";
import { useAuth } from "@/_core/hooks/useAuth";
import { getLoginUrl } from "@/const";

// ─── PnlChart ─────────────────────────────────────────────────────────────────
interface SnapRow { id: number; capital: number; pnl: number; guardBlocks: number; capitalSaved: number; snapshotAt: Date | number; }

function PnlChart({ snapshots }: { snapshots: SnapRow[] }) {
  const sorted = [...snapshots].sort((a, b) => +new Date(a.snapshotAt) - +new Date(b.snapshotAt));
  const labels = sorted.map(s => new Date(s.snapshotAt).toLocaleTimeString("en-US", { hour12: false, hour: "2-digit", minute: "2-digit" }));
  const capitalData = sorted.map(s => s.capital);
  const baseline = 125000;

  const data = {
    labels,
    datasets: [
      {
        label: "Capital (€)",
        data: capitalData,
        borderColor: "#4ade80",
        backgroundColor: "rgba(74,222,128,0.08)",
        borderWidth: 2,
        pointRadius: 4,
        pointBackgroundColor: sorted.map((s: SnapRow) => s.guardBlocks > 0 ? "#f87171" : "#4ade80"),
        pointBorderColor: sorted.map((s: SnapRow) => s.guardBlocks > 0 ? "#f87171" : "#4ade80"),
        fill: true,
        tension: 0.3,
      },
      {
        label: "Baseline (€)",
        data: sorted.map(() => baseline),
        borderColor: "rgba(255,255,255,0.15)",
        borderWidth: 1,
        borderDash: [4, 4],
        pointRadius: 0,
        fill: false,
        tension: 0,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "oklch(0.14 0.01 240)",
        titleColor: "oklch(0.72 0.18 145)",
        bodyColor: "oklch(0.80 0.01 240)",
        borderColor: "oklch(0.22 0.01 240)",
        borderWidth: 1,
        callbacks: {
          label: (ctx: any) => {
            const snap = sorted[ctx.dataIndex];
            const lines = [`Capital: €${ctx.raw.toLocaleString()}`];
            if (snap?.guardBlocks > 0) lines.push(`⛔ Guard blocks: ${snap.guardBlocks}`);
            if (snap?.capitalSaved > 0) lines.push(`✅ Saved: €${snap.capitalSaved.toLocaleString()}`);
            return lines;
          },
        },
      },
    },
    scales: {
      x: { ticks: { color: "rgba(255,255,255,0.3)", font: { family: "monospace", size: 10 } }, grid: { color: "rgba(255,255,255,0.04)" } },
      y: { ticks: { color: "rgba(255,255,255,0.3)", font: { family: "monospace", size: 10 }, callback: (v: any) => `€${(v/1000).toFixed(0)}k` }, grid: { color: "rgba(255,255,255,0.04)" } },
    },
  };

  return (
    <div className="rounded p-4" style={{ background: "oklch(0.12 0.01 240)" }}>
      <div className="flex items-center justify-between mb-3">
        <div className="text-[10px] font-mono uppercase tracking-widest" style={{ color: "oklch(0.45 0.01 240)" }}>P&L History</div>
        <div className="flex items-center gap-3 text-[10px] font-mono">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ background: "#4ade80" }} />Capital</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ background: "#f87171" }} />Guard Block</span>
          <span className="flex items-center gap-1"><span className="w-4 h-px" style={{ background: "rgba(255,255,255,0.2)" }} />Baseline 125k</span>
        </div>
      </div>
      <div style={{ height: "220px" }}>
        <Line data={data} options={options as any} />
      </div>
    </div>
  );
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
function fmt(n: number, decimals = 2) {
  return n.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}
function fmtPct(n: number) {
  const sign = n >= 0 ? "+" : "";
  return `${sign}${(n * 100).toFixed(2)}%`;
}
function fmtCurrency(n: number) {
  return `€${fmt(n, 0)}`;
}

const DOMAIN_COLORS: Record<string, string> = {
  trading: "#60a5fa",
  bank: "#a78bfa",
  ecom: "#34d399",
};

// ─── Component ─────────────────────────────────────────────────────────────

// Predictions High Risk : détermine si le mode défensif est actif
// (Flash Crash Risk 73% ou Supply Shock Warning 82% = HIGH)
const HIGH_RISK_PREDICTIONS = [
  { id: "flash-crash", title: "Flash Crash Risk", probability: 73, domain: "Trading", coherence: "0.40", lock: "15s" },
  { id: "supply-shock", title: "Supply Shock Warning", probability: 82, domain: "E-Commerce", coherence: "0.45", lock: "20s" },
];

export default function Portfolio() {
  const { user, loading: authLoading } = useAuth();
  const [activeTab, setActiveTab] = useState<"overview" | "positions" | "history" | "correlation">("overview");
  const [corrDays, setCorrDays] = useState(7);
  const [alertThreshold, setAlertThreshold] = useState(-5000);
  // Mode défensif actif si au moins une prédiction HIGH RISK est présente
  const defensiveModeActive = HIGH_RISK_PREDICTIONS.length > 0;

  const walletQuery = trpc.portfolio.getWallet.useQuery(undefined, {
    enabled: !!user,
    refetchInterval: 30000,
  });
  const positionsQuery = trpc.portfolio.getPositions.useQuery(undefined, {
    enabled: !!user && activeTab === "positions",
  });
  const historyQuery = trpc.portfolio.getHistory.useQuery(
    { limit: 30 },
    { enabled: !!user && activeTab === "history" }
  );
  const correlationQuery = trpc.portfolio.getCorrelationHistory.useQuery(
    { days: corrDays },
    { enabled: !!user && activeTab === "correlation", refetchInterval: 60000 }
  );

  const utils = trpc.useUtils();
  const saveSnapshotMut = trpc.portfolio.saveSnapshot.useMutation({
    onSuccess: () => utils.portfolio.getHistory.invalidate(),
  });

  const wallet = walletQuery.data;

  // ─── Not logged in ─────────────────────────────────────────────────────────
  if (authLoading && !user) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="font-mono text-sm" style={{ color: "oklch(0.55 0.01 240)" }}>
          Authenticating...
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6">
        <div className="text-center">
          <div className="text-[10px] font-mono tracking-[0.3em] uppercase mb-3" style={{ color: "oklch(0.72 0.18 145)" }}>
            Obsidia Labs — OS4
          </div>
          <h1 className="font-mono font-bold text-2xl text-foreground mb-2">Personal Portfolio</h1>
          <p className="font-mono text-sm max-w-md text-center" style={{ color: "oklch(0.55 0.01 240)" }}>
            Sign in to access your personal financial laboratory. Your wallet, positions, and Guard X-108
            protection history are saved across sessions.
          </p>
        </div>
        <a
          href={getLoginUrl()}
          className="px-6 py-3 rounded font-mono text-sm font-bold"
          style={{ background: "oklch(0.72 0.18 145)", color: "oklch(0.10 0.01 240)" }}
        >
          Sign in with Manus OAuth →
        </a>
        <Link href="/how-it-works" className="font-mono text-xs" style={{ color: "oklch(0.55 0.01 240)" }}>
          Understand the system first →
        </Link>
      </div>
    );
  }

  // ─── Logged in ─────────────────────────────────────────────────────────────
  return (
    <div className="flex flex-col gap-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between pt-6">
        <div>
          <div className="text-[10px] font-mono tracking-[0.3em] uppercase mb-1" style={{ color: "oklch(0.72 0.18 145)" }}>
            Obsidia Labs — OS4
          </div>
          <div className="flex items-center gap-3">
            <h1 className="font-mono font-bold text-2xl text-foreground">
              Portfolio
              <span className="ml-3 text-sm font-normal" style={{ color: "oklch(0.55 0.01 240)" }}>
                {user.name ?? user.email ?? "Anonymous"}
              </span>
            </h1>
            {/* Badge Mode Défensif Actif */}
            {defensiveModeActive && (
              <Link href="/predictions">
                <div
                  className="flex items-center gap-2 px-3 py-1.5 rounded-full font-mono text-[10px] font-bold cursor-pointer"
                  style={{ background: "#f8717120", border: "1px solid #f8717155", color: "#f87171" }}
                  title={`${HIGH_RISK_PREDICTIONS.length} prédiction(s) à haut risque active(s)`}
                >
                  <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: "#f87171", display: "inline-block" }} />
                  Mode Défensif Actif
                  <span style={{ color: "#f87171", opacity: 0.7 }}>({HIGH_RISK_PREDICTIONS.length})</span>
                </div>
              </Link>
            )}
          </div>
        </div>
        <div className="flex items-center gap-3">
          {wallet && (
            <button
              onClick={() => saveSnapshotMut.mutate({
                capital: wallet.capital,
                pnl: wallet.pnl24h,
                guardBlocks: wallet.guardBlocks,
                capitalSaved: wallet.capitalSaved,
              })}
              disabled={saveSnapshotMut.isPending}
              className="px-3 py-1.5 rounded font-mono text-xs border"
              style={{ borderColor: "oklch(0.72 0.18 145 / 0.4)", color: "oklch(0.72 0.18 145)" }}
            >
              {saveSnapshotMut.isPending ? "Saving..." : "Save Snapshot"}
            </button>
          )}
        </div>
      </div>

      {/* Wallet Summary Cards */}
      {walletQuery.isLoading ? (
        <div className="grid grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="rounded p-4 animate-pulse" style={{ background: "oklch(0.12 0.01 240)" }}>
              <div className="h-3 w-16 rounded mb-2" style={{ background: "oklch(0.20 0.01 240)" }} />
              <div className="h-6 w-24 rounded" style={{ background: "oklch(0.20 0.01 240)" }} />
            </div>
          ))}
        </div>
      ) : wallet ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="rounded p-4" style={{ background: "oklch(0.12 0.01 240)" }}>
            <div className="text-[10px] font-mono uppercase tracking-widest mb-1" style={{ color: "oklch(0.45 0.01 240)" }}>Capital</div>
            <div className="font-mono font-bold text-xl text-foreground">{fmtCurrency(wallet.capital)}</div>
            <div className="text-[10px] font-mono mt-1" style={{ color: wallet.pnl24h >= 0 ? "#4ade80" : "#f87171" }}>
              {fmtPct(wallet.pnl24hPct)} 24h
            </div>
          </div>
          <div className="rounded p-4" style={{ background: "oklch(0.12 0.01 240)" }}>
            <div className="text-[10px] font-mono uppercase tracking-widest mb-1" style={{ color: "oklch(0.45 0.01 240)" }}>P&L 24h</div>
            <div className="font-mono font-bold text-xl" style={{ color: wallet.pnl24h >= 0 ? "#4ade80" : "#f87171" }}>
              {wallet.pnl24h >= 0 ? "+" : ""}{fmtCurrency(wallet.pnl24h)}
            </div>
            <div className="text-[10px] font-mono mt-1" style={{ color: "oklch(0.45 0.01 240)" }}>unrealized</div>
          </div>
          <div className="rounded p-4" style={{ background: "oklch(0.12 0.01 240)" }}>
            <div className="text-[10px] font-mono uppercase tracking-widest mb-1" style={{ color: "oklch(0.45 0.01 240)" }}>Guard Blocks</div>
            <div className="font-mono font-bold text-xl" style={{ color: "#f87171" }}>{wallet.guardBlocks}</div>
            <div className="text-[10px] font-mono mt-1" style={{ color: "oklch(0.45 0.01 240)" }}>by X-108</div>
          </div>
          <div className="rounded p-4" style={{ background: "oklch(0.12 0.01 240)" }}>
            <div className="text-[10px] font-mono uppercase tracking-widest mb-1" style={{ color: "oklch(0.45 0.01 240)" }}>Capital Saved</div>
            <div className="font-mono font-bold text-xl" style={{ color: "oklch(0.72 0.18 145)" }}>{fmtCurrency(wallet.capitalSaved)}</div>
            <div className="text-[10px] font-mono mt-1" style={{ color: "oklch(0.45 0.01 240)" }}>by guard</div>
          </div>
        </div>
      ) : null}

      {/* Tabs */}
      <div className="flex gap-1 border-b" style={{ borderColor: "oklch(0.20 0.01 240)" }}>
        {(["overview", "positions", "history", "correlation"] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className="px-4 py-2 font-mono text-xs uppercase tracking-widest"
            style={{
              color: activeTab === tab ? "oklch(0.72 0.18 145)" : "oklch(0.45 0.01 240)",
              borderBottom: activeTab === tab ? "2px solid oklch(0.72 0.18 145)" : "2px solid transparent",
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === "overview" && wallet && (
        <div className="grid grid-cols-2 gap-6">
          {/* Bank Account */}
          <div className="rounded p-5" style={{ background: "oklch(0.12 0.01 240)" }}>
            <div className="text-[10px] font-mono uppercase tracking-widest mb-3" style={{ color: "#a78bfa" }}>
              Bank Account
            </div>
            <div className="flex justify-between mb-2">
              <span className="font-mono text-xs" style={{ color: "oklch(0.55 0.01 240)" }}>Balance</span>
              <span className="font-mono text-sm text-foreground">{fmtCurrency(wallet.bankBalance)}</span>
            </div>
            <div className="flex justify-between mb-3">
              <span className="font-mono text-xs" style={{ color: "oklch(0.55 0.01 240)" }}>Liquidity Ratio</span>
              <span className="font-mono text-sm" style={{ color: wallet.bankLiquidity > 0.6 ? "#4ade80" : "#fbbf24" }}>
                {(wallet.bankLiquidity * 100).toFixed(1)}%
              </span>
            </div>
            <div className="w-full rounded-full h-1.5" style={{ background: "oklch(0.20 0.01 240)" }}>
              <div
                className="h-1.5 rounded-full"
                style={{
                  width: `${Math.min(wallet.bankLiquidity * 100, 100)}%`,
                  background: wallet.bankLiquidity > 0.6 ? "#4ade80" : "#fbbf24",
                }}
              />
            </div>
            <Link href="/bank" className="block mt-3 text-[10px] font-mono" style={{ color: "#a78bfa" }}>
              Open BankWorld →
            </Link>
          </div>

          {/* Guard X-108 Stats */}
          <div className="rounded p-5" style={{ background: "oklch(0.12 0.01 240)" }}>
            <div className="text-[10px] font-mono uppercase tracking-widest mb-3" style={{ color: "oklch(0.72 0.18 145)" }}>
              Guard X-108 Protection
            </div>
            <div className="flex justify-between mb-2">
              <span className="font-mono text-xs" style={{ color: "oklch(0.55 0.01 240)" }}>Blocks</span>
              <span className="font-mono text-sm" style={{ color: "#f87171" }}>{wallet.guardBlocks}</span>
            </div>
            <div className="flex justify-between mb-2">
              <span className="font-mono text-xs" style={{ color: "oklch(0.55 0.01 240)" }}>Capital Saved</span>
              <span className="font-mono text-sm" style={{ color: "oklch(0.72 0.18 145)" }}>{fmtCurrency(wallet.capitalSaved)}</span>
            </div>
            <div className="flex justify-between mb-3">
              <span className="font-mono text-xs" style={{ color: "oklch(0.55 0.01 240)" }}>Protection Rate</span>
              <span className="font-mono text-sm" style={{ color: "#4ade80" }}>
                {wallet.capital > 0 ? ((wallet.capitalSaved / (wallet.capital + wallet.capitalSaved)) * 100).toFixed(1) : "0.0"}%
              </span>
            </div>
            <Link href="/control" className="block mt-3 text-[10px] font-mono" style={{ color: "oklch(0.72 0.18 145)" }}>
              Open Control Tower →
            </Link>
          </div>

          {/* Quick Actions */}
          <div className="col-span-2 rounded p-5" style={{ background: "oklch(0.12 0.01 240)" }}>
            <div className="text-[10px] font-mono uppercase tracking-widest mb-3" style={{ color: "oklch(0.45 0.01 240)" }}>
              Quick Actions
            </div>
            <div className="flex gap-3 flex-wrap">
              <Link href="/trading" className="px-4 py-2 rounded font-mono text-xs font-bold" style={{ background: "#60a5fa22", color: "#60a5fa", border: "1px solid #60a5fa44" }}>
                Run Trading Simulation
              </Link>
              <Link href="/bank" className="px-4 py-2 rounded font-mono text-xs font-bold" style={{ background: "#a78bfa22", color: "#a78bfa", border: "1px solid #a78bfa44" }}>
                Open BankWorld
              </Link>
              <Link href="/stress" className="px-4 py-2 rounded font-mono text-xs font-bold" style={{ background: "#f8717122", color: "#f87171", border: "1px solid #f8717144" }}>
                Run Stress Test
              </Link>
              <Link href="/proof" className="px-4 py-2 rounded font-mono text-xs font-bold" style={{ background: "oklch(0.72 0.18 145 / 0.15)", color: "oklch(0.72 0.18 145)", border: "1px solid oklch(0.72 0.18 145 / 0.3)" }}>
                View Proofs
              </Link>
            </div>
          </div>
        </div>
      )}

      {activeTab === "positions" && (
        <div>
          {positionsQuery.isLoading ? (
            <div className="font-mono text-sm text-center py-8" style={{ color: "oklch(0.45 0.01 240)" }}>Loading positions...</div>
          ) : !positionsQuery.data || positionsQuery.data.length === 0 ? (
            <div className="text-center py-12">
              <div className="font-mono text-sm mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>No open positions</div>
              <div className="font-mono text-xs" style={{ color: "oklch(0.35 0.01 240)" }}>
                Run a simulation to create positions
              </div>
              <Link href="/trading" className="inline-block mt-4 px-4 py-2 rounded font-mono text-xs" style={{ background: "#60a5fa22", color: "#60a5fa" }}>
                TradingWorld →
              </Link>
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              {positionsQuery.data.map(pos => (
                <div key={pos.id} className="flex items-center justify-between rounded p-4" style={{ background: "oklch(0.12 0.01 240)" }}>
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full" style={{ background: DOMAIN_COLORS[pos.domain] ?? "#888" }} />
                    <div>
                      <div className="font-mono text-sm font-bold text-foreground">{pos.asset}</div>
                      <div className="font-mono text-[10px]" style={{ color: "oklch(0.45 0.01 240)" }}>{pos.domain}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-mono text-sm text-foreground">{fmt(pos.quantity, 4)} units</div>
                    <div className="font-mono text-xs" style={{ color: "oklch(0.45 0.01 240)" }}>
                      avg {fmtCurrency(pos.avgEntryPrice)}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-mono text-sm text-foreground">{fmtCurrency(pos.currentValue)}</div>
                    <div className="font-mono text-xs" style={{ color: pos.unrealizedPnl >= 0 ? "#4ade80" : "#f87171" }}>
                      {pos.unrealizedPnl >= 0 ? "+" : ""}{fmtCurrency(pos.unrealizedPnl)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === "history" && (
        <div className="flex flex-col gap-4">
          {historyQuery.isLoading ? (
            <div className="font-mono text-sm text-center py-8" style={{ color: "oklch(0.45 0.01 240)" }}>Loading history...</div>
          ) : !historyQuery.data || historyQuery.data.length === 0 ? (
            <div className="text-center py-12">
              <div className="font-mono text-sm mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>No snapshots yet</div>
              <div className="font-mono text-xs" style={{ color: "oklch(0.35 0.01 240)" }}>
                Click "Save Snapshot" to record your current portfolio state
              </div>
            </div>
          ) : (
            <>
              {/* P&L Chart */}
              <PnlChart snapshots={historyQuery.data} />
              {/* Table */}
              <div className="flex flex-col gap-1.5">
                {historyQuery.data.map(snap => (
                  <div key={snap.id} className="flex items-center justify-between rounded p-3" style={{ background: "oklch(0.12 0.01 240)" }}>
                    <div className="font-mono text-xs" style={{ color: "oklch(0.45 0.01 240)" }}>
                      {new Date(snap.snapshotAt).toLocaleString()}
                    </div>
                    <div className="font-mono text-sm text-foreground">{fmtCurrency(snap.capital)}</div>
                    <div className="font-mono text-xs" style={{ color: snap.pnl >= 0 ? "#4ade80" : "#f87171" }}>
                      {snap.pnl >= 0 ? "+" : ""}{fmtCurrency(snap.pnl)}
                    </div>
                    <div className="font-mono text-xs" style={{ color: "#f87171" }}>{snap.guardBlocks} blocks</div>
                    <div className="font-mono text-xs" style={{ color: "oklch(0.72 0.18 145)" }}>
                      {fmtCurrency(snap.capitalSaved)} saved
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {/* ─── Correlation Panel ─────────────────────────────────────────────── */}
      {activeTab === "correlation" && (
        <CorrelationPanel
          query={correlationQuery}
          days={corrDays}
          onDaysChange={setCorrDays}
          alertThreshold={alertThreshold}
          onAlertThresholdChange={setAlertThreshold}
        />
      )}
    </div>
  );
}

// ─── Domain config for Correlation Panel ─────────────────────────────────────
const CORR_DOMAIN: Record<string, { color: string; bg: string; icon: string; label: string }> = {
  trading: { color: "#3b82f6", bg: "rgba(59,130,246,0.12)",  icon: "📈", label: "Trading" },
  bank:    { color: "#22c55e", bg: "rgba(34,197,94,0.12)",   icon: "🏦", label: "Bank" },
  ecom:    { color: "#a855f7", bg: "rgba(168,85,247,0.12)",  icon: "🛒", label: "E-Com" },
};

interface CorrelationPanelProps {
  query: ReturnType<typeof trpc.portfolio.getCorrelationHistory.useQuery>;
  days: number;
  onDaysChange: (d: number) => void;
  alertThreshold: number;
  onAlertThresholdChange: (v: number) => void;
}

interface CorrRow {
  id: number;
  capital: number;
  pnl: number;
  guardBlocks: number;
  capitalSaved: number;
  domain: "trading" | "bank" | "ecom";
  scenarioName: string | null;
  timestamp: number;
}
interface CorrStats {
  totalSims: number;
  totalPnl: number;
  totalGuardBlocks: number;
  totalCapitalSaved: number;
  byDomain: Record<string, { count: number; pnl: number; guardBlocks: number }>;
}
interface CorrData {
  rows: CorrRow[];
  stats: CorrStats;
}

function CorrelationPanel({ query, days, onDaysChange, alertThreshold, onAlertThresholdChange }: CorrelationPanelProps) {
  const data = query.data as CorrData | undefined;
  const isLoading = query.isLoading;
  const [thresholdInput, setThresholdInput] = React.useState(String(alertThreshold));
  const [saved, setSaved] = React.useState(false);

  const handleSaveThreshold = () => {
    const v = Number(thresholdInput);
    if (isNaN(v)) return;
    onAlertThresholdChange(v);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="flex flex-col gap-5">
      {/* Header row */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <div className="font-mono text-[9px] font-bold tracking-widest mb-0.5" style={{ color: "oklch(0.45 0.01 240)" }}>SIMULATION CORRELATION PANEL</div>
          <div className="font-mono text-xs" style={{ color: "oklch(0.55 0.01 240)" }}>Analyse des simulations exécutées par domaine</div>
        </div>
        {/* Period selector */}
        <div className="flex gap-1.5">
          {[1, 3, 7, 14, 30].map(d => (
            <button key={d} onClick={() => onDaysChange(d)}
              className="px-2.5 py-1 rounded font-mono text-[10px] font-bold"
              style={{
                background: days === d ? "oklch(0.72 0.18 145 / 0.15)" : "oklch(0.12 0.01 240)",
                border: `1px solid ${days === d ? "oklch(0.72 0.18 145)" : "oklch(0.20 0.01 240)"}`,
                color: days === d ? "oklch(0.72 0.18 145)" : "oklch(0.50 0.01 240)",
              }}>{d}j</button>
          ))}
        </div>
      </div>

      {/* Alert threshold config */}
      <div className="rounded p-4" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.22 0.01 240)" }}>
        <div className="flex items-center gap-2 mb-3">
          <span className="text-sm">⚠️</span>
          <div className="font-mono text-[9px] font-bold tracking-widest" style={{ color: "oklch(0.45 0.01 240)" }}>SEUIL D’ALERTE PNL</div>
          <div className="ml-auto font-mono text-[9px]" style={{ color: "oklch(0.35 0.01 240)" }}>Notification envoyée si PnL &lt; seuil</div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 flex-1">
            <span className="font-mono text-xs" style={{ color: "oklch(0.55 0.01 240)" }}>Seuil :</span>
            <input
              type="number"
              value={thresholdInput}
              onChange={e => setThresholdInput(e.target.value)}
              className="flex-1 rounded px-2 py-1 font-mono text-xs"
              style={{ background: "oklch(0.09 0.01 240)", border: "1px solid oklch(0.25 0.01 240)", color: "#f87171", maxWidth: "120px" }}
              step="500"
            />
            <span className="font-mono text-xs" style={{ color: "oklch(0.55 0.01 240)" }}>€</span>
          </div>
          <button
            onClick={handleSaveThreshold}
            className="px-3 py-1 rounded font-mono text-[10px] font-bold"
            style={{
              background: saved ? "oklch(0.72 0.18 145 / 0.15)" : "oklch(0.14 0.01 240)",
              border: `1px solid ${saved ? "oklch(0.72 0.18 145)" : "oklch(0.25 0.01 240)"}`,
              color: saved ? "oklch(0.72 0.18 145)" : "oklch(0.60 0.01 240)",
            }}
          >
            {saved ? "✓ Enregistré" : "Appliquer"}
          </button>
        </div>
        <div className="mt-2 font-mono text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>
          Seuil actif : <span style={{ color: "#f87171" }}>{alertThreshold.toLocaleString("fr-FR")} €</span>
          {" — "}
          <span>Une notification est envoyée au propriétaire dès qu’une simulation produit un PnL inférieur à ce seuil.</span>
        </div>
        {/* Visual examples of what triggers an alert */}
        <div className="mt-3 flex gap-2 flex-wrap">
          {[-1000, -5000, -10000, -25000].map(ex => (
            <button key={ex}
              onClick={() => { setThresholdInput(String(ex)); }}
              className="px-2 py-0.5 rounded font-mono text-[9px]"
              style={{
                background: alertThreshold === ex ? "rgba(248,113,113,0.15)" : "oklch(0.10 0.01 240)",
                border: `1px solid ${alertThreshold === ex ? "#f87171" : "oklch(0.20 0.01 240)"}`,
                color: alertThreshold === ex ? "#f87171" : "oklch(0.45 0.01 240)",
              }}
            >{ex.toLocaleString("fr-FR")} €</button>
          ))}
        </div>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-16">
          <div className="w-6 h-6 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {!isLoading && data && (
        <>
          {/* KPI summary cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label: "Simulations",    value: String(data.stats.totalSims),                                          color: "oklch(0.72 0.18 145)", icon: "🔬" },
              { label: "PnL Total",      value: `${data.stats.totalPnl >= 0 ? "+" : ""}${fmtCurrency(data.stats.totalPnl)}`, color: data.stats.totalPnl >= 0 ? "#4ade80" : "#f87171", icon: "📊" },
              { label: "Guard Blocks",   value: String(data.stats.totalGuardBlocks),                                   color: "#f87171",              icon: "🛡" },
              { label: "Capital Saved",  value: fmtCurrency(data.stats.totalCapitalSaved),                             color: "oklch(0.72 0.18 145)", icon: "✅" },
            ].map(card => (
              <div key={card.label} className="rounded p-4" style={{ background: "oklch(0.12 0.01 240)" }}>
                <div className="flex items-center gap-1.5 mb-2">
                  <span className="text-sm">{card.icon}</span>
                  <div className="font-mono text-[9px] font-bold tracking-widest" style={{ color: "oklch(0.45 0.01 240)" }}>{card.label.toUpperCase()}</div>
                </div>
                <div className="font-mono font-bold text-lg" style={{ color: card.color }}>{card.value}</div>
              </div>
            ))}
          </div>

          {/* Per-domain breakdown */}
          {Object.keys(data.stats.byDomain).length > 0 && (
            <div className="rounded p-4" style={{ background: "oklch(0.12 0.01 240)" }}>
              <div className="font-mono text-[9px] font-bold tracking-widest mb-3" style={{ color: "oklch(0.45 0.01 240)" }}>RÉPARTITION PAR DOMAINE</div>
              <div className="grid grid-cols-3 gap-3">
                {Object.entries(data.stats.byDomain).map(([domain, stats]) => {
                  const dc = CORR_DOMAIN[domain] ?? { color: "#888", bg: "rgba(136,136,136,0.1)", icon: "❓", label: domain };
                  const totalSims = data.stats.totalSims || 1;
                  const pct = Math.round((stats.count / totalSims) * 100);
                  return (
                    <div key={domain} className="rounded p-3" style={{ background: dc.bg, border: `1px solid ${dc.color}33` }}>
                      <div className="flex items-center gap-1.5 mb-2">
                        <span className="text-sm">{dc.icon}</span>
                        <span className="font-mono text-[9px] font-bold" style={{ color: dc.color }}>{dc.label.toUpperCase()}</span>
                        <span className="ml-auto font-mono text-[9px]" style={{ color: dc.color }}>{pct}%</span>
                      </div>
                      <div className="w-full rounded-full h-1 mb-2" style={{ background: "oklch(0.20 0.01 240)" }}>
                        <div className="h-1 rounded-full" style={{ width: `${pct}%`, background: dc.color }} />
                      </div>
                      <div className="font-mono text-xs font-bold" style={{ color: dc.color }}>{stats.count} sim{stats.count > 1 ? "s" : ""}</div>
                      <div className="font-mono text-[10px] mt-0.5" style={{ color: "oklch(0.55 0.01 240)" }}>
                        PnL : <span style={{ color: stats.pnl >= 0 ? "#4ade80" : "#f87171" }}>{stats.pnl >= 0 ? "+" : ""}{fmtCurrency(stats.pnl)}</span>
                      </div>
                      <div className="font-mono text-[10px]" style={{ color: "oklch(0.55 0.01 240)" }}>
                        Blocks : <span style={{ color: "#f87171" }}>{stats.guardBlocks}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Simulation log table */}
          {data.rows.length === 0 ? (
            <div className="text-center py-12 rounded" style={{ background: "oklch(0.12 0.01 240)" }}>
              <div className="font-mono text-sm mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>Aucune simulation sur {days} jour{days > 1 ? "s" : ""}</div>
              <div className="font-mono text-xs" style={{ color: "oklch(0.35 0.01 240)" }}>Lancez une simulation depuis TradingWorld, BankWorld ou EcomWorld</div>
              <div className="flex gap-3 justify-center mt-4">
                <Link href="/trading" className="px-3 py-1.5 rounded font-mono text-xs" style={{ background: "#3b82f622", color: "#3b82f6", border: "1px solid #3b82f644" }}>Trading →</Link>
                <Link href="/bank" className="px-3 py-1.5 rounded font-mono text-xs" style={{ background: "#22c55e22", color: "#22c55e", border: "1px solid #22c55e44" }}>Bank →</Link>
                <Link href="/ecom" className="px-3 py-1.5 rounded font-mono text-xs" style={{ background: "#a855f722", color: "#a855f7", border: "1px solid #a855f744" }}>E-Com →</Link>
              </div>
            </div>
          ) : (
            <div className="rounded overflow-hidden" style={{ border: "1px solid oklch(0.20 0.01 240)" }}>
              <div className="font-mono text-[9px] font-bold tracking-widest px-4 py-2" style={{ background: "oklch(0.10 0.01 240)", color: "oklch(0.45 0.01 240)" }}>
                JOURNAL DES SIMULATIONS — {days}J — {data.rows.length} entrée{data.rows.length > 1 ? "s" : ""}
              </div>
              {/* Table header */}
              <div className="grid font-mono text-[9px] font-bold tracking-widest px-4 py-2" style={{ gridTemplateColumns: "1fr 2fr 1fr 1fr 1fr 1fr", background: "oklch(0.11 0.01 240)", color: "oklch(0.40 0.01 240)" }}>
                <span>HEURE</span>
                <span>SCÉNARIO</span>
                <span>DOMAINE</span>
                <span>CAPITAL</span>
                <span>PNL</span>
                <span>GUARD</span>
              </div>
              {/* Rows */}
              <div className="flex flex-col" style={{ borderTop: "1px solid oklch(0.16 0.01 240)" }}>
                {data.rows.map(row => {
                  const dc = CORR_DOMAIN[row.domain] ?? { color: "#888", bg: "transparent", icon: "❓", label: row.domain };
                  return (
                    <div key={row.id} className="grid items-center px-4 py-2.5 font-mono text-xs" style={{ gridTemplateColumns: "1fr 2fr 1fr 1fr 1fr 1fr" }}>
                      <span style={{ color: "oklch(0.45 0.01 240)" }}>
                        {new Date(row.timestamp).toLocaleString("fr-FR", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" })}
                      </span>
                      <span className="truncate" style={{ color: "oklch(0.80 0.01 240)" }} title={row.scenarioName ?? "—"}>
                        {row.scenarioName ?? "—"}
                      </span>
                      <span className="flex items-center gap-1">
                        <span className="text-[10px]">{dc.icon}</span>
                        <span style={{ color: dc.color }}>{dc.label}</span>
                      </span>
                      <span style={{ color: "oklch(0.80 0.01 240)" }}>{fmtCurrency(row.capital)}</span>
                      <span style={{ color: row.pnl >= 0 ? "#4ade80" : "#f87171" }}>
                        {row.pnl >= 0 ? "+" : ""}{fmtCurrency(row.pnl)}
                      </span>
                      <span>
                        {row.guardBlocks > 0
                          ? <span style={{ color: "#f87171" }}>⛔ {row.guardBlocks}</span>
                          : <span style={{ color: "oklch(0.72 0.18 145)" }}>✅ 0</span>}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
