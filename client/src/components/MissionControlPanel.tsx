import React, { useState, useMemo } from "react";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import type { DecisionTicket } from "../../../drizzle/schema";

// ─── Types ──────────────────────────────────────────────────────────────────────────────────
type DomainFilter  = "TOUS" | "trading" | "bank" | "ecom";
type VerdictFilter = "TOUS" | "ALLOW" | "HOLD" | "BLOCK";
// Filtre temporel : ALL = pas de limite, 1h, 24h, 7j
type TimeFilter = "ALL" | "1h" | "24h" | "7j";

// Seuil en ms pour chaque option
const TIME_FILTER_MS: Record<TimeFilter, number | null> = {
  ALL: null,
  "1h":  60 * 60 * 1000,
  "24h": 24 * 60 * 60 * 1000,
  "7j":  7 * 24 * 60 * 60 * 1000,
};
const DOMAIN_COLOR: Record<string, string> = {
  trading: "oklch(0.65 0.18 220)",
  bank:    "oklch(0.75 0.18 75)",
  ecom:    "oklch(0.72 0.18 145)",
};
const VERDICT_COLOR: Record<string, string> = {
  ALLOW: "#4ade80",
  HOLD:  "#fbbf24",
  BLOCK: "#f87171",
};

// ─── Helpers pour extraire les données des champs JSON ────────────────────────
function getAuditTrail(t: DecisionTicket): { merkle_root?: string; anchor_ref?: string; hash_now?: string } {
  if (!t.auditTrail || typeof t.auditTrail !== "object") return {};
  return t.auditTrail as { merkle_root?: string; anchor_ref?: string; hash_now?: string };
}
function getX108(t: DecisionTicket): { tau?: number; elapsed?: number; irr?: boolean } {
  if (!t.x108 || typeof t.x108 !== "object") return {};
  return t.x108 as { tau?: number; elapsed?: number; irr?: boolean };
}
function getReasons(t: DecisionTicket): string[] {
  if (!Array.isArray(t.reasons)) return [];
  return t.reasons as string[];
}

