/**
 * DecisionEnvelopeCard — carte universelle CanonicalEnvelope OS4 V2
 * Affiche les 4 niveaux : Résultat → Pourquoi → Contexte → Preuve
 * Utilisée dans Mission, Live, Future, Past
 */
import React, { useState } from "react";
import { Link } from "wouter";

export interface CanonicalEnvelope {
  domain: "trading" | "bank" | "ecom";
  market_verdict: string;
  confidence: number;
  contradictions: number;
  unknowns: number;
  risk_flags: string[];
  x108_gate: "ALLOW" | "HOLD" | "BLOCK";
  reason_code: string;
  severity: "S1" | "S2" | "S3" | "S4";
  decision_id: string;
  trace_id?: string;
  ticket_required: boolean;
  ticket_id?: string;
  attestation_ref?: string;
  source: string;
  metrics?: Record<string, number>;
  raw_engine?: unknown;
  timestamp?: number;
}

interface DecisionEnvelopeCardProps {
  envelope: CanonicalEnvelope;
  /** Mode d'affichage : compact (feed), standard (détail), expanded (full) */
  variant?: "compact" | "standard" | "expanded";
  /** Lien vers la page Past pour ce run */
  pastLink?: string;
  /** Callback sélection */
  onSelect?: (env: CanonicalEnvelope) => void;
  selected?: boolean;
  className?: string;
}

// ─── Couleurs ─────────────────────────────────────────────────────────────────

const GATE_CFG = {
  ALLOW: { color: "oklch(0.72 0.18 145)", bg: "oklch(0.72 0.18 145 / 0.10)", label: "ALLOW" },
  HOLD:  { color: "oklch(0.72 0.18 45)",  bg: "oklch(0.72 0.18 45 / 0.10)",  label: "HOLD"  },
  BLOCK: { color: "oklch(0.65 0.25 25)",  bg: "oklch(0.65 0.25 25 / 0.10)",  label: "BLOCK" },
};

const SEV_CFG = {
  S1: { color: "oklch(0.72 0.18 145)", label: "S1" },
  S2: { color: "oklch(0.72 0.18 45)",  label: "S2" },
  S3: { color: "oklch(0.65 0.25 25)",  label: "S3" },
  S4: { color: "oklch(0.60 0.30 15)",  label: "S4" },
};

const DOMAIN_CFG = {
  trading: { icon: "📈", label: "Trading", accent: "oklch(0.72 0.18 145)" },
  bank:    { icon: "🏦", label: "Bank",    accent: "oklch(0.65 0.18 240)" },
  ecom:    { icon: "🛒", label: "Ecom",    accent: "oklch(0.72 0.18 45)"  },
};

// ─── Composant ────────────────────────────────────────────────────────────────

