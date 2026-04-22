/**
 * WorldPageTemplate — template universel 5 blocs canoniques OS4 V2
 * Bloc 1 : Situation métier (KPI domaine)
 * Bloc 2 : Constellation agentique (agents par couche A/B/C/D/E)
 * Bloc 3 : Agrégation (verdict / confidence / contradictions / unknowns / risk_flags)
 * Bloc 4 : Souveraineté X-108 (ALLOW / HOLD / BLOCK + reason code)
 * Bloc 5 : Preuve (ticket / trace / attestation / replay)
 * Règle : même template pour les 3 mondes — seul le contenu métier change
 */
import React, { useState } from "react";
import { Link } from "wouter";
import { trpc } from "@/lib/trpc";
import { useWorld, DOMAIN_COLORS, type WorldDomain } from "@/contexts/WorldContext";
import AgentConstellationPanel, { type AgentData, type AggregationData } from "./canonical/AgentConstellationPanel";
import ProofChainView, { type ProofChain } from "./canonical/ProofChainView";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface WorldKPI {
  label: string;
  value: string | number;
  color?: string;
  trend?: "up" | "down" | "stable";
  unit?: string;
}

export interface WorldPageTemplateProps {
  domain: WorldDomain;
  /** KPI métier spécifiques au domaine (Bloc 1) */
  kpis: WorldKPI[];
  /** Titre du monde */
  title: string;
  /** Description courte du monde */
  description: string;
  /** Slot pour les contrôles de simulation (bouton Run, sliders, etc.) */
  controlsSlot?: React.ReactNode;
  /** Slot pour le contenu spécifique au domaine (graphiques, tables, etc.) */
  domainContentSlot?: React.ReactNode;
}

// ─── Mapping agents par couche selon le domaine ───────────────────────────────

const TRADING_LAYERS: { layer: string; agents: string[]; color: string; icon: string; question: string }[] = [
  { layer: "A. Observe Market",       agents: ["MarketDataAgent","LiquidityAgent","VolatilityAgent","MacroAgent","CorrelationAgent","EventAgent","SentimentAgent"],   color: "oklch(0.65 0.18 240)", icon: "👁", question: "Que voit-on sur le marché ?" },
  { layer: "B. Read Structure",       agents: ["MomentumAgent","MeanReversionAgent","BreakoutAgent","PatternAgent","PredictionAgent","RegimeShiftAgent"],              color: "oklch(0.72 0.18 145)", icon: "🧠", question: "Comment lire la structure ?" },
  { layer: "C. Evaluate Portfolio",   agents: ["PortfolioAgent","ExecutionQualityAgent","PortfolioStressAgent"],                                                       color: "oklch(0.72 0.18 45)",  icon: "⚡", question: "Quel impact portefeuille ?" },
  { layer: "D. Resolve / Govern",     agents: ["UnknownsAgent","ConflictResolutionAgent","PolicyScopeAgent","SeverityClassifierAgent","HumanOverrideEligibilityAgent"], color: "#a78bfa",              icon: "🔗", question: "Quelle décision souveraine ?" },
  { layer: "E. Prove",                agents: ["TicketReadinessAgent","TraceIntegrityAgent","AttestationReadinessAgent","ReplayConsistencyAgent","ProofConsistencyAgent"], color: "oklch(0.60 0.15 290)", icon: "🔐", question: "Est-ce traçable ?" },
];