// ─── Composant ────────────────────────────────────────────────────────────────
export default function MissionControlPanel() {
  const [, navigate] = useLocation();

  // Filtres
  const [domainFilter,  setDomainFilter]  = useState<DomainFilter>("TOUS");
  const [verdictFilter, setVerdictFilter] = useState<VerdictFilter>("TOUS");
  const [showFallbackOnly, setShowFallbackOnly] = useState(false);
  const [timeFilter, setTimeFilter] = useState<TimeFilter>("ALL");

  // Données backend
  const ticketsQuery    = trpc.proof.allTickets.useQuery({ limit: 50 }, { refetchInterval: 8000 });
  const guardStatsQuery = trpc.proof.guardStats.useQuery(undefined, { refetchInterval: 10000 });
  const pythonStatusQuery = trpc.engine.pythonStatus.useQuery(undefined, { refetchInterval: 15000 });

  const tickets = ticketsQuery.data ?? [];
  const guardStats = guardStatsQuery.data;
  // Type aligné sur le vrai retour de engine.pythonStatus (server/routers.ts)
  type PythonStatus = {
    pythonOnline: boolean;
    pythonVersion: string | null;
    totalDecisions: number;
    lastDecisionTs: number | null;
    lastDecision: string | null;
    lastDomain: string | null;
  };
  const pythonStatus = pythonStatusQuery.data as PythonStatus | undefined;

  // ── Filtrage ──
  const filtered = useMemo(() => {
    const now = Date.now();
    const windowMs = TIME_FILTER_MS[timeFilter];
    return tickets.filter(t => {
      const domainOk  = domainFilter  === "TOUS" || t.domain  === domainFilter;
      const verdictOk = verdictFilter === "TOUS" || t.decision === verdictFilter;
      // fallback = pas de anchor_ref dans auditTrail (heuristique)
      const audit = getAuditTrail(t);
      const isFallback = !audit.anchor_ref;
      const fallbackOk = !showFallbackOnly || isFallback;
      // Filtre temporel : compare createdAt (ms UTC) avec now - windowMs
      const ts = t.createdAt instanceof Date ? t.createdAt.getTime() : Number(t.createdAt);
      const timeOk = windowMs === null || (now - ts) <= windowMs;
      return domainOk && verdictOk && fallbackOk && timeOk;
    });
  }, [tickets, domainFilter, verdictFilter, showFallbackOnly, timeFilter]);

  // ── Dernier run par domaine ──
  const lastByDomain = useMemo(() => {
    const map: Record<string, DecisionTicket> = {};
    for (const t of tickets) {
      if (t.domain && !map[t.domain]) map[t.domain] = t;
    }
    return map;
  }, [tickets]);

  // ── Derniers HOLD/BLOCK ──
  const lastIncidents = useMemo(() =>
    tickets.filter(t => t.decision === "BLOCK" || t.decision === "HOLD").slice(0, 5),
    [tickets]
  );

  // ── Deep-links — Règle 6 : contexte prérempli ──
  function openSimuler(t: DecisionTicket) {
    const domain = t.domain ?? "trading";
    // replayRef = "seed:step" si disponible
    const seed = t.replayRef?.split(":")?.[0] ?? "";
    navigate(`/simuler?domain=${domain}&seed=${seed}&rerun=1`);
  }
  function openPreuve(t: DecisionTicket) {
    navigate(`/preuves?ticketId=${t.id}`);
  }
  function openDecision(t: DecisionTicket) {
    const audit = getAuditTrail(t);
    const ref = audit.anchor_ref ?? audit.hash_now ?? String(t.id);
    navigate(`/decision?traceId=${ref}`);
  }

  function exportCSV() {
    const header = ["id", "domain", "decision", "source", "replayRef", "createdAt", "reason"];
    const rows = filtered.map(t => {
      const reasons = getReasons(t);
      const ts = t.createdAt instanceof Date ? t.createdAt.toISOString() : new Date(Number(t.createdAt)).toISOString();
      return [
        String(t.id),
        t.domain ?? "",
        t.decision,
        t.intentId ?? "",
        t.replayRef ?? "",
        ts,
        (reasons[0] ?? "").replace(/,/g, ";"),
      ].join(",");
    });
    const csv = [header.join(","), ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const period = timeFilter !== "ALL" ? `_${timeFilter}` : "";
    a.download = `os4_tickets${period}_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="flex flex-col gap-6">

      {/* ── 1. Health globale ── */}
      <div className="grid grid-cols-3 gap-3">
        <HealthCard
          label="Backend Python"
          status={pythonStatus?.pythonOnline ? "ONLINE" : "OFFLINE"}
          detail={pythonStatus?.pythonOnline
            ? `${pythonStatus.totalDecisions} décisions${pythonStatus.pythonVersion ? ` — v${pythonStatus.pythonVersion}` : ""}`
            : "Fallback actif"}
          color={pythonStatus?.pythonOnline ? "#4ade80" : "#f87171"}
        />
        <HealthCard
          label="Base de données"
          status={guardStats ? "OK" : "—"}
          detail={guardStats ? `${guardStats.totalDecisions ?? 0} tickets` : "En attente"}
          color={guardStats ? "#4ade80" : "oklch(0.55 0.01 240)"}
        />
        <HealthCard
          label="Dernier run"
          status={tickets[0]?.decision ?? "—"}
          detail={tickets[0] ? `${tickets[0].domain?.toUpperCase() ?? "?"} · ${new Date(tickets[0].createdAt).toLocaleTimeString("fr-FR")}` : "Aucun ticket"}
          color={tickets[0] ? VERDICT_COLOR[tickets[0].decision] ?? "oklch(0.55 0.01 240)" : "oklch(0.55 0.01 240)"}
        />
      </div>

      {/* ── 2. Dernier run par domaine ── */}
      <div>
        <div className="text-[9px] font-mono tracking-widest uppercase mb-2" style={{ color: "oklch(0.40 0.01 240)" }}>
          Dernier run par domaine
        </div>
        <div className="grid grid-cols-3 gap-2">
          {(["trading", "bank", "ecom"] as const).map(d => {
            const t = lastByDomain[d];
            const color = DOMAIN_COLOR[d];
            return (
              <div key={d} className="rounded p-3" style={{ background: "oklch(0.10 0.01 240)", border: `1px solid ${color}33` }}>
                <div className="text-[9px] font-mono font-bold uppercase mb-1" style={{ color }}>{d}</div>
                {t ? (
                  <>
                    <div className="font-mono text-sm font-bold" style={{ color: VERDICT_COLOR[t.decision] ?? "oklch(0.55 0.01 240)" }}>
                      {t.decision}
                    </div>
                    <div className="text-[9px] font-mono mt-0.5" style={{ color: "oklch(0.40 0.01 240)" }}>
                      {new Date(t.createdAt).toLocaleTimeString("fr-FR")}
                    </div>
                    <div className="flex gap-1 mt-2">
                      <ActionBtn label="↺ Relancer" onClick={() => openSimuler(t)} color={color} />
                      <ActionBtn label="🔍 Preuve" onClick={() => openPreuve(t)} color="oklch(0.55 0.01 240)" />
                    </div>
                  </>
                ) : (
                  <div className="text-[9px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>Aucun ticket</div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* ── 3. Derniers HOLD/BLOCK ── */}
      {lastIncidents.length > 0 && (
        <div>
          <div className="text-[9px] font-mono tracking-widest uppercase mb-2" style={{ color: "#fbbf24" }}>
            Derniers incidents (HOLD / BLOCK)
          </div>
          <div className="flex flex-col gap-1">
            {lastIncidents.map((t, i) => {
              const vColor = VERDICT_COLOR[t.decision] ?? "oklch(0.55 0.01 240)";
              const reasons = getReasons(t);
              return (
                <div key={i} className="flex items-center gap-3 px-3 py-2 rounded" style={{ background: "oklch(0.10 0.01 240)", border: `1px solid ${vColor}22` }}>
                  <span className="font-mono text-[10px] font-bold w-12" style={{ color: vColor }}>{t.decision}</span>
                  <span className="text-[9px] font-mono" style={{ color: DOMAIN_COLOR[t.domain] ?? "oklch(0.55 0.01 240)" }}>
                    {t.domain?.toUpperCase() ?? "?"}
                  </span>
                  <span className="text-[9px] font-mono flex-1 truncate" style={{ color: "oklch(0.50 0.01 240)" }}>
                    {reasons[0] ?? "—"}
                  </span>
                  <ActionBtn label="⚖ Décision" onClick={() => openDecision(t)} color={vColor} />
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── 4. Filtres + compteur ── */}
      <div className="flex flex-wrap gap-2 items-center justify-between mb-1">
        <span className="text-[9px] font-mono tracking-widest uppercase" style={{ color: "oklch(0.40 0.01 240)" }}>Filtres</span>
        <div className="flex items-center gap-2 px-3 py-1 rounded" style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.16 0.01 240)" }}>
          <span className="text-[9px] font-mono font-bold" style={{ color: filtered.length === 0 ? "oklch(0.40 0.01 240)" : "oklch(0.72 0.18 145)" }}>
            {filtered.length}
          </span>
          <span className="text-[9px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>
            {filtered.length > 1 ? "tickets" : "ticket"}{timeFilter !== "ALL" ? ` sur ${timeFilter}` : " au total"}
          </span>
        </div>
      </div>
      <div className="flex flex-wrap gap-2 items-center">
        <FilterGroup
          label="Domaine"
          options={["TOUS", "trading", "bank", "ecom"]}
          value={domainFilter}
          onChange={v => setDomainFilter(v as DomainFilter)}
          colorMap={DOMAIN_COLOR}
        />
        <FilterGroup
          label="Verdict"
          options={["TOUS", "ALLOW", "HOLD", "BLOCK"]}
          value={verdictFilter}
          onChange={v => setVerdictFilter(v as VerdictFilter)}
          colorMap={VERDICT_COLOR}
        />
        {/* Filtre temporel — agit sur createdAt des tickets */}
        <FilterGroup
          label="Période"
          options={["ALL", "1h", "24h", "7j"]}
          value={timeFilter}
          onChange={v => setTimeFilter(v as TimeFilter)}
        />
        <button
          onClick={() => setShowFallbackOnly(v => !v)}
          className="px-2 py-0.5 rounded font-mono text-[9px] font-bold"
          style={{
            background: showFallbackOnly ? "oklch(0.12 0.08 75 / 0.3)" : "oklch(0.12 0.01 240)",
            border: `1px solid ${showFallbackOnly ? "oklch(0.75 0.18 75 / 0.5)" : "oklch(0.18 0.01 240)"}`,
            color: showFallbackOnly ? "oklch(0.75 0.18 75)" : "oklch(0.45 0.01 240)",
          }}
        >
          {showFallbackOnly ? "⚠ Fallback seulement" : "Tous les runs"}
        </button>
        {/* Bouton Export CSV */}
        <button
          onClick={exportCSV}
          disabled={filtered.length === 0}
          className="px-2 py-0.5 rounded font-mono text-[9px] font-bold ml-auto"
          style={{
            background: filtered.length > 0 ? "oklch(0.65 0.18 240 / 0.12)" : "oklch(0.10 0.01 240)",
            border: `1px solid ${filtered.length > 0 ? "oklch(0.65 0.18 240 / 0.40)" : "oklch(0.16 0.01 240)"}`,
            color: filtered.length > 0 ? "oklch(0.65 0.18 240)" : "oklch(0.30 0.01 240)",
            cursor: filtered.length > 0 ? "pointer" : "not-allowed",
          }}
        >
          ⬇ Export CSV ({filtered.length})
        </button>
      </div>

      {/* ── 5. Tableau tickets ── */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <div className="text-[9px] font-mono tracking-widest uppercase" style={{ color: "oklch(0.40 0.01 240)" }}>
            Tickets ({filtered.length} / {tickets.length})
          </div>
          {ticketsQuery.isFetching && (
            <span className="text-[9px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>⟳ Actualisation…</span>
          )}
        </div>
        {filtered.length === 0 ? (
          <div className="py-8 text-center font-mono text-xs" style={{ color: "oklch(0.35 0.01 240)" }}>
            Aucun ticket correspondant aux filtres
          </div>
        ) : (
          <div className="rounded overflow-hidden" style={{ border: "1px solid oklch(0.16 0.01 240)" }}>
            <table className="w-full text-[10px] font-mono">
              <thead>
                <tr style={{ background: "oklch(0.09 0.01 240)" }}>
                  {["Domaine", "Verdict", "Raison", "Ref", "Heure", "Actions"].map(h => (
                    <th key={h} className="px-3 py-2 text-left font-bold" style={{ color: "oklch(0.45 0.01 240)" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.slice(0, 20).map((t, i) => {
                  const vColor = VERDICT_COLOR[t.decision] ?? "oklch(0.55 0.01 240)";
                  const dColor = DOMAIN_COLOR[t.domain] ?? "oklch(0.55 0.01 240)";
                  const audit = getAuditTrail(t);
                  const reasons = getReasons(t);
                  const isFallback = !audit.anchor_ref;
                  return (
                    <tr key={i} style={{ borderTop: "1px solid oklch(0.13 0.01 240)", background: i % 2 === 0 ? "oklch(0.10 0.01 240)" : "oklch(0.09 0.01 240)" }}>
                      <td className="px-3 py-2 font-bold" style={{ color: dColor }}>{t.domain?.toUpperCase() ?? "—"}</td>
                      <td className="px-3 py-2 font-bold" style={{ color: vColor }}>{t.decision}</td>
                      <td className="px-3 py-2 max-w-[160px] truncate" style={{ color: "oklch(0.50 0.01 240)" }}>
                        {reasons[0] ?? "—"}
                      </td>
                      <td className="px-3 py-2" style={{ color: "oklch(0.40 0.01 240)" }}>
                        {isFallback
                          ? <span style={{ color: "oklch(0.75 0.18 75)" }}>⚠ fallback</span>
                          : <span style={{ color: "#4ade80" }}>{(audit.hash_now ?? "").slice(0, 8)}…</span>
                        }
                      </td>
                      <td className="px-3 py-2" style={{ color: "oklch(0.40 0.01 240)" }}>
                        {new Date(t.createdAt).toLocaleTimeString("fr-FR")}
                      </td>
                      <td className="px-3 py-2">
                        <div className="flex gap-1">
                          <ActionBtn label="↺" title="Relancer dans Simuler" onClick={() => openSimuler(t)} color="oklch(0.65 0.18 220)" />
                          <ActionBtn label="🔍" title="Ouvrir preuve" onClick={() => openPreuve(t)} color="oklch(0.55 0.01 240)" />
                          <ActionBtn label="⚖" title="Ouvrir décision" onClick={() => openDecision(t)} color="oklch(0.72 0.18 145)" />
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}

// ─── Sous-composants ──────────────────────────────────────────────────────────
function HealthCard({ label, status, detail, color }: { label: string; status: string; detail: string; color: string }) {
  return (
    <div className="rounded p-3" style={{ background: "oklch(0.10 0.01 240)", border: `1px solid ${color}33` }}>
      <div className="text-[9px] font-mono uppercase tracking-widest mb-1" style={{ color: "oklch(0.40 0.01 240)" }}>{label}</div>
      <div className="font-mono font-bold text-sm" style={{ color }}>{status}</div>
      <div className="text-[9px] font-mono mt-0.5" style={{ color: "oklch(0.40 0.01 240)" }}>{detail}</div>
    </div>
  );
}

function ActionBtn({ label, title, onClick, color }: { label: string; title?: string; onClick: () => void; color: string }) {
  return (
    <button
      onClick={onClick}
      title={title}
      className="px-2 py-0.5 rounded font-mono text-[9px] font-bold"
      style={{ background: color + "18", border: `1px solid ${color}44`, color }}
    >
      {label}
    </button>
  );
}

function FilterGroup({ label, options, value, onChange, colorMap }: {
  label: string;
  options: string[];
  value: string;
  onChange: (v: string) => void;
  colorMap?: Record<string, string>;
}) {
  return (
    <div className="flex items-center gap-1">
      <span className="text-[9px] font-mono mr-1" style={{ color: "oklch(0.38 0.01 240)" }}>{label}:</span>
      {options.map(o => {
        const color = colorMap?.[o] ?? "oklch(0.55 0.01 240)";
        const active = value === o;
        return (
          <button
            key={o}
            onClick={() => onChange(o)}
            className="px-2 py-0.5 rounded font-mono text-[9px] font-bold"
            style={{
              background: active ? color + "22" : "oklch(0.12 0.01 240)",
              border: `1px solid ${active ? color + "55" : "oklch(0.18 0.01 240)"}`,
              color: active ? color : "oklch(0.45 0.01 240)",
            }}
          >
            {o}
          </button>
        );
      })}
    </div>
  );
}
