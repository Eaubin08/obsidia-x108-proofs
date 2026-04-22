import React from "react";

export type IWOPhase = "idle" | "in" | "wait" | "out";

interface InWaitOutProps {
  phase: IWOPhase;
  inLabel?: string;
  waitLabel?: string;
  outLabel?: string;
  inDescription?: string;
  waitDescription?: string;
  outDescription?: string;
}

const phaseConfig = {
  idle: { active: -1 },
  in: { active: 0 },
  wait: { active: 1 },
  out: { active: 2 },
};

export function InWaitOut({
  phase,
  inLabel = "IN",
  waitLabel = "WAIT",
  outLabel = "OUT",
  inDescription = "L'événement déclencheur arrive",
  waitDescription = "Le système analyse et protège",
  outDescription = "La décision tombe",
}: InWaitOutProps) {
  const active = phaseConfig[phase].active;

  const steps = [
    {
      id: 0,
      key: "in",
      icon: "📥",
      label: inLabel,
      description: inDescription,
      color: active === 0 ? "text-blue-400 border-blue-500/50 bg-blue-500/10" : active > 0 ? "text-blue-400/50 border-blue-500/20 bg-blue-500/5" : "text-[#4b5563] border-[#1e2a1e] bg-[#0a0f0a]",
      dot: active === 0 ? "bg-blue-400" : active > 0 ? "bg-blue-400/50" : "bg-[#2a3a2a]",
    },
    {
      id: 1,
      key: "wait",
      icon: "⏸",
      label: waitLabel,
      description: waitDescription,
      color: active === 1 ? "text-amber-400 border-amber-500/50 bg-amber-500/10 shadow-[0_0_15px_rgba(251,191,36,0.1)]" : active > 1 ? "text-amber-400/50 border-amber-500/20 bg-amber-500/5" : "text-[#4b5563] border-[#1e2a1e] bg-[#0a0f0a]",
      dot: active === 1 ? "bg-amber-400" : active > 1 ? "bg-amber-400/50" : "bg-[#2a3a2a]",
    },
    {
      id: 2,
      key: "out",
      icon: "📤",
      label: outLabel,
      description: outDescription,
      color: active === 2 ? "text-emerald-400 border-emerald-500/50 bg-emerald-500/10" : "text-[#4b5563] border-[#1e2a1e] bg-[#0a0f0a]",
      dot: active === 2 ? "bg-emerald-400" : "bg-[#2a3a2a]",
    },
  ];

  return (
    <div className="flex items-center gap-0">
      {steps.map((step, i) => (
        <React.Fragment key={step.key}>
          <div className={`flex-1 rounded-lg border p-3 transition-all duration-500 ${step.color}`}>
            <div className="flex items-center gap-2 mb-1">
              <div className={`w-2 h-2 rounded-full ${step.dot}`} />
              <span className="text-lg">{step.icon}</span>
              <span className="text-sm font-bold font-mono">{step.label}</span>
            </div>
            <div className="text-[10px] opacity-70 leading-relaxed">{step.description}</div>
          </div>
          {i < steps.length - 1 && (
            <div className={`flex-shrink-0 px-1 transition-all duration-500 ${active > i ? "text-[#4ade80]" : "text-[#2a3a2a]"}`}>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M4 10h12M12 6l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
}
