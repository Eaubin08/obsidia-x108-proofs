/**
 * BankWorld — Simulation d'institution financière
 * Connecté au vrai backend trpc.bank.simulate (bankEngine.ts)
 * Métriques IR/CIZ/DTS/TSG calculées par le moteur réel + explication LLM
 */
import { useState, useCallback, useContext, useRef, useEffect } from "react";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler } from "chart.js";
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler);
import { useViewMode } from "@/contexts/ViewModeContext";
import { trpc } from "@/lib/trpc";
import { DecisionBadge } from "@/components/MetricCard";
import { OpenBrainView, BrainData } from "@/components/OpenBrainView";
import { StrasbourgClock } from "@/components/StrasbourgClock";
import { PortfolioContext } from "@/App";
import { EngineBlock } from "@/components/EngineBlock";
import MarketExplanation from "@/components/MarketExplanation";
import CausalPipeline, { PipelineDomain } from "@/components/CausalPipeline";
import { ConceptTooltip, DecisionLegend } from "@/components/ConceptTooltip";
import CanonicalRealPanel from "@/components/CanonicalRealPanel";
import CanonicalProofPanel from "@/components/CanonicalProofPanel";
import SurfaceStatusBadge from "@/components/SurfaceStatusBadge";
import DecisionSummaryBar from "@/components/DecisionSummaryBar";
import PilotagePanel from "@/components/PilotagePanel";
import { ModeBadgeBar } from "@/components/ModeBadge";
import WorldMetierHeader from "@/components/WorldMetierHeader";
import ProjectionPanel from "@/components/ProjectionPanel";
import WorldPageTemplate from "@/components/WorldPageTemplate";

// ─── Types ────────────────────────────────────────────────────────────────────

interface SimResult {
  metrics: {
    finalBalance: number;
    totalDeposits: number;
    totalWithdrawals: number;
    totalFraudLoss: number;
    fraudCount: number;
    fraudDetectionRate: number;
    ir: number;
    ciz: number;
    dts: number;
    tsg: number;
    savingsGoalMet: boolean;
    reserveCompliance: number;
    stateHash: string;
    merkleRoot: string;
  };
  ticket: {
    decision: "ALLOW" | "HOLD" | "BLOCK";
    reasons: string[];
    x108?: { elapsed: number; tau: number; hold?: boolean; gate_active?: boolean; irr?: boolean };
  };
  steps: {
    t: number;
    balance: number;
    cashFlow: number;
    fraudDetected: boolean;
    fraudAmount: number;
    interestEarned: number;
    reserveRatio: number;
  }[];
}

interface RunRecord {
  id: string;
  label: string;
  timestamp: number;
  params: BankParams;
  result: SimResult;
  llmExplanation?: string;
}

interface BankParams {
  seed: number;
  steps: number;
  initialBalance: number;
  mu: number;
  sigma: number;
  withdrawalRate?: number;
  fraudRate: number;
  fraudAmount: number;
  fraudDetectionCapacity?: number; // 0..1, default 0.8
  interestRate: number;
  savingsGoal: number;
  reserveRatio: number;
}

// ─── Scénarios prédéfinis ─────────────────────────────────────────────────────

const SCENARIOS: { label: string; icon: string; desc: string; params: Partial<BankParams>; riskLevel: "low" | "medium" | "high" }[] = [
  {
    label: "Dépôt standard",
    icon: "⬆️",
    desc: "Flux de dépôts normaux, faible volatilité",
    params: { mu: 0.05, sigma: 0.2, fraudRate: 0.01, fraudAmount: 200, steps: 90 },
    riskLevel: "low",
  },
  {
    label: "Retrait massif",
    icon: "⬇️",
    desc: "Retraits importants, pression sur la liquidité",
    params: { mu: -0.08, sigma: 0.6, fraudRate: 0.02, fraudAmount: 500, steps: 90 },
    riskLevel: "medium",
  },
  {
    label: "Vague de fraude",
    icon: "⚠️",
    desc: "Taux de fraude élevé — test du détecteur",
    params: { mu: 0.01, sigma: 0.3, fraudRate: 0.15, fraudAmount: 1500, steps: 90 },
    riskLevel: "high",
  },
  {
    label: "Bank Run",
    icon: "🏃",
    desc: "Retrait de 90% du capital en 30 jours",
    params: { mu: -0.25, sigma: 1.2, fraudRate: 0.05, fraudAmount: 800, steps: 30 },
    riskLevel: "high",
  },
  {
    label: "Prêt à risque",
    icon: "🏦",
    desc: "Émission de prêts à fort levier",
    params: { mu: 0.03, sigma: 0.8, fraudRate: 0.03, fraudAmount: 600, steps: 180, savingsGoal: 200000 },
    riskLevel: "medium",
  },
  {
    label: "Effondrement systémique",
    icon: "💥",
    desc: "Scénario catastrophe — test ultime du Guard",
    params: { mu: -0.4, sigma: 2.0, fraudRate: 0.25, fraudAmount: 3000, steps: 60, reserveRatio: 0.05 },
    riskLevel: "high",
  },
  {
    label: "Crise Financière",
    icon: "⚠️",
    desc: "Dépenses > revenus (withdrawalRate=1.5) — Guard BLOCK sur CIZ + DTS + IR",
    params: { mu: 0.0, sigma: 0.6, withdrawalRate: 1.5, fraudRate: 0.05, fraudAmount: 800, steps: 180 },
    riskLevel: "high",
  },
  {
    label: "Fraude Massive",
    icon: "🚨",
    desc: "Capacité de détection réduite à 30% — Guard BLOCK sur fraudDetectionRate (31% < seuil 60%)",
    params: { mu: 0.0, sigma: 0.3, withdrawalRate: 0.7, fraudRate: 0.15, fraudAmount: 2000, fraudDetectionCapacity: 0.3, steps: 365 },
    riskLevel: "high",
  },
];

const CHAIN_SCENARIOS = [
  { label: "Dépôt +5 000€", params: { mu: 0.05, sigma: 0.1, fraudRate: 0.005, fraudAmount: 100, steps: 10 } },
  { label: "Investir 20 000€", params: { mu: 0.03, sigma: 0.4, fraudRate: 0.01, fraudAmount: 300, steps: 30 } },
  { label: "Retrait 5 000€ (profit)", params: { mu: -0.02, sigma: 0.15, fraudRate: 0.005, fraudAmount: 100, steps: 10 } },
  { label: "Prêt 30 000€ (levier)", params: { mu: 0.04, sigma: 0.7, fraudRate: 0.03, fraudAmount: 500, steps: 60 } },
  { label: "Investir 30 000€ (levier)", params: { mu: 0.02, sigma: 0.9, fraudRate: 0.04, fraudAmount: 700, steps: 60 } },
  { label: "Retrait massif 85 000€", params: { mu: -0.35, sigma: 1.5, fraudRate: 0.08, fraudAmount: 2000, steps: 30 } },
];

// ─── Helpers ──────────────────────────────────────────────────────────────────

const decisionColor = (d: "ALLOW" | "HOLD" | "BLOCK") =>
  d === "ALLOW" ? "#22c55e" : d === "HOLD" ? "#f59e0b" : "#ef4444";

const riskColor = (level: "low" | "medium" | "high") =>
  level === "low" ? "rgba(34,197,94,0.3)" : level === "medium" ? "rgba(245,158,11,0.3)" : "rgba(239,68,68,0.3)";

function buildBrainData(result: SimResult, label: string): BrainData {
  const { metrics, ticket } = result;
  const lastStep = result.steps[result.steps.length - 1];
  return {
    sees: [
      { label: "Scénario", value: label },
      { label: "Solde final", value: metrics.finalBalance.toFixed(0), unit: " €" },
      { label: "Fraudes détectées", value: metrics.fraudCount },
      { label: "Taux détection", value: (metrics.fraudDetectionRate * 100).toFixed(1), unit: "%" },
      { label: "Réserve", value: lastStep ? (lastStep.reserveRatio * 100).toFixed(1) : "—", unit: "%" },
    ],
    thinks: [
      {
        label: "IR — Taux de rendement",
        value: Math.max(0, Math.min(1, (metrics.ir + 0.5))),
        color: metrics.ir > 0 ? "green" : metrics.ir > -0.1 ? "amber" : "red",
        description: `Rendement annualisé : ${(metrics.ir * 100).toFixed(1)}%`,
      },
      {
        label: "CIZ — Intégrité du capital",
        value: Math.max(0, Math.min(1, metrics.ciz)),
        color: metrics.ciz > 0.9 ? "green" : metrics.ciz > 0.7 ? "amber" : "red",
        description: `Ratio capital final/initial : ${(metrics.ciz * 100).toFixed(1)}%`,
      },
      {
        label: "DTS — Ratio dettes/épargne",
        value: Math.max(0, Math.min(1, 1 - metrics.dts)),
        color: metrics.dts < 0.8 ? "green" : metrics.dts < 1.2 ? "amber" : "red",
        description: `Retraits / dépôts : ${(metrics.dts * 100).toFixed(1)}%`,
      },
      {
        label: "TSG — Écart objectif épargne",
        value: Math.max(0, Math.min(1, 1 - Math.max(0, metrics.tsg))),
        color: metrics.tsg < 0.2 ? "green" : metrics.tsg < 0.5 ? "amber" : "red",
        description: metrics.savingsGoalMet ? "Objectif épargne atteint ✓" : `Écart : ${(metrics.tsg * 100).toFixed(1)}%`,
      },
    ],
    decision: ticket.decision,
    decisionLabel:
      ticket.decision === "BLOCK"
        ? "Simulation bloquée — risque systémique détecté"
        : ticket.decision === "HOLD"
        ? "Simulation suspendue — vérification en cours"
        : "Simulation autorisée — profil sain",
    capitalImpact:
      ticket.decision === "BLOCK"
        ? `Capital protégé : +${(metrics.finalBalance).toLocaleString("fr-FR")} €`
        : undefined,
  };
}

// ─── Component ────────────────────────────────────────────────────────────────

