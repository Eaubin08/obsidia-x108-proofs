import React, { useState, useEffect, useRef, useContext, useCallback } from "react";
import { trpc } from "@/lib/trpc";
import { DecisionBadge } from "@/components/MetricCard";
import { useViewMode } from "@/contexts/ViewModeContext";
import { OpenBrainView, BrainData } from "@/components/OpenBrainView";
import { StrasbourgClock } from "@/components/StrasbourgClock";
import { PortfolioContext } from "@/App";
import { EngineBlock } from "@/components/EngineBlock";
import MarketExplanation from "@/components/MarketExplanation";
import CausalPipeline from "@/components/CausalPipeline";
import MarketMechanics from "@/components/MarketMechanics";
import { ConceptTooltip, DecisionLegend } from "@/components/ConceptTooltip";
import CanonicalRealPanel from "@/components/CanonicalRealPanel";
import CanonicalProofPanel from "@/components/CanonicalProofPanel";
import SurfaceStatusBadge from "@/components/SurfaceStatusBadge";
import DecisionSummaryBar from "@/components/DecisionSummaryBar";
import PilotagePanel from "@/components/PilotagePanel";
import { ModeBadgeBar } from "@/components/ModeBadge";
import WorldMetierHeader from "@/components/WorldMetierHeader";
import ProjectionPanel from "@/components/ProjectionPanel";
import WorldPageTemplate from "@/components/WorldPageTemplate";

// ─── Live Market Engine (client-side GBM tick) ────────────────────────────────
function nextPrice(prev: number, mu = 0.0002, sigma = 0.012, crash = false): number {
  const z = Math.sqrt(-2 * Math.log(Math.random() + 1e-10)) * Math.cos(2 * Math.PI * Math.random());
  const drift = crash ? -0.008 : mu;
  const vol = crash ? 0.035 : sigma;
  return Math.max(0.01, prev * Math.exp((drift - 0.5 * vol * vol) + vol * z));
}

interface PriceTick { price: number; time: number; change: number; volume: number; }
interface OrderEntry { price: number; size: number; side: "bid" | "ask"; }
interface TradeAction {
  type: "BUY" | "SELL"; amount: number; price: number; timestamp: number;
  decision: "ALLOW" | "HOLD" | "BLOCK"; holdRemaining?: number; capitalImpact?: number;
}

// Mulberry32 PRNG — same algorithm as the backend engine, seeded on price
function mulberry32(seed: number) {
  let s = seed >>> 0;
  return () => {
    s += 0x6d2b79f5;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 0xffffffff;
  };
}

function generateOrderBook(mid: number, volumeHint = 0): OrderEntry[] {
  // Seed = integer part of price * 100 + volume hint — deterministic per price level
  const seed = Math.round(mid * 100) + Math.round(volumeHint) * 31337;
  const rand = mulberry32(seed);
  const entries: OrderEntry[] = [];
  // Spread widens with volatility (approximated by fractional part of price)
  const spreadFactor = 0.03 + (mid % 1) * 0.04;
  for (let i = 1; i <= 8; i++) {
    const askSize = Math.floor(rand() * 800 + 100);
    const bidSize = Math.floor(rand() * 800 + 100);
    entries.push({ price: mid + i * spreadFactor, size: askSize, side: "ask" });
    entries.push({ price: mid - i * spreadFactor, size: bidSize, side: "bid" });
  }
  return entries.sort((a, b) => b.price - a.price);
}

function buildBrainData(trade: TradeAction): BrainData {
  const coherence = trade.decision === "ALLOW" ? 0.92 : trade.decision === "HOLD" ? 0.65 : 0.28;
  return {
    sees: [
      { label: "Action", value: trade.type },
      { label: "Montant", value: trade.amount, unit: " €" },
      { label: "Prix", value: trade.price.toFixed(2), unit: " €" },
      { label: "Cohérence", value: (coherence * 100).toFixed(0), unit: "%" },
    ],
    thinks: [
      { label: "Cohérence structurelle", value: coherence, color: coherence >= 0.7 ? "green" : coherence >= 0.5 ? "amber" : "red", description: coherence < 0.5 ? "Incohérence détectée — Flash Crash probable" : "Cohérence acceptable" },
      { label: "Verrou temporel", value: trade.decision === "HOLD" ? 0.5 : 1, color: trade.decision === "HOLD" ? "amber" : "green", description: trade.decision === "HOLD" ? "Pause obligatoire — marché trop instable" : "Verrou levé" },
      { label: "Risque irréversibilité", value: 0.6, color: "amber", description: "Ordre de marché irréversible" },
    ],
    decision: trade.decision,
    decisionLabel: trade.decision === "BLOCK" ? "Ordre bloqué — risque trop élevé" : trade.decision === "HOLD" ? "Pause obligatoire — marché instable" : "Ordre autorisé",
    capitalImpact: trade.decision === "BLOCK" ? `Capital protégé : +${trade.amount.toLocaleString("fr-FR")} €` : undefined,
  };
}

const NEWS_ITEMS = [
  { text: "FED : Hausse des taux de 75bps — surprise", severity: "critical" },
  { text: "BCE maintient ses taux — décision attendue", severity: "neutral" },
  { text: "Flash Crash détecté sur NASDAQ — -8% en 3 minutes", severity: "critical" },
  { text: "Inflation US : 4.2% — au-dessus des attentes", severity: "high" },
  { text: "Apple Q4 : +12% de revenus — dépassement consensus", severity: "positive" },
  { text: "Obsidia Guard X-108 : 0 violations détectées ce jour", severity: "positive" },
  { text: "Liquidité réduite — écarts d’achat/vente très larges", severity: "high" },
  { text: "Changement de tendance détecté : marché haussier → baissier", severity: "critical" },
];

