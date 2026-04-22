/**
 * RunBreadcrumb.tsx — OS4
 * Fil de navigation opératoire : domain → scénario → seed → verdict X-108 → trace
 * Affiché dans Simuler (après run), Decision (sur chaque ticket), Preuves (sur chaque preuve)
 *
 * Props :
 *   domain      — "trading" | "bank" | "ecom" | string
 *   scenarioId  — identifiant du scénario (ex: "flash_crash")
 *   seed        — seed du run (number | string)
 *   verdict     — "ALLOW" | "HOLD" | "BLOCK" | null
 *   traceId     — hash court de la trace (ex: "a1b2c3d4")
 *   ticketId    — id du ticket DB (pour le deep-link Preuves)
 *   onSimuler   — callback pour relancer dans Simuler (optionnel)
 *   onPreuves   — callback pour ouvrir dans Preuves (optionnel)
 *   onDecision  — callback pour ouvrir dans Decision (optionnel)
 *   className   — classes CSS supplémentaires
 */
import React from "react";
import { useLocation } from "wouter";

// ─── Types ─────────────────────────────────────────────────────────────────────
export interface RunBreadcrumbProps {
  domain?: string | null;
  scenarioId?: string | null;
  seed?: number | string | null;
  verdict?: "ALLOW" | "HOLD" | "BLOCK" | null;
  traceId?: string | null;
  ticketId?: string | number | null;
  onSimuler?: () => void;
  onPreuves?: () => void;
  onDecision?: () => void;
  className?: string;
}

// ─── Couleurs par verdict ──────────────────────────────────────────────────────
const VERDICT_COLOR: Record<string, string> = {
  ALLOW: "oklch(0.72 0.18 145)",   // vert
  HOLD:  "oklch(0.80 0.18 75)",    // ambre
  BLOCK: "oklch(0.65 0.22 25)",    // rouge
};

const DOMAIN_LABEL: Record<string, string> = {
  trading: "TRADING",
  bank:    "BANK",
  ecom:    "ECOM",
};

// ─── Composant ─────────────────────────────────────────────────────────────────
export default function RunBreadcrumb({
  domain,
  scenarioId,
  seed,
  verdict,
  traceId,
  ticketId,
  onSimuler,
  onPreuves,
  onDecision,
  className = "",
}: RunBreadcrumbProps) {
  const [, navigate] = useLocation();

  const verdictColor = verdict ? VERDICT_COLOR[verdict] ?? "oklch(0.55 0.01 240)" : "oklch(0.35 0.01 240)";
  const domainLabel  = domain ? (DOMAIN_LABEL[domain] ?? domain.toUpperCase()) : "—";
  const scenarioLabel = scenarioId ? scenarioId.replace(/_/g, " ") : "—";
  const seedLabel     = seed != null ? `seed:${seed}` : "—";
  const traceLabel    = traceId ? `${String(traceId).slice(0, 10)}…` : "—";

  // Deep-links
  const handleSimuler = () => {
    if (onSimuler) { onSimuler(); return; }
    if (domain && scenarioId && seed != null) {
      navigate(`/simuler?domain=${domain}&scenarioId=${scenarioId}&seed=${seed}&rerun=1`);
    } else {
      navigate("/simuler");
    }
  };

  const handlePreuves = () => {
    if (onPreuves) { onPreuves(); return; }
    navigate("/preuves");
  };

  const handleDecision = () => {
    if (onDecision) { onDecision(); return; }
    navigate("/decision");
  };

  // Séparateur
  const Sep = () => (
    <span className="font-mono text-[10px]" style={{ color: "oklch(0.28 0.01 240)" }}>›</span>
  );

  return (
    <div
      className={`flex items-center flex-wrap gap-1.5 px-3 py-2 rounded font-mono text-[10px] ${className}`}
      style={{
        background: "oklch(0.09 0.01 240)",
        border: "1px solid oklch(0.16 0.01 240)",
      }}
    >
      {/* Domaine */}
      <span className="font-bold" style={{ color: "oklch(0.55 0.01 240)" }}>RUN</span>
      <Sep />

      <span className="px-1.5 py-0.5 rounded text-[9px] font-bold"
        style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.65 0.18 240)" }}>
        {domainLabel}
      </span>
      <Sep />

      {/* Scénario */}
      <span style={{ color: "oklch(0.60 0.01 240)" }}>{scenarioLabel}</span>
      <Sep />

      {/* Seed */}
      <span style={{ color: "oklch(0.45 0.01 240)" }}>{seedLabel}</span>
      <Sep />

      {/* Verdict */}
      {verdict ? (
        <span className="px-1.5 py-0.5 rounded text-[9px] font-bold"
          style={{ background: `${verdictColor}15`, color: verdictColor, border: `1px solid ${verdictColor}40` }}>
          {verdict}
        </span>
      ) : (
        <span style={{ color: "oklch(0.35 0.01 240)" }}>—</span>
      )}
      <Sep />

      {/* Trace */}
      <span className="font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>{traceLabel}</span>

      {/* Actions */}
      <div className="flex items-center gap-1 ml-auto">
        {(domain && scenarioId && seed != null) && (
          <button
            onClick={handleSimuler}
            className="px-2 py-0.5 rounded text-[9px] font-bold transition-all"
            style={{ background: "oklch(0.72 0.18 145 / 0.10)", color: "oklch(0.72 0.18 145)", border: "1px solid oklch(0.72 0.18 145 / 0.30)" }}
            title="Relancer ce run dans Simuler"
          >
            ↺ Relancer
          </button>
        )}
        {ticketId && (
          <button
            onClick={handlePreuves}
            className="px-2 py-0.5 rounded text-[9px] font-bold transition-all"
            style={{ background: "oklch(0.60 0.12 200 / 0.10)", color: "oklch(0.60 0.12 200)", border: "1px solid oklch(0.60 0.12 200 / 0.30)" }}
            title="Voir la preuve dans Preuves"
          >
            ⊞ Preuve
          </button>
        )}
        {traceId && (
          <button
            onClick={handleDecision}
            className="px-2 py-0.5 rounded text-[9px] font-bold transition-all"
            style={{ background: "oklch(0.65 0.18 240 / 0.10)", color: "oklch(0.65 0.18 240)", border: "1px solid oklch(0.65 0.18 240 / 0.30)" }}
            title="Voir la décision dans Decision"
          >
            ⊞ Décision
          </button>
        )}
      </div>
    </div>
  );
}
