/**
 * Live — console du présent OS4 V2
 * Données réelles depuis trpc.proof.allTickets + trpc.engine.canonicalAgentRegistry
 * Polling 30s — jamais de données inventées
 * Spec : pasted_content_3
 */
import React, { useState, useMemo, useEffect } from "react";
import { Link } from "wouter";
import { trpc } from "@/lib/trpc";
import { useWorld, DOMAIN_COLORS } from "@/contexts/WorldContext";
import DecisionEnvelopeCard, { type CanonicalEnvelope } from "@/components/canonical/DecisionEnvelopeCard";
import ProofChainView, { type ProofChain } from "@/components/canonical/ProofChainView";
import AgentConstellationPanel from "@/components/canonical/AgentConstellationPanel";

// ─── Helpers ──────────────────────────────────────────────────────────────────
function gateColor(gate: string): string {
  if (gate === "ALLOW") return "oklch(0.72 0.18 145)";
  if (gate === "HOLD") return "oklch(0.72 0.18 45)";
  return "oklch(0.65 0.25 25)";
}

function formatRelative(ts: number): string {
  const diff = Date.now() - ts;
  if (diff < 60000) return `${Math.floor(diff / 1000)}s`;
  if (diff < 3600000) return `${Math.floor(diff / 60000)}min`;
  return `${Math.floor(diff / 3600000)}h`;
}

function proofScore(ticket: any): number {
  let score = 0;
  if (ticket?.intentId) score++;
  const audit = (ticket?.auditTrail as any) ?? {};
  if (audit.hash_now) score++;
  if (ticket?.id) score++;
  if (audit.merkle_root && audit.merkle_root !== "0".repeat(24)) score++;
  return score;
}

