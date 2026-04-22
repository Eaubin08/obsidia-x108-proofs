/**
 * EcomWorld.tsx — OS4 v19
 * Pipeline WORLD → AGENTS → DECISIONS → X108 → PROOF
 * Tabs: Overview | Agents | Scenarios | Decision Stream
 */
import React, { useState, useEffect, useRef, useContext, useCallback } from "react";
import { useViewMode } from "@/contexts/ViewModeContext";
import { trpc } from "@/lib/trpc";
import { PortfolioContext } from "@/App";
import { DecisionBadge, HashDisplay } from "@/components/MetricCard";
import { MiniLineChart } from "@/components/MiniChart";
import { ConceptTooltip, DecisionLegend } from "@/components/ConceptTooltip";
import DecisionSummaryBar from "@/components/DecisionSummaryBar";
import PilotagePanel from "@/components/PilotagePanel";
import { ModeBadgeBar } from "@/components/ModeBadge";
import WorldMetierHeader from "@/components/WorldMetierHeader";
import ProjectionPanel from "@/components/ProjectionPanel";
import WorldPageTemplate from "@/components/WorldPageTemplate";

// ─── Types ────────────────────────────────────────────────────────────────────
const DEFAULT_PARAMS = {
  seed: 42, steps: 90, impressions: 10000,
  baseCTR: 0.03, baseCVR: 0.02, basePrice: 49.99, baseCOGS: 20,
  adSpend: 500, aiAgentEnabled: true, aiHoldSeconds: 10, priceElasticity: 1.5,
};
type Params = typeof DEFAULT_PARAMS;

interface StreamEvent {
  id: string;
  time: string;
  agent: string;
  proposal: string;
  engineScore: number;
  decision: "ALLOW" | "HOLD" | "BLOCK";
  reason: string;
  proofHash: string;
}

interface AgentCard {
  name: string;
  icon: string;
  goal: string;
  action: string;
  status: "active" | "blocked" | "hold";
}

// ─── Scenarios ────────────────────────────────────────────────────────────────
const SCENARIOS = [
  { id: "traffic_spike", label: "Traffic Spike", icon: "📈", desc: "10× traffic surge — agents propose aggressive discounts", params: { impressions: 100000, baseCTR: 0.08, adSpend: 2000 } },
  { id: "inventory_shortage", label: "Inventory Shortage", icon: "📦", desc: "Stock critically low — fulfillment agent blocked", params: { baseCVR: 0.001, adSpend: 5000 } },
  { id: "fake_reviews", label: "Fake Reviews Attack", icon: "🤖", desc: "Bot traffic detected — marketing agent HOLD", params: { baseCTR: 0.001, seed: 999 } },
  { id: "flash_sale", label: "Flash Sale", icon: "⚡", desc: "40% discount proposal — margin collapse risk", params: { basePrice: 29.99, adSpend: 3000 } },
  { id: "bot_traffic", label: "Bot Traffic", icon: "🚨", desc: "Fraudulent clicks — X-108 blocks ad spend", params: { baseCTR: 0.001, seed: 1337 } },
  { id: "competitor_ai", label: "Competitor AI Pricing", icon: "🤖", desc: "Rival AI undercuts every price in real-time — margin war", params: { basePrice: 19.99, baseCOGS: 18, adSpend: 4000 } },
  { id: "supply_crisis", label: "Global Supply Crisis", icon: "🌍", desc: "COGS +80%, delivery +14 days — fulfillment agent BLOCK", params: { baseCOGS: 36, baseCVR: 0.005, seed: 2024 } },
  { id: "viral_demand", label: "Viral Demand Spike", icon: "🔥", desc: "Product goes viral — 50× normal orders, stock exhausted", params: { impressions: 500000, baseCTR: 0.12, baseCVR: 0.08, adSpend: 0 } },
];

// ─── Helpers ──────────────────────────────────────────────────────────────────
function shortHash(seed: number | string): string {
  const n = typeof seed === "string" ? seed.split("").reduce((a, c) => a + c.charCodeAt(0), 0) : seed;
  return "0x" + Math.abs(n * 0x7f3a1b + 0xdeadbeef).toString(16).padStart(8, "0").slice(0, 8) + "…";
}

function buildAgents(result: any): AgentCard[] {
  const m = result?.metrics;
  const blocked = m?.agentBlockCount > 0;
  const held = m?.agentHoldCount > 0;
  return [
    { name: "Pricing Agent", icon: "💲", goal: "Maximize margin", action: m ? `Price: ${result.steps?.[result.steps.length - 1]?.price?.toFixed(2) ?? "—"} €` : "Idle", status: blocked ? "blocked" : "active" },
    { name: "Inventory Agent", icon: "📦", goal: "Prevent stockout", action: m ? `CVR: ${((result.steps?.[result.steps.length - 1]?.cvr ?? 0) * 100).toFixed(1)}%` : "Idle", status: held ? "hold" : "active" },
    { name: "Fulfillment Agent", icon: "🚚", goal: "Optimize delivery", action: m ? `Orders: ${result.steps?.[result.steps.length - 1]?.conversions ?? 0}` : "Idle", status: "active" },
    { name: "Marketing Agent", icon: "📣", goal: "Maximize ROAS", action: m ? `ROAS: ${m.avgROAS?.toFixed(2) ?? "—"}×` : "Idle", status: blocked ? "blocked" : "active" },
  ];
}

function buildDecisionProposals(result: any): any[] {
  if (!result?.steps) return [];
  const allActions = result.steps.flatMap((s: any) =>
    (s.agentActions ?? []).map((a: any) => ({ ...a, stepT: s.t, stepRevenue: s.revenue }))
  );
  return allActions.slice(-12).map((a: any, i: number) => ({
    time: `${String(Math.floor(i / 60)).padStart(2, "0")}:${String(i % 60).padStart(2, "0")}`,
    agent: a.agentId?.replace("agent-", "Agent ") ?? "—",
    proposal: `${a.actionType ?? "BID"} ${(a.amount ?? 500).toLocaleString()} €`,
    impact: a.x108Decision === "BLOCK" ? "⛔ Blocked" : a.x108Decision === "HOLD" ? `⏳ +${(a.amount ?? 500) * 0.05 | 0} € est.` : `+${(a.amount ?? 500) * 0.05 | 0} € est.`,
    decision: (a.x108Decision ?? "ALLOW") as "ALLOW" | "HOLD" | "BLOCK",
  }));
}

