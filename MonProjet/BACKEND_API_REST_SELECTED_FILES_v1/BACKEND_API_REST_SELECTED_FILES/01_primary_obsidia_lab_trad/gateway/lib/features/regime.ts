// lib/features/regime.ts
import { MarketData } from './volatility';

export type MarketRegime = 'BULL' | 'BEAR' | 'RANGE';

export function detectRegime(data: MarketData[]): MarketRegime {
  if (data.length < 20) return 'RANGE';

  const window = data.slice(-20);
  const first = window[0].close;
  const last = window[window.length - 1].close;
  const change = (last - first) / first;

  if (change > 0.02) return 'BULL';
  if (change < -0.02) return 'BEAR';
  return 'RANGE';
}
