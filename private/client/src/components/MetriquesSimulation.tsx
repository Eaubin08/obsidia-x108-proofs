/**
 * MetriquesSimulation.tsx — OS4 v48
 * Tableau de métriques financières en temps réel pour chaque domaine de simulation.
 * Se met à jour automatiquement via polling des endpoints tRPC history.
 */
import { useState, useEffect, useRef } from "react";
import { trpc } from "@/lib/trpc";

// ─── Types ────────────────────────────────────────────────────────────────────

type Domaine = "trading" | "bank" | "ecom";

interface MetriqueItem {
  label: string;
  valeur: string;
  sous: string;
  couleur: string;
  tendance?: "hausse" | "baisse" | "stable";
  important?: boolean;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function formatEur(n: number): string {
  if (Math.abs(n) >= 1_000_000) return `€${(n / 1_000_000).toFixed(2)}M`;
  if (Math.abs(n) >= 1_000) return `€${(n / 1_000).toFixed(1)}k`;
  return `€${n.toFixed(2)}`;
}

function formatPct(n: number): string {
  return `${n >= 0 ? "+" : ""}${(n * 100).toFixed(2)} %`;
}

function pnlColor(n: number): string {
  return n > 0 ? "#4ade80" : n < 0 ? "#f87171" : "#fbbf24";
}

function verdictColor(v: string): string {
  return v === "ALLOW" ? "#4ade80" : v === "HOLD" ? "#fbbf24" : "#f87171";
}

function verdictLabel(v: string): string {
  return v === "ALLOW" ? "AUTORISÉ" : v === "HOLD" ? "EN ATTENTE" : "BLOQUÉ";
}

// ─── Calcul des métriques depuis l'historique des tickets ─────────────────────

function calculerMetriques(tickets: any[], domaine: Domaine, capitalBase: number): MetriqueItem[] {
  if (!tickets || tickets.length === 0) {
    return getMetriquesVides(domaine, capitalBase);
  }

  const total = tickets.length;
  const blocks = tickets.filter(t => t.decision === "BLOCK").length;
  const holds = tickets.filter(t => t.decision === "HOLD").length;
  const allows = tickets.filter(t => t.decision === "ALLOW").length;
  const tauxBlocage = total > 0 ? blocks / total : 0;
  const dernier = tickets[0];
  const verdict = dernier?.decision ?? "ALLOW";

  // Estimation du P&L cumulé depuis les tickets
  // Les tickets contiennent les raisons qui incluent les métriques
  const pnlEstime = tickets.reduce((acc, t) => {
    // Extraire le PnL des raisons si disponible
    const reasons = t.reasons ?? [];
    const pnlReason = reasons.find((r: string) => r.includes("pnl") || r.includes("return"));
    if (pnlReason) {
      const match = pnlReason.match(/[-+]?\d+\.?\d*/);
      if (match) acc += parseFloat(match[0]);
    }
    return acc;
  }, 0);

  if (domaine === "trading") {
    const capitalActuel = capitalBase * (1 + (allows > 0 ? allows * 0.02 - blocks * 0.05 : 0));
    const pnl = capitalActuel - capitalBase;
    const pnlPct = pnl / capitalBase;
    const capitalProtege = blocks * capitalBase * 0.05;
    return [
      { label: "Capital investi",    valeur: formatEur(capitalBase),      sous: "Base de simulation",                  couleur: "#60a5fa",   important: true },
      { label: "Valeur actuelle",    valeur: formatEur(capitalActuel),     sous: `${total} décisions traitées`,         couleur: "#60a5fa",   important: true },
      { label: "P&L net",            valeur: formatEur(pnl),               sous: formatPct(pnlPct),                     couleur: pnlColor(pnl), important: true, tendance: pnl > 0 ? "hausse" : pnl < 0 ? "baisse" : "stable" },
      { label: "Capital protégé",    valeur: formatEur(capitalProtege),    sous: `${blocks} blocages Guard`,            couleur: "oklch(0.72 0.18 145)" },
      { label: "Décisions Guard",    valeur: `${total}`,                   sous: `BLOCK ${blocks} · HOLD ${holds} · ALLOW ${allows}`, couleur: "#a78bfa" },
      { label: "Taux de blocage",    valeur: `${(tauxBlocage * 100).toFixed(1)} %`, sous: "Décisions bloquées / total",  couleur: tauxBlocage > 0.3 ? "#f87171" : "#4ade80" },
      { label: "Dernier verdict",    valeur: verdictLabel(verdict),        sous: `Ticket #${dernier?.id != null ? String(dernier.id).slice(0, 8) : "—"}`, couleur: verdictColor(verdict), important: true },
      { label: "Volatilité Guard",   valeur: tauxBlocage > 0.4 ? "ÉLEVÉE" : tauxBlocage > 0.2 ? "MODÉRÉE" : "FAIBLE", sous: "Niveau de risque détecté", couleur: tauxBlocage > 0.4 ? "#f87171" : tauxBlocage > 0.2 ? "#fbbf24" : "#4ade80" },
    ];
  }

  if (domaine === "bank") {
    const soldeInitial = capitalBase;
    // Extraire CIZ et DTS réels depuis les thresholds stockés dans les tickets
    const cizValues = tickets
      .map((t: any) => {
        const th = t.thresholds as Record<string, number> | null;
        return th?.ciz ?? (t.metrics as any)?.ciz ?? null;
      })
      .filter((v: any) => v !== null) as number[];
    const dtsValues = tickets
      .map((t: any) => {
        const th = t.thresholds as Record<string, number> | null;
        return th?.dts ?? (t.metrics as any)?.dts ?? null;
      })
      .filter((v: any) => v !== null) as number[];
    const avgCiz = cizValues.length > 0 ? cizValues.reduce((a: number, b: number) => a + b, 0) / cizValues.length : null;
    const avgDts = dtsValues.length > 0 ? dtsValues.reduce((a: number, b: number) => a + b, 0) / dtsValues.length : null;
    // Solde estimé depuis CIZ moyen si disponible, sinon estimation classique
    const soldeActuel = avgCiz !== null
      ? soldeInitial * avgCiz
      : soldeInitial * (1 + allows * 0.003 - blocks * 0.02);
    const fluxNet = soldeActuel - soldeInitial;
    const fraudesBloquees = blocks;
    const montantProtege = fraudesBloquees * soldeInitial * 0.08;
    const tauxRetention = total > 0 ? (holds + allows) / total : 1;
    return [
      { label: "Solde initial",      valeur: formatEur(soldeInitial),      sous: "Capital de départ",                   couleur: "#a78bfa",   important: true },
      { label: "Solde actuel",       valeur: formatEur(soldeActuel),       sous: `Après ${total} opérations`,           couleur: "#a78bfa",   important: true },
      { label: "Flux net",           valeur: formatEur(fluxNet),           sous: formatPct(fluxNet / soldeInitial),     couleur: pnlColor(fluxNet), important: true, tendance: fluxNet > 0 ? "hausse" : fluxNet < 0 ? "baisse" : "stable" },
      { label: "CIZ (intégrité capital)", valeur: avgCiz !== null ? `${(avgCiz * 100).toFixed(1)} %` : "—", sous: avgCiz !== null ? (avgCiz > 0.9 ? "Excellent" : avgCiz > 0.7 ? "Correct" : "Risqué") : "Moteur réel", couleur: avgCiz !== null ? (avgCiz > 0.9 ? "#4ade80" : avgCiz > 0.7 ? "#fbbf24" : "#f87171") : "#a78bfa" },
      { label: "DTS (ratio dettes)",  valeur: avgDts !== null ? `${(avgDts * 100).toFixed(1)} %` : "—", sous: avgDts !== null ? (avgDts < 0.8 ? "Sain" : avgDts < 1.2 ? "Modéré" : "Excessif") : "Moteur réel", couleur: avgDts !== null ? (avgDts < 0.8 ? "#4ade80" : avgDts < 1.2 ? "#fbbf24" : "#f87171") : "#a78bfa" },
      { label: "Fraudes bloquées",   valeur: `${fraudesBloquees}`,         sous: `${formatEur(montantProtege)} protégés`, couleur: "#f87171" },
      { label: "Décisions Guard",    valeur: `${total}`,                   sous: `BLOCK ${blocks} · HOLD ${holds} · ALLOW ${allows}`, couleur: "#a78bfa" },
      { label: "Dernier verdict",    valeur: verdictLabel(verdict),        sous: `Ticket #${dernier?.id != null ? String(dernier.id).slice(0, 8) : "—"}`, couleur: verdictColor(verdict), important: true },
    ];
  }

  // ecom
  const revenuBase = capitalBase * 2.5;
  const revenuActuel = revenuBase * (1 + allows * 0.01 - blocks * 0.03);
  const margeActuelle = revenuActuel * 0.35;
  const conversions = Math.round(allows * 12 + holds * 3);
  const pnlEcom = margeActuelle - capitalBase * 0.5;
  return [
    { label: "Revenu total",         valeur: formatEur(revenuActuel),      sous: `${total} décisions traitées`,         couleur: "#34d399",   important: true },
    { label: "Marge brute",          valeur: formatEur(margeActuelle),     sous: `${((margeActuelle / revenuActuel) * 100).toFixed(1)} % du revenu`, couleur: "#34d399", important: true },
    { label: "P&L net",              valeur: formatEur(pnlEcom),           sous: formatPct(pnlEcom / (capitalBase * 0.5)), couleur: pnlColor(pnlEcom), important: true, tendance: pnlEcom > 0 ? "hausse" : "baisse" },
    { label: "Conversions",          valeur: `${conversions}`,             sous: "Commandes validées",                  couleur: "#60a5fa" },
    { label: "Blocages Guard",       valeur: `${blocks}`,                  sous: `Bots/fraudes bloqués`,                couleur: "#f87171" },
    { label: "Agents actifs",        valeur: `${Math.max(1, allows)}`,     sous: "Agents X-108 en surveillance",        couleur: "oklch(0.72 0.18 145)" },
    { label: "Décisions Guard",      valeur: `${total}`,                   sous: `BLOCK ${blocks} · HOLD ${holds} · ALLOW ${allows}`, couleur: "#a78bfa" },
    { label: "Dernier verdict",      valeur: verdictLabel(verdict),        sous: `Ticket #${dernier?.id != null ? String(dernier.id).slice(0, 8) : "—"}`, couleur: verdictColor(verdict), important: true },
  ];
}

function getMetriquesVides(domaine: Domaine, capitalBase: number): MetriqueItem[] {
  if (domaine === "trading") return [
    { label: "Capital investi",  valeur: formatEur(capitalBase), sous: "Base de simulation",    couleur: "#60a5fa", important: true },
    { label: "Valeur actuelle",  valeur: formatEur(capitalBase), sous: "Aucune simulation",     couleur: "#60a5fa", important: true },
    { label: "P&L net",          valeur: "€0,00",                sous: "+0,00 %",               couleur: "#fbbf24", important: true },
    { label: "Capital protégé",  valeur: "€0,00",                sous: "0 blocage Guard",       couleur: "oklch(0.72 0.18 145)" },
    { label: "Décisions Guard",  valeur: "0",                    sous: "Lancez une simulation", couleur: "#a78bfa" },
    { label: "Taux de blocage",  valeur: "—",                    sous: "Aucune donnée",         couleur: "oklch(0.45 0.01 240)" },
    { label: "Dernier verdict",  valeur: "—",                    sous: "En attente",            couleur: "oklch(0.45 0.01 240)", important: true },
    { label: "Volatilité Guard", valeur: "—",                    sous: "Aucune donnée",         couleur: "oklch(0.45 0.01 240)" },
  ];
  if (domaine === "bank") return [
    { label: "Solde initial",    valeur: formatEur(capitalBase), sous: "Capital de départ",     couleur: "#a78bfa", important: true },
    { label: "Solde actuel",     valeur: formatEur(capitalBase), sous: "Aucune simulation",     couleur: "#a78bfa", important: true },
    { label: "Flux net",         valeur: "€0,00",                sous: "+0,00 %",               couleur: "#fbbf24", important: true },
    { label: "Fraudes bloquées", valeur: "0",                    sous: "€0,00 protégés",        couleur: "#f87171" },
    { label: "Montant protégé",  valeur: "€0,00",                sous: "Pertes évitées",        couleur: "oklch(0.72 0.18 145)" },
    { label: "Taux de rétention",valeur: "—",                    sous: "Aucune donnée",         couleur: "oklch(0.45 0.01 240)" },
    { label: "Décisions Guard",  valeur: "0",                    sous: "Lancez une simulation", couleur: "#a78bfa" },
    { label: "Dernier verdict",  valeur: "—",                    sous: "En attente",            couleur: "oklch(0.45 0.01 240)", important: true },
  ];
  return [
    { label: "Revenu total",     valeur: "€0,00",                sous: "Aucune simulation",     couleur: "#34d399", important: true },
    { label: "Marge brute",      valeur: "€0,00",                sous: "0 % du revenu",         couleur: "#34d399", important: true },
    { label: "P&L net",          valeur: "€0,00",                sous: "+0,00 %",               couleur: "#fbbf24", important: true },
    { label: "Conversions",      valeur: "0",                    sous: "Commandes validées",    couleur: "#60a5fa" },
    { label: "Blocages Guard",   valeur: "0",                    sous: "Bots/fraudes bloqués",  couleur: "#f87171" },
    { label: "Agents actifs",    valeur: "0",                    sous: "Agents X-108",          couleur: "oklch(0.72 0.18 145)" },
    { label: "Décisions Guard",  valeur: "0",                    sous: "Lancez une simulation", couleur: "#a78bfa" },
    { label: "Dernier verdict",  valeur: "—",                    sous: "En attente",            couleur: "oklch(0.45 0.01 240)", important: true },
  ];
}

// ─── Composant principal ──────────────────────────────────────────────────────

interface Props {
  domaine: Domaine;
  couleur: string;
  capitalBase?: number;
}

export default function MetriquesSimulation({ domaine, couleur, capitalBase = 100_000 }: Props) {
  const [metriques, setMetriques] = useState<MetriqueItem[]>(() => getMetriquesVides(domaine, capitalBase));
  const [lastUpdate, setLastUpdate] = useState<string>("—");
  const prevCountRef = useRef(0);

  // Polling de l'historique des tickets pour ce domaine (10s — assez fréquent sans surcharger)
  const historyQuery = domaine === "trading"
    ? trpc.trading.history.useQuery({ limit: 20 }, { refetchInterval: 10000 })
    : domaine === "bank"
    ? trpc.bank.history.useQuery({ limit: 20 }, { refetchInterval: 10000 })
    : trpc.ecom.history.useQuery({ limit: 20 }, { refetchInterval: 10000 });

  useEffect(() => {
    const tickets = historyQuery.data ?? [];
    const newCount = tickets.length;
    prevCountRef.current = newCount;

    const nouvelles = calculerMetriques(tickets, domaine, capitalBase);
    setMetriques(nouvelles);

    const now = new Date();
    setLastUpdate(`${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}`);
  }, [historyQuery.data, domaine, capitalBase]);

  const isLoading = historyQuery.isLoading;
  const hasData = (historyQuery.data?.length ?? 0) > 0;

  return (
    <div className="rounded-lg p-4" style={{
      background: "oklch(0.09 0.01 240)",
      border: `1px solid ${couleur}25`,

    }}>
      {/* En-tête du tableau */}
      <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full" style={{ background: hasData ? "#4ade80" : "oklch(0.35 0.01 240)" }} />
          <span className="font-mono font-bold text-xs" style={{ color: couleur }}>
            Métriques en temps réel
          </span>
          {isLoading && (
            <div className="w-3 h-3 rounded-full border-2 border-t-transparent animate-spin"
              style={{ borderColor: `${couleur} transparent transparent transparent` }} />
          )}
        </div>
        <div className="flex items-center gap-3">
          {hasData ? (
            <span className="text-[9px] font-mono px-2 py-0.5 rounded" style={{ background: "#4ade8012", color: "#4ade80", border: "1px solid #4ade8025" }}>
              ● {historyQuery.data?.length} décisions
            </span>
          ) : (
            <span className="text-[9px] font-mono px-2 py-0.5 rounded" style={{ background: "oklch(0.12 0.01 240)", color: "oklch(0.40 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
              ○ En attente de simulation
            </span>
          )}
          <span className="text-[9px] font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>
            Mis à jour : {lastUpdate}
          </span>
        </div>
      </div>

      {/* Métriques importantes en grand */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        {metriques.filter(m => m.important).map(m => (
          <div key={m.label} className="p-3 rounded-lg text-center"
            style={{ background: "oklch(0.11 0.01 240)", border: `1px solid ${m.couleur}20` }}>
            <div className="font-mono font-bold text-base mb-0.5" style={{ color: m.couleur }}>
              {m.valeur}
              {m.tendance === "hausse" && <span className="text-[10px] ml-1">▲</span>}
              {m.tendance === "baisse" && <span className="text-[10px] ml-1">▼</span>}
            </div>
            <div className="text-[9px] font-mono text-muted-foreground">{m.label}</div>
            <div className="text-[8px] font-mono mt-0.5" style={{ color: "oklch(0.40 0.01 240)" }}>{m.sous}</div>
          </div>
        ))}
      </div>

      {/* Tableau complet */}
      <div className="rounded overflow-hidden" style={{ border: "1px solid oklch(0.16 0.01 240)" }}>
        <table className="w-full text-[10px] font-mono">
          <thead>
            <tr style={{ background: "oklch(0.11 0.01 240)" }}>
              <th className="text-left px-3 py-2 font-bold" style={{ color: "oklch(0.50 0.01 240)" }}>Métrique</th>
              <th className="text-right px-3 py-2 font-bold" style={{ color: "oklch(0.50 0.01 240)" }}>Valeur</th>
              <th className="text-right px-3 py-2 font-bold hidden md:table-cell" style={{ color: "oklch(0.50 0.01 240)" }}>Détail</th>
            </tr>
          </thead>
          <tbody>
            {metriques.map((m, i) => (
              <tr key={m.label} style={{ background: i % 2 === 0 ? "oklch(0.095 0.01 240)" : "oklch(0.10 0.01 240)", borderTop: "1px solid oklch(0.13 0.01 240)" }}>
                <td className="px-3 py-2" style={{ color: "oklch(0.60 0.01 240)" }}>{m.label}</td>
                <td className="px-3 py-2 text-right font-bold" style={{ color: m.couleur }}>
                  {m.valeur}
                  {m.tendance === "hausse" && <span className="text-[8px] ml-1">▲</span>}
                  {m.tendance === "baisse" && <span className="text-[8px] ml-1">▼</span>}
                </td>
                <td className="px-3 py-2 text-right hidden md:table-cell" style={{ color: "oklch(0.40 0.01 240)" }}>{m.sous}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Message si pas de données */}
      {!hasData && !isLoading && (
        <div className="mt-3 text-center text-[10px] font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>
          Lancez une simulation ci-dessous pour voir les métriques se mettre à jour automatiquement.
        </div>
      )}
    </div>
  );
}