function buildStreamEvents(result: any, scenario: string): StreamEvent[] {
  if (!result?.steps) return [];
  const allActions = result.steps.flatMap((s: any, si: number) =>
    (s.agentActions ?? []).map((a: any, ai: number) => ({ ...a, si, ai }))
  );
  return allActions.slice(-20).map((a: any, i: number) => ({
    id: `ev-${i}`,
    time: new Date(Date.now() - (20 - i) * 3000).toLocaleTimeString("en-US", { hour12: false }),
    agent: a.agentId?.replace("agent-", "Agent ") ?? "—",
    proposal: `${a.actionType ?? "BID"} ${(a.amount ?? 500).toLocaleString()} €`,
    engineScore: a.coherence ?? 0.85,
    decision: (a.x108Decision ?? "ALLOW") as "ALLOW" | "HOLD" | "BLOCK",
    reason: a.x108Decision === "BLOCK" ? "Risque trop élevé" : a.x108Decision === "HOLD" ? "Vérification en cours" : "Action autorisée",
    proofHash: shortHash(a.si * 100 + a.ai + scenario.length),
  }));
}

// ─── Section Header ───────────────────────────────────────────────────────────
function SectionHeader({ step, title, subtitle }: { step: string; title: string; subtitle: string }) {
  return (
    <div className="flex items-center gap-3 mb-3">
      <div className="w-7 h-7 rounded flex items-center justify-center font-mono font-bold text-xs flex-shrink-0"
        style={{ background: "oklch(0.75 0.18 75 / 0.15)", color: "oklch(0.75 0.18 75)", border: "1px solid oklch(0.75 0.18 75 / 0.3)" }}>
        {step}
      </div>
      <div>
        <div className="font-mono font-bold text-sm text-foreground">{title}</div>
        <div className="text-[10px] text-muted-foreground">{subtitle}</div>
      </div>
    </div>
  );
}

function Divider() {
  return (
    <div className="flex items-center gap-2 my-1">
      <div className="flex-1 h-px" style={{ background: "oklch(0.20 0.01 240)" }} />
      <div className="text-[9px] font-mono" style={{ color: "oklch(0.30 0.01 240)" }}>▼</div>
      <div className="flex-1 h-px" style={{ background: "oklch(0.20 0.01 240)" }} />
    </div>
  );
}

