/**
 * Mission — surface d'entrée OS4 V2
 * Données RÉELLES depuis trpc.proof.guardStats + trpc.proof.allTickets
 * 3 WorldCards dynamiques + accès rapide 4 surfaces + alertes critiques
 */
import React from "react";
import { Link } from "wouter";
import { useWorld, DOMAIN_COLORS, type WorldDomain } from "@/contexts/WorldContext";
import { trpc } from "@/lib/trpc";

// ─── Types ────────────────────────────────────────────────────────────────────
type GateDecision = "ALLOW" | "HOLD" | "BLOCK";

const GATE_CFG: Record<GateDecision, { color: string; bg: string; label: string }> = {
  ALLOW: { color: "oklch(0.72 0.18 145)", bg: "oklch(0.72 0.18 145 / 0.10)", label: "ALLOW" },
  HOLD:  { color: "oklch(0.72 0.18 45)",  bg: "oklch(0.72 0.18 45 / 0.10)",  label: "HOLD"  },
  BLOCK: { color: "oklch(0.65 0.25 25)",  bg: "oklch(0.65 0.25 25 / 0.10)",  label: "BLOCK" },
};

const DOMAIN_AGENTS: Record<WorldDomain, number> = {
  trading: 17,
  bank: 12,
  ecom: 12,
};