// ─── Story Mode ─────────────────────────────────────────────────────────────
const STORY_STEPS = [
  {
    id: 1,
    phase: "WORLD",
    icon: "🌍",
    title: "Le marché s'emballe",
    description: "Un algorithme de trading haute fréquence déclenche une vente massive. Le prix chute de 12% en 3 secondes. C'est le début d'un Flash Crash.",
    highlight: "Prix : 100 € → 88 € en 3s",
    color: "#f87171",
    action: "Simuler le crash",
  },
  {
    id: 2,
    phase: "AGENT",
    icon: "🤖",
    title: "L'agent reçoit l'ordre",
    description: "Un agent autonome reçoit un ordre d'achat de 50 000 € sur BTC. Il transmet la demande au moteur Obsidia pour évaluation.",
    highlight: "ACHAT 50 000 € · BTC · irréversible",
    color: "oklch(0.65 0.18 220)",
    action: "Transmettre l'ordre",
  },
  {
    id: 3,
    phase: "GUARD X-108",
    icon: "🛡️",
    title: "Le Guard analyse",
    description: "Le Guard X-108 détecte une volatilité de 45% (seuil : 25%), une cohérence structurelle de 0.18 (seuil : 0.4), et un risque de ruine de 73%. Décision : BLOCK.",
    highlight: "Vol 45% · Cohérence 0.18 · Ruine 73%",
    color: "#f87171",
    action: "Analyser",
  },
  {
    id: 4,
    phase: "DÉCISION",
    icon: "⛔",
    title: "BLOCK — Capital protégé",
    description: "L'ordre est bloqué. Les 50 000 € ne sont pas investis dans un marché en chute libre. Le Guard a évité une perte estimée à 18 500 €.",
    highlight: "50 000 € protégés · Perte évitée : ~18 500 €",
    color: "#4ade80",
    action: "Voir la preuve",
  },
  {
    id: 5,
    phase: "PROOF",
    icon: "🔐",
    title: "Preuve cryptographique",
    description: "Chaque décision est horodatée, hashée (SHA-256), et ancrée dans une chaîne Merkle. La décision BLOCK est irréfutable et auditable à tout moment.",
    highlight: "Hash : 0x4f3a...c8b2 · Merkle root vérifié",
    color: "oklch(0.65 0.18 220)",
    action: "Terminer",
  },
];

