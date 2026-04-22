/**
 * BarreMetriques.tsx — OS4 v49b
 * Barre de métriques compacte et réutilisable.
 * Affiche 4-6 chiffres clés en ligne, auto-rafraîchis via les props parentes.
 * AUCUNE animation interne — les valeurs se mettent à jour silencieusement.
 */

// ─── Types ────────────────────────────────────────────────────────────────────

export interface MetriqueKV {
  label: string;
  valeur: string;
  couleur?: string;
  /** Optionnel : flèche de tendance */
  tendance?: "hausse" | "baisse" | "stable" | null;
  /** Optionnel : tooltip au survol */
  info?: string;
}

interface Props {
  metriques: MetriqueKV[];
  /** Couleur de l'accent (bord gauche + point live) */
  accent?: string;
  /** Conservé pour compatibilité ascendante — ignoré (pas d'animation interne) */
  refreshMs?: number;
  /** Afficher le badge "live" */
  live?: boolean;
  /** Classe CSS supplémentaire */
  className?: string;
}

// ─── Composant ────────────────────────────────────────────────────────────────

export default function BarreMetriques({
  metriques,
  accent = "oklch(0.72 0.18 145)",
  live = false,
  className = "",
}: Props) {
  return (
    <div
      className={`flex items-center gap-0 flex-wrap rounded ${className}`}
      style={{
        background: "oklch(0.09 0.01 240)",
        border: "1px solid oklch(0.16 0.01 240)",
        borderLeft: `2px solid ${accent}`,
      }}
    >
      {/* Badge live optionnel */}
      {live && (
        <div
          className="flex items-center gap-1.5 px-3 py-2 shrink-0"
          style={{ borderRight: "1px solid oklch(0.16 0.01 240)" }}
        >
          <div
            className="w-1.5 h-1.5 rounded-full"
            style={{ background: "#4ade80", boxShadow: "0 0 4px #4ade80" }}
          />
          <span className="text-[8px] font-mono font-bold tracking-widest uppercase" style={{ color: "#4ade80" }}>
            live
          </span>
        </div>
      )}

      {/* Métriques */}
      {metriques.map((m, i) => (
        <div
          key={m.label}
          className="flex items-center gap-2 px-3 py-2"
          style={{
            borderRight: i < metriques.length - 1 ? "1px solid oklch(0.14 0.01 240)" : "none",
          }}
          title={m.info}
        >
          <span className="text-[9px] font-mono" style={{ color: "oklch(0.42 0.01 240)", whiteSpace: "nowrap" }}>
            {m.label}
          </span>
          <span
            className="text-[11px] font-mono font-bold"
            style={{ color: m.couleur ?? "oklch(0.75 0.01 240)", whiteSpace: "nowrap" }}
          >
            {m.valeur}
            {m.tendance === "hausse" && <span className="text-[8px] ml-0.5">▲</span>}
            {m.tendance === "baisse" && <span className="text-[8px] ml-0.5">▼</span>}
          </span>
        </div>
      ))}
    </div>
  );
}