// ─── WorldCard (données réelles) ──────────────────────────────────────────────
function WorldCard({ domain, active, onClick, tickets, guardStats }: {
  domain: WorldDomain;
  active: boolean;
  onClick: () => void;
  tickets: any[];
  guardStats: any;
}) {
  const colors = DOMAIN_COLORS[domain];
  const ds = (guardStats?.byDomain?.[domain] ?? { total: 0, blocked: 0, held: 0 }) as { total: number; blocked: number; held: number };
  const domainTickets = tickets.filter((t: any) => t.domain === domain);
  const lastTicket = domainTickets[0] as any | undefined;
  const lastGate = (lastTicket?.decision ?? null) as GateDecision | null;
  const gate = lastGate ? GATE_CFG[lastGate] : null;
  const proofComplete = lastTicket ? !!(lastTicket.auditTrail as any)?.merkle_root : false;
  const agentsActive = DOMAIN_AGENTS[domain];
  const reasons = lastTicket?.reasons as string[] | undefined;

  return (
    <button
      onClick={onClick}
      className="rounded text-left transition-all w-full"
      style={{
        background: active ? colors.bg : "oklch(0.11 0.01 240)",
        border: `1px solid ${active ? colors.border : "oklch(0.18 0.01 240)"}`,
        outline: active ? `1px solid ${colors.accent}` : "none",
        outlineOffset: "1px",
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3"
        style={{ borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
        <div className="flex items-center gap-2">
          <span className="text-xl">{colors.icon}</span>
          <div>
            <div className="text-xs font-mono font-bold" style={{ color: colors.accent }}>{colors.label}</div>
            <div className="text-[9px] font-mono" style={{ color: "oklch(0.50 0.01 240)" }}>
              {agentsActive} agents actifs
            </div>
          </div>
        </div>
        <div className="flex flex-col items-end gap-1">
          {gate ? (
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded"
              style={{ background: gate.bg, border: `1px solid ${gate.color}40`, color: gate.color }}>
              X-108 {gate.label}
            </span>
          ) : (
            <span className="text-[9px] font-mono px-2 py-0.5 rounded"
              style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.40 0.01 240)" }}>
              Aucune décision
            </span>
          )}
          <span className="text-[9px] font-mono" style={{ color: "oklch(0.50 0.01 240)" }}>
            {ds.total} décisions
          </span>
        </div>
      </div>

      {/* Dernier verdict */}
      <div className="px-4 py-2" style={{ borderBottom: "1px solid oklch(0.14 0.01 240)" }}>
        <div className="text-[9px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>Dernier intent</div>
        <div className="text-[10px] font-mono font-bold mt-0.5 truncate" style={{ color: "oklch(0.80 0.01 240)" }}>
          {lastTicket?.intentId ?? "—"}
        </div>
        {reasons && reasons.length > 0 && (
          <div className="text-[8px] font-mono mt-0.5 truncate" style={{ color: "oklch(0.45 0.01 240)" }}>
            {reasons[0]}
          </div>
        )}
      </div>

      {/* Métriques DB */}
      <div className="px-4 py-2 grid grid-cols-3 gap-2">
        {[
          { label: "Total", value: String(ds.total), color: colors.accent },
          { label: "Bloquées", value: String(ds.blocked), color: "oklch(0.65 0.25 25)" },
          { label: "En attente", value: String(ds.held), color: "oklch(0.72 0.18 45)" },
        ].map(m => (
          <div key={m.label}>
            <div className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>{m.label}</div>
            <div className="text-[14px] font-mono font-bold" style={{ color: m.color }}>{m.value}</div>
          </div>
        ))}
      </div>

      {/* Proof */}
      <div className="px-4 pb-3 flex items-center justify-between">
        <span className="text-[8px] font-mono" style={{ color: proofComplete ? "oklch(0.72 0.18 145)" : lastTicket ? "oklch(0.72 0.18 45)" : "oklch(0.40 0.01 240)" }}>
          {proofComplete ? "✓ Proof complete" : lastTicket ? "⚠ Proof partial" : "— Aucune preuve"}
        </span>
        {lastTicket && (
          <span className="text-[8px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>
            #{lastTicket.id}
          </span>
        )}
      </div>
    </button>
  );
}

// ─── QuickAccessCard ──────────────────────────────────────────────────────────
function QuickAccessCard({ href, icon, label, description, accent }: {
  href: string; icon: string; label: string; description: string; accent: string;
}) {
  return (
    <Link href={href}>
      <div className="rounded p-4 cursor-pointer transition-all"
        style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}
        onMouseOver={e => { (e.currentTarget as HTMLDivElement).style.borderColor = accent + "60"; }}
        onMouseOut={e => { (e.currentTarget as HTMLDivElement).style.borderColor = "oklch(0.18 0.01 240)"; }}
      >
        <div className="text-xl mb-2">{icon}</div>
        <div className="text-[11px] font-mono font-bold" style={{ color: accent }}>{label}</div>
        <div className="text-[9px] font-mono mt-1" style={{ color: "oklch(0.50 0.01 240)" }}>{description}</div>
      </div>
    </Link>
  );
}

// ─── Mission ──────────────────────────────────────────────────────────────────
export default function Mission() {
  const { domain, setDomain } = useWorld();

  // Données réelles
  const { data: guardStats, isLoading: loadingGuard } = trpc.proof.guardStats.useQuery(undefined, {
    refetchInterval: 30000,
  });
  const { data: tickets = [], isLoading: loadingTickets } = trpc.proof.allTickets.useQuery(
    { limit: 100 },
    { refetchInterval: 30000 }
  ) as { data: any[]; isLoading: boolean };

  const isLoading = loadingGuard || loadingTickets;

  // Alertes critiques
  const criticalTickets = tickets.filter((t: any) => t.decision === "BLOCK" || t.decision === "HOLD");
  const lastCritical = criticalTickets[0] as any | undefined;
  const proofGaps = tickets.filter((t: any) => !(t.auditTrail as any)?.merkle_root);

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 flex flex-col gap-6">

      {/* ── En-tête Mission ─────────────────────────────────────────────────── */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-base font-mono font-bold tracking-widest" style={{ color: "oklch(0.72 0.18 145)" }}>
            OBSIDIA OS4
          </h1>
          <p className="text-[10px] font-mono mt-0.5" style={{ color: "oklch(0.50 0.01 240)" }}>
            Gouvernance pour agents autonomes — Observation · Interprétation · Décision · Preuve
          </p>
        </div>
        <div className="flex items-center gap-2">
          {isLoading && (
            <span className="text-[9px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>chargement…</span>
          )}
          <div className="flex items-center gap-1.5 px-2 py-1 rounded text-[9px] font-mono"
            style={{ background: "oklch(0.14 0.04 145)", border: "1px solid oklch(0.72 0.18 145 / 0.3)", color: "oklch(0.72 0.18 145)" }}>
            <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: "oklch(0.72 0.18 145)" }} />
            3 mondes actifs
          </div>
        </div>
      </div>

      {/* ── Stats globales réelles ───────────────────────────────────────────── */}
      {guardStats && (
        <div className="rounded p-3 grid grid-cols-2 md:grid-cols-4 gap-3"
          style={{ background: "oklch(0.115 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
          {[
            { label: "Décisions totales", value: guardStats.totalDecisions, color: "oklch(0.65 0.18 240)" },
            { label: "Bloquées X-108",    value: guardStats.totalBlocked,   color: "oklch(0.65 0.25 25)" },
            { label: "En attente",        value: guardStats.totalHeld,      color: "oklch(0.72 0.18 45)" },
            { label: "Proof gaps",        value: proofGaps.length,          color: "#a78bfa" },
          ].map(s => (
            <div key={s.label} className="flex flex-col gap-0.5">
              <div className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>{s.label}</div>
              <div className="text-xl font-mono font-bold" style={{ color: s.color }}>{s.value}</div>
            </div>
          ))}
        </div>
      )}

      {/* ── Pipeline OS4 ────────────────────────────────────────────────────── */}
      <div className="rounded p-3 flex items-center gap-1 overflow-x-auto"
        style={{ background: "oklch(0.115 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
        {[
          { step: "Observe",    color: "oklch(0.65 0.18 240)", desc: "Agents domaine lisent les signaux" },
          { step: "Interpret",  color: "oklch(0.72 0.18 145)", desc: "Agents interprètent et proposent" },
          { step: "Contradict", color: "oklch(0.72 0.18 45)",  desc: "Agents détectent les conflits" },
          { step: "Aggregate",  color: "#a78bfa",               desc: "Voix unique du domaine" },
          { step: "X-108",      color: "oklch(0.72 0.18 145)", desc: "Gate de gouvernance" },
          { step: "Proof",      color: "oklch(0.60 0.15 290)", desc: "Traçabilité formelle" },
        ].map((s, i, arr) => (
          <React.Fragment key={s.step}>
            <div className="flex flex-col items-center gap-0.5 shrink-0">
              <span className="text-[9px] font-mono font-bold px-2 py-0.5 rounded"
                style={{ background: s.color + "18", border: `1px solid ${s.color}40`, color: s.color }}>
                {s.step}
              </span>
              <span className="text-[7px] font-mono text-center" style={{ color: "oklch(0.40 0.01 240)", maxWidth: "80px" }}>
                {s.desc}
              </span>
            </div>
            {i < arr.length - 1 && <span className="text-[10px] shrink-0" style={{ color: "oklch(0.30 0.01 240)" }}>→</span>}
          </React.Fragment>
        ))}
      </div>

      {/* ── 3 WorldCards (données réelles) ──────────────────────────────────── */}
      <div>
        <div className="text-[9px] font-mono mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>
          Sélectionner un monde pour filtrer toutes les surfaces
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {(["trading", "bank", "ecom"] as WorldDomain[]).map(d => (
            <WorldCard
              key={d}
              domain={d}
              active={domain === d}
              onClick={() => setDomain(d)}
              tickets={tickets}
              guardStats={guardStats}
            />
          ))}
        </div>
      </div>

      {/* ── Accès rapide 4 surfaces ──────────────────────────────────────────── */}
      <div>
        <div className="text-[9px] font-mono mb-2" style={{ color: "oklch(0.45 0.01 240)" }}>
          Surfaces de travail
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <QuickAccessCard href="/live"    icon="⚡" label="Live"    description="Console du présent — décisions en cours, feed d'enveloppes, proof snapshot" accent="oklch(0.72 0.18 145)" />
          <QuickAccessCard href="/future"  icon="🔭" label="Future"  description="Cockpit de simulation — configurer, lancer, observer la constellation agentique" accent="oklch(0.65 0.18 240)" />
          <QuickAccessCard href="/past"    icon="📚" label="Past"    description="Registre prouvé — historique, proof chains, replay, compare runs" accent="#a78bfa" />
          <QuickAccessCard href="/control" icon="🛡️" label="Control" description="Tour de commandement — santé système, alertes, next actions" accent="oklch(0.72 0.18 45)" />
        </div>
      </div>

      {/* ── Alertes critiques (données réelles) ─────────────────────────────── */}
      {(lastCritical || proofGaps.length > 0) && (
        <div>
          <div className="text-[9px] font-mono mb-2" style={{ color: "oklch(0.65 0.25 25)" }}>
            ⚠ Alertes actives
          </div>
          <div className="flex flex-col gap-2">
            {lastCritical && (
              <Link href="/past">
                <div className="rounded p-3 cursor-pointer flex items-center gap-3"
                  style={{ background: "oklch(0.10 0.04 25 / 0.4)", border: "1px solid oklch(0.65 0.25 25 / 0.4)" }}>
                  <span className="text-lg">🚨</span>
                  <div className="flex-1 min-w-0">
                    <div className="text-[11px] font-mono font-bold" style={{ color: "oklch(0.65 0.25 25)" }}>
                      Dernier run critique — {lastCritical.decision} · {String(lastCritical.domain ?? "").toUpperCase()}
                    </div>
                    <div className="text-[9px] font-mono mt-0.5 truncate" style={{ color: "oklch(0.45 0.01 240)" }}>
                      Intent: {lastCritical.intentId} · #{lastCritical.id}
                    </div>
                  </div>
                  <span style={{ color: "oklch(0.35 0.01 240)" }}>→</span>
                </div>
              </Link>
            )}
            {proofGaps.length > 0 && (
              <Link href="/past">
                <div className="rounded p-3 cursor-pointer flex items-center gap-3"
                  style={{ background: "oklch(0.10 0.04 290 / 0.4)", border: "1px solid oklch(0.60 0.15 290 / 0.4)" }}>
                  <span className="text-lg">🔐</span>
                  <div className="flex-1 min-w-0">
                    <div className="text-[11px] font-mono font-bold" style={{ color: "#a78bfa" }}>
                      {proofGaps.length} proof gap{proofGaps.length > 1 ? "s" : ""} détecté{proofGaps.length > 1 ? "s" : ""}
                    </div>
                    <div className="text-[9px] font-mono mt-0.5" style={{ color: "oklch(0.45 0.01 240)" }}>
                      Décisions sans attestation Merkle complète — voir Past
                    </div>
                  </div>
                  <span style={{ color: "oklch(0.35 0.01 240)" }}>→</span>
                </div>
              </Link>
            )}
          </div>
        </div>
      )}

    </div>
  );
}