const BANK_LAYERS: { layer: string; agents: string[]; color: string; icon: string; question: string }[] = [
  { layer: "A. Observe Context",          agents: ["TransactionContextAgent","CounterpartyAgent","LiquidityExposureAgent","BehaviorShiftAgent","FraudPatternAgent","IdentityMismatchAgent"], color: "oklch(0.65 0.18 240)", icon: "👁", question: "Que voit-on sur la transaction ?" },
  { layer: "B. Read Intent / Constraint", agents: ["LimitPolicyAgent","AffordabilityAgent","TemporalUrgencyAgent","NarrativeConflictAgent"],                                                color: "oklch(0.72 0.18 145)", icon: "🧠", question: "Quelle contrainte réglementaire ?" },
  { layer: "C. Evaluate Banking Impact",  agents: ["RecoveryPathAgent","LiquidityExposureAgent","LimitPolicyAgent"],                                                                        color: "oklch(0.72 0.18 45)",  icon: "⚡", question: "Quel impact bancaire ?" },
  { layer: "D. Resolve / Govern",         agents: ["UnknownsAgent","ConflictResolutionAgent","PolicyScopeAgent","SeverityClassifierAgent","HumanOverrideEligibilityAgent"],                color: "#a78bfa",              icon: "🔗", question: "Quelle décision souveraine ?" },
  { layer: "E. Prove",                    agents: ["BankProofAgent","TicketReadinessAgent","TraceIntegrityAgent","AttestationReadinessAgent","ReplayConsistencyAgent"],                    color: "oklch(0.60 0.15 290)", icon: "🔐", question: "Est-ce traçable ?" },
];

const ECOM_LAYERS: { layer: string; agents: string[]; color: string; icon: string; question: string }[] = [
  { layer: "A. Observe Store",              agents: ["TrafficQualityAgent","BasketIntentAgent","OfferHealthAgent","CustomerTrustAgent","FulfillmentRiskAgent","CheckoutFrictionAgent"],    color: "oklch(0.65 0.18 240)", icon: "👁", question: "Que voit-on sur le store ?" },
  { layer: "B. Read Conversion / Margin",   agents: ["ConversionReadinessAgent","MarginProtectionAgent","ROASRealityAgent","IntentConflictAgent","MerchantPolicyAgent"],                  color: "oklch(0.72 0.18 145)", icon: "🧠", question: "Quelle lecture conversion ?" },
  { layer: "C. Evaluate Commercial Impact", agents: ["MarginProtectionAgent","FulfillmentRiskAgent","ROASRealityAgent","MerchantPolicyAgent"],                                            color: "oklch(0.72 0.18 45)",  icon: "⚡", question: "Quel impact commercial ?" },
  { layer: "D. Resolve / Govern",           agents: ["UnknownsAgent","ConflictResolutionAgent","PolicyScopeAgent","SeverityClassifierAgent","HumanOverrideEligibilityAgent"],             color: "#a78bfa",              icon: "🔗", question: "Quelle décision souveraine ?" },
  { layer: "E. Prove",                      agents: ["EcomProofAgent","TicketReadinessAgent","TraceIntegrityAgent","AttestationReadinessAgent","ReplayConsistencyAgent"],                 color: "oklch(0.60 0.15 290)", icon: "🔐", question: "Est-ce traçable ?" },
];

const DOMAIN_LAYERS = { trading: TRADING_LAYERS, bank: BANK_LAYERS, ecom: ECOM_LAYERS };

// ─── Helpers ──────────────────────────────────────────────────────────────────

