// lib/features/friction.ts
import { MarketData } from './volatility';

export function computeFriction(data: MarketData[]): number {
  if (data.length === 0) return 0.01;

  // Simulation de la friction (slippage + spread) basée sur le volume
  const avgVolume = data.reduce((acc, d) => acc + d.volume, 0) / data.length;
  const lastVolume = data[data.length - 1].volume;
  
  // Plus le volume est faible par rapport à la moyenne, plus la friction est élevée
  const ratio = avgVolume / (lastVolume || 1);
  return Math.min(0.05, 0.001 * ratio); 
}
