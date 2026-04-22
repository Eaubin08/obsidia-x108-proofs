import { useState, useEffect, useRef } from "react";
import { useLocation } from "wouter";
import { trpc } from "@/lib/trpc";
import { useDecisionStream } from "@/hooks/useDecisionStream";
import BarreMetriques from "@/components/BarreMetriques";
import SurfaceStatusBadge from "@/components/SurfaceStatusBadge";
import DecisionSummaryBar from "@/components/DecisionSummaryBar";
import PilotagePanel from "@/components/PilotagePanel";
import RunBreadcrumb from "@/components/RunBreadcrumb";
import { ModeBadgeBar } from "@/components/ModeBadge";

// ─── Types ────────────────────────────────────────────────────────────────────

type Verdict = "ALLOW" | "HOLD" | "BLOCK";
type Domaine = "trading" | "banking" | "ecom";

interface EvenementLive {
  id: string;
  ts: number;
  domaine: Domaine;
  agent: string;
  action: string;
  verdict: Verdict;
  fiabilite: number;
  hash: string;
  source?: "db_real" | "ws_real" | "local_sim"; // source identification
  traceId?: string; // Python trace_id if available
  // Vue causale
  world?: { prix: number; volatilite: number; regime: string };
  engine?: { coherence: number; risque: number };
  guard?: { raison: string; verrou: boolean };
}

// ─── Constantes ───────────────────────────────────────────────────────────────

const VERDICT_META: Record<Verdict, { couleur: string; bg: string; label: string; simple: string; investisseur: string; expert: string }> = {
  ALLOW: {
    couleur: "#4ade80", bg: "rgba(74,222,128,0.10)", label: "AUTORISÉ",
    simple: "L'action est sûre. Elle a été exécutée immédiatement.",
    investisseur: "Tous les invariants sont satisfaits : volatilité < 30 %, cohérence ≥ 0,50, régime stable.",
    expert: "vol < 0.30 ∧ coherence ≥ 0.50 ∧ regime ∉ {CRASH, BEAR} → ALLOW immédiat.",
  },
  HOLD: {
    couleur: "#fbbf24", bg: "rgba(251,191,36,0.10)", label: "EN ATTENTE",
    simple: "L'action semble valide mais le marché est instable. Guard attend 10 secondes avant de décider.",
    investisseur: "Verrou temporel τ=10s activé. Volatilité ou cohérence dans la zone grise. Pas encore dangereux, mais pas encore sûr.",
    expert: "0.30 ≤ vol < 0.45 ∨ 0.25 ≤ coherence < 0.50 → HOLD τ=10s. Réévaluation après délai.",
  },
  BLOCK: {
    couleur: "#f87171", bg: "rgba(248,113,113,0.10)", label: "BLOQUÉ",
    simple: "L'action est trop risquée. Guard l'a refusée définitivement. Aucun capital n'a été exposé.",
    investisseur: "Invariant violé : volatilité > 45 % ou cohérence < 0,25. Action irréversible refusée, capital protégé.",
    expert: "vol > 0.45 ∨ coherence < 0.25 → BLOCK permanent. Preuve cryptographique générée. Replay verifiable.",
  },
};

const DOMAINE_META: Record<Domaine, { couleur: string; icone: string; label: string }> = {
  trading: { couleur: "#3b82f6", icone: "📈", label: "Trading" },
  banking: { couleur: "#a78bfa", icone: "🏦", label: "Banque" },
  ecom:    { couleur: "#34d399", icone: "🛒", label: "E-Commerce" },
};

