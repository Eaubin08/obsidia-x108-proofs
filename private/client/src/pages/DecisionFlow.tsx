import React, { useState, useEffect, useCallback } from "react";
import { Link } from "wouter";
import { trpc } from "@/lib/trpc";

// ─── Types ────────────────────────────────────────────────────────────────────

type Domain = "trading" | "banking" | "ecom";
type Decision = "ALLOW" | "HOLD" | "BLOCK";

interface FlowStep {
  id: string;
  ts: string;
  stage: "market" | "agent" | "prediction" | "guard" | "temporal" | "decision" | "proof";
  label: string;
  detail: string;
  decision?: Decision;
  domain?: Domain;
}

// ─── Constants ────────────────────────────────────────────────────────────────

const STAGE_META: Record<FlowStep["stage"], { icon: string; color: string; bg: string; title: string; question: string }> = {
  market:     { icon: "🌍", color: "#60a5fa", bg: "rgba(96,165,250,0.10)",  title: "Market Context",    question: "Que se passe-t-il ?" },
  agent:      { icon: "🤖", color: "#a78bfa", bg: "rgba(167,139,250,0.10)", title: "Agent Analysis",    question: "Qui agit ?" },
  prediction: { icon: "📡", color: "#f59e0b", bg: "rgba(245,158,11,0.10)",  title: "Prediction Engine", question: "Que risque-t-il d'arriver ?" },
  guard:      { icon: "🛡",  color: "#34d399", bg: "rgba(52,211,153,0.10)",  title: "Guard X-108",       question: "Le seuil est-il respecté ?" },
  temporal:   { icon: "⏱",  color: "#94a3b8", bg: "rgba(148,163,184,0.10)", title: "Temporal Lock",     question: "Faut-il attendre ?" },
  decision:   { icon: "⚖️", color: "#a78bfa", bg: "rgba(167,139,250,0.10)", title: "Verdict",           question: "Que juge le Guard ?" },
  proof:      { icon: "🔐", color: "#34d399", bg: "rgba(52,211,153,0.10)",  title: "Proof Generated",   question: "Comment vérifier ?" },
};

const DECISION_META: Record<Decision, { color: string; bg: string; label: string; desc: string }> = {
  ALLOW: { color: "#4ade80", bg: "rgba(74,222,128,0.15)", label: "ALLOW",  desc: "Action exécutée immédiatement" },
  HOLD:  { color: "#fbbf24", bg: "rgba(251,191,36,0.15)",  label: "HOLD",   desc: "Action valide — en attente du temporal lock" },
  BLOCK: { color: "#f87171", bg: "rgba(248,113,113,0.15)", label: "BLOCK",  desc: "Action rejetée — risque ou incohérence détectée" },
};

const DOMAIN_META: Record<Domain, { color: string; icon: string; label: string }> = {
  trading: { color: "#3b82f6", icon: "📈", label: "Trading" },
  banking: { color: "#22c55e", icon: "🏦", label: "Banking" },
  ecom:    { color: "#a855f7", icon: "🛒", label: "E-Com" },
};

// ─── Glossary tooltip ─────────────────────────────────────────────────────────

const GLOSSARY: Record<string, string> = {
  "Guard X-108":    "Moteur de décision qui valide chaque action proposée par un agent. Il évalue la cohérence, le risque et les seuils.",
  "Temporal Lock":  "Période de refroidissement empêchant l'exécution d'actions irréversibles trop rapidement. Durée typique : 10 secondes.",
  "ALLOW":          "L'action est exécutée immédiatement. Le guard a validé tous les critères.",
  "HOLD":           "L'action est valide mais attend l'expiration du temporal lock avant d'être exécutée.",
  "BLOCK":          "L'action est rejetée. Le guard a détecté un risque ou une incohérence.",
  "Merkle Anchor":  "Empreinte cryptographique de la décision stockée dans un arbre de Merkle. Permet de prouver qu'une décision a eu lieu sans en révéler le contenu.",
  "Coherence":      "Score de cohérence de l'agent (0 à 1). Doit dépasser le seuil minimum pour que l'action soit autorisée.",
  "Confidence":     "Niveau de certitude de l'agent sur son signal (0 à 1). Plus il est élevé, plus le signal est fiable.",
};