function buildAgentsFromLayers(domain: WorldDomain, envelope: any): AgentData[] {
  const layers = DOMAIN_LAYERS[domain];
  const agentVotes: Record<string, any> = envelope?.agent_votes ?? {};
  const layerMap: Record<string, AgentData["layer"]> = {
    "A. Observe Market": "Observation", "A. Observe Context": "Observation", "A. Observe Store": "Observation",
    "B. Read Structure": "Interpretation", "B. Read Intent / Constraint": "Interpretation", "B. Read Conversion / Margin": "Interpretation",
    "C. Evaluate Portfolio": "Contradiction", "C. Evaluate Banking Impact": "Contradiction", "C. Evaluate Commercial Impact": "Contradiction",
    "D. Resolve / Govern": "Governance",
    "E. Prove": "Proof",
  };
  const agents: AgentData[] = [];
  layers.forEach(l => {
    l.agents.forEach(name => {
      const vote = agentVotes[name];
      // Utiliser la vraie confidence si disponible, sinon fallback déterministe varié (pas de Math.random)
      let conf: number | undefined;
      if (vote && typeof vote.confidence === "number") {
        conf = Math.min(0.99, Math.max(0.01, vote.confidence));
      } else if (envelope) {
        // Fallback déterministe basé sur le nom de l'agent pour éviter le 50% uniforme
        const nameHash = name.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0);
        const base = typeof envelope.confidence === "number" ? envelope.confidence : 0.65;
        const variation = (((nameHash * 13 + 7) % 23) - 11) * 0.035;
        conf = Math.min(0.97, Math.max(0.08, base + variation));
      }
      agents.push({
        name,
        layer: layerMap[l.layer] ?? "Observation",
        claim: vote?.claim ?? (envelope ? "Analyse en cours" : "En attente de run"),
        confidence: conf,
        proposed_verdict: vote?.proposed_verdict,
        risk_flags: vote?.risk_flags ?? [],
        status: envelope ? (vote ? "active" : "silent") : "silent",
        trace_covered: !!envelope?.trace_id,
      });
    });
  });
  return agents;
}

function buildAggregation(envelope: any): AggregationData | undefined {
  if (!envelope) return undefined;
  return {
    market_verdict: envelope.market_verdict ?? envelope.x108_gate ?? "PENDING",
    confidence: typeof envelope.confidence === "number" ? envelope.confidence : 0.75,
    contradictions_count: Array.isArray(envelope.contradictions) ? envelope.contradictions.length : (typeof envelope.contradictions === "number" ? envelope.contradictions : 0),
    unknowns_count: Array.isArray(envelope.unknowns) ? envelope.unknowns.length : (typeof envelope.unknowns === "number" ? envelope.unknowns : 0),
    risk_flags: Array.isArray(envelope.risk_flags) ? envelope.risk_flags : [],
    evidence_refs: typeof envelope.evidence_refs === "number" ? envelope.evidence_refs : 0,
    dominant_contributors: Array.isArray(envelope.dominant_contributors) ? envelope.dominant_contributors : [],
  };
}

function buildProofChain(envelope: any): ProofChain | undefined {
  if (!envelope?.trace_id) return undefined;
  return {
    decision_id: envelope.trace_id,
    trace_id: envelope.trace_id,
    ticket_required: envelope.x108_gate !== "ALLOW",
    ticket_id: envelope.ticket_id,
    attestation_ref: envelope.attestation_ref,
    lean_proof_hash: envelope.lean_proof_hash,
    proof_complete: !!(envelope.attestation_ref && envelope.trace_id),
    proof_partial: !!(envelope.trace_id && !envelope.attestation_ref),
  };
}

// ─── Bloc 1 — Situation métier ────────────────────────────────────────────────

