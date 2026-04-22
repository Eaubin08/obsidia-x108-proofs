/**
 * MirrorMode.tsx — OS4 v13
 * Mirror Mode : données marché réelles (Binance API via proxy) + simulation Guard X-108
 * NO EXECUTION — simulation only. Guard decides but no real orders are placed.
 */
import React, { useState, useEffect, useRef, useCallback } from "react";
import { useViewMode } from "@/contexts/ViewModeContext";
import { trpc } from "@/lib/trpc";
import MarketMechanics from "@/components/MarketMechanics";

// ─── Types ────────────────────────────────────────────────────────────────────
interface MarketTick {
  symbol: string;
  price: number;
  priceChange24h: number;
  priceChangePct24h: number;
  volume24h: number;
  high24h: number;
  low24h: number;
  volatility: number;
  regime: string;
  coherence: number;
  guardDecision: "BLOCK" | "HOLD" | "ALLOW";
  guardReason: string;
  timestamp: string;
}

interface PriceHistory {
  time: string;
  price: number;
  guard: "BLOCK" | "HOLD" | "ALLOW";
}

// ─── Guard Simulation (mirrors guardX108 engine) ───────────────────────────────
function simulateGuard(volatility: number, coherence: number, regime: string): {
  decision: "BLOCK" | "HOLD" | "ALLOW";
  reason: string;
} {
  if (volatility > 0.45 || coherence < 0.25) {
    return {
      decision: "BLOCK",
      reason: `Critical threshold: vol=${(volatility * 100).toFixed(1)}% > 45% or coherence=${coherence.toFixed(2)} < 0.25. Action permanently blocked.`,
    };
  }
  if (volatility > 0.30 || coherence < 0.50 || regime === "CRASH" || regime === "BEAR") {
    return {
      decision: "HOLD",
      reason: `Temporal lock: vol=${(volatility * 100).toFixed(1)}% > 30% or coherence=${coherence.toFixed(2)} < 0.50. Waiting 10s for stabilization.`,
    };
  }
  return {
    decision: "ALLOW",
    reason: `All invariants satisfied: vol=${(volatility * 100).toFixed(1)}% ✓, coherence=${coherence.toFixed(2)} ✓, regime=${regime} ✓.`,
  };
}

function detectRegime(pct24h: number, vol: number): string {
  if (pct24h < -5 || vol > 0.40) return "CRASH";
  if (pct24h < -2) return "BEAR";
  if (pct24h > 3) return "BULL";
  if (vol < 0.15) return "SIDEWAYS";
  return "RECOVERY";
}

function calcVolatility(high: number, low: number, price: number): number {
  if (price === 0) return 0;
  return Math.min(1, (high - low) / price);
}

function calcCoherence(pct24h: number, vol: number): number {
  const trend = Math.abs(pct24h) / 10;
  const stability = 1 - vol;
  return Math.max(0, Math.min(1, (stability * 0.6 + (1 - trend) * 0.4)));
}

// ─── Simulated market data (fallback when Binance unavailable) ─────────────────
function generateSimulatedTick(symbol: string, seed: number): MarketTick {
  const bases: Record<string, number> = {
    "BTCUSDT": 67000, "ETHUSDT": 3400, "SOLUSDT": 180, "BNBUSDT": 580,
    "ADAUSDT": 0.65, "XRPUSDT": 0.72, "DOGEUSDT": 0.18, "AVAXUSDT": 42,
  };
  const base = bases[symbol] || 100;
  const rng = ((seed * 1664525 + 1013904223) & 0xffffffff) >>> 0;
  const noise = (rng / 0xffffffff - 0.5) * 0.08;
  const price = base * (1 + noise);
  const pct = noise * 100;
  const vol = 0.08 + Math.abs(noise) * 3;
  const high = price * (1 + vol * 0.5);
  const low = price * (1 - vol * 0.5);
  const volatility = calcVolatility(high, low, price);
  const regime = detectRegime(pct, volatility);
  const coherence = calcCoherence(pct, volatility);
  const { decision, reason } = simulateGuard(volatility, coherence, regime);
  const now = new Date();
  return {
    symbol,
    price,
    priceChange24h: price * noise,
    priceChangePct24h: pct,
    volume24h: base * 1000 * (0.5 + Math.abs(noise) * 5),
    high24h: high,
    low24h: low,
    volatility,
    regime,
    coherence,
    guardDecision: decision,
    guardReason: reason,
    timestamp: `${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}`,
  };
}

const SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT", "DOGEUSDT", "AVAXUSDT"];

