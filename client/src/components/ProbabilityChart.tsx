/**
 * ProbabilityChart — 24h probability trend chart for predictions
 * Uses Chart.js line chart with 6 prediction series.
 * Simulation events are rendered as vertical annotation lines colored by domain:
 *   trading → blue (#3b82f6)
 *   bank    → green (#22c55e)
 *   ecom    → purple (#a855f7)
 */
import { useEffect, useRef, useMemo } from "react";
import { Chart, registerables } from "chart.js";
import { trpc } from "@/lib/trpc";

Chart.register(...registerables);

// Domain colors aligned with OS4 palette
const DOMAIN_COLORS: Record<string, { border: string; bg: string; label: string }> = {
  "flash-crash":      { border: "#ef4444", bg: "rgba(239,68,68,0.12)",    label: "Flash Crash Risk" },
  "regime-shift":     { border: "#f97316", bg: "rgba(249,115,22,0.10)",   label: "Regime Shift" },
  "fraud-wave":       { border: "#eab308", bg: "rgba(234,179,8,0.10)",    label: "Fraud Wave Risk" },
  "liquidity-crisis": { border: "#8b5cf6", bg: "rgba(139,92,246,0.10)",   label: "Liquidity Crisis" },
  "supply-shock":     { border: "#06b6d4", bg: "rgba(6,182,212,0.10)",    label: "Supply Shock" },
  "demand-surge":     { border: "#22c55e", bg: "rgba(34,197,94,0.10)",    label: "Demand Surge" },
};

// Per-domain simulation marker colors
const SIM_DOMAIN_COLORS: Record<string, { line: string; fill: string; label: string }> = {
  trading: { line: "rgba(59,130,246,0.90)",  fill: "rgba(59,130,246,0.12)",  label: "Trading" },
  bank:    { line: "rgba(34,197,94,0.90)",   fill: "rgba(34,197,94,0.12)",   label: "Bank" },
  ecom:    { line: "rgba(168,85,247,0.90)",  fill: "rgba(168,85,247,0.12)",  label: "E-Com" },
};

export interface SimulationMarker {
  id: number;
  timestamp: number;   // Unix ms
  capital: number;
  pnl: number;
  guardBlocks: number;
  capitalSaved: number;
  domain?: string;
  scenarioName?: string | null;
}

interface ProbabilityChartProps {
  activeDomain?: "trading" | "bank" | "ecom";
  height?: number;
  simulationMarkers?: SimulationMarker[];
}

