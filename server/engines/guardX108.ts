import crypto from "crypto";
import { z } from "zod";

// ─── Zod Schemas ──────────────────────────────────────────────────────────────

export const X108Schema = z.object({
  tau: z.number(),           // threshold in seconds (≥0)
  elapsed: z.number(),       // time elapsed since intent creation
  irr: z.boolean(),          // irreversibility flag
  gate_active: z.boolean(),  // true when elapsed < tau AND irr=true
});

export const DecisionTicketSchema = z.object({
  intent_id: z.string(),
  domain: z.enum(["trading", "bank", "ecom", "system"]),
  decision: z.enum(["ALLOW", "HOLD", "BLOCK"]),
  reasons: z.array(z.string()),
  thresholds: z.record(z.string(), z.number()),
  x108: X108Schema,
  audit: z.object({
    hash_prev: z.string(),
    hash_now: z.string(),
    merkle_root: z.string(),
  anchor_ref: z.string().optional(),
  ts_utc: z.string(),
  // ts_utc is ISO 8601 UTC string
  }),
  replay_ref: z.string().optional(), // "seed:step"
});

export type DecisionTicket = z.infer<typeof DecisionTicketSchema>;
export type X108 = z.infer<typeof X108Schema>;

// ─── Hash utilities ───────────────────────────────────────────────────────────

export function sha256(data: string): string {
  return crypto.createHash("sha256").update(data, "utf8").digest("hex");
}

export function merkle2(a: string, b: string): string {
  return sha256(a + b);
}

export function computeMerkleRoot(hashes: string[]): string {
  if (hashes.length === 0) return sha256("empty");
  if (hashes.length === 1) return hashes[0];
  let layer = [...hashes];
  while (layer.length > 1) {
    const next: string[] = [];
    for (let i = 0; i < layer.length; i += 2) {
      const a = layer[i];
      const b = layer[i + 1] ?? layer[i]; // duplicate last if odd
      next.push(merkle2(a, b));
    }
    layer = next;
  }
  return layer[0];
}

// ─── Global hash chain state ──────────────────────────────────────────────────

let _chainHead = sha256("GENESIS_OS4_PLATFORM");
const _ticketHashes: string[] = [];

export function getChainHead(): string {
  return _chainHead;
}

export function resetChain(): void {
  _chainHead = sha256("GENESIS_OS4_PLATFORM");
  _ticketHashes.length = 0;
}

// ─── Guard X-108 Decision Engine ─────────────────────────────────────────────

export interface GuardInput {
  intent_id: string;
  domain: "trading" | "bank" | "ecom" | "system";
  metrics: Record<string, number>;
  thresholds: Record<string, number>;
  tau: number;          // seconds — mandatory hold duration
  elapsed: number;      // seconds since intent was created
  irr: boolean;         // is this an irreversible action?
  replay_ref?: string;
}

export function runGuard(input: GuardInput): DecisionTicket {
  const { intent_id, domain, metrics, thresholds, tau, elapsed, irr } = input;

  // X-108 gate: if irreversible AND not enough time elapsed → HOLD
  const gate_active = irr && elapsed < tau && tau >= 0;

  const reasons: string[] = [];
  let decision: "ALLOW" | "HOLD" | "BLOCK" = "ALLOW";

  // 1. Temporal gate check
  if (gate_active) {
    decision = "HOLD";
    reasons.push(`X-108: temporal gate active — ${(tau - elapsed).toFixed(1)}s remaining`);
  }

  // 2. Threshold checks (only if not already HOLD from gate)
  // Threshold keys use prefix convention: min_<metric> or max_<metric>
  // The metric name is extracted by stripping the prefix.
  if (decision !== "HOLD") {
    for (const [key, threshold] of Object.entries(thresholds)) {
      // Extract metric name: "min_ciz" → "ciz", "max_dts" → "dts"
      let metricName = key;
      let direction: "min" | "max" | null = null;
      if (key.startsWith("max_")) {
        metricName = key.slice(4);
        direction = "max";
      } else if (key.startsWith("min_")) {
        metricName = key.slice(4);
        direction = "min";
      }
      const value = metrics[metricName] ?? metrics[key];
      if (value === undefined) continue;
      if (direction === "max" && value > threshold) {
        decision = "BLOCK";
        reasons.push(`${metricName}: ${value.toFixed(4)} > max threshold ${threshold}`);
      } else if (direction === "min" && value < threshold) {
        decision = "BLOCK";
        reasons.push(`${metricName}: ${value.toFixed(4)} < min threshold ${threshold}`);
      }
    }
  }

  if (reasons.length === 0) {
    reasons.push("All checks passed");
  }

  // 3. Build audit trail
  const payload = JSON.stringify({ intent_id, domain, decision, metrics, thresholds, tau, elapsed, irr });
  const hash_now = sha256(_chainHead + payload);
  const hash_prev = _chainHead;

  _ticketHashes.push(hash_now);
  const merkle_root = computeMerkleRoot([..._ticketHashes]);
  _chainHead = hash_now;

  const ticket: DecisionTicket = {
    intent_id,
    domain,
    decision,
    reasons,
    thresholds,
    x108: { tau, elapsed, irr, gate_active },
    audit: {
      hash_prev,
      hash_now,
      merkle_root,
      anchor_ref: `os4:${domain}:${Date.now()}`,
      ts_utc: new Date().toISOString(),
    },
    replay_ref: input.replay_ref,
  };

  return ticket;
}

// ─── Replay Verifier ─────────────────────────────────────────────────────────

export interface ReplayResult {
  match: boolean;
  original_hash: string;
  replayed_hash: string;
  delta_ms: number;
}

export function verifyReplay(
  originalTicket: DecisionTicket,
  replayedTicket: DecisionTicket
): ReplayResult {
  return {
    match: originalTicket.audit.hash_now === replayedTicket.audit.hash_now,
    original_hash: originalTicket.audit.hash_now,
    replayed_hash: replayedTicket.audit.hash_now,
    delta_ms: 0,
  };
}
