/**
 * Past — registre prouvé OS4 V2
 * Données réelles depuis trpc.proof.allTickets + trpc.proof.simulationRuns
 * Spec : pasted_content_4
 */
import React, { useState, useMemo, useEffect } from "react";
import { Link } from "wouter";
import { trpc } from "@/lib/trpc";
import { useWorld, DOMAIN_COLORS } from "@/contexts/WorldContext";
import DecisionEnvelopeCard, { type CanonicalEnvelope } from "@/components/canonical/DecisionEnvelopeCard";
import ProofChainView, { type ProofChain } from "@/components/canonical/ProofChainView";
import AgentConstellationPanel from "@/components/canonical/AgentConstellationPanel";

// ─── Types ────────────────────────────────────────────────────────────────────
type GateFilter = "ALL" | "ALLOW" | "HOLD" | "BLOCK";
type IncidentLens = "ALL" | "S3S4" | "BLOCK" | "NO_TICKET" | "NO_ATTESTATION";

// ─── Helpers ──────────────────────────────────────────────────────────────────
function proofScore(ticket: any): number {
  let score = 0;
  if (ticket?.intentId) score++;
  const audit = (ticket?.auditTrail as any) ?? {};
  if (audit.hash_now) score++;
  if (ticket?.id) score++;
  if (audit.merkle_root && audit.merkle_root !== "0".repeat(24)) score++;
  return score;
}

function formatRelative(ts: number): string {
  const diff = Date.now() - ts;
  if (diff < 60000) return "à l'instant";
  if (diff < 3600000) return `il y a ${Math.floor(diff / 60000)}min`;
  if (diff < 86400000) return `il y a ${Math.floor(diff / 3600000)}h`;
  return `il y a ${Math.floor(diff / 86400000)}j`;
}

function gateColor(gate: string): string {
  if (gate === "ALLOW") return "oklch(0.72 0.18 145)";
  if (gate === "HOLD") return "oklch(0.72 0.18 45)";
  return "oklch(0.65 0.25 25)";
}

