/**
 * WorldContext — filtre monde global OS4 V2
 * Persiste le monde actif (Trading / Bank / Ecom) et la temporalité (Live / Simu / Fallback / Mixed / Demo)
 * Disponible dans toute l'app via useWorld()
 */
import React, { createContext, useContext, useState, useCallback } from "react";

export type WorldDomain = "trading" | "bank" | "ecom";
export type OperatingMode = "LIVE" | "SIMU" | "FALLBACK" | "MIXED" | "DEMO";

export interface WorldState {
  /** Monde actif */
  domain: WorldDomain;
  /** Mode de lecture */
  mode: OperatingMode;
  /** Source dominante (ex: "real-time", "simulation", "fallback") */
  source: string;
  /** Gate X-108 courant */
  x108Gate: "ALLOW" | "HOLD" | "BLOCK" | null;
  /** Dernier decision_id connu */
  lastDecisionId: string | null;
  /** Statut preuve courant */
  proofStatus: "COMPLETE" | "PARTIAL" | "MISSING" | null;
  /** Timestamp de la dernière mise à jour du gate (ms UTC) */
  gateUpdatedAt: number | null;
  /** Setters */
  setDomain: (d: WorldDomain) => void;
  setMode: (m: OperatingMode) => void;
  setSource: (s: string) => void;
  setX108Gate: (g: "ALLOW" | "HOLD" | "BLOCK" | null) => void;
  setLastDecisionId: (id: string | null) => void;
  setProofStatus: (s: "COMPLETE" | "PARTIAL" | "MISSING" | null) => void;
}

const defaultState: WorldState = {
  domain: "trading",
  mode: "DEMO",
  source: "simulation",
  x108Gate: null,
  lastDecisionId: null,
  proofStatus: null,
  gateUpdatedAt: null,
  setDomain: () => {},
  setMode: () => {},
  setSource: () => {},
  setX108Gate: () => {},
  setLastDecisionId: () => {},
  setProofStatus: () => {},
};

export const WorldContext = createContext<WorldState>(defaultState);

export function WorldProvider({ children }: { children: React.ReactNode }) {
  const [domain, setDomainState] = useState<WorldDomain>("trading");
  const [mode, setModeState] = useState<OperatingMode>("DEMO");
  const [source, setSourceState] = useState<string>("simulation");
  const [x108Gate, setX108GateState] = useState<"ALLOW" | "HOLD" | "BLOCK" | null>(null);
  const [lastDecisionId, setLastDecisionIdState] = useState<string | null>(null);
  const [proofStatus, setProofStatusState] = useState<"COMPLETE" | "PARTIAL" | "MISSING" | null>(null);
  const [gateUpdatedAt, setGateUpdatedAt] = useState<number | null>(null);

  const setDomain = useCallback((d: WorldDomain) => setDomainState(d), []);
  const setMode = useCallback((m: OperatingMode) => setModeState(m), []);
  const setSource = useCallback((s: string) => setSourceState(s), []);
  const setX108Gate = useCallback((g: "ALLOW" | "HOLD" | "BLOCK" | null) => {
    setX108GateState(g);
    setGateUpdatedAt(Date.now());
  }, []);
  const setLastDecisionId = useCallback((id: string | null) => setLastDecisionIdState(id), []);
  const setProofStatus = useCallback((s: "COMPLETE" | "PARTIAL" | "MISSING" | null) => setProofStatusState(s), []);

  return (
    <WorldContext.Provider value={{
      domain, mode, source, x108Gate, lastDecisionId, proofStatus, gateUpdatedAt,
      setDomain, setMode, setSource, setX108Gate, setLastDecisionId, setProofStatus,
    }}>
      {children}
    </WorldContext.Provider>
  );
}

export function useWorld() {
  return useContext(WorldContext);
}

/** Couleurs par domaine */
export const DOMAIN_COLORS: Record<WorldDomain, { accent: string; bg: string; border: string; label: string; icon: string }> = {
  trading: {
    accent: "oklch(0.72 0.18 145)",
    bg: "oklch(0.72 0.18 145 / 0.08)",
    border: "oklch(0.72 0.18 145 / 0.25)",
    label: "Trading",
    icon: "📈",
  },
  bank: {
    accent: "oklch(0.65 0.18 240)",
    bg: "oklch(0.65 0.18 240 / 0.08)",
    border: "oklch(0.65 0.18 240 / 0.25)",
    label: "Bank",
    icon: "🏦",
  },
  ecom: {
    accent: "oklch(0.72 0.18 45)",
    bg: "oklch(0.72 0.18 45 / 0.08)",
    border: "oklch(0.72 0.18 45 / 0.25)",
    label: "Ecom",
    icon: "🛒",
  },
};

/** Couleurs par mode */
export const MODE_COLORS: Record<OperatingMode, { color: string; bg: string; label: string }> = {
  LIVE:     { color: "oklch(0.72 0.18 145)", bg: "oklch(0.72 0.18 145 / 0.10)", label: "LIVE" },
  SIMU:     { color: "oklch(0.65 0.18 240)", bg: "oklch(0.65 0.18 240 / 0.10)", label: "SIMU" },
  FALLBACK: { color: "oklch(0.72 0.18 45)",  bg: "oklch(0.72 0.18 45 / 0.10)",  label: "FALLBACK" },
  MIXED:    { color: "#a78bfa",               bg: "oklch(0.60 0.15 290 / 0.10)", label: "MIXED" },
  DEMO:     { color: "oklch(0.55 0.01 240)",  bg: "oklch(0.14 0.01 240)",        label: "DEMO" },
};

/** Couleurs par gate X-108 */
export const GATE_COLORS: Record<"ALLOW" | "HOLD" | "BLOCK", { color: string; bg: string }> = {
  ALLOW: { color: "oklch(0.72 0.18 145)", bg: "oklch(0.72 0.18 145 / 0.12)" },
  HOLD:  { color: "oklch(0.72 0.18 45)",  bg: "oklch(0.72 0.18 45 / 0.12)"  },
  BLOCK: { color: "oklch(0.65 0.25 25)",  bg: "oklch(0.65 0.25 25 / 0.12)"  },
};
