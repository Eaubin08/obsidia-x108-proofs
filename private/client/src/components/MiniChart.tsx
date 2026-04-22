import React, { useMemo } from "react";

interface LineChartProps {
  data: number[];
  width?: number;
  height?: number;
  color?: string;
  fillColor?: string;
  showDots?: boolean;
  className?: string;
}

export function MiniLineChart({
  data,
  width = 400,
  height = 120,
  color = "oklch(0.72 0.18 145)",
  fillColor,
  showDots = false,
  className = "",
}: LineChartProps) {
  const { path, fillPath, dots } = useMemo(() => {
    if (!data || data.length < 2) return { path: "", fillPath: "", dots: [] };
    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;
    const pad = 4;
    const w = width - pad * 2;
    const h = height - pad * 2;

    const points = data.map((v, i) => ({
      x: pad + (i / (data.length - 1)) * w,
      y: pad + h - ((v - min) / range) * h,
    }));

    const path = points
      .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x.toFixed(2)} ${p.y.toFixed(2)}`)
      .join(" ");

    const fillPath =
      path +
      ` L ${points[points.length - 1].x.toFixed(2)} ${(pad + h).toFixed(2)} L ${pad} ${(pad + h).toFixed(2)} Z`;

    return { path, fillPath, dots: points };
  }, [data, width, height]);

  if (!path) return null;

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className={className}
      style={{ width: "100%", height: "100%" }}
      preserveAspectRatio="none"
    >
      {fillColor && (
        <path d={fillPath} fill={fillColor} opacity={0.15} />
      )}
      <path d={path} fill="none" stroke={color} strokeWidth={1.5} strokeLinejoin="round" />
      {showDots &&
        dots.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r={2} fill={color} />
        ))}
    </svg>
  );
}

interface BarChartProps {
  data: number[];
  width?: number;
  height?: number;
  positiveColor?: string;
  negativeColor?: string;
  className?: string;
}

export function MiniBarChart({
  data,
  width = 400,
  height = 80,
  positiveColor = "oklch(0.72 0.18 145)",
  negativeColor = "oklch(0.62 0.22 25)",
  className = "",
}: BarChartProps) {
  const bars = useMemo(() => {
    if (!data || data.length === 0) return [];
    const max = Math.max(...data.map(Math.abs)) || 1;
    const pad = 2;
    const w = (width - pad * 2) / data.length;
    const midY = height / 2;

    return data.map((v, i) => {
      const barH = (Math.abs(v) / max) * (height / 2 - pad);
      const x = pad + i * w + w * 0.1;
      const bw = w * 0.8;
      const y = v >= 0 ? midY - barH : midY;
      return { x, y, w: bw, h: barH, positive: v >= 0 };
    });
  }, [data, width, height]);

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className={className}
      style={{ width: "100%", height: "100%" }}
      preserveAspectRatio="none"
    >
      <line x1={0} y1={height / 2} x2={width} y2={height / 2} stroke="oklch(0.25 0.01 240)" strokeWidth={0.5} />
      {bars.map((b, i) => (
        <rect
          key={i}
          x={b.x}
          y={b.y}
          width={b.w}
          height={Math.max(b.h, 0.5)}
          fill={b.positive ? positiveColor : negativeColor}
          opacity={0.8}
        />
      ))}
    </svg>
  );
}

interface FunnelChartProps {
  stages: { label: string; value: number; color?: string }[];
  className?: string;
}

export function FunnelChart({ stages, className = "" }: FunnelChartProps) {
  if (!stages || stages.length === 0) return null;
  const max = stages[0].value || 1;

  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      {stages.map((s, i) => {
        const pct = (s.value / max) * 100;
        const color = s.color || `oklch(${0.72 - i * 0.05} 0.18 ${145 + i * 20})`;
        return (
          <div key={i} className="flex items-center gap-2">
            <div className="text-xs text-muted-foreground w-24 text-right shrink-0">{s.label}</div>
            <div className="flex-1 h-5 bg-muted rounded-sm overflow-hidden">
              <div
                className="h-full rounded-sm transition-all"
                style={{ width: `${pct}%`, background: color }}
              />
            </div>
            <div className="text-xs font-mono w-16 text-right">{s.value.toLocaleString()}</div>
          </div>
        );
      })}
    </div>
  );
}
