// lib/core/invariants.ts
export const INVARIANTS = {
  HIERARCHY: 'BLOCK > HOLD > ALLOW',
  X108_TEMPORAL_LOCK: 30, // secondes
  MAX_DRAWDOWN: 0.10,     // 10%
  MAX_POSITION_SIZE: 0.20, // 20%
  STOP_LOSS: 0.03         // 3%
} as const;

export type Decision = 'BLOCK' | 'HOLD' | 'EXECUTE';