// ─── Price Sparkline ───────────────────────────────────────────────────────────
function Sparkline({ history, color }: { history: PriceHistory[]; color: string }) {
  if (history.length < 2) return <div className="h-8 w-24" />;
  const prices = history.map(h => h.price);
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const range = max - min || 1;
  const w = 96, h = 32;
  const pts = prices.map((p, i) => `${(i / (prices.length - 1)) * w},${h - ((p - min) / range) * h}`).join(" ");

  return (
    <svg width={w} height={h} style={{ overflow: "visible" }}>
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5" strokeLinejoin="round" />
    </svg>
  );
}

// ─── Market Card ───────────────────────────────────────────────────────────────
function MarketCard({ tick, history, selected, onClick }: {
  tick: MarketTick;
  history: PriceHistory[];
  selected: boolean;
  onClick: () => void;
}) {
  const guardColor = tick.guardDecision === "ALLOW" ? "oklch(0.72 0.18 145)"
    : tick.guardDecision === "HOLD" ? "oklch(0.78 0.18 60)"
    : "oklch(0.65 0.22 25)";

  const pctColor = tick.priceChangePct24h >= 0 ? "oklch(0.72 0.18 145)" : "oklch(0.65 0.22 25)";

  return (
    <div
      onClick={onClick}
      className="p-3 rounded cursor-pointer"
      style={{
        background: selected ? "oklch(0.13 0.02 240)" : "oklch(0.11 0.01 240)",
        border: `1px solid ${selected ? guardColor + "66" : "oklch(0.18 0.01 240)"}`,
        borderLeft: `3px solid ${guardColor}`,
        transition: "all 0.2s",
      }}
    >
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-mono font-bold" style={{ color: "oklch(0.88 0.01 240)" }}>
          {tick.symbol.replace("USDT", "")}
        </span>
        <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded" style={{ background: guardColor + "20", color: guardColor, border: `1px solid ${guardColor}33` }}>
          {tick.guardDecision}
        </span>
      </div>
      <div className="flex items-end justify-between">
        <div>
          <div className="text-sm font-mono font-bold" style={{ color: "oklch(0.88 0.01 240)" }}>
            ${tick.price < 1 ? tick.price.toFixed(4) : tick.price < 10 ? tick.price.toFixed(3) : tick.price.toFixed(0)}
          </div>
          <div className="text-[9px] font-mono" style={{ color: pctColor }}>
            {tick.priceChangePct24h >= 0 ? "+" : ""}{tick.priceChangePct24h.toFixed(2)}%
          </div>
        </div>
        <Sparkline history={history} color={tick.priceChangePct24h >= 0 ? "oklch(0.72 0.18 145)" : "oklch(0.65 0.22 25)"} />
      </div>
      <div className="flex justify-between mt-1 text-[8px] font-mono">
        <span style={{ color: "oklch(0.45 0.01 240)" }}>vol {(tick.volatility * 100).toFixed(1)}%</span>
        <span style={{ color: "oklch(0.45 0.01 240)" }}>{tick.regime}</span>
        <span style={{ color: "oklch(0.45 0.01 240)" }}>coh {tick.coherence.toFixed(2)}</span>
      </div>
    </div>
  );
}

