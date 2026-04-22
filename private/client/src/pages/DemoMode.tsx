import { useState, useEffect, useRef } from "react";
import { Link } from "wouter";

// ─── Demo steps ───────────────────────────────────────────────────────────────

interface DemoStep {
  id: number;
  title: string;
  subtitle: string;
  icon: string;
  status: "pending" | "active" | "done";
  detail: string;
  simpleExplanation: string;
  expertDetail: string;
  duration: number; // ms for auto-advance
}

const DEMO_STEPS_TEMPLATE: Omit<DemoStep, "status">[] = [
  {
    id: 1,
    title: "Agent Decision",
    subtitle: "Agent Alpha proposes an action",
    icon: "🤖",
    detail: "SELL 1.2 BTC — market order",
    simpleExplanation: "Un agent autonome souhaite vendre 1.2 BTC. Le moteur Obsidia intercepte la décision avant toute exécution.",
    expertDetail: "Action: SELL · Asset: BTC · Qty: 1.2 · Type: MARKET · Coherence: 0.21 < threshold 0.30",
    duration: 2000,
  },
  {
    id: 2,
    title: "Temporal Lock",
    subtitle: "X-108 gate activated — waiting 10s",
    icon: "⏱",
    detail: "τ = 10s · Irreversible action detected",
    simpleExplanation: "Le verrou temporel X-108 bloque l'exécution pendant 10 secondes. Aucune action irréversible ne peut s'exécuter sans ce délai de sécurité.",
    expertDetail: "TemporalGate: LOCKED · τ = 10s · elapsed = 0.0s → 10.0s · State: HOLD",
    duration: 3500,
  },
  {
    id: 3,
    title: "Consensus Vote",
    subtitle: "4 nodes voting — PBFT 3/4 required",
    icon: "🗳",
    detail: "Paris ✓ · London ✓ · Frankfurt ✓ · Amsterdam ✓",
    simpleExplanation: "Les 4 serveurs géographiques votent sur la décision. La majorité (3/4) doit être d'accord pour que la décision soit validée.",
    expertDetail: "PBFT Round 1 · Paris: ALLOW (11ms) · London: ALLOW (14ms) · Frankfurt: ALLOW (9ms) · Amsterdam: ALLOW (16ms) · Consensus: 4/4 REACHED",
    duration: 3000,
  },
  {
    id: 4,
    title: "Final Decision",
    subtitle: "Guard X-108 issues verdict",
    icon: "✅",
    detail: "Decision: ALLOW",
    simpleExplanation: "Après le délai de sécurité et le vote unanime des serveurs, le moteur autorise l'action. La décision est ALLOW.",
    expertDetail: "Decision: ALLOW · Coherence: 0.21 · Consensus: 4/4 · Latency: 11ms · Guard: X-108 STD v1.0",
    duration: 2000,
  },
  {
    id: 5,
    title: "Merkle Anchoring",
    subtitle: "Decision cryptographically sealed",
    icon: "⛓",
    detail: "Merkle root generated · RFC 3161 timestamp",
    simpleExplanation: "La décision est scellée cryptographiquement dans un arbre Merkle. Toute modification ultérieure serait détectable. La preuve est horodatée.",
    expertDetail: "Merkle root: b9ac7a04... · SHA-256 · RFC 3161 TSA: FreeTSA · Bitcoin OTS: Block #876,234 · Seal: V18.3.1",
    duration: 2000,
  },
];

// ─── Metrics ──────────────────────────────────────────────────────────────────

interface DemoMetrics {
  decisionsAnalysed: number;
  blockedActions: number;
  avgLatency: number;
  consensusSuccess: number;
}

// ─── Component ────────────────────────────────────────────────────────────────