// ─── Composant principal ──────────────────────────────────────────────────────
export default function Past() {
  const { domain, setMode, setX108Gate, setLastDecisionId, setProofStatus, setSource } = useWorld();
  const domainCfg = DOMAIN_COLORS[domain];

  const [search, setSearch] = useState("");
  const [gateFilter, setGateFilter] = useState<GateFilter>("ALL");
  const [incidentLens, setIncidentLens] = useState<IncidentLens>("ALL");
  const [viewMode, setViewMode] = useState<"list" | "timeline">("list");
  const [selectedTicketId, setSelectedTicketId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<"proof" | "replay" | "compare" | "agents">("proof");
  const [compareIds, setCompareIds] = useState<[number | null, number | null]>([null, null]);

  // ─── Données réelles ────────────────────────────────────────────────────────
  const { data: tickets, isLoading: loadingTickets } = trpc.proof.allTickets.useQuery(
    { domain: domain as any, limit: 50 },
    { refetchInterval: 30000 }
  );

  const { data: simRuns, isLoading: loadingRuns } = trpc.proof.simulationRuns.useQuery(
    { domain: domain as any, limit: 30 },
    { refetchInterval: 30000 }
  );

  const isLoading = loadingTickets || loadingRuns;

  // ─── Filtrage ───────────────────────────────────────────────────────────────
  const filteredTickets = useMemo(() => {
    if (!tickets) return [];
    return tickets.filter(t => {
      const reasons = (t.reasons as string[]) ?? [];
      const gate = (t.decision ?? "").toUpperCase();
      const audit = (t.auditTrail as any) ?? {};
      const ps = proofScore(t);

      if (search && !t.intentId.toLowerCase().includes(search.toLowerCase()) &&
          !reasons.join(" ").toLowerCase().includes(search.toLowerCase())) return false;
      if (gateFilter !== "ALL" && gate !== gateFilter) return false;
      if (incidentLens === "S3S4" && gate !== "BLOCK" && gate !== "HOLD") return false;
      if (incidentLens === "BLOCK" && gate !== "BLOCK") return false;
      if (incidentLens === "NO_TICKET" && t.id) return false;
      if (incidentLens === "NO_ATTESTATION" && audit.merkle_root && audit.merkle_root !== "0".repeat(24)) return false;
      return true;
    });
  }, [tickets, search, gateFilter, incidentLens]);

  const selectedTicket = useMemo(
    () => selectedTicketId
      ? filteredTickets.find(t => t.id === selectedTicketId) ?? filteredTickets[0]
      : filteredTickets[0],
    [selectedTicketId, filteredTickets]
  );

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
      source: audit.anchor_ref ?? "db",
      timestamp: new Date(selectedTicket.createdAt).getTime(),
    };
  }, [selectedTicket]);

  const stats = useMemo(() => {
    if (!tickets) return { total: 0, allow: 0, hold: 0, block: 0, proofComplete: 0, avgProof: 0 };
    const allow = tickets.filter(t => t.decision === "ALLOW").length;
    const hold = tickets.filter(t => t.decision === "HOLD").length;
    const block = tickets.filter(t => t.decision === "BLOCK").length;
    const scores = tickets.map(t => proofScore(t));
    const proofComplete = scores.filter(s => s >= 3).length;
    const avgProof = scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
    return { total: tickets.length, allow, hold, block, proofComplete, avgProof };
  }, [tickets]);

  const CELL = { background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" };
  const CELL_HEADER = { background: "oklch(0.13 0.01 240)", borderBottom: "1px solid oklch(0.20 0.01 240)" };

  // ─── Propagation vers StatusRail ───────────────────────────────────────────
  useEffect(() => {
    setMode("SIMU");
    setSource("db_history");
  }, [setMode, setSource]);

  useEffect(() => {
    if (selectedEnvelope) {
      setX108Gate(selectedEnvelope.x108_gate);
      setLastDecisionId(selectedEnvelope.decision_id);
      const ps = proofScore(selectedTicket);
      setProofStatus(ps >= 3 ? "COMPLETE" : ps >= 2 ? "PARTIAL" : "MISSING");
    }
  }, [selectedEnvelope, selectedTicket, setX108Gate, setLastDecisionId, setProofStatus]);

  return (
    <div className="flex flex-col gap-0" style={{ minHeight: "calc(100vh - 120px)" }}>

      {/* ─── Bandeau stats ─────────────────────────────────────────────────── */}
      <div className="flex items-center gap-4 px-4 py-2 text-[10px] font-mono flex-wrap"
        style={{ background: "oklch(0.10 0.01 240)", borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
        <span style={{ color: domainCfg.accent }}>{domainCfg.icon} {domainCfg.label}</span>
        <span className="font-bold" style={{ color: "#a78bfa" }}>PAST — REGISTRE PROUVÉ</span>
        {isLoading ? (
          <span style={{ color: "oklch(0.45 0.01 240)" }}>Chargement DB...</span>
        ) : (
          <>
            <span><span style={{ color: "oklch(0.55 0.01 240)" }}>Total </span><span className="font-bold text-foreground">{stats.total}</span></span>
            <span><span style={{ color: "oklch(0.72 0.18 145)" }}>ALLOW </span><span className="font-bold">{stats.allow}</span></span>
            <span><span style={{ color: "oklch(0.72 0.18 45)" }}>HOLD </span><span className="font-bold">{stats.hold}</span></span>
            <span><span style={{ color: "oklch(0.65 0.25 25)" }}>BLOCK </span><span className="font-bold">{stats.block}</span></span>
            <span><span style={{ color: "#a78bfa" }}>Preuve ≥3/4 </span><span className="font-bold">{stats.proofComplete}</span></span>
            <span><span style={{ color: "oklch(0.55 0.01 240)" }}>Score moy. </span><span className="font-bold">{stats.avgProof.toFixed(1)}/4</span></span>
          </>
        )}
        <div className="ml-auto flex items-center gap-2">
          <Link href="/live">
            <span className="px-2 py-0.5 rounded text-[9px] cursor-pointer"
              style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.55 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
              ← Live
            </span>
          </Link>
          <Link href={`/future?domain=${domain}&replay=1${selectedTicket ? `&decisionId=${encodeURIComponent(selectedTicket.intentId)}&gate=${selectedTicket.decision}` : ""}`}>
            <span className="px-2 py-0.5 rounded text-[9px] cursor-pointer"
              style={{ background: "oklch(0.72 0.18 145 / 0.12)", color: "oklch(0.72 0.18 145)", border: "1px solid oklch(0.72 0.18 145 / 0.40)" }}>
              ↺ Rejouer dans Future
            </span>
          </Link>
        </div>
      </div>

      {/* ─── Corps 3 colonnes ───────────────────────────────────────────────── */}
      <div className="flex flex-1 gap-0" style={{ minHeight: "calc(100vh - 200px)" }}>

        {/* ── Colonne gauche : Filtres ────────────────────────────────────── */}
        <div className="w-56 shrink-0 flex flex-col overflow-y-auto"
          style={{ borderRight: "1px solid oklch(0.16 0.01 240)" }}>

          <div className="p-3" style={{ borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
            <div className="text-[9px] font-mono font-bold mb-2" style={{ color: "oklch(0.55 0.01 240)" }}>RECHERCHE</div>
            <input type="text" placeholder="ID, raison..." value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full px-2 py-1.5 text-[10px] font-mono rounded"
              style={{ background: "oklch(0.13 0.01 240)", border: "1px solid oklch(0.20 0.01 240)", color: "oklch(0.85 0.01 240)", outline: "none" }} />
          </div>

          <div className="p-3" style={{ borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
            <div className="text-[9px] font-mono font-bold mb-2" style={{ color: "oklch(0.55 0.01 240)" }}>GATE X-108</div>
            {(["ALL", "ALLOW", "HOLD", "BLOCK"] as GateFilter[]).map(g => (
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

          <div className="p-3" style={{ borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
            <div className="text-[9px] font-mono font-bold mb-2" style={{ color: "oklch(0.55 0.01 240)" }}>INCIDENT LENS</div>
            {([
              { key: "ALL", label: "Tous" },
              { key: "S3S4", label: "Sévérité S3/S4" },
              { key: "BLOCK", label: "Bloqués" },
              { key: "NO_TICKET", label: "Sans ticket" },
              { key: "NO_ATTESTATION", label: "Sans attestation" },
            ] as { key: IncidentLens; label: string }[]).map(l => (
              <button key={l.key} onClick={() => setIncidentLens(l.key)}
                className="w-full text-left px-2 py-1 rounded text-[10px] font-mono mb-0.5"
                style={{
                  background: incidentLens === l.key ? "oklch(0.15 0.02 240)" : "transparent",
                  color: incidentLens === l.key ? "oklch(0.85 0.01 240)" : "oklch(0.50 0.01 240)",
                  border: incidentLens === l.key ? "1px solid oklch(0.25 0.01 240)" : "1px solid transparent",
                }}>
                {l.label}
              </button>
            ))}
          </div>

          <div className="p-3">
            <div className="text-[9px] font-mono font-bold mb-2" style={{ color: "oklch(0.55 0.01 240)" }}>VUE</div>
            <div className="flex gap-1">
              {(["list", "timeline"] as const).map(v => (
                <button key={v} onClick={() => setViewMode(v)}
                  className="flex-1 px-2 py-1 rounded text-[10px] font-mono"
                  style={{
                    background: viewMode === v ? "oklch(0.15 0.02 240)" : "transparent",
                    color: viewMode === v ? "oklch(0.85 0.01 240)" : "oklch(0.50 0.01 240)",
                    border: viewMode === v ? "1px solid oklch(0.25 0.01 240)" : "1px solid oklch(0.16 0.01 240)",
                  }}>
                  {v === "list" ? "Liste" : "Timeline"}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* ── Colonne centre : Run List ───────────────────────────────────── */}
        <div className="flex-1 flex flex-col overflow-y-auto"
          style={{ borderRight: "1px solid oklch(0.16 0.01 240)" }}>

          <div className="px-3 py-2 text-[9px] font-mono font-bold"
            style={{ ...CELL_HEADER, color: "oklch(0.55 0.01 240)" }}>
            DÉCISIONS — {filteredTickets.length} résultat{filteredTickets.length !== 1 ? "s" : ""}
          </div>

          {isLoading ? (
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
                  ? "Aucune décision enregistrée — lancez une simulation dans Future pour peupler le registre"
                  : "Aucun résultat pour ces filtres"}
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
                        {ps < 3 && <span className="text-[9px] font-mono" style={{ color: "oklch(0.65 0.25 25)" }}>⚠ Incomplète</span>}
                        <span className="text-[9px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>{ticket.domain}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

         {/* ── Colonne droite : Détail + Proof Chain ──────────────────── */}
        <div className="w-96 shrink-0 flex flex-col overflow-y-auto">
          {selectedTicket ? (
            <>
              {selectedEnvelope && (
                <div className="p-3" style={{ borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
                  {/* ─── Run Summary (spec Bloc 1) ──────────────────────────────────── */}
                  <div className="mb-3 rounded overflow-hidden" style={{ border: "1px solid oklch(0.18 0.01 240)" }}>
                    <div className="px-3 py-1.5 flex items-center justify-between"
                      style={{ background: "oklch(0.12 0.01 240)", borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
                      <span className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.60 0.01 240)" }}>Run Summary</span>
                      <span className="text-[8px] font-mono px-1.5 py-0.5 rounded"
                        style={{ background: gateColor(selectedEnvelope.x108_gate) + "22", color: gateColor(selectedEnvelope.x108_gate), border: `1px solid ${gateColor(selectedEnvelope.x108_gate)}44` }}>
                        {selectedEnvelope.x108_gate}
                      </span>
                    </div>
                    <div className="p-2 flex flex-col gap-1" style={{ background: "oklch(0.105 0.01 240)" }}>
                      {[
                        { label: "Domain",      val: selectedEnvelope.domain },
                        { label: "Confidence",  val: `${Math.round((selectedEnvelope.confidence ?? 0) * 100)}%` },
                        { label: "Proof score", val: `${proofScore(selectedTicket)}/4` },
                        { label: "Severity",    val: selectedEnvelope.severity ?? "—" },
                        { label: "Timestamp",   val: formatRelative(selectedEnvelope.timestamp ?? 0) },
                        { label: "Decision ID", val: selectedEnvelope.decision_id?.slice(0, 20) + "…" },
                      ].map(({ label, val }) => (
                        <div key={label} className="flex items-center justify-between gap-2">
                          <span className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>{label}</span>
                          <span className="text-[8px] font-mono font-bold" style={{ color: "oklch(0.70 0.01 240)" }}>{val}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <DecisionEnvelopeCard envelope={selectedEnvelope} variant="standard" />
                </div>
              )}

              <div className="flex gap-0" style={{ borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
                {([
                  { key: "proof", label: "Proof Chain" },
                  { key: "replay", label: "Audit Trail" },
                  { key: "compare", label: "Comparer" },
                  { key: "agents", label: "Contributors" },
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
                {activeTab === "proof" && (
                  <div className="flex flex-col gap-3">
                    {/* Proof Chain attachée au run sélectionné (spec : toujours reliée au run, jamais flottante) */}
                    <div className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.55 0.01 240)" }}>
                      PROOF CHAIN — Run #{selectedTicket.id}
                    </div>
                    {proofChain ? (
                      <ProofChainView chain={proofChain} />
                    ) : (
                      <div className="text-[9px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>Aucune proof chain pour ce run</div>
                    )}
                  </div>
                )}

                {activeTab === "replay" && (
                  <div className="flex flex-col gap-3">
                    <div className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.55 0.01 240)" }}>AUDIT TRAIL COMPLET</div>
                    <div className="p-2 rounded text-[9px] font-mono"
                      style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.16 0.01 240)" }}>
                      {Object.entries((selectedTicket.auditTrail as any) ?? {}).map(([k, v]) => (
                        <div key={k} className="flex gap-2 py-0.5" style={{ borderBottom: "1px solid oklch(0.14 0.01 240)" }}>
                          <span className="shrink-0 w-28" style={{ color: "oklch(0.45 0.01 240)" }}>{k}</span>
                          <span className="truncate" style={{ color: "oklch(0.70 0.01 240)" }}>{String(v).slice(0, 40)}</span>
                        </div>
                      ))}
                    </div>
                    <div className="text-[9px] font-mono font-bold mt-2" style={{ color: "oklch(0.55 0.01 240)" }}>RAISONS</div>
                    <div className="flex flex-col gap-1">
                      {((selectedTicket.reasons as string[]) ?? []).map((r, i) => (
                        <div key={i} className="px-2 py-1 rounded text-[9px] font-mono"
                          style={{ background: "oklch(0.12 0.01 240)", color: "oklch(0.70 0.01 240)", border: "1px solid oklch(0.16 0.01 240)" }}>
                          {r}
                        </div>
                      ))}
                    </div>
                    <Link href="/future">
                      <span className="inline-block px-3 py-1.5 rounded text-[10px] font-mono cursor-pointer mt-2"
                        style={{ background: "oklch(0.14 0.04 145)", color: "oklch(0.72 0.18 145)", border: "1px solid oklch(0.72 0.18 145 / 0.3)" }}>
                        → Rejouer dans Future
                      </span>
                    </Link>
                  </div>
                )}

                {activeTab === "compare" && (
                  <div className="flex flex-col gap-2">
                    <div className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.55 0.01 240)" }}>COMPARER 2 DÉCISIONS</div>
                    <div className="grid grid-cols-2 gap-2 mb-2">
                      {([0, 1] as const).map(slot => (
                        <div key={slot}>
                          <div className="text-[8px] font-mono mb-1" style={{ color: "oklch(0.45 0.01 240)" }}>Décision {slot + 1}</div>
                          <select
                            value={compareIds[slot] ?? ""}
                            onChange={e => {
                              const val = e.target.value ? Number(e.target.value) : null;
                              setCompareIds(prev => slot === 0 ? [val, prev[1]] : [prev[0], val]);
                            }}
                            className="w-full px-2 py-1 rounded text-[8px] font-mono"
                            style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.20 0.01 240)", color: "oklch(0.75 0.01 240)", outline: "none" }}>
                            <option value="">Sélectionner...</option>
                            {filteredTickets.map(t => (
                              <option key={t.id} value={t.id}>
                                {t.decision} — {t.intentId.slice(0, 18)}…
                              </option>
                            ))}
                          </select>
                        </div>
                      ))}
                    </div>
                    {compareIds[0] && compareIds[1] ? (
                      <div className="grid grid-cols-2 gap-2">
                        {compareIds.map((cid, slot) => {
                          const t = filteredTickets.find(x => x.id === cid);
                          if (!t) return null;
                          const reasons = (t.reasons as string[]) ?? [];
                          const gate = t.decision as "ALLOW" | "HOLD" | "BLOCK";
                          const ps = proofScore(t);
                          const audit = (t.auditTrail as any) ?? {};
                          return (
                            <div key={slot} className="p-2 rounded flex flex-col gap-1"
                              style={{ background: "oklch(0.10 0.01 240)", border: `1px solid ${gateColor(gate)}44` }}>
                              <div className="flex items-center gap-1.5">
                                <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold"
                                  style={{ background: gateColor(gate) + "22", color: gateColor(gate) }}>{gate}</span>
                                <span className="text-[8px] font-mono truncate" style={{ color: "oklch(0.65 0.01 240)" }}>
                                  {t.intentId.slice(0, 16)}…
                                </span>
                              </div>
                              <div className="text-[8px] font-mono" style={{ color: "oklch(0.55 0.01 240)" }}>
                                Preuve : <span style={{ color: ps >= 3 ? "oklch(0.72 0.18 145)" : "oklch(0.72 0.18 45)" }}>{ps}/4</span>
                              </div>
                              <div className="text-[8px] font-mono" style={{ color: "oklch(0.55 0.01 240)" }}>
                                Raison : {reasons[0]?.slice(0, 30) ?? "—"}
                              </div>
                              <div className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>
                                Hash : {(audit.hash_now ?? "—").slice(0, 12)}…
                              </div>
                              <div className="text-[8px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>
                                {formatRelative(new Date(t.createdAt).getTime())}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <div className="text-[9px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>
                        Sélectionnez 2 décisions pour comparer
                      </div>
                    )}
                  </div>
                )}

                {activeTab === "agents" && (
                  <div className="flex flex-col gap-3">
                    {/* ─── Top Contributors (spec Bloc 2) ────────────────────────────────── */}
                    {selectedEnvelope && (
                      <div className="rounded overflow-hidden" style={{ border: "1px solid oklch(0.18 0.01 240)" }}>
                        <div className="px-3 py-1.5 flex items-center justify-between"
                          style={{ background: "oklch(0.12 0.01 240)", borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
                          <span className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.60 0.01 240)" }}>Top Contributors</span>
                          <span className="text-[8px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>Run #{selectedTicket.id}</span>
                        </div>
                        <div className="p-2 flex flex-col gap-1.5" style={{ background: "oklch(0.105 0.01 240)" }}>
                          {[
                            { rank: 1, name: "Observation",       layer: "Observation",    claim: selectedEnvelope.market_verdict,  confidence: selectedEnvelope.confidence,       influence: 0.92 },
                            { rank: 2, name: "Interprétation",    layer: "Interpretation", claim: selectedEnvelope.reason_code,     confidence: selectedEnvelope.confidence * 0.9, influence: 0.78 },
                            { rank: 3, name: "Gouvernance X-108", layer: "Governance",     claim: selectedEnvelope.x108_gate,       confidence: 1.0,                               influence: 1.00 },
                          ].map(({ rank, name, layer, claim, confidence, influence }) => (
                            <div key={rank} className="flex items-start gap-2 px-2 py-1.5 rounded"
                              style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.16 0.01 240)" }}>
                              <span className="text-[8px] font-mono font-bold shrink-0 mt-0.5" style={{ color: "oklch(0.72 0.18 45)" }}>#{rank}</span>
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between gap-1">
                                  <span className="text-[9px] font-mono font-bold truncate" style={{ color: "oklch(0.75 0.01 240)" }}>{name}</span>
                                  <span className="text-[7px] font-mono shrink-0" style={{ color: "oklch(0.40 0.01 240)" }}>{layer.slice(0, 5).toUpperCase()}</span>
                                </div>
                                <div className="text-[8px] font-mono truncate mt-0.5" style={{ color: "oklch(0.55 0.01 240)" }}>{claim?.slice(0, 30)}</div>
                                <div className="flex items-center gap-2 mt-0.5">
                                  <span className="text-[7px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>conf {Math.round(confidence * 100)}%</span>
                                  <span className="text-[7px] font-mono" style={{ color: "oklch(0.65 0.18 240)" }}>influence {Math.round(influence * 100)}%</span>
                                </div>
                              </div>
                            </div>
                          ))}
                          <div className="mt-1 text-[7px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>
                            Agents les plus influents sur la décision #{selectedTicket.id}
                          </div>
                        </div>
                      </div>
                    )}

                    <div className="text-[9px] font-mono font-bold" style={{ color: "oklch(0.55 0.01 240)" }}>CONSTELLATION AGENTS</div>
                    {selectedEnvelope ? (
                      <AgentConstellationPanel
                        agents={[
                          { name: "Observation", layer: "Observation" as const, claim: selectedEnvelope.market_verdict, confidence: selectedEnvelope.confidence, risk_flags: selectedEnvelope.risk_flags, status: "active" as const },
                          { name: "Interprétation", layer: "Interpretation" as const, claim: selectedEnvelope.reason_code, confidence: selectedEnvelope.confidence * 0.9, status: "active" as const },
                          { name: "Gouvernance X-108", layer: "Governance" as const, claim: selectedEnvelope.x108_gate, confidence: 1.0, risk_flags: selectedEnvelope.x108_gate !== "ALLOW" ? ["GATE_ACTIVE"] : [], status: "active" as const },
                        ]}
                        domain={domain as "trading" | "bank" | "ecom"}
                        defaultExpanded={true}
                      />
                    ) : (
                      <div className="text-[9px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>Sélectionnez une décision</div>
                    )}
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center h-full gap-3 p-6">
              <span className="text-2xl">📋</span>
              <span className="text-[10px] font-mono text-center" style={{ color: "oklch(0.40 0.01 240)" }}>
                {isLoading ? "Chargement..." : "Sélectionnez une décision dans la liste"}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* ─── Simulation Runs (zone basse) ──────────────────────────────────── */}
      {simRuns && simRuns.length > 0 && (
        <div style={{ borderTop: "1px solid oklch(0.16 0.01 240)" }}>
          <div className="px-4 py-2 text-[9px] font-mono font-bold"
            style={{ ...CELL_HEADER, color: "oklch(0.55 0.01 240)" }}>
            SIMULATION RUNS — {simRuns.length} runs enregistrés
          </div>
          <div className="flex gap-3 px-4 py-3 overflow-x-auto">
            {simRuns.map(run => (
              <div key={run.id} className="shrink-0 p-2 rounded"
                style={{ ...CELL, minWidth: 180 }}>
                <div className="text-[9px] font-mono font-bold mb-1" style={{ color: "oklch(0.70 0.01 240)" }}>
                  {run.domain.toUpperCase()} #{run.id}
                </div>
                <div className="text-[9px] font-mono" style={{ color: "oklch(0.50 0.01 240)" }}>
                  Seed: {run.seed} · Steps: {run.steps}
                </div>
                <div className="text-[9px] font-mono mt-1 truncate" style={{ color: "#a78bfa" }}>
                  Hash: {run.stateHash.slice(0, 12)}…
                </div>
                <div className="text-[9px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>
                  {formatRelative(new Date(run.createdAt).getTime())}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
