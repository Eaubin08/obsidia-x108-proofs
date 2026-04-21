/**
 * CanonicalAgentPanel — Visualisation du pipeline canonique OS4
 * Affiche le résultat complet d'un run CanonicalEnvelope :
 * - Gate X-108 (ALLOW/HOLD/BLOCK) + sévérité
 * - Confidence, contradictions, unknowns, risk_flags
 * - Evidence refs (agents ayant voté)
 * - Métriques domaine (buy/sell/hold scores, etc.)
 * - Source (canonical_framework / canonical_fallback)
 */
import React, { useState } from "react";
import { trpc } from "@/lib/trpc";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

// ─── Types alignés avec CanonicalEnvelope backend ─────────────────────────────
interface CanonicalEnvelope {
  domain: "trading" | "bank" | "ecom";
  market_verdict: string;
  confidence: number;
  contradictions: string[];
  unknowns: string[];
  risk_flags: string[];
  x108_gate: "ALLOW" | "HOLD" | "BLOCK";
  reason_code: string;
  severity: "S0" | "S1" | "S2" | "S3" | "S4";
  decision_id: string;
  trace_id: string;
  ticket_required: boolean;
  ticket_id: string | null;
  attestation_ref: string | null;
  source: string;
  evidence_refs: string[];
  metrics: Record<string, unknown>;
  raw_engine: Record<string, unknown>;
  python_available: boolean;
  elapsed_ms: number;
}

interface Props {
  domain: "trading" | "bank" | "ecom";
  scenarioId?: string;
  seed?: number;
  /** Si fourni, affiche directement sans déclencher un run */
  envelope?: CanonicalEnvelope;
  className?: string;
}

// ─── Couleurs par gate ─────────────────────────────────────────────────────────
const GATE_COLORS = {
  ALLOW: { bg: "oklch(0.22 0.08 145)", border: "oklch(0.55 0.18 145)", text: "oklch(0.85 0.18 145)", label: "ALLOW" },
  HOLD:  { bg: "oklch(0.22 0.08 60)",  border: "oklch(0.65 0.18 60)",  text: "oklch(0.85 0.18 60)",  label: "HOLD" },
  BLOCK: { bg: "oklch(0.22 0.08 25)",  border: "oklch(0.65 0.22 25)",  text: "oklch(0.85 0.22 25)",  label: "BLOCK" },
};

const SEVERITY_COLORS: Record<string, string> = {
  S0: "oklch(0.72 0.18 145)",
  S1: "oklch(0.72 0.18 200)",
  S2: "oklch(0.72 0.18 60)",
  S3: "oklch(0.72 0.18 45)",
  S4: "oklch(0.65 0.25 25)",
};

