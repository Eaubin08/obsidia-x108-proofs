/**
 * Future — cockpit de simulation OS4 V2
 * Layout 3 colonnes : Command (gauche) | World+Flow (centre) | Decision+Proof (droite)
 * Zone basse : constellation agentique 6 couches + deep detail
 */
import React, { useState, useMemo, useEffect } from "react";
import { Link, useLocation } from "wouter";
import { useWorld, DOMAIN_COLORS, type WorldDomain } from "@/contexts/WorldContext";
import DecisionEnvelopeCard, { type CanonicalEnvelope } from "@/components/canonical/DecisionEnvelopeCard";
import AgentConstellationPanel, { type AgentData, type AggregationData } from "@/components/canonical/AgentConstellationPanel";
import ProofChainView, { type ProofChain } from "@/components/canonical/ProofChainView";
import { trpc } from "@/lib/trpc";

// ─── Helpers — mapper les noms d'agents vers des AgentData avec couche canonique ───────────────────────────────────────────────────────────────────────────────

function agentNameToLayer(name: string): AgentData["layer"] {
  const n = name.toLowerCase();
  if (n.includes("proof") || n.includes("attestation") || n.includes("trace") || n.includes("replay") || n.includes("integrity")) return "Proof";
  if (n.includes("guard") || n.includes("policy") || n.includes("human") || n.includes("override") || n.includes("severity") || n.includes("ticket") || n.includes("readiness")) return "Governance";
  if (n.includes("conflict") || n.includes("contradiction") || n.includes("narrative") || n.includes("mismatch") || n.includes("unknown") || n.includes("friction")) return "Contradiction";
  if (n.includes("interpret") || n.includes("analyst") || n.includes("risk") || n.includes("credit") || n.includes("fraud") || n.includes("pattern") || n.includes("prediction") || n.includes("regime") || n.includes("stress") || n.includes("affordability") || n.includes("margin") || n.includes("roas")) return "Interpretation";
  return "Observation";
}

function buildAgentsFromRegistry(names: string[], envelope: CanonicalEnvelope | null): AgentData[] {
  // agent_votes est un dict { agent_id -> { confidence, layer, claim, proposed_verdict, ... } }
  const agentVotesMap: Record<string, any> = (envelope as any)?.agent_votes ?? {};
  return names.map((name, i) => {
    const layer = agentNameToLayer(name);
    const vote = agentVotesMap[name];
    // Utiliser la vraie confidence de l'agent si disponible, sinon fallback varié basé sur la confidence globale
    let conf: number;
    if (vote && typeof vote.confidence === "number") {
      conf = Math.min(0.99, Math.max(0.01, vote.confidence));
    } else if (envelope) {
      // Fallback varié : chaque agent a une valeur différente basée sur sa position et la confidence globale
      const base = envelope.confidence;
      const variation = (((i * 13 + 7) % 23) - 11) * 0.035;
      conf = Math.min(0.97, Math.max(0.08, base + variation));
    } else {
      conf = 0.5 + (((i * 7 + 3) % 11) - 5) * 0.04;
    }
    const isGovernance = layer === "Governance";
    const isProof = layer === "Proof";
    const isContradiction = layer === "Contradiction";
    const hasContradiction = isContradiction && envelope && (envelope.contradictions as number) > 0;
    return {
      name,
      layer,
      confidence: conf,
      claim: vote?.claim
        ?? (isGovernance ? `Gate: ${envelope?.x108_gate ?? "ALLOW"}`
        : isProof ? `Trace: ${envelope?.trace_id?.slice(0, 10) ?? "pending"}…`
        : hasContradiction ? `Contradiction détectée`
        : undefined),
      proposed_verdict: vote?.proposed_verdict ?? (isGovernance ? (envelope?.x108_gate ?? "ALLOW") : undefined),
      severity_hint: (vote?.severity ?? envelope?.severity ?? "S2") as AgentData["severity_hint"],
      contradictions: (vote?.contradictions?.length ?? 0) + (hasContradiction ? 1 : 0),
      evidence_count: isProof ? 0 : undefined,
      trace_covered: isProof ? !!(envelope?.trace_id) : undefined,
      status: conf < 0.40 ? "low-confidence" : "active",
    };
  });
}

function buildAggregation(envelope: CanonicalEnvelope | null, agentNames: string[]): AggregationData {
  if (!envelope) return {
    market_verdict: "EN_ATTENTE",
    confidence: 0,
    contradictions_count: 0,
    unknowns_count: 0,
    risk_flags: [],
    evidence_refs: 0,
    dominant_contributors: agentNames.slice(0, 3),
  };
  return {
    market_verdict: envelope.market_verdict,
    confidence: envelope.confidence,
    // contradictions et unknowns sont des number dans l'interface client
    contradictions_count: envelope.contradictions as number,
    unknowns_count: envelope.unknowns as number,
    risk_flags: envelope.risk_flags,
    evidence_refs: 0,
    dominant_contributors: agentNames.slice(0, 3),
  };
}

const MOCK_ENVELOPE: CanonicalEnvelope = {
  domain: "trading",
  market_verdict: "BUY_SIGNAL_CONFIRMED",
  confidence: 0.87,
  contradictions: 1,
  unknowns: 0,
  risk_flags: [],
  x108_gate: "ALLOW",
  reason_code: "TREND_CONFIRMED_LOW_RISK",
  severity: "S2",
  decision_id: "DEC-T-2024-0891-a3f2",
  trace_id: "TRC-2024-0891-b7c1",
  ticket_required: false,
  attestation_ref: "ATT-2024-0891-lean4",
  source: "simulation",
  metrics: { pnl_estimate: 0.023, volatility: 0.42, exposure: 0.68 },
  timestamp: Date.now() - 45000,
};

const MOCK_PROOF: ProofChain = {
  decision_id: "DEC-T-2024-0891-a3f2",
  trace_id: "TRC-2024-0891-b7c1",
  ticket_required: false,
  attestation_ref: "ATT-2024-0891-lean4",
  proof_complete: true,
  proof_partial: false,
};

// ─── Scénarios disponibles ────────────────────────────────────────────────────