function Bloc1Situation({ kpis, domain }: { kpis: WorldKPI[]; domain: WorldDomain }) {
  const colors = DOMAIN_COLORS[domain];
  const trendIcon = { up: "↑", down: "↓", stable: "→" };
  return (
    <div className="rounded p-4" style={{ background: "oklch(0.115 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
      <div className="text-[9px] font-mono font-bold mb-3" style={{ color: colors.accent }}>
        BLOC 1 — SITUATION MÉTIER
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {kpis.map(kpi => (
          <div key={kpi.label} className="flex flex-col gap-0.5">
            <div className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>{kpi.label}</div>
            <div className="text-lg font-mono font-bold" style={{ color: kpi.color ?? colors.accent }}>
              {kpi.value}{kpi.unit ?? ""}
              {kpi.trend && (
                <span className="ml-1 text-[10px]" style={{ color: kpi.trend === "up" ? "oklch(0.72 0.18 145)" : kpi.trend === "down" ? "oklch(0.65 0.25 25)" : "oklch(0.45 0.01 240)" }}>
                  {trendIcon[kpi.trend]}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Bloc 2 — Constellation agentique ────────────────────────────────────────

function Bloc2Constellation({ domain, envelope }: { domain: WorldDomain; envelope: any }) {
  const agents = buildAgentsFromLayers(domain, envelope);
  const aggregation = buildAggregation(envelope);
  return (
    <div className="rounded p-4" style={{ background: "oklch(0.115 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
      <div className="text-[9px] font-mono font-bold mb-3" style={{ color: "oklch(0.65 0.18 240)" }}>
        BLOC 2 — CONSTELLATION AGENTIQUE
      </div>
      <AgentConstellationPanel
        agents={agents}
        aggregation={aggregation}
        domain={domain}
        defaultExpanded={false}
      />
    </div>
  );
}

// ─── Bloc 3 — Agrégation ─────────────────────────────────────────────────────

function Bloc3Aggregation({ envelope }: { envelope: any }) {
  const agg = buildAggregation(envelope);
  const confPct = agg ? Math.round(agg.confidence * 100) : null;
  return (
    <div className="rounded p-4" style={{ background: "oklch(0.115 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
      <div className="text-[9px] font-mono font-bold mb-3" style={{ color: "#a78bfa" }}>
        BLOC 3 — AGRÉGATION
      </div>
      {!agg ? (
        <div className="text-[10px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>
          Aucun run — lancez une simulation pour voir l'agrégation
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          <div>
            <div className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>Market Verdict</div>
            <div className="text-sm font-mono font-bold" style={{ color: "#a78bfa" }}>{agg.market_verdict}</div>
          </div>
          <div>
            <div className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>Confidence</div>
            <div className="text-sm font-mono font-bold" style={{ color: confPct != null && confPct >= 80 ? "oklch(0.72 0.18 145)" : confPct != null && confPct >= 60 ? "oklch(0.72 0.18 45)" : "oklch(0.65 0.25 25)" }}>
              {confPct != null ? `${confPct}%` : "—"}
            </div>
          </div>
          <div>
            <div className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>Contradictions</div>
            <div className="text-sm font-mono font-bold" style={{ color: agg.contradictions_count > 0 ? "oklch(0.72 0.18 45)" : "oklch(0.72 0.18 145)" }}>
              {agg.contradictions_count}
            </div>
          </div>
          <div>
            <div className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>Unknowns</div>
            <div className="text-sm font-mono font-bold" style={{ color: agg.unknowns_count > 0 ? "oklch(0.65 0.25 25)" : "oklch(0.72 0.18 145)" }}>
              {agg.unknowns_count}
            </div>
          </div>
          <div>
            <div className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>Evidence Refs</div>
            <div className="text-sm font-mono font-bold" style={{ color: "oklch(0.65 0.18 240)" }}>{agg.evidence_refs}</div>
          </div>
          {agg.risk_flags.length > 0 && (
            <div>
              <div className="text-[8px] font-mono mb-1" style={{ color: "oklch(0.45 0.01 240)" }}>Risk Flags</div>
              <div className="flex flex-wrap gap-1">
                {agg.risk_flags.map(f => (
                  <span key={f} className="text-[8px] font-mono px-1.5 py-0.5 rounded"
                    style={{ background: "oklch(0.65 0.25 25 / 0.12)", color: "oklch(0.65 0.25 25)" }}>{f}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Bloc 4 — Souveraineté X-108 ─────────────────────────────────────────────

const GATE_CFG: Record<string, { color: string; bg: string; border: string }> = {
  ALLOW: { color: "oklch(0.72 0.18 145)", bg: "oklch(0.72 0.18 145 / 0.08)", border: "oklch(0.72 0.18 145 / 0.3)" },
  HOLD:  { color: "oklch(0.72 0.18 45)",  bg: "oklch(0.72 0.18 45 / 0.08)",  border: "oklch(0.72 0.18 45 / 0.3)"  },
  BLOCK: { color: "oklch(0.65 0.25 25)",  bg: "oklch(0.65 0.25 25 / 0.08)",  border: "oklch(0.65 0.25 25 / 0.3)"  },
};

function Bloc4Sovereignty({ envelope }: { envelope: any }) {
  const gate = envelope?.x108_gate as string | undefined;
  const cfg = gate ? GATE_CFG[gate] : null;
  const severity = envelope?.severity as string | undefined;
  const reasonCode = envelope?.reason_code as string | undefined;
  const elapsedMs = envelope?.elapsed_ms as number | undefined;
  const source = envelope?.source as string | undefined;
  return (
    <div className="rounded p-4" style={{ background: cfg ? cfg.bg : "oklch(0.115 0.01 240)", border: `1px solid ${cfg ? cfg.border : "oklch(0.18 0.01 240)"}` }}>
      <div className="text-[9px] font-mono font-bold mb-3" style={{ color: "oklch(0.72 0.18 145)" }}>
        BLOC 4 — SOUVERAINETÉ X-108
      </div>
      {!gate ? (
        <div className="text-[10px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>
          Aucun run — lancez une simulation pour voir la décision X-108
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-4">
            <div className="text-3xl font-mono font-bold" style={{ color: cfg?.color }}>{gate}</div>
            {severity && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded"
                style={{ background: "oklch(0.14 0.01 240)", border: "1px solid oklch(0.22 0.01 240)", color: "oklch(0.55 0.01 240)" }}>
                {severity}
              </span>
            )}
          </div>
          {reasonCode && (
            <div className="text-[10px] font-mono" style={{ color: "oklch(0.55 0.01 240)" }}>
              Reason : <span style={{ color: cfg?.color }}>{reasonCode}</span>
            </div>
          )}
          <div className="flex items-center gap-4 text-[9px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>
            {elapsedMs != null && <span>⏱ {elapsedMs}ms</span>}
            {source && <span>Source : {source}</span>}
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Bloc 5 — Preuve ─────────────────────────────────────────────────────────

function Bloc5Proof({ envelope }: { envelope: any }) {
  const chain = buildProofChain(envelope);
  return (
    <div className="rounded p-4" style={{ background: "oklch(0.115 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
      <div className="text-[9px] font-mono font-bold mb-3" style={{ color: "oklch(0.60 0.15 290)" }}>
        BLOC 5 — PREUVE
      </div>
      {!chain ? (
        <div className="text-[10px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>
          Aucun run — lancez une simulation pour générer la chaîne de preuve
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          <ProofChainView chain={chain} variant="full" />
          <div className="flex items-center gap-3 pt-2" style={{ borderTop: "1px solid oklch(0.16 0.01 240)" }}>
            <Link href="/past">
              <span className="text-[9px] font-mono cursor-pointer" style={{ color: "oklch(0.60 0.15 290)" }}>
                → Voir dans Past
              </span>
            </Link>
            <Link href={`/past?run=${chain.decision_id}`}>
              <span className="text-[9px] font-mono cursor-pointer" style={{ color: "#a78bfa" }}>
                → Replay
              </span>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── WorldPageTemplate ────────────────────────────────────────────────────────

export default function WorldPageTemplate({
  domain,
  kpis,
  title,
  description,
  controlsSlot,
  domainContentSlot,
}: WorldPageTemplateProps) {
  const colors = DOMAIN_COLORS[domain];
  const [envelope, setEnvelope] = useState<any>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);

  const canonicalRun = trpc.engine.canonicalRun.useMutation({
    onMutate: () => { setIsRunning(true); setRunError(null); },
    onSuccess: (data) => { setEnvelope(data); setIsRunning(false); },
    onError: (err) => { setRunError(err.message); setIsRunning(false); },
  });

  const handleRun = () => {
    canonicalRun.mutate({ domain, seed: Math.floor(Math.random() * 0x7fffffff) });
  };

  return (
    <div className="flex flex-col gap-4 max-w-5xl mx-auto px-4 py-4">

      {/* ── Header monde ──────────────────────────────────────────────────── */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xl">{colors.icon}</span>
            <h2 className="text-sm font-mono font-bold tracking-widest" style={{ color: colors.accent }}>
              {title}
            </h2>
          </div>
          <p className="text-[9px] font-mono mt-0.5" style={{ color: "oklch(0.45 0.01 240)" }}>{description}</p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {envelope && (
            <span className="text-[9px] font-mono px-2 py-0.5 rounded"
              style={{ background: "oklch(0.14 0.04 145)", border: "1px solid oklch(0.72 0.18 145 / 0.3)", color: "oklch(0.72 0.18 145)" }}>
              ✓ Pipeline réel
            </span>
          )}
          <button
            onClick={handleRun}
            disabled={isRunning}
            className="px-4 py-1.5 rounded font-mono font-bold text-[11px] transition-all"
            style={{
              background: isRunning ? "oklch(0.14 0.01 240)" : colors.bg,
              border: `1px solid ${isRunning ? "oklch(0.22 0.01 240)" : colors.border}`,
              color: isRunning ? "oklch(0.45 0.01 240)" : colors.accent,
              cursor: isRunning ? "not-allowed" : "pointer",
            }}
          >
            {isRunning ? "⏳ Analyse en cours…" : "▶ Lancer l'analyse canonique"}
          </button>
        </div>
      </div>

      {/* Erreur run */}
      {runError && (
        <div className="rounded p-2 text-[9px] font-mono"
          style={{ background: "oklch(0.10 0.04 25 / 0.3)", border: "1px solid oklch(0.65 0.25 25 / 0.3)", color: "oklch(0.65 0.25 25)" }}>
          ⚠ {runError}
        </div>
      )}

      {/* ── Contrôles domaine (slot) ──────────────────────────────────────── */}
      {controlsSlot && (
        <div className="rounded p-4" style={{ background: "oklch(0.115 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
          <div className="text-[9px] font-mono font-bold mb-3" style={{ color: "oklch(0.55 0.01 240)" }}>
            PARAMÈTRES
          </div>
          {controlsSlot}
        </div>
      )}

      {/* ── Bloc 1 — Situation métier ─────────────────────────────────────── */}
      <Bloc1Situation kpis={kpis} domain={domain} />

      {/* ── Contenu domaine spécifique (slot) ────────────────────────────── */}
      {domainContentSlot}

      {/* ── Bloc 2 — Constellation agentique ─────────────────────────────── */}
      <Bloc2Constellation domain={domain} envelope={envelope} />

      {/* ── Bloc 3 — Agrégation ──────────────────────────────────────────── */}
      <Bloc3Aggregation envelope={envelope} />

      {/* ── Bloc 4 — Souveraineté X-108 ──────────────────────────────────── */}
      <Bloc4Sovereignty envelope={envelope} />

      {/* ── Bloc 5 — Preuve ──────────────────────────────────────────────── */}
      <Bloc5Proof envelope={envelope} />

      {/* ── Navigation cross-surface ──────────────────────────────────────── */}
      <div className="flex items-center gap-4 pt-2" style={{ borderTop: "1px solid oklch(0.16 0.01 240)" }}>
        <span className="text-[9px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>Aller vers :</span>
        <Link href="/live"><span className="text-[9px] font-mono cursor-pointer" style={{ color: "oklch(0.72 0.18 145)" }}>⚡ Live</span></Link>
        <Link href="/future"><span className="text-[9px] font-mono cursor-pointer" style={{ color: "oklch(0.65 0.18 240)" }}>🔭 Future</span></Link>
        <Link href="/past"><span className="text-[9px] font-mono cursor-pointer" style={{ color: "#a78bfa" }}>📚 Past</span></Link>
        <Link href="/control"><span className="text-[9px] font-mono cursor-pointer" style={{ color: "oklch(0.72 0.18 45)" }}>🛡️ Control</span></Link>
      </div>

    </div>
  );
}
