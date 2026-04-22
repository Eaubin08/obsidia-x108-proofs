import React, { useEffect, useRef, useState } from "react";

interface StrasbourgClockProps {
  active: boolean;
  tau: number; // secondes (ex: 10)
  elapsed?: number; // secondes écoulées (0..tau)
  onComplete?: () => void;
  label?: string;
}

export function StrasbourgClock({ active, tau, elapsed: externalElapsed, onComplete, label }: StrasbourgClockProps) {
  const [elapsed, setElapsed] = useState(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (externalElapsed !== undefined) {
      setElapsed(externalElapsed);
      return;
    }
    if (active && elapsed < tau) {
      intervalRef.current = setInterval(() => {
        setElapsed((prev) => {
          const next = prev + 0.1;
          if (next >= tau) {
            clearInterval(intervalRef.current!);
            onComplete?.();
            return tau;
          }
          return next;
        });
      }, 100);
    } else if (!active) {
      setElapsed(0);
      if (intervalRef.current) clearInterval(intervalRef.current);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [active, tau, externalElapsed]);

  const progress = Math.min(elapsed / tau, 1);
  const remaining = Math.max(tau - elapsed, 0);
  const isComplete = elapsed >= tau;

  // SVG clock face
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference * (1 - progress);

  const color = isComplete
    ? "#4ade80"
    : progress > 0.7
    ? "#fbbf24"
    : "#f87171";

  return (
    <div className={`flex flex-col items-center gap-2 p-3 rounded-lg border transition-all duration-300 ${
      active && !isComplete
        ? "border-amber-500/50 bg-amber-500/5 shadow-[0_0_20px_rgba(251,191,36,0.1)]"
        : isComplete
        ? "border-emerald-500/50 bg-emerald-500/5"
        : "border-[#1e2a1e] bg-[#0a0f0a]"
    }`}>
      {/* Clock face */}
      <div className="relative">
        <svg width="96" height="96" viewBox="0 0 96 96">
          {/* Background circle */}
          <circle
            cx="48" cy="48" r={radius}
            fill="none"
            stroke="#1a2a1a"
            strokeWidth="6"
          />
          {/* Progress arc */}
          <circle
            cx="48" cy="48" r={radius}
            fill="none"
            stroke={color}
            strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            transform="rotate(-90 48 48)"
            style={{ transition: "stroke-dashoffset 0.1s linear, stroke 0.3s ease" }}
          />
          {/* Tick marks */}
          {Array.from({ length: 12 }).map((_, i) => {
            const angle = (i * 30 * Math.PI) / 180;
            const x1 = 48 + 28 * Math.sin(angle);
            const y1 = 48 - 28 * Math.cos(angle);
            const x2 = 48 + 32 * Math.sin(angle);
            const y2 = 48 - 32 * Math.cos(angle);
            return (
              <line key={i} x1={x1} y1={y1} x2={x2} y2={y2}
                stroke="#2a3a2a" strokeWidth="1.5" />
            );
          })}
          {/* Center dot */}
          <circle cx="48" cy="48" r="3" fill={color} />
          {/* Hand */}
          {active && (
            <line
              x1="48" y1="48"
              x2={48 + 24 * Math.sin(progress * 2 * Math.PI)}
              y2={48 - 24 * Math.cos(progress * 2 * Math.PI)}
              stroke={color}
              strokeWidth="2"
              strokeLinecap="round"
              style={{ transition: "all 0.1s linear" }}
            />
          )}
        </svg>
        {/* Center time display */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-lg font-bold font-mono" style={{ color }}>
            {isComplete ? "✓" : remaining.toFixed(1)}
          </span>
          {!isComplete && <span className="text-[8px] text-[#6b7280] font-mono">sec</span>}
        </div>
      </div>

      {/* Status */}
      <div className="text-center">
        {label && <div className="text-[9px] text-[#6b7280] font-mono mb-1 uppercase tracking-widest">{label}</div>}
        {active && !isComplete ? (
          <div className="text-xs font-mono text-amber-400 font-bold animate-pulse">
            ⏸ HOLD ACTIF
          </div>
        ) : isComplete ? (
          <div className="text-xs font-mono text-emerald-400 font-bold">
            ✓ GATE PASSÉE
          </div>
        ) : (
          <div className="text-xs font-mono text-[#4b5563]">
            τ = {tau}s
          </div>
        )}
        {active && !isComplete && (
          <div className="text-[9px] text-[#6b7280] mt-1">
            Le temps est une primitive de sécurité
          </div>
        )}
      </div>
    </div>
  );
}
