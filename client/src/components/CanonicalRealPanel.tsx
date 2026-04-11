import React, { useState } from "react";

export interface CanonicalEnvelope {
  domain?: string;
  market_verdict?: string;
  x108_gate?: "ALLOW" | "HOLD" | "BLOCK";
  reason_code?: string;
  violation_code?: string | null;
  severity?: "S0" | "S1" | "S2" | "S3" | "S4";
  decision_id?: string;
  trace_id?: string;
  ticket_required?: boolean;
  ticket_id?: string | null;
  attestation_ref?: string | null;
  metrics?: Record<string, unknown>;
  raw_engine?: Record<string, unknown> | null;
}

const GATE_COLOR: Record<string, string> = {
  ALLOW: "oklch(0.72 0.18 145)",
  HOLD:  "oklch(0.78 0.18 80)",
  BLOCK: "oklch(0.65 0.25 25)",
};

const SEV_COLOR: Record<string, string> = {
  S0: "oklch(0.72 0.18 145)",
  S1: "oklch(0.78 0.18 80)",
  S2: "oklch(0.78 0.18 80)",
  S3: "oklch(0.65 0.25 25)",
  S4: "oklch(0.65 0.25 25)",
};

function short(s?: string | null, n = 16) {
  if (!s) return "N/A";
  return s.length > n ? s.slice(0, n) + "…" : s;
}

/** Détermine si la décision vient de Python ou du fallback local */
function detectSource(payload: CanonicalEnvelope): "python" | "os4_local_fallback" {
  if (!payload) return "os4_local_fallback";
  const id = payload.decision_id ?? "";
  const trace = payload.trace_id ?? "";
  // Python trace_id est un UUID v4, decision_id commence par "py-"
  if (id.startsWith("py-") || /^[0-9a-f]{8}-[0-9a-f]{4}-4/.test(trace)) return "python";
  return "os4_local_fallback";
}

const SOURCE_LABEL: Record<string, { icon: string; label: string; color: string }> = {
  python: { icon: "⬡", label: "source: python_backend", color: "oklch(0.72 0.18 145)" },
  os4_local_fallback: { icon: "⚠", label: "source: os4_local_fallback", color: "oklch(0.75 0.18 75)" },
};

