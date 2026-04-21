import React from "react";

// ─── Types ────────────────────────────────────────────────────────────────────
export type CommandDomain = "trading" | "bank" | "ecom";

// Règle 1 : Source — fallback reste un état dégradé, pas un mode normal
export type CommandSource = "auto" | "python_preferred" | "fallback_only_debug";

// Règle 2 : Mode — définitions strictes
export type CommandMode = "brut" | "gouverne" | "gouverne_preuve";

export interface CommandParams {
  domain: CommandDomain;
  scenarioId: string;
  mode: CommandMode;
  source: CommandSource;
  // Trading
  taille?: number;       // taille de position (€)
  risque?: number;       // 0–100 %
  volatilite?: number;   // 0–1
  // Bank
  montant?: number;      // montant transaction (€)
  urgence?: number;      // 0–1
  contrepartie?: number; // score 0–1
  identiteNouvelle?: boolean;
  // Ecom
  panier?: number;       // valeur panier (€)
  marge?: number;        // 0–100 %
  trafic?: number;       // req/s
  friction?: number;     // 0–1
  // Communs
  elapsed?: number;      // secondes
  tau?: number;          // seuil temporel
  irreversible?: boolean;
  stressIntensity?: number; // 0–1
}

interface CommandPanelProps {
  params: CommandParams;
  onChange: (next: CommandParams) => void;
  onRun: () => void;
  loading?: boolean;
  availableScenarios?: { id: string; label: string; domain?: string }[];
}

// ─── Constantes ───────────────────────────────────────────────────────────────
const DOMAIN_COLOR: Record<CommandDomain, string> = {
  trading: "oklch(0.65 0.18 220)",
  bank:    "oklch(0.75 0.18 75)",
  ecom:    "oklch(0.72 0.18 145)",
};

const DOMAIN_LABEL: Record<CommandDomain, string> = {
  trading: "Trading",
  bank:    "Bank",
  ecom:    "E-Com",
};

const MODE_DEFS: Record<CommandMode, { label: string; desc: string; color: string }> = {
  brut:          { label: "Brut",           desc: "Verdict métier uniquement — non exécutoire",             color: "oklch(0.55 0.05 240)" },
  gouverne:      { label: "Gouverné",       desc: "Verdict + Gate X-108",                                   color: "oklch(0.72 0.18 145)" },
  gouverne_preuve: { label: "Gouverné + Preuve", desc: "Verdict + X-108 + ticket / trace / attestation",   color: "oklch(0.65 0.18 220)" },
};

const SOURCE_DEFS: Record<CommandSource, { label: string; desc: string; color: string; warning?: boolean }> = {
  auto:               { label: "Auto",                desc: "Python si disponible, fallback sinon",                        color: "oklch(0.72 0.18 145)" },
  python_preferred:   { label: "Python préféré",      desc: "Force Python — erreur si hors ligne",                         color: "oklch(0.65 0.18 220)" },
  fallback_only_debug: { label: "⚠ Fallback debug",  desc: "Mode dégradé local uniquement — résultats non souverains",    color: "oklch(0.75 0.18 75)", warning: true },
};

const SCENARIOS_BY_DOMAIN: Record<CommandDomain, { id: string; label: string }[]> = {
  trading: [
    { id: "flash_crash",         label: "Flash Crash" },
    { id: "black_swan",          label: "Black Swan" },
    { id: "market_manipulation", label: "Manipulation de marché" },
    { id: "clock_drift",         label: "Dérive temporelle" },
  ],
  bank: [
    { id: "bank_run",            label: "Bank Run" },
    { id: "fraud_attack",        label: "Attaque fraude" },
    { id: "fraud_wave",          label: "Vague de fraude" },
    { id: "credit_bubble_burst", label: "Éclatement bulle crédit" },
  ],
  ecom: [
    { id: "traffic_spike",       label: "Pic de trafic" },
    { id: "bot_traffic_attack",  label: "Attaque bots" },
    { id: "supply_chain_break",  label: "Rupture supply chain" },
    { id: "ai_adversarial",      label: "Adversarial AI" },
  ],
};

// ─── Sous-composants ──────────────────────────────────────────────────────────
function SliderField({ label, value, min, max, step = 1, unit = "", onChange }: {
  label: string; value: number; min: number; max: number; step?: number; unit?: string;
  onChange: (v: number) => void;
}) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between items-center">
        <span className="text-[10px] font-mono" style={{ color: "oklch(0.55 0.01 240)" }}>{label}</span>
        <span className="text-[10px] font-mono font-bold" style={{ color: "oklch(0.80 0.02 240)" }}>
          {typeof value === "number" && step < 1 ? value.toFixed(2) : value}{unit}
        </span>
      </div>
      <input
        type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(Number(e.target.value))}
        className="w-full h-1 rounded appearance-none cursor-pointer"
        style={{ accentColor: "oklch(0.72 0.18 145)" }}
      />
    </div>
  );
}

