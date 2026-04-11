import React, { useState } from "react";

export interface MoltbookEntry {
  id: string;
  timestamp: number;
  vertical: "TRADING" | "BANK" | "ECOM";
  decision: "ALLOW" | "HOLD" | "BLOCK";
  intentHash: string;
  merkleRoot: string;
  tau: number;
  elapsed: number;
  coherence: number;
  capitalImpact?: number; // positif = sauvé, négatif = perdu
  x108Fee?: number; // frais en $X108
  payload: Record<string, unknown>;
}

const verticalIcon: Record<string, string> = { TRADING: "📈", BANK: "🏦", ECOM: "🛒" };
const decisionStyle: Record<string, { text: string; bg: string; border: string }> = {
  ALLOW: { text: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/30" },
  HOLD: { text: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/30" },
  BLOCK: { text: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/30" },
};

interface MoltbookFeedProps {
  entries: MoltbookEntry[];
  maxVisible?: number;
}

export function MoltbookFeed({ entries, maxVisible = 8 }: MoltbookFeedProps) {
  const [expanded, setExpanded] = useState<string | null>(null);
  const visible = entries.slice(0, maxVisible);

  const totalCapitalSaved = entries
    .filter(e => e.capitalImpact && e.capitalImpact > 0)
    .reduce((sum, e) => sum + (e.capitalImpact || 0), 0);

  const totalX108Fees = entries
    .filter(e => e.x108Fee)
    .reduce((sum, e) => sum + (e.x108Fee || 0), 0);

  return (
    <div className="rounded-lg border border-[#1e2a1e] bg-[#0a0f0a] overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-[#1e2a1e] bg-[#0d140d] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-[#4ade80]/70 uppercase tracking-widest">🌐 MOLTBOOK</span>
          <span className="text-[9px] text-[#6b7280] font-mono">— Internet des Agents X-108</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-[9px] text-[#6b7280] font-mono">Capital protégé</div>
            <div className="text-xs font-bold text-emerald-400 font-mono">
              +{totalCapitalSaved.toLocaleString("fr-FR")} €
            </div>
          </div>
          <div className="text-right">
            <div className="text-[9px] text-[#6b7280] font-mono">Frais $X108</div>
            <div className="text-xs font-bold text-[#4ade80] font-mono">
              {totalX108Fees.toFixed(4)} $X108
            </div>
          </div>
        </div>
      </div>

      {/* Feed */}
      <div className="divide-y divide-[#1e2a1e]">
        {visible.length === 0 ? (
          <div className="p-6 text-center text-[#4b5563] text-xs font-mono">
            Aucune décision publiée — Lancez une simulation
          </div>
        ) : (
          visible.map((entry) => {
            const ds = decisionStyle[entry.decision];
            const isExpanded = expanded === entry.id;
            return (
              <div key={entry.id} className="p-3 hover:bg-[#0d140d] transition-colors">
                <div className="flex items-start gap-3">
                  {/* Vertical badge */}
                  <div className="flex-shrink-0 text-base">{verticalIcon[entry.vertical]}</div>

                  {/* Main content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded border ${ds.text} ${ds.bg} ${ds.border}`}>
                        {entry.decision}
                      </span>
                      <span className="text-[10px] text-[#6b7280] font-mono">{entry.vertical}</span>
                      <span className="text-[9px] text-[#4b5563] font-mono ml-auto">
                        {new Date(entry.timestamp).toLocaleTimeString("fr-FR")}
                      </span>
                    </div>

                    {/* Hash */}
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[9px] text-[#4b5563] font-mono">intent:</span>
                      <code className="text-[9px] text-[#4ade80]/60 font-mono truncate">{entry.intentHash}</code>
                    </div>

                    {/* Metrics row */}
                    <div className="flex items-center gap-3 flex-wrap">
                      <span className="text-[9px] font-mono text-[#9ca3af]">
                        τ={entry.tau}s elapsed={entry.elapsed.toFixed(1)}s
                      </span>
                      <span className="text-[9px] font-mono text-[#9ca3af]">
                        coherence={entry.coherence.toFixed(2)}
                      </span>
                      {entry.capitalImpact && entry.capitalImpact > 0 && (
                        <span className="text-[9px] font-mono text-emerald-400">
                          💰 +{entry.capitalImpact.toLocaleString("fr-FR")} €
                        </span>
                      )}
                      {entry.x108Fee && (
                        <span className="text-[9px] font-mono text-[#4ade80]">
                          fee={entry.x108Fee.toFixed(6)} $X108
                        </span>
                      )}
                    </div>

                    {/* Expandable payload */}
                    <button
                      onClick={() => setExpanded(isExpanded ? null : entry.id)}
                      className="mt-1 text-[9px] text-[#4b5563] hover:text-[#6b7280] font-mono transition-colors"
                    >
                      {isExpanded ? "▲ masquer payload" : "▼ voir payload JSON"}
                    </button>

                    {isExpanded && (
                      <div className="mt-2 rounded bg-[#050a05] border border-[#1e2a1e] p-2 overflow-x-auto">
                        <pre className="text-[9px] text-[#4ade80]/70 font-mono whitespace-pre-wrap">
                          {JSON.stringify({
                            intent_id: entry.id,
                            standard: "X-108 STD 1.0",
                            vertical: entry.vertical,
                            decision: entry.decision,
                            tau: entry.tau,
                            elapsed: entry.elapsed,
                            coherence: entry.coherence,
                            intent_hash: entry.intentHash,
                            merkle_root: entry.merkleRoot,
                            payload: entry.payload,
                          }, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {entries.length > maxVisible && (
        <div className="px-4 py-2 border-t border-[#1e2a1e] text-center">
          <span className="text-[9px] text-[#4b5563] font-mono">
            +{entries.length - maxVisible} décisions supplémentaires dans l'audit trail
          </span>
        </div>
      )}
    </div>
  );
}
