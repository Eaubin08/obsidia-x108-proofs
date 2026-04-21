import React, { useState } from "react";
import { Link } from "wouter";

const PROBLEM_CASES = [
  {
    icon: "📉",
    title: "Flash Crash — 2010",
    desc: "A trading algorithm sold $4.1B in futures in 20 minutes. No human could stop it. The Dow Jones fell 1000 points in minutes.",
    cost: "$1T market cap lost",
    color: "#f87171",
  },
  {
    icon: "🏦",
    title: "Account Takeover — Daily",
    desc: "Automated fraud bots initiate wire transfers at 3am. By the time humans notice, the money is gone. Irreversible.",
    cost: "$6B/year in losses",
    color: "#f87171",
  },
  {
    icon: "🤖",
    title: "Ad Bot Chaos — E-commerce",
    desc: "An AI ad optimizer spends $50K on ads for an out-of-stock product. No coherence check. No safety gate.",
    cost: "Millions wasted",
    color: "#f87171",
  },
];

const SOLUTION_PRINCIPLES = [
  {
    id: "temporal",
    title: "Temporal Safety Gate",
    formula: "τ = 10s mandatory wait",
    desc: "Every irreversible action is paused. The system recomputes global coherence. If it fails, the action is blocked.",
  },
  {
    id: "deterministic",
    title: "Deterministic Decisions",
    formula: "seed(s) → decision(d) always",
    desc: "Given the same world state and seed, the guard always produces the same decision. No randomness in safety.",
  },
  {
    id: "cryptographic",
    title: "Cryptographic Audit",
    formula: "H(n) = SHA256(H(n-1) || data)",
    desc: "Every decision is hashed and chained. Tampering with any entry invalidates the entire chain.",
  },
  {
    id: "formal",
    title: "Formal Verification",
    formula: "∀ action: irreversible(a) → HOLD(a)",
    desc: "33 theorems proven in Lean 4. The guard behavior is mathematically verified, not just tested.",
  },
];

const OS_LAYERS = [
  {
    id: "OS4",
    title: "OS4 — Interface / Worlds",
    color: "oklch(0.65 0.18 220)",
    items: ["TradingWorld — GBM + Markov + GARCH", "BankWorld — Log-normal + Fraud detection", "EcomWorld — Funnel + Agent decisions", "Scenario Engine — 5 stress scenarios", "Automated Tests — Unit + Replay + Stress"],
    position: "top",
  },
  {
    id: "OS3",
    title: "OS3 — Audit / Proof",
    color: "oklch(0.65 0.18 220)",
    items: ["Decision logs — every action recorded", "Hash chain — SHA-256 chained entries", "Merkle tree — tamper-evident root", "Replay verifier — deterministic replay", "Formal proofs — Lean 4 + TLA+"],
    position: "upper",
  },
  {
    id: "X108",
    title: "X-108 GUARD",
    color: "oklch(0.72 0.18 145)",
    items: ["BLOCK — invariant violation detected", "HOLD — τ=10s coherence recomputation", "ALLOW — all invariants satisfied", "Temporal gate — irreversibility check", "Coherence score — global consistency"],
    highlight: true,
    position: "middle",
  },
  {
    id: "OS2",
    title: "OS2 — Runtime Engine",
    color: "oklch(0.65 0.18 220)",
    items: ["Decision pipeline — world → agent → guard", "Strategy generation — action proposals", "State updates — world state transitions", "Execution engine — post-guard actions"],
    position: "lower",
  },
  {
    id: "OS1",
    title: "OS1 — Registry / Agents",
    color: "oklch(0.65 0.18 220)",
    items: ["Agent registry — all agents registered", "World adapters — domain interfaces", "Strategy engines — per-domain logic", "Module inventory — system components"],
    position: "low",
  },
  {
    id: "OS0",
    title: "OS0 — Invariants / IR",
    color: "oklch(0.65 0.18 220)",
    items: ["IR language — irreversibility contracts", "Contract validation — pre/post conditions", "Hash invariants — state integrity", "Execution determinism — reproducibility"],
    position: "bottom",
  },
];

