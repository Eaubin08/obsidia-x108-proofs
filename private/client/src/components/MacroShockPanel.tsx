import React from "react";

export type MacroShock = "flash_crash" | "rate_hike" | "fraud_attack" | "supply_shock" | null;

export interface ShockConfig {
  id: MacroShock;
  label: string;
  icon: string;
  description: string;
  color: string;
  borderColor: string;
  bgColor: string;
  effects: {
    trading?: string;
    bank?: string;
    ecom?: string;
  };
}

export const MACRO_SHOCKS: ShockConfig[] = [
  {
    id: "flash_crash",
    label: "Flash Crash",
    icon: "💥",
    description: "Effondrement soudain des marchés (-15% en 5min)",
    color: "text-red-400",
    borderColor: "border-red-500/50",
    bgColor: "bg-red-500/10",
    effects: {
      trading: "Régime Crisis activé — Jump diffusion +300% — Spread ×5",
      bank: "CIZ explose → 0.95 — DTS → 0.88 — Blocages sécurité",
      ecom: "Agents paniquent — HOLD X-108 déclenché — Supply issues",
    },
  },
  {
    id: "rate_hike",
    label: "Macro Rate Hike",
    icon: "📈",
    description: "Hausse surprise des taux directeurs (+75bps)",
    color: "text-amber-400",
    borderColor: "border-amber-500/50",
    bgColor: "bg-amber-500/10",
    effects: {
      trading: "Régime trend_down — Corrélations sectorielles modifiées",
      bank: "IR → 0.75 — Flux de trésorerie perturbés — TSG dégradé",
      ecom: "CVR chute — Marge compressée — Agents en mode défensif",
    },
  },
  {
    id: "fraud_attack",
    label: "Fraud Attack",
    icon: "🔓",
    description: "Vague de tentatives d'account takeover",
    color: "text-purple-400",
    borderColor: "border-purple-500/50",
    bgColor: "bg-purple-500/10",
    effects: {
      trading: "Volatilité anormale — Ordres suspects détectés",
      bank: "CIZ → 0.92 — 9 tests ontologiques activés — BLOCK massif",
      ecom: "Cohérence agents < 0.6 — BLOCK automatique X-108",
    },
  },
  {
    id: "supply_shock",
    label: "Supply Shock",
    icon: "🏭",
    description: "Rupture d'approvisionnement critique",
    color: "text-orange-400",
    borderColor: "border-orange-500/50",
    bgColor: "bg-orange-500/10",
    effects: {
      trading: "Secteur energy en crise — Corrélations tech/energy inversées",
      bank: "DTS → 0.80 — Liquidité tendue — Réserves sous pression",
      ecom: "Stock → 0 — Agent pub veut dépenser malgré rupture — BLOCK",
    },
  },
];

interface MacroShockPanelProps {
  activeShock: MacroShock;
  onShockSelect: (shock: MacroShock) => void;
}

export function MacroShockPanel({ activeShock, onShockSelect }: MacroShockPanelProps) {
  return (
    <div className="rounded-lg border border-[#1e2a1e] bg-[#0a0f0a] p-4">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-xs font-mono text-[#4ade80]/70 uppercase tracking-widest">⚡ MACRO SHOCK EVENTS</span>
        {activeShock && (
          <span className="ml-auto text-[10px] font-mono text-red-400">● ACTIF</span>
        )}
      </div>
      <div className="grid grid-cols-2 gap-2 mb-3">
        {MACRO_SHOCKS.map((shock) => {
          const isActive = activeShock === shock.id;
          return (
            <button
              key={shock.id}
              onClick={() => onShockSelect(isActive ? null : shock.id)}
              className={`text-left p-3 rounded-lg border transition-all duration-300 ${
                isActive
                  ? `${shock.bgColor} ${shock.borderColor} ${shock.color}`
                  : "bg-[#0d140d] border-[#1e2a1e] text-[#6b7280] hover:border-[#2a3a2a] hover:text-[#9ca3af]"
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="text-base">{shock.icon}</span>
                <span className="text-xs font-bold font-mono">{shock.label}</span>
                {isActive && <span className="ml-auto text-[10px]">●</span>}
              </div>
              <div className="text-[9px] opacity-70 leading-relaxed">{shock.description}</div>
            </button>
          );
        })}
      </div>
      {activeShock && (() => {
        const shock = MACRO_SHOCKS.find(s => s.id === activeShock)!;
        return (
          <div className={`rounded-lg border p-3 ${shock.bgColor} ${shock.borderColor}`}>
            <div className={`text-[10px] font-mono font-bold mb-2 ${shock.color}`}>
              {shock.icon} IMPACT SYNCHRONISÉ SUR TOUTES LES VERTICALES
            </div>
            <div className="space-y-1.5">
              {shock.effects.trading && (
                <div className="flex gap-2">
                  <span className="text-[9px] font-mono text-[#4ade80] w-16 flex-shrink-0">📈 TRADING</span>
                  <span className="text-[9px] text-[#d1d5db]">{shock.effects.trading}</span>
                </div>
              )}
              {shock.effects.bank && (
                <div className="flex gap-2">
                  <span className="text-[9px] font-mono text-[#60a5fa] w-16 flex-shrink-0">🏦 BANK</span>
                  <span className="text-[9px] text-[#d1d5db]">{shock.effects.bank}</span>
                </div>
              )}
              {shock.effects.ecom && (
                <div className="flex gap-2">
                  <span className="text-[9px] font-mono text-[#f59e0b] w-16 flex-shrink-0">🛒 ECOM</span>
                  <span className="text-[9px] text-[#d1d5db]">{shock.effects.ecom}</span>
                </div>
              )}
            </div>
          </div>
        );
      })()}
      {!activeShock && (
        <div className="text-[9px] text-[#4b5563] text-center font-mono">
          Sélectionne un scénario pour simuler un choc synchronisé sur les 3 verticales
        </div>
      )}
    </div>
  );
}