function GlossaryTooltip({ term }: { term: string }) {
  const [open, setOpen] = useState(false);
  const def = GLOSSARY[term];
  if (!def) return <span className="font-bold">{term}</span>;
  return (
    <span className="relative inline-block">
      <button
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        className="font-bold underline decoration-dotted cursor-help"
        style={{ color: "oklch(0.72 0.18 145)" }}
      >
        {term}
      </button>
      {open && (
        <span
          className="absolute z-50 left-0 bottom-full mb-1 rounded px-3 py-2 text-xs font-mono shadow-lg"
          style={{
            background: "oklch(0.14 0.01 240)",
            border: "1px solid oklch(0.72 0.18 145 / 0.4)",
            color: "oklch(0.85 0.01 240)",
            minWidth: "240px",
            maxWidth: "320px",
            whiteSpace: "normal",
          }}
        >
          <span className="block font-bold mb-1" style={{ color: "oklch(0.72 0.18 145)" }}>{term}</span>
          {def}
        </span>
      )}
    </span>
  );
}

// ─── Simulated live flow generator ────────────────────────────────────────────

function generateFlow(domain: Domain, decision: Decision): FlowStep[] {
  const now = Date.now();
  const fmt = (offset: number) => new Date(now + offset).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  const domainLabel = DOMAIN_META[domain].label;

  const flows: FlowStep[] = [
    {
      id: "market",
      ts: fmt(0),
      stage: "market",
      label: domain === "trading" ? "BTC volatility spike detected" : domain === "banking" ? "Large transfer request €50k" : "Traffic surge +340% detected",
      detail: domain === "trading" ? "Volatility: 0.81 · Trend: downward · Volume: +220%" : domain === "banking" ? "Amount: €50,000 · Recipient: external · Fraud score: 0.12" : "Impressions: +340% · CVR: 0.04 · ROAS: 2.1",
      domain,
    },
    {
      id: "agent",
      ts: fmt(800),
      stage: "agent",
      label: domain === "trading" ? "Agent Alpha — Signal SELL" : domain === "banking" ? "Agent Sentinel — Signal ALLOW" : "Agent Mercury — Signal PROMOTE",
      detail: domain === "trading" ? "Confidence: 0.41 · Risk score: 0.73 · Strategy: momentum" : domain === "banking" ? "Confidence: 0.88 · Risk score: 0.12 · Strategy: compliance" : "Confidence: 0.67 · Risk score: 0.31 · Strategy: growth",
      domain,
    },
    {
      id: "prediction",
      ts: fmt(1200),
      stage: "prediction",
      label: domain === "trading" ? "Flash crash probability: 63%" : domain === "banking" ? "Fraud probability: 8%" : "Revenue uplift probability: 71%",
      detail: domain === "trading" ? "Window: 2–4h · Guard thresholds adjusted · High risk" : domain === "banking" ? "Window: immediate · Guard thresholds nominal · Low risk" : "Window: 24h · Guard thresholds nominal · Opportunity",
      domain,
    },
    {
      id: "guard",
      ts: fmt(1600),
      stage: "guard",
      label: `Guard X-108 — Coherence ${domain === "trading" ? "0.41 > 0.18 ✓" : domain === "banking" ? "0.88 > 0.18 ✓" : "0.67 > 0.18 ✓"}`,
      detail: `Threshold: 0.18 · Signal: ${domain === "trading" ? "0.41" : domain === "banking" ? "0.88" : "0.67"} · Consensus: 4/4 · ${decision === "BLOCK" ? "Risk exceeded — BLOCK" : "Criteria met"}`,
      domain,
    },
    {
      id: "temporal",
      ts: fmt(2000),
      stage: "temporal",
      label: decision === "ALLOW" ? "Temporal Lock expired — 10s elapsed" : decision === "HOLD" ? "Temporal Lock active — 10s remaining" : "Temporal Lock bypassed — BLOCK",
      detail: decision === "ALLOW" ? "Cooldown: 10s · Elapsed: 10s · Lock released" : decision === "HOLD" ? "Cooldown: 10s · Elapsed: 0s · Waiting..." : "Action rejected before lock — no wait required",
      domain,
    },
    {
      id: "decision",
      ts: fmt(2400),
      stage: "decision",
      label: `Decision: ${decision}`,
      detail: DECISION_META[decision].desc,
      decision,
      domain,
    },
    {
      id: "proof",
      ts: fmt(2800),
      stage: "proof",
      label: "Merkle Anchor generated",
      detail: `Root: a3f8c2d1...${Math.random().toString(16).slice(2, 10)} · Timestamp: ${fmt(2800)} · Domain: ${domainLabel} · Immutable`,
      domain,
    },
  ];

  return flows;
}