// ─── Pipeline Diagram ─────────────────────────────────────────────────────────
function PipelineDiagram({ activeStep }: { activeStep: number }) {
  const steps = [
    { label: "WORLD", sub: "Market" },
    { label: "AGENTS", sub: "Proposals" },
    { label: "ENGINE", sub: "Metrics" },
    { label: "X-108", sub: "Guard" },
    { label: "DECISION", sub: "Output" },
    { label: "PROOF", sub: "Hash" },
  ];
  return (
    <div className="flex items-center justify-between mb-4 rounded p-3" style={{ background: "oklch(0.09 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
      {steps.map((s, i) => (
        <React.Fragment key={s.label}>
          <div className="flex flex-col items-center gap-0.5">
            <div className="px-2 py-1 rounded font-mono font-bold text-[9px] transition-all duration-300" style={{
              background: i <= activeStep ? "oklch(0.75 0.18 75 / 0.15)" : "oklch(0.14 0.01 240)",
              border: `1px solid ${i <= activeStep ? "oklch(0.75 0.18 75 / 0.5)" : "oklch(0.20 0.01 240)"}`,
              color: i <= activeStep ? "oklch(0.75 0.18 75)" : "oklch(0.40 0.01 240)",
              boxShadow: i === activeStep ? "0 0 8px oklch(0.75 0.18 75 / 0.3)" : "none",
            }}>{s.label}</div>
            <div className="text-[8px]" style={{ color: "oklch(0.35 0.01 240)" }}>{s.sub}</div>
          </div>
          {i < steps.length - 1 && (
            <div className="text-[9px] font-mono" style={{ color: i < activeStep ? "oklch(0.75 0.18 75)" : "oklch(0.25 0.01 240)" }}>→</div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────
export default function EcomWorld() {
  const portfolio = useContext(PortfolioContext);
  const { isSimple } = useViewMode();
  const { onGuardBlock } = portfolio;
  const [activeTab, setActiveTab] = useState<"overview" | "agents" | "scenarios" | "stream">("overview");
  const [params, setParams] = useState<Params>(DEFAULT_PARAMS);
  const [result, setResult] = useState<any>(null);
  const [activeScenario, setActiveScenario] = useState<string>("default");
  const [runningScenario, setRunningScenario] = useState<string | null>(null);

  const updateWalletMut = trpc.portfolio.updateWallet.useMutation();
  const saveSnapshotMut = trpc.portfolio.saveSnapshot.useMutation();
  const upsertPositionMut = trpc.portfolio.upsertPosition.useMutation();
  // Stats Guard réelles depuis la DB (persistantes entre sessions)
  const guardStatsQuery = trpc.proof.guardStats.useQuery(undefined, { refetchInterval: 15000 });
  const guardStats = guardStatsQuery.data;
  const ecomBlocked = guardStats?.byDomain?.ecom?.blocked ?? 0;
  const ecomTotal = guardStats?.byDomain?.ecom?.total ?? 0;

  const simulate = trpc.ecom.simulate.useMutation({
    onSuccess: (data) => {
      setResult(data);
      setRunningScenario(null);
      const metrics = data?.metrics;
      if (!metrics) return;
      if (metrics.agentBlockCount > 0) onGuardBlock();
      // Persist scenario result to portfolio (fire-and-forget)
      const revenue = metrics.totalRevenue ?? 0;
      const profit = metrics.totalMargin ?? 0;
      const guardBlocks = metrics.agentBlockCount ?? 0;
      const capitalSaved = guardBlocks * 1000; // estimated per blocked action
      updateWalletMut.mutate({
        capital: revenue,
        pnl24h: profit,
        guardBlocks,
        capitalSaved,
      });
      saveSnapshotMut.mutate({
        capital: revenue,
        pnl: profit,
        guardBlocks,
        capitalSaved,
        domain: "ecom",
        scenarioName: activeScenario !== "default" ? activeScenario : "E-Com Simulation",
      });
      upsertPositionMut.mutate({
        domain: "ecom",
        asset: `SCENARIO:${activeScenario}`,
        quantity: metrics.totalConversions ?? 1,
        avgEntryPrice: revenue / Math.max(1, metrics.totalConversions ?? 1),
        currentValue: revenue,
        unrealizedPnl: profit,
      });
    },
  });

  const handleRun = useCallback((overrideParams?: Partial<Params>, scenarioId?: string) => {
    const merged = { ...params, ...(overrideParams ?? {}) };
    setRunningScenario(scenarioId ?? "default");
    simulate.mutate(merged);
  }, [params, simulate]);

  useEffect(() => { handleRun(); }, []);

  const m = result?.metrics;
  const revenues = result?.steps?.map((s: any) => s.revenue) ?? [];
  const lastStep = result?.steps?.[result.steps.length - 1];
  const agents = buildAgents(result);
  const proposals = buildDecisionProposals(result);
  const streamEvents = buildStreamEvents(result, activeScenario);

  // Pipeline step: how far we are in the pipeline
  const pipelineStep = !result ? 0 : simulate.isPending ? 1 : proposals.length > 0 ? 4 : 2;

  // Last blocked action for X108 + Proof
  const allActions = result?.steps?.flatMap((s: any) =>
    (s.agentActions ?? []).map((a: any) => ({ ...a }))
  ) ?? [];
  const lastBlock = allActions.filter((a: any) => a.x108Decision === "BLOCK").pop();
  const lastDecision = lastBlock ?? allActions[allActions.length - 1];

  const TABS = [
    { id: "overview", label: "Overview" },
    { id: "agents", label: "Agents" },
    { id: "scenarios", label: "Scenarios" },
    { id: "stream", label: "Decision Stream" },
  ] as const;

  // Variables extraites pour éviter les ternaires imbriqués dans JSX (erreur Babel/Vite)
  const _ecomBlockCount = allActions.filter((a: any) => a.x108Decision === "BLOCK").length;
  const _ecomBlockStr = _ecomBlockCount > 0 ? String(_ecomBlockCount) + " bloqués" : "0 bloqué";
  const _ecomRevStr = m ? String((m.totalRevenue / 1000).toFixed(1)) + "k €" : "En attente";
  const _ecomLastVal = lastDecision ? lastDecision.x108Decision : "En attente";
  const _ecomLastGate = lastDecision?.x108Decision as string | undefined;
  const _ecomLastColor = _ecomLastGate === "BLOCK" ? "oklch(0.65 0.25 25)" : _ecomLastGate === "HOLD" ? "oklch(0.72 0.18 45)" : "oklch(0.72 0.18 145)";
  const _ecomLastIcon = _ecomLastGate === "BLOCK" ? "X" : _ecomLastGate === "HOLD" ? "||" : "OK";
  const _ecomLastDecision = (_ecomLastGate === "ALLOW" || _ecomLastGate === "HOLD" || _ecomLastGate === "BLOCK") ? _ecomLastGate as "ALLOW" | "HOLD" | "BLOCK" : null;

  return (
    <div className="flex flex-col gap-0">
      {/* ─── Barre de régime opératoire ─────────────────────────────────────── */}
      <ModeBadgeBar
        mode={result?.canonical?.trace_id ? "LIVE" : result ? "DEMO" : "DEMO"}
        detail={result?.canonical?.trace_id ? `trace : ${result.canonical.trace_id.slice(0, 12)}` : "Simulation e-commerce — aucune transaction réelle"}
        right={lastDecision ? `dernier : ${lastDecision.x108Decision}` : undefined}
      />
      {/* ── Header métier E-Commerce ── */}
      <WorldMetierHeader
        domain="ecom"
        mode="LIVE"
        x108Status={result?.canonical?.trace_id ? "ONLINE" : "DEGRADED"}
        lastDecision={_ecomLastDecision}
        decisionCount={_ecomBlockCount || undefined}
        verdicts={[
          { label: "Clients protégés", value: _ecomBlockStr, color: "oklch(0.72 0.18 45)", icon: "🛡️" },
          { label: "Revenue", value: _ecomRevStr, color: "oklch(0.72 0.18 145)", icon: "💰" },
          { label: "Dernière action", value: _ecomLastVal, color: _ecomLastColor, icon: _ecomLastIcon },
        ]}
        className="mb-2"
      />
      {/* ── TOP BAR ───────────────────────────────────────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-base font-bold font-mono" style={{ color: "oklch(0.75 0.18 75)" }}>E-commerce World</h2>
            <p className="text-[10px] text-muted-foreground mt-0.5">
            This simulated marketplace models traffic, conversion dynamics, pricing strategies and inventory constraints. Agents attempt to optimize revenue and margin while the X-108 governance kernel prevents dangerous decisions.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <a href="/future?domain=ecom"
            className="flex items-center gap-1 px-2 py-0.5 rounded text-[9px] font-mono font-bold"
            style={{ background: "oklch(0.72 0.18 45 / 0.12)", border: "1px solid oklch(0.72 0.18 45 / 0.35)", color: "oklch(0.72 0.18 45)" }}>
            ▶ Simuler dans Future
          </a>
          <div className="flex items-center gap-1.5 px-2 py-1 rounded" style={{ background: "oklch(0.75 0.18 75 / 0.08)", border: "1px solid oklch(0.75 0.18 75 / 0.25)" }}>
            <div className="w-1.5 h-1.5 rounded-full bg-amber-400" />
            <span className="text-[10px] font-mono text-amber-400">Guard X-108 actif</span>
          </div>
          <button onClick={() => handleRun()} disabled={simulate.isPending}
            className="px-3 py-1.5 rounded font-mono text-xs font-bold transition-all"
            style={{ background: simulate.isPending ? "oklch(0.22 0.01 240)" : "oklch(0.75 0.18 75)", color: simulate.isPending ? "oklch(0.55 0.01 240)" : "oklch(0.10 0.01 240)" }}>
            {simulate.isPending ? "⟳ RUNNING…" : "▶ RUN"}
          </button>
        </div>
      </div>      {/* ── BLOC 1 : Résultat visible en 3s ── */}
      <div className="mb-3">
        <DecisionSummaryBar
          gate={lastDecision?.x108Decision ?? null}
          verdict={lastDecision?.x108Decision === "BLOCK" ? "ACTION_BLOCKED" : lastDecision?.x108Decision === "HOLD" ? "HOLD_X108" : lastDecision?.x108Decision === "ALLOW" ? "ACTION_EXECUTED" : undefined}
          source={result?.canonical?.trace_id ? "python" : result ? "os4_local_fallback" : undefined}
          reason={lastDecision?.x108Decision === "BLOCK" ? "Risque trop élevé — seuil de sécurité dépassé" : lastDecision?.x108Decision === "HOLD" ? "Vérification en cours — action suspendue" : lastDecision?.x108Decision === "ALLOW" ? "Toutes les règles respectées" : undefined}
          loading={simulate.isPending}
          domain="ecom"
        />
      </div>
      {/* ── WORLD EXPLAINED ──────────────────────────────────────── */}
      <div className="mb-4 rounded-lg p-4" style={{ background: "oklch(0.75 0.18 75 / 0.05)", border: "1px solid oklch(0.75 0.18 75 / 0.15)" }}>
        <div className="font-mono text-[9px] font-bold tracking-widest mb-2" style={{ color: "oklch(0.75 0.18 75)" }}>WORLD EXPLAINED</div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div>
            <div className="font-mono text-[9px] font-bold mb-1" style={{ color: "oklch(0.75 0.18 75 / 0.7)" }}>WHAT IS HAPPENING</div>
            <p className="font-mono text-[10px] leading-relaxed" style={{ color: "oklch(0.50 0.01 240)" }}>Agent Mercury monitors a simulated marketplace — traffic, conversion rates, inventory, pricing. Each pricing or promotion decision is proposed to Guard X-108 before execution.</p>
          </div>
          <div>
            <div className="font-mono text-[9px] font-bold mb-1" style={{ color: "oklch(0.75 0.18 75 / 0.7)" }}>WHY IT MATTERS</div>
            <p className="font-mono text-[10px] leading-relaxed" style={{ color: "oklch(0.50 0.01 240)" }}>Aggressive pricing or flash sales can destroy margins. Guard X-108 blocks decisions that would cause irreversible financial damage, even when the agent is confident.</p>
          </div>
          <div>
            <div className="font-mono text-[9px] font-bold mb-1" style={{ color: "oklch(0.75 0.18 75 / 0.7)" }}>WHAT IT PROVES</div>
            <p className="font-mono text-[10px] leading-relaxed" style={{ color: "oklch(0.50 0.01 240)" }}>Every blocked decision is cryptographically anchored. Negative margin events are explained, not hidden — the system shows exactly why it intervened.</p>
          </div>
        </div>
      </div>

      {/* ── PIPELINE DIAGRAM ──────────────────────────────────────────────── */}      {activeTab === "overview" && <PipelineDiagram activeStep={pipelineStep} />}

      {/* ── TABS ────────────────────────────────────────────────────────── */}
      <div className="flex items-center gap-1 mb-4 border-b" style={{ borderColor: "oklch(0.20 0.01 240)" }}>
        {TABS.map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)}
            className="px-3 py-2 font-mono text-xs transition-all"
            style={{
              color: activeTab === tab.id ? "oklch(0.75 0.18 75)" : "oklch(0.45 0.01 240)",
              borderBottom: activeTab === tab.id ? "2px solid oklch(0.75 0.18 75)" : "2px solid transparent",
              marginBottom: "-1px",
            }}>
            {tab.label}
          </button>
        ))}
      </div>

      {/* ══════════════════════════════════════════════════════════════════
          TAB: OVERVIEW — Full pipeline WORLD → AGENTS → DECISIONS → X108 → PROOF
      ══════════════════════════════════════════════════════════════════ */}
      {activeTab === "overview" && (
        <div className="flex flex-col gap-3">

          {/* ── BLOC 1 : WORLD ──────────────────────────────────────────── */}
          <div className="rounded p-4" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
            <SectionHeader step="1" title="E-commerce World" subtitle="Simulated marketplace — traffic · conversion · inventory · pricing" />
            <div className="grid grid-cols-5 gap-2 mb-3">
              {[
                { label: "Traffic", value: m ? `${(m.totalImpressions / 1000).toFixed(0)}k` : "—", icon: "👁", color: "oklch(0.65 0.15 200)" },
                { label: "Conversion", value: lastStep ? `${(lastStep.cvr * 100).toFixed(1)}%` : "—", icon: "🎯", color: "#4ade80" },
                { label: "Revenue", value: m ? `${(m.totalRevenue / 1000).toFixed(1)}k €` : "—", icon: "💰", color: "oklch(0.75 0.18 75)" },
                { label: "Orders", value: lastStep ? `${lastStep.conversions}` : "—", icon: "📦", color: "oklch(0.72 0.18 145)" },
                { label: "Inventory", value: lastStep ? `${(lastStep.cvr * 100).toFixed(0)}%` : "—", icon: "🏭", color: "#f87171" },
              ].map(item => (
                <div key={item.label} className="rounded p-2 text-center" style={{ background: "oklch(0.14 0.01 240)" }}>
                  <div className="text-lg mb-0.5">{item.icon}</div>
                  <div className="font-mono font-bold text-sm" style={{ color: item.color }}>{item.value}</div>
                  <div className="text-[9px] text-muted-foreground">{item.label}</div>
                </div>
              ))}
            </div>
            {revenues.length > 0 && (
              <div style={{ height: "80px" }}>
                <MiniLineChart data={revenues} color="oklch(0.75 0.18 75)" fillColor="oklch(0.75 0.18 75)" />
              </div>
            )}
            {!revenues.length && (
              <div className="h-16 flex items-center justify-center text-[10px] text-muted-foreground font-mono">
                Run simulation to see traffic + orders timeline
              </div>
            )}
          </div>

          <Divider />

          {/* ── BLOC 2 : AGENTS ─────────────────────────────────────────── */}
          <div className="rounded p-4" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
            <SectionHeader step="2" title="Autonomous Commerce Agents" subtitle="4 agents monitoring market conditions and proposing actions" />
            <div className="grid grid-cols-4 gap-2">
              {agents.map(agent => (
                <div key={agent.name} className="rounded p-3 flex flex-col gap-2" style={{
                  background: "oklch(0.14 0.01 240)",
                  border: `1px solid ${agent.status === "blocked" ? "oklch(0.45 0.18 25 / 0.4)" : agent.status === "hold" ? "oklch(0.75 0.18 75 / 0.3)" : "oklch(0.22 0.01 240)"}`,
                }}>
                  <div className="flex items-center justify-between">
                    <span className="text-xl">{agent.icon}</span>
                    <span className="text-[9px] font-mono px-1.5 py-0.5 rounded" style={{
                      background: agent.status === "blocked" ? "oklch(0.45 0.18 25 / 0.2)" : agent.status === "hold" ? "oklch(0.75 0.18 75 / 0.15)" : "oklch(0.72 0.18 145 / 0.15)",
                      color: agent.status === "blocked" ? "#f87171" : agent.status === "hold" ? "oklch(0.75 0.18 75)" : "#4ade80",
                    }}>
                      {agent.status.toUpperCase()}
                    </span>
                  </div>
                  <div className="font-mono font-bold text-xs text-foreground">{agent.name}</div>
                  <div className="text-[9px] text-muted-foreground">Goal: {agent.goal}</div>
                  <div className="text-[9px] font-mono" style={{ color: "oklch(0.65 0.01 240)" }}>Action: {agent.action}</div>
                </div>
              ))}
            </div>
          </div>

          <Divider />

          {/* ── BLOC 3 : DECISION PROPOSALS ─────────────────────────────── */}
          <div className="rounded p-4" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
            <SectionHeader step="3" title="Agent Decisions" subtitle="Proposals submitted to Guard X-108 for evaluation" />
            {proposals.length === 0 ? (
              <div className="text-[10px] text-muted-foreground font-mono text-center py-4">Run simulation to see proposals</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-[10px] font-mono">
                  <thead>
                    <tr style={{ borderBottom: "1px solid oklch(0.20 0.01 240)" }}>
                      {["Time", "Agent", "Proposal", "Impact", "Decision"].map(h => (
                        <th key={h} className="text-left pb-2 pr-4" style={{ color: "oklch(0.45 0.01 240)" }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {proposals.slice(0, 8).map((p, i) => (
                      <tr key={i} style={{ borderBottom: "1px solid oklch(0.15 0.01 240)" }}>
                        <td className="py-1.5 pr-4 text-muted-foreground">{p.time}</td>
                        <td className="py-1.5 pr-4 text-foreground">{p.agent}</td>
                        <td className="py-1.5 pr-4" style={{ color: "oklch(0.75 0.18 75)" }}>{p.proposal}</td>
                        <td className="py-1.5 pr-4 text-muted-foreground">{p.impact}</td>
                        <td className="py-1.5"><DecisionBadge decision={p.decision} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <Divider />

          {/* ── BLOC 4 : GOVERNANCE X-108 ───────────────────────────────── */}
          <div className="rounded p-4" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
            <SectionHeader step="4" title="Governance Kernel — X108" subtitle="Formal evaluation of agent proposals — BLOCK · HOLD · ALLOW" />
            <div className="mb-3"><DecisionLegend compact /></div>
            {lastDecision ? (
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded p-3" style={{ background: "oklch(0.14 0.01 240)" }}>
                  <div className="text-[9px] text-muted-foreground font-mono mb-2">LAST PROPOSAL</div>
                  <div className="font-mono text-xs text-foreground mb-1">{lastDecision.actionType ?? "BID"} — {(lastDecision.amount ?? 500).toLocaleString()} €</div>
                  <div className="text-[9px] text-muted-foreground">Agent: {lastDecision.agentId?.replace("agent-", "Agent ") ?? "—"}</div>
                </div>
                <div className="rounded p-3" style={{ background: "oklch(0.14 0.01 240)" }}>
                  <div className="text-[9px] text-muted-foreground font-mono mb-2"><ConceptTooltip term="Guard X-108" showIcon>X-108 DECISION</ConceptTooltip></div>
                  <div className="flex items-center gap-2 mb-1">
                    <DecisionBadge decision={(lastDecision.x108Decision ?? "ALLOW") as "ALLOW" | "HOLD" | "BLOCK"} />
                  </div>
                    <div className="text-[9px]" style={{ color: lastDecision.x108Decision === "BLOCK" ? "#f87171" : lastDecision.x108Decision === "HOLD" ? "oklch(0.75 0.18 75)" : "#4ade80" }}>
                    Raison : {lastDecision.x108Decision === "BLOCK" ? "Risque trop élevé — seuil de sécurité dépassé" : lastDecision.x108Decision === "HOLD" ? "Vérification en cours — action suspendue" : "Toutes les règles respectées — action sûre"}
                  </div>
                </div>
                <div className="rounded p-2" style={{ background: "oklch(0.14 0.01 240)" }}>
                  <div className="text-[9px] text-muted-foreground font-mono mb-1">RISK SCORE</div>
                  <div className="h-1.5 rounded-full bg-black/30">
                    <div className="h-full rounded-full" style={{ width: `${((1 - (lastDecision.coherence ?? 0.85)) * 100).toFixed(0)}%`, background: "#f87171" }} />
                  </div>
                  <div className="font-mono text-xs mt-1" style={{ color: "#f87171" }}>{((1 - (lastDecision.coherence ?? 0.85)) * 100).toFixed(0)}%</div>
                </div>
                <div className="rounded p-2" style={{ background: "oklch(0.14 0.01 240)" }}>
                  <div className="text-[9px] text-muted-foreground font-mono mb-1">FIABILITÉ</div>
                  <div className="h-1.5 rounded-full bg-black/30">
                    <div className="h-full rounded-full" style={{ width: `${((lastDecision.coherence ?? 0.85) * 100).toFixed(0)}%`, background: "#4ade80" }} />
                  </div>
                  <div className="font-mono text-xs mt-1" style={{ color: "#4ade80" }}>{((lastDecision.coherence ?? 0.85) * 100).toFixed(0)}%</div>
                </div>
              </div>
            ) : (
              <div className="text-[10px] text-muted-foreground font-mono text-center py-4">Lancez une simulation pour voir les décisions de Guard X-108</div>
            )}
            {m && (
              <div className="grid grid-cols-3 gap-2 mt-3">
                {[
                  { label: "BLOCK", value: m.agentBlockCount ?? 0, color: "#f87171" },
                  { label: "HOLD", value: m.agentHoldCount ?? 0, color: "oklch(0.75 0.18 75)" },
                  { label: "ALLOW", value: (allActions.length - (m.agentBlockCount ?? 0) - (m.agentHoldCount ?? 0)), color: "#4ade80" },
                ].map(item => (
                  <div key={item.label} className="rounded p-2 text-center" style={{ background: "oklch(0.14 0.01 240)" }}>
                    <div className="font-mono font-bold text-lg" style={{ color: item.color }}>{item.value}</div>
                    <div className="text-[9px] text-muted-foreground">{item.label}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <Divider />

          {/* ── BLOC 5 : PROOF — Canonical Python backend ───────────────── */}
          <div className="rounded p-4" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
            <SectionHeader step="5" title="Decision Proof" subtitle="Canonical Python backend — OS4 runtime trace" />
            {result?.canonical ? (
              <div className="flex flex-col gap-2">
                {/* Source + verdict badges */}
                <div className="flex items-center gap-2 flex-wrap mb-1">
                  <span className="text-[9px] font-mono px-2 py-0.5 rounded" style={{ background: "oklch(0.72 0.18 145 / 0.12)", color: "oklch(0.72 0.18 145)", border: "1px solid oklch(0.72 0.18 145 / 0.25)" }}>
                    {(result.canonical.trace_id ?? '').startsWith('py-') || (result.canonical.decision_id ?? '').startsWith('py-') ? '⬡ source: python_backend' : '□ source: os4_local_fallback'}
                  </span>
                  <span className="text-[9px] font-mono px-2 py-0.5 rounded" style={{
                    background: result.canonical.x108_gate === 'ALLOW' ? 'oklch(0.72 0.18 145 / 0.10)' : result.canonical.x108_gate === 'HOLD' ? 'oklch(0.75 0.18 75 / 0.10)' : 'oklch(0.45 0.18 25 / 0.10)',
                    color: result.canonical.x108_gate === 'ALLOW' ? '#4ade80' : result.canonical.x108_gate === 'HOLD' ? '#fbbf24' : '#f87171',
                    border: `1px solid ${result.canonical.x108_gate === 'ALLOW' ? '#4ade8030' : result.canonical.x108_gate === 'HOLD' ? '#fbbf2430' : '#f8717130'}`,
                  }}>
                    X-108: {result.canonical.x108_gate}
                  </span>
                  <span className="text-[9px] font-mono px-2 py-0.5 rounded" style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.50 0.01 240)" }}>
                    severity: {result.canonical.severity ?? 'S0'}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div className="rounded p-3" style={{ background: "oklch(0.14 0.01 240)" }}>
                    <div className="text-[9px] text-muted-foreground font-mono mb-1">TRACE ID (Python)</div>
                    <div className="font-mono text-[10px] truncate" style={{ color: "oklch(0.72 0.18 145)" }}>
                      {result.canonical.trace_id ? result.canonical.trace_id.slice(0, 22) + '…' : '—'}
                    </div>
                  </div>
                  <div className="rounded p-3" style={{ background: "oklch(0.14 0.01 240)" }}>
                    <div className="text-[9px] text-muted-foreground font-mono mb-1">DECISION ID</div>
                    <div className="font-mono text-[10px] truncate" style={{ color: "oklch(0.72 0.18 145)" }}>
                      {result.canonical.decision_id ?? '—'}
                    </div>
                  </div>
                  <div className="rounded p-3" style={{ background: "oklch(0.14 0.01 240)" }}>
                    <div className="text-[9px] text-muted-foreground font-mono mb-1">MARKET VERDICT</div>
                    <div className="font-mono text-[10px] text-foreground">{result.canonical.market_verdict ?? '—'}</div>
                  </div>
                  <div className="rounded p-3" style={{ background: "oklch(0.14 0.01 240)" }}>
                    <div className="text-[9px] text-muted-foreground font-mono mb-1">REASON CODE</div>
                    <div className="font-mono text-[10px] text-foreground">{result.canonical.reason_code ?? '—'}</div>
                  </div>
                </div>
                {result.canonical.ticket_id && (
                  <div className="rounded p-2" style={{ background: "oklch(0.14 0.01 240)" }}>
                    <div className="text-[9px] text-muted-foreground font-mono mb-1">TICKET ID</div>
                    <div className="font-mono text-[10px]" style={{ color: "oklch(0.72 0.18 145)" }}>{result.canonical.ticket_id}</div>
                  </div>
                )}
                {result.canonical.attestation_ref && (
                  <div className="rounded p-2" style={{ background: "oklch(0.14 0.01 240)" }}>
                    <div className="text-[9px] text-muted-foreground font-mono mb-1">ATTESTATION REF</div>
                    <div className="font-mono text-[10px] truncate" style={{ color: "oklch(0.72 0.18 145)" }}>{result.canonical.attestation_ref}</div>
                  </div>
                )}
                <div className="rounded p-2" style={{ background: "oklch(0.72 0.18 145 / 0.08)", border: "1px solid oklch(0.72 0.18 145 / 0.2)" }}>
                  <div className="text-[9px] font-mono mb-1" style={{ color: "oklch(0.72 0.18 145)" }}>✓ Canonical Python decision — OS4 runtime trace immutably recorded</div>
                  <div className="text-[9px] text-muted-foreground">{"Source: Obsidia-lab-trad Python backend. The trace_id is a UUID generated by the Python kernel and stored in api_store. Any auditor can replay this decision via /v1/replay/{trace_id}."}</div>
                </div>
              </div>
            ) : (
              <div className="text-[10px] text-muted-foreground font-mono text-center py-4">Run simulation to generate canonical proof</div>
            )}
          </div>

        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════════
          TAB: AGENTS — Detailed agent cards
      ══════════════════════════════════════════════════════════════════ */}
      {activeTab === "agents" && (
        <div className="flex flex-col gap-4">
          <div className="grid grid-cols-2 gap-3">
            {agents.map(agent => (
              <div key={agent.name} className="rounded p-4" style={{
                background: "oklch(0.11 0.01 240)",
                border: `1px solid ${agent.status === "blocked" ? "oklch(0.45 0.18 25 / 0.5)" : agent.status === "hold" ? "oklch(0.75 0.18 75 / 0.4)" : "oklch(0.20 0.01 240)"}`,
              }}>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{agent.icon}</span>
                    <div>
                      <div className="font-mono font-bold text-sm text-foreground">{agent.name}</div>
                      <div className="text-[9px] text-muted-foreground">Goal: {agent.goal}</div>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-1 rounded" style={{
                    background: agent.status === "blocked" ? "oklch(0.45 0.18 25 / 0.2)" : agent.status === "hold" ? "oklch(0.75 0.18 75 / 0.15)" : "oklch(0.72 0.18 145 / 0.15)",
                    color: agent.status === "blocked" ? "#f87171" : agent.status === "hold" ? "oklch(0.75 0.18 75)" : "#4ade80",
                  }}>
                    {agent.status.toUpperCase()}
                  </span>
                </div>
                <div className="rounded p-2" style={{ background: "oklch(0.14 0.01 240)" }}>
                  <div className="text-[9px] text-muted-foreground font-mono mb-1">CURRENT ACTION</div>
                  <div className="font-mono text-xs text-foreground">{agent.action}</div>
                </div>
              </div>
            ))}
          </div>
          {m && (
            <div className="rounded p-4" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
              <div className="text-[10px] font-mono uppercase tracking-widest mb-3" style={{ color: "oklch(0.45 0.01 240)" }}>Agent Performance</div>
              <div className="grid grid-cols-4 gap-2">
                {[
                  { label: "Total Revenue", value: `${(m.totalRevenue / 1000).toFixed(1)}k €`, color: "#4ade80" },
                  { label: "Total Margin", value: `${m.totalMargin >= 0 ? "+" : ""}${(m.totalMargin / 1000).toFixed(1)}k €`, color: m.totalMargin >= 0 ? "#4ade80" : "#f87171" },
                  { label: "Avg ROAS", value: `${m.avgROAS?.toFixed(2) ?? "—"}×`, color: "oklch(0.65 0.18 220)" },
                  { label: "X-108 Compliance", value: `${((m.x108ComplianceRate ?? 0) * 100).toFixed(0)}%`, color: "#4ade80" },
                ].map(item => (
                  <div key={item.label} className="rounded p-2 text-center" style={{ background: "oklch(0.14 0.01 240)" }}>
                    <div className="font-mono font-bold text-sm" style={{ color: item.color }}>{item.value}</div>
                    <div className="text-[9px] text-muted-foreground">{item.label}</div>
                  </div>
                ))}
              </div>
              {m.totalMargin < 0 && (
                <div className="mt-2 rounded px-3 py-2 text-[9px] font-mono" style={{ background: "rgba(248,113,113,0.08)", border: "1px solid rgba(248,113,113,0.25)", color: "#f87171" }}>
                  ⚠️ Negative margin — COGS ({(m.totalCOGS / 1000).toFixed(1)}k €) + Ad spend ({(m.totalAdSpend / 1000).toFixed(1)}k €) exceed revenue. This is expected for high-stress scenarios (Flash Sale, Supply Crisis). Guard X-108 blocked {m.agentBlockCount ?? 0} actions to limit losses.
                </div>
              )}
              {/* Stats Guard DB globales */}
              <div className="mt-2 rounded px-3 py-2 text-[9px] font-mono flex items-center gap-3" style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
                <span style={{ color: "oklch(0.45 0.01 240)" }}>HISTORIQUE GLOBAL (DB)</span>
                <span style={{ color: "#f87171" }}>🛡 {ecomBlocked} BLOCK</span>
                <span style={{ color: "oklch(0.45 0.01 240)" }}>sur {ecomTotal} décisions ecom</span>
                <span className="ml-auto text-[8px] px-1.5 py-0.5 rounded" style={{ background: "oklch(0.60 0.12 200 / 0.15)", color: "oklch(0.60 0.12 200)" }}>source DB</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ════════════════════════════════════════════════════════════
          TAB: SCENARIOS — Scenario Runner
      ══════════════════════════════════════════════════════════════════ */}
      {activeTab === "scenarios" && (
        <div className="flex flex-col gap-3">
          <div className="rounded p-3" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
            <div className="text-[10px] font-mono uppercase tracking-widest mb-3" style={{ color: "oklch(0.45 0.01 240)" }}>Scenario Runner</div>
            <div className="flex flex-col gap-2">
              {SCENARIOS.map(sc => (
                <div key={sc.id} className="flex items-center justify-between rounded p-3" style={{
                  background: activeScenario === sc.id ? "oklch(0.75 0.18 75 / 0.08)" : "oklch(0.14 0.01 240)",
                  border: `1px solid ${activeScenario === sc.id ? "oklch(0.75 0.18 75 / 0.3)" : "oklch(0.20 0.01 240)"}`,
                }}>
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{sc.icon}</span>
                    <div>
                      <div className="font-mono font-bold text-xs text-foreground">{sc.label}</div>
                      <div className="text-[9px] text-muted-foreground">{sc.desc}</div>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setActiveScenario(sc.id);
                      handleRun(sc.params as Partial<Params>, sc.id);
                    }}
                    disabled={simulate.isPending && runningScenario === sc.id}
                    className="px-3 py-1.5 rounded font-mono text-xs font-bold transition-all flex-shrink-0"
                    style={{
                      background: runningScenario === sc.id && simulate.isPending ? "oklch(0.22 0.01 240)" : "oklch(0.75 0.18 75)",
                      color: runningScenario === sc.id && simulate.isPending ? "oklch(0.55 0.01 240)" : "oklch(0.10 0.01 240)",
                    }}>
                    {runningScenario === sc.id && simulate.isPending ? "⟳ Running…" : "▶ Run Scenario"}
                  </button>
                </div>
              ))}
            </div>
          </div>
          {result && activeScenario !== "default" && (
            <div className="rounded p-4" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.75 0.18 75 / 0.2)" }}>
              <div className="text-[10px] font-mono uppercase tracking-widest mb-3" style={{ color: "oklch(0.75 0.18 75)" }}>
                Scenario Result — {SCENARIOS.find(s => s.id === activeScenario)?.label}
              </div>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { label: "Revenue", value: m ? `${(m.totalRevenue / 1000).toFixed(1)}k €` : "—", color: "#4ade80" },
                  { label: "Guard Blocks", value: m?.agentBlockCount ?? 0, color: "#f87171" },
                  { label: "Compliance", value: `${((m?.x108ComplianceRate ?? 0) * 100).toFixed(0)}%`, color: "oklch(0.72 0.18 145)" },
                ].map(item => (
                  <div key={item.label} className="rounded p-3 text-center" style={{ background: "oklch(0.14 0.01 240)" }}>
                    <div className="font-mono font-bold text-base" style={{ color: item.color }}>{item.value}</div>
                    <div className="text-[9px] text-muted-foreground">{item.label}</div>
                  </div>
                ))}
              </div>
              {revenues.length > 0 && (
                <div className="mt-3" style={{ height: "80px" }}>
                  <MiniLineChart data={revenues} color="oklch(0.75 0.18 75)" fillColor="oklch(0.75 0.18 75)" />
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════════
          TAB: DECISION STREAM
      ══════════════════════════════════════════════════════════════════ */}
      {activeTab === "stream" && (
        <div className="flex flex-col gap-3">
          <div className="rounded p-4" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
            <div className="flex items-center justify-between mb-3">
              <div className="text-[10px] font-mono uppercase tracking-widest" style={{ color: "oklch(0.45 0.01 240)" }}>Decision Stream</div>
              <div className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-green-400" />
                <span className="text-[9px] font-mono text-green-400">LIVE</span>
              </div>
            </div>
            {streamEvents.length === 0 ? (
              <div className="text-[10px] text-muted-foreground font-mono text-center py-8">Run simulation to see decision stream</div>
            ) : (
              <div className="flex flex-col gap-0">
                <div className="grid grid-cols-6 gap-2 pb-2 mb-1 text-[9px] font-mono" style={{ color: "oklch(0.35 0.01 240)", borderBottom: "1px solid oklch(0.18 0.01 240)" }}>
                  <div>TIME</div>
                  <div>AGENT</div>
                  <div className="col-span-2">PROPOSAL</div>
                  <div>DECISION</div>
                  <div>PROOF</div>
                </div>
                {streamEvents.map(ev => (
                  <div key={ev.id} className="grid grid-cols-6 gap-2 py-1.5 text-[10px] font-mono" style={{ borderBottom: "1px solid oklch(0.14 0.01 240)" }}>
                    <div style={{ color: "oklch(0.40 0.01 240)" }}>{ev.time}</div>
                    <div className="text-foreground truncate">{ev.agent}</div>
                    <div className="col-span-2 truncate" style={{ color: "oklch(0.65 0.01 240)" }}>{ev.proposal}</div>
                    <div><DecisionBadge decision={ev.decision} /></div>
                    <div className="truncate" style={{ color: "oklch(0.72 0.18 145)" }}>{ev.proofHash}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
          {m && (
            <div className="grid grid-cols-4 gap-2">
              {[
                { label: "Total Events", value: allActions.length, color: "oklch(0.65 0.15 200)" },
                { label: "BLOCK", value: m.agentBlockCount ?? 0, color: "#f87171" },
                { label: "HOLD", value: m.agentHoldCount ?? 0, color: "oklch(0.75 0.18 75)" },
                { label: "ALLOW", value: allActions.length - (m.agentBlockCount ?? 0) - (m.agentHoldCount ?? 0), color: "#4ade80" },
              ].map(item => (
                <div key={item.label} className="rounded p-3 text-center" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
                  <div className="font-mono font-bold text-lg" style={{ color: item.color }}>{item.value}</div>
                  <div className="text-[9px] text-muted-foreground">{item.label}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── BLOC 4 : Pilotage ── */}
      <PilotagePanel
        domain="ecom"
        onRerun={() => handleRun()}
        onReset={() => setResult(null)}
        loading={simulate.isPending}
        pythonAvailable={result?.canonical?.trace_id ? true : result ? false : undefined}
        mode={result?.canonical?.trace_id ? "real" : result ? "fallback" : undefined}
        scenarioLabel={activeScenario !== "default" ? activeScenario : undefined}
      />
      {/* ── BLOC 5 : Projection futur ── */}
      <ProjectionPanel
        domain="ecom"
        horizon="7j"
        scenarios={m?.agentBlockCount > 0 ? [
          { label: "Optimisation des marges", probability: 0.50, outcome: "continuation", description: "Guard a bloqué les décisions risquées — marges protégées" },
          { label: "Pression concurrentielle", probability: 0.30, outcome: "degradation", description: "Concurrents non gouvernés agressifs" },
          { label: "Croissance organique", probability: 0.20, outcome: "recovery", description: "Conversion en hausse sur trafic organique" },
        ] : undefined}
      />

      {/* ─── SECTION CANONIQUE — 5 blocs ─── */}
      <div className="mt-8 border-t pt-6" style={{ borderColor: "oklch(0.20 0.01 240)" }}>
        <div className="text-[10px] font-mono uppercase tracking-widest mb-4" style={{ color: "oklch(0.40 0.01 240)" }}>Vue canonique — pipeline complet</div>
        <WorldPageTemplate
          domain="ecom"
          title="Ecom World — Vue Canonique"
          description="Pipeline complet : Situation → Constellation agentique → Agrégation → Souveraineté X-108 → Preuve"
          kpis={[
            { label: "Revenu total", value: m ? (m.totalRevenue ?? 0).toLocaleString("fr-FR") + " €" : "En attente", color: "oklch(0.72 0.18 145)" },
            { label: "CTR", value: m ? ((m.avgCTR ?? 0) * 100).toFixed(1) + "%" : "En attente", color: "oklch(0.65 0.18 240)" },
            { label: "Décisions bloquées", value: m ? String(m.agentBlockCount ?? 0) : "0", color: m?.agentBlockCount > 0 ? "oklch(0.65 0.25 25)" : "oklch(0.72 0.18 145)" },
            { label: "Marge nette", value: m ? ((m.netMargin ?? 0) * 100).toFixed(1) + "%" : "En attente", color: "oklch(0.72 0.18 45)" },
          ]}
          domainContentSlot={
            m ? (
              <div className="grid grid-cols-3 gap-3 text-[11px]">
                <div className="rounded p-2" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
                  <div className="text-muted-foreground mb-1">CVR moyen</div>
                  <div className="font-mono font-bold" style={{ color: "oklch(0.72 0.18 145)" }}>{((m.avgCVR ?? 0) * 100).toFixed(1)}%</div>
                </div>
                <div className="rounded p-2" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
                  <div className="text-muted-foreground mb-1">Conversions</div>
                  <div className="font-mono font-bold" style={{ color: "oklch(0.65 0.18 240)" }}>{m.totalConversions ?? 0}</div>
                </div>
                <div className="rounded p-2" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
                  <div className="text-muted-foreground mb-1">Dépenses pub</div>
                  <div className="font-mono font-bold" style={{ color: "oklch(0.72 0.18 45)" }}>{(m.totalAdSpend ?? 0).toLocaleString("fr-FR")} €</div>
                </div>
              </div>
            ) : undefined
          }
        />
      </div>
    </div>
  );
}
