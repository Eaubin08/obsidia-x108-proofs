// lib/simulation/simLite.ts
import { MarketData, computeVolatility } from '../features/volatility';

export interface SimulationResult {
  maxDrawdown: number;
  ruinProbability: number;
  expectedReturn: number;
  paths: number[][];
}

export interface TradeIntent {
  asset: string;
  amount: number;
  action: 'BUY' | 'SELL';
}

export async function runSimulation(
  intent: TradeIntent,
  marketData: MarketData[],
  numPaths = 1000
): Promise<SimulationResult> {
  // Real Monte Carlo based on market data
  const volatility = computeVolatility(marketData);
  const returns = marketData.slice(1).map((d, i) => (d.close - marketData[i].close) / marketData[i].close);
  const drift = returns.reduce((a, b) => a + b, 0) / returns.length;
  
  const paths: number[][] = [];
  let ruinCount = 0;
  let totalReturn = 0;
  let maxDD = 0;

  const initialCapital = 10000;
  const horizon = 30; // 30 days
  const dt = 1 / 252; // daily step

  for (let i = 0; i < numPaths; i++) {
    const path: number[] = [initialCapital];
    let currentCapital = initialCapital;
    
    for (let t = 0; t < horizon; t++) {
      // Geometric Brownian Motion
      const epsilon = Math.sqrt(-2 * Math.log(Math.random())) * Math.cos(2 * Math.PI * Math.random());
      const dailyReturn = (drift - 0.5 * Math.pow(volatility, 2)) * dt + volatility * Math.sqrt(dt) * epsilon;
      
      currentCapital *= (1 + dailyReturn);
      path.push(currentCapital);
      
      if (currentCapital < initialCapital * 0.5) {
        ruinCount++;
        break; // Stop path if ruined
      }
    }
    
    paths.push(path);
    totalReturn += (currentCapital - initialCapital) / initialCapital;
    
    const peak = Math.max(...path);
    const dd = (peak - currentCapital) / peak;
    if (dd > maxDD) maxDD = dd;
  }

  return {
    maxDrawdown: maxDD,
    ruinProbability: ruinCount / numPaths,
    expectedReturn: totalReturn / numPaths,
    paths: paths.slice(0, 5) // Return 5 paths for visualization
  };
}