export default function DemoMode() {
  const [steps, setSteps] = useState<DemoStep[]>(
    DEMO_STEPS_TEMPLATE.map(s => ({ ...s, status: "pending" as const }))
  );
  const [currentStep, setCurrentStep] = useState<number>(-1); // -1 = not started
  const [isRunning, setIsRunning] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [showExpert, setShowExpert] = useState(false);
  const [metrics, setMetrics] = useState<DemoMetrics>({
    decisionsAnalysed: 124,
    blockedActions: 38,
    avgLatency: 11,
    consensusSuccess: 100,
  });
  const [lockProgress, setLockProgress] = useState(0); // 0-100 for temporal lock animation
  const lockIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (lockIntervalRef.current) clearInterval(lockIntervalRef.current);
    };
  }, []);

  const resetDemo = () => {
    if (lockIntervalRef.current) clearInterval(lockIntervalRef.current);
    setSteps(DEMO_STEPS_TEMPLATE.map(s => ({ ...s, status: "pending" as const })));
    setCurrentStep(-1);
    setIsRunning(false);
    setIsComplete(false);
    setLockProgress(0);
    setMetrics({
      decisionsAnalysed: 124,
      blockedActions: 38,
      avgLatency: 11,
      consensusSuccess: 100,
    });
  };

  const startDemo = () => {
    resetDemo();
    setTimeout(() => {
      setCurrentStep(0);
      setIsRunning(true);
      setSteps(prev => prev.map((s, i) => ({ ...s, status: i === 0 ? "active" : "pending" })));
    }, 100);
  };

  const nextStep = () => {
    if (currentStep < 0) {
      startDemo();
      return;
    }
    if (currentStep >= steps.length - 1) {
      // Complete
      setSteps(prev => prev.map(s => ({ ...s, status: "done" })));
      setIsComplete(true);
      setIsRunning(false);
      setMetrics(m => ({
        ...m,
        decisionsAnalysed: m.decisionsAnalysed + 1,
        blockedActions: m.blockedActions,
        avgLatency: 11,
        consensusSuccess: 100,
      }));
      return;
    }

    const next = currentStep + 1;

    // Animate temporal lock progress for step 2
    if (next === 1) {
      setLockProgress(0);
      const start = Date.now();
      const duration = 3000;
      lockIntervalRef.current = setInterval(() => {
        const elapsed = Date.now() - start;
        const pct = Math.min(100, (elapsed / duration) * 100);
        setLockProgress(pct);
        if (pct >= 100 && lockIntervalRef.current) {
          clearInterval(lockIntervalRef.current);
          lockIntervalRef.current = null;
        }
      }, 50);
    }

    setCurrentStep(next);
    setSteps(prev =>
      prev.map((s, i) => ({
        ...s,
        status: i < next ? "done" : i === next ? "active" : "pending",
      }))
    );
  };

  const activeStep = currentStep >= 0 && currentStep < steps.length ? steps[currentStep] : null;

  return (
    <div className="flex flex-col max-w-4xl mx-auto px-4 pb-16" style={{ gap: "40px" }}>

      {/* ─── Header ─────────────────────────────────────────────────────────── */}
      <div className="pt-8">
        <div className="text-[10px] font-mono tracking-[0.3em] uppercase mb-1" style={{ color: "oklch(0.72 0.18 145)" }}>
          Obsidia Labs — OS4
        </div>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="font-mono font-bold text-2xl text-foreground mb-2">
              Demo Mode
            </h1>
            <p className="text-sm" style={{ color: "oklch(0.55 0.01 240)", maxWidth: "520px" }}>
              Simulation pas-à-pas de la chaîne de gouvernance complète du moteur Obsidia X-108.
              Chaque étape montre un composant différent du système.
            </p>
          </div>
          {/* Simple/Expert toggle */}
          <div className="flex items-center gap-1 rounded-lg p-1 flex-shrink-0" style={{ background: "oklch(0.13 0.01 240)", border: "1px solid oklch(0.22 0.01 240)" }}>
            <button
              onClick={() => setShowExpert(false)}
              className="px-3 py-1.5 rounded font-mono text-[10px] font-bold transition-colors"
              style={{
                background: !showExpert ? "oklch(0.72 0.18 145 / 0.20)" : "transparent",
                color: !showExpert ? "oklch(0.72 0.18 145)" : "oklch(0.40 0.01 240)",
              }}
            >
              Simple
            </button>
            <button
              onClick={() => setShowExpert(true)}
              className="px-3 py-1.5 rounded font-mono text-[10px] font-bold transition-colors"
              style={{
                background: showExpert ? "oklch(0.60 0.12 200 / 0.20)" : "transparent",
                color: showExpert ? "oklch(0.60 0.12 200)" : "oklch(0.40 0.01 240)",
              }}
            >
              Expert
            </button>
          </div>
        </div>
      </div>

      {/* ─── Pipeline visual ─────────────────────────────────────────────────── */}
      <div
        className="rounded-lg"
        style={{ padding: "24px 32px", background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}
      >
        <div className="flex items-center justify-between gap-2 flex-wrap">
          {DEMO_STEPS_TEMPLATE.map((step, i) => {
            const s = steps[i];
            const isDone = s.status === "done";
            const isActive = s.status === "active";
            const isPending = s.status === "pending";

            return (
              <div key={step.id} className="flex items-center gap-2">
                <div className="flex flex-col items-center gap-1">
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center text-lg font-mono font-bold"
                    style={{
                      background: isDone
                        ? "oklch(0.60 0.12 200 / 0.20)"
                        : isActive
                          ? "oklch(0.72 0.18 145 / 0.20)"
                          : "oklch(0.14 0.01 240)",
                      border: `2px solid ${isDone ? "oklch(0.60 0.12 200)" : isActive ? "oklch(0.72 0.18 145)" : "oklch(0.22 0.01 240)"}`,
                      boxShadow: isActive ? "0 0 16px oklch(0.72 0.18 145 / 0.4)" : "none",
                    }}
                  >
                    {isDone ? "✓" : step.icon}
                  </div>
                  <span
                    className="font-mono text-[8px] text-center"
                    style={{
                      color: isDone ? "oklch(0.60 0.12 200)" : isActive ? "oklch(0.72 0.18 145)" : "oklch(0.35 0.01 240)",
                      maxWidth: "60px",
                    }}
                  >
                    {step.title}
                  </span>
                </div>
                {i < DEMO_STEPS_TEMPLATE.length - 1 && (
                  <div
                    className="w-8 h-px mt-[-12px]"
                    style={{ background: isDone ? "oklch(0.60 0.12 200)" : "oklch(0.22 0.01 240)" }}
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* ─── Active step detail ──────────────────────────────────────────────── */}
      {!isComplete && (
        <div
          className="rounded-lg min-h-[200px]"
          style={{
            padding: "32px",
            background: currentStep >= 0 ? "oklch(0.10 0.01 240)" : "oklch(0.09 0.01 240)",
            border: `1px solid ${currentStep >= 0 ? "oklch(0.72 0.18 145 / 0.4)" : "oklch(0.18 0.01 240)"}`,
          }}
        >
          {currentStep < 0 ? (
            /* Not started */
            <div className="flex flex-col items-center justify-center h-full gap-4 py-8">
              <div className="text-4xl">🎬</div>
              <p className="font-mono text-sm text-center" style={{ color: "oklch(0.50 0.01 240)", maxWidth: "400px" }}>
                Cliquez sur <strong style={{ color: "oklch(0.72 0.18 145)" }}>Start Demo</strong> pour lancer la simulation de la chaîne de gouvernance Obsidia.
              </p>
              <p className="font-mono text-[10px] text-center" style={{ color: "oklch(0.35 0.01 240)" }}>
                5 étapes · Agent → Temporal Lock → Consensus → Decision → Merkle Anchor
              </p>
            </div>
          ) : activeStep ? (
            /* Active step */
            <div>
              {/* Step header */}
              <div className="flex items-start justify-between gap-4 mb-6">
                <div className="flex items-center gap-4">
                  <div
                    className="w-14 h-14 rounded-full flex items-center justify-center text-2xl flex-shrink-0"
                    style={{ background: "oklch(0.72 0.18 145 / 0.15)", border: "2px solid oklch(0.72 0.18 145 / 0.5)" }}
                  >
                    {activeStep.icon}
                  </div>
                  <div>
                    <div className="font-mono text-[9px] font-bold mb-0.5" style={{ color: "oklch(0.72 0.18 145)" }}>
                      STEP {activeStep.id} / {steps.length}
                    </div>
                    <h2 className="font-mono font-bold text-lg text-foreground">{activeStep.title}</h2>
                    <p className="font-mono text-xs mt-0.5" style={{ color: "oklch(0.50 0.01 240)" }}>{activeStep.subtitle}</p>
                  </div>
                </div>
                <div
                  className="font-mono text-[10px] px-2 py-1 rounded flex-shrink-0"
                  style={{ background: "oklch(0.72 0.18 145 / 0.10)", color: "oklch(0.72 0.18 145)", border: "1px solid oklch(0.72 0.18 145 / 0.3)" }}
                >
                  ● RUNNING
                </div>
              </div>

              {/* Temporal lock progress bar */}
              {activeStep.id === 2 && (
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-mono text-[10px]" style={{ color: "oklch(0.50 0.01 240)" }}>Temporal Lock Progress</span>
                    <span className="font-mono text-[10px] font-bold" style={{ color: "oklch(0.72 0.18 145)" }}>
                      {Math.round(lockProgress * 10 / 100) / 10}s / 10s
                    </span>
                  </div>
                  <div className="w-full h-2 rounded-full" style={{ background: "oklch(0.16 0.01 240)" }}>
                    <div
                      className="h-2 rounded-full"
                      style={{
                        width: `${lockProgress}%`,
                        background: "oklch(0.72 0.18 145)",
                        boxShadow: "0 0 8px oklch(0.72 0.18 145 / 0.6)",
                      }}
                    />
                  </div>
                </div>
              )}

              {/* Consensus nodes */}
              {activeStep.id === 3 && (
                <div className="grid grid-cols-4 gap-3 mb-6">
                  {["Paris", "London", "Frankfurt", "Amsterdam"].map((node, i) => (
                    <div
                      key={node}
                      className="rounded-lg flex flex-col items-center gap-1.5"
                      style={{ padding: "12px 8px", background: "oklch(0.13 0.01 240)", border: "1px solid oklch(0.60 0.12 200 / 0.4)" }}
                    >
                      <div className="w-2 h-2 rounded-full" style={{ background: "oklch(0.60 0.12 200)" }} />
                      <span className="font-mono text-[9px] font-bold text-foreground">{node}</span>
                      <span className="font-mono text-[8px]" style={{ color: "oklch(0.60 0.12 200)" }}>ALLOW</span>
                      <span className="font-mono text-[8px]" style={{ color: "oklch(0.40 0.01 240)" }}>{[11, 14, 9, 16][i]}ms</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Decision badge */}
              {activeStep.id === 4 && (
                <div className="flex items-center justify-center mb-6">
                  <div
                    className="rounded-xl flex flex-col items-center gap-2"
                    style={{ padding: "24px 48px", background: "oklch(0.72 0.18 145 / 0.10)", border: "2px solid oklch(0.72 0.18 145 / 0.5)" }}
                  >
                    <div className="font-mono text-[10px]" style={{ color: "oklch(0.50 0.01 240)" }}>FINAL DECISION</div>
                    <div className="font-mono font-bold text-3xl" style={{ color: "oklch(0.72 0.18 145)" }}>ALLOW</div>
                    <div className="font-mono text-[9px]" style={{ color: "oklch(0.45 0.01 240)" }}>Consensus 4/4 · Latency 11ms</div>
                  </div>
                </div>
              )}

              {/* Merkle anchor */}
              {activeStep.id === 5 && (
                <div
                  className="rounded-lg mb-6"
                  style={{ padding: "16px 20px", background: "oklch(0.13 0.01 240)", border: "1px solid oklch(0.22 0.01 240)" }}
                >
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { label: "Merkle root", value: "b9ac7a04..." },
                      { label: "Algorithm", value: "SHA-256" },
                      { label: "TSA", value: "FreeTSA" },
                      { label: "Bitcoin OTS", value: "Block #876,234" },
                    ].map(item => (
                      <div key={item.label}>
                        <div className="font-mono text-[9px]" style={{ color: "oklch(0.45 0.01 240)" }}>{item.label}</div>
                        <div className="font-mono text-xs font-bold text-foreground">{item.value}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Explanation */}
              <div
                className="rounded-lg"
                style={{ padding: "16px 20px", background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}
              >
                <p className="text-sm" style={{ color: "oklch(0.65 0.01 240)" }}>
                  {showExpert ? activeStep.expertDetail : activeStep.simpleExplanation}
                </p>
              </div>
            </div>
          ) : null}
        </div>
      )}

      {/* ─── Completion screen ───────────────────────────────────────────────── */}
      {isComplete && (
        <div
          className="rounded-lg"
          style={{ padding: "40px 32px", background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.72 0.18 145 / 0.4)", textAlign: "center" }}
        >
          <div className="text-4xl mb-4">🎉</div>
          <h2 className="font-mono font-bold text-xl text-foreground mb-2">Demo Complete</h2>
          <p className="text-sm mb-6" style={{ color: "oklch(0.50 0.01 240)" }}>
            La chaîne de gouvernance complète a été simulée avec succès.
          </p>
          <div className="grid grid-cols-2 gap-4 max-w-sm mx-auto mb-6">
            {[
              { label: "Steps completed", value: "5/5" },
              { label: "Decision", value: "ALLOW" },
              { label: "Consensus", value: "4/4" },
              { label: "Merkle seal", value: "Active" },
            ].map(item => (
              <div key={item.label} className="rounded-lg" style={{ padding: "12px 16px", background: "oklch(0.13 0.01 240)", border: "1px solid oklch(0.22 0.01 240)" }}>
                <div className="font-mono text-[9px]" style={{ color: "oklch(0.45 0.01 240)" }}>{item.label}</div>
                <div className="font-mono font-bold text-sm" style={{ color: "oklch(0.72 0.18 145)" }}>{item.value}</div>
              </div>
            ))}
          </div>
          <div className="flex items-center justify-center gap-3">
            <Link href="/proof-center">
              <span className="font-mono text-xs px-4 py-2 rounded cursor-pointer" style={{ background: "oklch(0.14 0.01 240)", border: "1px solid oklch(0.22 0.01 240)", color: "oklch(0.60 0.12 200)" }}>
                View Proof Center →
              </span>
            </Link>
            <Link href="/control">
              <span className="font-mono text-xs px-4 py-2 rounded cursor-pointer" style={{ background: "oklch(0.14 0.01 240)", border: "1px solid oklch(0.22 0.01 240)", color: "oklch(0.60 0.12 200)" }}>
                Control Tower →
              </span>
            </Link>
          </div>
        </div>
      )}

      {/* ─── Controls ───────────────────────────────────────────────────────── */}
      <div className="flex items-center gap-4">
        {!isComplete ? (
          <button
            onClick={nextStep}
            className="px-6 py-3 rounded-lg font-mono text-sm font-bold"
            style={{
              background: "oklch(0.72 0.18 145 / 0.15)",
              border: "1px solid oklch(0.72 0.18 145 / 0.5)",
              color: "oklch(0.72 0.18 145)",
            }}
          >
            {currentStep < 0 ? "▶ Start Demo" : currentStep >= steps.length - 1 ? "✓ Complete" : `Next Step →  (${currentStep + 2}/${steps.length})`}
          </button>
        ) : (
          <button
            onClick={resetDemo}
            className="px-6 py-3 rounded-lg font-mono text-sm font-bold"
            style={{
              background: "oklch(0.60 0.12 200 / 0.15)",
              border: "1px solid oklch(0.60 0.12 200 / 0.5)",
              color: "oklch(0.60 0.12 200)",
            }}
          >
            ↺ Reset Demo
          </button>
        )}

        {currentStep >= 0 && !isComplete && (
          <button
            onClick={resetDemo}
            className="px-4 py-3 rounded-lg font-mono text-xs"
            style={{
              background: "oklch(0.13 0.01 240)",
              border: "1px solid oklch(0.22 0.01 240)",
              color: "oklch(0.45 0.01 240)",
            }}
          >
            ↺ Reset
          </button>
        )}

        {currentStep >= 0 && (
          <div className="font-mono text-[10px]" style={{ color: "oklch(0.40 0.01 240)" }}>
            Step {Math.max(0, currentStep + 1)} of {steps.length}
          </div>
        )}
      </div>

      {/* ─── Live Metrics ────────────────────────────────────────────────────── */}
      <section>
        <h2 className="font-mono font-bold text-sm uppercase tracking-widest mb-4" style={{ color: "oklch(0.72 0.18 145)" }}>
          Live Metrics
        </h2>
        <div className="grid grid-cols-4 gap-4">
          {[
            { label: "Decisions analysed", value: metrics.decisionsAnalysed.toString(), color: "#60a5fa" },
            { label: "Blocked actions", value: metrics.blockedActions.toString(), color: "#f87171" },
            { label: "Average latency", value: `${metrics.avgLatency}ms`, color: "#4ade80" },
            { label: "Consensus success", value: `${metrics.consensusSuccess}%`, color: "#a78bfa" },
          ].map(item => (
            <div
              key={item.label}
              className="rounded-lg flex flex-col gap-1"
              style={{ padding: "20px 16px", background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}
            >
              <div className="font-mono font-bold text-2xl" style={{ color: item.color }}>{item.value}</div>
              <div className="font-mono text-[9px]" style={{ color: "oklch(0.45 0.01 240)" }}>{item.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ─── Navigation ──────────────────────────────────────────────────────── */}
      <section>
        <h2 className="font-mono font-bold text-sm uppercase tracking-widest mb-4" style={{ color: "oklch(0.72 0.18 145)" }}>
          Explore Further
        </h2>
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: "How It Works", desc: "Architecture pédagogique", href: "/demo", icon: "📖" },
            { label: "Proof Center", desc: "Preuves formelles", href: "/proof-center", icon: "📐" },
            { label: "Control Tower", desc: "Supervision live", href: "/control", icon: "🗼" },
          ].map(item => (
            <Link key={item.label} href={item.href}>
              <div
                className="rounded-lg cursor-pointer"
                style={{ padding: "16px 20px", background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span>{item.icon}</span>
                  <span className="font-mono font-bold text-xs text-foreground">{item.label}</span>
                </div>
                <p className="font-mono text-[10px]" style={{ color: "oklch(0.45 0.01 240)" }}>{item.desc}</p>
              </div>
            </Link>
          ))}
        </div>
      </section>

    </div>
  );
}