export default function CanonicalRealPanel({
  title,
  payload,
  loading,
}: {
  title: string;
  payload?: CanonicalEnvelope | null;
  loading?: boolean;
}) {
  const [showRaw, setShowRaw] = useState(false);

  if (loading) {
    return (
      <div
        className="rounded border border-white/10 p-4 mb-4 text-xs font-mono animate-pulse"
        style={{ background: "oklch(0.14 0.02 240 / 0.6)" }}
      >
        <div className="text-muted-foreground">Chargement backend canonique…</div>
      </div>
    );
  }
  if (!payload) return null;

  const gateColor = GATE_COLOR[payload.x108_gate ?? ""] ?? "oklch(0.65 0.18 220)";
  const sevColor = SEV_COLOR[payload.severity ?? ""] ?? "oklch(0.65 0.18 220)";
  const src = detectSource(payload);
  const srcCfg = SOURCE_LABEL[src];

  const hasMetrics = payload.metrics && Object.keys(payload.metrics).length > 0;
  const hasRawEngine = payload.raw_engine && Object.keys(payload.raw_engine).length > 0;

  return (
    <div
      className="rounded border border-white/10 p-4 mb-4"
      style={{ background: "oklch(0.14 0.02 240 / 0.6)" }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
        <span className="text-xs font-mono font-bold" style={{ color: "oklch(0.65 0.18 220)" }}>
          {title}
        </span>
        <div className="flex items-center gap-2">
          {/* Badge source */}
          <span
            className="inline-flex items-center gap-1 font-mono text-[9px] px-1.5 py-0.5 rounded"
            style={{
              background: src === "python"
                ? "oklch(0.13 0.06 145 / 0.35)"
                : "oklch(0.13 0.06 75 / 0.35)",
              border: `1px solid ${srcCfg.color}55`,
              color: srcCfg.color,
            }}
          >
            {srcCfg.icon} {srcCfg.label}
          </span>
          <span className="text-[9px] font-mono text-muted-foreground uppercase tracking-widest">
            BACKEND CANONIQUE · RÉEL
          </span>
        </div>
      </div>

      {/* Gate + Severity — ligne principale */}
      <div className="flex items-center gap-4 mb-3 flex-wrap">
        <span
          className="text-2xl font-black font-mono tracking-tight"
          style={{ color: gateColor }}
        >
          {payload.x108_gate ?? "—"}
        </span>
        {payload.severity && (
          <span
            className="text-xs font-mono font-bold px-2 py-0.5 rounded"
            style={{ color: sevColor, border: `1px solid ${sevColor}` }}
          >
            {payload.severity}
          </span>
        )}
        {payload.violation_code && (
          <span className="text-[10px] font-mono text-red-400/80">{payload.violation_code}</span>
        )}
      </div>

      {/* Grille des champs canoniques */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 text-xs font-mono mb-3">
        <div>
          <div className="text-muted-foreground text-[10px] mb-0.5">Verdict métier</div>
          <div className="font-bold">{payload.market_verdict ?? "—"}</div>
        </div>
        <div>
          <div className="text-muted-foreground text-[10px] mb-0.5">Reason code</div>
          <div className="font-bold text-amber-400/90">{payload.reason_code ?? "—"}</div>
        </div>
        <div>
          <div className="text-muted-foreground text-[10px] mb-0.5">Decision ID</div>
          <div className="font-bold break-all text-[10px]">{short(payload.decision_id, 20)}</div>
        </div>
        <div>
          <div className="text-muted-foreground text-[10px] mb-0.5">Trace ID</div>
          <div className="font-bold break-all text-[10px]">{short(payload.trace_id, 20)}</div>
        </div>
        <div>
          <div className="text-muted-foreground text-[10px] mb-0.5">Ticket ID</div>
          <div className="font-bold break-all text-[10px]">{short(payload.ticket_id, 16)}</div>
        </div>
        <div>
          <div className="text-muted-foreground text-[10px] mb-0.5">Ticket requis</div>
          <div
            className="font-bold"
            style={{ color: payload.ticket_required ? "oklch(0.72 0.18 145)" : "oklch(0.55 0.05 240)" }}
          >
            {payload.ticket_required ? "OUI" : "NON"}
          </div>
        </div>
        <div className="col-span-2">
          <div className="text-muted-foreground text-[10px] mb-0.5">Attestation ref</div>
          <div className="font-bold break-all text-[10px]">{short(payload.attestation_ref, 32)}</div>
        </div>
      </div>

      {/* Metrics inline */}
      {hasMetrics && (
        <div
          className="rounded p-2 mb-2"
          style={{ background: "oklch(0.11 0.01 240 / 0.5)", border: "1px solid oklch(0.18 0.01 240)" }}
        >
          <div className="text-[9px] font-mono text-muted-foreground mb-1.5 uppercase tracking-widest">
            Métriques moteur
          </div>
          <div className="flex flex-wrap gap-3">
            {Object.entries(payload.metrics!).slice(0, 8).map(([k, v]) => (
              <div key={k} className="flex flex-col">
                <span className="text-[9px] text-muted-foreground font-mono">{k}</span>
                <span className="text-[10px] font-mono font-bold" style={{ color: "oklch(0.75 0.02 240)" }}>
                  {typeof v === "number" ? v.toFixed(3) : String(v)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* raw_engine toggle */}
      {hasRawEngine && (
        <div>
          <button
            onClick={() => setShowRaw((p) => !p)}
            className="text-[9px] font-mono px-2 py-0.5 rounded transition-colors"
            style={{
              background: "oklch(0.11 0.01 240 / 0.5)",
              border: "1px solid oklch(0.22 0.01 240)",
              color: "oklch(0.45 0.01 240)",
            }}
          >
            {showRaw ? "▲ masquer raw_engine" : "▼ raw_engine"}
          </button>
          {showRaw && (
            <pre
              className="mt-2 rounded p-2 text-[9px] font-mono overflow-x-auto"
              style={{
                background: "oklch(0.09 0.01 240)",
                border: "1px solid oklch(0.16 0.01 240)",
                color: "oklch(0.45 0.01 240)",
                maxHeight: "160px",
              }}
            >
              {JSON.stringify(payload.raw_engine, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
