import React from "react";
import { useAuth } from "@/_core/hooks/useAuth";
import { getLoginUrl } from "@/const";
import { Link } from "wouter";
import SurfaceStatusBadge from "@/components/SurfaceStatusBadge";
import { trpc } from "@/lib/trpc";

// ─── Carte de surface ─────────────────────────────────────────────────────────
type SurfaceCard = {
  path: string;
  label: string;
  type: "operable" | "pedagogical";
  status: "REAL" | "PARTIAL" | "LOCAL_ONLY" | "SCAFFOLD";
  source: "python" | "db_real" | "ws_real" | "os4_local_fallback" | "preview_local";
  description: string;
  domain?: string;
};

const SURFACES: SurfaceCard[] = [
  // Pages opérables
  {
    path: "/trading",
    label: "TradingWorld",
    type: "operable",
    status: "REAL",
    source: "python",
    description: "Ordres BUY/SELL soumis au Guard X-108. Décision Python réelle, trace_id, ticket, attestation.",
    domain: "trading",
  },
  {
    path: "/bank",
    label: "BankWorld",
    type: "operable",
    status: "REAL",
    source: "python",
    description: "Virements et retraits bancaires. HOLD X-108 si irréversible et elapsed < 108s.",
    domain: "bank",
  },
  {
    path: "/ecom",
    label: "EcomWorld",
    type: "operable",
    status: "REAL",
    source: "python",
    description: "Simulation e-commerce. Verdict canonique Python : x108_gate, market_verdict, severity.",
    domain: "ecom",
  },
  {
    path: "/simuler",
    label: "Simuler",
    type: "operable",
    status: "REAL",
    source: "python",
    description: "Scénarios adversariaux (flash_crash, bank_run…). batchRun Python-first, pythonAvailable, step.source.",
  },
  {
    path: "/decision",
    label: "Décision",
    type: "operable",
    status: "REAL",
    source: "db_real",
    description: "Centre multi-domaines. Tickets DB réels + WebSocket live. Source identifiée par événement.",
  },
  {
    path: "/preuves",
    label: "Preuves",
    type: "operable",
    status: "REAL",
    source: "python",
    description: "Replay Python, verify ticket api_store, attestation merkle_root repo Git.",
  },
  {
    path: "/controle",
    label: "Contrôle",
    type: "operable",
    status: "REAL",
    source: "python",
    description: "État des constellations, violations, severity, health. batchRun Python avec pythonAvailable.",
  },
  // Pages pédagogiques
  {
    path: "/decision-lifecycle",
    label: "Cycle de décision",
    type: "pedagogical",
    status: "LOCAL_ONLY",
    source: "preview_local",
    description: "Explication visuelle du cycle complet : observation → interprétation → Guard X-108 → ticket.",
  },
  {
    path: "/governance",
    label: "Gouvernance X-108",
    type: "pedagogical",
    status: "LOCAL_ONLY",
    source: "preview_local",
    description: "Règles X-108 : min_wait_s, elapsed_s, irréversibilité, HOLD/BLOCK/ALLOW.",
  },
  {
    path: "/how-it-works",
    label: "Comment ça marche",
    type: "pedagogical",
    status: "LOCAL_ONLY",
    source: "preview_local",
    description: "Architecture façade/noyau, chaîne de preuve, contrat canonique.",
  },
];

const CHAIN_STEPS = [
  { id: "A", label: "Observation", desc: "Agents lisent le réel du domaine", color: "oklch(0.65 0.12 240)" },
  { id: "B", label: "Interprétation", desc: "Verdict métier proposé (non souverain)", color: "oklch(0.65 0.15 200)" },
  { id: "C", label: "Contradiction", desc: "Détection conflits, unknowns, incohérences", color: "oklch(0.65 0.18 75)" },
  { id: "D", label: "Agrégation", desc: "Signal unifié par domaine", color: "oklch(0.65 0.18 50)" },
  { id: "E", label: "Guard X-108", desc: "Juge souverain unique — ALLOW / HOLD / BLOCK", color: "oklch(0.72 0.18 145)", sovereign: true },
  { id: "F", label: "Ticket / Trace", desc: "Preuve exécutable, replay, attestation", color: "oklch(0.72 0.18 145)" },
];

