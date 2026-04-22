import React, { useState } from "react";
import type { CommandParams } from "./CommandPanel";

// ─── Types ────────────────────────────────────────────────────────────────────
export interface BeforeAfterResult {
  // Bloc 2 — Verdict métier
  marketVerdict: string;        // ex: "EXECUTE_LONG", "AUTHORIZE", "PAY"
  agentProposal?: string;       // proposition textuelle de l'agent
  metierMetrics?: Record<string, number | string>;

  // Bloc 3 — Gate souverain X-108
  x108Gate: "ALLOW" | "HOLD" | "BLOCK";
  x108Reason?: string;
  x108ViolationCode?: string;
  severity?: string;

  // Bloc 4 — Preuve
  traceId?: string;
  ticketId?: string;
  stateHash?: string;
  merkleRoot?: string;
  source: "python" | "os4_local_fallback" | "fallback_only_debug";
  attestationRef?: string;
  // Replay — format "scenarioId:seed" — utilisé pour le deep-link Simuler
  replayRef?: string;
}

interface BeforeAfterPanelProps {
  params: CommandParams;
  result: BeforeAfterResult;
  loading?: boolean;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
const GATE_COLOR: Record<string, string> = {
  ALLOW: "#4ade80",
  HOLD:  "#fbbf24",
  BLOCK: "#f87171",
};

const SOURCE_COLOR: Record<string, string> = {
  python:              "oklch(0.72 0.18 145)",
  os4_local_fallback:  "oklch(0.75 0.18 75)",
  fallback_only_debug: "oklch(0.75 0.18 75)",
};

const DOMAIN_COLOR: Record<string, string> = {
  trading: "oklch(0.65 0.18 220)",
  bank:    "oklch(0.75 0.18 75)",
  ecom:    "oklch(0.72 0.18 145)",
};

const MODE_LABEL: Record<string, string> = {
  brut:            "Brut — non exécutoire",
  gouverne:        "Gouverné",
  gouverne_preuve: "Gouverné + Preuve",
};

// ─── Composant ────────────────────────────────────────────────────────────────
export default function BeforeAfterPanel({ params, result, loading }: BeforeAfterPanelProps) {
  if (loading) {
    return (
      <div className="rounded p-4 flex items-center justify-center" style={{ background: "oklch(0.10 0.01 240)", border: "1px solid oklch(0.18 0.01 240)", minHeight: "120px" }}>
        <span className="font-mono text-xs" style={{ color: "oklch(0.45 0.01 240)" }}>⟳ Exécution en cours…</span>
      </div>
    );
  }

  const gateColor = GATE_COLOR[result.x108Gate] ?? "oklch(0.55 0.01 240)";
  const domainColor = DOMAIN_COLOR[params.domain] ?? "oklch(0.65 0.18 220)";
  const sourceColor = SOURCE_COLOR[result.source] ?? "oklch(0.55 0.01 240)";
  const isFallback = result.source !== "python";

  return (
    <div className="flex flex-col gap-2">
      {/* Label */}
      <div className="flex items-center gap-2">
        <span className="text-[9px] font-mono tracking-widest uppercase" style={{ color: "oklch(0.40 0.01 240)" }}>
          Résultat du run
        </span>
        {isFallback && (
          <span className="text-[9px] font-mono px-1.5 py-0.5 rounded" style={{ background: "oklch(0.12 0.08 75 / 0.3)", color: "oklch(0.75 0.18 75)", border: "1px solid oklch(0.75 0.18 75 / 0.3)" }}>
            ⚠ fallback — non souverain
          </span>
        )}
      </div>

      {/* 4 blocs horizontaux */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">

        {/* ── Bloc 1 : Input ── */}
        <div className="rounded p-3 flex flex-col gap-2" style={{ background: "oklch(0.11 0.01 240)", border: `1px solid ${domainColor}33` }}>
          <div className="text-[9px] font-mono font-bold tracking-widest uppercase" style={{ color: domainColor }}>
            1 · Input
          </div>
          <div className="flex flex-col gap-1">
            <Row label="Domaine"  value={params.domain.toUpperCase()} color={domainColor} />
            <Row label="Scénario" value={params.scenarioId.replace(/_/g, " ")} />
            <Row label="Mode"     value={MODE_LABEL[params.mode] ?? params.mode} />
            <Row label="Source"   value={params.source} color={sourceColor} />
            {params.domain === "trading" && params.taille !== undefined && (
              <Row label="Taille" value={`${params.taille.toLocaleString("fr-FR")} €`} />
            )}
            {params.domain === "bank" && params.montant !== undefined && (
              <Row label="Montant" value={`${params.montant.toLocaleString("fr-FR")} €`} />
            )}
            {params.domain === "ecom" && params.panier !== undefined && (
              <Row label="Panier" value={`${params.panier.toLocaleString("fr-FR")} €`} />
            )}
            {params.elapsed !== undefined && <Row label="Elapsed" value={`${params.elapsed}s`} />}
            {params.irreversible && <Row label="Irréversible" value="OUI" color="#f87171" />}
          </div>
        </div>

        {/* ── Bloc 2 : Verdict métier ── */}
        <div className="rounded p-3 flex flex-col gap-2" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
          <div className="text-[9px] font-mono font-bold tracking-widest uppercase" style={{ color: "oklch(0.55 0.01 240)" }}>
            2 · Verdict métier
          </div>
          <div className="flex flex-col gap-1">
            <div className="font-mono text-sm font-bold" style={{ color: "oklch(0.80 0.02 240)" }}>
              {result.marketVerdict}
            </div>
            {result.agentProposal && (
              <div className="text-[9px] font-mono leading-tight" style={{ color: "oklch(0.45 0.01 240)" }}>
                {result.agentProposal}
              </div>
            )}
            {result.metierMetrics && Object.entries(result.metierMetrics).slice(0, 4).map(([k, v]) => (
              <Row key={k} label={k} value={String(v)} />
            ))}
          </div>
        </div>

        {/* ── Bloc 3 : Gate souverain X-108 ── */}
        <div className="rounded p-3 flex flex-col gap-2" style={{ background: "oklch(0.11 0.01 240)", border: `1.5px solid ${gateColor}44` }}>
          <div className="text-[9px] font-mono font-bold tracking-widest uppercase" style={{ color: gateColor }}>
            3 · Gate X-108
          </div>
          <div className="flex flex-col gap-1">
            <div className="font-mono text-lg font-bold" style={{ color: gateColor }}>
              {result.x108Gate}
            </div>
            {result.severity && (
              <span className="text-[9px] font-mono px-1.5 py-0.5 rounded inline-block w-fit" style={{ background: `${gateColor}18`, color: gateColor, border: `1px solid ${gateColor}33` }}>
                {result.severity}
              </span>
            )}
            {result.x108Reason && (
              <div className="text-[9px] font-mono leading-tight" style={{ color: "oklch(0.50 0.01 240)" }}>
                {result.x108Reason}
              </div>
            )}
            {result.x108ViolationCode && (
              <div className="text-[9px] font-mono" style={{ color: "#f87171" }}>
                {result.x108ViolationCode}
              </div>
            )}
          </div>
        </div>

        {/* ── Bloc 4 : Preuve ── */}
        <div className="rounded p-3 flex flex-col gap-2" style={{ background: "oklch(0.11 0.01 240)", border: "1px solid oklch(0.18 0.01 240)" }}>
          <div className="text-[9px] font-mono font-bold tracking-widest uppercase" style={{ color: sourceColor }}>
            4 · Preuve
          </div>
          <div className="flex flex-col gap-1">
            <Row label="Source" value={result.source} color={sourceColor} />
            {result.traceId && <Row label="trace_id" value={result.traceId.slice(0, 12) + "…"} mono />}
            {result.ticketId && <Row label="ticket_id" value={result.ticketId.slice(0, 12) + "…"} mono />}
            {result.stateHash && <Row label="state_hash" value={result.stateHash.slice(0, 10) + "…"} mono />}
            {result.merkleRoot && <Row label="merkle_root" value={result.merkleRoot.slice(0, 10) + "…"} mono />}
            {result.attestationRef && <Row label="attestation" value={result.attestationRef.slice(0, 10) + "…"} mono />}
            {!result.traceId && !result.ticketId && (
              <div className="text-[9px] font-mono" style={{ color: "oklch(0.38 0.01 240)" }}>
                {params.mode === "brut" ? "Mode brut — aucune preuve émise" : "Aucune trace disponible"}
              </div>
            )}
          </div>
          {/* replayRef — visible uniquement si présent (mode gouverne/gouverne_preuve) */}
          {result.replayRef && (
            <ReplayRefBadge replayRef={result.replayRef} domain={params.domain} />
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Row helper ──────────────────────────────────────────────────────────────────────────────────
function Row({ label, value, color, mono }: { label: string; value: string; color?: string; mono?: boolean }) {
  return (
    <div className="flex items-center justify-between gap-1">
      <span className="text-[9px] font-mono" style={{ color: "oklch(0.38 0.01 240)" }}>{label}</span>
      <span className={`text-[9px] ${mono ? "font-mono" : ""} font-bold`} style={{ color: color ?? "oklch(0.65 0.02 240)" }}>
        {value}
      </span>
    </div>
  );
}

// ─── ReplayRefBadge ───────────────────────────────────────────────────────────────────────────────
// Affiche le replayRef avec un bouton copier et le deep-link Simuler complet
function ReplayRefBadge({ replayRef, domain }: { replayRef: string; domain: string }) {
  const [copied, setCopied] = useState(false);
  // Construire le deep-link complet depuis le replayRef
  // Format attendu : "scenarioId:seed" ou intentId (fallback)
  const parts = replayRef.split(":");
  const scenarioId = parts.length >= 2 ? parts[0] : null;
  const seed = parts.length >= 2 ? parts[1] : null;
  const deepLink = scenarioId && seed
    ? `/simuler?domain=${domain}&scenarioId=${scenarioId}&seed=${seed}&rerun=1`
    : null;

  function handleCopy() {
    const toCopy = deepLink ? `${window.location.origin}${deepLink}` : replayRef;
    navigator.clipboard.writeText(toCopy).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    }).catch(() => {});
  }

  return (
    <div className="mt-1 pt-2 flex flex-col gap-1" style={{ borderTop: "1px solid oklch(0.18 0.01 240)" }}>
      <div className="flex items-center justify-between gap-1">
        <span className="text-[9px] font-mono" style={{ color: "oklch(0.38 0.01 240)" }}>replay_ref</span>
        <button
          onClick={handleCopy}
          className="text-[9px] font-mono px-1.5 py-0.5 rounded"
          style={{
            background: copied ? "oklch(0.12 0.06 145 / 0.3)" : "oklch(0.14 0.01 240)",
            color: copied ? "oklch(0.72 0.18 145)" : "oklch(0.55 0.01 240)",
            border: `1px solid ${copied ? "oklch(0.72 0.18 145 / 0.3)" : "oklch(0.22 0.01 240)"}`,
            cursor: "pointer",
          }}
        >
          {copied ? "✓ copié" : "📋 copier"}
        </button>
      </div>
      <div className="font-mono text-[9px] break-all" style={{ color: "oklch(0.65 0.18 220)" }}>
        {replayRef}
      </div>
      {deepLink && (
        <a
          href={deepLink}
          className="text-[9px] font-mono underline"
          style={{ color: "oklch(0.55 0.01 240)" }}
        >
          → Ouvrir dans Simuler
        </a>
      )}
    </div>
  );
}