/**
 * Market.tsx — OS4 v30
 * Page centrale : lecture du marché par domaine.
 * Flux : Market → Agents → Decision → Guard X-108 → Proof
 * Trois domaines : Trading (live Binance) / Bank / E-Commerce
 */
import React, { useState, useEffect } from "react";
import { Link } from "wouter";
import { trpc } from "@/lib/trpc";
import { useViewMode } from "@/contexts/ViewModeContext";

// ─── Types ────────────────────────────────────────────────────────────────────
type Domain = "trading" | "bank" | "ecom";

// ─── Flux visuel ─────────────────────────────────────────────────────────────
const FLUX_STEPS = [
  { id: "market", label: "Market", icon: "📊", color: "oklch(0.60 0.12 200)", href: "/market" },
  { id: "agents", label: "Agents", icon: "🤖", color: "oklch(0.72 0.18 145)", href: "/control" },
  { id: "decision", label: "Decision", icon: "⚖", color: "#f59e0b", href: "/stream" },
  { id: "guard", label: "Guard X-108", icon: "🛡", color: "#f87171", href: "/engine" },
  { id: "proof", label: "Proof", icon: "⛓", color: "#a78bfa", href: "/proof-center" },
];

// ─── Composant FluxBar ────────────────────────────────────────────────────────
function FluxBar({ active }: { active: string }) {
  return (
    <div className="flex items-center justify-center gap-0 mb-10 flex-wrap">
      {FLUX_STEPS.map((step, i) => (
        <React.Fragment key={step.id}>
          <Link href={step.href}>
            <div
              className="flex items-center gap-1.5 px-3 py-2 rounded font-mono text-[10px] font-bold cursor-pointer"
              style={{
                background: step.id === active ? `${step.color}22` : "oklch(0.12 0.01 240)",
                border: `1px solid ${step.id === active ? step.color : "oklch(0.20 0.01 240)"}`,
                color: step.id === active ? step.color : "oklch(0.45 0.01 240)",
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

// ─── Composant TradingMarket ──────────────────────────────────────────────────
function TradingMarket({ isSimple }: { isSimple: boolean }) {
  const { data, isLoading } = trpc.mirror.prices.useQuery({ symbols: ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"] });

  const REGIME_LABEL: Record<string, string> = {
    BULL: "Bullish",
    BEAR: "Bearish",
    CRASH: "Crash",
    NEUTRAL: "Neutral",
  };
  const REGIME_COLOR: Record<string, string> = {
    BULL: "oklch(0.72 0.18 145)",
    BEAR: "#f87171",
    CRASH: "#ef4444",
    NEUTRAL: "oklch(0.55 0.01 240)",
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 gap-4">
        {[0, 1, 2, 3].map(i => (
          <div key={i} className="rounded-lg animate-pulse" style={{ height: 120, background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }} />
        ))}
      </div>
    );
  }

  const assets = data?.data ?? [];

  return (
    <div>
      {/* Live badge */}
      <div className="flex items-center gap-2 mb-4">
        <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: "oklch(0.72 0.18 145)" }} />
        <span className="font-mono text-[9px] tracking-widest" style={{ color: "oklch(0.45 0.01 240)" }}>
          LIVE MARKET DATA — BINANCE
        </span>
        <span className="font-mono text-[9px]" style={{ color: "oklch(0.35 0.01 240)" }}>
          {data?.success ? "● Connected" : "● Live data"}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        {assets.map(asset => {
          const sym = asset.symbol.replace("USDT", "");
          const change = asset.change24h;
          const isUp = change >= 0;
          const regime = asset.regime as string;
          return (
            <div key={asset.symbol} className="rounded-lg p-4" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono font-bold text-sm text-foreground">{sym}</span>
                <span className="font-mono text-[9px] px-1.5 py-0.5 rounded" style={{ background: `${REGIME_COLOR[regime] ?? "#888"}22`, color: REGIME_COLOR[regime] ?? "#888", border: `1px solid ${REGIME_COLOR[regime] ?? "#888"}44` }}>
                  {REGIME_LABEL[regime] ?? regime}
                </span>
              </div>
              <div className="font-mono font-bold text-xl text-foreground mb-1">
                ${asset.price.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
              <div className="flex items-center gap-3 font-mono text-[10px]">
                <span style={{ color: isUp ? "oklch(0.72 0.18 145)" : "#f87171" }}>
                  {isUp ? "▲" : "▼"} {Math.abs(change * 100).toFixed(2)}%
                </span>
                {!isSimple && (
                  <>
                    <span style={{ color: "oklch(0.45 0.01 240)" }}>Vol: {asset.volatility.toFixed(4)}</span>
                    <span style={{ color: "oklch(0.45 0.01 240)" }}>Fiabilité: {asset.coherence.toFixed(2)}</span>
                  </>
                )}
              </div>
              {isSimple && (
                <div className="mt-2 font-mono text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>
                  {regime === "CRASH" ? "⚠ Risque élevé — Guard peut bloquer" :
                   regime === "BULL" ? "✓ Stable — Guard autorise" :
                   regime === "BEAR" ? "↓ En baisse — Guard peut suspendre" :
                   "→ Stable — Guard monitoring"}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Agent signal */}
      <div className="rounded-lg p-4 mb-4" style={{ background: "oklch(0.72 0.18 145 / 0.07)", border: "1px solid oklch(0.72 0.18 145 / 0.3)" }}>
        <div className="font-mono text-[9px] font-bold tracking-widest mb-2" style={{ color: "oklch(0.72 0.18 145)" }}>AGENT ALPHA — LAST SIGNAL</div>
        <div className="grid grid-cols-3 gap-3 font-mono text-[10px]">
          <div>
            <div style={{ color: "oklch(0.45 0.01 240)" }}>Asset</div>
            <div className="font-bold text-foreground">BTC/USDT</div>
          </div>
          <div>
            <div style={{ color: "oklch(0.45 0.01 240)" }}>Signal</div>
            <div className="font-bold" style={{ color: assets[0]?.regime === "CRASH" ? "#f87171" : "oklch(0.72 0.18 145)" }}>
              {assets[0]?.regime === "CRASH" ? "SELL" : assets[0]?.regime === "BULL" ? "BUY" : "HOLD"}
            </div>
          </div>
          <div>
            <div style={{ color: "oklch(0.45 0.01 240)" }}>Guard verdict</div>
            <div className="font-bold" style={{ color: assets[0]?.coherence > 0.6 ? "oklch(0.72 0.18 145)" : "#f59e0b" }}>
              {assets[0]?.coherence > 0.6 ? "ALLOW" : "HOLD"}
            </div>
          </div>
        </div>
      </div>

      <div className="flex gap-3">
        <Link href="/simulation-worlds/trading">
          <button className="px-4 py-2 rounded font-mono text-xs font-bold" style={{ background: "oklch(0.72 0.18 145)", color: "oklch(0.10 0.01 240)" }}>
            Run Trading Simulation →
          </button>
        </Link>
        <Link href="/mirror">
          <button className="px-4 py-2 rounded font-mono text-xs font-bold" style={{ background: "transparent", color: "oklch(0.60 0.12 200)", border: "1px solid oklch(0.60 0.12 200 / 0.5)" }}>
            Mirror Mode →
          </button>
        </Link>
      </div>
    </div>
  );
}

// ─── Composant BankMarket ─────────────────────────────────────────────────────
function BankMarket({ isSimple }: { isSimple: boolean }) {
  // Données statiques représentatives (pas de query live pour bank)
  const transactions = [
    { id: "TXN-001", amount: 5000, riskScore: 0.08, status: "safe", type: "transfer", from: "ACC-4821", to: "ACC-7734" },
    { id: "TXN-002", amount: 48000, riskScore: 0.72, status: "suspicious", type: "withdrawal", from: "ACC-2291", to: "EXT-8821" },
    { id: "TXN-003", amount: 1200, riskScore: 0.12, status: "safe", type: "payment", from: "ACC-3341", to: "MERCH-442" },
    { id: "TXN-004", amount: 95000, riskScore: 0.89, status: "fraud", type: "transfer", from: "ACC-9921", to: "EXT-0012" },
  ];

  const STATUS_COLOR: Record<string, string> = {
    safe: "oklch(0.72 0.18 145)",
    suspicious: "#f59e0b",
    fraud: "#f87171",
  };
  const GUARD_VERDICT: Record<string, string> = {
    safe: "ALLOW",
    suspicious: "HOLD",
    fraud: "BLOCK",
  };

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <div className="w-1.5 h-1.5 rounded-full" style={{ background: "oklch(0.60 0.12 200)" }} />
        <span className="font-mono text-[9px] tracking-widest" style={{ color: "oklch(0.45 0.01 240)" }}>
          BANK TRANSACTION MONITOR
        </span>
      </div>

      <div className="space-y-3 mb-6">
        {transactions.map(tx => (
          <div key={tx.id} className="rounded-lg p-3" style={{ background: "oklch(0.12 0.01 240)", border: `1px solid ${STATUS_COLOR[tx.status]}33` }}>
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono font-bold text-xs text-foreground">{tx.id}</span>
              <div className="flex items-center gap-2">
                <span className="font-mono text-[9px] px-1.5 py-0.5 rounded" style={{ background: `${STATUS_COLOR[tx.status]}22`, color: STATUS_COLOR[tx.status], border: `1px solid ${STATUS_COLOR[tx.status]}44` }}>
                  {tx.status.toUpperCase()}
                </span>
                <span className="font-mono text-[9px] font-bold px-1.5 py-0.5 rounded" style={{ background: "oklch(0.10 0.01 240)", color: STATUS_COLOR[tx.status], border: `1px solid ${STATUS_COLOR[tx.status]}55` }}>
                  Guard: {GUARD_VERDICT[tx.status]}
                </span>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2 font-mono text-[10px]">
              <div>
                <div style={{ color: "oklch(0.40 0.01 240)" }}>Amount</div>
                <div className="font-bold text-foreground">${tx.amount.toLocaleString()}</div>
              </div>
              <div>
                <div style={{ color: "oklch(0.40 0.01 240)" }}>Risk score</div>
                <div className="font-bold" style={{ color: tx.riskScore > 0.5 ? "#f87171" : "oklch(0.72 0.18 145)" }}>{tx.riskScore.toFixed(2)}</div>
              </div>
              <div>
                <div style={{ color: "oklch(0.40 0.01 240)" }}>Type</div>
                <div className="font-bold text-foreground capitalize">{tx.type}</div>
              </div>
            </div>
            {isSimple && (
              <div className="mt-2 font-mono text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>
                {tx.status === "fraud" ? "⛔ Obsidia blocked this transaction — capital protected" :
                 tx.status === "suspicious" ? "⏸ Obsidia held this transaction for review" :
                 "✓ Transaction validated and executed"}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="flex gap-3">
        <Link href="/simulation-worlds/bank">
          <button className="px-4 py-2 rounded font-mono text-xs font-bold" style={{ background: "oklch(0.60 0.12 200)", color: "oklch(0.10 0.01 240)" }}>
            Run Bank Simulation →
          </button>
        </Link>
      </div>
    </div>
  );
}

// ─── Composant EcomMarket ─────────────────────────────────────────────────────
function EcomMarket({ isSimple }: { isSimple: boolean }) {
  const products = [
    { id: "PROD-001", name: "Wireless Headphones", price: 89.99, stock: 142, demandIndex: "high", priceChange: +0.05, agentAction: "RAISE_PRICE" },
    { id: "PROD-002", name: "USB-C Hub", price: 29.99, stock: 8, demandIndex: "critical", priceChange: +0.15, agentAction: "RAISE_PRICE" },
    { id: "PROD-003", name: "Laptop Stand", price: 49.99, stock: 312, demandIndex: "low", priceChange: -0.10, agentAction: "DISCOUNT" },
    { id: "PROD-004", name: "Mechanical Keyboard", price: 159.99, stock: 45, demandIndex: "medium", priceChange: 0, agentAction: "HOLD" },
  ];

  const DEMAND_COLOR: Record<string, string> = {
    high: "oklch(0.72 0.18 145)",
    critical: "#f87171",
    low: "oklch(0.45 0.01 240)",
    medium: "#f59e0b",
  };
  const GUARD_VERDICT: Record<string, string> = {
    RAISE_PRICE: "HOLD",
    DISCOUNT: "ALLOW",
    HOLD: "ALLOW",
  };
  const GUARD_COLOR: Record<string, string> = {
    HOLD: "#f59e0b",
    ALLOW: "oklch(0.72 0.18 145)",
    BLOCK: "#f87171",
  };

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <div className="w-1.5 h-1.5 rounded-full" style={{ background: "#f59e0b" }} />
        <span className="font-mono text-[9px] tracking-widest" style={{ color: "oklch(0.45 0.01 240)" }}>
          E-COMMERCE PRODUCT MONITOR
        </span>
      </div>

      <div className="space-y-3 mb-6">
        {products.map(prod => {
          const verdict = GUARD_VERDICT[prod.agentAction] ?? "ALLOW";
          return (
            <div key={prod.id} className="rounded-lg p-3" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono font-bold text-xs text-foreground">{prod.name}</span>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[9px] px-1.5 py-0.5 rounded" style={{ background: `${DEMAND_COLOR[prod.demandIndex]}22`, color: DEMAND_COLOR[prod.demandIndex], border: `1px solid ${DEMAND_COLOR[prod.demandIndex]}44` }}>
                    {prod.demandIndex.toUpperCase()}
                  </span>
                  <span className="font-mono text-[9px] font-bold px-1.5 py-0.5 rounded" style={{ background: "oklch(0.10 0.01 240)", color: GUARD_COLOR[verdict], border: `1px solid ${GUARD_COLOR[verdict]}55` }}>
                    Guard: {verdict}
                  </span>
                </div>
              </div>
              <div className="grid grid-cols-4 gap-2 font-mono text-[10px]">
                <div>
                  <div style={{ color: "oklch(0.40 0.01 240)" }}>Price</div>
                  <div className="font-bold text-foreground">${prod.price.toFixed(2)}</div>
                </div>
                <div>
                  <div style={{ color: "oklch(0.40 0.01 240)" }}>Stock</div>
                  <div className="font-bold" style={{ color: prod.stock < 20 ? "#f87171" : "text-foreground" }}>{prod.stock}</div>
                </div>
                <div>
                  <div style={{ color: "oklch(0.40 0.01 240)" }}>Δ Price</div>
                  <div className="font-bold" style={{ color: prod.priceChange > 0 ? "#f87171" : prod.priceChange < 0 ? "oklch(0.72 0.18 145)" : "oklch(0.45 0.01 240)" }}>
                    {prod.priceChange > 0 ? "+" : ""}{(prod.priceChange * 100).toFixed(0)}%
                  </div>
                </div>
                <div>
                  <div style={{ color: "oklch(0.40 0.01 240)" }}>Agent</div>
                  <div className="font-bold text-foreground text-[9px]">{prod.agentAction.replace("_", " ")}</div>
                </div>
              </div>
              {isSimple && (
                <div className="mt-2 font-mono text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>
                  {verdict === "HOLD" ? `⏸ Agent wants to raise price +${(prod.priceChange * 100).toFixed(0)}% — Guard paused for review` :
                   verdict === "BLOCK" ? "⛔ Price change blocked — exceeds coherence threshold" :
                   "✓ Price action validated by Guard"}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="flex gap-3">
        <Link href="/simulation-worlds/ecom">
          <button className="px-4 py-2 rounded font-mono text-xs font-bold" style={{ background: "#f59e0b", color: "oklch(0.10 0.01 240)" }}>
            Run E-Com Simulation →
          </button>
        </Link>
      </div>
    </div>
  );
}

// ─── Page principale ──────────────────────────────────────────────────────────
export default function Market() {
  const [domain, setDomain] = useState<Domain>("trading");
  const { isSimple } = useViewMode();

  const TABS: { id: Domain; label: string; icon: string; color: string }[] = [
    { id: "trading", label: "Trading", icon: "📈", color: "oklch(0.72 0.18 145)" },
    { id: "bank", label: "Bank", icon: "🏦", color: "oklch(0.60 0.12 200)" },
    { id: "ecom", label: "E-Commerce", icon: "🛒", color: "#f59e0b" },
  ];

  return (
    <div className="max-w-5xl mx-auto" style={{ color: "oklch(0.90 0.01 240)", paddingTop: "24px" }}>

      {/* Header */}
      <div className="mb-6 rounded p-5" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.72 0.18 145 / 0.20)" }}>
        <div className="font-mono text-[9px] font-bold tracking-[0.3em] uppercase mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>
          OBSIDIA OS4 — STEP 1 OF 5
        </div>
        <h1 className="font-mono font-bold text-3xl text-foreground mb-2">Market</h1>
        <p className="font-mono text-sm mb-3" style={{ color: "oklch(0.72 0.18 145)" }}>
          The world provides context. Agents observe. Guard X-108 decides.
        </p>
        <p className="font-mono text-xs max-w-2xl leading-relaxed mb-4" style={{ color: "oklch(0.55 0.01 240)" }}>
          {isSimple
            ? "Market data feeds the governance pipeline. Each signal is observed by an autonomous agent, evaluated by Guard X-108, and every decision is cryptographically proven."
            : "Real-time market data by domain. Each signal feeds into the governance pipeline: agent proposal → Guard X-108 evaluation → Verdict → cryptographic proof."}
        </p>
        {/* Pipeline narrative */}
        <div className="flex items-center gap-1 flex-wrap">
          {[
            { label: "WORLD",       color: "#60a5fa", active: true },
            { label: "AGENT",       color: "#a78bfa", active: false },
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

      {/* Flux visuel */}
      <FluxBar active="market" />

      {/* Domain tabs */}
      <div className="flex items-center gap-2 mb-6">
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setDomain(tab.id)}
            className="flex items-center gap-1.5 px-4 py-2 rounded font-mono text-xs font-bold transition-all"
            style={{
              background: domain === tab.id ? `${tab.color}20` : "oklch(0.12 0.01 240)",
              border: `1px solid ${domain === tab.id ? tab.color : "oklch(0.20 0.01 240)"}`,
              color: domain === tab.id ? tab.color : "oklch(0.45 0.01 240)",
            }}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Domain content */}
      <div className="rounded-lg p-6" style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
        {domain === "trading" && <TradingMarket isSimple={isSimple} />}
        {domain === "bank" && <BankMarket isSimple={isSimple} />}
        {domain === "ecom" && <EcomMarket isSimple={isSimple} />}
      </div>

      {/* Bottom CTA */}
      <div className="mt-8 rounded-lg p-5" style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
        <div className="font-mono text-[9px] font-bold tracking-widest mb-3" style={{ color: "oklch(0.45 0.01 240)" }}>NEXT STEPS IN THE PIPELINE</div>
        <div className="flex flex-wrap gap-3">
          <Link href="/control">
            <button className="px-4 py-2 rounded font-mono text-xs font-bold" style={{ background: "oklch(0.72 0.18 145 / 0.15)", color: "oklch(0.72 0.18 145)", border: "1px solid oklch(0.72 0.18 145 / 0.4)" }}>
              🤖 Control Tower — Agents →
            </button>
          </Link>
          <Link href="/stream">
            <button className="px-4 py-2 rounded font-mono text-xs font-bold" style={{ background: "oklch(0.60 0.12 200 / 0.15)", color: "oklch(0.60 0.12 200)", border: "1px solid oklch(0.60 0.12 200 / 0.4)" }}>
              ⚖ Decision Stream →
            </button>
          </Link>
          <Link href="/proof-center">
            <button className="px-4 py-2 rounded font-mono text-xs font-bold" style={{ background: "#a78bfa22", color: "#a78bfa", border: "1px solid #a78bfa44" }}>
              ⛓ Proof Center →
            </button>
          </Link>
          <Link href="/demo-mode">
            <button className="px-4 py-2 rounded font-mono text-xs font-bold" style={{ background: "oklch(0.72 0.18 145)", color: "oklch(0.10 0.01 240)" }}>
              ▶ Start Demo →
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
}
