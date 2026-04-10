/**
 * EngineBlock.tsx
 * Bloc pédagogique WORLD → AGENT → ENGINE → GUARD X-108 → PROOF
 * Réutilisable sur TradingWorld, BankWorld, EcomWorld.
 * Branché sur engine.decision (moteur réel du repo).
 */

import { useState, useEffect } from "react";
import { trpc } from "@/lib/trpc";

// ─── Types ────────────────────────────────────────────────────────────────────

interface EngineBlockProps {
  domain: "trading" | "bank" | "ecom";
  amount?: number;
  irreversible?: boolean;
  asset?: string;
  side?: "BUY" | "SELL" | "HOLD";
  coherence?: number;
  volatility?: number;
  timeElapsed?: number;
  tau?: number;
  label?: string; // e.g. "ACHETER BTC 0.1"
  onDecision?: (decision: string, ticket: any) => void;
}

// ─── Step labels ──────────────────────────────────────────────────────────────

const STEPS = [
  { id: "world",  label: "WORLD",      icon: "🌍", desc: "Signal de marché entrant" },
  { id: "agent",  label: "AGENT",      icon: "🤖", desc: "Intention formulée" },
  { id: "engine", label: "ENGINE",     icon: "⚙️",  desc: "Analyse contextuelle" },
  { id: "guard",  label: "GUARD X-108",icon: "🛡️",  desc: "Vérification formelle" },
  { id: "proof",  label: "PROOF",      icon: "🔐", desc: "Trace cryptographique" },
];

// ─── Decision badge ───────────────────────────────────────────────────────────

function DecisionBadge({ decision }: { decision: string }) {
  const map: Record<string, { bg: string; text: string; label: string }> = {
    BLOCK:   { bg: "bg-red-900/60",    text: "text-red-300",    label: "⛔ BLOCK" },
    HOLD:    { bg: "bg-amber-900/60",  text: "text-amber-300",  label: "⏸ HOLD" },
    ALLOW:   { bg: "bg-emerald-900/60",text: "text-emerald-300",label: "✅ ALLOW" },
    EXECUTE: { bg: "bg-emerald-900/60",text: "text-emerald-300",label: "✅ EXECUTE" },
  };
  const style = map[decision] ?? map["ALLOW"];
  return (
    <span className={`px-3 py-1 rounded font-mono text-sm font-bold ${style.bg} ${style.text}`}>
      {style.label}
    </span>
  );
}

// ─── Gate badge ───────────────────────────────────────────────────────────────