export default function BankWorld() {
  const portfolio = useContext(PortfolioContext);
  const { isSimple } = useViewMode();

  // tRPC mutations
  const simulateMut = trpc.bank.simulate.useMutation();
  const explainMut = trpc.ai.explainDecision.useMutation();
  // Stats Guard réelles depuis la DB (persistantes entre sessions)
  const guardStatsQuery = trpc.proof.guardStats.useQuery(undefined, { refetchInterval: 15000 });
  const guardStats = guardStatsQuery.data;
  const updateWalletMut = trpc.portfolio.updateWallet.useMutation();
  const saveSnapshotMut = trpc.portfolio.saveSnapshot.useMutation();
  const upsertPositionMut = trpc.portfolio.upsertPosition.useMutation();

  // State
  const [activeTab, setActiveTab] = useState<"scenarios" | "chain" | "history" | "attacks">("scenarios");
  const [lastResult, setLastResult] = useState<SimResult | null>(null);
  const [lastLabel, setLastLabel] = useState<string>("");
  const [llmExplanation, setLlmExplanation] = useState<string>("");
  const [isLoadingLLM, setIsLoadingLLM] = useState(false);
  const [runHistory, setRunHistory] = useState<RunRecord[]>([]);
  const [holdActive, setHoldActive] = useState(false);
  const [holdElapsed, setHoldElapsed] = useState(0);
  const [chainRunning, setChainRunning] = useState(false);
  const [chainStep, setChainStep] = useState(0);
  const [chainResults, setChainResults] = useState<{ label: string; result: SimResult }[]>([]);
  const [totalCapital, setTotalCapital] = useState(100000);
  const [totalSaved, setTotalSaved] = useState(0);
  const [totalBlocked, setTotalBlocked] = useState(0);
  const [canonicalEnvelope, setCanonicalEnvelope] = useState<any>(null);
  const [canonicalVerify, setCanonicalVerify] = useState<any>(null);
  const canonicalAttestation = trpc.engine.attestation.useQuery({ day: undefined });
  const decisionEnvelopeMut = trpc.engine.decisionEnvelope.useMutation({
    onSuccess: (data) => {
      setCanonicalEnvelope(data);
      if (data?.ticket_id) {
        verifyTicketMut.mutate({ ticketId: data.ticket_id });
      }
    },
  });
  const verifyTicketMut = trpc.engine.verifyTicket.useMutation({
    onSuccess: (data) => setCanonicalVerify(data),
  });
  // Graphique : historique des soldes (max 100 points)
  const [balanceHistory, setBalanceHistory] = useState<{ label: string; balance: number; decision: string }[]>([]);
  // Mode automatique
  const [autoRunning, setAutoRunning] = useState(false);
  const autoRunRef = useRef(false);
  // Panneau formules
  const [showFormulas, setShowFormulas] = useState(false);
  // Comparateur Python
  const [showComparator, setShowComparator] = useState(false);
  const [pythonResult, setPythonResult] = useState<{ decision: string; reasons: string[]; metrics?: Record<string, number> } | null>(null);
  const [pythonLoading, setPythonLoading] = useState(false);
  const [pythonError, setPythonError] = useState<string | null>(null);
  // Mode Story Crise Bancaire
  const [bankStoryActive, setBankStoryActive] = useState(false);
  const [bankStoryStep, setBankStoryStep] = useState(0);
  const [bankStoryResults, setBankStoryResults] = useState<{ label: string; result: SimResult; explanation: string }[]>([]);
  const [bankStoryRunning, setBankStoryRunning] = useState(false);

  const BANK_STORY_STEPS = [
    {
      title: "Étape 1 — Dépôts normaux",
      icon: "⬆️",
      desc: "La banque reçoit des dépôts réguliers. IR positif, CIZ > 1. Le Guard autorise.",
      params: { mu: 0.05, sigma: 0.15, withdrawalRate: 0.5, fraudRate: 0.005, fraudAmount: 100, steps: 60 },
      expectedDecision: "ALLOW" as const,
    },
    {
      title: "Étape 2 — Fraude détectée",
      icon: "⚠️",
      desc: "Une vague de transactions suspectes est détectée. Le Guard passe en HOLD.",
      params: { mu: 0.01, sigma: 0.3, withdrawalRate: 0.8, fraudRate: 0.12, fraudAmount: 1200, steps: 30 },
      expectedDecision: "HOLD" as const,
    },
    {
      title: "Étape 3 — Retraits massifs",
      icon: "⚡",
      desc: "Les clients retirent massivement. DTS > 1, IR négatif. Le Guard évalue le risque.",
      params: { mu: -0.15, sigma: 0.8, withdrawalRate: 1.2, fraudRate: 0.03, fraudAmount: 500, steps: 45 },
      expectedDecision: "HOLD" as const,
    },
    {
      title: "Étape 4 — Crise systémique",
      icon: "💥",
      desc: "Dépenses 50% supérieures aux revenus. CIZ < 0.7, DTS > 1.5. Guard BLOCK.",
      params: { mu: -0.3, sigma: 1.2, withdrawalRate: 1.5, fraudRate: 0.08, fraudAmount: 2000, steps: 60 },
      expectedDecision: "BLOCK" as const,
    },
    {
      title: "Étape 5 — Bilan de crise",
      icon: "📋",
      desc: "Analyse post-crise : capital protégé par le Guard, pertes évitées calculées.",
      params: { mu: 0.02, sigma: 0.2, withdrawalRate: 0.6, fraudRate: 0.01, fraudAmount: 200, steps: 30 },
      expectedDecision: "ALLOW" as const,
    },
  ];

  const runBankStory = useCallback(async () => {
    setBankStoryActive(true);
    setBankStoryStep(0);
    setBankStoryResults([]);
    setBankStoryRunning(true);
    const results: { label: string; result: SimResult; explanation: string }[] = [];
    for (let i = 0; i < BANK_STORY_STEPS.length; i++) {
      const step = BANK_STORY_STEPS[i];
      setBankStoryStep(i);
      try {
        const result = await simulateMut.mutateAsync({
          seed: 42 + i * 7,
          steps: step.params.steps,
          initialBalance: totalCapital,
          mu: step.params.mu,
          sigma: step.params.sigma,
          withdrawalRate: step.params.withdrawalRate,
          fraudRate: step.params.fraudRate,
          fraudAmount: step.params.fraudAmount,
          interestRate: 0.03,
          savingsGoal: totalCapital * 1.5,
          reserveRatio: 0.1,
        }) as unknown as SimResult;
        let explanation = "";
        try {
          const llmRes = await explainMut.mutateAsync({
            vertical: "BANK" as const,
            decision: result.ticket.decision,
            metrics: { ir: result.metrics.ir, ciz: result.metrics.ciz, dts: result.metrics.dts, tsg: result.metrics.tsg },
            context: `Crise Bancaire - ${step.title} : IR=${(result.metrics.ir * 100).toFixed(1)}%, CIZ=${(result.metrics.ciz * 100).toFixed(1)}%, DTS=${(result.metrics.dts * 100).toFixed(1)}%`,
          });
          explanation = llmRes.explanation ?? "";
        } catch { explanation = step.desc; }
        results.push({ label: step.title, result, explanation });
        setBankStoryResults([...results]);
        await new Promise(r => setTimeout(r, 400));
      } catch { break; }
    }
    setBankStoryRunning(false);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [simulateMut, explainMut, totalCapital]);

  const runPythonEngine = useCallback(async (params: BankParams) => {
    setPythonLoading(true);
    setPythonError(null);
    setPythonResult(null);
    try {
      const res = await fetch("/api/python-engine/decision", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agent_id: "cortex_central",
          action: "bank_simulation",
          amount: params.initialBalance,
          irreversible: true,
          metadata: { mu: params.mu, sigma: params.sigma, fraudRate: params.fraudRate, steps: params.steps },
        }),
      });
      const data = await res.json();
      // Si le moteur Python est indisponible (503), afficher un message clair
      if (!res.ok || data.available === false) {
        setPythonError(data.message ?? `Moteur Python indisponible (HTTP ${res.status})`);
        return;
      }
      setPythonResult(data);
    } catch (err) {
      setPythonError("Moteur Python OS0/OS1/OS2 non disponible dans cet environnement. Le moteur TypeScript OS4 est actif.");
    } finally {
      setPythonLoading(false);
    }
  }, []);

  // ─── Exécuter une simulation via le vrai backend ──────────────────────────
  const runSimulation = useCallback(
    async (label: string, overrideParams?: Partial<BankParams>) => {
      const seed = Math.floor(Math.random() * 100000);
      const params: BankParams = {
        seed,
        steps: 90,
        initialBalance: totalCapital,
        mu: 0.02,
        sigma: 0.5,
        fraudRate: 0.02,
        fraudAmount: 500,
        interestRate: 0.03,
        savingsGoal: totalCapital * 1.5,
        reserveRatio: 0.1,
        ...overrideParams,
      };

      try {
        const result = await simulateMut.mutateAsync(params) as unknown as SimResult;
        setLastResult(result);
        setLastLabel(label);

        // Hold timer si HOLD
        if (result.ticket.decision === "HOLD") {
          setHoldActive(true);
          setHoldElapsed(0);
          const interval = setInterval(() => {
            setHoldElapsed((e) => {
              if (e >= 10) {
                clearInterval(interval);
                setHoldActive(false);
                return 0;
              }
              return e + 1;
            });
          }, 1000);
        }

        // Mise à jour capital
        const newCapital = result.metrics.finalBalance;
        setTotalCapital(newCapital);
        if (result.ticket.decision === "BLOCK") {
          setTotalBlocked((b) => b + 1);
          setTotalSaved((s) => s + params.initialBalance);
        }

        // Graphique solde
        setBalanceHistory((h) => [...h, { label: label.slice(0, 16), balance: newCapital, decision: result.ticket.decision }].slice(-100));

        // Enregistrement historique
        const record: RunRecord = {
          id: `run-${Date.now()}`,
          label,
          timestamp: Date.now(),
          params,
          result,
        };
        setRunHistory((h) => [record, ...h].slice(0, 20));

        // Portfolio DB
        if (result.ticket.decision === "BLOCK") {
          updateWalletMut.mutate({ guardBlocks: 1, capitalSaved: params.initialBalance });
          saveSnapshotMut.mutate({
            capital: params.initialBalance,
            pnl: 0,
            guardBlocks: 1,
            capitalSaved: params.initialBalance,
            domain: "bank",
            scenarioName: `${label} — BLOCK`,
          });
        } else if (result.ticket.decision === "ALLOW") {
          const pnl = newCapital - params.initialBalance;
          updateWalletMut.mutate({ bankBalance: newCapital, bankLiquidity: result.metrics.ciz });
          saveSnapshotMut.mutate({
            capital: newCapital,
            pnl,
            guardBlocks: 0,
            capitalSaved: 0,
            domain: "bank",
            scenarioName: label,
          });
          if (portfolio) portfolio.onTradingUpdate({ pnl });
        }
        if (portfolio && result.ticket.decision === "BLOCK") portfolio.onGuardBlock();

        upsertPositionMut.mutate({
          domain: "bank",
          asset: `BANK:${label.slice(0, 24)}`,
          quantity: 1,
          avgEntryPrice: params.initialBalance,
          currentValue: newCapital,
          unrealizedPnl: newCapital - params.initialBalance,
        });

        // Appel backend canonique (fire-and-forget)
        decisionEnvelopeMut.mutate({
          domain: "bank",
          amount: params.initialBalance,
          irreversible: result.ticket.decision === "BLOCK",
          coherence: result.metrics.ciz,
          volatility: Math.max(0, 1 - result.metrics.ciz),
          timeElapsed: 12,
          tau: 10,
        });

        // Explication LLM (fire-and-forget)
        setIsLoadingLLM(true);
        setLlmExplanation("");
        explainMut
          .mutateAsync({
            vertical: "BANK",
            decision: result.ticket.decision,
            metrics: {
              IR: result.metrics.ir,
              CIZ: result.metrics.ciz,
              DTS: result.metrics.dts,
              TSG: result.metrics.tsg,
              fraudDetectionRate: result.metrics.fraudDetectionRate,
              reserveCompliance: result.metrics.reserveCompliance,
            },
            context: label,
            capitalImpact: newCapital - params.initialBalance,
          })
          .then((r) => {
            setLlmExplanation(r.explanation);
            setRunHistory((h) =>
              h.map((rec) => (rec.id === record.id ? { ...rec, llmExplanation: r.explanation } : rec))
            );
          })
          .catch(() => setLlmExplanation("Explication indisponible."))
          .finally(() => setIsLoadingLLM(false));

        return result;
      } catch (err) {
        console.error("[BankWorld] Simulation error:", err);
        return null;
      }
    },
    [totalCapital, simulateMut, explainMut, updateWalletMut, saveSnapshotMut, upsertPositionMut, portfolio]
  );

  // ─── Chaîne d'investissement ──────────────────────────────────────────────
  const runChain = useCallback(async () => {
    setChainRunning(true);
    setChainStep(0);
    setChainResults([]);
    let currentCapital = 100000;
    setTotalCapital(currentCapital);

    for (let i = 0; i < CHAIN_SCENARIOS.length; i++) {
      const step = CHAIN_SCENARIOS[i];
      setChainStep(i + 1);
      await new Promise((r) => setTimeout(r, 600));
      const result = await runSimulation(step.label, {
        ...step.params,
        initialBalance: currentCapital,
        savingsGoal: currentCapital * 1.5,
      });
      if (result) {
        currentCapital = result.metrics.finalBalance;
        setChainResults((cr) => [...cr, { label: step.label, result }]);
      }
    }
    setChainRunning(false);
  }, [runSimulation]);

  const resetState = () => {
    setLastResult(null);
    setLastLabel("");
    setLlmExplanation("");
    setRunHistory([]);
    setChainResults([]);
    setChainStep(0);
    setTotalCapital(100000);
    setTotalSaved(0);
    setTotalBlocked(0);
    setBalanceHistory([]);
    autoRunRef.current = false;
    setAutoRunning(false);
  };

  // ─── Mode automatique : 10 simulations aléatoires ────────────────────────
  const runAutoMode = useCallback(async () => {
    if (autoRunning) {
      autoRunRef.current = false;
      setAutoRunning(false);
      return;
    }
    autoRunRef.current = true;
    setAutoRunning(true);
    const randomScenario = () => SCENARIOS[Math.floor(Math.random() * SCENARIOS.length)];
    for (let i = 0; i < 10; i++) {
      if (!autoRunRef.current) break;
      const s = randomScenario();
      await runSimulation(`Auto #${i + 1} — ${s.label}`, s.params);
      await new Promise((r) => setTimeout(r, 800));
    }
    autoRunRef.current = false;
    setAutoRunning(false);
  }, [autoRunning, runSimulation]);

  const isLoading = simulateMut.isPending;

  return (
    <div className="p-4 max-w-7xl mx-auto space-y-6">
      {/* ─── Barre de régime opératoire ─────────────────────────────────────── */}
      <ModeBadgeBar
        mode={(canonicalAttestation.data as any)?.source === "local_fallback" ? "FALLBACK" : (canonicalAttestation.data as any)?.merkle_root ? "LIVE" : "DEMO"}
        detail={(canonicalAttestation.data as any)?.merkle_root ? `Merkle : ${((canonicalAttestation.data as any)?.merkle_root as string)?.slice(0, 12) ?? "—"}` : "Simulation bancaire — aucune transaction réelle"}
        right={lastResult ? `dernier : ${lastResult.ticket.decision} · bank` : undefined}
      />
      {/* ── Header métier Banque ── */}
      <WorldMetierHeader
        domain="bank"
        mode="LIVE"
        x108Status={(canonicalAttestation.data as any)?.merkle_root ? "ONLINE" : "DEGRADED"}
        lastDecision={lastResult?.ticket?.decision === "ALLOW" || lastResult?.ticket?.decision === "HOLD" || lastResult?.ticket?.decision === "BLOCK" ? lastResult.ticket.decision : null}
        decisionCount={totalSaved > 0 ? Math.ceil(totalSaved / (totalCapital || 100000)) : undefined}
        verdicts={[
          { label: "Capital protégé", value: totalSaved > 0 ? `+${totalSaved.toLocaleString("fr-FR")} €` : "€ 0 protégé", color: "oklch(0.65 0.18 240)", icon: "🛡️" },
          { label: "Capital actuel", value: `${totalCapital.toLocaleString("fr-FR")} €`, color: "oklch(0.72 0.18 45)", icon: "🏦" },
          { label: "Dernière décision", value: lastResult ? lastResult.ticket.decision : "En attente", color: lastResult?.ticket?.decision === "BLOCK" ? "oklch(0.65 0.25 25)" : lastResult?.ticket?.decision === "HOLD" ? "oklch(0.72 0.18 45)" : "oklch(0.72 0.18 145)", icon: lastResult?.ticket?.decision === "BLOCK" ? "❌" : lastResult?.ticket?.decision === "HOLD" ? "⏸️" : "✅" },
        ]}
        sliders={[
          { key: "totalCapital", label: "Capital initial (€)", min: 10000, max: 1000000, step: 10000, value: totalCapital, unit: " €", color: "oklch(0.65 0.18 240)" },
        ]}
        onSliderChange={(key, val) => { if (key === "totalCapital") setTotalCapital(val); }}
      />
      {/* ─── Header ─── */}
      <div className="panel p-4">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h1 className="text-lg font-bold font-mono" style={{ color: "#f59e0b" }}>
              🏦 BANK WORLD — Simulation d'institution financière
            </h1>
            <p className="text-xs text-muted-foreground mt-1">
              Moteur log-normal + détection de fraude · Guard X-108 évalue chaque simulation · Métriques IR/CIZ/DTS/TSG calculées en temps réel
            </p>
          </div>
          <div className="flex items-center gap-3">
              <a href="/future?domain=bank"
                className="flex items-center gap-1 px-2 py-0.5 rounded text-[9px] font-mono font-bold"
                style={{ background: "oklch(0.65 0.18 240 / 0.12)", border: "1px solid oklch(0.65 0.18 240 / 0.35)", color: "oklch(0.65 0.18 240)" }}>
                ▶ Simuler dans Future
              </a>
              <SurfaceStatusBadge
                status={
                  canonicalAttestation.isLoading ? "LOADING"
                  : canonicalAttestation.error ? "ERROR"
                  : (canonicalAttestation.data as any)?.source === "local_fallback" ? "PARTIAL"
                  : (canonicalAttestation.data as any)?.merkle_root ? "REAL"
                  : "PARTIAL"
                }
                source={
                  (canonicalAttestation.data as any)?.source === "local_fallback" ? "os4_local_fallback"
                  : (canonicalAttestation.data as any)?.merkle_root ? "python"
                  : undefined
                }
              />
          <button
            onClick={runAutoMode}
            disabled={isLoading && !autoRunning}
            className="text-xs font-mono px-3 py-1 rounded border transition-colors"
            style={{
              borderColor: autoRunning ? "#ef4444" : "#f59e0b",
              color: autoRunning ? "#ef4444" : "#f59e0b",
              background: autoRunning ? "rgba(239,68,68,0.08)" : "rgba(245,158,11,0.08)",
            }}
          >
            {autoRunning ? "⏹ Arrêter" : "▶▶ 10 simulations"}
          </button>
          <button
            onClick={() => { setBankStoryActive(true); setBankStoryResults([]); setBankStoryRunning(false); }}
            className="text-xs font-mono px-3 py-1 rounded border transition-colors"
            style={{ borderColor: "rgba(96,165,250,0.4)", color: "oklch(0.65 0.18 220)", background: "rgba(96,165,250,0.06)" }}
          >
            🏦 Mode Story
          </button>
          <button
            onClick={resetState}
            className="text-xs font-mono px-3 py-1 rounded border border-border hover:bg-muted"
          >
            ↺ Reset
          </button>
        </div>
        </div>

        {/* ── BLOC 1 : Résultat visible en 3s ── */}
        <div className="mt-2">
          <DecisionSummaryBar
            gate={lastResult?.ticket?.decision ?? null}
            verdict={lastResult?.ticket?.decision === "BLOCK" ? "TRANSACTION_BLOCKED" : lastResult?.ticket?.decision === "HOLD" ? "HOLD_X108" : lastResult?.ticket?.decision === "ALLOW" ? "TRANSACTION_VALIDATED" : undefined}
            source={canonicalEnvelope?.source ?? (lastResult ? "os4_local_fallback" : undefined)}
            severity={canonicalEnvelope?.severity}
            reason={lastResult?.ticket?.reasons?.[0]}
            loading={isLoading}
            domain="bank"
          />
        </div>
        {/* ─── KPIs ─── */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {[
            {
              label: "Capital actuel",
              value: `${totalCapital.toLocaleString("fr-FR")} €`,
              color: totalCapital > 80000 ? "#22c55e" : totalCapital > 50000 ? "#f59e0b" : "#ef4444",
            },
            {
              label: "Simulations",
              value: runHistory.length,
              color: "#60a5fa",
            },
            {
              label: "Bloquées",
              value: guardStats ? guardStats.byDomain?.bank?.blocked ?? 0 : totalBlocked,
              color: (guardStats?.byDomain?.bank?.blocked ?? totalBlocked) > 0 ? "#ef4444" : "#6b7280",
              badge: guardStats ? "DB" : undefined,
            },
            {
              label: "Capital protégé",
              value: totalSaved > 0 ? `${totalSaved.toLocaleString("fr-FR")} €` : "0 €",
              color: "#a78bfa",
            },
            {
              label: "Dernier verdict",
              value: lastResult ? lastResult.ticket.decision : "—",
              color: lastResult ? decisionColor(lastResult.ticket.decision) : "#6b7280",
            },
          ].map((m) => (
            <div key={m.label} className="panel p-3 text-center relative">
              <div className="text-xs text-muted-foreground mb-1 flex items-center justify-center gap-1">
                {m.label}
                {(m as any).badge && (
                  <span className="text-[8px] px-1 py-0.5 rounded" style={{ background: "oklch(0.60 0.12 200 / 0.15)", color: "oklch(0.60 0.12 200)" }}>{(m as any).badge}</span>
                )}
              </div>
              <div className="text-sm font-bold font-mono" style={{ color: m.color }}>
                {m.value}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ─── Tabs ─── */}
      <div className="flex gap-2 flex-wrap">
        {(["scenarios", "chain", "history", "attacks"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className="text-xs font-mono px-4 py-2 rounded border transition-colors"
            style={{
              borderColor: activeTab === tab ? "#f59e0b" : "rgba(255,255,255,0.1)",
              color: activeTab === tab ? "#f59e0b" : "#9ca3af",
              background: activeTab === tab ? "rgba(245,158,11,0.1)" : "transparent",
            }}
          >
            {tab === "scenarios"
              ? "⚡ Scénarios"
              : tab === "chain"
              ? "🔗 Chaîne"
              : tab === "history"
              ? "📋 Historique"
              : "💥 Attaques"}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* ─── Left Panel ─── */}
        <div className="space-y-4">
          {/* Scénarios */}
          {activeTab === "scenarios" && (
            <div className="panel p-4">
              <h3 className="text-xs font-mono font-bold mb-3" style={{ color: "#f59e0b" }}>
                ⚡ SCÉNARIOS — Simulation via moteur réel
              </h3>
              <div className="grid grid-cols-1 gap-2">
                {SCENARIOS.map((s) => (
                  <button
                    key={s.label}
                    onClick={() => runSimulation(s.label, s.params)}
                    disabled={isLoading}
                    className="text-left p-3 rounded border transition-colors hover:bg-muted disabled:opacity-50"
                    style={{ borderColor: riskColor(s.riskLevel) }}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-base">{s.icon}</span>
                      <span className="text-xs font-mono font-bold">{s.label}</span>
                      <span
                        className="ml-auto text-[9px] font-mono px-1.5 py-0.5 rounded"
                        style={{
                          background: riskColor(s.riskLevel),
                          color: s.riskLevel === "low" ? "#22c55e" : s.riskLevel === "medium" ? "#f59e0b" : "#ef4444",
                        }}
                      >
                        {s.riskLevel === "low" ? "FAIBLE" : s.riskLevel === "medium" ? "MOYEN" : "ÉLEVÉ"}
                      </span>
                    </div>
                    <div className="text-[10px] text-muted-foreground">{s.desc}</div>
                  </button>
                ))}
              </div>
              {isLoading && (
                <div className="mt-3 text-center text-xs font-mono text-amber-400">
                  ⏳ Simulation en cours — moteur log-normal + Guard X-108...
                </div>
              )}
            </div>
          )}

          {/* Chaîne */}
          {activeTab === "chain" && (
            <div className="panel p-4">
              <h3 className="text-xs font-mono font-bold mb-3" style={{ color: "#f59e0b" }}>
                🔗 INVESTMENTCHAIN — Séquence de 6 simulations enchaînées
              </h3>
              <p className="text-[10px] text-muted-foreground mb-3">
                Chaque étape utilise le capital résultant de la précédente. Le Guard X-108 évalue chaque simulation avec le vrai moteur backend.
              </p>
              <div className="space-y-2 mb-4">
                {CHAIN_SCENARIOS.map((step, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-2 p-2 rounded text-[10px] font-mono"
                    style={{
                      background:
                        chainStep > i
                          ? "rgba(34,197,94,0.1)"
                          : chainStep === i + 1
                          ? "rgba(245,158,11,0.1)"
                          : "rgba(255,255,255,0.02)",
                      border: `1px solid ${
                        chainStep > i
                          ? "rgba(34,197,94,0.3)"
                          : chainStep === i + 1
                          ? "rgba(245,158,11,0.3)"
                          : "rgba(255,255,255,0.06)"
                      }`,
                    }}
                  >
                    <span
                      style={{
                        color: chainStep > i ? "#22c55e" : chainStep === i + 1 ? "#f59e0b" : "#6b7280",
                      }}
                    >
                      {chainStep > i ? "✅" : chainStep === i + 1 ? "⏳" : `${i + 1}.`}
                    </span>
                    <span className="flex-1">{step.label}</span>
                    {chainResults[i] && (
                      <span style={{ color: decisionColor(chainResults[i].result.ticket.decision) }}>
                        {chainResults[i].result.ticket.decision}
                      </span>
                    )}
                    {chainResults[i] && (
                      <span className="text-muted-foreground">
                        {chainResults[i].result.metrics.finalBalance.toLocaleString("fr-FR")} €
                      </span>
                    )}
                  </div>
                ))}
              </div>
              <button
                onClick={runChain}
                disabled={chainRunning}
                className="w-full py-2 rounded font-mono text-xs font-bold transition-colors"
                style={{
                  background: chainRunning ? "rgba(245,158,11,0.3)" : "rgba(245,158,11,0.8)",
                  color: "#000",
                }}
              >
                {chainRunning
                  ? `⏳ Étape ${chainStep}/${CHAIN_SCENARIOS.length} — simulation backend en cours...`
                  : "▶ Lancer la chaîne d'investissement (6 simulations réelles)"}
              </button>
              {chainResults.length > 0 && (
                <div className="mt-3 grid grid-cols-3 gap-2">
                  {(["ALLOW", "HOLD", "BLOCK"] as const).map((d) => (
                    <div key={d} className="text-center p-2 rounded" style={{ background: "rgba(255,255,255,0.03)" }}>
                      <div className="text-lg font-bold font-mono" style={{ color: decisionColor(d) }}>
                        {chainResults.filter((r) => r.result.ticket.decision === d).length}
                      </div>
                      <div className="text-[10px] text-muted-foreground">{d}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Historique */}
          {activeTab === "history" && (
            <div className="panel p-4">
              <h3 className="text-xs font-mono font-bold mb-3" style={{ color: "#f59e0b" }}>
                📋 HISTORIQUE — {runHistory.length} simulations
              </h3>
              {runHistory.length === 0 ? (
                <p className="text-[10px] text-muted-foreground text-center py-4">
                  Aucune simulation. Utilisez les onglets Scénarios ou Chaîne.
                </p>
              ) : (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {runHistory.map((rec) => (
                    <div
                      key={rec.id}
                      className="p-2 rounded text-[10px] font-mono"
                      style={{
                        background: "rgba(255,255,255,0.02)",
                        border: `1px solid ${decisionColor(rec.result.ticket.decision)}33`,
                      }}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span style={{ color: decisionColor(rec.result.ticket.decision) }}>
                          {rec.result.ticket.decision}
                        </span>
                        <span className="text-muted-foreground">
                          {new Date(rec.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <div className="text-white/80 mb-1">{rec.label}</div>
                      <div className="grid grid-cols-4 gap-1 mb-1">
                        {[
                          { k: "IR", v: rec.result.metrics.ir },
                          { k: "CIZ", v: rec.result.metrics.ciz },
                          { k: "DTS", v: rec.result.metrics.dts },
                          { k: "TSG", v: rec.result.metrics.tsg },
                        ].map((m) => (
                          <div key={m.k} className="text-center">
                            <div className="text-[8px] text-muted-foreground">{m.k}</div>
                            <div
                              className="text-[9px] font-bold"
                              style={{ color: m.v > 0.5 ? "#22c55e" : m.v > 0 ? "#f59e0b" : "#ef4444" }}
                            >
                              {(m.v * 100).toFixed(0)}%
                            </div>
                          </div>
                        ))}
                      </div>
                      <div className="text-muted-foreground">
                        Capital: {rec.params.initialBalance.toLocaleString("fr-FR")} →{" "}
                        {rec.result.metrics.finalBalance.toLocaleString("fr-FR")} € · Fraudes:{" "}
                        {rec.result.metrics.fraudCount}
                      </div>
                      {rec.llmExplanation && (
                        <div
                          className="mt-1 p-1.5 rounded text-[9px] italic"
                          style={{ background: "rgba(167,139,250,0.08)", color: "#a78bfa" }}
                        >
                          🤖 {rec.llmExplanation}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Attaques */}
          {activeTab === "attacks" && (
            <div className="panel p-4">
              <h3 className="text-xs font-mono font-bold mb-3" style={{ color: "#ef4444" }}>
                💥 ATTAQUES BANCAIRES — Scénarios adversariaux
              </h3>
              <div className="space-y-2">
                {[
                  {
                    label: "🏃 Bank Run — Retrait massif",
                    desc: "Retrait de 90% du capital en 30 jours",
                    params: { mu: -0.3, sigma: 1.5, fraudRate: 0.05, fraudAmount: 1000, steps: 30 },
                  },
                  {
                    label: "💧 Liquidity Drain — Assèchement",
                    desc: "Drain progressif de liquidité sur 60 jours",
                    params: { mu: -0.15, sigma: 0.8, fraudRate: 0.03, fraudAmount: 600, steps: 60 },
                  },
                  {
                    label: "🚨 Fraud Wave — 25% de fraudes",
                    desc: "Vague de fraude coordonnée",
                    params: { mu: 0.01, sigma: 0.3, fraudRate: 0.25, fraudAmount: 2000, steps: 30 },
                  },
                  {
                    label: "📈 Interest Rate Shock",
                    desc: "Choc de taux — prêts à risque élevé",
                    params: { mu: 0.02, sigma: 1.0, fraudRate: 0.04, fraudAmount: 800, steps: 90 },
                  },
                  {
                    label: "💳 Credit Bubble — Levier 3x",
                    desc: "Bulle de crédit avec levier excessif",
                    params: { mu: 0.05, sigma: 1.8, fraudRate: 0.06, fraudAmount: 1200, steps: 60 },
                  },
                  {
                    label: "🌪️ Systemic Collapse — Effondrement",
                    desc: "Scénario catastrophe — test ultime",
                    params: { mu: -0.5, sigma: 3.0, fraudRate: 0.3, fraudAmount: 5000, steps: 30, reserveRatio: 0.02 },
                  },
                  {
                    label: "🔒 Bail-In — Conversion forcée",
                    desc: "Bail-in réglementaire d'urgence",
                    params: { mu: -0.2, sigma: 1.2, fraudRate: 0.08, fraudAmount: 1500, steps: 45 },
                  },
                  {
                    label: "🤖 CBDC Crisis — Fuite digitale",
                    desc: "60% des dépôts migrent vers CBDC",
                    params: { mu: -0.12, sigma: 0.9, fraudRate: 0.04, fraudAmount: 700, steps: 60 },
                  },
                ].map((a) => (
                  <button
                    key={a.label}
                    onClick={() => runSimulation(a.label, a.params)}
                    disabled={isLoading}
                    className="w-full text-left p-3 rounded border transition-colors hover:bg-muted disabled:opacity-50"
                    style={{ borderColor: "rgba(239,68,68,0.3)" }}
                  >
                    <div className="text-xs font-mono font-bold mb-1" style={{ color: "#ef4444" }}>
                      {a.label}
                    </div>
                    <div className="text-[10px] text-muted-foreground">{a.desc}</div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* ─── Right Panel — Résultats Guard X-108 ─── */}
        <div className="space-y-4">
          {lastResult ? (
            <>
              {/* Décision principale */}
              <div className="panel p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-xs font-mono font-bold" style={{ color: "#f59e0b" }}>
                    <ConceptTooltip term="Guard X-108" showIcon>🛡️ GUARD X-108</ConceptTooltip> — Décision
                  </h3>
                  <DecisionBadge decision={lastResult.ticket.decision} />
                </div>
                <div className="text-sm font-mono font-bold mb-2" style={{ color: decisionColor(lastResult.ticket.decision) }}>
                  {lastLabel}
                </div>

                {/* Métriques IR/CIZ/DTS/TSG — calculées par le vrai moteur avec jauges Guard */}
                <div className="space-y-2 mb-3">
                  {/* CIZ — seuil Guard : min 0.95 */}
                  {(() => {
                    const ciz = lastResult.metrics.ciz;
                    const threshold = 0.95;
                    const pct = Math.min(Math.max(ciz / 2, 0), 1) * 100; // 0..200% mapped to 0..100%
                    const thresholdPct = (threshold / 2) * 100;
                    const color = ciz >= threshold ? "#22c55e" : ciz >= threshold * 0.9 ? "#f59e0b" : "#ef4444";
                    const zone = ciz >= threshold ? "SAFE" : ciz >= threshold * 0.9 ? "ALERTE" : "BLOCK";
                    return (
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-[10px] font-mono text-muted-foreground">CIZ — Intégrité capital</span>
                          <div className="flex items-center gap-2">
                            <span className="text-[9px] font-mono" style={{ color: "#6b7280" }}>seuil: {(threshold*100).toFixed(0)}%</span>
                            <span className="text-[10px] font-mono font-bold" style={{ color }}>{(ciz * 100).toFixed(1)}%</span>
                            <span className="text-[8px] font-mono px-1 rounded" style={{ background: color + "22", color }}>{zone}</span>
                          </div>
                        </div>
                        <div className="relative h-2 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.06)" }}>
                          <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, background: color }} />
                          <div className="absolute top-0 bottom-0 w-px" style={{ left: `${thresholdPct}%`, background: "#f59e0b", opacity: 0.8 }} />
                        </div>
                      </div>
                    );
                  })()}
                  {/* DTS — seuil Guard : max 0.90 */}
                  {(() => {
                    const dts = lastResult.metrics.dts;
                    const threshold = 0.90;
                    const pct = Math.min(dts / 2, 1) * 100;
                    const thresholdPct = (threshold / 2) * 100;
                    const color = dts <= threshold ? "#22c55e" : dts <= threshold * 1.1 ? "#f59e0b" : "#ef4444";
                    const zone = dts <= threshold ? "SAFE" : dts <= threshold * 1.1 ? "ALERTE" : "BLOCK";
                    return (
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-[10px] font-mono text-muted-foreground">DTS — Ratio dépenses/revenus</span>
                          <div className="flex items-center gap-2">
                            <span className="text-[9px] font-mono" style={{ color: "#6b7280" }}>seuil: {(threshold*100).toFixed(0)}%</span>
                            <span className="text-[10px] font-mono font-bold" style={{ color }}>{(dts * 100).toFixed(1)}%</span>
                            <span className="text-[8px] font-mono px-1 rounded" style={{ background: color + "22", color }}>{zone}</span>
                          </div>
                        </div>
                        <div className="relative h-2 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.06)" }}>
                          <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, background: color }} />
                          <div className="absolute top-0 bottom-0 w-px" style={{ left: `${thresholdPct}%`, background: "#f59e0b", opacity: 0.8 }} />
                        </div>
                      </div>
                    );
                  })()}
                  {/* IR — seuil Guard : min -5% */}
                  {(() => {
                    const ir = lastResult.metrics.ir;
                    const threshold = -0.05;
                    const pct = Math.min(Math.max((ir + 1) / 2, 0), 1) * 100;
                    const thresholdPct = ((threshold + 1) / 2) * 100;
                    const color = ir >= threshold ? (ir > 0 ? "#22c55e" : "#f59e0b") : "#ef4444";
                    const zone = ir >= threshold ? (ir > 0 ? "SAFE" : "ALERTE") : "BLOCK";
                    return (
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-[10px] font-mono text-muted-foreground">IR — Rendement annualisé</span>
                          <div className="flex items-center gap-2">
                            <span className="text-[9px] font-mono" style={{ color: "#6b7280" }}>seuil: {(threshold*100).toFixed(0)}%</span>
                            <span className="text-[10px] font-mono font-bold" style={{ color }}>{(ir * 100).toFixed(1)}%</span>
                            <span className="text-[8px] font-mono px-1 rounded" style={{ background: color + "22", color }}>{zone}</span>
                          </div>
                        </div>
                        <div className="relative h-2 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.06)" }}>
                          <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, background: color }} />
                          <div className="absolute top-0 bottom-0 w-px" style={{ left: `${thresholdPct}%`, background: "#f59e0b", opacity: 0.8 }} />
                        </div>
                      </div>
                    );
                  })()}
                  {/* TSG — objectif épargne */}
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono text-muted-foreground">TSG — Écart objectif épargne</span>
                    <span className="text-[10px] font-mono font-bold" style={{ color: lastResult.metrics.savingsGoalMet ? "#22c55e" : lastResult.metrics.tsg < 0.3 ? "#f59e0b" : "#ef4444" }}>
                      {lastResult.metrics.savingsGoalMet ? "✓ ATTEINT" : `-${(lastResult.metrics.tsg * 100).toFixed(1)}%`}
                    </span>
                  </div>
                </div>

                {/* Métriques financières détaillées */}
                <div className="grid grid-cols-2 gap-2 mb-3">
                  {[
                    {
                      label: "Solde final",
                      value: `${lastResult.metrics.finalBalance.toLocaleString("fr-FR")} €`,
                      color: lastResult.metrics.finalBalance > totalCapital ? "#22c55e" : "#ef4444",
                    },
                    {
                      label: "P&L",
                      value: `${(lastResult.metrics.finalBalance - totalCapital).toLocaleString("fr-FR")} €`,
                      color: lastResult.metrics.finalBalance >= totalCapital ? "#22c55e" : "#ef4444",
                    },
                    {
                      label: "Fraudes détectées",
                      value: `${lastResult.metrics.fraudCount} (${(lastResult.metrics.fraudDetectionRate * 100).toFixed(0)}% bloquées)`,
                      color: "#60a5fa",
                    },
                    {
                      label: "Conformité réserve",
                      value: `${(lastResult.metrics.reserveCompliance * 100).toFixed(1)}%`,
                      color: lastResult.metrics.reserveCompliance > 0.9 ? "#22c55e" : "#f59e0b",
                    },
                  ].map((m) => (
                    <div
                      key={m.label}
                      className="flex items-center justify-between px-3 py-2 rounded"
                      style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)" }}
                    >
                      <span className="text-[10px] text-muted-foreground">{m.label}</span>
                      <span className="text-[10px] font-mono font-bold" style={{ color: m.color }}>
                        {m.value}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Raisons Guard */}
                <div className="space-y-1 mb-3">
                  {lastResult.ticket.reasons.map((r, i) => (
                    <div
                      key={i}
                      className="text-[10px] font-mono p-2 rounded"
                      style={{ background: "rgba(255,255,255,0.02)", color: "#9ca3af" }}
                    >
                      • {r}
                    </div>
                  ))}
                </div>

                {/* Explication LLM */}
                <div
                  className="p-3 rounded"
                  style={{ background: "rgba(167,139,250,0.08)", border: "1px solid rgba(167,139,250,0.2)" }}
                >
                  <div className="text-[9px] font-mono uppercase tracking-widest mb-1" style={{ color: "#a78bfa" }}>
                    🤖 Explication IA
                  </div>
                  {isLoadingLLM ? (
                    <div className="text-[10px] text-muted-foreground italic">Analyse en cours...</div>
                  ) : llmExplanation ? (
                    <div className="text-[10px] text-white/80 leading-relaxed">{llmExplanation}</div>
                  ) : (
                    <div className="text-[10px] text-muted-foreground italic">En attente de simulation...</div>
                  )}
                </div>

                {/* Hash Merkle */}
                <div className="mt-2 text-[8px] font-mono text-muted-foreground/50 break-all">
                  Merkle: {lastResult.metrics.merkleRoot.slice(0, 32)}...
                </div>
              </div>

              {/* Open Brain View */}
              <OpenBrainView data={buildBrainData(lastResult, lastLabel)} />

              {/* Hold Clock */}
              {holdActive && (
                <div className="panel p-4">
                  <StrasbourgClock active={holdActive} tau={10} elapsed={holdElapsed} label="HOLD BANCAIRE X-108" />
                </div>
              )}
            </>
          ) : (
            <div
              className="panel p-4 flex flex-col items-center justify-center text-center"
              style={{ minHeight: "200px" }}
            >
              <div className="text-3xl mb-3">🏦</div>
              <div className="text-xs font-mono text-muted-foreground mb-2">Guard X-108 en veille</div>
              <div className="text-[10px] text-muted-foreground">
                Choisissez un scénario pour déclencher{" "}
                <ConceptTooltip term="Guard X-108" showIcon>Guard X-108</ConceptTooltip>
              </div>
              <div className="text-[10px] text-muted-foreground mt-2">
                Capital initial : 100 000 € · Moteur : log-normal + détection fraude
              </div>
              <div className="mt-3">
                <DecisionLegend compact />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ─── Graphique évolution du solde ─── */}
      {balanceHistory.length > 1 && (
        <div className="panel p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-mono font-bold" style={{ color: "#f59e0b" }}>📈 ÉVOLUTION DU SOLDE — {balanceHistory.length} simulations</h3>
            <span className="text-[9px] font-mono text-muted-foreground">Capital initial : 100 000 €</span>
          </div>
          <div style={{ height: "200px" }}>
            <Line
              data={{
                labels: balanceHistory.map((b) => b.label),
                datasets: [
                  {
                    label: "Solde (€)",
                    data: balanceHistory.map((b) => b.balance),
                    borderColor: "#f59e0b",
                    backgroundColor: "rgba(245,158,11,0.08)",
                    fill: true,
                    tension: 0.3,
                    pointRadius: balanceHistory.map((b) =>
                      b.decision === "BLOCK" ? 5 : b.decision === "HOLD" ? 4 : 2
                    ),
                    pointBackgroundColor: balanceHistory.map((b) =>
                      b.decision === "BLOCK" ? "#ef4444" : b.decision === "HOLD" ? "#f59e0b" : "#22c55e"
                    ),
                    borderWidth: 1.5,
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: { tooltip: { callbacks: { label: (ctx) => `${(ctx.parsed.y ?? 0).toLocaleString("fr-FR")} €` } }, legend: { display: false } },
                scales: {
                  x: { ticks: { color: "#6b7280", font: { size: 8 }, maxRotation: 0, maxTicksLimit: 10 }, grid: { color: "rgba(255,255,255,0.04)" } },
                  y: { ticks: { color: "#9ca3af", font: { size: 9 }, callback: (v) => `€${Number(v).toLocaleString("fr-FR")}` }, grid: { color: "rgba(255,255,255,0.04)" } },
                },
              }}
            />
          </div>
          <div className="flex gap-4 mt-2 text-[9px] font-mono text-muted-foreground">
            <span><span style={{ color: "#22c55e" }}>●</span> ALLOW</span>
            <span><span style={{ color: "#f59e0b" }}>●</span> HOLD</span>
            <span><span style={{ color: "#ef4444" }}>●</span> BLOCK</span>
            <span className="ml-auto">Solde min : {Math.min(...balanceHistory.map(b => b.balance)).toLocaleString("fr-FR")} € · max : {Math.max(...balanceHistory.map(b => b.balance)).toLocaleString("fr-FR")} €</span>
            <button
              onClick={() => {
                const header = "run,label,solde_eur,decision,ir,ciz,dts,tsg";
                const rows = runHistory.slice().reverse().map((r, i) => [
                  i + 1,
                  `"${r.label.replace(/"/g, '""')}"`,
                  r.result.metrics.finalBalance.toFixed(2),
                  r.result.ticket.decision,
                  r.result.metrics.ir.toFixed(4),
                  r.result.metrics.ciz.toFixed(4),
                  r.result.metrics.dts.toFixed(4),
                  r.result.metrics.tsg.toFixed(4),
                ].join(","));
                const csv = [header, ...rows].join("\n");
                const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `bankworld_runs_${new Date().toISOString().slice(0,10)}.csv`;
                a.click();
                URL.revokeObjectURL(url);
              }}
              className="text-[9px] font-mono px-2 py-0.5 rounded border border-border hover:bg-muted transition-colors"
              style={{ color: "#a78bfa" }}
            >
              ⬇ CSV
            </button>
            <button
              onClick={async () => {
                if (!lastResult) return;
                const { jsPDF } = await import("jspdf");
                const doc = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });
                const now = new Date();
                const dateStr = now.toLocaleString("fr-FR");
                // En-tête
                doc.setFillColor(15, 15, 20);
                doc.rect(0, 0, 210, 40, "F");
                doc.setTextColor(245, 158, 11);
                doc.setFontSize(16);
                doc.setFont("helvetica", "bold");
                doc.text("RAPPORT DE SIMULATION BANCAIRE", 15, 18);
                doc.setTextColor(161, 161, 170);
                doc.setFontSize(9);
                doc.setFont("helvetica", "normal");
                doc.text(`OS4 — Obsidia Governance Platform — ${dateStr}`, 15, 26);
                doc.text(`Scénario : ${lastLabel}`, 15, 33);
                // Décision Guard
                const dec = lastResult.ticket.decision;
                const decColor: [number, number, number] = dec === "ALLOW" ? [34, 197, 94] : dec === "HOLD" ? [245, 158, 11] : [239, 68, 68];
                doc.setFillColor(...decColor);
                doc.roundedRect(155, 12, 45, 16, 3, 3, "F");
                doc.setTextColor(0, 0, 0);
                doc.setFontSize(12);
                doc.setFont("helvetica", "bold");
                doc.text(`GUARD : ${dec}`, 177.5, 22, { align: "center" });
                // Métriques IR/CIZ/DTS/TSG
                doc.setTextColor(255, 255, 255);
                doc.setFontSize(11);
                doc.setFont("helvetica", "bold");
                doc.text("MÉTRIQUES FONDAMENTALES", 15, 52);
                const metrics = [
                  { label: "IR — Taux de Rendement Interne", value: `${(lastResult.metrics.ir * 100).toFixed(2)}%`, color: lastResult.metrics.ir > 0 ? [34, 197, 94] : [239, 68, 68] },
                  { label: "CIZ — Intégrité du Capital", value: `${(lastResult.metrics.ciz * 100).toFixed(2)}%`, color: lastResult.metrics.ciz > 1 ? [34, 197, 94] : [245, 158, 11] },
                  { label: "DTS — Ratio Dettes/Épargne", value: `${(lastResult.metrics.dts * 100).toFixed(2)}%`, color: lastResult.metrics.dts < 1 ? [34, 197, 94] : [239, 68, 68] },
                  { label: "TSG — Écart Objectif Épargne", value: `${(lastResult.metrics.tsg * 100).toFixed(2)}%`, color: lastResult.metrics.tsg < 0.2 ? [34, 197, 94] : [245, 158, 11] },
                ];
                metrics.forEach((m, i) => {
                  const y = 62 + i * 14;
                  doc.setFillColor(30, 30, 40);
                  doc.roundedRect(15, y - 5, 180, 12, 2, 2, "F");
                  doc.setTextColor(161, 161, 170);
                  doc.setFontSize(9);
                  doc.setFont("helvetica", "normal");
                  doc.text(m.label, 20, y + 2);
                  doc.setTextColor(...(m.color as [number, number, number]));
                  doc.setFontSize(11);
                  doc.setFont("helvetica", "bold");
                  doc.text(m.value, 185, y + 2, { align: "right" });
                });
                // Statistiques supplémentaires
                doc.setTextColor(255, 255, 255);
                doc.setFontSize(11);
                doc.setFont("helvetica", "bold");
                doc.text("STATISTIQUES DE SIMULATION", 15, 126);
                const stats = [
                  ["Solde final", `${lastResult.metrics.finalBalance.toLocaleString("fr-FR")} €`],
                  ["Total dépôts", `${lastResult.metrics.totalDeposits.toLocaleString("fr-FR")} €`],
                  ["Total retraits", `${lastResult.metrics.totalWithdrawals.toLocaleString("fr-FR")} €`],
                  ["Fraudes détectées", `${lastResult.metrics.fraudCount}`],
                  ["Taux détection fraude", `${(lastResult.metrics.fraudDetectionRate * 100).toFixed(1)}%`],
                  ["Conformité réserve", `${(lastResult.metrics.reserveCompliance * 100).toFixed(1)}%`],
                  ["Objectif épargne", lastResult.metrics.savingsGoalMet ? "✓ Atteint" : "✗ Non atteint"],
                ];
                stats.forEach(([label, value], i) => {
                  const y = 136 + i * 10;
                  doc.setTextColor(161, 161, 170);
                  doc.setFontSize(9);
                  doc.setFont("helvetica", "normal");
                  doc.text(label, 20, y);
                  doc.setTextColor(220, 220, 220);
                  doc.setFont("helvetica", "bold");
                  doc.text(value, 185, y, { align: "right" });
                });
                // Section Guard X-108 — seuils et valeurs réelles
                doc.setTextColor(255, 255, 255);
                doc.setFontSize(11);
                doc.setFont("helvetica", "bold");
                doc.text("GUARD X-108 — ANALYSE DES SEUILS", 15, 212);
                const guardChecks = [
                  {
                    name: "CIZ — Intégrité capital",
                    value: lastResult.metrics.ciz,
                    threshold: 0.95,
                    direction: "min" as const,
                    display: `${(lastResult.metrics.ciz * 100).toFixed(1)}%`,
                    thresholdDisplay: "95%",
                  },
                  {
                    name: "DTS — Ratio dépenses/revenus",
                    value: lastResult.metrics.dts,
                    threshold: 0.90,
                    direction: "max" as const,
                    display: `${(lastResult.metrics.dts * 100).toFixed(1)}%`,
                    thresholdDisplay: "90%",
                  },
                  {
                    name: "IR — Rendement annualisé",
                    value: lastResult.metrics.ir,
                    threshold: -0.05,
                    direction: "min" as const,
                    display: `${(lastResult.metrics.ir * 100).toFixed(1)}%`,
                    thresholdDisplay: "-5%",
                  },
                  {
                    name: "FDR — Taux détection fraude",
                    value: lastResult.metrics.fraudDetectionRate,
                    threshold: 0.60,
                    direction: "min" as const,
                    display: `${(lastResult.metrics.fraudDetectionRate * 100).toFixed(1)}%`,
                    thresholdDisplay: "60%",
                  },
                ];
                guardChecks.forEach((check, i) => {
                  const y = 222 + i * 12;
                  const violated = check.direction === "min" ? check.value < check.threshold : check.value > check.threshold;
                  const statusColor: [number, number, number] = violated ? [239, 68, 68] : [34, 197, 94];
                  const status = violated ? "BLOCK" : "SAFE";
                  doc.setFillColor(20, 20, 30);
                  doc.roundedRect(15, y - 4, 180, 10, 1, 1, "F");
                  doc.setTextColor(161, 161, 170);
                  doc.setFontSize(8);
                  doc.setFont("helvetica", "normal");
                  doc.text(check.name, 20, y + 2);
                  doc.setTextColor(180, 180, 180);
                  doc.text(`valeur: ${check.display}  |  seuil: ${check.direction === "min" ? "≥" : "≤"} ${check.thresholdDisplay}`, 90, y + 2);
                  doc.setTextColor(...statusColor);
                  doc.setFont("helvetica", "bold");
                  doc.text(status, 185, y + 2, { align: "right" });
                });
                // Raisons textuelles du Guard
                if (lastResult.ticket.reasons.length > 0 && lastResult.ticket.reasons[0] !== "All checks passed") {
                  doc.setTextColor(239, 68, 68);
                  doc.setFontSize(9);
                  doc.setFont("helvetica", "bold");
                  doc.text("⚠️ Violations détectées :", 15, 278);
                  lastResult.ticket.reasons.slice(0, 3).forEach((reason, i) => {
                    doc.setTextColor(239, 100, 100);
                    doc.setFontSize(8);
                    doc.setFont("helvetica", "normal");
                    doc.text(`• ${reason}`, 20, 285 + i * 7);
                  });
                }
                // Explication LLM
                if (llmExplanation) {
                  doc.addPage();
                  doc.setFillColor(15, 15, 20);
                  doc.rect(0, 0, 210, 20, "F");
                  doc.setTextColor(245, 158, 11);
                  doc.setFontSize(12);
                  doc.setFont("helvetica", "bold");
                  doc.text("EXPLICATION LLM — ANALYSE OBSIDIA", 15, 14);
                  doc.setTextColor(200, 200, 200);
                  doc.setFontSize(9);
                  doc.setFont("helvetica", "normal");
                  const explanationLines = doc.splitTextToSize(llmExplanation, 180);
                  doc.text(explanationLines, 15, 30);
                }
                // Pied de page
                const pageCount = doc.getNumberOfPages();
                for (let p = 1; p <= pageCount; p++) {
                  doc.setPage(p);
                  doc.setTextColor(80, 80, 80);
                  doc.setFontSize(7);
                  doc.text(`OS4 Obsidia Governance Platform — Page ${p}/${pageCount} — ${dateStr}`, 105, 290, { align: "center" });
                }
                doc.save(`rapport_bank_${lastLabel.replace(/[^a-z0-9]/gi, "_").toLowerCase()}_${now.toISOString().slice(0,10)}.pdf`);
              }}
              disabled={!lastResult}
              className="text-[9px] font-mono px-2 py-0.5 rounded border border-border hover:bg-muted transition-colors disabled:opacity-40"
              style={{ color: "#f87171" }}
            >
              📄 PDF
            </button>
          </div>
        </div>
      )}

      {/* ─── Panneau Formules IR/CIZ/DTS/TSG ─── */}
      <div className="panel p-4">
        <button
          onClick={() => setShowFormulas((v) => !v)}
          className="w-full flex items-center justify-between text-xs font-mono font-bold"
          style={{ color: "#60a5fa" }}
        >
          <span>📊 COMMENT ÇA SE CALCULE ? — Formules IR / CIZ / DTS / TSG</span>
          <span>{showFormulas ? "▲ Masquer" : "▼ Afficher"}</span>
        </button>
        {showFormulas && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              {
                name: "IR — Taux de Rendement Interne",
                color: "#22c55e",
                formula: "IR = (Solde_final − Solde_initial) / Solde_initial",
                detail: "Rendement annualisé réel du compte sur la période simulée.",
                healthy: "IR > 0 = compte qui grandit",
                danger: "IR < −0.1 = perte significative",
                example: lastResult ? `Exemple : (${lastResult.metrics.finalBalance.toFixed(0)} − ${totalCapital.toFixed(0)}) / ${totalCapital.toFixed(0)} = ${(lastResult.metrics.ir * 100).toFixed(1)}%` : "Ex : (131 622 − 100 000) / 100 000 = +31.6%",
              },
              {
                name: "CIZ — Cohérence Intégrale du Capital",
                color: "#f59e0b",
                formula: "CIZ = Solde_final / Solde_initial",
                detail: "Ratio de conservation du capital. CIZ = 1.0 signifie capital intact, CIZ = 1.3 signifie +30%.",
                healthy: "CIZ > 1.0 = capital préservé",
                danger: "CIZ < 0.95 = capital a perdu > 5% → Guard BLOCK",
                example: lastResult ? `Exemple : ${lastResult.metrics.finalBalance.toFixed(0)} / ${totalCapital.toFixed(0)} = ${lastResult.metrics.ciz.toFixed(3)}` : "Ex : 131 622 / 100 000 = 1.316",
              },
              {
                name: "DTS — Ratio Dépenses / Revenus",
                color: "#a78bfa",
                formula: "DTS = Total_Retraits / Total_Dépôts",
                detail: "Mesure si les dépenses sont couvertes par les revenus. DTS = 0.7 = 70% des revenus dépensés.",
                healthy: "DTS < 1.0 = dépenses < revenus (sain)",
                danger: "DTS > 0.90 = dépenses > 90% des revenus → Guard BLOCK",
                example: lastResult ? `Exemple : ${lastResult.metrics.totalWithdrawals.toFixed(0)} / ${lastResult.metrics.totalDeposits.toFixed(0)} = ${lastResult.metrics.dts.toFixed(3)}` : "Ex : 70 000 / 100 000 = 0.700",
              },
              {
                name: "TSG — Écart Objectif Épargne",
                color: "#60a5fa",
                formula: "TSG = (Objectif − Solde_final) / Objectif",
                detail: "Mesure le chemin restant vers l'objectif d'épargne. TSG = 0 = objectif atteint.",
                healthy: "TSG < 0.2 = proche de l'objectif",
                danger: "TSG > 0.5 = loin de l'objectif → Guard HOLD",
                example: lastResult ? `Exemple : (${(totalCapital * 1.5).toFixed(0)} − ${lastResult.metrics.finalBalance.toFixed(0)}) / ${(totalCapital * 1.5).toFixed(0)} = ${(lastResult.metrics.tsg * 100).toFixed(1)}%` : "Ex : (150 000 − 131 622) / 150 000 = 12.3%",
              },
            ].map((f) => (
              <div
                key={f.name}
                className="p-3 rounded"
                style={{ background: "rgba(255,255,255,0.02)", border: `1px solid ${f.color}33` }}
              >
                <div className="text-xs font-mono font-bold mb-1" style={{ color: f.color }}>{f.name}</div>
                <div
                  className="text-[11px] font-mono p-2 rounded mb-2"
                  style={{ background: "rgba(0,0,0,0.3)", color: "#e5e7eb", fontFamily: "monospace" }}
                >
                  {f.formula}
                </div>
                <div className="text-[10px] text-muted-foreground mb-2">{f.detail}</div>
                <div className="grid grid-cols-2 gap-1 mb-2">
                  <div className="text-[9px] p-1 rounded" style={{ background: "rgba(34,197,94,0.08)", color: "#22c55e" }}>
                    ✅ {f.healthy}
                  </div>
                  <div className="text-[9px] p-1 rounded" style={{ background: "rgba(239,68,68,0.08)", color: "#ef4444" }}>
                    ⚠️ {f.danger}
                  </div>
                </div>
                <div className="text-[9px] font-mono italic" style={{ color: "#6b7280" }}>{f.example}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ─── Comparateur TypeScript vs Python ─── */}
      {lastResult && (
        <div className="panel p-4">
          <button
            onClick={() => {
              setShowComparator((v) => !v);
              if (!showComparator && !pythonResult && !pythonLoading) {
                // Reconstruire les params depuis le dernier run
                const params: BankParams = {
                  seed: 42,
                  steps: 90,
                  initialBalance: totalCapital,
                  mu: 0.02,
                  sigma: 0.5,
                  fraudRate: 0.02,
                  fraudAmount: 500,
                  interestRate: 0.03,
                  savingsGoal: totalCapital * 1.5,
                  reserveRatio: 0.1,
                };
                runPythonEngine(params);
              }
            }}
            className="w-full flex items-center justify-between text-xs font-mono font-bold"
            style={{ color: "oklch(0.65 0.18 220)" }}
          >
            <span>⚖️ COMPARATEUR — Moteur TypeScript vs Moteur Python</span>
            <span>{showComparator ? "▲ Masquer" : "▼ Afficher"}</span>
          </button>
          {showComparator && (
            <div className="mt-4">
              <p className="text-[10px] text-muted-foreground mb-4">
                Les deux moteurs reçoivent les mêmes paramètres. Le moteur TypeScript (OS4 bankEngine) utilise un modèle log-normal + détection fraude.
                Le moteur Python (Obsidia-lab-trad) utilise OS0/OS1/OS2 avec le Guard X-108 original.
              </p>
              <div className="grid grid-cols-2 gap-4">
                {/* Moteur TypeScript */}
                <div className="p-3 rounded" style={{ background: "rgba(245,158,11,0.06)", border: "1px solid rgba(245,158,11,0.3)" }}>
                  <div className="text-[9px] font-mono uppercase tracking-widest mb-2" style={{ color: "#f59e0b" }}>🟡 Moteur TypeScript — bankEngine.ts</div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs font-mono font-bold" style={{ color: lastResult.ticket.decision === "ALLOW" ? "#22c55e" : lastResult.ticket.decision === "HOLD" ? "#f59e0b" : "#ef4444" }}>
                      {lastResult.ticket.decision}
                    </span>
                    <span className="text-[9px] text-muted-foreground">décision</span>
                  </div>
                  <div className="grid grid-cols-2 gap-1 mb-2">
                    {[
                      { k: "IR", v: `${(lastResult.metrics.ir * 100).toFixed(1)}%` },
                      { k: "CIZ", v: lastResult.metrics.ciz.toFixed(3) },
                      { k: "DTS", v: lastResult.metrics.dts.toFixed(3) },
                      { k: "TSG", v: `${(lastResult.metrics.tsg * 100).toFixed(1)}%` },
                    ].map(m => (
                      <div key={m.k} className="text-center p-1 rounded" style={{ background: "rgba(0,0,0,0.2)" }}>
                        <div className="text-[8px] text-muted-foreground">{m.k}</div>
                        <div className="text-[10px] font-mono font-bold text-foreground">{m.v}</div>
                      </div>
                    ))}
                  </div>
                  <div className="space-y-0.5">
                    {lastResult.ticket.reasons.slice(0, 3).map((r, i) => (
                      <div key={i} className="text-[9px] text-muted-foreground">• {r}</div>
                    ))}
                  </div>
                </div>

                {/* Moteur Python */}
                <div className="p-3 rounded" style={{ background: "rgba(96,165,250,0.06)", border: "1px solid rgba(96,165,250,0.3)" }}>
                  <div className="text-[9px] font-mono uppercase tracking-widest mb-2" style={{ color: "oklch(0.65 0.18 220)" }}>🔵 Moteur Python — OS0/OS1/OS2</div>
                  {pythonLoading ? (
                    <div className="text-[10px] text-muted-foreground italic">⏳ Appel au moteur Python...</div>
                  ) : pythonError ? (
                    <div>
                      <div className="text-[10px] text-red-400 mb-2">⚠️ {pythonError}</div>
                      <div className="text-[9px] text-muted-foreground">Le moteur Python nécessite que le serveur Obsidia-lab-trad soit démarré localement (port 3001).</div>
                      <button
                        onClick={() => {
                          const params: BankParams = { seed: 42, steps: 90, initialBalance: totalCapital, mu: 0.02, sigma: 0.5, fraudRate: 0.02, fraudAmount: 500, interestRate: 0.03, savingsGoal: totalCapital * 1.5, reserveRatio: 0.1 };
                          runPythonEngine(params);
                        }}
                        className="mt-2 text-[9px] font-mono px-2 py-1 rounded border border-blue-400/30 text-blue-400 hover:bg-blue-400/10"
                      >
                        ↺ Réessayer
                      </button>
                    </div>
                  ) : pythonResult ? (
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-mono font-bold" style={{ color: pythonResult.decision === "ACT" || pythonResult.decision === "ALLOW" ? "#22c55e" : pythonResult.decision === "HOLD" ? "#f59e0b" : "#ef4444" }}>
                          {pythonResult.decision}
                        </span>
                        <span className="text-[9px] text-muted-foreground">décision</span>
                        {/* Badge accord/désaccord */}
                        {(() => {
                          const tsDecision = lastResult.ticket.decision;
                          const pyDecision = pythonResult.decision === "ACT" ? "ALLOW" : pythonResult.decision;
                          const agree = tsDecision === pyDecision;
                          return (
                            <span className="ml-auto text-[8px] font-mono px-1.5 py-0.5 rounded" style={{ background: agree ? "rgba(34,197,94,0.15)" : "rgba(239,68,68,0.15)", color: agree ? "#22c55e" : "#ef4444" }}>
                              {agree ? "✓ ACCORD" : "⚡ DÉSACCORD"}
                            </span>
                          );
                        })()}
                      </div>
                      {pythonResult.metrics && (
                        <div className="grid grid-cols-2 gap-1 mb-2">
                          {Object.entries(pythonResult.metrics).slice(0, 4).map(([k, v]) => (
                            <div key={k} className="text-center p-1 rounded" style={{ background: "rgba(0,0,0,0.2)" }}>
                              <div className="text-[8px] text-muted-foreground">{k}</div>
                              <div className="text-[10px] font-mono font-bold text-foreground">{typeof v === "number" ? v.toFixed(3) : v}</div>
                            </div>
                          ))}
                        </div>
                      )}
                      <div className="space-y-0.5">
                        {(pythonResult.reasons ?? []).slice(0, 3).map((r, i) => (
                          <div key={i} className="text-[9px] text-muted-foreground">• {r}</div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => {
                        const params: BankParams = { seed: 42, steps: 90, initialBalance: totalCapital, mu: 0.02, sigma: 0.5, fraudRate: 0.02, fraudAmount: 500, interestRate: 0.03, savingsGoal: totalCapital * 1.5, reserveRatio: 0.1 };
                        runPythonEngine(params);
                      }}
                      className="text-[10px] font-mono px-3 py-2 rounded border transition-colors w-full"
                      style={{ borderColor: "oklch(0.65 0.18 220 / 0.4)", color: "oklch(0.65 0.18 220)" }}
                    >
                      ▶ Interroger le moteur Python
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ─── Mode Story Crise Bancaire ─── */}
      {bankStoryActive && (
        <div
          style={{
            position: "fixed", inset: 0, zIndex: 50,
            background: "rgba(0,0,0,0.85)",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}
        >
          <div
            className="panel p-6 flex flex-col gap-5"
            style={{ width: "min(700px, 95vw)", maxHeight: "85vh", overflowY: "auto" }}
          >
            <div className="flex items-center justify-between">
              <div className="text-xs font-mono font-bold" style={{ color: "#f59e0b" }}>
                🏦 MODE STORY — CRISE BANCAIRE
              </div>
              <button
                onClick={() => setBankStoryActive(false)}
                className="text-zinc-500 hover:text-zinc-200 text-lg font-bold"
              >
                ×
              </button>
            </div>

            {/* Barre de progression */}
            <div className="flex gap-2">
              {BANK_STORY_STEPS.map((s, i) => (
                <div
                  key={i}
                  className="flex-1 h-1 rounded-full"
                  style={{
                    background: i < bankStoryResults.length ? "#4ade80"
                      : i === bankStoryStep && bankStoryRunning ? "#f59e0b"
                      : "rgba(255,255,255,0.1)",
                  }}
                />
              ))}
            </div>

            {/* Étape en cours */}
            {bankStoryRunning && bankStoryResults.length < BANK_STORY_STEPS.length && (
              <div className="text-center py-4">
                <div className="text-2xl mb-2">{BANK_STORY_STEPS[bankStoryStep]?.icon}</div>
                <div className="text-sm font-mono font-bold text-zinc-200">{BANK_STORY_STEPS[bankStoryStep]?.title}</div>
                <div className="text-xs text-zinc-500 mt-1">{BANK_STORY_STEPS[bankStoryStep]?.desc}</div>
                <div className="text-[10px] text-zinc-600 mt-2 animate-pulse">Simulation en cours…</div>
              </div>
            )}

            {/* Résultats des étapes terminées */}
            {bankStoryResults.map((r, i) => {
              const dec = r.result.ticket.decision;
              const decColor = dec === "ALLOW" ? "#4ade80" : dec === "HOLD" ? "#f59e0b" : "#ef4444";
              return (
                <div
                  key={i}
                  className="p-3 rounded"
                  style={{ background: `${decColor}08`, border: `1px solid ${decColor}25` }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-xs font-mono font-bold text-zinc-200">
                      {BANK_STORY_STEPS[i]?.icon} {r.label}
                    </div>
                    <span
                      className="text-[9px] font-mono font-bold px-2 py-0.5 rounded"
                      style={{ background: `${decColor}20`, color: decColor }}
                    >
                      {dec}
                    </span>
                  </div>
                  <div className="grid grid-cols-4 gap-2 mb-2">
                    {[
                      { label: "IR", value: `${(r.result.metrics.ir * 100).toFixed(1)}%`, color: r.result.metrics.ir > 0 ? "#4ade80" : "#ef4444" },
                      { label: "CIZ", value: `${(r.result.metrics.ciz * 100).toFixed(1)}%`, color: r.result.metrics.ciz > 1 ? "#4ade80" : "#f59e0b" },
                      { label: "DTS", value: `${(r.result.metrics.dts * 100).toFixed(1)}%`, color: r.result.metrics.dts < 1 ? "#4ade80" : "#ef4444" },
                      { label: "TSG", value: `${(r.result.metrics.tsg * 100).toFixed(1)}%`, color: r.result.metrics.tsg < 0.2 ? "#4ade80" : "#f59e0b" },
                    ].map(m => (
                      <div key={m.label} className="text-center">
                        <div className="text-[8px] text-zinc-600 uppercase">{m.label}</div>
                        <div className="text-xs font-mono font-bold" style={{ color: m.color }}>{m.value}</div>
                      </div>
                    ))}
                  </div>
                  {r.explanation && (
                    <div className="text-[10px] text-zinc-400 leading-relaxed border-t border-zinc-800 pt-2">
                      {r.explanation.slice(0, 300)}{r.explanation.length > 300 ? "…" : ""}
                    </div>
                  )}
                </div>
              );
            })}

            {/* Bilan final */}
            {!bankStoryRunning && bankStoryResults.length === BANK_STORY_STEPS.length && (
              <div className="p-3 rounded text-center" style={{ background: "rgba(74,222,128,0.06)", border: "1px solid rgba(74,222,128,0.2)" }}>
                <div className="text-xs font-mono font-bold text-emerald-400 mb-1">✅ CRISE BANCAIRE SIMULÉE</div>
                <div className="text-[10px] text-zinc-400">
                  5 étapes complètes — Guard X-108 a protégé le capital lors de la crise systémique.
                  Pertes évitées : {(
                    bankStoryResults[3]?.result.metrics.finalBalance
                      ? Math.abs(bankStoryResults[3].result.metrics.finalBalance - totalCapital).toLocaleString("fr-FR")
                      : "—"
                  )} €
                </div>
              </div>
            )}

            {/* Boutons */}
            <div className="flex gap-3 justify-center">
              {!bankStoryRunning && bankStoryResults.length === 0 && (
                <button
                  onClick={runBankStory}
                  className="text-xs font-mono px-4 py-2 rounded font-bold"
                  style={{ background: "rgba(245,158,11,0.2)", color: "#f59e0b", border: "1px solid rgba(245,158,11,0.4)" }}
                >
                  ▶ Lancer la simulation
                </button>
              )}
              {!bankStoryRunning && bankStoryResults.length > 0 && (
                <button
                  onClick={runBankStory}
                  className="text-xs font-mono px-3 py-1.5 rounded"
                  style={{ background: "rgba(255,255,255,0.05)", color: "#a1a1aa", border: "1px solid rgba(255,255,255,0.1)" }}
                >
                  🔄 Rejouer
                </button>
              )}
              <button
                onClick={() => setBankStoryActive(false)}
                className="text-xs font-mono px-3 py-1.5 rounded"
                style={{ background: "rgba(255,255,255,0.05)", color: "#a1a1aa", border: "1px solid rgba(255,255,255,0.1)" }}
              >
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ─── Market Explanation ─── */}
      <MarketExplanation domain="bank" />

      {/* ─── Causal Pipeline ─── */}
      <CausalPipeline domain={"BANK" as PipelineDomain} />

      {/* ── BLOC 4 : Pilotage ── */}
      <PilotagePanel
        domain="bank"
        onRerun={() => lastLabel ? runSimulation(lastLabel, {}) : undefined}
        onReset={() => { setLastResult(null); setCanonicalEnvelope(null); setCanonicalVerify(null); }}
        loading={isLoading}
        pythonAvailable={(canonicalAttestation.data as any)?.merkle_root ? true : canonicalAttestation.isLoading ? undefined : false}
        mode={canonicalEnvelope?.source === "python" ? "real" : canonicalEnvelope ? "fallback" : undefined}
      />
      {/* ── BLOC 5 : Projection futur ── */}
      <ProjectionPanel
        domain="bank"
        horizon="24h"
        scenarios={lastResult?.ticket?.decision === "BLOCK" ? [
          { label: "Restructuration nécessaire", probability: 0.60, outcome: "degradation", description: "CIZ < seuil — révision des limites de retrait" },
          { label: "Injection de liquidités", probability: 0.30, outcome: "recovery", description: "Recapitalisation d'urgence possible" },
          { label: "Statu quo", probability: 0.10, outcome: "neutral", description: "Gel temporaire des opérations" },
        ] : undefined}
      />
      {/* ─── Canonical Real Panel (backend canonique) ─── */}
      {(canonicalEnvelope || decisionEnvelopeMut.isPending) && (
        <div className="mt-4">
          <CanonicalRealPanel
            title="BANK WORLD — DÉCISION CANONIQUE X-108"
            payload={canonicalEnvelope}
            loading={decisionEnvelopeMut.isPending}
          />
          <CanonicalProofPanel
            verify={canonicalVerify}
            attestation={canonicalAttestation.data}
          />
        </div>
      )}

      {/* ─── Engine Block ─── */}
      <EngineBlock
        domain="bank"
        amount={lastResult ? lastResult.metrics.finalBalance : 100000}
        irreversible={lastResult ? lastResult.ticket.decision === "BLOCK" : false}
        coherence={lastResult ? lastResult.metrics.ciz : 0.72}
        volatility={lastResult ? Math.max(0, 1 - lastResult.metrics.ciz) : 0.18}
        timeElapsed={12}
        tau={10}
        label={lastLabel || "SIMULATION BANCAIRE — GUARD X-108"}
      />

      {/* ─── SECTION CANONIQUE — 5 blocs ─── */}
      <div className="mt-8 border-t pt-6" style={{ borderColor: "oklch(0.20 0.01 240)" }}>
        <div className="text-[10px] font-mono uppercase tracking-widest mb-4" style={{ color: "oklch(0.40 0.01 240)" }}>Vue canonique — pipeline complet</div>
        <WorldPageTemplate
          domain="bank"
          title="Bank World — Vue Canonique"
          description="Pipeline complet : Situation → Constellation agentique → Agrégation → Souveraineté X-108 → Preuve"
          kpis={[
            { label: "Solde final", value: lastResult ? lastResult.metrics.finalBalance.toLocaleString("fr-FR") + " €" : "En attente", color: "oklch(0.72 0.18 145)" },
            { label: "CIZ", value: lastResult ? (lastResult.metrics.ciz * 100).toFixed(1) + "%" : "En attente", color: lastResult && lastResult.metrics.ciz >= 0.7 ? "oklch(0.72 0.18 145)" : "oklch(0.65 0.25 25)" },
            { label: "Décision", value: lastResult ? lastResult.ticket.decision : "En attente", color: lastResult?.ticket.decision === "BLOCK" ? "oklch(0.65 0.25 25)" : lastResult?.ticket.decision === "HOLD" ? "oklch(0.72 0.18 45)" : "oklch(0.72 0.18 145)" },
            { label: "Fraudes", value: lastResult ? String(lastResult.metrics.fraudCount ?? 0) : "0", color: "oklch(0.65 0.25 25)" },
          ]}
          domainContentSlot={
            lastResult ? (
              <div className="grid grid-cols-3 gap-3 text-[11px]">
                <div className="rounded p-2" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
                  <div className="text-muted-foreground mb-1">IR (Rendement)</div>
                  <div className="font-mono font-bold" style={{ color: "oklch(0.72 0.18 145)" }}>{(lastResult.metrics.ir * 100).toFixed(1)}%</div>
                </div>
                <div className="rounded p-2" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
                  <div className="text-muted-foreground mb-1">DTS (Dettes/Épargne)</div>
                  <div className="font-mono font-bold" style={{ color: lastResult.metrics.dts > 1 ? "oklch(0.65 0.25 25)" : "oklch(0.72 0.18 45)" }}>{(lastResult.metrics.dts * 100).toFixed(1)}%</div>
                </div>
                <div className="rounded p-2" style={{ background: "oklch(0.12 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
                  <div className="text-muted-foreground mb-1">TSG (Écart objectif)</div>
                  <div className="font-mono font-bold" style={{ color: lastResult.metrics.tsg > 0.3 ? "oklch(0.65 0.25 25)" : "oklch(0.72 0.18 145)" }}>{(lastResult.metrics.tsg * 100).toFixed(1)}%</div>
                </div>
              </div>
            ) : undefined
          }
        />
      </div>
    </div>
  );
}
