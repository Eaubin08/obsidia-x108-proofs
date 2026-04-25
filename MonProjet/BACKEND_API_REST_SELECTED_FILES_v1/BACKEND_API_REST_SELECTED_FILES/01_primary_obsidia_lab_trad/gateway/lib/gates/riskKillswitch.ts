// lib/gates/riskKillswitch.ts
import { GateResult } from './integrityGate';

export async function riskKillswitch(currentDrawdown: number, maxAllowed: number): Promise<GateResult> {
  if (currentDrawdown > maxAllowed) {
    return {
      status: 'BLOCK',
      reason: `Risk Killswitch triggered: Drawdown (${(currentDrawdown * 100).toFixed(2)}%) exceeds limit (${(maxAllowed * 100).toFixed(2)}%)`
    };
  }

  return { status: 'PASS' };
}
