// lib/gates/x108TemporalLock.ts
import { GateResult } from './integrityGate';

export async function x108TemporalLock(lastExecutionTime: number): Promise<GateResult> {
  const LOCK_PERIOD = 30 * 1000; // 30 seconds
  const now = Date.now();
  const elapsed = now - lastExecutionTime;

  if (elapsed < LOCK_PERIOD) {
    return {
      status: 'HOLD',
      reason: `X-108 Temporal Lock active. Wait ${Math.ceil((LOCK_PERIOD - elapsed) / 1000)}s.`
    };
  }

  return { status: 'PASS' };
}