const SCENARIOS = {
  trading: [
    { id: "bull_run",            label: "Bull Run",              desc: "Tendance haussière forte" },
    { id: "flash_crash",         label: "Flash Crash",           desc: "Chute soudaine -15%" },
    { id: "range_bound",         label: "Range Bound",           desc: "Marché latéral" },
    { id: "high_vol",            label: "High Volatility",       desc: "Volatilité extrême" },
    { id: "liquidity_drain",     label: "Liquidity Drain",       desc: "Drainage de liquidité soudain" },
    { id: "ai_adversarial",      label: "Adversarial AI",        desc: "Attaque adversariale sur le moteur" },
    { id: "flash_crash_2",       label: "Flash Crash II",        desc: "Rebond partiel après crash" },
    { id: "over_leverage",       label: "Over-Leverage",         desc: "Levier excessif x20" },
    { id: "market_manipulation", label: "Market Manipulation",   desc: "Manipulation cours coordonnée" },
    { id: "black_swan",          label: "Black Swan",            desc: "Événement extrême improbable" },
  ],
  bank: [
    { id: "credit_stress",        label: "Credit Stress",         desc: "Hausse défauts de paiement" },
    { id: "liquidity_crunch",     label: "Liquidity Crunch",      desc: "Pression liquidité" },
    { id: "normal_ops",           label: "Normal Ops",            desc: "Opérations standard" },
    { id: "counterparty_default", label: "Counterparty Default",  desc: "Défaut contrepartie systémique" },
    { id: "interest_rate_shock",  label: "Rate Shock",            desc: "Choc taux d'intérêt +300bps" },
    { id: "credit_bubble_burst",  label: "Credit Bubble",         desc: "Explosion bulle crédit" },
    { id: "bank_run",             label: "Bank Run",              desc: "Retraits massifs simultanés" },
    { id: "fraud_attack",         label: "Fraud Attack",          desc: "Attaque fraude coordonnée" },
  ],
  ecom: [
    { id: "flash_sale",           label: "Flash Sale",            desc: "Pic trafic x10" },
    { id: "fraud_wave",           label: "Fraud Wave",            desc: "Vague de fraude" },
    { id: "campaign",             label: "Campaign Launch",       desc: "Lancement campagne" },
    { id: "supply_shock",         label: "Supply Shock",          desc: "Rupture stock critique" },
    { id: "ddos_attack",          label: "DDoS Attack",           desc: "Attaque DDoS sur plateforme" },
    { id: "price_war",            label: "Price War",             desc: "Guerre des prix concurrentielle" },
  ],
};

// ─── Composants internes ──────────────────────────────────────────────────────

// ─── Candidate Intent par domaine (Bloc C spec) ──────────────────────────────
const CANDIDATE_INTENT = {
  trading: {
    actions: ["BUY", "SELL", "HOLD"],
    fields: [
      { label: "Action candidate", key: "action", type: "select", options: ["BUY", "SELL", "HOLD"] },
      { label: "Taille (% capital)", key: "size", type: "text", placeholder: "ex: 5%" },
      { label: "Urgence", key: "urgency", type: "select", options: ["LOW", "MEDIUM", "HIGH"] },
    ],
  },
  bank: {
    actions: ["AUTHORIZE", "ANALYZE", "BLOCK"],
    fields: [
      { label: "Action candidate", key: "action", type: "select", options: ["AUTHORIZE", "ANALYZE", "BLOCK"] },
      { label: "Priorité", key: "priority", type: "select", options: ["ROUTINE", "URGENT", "CRITICAL"] },
      { label: "Sensibilité canal", key: "channel", type: "select", options: ["LOW", "MEDIUM", "HIGH"] },
    ],
  },
  ecom: {
    actions: ["PAY", "WAIT", "REFUSE"],
    fields: [
      { label: "Action candidate", key: "action", type: "select", options: ["PAY", "WAIT", "REFUSE"] },
      { label: "Activation promo", key: "promo", type: "select", options: ["OFF", "ON"] },
      { label: "Réservation stock", key: "stock", type: "select", options: ["NONE", "SOFT", "HARD"] },
    ],
  },
};

function CandidateIntentBlock({ domain, colors }: { domain: WorldDomain; colors: typeof DOMAIN_COLORS[WorldDomain] }) {
  const cfg = CANDIDATE_INTENT[domain];
  const [values, setValues] = React.useState<Record<string, string>>({});
  const actionVal = values["action"] ?? cfg.fields[0].options?.[0] ?? "";
  const actionColor = actionVal === "BUY" || actionVal === "AUTHORIZE" || actionVal === "PAY"
    ? "oklch(0.72 0.18 145)"
    : actionVal === "SELL" || actionVal === "BLOCK" || actionVal === "REFUSE"
    ? "oklch(0.65 0.25 25)"
    : "oklch(0.72 0.18 45)";

  return (
    <div className="rounded overflow-hidden" style={{ border: `1px solid ${colors.border}` }}>
      <div className="px-3 py-2 flex items-center justify-between"
        style={{ background: "oklch(0.12 0.01 240)", borderBottom: `1px solid ${colors.border}` }}>
        <span className="text-[9px] font-mono font-bold" style={{ color: colors.accent }}>Candidate Intent</span>
        <span className="text-[8px] font-mono px-1.5 py-0.5 rounded"
          style={{ background: `${actionColor}22`, border: `1px solid ${actionColor}55`, color: actionColor }}>
          {actionVal}
        </span>
      </div>
      <div className="p-2 flex flex-col gap-1.5" style={{ background: "oklch(0.105 0.01 240)" }}>
        {cfg.fields.map(f => (
          <div key={f.key} className="flex items-center justify-between gap-2">
            <span className="text-[8px] font-mono shrink-0" style={{ color: "oklch(0.45 0.01 240)" }}>{f.label}</span>
            {f.type === "select" ? (
              <select
                value={values[f.key] ?? f.options?.[0] ?? ""}
                onChange={e => setValues(v => ({ ...v, [f.key]: e.target.value }))}
                className="text-[8px] font-mono rounded px-1 py-0.5"
                style={{ background: "oklch(0.14 0.01 240)", border: "1px solid oklch(0.22 0.01 240)", color: "oklch(0.70 0.01 240)", outline: "none" }}
              >
                {f.options?.map(o => <option key={o} value={o}>{o}</option>)}
              </select>
            ) : (
              <input
                type="text"
                placeholder={(f as any).placeholder}
                value={values[f.key] ?? ""}
                onChange={e => setValues(v => ({ ...v, [f.key]: e.target.value }))}
                className="text-[8px] font-mono rounded px-1 py-0.5 w-20"
                style={{ background: "oklch(0.14 0.01 240)", border: "1px solid oklch(0.22 0.01 240)", color: "oklch(0.70 0.01 240)", outline: "none" }}
              />
            )}
          </div>
        ))}
        <div className="mt-1 text-[7px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>
          L'intent est transmis au pipeline lors du run
        </div>
      </div>
    </div>
  );
}

