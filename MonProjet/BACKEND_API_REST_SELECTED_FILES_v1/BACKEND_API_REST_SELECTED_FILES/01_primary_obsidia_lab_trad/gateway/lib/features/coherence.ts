// lib/features/coherence.ts
import { MarketData } from './volatility';

export function computeCoherence(data: MarketData[]): number {
  if (data.length < 5) return 1.0;

  // Simulation de cohérence entre indicateurs (ex: RSI vs Price Action)
  // Dans un vrai système, on calculerait la corrélation.
  // Ici on simule une valeur basée sur la tendance récente.
  const lastPrices = data.slice(-5).map(d => d.close);
  const isTrending = lastPrices.every((p, i, arr) => i === 0 || p >= arr[i-1]) || 
                     lastPrices.every((p, i, arr) => i === 0 || p <= arr[i-1]);
  
  return isTrending ? 0.95 : 0.65;
}