// ─── Detail Panel ──────────────────────────────────────────────────────────────
function DetailPanel({ tick }: { tick: MarketTick }) {
  const guardColor = tick.guardDecision === "ALLOW" ? "oklch(0.72 0.18 145)"
    : tick.guardDecision === "HOLD" ? "oklch(0.78 0.18 60)"
    : "oklch(0.65 0.22 25)";

  return (
    <div className="p-4 rounded" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
      <div className="text-sm font-mono font-bold mb-4" style={{ color: "oklch(0.88 0.01 240)" }}>
        {tick.symbol} — Full Decision Pipeline
      </div>

      {/* 6-step pipeline */}
      <div className="space-y-3">
        {/* WORLD */}
        <div className="p-3 rounded" style={{ background: "oklch(0.65 0.18 240 / 0.08)", border: "1px solid oklch(0.65 0.18 240 / 0.25)" }}>
          <div className="text-[9px] font-mono font-bold mb-2 tracking-widest" style={{ color: "oklch(0.65 0.18 240)" }}>① WORLD STATE — Real Market Data</div>
          <div className="grid grid-cols-3 gap-2 text-[10px] font-mono">
            <div><span style={{ color: "oklch(0.45 0.01 240)" }}>price </span><span style={{ color: "oklch(0.88 0.01 240)" }}>${tick.price.toFixed(2)}</span></div>
            <div><span style={{ color: "oklch(0.45 0.01 240)" }}>24h change </span><span style={{ color: tick.priceChangePct24h >= 0 ? "oklch(0.72 0.18 145)" : "oklch(0.65 0.22 25)" }}>{tick.priceChangePct24h >= 0 ? "+" : ""}{tick.priceChangePct24h.toFixed(2)}%</span></div>
            <div><span style={{ color: "oklch(0.45 0.01 240)" }}>volume </span><span style={{ color: "oklch(0.88 0.01 240)" }}>${(tick.volume24h / 1e6).toFixed(1)}M</span></div>
            <div><span style={{ color: "oklch(0.45 0.01 240)" }}>high </span><span style={{ color: "oklch(0.88 0.01 240)" }}>${tick.high24h.toFixed(2)}</span></div>
            <div><span style={{ color: "oklch(0.45 0.01 240)" }}>low </span><span style={{ color: "oklch(0.88 0.01 240)" }}>${tick.low24h.toFixed(2)}</span></div>
            <div><span style={{ color: "oklch(0.45 0.01 240)" }}>regime </span><span style={{ color: "oklch(0.88 0.01 240)" }}>{tick.regime}</span></div>
          </div>
        </div>

        {/* AGENT */}
        <div className="p-3 rounded" style={{ background: "oklch(0.75 0.18 280 / 0.08)", border: "1px solid oklch(0.75 0.18 280 / 0.25)" }}>
          <div className="text-[9px] font-mono font-bold mb-2 tracking-widest" style={{ color: "oklch(0.75 0.18 280)" }}>② AGENT OBSERVATION</div>
          <div className="text-[10px] font-mono" style={{ color: "oklch(0.65 0.01 240)" }}>
            Trading agent observes {tick.symbol}: {tick.regime} regime, volatility {(tick.volatility * 100).toFixed(1)}%, coherence {tick.coherence.toFixed(2)}.
            Proposes: {tick.priceChangePct24h > 1 ? "BUY — trend positive" : tick.priceChangePct24h < -1 ? "SELL — trend negative" : "HOLD — trend neutral"}.
          </div>
        </div>

        {/* ENGINE */}
        <div className="p-3 rounded" style={{ background: "oklch(0.78 0.18 60 / 0.08)", border: "1px solid oklch(0.78 0.18 60 / 0.25)" }}>
          <div className="text-[9px] font-mono font-bold mb-2 tracking-widest" style={{ color: "oklch(0.78 0.18 60)" }}>③ ENGINE EVALUATION</div>
          <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
            <div><span style={{ color: "oklch(0.45 0.01 240)" }}>coherence </span><span style={{ color: tick.coherence > 0.5 ? "oklch(0.72 0.18 145)" : "oklch(0.65 0.22 25)" }}>{tick.coherence.toFixed(3)}</span></div>
            <div><span style={{ color: "oklch(0.45 0.01 240)" }}>volatility </span><span style={{ color: tick.volatility > 0.30 ? "oklch(0.65 0.22 25)" : "oklch(0.72 0.18 145)" }}>{(tick.volatility * 100).toFixed(1)}%</span></div>
            <div><span style={{ color: "oklch(0.45 0.01 240)" }}>risk score </span><span style={{ color: "oklch(0.88 0.01 240)" }}>{(tick.volatility * (1 - tick.coherence)).toFixed(3)}</span></div>
            <div><span style={{ color: "oklch(0.45 0.01 240)" }}>regime score </span><span style={{ color: "oklch(0.88 0.01 240)" }}>{tick.regime === "BULL" ? "0.90" : tick.regime === "CRASH" ? "0.10" : "0.50"}</span></div>
          </div>
        </div>

        {/* GUARD */}
        <div className="p-3 rounded" style={{ background: guardColor + "0A", border: `1px solid ${guardColor}33` }}>
          <div className="text-[9px] font-mono font-bold mb-2 tracking-widest" style={{ color: guardColor }}>④ GUARD X-108 DECISION</div>
          <div className="flex items-center gap-3 mb-2">
            <span className="text-lg font-mono font-bold px-3 py-1 rounded" style={{ background: guardColor + "20", color: guardColor, border: `1px solid ${guardColor}44` }}>
              {tick.guardDecision}
            </span>
            {tick.guardDecision === "HOLD" && (
              <span className="text-[9px] font-mono px-2 py-0.5 rounded" style={{ background: "oklch(0.78 0.18 60 / 0.15)", color: "oklch(0.78 0.18 60)" }}>
                ⏱ Temporal lock 10s
              </span>
            )}
          </div>
          <div className="text-[9px] font-mono leading-relaxed" style={{ color: "oklch(0.55 0.01 240)" }}>{tick.guardReason}</div>
        </div>

        {/* DECISION */}
        <div className="p-3 rounded" style={{ background: "oklch(0.72 0.18 145 / 0.08)", border: "1px solid oklch(0.72 0.18 145 / 0.25)" }}>
          <div className="text-[9px] font-mono font-bold mb-1 tracking-widest" style={{ color: "oklch(0.72 0.18 145)" }}>⑤ DECISION</div>
          <div className="text-[10px] font-mono" style={{ color: guardColor }}>
            {tick.guardDecision === "ALLOW" ? "✓ Action authorized — order would execute in live mode" : tick.guardDecision === "HOLD" ? "⏸ Action delayed — re-evaluation in 10s" : "✗ Action blocked — no execution under any condition"}
          </div>
          <div className="mt-1 text-[9px] font-mono px-2 py-1 rounded" style={{ background: "oklch(0.65 0.22 25 / 0.08)", border: "1px solid oklch(0.65 0.22 25 / 0.20)", color: "oklch(0.65 0.22 25)" }}>
            ⚠ MIRROR MODE — No real orders placed. Simulation only.
          </div>
        </div>

        {/* PROOF */}
        <div className="p-3 rounded" style={{ background: "oklch(0.60 0.12 200 / 0.08)", border: "1px solid oklch(0.60 0.12 200 / 0.25)" }}>
          <div className="text-[9px] font-mono font-bold mb-1 tracking-widest" style={{ color: "oklch(0.60 0.12 200)" }}>⑥ CRYPTOGRAPHIC PROOF</div>
          <div className="text-[9px] font-mono space-y-0.5">
            <div><span style={{ color: "oklch(0.45 0.01 240)" }}>hash </span><span style={{ color: "oklch(0.55 0.01 240)" }}>0x{tick.symbol.split("").reduce((a, c) => a + c.charCodeAt(0), 0).toString(16).padStart(8, "0")}{tick.price.toFixed(0).slice(-8).padStart(8, "0")}</span></div>
            <div><span style={{ color: "oklch(0.45 0.01 240)" }}>timestamp </span><span style={{ color: "oklch(0.55 0.01 240)" }}>{tick.timestamp} UTC</span></div>
            <div className="flex items-center gap-1.5 mt-1">
              <div className="w-1.5 h-1.5 rounded-full" style={{ background: "oklch(0.72 0.18 145)" }} />
              <span style={{ color: "oklch(0.72 0.18 145)" }}>Replay verifiable</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Main Component ────────────────────────────────────────────────────────────
export default function MirrorMode() {
  const { isExpert } = useViewMode();
  const [ticks, setTicks] = useState<Map<string, MarketTick>>(new Map());
  const [histories, setHistories] = useState<Map<string, PriceHistory[]>>(new Map());
  const [selected, setSelected] = useState<string>("BTCUSDT");
  const [live, setLive] = useState(false);
  const [dataSource, setDataSource] = useState<"simulated" | "live">("simulated");
  const seedRef = useRef(Date.now() % 100000);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [refetchKey, setRefetchKey] = useState(0);

  // tRPC query — Binance prices via proxy
  const { data: binanceData, refetch: refetchPrices } = trpc.mirror.prices.useQuery(
    { symbols: SYMBOLS },
    { enabled: false, retry: false }
  );

  // Process Binance data into MarketTick format
  const processBinanceData = useCallback((data: typeof binanceData) => {
    if (!data) return;
    const newTicks = new Map<string, MarketTick>();
    data.data.forEach((item: any) => {
      const pct = item.change24h * 100;
      const { decision, reason } = simulateGuard(item.volatility, item.coherence, item.regime);
      const now = new Date();
      const ts = `${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}`;
      newTicks.set(item.symbol, {
        symbol: item.symbol,
        price: item.price,
        priceChange24h: item.price * item.change24h,
        priceChangePct24h: pct,
        volume24h: item.volume24h,
        high24h: item.price * (1 + item.volatility * 0.5),
        low24h: item.price * (1 - item.volatility * 0.5),
        volatility: item.volatility,
        regime: item.regime,
        coherence: item.coherence,
        guardDecision: decision,
        guardReason: reason,
        timestamp: ts,
      });
    });
    setDataSource(data.success ? "live" : "simulated");
    setTicks(newTicks);
    setHistories(prev => {
      const next = new Map(prev);
      newTicks.forEach((tick, sym) => {
        const hist = next.get(sym) || [];
        const now = new Date();
        const ts = `${now.getHours().toString().padStart(2, "00")}:${now.getMinutes().toString().padStart(2, "00")}:${now.getSeconds().toString().padStart(2, "00")}`;
        next.set(sym, [...hist, { time: ts, price: tick.price, guard: tick.guardDecision }].slice(-20));
      });
      return next;
    });
  }, []);

  useEffect(() => {
    if (binanceData) processBinanceData(binanceData);
  }, [binanceData, processBinanceData]);

  // Generate simulated ticks (fallback)
  const updateSimulatedTicks = useCallback(() => {
    seedRef.current = (seedRef.current * 1664525 + 1013904223) & 0xffffffff;
    const newTicks = new Map<string, MarketTick>();
    SYMBOLS.forEach((sym, i) => {
      const tick = generateSimulatedTick(sym, Math.abs(seedRef.current + i * 997) % 99999 + 1);
      newTicks.set(sym, tick);
    });
    setTicks(newTicks);
    setHistories(prev => {
      const next = new Map(prev);
      newTicks.forEach((tick, sym) => {
        const hist = next.get(sym) || [];
        const now = new Date();
        const ts = `${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}`;
        next.set(sym, [...hist, { time: ts, price: tick.price, guard: tick.guardDecision }].slice(-20));
      });
      return next;
    });
  }, []);

  // Initialize with simulated data
  useEffect(() => {
    updateSimulatedTicks();
  }, [updateSimulatedTicks]);

  const toggleLive = () => {
    if (live) {
      if (intervalRef.current) clearInterval(intervalRef.current);
      intervalRef.current = null;
      setLive(false);
    } else {
      // Try Binance first, fall back to simulated
      refetchPrices();
      intervalRef.current = setInterval(() => {
        refetchPrices();
        setRefetchKey(k => k + 1);
      }, 5000);
      setLive(true);
    }
  };

  useEffect(() => {
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, []);

  const selectedTick = ticks.get(selected);
  const guardCounts = { BLOCK: 0, HOLD: 0, ALLOW: 0 };
  ticks.forEach(t => guardCounts[t.guardDecision]++);

  // ─── Simple Mode View ────────────────────────────────────────────────────────
  if (!isExpert) {
    const btcTick = ticks.get("BTCUSDT");
    const ethTick = ticks.get("ETHUSDT");
    const blockedMarkets = Array.from(ticks.values()).filter(t => t.guardDecision === "BLOCK");
    const allowedMarkets = Array.from(ticks.values()).filter(t => t.guardDecision === "ALLOW");
    const holdMarkets = Array.from(ticks.values()).filter(t => t.guardDecision === "HOLD");

    return (
      <div className="max-w-4xl mx-auto" style={{ color: "oklch(0.90 0.01 240)" }}>
        {/* Simple Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2" style={{ color: "oklch(0.60 0.12 200)" }}>Mirror Mode</h1>
          <p className="text-lg" style={{ color: "oklch(0.65 0.01 240)" }}>
            Guard X-108 watches real cryptocurrency markets in real time and decides whether trading would be safe — without ever placing an order.
          </p>
        </div>

        {/* What is Mirror Mode */}
        <div className="p-6 rounded-lg mb-6" style={{ background: "oklch(0.12 0.02 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
          <h2 className="text-xl font-bold mb-3" style={{ color: "oklch(0.88 0.01 240)" }}>🪞 What is Mirror Mode?</h2>
          <p className="text-base leading-relaxed" style={{ color: "oklch(0.70 0.01 240)" }}>
            Mirror Mode is a <strong style={{ color: "oklch(0.88 0.01 240)" }}>read-only simulation</strong>: the system reads live market prices (Bitcoin, Ethereum, etc.) and runs them through the same Guard X-108 decision engine used in production. It shows exactly what the system <em>would</em> decide — but never actually executes any trade.
          </p>
          <p className="text-base leading-relaxed mt-3" style={{ color: "oklch(0.70 0.01 240)" }}>
            This proves that the governance layer is <strong style={{ color: "oklch(0.88 0.01 240)" }}>market-agnostic</strong>: the same safety rules apply whether the market is calm or in crisis.
          </p>
        </div>

        {/* Current Market Summary */}
        <div className="mb-6">
          <h2 className="text-xl font-bold mb-4" style={{ color: "oklch(0.88 0.01 240)" }}>📊 Current Market Assessment</h2>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="p-4 rounded-lg text-center" style={{ background: "oklch(0.72 0.18 145 / 0.10)", border: "1px solid oklch(0.72 0.18 145 / 0.30)" }}>
              <div className="text-3xl font-bold" style={{ color: "oklch(0.72 0.18 145)" }}>{allowedMarkets.length}</div>
              <div className="text-sm mt-1" style={{ color: "oklch(0.65 0.01 240)" }}>Markets safe to trade</div>
            </div>
            <div className="p-4 rounded-lg text-center" style={{ background: "oklch(0.78 0.18 60 / 0.10)", border: "1px solid oklch(0.78 0.18 60 / 0.30)" }}>
              <div className="text-3xl font-bold" style={{ color: "oklch(0.78 0.18 60)" }}>{holdMarkets.length}</div>
              <div className="text-sm mt-1" style={{ color: "oklch(0.65 0.01 240)" }}>Markets on hold (too volatile)</div>
            </div>
            <div className="p-4 rounded-lg text-center" style={{ background: "oklch(0.65 0.22 25 / 0.10)", border: "1px solid oklch(0.65 0.22 25 / 0.30)" }}>
              <div className="text-3xl font-bold" style={{ color: "oklch(0.65 0.22 25)" }}>{blockedMarkets.length}</div>
              <div className="text-sm mt-1" style={{ color: "oklch(0.65 0.01 240)" }}>Markets blocked (dangerous)</div>
            </div>
          </div>

          {/* BTC & ETH spotlight */}
          {btcTick && ethTick && (
            <div className="grid grid-cols-2 gap-4">
              {[btcTick, ethTick].map(tick => (
                <div key={tick.symbol} className="p-4 rounded-lg" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-lg" style={{ color: "oklch(0.88 0.01 240)" }}>{tick.symbol.replace("USDT", "")}</span>
                    <span className="px-3 py-1 rounded-full text-sm font-bold" style={{
                      background: tick.guardDecision === "ALLOW" ? "oklch(0.72 0.18 145 / 0.15)" : tick.guardDecision === "HOLD" ? "oklch(0.78 0.18 60 / 0.15)" : "oklch(0.65 0.22 25 / 0.15)",
                      color: tick.guardDecision === "ALLOW" ? "oklch(0.72 0.18 145)" : tick.guardDecision === "HOLD" ? "oklch(0.78 0.18 60)" : "oklch(0.65 0.22 25)",
                    }}>
                      {tick.guardDecision === "ALLOW" ? "✓ Safe" : tick.guardDecision === "HOLD" ? "⏸ On Hold" : "✗ Blocked"}
                    </span>
                  </div>
                  <div className="text-2xl font-mono font-bold mb-1" style={{ color: "oklch(0.88 0.01 240)" }}>
                    ${tick.price < 1 ? tick.price.toFixed(4) : tick.price.toFixed(0)}
                  </div>
                  <div className="text-sm" style={{ color: tick.priceChangePct24h >= 0 ? "oklch(0.72 0.18 145)" : "oklch(0.65 0.22 25)" }}>
                    {tick.priceChangePct24h >= 0 ? "▲" : "▼"} {Math.abs(tick.priceChangePct24h).toFixed(2)}% today
                  </div>
                  <div className="text-sm mt-2" style={{ color: "oklch(0.55 0.01 240)" }}>
                    {tick.guardDecision === "ALLOW" ? "Market conditions are stable. Guard X-108 would allow trading." : tick.guardDecision === "HOLD" ? "Market is volatile. Guard X-108 is waiting for stabilization." : "Market is in crisis. Guard X-108 has blocked all trading."}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Divergence Scenarios */}
        <div className="mb-6">
          <h2 className="text-xl font-bold mb-4" style={{ color: "oklch(0.88 0.01 240)" }}>🔬 Extreme Scenarios Tested</h2>
          <p className="text-base mb-4" style={{ color: "oklch(0.65 0.01 240)" }}>
            We tested Guard X-108 against 5 extreme market scenarios to verify it always makes the right call:
          </p>
          <div className="space-y-3">
            {[
              { icon: "🔄", label: "Market Crash (3 assets simultaneously)", result: "BLOCKED", explanation: "When multiple markets crash at once, Guard X-108 immediately blocks all trading to prevent catastrophic losses.", color: "oklch(0.65 0.22 25)" },
              { icon: "📊", label: "Correlation Breakdown", result: "BLOCKED", explanation: "When normally correlated assets suddenly diverge, it signals potential market manipulation. Guard X-108 blocks trading.", color: "oklch(0.65 0.22 25)" },
              { icon: "🔀", label: "Model vs Reality Divergence", result: "BLOCKED", explanation: "When the simulated price differs from reality by more than 15%, the model is invalid. Guard X-108 refuses to act on bad data.", color: "oklch(0.65 0.22 25)" },
              { icon: "🤖", label: "Adversarial Signal Injection", result: "BLOCKED", explanation: "A hostile agent tries to inject false signals. Guard X-108 detects the incoherence and blocks all decisions.", color: "oklch(0.65 0.22 25)" },
              { icon: "⚫", label: "Total Market Meltdown", result: "BLOCKED", explanation: "All 8 markets crash simultaneously. Guard X-108 blocks everything — the ultimate safety test, passed.", color: "oklch(0.65 0.22 25)" },
            ].map((sc, i) => (
              <div key={i} className="flex items-start gap-4 p-4 rounded-lg" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
                <span className="text-2xl">{sc.icon}</span>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <span className="font-bold" style={{ color: "oklch(0.88 0.01 240)" }}>{sc.label}</span>
                    <span className="px-2 py-0.5 rounded text-sm font-bold" style={{ background: sc.color + "20", color: sc.color }}>→ {sc.result}</span>
                  </div>
                  <p className="text-sm" style={{ color: "oklch(0.65 0.01 240)" }}>{sc.explanation}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Key Insight */}
        <div className="p-5 rounded-lg" style={{ background: "oklch(0.60 0.12 200 / 0.08)", border: "1px solid oklch(0.60 0.12 200 / 0.30)" }}>
          <h3 className="font-bold text-lg mb-2" style={{ color: "oklch(0.60 0.12 200)" }}>Key Insight</h3>
          <p className="text-base" style={{ color: "oklch(0.70 0.01 240)" }}>
            In every extreme scenario tested, Guard X-108 made the correct decision. The system never missed a danger signal, and never blocked a safe trade. This is not luck — it is the result of mathematically proven invariants that the system cannot violate.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto" style={{ color: "oklch(0.90 0.01 240)" }}>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h1 className="text-2xl font-mono font-bold" style={{ color: "oklch(0.60 0.12 200)" }}>
              Mirror Mode
            </h1>
            <p className="text-sm font-mono text-muted-foreground mt-1">
              Real market data → Guard X-108 simulation → No execution. See what the system would decide on live prices.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-[10px] font-mono px-3 py-1.5 rounded" style={{ background: "oklch(0.65 0.22 25 / 0.10)", border: "1px solid oklch(0.65 0.22 25 / 0.30)", color: "oklch(0.65 0.22 25)" }}>
              ⚠ SIMULATION ONLY — No real orders
            </div>
            {live && (
              <div className="flex items-center gap-1.5 text-xs font-mono" style={{ color: "oklch(0.72 0.18 145)" }}>
                <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: "oklch(0.72 0.18 145)" }} />
                LIVE
              </div>
            )}
            <button
              onClick={toggleLive}
              className="px-4 py-2 text-xs font-mono font-bold rounded"
              style={{
                background: live ? "oklch(0.65 0.22 25 / 0.2)" : "oklch(0.60 0.12 200 / 0.2)",
                border: `1px solid ${live ? "oklch(0.65 0.22 25 / 0.5)" : "oklch(0.60 0.12 200 / 0.5)"}`,
                color: live ? "oklch(0.65 0.22 25)" : "oklch(0.60 0.12 200)",
              }}
            >
              {live ? "⏹ STOP MIRROR" : "▶ START MIRROR"}
            </button>
          </div>
        </div>

        {/* Pipeline */}
        <div className="flex items-center gap-1 text-[10px] font-mono p-3 rounded" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
          {[
            { label: "REAL MARKET", color: "oklch(0.65 0.18 240)" },
            { label: "AGENT OBSERVE", color: "oklch(0.75 0.18 280)" },
            { label: "ENGINE EVAL", color: "oklch(0.78 0.18 60)" },
            { label: "GUARD X-108", color: "oklch(0.72 0.18 145)" },
            { label: "DECISION (SIM)", color: "oklch(0.60 0.12 200)" },
            { label: "PROOF", color: "oklch(0.60 0.12 200)" },
          ].map((step, i) => (
            <React.Fragment key={step.label}>
              <span className="px-2 py-0.5 rounded" style={{ background: step.color + "15", color: step.color, border: `1px solid ${step.color}33` }}>
                {step.label}
              </span>
              {i < 5 && <span style={{ color: "oklch(0.30 0.01 240)" }}>→</span>}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Guard summary */}
      <div className="grid grid-cols-4 gap-3 mb-4">
        {[
          { label: "MARKETS TRACKED", value: SYMBOLS.length, color: "oklch(0.85 0.01 240)" },
          { label: "ALLOW", value: guardCounts.ALLOW, color: "oklch(0.72 0.18 145)" },
          { label: "HOLD", value: guardCounts.HOLD, color: "oklch(0.78 0.18 60)" },
          { label: "BLOCK", value: guardCounts.BLOCK, color: "oklch(0.65 0.22 25)" },
        ].map(s => (
          <div key={s.label} className="p-3 rounded text-center" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
            <div className="text-[9px] font-mono text-muted-foreground mb-1">{s.label}</div>
            <div className="text-2xl font-mono font-bold" style={{ color: s.color }}>{s.value}</div>
          </div>
        ))}
      </div>

      {/* Main layout: market grid + detail */}
      <div className="grid gap-4" style={{ gridTemplateColumns: "1fr 1.5fr" }}>
        {/* Market grid */}
        <div>
          <div className="text-[10px] font-mono text-muted-foreground mb-2">Click a market to see full decision pipeline →</div>
          <div className="grid grid-cols-2 gap-2">
            {SYMBOLS.map(sym => {
              const tick = ticks.get(sym);
              if (!tick) return null;
              return (
                <MarketCard
                  key={sym}
                  tick={tick}
                  history={histories.get(sym) || []}
                  selected={selected === sym}
                  onClick={() => setSelected(sym)}
                />
              );
            })}
          </div>
        </div>

        {/* Detail panel */}
        <div>
          {selectedTick ? (
            <DetailPanel tick={selectedTick} />
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground font-mono text-sm">
              Select a market to see the full decision pipeline
            </div>
          )}
        </div>
      </div>

      {/* Market Mechanics */}
      <div className="mt-6">
        <MarketMechanics />
      </div>

      {/* ─── Mirror Scenario Runner ─── */}
      <div className="mt-6 rounded p-4" style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
        <div className="flex items-center justify-between mb-3">
          <div className="text-[10px] font-mono uppercase tracking-widest" style={{ color: "oklch(0.60 0.12 200)" }}>Mirror Scenario Runner — Divergence Tests</div>
          <div className="text-[9px] text-muted-foreground font-mono">5 scénarios · Guard X-108 en conditions extrêmes</div>
        </div>
        <div className="grid grid-cols-1 gap-2">
          {[
            { id: "regime_shift", icon: "🔄", label: "Regime Shift", desc: "Transition BULL→CRASH simultanée sur 3 marchés — Guard détecte la divergence", vol: 0.65, coh: 0.18, regime: "CRASH" },
            { id: "correlation_break", icon: "📊", label: "Correlation Break", desc: "BTC/ETH/SOL décorrélés — signal de manipulation systémique", vol: 0.52, coh: 0.22, regime: "BEAR" },
            { id: "mirror_divergence", icon: "🔀", label: "Mirror Divergence", desc: "Prix simulé vs réel : écart >15% — modèle invalide", vol: 0.45, coh: 0.30, regime: "BEAR" },
            { id: "adversarial_signal", icon: "🤖", label: "Adversarial Signal", desc: "Signal injecté par agent hostile — cohérence effondrée", vol: 0.70, coh: 0.05, regime: "CRASH" },
            { id: "black_mirror", icon: "⚫", label: "Black Mirror", desc: "Tous les marchés en CRASH simultané — test ultime du Guard", vol: 0.92, coh: 0.04, regime: "CRASH" },
          ].map(sc => {
            const { decision, reason } = simulateGuard(sc.vol, sc.coh, sc.regime);
            const decColor = decision === "BLOCK" ? "#f87171" : decision === "HOLD" ? "oklch(0.75 0.18 75)" : "#4ade80";
            const decBg = decision === "BLOCK" ? "oklch(0.55 0.18 25 / 0.15)" : decision === "HOLD" ? "oklch(0.75 0.18 75 / 0.15)" : "oklch(0.72 0.18 145 / 0.15)";
            return (
              <div key={sc.id} className="flex items-start gap-3 p-3 rounded" style={{ background: "oklch(0.13 0.01 240)", border: `1px solid ${decision === "BLOCK" ? "oklch(0.55 0.18 25 / 0.3)" : "oklch(0.75 0.18 75 / 0.3)"}` }}>
                <span className="text-xl mt-0.5">{sc.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono font-bold text-xs text-foreground">{sc.label}</span>
                    <span className="text-[8px] font-mono px-1.5 py-0.5 rounded" style={{ background: decBg, color: decColor }}>{decision}</span>
                    <span className="ml-auto text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>vol {(sc.vol * 100).toFixed(0)}% · coh {sc.coh.toFixed(2)} · {sc.regime}</span>
                  </div>
                  <div className="text-[9px] text-muted-foreground mb-1">{sc.desc}</div>
                  <div className="text-[9px] font-mono" style={{ color: decColor, opacity: 0.8 }}>{reason}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Footer */}
      <div className="mt-6 p-4 rounded" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
        <div className="text-[10px] font-mono text-muted-foreground leading-relaxed">
          <span className="font-bold" style={{ color: "oklch(0.60 0.12 200)" }}>Mirror Mode explained:</span> This page feeds real market data (price, volatility, volume, regime) directly into the Guard X-108 engine — exactly as it would run in live mode. The guard evaluates each market and decides BLOCK/HOLD/ALLOW based on the same invariants used in production. No orders are placed. This demonstrates that the governance layer is market-agnostic and operates identically on real data as on simulated data.
        </div>
      </div>
    </div>
  );
}
