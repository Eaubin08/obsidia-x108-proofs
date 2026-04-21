/**
 * Control — tour de commandement OS4 V2
 * Données réelles depuis trpc.proof.guardStats + trpc.proof.simulationRuns
 * Spec : pasted_content_5
 */
import React, { useState, useMemo, useEffect } from "react";
import { Link } from "wouter";
import { trpc } from "@/lib/trpc";
import { useWorld, DOMAIN_COLORS, type WorldDomain } from "@/contexts/WorldContext";
import HealthMatrix, { type HealthMatrixData } from "@/components/canonical/HealthMatrix";
import IncidentCard, { type IncidentData } from "@/components/canonical/IncidentCard";

// ─── Helpers ──────────────────────────────────────────────────────────────────
function formatRelative(ts: number): string {
  const diff = Date.now() - ts;
  if (diff < 60000) return `${Math.floor(diff / 1000)}s`;
  if (diff < 3600000) return `${Math.floor(diff / 60000)}min`;
  return `${Math.floor(diff / 3600000)}h`;
}

// ─── Dériver HealthMatrix depuis guardStats ────────────────────────────────────
function deriveHealthMatrix(
  domain: WorldDomain,
  guardStats: any,
  agentRegistry: any
): HealthMatrixData {
  const domainStats = guardStats?.byDomain?.[domain] ?? { total: 0, blocked: 0, held: 0 };
  const total = domainStats.total;
  const blocked = domainStats.blocked;
  const held = domainStats.held;
  const allowed = total - blocked - held;

  // Agents actifs depuis le registre
  const agents = agentRegistry?.[domain] ?? [];
  const agentCount = agents.length;
  const agentHealth = agentCount > 0 ? Math.min(100, 70 + agentCount * 2) : 0;

  // Proof coverage : % de décisions avec proof complète (approx)
  const proofCoverage = total > 0 ? Math.round((allowed / total) * 100) : 0;

  // Decision quality : % non-bloquées
  const decisionQuality = total > 0 ? Math.round(((total - blocked) / total) * 100) : 0;

  // Risk exposure : % bloquées (plus c'est haut, plus c'est risqué)
  const riskExposure = total > 0 ? Math.round((blocked / total) * 100) : 0;

  return {
    domain,
    agent_health: {
      label: "Agent Health",
      score: agentHealth,
      trend: agentHealth >= 80 ? "stable" : "down",
      details: `${agentCount} agents actifs`,
    },
    proof_coverage: {
      label: "Proof Coverage",
      score: proofCoverage,
      trend: proofCoverage >= 80 ? "up" : "down",
      details: `${proofCoverage}% des décisions prouvées`,
    },
    decision_quality: {
      label: "Decision Quality",
      score: decisionQuality,
      trend: decisionQuality >= 80 ? "up" : "down",
      details: `${allowed}/${total} autorisées`,
    },
    risk_exposure: {
      label: "Risk Exposure",
      score: riskExposure,
      trend: riskExposure > 20 ? "up" : "stable",
      details: `${blocked} bloquées, ${held} en attente`,
      critical: riskExposure > 30,
    },
    last_updated: Date.now(),
  };
}

// ─── Dériver incidents depuis les tickets BLOCK/HOLD récents ─────────────────
function deriveIncidents(tickets: any[]): IncidentData[] {
  if (!tickets || tickets.length === 0) return [];
  const critical = tickets
    .filter(t => t.decision === "BLOCK" || t.decision === "HOLD")
    .slice(0, 5);

  return critical.map((t, i) => {
    const reasons = (t.reasons as string[]) ?? [];
    const gate = t.decision as "ALLOW" | "HOLD" | "BLOCK";
    const ts = new Date(t.createdAt).getTime();
    return {
      id: `INC-${String(t.id).padStart(3, "0")}`,
      title: reasons[0] ?? `Décision ${gate} — ${t.domain}`,
      domain: (t.domain === "trading" || t.domain === "bank" || t.domain === "ecom" ? t.domain : "trading") as WorldDomain,
      severity: gate === "BLOCK" ? "S4" : "S3",
      status: gate === "BLOCK" ? "investigating" : "active",
      trigger: reasons.slice(0, 2).join(", ") || `Gate ${gate}`,
      x108_response: gate,
      decision_id: t.intentId,
      timestamp: ts,
      description: `X-108 a émis un ${gate} sur la décision ${t.intentId.slice(0, 20)}… — ${reasons.join(", ") || "Aucun détail"}`,
      next_action: gate === "BLOCK"
        ? "Vérifier le ticket et l'attestation dans Past"
        : "Réviser les paramètres agents dans Future",
    };
  });
}

// ─── Next Actions dynamiques ──────────────────────────────────────────────────
function deriveNextActions(guardStats: any, incidents: IncidentData[]) {
  type ActionDomain = WorldDomain | "system";
  const actions: Array<{ id: string; priority: string; label: string; domain: ActionDomain; link: string; due: string }> = [];

  // P1 : domaines avec risk_exposure > 30%
  const domains: WorldDomain[] = ["trading", "bank", "ecom"];
  for (const d of domains) {
    const ds = guardStats?.byDomain?.[d];
    if (ds && ds.total > 0 && ds.blocked / ds.total > 0.3) {
      actions.push({
        id: `NA-${d}-block`,
        priority: "P1",
        label: `Taux de blocage élevé — ${d} (${Math.round(ds.blocked / ds.total * 100)}%)`,
        domain: d,
        link: "/past",
        due: "Aujourd'hui",
      });
    }
  }

  // P2 : incidents actifs
  for (const inc of incidents.slice(0, 2)) {
    actions.push({
      id: `NA-${inc.id}`,
      priority: "P2",
      label: inc.next_action ?? inc.title,
      domain: inc.domain,
      link: inc.x108_response === "BLOCK" ? "/past" : "/live",
      due: "Aujourd'hui",
    });
  }

  // P3 : amélioration proof si aucun P1
  if (actions.filter(a => a.priority === "P1").length === 0) {
    actions.push({
      id: "NA-proof",
      priority: "P3",
      label: "Améliorer proof coverage — lancer une simulation",
      domain: "trading",
      link: "/future",
      due: "Cette semaine",
    });
  }

  return actions.slice(0, 5);
}