export default function Home() {
  const { user, isAuthenticated } = useAuth();
  const attestation = trpc.engine.attestation.useQuery({ day: undefined });
  const pythonStatus = trpc.engine.pythonStatus.useQuery(undefined, { refetchInterval: 30000 });

  const operable = SURFACES.filter((s) => s.type === "operable");
  const pedagogical = SURFACES.filter((s) => s.type === "pedagogical");

  return (
    <div
      className="min-h-screen"
      style={{ background: "oklch(0.09 0.01 240)", color: "oklch(0.85 0.02 240)" }}
    >
      {/* ── Hero ─────────────────────────────────────────────────────────── */}
      <div
        className="px-6 py-12 border-b"
        style={{ borderColor: "oklch(0.16 0.01 240)", background: "oklch(0.10 0.02 240)" }}
      >
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center gap-3 mb-4">
            <span
              className="font-mono text-xs font-bold tracking-widest px-2 py-1 rounded"
              style={{
                background: "oklch(0.13 0.06 145 / 0.4)",
                border: "1px solid oklch(0.72 0.18 145 / 0.3)",
                color: "oklch(0.72 0.18 145)",
              }}
            >
              OS4
            </span>
            <span className="font-mono text-xs" style={{ color: "oklch(0.45 0.01 240)" }}>
              Obsidia Governance Platform
            </span>
          </div>

          <h1
            className="text-3xl font-mono font-bold mb-3"
            style={{ color: "oklch(0.90 0.02 240)" }}
          >
            Gouvernance pour agents autonomes
          </h1>

          <p className="text-sm max-w-2xl mb-6" style={{ color: "oklch(0.55 0.02 240)", lineHeight: "1.7" }}>
            OS4 est la façade opérationnelle du noyau Obsidia. Chaque décision passe par le Guard X-108 —
            juge souverain unique — avant d'être exécutée. Toute valeur affichée est rattachée à une source
            explicite : <span style={{ color: "oklch(0.72 0.18 145)" }}>python</span>,{" "}
            <span style={{ color: "oklch(0.65 0.18 220)" }}>db_real</span>,{" "}
            <span style={{ color: "oklch(0.70 0.15 180)" }}>ws_real</span> ou{" "}
            <span style={{ color: "oklch(0.75 0.18 75)" }}>os4_local_fallback</span>.
          </p>

          {/* Statut Python live + Attestation */}
          <div className="flex flex-wrap gap-3">
          <div
            className="inline-flex items-center gap-3 px-3 py-2 rounded font-mono text-xs"
            style={{
              background: "oklch(0.12 0.04 145 / 0.3)",
              border: "1px solid oklch(0.72 0.18 145 / 0.25)",
            }}
          >
            <span style={{ color: "oklch(0.45 0.01 240)" }}>Attestation noyau :</span>
            {attestation.isLoading ? (
              <span style={{ color: "oklch(0.45 0.01 240)" }}>chargement…</span>
            ) : attestation.data?.merkle_root ? (
              <>
                <span style={{ color: "oklch(0.72 0.18 145)" }}>
                  {attestation.data.merkle_root.slice(0, 16)}…
                </span>
                <span
                  className="px-1.5 py-0.5 rounded text-[9px]"
                  style={{
                    background: "oklch(0.13 0.06 145 / 0.4)",
                    color: "oklch(0.72 0.18 145)",
                  }}
                >
                  ✓ LIVE
                </span>
              </>
            ) : (
              <span style={{ color: "oklch(0.75 0.18 75)" }}>Python hors ligne — fallback actif</span>
            )}
          </div>
          {/* Statut Python live */}
          <div
            className="inline-flex items-center gap-3 px-3 py-2 rounded font-mono text-xs"
            style={{
              background: pythonStatus.data?.pythonOnline ? "oklch(0.12 0.06 145 / 0.3)" : "oklch(0.12 0.04 75 / 0.3)",
              border: `1px solid ${pythonStatus.data?.pythonOnline ? "oklch(0.72 0.18 145 / 0.25)" : "oklch(0.75 0.18 75 / 0.25)"}`,
            }}
          >
            <span style={{ color: "oklch(0.45 0.01 240)" }}>Backend Python :</span>
            {pythonStatus.isLoading ? (
              <span style={{ color: "oklch(0.45 0.01 240)" }}>vérification…</span>
            ) : pythonStatus.data?.pythonOnline ? (
              <span style={{ color: "oklch(0.72 0.18 145)" }}>EN LIGNE</span>
            ) : (
              <span style={{ color: "oklch(0.75 0.18 75)" }}>HORS LIGNE — fallback actif</span>
            )}
            {pythonStatus.data && (
              <span style={{ color: "oklch(0.45 0.01 240)" }}>
                {pythonStatus.data.totalDecisions} décisions en DB
                {pythonStatus.data.lastDecision && (
                  <> · dernière : <span style={{ color: pythonStatus.data.lastDecision === "ALLOW" ? "#4ade80" : pythonStatus.data.lastDecision === "HOLD" ? "#fbbf24" : "#f87171" }}>{pythonStatus.data.lastDecision}</span></>
                )}
              </span>
            )}
          </div>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-10 space-y-12">

        {/* ── Chaîne de décision ──────────────────────────────────────────── */}
        <section>
          <h2 className="font-mono text-xs font-bold tracking-widest mb-5" style={{ color: "oklch(0.45 0.01 240)" }}>
            ARCHITECTURE — CHAÎNE DE DÉCISION
          </h2>
          <div className="flex flex-wrap items-center gap-1">
            {CHAIN_STEPS.map((step, i) => (
              <React.Fragment key={step.id}>
                <div
                  className="flex flex-col items-center px-3 py-2 rounded text-center"
                  style={{
                    background: step.sovereign
                      ? "oklch(0.13 0.06 145 / 0.5)"
                      : "oklch(0.12 0.02 240 / 0.5)",
                    border: `1px solid ${step.color}${step.sovereign ? "66" : "33"}`,
                    minWidth: "90px",
                  }}
                >
                  <span
                    className="font-mono text-[9px] font-bold mb-0.5"
                    style={{ color: step.color }}
                  >
                    {step.id}
                  </span>
                  <span
                    className="font-mono text-[10px] font-bold"
                    style={{ color: step.sovereign ? "oklch(0.72 0.18 145)" : "oklch(0.75 0.02 240)" }}
                  >
                    {step.label}
                  </span>
                  <span
                    className="text-[9px] mt-0.5 leading-tight"
                    style={{ color: "oklch(0.40 0.01 240)" }}
                  >
                    {step.desc}
                  </span>
                </div>
                {i < CHAIN_STEPS.length - 1 && (
                  <span className="font-mono text-xs" style={{ color: "oklch(0.30 0.01 240)" }}>→</span>
                )}
              </React.Fragment>
            ))}
          </div>
          <p className="text-[10px] font-mono mt-3" style={{ color: "oklch(0.35 0.01 240)" }}>
            Règle : <span style={{ color: "oklch(0.72 0.18 145)" }}>les agents proposent — X-108 dispose.</span>{" "}
            Aucun agent ne peut autoriser seul une action irréversible.
          </p>
        </section>

        {/* ── Loi de source de vérité ─────────────────────────────────────── */}
        <section>
          <h2 className="font-mono text-xs font-bold tracking-widest mb-4" style={{ color: "oklch(0.45 0.01 240)" }}>
            LOI DE SOURCE DE VÉRITÉ
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
            {[
              { src: "python", icon: "⬡", color: "oklch(0.72 0.18 145)", desc: "Décision backend Python Obsidia-lab-trad" },
              { src: "db_real", icon: "◈", color: "oklch(0.65 0.18 220)", desc: "Donnée lue depuis MySQL/TiDB" },
              { src: "ws_real", icon: "◉", color: "oklch(0.70 0.15 180)", desc: "Donnée WebSocket temps réel" },
              { src: "os4_local_fallback", icon: "⚠", color: "oklch(0.75 0.18 75)", desc: "Moteur local (Python indisponible)" },
              { src: "preview_local", icon: "○", color: "oklch(0.55 0.05 240)", desc: "Simulation pédagogique locale" },
            ].map((s) => (
              <div
                key={s.src}
                className="p-2 rounded"
                style={{
                  background: "oklch(0.11 0.01 240 / 0.5)",
                  border: "1px solid oklch(0.18 0.01 240)",
                }}
              >
                <div className="flex items-center gap-1 mb-1">
                  <span style={{ color: s.color, fontSize: "12px" }}>{s.icon}</span>
                  <span className="font-mono text-[10px] font-bold" style={{ color: s.color }}>
                    {s.src}
                  </span>
                </div>
                <p className="text-[9px] leading-tight" style={{ color: "oklch(0.40 0.01 240)" }}>
                  {s.desc}
                </p>
              </div>
            ))}
          </div>
          <p className="text-[10px] font-mono mt-2" style={{ color: "oklch(0.35 0.01 240)" }}>
            Un fallback peut exister. Il ne peut jamais usurper la décision finale.
          </p>
        </section>

        {/* ── Pages opérables ─────────────────────────────────────────────── */}
        <section>
          <h2 className="font-mono text-xs font-bold tracking-widest mb-1" style={{ color: "oklch(0.45 0.01 240)" }}>
            SURFACES OPÉRABLES
          </h2>
          <p className="text-[10px] font-mono mb-4" style={{ color: "oklch(0.35 0.01 240)" }}>
            Ces pages lisent des données backend réelles. Chaque valeur a une source identifiée.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {operable.map((s) => (
              <Link key={s.path} href={s.path}>
                <div
                  className="p-4 rounded cursor-pointer transition-all"
                  style={{
                    background: "oklch(0.11 0.02 240 / 0.5)",
                    border: "1px solid oklch(0.18 0.01 240)",
                  }}
                  onMouseOver={(e) => {
                    (e.currentTarget as HTMLDivElement).style.borderColor = "oklch(0.72 0.18 145 / 0.4)";
                  }}
                  onMouseOut={(e) => {
                    (e.currentTarget as HTMLDivElement).style.borderColor = "oklch(0.18 0.01 240)";
                  }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-mono text-sm font-bold" style={{ color: "oklch(0.85 0.02 240)" }}>
                      {s.label}
                    </span>
                    <SurfaceStatusBadge status={s.status} source={s.source} />
                  </div>
                  <p className="text-[10px] leading-relaxed" style={{ color: "oklch(0.45 0.01 240)" }}>
                    {s.description}
                  </p>
                  {s.domain && (
                    <div
                      className="mt-2 inline-block font-mono text-[9px] px-1.5 py-0.5 rounded"
                      style={{
                        background: "oklch(0.13 0.02 240 / 0.5)",
                        border: "1px solid oklch(0.22 0.01 240)",
                        color: "oklch(0.50 0.01 240)",
                      }}
                    >
                      domaine : {s.domain}
                    </div>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* ── Pages pédagogiques ──────────────────────────────────────────── */}
        <section>
          <h2 className="font-mono text-xs font-bold tracking-widest mb-1" style={{ color: "oklch(0.45 0.01 240)" }}>
            SURFACES PÉDAGOGIQUES
          </h2>
          <p className="text-[10px] font-mono mb-4" style={{ color: "oklch(0.35 0.01 240)" }}>
            Ces pages expliquent l'architecture. Elles ne prennent pas de décisions souveraines.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {pedagogical.map((s) => (
              <Link key={s.path} href={s.path}>
                <div
                  className="p-3 rounded cursor-pointer transition-all"
                  style={{
                    background: "oklch(0.10 0.01 240 / 0.5)",
                    border: "1px solid oklch(0.16 0.01 240)",
                  }}
                  onMouseOver={(e) => {
                    (e.currentTarget as HTMLDivElement).style.borderColor = "oklch(0.45 0.05 240 / 0.5)";
                  }}
                  onMouseOut={(e) => {
                    (e.currentTarget as HTMLDivElement).style.borderColor = "oklch(0.16 0.01 240)";
                  }}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-mono text-xs font-bold" style={{ color: "oklch(0.65 0.02 240)" }}>
                      {s.label}
                    </span>
                    <SurfaceStatusBadge status={s.status} compact />
                  </div>
                  <p className="text-[9px] leading-relaxed" style={{ color: "oklch(0.38 0.01 240)" }}>
                    {s.description}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* ── Contrat canonique ───────────────────────────────────────────── */}
        <section>
          <h2 className="font-mono text-xs font-bold tracking-widest mb-4" style={{ color: "oklch(0.45 0.01 240)" }}>
            CONTRAT CANONIQUE — OBJET DE SORTIE SOUVERAIN
          </h2>
          <div
            className="rounded p-4 font-mono text-[10px] leading-relaxed overflow-x-auto"
            style={{
              background: "oklch(0.10 0.01 240)",
              border: "1px solid oklch(0.18 0.01 240)",
              color: "oklch(0.55 0.02 240)",
            }}
          >
            <pre style={{ margin: 0 }}>{`{
  "domain":          "trading | bank | ecom",
  "market_verdict":  "EXECUTE_LONG | AUTHORIZE | PAY | ...",
  "x108_gate":       "ALLOW | HOLD | BLOCK",          // ← souverain
  "reason_code":     "PYTHON_ENGINE | X108_HOLD | ...",
  "violation_code":  "X108_ELAPSED_TOO_SHORT | ...",  // si HOLD/BLOCK
  "severity":        "S0 | S1 | S2 | S3 | S4",
  "decision_id":     "py-xxxxxxxx",
  "trace_id":        "uuid-v4",                       // ← replay Python
  "ticket_required": true,
  "ticket_id":       "uuid-v4",                       // si ALLOW
  "attestation_ref": "sha256:...",                    // merkle_root
  "metrics":         { ... },                         // métriques brutes
  "raw_engine":      { ... },                         // avant gouvernance
  "source":          "python | os4_local_fallback"    // ← OBLIGATOIRE
}`}</pre>
          </div>
        </section>

        {/* ── Login ───────────────────────────────────────────────────────── */}
        {!isAuthenticated && (
          <section className="text-center py-6">
            <a
              href={getLoginUrl()}
              className="inline-flex items-center gap-2 px-6 py-3 rounded font-mono text-sm font-bold transition-all"
              style={{
                background: "oklch(0.13 0.06 145 / 0.4)",
                border: "1px solid oklch(0.72 0.18 145 / 0.5)",
                color: "oklch(0.72 0.18 145)",
              }}
            >
              Accéder à la plateforme →
            </a>
          </section>
        )}
      </div>
    </div>
  );
}