export default function ProbabilityChart({
  activeDomain,
  height = 280,
  simulationMarkers = [],
}: ProbabilityChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<Chart | null>(null);

  const { data, isLoading } = trpc.prediction.getHistory24h.useQuery(
    { domain: activeDomain },
    { refetchInterval: 5 * 60 * 1000 }
  );

  // Build unified time axis (last 24h, hourly)
  const timeLabels = useMemo(() => {
    const now = Date.now();
    return Array.from({ length: 24 }, (_, i) => {
      const t = new Date(now - (23 - i) * 3600000);
      return `${t.getHours().toString().padStart(2, "00")}:00`;
    });
  }, []);

  useEffect(() => {
    if (!canvasRef.current || !data) return;

    if (chartRef.current) {
      chartRef.current.destroy();
      chartRef.current = null;
    }

    const now = Date.now();

    // ── Probability datasets ──────────────────────────────────────────────────
    const datasets = data.map((series) => {
      const color =
        DOMAIN_COLORS[series.predictionId] ??
        { border: "#6b7280", bg: "rgba(107,114,128,0.1)", label: series.predictionId };

      const buckets = Array.from({ length: 24 }, (_, i) => {
        const bucketStart = now - (23 - i) * 3600000;
        const bucketEnd = bucketStart + 3600000;
        const matching = series.points.filter(
          (p) => p.t >= bucketStart && p.t < bucketEnd
        );
        if (matching.length === 0) return null;
        return Math.round(
          matching.reduce((sum, p) => sum + p.probability, 0) / matching.length
        );
      });

      return {
        label: color.label,
        data: buckets,
        borderColor: color.border,
        backgroundColor: color.bg,
        borderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 5,
        tension: 0.4,
        fill: false,
        spanGaps: true,
        type: "line" as const,
      };
    });

    // ── Map simulation markers to hourly bucket indices ───────────────────────
    const simMapped = simulationMarkers
      .map((m) => {
        const hoursAgo = (now - m.timestamp) / 3600000;
        if (hoursAgo < 0 || hoursAgo > 24) return null;
        const bucketIndex = Math.max(0, Math.min(23, Math.round(23 - hoursAgo)));
        return { bucketIndex, meta: m };
      })
      .filter(Boolean) as { bucketIndex: number; meta: SimulationMarker }[];

    // ── Custom plugin: vertical dashed lines colored by domain ────────────────
    const verticalLinesPlugin = {
      id: "simulationVerticalLines",
      afterDraw(chart: Chart) {
        if (simMapped.length === 0) return;
        const ctx = chart.ctx;
        const xAxis = chart.scales["x"];
        const yAxis = chart.scales["y"];
        if (!xAxis || !yAxis) return;

        simMapped.forEach((point) => {
          const domainKey = point.meta.domain ?? "trading";
          const dc = SIM_DOMAIN_COLORS[domainKey] ?? SIM_DOMAIN_COLORS["trading"];
          const xPixel = xAxis.getPixelForValue(point.bucketIndex);
          const yTop = yAxis.top;
          const yBottom = yAxis.bottom;

          ctx.save();

          // Filled band
          ctx.fillStyle = dc.fill;
          ctx.fillRect(xPixel - 3, yTop, 6, yBottom - yTop);

          // Dashed vertical line
          ctx.beginPath();
          ctx.setLineDash([4, 4]);
          ctx.strokeStyle = dc.line;
          ctx.lineWidth = 1.5;
          ctx.moveTo(xPixel, yTop);
          ctx.lineTo(xPixel, yBottom);
          ctx.stroke();

          // Domain label at top
          ctx.setLineDash([]);
          ctx.fillStyle = dc.line;
          ctx.font = "bold 8px Inter, sans-serif";
          ctx.textAlign = "center";
          ctx.fillText(dc.label.toUpperCase(), xPixel, yTop + 9);

          // Triangle marker at y=100 position
          const yMarker = yAxis.getPixelForValue(100);
          ctx.beginPath();
          ctx.moveTo(xPixel, yMarker + 2);
          ctx.lineTo(xPixel - 5, yMarker - 7);
          ctx.lineTo(xPixel + 5, yMarker - 7);
          ctx.closePath();
          ctx.fillStyle = dc.line;
          ctx.fill();

          ctx.restore();
        });
      },
    };

    chartRef.current = new Chart(canvasRef.current, {
      type: "line",
      data: {
        labels: timeLabels,
        datasets,
      },
      plugins: [verticalLinesPlugin],
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: "index",
          intersect: false,
        },
        plugins: {
          legend: {
            position: "top",
            labels: {
              color: "#94a3b8",
              font: { size: 11, family: "Inter, sans-serif" },
              boxWidth: 12,
              padding: 12,
            },
          },
          tooltip: {
            backgroundColor: "#1e293b",
            titleColor: "#e2e8f0",
            bodyColor: "#94a3b8",
            borderColor: "#334155",
            borderWidth: 1,
            callbacks: {
              afterBody: (items) => {
                // Show simulation details if any marker falls on this bucket
                const idx = items[0]?.dataIndex;
                if (idx === undefined) return [];
                const hits = simMapped.filter((d) => d.bucketIndex === idx);
                if (hits.length === 0) return [];
                return hits.flatMap((h) => {
                  const ts = new Date(h.meta.timestamp).toLocaleTimeString("fr-FR", {
                    hour: "2-digit",
                    minute: "2-digit",
                  });
                  const domainKey = h.meta.domain ?? "trading";
                  const dc = SIM_DOMAIN_COLORS[domainKey] ?? SIM_DOMAIN_COLORS["trading"];
                  const lines = [
                    "",
                    `▶ Simulation ${dc.label} @ ${ts}`,
                    `  Capital: ${h.meta.capital.toLocaleString("fr-FR")} €`,
                    `  PnL: ${h.meta.pnl >= 0 ? "+" : ""}${h.meta.pnl.toFixed(2)} €`,
                    `  Guard blocks: ${h.meta.guardBlocks}`,
                    `  Capital saved: ${h.meta.capitalSaved.toLocaleString("fr-FR")} €`,
                  ];
                  if (h.meta.scenarioName) lines.push(`  Scénario: ${h.meta.scenarioName}`);
                  return lines;
                });
              },
              label: (ctx) => ` ${ctx.dataset.label}: ${ctx.parsed.y ?? "—"}%`,
            },
          },
        },
        scales: {
          x: {
            grid: { color: "rgba(148,163,184,0.08)" },
            ticks: { color: "#64748b", font: { size: 10 }, maxTicksLimit: 8 },
          },
          y: {
            min: 0,
            max: 100,
            grid: { color: "rgba(148,163,184,0.08)" },
            ticks: {
              color: "#64748b",
              font: { size: 10 },
              callback: (v) => `${v}%`,
            },
          },
        },
      },
    });

    return () => {
      chartRef.current?.destroy();
      chartRef.current = null;
    };
  }, [data, timeLabels, simulationMarkers]);

  if (isLoading) {
    return (
      <div
        style={{ height }}
        className="flex items-center justify-center bg-slate-800/40 rounded-lg border border-slate-700/50"
      >
        <div className="text-center">
          <div className="w-6 h-6 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          <p className="text-slate-400 text-xs">Loading 24h trend data…</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div
        style={{ height }}
        className="flex items-center justify-center bg-slate-800/40 rounded-lg border border-slate-700/50"
      >
        <p className="text-slate-500 text-sm">No trend data available yet</p>
      </div>
    );
  }

  // Count markers per domain for the legend
  const domainCounts = simulationMarkers.reduce<Record<string, number>>((acc, m) => {
    const d = m.domain ?? "trading";
    acc[d] = (acc[d] ?? 0) + 1;
    return acc;
  }, {});

  return (
    <div className="space-y-1">
      <div
        style={{ height }}
        className="bg-slate-800/40 rounded-lg border border-slate-700/50 p-3"
      >
        <canvas ref={canvasRef} />
      </div>

      {/* Domain-colored simulation legend */}
      {simulationMarkers.length > 0 && (
        <div className="flex items-center gap-4 px-1 flex-wrap">
          <span className="text-xs text-slate-500">Simulations :</span>
          {Object.entries(domainCounts).map(([domain, count]) => {
            const dc = SIM_DOMAIN_COLORS[domain] ?? SIM_DOMAIN_COLORS["trading"];
            return (
              <div key={domain} className="flex items-center gap-1.5">
                <div
                  className="w-3 h-3 rounded-sm"
                  style={{ backgroundColor: dc.line }}
                />
                <span className="text-xs font-mono" style={{ color: dc.line }}>
                  {dc.label} ×{count}
                </span>
              </div>
            );
          })}
          <span className="text-xs text-slate-600 ml-1">— survolez les marqueurs pour les détails</span>
        </div>
      )}
    </div>
  );
}
