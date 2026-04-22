/**
 * useDecisionStream.ts — OS4 v20
 * React hook that polls the tRPC stream.getEvents endpoint every 1.2 seconds.
 * Replaces the WebSocket approach which is incompatible with the Manus tunnel proxy.
 * Provides identical live-stream UX via HTTP polling.
 */
import { useState, useEffect, useRef, useCallback } from "react";
import { trpc } from "@/lib/trpc";

export interface LiveDecisionEvent {
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

export interface StreamStats {
  total: number;
  block: number;
  hold: number;
  allow: number;
  blockRate: number;
  holdRate: number;
  allowRate: number;
}

interface UseDecisionStreamResult {
  events: LiveDecisionEvent[];
  stats: StreamStats;
  connected: boolean;
  latency: number;
}

const MAX_EVENTS = 50;
const POLL_INTERVAL_MS = 1200;

export function useDecisionStream(): UseDecisionStreamResult {
  const [events, setEvents] = useState<LiveDecisionEvent[]>([]);
  const [stats, setStats] = useState<StreamStats>({
    total: 0, block: 0, hold: 0, allow: 0,
    blockRate: 0, holdRate: 0, allowRate: 0,
  });
  const [connected, setConnected] = useState(false);
  const [latency, setLatency] = useState(0);
  const seenIdsRef = useRef<Set<string>>(new Set());
  const lastPollRef = useRef<number>(Date.now());

  // tRPC polling — refetchInterval drives the "live" feel
  const { data, isSuccess, isError } = trpc.stream.getEvents.useQuery(
    { limit: 50 },
    {
      refetchInterval: POLL_INTERVAL_MS,
      refetchIntervalInBackground: true,
      staleTime: 0,
    }
  );

  useEffect(() => {
    if (isSuccess) {
      setConnected(true);
      const now = Date.now();
      setLatency(now - lastPollRef.current);
      lastPollRef.current = now;
    }
    if (isError) {
      setConnected(false);
    }
  }, [isSuccess, isError]);

  const updateStats = useCallback((evts: LiveDecisionEvent[]) => {
    const block = evts.filter(e => e.guard.decision === "BLOCK").length;
    const hold = evts.filter(e => e.guard.decision === "HOLD").length;
    const allow = evts.filter(e => e.guard.decision === "ALLOW").length;
    const total = evts.length;
    setStats({
      total,
      block,
      hold,
      allow,
      blockRate: total > 0 ? block / total : 0,
      holdRate: total > 0 ? hold / total : 0,
      allowRate: total > 0 ? allow / total : 0,
    });
  }, []);

  useEffect(() => {
    if (!data || data.length === 0) return;

    // Cast server data to client type (same shape)
    const incoming = data as unknown as LiveDecisionEvent[];

    // Find new events not yet seen
    const newEvents = incoming.filter(e => !seenIdsRef.current.has(e.id));
    if (newEvents.length === 0) return;

    // Mark as seen
    newEvents.forEach(e => seenIdsRef.current.add(e.id));

    // Prepend new events (newest first) and cap at MAX_EVENTS
    setEvents(prev => {
      const merged = [...newEvents.slice().reverse(), ...prev].slice(0, MAX_EVENTS);
      updateStats(merged);
      return merged;
    });
  }, [data, updateStats]);

  return { events, stats, connected, latency };
}