export default function DecisionEnvelopeCard({
  envelope: env,
  variant = "standard",
  pastLink,
  onSelect,
  selected = false,
  className = "",
}: DecisionEnvelopeCardProps) {
  const [showProof, setShowProof] = useState(false);
  const gate = GATE_CFG[env.x108_gate];
  const sev = SEV_CFG[env.severity];
  const dom = DOMAIN_CFG[env.domain];
  const confPct = Math.round(env.confidence * 100);
  const proofComplete = !!env.trace_id && (!env.ticket_required || !!env.ticket_id) && !!env.attestation_ref;

  // ── Compact ──────────────────────────────────────────────────────────────────
  if (variant === "compact") {
    return (
      <button
        onClick={() => onSelect?.(env)}
        className={`w-full text-left px-3 py-2 rounded transition-all ${className}`}
        style={{
          background: selected ? "oklch(0.14 0.02 145 / 0.4)" : "oklch(0.12 0.01 240)",
          border: `1px solid ${selected ? "oklch(0.72 0.18 145 / 0.5)" : "oklch(0.18 0.01 240)"}`,
        }}
      >
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-1.5 min-w-0">
            <span className="text-[10px]">{dom.icon}</span>
            <span className="text-[9px] font-mono font-bold truncate" style={{ color: dom.accent }}>{dom.label}</span>
            <span className="text-[9px] font-mono truncate" style={{ color: "oklch(0.65 0.01 240)" }}>{env.market_verdict}</span>
          </div>
          <div className="flex items-center gap-1.5 shrink-0">
            <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded"
              style={{ background: gate.bg, color: gate.color }}>{gate.label}</span>
            <span className="text-[9px] font-mono" style={{ color: sev.color }}>{sev.label}</span>
            <span className="text-[9px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>{confPct}%</span>
          </div>
        </div>
        {env.contradictions > 0 && (
          <div className="mt-1 text-[8px] font-mono" style={{ color: "oklch(0.72 0.18 45)" }}>
            ⚠ {env.contradictions} contradiction{env.contradictions > 1 ? "s" : ""}
          </div>
        )}
      </button>
    );
  }

  // ── Standard / Expanded ───────────────────────────────────────────────────────
  return (
    <div
      className={`rounded overflow-hidden ${className}`}
      style={{
        background: "oklch(0.11 0.01 240)",
        border: `1px solid ${selected ? "oklch(0.72 0.18 145 / 0.5)" : "oklch(0.18 0.01 240)"}`,
      }}
    >
      {/* ── Niveau 1 : Résultat final ──────────────────────────────────────── */}
      <div className="px-4 py-3" style={{ borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-2">
            <span className="text-base">{dom.icon}</span>
            <div>
              <div className="text-[10px] font-mono font-bold" style={{ color: dom.accent }}>{dom.label}</div>
              <div className="text-sm font-mono font-bold" style={{ color: "oklch(0.88 0.01 240)" }}>{env.market_verdict}</div>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-[11px] font-mono font-bold px-2 py-1 rounded"
              style={{ background: gate.bg, border: `1px solid ${gate.color}40`, color: gate.color }}>
              X-108 {gate.label}
            </span>
            <span className="text-[10px] font-mono font-bold" style={{ color: sev.color }}>{sev.label}</span>
            <span className="text-[10px] font-mono" style={{ color: "oklch(0.55 0.01 240)" }}>
              {confPct}% conf
            </span>
          </div>
        </div>
      </div>

      {/* ── Niveau 2 : Pourquoi ────────────────────────────────────────────── */}
      <div className="px-4 py-2" style={{ borderBottom: "1px solid oklch(0.14 0.01 240)" }}>
        <div className="flex flex-wrap gap-3 text-[9px] font-mono">
          <div>
            <span style={{ color: "oklch(0.45 0.01 240)" }}>reason </span>
            <span style={{ color: "oklch(0.72 0.01 240)" }}>{env.reason_code}</span>
          </div>
          {env.contradictions > 0 && (
            <div>
              <span style={{ color: "oklch(0.45 0.01 240)" }}>contradictions </span>
              <span style={{ color: "oklch(0.72 0.18 45)" }}>{env.contradictions}</span>
            </div>
          )}
          {env.unknowns > 0 && (
            <div>
              <span style={{ color: "oklch(0.45 0.01 240)" }}>unknowns </span>
              <span style={{ color: "oklch(0.65 0.18 240)" }}>{env.unknowns}</span>
            </div>
          )}
          {env.risk_flags.length > 0 && (
            <div className="flex gap-1 flex-wrap">
              {env.risk_flags.slice(0, 3).map(f => (
                <span key={f} className="px-1 py-0.5 rounded" style={{ background: "oklch(0.65 0.25 25 / 0.15)", color: "oklch(0.65 0.25 25)" }}>{f}</span>
              ))}
              {env.risk_flags.length > 3 && <span style={{ color: "oklch(0.45 0.01 240)" }}>+{env.risk_flags.length - 3}</span>}
            </div>
          )}
        </div>
      </div>

      {/* ── Niveau 3 : Contexte ────────────────────────────────────────────── */}
      <div className="px-4 py-2" style={{ borderBottom: "1px solid oklch(0.14 0.01 240)" }}>
        <div className="flex flex-wrap gap-3 text-[9px] font-mono">
          <div>
            <span style={{ color: "oklch(0.45 0.01 240)" }}>source </span>
            <span style={{ color: "oklch(0.60 0.01 240)" }}>{env.source}</span>
          </div>
          {env.timestamp && (
            <div>
              <span style={{ color: "oklch(0.45 0.01 240)" }}>at </span>
              <span style={{ color: "oklch(0.55 0.01 240)" }}>{new Date(env.timestamp).toLocaleTimeString()}</span>
            </div>
          )}
          {env.metrics && Object.entries(env.metrics).slice(0, 3).map(([k, v]) => (
            <div key={k}>
              <span style={{ color: "oklch(0.45 0.01 240)" }}>{k} </span>
              <span style={{ color: "oklch(0.65 0.01 240)" }}>{typeof v === "number" ? v.toFixed(3) : v}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Niveau 4 : Preuve ──────────────────────────────────────────────── */}
      <div className="px-4 py-2">
        <button
          onClick={() => setShowProof(v => !v)}
          className="flex items-center gap-1.5 text-[9px] font-mono w-full text-left"
          style={{ color: proofComplete ? "oklch(0.72 0.18 145)" : "oklch(0.55 0.01 240)" }}
        >
          <span>{proofComplete ? "✓" : "⚠"}</span>
          <span>Proof {proofComplete ? "COMPLETE" : "PARTIAL"}</span>
          <span className="ml-auto">{showProof ? "▲" : "▼"}</span>
        </button>
        {showProof && (
          <div className="mt-2 grid grid-cols-2 gap-1 text-[8px] font-mono">
            {[
              { label: "decision_id", value: env.decision_id, short: true },
              { label: "trace_id",    value: env.trace_id,    short: true },
              { label: "ticket_id",   value: env.ticket_id,   short: false },
              { label: "attestation", value: env.attestation_ref, short: false },
            ].map(({ label, value, short }) => (
              <div key={label}>
                <span style={{ color: "oklch(0.40 0.01 240)" }}>{label} </span>
                <span style={{ color: value ? "oklch(0.65 0.01 240)" : "oklch(0.35 0.01 240)" }}>
                  {value ? (short ? value.slice(0, 12) + "…" : value) : "—"}
                </span>
              </div>
            ))}
          </div>
        )}
        {/* ─── Phrase d'interprétation (spec : titre métier + phrase + statut + action) ──────────────────────────── */}
        {(variant === "standard" || variant === "expanded") && (() => {
          const envStatus = env.x108_gate === "ALLOW" && proofComplete ? "normal"
            : env.x108_gate === "BLOCK" || env.severity === "S4" ? "critical"
            : "watch";
          const envStatusColor = envStatus === "normal" ? "oklch(0.72 0.18 145)" : envStatus === "watch" ? "oklch(0.72 0.18 45)" : "oklch(0.65 0.25 25)";
          const envStatusLabel = envStatus === "normal" ? "Décision validée" : envStatus === "watch" ? "En attente de validation" : "Décision bloquée";
          const envPhrase = env.x108_gate === "ALLOW"
            ? `Décision ${env.market_verdict} autorisée à ${confPct}% de confiance${proofComplete ? ", preuve complète" : ", preuve partielle"}.`
            : env.x108_gate === "HOLD"
            ? `Décision ${env.market_verdict} suspendue (${env.severity}) — validation opérateur requise.`
            : `Décision ${env.market_verdict} bloquée (${env.severity}) — ${env.risk_flags?.[0] ?? env.reason_code}.`;
          const envAction = env.x108_gate === "ALLOW" && proofComplete ? "Aucune action requise"
            : env.x108_gate === "HOLD" ? "Valider ou rejeter dans Control"
            : "Investiguer dans Past ou Future";
          return (
            <div className="mt-3 rounded p-2" style={{ background: `${envStatusColor}0a`, border: `1px solid ${envStatusColor}33` }}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-[8px] font-mono font-bold" style={{ color: envStatusColor }}>{envStatusLabel}</span>
                <span className="text-[7px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>{env.severity} — {confPct}%</span>
              </div>
              <div className="text-[8px] font-mono" style={{ color: "oklch(0.55 0.01 240)" }}>{envPhrase}</div>
              <div className="mt-1 text-[7px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>→ {envAction}</div>
            </div>
          );
        })()}

        {/* Actions */}
        {variant === "expanded" && (
          <div className="mt-3 flex flex-wrap gap-2">
            {pastLink && (
              <Link href={pastLink}>
                <button className="px-2 py-1 rounded text-[9px] font-mono"
                  style={{ background: "oklch(0.14 0.01 240)", border: "1px solid oklch(0.22 0.01 240)", color: "oklch(0.65 0.01 240)" }}>
                  Open in Past
                </button>
              </Link>
            )}
            <button className="px-2 py-1 rounded text-[9px] font-mono"
              style={{ background: "oklch(0.14 0.01 240)", border: "1px solid oklch(0.22 0.01 240)", color: "oklch(0.65 0.01 240)" }}>
              Open proof chain
            </button>
            <button className="px-2 py-1 rounded text-[9px] font-mono"
              style={{ background: "oklch(0.14 0.01 240)", border: "1px solid oklch(0.22 0.01 240)", color: "oklch(0.65 0.01 240)" }}>
              Replay this setup
            </button>
            <button className="px-2 py-1 rounded text-[9px] font-mono"
              style={{ background: "oklch(0.14 0.01 240)", border: "1px solid oklch(0.22 0.01 240)", color: "oklch(0.65 0.01 240)" }}>
              Export run
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