function ToggleField({ label, value, onChange }: { label: string; value: boolean; onChange: (v: boolean) => void }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-[10px] font-mono" style={{ color: "oklch(0.55 0.01 240)" }}>{label}</span>
      <button
        onClick={() => onChange(!value)}
        className="px-2 py-0.5 rounded font-mono text-[10px] font-bold transition-all"
        style={{
          background: value ? "oklch(0.13 0.06 145 / 0.4)" : "oklch(0.12 0.01 240)",
          border: `1px solid ${value ? "oklch(0.72 0.18 145 / 0.5)" : "oklch(0.22 0.01 240)"}`,
          color: value ? "oklch(0.72 0.18 145)" : "oklch(0.45 0.01 240)",
        }}
      >
        {value ? "OUI" : "NON"}
      </button>
    </div>
  );
}

// ─── Composant principal ──────────────────────────────────────────────────────
export default function CommandPanel({ params, onChange, onRun, loading, availableScenarios }: CommandPanelProps) {
  const accent = DOMAIN_COLOR[params.domain];
  const scenarios = availableScenarios ?? SCENARIOS_BY_DOMAIN[params.domain];

  function set<K extends keyof CommandParams>(key: K, value: CommandParams[K]) {
    onChange({ ...params, [key]: value });
  }

  // Si le domaine change, réinitialiser le scénario
  function setDomain(d: CommandDomain) {
    const firstScenario = SCENARIOS_BY_DOMAIN[d][0].id;
    onChange({ ...params, domain: d, scenarioId: firstScenario });
  }

  return (
    <div className="rounded p-4 flex flex-col gap-4" style={{ background: "oklch(0.10 0.01 240)", border: `1px solid ${accent}33` }}>
      {/* ── Titre ── */}
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-mono font-bold tracking-widest uppercase" style={{ color: accent }}>
          Poste de Commande
        </span>
        <span className="text-[9px] font-mono px-2 py-0.5 rounded" style={{ background: "oklch(0.13 0.01 240)", color: "oklch(0.40 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
          OS4 / Guard X-108
        </span>
      </div>

      {/* ── Ligne 1 : Domaine + Scénario ── */}
      <div className="grid grid-cols-2 gap-3">
        {/* Domaine */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[9px] font-mono tracking-widest uppercase" style={{ color: "oklch(0.40 0.01 240)" }}>Domaine</span>
          <div className="flex gap-1">
            {(["trading", "bank", "ecom"] as CommandDomain[]).map(d => (
              <button
                key={d}
                onClick={() => setDomain(d)}
                className="flex-1 py-1.5 rounded font-mono text-[10px] font-bold transition-all"
                style={{
                  background: params.domain === d ? `${DOMAIN_COLOR[d]}22` : "oklch(0.12 0.01 240)",
                  border: `1px solid ${params.domain === d ? DOMAIN_COLOR[d] + "66" : "oklch(0.18 0.01 240)"}`,
                  color: params.domain === d ? DOMAIN_COLOR[d] : "oklch(0.45 0.01 240)",
                }}
              >
                {DOMAIN_LABEL[d]}
              </button>
            ))}
          </div>
        </div>

        {/* Scénario */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[9px] font-mono tracking-widest uppercase" style={{ color: "oklch(0.40 0.01 240)" }}>Scénario</span>
          <select
            value={params.scenarioId}
            onChange={e => set("scenarioId", e.target.value)}
            className="w-full py-1.5 px-2 rounded font-mono text-[10px] outline-none"
            style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.20 0.01 240)", color: "oklch(0.75 0.02 240)" }}
          >
            {scenarios.map(s => (
              <option key={s.id} value={s.id}>{s.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* ── Ligne 2 : Mode + Source ── */}
      <div className="grid grid-cols-2 gap-3">
        {/* Mode — Règle 2 : définitions strictes */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[9px] font-mono tracking-widest uppercase" style={{ color: "oklch(0.40 0.01 240)" }}>Mode d'exécution</span>
          <div className="flex flex-col gap-1">
            {(Object.entries(MODE_DEFS) as [CommandMode, typeof MODE_DEFS[CommandMode]][]).map(([k, def]) => (
              <button
                key={k}
                onClick={() => set("mode", k)}
                className="text-left px-2 py-1.5 rounded transition-all"
                style={{
                  background: params.mode === k ? `${def.color}18` : "oklch(0.12 0.01 240)",
                  border: `1px solid ${params.mode === k ? def.color + "55" : "oklch(0.18 0.01 240)"}`,
                }}
              >
                <div className="font-mono text-[10px] font-bold" style={{ color: params.mode === k ? def.color : "oklch(0.50 0.01 240)" }}>
                  {def.label}
                </div>
                <div className="font-mono text-[9px] leading-tight mt-0.5" style={{ color: "oklch(0.38 0.01 240)" }}>
                  {def.desc}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Source — Règle 1 : fallback = état dégradé */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[9px] font-mono tracking-widest uppercase" style={{ color: "oklch(0.40 0.01 240)" }}>Source de décision</span>
          <div className="flex flex-col gap-1">
            {(Object.entries(SOURCE_DEFS) as [CommandSource, typeof SOURCE_DEFS[CommandSource]][]).map(([k, def]) => (
              <button
                key={k}
                onClick={() => set("source", k)}
                className="text-left px-2 py-1.5 rounded transition-all"
                style={{
                  background: params.source === k ? `${def.color}18` : "oklch(0.12 0.01 240)",
                  border: `1px solid ${params.source === k ? def.color + "55" : "oklch(0.18 0.01 240)"}`,
                }}
              >
                <div className="font-mono text-[10px] font-bold" style={{ color: params.source === k ? def.color : "oklch(0.50 0.01 240)" }}>
                  {def.label}
                </div>
                <div className="font-mono text-[9px] leading-tight mt-0.5" style={{ color: def.warning ? "oklch(0.65 0.15 75)" : "oklch(0.38 0.01 240)" }}>
                  {def.desc}
                </div>
              </button>
            ))}
          </div>
          {params.source === "fallback_only_debug" && (
            <div className="px-2 py-1.5 rounded font-mono text-[9px]" style={{ background: "oklch(0.12 0.08 75 / 0.3)", border: "1px solid oklch(0.75 0.18 75 / 0.4)", color: "oklch(0.75 0.18 75)" }}>
              ⚠ Mode dégradé — décisions non souveraines
            </div>
          )}
        </div>
      </div>

      {/* ── Ligne 3 : Paramètres domain-aware — Règle 3 ── */}
      <div className="flex flex-col gap-2">
        <span className="text-[9px] font-mono tracking-widest uppercase" style={{ color: "oklch(0.40 0.01 240)" }}>
          Paramètres — {DOMAIN_LABEL[params.domain]}
        </span>
        <div className="grid grid-cols-2 gap-3">
          {/* Trading */}
          {params.domain === "trading" && <>
            <SliderField label="Taille position (€)" value={params.taille ?? 10000} min={1000} max={1000000} step={1000} unit="€" onChange={v => set("taille", v)} />
            <SliderField label="Risque (%)" value={params.risque ?? 20} min={0} max={100} step={1} unit="%" onChange={v => set("risque", v)} />
            <SliderField label="Volatilité" value={params.volatilite ?? 0.20} min={0} max={1} step={0.01} onChange={v => set("volatilite", v)} />
            <SliderField label="Intensité stress" value={params.stressIntensity ?? 0.5} min={0} max={1} step={0.01} onChange={v => set("stressIntensity", v)} />
          </>}
          {/* Bank */}
          {params.domain === "bank" && <>
            <SliderField label="Montant transaction (€)" value={params.montant ?? 50000} min={100} max={10000000} step={100} unit="€" onChange={v => set("montant", v)} />
            <SliderField label="Urgence" value={params.urgence ?? 0.3} min={0} max={1} step={0.01} onChange={v => set("urgence", v)} />
            <SliderField label="Score contrepartie" value={params.contrepartie ?? 0.7} min={0} max={1} step={0.01} onChange={v => set("contrepartie", v)} />
            <SliderField label="Intensité stress" value={params.stressIntensity ?? 0.5} min={0} max={1} step={0.01} onChange={v => set("stressIntensity", v)} />
          </>}
          {/* Ecom */}
          {params.domain === "ecom" && <>
            <SliderField label="Valeur panier (€)" value={params.panier ?? 150} min={10} max={10000} step={10} unit="€" onChange={v => set("panier", v)} />
            <SliderField label="Marge (%)" value={params.marge ?? 30} min={0} max={100} step={1} unit="%" onChange={v => set("marge", v)} />
            <SliderField label="Trafic (req/s)" value={params.trafic ?? 100} min={1} max={10000} step={1} onChange={v => set("trafic", v)} />
            <SliderField label="Intensité stress" value={params.stressIntensity ?? 0.5} min={0} max={1} step={0.01} onChange={v => set("stressIntensity", v)} />
          </>}
          {/* Communs */}
          <SliderField label="Elapsed (s)" value={params.elapsed ?? 5} min={0} max={60} step={1} unit="s" onChange={v => set("elapsed", v)} />
          <SliderField label="Tau (seuil temporel)" value={params.tau ?? 10} min={0} max={60} step={1} unit="s" onChange={v => set("tau", v)} />
        </div>
        <div className="grid grid-cols-2 gap-3 pt-1">
          <ToggleField label="Irréversible" value={params.irreversible ?? false} onChange={v => set("irreversible", v)} />
          {params.domain === "bank" && (
            <ToggleField label="Identité nouvelle" value={params.identiteNouvelle ?? false} onChange={v => set("identiteNouvelle", v)} />
          )}
        </div>
      </div>

      {/* ── Bouton Run ── */}
      <button
        onClick={onRun}
        disabled={loading}
        className="w-full py-2.5 rounded font-mono text-sm font-bold tracking-widest uppercase transition-all"
        style={{
          background: loading ? "oklch(0.14 0.01 240)" : `${accent}22`,
          border: `1.5px solid ${loading ? "oklch(0.22 0.01 240)" : accent + "66"}`,
          color: loading ? "oklch(0.45 0.01 240)" : accent,
          cursor: loading ? "not-allowed" : "pointer",
        }}
      >
        {loading ? "⟳ Exécution en cours…" : "▶ Lancer le scénario"}
      </button>
    </div>
  );
}
