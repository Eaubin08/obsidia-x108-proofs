// lib/gates/integrityGate.ts
export interface GateResult {
  status: 'PASS' | 'BLOCK' | 'HOLD';
  reason?: string;
}

export async function integrityGate(coherence: number): Promise<GateResult> {
  if (coherence < 0.3) {
    return {
      status: 'BLOCK',
      reason: 'Low coherence: market data unreliable'
    };
  }
  
  return { status: 'PASS' };
}
