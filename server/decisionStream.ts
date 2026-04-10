/**
 * decisionStream.ts — OS4 v17
 * WebSocket server that broadcasts live decision events to ControlTower.
 * Emits one DecisionEvent per second (or on real engine triggers).
 */
import { WebSocketServer, WebSocket } from "ws";
import type { Server } from "http";

// ─── Types ────────────────────────────────────────────────────────────────────
export interface DecisionEvent {
  id: string;
  timestamp: number;
  domain: "TRADING" | "BANKING" | "ECOMMERCE";
  world: {
    price?: number;
    volatility: number;
    liquidity: number;
    regime: string;
  };
  agent: {
    id: string;
    proposal: string;
    amount?: number;
  };
  engine: {
    coherence: number;
    risk: number;
    stateConsistency: boolean;
  };
  guard: {
    decision: "BLOCK" | "HOLD" | "ALLOW";
    reason: string;
    holdDuration?: number;
  };
  proof: {
    hash: string;
    lean4: boolean;
    tlaPlus: boolean;
    merkleLeaf: string;
  };
}

// ─── Simulation helpers ────────────────────────────────────────────────────────
const DOMAINS: DecisionEvent["domain"][] = ["TRADING", "BANKING", "ECOMMERCE"];
const TRADING_PROPOSALS = ["BUY 0.5 BTC", "SELL 1.2 ETH", "BUY 10 SOL", "SELL 0.3 BTC", "BUY 5 BNB"];
const BANKING_PROPOSALS = ["TRANSFER €12,500", "INVEST €50,000", "WITHDRAW €8,000", "DEPOSIT €25,000"];
const ECOM_PROPOSALS = ["PRICE CHANGE +15%", "BULK ORDER $4,200", "REFUND $890", "FLASH SALE −30%"];

function randomBetween(min: number, max: number) {
  return Math.random() * (max - min) + min;
}

function generateDecisionEvent(): DecisionEvent {
  const domain = DOMAINS[Math.floor(Math.random() * DOMAINS.length)];
  const volatility = randomBetween(0.05, 0.65);
  const coherence = randomBetween(0.10, 0.95);
  const risk = randomBetween(0.05, 0.90);
  const liquidity = randomBetween(0.30, 0.95);

  // Guard logic (mirrors server-side Guard X-108)
  let decision: "BLOCK" | "HOLD" | "ALLOW";
  let reason: string;
  let holdDuration: number | undefined;

  if (volatility > 0.45 || coherence < 0.25) {
    decision = "BLOCK";
    reason = volatility > 0.45
      ? `volatility=${(volatility * 100).toFixed(1)}% exceeds 45% threshold`
      : `coherence=${coherence.toFixed(2)} below 0.25 minimum`;
  } else if (volatility > 0.30 || coherence < 0.50 || risk > 0.70) {
    decision = "HOLD";
    holdDuration = 10;
    reason = volatility > 0.30
      ? `volatility=${(volatility * 100).toFixed(1)}% > 30% — temporal lock τ=10s`
      : risk > 0.70
      ? `risk=${risk.toFixed(2)} > 0.70 — monitoring period`
      : `coherence=${coherence.toFixed(2)} borderline — re-evaluation pending`;
  } else {
    decision = "ALLOW";
    reason = `all invariants satisfied (coh=${coherence.toFixed(2)}, vol=${(volatility * 100).toFixed(1)}%, risk=${risk.toFixed(2)})`;
  }

  const proposals =
    domain === "TRADING" ? TRADING_PROPOSALS :
    domain === "BANKING" ? BANKING_PROPOSALS :
    ECOM_PROPOSALS;
  const proposal = proposals[Math.floor(Math.random() * proposals.length)];

  const hash = Math.random().toString(16).slice(2, 10) + Math.random().toString(16).slice(2, 10);
  const merkleLeaf = "0x" + Math.random().toString(16).slice(2, 18);

  return {
    id: `evt_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
    timestamp: Date.now(),
    domain,
    world: {
      price: domain === "TRADING" ? Math.round(randomBetween(40000, 80000)) : undefined,
      volatility,
      liquidity,
      regime: volatility > 0.40 ? "CRISIS" : volatility > 0.25 ? "VOLATILE" : coherence > 0.70 ? "BULL" : "NEUTRAL",
    },
    agent: {
      id: `agent_${domain.toLowerCase()}_${Math.floor(Math.random() * 3) + 1}`,
      proposal,
      amount: domain === "TRADING" ? Math.round(randomBetween(1000, 50000)) : undefined,
    },
    engine: {
      coherence,
      risk,
      stateConsistency: coherence > 0.30,
    },
    guard: {
      decision,
      reason,
      holdDuration,
    },
    proof: {
      hash,
      lean4: true,
      tlaPlus: true,
      merkleLeaf,
    },
  };
}

// ─── WebSocket Server ─────────────────────────────────────────────────────────
let wss: WebSocketServer | null = null;
let broadcastInterval: ReturnType<typeof setInterval> | null = null;

// Keep a rolling buffer of the last 50 events for new connections
const eventBuffer: DecisionEvent[] = [];
const BUFFER_SIZE = 50;

function broadcast(event: DecisionEvent) {
  // Add to buffer
  eventBuffer.push(event);
  if (eventBuffer.length > BUFFER_SIZE) eventBuffer.shift();

  if (!wss) return;
  const payload = JSON.stringify({ type: "decision", data: event });
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(payload);
    }
  });
}

export function initDecisionStream(httpServer: Server) {
  wss = new WebSocketServer({ server: httpServer, path: "/ws/decisions" });

  wss.on("connection", (ws) => {
    // Send last 20 buffered events on connect for immediate display
    const recent = eventBuffer.slice(-20);
    ws.send(JSON.stringify({ type: "history", data: recent }));

    ws.on("error", () => {/* ignore */});
  });

  // Broadcast a new decision event every 1.2 seconds
  broadcastInterval = setInterval(() => {
    broadcast(generateDecisionEvent());
  }, 1200);

  console.log("[DecisionStream] WebSocket server initialized at /ws/decisions");
}

// Allow external code to inject real engine decisions into the stream
export function emitDecisionEvent(event: DecisionEvent) {
  broadcast(event);
}

// Allow tRPC polling to read the current buffer (HTTP-compatible fallback)
export function getEventBuffer(limit = 50): DecisionEvent[] {
  return eventBuffer.slice(-limit);
}