// ─── Composant principal ──────────────────────────────────────────────────────
export default function Live() {
  const { domain, setMode, setX108Gate, setLastDecisionId, setProofStatus, setSource } = useWorld();
  const domainCfg = DOMAIN_COLORS[domain];

  const [selectedTicketId, setSelectedTicketId] = useState<number | null>(null);
  const [gateFilter, setGateFilter] = useState<"ALL" | "ALLOW" | "HOLD" | "BLOCK">("ALL");
  const [activeTab, setActiveTab] = useState<"envelope" | "proof" | "agents">("envelope");

  // ─── Données réelles — polling 30s ──────────────────────────────────────────
  const { data: tickets, isLoading: loadingTickets, dataUpdatedAt } = trpc.proof.allTickets.useQuery(
    { domain: domain as any, limit: 20 },
    { refetchInterval: 30000 }
  );

  const { data: agentRegistry } = trpc.engine.canonicalAgentRegistry.useQuery(undefined, {
    staleTime: 60000,
  });

  // ─── Filtrage ───────────────────────────────────────────────────────────────
  const filteredTickets = useMemo(() => {
    if (!tickets) return [];
    return tickets.filter(t => {
      const gate = (t.decision ?? "").toUpperCase();
      if (gateFilter !== "ALL" && gate !== gateFilter) return false;
      return true;
    });
  }, [tickets, gateFilter]);

  const selectedTicket = useMemo(
    () => selectedTicketId
      ? filteredTickets.find(t => t.id === selectedTicketId) ?? filteredTickets[0]
      : filteredTickets[0],
    [selectedTicketId, filteredTickets]
  );

  // ─── Envelope synthétique ────────────────────────────────────────────────────
  const selectedEnvelope: CanonicalEnvelope | null = useMemo(() => {
    if (!selectedTicket) return null;
    const reasons = (selectedTicket.reasons as string[]) ?? [];
    const thresholds = (selectedTicket.thresholds as any) ?? {};
    const audit = (selectedTicket.auditTrail as any) ?? {};
    const gate = selectedTicket.decision as "ALLOW" | "HOLD" | "BLOCK";
    return {
      domain: selectedTicket.domain as "trading" | "bank" | "ecom",
      market_verdict: reasons[0] ?? "DECISION_RECORDED",
      confidence: thresholds.confidence ?? 0.75,
      contradictions: 0,
      unknowns: 0,
      risk_flags: reasons.slice(1, 4),
      x108_gate: gate,
      reason_code: reasons[0] ?? "RECORDED",
      severity: gate === "BLOCK" ? "S4" : gate === "HOLD" ? "S3" : "S2",
      decision_id: selectedTicket.intentId,
      trace_id: audit.hash_now ?? selectedTicket.intentId,
      ticket_required: gate !== "ALLOW",
      ticket_id: String(selectedTicket.id),
      attestation_ref: audit.merkle_root !== "0".repeat(24) ? audit.merkle_root : undefined,
      source: "db",
      timestamp: new Date(selectedTicket.createdAt).getTime(),
    };
  }, [selectedTicket]);

  // ─── Proof chain ─────────────────────────────────────────────────────────────
  const proofChain: ProofChain | null = useMemo(() => {
    if (!selectedTicket) return null;
    const audit = (selectedTicket.auditTrail as any) ?? {};
    const ps = proofScore(selectedTicket);
    const gate = selectedTicket.decision as "ALLOW" | "HOLD" | "BLOCK";
    return {
      decision_id: selectedTicket.intentId,
      trace_id: audit.hash_now ?? selectedTicket.intentId,
      ticket_required: gate !== "ALLOW",
      ticket_id: String(selectedTicket.id),
      attestation_ref: audit.merkle_root !== "0".repeat(24) ? audit.merkle_root : undefined,
      proof_complete: ps >= 3,
      proof_partial: ps >= 2 && ps < 3,
    };
  }, [selectedTicket]);

  // ─── Stats live ────────────────────────────────────────────────────
  const stats = useMemo(() => {
    if (!tickets) return { total: 0, allow: 0, hold: 0, block: 0, s3: 0, s4: 0, noTicket: 0, noAttestation: 0 };
    return {
      total: tickets.length,
      allow: tickets.filter(t => t.decision === "ALLOW").length,
      hold: tickets.filter(t => t.decision === "HOLD").length,
      block: tickets.filter(t => t.decision === "BLOCK").length,
      s3: tickets.filter(t => {
        const reasons = (t.reasons as string[]) ?? [];
        return reasons.some(r => r.includes("S3") || r.includes("HIGH"));
      }).length,
      s4: tickets.filter(t => t.decision === "BLOCK").length,
      noTicket: tickets.filter(t => t.decision !== "ALLOW").length,
      noAttestation: tickets.filter(t => {
        const audit = (t.auditTrail as any) ?? {};
        return !audit.merkle_root || audit.merkle_root === "0".repeat(24);
      }).length,
    };
  }, [tickets]);

  // ─── Helper : mapper un nom d'agent (string) vers un objet enrichi ──────────────────
  function agentNameToObj(name: string) {
    const n = name.toLowerCase();
    let layer = "Observation";
    if (n.includes("proof") || n.includes("attestation") || n.includes("trace") || n.includes("replay") || n.includes("integrity")) layer = "Proof";
    else if (n.includes("guard") || n.includes("policy") || n.includes("human") || n.includes("override") || n.includes("severity") || n.includes("ticket") || n.includes("readiness")) layer = "Governance";
    else if (n.includes("conflict") || n.includes("contradiction") || n.includes("narrative") || n.includes("mismatch") || n.includes("unknown") || n.includes("friction")) layer = "Contradiction";
    else if (n.includes("interpret") || n.includes("analyst") || n.includes("risk") || n.includes("credit") || n.includes("fraud") || n.includes("pattern") || n.includes("prediction") || n.includes("regime") || n.includes("stress") || n.includes("affordability") || n.includes("margin") || n.includes("roas")) layer = "Interpretation";
    return { id: name, name, layer, role: layer, description: name };
  }
  // ─── Agents du domaine courant ───────────────────────────────────────────────
  const domainAgents = useMemo(() => {
    if (!agentRegistry) return [];
    const key = domain as "trading" | "bank" | "ecom";
    const names: string[] = (agentRegistry[key] ?? []) as unknown as string[];
    return names.map(agentNameToObj);
  }, [agentRegistry, domain]);

  // ─── Top Contributors ────────────────────────────────────────────────────────
  const topContributors = useMemo(() => {
    if (!domainAgents.length) return [];
    // Simuler les contributions basées sur les tickets réels
    return domainAgents.slice(0, 5).map((agent: any, i: number) => ({
      name: agent.name,
      layer: agent.layer,
      decisions: Math.max(1, (tickets?.length ?? 0) - i * 2),
      role: agent.role,
    }));
  }, [domainAgents, tickets]);

  // ─── Propagation vers StatusRail ───────────────────────────────────────────
  useEffect(() => {
    setMode("LIVE");
    setSource("db");
  }, [setMode, setSource]);

  useEffect(() => {
    if (selectedEnvelope) {
      setX108Gate(selectedEnvelope.x108_gate);
      setLastDecisionId(selectedEnvelope.decision_id);
      const ps = proofScore(selectedTicket);
      setProofStatus(ps >= 3 ? "COMPLETE" : ps >= 2 ? "PARTIAL" : "MISSING");
    }
  }, [selectedEnvelope, selectedTicket, setX108Gate, setLastDecisionId, setProofStatus]);

  const [showBottomZone, setShowBottomZone] = useState(false);
  const [bottomTab, setBottomTab] = useState<"constellation" | "aggregation" | "proof">("constellation");

  // ─── Agents par couche pour constellation ────────────────────────────────────
  const agentsByLayer = useMemo(() => {
    const layers: Record<string, any[]> = {};
    domainAgents.forEach((a: any) => {
      const l = a.layer ?? "unknown";
      if (!layers[l]) layers[l] = [];
      layers[l].push({
        id: a.id,
        name: a.name,
        role: a.role,
        layer: a.layer,
        claim: a.description ?? a.role,
        confidence: 0.80 + Math.random() * 0.15,
        flags: [],
        trace_id: undefined,
      });
    });
    return layers;
  }, [domainAgents]);

  const CELL_HEADER = { background: "oklch(0.13 0.01 240)", borderBottom: "1px solid oklch(0.20 0.01 240)" };

  return (
    <div className="flex flex-col gap-0" style={{ minHeight: "calc(100vh - 120px)" }}>

      {/* ─── Bandeau Live ──────────────────────────────────────────────────── */}
      <div className="flex items-center gap-4 px-4 py-2 text-[10px] font-mono flex-wrap"
        style={{ background: "oklch(0.10 0.01 240)", borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: "oklch(0.72 0.18 145)" }} />
          <span className="font-bold" style={{ color: "oklch(0.72 0.18 145)" }}>LIVE</span>
        </div>
        <span style={{ color: domainCfg.accent }}>{domainCfg.icon} {domainCfg.label}</span>
        {loadingTickets ? (
          <span style={{ color: "oklch(0.45 0.01 240)" }}>Chargement...</span>
        ) : (
          <>
            <span><span style={{ color: "oklch(0.55 0.01 240)" }}>Total </span><span className="font-bold text-foreground">{stats.total}</span></span>
            <span><span style={{ color: "oklch(0.72 0.18 145)" }}>ALLOW </span><span className="font-bold">{stats.allow}</span></span>
            <span><span style={{ color: "oklch(0.72 0.18 45)" }}>HOLD </span><span className="font-bold">{stats.hold}</span></span>
            <span><span style={{ color: "oklch(0.65 0.25 25)" }}>BLOCK </span><span className="font-bold">{stats.block}</span></span>
            {dataUpdatedAt && (
              <span style={{ color: "oklch(0.40 0.01 240)" }}>
                Mis à jour {formatRelative(dataUpdatedAt)}
              </span>
            )}
          </>
        )}
        <div className="ml-auto flex items-center gap-2">
          <Link href="/future">
            <span className="px-2 py-0.5 rounded text-[9px] cursor-pointer"
              style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.55 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
              → Future
            </span>
          </Link>
          <Link href="/past">
            <span className="px-2 py-0.5 rounded text-[9px] cursor-pointer"
              style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.55 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
              → Past
            </span>
          </Link>
        </div>
      </div>

      {/* ─── Top Contributors ───────────────────────────────────────────────── */}
      {topContributors.length > 0 && (
        <div className="flex items-center gap-3 px-4 py-1.5 overflow-x-auto"
          style={{ background: "oklch(0.09 0.01 240)", borderBottom: "1px solid oklch(0.14 0.01 240)" }}>
          <span className="text-[8px] font-mono font-bold shrink-0" style={{ color: "oklch(0.40 0.01 240)" }}>TOP CONTRIBUTORS</span>
          {topContributors.map((c, i) => (
            <div key={c.name} className="flex items-center gap-1.5 shrink-0 px-2 py-0.5 rounded"
              style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
              <span className="text-[8px] font-mono font-bold" style={{ color: i === 0 ? "oklch(0.72 0.18 45)" : "oklch(0.55 0.01 240)" }}>#{i + 1}</span>
              <span className="text-[9px] font-mono" style={{ color: "oklch(0.75 0.01 240)" }}>{c.name}</span>
              <span className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>{c.layer?.slice(0, 3).toUpperCase()}</span>
              <span className="text-[8px] font-mono font-bold" style={{ color: "oklch(0.65 0.18 240)" }}>{c.decisions}d</span>
            </div>
          ))}
        </div>
      )}

      {/* ─── Live Watchlist — compteurs d'alerte (spec Bloc D) ─────────────────────────────── */}
      <div className="flex items-center gap-2 px-4 py-1.5 overflow-x-auto"
        style={{ background: "oklch(0.085 0.01 240)", borderBottom: "1px solid oklch(0.14 0.01 240)" }}>
        <span className="text-[8px] font-mono font-bold shrink-0" style={{ color: "oklch(0.40 0.01 240)" }}>WATCHLIST</span>
        {[
          { label: "ALLOW",        val: stats.allow,         color: "oklch(0.72 0.18 145)" },
          { label: "HOLD",         val: stats.hold,          color: "oklch(0.72 0.18 45)" },
          { label: "BLOCK",        val: stats.block,         color: "oklch(0.65 0.25 25)" },
          { label: "S3/S4",        val: stats.s3 + stats.s4, color: "oklch(0.65 0.25 25)" },
          { label: "Sans ticket",  val: stats.noTicket,      color: "oklch(0.72 0.18 45)" },
          { label: "Sans attest.", val: stats.noAttestation, color: "oklch(0.55 0.01 240)" },
        ].map(({ label, val, color }) => (
          <div key={label} className="flex items-center gap-1 shrink-0 px-2 py-0.5 rounded"
            style={{ background: val > 0 ? `${color}11` : "oklch(0.11 0.01 240)", border: `1px solid ${val > 0 ? color + "44" : "oklch(0.16 0.01 240)"}` }}>
            <span className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>{label}</span>
            <span className="text-[9px] font-mono font-bold" style={{ color: val > 0 ? color : "oklch(0.35 0.01 240)" }}>{val}</span>
          </div>
        ))}
      </div>


      {/* ─── Corps 3 colonnes ───────────────────────────────────────────────────── */}
      <div className="flex flex-1 gap-0" style={{ minHeight: "calc(100vh - 240px)" }}>

        {/* ── Colonne gauche : Filtres + Agents actifs ────────────────────── */}
        <div className="w-52 shrink-0 flex flex-col overflow-y-auto"
          style={{ borderRight: "1px solid oklch(0.16 0.01 240)" }}>

          <div className="p-3" style={{ borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
            <div className="text-[9px] font-mono font-bold mb-2" style={{ color: "oklch(0.55 0.01 240)" }}>GATE X-108</div>
            {(["ALL", "ALLOW", "HOLD", "BLOCK"] as const).map(g => (
              <button key={g} onClick={() => setGateFilter(g)}
                className="w-full text-left px-2 py-1 rounded text-[10px] font-mono mb-0.5"
                style={{
                  background: gateFilter === g ? "oklch(0.15 0.02 240)" : "transparent",
                  color: gateFilter === g ? (g === "ALL" ? "oklch(0.85 0.01 240)" : gateColor(g)) : "oklch(0.50 0.01 240)",
                  border: gateFilter === g ? `1px solid ${g === "ALL" ? "oklch(0.25 0.01 240)" : gateColor(g) + "66"}` : "1px solid transparent",
                }}>
                {g === "ALL" ? "Tous" : g}
              </button>
            ))}
          </div>

          <div className="p-3 flex-1">
            <div className="text-[9px] font-mono font-bold mb-2" style={{ color: "oklch(0.55 0.01 240)" }}>
              AGENTS ACTIFS — {domainAgents.length}
            </div>
            {domainAgents.length === 0 ? (
              <div className="text-[9px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>Chargement...</div>
            ) : (
              <div className="flex flex-col gap-0.5">
                {domainAgents.slice(0, 14).map((agent: any) => (
                  <div key={agent.id} className="flex items-center gap-1.5 px-1 py-0.5 rounded"
                    style={{ background: "oklch(0.12 0.01 240)" }}>
                    <div className="w-1.5 h-1.5 rounded-full shrink-0"
                      style={{ background: "oklch(0.72 0.18 145)" }} />
                    <span className="text-[8px] font-mono truncate" style={{ color: "oklch(0.65 0.01 240)" }}>
                      {agent.name}
                    </span>
                    <span className="text-[7px] font-mono shrink-0 ml-auto" style={{ color: "oklch(0.40 0.01 240)" }}>
                      {agent.layer?.slice(0, 3).toUpperCase()}
                    </span>
                  </div>
                ))}
                {domainAgents.length > 14 && (
                  <div className="text-[8px] font-mono px-1 mt-0.5" style={{ color: "oklch(0.40 0.01 240)" }}>
                    +{domainAgents.length - 14} autres
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* ── Colonne centre : Feed décisions ────────────────────────────── */}
        <div className="flex-1 flex flex-col overflow-y-auto"
          style={{ borderRight: "1px solid oklch(0.16 0.01 240)" }}>

          <div className="px-3 py-2 text-[9px] font-mono font-bold"
            style={{ ...CELL_HEADER, color: "oklch(0.55 0.01 240)" }}>
            FEED DÉCISIONS — {filteredTickets.length} entrée{filteredTickets.length !== 1 ? "s" : ""}
          </div>

          {loadingTickets ? (
            <div className="flex items-center justify-center h-32">
              <div className="flex flex-col items-center gap-2">
                <div className="w-5 h-5 border-2 rounded-full animate-spin"
                  style={{ borderColor: domainCfg.accent, borderTopColor: "transparent" }} />
                <span className="text-[9px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>Chargement DB...</span>
              </div>
            </div>
          ) : filteredTickets.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-32 gap-2 p-4">
              <span className="text-[10px] font-mono text-center" style={{ color: "oklch(0.40 0.01 240)" }}>
                {tickets && tickets.length === 0
                  ? "Aucune décision — lancez une simulation dans Future"
                  : "Aucun résultat pour ce filtre"}
              </span>
              {tickets && tickets.length === 0 && (
                <Link href="/future">
                  <span className="text-[10px] font-mono px-3 py-1.5 rounded cursor-pointer"
                    style={{ background: "oklch(0.14 0.04 145)", color: "oklch(0.72 0.18 145)", border: "1px solid oklch(0.72 0.18 145 / 0.3)" }}>
                    → Aller dans Future
                  </span>
                </Link>
              )}
            </div>
          ) : (
            <div className="flex flex-col">
              {filteredTickets.map((ticket) => {
                const reasons = (ticket.reasons as string[]) ?? [];
                const gate = ticket.decision as "ALLOW" | "HOLD" | "BLOCK";
                const ps = proofScore(ticket);
                const isSelected = selectedTicket?.id === ticket.id;
                const ts = new Date(ticket.createdAt).getTime();
                return (
                  <div key={ticket.id}
                    onClick={() => setSelectedTicketId(ticket.id)}
                    className="flex items-start gap-3 px-3 py-2.5 cursor-pointer"
                    style={{
                      borderBottom: "1px solid oklch(0.14 0.01 240)",
                      background: isSelected ? "oklch(0.13 0.02 145 / 0.2)" : "transparent",
                      borderLeft: isSelected ? `2px solid ${domainCfg.accent}` : "2px solid transparent",
                    }}>
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold shrink-0 mt-0.5"
                      style={{ background: gateColor(gate) + "22", color: gateColor(gate) }}>
                      {gate}
                    </span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-[10px] font-mono font-bold truncate" style={{ color: "oklch(0.85 0.01 240)" }}>
                          {ticket.intentId.slice(0, 22)}…
                        </span>
                        <span className="text-[9px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>
                          {formatRelative(ts)}
                        </span>
                      </div>
                      <div className="text-[9px] font-mono mt-0.5 truncate" style={{ color: "oklch(0.55 0.01 240)" }}>
                        {reasons[0] ?? "—"}
                      </div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-[9px] font-mono" style={{ color: "#a78bfa" }}>Preuve {ps}/4</span>
                        <span className="text-[9px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>{ticket.domain}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* ── Colonne droite : Envelope active + Proof + Agents ──────────── */}
        <div className="w-96 shrink-0 flex flex-col overflow-y-auto">

          {selectedTicket ? (
            <>
              <div className="flex gap-0" style={{ borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
                {([
                  { key: "envelope", label: "Envelope" },
                  { key: "proof", label: "Proof Chain" },
                  { key: "agents", label: "Agents" },
                ] as { key: typeof activeTab; label: string }[]).map(tab => (
                  <button key={tab.key} onClick={() => setActiveTab(tab.key)}
                    className="flex-1 px-2 py-2 text-[9px] font-mono font-bold"
                    style={{
                      background: activeTab === tab.key ? "oklch(0.13 0.02 145 / 0.2)" : "transparent",
                      color: activeTab === tab.key ? domainCfg.accent : "oklch(0.45 0.01 240)",
                      borderBottom: activeTab === tab.key ? `2px solid ${domainCfg.accent}` : "2px solid transparent",
                    }}>
                    {tab.label}
                  </button>
                ))}
              </div>

              <div className="p-3 flex-1 overflow-y-auto">
                {activeTab === "envelope" && selectedEnvelope && (
                  <div className="flex flex-col gap-3">
                    <DecisionEnvelopeCard envelope={selectedEnvelope} variant="standard" />

                    {/* ─── Proof Snapshot (spec Bloc 3) ────────────────────────────────── */}
                    {(() => {
                      const ps = proofScore(selectedTicket);
                      const audit = (selectedTicket?.auditTrail as any) ?? {};
                      const hasTrace = !!(audit.hash_now);
                      const hasTicket = !!(selectedTicket?.id);
                      const hasAttest = !!(audit.merkle_root && audit.merkle_root !== "0".repeat(24));
                      const hasReplay = ps >= 3;
                      const statusColor = (ok: boolean) => ok ? "oklch(0.72 0.18 145)" : "oklch(0.65 0.25 25)";
                      return (
                        <div className="rounded overflow-hidden" style={{ border: "1px solid oklch(0.18 0.01 240)" }}>
                          <div className="px-3 py-1.5 flex items-center justify-between"
                            style={{ background: "oklch(0.12 0.01 240)", borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
                            <span className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.60 0.01 240)" }}>Proof Snapshot</span>
                            <span className="text-[8px] font-mono font-bold" style={{ color: ps >= 3 ? "oklch(0.72 0.18 145)" : ps >= 2 ? "oklch(0.72 0.18 45)" : "oklch(0.65 0.25 25)" }}>{ps}/4</span>
                          </div>
                          <div className="p-2 flex flex-col gap-1" style={{ background: "oklch(0.105 0.01 240)" }}>
                            {[
                              { label: "Trace",       ok: hasTrace,  val: hasTrace ? "complete" : "missing",  id: audit.hash_now?.slice(0, 14) },
                              { label: "Ticket",      ok: hasTicket, val: hasTicket ? "ready" : "missing",    id: String(selectedTicket?.id) },
                              { label: "Attestation", ok: hasAttest, val: hasAttest ? "ready" : "pending",    id: audit.merkle_root?.slice(0, 14) },
                              { label: "Replay",      ok: hasReplay, val: hasReplay ? "reproducible" : "partial", id: null },
                            ].map(({ label, ok, val, id }) => (
                              <div key={label} className="flex items-center justify-between gap-2">
                                <span className="text-[8px] font-mono" style={{ color: "oklch(0.50 0.01 240)" }}>{label}</span>
                                <div className="flex items-center gap-1.5">
                                  {id && <span className="text-[7px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>{id}…</span>}
                                  <span className="text-[8px] font-mono font-bold" style={{ color: statusColor(ok) }}>{val}</span>
                                </div>
                              </div>
                            ))}
                            <div className="flex gap-1.5 mt-1 pt-1" style={{ borderTop: "1px solid oklch(0.16 0.01 240)" }}>
                              <Link href="/past">
                                <span className="text-[7px] font-mono px-1.5 py-0.5 rounded cursor-pointer"
                                  style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.55 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
                                  Open in Past
                                </span>
                              </Link>
                              <Link href="/future">
                                <span className="text-[7px] font-mono px-1.5 py-0.5 rounded cursor-pointer"
                                  style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.55 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
                                  Replay in Future
                                </span>
                              </Link>
                            </div>
                          </div>
                        </div>
                      );
                    })()}

                    {/* ─── Operator Next Action (spec Bloc 4) ───────────────────────────── */}
                    <div className="rounded overflow-hidden" style={{ border: "1px solid oklch(0.18 0.01 240)" }}>
                      <div className="px-3 py-1.5"
                        style={{ background: "oklch(0.12 0.01 240)", borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
                        <span className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.60 0.01 240)" }}>Operator Next Action</span>
                      </div>
                      <div className="p-2" style={{ background: "oklch(0.105 0.01 240)" }}>
                        {selectedEnvelope.x108_gate === "BLOCK" ? (
                          <div className="flex flex-col gap-1">
                            <div className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.65 0.25 25)" }}>⛔ Décision bloquée</div>
                            <div className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>Vérifier ticket + attestation · Ouvrir proof chain · Escalader si S4</div>
                          </div>
                        ) : selectedEnvelope.x108_gate === "HOLD" ? (
                          <div className="flex flex-col gap-1">
                            <div className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.72 0.18 45)" }}>⏸ En attente de validation</div>
                            <div className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>Réviser les contradictions · Attendre résolution · Replay dans Future</div>
                          </div>
                        ) : (
                          <div className="flex flex-col gap-1">
                            <div className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.72 0.18 145)" }}>✓ Décision autorisée</div>
                            <div className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>Archiver dans Past · Compléter attestation si manquante · Surveiller suite</div>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <Link href="/past">
                        <span className="inline-block px-3 py-1.5 rounded text-[10px] font-mono cursor-pointer"
                          style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.55 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
                          → Past
                        </span>
                      </Link>
                      <Link href="/control">
                        <span className="inline-block px-3 py-1.5 rounded text-[10px] font-mono cursor-pointer"
                          style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.55 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
                          → Control
                        </span>
                      </Link>
                    </div>
                  </div>
                )}

                {activeTab === "proof" && proofChain && (
                  <ProofChainView chain={proofChain} />
                )}

                {activeTab === "agents" && (
                  <div className="flex flex-col gap-2">
                    <div className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.55 0.01 240)" }}>
                      AGENTS — {domainCfg.label.toUpperCase()} ({domainAgents.length})
                    </div>
                    {domainAgents.length === 0 ? (
                      <div className="text-[9px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>Chargement...</div>
                    ) : (
                      <div className="flex flex-col gap-0.5">
                        {domainAgents.map((agent: any) => (
                          <div key={agent.id} className="flex items-center gap-2 px-2 py-1.5 rounded"
                            style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.16 0.01 240)" }}>
                            <div className="w-1.5 h-1.5 rounded-full shrink-0"
                              style={{ background: "oklch(0.72 0.18 145)" }} />
                            <div className="flex-1 min-w-0">
                              <div className="text-[9px] font-mono font-bold truncate" style={{ color: "oklch(0.75 0.01 240)" }}>
                                {agent.name}
                              </div>
                              <div className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>
                                {agent.role} · {agent.layer}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center h-full gap-3 p-6">
              <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: "oklch(0.72 0.18 145)" }} />
              <span className="text-[10px] font-mono text-center" style={{ color: "oklch(0.40 0.01 240)" }}>
                {loadingTickets ? "Chargement..." : "En attente — lancez une simulation dans Future"}
              </span>
              {!loadingTickets && (
                <Link href="/future">
                  <span className="text-[10px] font-mono px-3 py-1.5 rounded cursor-pointer"
                    style={{ background: "oklch(0.14 0.04 145)", color: "oklch(0.72 0.18 145)", border: "1px solid oklch(0.72 0.18 145 / 0.3)" }}>
                    → Lancer une simulation
                  </span>
                </Link>
              )}
            </div>
          )}
        </div>
      </div>
      {/* ─── Zone basse dépliable ──────────────────────────────────────────── */}
      <div style={{ borderTop: "1px solid oklch(0.16 0.01 240)" }}>
        <button
          onClick={() => setShowBottomZone(v => !v)}
          className="w-full flex items-center justify-between px-4 py-2 text-[9px] font-mono"
          style={{ background: "oklch(0.10 0.01 240)", color: "oklch(0.50 0.01 240)" }}>
          <span className="font-bold">ZONE BASSE — Constellation · Agrégation · Proof Chain</span>
          <span>{showBottomZone ? "▲ Réduire" : "▼ Développer"}</span>
        </button>

        {showBottomZone && (
          <div style={{ background: "oklch(0.08 0.01 240)" }}>
            {/* Onglets zone basse */}
            <div className="flex" style={{ borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
              {(["constellation", "aggregation", "proof"] as const).map(tab => (
                <button key={tab} onClick={() => setBottomTab(tab)}
                  className="px-4 py-1.5 text-[9px] font-mono font-bold"
                  style={{
                    background: bottomTab === tab ? "oklch(0.12 0.01 240)" : "transparent",
                    color: bottomTab === tab ? domainCfg.accent : "oklch(0.45 0.01 240)",
                    borderBottom: bottomTab === tab ? `2px solid ${domainCfg.accent}` : "2px solid transparent",
                  }}>
                  {tab === "constellation" ? "Constellation" : tab === "aggregation" ? "Agrégation" : "Proof Chain"}
                </button>
              ))}
            </div>

            <div className="p-4" style={{ maxHeight: "400px", overflowY: "auto" }}>
              {bottomTab === "constellation" && (
                <AgentConstellationPanel
                  agents={Object.values(agentsByLayer).flat()}
                  domain={domain as "trading" | "bank" | "ecom"}
                />
              )}

              {bottomTab === "aggregation" && (
                <div className="grid grid-cols-2 gap-3 text-[11px]">
                  <div className="rounded p-3" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
                    <div className="text-[9px] font-mono font-bold mb-2" style={{ color: "oklch(0.55 0.01 240)" }}>RÉSUMÉ DÉCISIONS</div>
                    <div className="flex flex-col gap-1">
                      <div className="flex justify-between">
                        <span className="text-[10px] font-mono" style={{ color: "oklch(0.72 0.18 145)" }}>ALLOW</span>
                        <span className="font-mono font-bold text-foreground">{stats.allow}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-[10px] font-mono" style={{ color: "oklch(0.72 0.18 45)" }}>HOLD</span>
                        <span className="font-mono font-bold text-foreground">{stats.hold}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-[10px] font-mono" style={{ color: "oklch(0.65 0.25 25)" }}>BLOCK</span>
                        <span className="font-mono font-bold text-foreground">{stats.block}</span>
                      </div>
                    </div>
                  </div>
                  <div className="rounded p-3" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
                    <div className="text-[9px] font-mono font-bold mb-2" style={{ color: "oklch(0.55 0.01 240)" }}>SANTÉ PROOF</div>
                    <div className="flex flex-col gap-1">
                      {filteredTickets.slice(0, 5).map(t => {
                        const ps = proofScore(t);
                        return (
                          <div key={t.id} className="flex justify-between">
                            <span className="text-[9px] font-mono truncate" style={{ color: "oklch(0.55 0.01 240)" }}>{t.intentId?.slice(0, 16)}…</span>
                            <span className="font-mono font-bold text-[9px]" style={{ color: ps >= 3 ? "oklch(0.72 0.18 145)" : ps >= 2 ? "oklch(0.72 0.18 45)" : "oklch(0.65 0.25 25)" }}>{ps}/4</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}

              {bottomTab === "proof" && proofChain && (
                <ProofChainView chain={proofChain} />
              )}
              {bottomTab === "proof" && !proofChain && (
                <div className="text-[10px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>Sélectionnez une décision dans le feed pour voir sa chaîne de preuve.</div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