export default function TradingWorld() {
  const portfolio = useContext(PortfolioContext);
  const { isSimple } = useViewMode();
  const { onTradingUpdate, onGuardBlock } = portfolio;
  const updateWalletMut = trpc.portfolio.updateWallet.useMutation();
  const upsertPositionMut = trpc.portfolio.upsertPosition.useMutation();

  const [prices, setPrices] = useState<PriceTick[]>(() => {
    const init: PriceTick[] = [];
    let p = 100;
    for (let i = 0; i < 60; i++) {
      p = nextPrice(p);
      init.push({ price: p, time: Date.now() - (60 - i) * 1000, change: 0, volume: Math.floor(Math.random() * 500 + 100) });
    }
    return init;
  });
  const [orderBook, setOrderBook] = useState<OrderEntry[]>(() => generateOrderBook(100));
  const [newsIndex, setNewsIndex] = useState(0);
  const [isFlashCrash, setIsFlashCrash] = useState(false);
  const [orderAmount, setOrderAmount] = useState(10000);
  const [lastTrade, setLastTrade] = useState<TradeAction | null>(null);
  const [holdActive, setHoldActive] = useState(false);
  const [holdElapsed, setHoldElapsed] = useState(0);
  const [aiExplanation, setAiExplanation] = useState<string | null>(null);
  const [positions, setPositions] = useState<TradeAction[]>([]);
  const [capitalSaved, setCapitalSaved] = useState(0);
  const [metrics, setMetrics] = useState<any>(null);
  const [storyMode, setStoryMode] = useState(false);
  const [storyStep, setStoryStep] = useState(0);
  const [storySimResult, setStorySimResult] = useState<any>(null);
  const [storyLLM, setStoryLLM] = useState<string | null>(null);
  const [canonicalEnvelope, setCanonicalEnvelope] = useState<any>(null);
  const [canonicalVerify, setCanonicalVerify] = useState<any>(null);
  const canonicalAttestation = trpc.engine.attestation.useQuery({ day: undefined });
  const decisionEnvelopeMut = trpc.engine.decisionEnvelope.useMutation({
    onSuccess: (data) => {
      setCanonicalEnvelope(data);
      if (data?.ticket_id) {
        verifyTicketMut.mutate({ ticketId: data.ticket_id });
      }
    },
  });
  const verifyTicketMut = trpc.engine.verifyTicket.useMutation({
    onSuccess: (data) => setCanonicalVerify(data),
  });

  const holdIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const saveSnapshotMut = trpc.portfolio.saveSnapshot.useMutation();

  const simulate = trpc.trading.simulate.useMutation({
    onSuccess: (data) => {
      if (data?.metrics) {
        setMetrics(data.metrics);
        // Persist scenario result to portfolio (fire-and-forget, only for authenticated users)
        const m = data.metrics;
        // ticket.decision tells us if guard blocked the scenario
        const wasBlocked = data.ticket?.decision === "BLOCK";
        const guardBlocksCount = wasBlocked ? 1 : 0;
        const capitalSavedEst = wasBlocked ? orderAmount : 0;
        const pnl = (m.totalReturn ?? 0) * orderAmount;
        // Update wallet with scenario P&L and guard stats
        updateWalletMut.mutate({
          pnl24h: pnl,
          guardBlocks: guardBlocksCount,
          capitalSaved: capitalSavedEst,
        });
        // Save a portfolio snapshot after each scenario run
        saveSnapshotMut.mutate({
          capital: orderAmount * (1 + (m.totalReturn ?? 0)),
          pnl,
          guardBlocks: guardBlocksCount,
          capitalSaved: capitalSavedEst,
          domain: "trading",
          scenarioName: wasBlocked ? "Flash Crash — BLOCK" : "Trading Simulation",
        });
        // Upsert position for the scenario
        upsertPositionMut.mutate({
          domain: "trading",
          asset: `SCENARIO:${m.stateHash?.slice(0, 8) ?? "run"}`,
          quantity: 1,
          avgEntryPrice: orderAmount,
          currentValue: orderAmount * (1 + (m.totalReturn ?? 0)),
          unrealizedPnl: pnl,
        });
      }
    },
  });
  const explainDecision = trpc.ai.explainDecision.useMutation({
    onSuccess: (data) => setAiExplanation(data.explanation),
  });
  const storyExplain = trpc.ai.explainDecision.useMutation({
    onSuccess: (data) => setStoryLLM(data.explanation),
  });
  const storySimulate = trpc.trading.simulate.useMutation({
    onSuccess: (data) => {
      setStorySimResult(data);
      // Auto-trigger LLM explanation at step 3 (Guard analysis)
      storyExplain.mutate({
        vertical: "TRADING",
        decision: data.ticket?.decision ?? "BLOCK",
        metrics: { coherence: 0.18, holdRemaining: 0, tau: 10 },
        context: "Flash Crash — ACHAT 50 000 € · BTC · irréversible",
        capitalImpact: 50000,
      });
    },
  });

  const startStory = useCallback(() => {
    setStoryMode(true);
    setStoryStep(0);
    setStorySimResult(null);
    setStoryLLM(null);
    // Trigger Flash Crash simulation immediately
    storySimulate.mutate({ seed: 42, steps: 252, S0: 100, mu: -0.08, sigma: 0.45, jumpLambda: 0.8, jumpMu: -0.40, jumpSigma: 0.15, garchAlpha: 0.3, garchBeta: 0.65, regimes: 2, frictionBps: 50 });
    setIsFlashCrash(true);
  }, [storySimulate]);

  const advanceStory = useCallback(() => {
    if (storyStep >= STORY_STEPS.length - 1) {
      setStoryMode(false);
      setStoryStep(0);
      setIsFlashCrash(false);
    } else {
      setStoryStep((s) => s + 1);
    }
  }, [storyStep]);

  // ── Live market tick (1 tick/s) ──
  useEffect(() => {
    const interval = setInterval(() => {
      setPrices((prev) => {
        const last = prev[prev.length - 1];
        const newPrice = nextPrice(last.price, 0.0002, 0.012, isFlashCrash);
        const change = (newPrice - last.price) / last.price;
        return [...prev.slice(-120), { price: newPrice, time: Date.now(), change, volume: Math.floor(Math.random() * 800 + 100) }];
      });
      setOrderBook(() => {
        const lastTick = prices[prices.length - 1];
        return generateOrderBook(lastTick?.price ?? 100, lastTick?.volume ?? 0);
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [isFlashCrash, prices]);

  // ── News rotation ──
  useEffect(() => {
    const interval = setInterval(() => setNewsIndex((i) => (i + 1) % NEWS_ITEMS.length), 8000);
    return () => clearInterval(interval);
  }, []);

  // ── Initial backend metrics ──
  useEffect(() => {
    simulate.mutate({ seed: 42, steps: 252, S0: 100, mu: 0.05, sigma: 0.2, jumpLambda: 0.1, jumpMu: -0.05, jumpSigma: 0.08, garchAlpha: 0.1, garchBeta: 0.85, regimes: 2, frictionBps: 5 });
  }, []);

  // ── Draw chart on canvas ──
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || prices.length < 2) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const w = canvas.width, h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    const vals = prices.map((p) => p.price);
    const minP = Math.min(...vals) * 0.999, maxP = Math.max(...vals) * 1.001;
    const range = maxP - minP || 1;
    ctx.strokeStyle = "rgba(255,255,255,0.04)";
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) { const y = (i / 4) * h; ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }
    const lastChange = prices[prices.length - 1]?.change ?? 0;
    const lineColor = lastChange >= 0 ? "#4ade80" : "#f87171";
    const gradient = ctx.createLinearGradient(0, 0, 0, h);
    gradient.addColorStop(0, lastChange >= 0 ? "rgba(74,222,128,0.25)" : "rgba(248,113,113,0.25)");
    gradient.addColorStop(1, "rgba(0,0,0,0)");
    ctx.beginPath();
    prices.forEach((p, i) => {
      const x = (i / (prices.length - 1)) * w;
      const y = h - ((p.price - minP) / range) * h;
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.strokeStyle = lineColor;
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.lineTo(w, h); ctx.lineTo(0, h); ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();
  }, [prices]);

  // ── Execute order ──
  const executeOrder = useCallback((type: "BUY" | "SELL") => {
    if (holdActive) return;
    const currentPrice = prices[prices.length - 1]?.price ?? 100;
    const change = prices[prices.length - 1]?.change ?? 0;
    const volatility = Math.abs(change);
    let decision: "ALLOW" | "HOLD" | "BLOCK" = "ALLOW";
    if (isFlashCrash || volatility > 0.025) decision = "BLOCK";
    else if (volatility > 0.015) decision = "HOLD";
    // Appel backend canonique en parallèle
    decisionEnvelopeMut.mutate({
      domain: "trading",
      amount: orderAmount,
      irreversible: true,
      asset: "BTC",
      side: type,
      coherence: isFlashCrash ? 0.15 : volatility > 0.015 ? 0.55 : 0.92,
      volatility,
      timeElapsed: 12,
      tau: 10,
    });

    const trade: TradeAction = { type, amount: orderAmount, price: currentPrice, timestamp: Date.now(), decision, holdRemaining: decision === "HOLD" ? 10 : 0, capitalImpact: decision === "BLOCK" ? orderAmount : 0 };
    setLastTrade(trade);
    setAiExplanation(null);

    if (decision === "BLOCK") {
      setCapitalSaved((prev) => prev + orderAmount);
      onGuardBlock();
      // Persist guard block to portfolio (fire-and-forget, only for authenticated users)
      updateWalletMut.mutate({ guardBlocks: 1, capitalSaved: orderAmount });
    } else if (decision === "ALLOW") {
      setPositions((prev) => [...prev.slice(-9), trade]);
      onTradingUpdate({ pnl: orderAmount * 0.01 });
      // Persist position and P&L to portfolio
      upsertPositionMut.mutate({ domain: "trading", asset: `BTC/${type}`, quantity: orderAmount / currentPrice, avgEntryPrice: currentPrice, currentValue: orderAmount, unrealizedPnl: orderAmount * 0.01 });
      updateWalletMut.mutate({ pnl24h: orderAmount * 0.01 });
    } else if (decision === "HOLD") {
      setHoldActive(true);
      setHoldElapsed(0);
      let e = 0;
      holdIntervalRef.current = setInterval(() => {
        e += 0.5;
        setHoldElapsed(e);
        if (e >= 10) {
          clearInterval(holdIntervalRef.current!);
          setHoldActive(false);
          setPositions((prev) => [...prev.slice(-9), { ...trade, decision: "ALLOW" }]);
          onTradingUpdate({ pnl: orderAmount * 0.01 });
          upsertPositionMut.mutate({ domain: "trading", asset: `BTC/${type}`, quantity: orderAmount / currentPrice, avgEntryPrice: currentPrice, currentValue: orderAmount, unrealizedPnl: orderAmount * 0.01 });
        }
      }, 50);
    }
  }, [prices, orderAmount, isFlashCrash, holdActive, onGuardBlock, onTradingUpdate, updateWalletMut, upsertPositionMut, positions.length]);

  const currentPrice = prices[prices.length - 1]?.price ?? 100;
  const prevPrice = prices[prices.length - 2]?.price ?? currentPrice;
  const priceChange = currentPrice - prevPrice;
  const priceChangePct = (priceChange / prevPrice) * 100;
  const isUp = priceChange >= 0;
  const news = NEWS_ITEMS[newsIndex];

  return (
    <div className="flex flex-col gap-3">
      {/* ─── STORY MODE OVERLAY ────────────────────────────────────────────────── */}
      {storyMode && (() => {
        const step = STORY_STEPS[storyStep];
        const isLoading = storySimulate.isPending && storyStep === 0;
        return (
          <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: "rgba(0,0,0,0.85)" }}>
            <div className="relative w-full max-w-lg mx-4 rounded-xl p-6" style={{ background: "oklch(0.11 0.01 240)", border: `2px solid ${step.color}40` }}>
              {/* Close */}
              <button onClick={() => { setStoryMode(false); setIsFlashCrash(false); }} className="absolute top-3 right-3 text-muted-foreground hover:text-foreground text-lg">✕</button>
              {/* Progress */}
              <div className="flex items-center gap-1 mb-5">
                {STORY_STEPS.map((s, i) => (
                  <div key={s.id} className="flex-1 h-1 rounded-full transition-all" style={{ background: i <= storyStep ? step.color : "oklch(0.22 0.01 240)" }} />
                ))}
              </div>
              {/* Phase badge */}
              <div className="flex items-center gap-2 mb-4">
                <span className="text-3xl">{step.icon}</span>
                <div>
                  <div className="text-[9px] font-mono font-bold uppercase tracking-widest" style={{ color: step.color }}>{step.phase}</div>
                  <div className="font-bold text-lg text-foreground">{step.title}</div>
                </div>
                <div className="ml-auto text-[10px] font-mono text-muted-foreground">{storyStep + 1} / {STORY_STEPS.length}</div>
              </div>
              {/* Description */}
              <p className="text-sm text-muted-foreground leading-relaxed mb-4">{step.description}</p>
              {/* Highlight */}
              <div className="px-3 py-2 rounded font-mono text-xs mb-4" style={{ background: `${step.color}15`, border: `1px solid ${step.color}40`, color: step.color }}>
                {step.highlight}
              </div>
              {/* Real data from simulation (step 3+) */}
              {storySimResult && storyStep >= 2 && (
                <div className="grid grid-cols-3 gap-2 mb-4">
                  {[
                    { label: "Volatility", value: `${((storySimResult.metrics?.avgVolatility ?? 0.45) * 100).toFixed(0)}%`, color: "#f87171" },
                    { label: "Max Drawdown", value: `${((storySimResult.metrics?.maxDrawdown ?? 0.37) * 100).toFixed(0)}%`, color: "#f87171" },
                    { label: "Décision", value: storySimResult.ticket?.decision ?? "BLOCK", color: storySimResult.ticket?.decision === "BLOCK" ? "#f87171" : storySimResult.ticket?.decision === "HOLD" ? "oklch(0.75 0.18 75)" : "#4ade80" },
                  ].map(m => (
                    <div key={m.label} className="rounded p-2 text-center" style={{ background: "oklch(0.14 0.01 240)" }}>
                      <div className="font-mono font-bold text-sm" style={{ color: m.color }}>{m.value}</div>
                      <div className="text-[9px] text-muted-foreground">{m.label}</div>
                    </div>
                  ))}
                </div>
              )}
              {/* LLM explanation (step 3+) */}
              {storyLLM && storyStep >= 2 && (
                <div className="p-3 rounded text-xs text-muted-foreground leading-relaxed mb-4" style={{ background: "oklch(0.13 0.01 240)", border: "1px solid oklch(0.22 0.01 240)" }}>
                  <div className="text-[9px] font-mono text-green-400/70 mb-1">🌐 Explication IA</div>
                  {storyLLM}
                </div>
              )}
              {/* Proof hash (step 5) */}
              {storyStep === 4 && storySimResult?.ticket && (
                <div className="p-2 rounded font-mono text-[10px] mb-4" style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.65 0.18 220 / 0.3)", color: "oklch(0.65 0.18 220)" }}>
                  Hash : {storySimResult.ticket.hash?.slice(0, 20) ?? "0x4f3a8c...c8b2"}...
                  <br />Merkle root : {storySimResult.ticket.merkleRoot?.slice(0, 16) ?? "0x9d2f..."} ✓
                </div>
              )}
              {/* CTA */}
              <button
                onClick={advanceStory}
                disabled={isLoading}
                className="w-full py-3 rounded font-mono font-bold text-sm transition-all"
                style={{ background: step.color, color: "oklch(0.10 0.01 240)" }}
              >
                {isLoading ? "⏳ Simulation en cours..." : storyStep >= STORY_STEPS.length - 1 ? "✓ Terminer le scénario" : `${step.action} →`}
              </button>
            </div>
          </div>
        );
      })()}
      {/* ─── Barre de régime opératoire ─────────────────────────────────────── */}
      <ModeBadgeBar
        mode={(canonicalAttestation.data as any)?.source === "local_fallback" ? "FALLBACK" : (canonicalAttestation.data as any)?.merkle_root ? "LIVE" : "DEMO"}
        detail={(canonicalAttestation.data as any)?.merkle_root ? `Merkle : ${((canonicalAttestation.data as any)?.merkle_root as string)?.slice(0, 12) ?? "—"}` : "Données simulées — aucun ordre réel"}
        right={lastTrade ? `dernier : ${lastTrade.decision} · ${orderAmount.toLocaleString("fr-FR")} €` : undefined}
      />
      {/* ── Header métier Trading ── */}
      <WorldMetierHeader
        domain="trading"
        mode="LIVE"
        x108Status={(canonicalAttestation.data as any)?.merkle_root ? "ONLINE" : "DEGRADED"}
        lastDecision={lastTrade?.decision === "ALLOW" || lastTrade?.decision === "HOLD" || lastTrade?.decision === "BLOCK" ? lastTrade.decision : null}
        decisionCount={capitalSaved > 0 ? Math.ceil(capitalSaved / (orderAmount || 1)) : undefined}
        verdicts={[
          { label: "Capital protégé", value: capitalSaved > 0 ? `+${capitalSaved.toLocaleString("fr-FR")} €` : "€ 0 protégé", color: "oklch(0.72 0.18 145)", icon: "🛡️" },
          { label: "Ordre", value: lastTrade ? lastTrade.decision : "En attente", color: lastTrade?.decision === "BLOCK" ? "oklch(0.65 0.25 25)" : lastTrade?.decision === "HOLD" ? "oklch(0.72 0.18 45)" : "oklch(0.72 0.18 145)", icon: lastTrade?.decision === "BLOCK" ? "❌" : lastTrade?.decision === "HOLD" ? "⏸️" : "✅" },
          { label: "Montant", value: `${orderAmount.toLocaleString("fr-FR")} €`, color: "oklch(0.60 0.12 200)", icon: "💰" },
        ]}
        sliders={[
          { key: "orderAmount", label: "Montant ordre (€)", min: 1000, max: 100000, step: 1000, value: orderAmount, unit: " €", color: "oklch(0.72 0.18 145)" },
        ]}
        onSliderChange={(key, val) => { if (key === "orderAmount") setOrderAmount(val); }}
      />
      {/* ── Badge statut surface ── */}
      <div className="flex items-center justify-between mb-1">
        <span className="font-mono text-xs font-bold" style={{ color: "oklch(0.65 0.18 220)" }}>TRADING WORLD</span>
        <div className="flex items-center gap-2">
          <a href="/future?domain=trading"
            className="flex items-center gap-1 px-2 py-0.5 rounded text-[9px] font-mono font-bold"
            style={{ background: "oklch(0.72 0.18 145 / 0.12)", border: "1px solid oklch(0.72 0.18 145 / 0.35)", color: "oklch(0.72 0.18 145)" }}>
            ▶ Simuler dans Future
          </a>
        <SurfaceStatusBadge
          status={
            canonicalAttestation.isLoading ? "LOADING"
            : canonicalAttestation.error ? "ERROR"
            : (canonicalAttestation.data as any)?.source === "local_fallback" ? "PARTIAL"
            : (canonicalAttestation.data as any)?.merkle_root ? "REAL"
            : "PARTIAL"
          }
          source={
            (canonicalAttestation.data as any)?.source === "local_fallback" ? "os4_local_fallback"
            : (canonicalAttestation.data as any)?.merkle_root ? "python"
            : undefined
          }
        />
        </div>
      </div>
      {/* ── BLOC 1 : Résultat visible en 3s ── */}
      <div className="mt-2">
        <DecisionSummaryBar
          gate={lastTrade?.decision ?? null}
          verdict={lastTrade?.decision === "BLOCK" ? "TRADE_BLOCKED" : lastTrade?.decision === "HOLD" ? "HOLD_X108" : lastTrade?.decision === "ALLOW" ? "TRADE_EXECUTED" : undefined}
          source={canonicalEnvelope?.source ?? (lastTrade ? "os4_local_fallback" : undefined)}
          severity={canonicalEnvelope?.severity}
          reason={lastTrade?.decision === "BLOCK" ? `Volatilité excessive — ${orderAmount.toLocaleString("fr-FR")} € protégés` : lastTrade?.decision === "HOLD" ? "Verrou τ=10s activé — marché instable" : lastTrade?.decision === "ALLOW" ? "Conditions nominales — ordre exécuté" : undefined}
          loading={decisionEnvelopeMut.isPending}
          domain="trading"
        />
      </div>
      {/* Bouton Mode Story */}
      <div className="flex justify-end">
        <button
          onClick={startStory}
          className="flex items-center gap-2 px-4 py-2 rounded font-mono font-bold text-sm transition-all"
          style={{ background: "oklch(0.65 0.18 220 / 0.15)", border: "1px solid oklch(0.65 0.18 220 / 0.5)", color: "oklch(0.65 0.18 220)" }}
        >
          📚 Mode Story — Flash Crash guidé
        </button>
      </div>
      {/* ── WORLD EXPLAINED ─────────────────────────────────────────────── */}
      <MarketExplanation domain="trading" />
      <MarketMechanics defaultOpen="orderbook" compact />
      <div className="mb-2">
        <CausalPipeline domain="TRADING" compact />
      </div>
      {/* News ticker */}
      <div className="flex items-center gap-3 px-3 py-2 rounded text-xs font-mono" style={{ background: news.severity === "critical" ? "oklch(0.20 0.08 25)" : news.severity === "high" ? "oklch(0.18 0.05 60)" : "oklch(0.14 0.01 240)", borderLeft: `3px solid ${news.severity === "critical" ? "#ef4444" : news.severity === "high" ? "oklch(0.75 0.18 75)" : news.severity === "positive" ? "#4ade80" : "oklch(0.35 0.01 240)"}` }}>
        <span className="w-1.5 h-1.5 rounded-full bg-red-400 flex-shrink-0" />
        <span className="text-[10px] font-bold" style={{ color: news.severity === "critical" ? "#f87171" : news.severity === "positive" ? "#4ade80" : "oklch(0.75 0.18 75)" }}>LIVE</span>
        <span className="text-muted-foreground flex-1">{news.text}</span>
        <button onClick={() => setIsFlashCrash((v) => !v)} className="ml-auto px-2 py-0.5 rounded text-[9px] font-bold flex-shrink-0" style={{ background: isFlashCrash ? "#ef4444" : "oklch(0.22 0.01 240)", color: isFlashCrash ? "white" : "oklch(0.55 0.01 240)" }}>
          {isFlashCrash ? "⚠ CRASH ACTIF" : "Simuler Crash"}
        </button>
      </div>

      {/* HOLD banner */}
      {holdActive && (
        <div className="flex items-center gap-3 px-3 py-2 rounded font-mono text-xs" style={{ background: "oklch(0.18 0.06 75)", border: "1px solid oklch(0.75 0.18 75 / 0.5)" }}>
          <span className="font-bold" style={{ color: "oklch(0.75 0.18 75)" }}>⏳ WAIT</span>
          <span className="text-muted-foreground">Guard X-108 — Pause obligatoire en cours (marché instable)</span>
          <div className="ml-auto flex items-center gap-2">
            <div className="w-32 h-1.5 rounded-full bg-black/40">
              <div className="h-full rounded-full transition-all" style={{ width: `${(holdElapsed / 10) * 100}%`, background: "oklch(0.75 0.18 75)" }} />
            </div>
            <span className="font-bold" style={{ color: "oklch(0.75 0.18 75)" }}>{(10 - holdElapsed).toFixed(0)}s</span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-12 gap-3">
        {/* Left + Center: Chart + Metrics + Brain */}
        <div className="col-span-8 flex flex-col gap-3">
          {/* Price header */}
          <div className="panel p-3">
            <div className="flex items-center justify-between mb-3">
              <div>
                <div className="flex items-center gap-3">
                  <span className="font-mono font-bold text-2xl text-foreground">{currentPrice.toFixed(2)} €</span>
                  <span className={`font-mono text-sm font-bold ${isUp ? "text-positive" : "text-negative"}`}>
                    {isUp ? "▲" : "▼"} {Math.abs(priceChange).toFixed(2)} ({priceChangePct > 0 ? "+" : ""}{priceChangePct.toFixed(2)}%)
                  </span>
                </div>
                <div className="text-[10px] text-muted-foreground mt-0.5 font-mono">OBSIDIA · Marché Continu · 1 tick/s · GBM + GARCH + Markov</div>
              </div>
              <div className="flex items-center gap-2">
                {isFlashCrash && <span className="px-2 py-1 rounded text-[10px] font-mono font-bold" style={{ background: "oklch(0.20 0.08 25)", color: "#f87171", border: "1px solid #ef4444/50" }}>⚠ FLASH CRASH</span>}
                <div className="flex items-center gap-1.5 px-2 py-1 rounded" style={{ background: "oklch(0.14 0.04 145)", border: "1px solid oklch(0.72 0.18 145 / 0.3)" }}>
                  <div className="w-1.5 h-1.5 rounded-full bg-green-400" />
                  <span className="text-[10px] font-mono text-green-400">LIVE</span>
                </div>
              </div>
            </div>
            <div style={{ height: "200px" }}>
              <canvas ref={canvasRef} width={800} height={200} style={{ width: "100%", height: "100%" }} />
            </div>
            <div className="flex items-end gap-0.5 mt-1" style={{ height: "24px" }}>
              {prices.slice(-50).map((p, i) => (
                <div key={i} className="flex-1 rounded-sm" style={{ height: `${Math.min(100, (p.volume / 1000) * 100)}%`, background: p.change >= 0 ? "rgba(74,222,128,0.35)" : "rgba(248,113,113,0.35)" }} />
              ))}
            </div>
          </div>

          {/* Metrics row */}
          {metrics && (
            <div className="grid grid-cols-5 gap-2">
              {[
                { label: "Sharpe", value: metrics.sharpe.toFixed(2), color: metrics.sharpe >= 1 ? "#4ade80" : metrics.sharpe >= 0 ? "oklch(0.75 0.18 75)" : "#f87171" },
                { label: "VaR 95%", value: `${(metrics.var95 * 100).toFixed(2)}%`, color: "#f87171" },
                { label: "Max DD", value: `${(metrics.maxDrawdown * 100).toFixed(1)}%`, color: "#f87171" },
                { label: "GARCH Vol", value: `${(metrics.garchVol * 100).toFixed(2)}%`, color: "oklch(0.75 0.18 75)" },
                { label: "Return", value: `${metrics.totalReturn >= 0 ? "+" : ""}${(metrics.totalReturn * 100).toFixed(2)}%`, color: metrics.totalReturn >= 0 ? "#4ade80" : "#f87171" },
              ].map((m) => (
                <div key={m.label} className="panel p-2 text-center">
                  <div className="font-mono font-bold text-sm" style={{ color: m.color }}>{m.value}</div>
                  <div className="text-[9px] text-muted-foreground">{m.label}</div>
                </div>
              ))}
            </div>
          )}

          {/* Cerveau Ouvert */}
          {lastTrade && (
            <div className="panel p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono text-green-400/70 uppercase tracking-widest">🧠 Cerveau Ouvert — Guard X-108</span>
                <div className="flex items-center gap-2">
                  <DecisionBadge decision={lastTrade.decision} />
                  <button onClick={() => explainDecision.mutate({ vertical: "TRADING", decision: lastTrade.decision, metrics: { coherence: lastTrade.decision === "ALLOW" ? 0.92 : 0.45, holdRemaining: lastTrade.holdRemaining ?? 0, tau: 10 }, context: `${lastTrade.type} ${lastTrade.amount}€ @ ${lastTrade.price.toFixed(2)}€`, capitalImpact: lastTrade.capitalImpact })} disabled={explainDecision.isPending} className="text-[10px] font-mono px-2 py-1 rounded border border-green-400/30 text-green-400 hover:bg-green-400/10 transition-colors">
                    {explainDecision.isPending ? "⟳..." : "🌐 Expliquer"}
                  </button>
                </div>
              </div>
              <OpenBrainView data={{ ...buildBrainData(lastTrade), explanation: aiExplanation ?? undefined }} />
              {lastTrade.decision === "BLOCK" && (
                <div className="mt-2 p-2 rounded text-xs font-mono" style={{ background: "oklch(0.12 0.04 145)", color: "#4ade80", border: "1px solid oklch(0.72 0.18 145 / 0.3)" }}>
                  ✓ Capital protégé : +{lastTrade.amount.toLocaleString("fr-FR")} € · Total sauvé : {capitalSaved.toLocaleString("fr-FR")} €
                </div>
              )}
            </div>
          )}

          {/* Positions */}
          {positions.length > 0 && (
            <div className="panel p-3">
              <div className="metric-label mb-2">Positions ouvertes ({positions.length})</div>
              <div className="space-y-1">
                {positions.slice(-5).reverse().map((p, i) => (
                  <div key={i} className="flex items-center justify-between text-xs font-mono py-1 border-b border-border/30 last:border-0">
                    <span className={p.type === "BUY" ? "text-positive" : "text-negative"}>{p.type === "BUY" ? "▲ ACHAT" : "▼ VENTE"}</span>
                    <span className="text-foreground">{p.amount.toLocaleString("fr-FR")} €</span>
                    <span className="text-muted-foreground">@ {p.price.toFixed(2)} €</span>
                    <span className="text-[9px] text-muted-foreground">{new Date(p.timestamp).toLocaleTimeString("fr-FR")}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right: Order book + Order panel */}
        <div className="col-span-4 flex flex-col gap-3">
          {/* Carnet d'ordres */}
          <div className="panel p-3">
            <div className="metric-label mb-2">Carnet d'Ordres</div>
            <div className="space-y-0.5">
              {orderBook.filter((o) => o.side === "ask").slice(0, 6).map((o, i) => (
                <div key={i} className="flex items-center justify-between text-[10px] font-mono relative py-0.5">
                  <div className="absolute right-0 top-0 bottom-0 rounded" style={{ width: `${Math.min(100, (o.size / 1500) * 100)}%`, background: "rgba(248,113,113,0.12)" }} />
                  <span className="text-negative z-10">{o.price.toFixed(2)}</span>
                  <span className="text-muted-foreground z-10">{o.size}</span>
                </div>
              ))}
              <div className="flex items-center justify-center py-1.5 my-1 rounded font-mono font-bold text-sm" style={{ background: isUp ? "oklch(0.14 0.04 145)" : "oklch(0.18 0.06 25)", color: isUp ? "#4ade80" : "#f87171" }}>
                {currentPrice.toFixed(2)}
              </div>
              {orderBook.filter((o) => o.side === "bid").slice(0, 6).map((o, i) => (
                <div key={i} className="flex items-center justify-between text-[10px] font-mono relative py-0.5">
                  <div className="absolute right-0 top-0 bottom-0 rounded" style={{ width: `${Math.min(100, (o.size / 1500) * 100)}%`, background: "rgba(74,222,128,0.12)" }} />
                  <span className="text-positive z-10">{o.price.toFixed(2)}</span>
                  <span className="text-muted-foreground z-10">{o.size}</span>
                </div>
              ))}
            </div>
          </div>

          {/* ── PASSATION D'ORDRE ── */}
          <div className="panel p-3">
            <div className="metric-label mb-3">Passation d'Ordre</div>
            <div className="mb-3">
              <div className="text-[10px] text-muted-foreground font-mono mb-1.5">Montant (€)</div>
              <div className="flex gap-1 flex-wrap mb-2">
                {[1000, 5000, 10000, 25000, 50000].map((v) => (
                  <button key={v} onClick={() => setOrderAmount(v)} className="px-2 py-1 rounded text-[10px] font-mono transition-all" style={{ background: orderAmount === v ? "oklch(0.65 0.18 220 / 0.2)" : "oklch(0.14 0.01 240)", color: orderAmount === v ? "oklch(0.65 0.18 220)" : "oklch(0.55 0.01 240)", border: `1px solid ${orderAmount === v ? "oklch(0.65 0.18 220 / 0.5)" : "oklch(0.22 0.01 240)"}` }}>
                    {v >= 1000 ? `${v / 1000}k` : v}
                  </button>
                ))}
              </div>
              <input type="number" value={orderAmount} onChange={(e) => setOrderAmount(Number(e.target.value) || 0)} className="w-full bg-input border border-border rounded px-2 py-1.5 font-mono text-sm text-foreground text-right" />
            </div>
            <div className="text-[10px] text-muted-foreground font-mono mb-3 flex justify-between">
              <span>Prix actuel</span>
              <span className={isUp ? "text-positive" : "text-negative"}>{currentPrice.toFixed(2)} €</span>
            </div>
            <div className="grid grid-cols-2 gap-2 mb-3">
              <button onClick={() => executeOrder("BUY")} disabled={holdActive} className="py-3 rounded font-mono font-bold text-sm transition-all" style={{ background: holdActive ? "oklch(0.18 0.01 240)" : "#16a34a", color: holdActive ? "oklch(0.45 0.01 240)" : "white" }}>
                ▲ ACHETER
              </button>
              <button onClick={() => executeOrder("SELL")} disabled={holdActive} className="py-3 rounded font-mono font-bold text-sm transition-all" style={{ background: holdActive ? "oklch(0.18 0.01 240)" : "#dc2626", color: holdActive ? "oklch(0.45 0.01 240)" : "white" }}>
                ▼ VENDRE
              </button>
            </div>
            <div className="text-[9px] text-muted-foreground font-mono text-center">
              <ConceptTooltip term="Guard X-108" showIcon>Guard X-108</ConceptTooltip> actif · <ConceptTooltip term="Temporal Lock" showIcon>τ=10s</ConceptTooltip> · {capitalSaved > 0 ? `${capitalSaved.toLocaleString("fr-FR")} € protégés` : "Aucun blocage ce jour"}
            </div>
            <div className="mt-2 flex justify-center">
              <DecisionLegend compact />
            </div>
            {holdActive && (
              <div className="mt-3 flex flex-col items-center">
                <StrasbourgClock active={holdActive} tau={10} elapsed={holdElapsed} label="HOLD TEMPOREL X-108" />
              </div>
            )}
          </div>
          {/* ── BLOC 4 : Pilotage ── */}
          <PilotagePanel
            domain="trading"
            onRerun={() => executeOrder("BUY")}
            onReset={() => { setLastTrade(null); setCanonicalEnvelope(null); setCanonicalVerify(null); }}
            loading={decisionEnvelopeMut.isPending || holdActive}
            pythonAvailable={(canonicalAttestation.data as any)?.merkle_root ? true : canonicalAttestation.isLoading ? undefined : false}
            mode={canonicalEnvelope?.source === "python" ? "real" : canonicalEnvelope ? "fallback" : undefined}
            scenarioLabel={isFlashCrash ? "Flash Crash actif" : "Normal"}
          />

          {capitalSaved > 0 && (
            <div className="panel p-2 text-center" style={{ border: "1px solid oklch(0.72 0.18 145 / 0.3)", background: "oklch(0.12 0.04 145)" }}>
              <div className="text-[9px] text-muted-foreground font-mono mb-0.5">Capital Sauvé par Guard X-108</div>
              <div className="font-mono font-bold text-lg" style={{ color: "#4ade80" }}>+{capitalSaved.toLocaleString("fr-FR")} €</div>
            </div>
          )}
        </div>
      </div>

      {/* ─── Scenario Runner ─── */}
      <div className="mt-6 rounded p-4" style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
        <div className="flex items-center justify-between mb-3">
          <div className="text-[10px] font-mono uppercase tracking-widest" style={{ color: "oklch(0.65 0.18 220)" }}>Scenario Runner — Adversarial Tests</div>
          <div className="text-[9px] text-muted-foreground font-mono">7 scénarios · cliquer pour simuler</div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          {[
            { id: "flash_crash", icon: "💥", label: "Flash Crash", desc: "Prix −40% en 1 tick — Guard BLOCK immédiat", params: { seed: 42, steps: 252, S0: 100, mu: -0.08, sigma: 0.45, jumpLambda: 0.8, jumpMu: -0.40, jumpSigma: 0.15, garchAlpha: 0.3, garchBeta: 0.65, regimes: 2, frictionBps: 50 }, expected: "BLOCK" },
            { id: "liquidity_drain", icon: "💧", label: "Assèchement de liquidité", desc: "Impossible d’acheter ou vendre — marché gelé", params: { seed: 99, steps: 252, S0: 100, mu: -0.02, sigma: 0.35, jumpLambda: 0.4, jumpMu: -0.15, jumpSigma: 0.10, garchAlpha: 0.25, garchBeta: 0.70, regimes: 2, frictionBps: 200 }, expected: "BLOCK" },
            { id: "black_swan", icon: "🦢", label: "Cygne Noir", desc: "Événement extrême improbable — tous les modèles dépassés", params: { seed: 1337, steps: 252, S0: 100, mu: -0.12, sigma: 0.65, jumpLambda: 1.0, jumpMu: -0.50, jumpSigma: 0.25, garchAlpha: 0.45, garchBeta: 0.50, regimes: 3, frictionBps: 100 }, expected: "BLOCK" },
            { id: "bear_market", icon: "🐻", label: "Long Bear Market", desc: "Tendance baissière 200 jours — érosion lente", params: { seed: 7, steps: 252, S0: 100, mu: -0.03, sigma: 0.18, jumpLambda: 0.05, jumpMu: -0.08, jumpSigma: 0.05, garchAlpha: 0.08, garchBeta: 0.88, regimes: 2, frictionBps: 5 }, expected: "HOLD" },
            { id: "pump_dump", icon: "📈", label: "Pump & Dump", desc: "Manipulation coordonnée — spoofing détecté", params: { seed: 2024, steps: 100, S0: 100, mu: 0.15, sigma: 0.55, jumpLambda: 0.6, jumpMu: 0.20, jumpSigma: 0.20, garchAlpha: 0.35, garchBeta: 0.60, regimes: 2, frictionBps: 30 }, expected: "BLOCK" },
            { id: "algo_war", icon: "🤖", label: "Guerre d’algorithmes", desc: "Conflits entre robots de trading — ordres contradictoires", params: { seed: 555, steps: 252, S0: 100, mu: 0.0, sigma: 0.42, jumpLambda: 0.9, jumpMu: -0.05, jumpSigma: 0.30, garchAlpha: 0.40, garchBeta: 0.55, regimes: 3, frictionBps: 80 }, expected: "HOLD" },
            { id: "normal_bull", icon: "📉", label: "Normal Bull Market", desc: "Conditions normales — Guard ALLOW", params: { seed: 42, steps: 252, S0: 100, mu: 0.05, sigma: 0.2, jumpLambda: 0.1, jumpMu: -0.05, jumpSigma: 0.08, garchAlpha: 0.1, garchBeta: 0.85, regimes: 2, frictionBps: 5 }, expected: "ALLOW" },
          ].map(sc => (
            <button key={sc.id} onClick={() => simulate.mutate(sc.params)}
              disabled={simulate.isPending}
              className="text-left p-3 rounded transition-all"
              style={{ background: "oklch(0.13 0.01 240)", border: `1px solid ${sc.expected === "BLOCK" ? "oklch(0.55 0.18 25 / 0.3)" : sc.expected === "HOLD" ? "oklch(0.75 0.18 75 / 0.3)" : "oklch(0.72 0.18 145 / 0.3)"}` }}>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-base">{sc.icon}</span>
                <span className="font-mono font-bold text-xs text-foreground">{sc.label}</span>
                <span className="ml-auto text-[8px] font-mono px-1 py-0.5 rounded" style={{ background: sc.expected === "BLOCK" ? "oklch(0.55 0.18 25 / 0.2)" : sc.expected === "HOLD" ? "oklch(0.75 0.18 75 / 0.2)" : "oklch(0.72 0.18 145 / 0.2)", color: sc.expected === "BLOCK" ? "#f87171" : sc.expected === "HOLD" ? "oklch(0.75 0.18 75)" : "#4ade80" }}>{sc.expected}</span>
              </div>
              <div className="text-[9px] text-muted-foreground">{sc.desc}</div>
            </button>
          ))}
        </div>
        {metrics && (
          <div className="mt-3 grid grid-cols-4 gap-2">
            {[
              { label: "Volatility", value: `${((metrics.avgVolatility ?? 0.2) * 100).toFixed(1)}%`, color: (metrics.avgVolatility ?? 0.2) > 0.4 ? "#f87171" : "#4ade80" },
              { label: "Coherence", value: (metrics.avgCoherence ?? 0.85).toFixed(2), color: (metrics.avgCoherence ?? 0.85) < 0.3 ? "#f87171" : "#4ade80" },
              { label: "Guard Blocks", value: metrics.guardBlockCount ?? 0, color: "#f87171" },
              { label: "Sharpe Ratio", value: (metrics.sharpeRatio ?? 1.2).toFixed(2), color: "oklch(0.65 0.18 220)" },
            ].map(m => (
              <div key={m.label} className="rounded p-2 text-center" style={{ background: "oklch(0.14 0.01 240)" }}>
                <div className="font-mono font-bold text-sm" style={{ color: m.color }}>{m.value}</div>
                <div className="text-[9px] text-muted-foreground">{m.label}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ─── Canonical Real Panel (backend canonique) ─── */}
      {(canonicalEnvelope || decisionEnvelopeMut.isPending) && (
        <div className="mt-4">
          <CanonicalRealPanel
            title="TRADING WORLD — DÉCISION CANONIQUE X-108"
            payload={canonicalEnvelope}
            loading={decisionEnvelopeMut.isPending}
          />
          <CanonicalProofPanel
            verify={canonicalVerify}
            attestation={canonicalAttestation.data}
          />
        </div>
      )}

      {/* ── BLOC 5 : Projection futur ── */}
      <div className="mt-4">
        <ProjectionPanel
          domain="trading"
          horizon="5 min"
          scenarios={isFlashCrash ? [
            { label: "Poursuite du crash", probability: 0.55, outcome: "degradation", description: "Momentum baissier — stop-loss en cascade" },
            { label: "Rebond technique", probability: 0.30, outcome: "recovery", description: "Oversold — acheteurs institutionnels" },
            { label: "Stabilisation", probability: 0.15, outcome: "neutral", description: "Intervention banque centrale probable" },
          ] : undefined}
        />
      </div>
      {/* ─── Pipeline Gouvernance X-108 (moteur réel du repo) ─── */}
      <div className="mt-6">
        <EngineBlock
          domain="trading"
          amount={orderAmount}
          irreversible={true}
          asset="BTC"
          side="BUY"
          coherence={0.75}
          volatility={0.15}
          timeElapsed={12}
          tau={10}
          label={`TRADE BTC — ${orderAmount.toLocaleString("fr-FR")} €`}
          onDecision={(decision) => {
            if (decision === "BLOCK" || decision === "HOLD") {
              setCapitalSaved((prev) => prev + orderAmount);
            }
          }}
        />
      </div>

      {/* ─── SECTION CANONIQUE — 5 blocs (Situation / Constellation / Agrégation / Souveraineté / Preuve) ─── */}
      <div className="mt-8 border-t pt-6" style={{ borderColor: "oklch(0.20 0.01 240)" }}>
        <div className="text-[10px] font-mono uppercase tracking-widest mb-4" style={{ color: "oklch(0.40 0.01 240)" }}>Vue canonique — pipeline complet</div>
        <WorldPageTemplate
          domain="trading"
          title="Trading World — Vue Canonique"
          description="Pipeline complet : Situation → Constellation agentique → Agrégation → Souveraineté X-108 → Preuve"
          kpis={[
            { label: "Capital", value: orderAmount.toLocaleString("fr-FR") + " €", color: "oklch(0.72 0.18 145)" },
            { label: "Flash Crash", value: isFlashCrash ? "ACTIF" : "NORMAL", color: isFlashCrash ? "oklch(0.65 0.25 25)" : "oklch(0.72 0.18 145)" },
            { label: "Capital protégé", value: capitalSaved.toLocaleString("fr-FR") + " €", color: "oklch(0.72 0.18 45)" },
            { label: "Positions", value: String(positions.length), color: "oklch(0.65 0.18 240)" },
          ]}
          domainContentSlot={
            metrics ? (
              <div className="grid grid-cols-3 gap-3 text-[11px]">
                <div className="rounded p-2" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
                  <div className="text-muted-foreground mb-1">Rendement total</div>
                  <div className="font-mono font-bold" style={{ color: "oklch(0.72 0.18 145)" }}>{((metrics.totalReturn ?? 0) * 100).toFixed(2)}%</div>
                </div>
                <div className="rounded p-2" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
                  <div className="text-muted-foreground mb-1">Drawdown max</div>
                  <div className="font-mono font-bold" style={{ color: "oklch(0.65 0.25 25)" }}>{((metrics.maxDrawdown ?? 0) * 100).toFixed(2)}%</div>
                </div>
                <div className="rounded p-2" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
                  <div className="text-muted-foreground mb-1">Sharpe ratio</div>
                  <div className="font-mono font-bold" style={{ color: "oklch(0.72 0.18 45)" }}>{(metrics.sharpeRatio ?? 0).toFixed(2)}</div>
                </div>
              </div>
            ) : undefined
          }
        />
      </div>
    </div>
  );
}
