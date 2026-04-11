import { Link } from "wouter";
import React, { useState, useEffect, useRef, useCallback } from "react";
import { trpc } from "@/lib/trpc";
import BarreMetriques from "@/components/BarreMetriques";
import { ModeBadgeBar } from "@/components/ModeBadge";

// ─── Constantes ───────────────────────────────────────────────────────────────

const REPO = "https://github.com/Eaubin08/Obsidia-lab-trad";

// ─── Démo 30s — Scénario Flash Crash ─────────────────────────────────────────

interface DemoStep {
  phase: "world" | "agent" | "guard" | "decision" | "proof";
  icon: string;
  label: string;
  detail: string;
  value?: string;
  valueColor?: string;
  duration: number;
}

const DEMO_STEPS: DemoStep[] = [
  {
    phase: "world",
    icon: "🌍",
    label: "Le marché s'effondre",
    detail: "BTC/USD chute de −18,4 % en 3 minutes. La volatilité explose à 34,2 %. Le marché est en état de choc.",
    value: "KRACH ÉCLAIR DÉTECTÉ",
    valueColor: "#f87171",
    duration: 5000,
  },
  {
    phase: "agent",
    icon: "🤖",
    label: "L'agent propose de tout vendre",
    detail: "L'agent de trading propose : VENDRE 100 % de la position BTC immédiatement. Capital en jeu : 125 000 €.",
    value: "VENDRE 100 % BTC — 125 000 €",
    valueColor: "#fbbf24",
    duration: 5000,
  },
  {
    phase: "guard",
    icon: "🛡",
    label: "Guard X-108 évalue le risque",
    detail: "Cohérence 0,12 < seuil 0,30. Invariant violé : schéma de krach détecté. Verrou temporel τ=10s activé.",
    value: "COHÉRENCE 0,12 — SOUS LE SEUIL",
    valueColor: "#f87171",
    duration: 6000,
  },
  {
    phase: "decision",
    icon: "⚡",
    label: "Action bloquée",
    detail: "Guard X-108 émet un BLOC. L'action irréversible est refusée. Capital protégé : 125 000 €.",
    value: "BLOQUÉ",
    valueColor: "#f87171",
    duration: 6000,
  },
  {
    phase: "proof",
    icon: "🔗",
    label: "Preuve cryptographique enregistrée",
    detail: "Hash de décision : b9ac7a04. Racine Merkle mise à jour. Horodatage RFC 3161 ancré. Piste d'audit complète.",
    value: "INTÉGRITÉ : VÉRIFIÉE",
    valueColor: "#4ade80",
    duration: 5000,
  },
  {
    phase: "proof",
    icon: "✅",
    label: "Résultat final",
    detail: "Scénario Flash Crash terminé. Guard X-108 a bloqué 1 action irréversible.",
    value: "CAPITAL PROTÉGÉ : 125 000 €",
    valueColor: "#4ade80",
    duration: 3000,
  },
];

// ─── Pipeline ─────────────────────────────────────────────────────────────────

const PIPELINE = [
  {
    id: "market", icon: "🌍", label: "Marché", sub: "Événements en temps réel",
    color: "#60a5fa", href: "/simuler",
    explication: "Le monde réel : cours du Bitcoin, transactions bancaires, trafic e-commerce. Tout ce qui peut déclencher une action.",
  },
  {
    id: "agent", icon: "🤖", label: "Agent", sub: "Observe et propose",
    color: "#fbbf24", href: "/controle",
    explication: "Un programme autonome qui surveille le marché et propose des actions (acheter, vendre, valider un virement…).",
  },
  {
    id: "guard", icon: "🛡", label: "Guard X-108", sub: "Le juge de chaque action",
    color: "oklch(0.72 0.18 145)", href: "/decision", highlight: true,
    explication: "Le cœur d'Obsidia. Il évalue chaque proposition selon des règles mathématiques prouvées. Aucune action ne passe sans son accord.",
  },
  {
    id: "decision", icon: "⚡", label: "Décision", sub: "Autoriser / Attendre / Bloquer",
    color: "#a78bfa", href: "/decision",
    explication: "Trois verdicts possibles : ALLOW (exécuter), HOLD (attendre 10 secondes), BLOCK (refuser définitivement).",
  },
  {
    id: "proof", icon: "🔗", label: "Preuve", sub: "Chaque décision est tracée",
    color: "#34d399", href: "/preuves",
    explication: "Chaque décision est signée cryptographiquement et enregistrée. Impossible à modifier ou effacer après coup.",
  },
];

// ─── Roadmap condensée ────────────────────────────────────────────────────────