export default function WhatIsObsidia() {
  const [activeLayer, setActiveLayer] = useState<string | null>("X108");

  const selectedLayer = OS_LAYERS.find((l) => l.id === activeLayer);

  return (
    <div className="flex flex-col gap-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="pt-4">
        <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-2">Obsidia Labs — Architecture</div>
        <h1 className="font-mono font-bold text-3xl text-foreground mb-2">What is Obsidia?</h1>
        <p className="text-muted-foreground font-mono text-sm max-w-2xl">
          A governance kernel for autonomous agents. It solves a fundamental problem: agents that act faster than humans can verify.
        </p>
      </div>

      {/* Problem */}
      <div className="panel p-5">
        <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-4">The Problem — Agents Act Faster Than Humans Can Verify</div>
        <div className="grid grid-cols-3 gap-4">
          {PROBLEM_CASES.map((c) => (
            <div key={c.title} className="flex flex-col gap-2 p-3 rounded" style={{ background: "oklch(0.12 0.02 0)", border: "1px solid oklch(0.20 0.02 0)" }}>
              <div className="text-2xl">{c.icon}</div>
              <div className="font-mono text-xs font-bold text-foreground">{c.title}</div>
              <div className="text-[10px] text-muted-foreground leading-relaxed">{c.desc}</div>
              <div className="text-[10px] font-mono font-bold" style={{ color: c.color }}>{c.cost}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Solution */}
      <div className="panel p-5">
        <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-4">The Solution — Guard X-108</div>
        <div className="grid grid-cols-2 gap-4">
          {SOLUTION_PRINCIPLES.map((p) => (
            <div key={p.id} className="flex flex-col gap-2 p-3 rounded" style={{ background: "oklch(0.12 0.02 145)", border: "1px solid oklch(0.72 0.18 145 / 0.2)" }}>
              <div className="font-mono text-xs font-bold" style={{ color: "oklch(0.72 0.18 145)" }}>{p.title}</div>
              <div className="font-mono text-[10px] px-2 py-1 rounded" style={{ background: "oklch(0.10 0.01 240)", color: "oklch(0.72 0.18 145)" }}>{p.formula}</div>
              <div className="text-[10px] text-muted-foreground leading-relaxed">{p.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Architecture Stack Interactive */}
      <div className="panel p-5">
        <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-4">Architecture — OS0 → OS4 Stack</div>
        <div className="grid grid-cols-12 gap-4">
          <div className="col-span-4 flex flex-col gap-1">
            {OS_LAYERS.map((layer) => (
              <button
                key={layer.id}
                onClick={() => setActiveLayer(layer.id)}
                className="flex items-center gap-3 px-3 py-2.5 rounded text-left transition-all"
                style={{
                  background: activeLayer === layer.id ? (layer.highlight ? "oklch(0.14 0.04 145)" : "oklch(0.15 0.02 220)") : "oklch(0.12 0.01 240)",
                  border: "1px solid " + (activeLayer === layer.id ? (layer.highlight ? "oklch(0.72 0.18 145 / 0.5)" : "oklch(0.65 0.18 220 / 0.4)") : "oklch(0.18 0.01 240)"),
                }}
              >
                <span className="text-[9px] font-mono font-bold w-10 flex-shrink-0" style={{ color: layer.highlight ? "oklch(0.72 0.18 145)" : "oklch(0.50 0.01 240)" }}>
                  {layer.id}
                </span>
                <span className="text-[10px] font-mono" style={{ color: layer.highlight ? "oklch(0.72 0.18 145)" : "oklch(0.65 0.01 240)" }}>
                  {layer.title.split(" — ")[1]}
                </span>
              </button>
            ))}
          </div>
          <div className="col-span-8">
            {selectedLayer && (
              <div className="p-4 rounded h-full" style={{ background: selectedLayer.highlight ? "oklch(0.12 0.03 145)" : "oklch(0.12 0.01 240)", border: "1px solid " + (selectedLayer.highlight ? "oklch(0.72 0.18 145 / 0.3)" : "oklch(0.20 0.01 240)") }}>
                <div className="font-mono text-sm font-bold mb-3" style={{ color: selectedLayer.highlight ? "oklch(0.72 0.18 145)" : "oklch(0.65 0.18 220)" }}>
                  {selectedLayer.title}
                </div>
                <div className="flex flex-col gap-2">
                  {selectedLayer.items.map((item) => (
                    <div key={item} className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground">
                      <div className="w-1 h-1 rounded-full flex-shrink-0" style={{ background: selectedLayer.highlight ? "oklch(0.72 0.18 145)" : "oklch(0.65 0.18 220)" }} />
                      {item}
                    </div>
                  ))}
                </div>
                {selectedLayer.id === "X108" && (
                  <div className="mt-4 p-3 rounded text-[10px] font-mono" style={{ background: "oklch(0.10 0.01 240)", color: "oklch(0.72 0.18 145)" }}>
                    X-108 sits between OS2 (Runtime) and OS3 (Audit).<br />
                    No action can bypass it. No layer can skip it.
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Rule */}
      <div className="panel p-5 flex flex-col gap-3">
        <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest">Structural Rule — No Layer Can Skip Another</div>
        <div className="flex items-center gap-2 font-mono text-sm flex-wrap">
          {["OS4", "→", "OS2", "→", "X108", "→", "execution", "→", "OS3"].map((step, i) => (
            <span
              key={i}
              className="px-2 py-1 rounded text-[11px]"
              style={{
                background: step === "X108" ? "oklch(0.14 0.04 145)" : step === "→" ? "transparent" : "oklch(0.14 0.01 240)",
                color: step === "X108" ? "oklch(0.72 0.18 145)" : step === "→" ? "oklch(0.35 0.01 240)" : "oklch(0.65 0.01 240)",
                border: step !== "→" ? "1px solid " + (step === "X108" ? "oklch(0.72 0.18 145 / 0.4)" : "oklch(0.20 0.01 240)") : "none",
              }}
            >
              {step}
            </span>
          ))}
        </div>
        <div className="text-[10px] text-muted-foreground font-mono">
          OS4 cannot directly execute. It must go through OS2 runtime, then X-108 guard, then execution, then OS3 proof.
        </div>
      </div>

      {/* Canonical Diagram */}
      <div className="panel p-5">
        <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-4">Canonical Diagram — Complete OS0 → OS4 Stack</div>
        <div className="grid grid-cols-2 gap-6">
          {/* ASCII Stack */}
          <div className="font-mono text-xs leading-relaxed" style={{ color: "oklch(0.55 0.01 240)" }}>
            <pre style={{ color: "inherit", fontSize: "11px", lineHeight: "1.8" }}>
{`HUMAN / WORLD
       │
       ▼
OS4 ─ Interface / Simulation / Worlds
       │
       ▼
OS3 ─ Audit / Proof / Verification
       │
       ▼`}
            </pre>
            <pre style={{ color: "oklch(0.72 0.18 145)", fontSize: "11px", lineHeight: "1.8", fontWeight: "bold" }}>
{`X108 ─ Temporal Guard (BLOCK/HOLD/ALLOW)`}
            </pre>
            <pre style={{ color: "inherit", fontSize: "11px", lineHeight: "1.8" }}>
{`       │
       ▼
OS2 ─ Runtime / Decision Engine
       │
       ▼
OS1 ─ Structure / Registry / Agents
       │
       ▼
OS0 ─ Invariants / IR / Contracts`}
            </pre>
          </div>
          {/* Tests by layer */}
          <div className="space-y-2">
            <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-3">Tests by Layer</div>
            {[
              { layer: "OS0", tests: ["Unit tests — IR contracts", "Unit tests — hash invariants"], color: "oklch(0.65 0.18 220)" },
              { layer: "OS1", tests: ["Unit tests — agent registry", "Unit tests — world adapters"], color: "oklch(0.65 0.18 220)" },
              { layer: "OS2", tests: ["Unit tests — decision pipeline", "Stress tests — runtime"], color: "oklch(0.65 0.18 220)" },
              { layer: "X108", tests: ["Scenario tests — BLOCK/HOLD/ALLOW", "Stress tests — invariant checks"], color: "oklch(0.72 0.18 145)", highlight: true },
              { layer: "OS3", tests: ["Replay tests — hash verification", "Proof tests — merkle integrity"], color: "oklch(0.65 0.18 220)" },
              { layer: "OS4", tests: ["Scenario tests — world simulations", "Integration tests — full pipeline"], color: "oklch(0.65 0.18 220)" },
            ].map(l => (
              <div key={l.layer} className="flex items-start gap-3 p-2 rounded" style={{ background: l.highlight ? "oklch(0.12 0.03 145)" : "oklch(0.10 0.01 240)", border: "1px solid " + (l.highlight ? "oklch(0.72 0.18 145 / 0.3)" : "oklch(0.16 0.01 240)") }}>
                <span className="text-[9px] font-mono font-bold w-8 flex-shrink-0 pt-0.5" style={{ color: l.color }}>{l.layer}</span>
                <div className="space-y-0.5">
                  {l.tests.map(t => (
                    <div key={t} className="text-[10px] font-mono text-muted-foreground">{t}</div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Nav */}
      <div className="flex gap-3 pb-4">
        <Link href="/decision-lifecycle" className="px-4 py-2 rounded font-mono text-sm font-bold" style={{ background: "oklch(0.72 0.18 145)", color: "oklch(0.10 0.01 240)" }}>
            See the Decision Lifecycle →
          </Link>
        <Link href="/simulation-worlds" className="px-4 py-2 rounded font-mono text-sm border" style={{ background: "transparent", color: "oklch(0.72 0.18 145)", borderColor: "oklch(0.72 0.18 145 / 0.5)" }}>
            Run a simulation →
          </Link>
      </div>
    </div>
  );
}