// ─── Composant principal ───────────────────────────────────────────────────────
export function CanonicalAgentPanel({ domain, scenarioId, seed, envelope: externalEnvelope, className = "" }: Props) {
  const [envelope, setEnvelope] = useState<CanonicalEnvelope | null>(externalEnvelope ?? null);
  const [showRaw, setShowRaw] = useState(false);

  const runMutation = trpc.engine.canonicalRun.useMutation({
    onSuccess: (data) => setEnvelope(data as CanonicalEnvelope),
  });

  const handleRun = () => {
    // Toujours générer un seed aléatoire pour que chaque run soit unique
    const dynamicSeed = seed ?? Math.floor(Math.random() * 0x7fffffff);
    runMutation.mutate({ domain, scenarioId, seed: dynamicSeed });
  };

  const gate = envelope ? GATE_COLORS[envelope.x108_gate] ?? GATE_COLORS.HOLD : null;

  // Filtrer les evidence_refs méta pour les afficher séparément
  const metaRefs = envelope?.evidence_refs.filter(r => r.startsWith("meta:")) ?? [];
  const agentRefs = envelope?.evidence_refs.filter(r => !r.startsWith("meta:")) ?? [];

  return (
    <div
      className={`rounded-lg border font-mono text-xs ${className}`}
      style={{ borderColor: "oklch(0.3 0.05 250)", background: "oklch(0.12 0.03 250)" }}
    >
      {/* ── Header ── */}
      <div className="flex items-center justify-between px-3 py-2 border-b" style={{ borderColor: "oklch(0.25 0.05 250)" }}>
        <div className="flex items-center gap-2">
          <span style={{ color: "oklch(0.65 0.15 250)" }}>Pipeline Canonique</span>
          <span style={{ color: "oklch(0.5 0.05 250)" }}>·</span>
          <span style={{ color: "oklch(0.75 0.15 200)", textTransform: "uppercase" }}>{domain}</span>
          {scenarioId && (
            <>
              <span style={{ color: "oklch(0.5 0.05 250)" }}>·</span>
              <span style={{ color: "oklch(0.65 0.1 200)" }}>{scenarioId}</span>
            </>
          )}
        </div>
        <Button
          size="sm"
          variant="outline"
          onClick={handleRun}
          disabled={runMutation.isPending}
          className="h-6 px-2 text-[10px]"
          style={{ borderColor: "oklch(0.35 0.1 250)", color: "oklch(0.75 0.1 250)" }}
        >
          {runMutation.isPending ? "Exécution…" : envelope ? "Relancer" : "Exécuter"}
        </Button>
      </div>

      {/* ── Résultat ── */}
      {!envelope && !runMutation.isPending && (
        <div className="px-3 py-4 text-center" style={{ color: "oklch(0.5 0.05 250)" }}>
          Cliquez sur "Exécuter" pour lancer le pipeline canonique
        </div>
      )}

      {runMutation.isPending && (
        <div className="px-3 py-4 text-center" style={{ color: "oklch(0.65 0.1 200)" }}>
          Exécution du pipeline ({domain})…
        </div>
      )}

      {envelope && gate && (
        <div className="p-3 flex flex-col gap-3">
          {/* ── Gate + Verdict ── */}
          <div className="flex items-start gap-3">
            <div
              className="flex-shrink-0 rounded px-3 py-2 text-center min-w-[80px]"
              style={{ background: gate.bg, border: `1px solid ${gate.border}` }}
            >
              <div className="text-lg font-bold" style={{ color: gate.text }}>{gate.label}</div>
              <div className="text-[9px] mt-0.5" style={{ color: "oklch(0.6 0.05 250)" }}>X-108 Gate</div>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span style={{ color: "oklch(0.8 0.1 250)" }}>{envelope.market_verdict}</span>
                <span
                  className="px-1.5 py-0.5 rounded text-[9px]"
                  style={{ background: "oklch(0.18 0.05 250)", color: SEVERITY_COLORS[envelope.severity] ?? "oklch(0.7 0.1 250)", border: `1px solid ${SEVERITY_COLORS[envelope.severity] ?? "oklch(0.4 0.1 250)"}` }}
                >
                  {envelope.severity}
                </span>
                {!envelope.python_available && (
                  <span className="px-1.5 py-0.5 rounded text-[9px]" style={{ background: "oklch(0.2 0.08 45)", color: "oklch(0.75 0.18 45)", border: "1px solid oklch(0.4 0.15 45)" }}>
                    FALLBACK
                  </span>
                )}
              </div>
              <div className="mt-1" style={{ color: "oklch(0.55 0.05 250)" }}>{envelope.reason_code}</div>
              <div className="mt-1 flex items-center gap-2">
                <span style={{ color: "oklch(0.5 0.05 250)" }}>Confiance :</span>
                <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: "oklch(0.2 0.05 250)" }}>
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${Math.round(envelope.confidence * 100)}%`,
                      background: envelope.confidence > 0.7 ? "oklch(0.65 0.18 145)" : envelope.confidence > 0.45 ? "oklch(0.65 0.18 60)" : "oklch(0.65 0.22 25)",
                    }}
                  />
                </div>
                <span style={{ color: "oklch(0.7 0.1 250)" }}>{Math.round(envelope.confidence * 100)}%</span>
              </div>
            </div>
          </div>

          {/* ── Contradictions / Unknowns / Risk Flags ── */}
          {(envelope.contradictions.length > 0 || envelope.unknowns.length > 0 || envelope.risk_flags.length > 0) && (
            <div className="flex flex-col gap-1.5">
              {envelope.contradictions.length > 0 && (
                <div>
                  <span style={{ color: "oklch(0.55 0.05 250)" }}>Contradictions : </span>
                  <span style={{ color: "oklch(0.75 0.2 25)" }}>{envelope.contradictions.join(", ")}</span>
                </div>
              )}
              {envelope.unknowns.length > 0 && (
                <div>
                  <span style={{ color: "oklch(0.55 0.05 250)" }}>Inconnus : </span>
                  <span style={{ color: "oklch(0.75 0.15 60)" }}>{envelope.unknowns.join(", ")}</span>
                </div>
              )}
              {envelope.risk_flags.length > 0 && (
                <div>
                  <span style={{ color: "oklch(0.55 0.05 250)" }}>Risk flags : </span>
                  <span style={{ color: "oklch(0.75 0.18 45)" }}>{envelope.risk_flags.join(", ")}</span>
                </div>
              )}
            </div>
          )}

          {/* ── Métriques domaine ── */}
          {Object.keys(envelope.metrics).length > 0 && (
            <div className="flex flex-wrap gap-2">
              {Object.entries(envelope.metrics).map(([k, v]) => (
                typeof v === "number" ? (
                  <div key={k} className="px-2 py-1 rounded" style={{ background: "oklch(0.16 0.04 250)" }}>
                    <span style={{ color: "oklch(0.5 0.05 250)" }}>{k}: </span>
                    <span style={{ color: "oklch(0.75 0.1 200)" }}>{typeof v === "number" ? v.toFixed(3) : String(v)}</span>
                  </div>
                ) : null
              ))}
            </div>
          )}

          {/* ── Agents ayant voté ── */}
          {agentRefs.length > 0 && (
            <div>
              <div style={{ color: "oklch(0.5 0.05 250)" }} className="mb-1">
                {agentRefs.length} agents domaine · {metaRefs.length} méta-agents
              </div>
              <div className="flex flex-wrap gap-1">
                {metaRefs.map(ref => (
                  <span key={ref} className="px-1.5 py-0.5 rounded text-[9px]" style={{ background: "oklch(0.18 0.06 280)", color: "oklch(0.65 0.12 280)", border: "1px solid oklch(0.28 0.06 280)" }}>
                    {ref.replace("meta:", "")}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* ── Trace / Attestation ── */}
          <div className="flex flex-col gap-0.5" style={{ color: "oklch(0.45 0.05 250)" }}>
            <div>trace_id: <span style={{ color: "oklch(0.6 0.08 200)" }}>{envelope.trace_id.slice(0, 16)}…</span></div>
            {envelope.attestation_ref && (
              <div>attestation: <span style={{ color: "oklch(0.6 0.08 200)" }}>{envelope.attestation_ref.slice(0, 16)}…</span></div>
            )}
            <div>source: <span style={{ color: envelope.python_available ? "oklch(0.65 0.18 145)" : "oklch(0.65 0.15 60)" }}>{envelope.source}</span></div>
            <div>elapsed: <span style={{ color: "oklch(0.6 0.08 200)" }}>{envelope.elapsed_ms}ms</span></div>
          </div>

          {/* ── Raw JSON toggle ── */}
          <button
            onClick={() => setShowRaw(v => !v)}
            className="text-left"
            style={{ color: "oklch(0.45 0.05 250)" }}
          >
            {showRaw ? "▾ Masquer JSON brut" : "▸ Voir JSON brut"}
          </button>
          {showRaw && (
            <pre
              className="text-[9px] overflow-auto max-h-48 p-2 rounded"
              style={{ background: "oklch(0.1 0.02 250)", color: "oklch(0.65 0.08 200)" }}
            >
              {JSON.stringify(envelope, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}

export default CanonicalAgentPanel;