const ROADMAP_PHASES = [
  {
    num: "1–14", title: "Moteur de base", status: "done",
    desc: "Guard X-108, verrou temporel τ=10s, chaîne Merkle, reproductibilité déterministe.",
  },
  {
    num: "18–24", title: "Preuves formelles", status: "done",
    desc: "33 théorèmes Lean 4, 7 invariants TLA+, 473 tests adversariaux, ancrage RFC 3161.",
  },
  {
    num: "28", title: "X108 STD v1.0 — Actuel", status: "current",
    desc: "Démonstrateur complet : moteur visible, preuves formelles, export audit, 3 domaines.",
  },
  {
    num: "32", title: "Coordination multi-agents", status: "next",
    desc: "Consensus inter-domaine, propagation des décisions entre agents spécialisés.",
  },
  {
    num: "36", title: "Ancrage on-chain", status: "next",
    desc: "Smart contract Ethereum — auditabilité publique et immuable sur la blockchain.",
  },
];

// ─── Composant ────────────────────────────────────────────────────────────────

export default function OS4Home() {
  const [demoActive, setDemoActive] = useState(false);
  const [demoStep, setDemoStep] = useState(0);
  const [demoProgress, setDemoProgress] = useState(0);
  const [demoComplete, setDemoComplete] = useState(false);
  const [pipelineActive, setPipelineActive] = useState(-1);
  const [pipelineHover, setPipelineHover] = useState<number | null>(null);
  const demoTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const demoProgressRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const pipelineTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Métriques globales — polling toutes les 5s
  const { data: tradingHist } = trpc.trading.history.useQuery({ limit: 50 }, { refetchInterval: 5000 });
  const { data: bankHist }    = trpc.bank.history.useQuery({ limit: 50 }, { refetchInterval: 5000 });
  const { data: ecomHist }    = trpc.ecom.history.useQuery({ limit: 50 }, { refetchInterval: 5000 });

  const allTickets = [...(tradingHist ?? []), ...(bankHist ?? []), ...(ecomHist ?? [])];
  const totalDecisions = allTickets.length;
  const totalBlocks = allTickets.filter(t => t.decision === "BLOCK").length;
  const tauxBlocage = totalDecisions > 0 ? totalBlocks / totalDecisions : 0;
  const capitalProtege = totalBlocks * 100_000 * 0.08;

  // Animation pipeline
  useEffect(() => {
    pipelineTimerRef.current = setInterval(() => {
      setPipelineActive(prev => (prev + 1) % PIPELINE.length);
    }, 1400);
    return () => { if (pipelineTimerRef.current) clearInterval(pipelineTimerRef.current); };
  }, []);

  const runDemo = useCallback(() => {
    setDemoActive(true);
    setDemoStep(0);
    setDemoProgress(0);
    setDemoComplete(false);
    let currentStep = 0;
    const advanceStep = () => {
      if (currentStep >= DEMO_STEPS.length) {
        setDemoComplete(true);
        setDemoActive(false);
        return;
      }
      setDemoStep(currentStep);
      setDemoProgress(0);
      const step = DEMO_STEPS[currentStep];
      const startTime = Date.now();
      if (demoProgressRef.current) clearInterval(demoProgressRef.current);
      demoProgressRef.current = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const pct = Math.min(100, (elapsed / step.duration) * 100);
        setDemoProgress(pct);
        if (pct >= 100 && demoProgressRef.current) clearInterval(demoProgressRef.current);
      }, 50);
      currentStep++;
      demoTimerRef.current = setTimeout(advanceStep, step.duration);
    };
    advanceStep();
  }, []);

  const stopDemo = useCallback(() => {
    if (demoTimerRef.current) clearTimeout(demoTimerRef.current);
    if (demoProgressRef.current) clearInterval(demoProgressRef.current);
    setDemoActive(false);
    setDemoComplete(false);
    setDemoStep(0);
    setDemoProgress(0);
  }, []);

  useEffect(() => {
    return () => {
      if (demoTimerRef.current) clearTimeout(demoTimerRef.current);
      if (demoProgressRef.current) clearInterval(demoProgressRef.current);
      if (pipelineTimerRef.current) clearInterval(pipelineTimerRef.current);
    };
  }, []);

  // Statut Python live
  const pythonStatusQuery = trpc.engine.pythonStatus.useQuery(undefined, { refetchInterval: 15000 });
  const pythonStatus = pythonStatusQuery.data as any;

  const currentDemoStep = DEMO_STEPS[demoStep] ?? DEMO_STEPS[DEMO_STEPS.length - 1];
  const activePipelineStep = pipelineHover !== null ? pipelineHover : pipelineActive;

  return (
    <div className="flex flex-col gap-0 max-w-5xl mx-auto">

      {/* ─── Bandeau opératoire ───────────────────────────────────────────────────────────────── */}
      <ModeBadgeBar
        mode={pythonStatus?.pythonOnline ? "LIVE" : totalDecisions > 0 ? "SIMU" : "DEMO"}
        detail={pythonStatus?.pythonOnline
          ? `Guard X-108 actif · ${pythonStatus.totalDecisions ?? 0} décisions en DB`
          : totalDecisions > 0
          ? `${totalDecisions} décisions enregistrées — moteur Python hors ligne`
          : "Aucune décision enregistrée — lancer une simulation"}
        right={pythonStatus?.lastDecision
          ? `dernier : ${pythonStatus.lastDecision} · ${pythonStatus.lastDomain ?? "—"}`
          : undefined}
      />

      {/* ═══════════════════════════════════════════════════════════════════════
          SECTION 1 — HERO
      ═══════════════════════════════════════════════════════════════════════ */}
      <section className="flex flex-col items-center text-center pt-12 pb-10 gap-5 px-4">
        <div className="text-[9px] font-mono tracking-[0.4em] uppercase" style={{ color: "oklch(0.72 0.18 145)" }}>
          Obsidia Labs — OS4
        </div>

        <h1 className="font-mono font-bold text-4xl md:text-5xl leading-tight text-foreground max-w-2xl">
          Obsidia protège les<br />
          <span style={{ color: "oklch(0.72 0.18 145)" }}>décisions autonomes</span>
        </h1>

        <p className="font-mono text-sm max-w-xl leading-relaxed" style={{ color: "oklch(0.60 0.01 240)" }}>
          Chaque action proposée par un agent est évaluée, validée et enregistrée<br />
          avant d'être exécutée. Aucune action irréversible ne passe sans accord.
        </p>

        {/* Badges de confiance */}
        <div className="flex flex-wrap justify-center gap-2 mt-1">
          {[
            "✓ Décisions traçables",
            "✓ Preuves vérifiables",
            "✓ Historique infalsifiable",
            "✓ Blocage automatique des risques",
          ].map(badge => (
            <span key={badge} className="text-[10px] font-mono px-2.5 py-1 rounded"
              style={{ background: "oklch(0.72 0.18 145 / 0.08)", color: "oklch(0.72 0.18 145)", border: "1px solid oklch(0.72 0.18 145 / 0.25)" }}>
              {badge}
            </span>
          ))}
        </div>

        {/* CTAs */}
        <div className="flex gap-3 mt-2 flex-wrap justify-center">
          <button
            onClick={runDemo}
            className="px-6 py-2.5 rounded font-mono text-sm font-bold"
            style={{ background: "oklch(0.72 0.18 145)", color: "oklch(0.10 0.01 240)" }}
          >
            ▶ Voir en 30 secondes
          </button>
          <Link href="/simuler" className="px-6 py-2.5 rounded font-mono text-sm font-bold"
            style={{ background: "oklch(0.60 0.12 200 / 0.15)", color: "oklch(0.60 0.12 200)", border: "1px solid oklch(0.60 0.12 200 / 0.5)" }}>
            Lancer une simulation →
          </Link>
          <Link href="/decision" className="px-6 py-2.5 rounded font-mono text-sm font-bold border"
            style={{ background: "transparent", color: "oklch(0.72 0.18 145)", borderColor: "oklch(0.72 0.18 145 / 0.5)" }}>
            Voir les décisions live →
          </Link>
        </div>
      </section>

      {/* Barre de métriques globales */}
      <div className="px-4 pb-4">
        <BarreMetriques
          live={totalDecisions > 0}
          accent="oklch(0.72 0.18 145)"
          refreshMs={5000}
          metriques={[
            { label: "Décisions traitées", valeur: totalDecisions > 0 ? totalDecisions.toString() : "—", couleur: "oklch(0.72 0.18 145)", info: "Total des décisions Guard X-108 enregistrées" },
            { label: "Taux de blocage",    valeur: totalDecisions > 0 ? `${(tauxBlocage * 100).toFixed(1)} %` : "—", couleur: tauxBlocage > 0.3 ? "#f87171" : "#4ade80", info: "Pourcentage d'actions bloquées par Guard" },
            { label: "Capital protégé",   valeur: capitalProtege > 0 ? (capitalProtege >= 1_000_000 ? `€${(capitalProtege/1_000_000).toFixed(1)}M` : `€${(capitalProtege/1_000).toFixed(0)}k`) : "—", couleur: "oklch(0.72 0.18 145)", info: "Estimation du capital protégé par les blocages" },
            { label: "Domaines actifs",   valeur: [(tradingHist?.length ?? 0) > 0 ? "Trading" : null, (bankHist?.length ?? 0) > 0 ? "Banque" : null, (ecomHist?.length ?? 0) > 0 ? "E-Com" : null].filter(Boolean).join(" · ") || "—", couleur: "oklch(0.60 0.12 200)", info: "Domaines ayant des simulations enregistrées" },
          ]}
        />
      </div>

      {/* ═══════════════════════════════════════════════════════════════════════
          SECTION 1b — PILOTER (3 BLOCS D’ACTION DIRECTE)
      ═══════════════════════════════════════════════════════════════════════ */}
      <section className="px-4 py-6" style={{ background: "oklch(0.10 0.01 240)", borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
        <div className="max-w-3xl mx-auto">
          <div className="text-[9px] font-mono tracking-[0.3em] uppercase mb-4" style={{ color: "oklch(0.72 0.18 145)" }}>
            Piloter maintenant
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">

            {/* Bloc 1 — Lancer un run */}
            <Link href="/simuler?domain=trading&scenarioId=flash_crash&rerun=1"
              className="flex flex-col gap-2 p-4 rounded cursor-pointer"
              style={{ background: "oklch(0.72 0.18 145 / 0.07)", border: "1px solid oklch(0.72 0.18 145 / 0.35)" }}>
              <div className="flex items-center gap-2">
                <span className="text-lg">▶</span>
                <span className="font-mono text-xs font-bold" style={{ color: "oklch(0.72 0.18 145)" }}>Lancer un run</span>
              </div>
              <div className="text-[10px] leading-relaxed" style={{ color: "oklch(0.55 0.01 240)" }}>
                Stress Lab prérempli — Flash Crash trading, mode gouverné, seed reproductible
              </div>
              <div className="text-[9px] font-mono mt-auto" style={{ color: "oklch(0.45 0.01 240)" }}>
                /simuler · Stress Lab
              </div>
            </Link>

            {/* Bloc 2 — Décisions live */}
            <Link href="/decision"
              className="flex flex-col gap-2 p-4 rounded cursor-pointer"
              style={{ background: "oklch(0.60 0.12 200 / 0.07)", border: "1px solid oklch(0.60 0.12 200 / 0.35)" }}>
              <div className="flex items-center gap-2">
                <span className="text-lg">⚡</span>
                <span className="font-mono text-xs font-bold" style={{ color: "oklch(0.60 0.12 200)" }}>Décisions live</span>
              </div>
              <div className="text-[10px] leading-relaxed" style={{ color: "oklch(0.55 0.01 240)" }}>
                Flux Guard X-108 en temps réel — {totalDecisions > 0 ? `${totalDecisions} décisions enregistrées` : "aucune décision encore"}
              </div>
              <div className="text-[9px] font-mono mt-auto" style={{ color: "oklch(0.45 0.01 240)" }}>
                /decision · WebSocket Guard
              </div>
            </Link>

            {/* Bloc 3 — Mission Control */}
            <Link href="/controle"
              className="flex flex-col gap-2 p-4 rounded cursor-pointer"
              style={{ background: "oklch(0.65 0.18 240 / 0.07)", border: "1px solid oklch(0.65 0.18 240 / 0.35)" }}>
              <div className="flex items-center gap-2">
                <span className="text-lg">🛡️</span>
                <span className="font-mono text-xs font-bold" style={{ color: "oklch(0.65 0.18 240)" }}>Mission Control</span>
              </div>
              <div className="text-[10px] leading-relaxed" style={{ color: "oklch(0.55 0.01 240)" }}>
                Tour de commandement — health, incidents, filtres, deep-links vers Simuler
              </div>
              <div className="text-[9px] font-mono mt-auto" style={{ color: "oklch(0.45 0.01 240)" }}>
                /controle · Mission Control
              </div>
            </Link>

          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════════
          SECTION 2 — PIPELINE ANIMÉ AVEC EXPLICATIONS
      ═══════════════════════════════════════════════════════════════════════ */}
      <section className="px-4 py-8" style={{ background: "oklch(0.08 0.01 240)", borderTop: "1px solid oklch(0.14 0.01 240)", borderBottom: "1px solid oklch(0.14 0.01 240)" }}>
        <div className="max-w-3xl mx-auto">
          <div className="text-[9px] font-mono tracking-[0.3em] uppercase mb-2 text-center" style={{ color: "oklch(0.45 0.01 240)" }}>
            Comment fonctionne Obsidia
          </div>
          <p className="text-center text-[11px] font-mono mb-6" style={{ color: "oklch(0.40 0.01 240)" }}>
            Passez la souris sur chaque étape pour comprendre son rôle
          </p>

          {/* Pipeline horizontal */}
          <div className="flex items-center justify-center gap-0 overflow-x-auto pb-2">
            {PIPELINE.map((step, i) => (
              <React.Fragment key={step.id}>
                <Link href={step.href}>
                  <div
                    className="flex flex-col items-center gap-2 px-4 py-3 rounded cursor-pointer"
                    style={{
                      background: activePipelineStep === i ? `${step.color}18` : "transparent",
                      border: `1px solid ${activePipelineStep === i ? step.color + "60" : "transparent"}`,
                      transform: activePipelineStep === i ? "scale(1.08)" : "scale(1)",
                      transition: "all 0.3s ease",
                      minWidth: "80px",
                    }}
                    onMouseEnter={() => setPipelineHover(i)}
                    onMouseLeave={() => setPipelineHover(null)}
                  >
                    <div className="w-10 h-10 rounded-full flex items-center justify-center text-lg"
                      style={{
                        background: activePipelineStep === i ? `${step.color}25` : "oklch(0.12 0.01 240)",
                        border: `2px solid ${activePipelineStep === i ? step.color : "oklch(0.20 0.01 240)"}`,
                        boxShadow: activePipelineStep === i ? `0 0 14px ${step.color}40` : "none",
                        transition: "all 0.3s ease",
                      }}>
                      {step.icon}
                    </div>
                    <div className="font-mono font-bold text-[10px] text-center"
                      style={{ color: activePipelineStep === i ? step.color : "oklch(0.50 0.01 240)", transition: "color 0.3s" }}>
                      {step.label}
                    </div>
                    <div className="text-[8px] font-mono text-center" style={{ color: "oklch(0.35 0.01 240)" }}>
                      {step.sub}
                    </div>
                  </div>
                </Link>
                {i < PIPELINE.length - 1 && (
                  <div className="flex items-center px-1 mb-8">
                    <div className="w-4 h-0.5" style={{ background: activePipelineStep === i ? PIPELINE[i].color + "80" : "oklch(0.18 0.01 240)", transition: "background 0.3s" }} />
                    <span className="text-[10px]" style={{ color: activePipelineStep === i ? PIPELINE[i].color : "oklch(0.30 0.01 240)", transition: "color 0.3s" }}>→</span>
                  </div>
                )}
              </React.Fragment>
            ))}
          </div>

          {/* Explication de l'étape active */}
          <div className="mt-4 min-h-[40px] text-center px-4">
            {activePipelineStep >= 0 && activePipelineStep < PIPELINE.length && (
              <p className="text-[12px] font-mono leading-relaxed" style={{ color: "oklch(0.65 0.01 240)" }}>
                <span style={{ color: PIPELINE[activePipelineStep].color, fontWeight: "bold" }}>
                  {PIPELINE[activePipelineStep].label} —{" "}
                </span>
                {PIPELINE[activePipelineStep].explication}
              </p>
            )}
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════════
          SECTION 3 — PROBLÈME / SOLUTION
      ═══════════════════════════════════════════════════════════════════════ */}
      <section className="px-4 py-10" style={{ background: "oklch(0.09 0.01 240)", borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
        <div className="max-w-3xl mx-auto">
          <h2 className="font-mono font-bold text-2xl text-foreground mb-8 text-center">
            Le problème — et comment Obsidia le résout
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Sans Obsidia */}
            <div className="p-5 rounded" style={{ background: "oklch(0.55 0.18 25 / 0.06)", border: "1px solid oklch(0.55 0.18 25 / 0.25)" }}>
              <div className="font-mono text-[9px] font-bold tracking-widest mb-4" style={{ color: "#f87171" }}>
                ⚠ SANS OBSIDIA
              </div>
              <div className="flex flex-col gap-3 font-mono text-[11px]">
                <div className="flex items-start gap-2">
                  <span style={{ color: "#f87171" }}>→</span>
                  <span style={{ color: "oklch(0.65 0.01 240)" }}>Un bot de trading peut vendre tout un portefeuille en moins de 100 ms</span>
                </div>
                <div className="flex items-start gap-2">
                  <span style={{ color: "#f87171" }}>→</span>
                  <span style={{ color: "oklch(0.65 0.01 240)" }}>Un agent peut déclencher des virements irréversibles sans confirmation</span>
                </div>
                <div className="flex items-start gap-2">
                  <span style={{ color: "#f87171" }}>→</span>
                  <span style={{ color: "oklch(0.65 0.01 240)" }}>Une fois l'action exécutée, il est trop tard</span>
                </div>
              </div>
            </div>

            {/* Avec Obsidia */}
            <div className="p-5 rounded" style={{ background: "oklch(0.72 0.18 145 / 0.06)", border: "1px solid oklch(0.72 0.18 145 / 0.25)" }}>
              <div className="font-mono text-[9px] font-bold tracking-widest mb-4" style={{ color: "oklch(0.72 0.18 145)" }}>
                ✓ AVEC OBSIDIA
              </div>
              <div className="flex flex-col gap-3 font-mono text-[11px]">
                <div className="flex items-start gap-2">
                  <span style={{ color: "oklch(0.72 0.18 145)" }}>→</span>
                  <span style={{ color: "oklch(0.65 0.01 240)" }}>Guard X-108 évalue chaque action avant qu'elle touche le monde réel</span>
                </div>
                <div className="flex items-start gap-2">
                  <span style={{ color: "#a78bfa" }}>→</span>
                  <span style={{ color: "oklch(0.65 0.01 240)" }}>Verdict : Autoriser / Attendre 10s / Bloquer définitivement</span>
                </div>
                <div className="flex items-start gap-2">
                  <span style={{ color: "oklch(0.72 0.18 145)" }}>→</span>
                  <span style={{ color: "oklch(0.65 0.01 240)" }}>Chaque décision est prouvée et enregistrée — impossible à falsifier</span>
                </div>
              </div>
            </div>
          </div>

          <div className="p-4 rounded text-center" style={{ background: "oklch(0.72 0.18 145 / 0.08)", border: "1px solid oklch(0.72 0.18 145 / 0.30)" }}>
            <span className="font-mono text-sm font-bold" style={{ color: "oklch(0.72 0.18 145)" }}>
              L'agent agit. Obsidia décide si c'est le bon moment.
            </span>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════════
          SECTION 4 — DÉMO INTERACTIVE
      ═══════════════════════════════════════════════════════════════════════ */}
      <section className="px-4 py-10">
        <div className="max-w-3xl mx-auto">
          <div className="text-[9px] font-mono tracking-[0.3em] uppercase mb-2" style={{ color: "oklch(0.60 0.12 200)" }}>
            Démo interactive
          </div>
          <h2 className="font-mono font-bold text-2xl text-foreground mb-2">
            Une décision complète en 30 secondes
          </h2>
          <p className="font-mono text-sm text-muted-foreground mb-6">
            Krach de marché → L'agent propose de tout vendre → Guard évalue → Action bloquée → Capital protégé.
          </p>

          <div className="rounded overflow-hidden" style={{ border: "1px solid oklch(0.18 0.02 240)" }}>
            {/* Header */}
            <div className="flex items-center justify-between px-5 py-3" style={{ background: "oklch(0.10 0.02 240)", borderBottom: "1px solid oklch(0.18 0.02 240)" }}>
              <div className="flex items-center gap-3">
                <span className="text-base">⚡</span>
                <span className="font-mono font-bold text-sm text-foreground">Démo Flash Crash</span>
                <span className="text-[9px] font-mono px-1.5 py-0.5 rounded" style={{ background: "oklch(0.65 0.18 145 / 0.15)", color: "#4ade80" }}>
                  Guard X-108 · Scénario réel
                </span>
              </div>
              <div className="flex gap-2">
                {!demoActive && !demoComplete && (
                  <button onClick={runDemo} className="px-4 py-1.5 rounded font-mono text-[10px] font-bold"
                    style={{ background: "oklch(0.72 0.18 145)", color: "oklch(0.10 0.01 240)" }}>
                    ▶ Lancer
                  </button>
                )}
                {demoActive && (
                  <button onClick={stopDemo} className="px-4 py-1.5 rounded font-mono text-[10px] font-bold"
                    style={{ background: "oklch(0.16 0.01 240)", color: "#f87171", border: "1px solid #f8717130" }}>
                    ■ Arrêter
                  </button>
                )}
                {demoComplete && (
                  <button onClick={runDemo} className="px-4 py-1.5 rounded font-mono text-[10px] font-bold"
                    style={{ background: "oklch(0.14 0.01 240)", color: "#4ade80", border: "1px solid #4ade8030" }}>
                    ↺ Rejouer
                  </button>
                )}
              </div>
            </div>

            {/* Timeline */}
            <div className="p-5">
              <div className="flex items-center gap-0 mb-5">
                {DEMO_STEPS.slice(0, 5).map((step, i) => {
                  const isActive = demoActive && demoStep === i;
                  const isDone = (demoActive && demoStep > i) || demoComplete;
                  return (
                    <React.Fragment key={step.phase + i}>
                      <div className="flex flex-col items-center gap-1.5" style={{ minWidth: 0, flex: 1 }}>
                        <div className="w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold"
                          style={{
                            background: isDone ? "oklch(0.65 0.18 145 / 0.25)" : isActive ? "oklch(0.65 0.18 145)" : "oklch(0.12 0.01 240)",
                            border: `2px solid ${isDone ? "#4ade8060" : isActive ? "#4ade80" : "oklch(0.20 0.01 240)"}`,
                            transform: isActive ? "scale(1.2)" : "scale(1)",
                            boxShadow: isActive ? "0 0 12px #4ade8040" : "none",
                            transition: "all 0.5s ease",
                          }}>
                          {isDone ? "✓" : step.icon}
                        </div>
                        <div className="text-[8px] font-mono text-center"
                          style={{ color: isActive ? "#4ade80" : isDone ? "oklch(0.55 0.01 240)" : "oklch(0.35 0.01 240)" }}>
                          {step.phase.toUpperCase()}
                        </div>
                      </div>
                      {i < 4 && (
                        <div className="h-0.5" style={{ flex: 1, background: isDone ? "#4ade8040" : "oklch(0.16 0.01 240)", marginBottom: "18px", transition: "background 0.5s" }} />
                      )}
                    </React.Fragment>
                  );
                })}
              </div>

              {/* Étape active */}
              {(demoActive || demoComplete) && (
                <div className="rounded p-4"
                  style={{
                    background: demoComplete ? "oklch(0.65 0.18 145 / 0.08)" : "oklch(0.09 0.01 240)",
                    border: `1px solid ${demoComplete ? "#4ade8030" : "oklch(0.18 0.01 240)"}`,
                    transition: "all 0.3s ease",
                  }}>
                  <div className="flex items-start gap-4">
                    <div className="text-2xl flex-shrink-0 mt-0.5">{currentDemoStep.icon}</div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2 flex-wrap">
                        <span className="font-mono font-bold text-xs text-foreground">{currentDemoStep.label}</span>
                        {currentDemoStep.value && (
                          <span className="font-mono font-bold text-xs px-2 py-0.5 rounded"
                            style={{ background: `${currentDemoStep.valueColor}15`, color: currentDemoStep.valueColor, border: `1px solid ${currentDemoStep.valueColor}30` }}>
                            {currentDemoStep.value}
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] font-mono leading-relaxed" style={{ color: "oklch(0.60 0.01 240)" }}>
                        {currentDemoStep.detail}
                      </p>
                      {demoActive && (
                        <div className="mt-3 h-1 rounded overflow-hidden" style={{ background: "oklch(0.16 0.01 240)" }}>
                          <div className="h-full rounded" style={{ width: `${demoProgress}%`, background: "oklch(0.65 0.18 145)", transition: "width 0.05s linear" }} />
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Idle */}
              {!demoActive && !demoComplete && (
                <div className="text-center py-8">
                  <div className="text-4xl mb-3">⚡</div>
                  <div className="font-mono text-sm mb-1" style={{ color: "oklch(0.55 0.01 240)" }}>
                    Voyez Guard X-108 en action
                  </div>
                  <div className="text-[11px] font-mono max-w-md mx-auto leading-relaxed" style={{ color: "oklch(0.40 0.01 240)" }}>
                    Cliquez "Lancer" pour voir un scénario complet de Flash Crash :<br />
                    Marché → Agent → Évaluation X-108 → Décision → Preuve cryptographique
                  </div>
                </div>
              )}

              {demoActive && (
                <div className="mt-3 flex items-center justify-between">
                  <div className="text-[9px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>
                    Étape {Math.min(demoStep + 1, DEMO_STEPS.length)} / {DEMO_STEPS.length}
                  </div>
                  <div className="text-[9px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>
                    Scénario : Flash Crash · Seed : 42
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Lien vers simulation complète */}
          <div className="mt-4 text-center">
            <Link href="/simuler" className="text-[11px] font-mono" style={{ color: "oklch(0.60 0.12 200)" }}>
              Lancer une vraie simulation interactive →
            </Link>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════════
          SECTION 5 — GARANTIES
      ═══════════════════════════════════════════════════════════════════════ */}
      <section className="px-4 py-10" style={{ background: "oklch(0.09 0.01 240)", borderTop: "1px solid oklch(0.16 0.01 240)", borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
        <div className="max-w-3xl mx-auto">
          <div className="text-[9px] font-mono tracking-[0.3em] uppercase mb-3" style={{ color: "oklch(0.60 0.12 200)" }}>
            Des garanties prouvées, pas des promesses
          </div>
          <h2 className="font-mono font-bold text-2xl text-foreground mb-8">
            Chaque règle de sécurité est prouvée mathématiquement
          </h2>
          <div className="grid grid-cols-2 gap-4 mb-8">
            {[
              {
                icon: "📐",
                title: "33 théorèmes formels",
                desc: "Chaque règle de sécurité est prouvée en Lean 4 — un langage de preuve mathématique. Pas testée : prouvée.",
              },
              {
                icon: "🔧",
                title: "7 invariants TLA+",
                desc: "Toutes les situations d'exécution possibles sont couvertes et vérifiées par spécification formelle.",
              },
              {
                icon: "🔗",
                title: "Historique infalsifiable",
                desc: "Chaque décision est ancrée dans une chaîne de hachage Merkle. Impossible à modifier après coup.",
              },
              {
                icon: "⚙️",
                title: "Exécution déterministe",
                desc: "Même entrée → même décision, à chaque fois. Entièrement reproductible et auditable.",
              },
            ].map(item => (
              <div key={item.title} className="p-4 rounded flex flex-col gap-2"
                style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
                <span className="text-2xl">{item.icon}</span>
                <div className="font-mono text-xs font-bold text-foreground">{item.title}</div>
                <div className="text-[10px] text-muted-foreground leading-relaxed">{item.desc}</div>
              </div>
            ))}
          </div>
          <div className="flex gap-3 flex-wrap">
            <Link href="/preuves" className="px-5 py-2.5 rounded font-mono text-sm font-bold"
              style={{ background: "oklch(0.60 0.12 200)", color: "oklch(0.95 0.01 240)" }}>
              Voir les preuves →
            </Link>
            <a href={REPO} target="_blank" rel="noopener noreferrer"
              className="px-5 py-2.5 rounded font-mono text-sm font-bold border"
              style={{ background: "transparent", color: "oklch(0.65 0.01 240)", borderColor: "oklch(0.25 0.01 240)" }}>
              Code source GitHub →
            </a>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════════
          SECTION 6 — EXPLORER
      ═══════════════════════════════════════════════════════════════════════ */}
      <section className="px-4 py-10" style={{ borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
        <div className="max-w-3xl mx-auto">
          <div className="text-[9px] font-mono tracking-[0.3em] uppercase mb-3" style={{ color: "oklch(0.65 0.18 240)" }}>
            Explorer la plateforme
          </div>
          <h2 className="font-mono font-bold text-2xl text-foreground mb-8">
            Choisissez un domaine pour commencer.
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {[
              {
                href: "/simuler",
                icon: "📈",
                title: "Trading",
                desc: "Krach éclair, guerre d'algorithmes — Guard X-108 bloque les ordres catastrophiques en temps réel.",
                color: "oklch(0.72 0.18 145)",
              },
              {
                href: "/simuler",
                icon: "🏦",
                title: "Banque",
                desc: "Ruée bancaire, vague de fraude — 10 scénarios adversariaux avec état persistant.",
                color: "oklch(0.60 0.12 200)",
              },
              {
                href: "/simuler",
                icon: "🛒",
                title: "E-Commerce",
                desc: "Trafic bot, demande virale, crise d'approvisionnement — gouvernance des agents commerce.",
                color: "oklch(0.65 0.18 240)",
              },
            ].map(card => (
              <Link key={card.title} href={card.href}
                className="p-5 rounded flex flex-col gap-3 cursor-pointer"
                style={{ background: "oklch(0.12 0.01 240)", border: `1px solid ${card.color}30`, transition: "border-color 0.2s" }}>
                <span className="text-3xl">{card.icon}</span>
                <div className="font-mono text-sm font-bold" style={{ color: card.color }}>{card.title} →</div>
                <div className="text-[10px] text-muted-foreground leading-relaxed">{card.desc}</div>
              </Link>
            ))}
          </div>

          {/* Liens secondaires */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { href: "/decision", label: "Décisions live", desc: "Flux Guard X-108 en temps réel" },
              { href: "/controle", label: "Supervision", desc: "Agents actifs + statistiques" },
              { href: "/preuves", label: "Preuves formelles", desc: "Lean 4 · TLA+ · Merkle" },
              { href: "/simuler", label: "Stress Lab", desc: "16 scénarios adversariaux" },
            ].map(item => (
              <Link key={item.href + item.label} href={item.href}
                className="p-3 rounded flex flex-col gap-1 cursor-pointer"
                style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
                <div className="font-mono text-xs font-bold" style={{ color: "oklch(0.65 0.01 240)" }}>{item.label} →</div>
                <div className="text-[9px] text-muted-foreground">{item.desc}</div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════════
          SECTION 7 — ROADMAP CONDENSÉE
      ═══════════════════════════════════════════════════════════════════════ */}
      <section className="px-4 py-10 pb-16" style={{ background: "oklch(0.08 0.01 240)" }}>
        <div className="max-w-3xl mx-auto">
          <div className="text-[9px] font-mono tracking-[0.3em] uppercase mb-3" style={{ color: "oklch(0.45 0.01 240)" }}>
            Où en est le projet
          </div>
          <h2 className="font-mono font-bold text-xl text-foreground mb-6">
            Roadmap Obsidia X-108
          </h2>

          <div className="flex flex-col gap-3">
            {ROADMAP_PHASES.map(phase => (
              <div key={phase.num} className="flex items-start gap-4 p-4 rounded"
                style={{
                  background: phase.status === "current"
                    ? "oklch(0.72 0.18 145 / 0.08)"
                    : phase.status === "done"
                    ? "oklch(0.11 0.01 240)"
                    : "oklch(0.09 0.01 240)",
                  border: `1px solid ${phase.status === "current" ? "oklch(0.72 0.18 145 / 0.35)" : phase.status === "done" ? "oklch(0.18 0.01 240)" : "oklch(0.14 0.01 240)"}`,
                }}>
                <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-mono font-bold"
                  style={{
                    background: phase.status === "current" ? "oklch(0.72 0.18 145 / 0.20)" : phase.status === "done" ? "oklch(0.16 0.01 240)" : "oklch(0.12 0.01 240)",
                    color: phase.status === "current" ? "oklch(0.72 0.18 145)" : phase.status === "done" ? "#4ade80" : "oklch(0.35 0.01 240)",
                    border: `1px solid ${phase.status === "current" ? "oklch(0.72 0.18 145 / 0.4)" : phase.status === "done" ? "#4ade8030" : "oklch(0.18 0.01 240)"}`,
                  }}>
                  {phase.status === "done" ? "✓" : phase.status === "current" ? "●" : "○"}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <span className="font-mono text-xs font-bold text-foreground">{phase.title}</span>
                    <span className="text-[9px] font-mono px-1.5 py-0.5 rounded"
                      style={{
                        background: phase.status === "current" ? "oklch(0.72 0.18 145 / 0.15)" : phase.status === "done" ? "#4ade8015" : "oklch(0.14 0.01 240)",
                        color: phase.status === "current" ? "oklch(0.72 0.18 145)" : phase.status === "done" ? "#4ade80" : "oklch(0.40 0.01 240)",
                      }}>
                      Phase {phase.num}
                    </span>
                    {phase.status === "current" && (
                      <span className="text-[9px] font-mono px-1.5 py-0.5 rounded" style={{ background: "oklch(0.72 0.18 145 / 0.15)", color: "oklch(0.72 0.18 145)" }}>
                        ● EN COURS
                      </span>
                    )}
                  </div>
                  <p className="text-[10px] leading-relaxed" style={{ color: "oklch(0.50 0.01 240)" }}>
                    {phase.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 text-center">
            <a href={REPO} target="_blank" rel="noopener noreferrer"
              className="text-[11px] font-mono" style={{ color: "oklch(0.55 0.01 240)" }}>
              Voir le code source complet sur GitHub →
            </a>
          </div>
        </div>
      </section>

    </div>
  );
}
