import React, { useState, useEffect, useRef } from "react";

// ─── Types ────────────────────────────────────────────────────────────────────
interface ThresholdConfig {
  holdTau: number;          // τ en secondes (défaut: 10)
  blockScore: number;       // Score X-108 > seuil → BLOCK
  holdScore: number;        // Score X-108 > seuil → HOLD
  maxVol: number;           // Vol max avant BLOCK
  maxDrawdown: number;      // Drawdown max avant BLOCK
  fraudThreshold: number;   // Taux fraude max avant BLOCK
  minLiquidity: number;     // Liquidité min avant HOLD
}

interface LiveDecision {
  id: string;
  timestamp: number;
  vertical: "TRADING" | "BANK" | "ECOM";
  decision: "ALLOW" | "HOLD" | "BLOCK";
  score: number;
  reason: string;
  capitalImpact: number;
}

interface TokenomicsData {
  totalFees: number;
  stakersShare: number;
  treasuryShare: number;
  buybackShare: number;
  circulatingSupply: number;
  burnedTokens: number;
  stakingAPY: number;
}

// ─── Seeded RNG ───────────────────────────────────────────────────────────────
function seededRng(seed: number) {
  let s = seed;
  return () => { s = (s * 1664525 + 1013904223) & 0xffffffff; return (s >>> 0) / 0xffffffff; };
}

function generateDecision(seed: number, thresholds: ThresholdConfig): LiveDecision {
  const rng = seededRng(seed);
  const verticals: ("TRADING" | "BANK" | "ECOM")[] = ["TRADING", "BANK", "ECOM"];
  const vertical = verticals[Math.floor(rng() * 3)];
  const score = rng();
  const decision: "ALLOW" | "HOLD" | "BLOCK" = score > thresholds.blockScore ? "BLOCK" : score > thresholds.holdScore ? "HOLD" : "ALLOW";
  const reasons = {
    ALLOW: ["Constance temporelle vérifiée", "Profil de risque nominal", "Liquidité suffisante"],
    HOLD: ["Volatilité anormale détectée", "Délai d'exécution suspect", "Vérification en cours"],
    BLOCK: ["Flash Crash imminent", "Fraude détectée", "Violation de constance X-108"],
  };
  const reasonList = reasons[decision];
  const capitalImpact = decision === "BLOCK" ? rng() * 10000 : decision === "HOLD" ? rng() * 500 : 0;
  return {
    id: `X108-${seed.toString(16).toUpperCase().padStart(6, "0")}`,
    timestamp: Date.now() - Math.floor(rng() * 60000),
    vertical,
    decision,
    score,
    reason: reasonList[Math.floor(rng() * reasonList.length)],
    capitalImpact,
  };
}

// ─── Components ───────────────────────────────────────────────────────────────
function DecisionRow({ d }: { d: LiveDecision }) {
  const colors = { ALLOW: "#4ade80", HOLD: "#f59e0b", BLOCK: "#ef4444" };
  const icons = { ALLOW: "✓", HOLD: "⏱", BLOCK: "✕" };
  const color = colors[d.decision];
  const elapsed = Math.floor((Date.now() - d.timestamp) / 1000);
  return (
    <div className="flex items-center gap-2 py-1 px-2 rounded text-[9px] font-mono border-b border-border/30 last:border-0">
      <span className="w-5 h-5 rounded flex items-center justify-center font-bold text-[10px]" style={{ background: `${color}20`, color }}>{icons[d.decision]}</span>
      <span className="text-muted-foreground w-8">{d.vertical.slice(0, 3)}</span>
      <span className="text-foreground flex-1">{d.reason}</span>
      <span className="font-mono" style={{ color }}>{d.score.toFixed(3)}</span>
      {d.capitalImpact > 0 && <span className="text-positive">+{d.capitalImpact.toFixed(0)} €</span>}
      <span className="text-muted-foreground">{elapsed}s</span>
    </div>
  );
}

