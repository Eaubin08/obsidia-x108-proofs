// lib/execution/erc8004Builder.ts
import { ERC8004Intent, Features } from '../../types/erc8004';
import { Decision } from '../core/invariants';

export function buildIntent(
  agentId: string,
  decision: Decision,
  asset: string,
  amount: number,
  features: Features,
  simulation: any,
  gates: any[]
): ERC8004Intent {
  return {
    agentId,
    action: decision === 'EXECUTE' ? 'BUY' : 'HOLD',
    asset,
    amount,
    limitPrice: 0, // À remplir avec le prix actuel
    timestamp: Date.now(),
    signature: '0x' + Math.random().toString(16).slice(2), // Mock signature
    governanceProof: {
      features,
      simulation,
      gates
    }
  };
}