// ─── Bandeau 4 cartes spec V2 (Infrastructure / Governance / Agent Fabric / Proof Fabric) ──
function SystemOverviewBar({
  guardStats,
  incidents,
  nextActions,
  loading,
}: {
  guardStats: any;
  incidents: IncidentData[];
  nextActions: any[];
  loading: boolean;
}) {
  const total = guardStats?.totalDecisions ?? 0;
  const blocked = guardStats?.totalBlocked ?? 0;
  const held = guardStats?.totalHeld ?? 0;
  const allowed = total - blocked - held;
  const healthScore = total > 0 ? Math.round(((total - blocked) / total) * 100) : 0;
  const scoreColor = healthScore >= 80 ? "oklch(0.72 0.18 145)" : healthScore >= 60 ? "oklch(0.72 0.18 45)" : "oklch(0.65 0.25 25)";
  const activeIncidents = incidents.filter(i => i.status === "active" || i.status === "investigating").length;
  const p1Actions = nextActions.filter(a => a.priority === "P1").length;
  // Agent Fabric
  const agentTotal = (guardStats?.byDomain?.trading?.agentCount ?? 17) + (guardStats?.byDomain?.bank?.agentCount ?? 12) + (guardStats?.byDomain?.ecom?.agentCount ?? 12);
  const agentHealth = loading ? 0 : Math.min(100, 70 + Math.floor(agentTotal / 2));
  const agentColor = agentHealth >= 80 ? "oklch(0.72 0.18 145)" : agentHealth >= 60 ? "oklch(0.72 0.18 45)" : "oklch(0.65 0.25 25)";
  // Proof Fabric
  const proofCoverage = total > 0 ? Math.round((allowed / total) * 100) : 0;
  const proofColor = proofCoverage >= 80 ? "oklch(0.72 0.18 145)" : proofCoverage >= 50 ? "oklch(0.72 0.18 45)" : "oklch(0.65 0.25 25)";

  const cards = [
    {
      key: "infra",
      label: "Infrastructure",
      icon: "⚙",
      score: loading ? null : healthScore,
      unit: "/100",
      color: scoreColor,
      detail: loading ? "Chargement..." : `${total} décisions · ${activeIncidents} incident${activeIncidents !== 1 ? "s" : ""}`,
      sub: loading ? "" : `ALLOW ${allowed} · HOLD ${held} · BLOCK ${blocked}`,
      link: "/live",
    },
    {
      key: "gov",
      label: "Governance X-108",
      icon: "🛡",
      score: loading ? null : (total > 0 ? Math.round((1 - blocked / total) * 100) : 100),
      unit: "/100",
      color: total > 0 && blocked / total > 0.3 ? "oklch(0.65 0.25 25)" : "oklch(0.72 0.18 145)",
      detail: loading ? "Chargement..." : `${p1Actions} action${p1Actions !== 1 ? "s" : ""} P1 · Gate actif`,
      sub: loading ? "" : `Taux blocage ${total > 0 ? Math.round(blocked / total * 100) : 0}%`,
      link: "/past",
    },
    {
      key: "agents",
      label: "Agent Fabric",
      icon: "🤖",
      score: loading ? null : agentHealth,
      unit: "/100",
      color: agentColor,
      detail: loading ? "Chargement..." : `41 agents · 3 domaines`,
      sub: "Trading 17 · Bank 12 · Ecom 12",
      link: "/future",
    },
    {
      key: "proof",
      label: "Proof Fabric",
      icon: "🔐",
      score: loading ? null : proofCoverage,
      unit: "%",
      color: proofColor,
      detail: loading ? "Chargement..." : `${proofCoverage}% couverture proof`,
      sub: loading ? "" : `${total - allowed} sans attestation complète`,
      link: "/past",
    },
  ];

  return (
    <div style={{ borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
      {/* Ligne titre */}
      <div className="flex items-center justify-between px-4 py-1.5"
        style={{ background: "oklch(0.105 0.01 240)", borderBottom: "1px solid oklch(0.14 0.01 240)" }}>
        <span className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.45 0.01 240)" }}>CONTROL — TOUR DE COMMANDEMENT OS4</span>
        <div className="flex items-center gap-2">
          {[{ href: "/live", label: "→ Live" }, { href: "/past", label: "→ Past" }, { href: "/future", label: "→ Future" }].map(l => (
            <Link key={l.href} href={l.href}>
              <span className="px-2 py-0.5 rounded text-[8px] font-mono cursor-pointer"
                style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.55 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
                {l.label}
              </span>
            </Link>
          ))}
        </div>
      </div>
      {/* 4 cartes */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-0" style={{ background: "oklch(0.09 0.01 240)" }}>
        {cards.map((card, i) => (
          <Link key={card.key} href={card.link}>
            <div className="flex flex-col gap-1 px-4 py-3 cursor-pointer"
              style={{
                borderRight: i < 3 ? "1px solid oklch(0.14 0.01 240)" : "none",
                borderBottom: "1px solid oklch(0.14 0.01 240)",
              }}>
              <div className="flex items-center gap-1.5">
                <span className="text-[10px]">{card.icon}</span>
                <span className="text-[8px] font-mono font-bold" style={{ color: "oklch(0.50 0.01 240)" }}>{card.label.toUpperCase()}</span>
              </div>
              <div className="flex items-baseline gap-1">
                <span className="text-2xl font-mono font-bold" style={{ color: card.color }}>
                  {card.score !== null ? card.score : "—"}
                </span>
                <span className="text-[9px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>{card.unit}</span>
              </div>
              <div className="text-[8px] font-mono" style={{ color: "oklch(0.55 0.01 240)" }}>{card.detail}</div>
              <div className="text-[7px] font-mono" style={{ color: "oklch(0.38 0.01 240)" }}>{card.sub}</div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

// ─── Control ──────────────────────────────────────────────────────────────────
export default function Control() {
  const { domain, setMode, setX108Gate, setLastDecisionId, setProofStatus, setSource } = useWorld();
  const domainCfg = DOMAIN_COLORS[domain];
  const [acknowledgedIds, setAcknowledgedIds] = useState<string[]>([]);
  const [activeIncidentFilter, setActiveIncidentFilter] = useState<"all" | "active" | "resolved">("all");
  const [showBottomZone, setShowBottomZone] = useState(false);
  const [bottomTab, setBottomTab] = useState<"domains" | "agents" | "governance" | "proof" | "trends" | "incident" | "lenses">("domains");
  const [watchlist, setWatchlist] = useState<string[]>([]);
  const [watchlistInput, setWatchlistInput] = useState("");

  // ─── Données réelles ─────────────────────────────────────────────────────────
  const { data: guardStats, isLoading: loadingGuard } = trpc.proof.guardStats.useQuery(undefined, {
    refetchInterval: 30000,
  });

  const { data: tickets, isLoading: loadingTickets } = trpc.proof.allTickets.useQuery(
    { limit: 50 },
    { refetchInterval: 30000 }
  );

  const { data: agentRegistry } = trpc.engine.canonicalAgentRegistry.useQuery(undefined, {
    staleTime: 60000,
  });

  const { data: simulationRuns } = trpc.proof.simulationRuns.useQuery(
    { domain: domain as any, limit: 20 },
    { staleTime: 30000 }
  );

  const loading = loadingGuard || loadingTickets;

  // ─── Dériver les matrices santé depuis les données réelles ───────────────────
  const healthMatrices = useMemo(() => {
    const domains: WorldDomain[] = ["trading", "bank", "ecom"];
    return Object.fromEntries(
      domains.map(d => [d, deriveHealthMatrix(d, guardStats, agentRegistry)])
    ) as Record<WorldDomain, HealthMatrixData>;
  }, [guardStats, agentRegistry]);

  // ─── Dériver les incidents depuis les tickets BLOCK/HOLD ─────────────────────
  const allIncidents = useMemo(() => deriveIncidents(tickets ?? []), [tickets]);

  // ─── Dériver les next actions ────────────────────────────────────────────────
  const nextActions = useMemo(
    () => deriveNextActions(guardStats, allIncidents),
    [guardStats, allIncidents]
  );

  const filteredIncidents = useMemo(() => {
    return allIncidents.filter(i => {
      if (activeIncidentFilter === "active") return i.status === "active" || i.status === "investigating";
      if (activeIncidentFilter === "resolved") return i.status === "resolved" || i.status === "suppressed";
      return true;
    }).filter(i => !acknowledgedIds.includes(i.id));
  }, [allIncidents, activeIncidentFilter, acknowledgedIds]);

  const priorityColor: Record<string, string> = {
    P1: "oklch(0.65 0.25 25)",
    P2: "oklch(0.72 0.18 45)",
    P3: "oklch(0.55 0.01 240)",
  };

  // ─── Propagation vers StatusRail ───────────────────────────────────────────
  useEffect(() => {
    setMode("MIXED");
    setSource("guard_stats");
  }, [setMode, setSource]);

  useEffect(() => {
    // Propager le gate du domaine actif (depuis les incidents)
    const domainIncidents = allIncidents.filter(i => i.domain === domain);
    const hasBlock = domainIncidents.some(i => i.x108_response === "BLOCK");
    const hasHold = domainIncidents.some(i => i.x108_response === "HOLD");
    setX108Gate(hasBlock ? "BLOCK" : hasHold ? "HOLD" : "ALLOW");
    // Propager le dernier decision_id depuis les tickets
    const lastTicket = tickets?.[0];
    if (lastTicket) setLastDecisionId(lastTicket.intentId);
    // Proof status global
    const hm = healthMatrices[domain];
    const proofScore = hm?.proof_coverage?.score ?? 0;
    setProofStatus(proofScore >= 80 ? "COMPLETE" : proofScore >= 50 ? "PARTIAL" : "MISSING");
  }, [allIncidents, domain, tickets, healthMatrices, setX108Gate, setLastDecisionId, setProofStatus]);

  return (
    <div className="flex flex-col gap-0" style={{ minHeight: "calc(100vh - 120px)" }}>

      {/* ── Header Control ───────────────────────────────────────────────────── */}
      <SystemOverviewBar
        guardStats={guardStats}
        incidents={allIncidents}
        nextActions={nextActions}
        loading={loading}
      />

      {/* ── Layout principal ─────────────────────────────────────────────────── */}
      <div className="p-4 flex flex-col gap-4">

        {/* ── 3 matrices santé (Trading / Bank / Ecom) ────────────────────── */}
        <div>
          <div className="text-[9px] font-mono mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>
            Matrices de santé — données réelles
          </div>
          {loading ? (
            <div className="flex items-center justify-center h-24">
              <div className="flex flex-col items-center gap-2">
                <div className="w-5 h-5 border-2 rounded-full animate-spin"
                  style={{ borderColor: "oklch(0.72 0.18 145)", borderTopColor: "transparent" }} />
                <span className="text-[9px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>Chargement DB...</span>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
              {(["trading", "bank", "ecom"] as WorldDomain[]).map(d => (
                <HealthMatrix key={d} data={healthMatrices[d]} />
              ))}
            </div>
          )}
        </div>

        {/* ── Incidents + Next Actions ─────────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">

          {/* Incidents */}
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <div className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.45 0.01 240)" }}>
                Incidents & Alertes — {allIncidents.length} détectés
              </div>
              <div className="flex gap-1">
                {(["all", "active", "resolved"] as const).map(f => (
                  <button key={f} onClick={() => setActiveIncidentFilter(f)}
                    className="px-2 py-0.5 rounded text-[8px] font-mono"
                    style={{
                      background: activeIncidentFilter === f ? "oklch(0.65 0.25 25 / 0.12)" : "transparent",
                      border: `1px solid ${activeIncidentFilter === f ? "oklch(0.65 0.25 25 / 0.40)" : "transparent"}`,
                      color: activeIncidentFilter === f ? "oklch(0.65 0.25 25)" : "oklch(0.50 0.01 240)",
                    }}>
                    {f}
                  </button>
                ))}
              </div>
            </div>
            {loading ? (
              <div className="text-[9px] font-mono p-4 text-center" style={{ color: "oklch(0.40 0.01 240)" }}>
                Chargement des incidents...
              </div>
            ) : filteredIncidents.length === 0 ? (
              <div className="p-4 rounded text-center" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.16 0.01 240)" }}>
                <div className="text-[10px] font-mono" style={{ color: "oklch(0.72 0.18 145)" }}>
                  ✓ Aucun incident actif
                </div>
                {tickets && tickets.length === 0 && (
                  <div className="text-[9px] font-mono mt-1" style={{ color: "oklch(0.40 0.01 240)" }}>
                    Lancez une simulation dans Future pour générer des décisions
                  </div>
                )}
              </div>
            ) : (
              <div className="flex flex-col gap-1.5">
                {filteredIncidents.map(inc => (
                  <IncidentCard
                    key={inc.id}
                    incident={inc}
                    onAcknowledge={() => setAcknowledgedIds(prev => [...prev, inc.id])}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Next Actions */}
          <div className="flex flex-col gap-2">
            <div className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.45 0.01 240)" }}>
              Actions Prioritaires
            </div>
            <div className="rounded overflow-hidden" style={{ border: "1px solid oklch(0.18 0.01 240)" }}>
              {nextActions.length === 0 ? (
                <div className="p-4 text-center">
                  <div className="text-[10px] font-mono" style={{ color: "oklch(0.72 0.18 145)" }}>
                    ✓ Aucune action prioritaire
                  </div>
                </div>
              ) : (
                <div className="flex flex-col gap-0.5 p-1.5">
                  {nextActions.map(action => {
                    const dom = DOMAIN_COLORS[action.domain as WorldDomain];
                    const pColor = priorityColor[action.priority] ?? "oklch(0.55 0.01 240)";
                    return (
                      <Link key={action.id} href={action.link}>
                        <div className="flex items-center gap-2 px-2 py-1.5 rounded cursor-pointer"
                          style={{ background: "oklch(0.115 0.01 240)" }}>
                          <span className="text-[8px] font-mono font-bold px-1 rounded"
                            style={{ background: `${pColor}15`, color: pColor }}>{action.priority}</span>
                          <span className="text-[9px]">{dom.icon}</span>
                          <span className="text-[9px] font-mono flex-1 truncate" style={{ color: "oklch(0.70 0.01 240)" }}>
                            {action.label}
                          </span>
                          <span className="text-[8px] font-mono shrink-0" style={{ color: "oklch(0.40 0.01 240)" }}>
                            {action.due}
                          </span>
                          <span className="text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>→</span>
                        </div>
                      </Link>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Stats par domaine */}
            <div className="rounded overflow-hidden" style={{ border: "1px solid oklch(0.18 0.01 240)" }}>
              <div className="px-3 py-2 text-[9px] font-mono font-bold"
                style={{ background: "oklch(0.12 0.01 240)", borderBottom: "1px solid oklch(0.16 0.01 240)", color: "oklch(0.55 0.01 240)" }}>
                Stats par domaine
              </div>
              <div className="p-2 flex flex-col gap-1">
                {(["trading", "bank", "ecom"] as WorldDomain[]).map(d => {
                  const ds = guardStats?.byDomain?.[d] ?? { total: 0, blocked: 0, held: 0 };
                  const dom = DOMAIN_COLORS[d];
                  const blockRate = ds.total > 0 ? Math.round(ds.blocked / ds.total * 100) : 0;
                  return (
                    <div key={d} className="flex items-center gap-2 px-2 py-1 rounded"
                      style={{ background: "oklch(0.115 0.01 240)" }}>
                      <span className="text-[9px]">{dom.icon}</span>
                      <span className="text-[9px] font-mono font-bold flex-1" style={{ color: dom.accent }}>
                        {dom.label}
                      </span>
                      <span className="text-[9px] font-mono" style={{ color: "oklch(0.55 0.01 240)" }}>
                        {ds.total} déc.
                      </span>
                      <span className="text-[9px] font-mono" style={{
                        color: blockRate > 20 ? "oklch(0.65 0.25 25)" : blockRate > 10 ? "oklch(0.72 0.18 45)" : "oklch(0.72 0.18 145)"
                      }}>
                        {blockRate}% bloqué
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* ── Liens deep recovery ──────────────────────────────────────────── */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
          {[
            { label: "Proof Recovery", desc: "Runs sans attestation", link: "/past", color: "#a78bfa" },
            { label: "Agent Recovery", desc: "Agents en erreur", link: "/future", color: "oklch(0.72 0.18 145)" },
            { label: "Incident Review", desc: "Décisions BLOCK/HOLD", link: "/past", color: "oklch(0.65 0.25 25)" },
            { label: "Live Monitor", desc: "Console temps réel", link: "/live", color: "oklch(0.72 0.18 45)" },
          ].map(item => (
            <Link key={item.label} href={item.link}>
              <div className="p-3 rounded cursor-pointer"
                style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.16 0.01 240)" }}>
                <div className="text-[10px] font-mono font-bold mb-0.5" style={{ color: item.color }}>
                  {item.label}
                </div>
                <div className="text-[9px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>
                  {item.desc}
                </div>
              </div>
            </Link>
          ))}
        </div>

        {/* ── Watchlist ─────────────────────────────────────────────────── */}
        <div className="rounded" style={{ border: "1px solid oklch(0.18 0.01 240)" }}>
          <div className="flex items-center justify-between px-3 py-2"
            style={{ background: "oklch(0.12 0.01 240)", borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
            <span className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.55 0.01 240)" }}>WATCHLIST</span>
            <span className="text-[8px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>{watchlist.length} épinglé{watchlist.length !== 1 ? "s" : ""}</span>
          </div>
          <div className="p-2">
            <div className="flex gap-2 mb-2">
              <input
                value={watchlistInput}
                onChange={e => setWatchlistInput(e.target.value)}
                onKeyDown={e => {
                  if (e.key === "Enter" && watchlistInput.trim()) {
                    setWatchlist(prev => [...prev, watchlistInput.trim()]);
                    setWatchlistInput("");
                  }
                }}
                placeholder="Decision ID à surveiller..."
                className="flex-1 px-2 py-1 rounded text-[9px] font-mono"
                style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.20 0.01 240)", color: "oklch(0.75 0.01 240)", outline: "none" }}
              />
              <button
                onClick={() => { if (watchlistInput.trim()) { setWatchlist(prev => [...prev, watchlistInput.trim()]); setWatchlistInput(""); } }}
                className="px-2 py-1 rounded text-[9px] font-mono"
                style={{ background: domainCfg.accent + "22", color: domainCfg.accent, border: `1px solid ${domainCfg.accent}44` }}>
                +
              </button>
            </div>
            {watchlist.length === 0 ? (
              <div className="text-[9px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>Aucun ID épinglé — entrez un Decision ID pour surveiller</div>
            ) : (
              <div className="flex flex-col gap-0.5">
                {watchlist.map(id => {
                  const match = tickets?.find(t => t.intentId?.includes(id));
                  const gate = match?.decision ?? "UNKNOWN";
                  const gColor = gate === "ALLOW" ? "oklch(0.72 0.18 145)" : gate === "HOLD" ? "oklch(0.72 0.18 45)" : gate === "BLOCK" ? "oklch(0.65 0.25 25)" : "oklch(0.45 0.01 240)";
                  return (
                    <div key={id} className="flex items-center gap-2 px-2 py-1 rounded"
                      style={{ background: "oklch(0.115 0.01 240)", border: match ? `1px solid ${gColor}33` : "1px solid oklch(0.16 0.01 240)" }}>
                      <span className="text-[9px] font-mono flex-1 truncate" style={{ color: "oklch(0.70 0.01 240)" }}>{id}</span>
                      {match && (
                        <span className="text-[8px] font-mono font-bold px-1 rounded" style={{ background: gColor + "22", color: gColor }}>{gate}</span>
                      )}
                      {!match && (
                        <span className="text-[8px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>non trouvé</span>
                      )}
                      <button onClick={() => setWatchlist(prev => prev.filter(w => w !== id))}
                        className="text-[8px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>✕</button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ─── Zone basse 6 onglets ──────────────────────────────────────────── */}
      <div style={{ borderTop: "1px solid oklch(0.16 0.01 240)" }}>
        <button
          onClick={() => setShowBottomZone(v => !v)}
          className="w-full flex items-center justify-between px-4 py-2 text-[9px] font-mono"
          style={{ background: "oklch(0.10 0.01 240)", color: "oklch(0.50 0.01 240)" }}>
          <span className="font-bold">ZONE BASSE — Domains · Agents · Governance · Proof · Trends · Incident Detail</span>
          <span>{showBottomZone ? "▲ Réduire" : "▼ Développer"}</span>
        </button>

        {showBottomZone && (
          <div style={{ background: "oklch(0.08 0.01 240)" }}>
            <div className="flex overflow-x-auto" style={{ borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
              {(["domains", "agents", "governance", "proof", "trends", "incident", "lenses"] as const).map(tab => (
                <button key={tab} onClick={() => setBottomTab(tab)}
                  className="px-4 py-1.5 text-[9px] font-mono font-bold shrink-0"
                  style={{
                    background: bottomTab === tab ? "oklch(0.12 0.01 240)" : "transparent",
                    color: bottomTab === tab ? domainCfg.accent : "oklch(0.45 0.01 240)",
                    borderBottom: bottomTab === tab ? `2px solid ${domainCfg.accent}` : "2px solid transparent",
                  }}>
                  {tab === "lenses" ? "Lenses" : tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            <div className="p-4" style={{ maxHeight: "400px", overflowY: "auto" }}>

              {bottomTab === "domains" && (
                <div className="grid grid-cols-3 gap-3">
                  {(["trading", "bank", "ecom"] as WorldDomain[]).map(d => {
                    const ds = guardStats?.byDomain?.[d] ?? { total: 0, blocked: 0, held: 0 };
                    const dom = DOMAIN_COLORS[d];
                    const blockRate = ds.total > 0 ? Math.round(ds.blocked / ds.total * 100) : 0;
                    const holdRate = ds.total > 0 ? Math.round(ds.held / ds.total * 100) : 0;
                    const allowRate = ds.total > 0 ? 100 - blockRate - holdRate : 0;
                    return (
                      <div key={d} className="rounded p-3" style={{ background: "oklch(0.11 0.01 240)", border: `1px solid ${dom.accent}33` }}>
                        <div className="flex items-center gap-2 mb-2">
                          <span>{dom.icon}</span>
                          <span className="text-[10px] font-mono font-bold" style={{ color: dom.accent }}>{dom.label}</span>
                        </div>
                        <div className="flex flex-col gap-1">
                          <div className="flex justify-between text-[9px] font-mono">
                            <span style={{ color: "oklch(0.55 0.01 240)" }}>Total</span>
                            <span className="font-bold text-foreground">{ds.total}</span>
                          </div>
                          <div className="flex justify-between text-[9px] font-mono">
                            <span style={{ color: "oklch(0.72 0.18 145)" }}>ALLOW</span>
                            <span>{allowRate}%</span>
                          </div>
                          <div className="flex justify-between text-[9px] font-mono">
                            <span style={{ color: "oklch(0.72 0.18 45)" }}>HOLD</span>
                            <span>{holdRate}%</span>
                          </div>
                          <div className="flex justify-between text-[9px] font-mono">
                            <span style={{ color: "oklch(0.65 0.25 25)" }}>BLOCK</span>
                            <span style={{ color: blockRate > 20 ? "oklch(0.65 0.25 25)" : "inherit" }}>{blockRate}%</span>
                          </div>
                        </div>
                        <Link href="/past">
                          <div className="mt-2 text-[8px] font-mono cursor-pointer" style={{ color: dom.accent }}>Voir dans Past →</div>
                        </Link>
                      </div>
                    );
                  })}
                </div>
              )}

              {bottomTab === "agents" && (
                <div className="flex flex-col gap-2">
                  {(["trading", "bank", "ecom"] as WorldDomain[]).map(d => {
                    // canonicalAgentRegistry retourne des strings — on les enrichit côté client
                    const rawNames: string[] = (agentRegistry?.[d] ?? []) as unknown as string[];
                    const agents = rawNames.map((name: string) => {
                      const n = name.toLowerCase();
                      let layer = "OBS";
                      if (n.includes("proof") || n.includes("attestation") || n.includes("trace") || n.includes("integrity")) layer = "PRF";
                      else if (n.includes("guard") || n.includes("policy") || n.includes("human") || n.includes("ticket") || n.includes("readiness") || n.includes("severity")) layer = "GOV";
                      else if (n.includes("conflict") || n.includes("contradiction") || n.includes("narrative") || n.includes("mismatch") || n.includes("unknown") || n.includes("friction")) layer = "CTR";
                      else if (n.includes("fraud") || n.includes("pattern") || n.includes("regime") || n.includes("stress") || n.includes("affordability") || n.includes("margin") || n.includes("roas") || n.includes("risk") || n.includes("prediction")) layer = "INT";
                      return { id: name, name, layer };
                    });
                    const dom = DOMAIN_COLORS[d];
                    return (
                      <div key={d}>
                        <div className="text-[9px] font-mono font-bold mb-1" style={{ color: dom.accent }}>
                          {dom.icon} {dom.label} — {agents.length} agents
                        </div>
                        <div className="grid grid-cols-2 gap-1">
                          {agents.slice(0, 8).map((a) => (
                            <div key={a.id} className="flex items-center gap-1.5 px-2 py-1 rounded"
                              style={{ background: "oklch(0.115 0.01 240)" }}>
                              <div className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: "oklch(0.72 0.18 145)" }} />
                              <span className="text-[8px] font-mono truncate" style={{ color: "oklch(0.65 0.01 240)" }}>{a.name}</span>
                              <span className="text-[7px] font-mono shrink-0 ml-auto" style={{ color: "oklch(0.40 0.01 240)" }}>{a.layer}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {bottomTab === "governance" && (
                <div className="grid grid-cols-2 gap-3">
                  <div className="rounded p-3" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
                    <div className="text-[9px] font-mono font-bold mb-2" style={{ color: "oklch(0.55 0.01 240)" }}>RÈGLES X-108</div>
                    <div className="flex flex-col gap-1 text-[9px] font-mono">
                      <div className="flex justify-between">
                        <span style={{ color: "oklch(0.55 0.01 240)" }}>Gate actif</span>
                        <span className="font-bold" style={{ color: "oklch(0.72 0.18 145)" }}>X-108 v2</span>
                      </div>
                      <div className="flex justify-between">
                        <span style={{ color: "oklch(0.55 0.01 240)" }}>Mode</span>
                        <span className="font-bold text-foreground">STRICT</span>
                      </div>
                      <div className="flex justify-between">
                        <span style={{ color: "oklch(0.55 0.01 240)" }}>Seuil BLOCK</span>
                        <span className="font-bold text-foreground">S3+</span>
                      </div>
                      <div className="flex justify-between">
                        <span style={{ color: "oklch(0.55 0.01 240)" }}>Proof requis</span>
                        <span className="font-bold text-foreground">3/4</span>
                      </div>
                    </div>
                  </div>
                  <div className="rounded p-3" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
                    <div className="text-[9px] font-mono font-bold mb-2" style={{ color: "oklch(0.55 0.01 240)" }}>INCIDENTS ACTIFS</div>
                    <div className="text-[11px] font-mono font-bold" style={{ color: allIncidents.length > 0 ? "oklch(0.65 0.25 25)" : "oklch(0.72 0.18 145)" }}>
                      {allIncidents.length}
                    </div>
                    <div className="text-[9px] font-mono mt-1" style={{ color: "oklch(0.45 0.01 240)" }}>
                      {allIncidents.filter(i => i.severity === "S4").length} S4 · {allIncidents.filter(i => i.severity === "S3").length} S3
                    </div>
                  </div>
                </div>
              )}

              {bottomTab === "proof" && (
                <div className="flex flex-col gap-2">
                  <div className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.55 0.01 240)" }}>PROOF COVERAGE PAR DOMAINE</div>
                  {(["trading", "bank", "ecom"] as WorldDomain[]).map(d => {
                    const matrix = healthMatrices[d];
                    const dom = DOMAIN_COLORS[d];
                    return (
                      <div key={d} className="flex items-center gap-3 px-3 py-2 rounded"
                        style={{ background: "oklch(0.11 0.01 240)" }}>
                        <span>{dom.icon}</span>
                        <span className="text-[9px] font-mono font-bold w-16" style={{ color: dom.accent }}>{dom.label}</span>
                        <div className="flex-1 h-1.5 rounded-full" style={{ background: "oklch(0.18 0.01 240)" }}>
                          <div className="h-full rounded-full" style={{
                            width: `${matrix?.proof_coverage?.score ?? 0}%`,
                            background: (matrix?.proof_coverage?.score ?? 0) >= 80 ? "oklch(0.72 0.18 145)" : "oklch(0.72 0.18 45)"
                          }} />
                        </div>
                        <span className="text-[9px] font-mono w-8 text-right" style={{ color: "oklch(0.65 0.01 240)" }}>
                          {matrix?.proof_coverage?.score ?? 0}%
                        </span>
                      </div>
                    );
                  })}
                  {simulationRuns && simulationRuns.length > 0 && (
                    <div className="mt-2">
                      <div className="text-[9px] font-mono font-bold mb-1" style={{ color: "oklch(0.55 0.01 240)" }}>DERNIERS RUNS</div>
                      {simulationRuns.slice(0, 5).map((run: any) => (
                        <div key={run.id} className="flex items-center gap-2 px-2 py-1 rounded mb-0.5"
                          style={{ background: "oklch(0.115 0.01 240)" }}>
                          <span className="text-[8px] font-mono truncate flex-1" style={{ color: "oklch(0.60 0.01 240)" }}>
                            {run.runId?.slice(0, 24)}…
                          </span>
                          <span className="text-[8px] font-mono" style={{ color: run.x108Gate === "ALLOW" ? "oklch(0.72 0.18 145)" : run.x108Gate === "BLOCK" ? "oklch(0.65 0.25 25)" : "oklch(0.72 0.18 45)" }}>
                            {run.x108Gate}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {bottomTab === "trends" && (
                <div className="grid grid-cols-3 gap-3">
                  {(["trading", "bank", "ecom"] as WorldDomain[]).map(d => {
                    const matrix = healthMatrices[d];
                    const dom = DOMAIN_COLORS[d];
                    return (
                      <div key={d} className="rounded p-3" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.16 0.01 240)" }}>
                        <div className="flex items-center gap-1 mb-2">
                          <span>{dom.icon}</span>
                          <span className="text-[9px] font-mono font-bold" style={{ color: dom.accent }}>{dom.label}</span>
                        </div>
                        <div className="flex flex-col gap-1 text-[9px] font-mono">
                          <div className="flex justify-between">
                            <span style={{ color: "oklch(0.55 0.01 240)" }}>Agent Health</span>
                            <span style={{ color: (matrix?.agent_health?.score ?? 0) >= 80 ? "oklch(0.72 0.18 145)" : "oklch(0.72 0.18 45)" }}>
                              {matrix?.agent_health?.score ?? 0}% {matrix?.agent_health?.trend === "up" ? "↑" : matrix?.agent_health?.trend === "down" ? "↓" : "→"}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span style={{ color: "oklch(0.55 0.01 240)" }}>Proof</span>
                            <span style={{ color: (matrix?.proof_coverage?.score ?? 0) >= 80 ? "oklch(0.72 0.18 145)" : "oklch(0.72 0.18 45)" }}>
                              {matrix?.proof_coverage?.score ?? 0}% {matrix?.proof_coverage?.trend === "up" ? "↑" : "↓"}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span style={{ color: "oklch(0.55 0.01 240)" }}>Risk</span>
                            <span style={{ color: (matrix?.risk_exposure?.score ?? 0) > 20 ? "oklch(0.65 0.25 25)" : "oklch(0.72 0.18 145)" }}>
                              {matrix?.risk_exposure?.score ?? 0}% {matrix?.risk_exposure?.trend === "up" ? "↑" : "→"}
                            </span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {bottomTab === "incident" && (
                <div className="flex flex-col gap-2">
                  {allIncidents.length === 0 ? (
                    <div className="text-[10px] font-mono text-center p-4" style={{ color: "oklch(0.72 0.18 145)" }}>
                      ✓ Aucun incident actif
                    </div>
                  ) : (
                    allIncidents.map(inc => (
                      <div key={inc.id} className="rounded p-3" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-[8px] font-mono font-bold px-1 rounded"
                            style={{ background: inc.severity === "S4" ? "oklch(0.65 0.25 25 / 0.15)" : "oklch(0.72 0.18 45 / 0.15)",
                              color: inc.severity === "S4" ? "oklch(0.65 0.25 25)" : "oklch(0.72 0.18 45)" }}>
                            {inc.severity}
                          </span>
                          <span className="text-[9px] font-mono font-bold flex-1 truncate" style={{ color: "oklch(0.75 0.01 240)" }}>{inc.title}</span>
                          <span className="text-[8px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>{inc.id}</span>
                        </div>
                        <div className="text-[9px] font-mono mb-1" style={{ color: "oklch(0.55 0.01 240)" }}>{inc.description}</div>
                        <div className="flex items-center gap-2">
                          <span className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>Action : {inc.next_action}</span>
                          <Link href="/past">
                            <span className="text-[8px] font-mono cursor-pointer" style={{ color: domainCfg.accent }}>→ Past</span>
                          </Link>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}

              {bottomTab === "lenses" && (() => {
                const allTicketsList = tickets ?? [];
                // Silent agents : agents du registre absents des derniers tickets
                // canonicalAgentRegistry retourne des strings — on les enrichit côté client
                const rawDomainNames: string[] = (agentRegistry?.[domain] ?? []) as unknown as string[];
                const domainAgents = rawDomainNames.map((name: string) => {
                  const n = name.toLowerCase();
                  let layer = "OBS";
                  if (n.includes("proof") || n.includes("attestation") || n.includes("trace") || n.includes("integrity")) layer = "PRF";
                  else if (n.includes("guard") || n.includes("policy") || n.includes("human") || n.includes("ticket") || n.includes("readiness") || n.includes("severity")) layer = "GOV";
                  else if (n.includes("conflict") || n.includes("contradiction") || n.includes("narrative") || n.includes("mismatch") || n.includes("unknown") || n.includes("friction")) layer = "CTR";
                  else if (n.includes("fraud") || n.includes("pattern") || n.includes("regime") || n.includes("stress") || n.includes("affordability") || n.includes("margin") || n.includes("roas") || n.includes("risk") || n.includes("prediction")) layer = "INT";
                  return { id: name, name, layer };
                });
                const recentTickets = allTicketsList.filter((t: any) => t.domain === domain).slice(0, 20);
                const activeAgentNames = new Set(
                  recentTickets.flatMap((t: any) => {
                    const audit = (t.auditTrail as any) ?? {};
                    return (audit.agents_involved ?? []) as string[];
                  })
                );
                const silentAgents = domainAgents.filter((a) => !activeAgentNames.has(a.name) && !activeAgentNames.has(a.id));

                // Contradiction spikes : tickets avec contradictions > 0
                const contSpikes = allTicketsList.filter((t: any) => {
                  const env = (t.envelope as any) ?? {};
                  return (env.contradictions ?? 0) > 0 || (typeof env.contradictions === "number" && env.contradictions > 0);
                }).slice(0, 10);

                // Proof gaps : tickets sans merkle_root
                const proofGaps = allTicketsList.filter((t: any) => !(t.auditTrail as any)?.merkle_root).slice(0, 10);

                // Missing links : tickets sans attestation_ref
                const missingLinks = allTicketsList.filter((t: any) => {
                  const env = (t.envelope as any) ?? {};
                  return !env.attestation_ref && !t.attestationRef;
                }).slice(0, 10);

                return (
                  <div className="flex flex-col gap-4">
                    <div className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.55 0.01 240)" }}>
                      LENSES — Analyse diagnostique du domaine {domain.toUpperCase()}
                    </div>
                    <div className="text-[8px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>
                      Ces lenses identifient les anomalies structurelles invisibles dans les vues standard : agents silencieux, pics de contradiction, lacunes de preuve, liens manquants.
                    </div>

                    <div className="grid grid-cols-2 gap-3">

                      {/* Silent Agents */}
                      <div className="rounded p-3" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
                        <div className="flex items-center justify-between mb-2">
                          <div className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.72 0.18 45)" }}>🔇 Silent Agents</div>
                          <span className="text-[10px] font-mono font-bold" style={{ color: silentAgents.length > 0 ? "oklch(0.72 0.18 45)" : "oklch(0.72 0.18 145)" }}>{silentAgents.length}</span>
                        </div>
                        <div className="text-[8px] font-mono mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>
                          Agents enregistrés n'ayant pas participé aux 20 dernières décisions.
                        </div>
                        {silentAgents.length === 0 ? (
                          <div className="text-[8px] font-mono" style={{ color: "oklch(0.72 0.18 145)" }}>✓ Tous les agents actifs</div>
                        ) : (
                          <div className="flex flex-col gap-0.5">
                            {silentAgents.slice(0, 6).map((a: any) => (
                              <div key={a.id ?? a.name} className="text-[8px] font-mono px-2 py-0.5 rounded" style={{ background: "oklch(0.13 0.01 240)", color: "oklch(0.60 0.01 240)" }}>
                                {a.name} <span style={{ color: "oklch(0.40 0.01 240)" }}>({a.layer?.slice(0, 3).toUpperCase() ?? "—"})</span>
                              </div>
                            ))}
                            {silentAgents.length > 6 && (
                              <div className="text-[8px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>+{silentAgents.length - 6} autres</div>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Contradiction Spikes */}
                      <div className="rounded p-3" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
                        <div className="flex items-center justify-between mb-2">
                          <div className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.65 0.25 25)" }}>⚡ Contradiction Spikes</div>
                          <span className="text-[10px] font-mono font-bold" style={{ color: contSpikes.length > 0 ? "oklch(0.65 0.25 25)" : "oklch(0.72 0.18 145)" }}>{contSpikes.length}</span>
                        </div>
                        <div className="text-[8px] font-mono mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>
                          Décisions avec contradictions inter-agents détectées.
                        </div>
                        {contSpikes.length === 0 ? (
                          <div className="text-[8px] font-mono" style={{ color: "oklch(0.72 0.18 145)" }}>✓ Aucun spike détecté</div>
                        ) : (
                          <div className="flex flex-col gap-0.5">
                            {contSpikes.slice(0, 5).map((t: any) => (
                              <Link key={t.id} href="/past">
                                <div className="text-[8px] font-mono px-2 py-0.5 rounded cursor-pointer" style={{ background: "oklch(0.13 0.01 240)", color: "oklch(0.65 0.25 25)" }}>
                                  #{t.id} {t.decision} — {t.intentId?.slice(0, 20)}…
                                </div>
                              </Link>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Proof Gaps */}
                      <div className="rounded p-3" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
                        <div className="flex items-center justify-between mb-2">
                          <div className="text-[9px] font-mono font-bold" style={{ color: "#a78bfa" }}>🔐 Proof Gaps</div>
                          <span className="text-[10px] font-mono font-bold" style={{ color: proofGaps.length > 0 ? "#a78bfa" : "oklch(0.72 0.18 145)" }}>{proofGaps.length}</span>
                        </div>
                        <div className="text-[8px] font-mono mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>
                          Décisions sans attestation Merkle complète — preuve incomplète.
                        </div>
                        {proofGaps.length === 0 ? (
                          <div className="text-[8px] font-mono" style={{ color: "oklch(0.72 0.18 145)" }}>✓ Toutes les preuves complètes</div>
                        ) : (
                          <div className="flex flex-col gap-0.5">
                            {proofGaps.slice(0, 5).map((t: any) => (
                              <Link key={t.id} href="/past">
                                <div className="text-[8px] font-mono px-2 py-0.5 rounded cursor-pointer" style={{ background: "oklch(0.13 0.01 240)", color: "#a78bfa" }}>
                                  #{t.id} {t.decision} — {t.intentId?.slice(0, 20)}…
                                </div>
                              </Link>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Missing Links */}
                      <div className="rounded p-3" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
                        <div className="flex items-center justify-between mb-2">
                          <div className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.65 0.18 240)" }}>🔗 Missing Links</div>
                          <span className="text-[10px] font-mono font-bold" style={{ color: missingLinks.length > 0 ? "oklch(0.65 0.18 240)" : "oklch(0.72 0.18 145)" }}>{missingLinks.length}</span>
                        </div>
                        <div className="text-[8px] font-mono mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>
                          Décisions sans référence d'attestation — chaîne de preuve brisée.
                        </div>
                        {missingLinks.length === 0 ? (
                          <div className="text-[8px] font-mono" style={{ color: "oklch(0.72 0.18 145)" }}>✓ Toutes les attestations présentes</div>
                        ) : (
                          <div className="flex flex-col gap-0.5">
                            {missingLinks.slice(0, 5).map((t: any) => (
                              <Link key={t.id} href="/past">
                                <div className="text-[8px] font-mono px-2 py-0.5 rounded cursor-pointer" style={{ background: "oklch(0.13 0.01 240)", color: "oklch(0.65 0.18 240)" }}>
                                  #{t.id} {t.decision} — {t.intentId?.slice(0, 20)}…
                                </div>
                              </Link>
                            ))}
                          </div>
                        )}
                      </div>

                    </div>
                  </div>
                );
              })()}

            </div>
          </div>
        )}
      </div>
    </div>
  );
}