function ThresholdSlider({ label, value, min, max, step, onChange, description, unit = "" }: {
  label: string; value: number; min: number; max: number; step: number;
  onChange: (v: number) => void; description: string; unit?: string;
}) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-[9px] font-mono">
        <span className="text-muted-foreground">{label}</span>
        <span className="text-foreground font-bold">{value}{unit}</span>
      </div>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-1 rounded-full appearance-none cursor-pointer"
        style={{ accentColor: "oklch(0.72 0.18 145)" }} />
      <div className="text-[8px] text-muted-foreground">{description}</div>
    </div>
  );
}

function DonutChart({ data }: { data: { label: string; value: number; color: string }[] }) {
  const total = data.reduce((a, b) => a + b.value, 0);
  let cumAngle = -Math.PI / 2;
  const cx = 60, cy = 60, r = 45, innerR = 28;
  const paths = data.map((d) => {
    const angle = (d.value / total) * 2 * Math.PI;
    const x1 = cx + r * Math.cos(cumAngle);
    const y1 = cy + r * Math.sin(cumAngle);
    cumAngle += angle;
    const x2 = cx + r * Math.cos(cumAngle);
    const y2 = cy + r * Math.sin(cumAngle);
    const xi1 = cx + innerR * Math.cos(cumAngle - angle);
    const yi1 = cy + innerR * Math.sin(cumAngle - angle);
    const xi2 = cx + innerR * Math.cos(cumAngle);
    const yi2 = cy + innerR * Math.sin(cumAngle);
    const large = angle > Math.PI ? 1 : 0;
    return { path: `M ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2} L ${xi2} ${yi2} A ${innerR} ${innerR} 0 ${large} 0 ${xi1} ${yi1} Z`, color: d.color, label: d.label, value: d.value };
  });
  return (
    <svg width="120" height="120" viewBox="0 0 120 120">
      {paths.map((p, i) => <path key={i} d={p.path} fill={p.color} opacity={0.85} />)}
      <text x="60" y="55" textAnchor="middle" fill="#9ca3af" fontSize="8" fontFamily="monospace">$X108</text>
      <text x="60" y="67" textAnchor="middle" fill="#d1d5db" fontSize="9" fontFamily="monospace" fontWeight="bold">0.1%</text>
    </svg>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────
export default function GovernanceX108() {
  const [thresholds, setThresholds] = useState<ThresholdConfig>({
    holdTau: 10, blockScore: 0.75, holdScore: 0.45,
    maxVol: 0.5, maxDrawdown: 0.15, fraudThreshold: 0.05, minLiquidity: 0.2,
  });
  const [decisions, setDecisions] = useState<LiveDecision[]>([]);
  const [autoRun, setAutoRun] = useState(false);
  const [seedCounter, setSeedCounter] = useState(1000);
  const [stats, setStats] = useState({ allow: 0, hold: 0, block: 0, totalCapital: 0 });
  const [tokenomics] = useState<TokenomicsData>({
    totalFees: 2847.3, stakersShare: 1423.65, treasuryShare: 854.19,
    buybackShare: 569.46, circulatingSupply: 21000000, burnedTokens: 142000, stakingAPY: 12.4,
  });
  const autoRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const addDecision = (seed: number) => {
    const d = generateDecision(seed, thresholds);
    setDecisions((prev) => [d, ...prev].slice(0, 20));
    setStats((s) => ({
      allow: s.allow + (d.decision === "ALLOW" ? 1 : 0),
      hold: s.hold + (d.decision === "HOLD" ? 1 : 0),
      block: s.block + (d.decision === "BLOCK" ? 1 : 0),
      totalCapital: s.totalCapital + d.capitalImpact,
    }));
    setSeedCounter((c) => c + 1);
  };

  useEffect(() => {
    if (autoRun) {
      autoRef.current = setInterval(() => {
        setSeedCounter((c) => { addDecision(c); return c + 1; });
      }, 2000);
    } else {
      if (autoRef.current) clearInterval(autoRef.current);
    }
    return () => { if (autoRef.current) clearInterval(autoRef.current); };
  }, [autoRun, thresholds]);

  const total = stats.allow + stats.hold + stats.block;
  const blockRate = total > 0 ? (stats.block / total * 100).toFixed(1) : "0.0";
  const holdRate = total > 0 ? (stats.hold / total * 100).toFixed(1) : "0.0";

  const donutData = [
    { label: "Stakers 50%", value: 50, color: "#4ade80" },
    { label: "Treasury 30%", value: 30, color: "#60a5fa" },
    { label: "Buyback 20%", value: 20, color: "#a78bfa" },
  ];

  return (
    <div className="flex flex-col gap-3 overflow-y-auto" style={{ maxHeight: "calc(100vh - 80px)" }}>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold font-mono" style={{ color: "oklch(0.80 0.15 60)" }}>Dashboard Gouvernance $X108</h2>
          <p className="text-muted-foreground text-xs mt-0.5">Seuils configurables · Simulation en direct · Tokenomics</p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => addDecision(seedCounter)}
            className="px-3 py-1.5 rounded font-mono text-xs border border-border text-muted-foreground hover:text-foreground transition-all">
            ▶ 1 Décision
          </button>
          <button onClick={() => setAutoRun((a) => !a)}
            className="px-3 py-1.5 rounded font-mono text-xs font-bold transition-all"
            style={{ background: autoRun ? "#ef4444" : "oklch(0.80 0.15 60)", color: "#0a0f0a" }}>
            {autoRun ? "⏹ STOP AUTO" : "▶ AUTO-RUN"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-3">
        {/* Left: Thresholds */}
        <div className="col-span-3 panel p-3 flex flex-col gap-3">
          <div className="font-mono text-[10px] text-muted-foreground uppercase tracking-widest">⚙️ Seuils Guard X-108</div>
          <div className="space-y-3">
            <ThresholdSlider label="τ HOLD (secondes)" value={thresholds.holdTau} min={1} max={30} step={1}
              onChange={(v) => setThresholds((t) => ({ ...t, holdTau: v }))}
              description="Durée minimale de réflexion avant exécution" unit="s" />
            <ThresholdSlider label="Score → BLOCK" value={thresholds.blockScore} min={0.5} max={0.99} step={0.01}
              onChange={(v) => setThresholds((t) => ({ ...t, blockScore: v }))}
              description="Score X-108 au-dessus duquel l'ordre est bloqué" />
            <ThresholdSlider label="Score → HOLD" value={thresholds.holdScore} min={0.1} max={0.7} step={0.01}
              onChange={(v) => setThresholds((t) => ({ ...t, holdScore: v }))}
              description="Score X-108 au-dessus duquel l'ordre est suspendu" />
            <ThresholdSlider label="Vol max → BLOCK" value={thresholds.maxVol} min={0.1} max={1.0} step={0.01}
              onChange={(v) => setThresholds((t) => ({ ...t, maxVol: v }))}
              description="Volatilité annualisée déclenchant un BLOCK" />
            <ThresholdSlider label="Drawdown max" value={thresholds.maxDrawdown} min={0.05} max={0.5} step={0.01}
              onChange={(v) => setThresholds((t) => ({ ...t, maxDrawdown: v }))}
              description="Drawdown maximum avant intervention" />
            <ThresholdSlider label="Taux fraude max" value={thresholds.fraudThreshold} min={0.01} max={0.2} step={0.01}
              onChange={(v) => setThresholds((t) => ({ ...t, fraudThreshold: v }))}
              description="Taux de fraude déclenchant un BLOCK bancaire" />
            <ThresholdSlider label="Liquidité min" value={thresholds.minLiquidity} min={0.05} max={0.5} step={0.01}
              onChange={(v) => setThresholds((t) => ({ ...t, minLiquidity: v }))}
              description="Liquidité minimale du carnet d'ordres" />
          </div>
          <div className="mt-2 p-2 rounded text-[9px] font-mono" style={{ background: "#f59e0b08", border: "1px solid #f59e0b25" }}>
            <div className="text-amber-400 font-bold mb-1">⚠ Impact des seuils</div>
            <div className="text-muted-foreground">Score BLOCK = {thresholds.blockScore} → ~{((1 - thresholds.blockScore) * 100).toFixed(0)}% des ordres bloqués</div>
            <div className="text-muted-foreground">τ = {thresholds.holdTau}s → Délai de réflexion obligatoire</div>
          </div>
        </div>

        {/* Center: Live Feed + Stats */}
        <div className="col-span-6 flex flex-col gap-3">
          {/* Stats */}
          <div className="grid grid-cols-4 gap-2">
            {[
              { label: "ALLOW", value: stats.allow, color: "#4ade80", pct: total > 0 ? (stats.allow / total * 100).toFixed(0) : "0" },
              { label: "HOLD", value: stats.hold, color: "#f59e0b", pct: holdRate },
              { label: "BLOCK", value: stats.block, color: "#ef4444", pct: blockRate },
              { label: "Capital Sauvé", value: `${stats.totalCapital.toFixed(0)} €`, color: "#4ade80", pct: null },
            ].map((s) => (
              <div key={s.label} className="panel p-2 text-center">
                <div className="text-[9px] text-muted-foreground font-mono mb-1">{s.label}</div>
                <div className="font-mono font-bold text-sm" style={{ color: s.color }}>{s.value}</div>
                {s.pct !== null && <div className="text-[8px] text-muted-foreground">{s.pct}%</div>}
              </div>
            ))}
          </div>

          {/* Distribution bar */}
          {total > 0 && (
            <div className="panel p-3">
              <div className="font-mono text-[10px] text-muted-foreground uppercase tracking-widest mb-2">Distribution des Décisions</div>
              <div className="h-4 rounded-full overflow-hidden flex">
                <div className="h-full bg-green-400/70 transition-all" style={{ width: `${stats.allow / total * 100}%` }} />
                <div className="h-full bg-amber-400/70 transition-all" style={{ width: `${stats.hold / total * 100}%` }} />
                <div className="h-full bg-red-400/70 transition-all" style={{ width: `${stats.block / total * 100}%` }} />
              </div>
              <div className="flex justify-between mt-1 text-[8px] font-mono text-muted-foreground">
                <span className="text-green-400">ALLOW {(stats.allow / total * 100).toFixed(0)}%</span>
                <span className="text-amber-400">HOLD {holdRate}%</span>
                <span className="text-red-400">BLOCK {blockRate}%</span>
              </div>
            </div>
          )}

          {/* Live Decision Feed */}
          <div className="panel p-3 flex-1">
            <div className="flex items-center justify-between mb-2">
              <div className="font-mono text-[10px] text-muted-foreground uppercase tracking-widest">
                🔴 Flux de Décisions en Direct
                {autoRun && <span className="ml-2 text-positive animate-pulse">● AUTO</span>}
              </div>
              <span className="text-[9px] font-mono text-muted-foreground">{decisions.length} décisions</span>
            </div>
            <div className="space-y-0">
              {decisions.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground text-xs font-mono">
                  Cliquez sur "▶ 1 Décision" ou "▶ AUTO-RUN" pour voir le flux
                </div>
              ) : (
                decisions.map((d) => <DecisionRow key={d.id} d={d} />)
              )}
            </div>
          </div>

          {/* X-108 Formal Pipeline */}
          <div className="panel p-3 mb-1">
            <div className="font-mono text-[10px] text-muted-foreground uppercase tracking-widest mb-3">X-108 Guard — Formal Decision Pipeline</div>
            <div className="flex flex-col gap-0">
              {([
                { step: "ACTION REQUEST", desc: "Agent proposes an irreversible action", color: "#60a5fa", icon: "⚡" },
                { step: "IRREVERSIBILITY CHECK", desc: "Is action irreversible? If yes, enforce HOLD", color: "#f59e0b", icon: "❓" },
                { step: `HOLD τ = ${thresholds.holdTau}s`, desc: "Mandatory waiting period", color: "#f59e0b", icon: "⏱" },
                { step: "COHERENCE RECOMPUTE", desc: "GARCH + Merkle + 9 ontological tests", color: "#a78bfa", icon: "🔄" },
                { step: "DECISION", desc: "BLOCK → HOLD → ALLOW (priority order)", color: "#4ade80", icon: "🛡" },
              ] as { step: string; desc: string; color: string; icon: string }[]).map((item, i, arr) => (
                <div key={i}>
                  <div className="flex items-center gap-2 px-2 py-1.5 rounded" style={{ background: `${item.color}10`, border: `1px solid ${item.color}25` }}>
                    <span className="text-xs">{item.icon}</span>
                    <div>
                      <div className="font-mono font-bold text-[9px]" style={{ color: item.color }}>{item.step}</div>
                      <div className="text-[8px] text-muted-foreground">{item.desc}</div>
                    </div>
                  </div>
                  {i < arr.length - 1 && <div className="text-center text-[8px] text-muted-foreground py-0.5">↓</div>}
                </div>
              ))}
            </div>
            <div className="mt-2 px-2 py-1 rounded font-mono text-[8px] font-bold text-center" style={{ background: "oklch(0.12 0.02 0)", border: "1px solid #f8717130", color: "#f87171" }}>
              RULE: BLOCK &gt; HOLD &gt; ALLOW — Safety takes absolute priority
            </div>
          </div>
          {/* Cycle IN→WAIT→OUT explanation */}
          <div className="panel p-3">
            <div className="font-mono text-[10px] text-muted-foreground uppercase tracking-widest mb-3">Cycle IN → WAIT → OUT</div>
            <div className="flex items-stretch gap-0">
              {[
                { phase: "IN", icon: "⚡", color: "#ef4444", desc: "Ordre reçu — Guard X-108 intercepte avant exécution" },
                { phase: "→", icon: "", color: "#374151", desc: "" },
                { phase: "WAIT", icon: "⏱", color: "#f59e0b", desc: `τ = ${thresholds.holdTau}s — Analyse déterministe (GARCH, Merkle, 9 tests)` },
                { phase: "→", icon: "", color: "#374151", desc: "" },
                { phase: "OUT", icon: "🛡", color: "#4ade80", desc: "Décision ALLOW/HOLD/BLOCK avec hash SHA-256 immuable" },
              ].map((item, i) => (
                item.phase === "→" ? (
                  <div key={i} className="flex items-center px-2 text-muted-foreground text-sm">→</div>
                ) : (
                  <div key={i} className="flex-1 rounded-lg p-2" style={{ background: `${item.color}08`, border: `1px solid ${item.color}20` }}>
                    <div className="flex items-center gap-1 mb-1">
                      <span>{item.icon}</span>
                      <span className="font-mono font-bold text-xs" style={{ color: item.color }}>{item.phase}</span>
                    </div>
                    <div className="text-[8px] text-muted-foreground leading-relaxed">{item.desc}</div>
                  </div>
                )
              ))}
            </div>
          </div>
        </div>

        {/* Right: Tokenomics $X108 */}
        <div className="col-span-3 flex flex-col gap-3">
          {/* Donut Chart */}
          <div className="panel p-3">
            <div className="font-mono text-[10px] text-muted-foreground uppercase tracking-widest mb-3">💎 Tokenomics $X108</div>
            <div className="flex items-center gap-3">
              <DonutChart data={donutData} />
              <div className="space-y-2 flex-1">
                {donutData.map((d) => (
                  <div key={d.label} className="flex items-center gap-2 text-[9px] font-mono">
                    <div className="w-2 h-2 rounded-full" style={{ background: d.color }} />
                    <span className="text-muted-foreground">{d.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Tokenomics Stats */}
          <div className="panel p-3 space-y-2">
            <div className="font-mono text-[10px] text-muted-foreground uppercase tracking-widest mb-2">Métriques $X108</div>
            {[
              { label: "Frais totaux collectés", value: `${tokenomics.totalFees.toFixed(1)} €`, color: "#4ade80" },
              { label: "→ Stakers (50%)", value: `${tokenomics.stakersShare.toFixed(1)} €`, color: "#4ade80" },
              { label: "→ Treasury (30%)", value: `${tokenomics.treasuryShare.toFixed(1)} €`, color: "#60a5fa" },
              { label: "→ Buyback (20%)", value: `${tokenomics.buybackShare.toFixed(1)} €`, color: "#a78bfa" },
              { label: "Supply en circulation", value: `${(tokenomics.circulatingSupply / 1e6).toFixed(1)}M`, color: "#d1d5db" },
              { label: "Tokens brûlés", value: `${(tokenomics.burnedTokens / 1000).toFixed(0)}k`, color: "#f87171" },
              { label: "APY Staking", value: `${tokenomics.stakingAPY}%`, color: "#4ade80" },
            ].map((item) => (
              <div key={item.label} className="flex justify-between text-[9px] font-mono">
                <span className="text-muted-foreground">{item.label}</span>
                <span style={{ color: item.color }}>{item.value}</span>
              </div>
            ))}
          </div>

          {/* Fee Model */}
          <div className="panel p-3">
            <div className="font-mono text-[10px] text-muted-foreground uppercase tracking-widest mb-2">Modèle de Frais</div>
            <div className="text-center py-2">
              <div className="font-mono font-bold text-2xl" style={{ color: "oklch(0.80 0.15 60)" }}>0.1%</div>
              <div className="text-[9px] text-muted-foreground mt-1">par transaction protégée</div>
            </div>
            <div className="space-y-1 text-[9px] font-mono text-muted-foreground">
              <div>• Prélevé uniquement sur les BLOCK</div>
              <div>• HOLD : 0.05% (demi-frais)</div>
              <div>• ALLOW : 0% (gratuit)</div>
              <div>• Paiement en $X108 ou ETH</div>
            </div>
          </div>

          {/* Governance Votes */}
          <div className="panel p-3">
            <div className="font-mono text-[10px] text-muted-foreground uppercase tracking-widest mb-2">Gouvernance DAO</div>
            <div className="space-y-2">
              {[
                { proposal: "Augmenter τ à 15s", for: 67, against: 33, status: "ACTIVE" },
                { proposal: "Réduire frais à 0.08%", for: 45, against: 55, status: "REJECTED" },
                { proposal: "Ajouter vertical DeFi", for: 82, against: 18, status: "PASSED" },
              ].map((vote) => (
                <div key={vote.proposal} className="space-y-0.5">
                  <div className="flex justify-between text-[9px] font-mono">
                    <span className="text-foreground">{vote.proposal}</span>
                    <span className={`text-[8px] px-1 rounded ${vote.status === "ACTIVE" ? "text-amber-400 bg-amber-400/10" : vote.status === "PASSED" ? "text-green-400 bg-green-400/10" : "text-red-400 bg-red-400/10"}`}>{vote.status}</span>
                  </div>
                  <div className="h-1 rounded-full bg-black/30 overflow-hidden flex">
                    <div className="h-full bg-green-400/60" style={{ width: `${vote.for}%` }} />
                    <div className="h-full bg-red-400/60" style={{ width: `${vote.against}%` }} />
                  </div>
                  <div className="flex justify-between text-[8px] font-mono text-muted-foreground">
                    <span className="text-green-400">Pour {vote.for}%</span>
                    <span className="text-red-400">Contre {vote.against}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
