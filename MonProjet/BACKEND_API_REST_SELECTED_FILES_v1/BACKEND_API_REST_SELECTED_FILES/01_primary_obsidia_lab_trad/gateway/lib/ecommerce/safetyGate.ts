// lib/ecommerce/safetyGate.ts
export interface AgentAction {
  id: string;
  agent_id: string;
  type: 'PURCHASE' | 'BID' | 'LIST';
  amount: number;
  recipient: string;
  timestamp: number;
  coherence: number;
}

export interface SafetyGateResult {
  decision: 'ALLOW' | 'BLOCK';
  reason: string;
  coherence: number;
  temporal_delta: number;
}

export interface TokenomicsModel {
  fee_rate: number;
  staker_share: number;
  treasury_share: number;
  buyback_share: number;
}

export function evaluateAction(
  action: AgentAction,
  previousAction: AgentAction | null
): SafetyGateResult {
  // Temporal Lock (10s minimum)
  const delta = (action.timestamp - (previousAction?.timestamp || 0)) / 1000; // in seconds
  
  if (delta < 10) {
    return {
      decision: 'BLOCK',
      reason: 'Temporal constraint: action too fast (<10s)',
      coherence: action.coherence,
      temporal_delta: delta
    };
  }

  // Coherence threshold (0.6 minimum)
  if (action.coherence < 0.6) {
    return {
      decision: 'BLOCK',
      reason: 'Low coherence: suspicious intent',
      coherence: action.coherence,
      temporal_delta: delta
    };
  }

  return {
    decision: 'ALLOW',
    reason: 'Action passed all gates',
    coherence: action.coherence,
    temporal_delta: delta
  };
}

export function calculateFees(
  transactionAmount: number,
  model: TokenomicsModel
): { totalFee: number; stakerReward: number; treasuryAmount: number; buybackAmount: number; } {
  const totalFee = transactionAmount * model.fee_rate;
  return {
    totalFee,
    stakerReward: totalFee * model.staker_share,
    treasuryAmount: totalFee * model.treasury_share,
    buybackAmount: totalFee * model.buyback_share
  };
}