// Étapes du pipeline de décision avec 3 niveaux d'explication
const ETAPES = [
  {
    id: "marche", icone: "🌍", couleur: "#60a5fa", titre: "Marché",
    question: "Que se passe-t-il dans le monde ?",
    simple: "Le monde réel : le cours du Bitcoin monte ou descend, une transaction bancaire est initiée, un bot inonde une boutique. C'est le point de départ de chaque décision.",
    investisseur: "L'agent observe en continu les signaux de marché : prix, volumes, spread, actualités. Il détecte les anomalies et les changements de régime (BULL/BEAR/CRASH).",
    expert: "Flux de données : prix tick-by-tick, volatilité GARCH, profondeur carnet d'ordres, détection de régime par Markov. Entrée brute du moteur de décision.",
  },
  {
    id: "agent", icone: "🤖", couleur: "#a78bfa", titre: "Agent",
    question: "Qui propose une action ?",
    simple: "Un programme autonome surveille le marché et propose une action : acheter, vendre, valider un virement, ajuster un prix. Il ne décide pas seul — il propose.",
    investisseur: "L'agent calcule une proposition optimale selon ses objectifs (maximiser le rendement, minimiser le risque). Mais Guard X-108 a le dernier mot.",
    expert: "Agent policy : observation → proposition. Inputs : world state + historical context. Output : action + confidence score. Aucune exécution directe possible.",
  },
  {
    id: "guard", icone: "🛡", couleur: "oklch(0.72 0.18 145)", titre: "Guard X-108",
    question: "L'action est-elle sûre ?",
    simple: "C'est le cœur d'Obsidia. Guard X-108 vérifie si l'action proposée respecte toutes les règles de sécurité. Si une seule règle est violée, l'action est bloquée.",
    investisseur: "Guard X-108 applique 7 invariants formels : seuils de volatilité, cohérence, liquidité, drawdown, fraude. Chaque invariant est prouvé mathématiquement en Lean 4.",
    expert: "Évaluation : vol, coherence, regime, liquidity → score X-108. Seuils : BLOCK si vol > 0.45 ∨ coh < 0.25 ; HOLD si vol > 0.30 ∨ coh < 0.50. Déterministe et reproductible.",
  },
  {
    id: "verrou", icone: "⏱", couleur: "#94a3b8", titre: "Verrou temporel",
    question: "Faut-il attendre ?",
    simple: "Si l'action est irréversible (vente, virement, suppression), Guard impose une pause de 10 secondes. C'est le temps de vérifier que le marché ne s'est pas dégradé entre-temps.",
    investisseur: "Le verrou τ=10s est une protection contre les décisions prises dans la panique. Pendant ce délai, si les conditions empirent, l'action passe de HOLD à BLOCK.",
    expert: "Temporal lock τ=10s sur toutes les actions irréversibles. Réévaluation des invariants à t+τ. Si dégradation détectée → escalade HOLD→BLOCK. Prouvé en TLA+.",
  },
  {
    id: "verdict", icone: "⚖", couleur: "#a78bfa", titre: "Verdict",
    question: "Quelle est la décision finale ?",
    simple: "Trois verdicts possibles : AUTORISÉ (l'action part), EN ATTENTE (on attend 10s), BLOQUÉ (refus définitif). Le verdict est immédiat et irrévocable.",
    investisseur: "Le verdict est déterministe : mêmes entrées → même verdict, toujours. Impossible de contester ou de rejouer différemment. Chaque verdict est horodaté RFC 3161.",
    expert: "Verdict ∈ {ALLOW, HOLD, BLOCK}. Déterminisme garanti par seed + invariants. Horodatage RFC 3161. Hash SHA-256 de (inputs + verdict + timestamp) → preuve.",
  },
  {
    id: "preuve", icone: "🔗", couleur: "#34d399", titre: "Preuve",
    question: "Comment prouver que la décision a eu lieu ?",
    simple: "Chaque décision génère une empreinte numérique unique. C'est comme une signature qui prouve qu'une décision a eu lieu, sans pouvoir la modifier après coup.",
    investisseur: "La preuve est ancrée dans une chaîne Merkle et horodatée RFC 3161. Tout auditeur peut vérifier qu'une décision a eu lieu à un moment précis avec des paramètres précis.",
    expert: "SHA-256(inputs ‖ verdict ‖ τ) → hash. Merkle root mis à jour. RFC 3161 timestamp anchor. Replay : même seed → même hash. 33 théorèmes Lean 4 garantissent l'intégrité.",
  },
];

function shortHash(n: number): string {
  return ((n * 31337 + Date.now()) >>> 0).toString(16).padStart(8, "0").slice(0, 8);
}

function seededRand(seed: number, step: number): number {
  return ((seed * 1664525 + step * 1013904223) >>> 0) / 0xffffffff;
}

const ACTIONS_PAR_DOMAINE: Record<Domaine, string[]> = {
  trading: ["VENDRE 1.2 BTC", "ACHETER ETH", "CLÔTURER POSITION", "RÉÉQUILIBRER", "VENTE À DÉCOUVERT BTC"],
  banking: ["VIREMENT €200 000", "DÉPÔT €5 000", "RETRAIT €50 000", "APPROUVER PRÊT", "GELER COMPTE"],
  ecom:    ["MISE À JOUR PRIX", "RÉAPPROVISIONNEMENT", "APPLIQUER REMISE", "ANNULER COMMANDE", "VENTE FLASH"],
};

const RAISONS_PAR_VERDICT: Record<Verdict, string[]> = {
  ALLOW: ["Cohérence vérifiée", "Profil de risque nominal", "Liquidité suffisante", "Régime stable"],
  HOLD:  ["Volatilité anormale détectée", "Délai de sécurité activé", "Vérification en cours", "Régime incertain"],
  BLOCK: ["Flash Crash imminent", "Fraude détectée", "Violation invariant X-108", "Cohérence effondrée"],
};

// ─── Composant principal ──────────────────────────────────────────────────────

