// lib/features/volatility.ts
export interface MarketData {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export function computeVolatility(data: MarketData[], window = 24): number {
  if (data.length < 2) return 0;
  
  const returns = data.slice(-window).map((d, i, arr) => 
    i > 0 ? Math.log(d.close / arr[i-1].close) : 0
  );
  
  const mean = returns.reduce((a, b) => a + b, 0) / returns.length;
  const variance = returns.reduce((acc, r) => acc + Math.pow(r - mean, 2), 0) / returns.length;
  
  return Math.sqrt(variance) * Math.sqrt(252); // Annualisée
}