function GateBadge({ label, status }: { label: string; status: string }) {
  const color =
    status === "PASS" ? "text-emerald-400" :
    status === "HOLD" ? "text-amber-400" :
    "text-red-400";
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="text-zinc-400">{label}</span>
      <span className={`font-mono font-bold ${color}`}>{status}</span>
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

export function EngineBlock({
  domain,
  amount = 1000,
  irreversible = true,
  asset,
  side,
  coherence,
  volatility,
  timeElapsed,
  tau = 10,
  label,
  onDecision,
}: EngineBlockProps) {
  const [activeStep, setActiveStep] = useState(-1);
  const [ticket, setTicket] = useState<any>(null);
  const [running, setRunning] = useState(false);
  const [holdTimer, setHoldTimer] = useState(0);

  const decisionMutation = trpc.engine.decision.useMutation({
    onSuccess: (data) => {
      setTicket(data);
      setActiveStep(4); // PROOF step
      setRunning(false);
      onDecision?.(data.decision, data);
    },
    onError: () => {
      setRunning(false);
    },
  });

  // Animate pipeline steps
  useEffect(() => {
    if (!running) return;
    let step = 0;
    const interval = setInterval(() => {
      setActiveStep(step);
      step++;
      if (step >= STEPS.length - 1) clearInterval(interval);
    }, 400);
    return () => clearInterval(interval);
  }, [running]);

  // HOLD countdown
  useEffect(() => {
    if (!ticket || ticket.decision !== "HOLD") return;
    const remaining = ticket.guard_evaluation?.temporalLock?.holdRemaining ?? 0;
    setHoldTimer(remaining);
    if (remaining <= 0) return;
    const interval = setInterval(() => {
      setHoldTimer((t) => {
        if (t <= 1) { clearInterval(interval); return 0; }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [ticket]);

  const handleEvaluate = () => {
    setRunning(true);
    setActiveStep(0);
    setTicket(null);
    decisionMutation.mutate({
      domain,
      amount,
      irreversible,
      asset,
      side,
      coherence,
      volatility,
      timeElapsed,
      tau,
    });
  };

  return (
    <div className="border border-zinc-700/50 rounded-lg bg-zinc-900/60 p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-zinc-200 uppercase tracking-wider">
            Pipeline Gouvernance X-108
          </h3>
          {label && (
            <p className="text-xs text-zinc-400 mt-0.5">Action : <span className="text-amber-400 font-mono">{label}</span></p>
          )}
        </div>
        <button
          onClick={handleEvaluate}
          disabled={running}
          className="px-4 py-1.5 text-xs font-bold rounded bg-amber-600 hover:bg-amber-500 text-black disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {running ? "Analyse..." : "▶ Évaluer"}
        </button>
      </div>

      {/* Pipeline steps */}
      <div className="flex items-center gap-1 overflow-x-auto pb-1">
        {STEPS.map((step, i) => {
          const isActive = activeStep === i;
          const isDone = activeStep > i;
          const isPending = activeStep < i;
          return (
            <div key={step.id} className="flex items-center gap-1 flex-shrink-0">
              <div
                className={`flex flex-col items-center gap-1 px-3 py-2 rounded transition-all duration-300 ${
                  isActive
                    ? "bg-amber-900/60 border border-amber-500/60 scale-105"
                    : isDone
                    ? "bg-emerald-900/30 border border-emerald-700/40"
                    : "bg-zinc-800/40 border border-zinc-700/30 opacity-50"
                }`}
              >
                <span className="text-lg">{step.icon}</span>
                <span className={`text-xs font-bold ${isActive ? "text-amber-300" : isDone ? "text-emerald-400" : "text-zinc-500"}`}>
                  {step.label}
                </span>
                <span className="text-[10px] text-zinc-500 text-center max-w-[70px]">{step.desc}</span>
              </div>
              {i < STEPS.length - 1 && (
                <div className={`text-lg transition-colors ${isDone ? "text-emerald-500" : "text-zinc-600"}`}>→</div>
              )}
            </div>
          );
        })}
      </div>

      {/* Result */}
      {ticket && (
        <div className="border border-zinc-700/40 rounded bg-zinc-800/40 p-3 space-y-3">
          {/* Decision */}
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <div className="flex items-center gap-3">
                <span className="text-xs text-zinc-400">Décision finale :</span>
                <DecisionBadge decision={ticket.decision} />
              </div>
              <p className="text-xs text-zinc-400 font-mono">{ticket.reasons?.[0]}</p>
            </div>
            {ticket.decision === "HOLD" && holdTimer > 0 && (
              <div className="text-center">
                <div className="text-2xl font-mono font-bold text-amber-400">{holdTimer}s</div>
                <div className="text-[10px] text-zinc-500">HOLD restant</div>
              </div>
            )}
          </div>

          {/* Guard gates */}
          <div className="grid grid-cols-3 gap-2 border-t border-zinc-700/30 pt-2">
            <GateBadge label="Integrity Gate" status={ticket.guard_evaluation?.integrityGate?.status ?? "?"} />
            <GateBadge label="Temporal Lock" status={ticket.guard_evaluation?.temporalLock?.status ?? "?"} />
            <GateBadge label="Risk Killswitch" status={ticket.guard_evaluation?.riskKillswitch?.status ?? "?"} />
          </div>

          {/* Coherence */}
          <div className="grid grid-cols-2 gap-3 border-t border-zinc-700/30 pt-2">
            <div>
              <div className="text-[10px] text-zinc-500 mb-1">Cohérence avant/après</div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-zinc-300">{(ticket.coherence_before * 100).toFixed(1)}%</span>
                <span className="text-zinc-600">→</span>
                <span className={`text-xs font-mono font-bold ${ticket.coherence_after >= ticket.coherence_before ? "text-emerald-400" : "text-red-400"}`}>
                  {(ticket.coherence_after * 100).toFixed(1)}%
                </span>
              </div>
            </div>
            <div>
              <div className="text-[10px] text-zinc-500 mb-1">τ / Elapsed</div>
              <div className="text-xs font-mono text-zinc-300">{ticket.tau}s / {ticket.hold_elapsed?.toFixed(1)}s</div>
            </div>
          </div>

          {/* Proof hash */}
          <div className="border-t border-zinc-700/30 pt-2">
            <div className="text-[10px] text-zinc-500 mb-1">Hash chain (SHA-256)</div>
            <div className="font-mono text-[10px] text-emerald-400/80 break-all">
              {ticket.proof?.hash_chain_id?.slice(0, 48)}…
            </div>
            <div className="flex gap-3 mt-1">
              <span className="text-[10px] text-zinc-500">
                Lean4 <span className={ticket.proof?.lean_status === "PASS" ? "text-emerald-400" : "text-red-400"}>{ticket.proof?.lean_status}</span>
              </span>
              <span className="text-[10px] text-zinc-500">
                TLA+ <span className={ticket.proof?.tla_status === "PASS" ? "text-emerald-400" : "text-red-400"}>{ticket.proof?.tla_status}</span>
              </span>
              <span className="text-[10px] text-zinc-500">
                ProofKit <span className={ticket.proof?.proofkit_overall === "PASS" ? "text-emerald-400" : "text-amber-400"}>{ticket.proof?.proofkit_overall}</span>
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
