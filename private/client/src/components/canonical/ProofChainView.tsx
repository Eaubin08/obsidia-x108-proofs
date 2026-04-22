/**
 * ProofChainView — chaîne de preuve canonique OS4 V2
 * Visualise : Decision ID → Trace ID → Ticket ID → Attestation Ref
 * Règle : jamais mentir sur l'état de la preuve
 */
import React from "react";

export interface ProofChain {
  decision_id: string;
  trace_id?: string;
  ticket_required: boolean;
  ticket_id?: string;
  attestation_ref?: string;
  lean_proof_hash?: string;
  proof_complete: boolean;
  proof_partial: boolean;
}

interface ProofChainViewProps {
  chain: ProofChain;
  variant?: "inline" | "full";
  className?: string;
}

type StepStatus = "complete" | "missing" | "not-required";

interface ChainStep {
  label: string;
  value?: string;
  status: StepStatus;
  icon: string;
}

function buildSteps(chain: ProofChain): ChainStep[] {
  return [
    {
      label: "Decision ID",
      value: chain.decision_id,
      status: chain.decision_id ? "complete" : "missing",
      icon: "⚖️",
    },
    {
      label: "Trace ID",
      value: chain.trace_id,
      status: chain.trace_id ? "complete" : "missing",
      icon: "🔍",
    },
    {
      label: "Ticket",
      value: chain.ticket_id,
      status: !chain.ticket_required ? "not-required" : chain.ticket_id ? "complete" : "missing",
      icon: "🎫",
    },
    {
      label: "Attestation",
      value: chain.attestation_ref,
      status: chain.attestation_ref ? "complete" : "missing",
      icon: "🔐",
    },
  ];
}

const STATUS_CFG = {
  complete:     { color: "oklch(0.72 0.18 145)", dot: "oklch(0.72 0.18 145)", label: "✓" },
  missing:      { color: "oklch(0.65 0.25 25)",  dot: "oklch(0.65 0.25 25)",  label: "✗" },
  "not-required": { color: "oklch(0.40 0.01 240)", dot: "oklch(0.30 0.01 240)", label: "—" },
};

export default function ProofChainView({ chain, variant = "inline", className = "" }: ProofChainViewProps) {
  const steps = buildSteps(chain);
  const overallColor = chain.proof_complete
    ? "oklch(0.72 0.18 145)"
    : chain.proof_partial
    ? "oklch(0.72 0.18 45)"
    : "oklch(0.65 0.25 25)";
  const overallLabel = chain.proof_complete ? "COMPLETE" : chain.proof_partial ? "PARTIAL" : "MISSING";

  if (variant === "inline") {
    return (
      <div className={`flex items-center gap-1.5 flex-wrap ${className}`}>
        <span className="text-[9px] font-mono font-bold" style={{ color: overallColor }}>
          Proof {overallLabel}
        </span>
        {steps.map((step, i) => {
          const cfg = STATUS_CFG[step.status];
          return (
            <React.Fragment key={step.label}>
              <div className="flex items-center gap-0.5">
                <span className="text-[8px] font-mono" style={{ color: cfg.color }}>{cfg.label}</span>
                <span className="text-[8px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>{step.label}</span>
              </div>
              {i < steps.length - 1 && <span className="text-[8px]" style={{ color: "oklch(0.30 0.01 240)" }}>→</span>}
            </React.Fragment>
          );
        })}
      </div>
    );
  }

  // Full variant
  return (
    <div className={`rounded p-3 ${className}`}
      style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-[10px] font-mono font-bold" style={{ color: "oklch(0.65 0.01 240)" }}>
          Proof Chain
        </span>
        <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded"
          style={{ background: `${overallColor}18`, border: `1px solid ${overallColor}40`, color: overallColor }}>
          {overallLabel}
        </span>
      </div>

      {/* Steps */}
      <div className="relative">
        {steps.map((step, i) => {
          const cfg = STATUS_CFG[step.status];
          return (
            <div key={step.label} className="flex items-start gap-3 mb-3">
              {/* Timeline */}
              <div className="flex flex-col items-center">
                <div className="w-4 h-4 rounded-full flex items-center justify-center text-[8px] font-mono font-bold"
                  style={{ background: `${cfg.dot}20`, border: `1.5px solid ${cfg.dot}`, color: cfg.color }}>
                  {cfg.label}
                </div>
                {i < steps.length - 1 && (
                  <div className="w-px h-4 mt-0.5"
                    style={{ background: step.status === "complete" ? "oklch(0.72 0.18 145 / 0.3)" : "oklch(0.20 0.01 240)" }} />
                )}
              </div>
              {/* Content */}
              <div className="flex-1 min-w-0 -mt-0.5">
                <div className="flex items-center gap-1.5">
                  <span className="text-[9px]">{step.icon}</span>
                  <span className="text-[9px] font-mono font-bold" style={{ color: cfg.color }}>{step.label}</span>
                </div>
                {step.value ? (
                  <div className="text-[8px] font-mono mt-0.5 break-all" style={{ color: "oklch(0.55 0.01 240)" }}>
                    {step.value.length > 40 ? step.value.slice(0, 40) + "…" : step.value}
                  </div>
                ) : (
                  <div className="text-[8px] font-mono mt-0.5" style={{ color: "oklch(0.35 0.01 240)" }}>
                    {step.status === "not-required" ? "Non requis" : "Manquant"}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Lean proof hash */}
      {chain.lean_proof_hash && (
        <div className="mt-2 pt-2 text-[8px] font-mono" style={{ borderTop: "1px solid oklch(0.16 0.01 240)", color: "oklch(0.45 0.01 240)" }}>
          <span style={{ color: "oklch(0.40 0.01 240)" }}>lean4 </span>
          {chain.lean_proof_hash.slice(0, 32)}…
        </div>
      )}
    </div>
  );
}