// ─── Flow card ────────────────────────────────────────────────────────────────

function FlowCard({ step, index, total, isActive }: { step: FlowStep; index: number; total: number; isActive: boolean }) {
  const meta = STAGE_META[step.stage];
  const decMeta = step.decision ? DECISION_META[step.decision] : null;

  return (
    <div className="flex gap-4">
      {/* Timeline line */}
      <div className="flex flex-col items-center" style={{ minWidth: "32px" }}>
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0"
          style={{
            background: isActive ? meta.bg : "oklch(0.12 0.01 240)",
            border: `2px solid ${isActive ? meta.color : "oklch(0.22 0.01 240)"}`,
            color: isActive ? meta.color : "oklch(0.40 0.01 240)",
          }}
        >
          {meta.icon}
        </div>
        {index < total - 1 && (
          <div className="w-px flex-1 mt-1" style={{ background: isActive ? `${meta.color}44` : "oklch(0.18 0.01 240)", minHeight: "24px" }} />
        )}
      </div>

      {/* Content */}
      <div
        className="flex-1 rounded p-3 mb-3"
        style={{
          background: isActive ? meta.bg : "oklch(0.10 0.01 240)",
          border: `1px solid ${isActive ? `${meta.color}44` : "oklch(0.16 0.01 240)"}`,
        }}
      >
        <div className="flex items-center justify-between mb-1">
          <div className="font-mono text-[9px] font-bold tracking-widest" style={{ color: isActive ? meta.color : "oklch(0.40 0.01 240)" }}>
            {meta.title.toUpperCase()}
          </div>
          <div className="font-mono text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>{step.ts}</div>
        </div>
        <div className="font-mono text-xs font-bold mb-1" style={{ color: isActive ? "oklch(0.90 0.01 240)" : "oklch(0.55 0.01 240)" }}>
          {step.label}
        </div>
        <div className="font-mono text-[10px]" style={{ color: "oklch(0.50 0.01 240)" }}>
          {step.detail}
        </div>
        {decMeta && (
          <div
            className="mt-2 inline-flex items-center gap-1.5 px-2 py-1 rounded font-mono text-xs font-bold"
            style={{ background: decMeta.bg, color: decMeta.color, border: `1px solid ${decMeta.color}44` }}
          >
            {step.decision === "ALLOW" ? "✅" : step.decision === "HOLD" ? "⏳" : "⛔"} {decMeta.label}
            <span className="font-normal text-[9px]">— {decMeta.desc}</span>
          </div>
        )}
        {step.stage === "guard" && (
          <div className="mt-1.5 font-mono text-[9px]" style={{ color: "oklch(0.45 0.01 240)" }}>
            <GlossaryTooltip term="Guard X-108" /> · <GlossaryTooltip term="Coherence" />
          </div>
        )}
        {step.stage === "temporal" && (
          <div className="mt-1.5 font-mono text-[9px]" style={{ color: "oklch(0.45 0.01 240)" }}>
            <GlossaryTooltip term="Temporal Lock" />
          </div>
        )}
        {step.stage === "proof" && (
          <div className="mt-1.5 font-mono text-[9px]" style={{ color: "oklch(0.45 0.01 240)" }}>
            <GlossaryTooltip term="Merkle Anchor" />
          </div>
        )}
        {step.stage === "agent" && (
          <div className="mt-1.5 font-mono text-[9px]" style={{ color: "oklch(0.45 0.01 240)" }}>
            <GlossaryTooltip term="Confidence" />
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function DecisionFlow() {
  const [domain, setDomain] = useState<Domain>("trading");
  const [decision, setDecision] = useState<Decision>("HOLD");
  const [flow, setFlow] = useState<FlowStep[]>(() => generateFlow("trading", "HOLD"));
  const [activeStep, setActiveStep] = useState(0);
  const [running, setRunning] = useState(false);
  const [autoPlay, setAutoPlay] = useState(false);

  // Fetch real decisions from trading history
  const tradingHistoryQuery = trpc.trading.history.useQuery(
    { limit: 3 },
    { refetchInterval: 10000, retry: false }
  );
  const bankHistoryQuery = trpc.bank.history.useQuery(
    { limit: 2 },
    { refetchInterval: 10000, retry: false }
  );

  const recentDecisions = [
    ...(tradingHistoryQuery.data ?? []).map((d) => ({ id: d.id, decision: d.decision, intentId: d.intentId, createdAt: d.createdAt instanceof Date ? d.createdAt.getTime() : Number(d.createdAt ?? 0), domain: "trading" })),
    ...(bankHistoryQuery.data ?? []).map((d) => ({ id: d.id, decision: d.decision, intentId: d.intentId, createdAt: d.createdAt instanceof Date ? d.createdAt.getTime() : Number(d.createdAt ?? 0), domain: "banking" })),
  ].slice(0, 5) as Array<{
    id: number;
    domain: string;
    decision: string;
    intentId?: string;
    createdAt?: number;
  }>;

  const regenerate = useCallback((d: Domain, dec: Decision) => {
    setFlow(generateFlow(d, dec));
    setActiveStep(0);
    setRunning(false);
  }, []);

  // Step-by-step animation
  useEffect(() => {
    if (!running) return;
    if (activeStep >= flow.length) { setRunning(false); return; }
    const t = setTimeout(() => setActiveStep(s => s + 1), 600);
    return () => clearTimeout(t);
  }, [running, activeStep, flow.length]);

  // Auto-play on domain/decision change
  useEffect(() => {
    if (autoPlay) {
      setRunning(true);
    }
  }, [flow, autoPlay]);

  const handleDomain = (d: Domain) => { setDomain(d); regenerate(d, decision); };
  const handleDecision = (dec: Decision) => { setDecision(dec); regenerate(domain, dec); };

  const domainMeta = DOMAIN_META[domain];

  return (
    <div className="max-w-5xl mx-auto py-6 px-4 flex flex-col gap-6">

      {/* Header */}
      {/* Institutional header */}
      <div className="rounded p-5" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.72 0.18 145 / 0.25)" }}>
        <div className="font-mono text-[9px] font-bold tracking-widest mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>
          OBSIDIA OS4 — GOVERNANCE ENGINE
        </div>
        <h1 className="font-mono text-2xl font-bold mb-2" style={{ color: "oklch(0.90 0.01 240)" }}>
          Decision Pipeline
        </h1>
        <p className="font-mono text-sm mb-4" style={{ color: "oklch(0.72 0.18 145)" }}>
          Obsidia verifies autonomous decisions before execution.
        </p>
        <p className="font-mono text-xs mb-4" style={{ color: "oklch(0.55 0.01 240)" }}>
          Every decision is evaluated, validated and cryptographically proven.
        </p>
        {/* Guard X-108 central role */}
        <div className="flex flex-wrap gap-4 items-start">
          <div className="flex-1 rounded p-3" style={{ background: "oklch(0.72 0.18 145 / 0.06)", border: "1px solid oklch(0.72 0.18 145 / 0.30)" }}>
            <div className="font-mono text-[9px] font-bold tracking-widest mb-1" style={{ color: "oklch(0.72 0.18 145)" }}>GUARD X-108 — THE JUDGE</div>
            <div className="font-mono text-xs" style={{ color: "oklch(0.75 0.01 240)" }}>
              Guard X-108 is the algorithmic tribunal at the heart of Obsidia. Every action proposed by an agent must pass through it before execution. It evaluates coherence, risk, and temporal constraints — then issues a <strong style={{color:"#a78bfa"}}>Verdict</strong>.
            </div>
          </div>
          <div className="flex flex-col gap-1 font-mono text-[10px]" style={{ minWidth: "160px" }}>
            {["Agents propose", "Guard X-108 evaluates", "Verdict issued", "Proof generated"].map((s, i) => (
              <div key={s} className="flex items-center gap-2">
                <span style={{ color: i === 1 ? "oklch(0.72 0.18 145)" : "oklch(0.40 0.01 240)" }}>{i === 1 ? "▶" : "·"}</span>
                <span style={{ color: i === 1 ? "oklch(0.72 0.18 145)" : "oklch(0.60 0.01 240)", fontWeight: i === 1 ? "bold" : "normal" }}>{s}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Pipeline summary bar */}
      <div className="flex items-center gap-1 flex-wrap rounded p-3" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
        {Object.entries(STAGE_META).map(([key, meta], i, arr) => (
          <React.Fragment key={key}>
            <div
              className="flex items-center gap-1 px-2 py-1 rounded font-mono text-[9px] font-bold"
              style={{
                background: activeStep > i ? meta.bg : "oklch(0.13 0.01 240)",
                color: activeStep > i ? meta.color : "oklch(0.35 0.01 240)",
                border: `1px solid ${activeStep > i ? `${meta.color}44` : "oklch(0.18 0.01 240)"}`,
              }}
            >
              <span>{meta.icon}</span>
              <span>{meta.title}</span>
            </div>
            {i < arr.length - 1 && (
              <span className="font-mono text-[9px]" style={{ color: "oklch(0.30 0.01 240)" }}>→</span>
            )}
          </React.Fragment>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

        {/* Left: controls */}
        <div className="flex flex-col gap-4">

          {/* Domain selector */}
          <div className="rounded p-4" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
            <div className="font-mono text-[9px] font-bold tracking-widest mb-3" style={{ color: "oklch(0.45 0.01 240)" }}>
              1 — CHOISIR UN MARCHÉ
            </div>
            <div className="flex flex-col gap-2">
              {(["trading", "banking", "ecom"] as Domain[]).map(d => {
                const dm = DOMAIN_META[d];
                return (
                  <button
                    key={d}
                    onClick={() => handleDomain(d)}
                    className="flex items-center gap-2 px-3 py-2.5 rounded font-mono text-xs font-bold text-left"
                    style={{
                      background: domain === d ? `${dm.color}18` : "oklch(0.09 0.01 240)",
                      border: `1px solid ${domain === d ? dm.color : "oklch(0.20 0.01 240)"}`,
                      color: domain === d ? dm.color : "oklch(0.55 0.01 240)",
                    }}
                  >
                    <span>{dm.icon}</span>
                    <div>
                      <div>{dm.label}</div>
                      <div className="font-normal text-[9px]" style={{ color: "oklch(0.45 0.01 240)" }}>
                        {d === "trading" ? "Agent Alpha · BTC/ETH" : d === "banking" ? "Agent Sentinel · Transfers" : "Agent Mercury · E-Commerce"}
                      </div>
                    </div>
                    {domain === d && <span className="ml-auto text-[9px]">●</span>}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Decision selector */}
          <div className="rounded p-4" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
            <div className="font-mono text-[9px] font-bold tracking-widest mb-3" style={{ color: "oklch(0.45 0.01 240)" }}>
              RÉSULTAT GUARD X-108
            </div>
            <div className="flex flex-col gap-2">
              {(["ALLOW", "HOLD", "BLOCK"] as Decision[]).map(dec => {
                const dm = DECISION_META[dec];
                return (
                  <button
                    key={dec}
                    onClick={() => handleDecision(dec)}
                    className="flex items-center gap-2 px-3 py-2 rounded font-mono text-xs font-bold text-left"
                    style={{
                      background: decision === dec ? dm.bg : "oklch(0.09 0.01 240)",
                      border: `1px solid ${decision === dec ? dm.color : "oklch(0.20 0.01 240)"}`,
                      color: decision === dec ? dm.color : "oklch(0.50 0.01 240)",
                    }}
                  >
                    <span>{dec === "ALLOW" ? "✅" : dec === "HOLD" ? "⏳" : "⛔"}</span>
                    <div>
                      <div>{dm.label}</div>
                      <div className="font-normal text-[9px]" style={{ color: "oklch(0.45 0.01 240)" }}>{dm.desc}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Play controls */}
          <div className="flex gap-2">
            <button
              onClick={() => { setActiveStep(0); setRunning(true); }}
              className="flex-1 py-2 rounded font-mono text-xs font-bold"
              style={{ background: "oklch(0.72 0.18 145 / 0.15)", border: "1px solid oklch(0.72 0.18 145 / 0.5)", color: "oklch(0.72 0.18 145)" }}
            >
              ▶ Rejouer
            </button>
            <button
              onClick={() => setAutoPlay(a => !a)}
              className="px-3 py-2 rounded font-mono text-[10px] font-bold"
              style={{
                background: autoPlay ? "oklch(0.60 0.12 200 / 0.15)" : "oklch(0.12 0.01 240)",
                border: `1px solid ${autoPlay ? "oklch(0.60 0.12 200 / 0.5)" : "oklch(0.22 0.01 240)"}`,
                color: autoPlay ? "oklch(0.60 0.12 200)" : "oklch(0.50 0.01 240)",
              }}
            >
              {autoPlay ? "⏸ Auto" : "⏵ Auto"}
            </button>
          </div>

          {/* Glossary */}
          <div className="rounded p-4" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
            <div className="font-mono text-[9px] font-bold tracking-widest mb-3" style={{ color: "oklch(0.45 0.01 240)" }}>
              GLOSSAIRE (survoler pour définition)
            </div>
            <div className="flex flex-col gap-1.5">
              {Object.keys(GLOSSARY).map(term => (
                <div key={term} className="font-mono text-[10px]">
                  <GlossaryTooltip term={term} />
                </div>
              ))}
            </div>
          </div>

          {/* Navigation links */}
          <div className="rounded p-3" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
            <div className="font-mono text-[9px] font-bold tracking-widest mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>EXPLORER LE PIPELINE</div>
            <div className="flex flex-col gap-1">
              {[
                { href: "/market", label: "1 · Market", color: "#60a5fa" },
                { href: "/agents", label: "2 · Agents", color: "#a78bfa" },
                { href: "/predictions", label: "3 · Anticipation", color: "#f59e0b" },
                { href: "/proof-center", label: "5 · Proof", color: "#34d399" },
                { href: "/control", label: "6 · Control", color: "#94a3b8" },
              ].map(item => (
                <Link key={item.href} href={item.href}>
                  <span className="block px-2 py-1 rounded font-mono text-[10px] font-bold" style={{ color: item.color }}>
                    {item.label} →
                  </span>
                </Link>
              ))}
            </div>
          </div>
        </div>

        {/* Right: flow timeline */}
        <div className="lg:col-span-2 flex flex-col gap-2">
          <div className="flex items-center justify-between mb-2">
            <div className="font-mono text-[9px] font-bold tracking-widest" style={{ color: "oklch(0.45 0.01 240)" }}>
              PIPELINE — {domainMeta.icon} {domainMeta.label.toUpperCase()} — VERDICT : {decision}
            </div>
            <div className="font-mono text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>
              Étape {Math.min(activeStep, flow.length)}/{flow.length}
            </div>
          </div>

          {flow.map((step, i) => (
            <FlowCard
              key={step.id}
              step={step}
              index={i}
              total={flow.length}
              isActive={i < activeStep}
            />
          ))}

          {activeStep >= flow.length && (
            <div
              className="rounded p-4 text-center font-mono text-sm font-bold mt-2"
              style={{ background: "oklch(0.72 0.18 145 / 0.10)", border: "1px solid oklch(0.72 0.18 145 / 0.4)", color: "oklch(0.72 0.18 145)" }}
            >
              ✓ Pipeline complet — Verdict {decision} · Preuve générée
            </div>
          )}
        </div>
      </div>

      {/* Live decisions from stream */}
      {recentDecisions.length > 0 && (
        <div className="rounded p-4" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
          <div className="font-mono text-[9px] font-bold tracking-widest mb-3" style={{ color: "oklch(0.45 0.01 240)" }}>
            DÉCISIONS RÉELLES — LIVE STREAM
          </div>
          <div className="flex flex-col gap-2">
            {recentDecisions.slice(0, 5).map((d) => {
              const dec = (d.decision?.toUpperCase() ?? "ALLOW") as Decision;
              const dom = (d.domain ?? "trading") as Domain;
              const decMeta = DECISION_META[dec] ?? DECISION_META.ALLOW;
              const domMeta = DOMAIN_META[dom] ?? DOMAIN_META.trading;
              return (
                <div key={d.id} className="flex items-center gap-3 font-mono text-xs">
                  <span style={{ color: domMeta.color }}>{domMeta.icon} {domMeta.label}</span>
                  <span
                    className="px-2 py-0.5 rounded font-bold"
                    style={{ background: decMeta.bg, color: decMeta.color, border: `1px solid ${decMeta.color}44` }}
                  >
                    {dec}
                  </span>
                  <span style={{ color: "oklch(0.45 0.01 240)" }} className="truncate flex-1">{d.intentId ? d.intentId.split(":").slice(0, 2).join(" · ") : `Décision #${d.id}`}</span>
                  <span style={{ color: "oklch(0.35 0.01 240)" }}>
                    {d.createdAt ? new Date(d.createdAt).toLocaleTimeString("fr-FR") : "—"}
                  </span>
                </div>
              );
            })}
          </div>
          <div className="mt-3">
            <Link href="/stream">
              <span className="font-mono text-[10px] font-bold" style={{ color: "oklch(0.72 0.18 145)" }}>
                Voir toutes les décisions →
              </span>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