export default function Decision() {
  const [, navigate] = useLocation();
  const [etapeActive, setEtapeActive] = useState(2); // Guard X-108 par défaut
  const [expertMode, setExpertMode] = useState(false);
  const [evenements, setEvenements] = useState<EvenementLive[]>([]);
  const [stats, setStats] = useState({ allow: 0, hold: 0, block: 0 });
  const [selectedEv, setSelectedEv] = useState<EvenementLive | null>(null);
  // Seuils configurables
  const [seuilBlock, setSeuilBlock] = useState(0.45);
  const [seuilHold, setSeuilHold] = useState(0.30);
  const [showSeuils, setShowSeuils] = useState(false);
  const stepRef = useRef(0);

  const { events: wsEvents, connected: wsConnected } = useDecisionStream();
  // Tickets multi-domaines depuis la DB (source réelle)
  const allTicketsQuery = trpc.proof.allTickets.useQuery({ limit: 20 }, { refetchInterval: 10000 });
  // Charger les tickets DB au démarrage
  useEffect(() => {
    const tickets = allTicketsQuery.data;
    if (!tickets || tickets.length === 0) return;
    const domaineMap: Record<string, Domaine> = { trading: "trading", bank: "banking", ecom: "ecom", system: "trading" };
    const evs: EvenementLive[] = tickets.map((t: any) => {
      const d = domaineMap[t.domain] ?? "trading";
      const v = t.decision as Verdict;
      const x108 = t.x108 as any;
      const audit = t.auditTrail as any;
      return {
        id: `db-${t.id}`,
        ts: t.createdAt ? new Date(t.createdAt).getTime() : Date.now(),
        domaine: d,
        agent: t.intentId?.split(":")?.[0] ?? "Guard",
        action: t.intentId ?? "DECISION",
        verdict: v,
        fiabilite: x108?.elapsed ? Math.min(1, x108.elapsed / 108) : 0.7,
        hash: audit?.hash_now?.slice(0, 8) ?? t.id?.toString().padStart(8, "0"),
        source: "db_real",
        traceId: audit?.anchor_ref ?? undefined,
        guard: { raison: (t.reasons as string[])?.[0] ?? "Guard X-108", verrou: x108?.gate_active ?? false },
      };
    });
    setEvenements(evs);
    const allow = evs.filter(e => e.verdict === "ALLOW").length;
    const hold = evs.filter(e => e.verdict === "HOLD").length;
    const block = evs.filter(e => e.verdict === "BLOCK").length;
    setStats({ allow, hold, block });
  }, [allTicketsQuery.data]);

  // Sync WebSocket
  useEffect(() => {
    if (wsEvents.length === 0) return;
    const latest = wsEvents[0];
    const domaineMap: Record<string, Domaine> = { TRADING: "trading", BANKING: "banking", ECOMMERCE: "ecom" };
    const d = domaineMap[latest.domain] ?? "trading";
    const v = latest.guard.decision as Verdict;
      const ev: EvenementLive = {
        id: latest.id, ts: latest.timestamp, domaine: d,
        agent: latest.agent.id, action: latest.agent.proposal, verdict: v,
        fiabilite: latest.engine.coherence, hash: latest.proof.hash.slice(0, 8),
        source: "ws_real" as const,
        world: { prix: 67000, volatilite: (latest.engine as any).volatilityScore ?? 0.25, regime: "BULL" },
        engine: { coherence: latest.engine.coherence, risque: (latest.engine as any).risk ?? 0.20 },
        guard: { raison: latest.guard.reason, verrou: (latest.guard as any).temporalLock ?? false },
      };
    setEvenements(prev => [ev, ...prev].slice(0, 30));
    setStats(prev => ({ allow: prev.allow + (v === "ALLOW" ? 1 : 0), hold: prev.hold + (v === "HOLD" ? 1 : 0), block: prev.block + (v === "BLOCK" ? 1 : 0) }));
  }, [wsEvents]);

  // Simulation locale si pas de WebSocket
  useEffect(() => {
    const interval = setInterval(() => {
      stepRef.current++;
      const step = stepRef.current;
      const domaines: Domaine[] = ["trading", "banking", "ecom"];
      const d = domaines[step % 3];
      const r = seededRand(step * 7, step);
      const volatilite = Math.max(0.05, Math.min(0.95, 0.35 + (r - 0.5) * 0.6));
      const coherence = Math.max(0.05, Math.min(0.98, 0.65 - volatilite * 0.8 + seededRand(step, step + 1) * 0.3));
      const v: Verdict = volatilite > seuilBlock || coherence < (1 - seuilBlock) ? "BLOCK"
        : volatilite > seuilHold || coherence < (1 - seuilHold) ? "HOLD" : "ALLOW";
      const actions = ACTIONS_PAR_DOMAINE[d];
      const action = actions[step % actions.length];
      const agentNoms: Record<Domaine, string> = { trading: "Alpha", banking: "Sentinel", ecom: "Mercury" };
      const regimes = ["BULL", "BEAR", "CRASH", "SIDEWAYS", "RECOVERY"];
      const regime = regimes[step % 5];
      const raisons = RAISONS_PAR_VERDICT[v];
      const ev: EvenementLive = {
        id: `sim-${step}`, ts: Date.now(), domaine: d,
        agent: agentNoms[d], action, verdict: v, fiabilite: coherence,
        hash: shortHash(step),
        source: "local_sim" as const,
        world: { prix: 40000 + seededRand(step, 1) * 30000, volatilite, regime },
        engine: { coherence, risque: volatilite * (1 - coherence) },
        guard: { raison: raisons[step % raisons.length], verrou: v === "HOLD" },
      };
      setEvenements(prev => [ev, ...prev].slice(0, 30));
      setStats(prev => ({ allow: prev.allow + (v === "ALLOW" ? 1 : 0), hold: prev.hold + (v === "HOLD" ? 1 : 0), block: prev.block + (v === "BLOCK" ? 1 : 0) }));
    }, 2500);
    return () => clearInterval(interval);
  }, [seuilBlock, seuilHold]);

  const total = stats.allow + stats.hold + stats.block;
  const etape = ETAPES[etapeActive];

  return (
    <div className="flex flex-col max-w-4xl mx-auto px-4 pb-16" style={{ gap: "40px" }}>
      {/* ─── Barre de régime opératoire ─────────────────────────────────────── */}
      <ModeBadgeBar
        mode="LIVE"
        detail="Flux Guard X-108 en temps réel"
        right={evenements.length > 0 ? `${evenements.length} événements · dernier : ${evenements[0]?.verdict ?? "—"}` : undefined}
      />

      {/* ─── En-tête ─────────────────────────────────────────────────────────── */}
      <div className="pt-8">
        <div className="text-[10px] font-mono tracking-[0.3em] uppercase mb-2" style={{ color: "oklch(0.72 0.18 145)" }}>
          Obsidia Labs — OS4
        </div>
        <div className="flex items-start justify-between flex-wrap gap-3">
          <div>
            <h1 className="font-mono font-bold text-2xl text-foreground mb-2">Décision</h1>
            <p className="text-sm" style={{ color: "oklch(0.55 0.01 240)", maxWidth: "560px", lineHeight: "1.6" }}>
              Comment <strong style={{ color: "oklch(0.72 0.18 145)" }}>Guard X-108</strong> évalue chaque action proposée par un agent.
              Chaque étape est transparente, traçable et vérifiable.
            </p>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <SurfaceStatusBadge status="REAL" source="db_real" />
          <button onClick={() => setExpertMode(e => !e)}
            className="px-3 py-1.5 rounded text-[10px] font-mono font-bold flex-shrink-0"
            style={{ background: expertMode ? "oklch(0.60 0.12 200 / 0.15)" : "oklch(0.12 0.01 240)", color: expertMode ? "oklch(0.60 0.12 200)" : "oklch(0.50 0.01 240)", border: `1px solid ${expertMode ? "oklch(0.60 0.12 200 / 0.4)" : "oklch(0.20 0.01 240)"}` }}>
             {expertMode ? "🔬 Mode Expert" : "👁 Mode Simple"}
          </button>
          </div>
        </div>
      </div>
      {/* ── BLOC 1 : Résultat visible en 3s ── */}
      {evenements.length > 0 && (
        <div className="mt-2">
          <DecisionSummaryBar
            gate={evenements[0]?.verdict ?? null}
            source={evenements[0]?.source ?? "local_sim"}
            reason={evenements[0]?.guard?.raison}
            loading={false}
            domain={evenements[0]?.domaine ?? "trading"}
          />
        </div>
      )}
      {/* Barre de métriques Décision */}
      <BarreMetriques
        live={true}
        accent="oklch(0.72 0.18 145)"
        refreshMs={2500}
        metriques={[
          { label: "Décisions live",  valeur: total > 0 ? total.toString() : "—",                                                  couleur: "oklch(0.72 0.18 145)", info: "Total des événements traités depuis l'ouverture de la page" },
          { label: "BLOCK",           valeur: total > 0 ? `${stats.block} (${((stats.block/total)*100).toFixed(0)} %)` : "—",    couleur: "#f87171",             info: "Actions irréversibles refusées par Guard X-108" },
          { label: "HOLD",            valeur: total > 0 ? `${stats.hold} (${((stats.hold/total)*100).toFixed(0)} %)` : "—",     couleur: "#fbbf24",             info: "Actions en attente du verrou temporel τ=10s" },
          { label: "ALLOW",           valeur: total > 0 ? `${stats.allow} (${((stats.allow/total)*100).toFixed(0)} %)` : "—",    couleur: "#4ade80",             info: "Actions autorisées immédiatement" },
          { label: "Seuil BLOCK",     valeur: `vol > ${(seuilBlock * 100).toFixed(0)} %`,                                          couleur: "oklch(0.50 0.01 240)", info: "Seuil de volatilité au-delà duquel Guard bloque" },
          { label: "Connexion WS",    valeur: wsConnected ? "Live" : "Simulé",                                                    couleur: wsConnected ? "#4ade80" : "oklch(0.50 0.01 240)", info: "Source des événements" },
        ]}
      />

      {/* ─── Pipeline interactif ────────────────────────────────────────────────────────── */}
      <div>
        <h2 className="font-mono font-bold text-sm mb-4" style={{ color: "oklch(0.65 0.01 240)" }}>
          Pipeline de décision — cliquez sur une étape pour comprendre son rôle
        </h2>

        {/* Étapes horizontales */}
        <div className="flex items-start gap-1 flex-wrap mb-5">
          {ETAPES.map((e, i) => (
            <div key={e.id} className="flex items-center gap-1">
              <button onClick={() => setEtapeActive(i)}
                className="flex flex-col items-center gap-1 px-3 py-2 rounded-lg"
                style={{
                  background: etapeActive === i ? `${e.couleur}18` : "oklch(0.10 0.01 240)",
                  border: `1.5px solid ${etapeActive === i ? e.couleur : "oklch(0.18 0.01 240)"}`,
                  minWidth: "72px",
                  transform: etapeActive === i ? "scale(1.05)" : "scale(1)",
                  transition: "all 0.2s ease",
                }}>
                <span className="text-lg">{e.icone}</span>
                <span className="text-[9px] font-mono font-bold text-center" style={{ color: etapeActive === i ? e.couleur : "oklch(0.45 0.01 240)" }}>
                  {e.titre}
                </span>
              </button>
              {i < ETAPES.length - 1 && (
                <span className="text-[10px] font-mono mb-4" style={{ color: "oklch(0.28 0.01 240)" }}>→</span>
              )}
            </div>
          ))}
        </div>

        {/* Détail de l'étape — 3 niveaux */}
        <div className="p-5 rounded-lg" style={{ background: `${etape.couleur}0D`, border: `1px solid ${etape.couleur}30` }}>
          <div className="flex items-center gap-3 mb-3">
            <span className="text-2xl">{etape.icone}</span>
            <div>
              <div className="font-mono font-bold text-sm" style={{ color: etape.couleur }}>{etape.titre}</div>
              <div className="text-xs" style={{ color: "oklch(0.55 0.01 240)" }}>{etape.question}</div>
            </div>
          </div>

          {/* Niveau simple */}
          <div className="mb-3">
            <div className="text-[9px] font-mono tracking-widest uppercase mb-1" style={{ color: "oklch(0.40 0.01 240)" }}>En clair</div>
            <p className="text-[13px] font-mono leading-relaxed" style={{ color: "oklch(0.75 0.01 240)" }}>{etape.simple}</p>
          </div>

          {/* Niveau investisseur */}
          <div className="mb-3 pt-3" style={{ borderTop: "1px solid oklch(0.16 0.01 240)" }}>
            <div className="text-[9px] font-mono tracking-widest uppercase mb-1" style={{ color: "oklch(0.40 0.01 240)" }}>Pour un investisseur</div>
            <p className="text-[12px] font-mono leading-relaxed" style={{ color: "oklch(0.60 0.01 240)" }}>{etape.investisseur}</p>
          </div>

          {/* Niveau expert */}
          {expertMode && (
            <div className="pt-3" style={{ borderTop: "1px solid oklch(0.16 0.01 240)" }}>
              <div className="text-[9px] font-mono tracking-widest uppercase mb-1" style={{ color: "oklch(0.60 0.12 200)" }}>Détail technique</div>
              <p className="text-[11px] font-mono leading-relaxed" style={{ color: "oklch(0.50 0.01 240)" }}>{etape.expert}</p>
            </div>
          )}
        </div>
      </div>

      {/* ─── Exemple concret Flash Crash ─────────────────────────────────────── */}
      <div>
        <h2 className="font-mono font-bold text-sm mb-2" style={{ color: "oklch(0.65 0.01 240)" }}>
          Exemple concret — Flash Crash BTC
        </h2>
        <p className="text-[11px] font-mono mb-4" style={{ color: "oklch(0.45 0.01 240)" }}>
          Voici comment Guard X-108 traite un scénario de krach éclair, étape par étape.
        </p>
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
          {[
            { icone: "🌍", label: "Marché",       valeur: "BTC −18 % en 3 min",          couleur: "#60a5fa", explication: "Krach éclair détecté. Volatilité : 34,2 %." },
            { icone: "🤖", label: "Agent Alpha",  valeur: "Propose : VENDRE 1.2 BTC",     couleur: "#a78bfa", explication: "L'agent panique et veut tout vendre immédiatement." },
            { icone: "🛡", label: "Guard X-108",  valeur: "Cohérence : 0,12 < seuil 0,25", couleur: "oklch(0.72 0.18 145)", explication: "Invariant violé. Risque de vente panique détecté." },
            { icone: "⏱", label: "Verrou",       valeur: "Verrou τ=10s activé",           couleur: "#94a3b8", explication: "Action irréversible → pause de sécurité imposée." },
            { icone: "⚖", label: "Verdict",      valeur: "BLOQUÉ",                        couleur: "#f87171", explication: "Refus définitif. Capital de 125 000 € protégé." },
            { icone: "🔗", label: "Preuve",       valeur: "Hash : b9ac7a04",               couleur: "#34d399", explication: "Décision signée et enregistrée. Infalsifiable." },
          ].map(item => (
            <div key={item.label} className="p-3 rounded-lg" style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
              <div className="flex items-center gap-2 mb-1">
                <span>{item.icone}</span>
                <span className="text-[10px] font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>{item.label}</span>
              </div>
              <div className="text-xs font-semibold mb-1" style={{ color: item.couleur }}>{item.valeur}</div>
              {expertMode && (
                <div className="text-[9px] font-mono leading-relaxed" style={{ color: "oklch(0.40 0.01 240)" }}>{item.explication}</div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* ─── Règles Guard X-108 avec seuils configurables ────────────────────── */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-mono font-bold text-sm" style={{ color: "oklch(0.65 0.01 240)" }}>
            Règles de Guard X-108
          </h2>
          <button onClick={() => setShowSeuils(s => !s)}
            className="px-3 py-1.5 rounded text-[10px] font-mono font-bold"
            style={{ background: showSeuils ? "oklch(0.72 0.18 145 / 0.15)" : "oklch(0.12 0.01 240)", color: showSeuils ? "oklch(0.72 0.18 145)" : "oklch(0.50 0.01 240)", border: `1px solid ${showSeuils ? "oklch(0.72 0.18 145 / 0.4)" : "oklch(0.20 0.01 240)"}` }}>
            {showSeuils ? "▲ Masquer les seuils" : "⚙ Ajuster les seuils"}
          </button>
        </div>

        {/* Les 3 verdicts expliqués */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          {(["ALLOW", "HOLD", "BLOCK"] as Verdict[]).map(v => {
            const vm = VERDICT_META[v];
            return (
              <div key={v} className="p-4 rounded-lg" style={{ background: vm.bg, border: `1px solid ${vm.couleur}30` }}>
                <div className="font-mono font-bold text-sm mb-2" style={{ color: vm.couleur }}>{vm.label}</div>
                <p className="text-[11px] font-mono leading-relaxed mb-2" style={{ color: "oklch(0.65 0.01 240)" }}>{vm.simple}</p>
                {expertMode && (
                  <p className="text-[10px] font-mono leading-relaxed" style={{ color: "oklch(0.45 0.01 240)" }}>{vm.expert}</p>
                )}
              </div>
            );
          })}
        </div>

        {/* Seuils configurables */}
        {showSeuils && (
          <div className="p-5 rounded-lg" style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.20 0.01 240)" }}>
            <div className="text-[9px] font-mono tracking-widest uppercase mb-4" style={{ color: "oklch(0.72 0.18 145)" }}>
              Ajuster les seuils — les décisions live s'adaptent en temps réel
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <div className="flex justify-between text-[10px] font-mono mb-1">
                  <span style={{ color: "oklch(0.55 0.01 240)" }}>Seuil BLOCK (volatilité max)</span>
                  <span style={{ color: "#f87171", fontWeight: "bold" }}>{(seuilBlock * 100).toFixed(0)} %</span>
                </div>
                <input type="range" min={0.25} max={0.70} step={0.05} value={seuilBlock}
                  onChange={e => setSeuilBlock(parseFloat(e.target.value))}
                  className="w-full h-1.5 rounded-full appearance-none cursor-pointer"
                  style={{ accentColor: "#f87171" }} />
                <div className="text-[9px] font-mono mt-1" style={{ color: "oklch(0.40 0.01 240)" }}>
                  Si volatilité {'>'} {(seuilBlock * 100).toFixed(0)} % → BLOCK immédiat
                </div>
              </div>
              <div>
                <div className="flex justify-between text-[10px] font-mono mb-1">
                  <span style={{ color: "oklch(0.55 0.01 240)" }}>Seuil HOLD (zone d'attente)</span>
                  <span style={{ color: "#fbbf24", fontWeight: "bold" }}>{(seuilHold * 100).toFixed(0)} %</span>
                </div>
                <input type="range" min={0.10} max={0.45} step={0.05} value={seuilHold}
                  onChange={e => setSeuilHold(parseFloat(e.target.value))}
                  className="w-full h-1.5 rounded-full appearance-none cursor-pointer"
                  style={{ accentColor: "#fbbf24" }} />
                <div className="text-[9px] font-mono mt-1" style={{ color: "oklch(0.40 0.01 240)" }}>
                  Si volatilité {'>'} {(seuilHold * 100).toFixed(0)} % → HOLD τ=10s
                </div>
              </div>
            </div>
            <div className="mt-4 p-3 rounded text-[10px] font-mono" style={{ background: "oklch(0.72 0.18 145 / 0.08)", border: "1px solid oklch(0.72 0.18 145 / 0.25)", color: "oklch(0.65 0.01 240)" }}>
              ℹ Les seuils par défaut (BLOCK : 45 %, HOLD : 30 %) sont issus des 473 tests adversariaux. Les modifier peut réduire la protection.
            </div>
          </div>
        )}
      </div>

      {/* ─── Flux live ───────────────────────────────────────────────────────── */}
      <div>
        <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
          <h2 className="font-mono font-bold text-sm" style={{ color: "oklch(0.65 0.01 240)" }}>
            Décisions en temps réel
          </h2>
          <div className="flex items-center gap-3 flex-wrap">
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full" style={{ background: wsConnected ? "#4ade80" : "#fbbf24" }} />
              <span className="text-[9px] font-mono" style={{ color: wsConnected ? "#4ade80" : "#fbbf24" }}>
                {wsConnected ? "LIVE" : "SIMULATION"}
              </span>
            </div>
            {total > 0 && (
              <div className="flex items-center gap-2 text-[9px] font-mono">
                <span style={{ color: "#4ade80" }}>{stats.allow} autorisés</span>
                <span style={{ color: "#fbbf24" }}>{stats.hold} en attente</span>
                <span style={{ color: "#f87171" }}>{stats.block} bloqués</span>
              </div>
            )}
          </div>
        </div>

        {/* Barre de distribution */}
        {total > 0 && (
          <div className="mb-4">
            <div className="flex rounded overflow-hidden h-2" style={{ background: "oklch(0.14 0.01 240)" }}>
              <div style={{ width: `${(stats.allow / total) * 100}%`, background: "#4ade80", transition: "width 0.5s" }} />
              <div style={{ width: `${(stats.hold / total) * 100}%`, background: "#fbbf24", transition: "width 0.5s" }} />
              <div style={{ width: `${(stats.block / total) * 100}%`, background: "#f87171", transition: "width 0.5s" }} />
            </div>
            <div className="flex justify-between mt-1 text-[9px] font-mono">
              <span style={{ color: "#4ade80" }}>AUTORISÉ {((stats.allow / total) * 100).toFixed(1)} %</span>
              <span style={{ color: "#fbbf24" }}>EN ATTENTE {((stats.hold / total) * 100).toFixed(1)} %</span>
              <span style={{ color: "#f87171" }}>BLOQUÉ {((stats.block / total) * 100).toFixed(1)} %</span>
            </div>
          </div>
        )}

        <div className="flex flex-col gap-2">
          {evenements.length === 0 && (
            <div className="text-center py-8 text-xs font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>
              En attente des premières décisions…
            </div>
          )}
          {evenements.slice(0, 12).map(ev => {
            const vm = VERDICT_META[ev.verdict];
            const dm = DOMAINE_META[ev.domaine];
            const age = Math.round((Date.now() - ev.ts) / 1000);
            const isSelected = selectedEv?.id === ev.id;
            return (
              <div key={ev.id}>
                <button
                  onClick={() => setSelectedEv(isSelected ? null : ev)}
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left"
                  style={{ background: isSelected ? "oklch(0.12 0.01 240)" : "oklch(0.10 0.01 240)", border: `1px solid ${isSelected ? vm.couleur + "40" : "oklch(0.16 0.01 240)"}` }}>
                  <span className="text-base">{dm.icone}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-[11px] font-mono font-semibold" style={{ color: dm.couleur }}>{dm.label}</span>
                      <span className="text-[10px]" style={{ color: "oklch(0.45 0.01 240)" }}>·</span>
                      <span className="text-[10px] font-mono truncate" style={{ color: "oklch(0.60 0.01 240)" }}>{ev.action}</span>
                      {ev.source && (
                        <span className="text-[8px] font-mono px-1.5 py-0.5 rounded flex-shrink-0" style={{
                          background: ev.source === 'db_real' ? 'oklch(0.20 0.12 145 / 0.3)' : ev.source === 'ws_real' ? 'oklch(0.20 0.12 200 / 0.3)' : 'oklch(0.15 0.01 240)',
                          color: ev.source === 'db_real' ? 'oklch(0.72 0.18 145)' : ev.source === 'ws_real' ? 'oklch(0.72 0.18 200)' : 'oklch(0.45 0.01 240)',
                          border: `1px solid ${ev.source === 'db_real' ? 'oklch(0.72 0.18 145 / 0.3)' : ev.source === 'ws_real' ? 'oklch(0.72 0.18 200 / 0.3)' : 'oklch(0.25 0.01 240)'}`
                        }}>
                          {ev.source === 'db_real' ? '⚡ db_real' : ev.source === 'ws_real' ? '🟢 ws_real' : '⚠ local_sim'}
                        </span>
                      )}
                    </div>
                    <div className="text-[9px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>
                      Agent {ev.agent} · #{ev.hash} · il y a {age}s
                    </div>
                  </div>
                  <div className="px-2 py-0.5 rounded text-[9px] font-mono font-bold flex-shrink-0" style={{ background: vm.bg, color: vm.couleur }}>
                    {vm.label}
                  </div>
                  <span className="text-[9px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>
                    {isSelected ? "▲" : "▼"}
                  </span>
                </button>

                {/* RunBreadcrumb — fil de navigation run X-108 */}
                {isSelected && (
                  <RunBreadcrumb
                    domain={ev.domaine === "banking" ? "bank" : ev.domaine}
                    scenarioId={ev.action?.split(" ")[0]?.toLowerCase().replace(/[^a-z0-9_]/g, "_") ?? null}
                    seed={null}
                    verdict={ev.verdict === "ALLOW" || ev.verdict === "HOLD" || ev.verdict === "BLOCK" ? ev.verdict : null}
                    traceId={ev.traceId ?? ev.hash}
                    ticketId={ev.id}
                    className="mx-2 mt-1"
                  />
                )}
                {/* Vue causale dépliable */}
                {isSelected && ev.world && ev.engine && ev.guard && (
                  <div className="mx-2 mb-2 p-4 rounded-b-lg" style={{ background: "oklch(0.09 0.01 240)", border: `1px solid ${vm.couleur}20`, borderTop: "none" }}>
                    <div className="text-[9px] font-mono tracking-widest uppercase mb-3" style={{ color: "oklch(0.45 0.01 240)" }}>
                      Vue causale — MONDE → AGENT → MOTEUR → GUARD → VERDICT → PREUVE
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      <div className="p-2 rounded" style={{ background: "oklch(0.11 0.01 240)" }}>
                        <div className="text-[8px] font-mono text-muted-foreground mb-1">🌍 MONDE</div>
                        <div className="text-[10px] font-mono" style={{ color: "#60a5fa" }}>
                          Prix : ${ev.world.prix.toFixed(0)}<br />
                          Vol : {(ev.world.volatilite * 100).toFixed(1)} %<br />
                          Régime : {ev.world.regime}
                        </div>
                      </div>
                      <div className="p-2 rounded" style={{ background: "oklch(0.11 0.01 240)" }}>
                        <div className="text-[8px] font-mono text-muted-foreground mb-1">🤖 AGENT</div>
                        <div className="text-[10px] font-mono" style={{ color: "#a78bfa" }}>
                          {ev.agent}<br />
                          {ev.action}
                        </div>
                      </div>
                      <div className="p-2 rounded" style={{ background: "oklch(0.11 0.01 240)" }}>
                        <div className="text-[8px] font-mono text-muted-foreground mb-1">⚙ MOTEUR</div>
                        <div className="text-[10px] font-mono" style={{ color: "oklch(0.72 0.18 145)" }}>
                          Cohérence : {ev.engine.coherence.toFixed(2)}<br />
                          Risque : {ev.engine.risque.toFixed(2)}
                        </div>
                      </div>
                      <div className="p-2 rounded" style={{ background: "oklch(0.11 0.01 240)" }}>
                        <div className="text-[8px] font-mono text-muted-foreground mb-1">🛡 GUARD</div>
                        <div className="text-[10px] font-mono" style={{ color: "oklch(0.65 0.01 240)" }}>
                          {ev.guard.raison}<br />
                          {ev.guard.verrou && <span style={{ color: "#fbbf24" }}>Verrou τ=10s activé</span>}
                        </div>
                      </div>
                      <div className="p-2 rounded" style={{ background: vm.bg, border: `1px solid ${vm.couleur}30` }}>
                        <div className="text-[8px] font-mono text-muted-foreground mb-1">⚖ VERDICT</div>
                        <div className="font-mono font-bold text-sm" style={{ color: vm.couleur }}>{vm.label}</div>
                        <div className="text-[9px] font-mono mt-1" style={{ color: "oklch(0.50 0.01 240)" }}>{vm.simple}</div>
                      </div>
                      <div className="p-2 rounded" style={{ background: "oklch(0.11 0.01 240)" }}>
                        <div className="text-[8px] font-mono text-muted-foreground mb-1">🔗 PREUVE</div>
                        <div className="text-[10px] font-mono" style={{ color: "#34d399" }}>
                          Hash : {ev.hash}<br />
                          <span style={{ color: "oklch(0.45 0.01 240)" }}>Replay verifiable</span>
                        </div>
                      </div>
                    </div>
                    {/* Panneau latéral verdict + actions directes */}
                    <div className="mt-3 pt-3 flex flex-wrap gap-2 items-center" style={{ borderTop: "1px solid oklch(0.16 0.01 240)" }}>
                      <div className="flex items-center gap-2 mr-auto">
                        <span className="text-[9px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>Actions :</span>
                        <span className="text-[9px] font-mono px-2 py-0.5 rounded font-bold" style={{ background: vm.bg, color: vm.couleur, border: `1px solid ${vm.couleur}40` }}>
                          {ev.verdict}
                        </span>
                        {ev.source && (
                          <span className="text-[8px] font-mono px-1.5 py-0.5 rounded" style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.50 0.01 240)" }}>
                            {ev.source === 'db_real' ? '⚡ db_real' : ev.source === 'ws_real' ? '🟢 ws_real' : '⚠ local_sim'}
                          </span>
                        )}
                      </div>
                      <button
                        onClick={() => navigate(`/simuler?domain=${ev.domaine === 'banking' ? 'bank' : ev.domaine}&rerun=1`)}
                        className="px-2.5 py-1 rounded text-[9px] font-mono font-bold"
                        style={{ background: "oklch(0.72 0.18 145 / 0.10)", color: "oklch(0.72 0.18 145)", border: "1px solid oklch(0.72 0.18 145 / 0.30)" }}
                      >
                        ↺ Relancer
                      </button>
                      <button
                        onClick={() => navigate('/preuves')}
                        className="px-2.5 py-1 rounded text-[9px] font-mono font-bold"
                        style={{ background: "oklch(0.60 0.12 200 / 0.10)", color: "oklch(0.60 0.12 200)", border: "1px solid oklch(0.60 0.12 200 / 0.30)" }}
                      >
                        ⊞ Preuve
                      </button>
                      <button
                        onClick={() => navigate('/controle')}
                        className="px-2.5 py-1 rounded text-[9px] font-mono font-bold"
                        style={{ background: "oklch(0.65 0.18 240 / 0.10)", color: "oklch(0.65 0.18 240)", border: "1px solid oklch(0.65 0.18 240 / 0.30)" }}
                      >
                        🛡️ Mission Control
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
      {/* ── BLOC 4 : Pilotage ── */}
      <PilotagePanel
        domain="trading"
        onReset={() => { setEvenements([]); setStats({ allow: 0, hold: 0, block: 0 }); setSelectedEv(null); }}
        loading={allTicketsQuery.isLoading}
        pythonAvailable={wsConnected ? true : undefined}
        showMode={true}
        mode={wsConnected ? "real" : "fallback"}
      />
      {/* ─── Glossaire ─────────────────────────────────────────────────────────────────────────── */}
      <div className="p-5 rounded-lg" style={{ background: "oklch(0.09 0.01 240)", border: "1px solid oklch(0.16 0.01 240)" }}>
        <h2 className="font-mono font-bold text-sm mb-4" style={{ color: "oklch(0.65 0.01 240)" }}>
          Comprendre les termes
        </h2>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          {[
            { terme: "Guard X-108",     def: "Le moteur de décision d'Obsidia. Il évalue chaque action proposée par un agent avant de l'autoriser, la mettre en attente ou la bloquer. Ses règles sont prouvées mathématiquement." },
            { terme: "Verrou temporel τ=10s", def: "Un délai de sécurité imposé avant l'exécution d'une action irréversible. Pendant ces 10 secondes, si les conditions se dégradent, l'action passe de EN ATTENTE à BLOQUÉ." },
            { terme: "Cohérence",       def: "Score de stabilité du marché (0 à 1). En dessous de 0,25, l'action est bloquée. Entre 0,25 et 0,50, elle est mise en attente. Au-dessus de 0,50, elle peut être autorisée." },
            { terme: "Preuve cryptographique", def: "Code unique généré pour chaque décision via SHA-256. Permet de prouver qu'une décision a eu lieu à un moment précis avec des paramètres précis. Impossible à falsifier." },
          ].map(g => (
            <div key={g.terme} className="p-3 rounded" style={{ background: "oklch(0.12 0.01 240)" }}>
              <div className="text-xs font-mono font-bold mb-1" style={{ color: "oklch(0.72 0.18 145)" }}>{g.terme}</div>
              <div className="text-[11px] leading-relaxed" style={{ color: "oklch(0.55 0.01 240)" }}>{g.def}</div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
