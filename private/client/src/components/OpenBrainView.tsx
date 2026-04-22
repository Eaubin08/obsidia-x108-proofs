import React from "react";

export type BrainDecision = "ALLOW" | "HOLD" | "BLOCK";

export interface BrainData {
  // VOIT — données brutes
  sees: {
    label: string;
    value: string | number;
    unit?: string;
  }[];
  // PENSE — jauges de risque
  thinks: {
    label: string;
    value: number; // 0..1
    color: "green" | "amber" | "red";
    description: string;
  }[];
  // DÉCIDE — résultat final
  decision: BrainDecision;
  decisionLabel: string;
  capitalImpact?: string; // ex: "Capital protégé : +15 000 €"
  explanation?: string;   // explication novice
}

const colorMap = {
  green: { bar: "bg-emerald-400", text: "text-emerald-400", border: "border-emerald-500/30" },
  amber: { bar: "bg-amber-400", text: "text-amber-400", border: "border-amber-500/30" },
  red: { bar: "bg-red-400", text: "text-red-400", border: "border-red-500/30" },
};

const decisionStyle: Record<BrainDecision, { bg: string; text: string; border: string; icon: string }> = {
  ALLOW: { bg: "bg-emerald-500/10", text: "text-emerald-400", border: "border-emerald-500/40", icon: "✓" },
  HOLD: { bg: "bg-amber-500/10", text: "text-amber-400", border: "border-amber-500/40", icon: "⏸" },
  BLOCK: { bg: "bg-red-500/10", text: "text-red-400", border: "border-red-500/40", icon: "✗" },
};

interface OpenBrainViewProps {
  data: BrainData;
  title?: string;
}

export function OpenBrainView({ data, title }: OpenBrainViewProps) {
  const ds = decisionStyle[data.decision];

  return (
    <div className="rounded-lg border border-[#1e2a1e] bg-[#0a0f0a] overflow-hidden">
      {title && (
        <div className="px-4 py-2 border-b border-[#1e2a1e] bg-[#0d140d]">
          <span className="text-xs font-mono text-[#4ade80]/70 uppercase tracking-widest">{title}</span>
        </div>
      )}
      <div className="grid grid-cols-3 divide-x divide-[#1e2a1e]">
        {/* VOIT */}
        <div className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-lg">👁</span>
            <div>
              <div className="text-[10px] font-mono text-[#4ade80]/50 uppercase tracking-widest">Ce que le système</div>
              <div className="text-sm font-bold text-[#4ade80]">VOIT</div>
            </div>
          </div>
          <div className="space-y-2">
            {data.sees.map((item, i) => (
              <div key={i} className="flex justify-between items-baseline gap-2">
                <span className="text-[10px] text-[#6b7280] font-mono truncate">{item.label}</span>
                <span className="text-xs font-mono text-white whitespace-nowrap">
                  {typeof item.value === "number" ? item.value.toLocaleString() : item.value}
                  {item.unit && <span className="text-[#6b7280] ml-0.5">{item.unit}</span>}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* PENSE */}
        <div className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-lg">🧠</span>
            <div>
              <div className="text-[10px] font-mono text-[#4ade80]/50 uppercase tracking-widest">Ce que le système</div>
              <div className="text-sm font-bold text-[#4ade80]">PENSE</div>
            </div>
          </div>
          <div className="space-y-3">
            {data.thinks.map((item, i) => {
              const c = colorMap[item.color];
              return (
                <div key={i}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-[10px] font-mono text-[#9ca3af]">{item.label}</span>
                    <span className={`text-[10px] font-mono font-bold ${c.text}`}>
                      {(item.value * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="h-1.5 bg-[#1a2a1a] rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${c.bar}`}
                      style={{ width: `${item.value * 100}%` }}
                    />
                  </div>
                  <div className="text-[9px] text-[#6b7280] mt-0.5">{item.description}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* DÉCIDE */}
        <div className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-lg">⚡</span>
            <div>
              <div className="text-[10px] font-mono text-[#4ade80]/50 uppercase tracking-widest">Ce que le système</div>
              <div className="text-sm font-bold text-[#4ade80]">DÉCIDE</div>
            </div>
          </div>
          <div className={`rounded-lg border p-3 mb-3 ${ds.bg} ${ds.border}`}>
            <div className="flex items-center gap-2">
              <span className={`text-2xl font-bold ${ds.text}`}>{ds.icon}</span>
              <span className={`text-lg font-bold font-mono ${ds.text}`}>{data.decision}</span>
            </div>
            <div className={`text-xs mt-1 ${ds.text} opacity-80`}>{data.decisionLabel}</div>
          </div>
          {data.capitalImpact && (
            <div className="rounded bg-[#0d1f0d] border border-emerald-900/40 p-2 mb-2">
              <div className="text-[10px] text-[#6b7280] font-mono">IMPACT FINANCIER</div>
              <div className="text-xs font-bold text-emerald-400 mt-0.5">{data.capitalImpact}</div>
            </div>
          )}
          {data.explanation && (
            <div className="rounded bg-[#1a1a0d] border border-amber-900/30 p-2">
              <div className="text-[10px] text-[#6b7280] font-mono mb-1">EXPLICATION</div>
              <div className="text-[10px] text-[#d1d5db] leading-relaxed italic">{data.explanation}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