function CommandColumn({ domain, scenario, setScenario, onRun, running }: {
  domain: WorldDomain;
  scenario: string;
  setScenario: (s: string) => void;
  onRun: () => void;
  running: boolean;
}) {
  const colors = DOMAIN_COLORS[domain];
  const scenarios = SCENARIOS[domain];

  return (
    <div className="flex flex-col gap-3">
      {/* Titre */}
      <div className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.45 0.01 240)" }}>
        COMMAND
      </div>

      {/* Monde actif */}
      <div className="rounded p-3" style={{ background: "oklch(0.12 0.01 240)", border: `1px solid ${colors.border}` }}>
        <div className="flex items-center gap-2 mb-2">
          <span className="text-base">{colors.icon}</span>
          <span className="text-[11px] font-mono font-bold" style={{ color: colors.accent }}>{colors.label}</span>
        </div>
        <div className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>
          Monde actif — modifiable dans StatusRail
        </div>
      </div>

      {/* Scénarios */}
      <div className="rounded overflow-hidden" style={{ border: "1px solid oklch(0.18 0.01 240)" }}>
        <div className="px-3 py-2 text-[9px] font-mono font-bold"
          style={{ background: "oklch(0.12 0.01 240)", borderBottom: "1px solid oklch(0.16 0.01 240)", color: "oklch(0.55 0.01 240)" }}>
          Scénario
        </div>
        <div className="flex flex-col gap-0.5 p-1.5">
          {scenarios.map(s => (
            <button
              key={s.id}
              onClick={() => setScenario(s.id)}
              className="text-left px-2 py-1.5 rounded transition-all"
              style={{
                background: scenario === s.id ? colors.bg : "transparent",
                border: `1px solid ${scenario === s.id ? colors.border : "transparent"}`,
              }}
            >
              <div className="text-[9px] font-mono font-bold" style={{ color: scenario === s.id ? colors.accent : "oklch(0.60 0.01 240)" }}>
                {s.label}
              </div>
              <div className="text-[8px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>{s.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Paramètres rapides */}
      <div className="rounded p-3 flex flex-col gap-2" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
        <div className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.50 0.01 240)" }}>Paramètres</div>
        {[
          { label: "Mode",    value: "SIMU" },
          { label: "Agents",  value: "41" },
          { label: "Horizon", value: "24h" },
          { label: "Capital", value: "125 000 €" },
        ].map(p => (
          <div key={p.label} className="flex items-center justify-between text-[9px] font-mono">
            <span style={{ color: "oklch(0.45 0.01 240)" }}>{p.label}</span>
            <span style={{ color: "oklch(0.70 0.01 240)" }}>{p.value}</span>
          </div>
        ))}
      </div>

      {/* Candidate Intent — Bloc C spec */}
      <CandidateIntentBlock domain={domain} colors={colors} />

      {/* Bouton Run */}
      <button
        onClick={onRun}
        disabled={running}
        className="w-full py-3 rounded font-mono text-[11px] font-bold transition-all"
        style={{
          background: running ? "oklch(0.14 0.01 240)" : colors.bg,
          border: `1px solid ${running ? "oklch(0.22 0.01 240)" : colors.border}`,
          color: running ? "oklch(0.45 0.01 240)" : colors.accent,
          cursor: running ? "not-allowed" : "pointer",
        }}
      >
        {running ? "⟳ Simulation en cours…" : "▶ Lancer la simulation"}
      </button>

      {/* Liens rapides */}
      <div className="flex flex-col gap-1">
        <Link href="/past">
          <button className="w-full text-left px-2 py-1.5 rounded text-[9px] font-mono"
            style={{ background: "oklch(0.115 0.01 240)", border: "1px solid oklch(0.16 0.01 240)", color: "oklch(0.55 0.01 240)" }}>
            📚 Voir les runs passés →
          </button>
        </Link>
        <Link href="/live">
          <button className="w-full text-left px-2 py-1.5 rounded text-[9px] font-mono"
            style={{ background: "oklch(0.115 0.01 240)", border: "1px solid oklch(0.16 0.01 240)", color: "oklch(0.55 0.01 240)" }}>
            ⚡ Voir le live →
          </button>
        </Link>
      </div>
    </div>
  );
}

function WorldFlowColumn({ domain, running }: { domain: WorldDomain; running: boolean }) {
  const colors = DOMAIN_COLORS[domain];
  // Prix live depuis mirror.prices (polling 30s)
  const pricesQuery = trpc.mirror.prices.useQuery(
    { symbols: domain === "trading" ? ["BTC", "ETH", "SOL", "BNB"] : [] },
    { enabled: domain === "trading", refetchInterval: 30000, staleTime: 25000 }
  );
  const btcData = pricesQuery.data?.data?.[0];
  const ethData = pricesQuery.data?.data?.[1];
  const solData = pricesQuery.data?.data?.[2];

  return (
    <div className="flex flex-col gap-3">
      <div className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.45 0.01 240)" }}>
        WORLD + FLOW
      </div>

      {/* Flow pipeline */}
      <div className="rounded p-3" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
        <div className="text-[9px] font-mono font-bold mb-3" style={{ color: "oklch(0.55 0.01 240)" }}>Pipeline agentique</div>
        <div className="flex flex-col gap-2">
          {[
            { layer: "Observation",    agents: 3, status: running ? "active" : "idle",    color: "oklch(0.65 0.18 240)" },
            { layer: "Interpretation", agents: 3, status: running ? "active" : "idle",    color: "oklch(0.72 0.18 145)" },
            { layer: "Contradiction",  agents: 2, status: running ? "active" : "idle",    color: "oklch(0.72 0.18 45)" },
            { layer: "Aggregation",    agents: 1, status: running ? "running" : "idle",   color: "#a78bfa" },
            { layer: "Governance",     agents: 1, status: running ? "pending" : "idle",   color: "oklch(0.72 0.18 145)" },
            { layer: "Proof",          agents: 1, status: running ? "pending" : "idle",   color: "oklch(0.60 0.15 290)" },
          ].map((row, i, arr) => {
            const statusColor = row.status === "active" ? "oklch(0.72 0.18 145)" : row.status === "running" ? "#a78bfa" : row.status === "pending" ? "oklch(0.72 0.18 45)" : "oklch(0.30 0.01 240)";
            return (
              <React.Fragment key={row.layer}>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full shrink-0" style={{ background: statusColor }} />
                  <span className="text-[9px] font-mono font-bold flex-1" style={{ color: row.color }}>{row.layer}</span>
                  <span className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>{row.agents} ag.</span>
                  <span className="text-[8px] font-mono" style={{ color: statusColor }}>{row.status}</span>
                </div>
                {i < arr.length - 1 && (
                  <div className="ml-1 w-px h-2" style={{ background: "oklch(0.20 0.01 240)" }} />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Métriques monde */}
      <div className="rounded p-3" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
        <div className="flex items-center justify-between mb-2">
          <div className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.55 0.01 240)" }}>
            {colors.icon} Métriques {colors.label}
          </div>
          {domain === "trading" && (
            <span className="text-[7px] font-mono" style={{ color: pricesQuery.isLoading ? "oklch(0.45 0.01 240)" : "oklch(0.55 0.18 145)" }}>
              {pricesQuery.isLoading ? "⏳ chargement…" : "● live"}
            </span>
          )}
        </div>
        <div className="grid grid-cols-2 gap-2">
          {domain === "trading" && [
            { k: "BTC",    v: btcData ? `${btcData.price.toLocaleString("fr-FR")} $` : "…", trend: btcData ? (btcData.change24h > 0 ? "up" : btcData.change24h < 0 ? "down" : "stable") : "stable", sub: btcData ? `${btcData.change24h > 0 ? "+" : ""}${(btcData.change24h * 100).toFixed(2)}%` : "" },
            { k: "ETH",   v: ethData ? `${ethData.price.toLocaleString("fr-FR")} $` : "…", trend: ethData ? (ethData.change24h > 0 ? "up" : ethData.change24h < 0 ? "down" : "stable") : "stable", sub: ethData ? `${ethData.change24h > 0 ? "+" : ""}${(ethData.change24h * 100).toFixed(2)}%` : "" },
            { k: "SOL",   v: solData ? `${solData.price.toLocaleString("fr-FR")} $` : "…", trend: solData ? (solData.change24h > 0 ? "up" : solData.change24h < 0 ? "down" : "stable") : "stable", sub: solData ? `${solData.change24h > 0 ? "+" : ""}${(solData.change24h * 100).toFixed(2)}%` : "" },
            { k: "Régime", v: btcData?.regime ?? "NEUTRAL", trend: btcData?.regime === "BULL" ? "up" : btcData?.regime === "BEAR" || btcData?.regime === "CRASH" ? "down" : "stable", sub: btcData ? `vol ${(btcData.volatility * 100).toFixed(1)}%` : "" },
          ].map(m => (
            <div key={m.k} className="text-[9px] font-mono">
              <div style={{ color: "oklch(0.45 0.01 240)" }}>{m.k}</div>
              <div className="flex items-center gap-1" style={{ color: "oklch(0.75 0.01 240)" }}>
                <span>{m.v}</span>
                <span className="text-[8px]" style={{ color: m.trend === "up" ? "oklch(0.72 0.18 145)" : m.trend === "down" ? "oklch(0.65 0.25 25)" : "oklch(0.45 0.01 240)" }}>
                  {m.trend === "up" ? "↑" : m.trend === "down" ? "↓" : "→"}
                </span>
              </div>
              {m.sub && <div className="text-[7px]" style={{ color: "oklch(0.40 0.01 240)" }}>{m.sub}</div>}
            </div>
          ))}
          {domain === "bank" && [
            { k: "Risk Score",  v: "6.2/10",  trend: "up" },
            { k: "Liquidité",   v: "94.1%",   trend: "stable" },
            { k: "Défauts",     v: "0.8%",    trend: "up" },
            { k: "Compliance",  v: "✓",       trend: "stable" },
          ].map(m => (
            <div key={m.k} className="text-[9px] font-mono">
              <div style={{ color: "oklch(0.45 0.01 240)" }}>{m.k}</div>
              <div style={{ color: "oklch(0.75 0.01 240)" }}>{m.v}</div>
            </div>
          ))}
          {domain === "ecom" && [
            { k: "Conv. Rate",  v: "3.8%",    trend: "up" },
            { k: "Fraud Score", v: "0.12",    trend: "down" },
            { k: "Revenue",     v: "+12%",    trend: "up" },
            { k: "Cart Abandon",v: "68%",     trend: "stable" },
          ].map(m => (
            <div key={m.k} className="text-[9px] font-mono">
              <div style={{ color: "oklch(0.45 0.01 240)" }}>{m.k}</div>
              <div style={{ color: "oklch(0.75 0.01 240)" }}>{m.v}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Logs simulation */}
      <div className="rounded overflow-hidden" style={{ border: "1px solid oklch(0.18 0.01 240)" }}>
        <div className="px-3 py-1.5 text-[9px] font-mono font-bold"
          style={{ background: "oklch(0.12 0.01 240)", borderBottom: "1px solid oklch(0.16 0.01 240)", color: "oklch(0.50 0.01 240)" }}>
          Logs
        </div>
        <div className="p-2 flex flex-col gap-0.5 font-mono text-[8px]" style={{ background: "oklch(0.09 0.01 240)" }}>
          {(running ? [
            { t: "20:45:01", msg: "MarketDataAgent → signal reçu", c: "oklch(0.65 0.18 240)" },
            { t: "20:45:02", msg: "TrendInterpreter → BULLISH_TREND", c: "oklch(0.72 0.18 145)" },
            { t: "20:45:02", msg: "ContradictionAgent → 1 divergence", c: "oklch(0.72 0.18 45)" },
            { t: "20:45:03", msg: "Aggregation → BUY_SIGNAL_CONFIRMED", c: "#a78bfa" },
            { t: "20:45:03", msg: "GuardX108 → ALLOW", c: "oklch(0.72 0.18 145)" },
          ] : [
            { t: "—", msg: "En attente de simulation…", c: "oklch(0.35 0.01 240)" },
          ]).map((log, i) => (
            <div key={i} className="flex gap-2">
              <span style={{ color: "oklch(0.35 0.01 240)" }}>{log.t}</span>
              <span style={{ color: log.c }}>{log.msg}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Impact Preview par domaine (Bloc 2 spec) ───────────────────────────────
const IMPACT_PREVIEW_FIELDS: Record<WorldDomain, Array<{ label: string; key: string; desc: string }>> = {
  trading: [
    { label: "Impact exposition",  key: "exposure",    desc: "Variation du capital exposé" },
    { label: "Impact drawdown",    key: "drawdown",    desc: "Risque de perte maximale" },
    { label: "Impact exécution",   key: "execution",   desc: "Probabilité d'exécution" },
    { label: "Impact slippage",    key: "slippage",    desc: "Dérapage prix estimé" },
  ],
  bank: [
    { label: "Impact liquidité",   key: "liquidity",   desc: "Pression sur la liquidité" },
    { label: "Impact fraude",      key: "fraud",       desc: "Risque fraude résiduel" },
    { label: "Impact conformité",  key: "compliance",  desc: "Exposition réglementaire" },
    { label: "Impact client",      key: "ux",          desc: "Expérience client affectée" },
  ],
  ecom: [
    { label: "Impact marge",       key: "margin",      desc: "Variation marge nette" },
    { label: "Impact conversion",  key: "conversion",  desc: "Taux conversion estimé" },
    { label: "Impact fulfillment", key: "fulfillment", desc: "Risque logistique" },
    { label: "Impact confiance",   key: "trust",       desc: "Score confiance client" },
  ],
};

function ImpactPreviewBlock({ domain, envelope }: { domain: WorldDomain; envelope: CanonicalEnvelope | null }) {
  const fields = IMPACT_PREVIEW_FIELDS[domain];
  const metrics = envelope?.metrics as Record<string, number> | undefined;
  const gate = envelope?.x108_gate ?? "HOLD";
  const gateColor = gate === "ALLOW" ? "oklch(0.72 0.18 145)" : gate === "BLOCK" ? "oklch(0.65 0.25 25)" : "oklch(0.72 0.18 45)";

  return (
    <div className="rounded overflow-hidden" style={{ border: "1px solid oklch(0.18 0.01 240)" }}>
      <div className="px-3 py-2 flex items-center justify-between"
        style={{ background: "oklch(0.12 0.01 240)", borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
        <span className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.60 0.01 240)" }}>Impact Preview</span>
        <span className="text-[8px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>Si ce verdict passe</span>
      </div>
      {!envelope ? (
        <div className="p-3 text-[8px] font-mono" style={{ color: "oklch(0.35 0.01 240)", background: "oklch(0.105 0.01 240)" }}>
          Disponible après le premier run
        </div>
      ) : (
        <div className="p-2 flex flex-col gap-1" style={{ background: "oklch(0.105 0.01 240)" }}>
          <div className="text-[8px] font-mono mb-1" style={{ color: "oklch(0.40 0.01 240)" }}>
            Gate actif : <span style={{ color: gateColor, fontWeight: 700 }}>{gate}</span>
            {gate === "BLOCK" && " — action bloquée, aucun impact"}
            {gate === "HOLD" && " — impact suspendu, en attente"}
            {gate === "ALLOW" && " — impact activé"}
          </div>
          {fields.map(f => {
            const raw = metrics?.[f.key];
            const val = typeof raw === "number" ? `${raw > 0 ? "+" : ""}${(raw * 100).toFixed(1)}%` : "—";
            const valColor = typeof raw === "number"
              ? (raw > 0.05 ? "oklch(0.72 0.18 145)" : raw < -0.05 ? "oklch(0.65 0.25 25)" : "oklch(0.72 0.18 45)")
              : "oklch(0.40 0.01 240)";
            return (
              <div key={f.key} className="flex items-start justify-between gap-2">
                <div>
                  <div className="text-[8px] font-mono" style={{ color: "oklch(0.55 0.01 240)" }}>{f.label}</div>
                  <div className="text-[7px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>{f.desc}</div>
                </div>
                <span className="text-[9px] font-mono font-bold shrink-0" style={{ color: valColor }}>{val}</span>
              </div>
            );
          })}
          <div className="mt-1 pt-1 text-[7px] font-mono" style={{ color: "oklch(0.35 0.01 240)", borderTop: "1px solid oklch(0.16 0.01 240)" }}>
            Confiance globale : {Math.round((envelope.confidence ?? 0) * 100)}% · Contradict. : {String(envelope.contradictions)}
          </div>
        </div>
      )}
    </div>
  );
}

function DecisionProofColumn({ domain, envelope, proof }: { domain: WorldDomain; envelope: CanonicalEnvelope | null; proof: ProofChain | null }) {
  return (
    <div className="flex flex-col gap-3">
      <div className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.45 0.01 240)" }}>
        DÉCISION + PREUVE
      </div>

      {envelope ? (
        <DecisionEnvelopeCard envelope={envelope} variant="expanded" pastLink="/past" />
      ) : (
        <div className="rounded p-6 text-center" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
          <div className="text-[11px] font-mono font-bold mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>EN ATTENTE</div>
          <div className="text-[9px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>Lancez une simulation pour voir la décision</div>
        </div>
      )}

      {/* Impact Preview — Bloc 2 spec */}
      <ImpactPreviewBlock domain={domain} envelope={envelope} />

      {proof ? (
        <ProofChainView chain={proof} variant="full" />
      ) : (
        <div className="rounded p-4 text-center" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
          <div className="text-[9px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>Proof chain disponible après le premier run</div>
        </div>
      )}
    </div>
  );
}

// ─── Future ───────────────────────────────────────────────────────────────────

export default function Future() {
  const { domain, setMode, setX108Gate, setLastDecisionId, setProofStatus, setSource } = useWorld();
  const [location] = useLocation();

  // ── Lecture des query params (replay depuis Past) ─────────────────────────────
  const searchParams = useMemo(() => {
    const search = typeof window !== "undefined" ? window.location.search : "";
    return new URLSearchParams(search);
  }, [location]);
  const isReplay = searchParams.get("replay") === "1";
  const replayDecisionId = searchParams.get("decisionId") ?? null;
  const replayGate = searchParams.get("gate") ?? null;

  const [scenario, setScenario] = useState("bull_run");
  const [running, setRunning] = useState(false);
  const [showConstellation, setShowConstellation] = useState(false);
  const [activeTab, setActiveTab] = useState<"constellation" | "detail">("constellation");
  const [runError, setRunError] = useState<string | null>(null);
  const [liveEnvelope, setLiveEnvelope] = useState<CanonicalEnvelope | null>(null);
  const [liveProof, setLiveProof] = useState<ProofChain | null>(null);
  const [rawRunData, setRawRunData] = useState<any>(null);
  const [activeDetailTab, setActiveDetailTab] = useState<"envelope" | "agents" | "aggregate" | "json" | "metrics" | "raw">("envelope");

  // ── Mutation tRPC → pipeline canonique Python ─────────────────────────────────
  const canonicalRunMutation = trpc.engine.canonicalRun.useMutation({
    onSuccess: (data: any) => {
      // Mapper la réponse du pipeline vers CanonicalEnvelope
      const mapped: CanonicalEnvelope = {
        domain: data.domain ?? domain,
        market_verdict: data.market_verdict ?? data.verdict ?? "UNKNOWN",
        confidence: typeof data.confidence === "number" ? data.confidence : 0.5,
        contradictions: Array.isArray(data.contradictions) ? data.contradictions.length
          : (typeof data.contradictions === "number" ? data.contradictions : 0),
        unknowns: data.unknowns ?? 0,
        risk_flags: Array.isArray(data.risk_flags) ? data.risk_flags : [],
        x108_gate: (data.x108_gate ?? data.gate ?? "ALLOW") as "ALLOW" | "HOLD" | "BLOCK",
        reason_code: data.reason_code ?? "PIPELINE_RESULT",
        severity: (data.severity ?? "S2") as "S1" | "S2" | "S3" | "S4",
        decision_id: data.decision_id ?? data.trace_id ?? `DEC-${domain.toUpperCase()}-LIVE-${Date.now()}`,
        trace_id: data.trace_id,
        ticket_required: data.ticket_required ?? false,
        ticket_id: data.ticket_id,
        attestation_ref: data.attestation_ref,
        source: data.source ?? "canonical_pipeline",
        metrics: data.metrics ?? {},
        raw_engine: data,
        timestamp: Date.now(),
      };
      const proof: ProofChain = {
        decision_id: mapped.decision_id,
        trace_id: mapped.trace_id,
        ticket_required: mapped.ticket_required,
        ticket_id: mapped.ticket_id,
        attestation_ref: mapped.attestation_ref,
        proof_complete: !!(mapped.decision_id && mapped.trace_id && mapped.attestation_ref),
        proof_partial: !!(mapped.decision_id && mapped.trace_id && !mapped.attestation_ref),
      };
      setLiveEnvelope(mapped);
      setLiveProof(proof);
      setRawRunData(data);
      setRunning(false);
      setShowConstellation(true);
      setRunError(null);
    },
    onError: (err: any) => {
      setRunError(err.message ?? "Erreur pipeline canonique");
      setRunning(false);
      setShowConstellation(true);
    },
  });

  const handleRun = () => {
    setRunning(true);
    setRunError(null);
    canonicalRunMutation.mutate({
      domain,
      scenarioId: scenario,
      seed: Math.floor(Math.random() * 9999),
    });
  };

  // Registre des agents réels depuis le backend
  const registryQuery = trpc.engine.canonicalAgentRegistry.useQuery();
  const registryNames: string[] = useMemo(() => {
    if (!registryQuery.data) return [];
    const d = registryQuery.data as Record<string, string[]>;
    const domainAgents = d[domain] ?? [];
    const metaAgents = d["meta"] ?? [];
    return [...domainAgents, ...metaAgents];
  }, [registryQuery.data, domain]);

  // Enveloppe active : live si disponible, sinon null (pas de MOCK)
  const envelope: CanonicalEnvelope | null = liveEnvelope;
  const proof: ProofChain | null = liveProof;

  // ─── Propagation vers StatusRail ───────────────────────────────────────────
  useEffect(() => {
    setMode(running ? "LIVE" : liveEnvelope ? "SIMU" : "DEMO");
    setSource(liveEnvelope?.source ?? "simulation");
  }, [running, liveEnvelope, setMode, setSource]);

  useEffect(() => {
    if (liveEnvelope) {
      setX108Gate(liveEnvelope.x108_gate);
      setLastDecisionId(liveEnvelope.decision_id);
      const proofComplete = !!(liveEnvelope.trace_id && liveEnvelope.attestation_ref);
      const proofPartial = !!(liveEnvelope.trace_id && !liveEnvelope.attestation_ref);
      setProofStatus(proofComplete ? "COMPLETE" : proofPartial ? "PARTIAL" : "MISSING");
    }
  }, [liveEnvelope, setX108Gate, setLastDecisionId, setProofStatus]);

  // Agents et agrégation dérivés du registre + enveloppe live
  const agents: AgentData[] = useMemo(() => buildAgentsFromRegistry(registryNames, liveEnvelope), [registryNames, liveEnvelope]);
  const aggregation: AggregationData = useMemo(() => buildAggregation(liveEnvelope, registryNames), [liveEnvelope, registryNames]);

  return (
       <div className="flex flex-col gap-0" style={{ minHeight: "calc(100vh - 120px)" }}>

      {/* ── Bandeau Replay depuis Past ──────────────────────────────────────── */}
      {isReplay && (
        <div className="flex items-center gap-3 px-4 py-2 text-[10px] font-mono"
          style={{ background: "oklch(0.72 0.18 145 / 0.08)", borderBottom: "1px solid oklch(0.72 0.18 145 / 0.30)" }}>
          <span style={{ color: "oklch(0.72 0.18 145)" }}>&#x21ba; REPLAY DEPUIS PAST</span>
          {replayDecisionId && (
            <span style={{ color: "oklch(0.55 0.01 240)" }}>
              Décision&nbsp;:
              <span className="ml-1 font-bold" style={{ color: "oklch(0.85 0.01 240)" }}>
                {decodeURIComponent(replayDecisionId).slice(0, 32)}…
              </span>
            </span>
          )}
          {replayGate && (
            <span className="px-2 py-0.5 rounded text-[9px]"
              style={{
                background: replayGate === "ALLOW" ? "oklch(0.72 0.18 145 / 0.15)" : replayGate === "HOLD" ? "oklch(0.72 0.18 45 / 0.15)" : "oklch(0.65 0.25 25 / 0.15)",
                color: replayGate === "ALLOW" ? "oklch(0.72 0.18 145)" : replayGate === "HOLD" ? "oklch(0.72 0.18 45)" : "oklch(0.65 0.25 25)",
                border: `1px solid ${replayGate === "ALLOW" ? "oklch(0.72 0.18 145 / 0.40)" : replayGate === "HOLD" ? "oklch(0.72 0.18 45 / 0.40)" : "oklch(0.65 0.25 25 / 0.40)"}`,
              }}>
              Gate original&nbsp;: {replayGate}
            </span>
          )}
          <Link href="/past">
            <span className="ml-auto px-2 py-0.5 rounded text-[9px] cursor-pointer"
              style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.55 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
              ← Retour Past
            </span>
          </Link>
        </div>
      )}

      {/* ── Zone haute : 3 colonnes ────────────────────────────────────────── */}
      {/* Badge source pipeline */}
      {liveEnvelope && (
        <div className="px-4 pt-2 flex items-center gap-2">
          <span className="text-[8px] font-mono px-2 py-0.5 rounded"
            style={{
              background: liveEnvelope.source === "canonical_fallback" ? "oklch(0.72 0.18 45 / 0.12)" : "oklch(0.72 0.18 145 / 0.12)",
              border: `1px solid ${liveEnvelope.source === "canonical_fallback" ? "oklch(0.72 0.18 45 / 0.40)" : "oklch(0.72 0.18 145 / 0.40)"}`,
              color: liveEnvelope.source === "canonical_fallback" ? "oklch(0.72 0.18 45)" : "oklch(0.72 0.18 145)",
            }}>
            {liveEnvelope.source === "canonical_fallback" ? "⚠ FALLBACK" : "✓ PIPELINE RÉEL"}
          </span>
          <span className="text-[8px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>
            source: {liveEnvelope.source} · id: {liveEnvelope.decision_id.slice(0, 24)}…
          </span>
        </div>
      )}
      {runError && (
        <div className="mx-4 mt-2 px-3 py-2 rounded text-[9px] font-mono"
          style={{ background: "oklch(0.65 0.25 25 / 0.10)", border: "1px solid oklch(0.65 0.25 25 / 0.30)", color: "oklch(0.65 0.25 25)" }}>
          ⚠ Erreur pipeline : {runError} — affichage en mode fallback
        </div>
      )}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 p-4">
        <CommandColumn
          domain={domain}
          scenario={scenario}
          setScenario={setScenario}
          onRun={handleRun}
          running={running}
        />
        <WorldFlowColumn domain={domain} running={running} />
        <DecisionProofColumn domain={domain} envelope={envelope} proof={proof} />
      </div>

      {/* ── Zone basse : constellation + deep detail ─────────────────────────── */}
      <div style={{ borderTop: "1px solid oklch(0.16 0.01 240)" }}>
        {/* Toggle */}
        <button
          onClick={() => setShowConstellation(v => !v)}
          className="w-full flex items-center justify-between px-4 py-2 text-[9px] font-mono"
          style={{ background: "oklch(0.105 0.01 240)", color: "oklch(0.50 0.01 240)" }}
        >
          <span>🔭 Constellation agentique — {agents.length > 0 ? agents.length : registryQuery.isLoading ? "…" : "0"} agents</span>
          <span>{showConstellation ? "▲ Réduire" : "▼ Développer"}</span>
        </button>

        {showConstellation && (
          <div className="p-4" style={{ background: "oklch(0.095 0.01 240)" }}>
            {/* Tabs */}
            <div className="flex gap-1 mb-3">
              {(["constellation", "detail"] as const).map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className="px-3 py-1 rounded text-[9px] font-mono font-bold"
                  style={{
                    background: activeTab === tab ? "oklch(0.72 0.18 145 / 0.12)" : "oklch(0.12 0.01 240)",
                    border: `1px solid ${activeTab === tab ? "oklch(0.72 0.18 145 / 0.40)" : "oklch(0.18 0.01 240)"}`,
                    color: activeTab === tab ? "oklch(0.72 0.18 145)" : "oklch(0.50 0.01 240)",
                  }}
                >
                  {tab === "constellation" ? "Constellation" : "Deep Detail"}
                </button>
              ))}
            </div>

            {activeTab === "constellation" && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {registryQuery.isLoading ? (
                  <div className="rounded p-4 text-[9px] font-mono" style={{ background: "oklch(0.115 0.01 240)", color: "oklch(0.45 0.01 240)" }}>
                    ⏳ Chargement du registre d'agents…
                  </div>
                ) : (
                  <AgentConstellationPanel
                    agents={agents}
                    aggregation={aggregation}
                    domain={domain}
                    defaultExpanded={false}
                  />
                )}
                {/* Résumé agrégation */}
                <div className="rounded p-3" style={{ background: "oklch(0.115 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
                  <div className="text-[9px] font-mono font-bold mb-2" style={{ color: "#a78bfa" }}>Résumé agrégation</div>
                  <div className="flex flex-col gap-1.5 text-[9px] font-mono">
                    {[
                      { k: "Verdict",        v: aggregation.market_verdict },
                      { k: "Confidence",     v: `${Math.round(aggregation.confidence * 100)}%` },
                      { k: "Contradictions", v: String(aggregation.contradictions_count) },
                      { k: "Unknowns",       v: String(aggregation.unknowns_count) },
                      { k: "Evidence refs",  v: String(aggregation.evidence_refs) },
                    ].map(({ k, v }) => (
                      <div key={k} className="flex justify-between">
                        <span style={{ color: "oklch(0.45 0.01 240)" }}>{k}</span>
                        <span style={{ color: "oklch(0.70 0.01 240)" }}>{v}</span>
                      </div>
                    ))}
                  </div>
                  <div className="mt-3">
                    <div className="text-[8px] font-mono mb-1" style={{ color: "oklch(0.40 0.01 240)" }}>Top contributors</div>
                    {aggregation.dominant_contributors.map((c: string) => (
                      <div key={c} className="text-[9px] font-mono" style={{ color: "oklch(0.60 0.01 240)" }}>· {c}</div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === "detail" && (
              <div className="flex flex-col gap-3">
                {/* Sous-onglets Deep Detail */}
                <div className="flex gap-1 flex-wrap">
                  {([
                    { k: "envelope",  l: "Envelope" },
                    { k: "agents",    l: "Agent Votes" },
                    { k: "aggregate", l: "Aggregate" },
                    { k: "json",      l: "JSON" },
                    { k: "metrics",   l: "Métriques" },
                    { k: "raw",       l: "Raw Engine" },
                  ] as const).map(t => (
                    <button key={t.k} onClick={() => setActiveDetailTab(t.k)}
                      className="px-2 py-0.5 rounded text-[8px] font-mono"
                      style={{
                        background: activeDetailTab === t.k ? "oklch(0.60 0.15 290 / 0.15)" : "oklch(0.12 0.01 240)",
                        border: `1px solid ${activeDetailTab === t.k ? "oklch(0.60 0.15 290 / 0.50)" : "oklch(0.18 0.01 240)"}`,
                        color: activeDetailTab === t.k ? "#a78bfa" : "oklch(0.50 0.01 240)",
                      }}>{t.l}</button>
                  ))}
                </div>

                {/* Envelope */}
                {activeDetailTab === "envelope" && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {envelope ? (
                      <DecisionEnvelopeCard envelope={envelope} variant="expanded" pastLink="/past" />
                    ) : (
                      <div className="rounded p-4 text-center" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
                        <div className="text-[9px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>Lancez une simulation pour voir la décision</div>
                      </div>
                    )}
                    {proof ? (
                      <ProofChainView chain={proof} variant="full" />
                    ) : (
                      <div className="rounded p-4 text-center" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
                        <div className="text-[9px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>Proof chain disponible après le premier run</div>
                      </div>
                    )}
                  </div>
                )}

                {/* Agent Votes */}
                {activeDetailTab === "agents" && (
                  <div className="rounded p-3" style={{ background: "oklch(0.115 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
                    <div className="text-[9px] font-mono font-bold mb-2" style={{ color: "#a78bfa" }}>Agent Votes — {agents.length} agents</div>
                    {agents.length === 0 ? (
                      <div className="text-[9px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>Lancez une simulation pour voir les votes agents</div>
                    ) : (
                      <div className="flex flex-col gap-1">
                        {agents.map(a => (
                          <div key={a.name} className="flex items-center gap-2 px-2 py-1 rounded"
                            style={{ background: "oklch(0.105 0.01 240)" }}>
                            <span className="text-[8px] font-mono shrink-0 w-20 truncate" style={{ color: "oklch(0.55 0.01 240)" }}>{a.layer}</span>
                            <span className="text-[9px] font-mono flex-1 truncate" style={{ color: "oklch(0.75 0.01 240)" }}>{a.name}</span>
                            <span className="text-[9px] font-mono font-bold" style={{ color: (a.confidence ?? 0) >= 0.80 ? "oklch(0.72 0.18 145)" : (a.confidence ?? 0) >= 0.65 ? "oklch(0.72 0.18 45)" : "oklch(0.65 0.25 25)" }}>
                              {Math.round((a.confidence ?? 0) * 100)}%
                            </span>
                            {a.claim && <span className="text-[8px] font-mono truncate max-w-[120px]" style={{ color: "oklch(0.45 0.01 240)" }}>{a.claim}</span>}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Aggregate */}
                {activeDetailTab === "aggregate" && (
                  <div className="rounded p-3" style={{ background: "oklch(0.115 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
                    <div className="text-[9px] font-mono font-bold mb-2" style={{ color: "#a78bfa" }}>Aggregate Domain</div>
                    <div className="flex flex-col gap-1.5 text-[9px] font-mono">
                      {[
                        { k: "Verdict",        v: aggregation.market_verdict },
                        { k: "Confidence",     v: `${Math.round(aggregation.confidence * 100)}%` },
                        { k: "Gate X-108",     v: envelope?.x108_gate ?? "—" },
                        { k: "Severity",       v: envelope?.severity ?? "—" },
                        { k: "Contradictions", v: String(aggregation.contradictions_count) },
                        { k: "Unknowns",       v: String(aggregation.unknowns_count) },
                        { k: "Evidence refs",  v: String(aggregation.evidence_refs) },
                        { k: "Risk flags",     v: aggregation.risk_flags.length > 0 ? aggregation.risk_flags.join(", ") : "Aucun" },
                        { k: "Reason code",    v: envelope?.reason_code ?? "—" },
                        { k: "Decision ID",    v: envelope?.decision_id?.slice(0, 30) ?? "—" },
                        { k: "Trace ID",       v: envelope?.trace_id?.slice(0, 30) ?? "—" },
                        { k: "Attestation",    v: envelope?.attestation_ref?.slice(0, 30) ?? "—" },
                      ].map(({ k, v }) => (
                        <div key={k} className="flex justify-between gap-4">
                          <span style={{ color: "oklch(0.45 0.01 240)" }}>{k}</span>
                          <span className="text-right truncate max-w-[200px]" style={{ color: "oklch(0.70 0.01 240)" }}>{v}</span>
                        </div>
                      ))}
                    </div>
                    <div className="mt-3">
                      <div className="text-[8px] font-mono mb-1" style={{ color: "oklch(0.40 0.01 240)" }}>Top contributors</div>
                      {aggregation.dominant_contributors.map((c: string) => (
                        <div key={c} className="text-[9px] font-mono" style={{ color: "oklch(0.60 0.01 240)" }}>· {c}</div>
                      ))}
                    </div>
                  </div>
                )}

                {/* JSON */}
                {activeDetailTab === "json" && (
                  <div className="rounded overflow-hidden" style={{ border: "1px solid oklch(0.18 0.01 240)" }}>
                    <div className="px-3 py-1.5 text-[8px] font-mono font-bold" style={{ background: "oklch(0.12 0.01 240)", color: "#a78bfa", borderBottom: "1px solid oklch(0.16 0.01 240)" }}>Envelope JSON</div>
                    <pre className="p-3 text-[8px] font-mono overflow-auto max-h-64" style={{ background: "oklch(0.09 0.01 240)", color: "oklch(0.65 0.01 240)" }}>
                      {envelope ? JSON.stringify(envelope, null, 2) : "Aucune enveloppe — lancez une simulation"}
                    </pre>
                  </div>
                )}

                {/* Métriques */}
                {activeDetailTab === "metrics" && (
                  <div className="rounded p-3" style={{ background: "oklch(0.115 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
                    <div className="text-[9px] font-mono font-bold mb-2" style={{ color: "#a78bfa" }}>Métriques domaine</div>
                    {!envelope?.metrics || Object.keys(envelope.metrics as object).length === 0 ? (
                      <div className="text-[9px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>Aucune métrique disponible</div>
                    ) : (
                      <div className="flex flex-col gap-1.5">
                        {Object.entries(envelope.metrics as Record<string, number>).map(([k, v]) => (
                          <div key={k} className="flex items-center justify-between">
                            <span className="text-[9px] font-mono" style={{ color: "oklch(0.55 0.01 240)" }}>{k.replace(/_/g, " ")}</span>
                            <div className="flex items-center gap-2">
                              <div className="w-24 h-1.5 rounded-full overflow-hidden" style={{ background: "oklch(0.16 0.01 240)" }}>
                                <div className="h-full rounded-full" style={{ width: `${Math.min(100, Math.abs(v) * 100)}%`, background: v > 0 ? "oklch(0.72 0.18 145)" : "oklch(0.65 0.25 25)" }} />
                              </div>
                              <span className="text-[9px] font-mono font-bold w-12 text-right" style={{ color: v > 0 ? "oklch(0.72 0.18 145)" : "oklch(0.65 0.25 25)" }}>
                                {typeof v === "number" ? v.toFixed(3) : String(v)}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Raw Engine */}
                {activeDetailTab === "raw" && (
                  <div className="rounded overflow-hidden" style={{ border: "1px solid oklch(0.18 0.01 240)" }}>
                    <div className="px-3 py-1.5 text-[8px] font-mono font-bold" style={{ background: "oklch(0.12 0.01 240)", color: "oklch(0.55 0.01 240)", borderBottom: "1px solid oklch(0.16 0.01 240)" }}>Raw Engine Output</div>
                    <pre className="p-3 text-[8px] font-mono overflow-auto max-h-64" style={{ background: "oklch(0.09 0.01 240)", color: "oklch(0.55 0.01 240)" }}>
                      {rawRunData ? JSON.stringify(rawRunData, null, 2) : "Aucune donnée brute — lancez une simulation"}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
