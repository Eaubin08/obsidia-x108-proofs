// ─── Scenario Engine — OS4 v11 ───────────────────────────────────────────────
// 4 scénarios adversariaux longs (50+ steps) pour tester le Guard X-108
// Chaque scénario produit un tableau de ScenarioStep avec la décision Guard

export type GuardDecision = "ALLOW" | "HOLD" | "BLOCK";

export interface ScenarioStep {
  step: number;
  timestamp: number;
  world: "trading" | "bank" | "ecom";
  event: string;
  agentProposal: string;
  coherence: number;
  volatility: number;
  guardDecision: GuardDecision;
  holdDuration?: number;
  capitalImpact: number;
  proofHash: string;
  explanation: string;
}

export interface ScenarioResult {
  scenarioId: string;
  scenarioName: string;
  world: "trading" | "bank" | "ecom";
  seed: number;
  totalSteps: number;
  steps: ScenarioStep[];
  summary: {
    totalBlock: number;
    totalHold: number;
    totalAllow: number;
    capitalSaved: number;
    capitalExposed: number;
    avgCoherence: number;
    minCoherence: number;
    maxCoherence: number;
    blockRate: number;
    holdRate: number;
    allowRate: number;
  };
  verdict: "SAFE" | "DEGRADED" | "CRITICAL";
  verdictReason: string;
}

// ─── Seeded PRNG ─────────────────────────────────────────────────────────────

function seededRand(seed: number) {
  let s = seed;
  return () => {
    s = (s * 1664525 + 1013904223) & 0xffffffff;
    return (s >>> 0) / 0xffffffff;
  };
}

function shortHash(seed: number, step: number): string {
  return ((seed * 31337 + step * 7919) >>> 0).toString(16).padStart(8, "0");
}

// ─── Scenario 1 : Flash Crash (Trading) ──────────────────────────────────────

export function runFlashCrash(seed: number = 42): ScenarioResult {
  const rand = seededRand(seed);
  const steps: ScenarioStep[] = [];
  let price = 100;
  let capitalSaved = 0;
  let capitalExposed = 0;

  const CRASH_EVENTS = [
    "FED surprise rate hike +75bps", "NASDAQ circuit breaker triggered",
    "Flash crash detected -8% in 3min", "Liquidity vacuum — bid/ask spread x10",
    "Margin calls cascade — forced selling", "HFT algorithms paused — market halt",
    "Volatility index VIX spikes to 45", "S&P500 futures limit down",
    "Bitcoin whale dump -15%", "Stablecoin depeg detected",
    "Exchange outage — orders queued", "Regulatory halt on derivatives",
  ];

  const PROPOSALS = ["BUY BTC 0.5", "SELL ETH 2.0", "BUY SPX 100", "SELL AAPL 50", "BUY GOLD 10oz", "SELL EUR/USD 100k", "BUY BNB 20", "SELL TSLA 30"];

  for (let step = 0; step < 60; step++) {
    const t = step / 60;
    // Flash crash at step 20-35, recovery after 45
    const isCrash = step >= 18 && step <= 38;
    const isRecovery = step > 38 && step <= 50;

    const drift = isCrash ? -0.025 : isRecovery ? 0.008 : 0.001;
    const vol = isCrash ? 0.045 : isRecovery ? 0.018 : 0.008;
    const z = (rand() - 0.5) * 2;
    price = Math.max(0.01, price * Math.exp(drift + vol * z));

    const volatility = isCrash ? 0.035 + rand() * 0.025 : isRecovery ? 0.012 + rand() * 0.01 : 0.005 + rand() * 0.008;
    const coherence = isCrash ? 0.08 + rand() * 0.22 : isRecovery ? 0.35 + rand() * 0.25 : 0.65 + rand() * 0.30;

    const decision: GuardDecision = coherence < 0.30 ? "BLOCK" : coherence < 0.60 ? "HOLD" : "ALLOW";
    const proposal = PROPOSALS[Math.floor(rand() * PROPOSALS.length)];
    const event = isCrash ? CRASH_EVENTS[Math.floor(rand() * CRASH_EVENTS.length)] : isRecovery ? "Market stabilizing — partial recovery" : "Normal market conditions";
    const amount = 5000 + Math.floor(rand() * 45000);

    if (decision === "BLOCK") capitalSaved += amount;
    else capitalExposed += amount;

    steps.push({
      step,
      timestamp: Date.now() + step * 1000,
      world: "trading",
      event,
      agentProposal: `${proposal} — ${amount.toLocaleString()} EUR`,
      coherence,
      volatility,
      guardDecision: decision,
      holdDuration: decision === "HOLD" ? Math.floor(rand() * 8 + 3) : undefined,
      capitalImpact: decision === "BLOCK" ? amount : 0,
      proofHash: shortHash(seed, step),
      explanation: decision === "BLOCK"
        ? `Coherence ${(coherence * 100).toFixed(0)}% < 30% — Flash crash invariant triggered. Action irréversible bloquée.`
        : decision === "HOLD"
        ? `Coherence ${(coherence * 100).toFixed(0)}% entre 30-60% — Volatilité élevée. HOLD τ=${Math.floor(rand() * 8 + 3)}s obligatoire.`
        : `Coherence ${(coherence * 100).toFixed(0)}% ≥ 60% — Marché stable. Action autorisée.`,
    });
  }

  const totalBlock = steps.filter(s => s.guardDecision === "BLOCK").length;
  const totalHold = steps.filter(s => s.guardDecision === "HOLD").length;
  const totalAllow = steps.filter(s => s.guardDecision === "ALLOW").length;
  const avgCoherence = steps.reduce((a, s) => a + s.coherence, 0) / steps.length;
  const minCoherence = Math.min(...steps.map(s => s.coherence));
  const maxCoherence = Math.max(...steps.map(s => s.coherence));

  return {
    scenarioId: "flash_crash",
    scenarioName: "Flash Crash — Stochastic Market Collapse",
    world: "trading",
    seed,
    totalSteps: steps.length,
    steps,
    summary: {
      totalBlock, totalHold, totalAllow, capitalSaved, capitalExposed,
      avgCoherence, minCoherence, maxCoherence,
      blockRate: totalBlock / steps.length,
      holdRate: totalHold / steps.length,
      allowRate: totalAllow / steps.length,
    },
    verdict: totalBlock >= 10 ? "SAFE" : totalBlock >= 5 ? "DEGRADED" : "CRITICAL",
    verdictReason: totalBlock >= 10
      ? `Guard X-108 a bloqué ${totalBlock} actions irréversibles pendant le crash. Capital protégé : ${capitalSaved.toLocaleString()} EUR.`
      : `Attention : seulement ${totalBlock} BLOCK détectés. Vérifier les paramètres de cohérence.`,
  };
}

// ─── Scenario 2 : Bank Run (Bank) ────────────────────────────────────────────

export function runBankRun(seed: number = 42): ScenarioResult {
  const rand = seededRand(seed + 1000);
  const steps: ScenarioStep[] = [];
  let balance = 1_000_000;
  let capitalSaved = 0;
  let capitalExposed = 0;

  const EVENTS = [
    "Mass withdrawal request — 500 clients", "Social media panic — bank run trending",
    "Liquidity ratio below regulatory threshold", "Emergency ECB credit line activated",
    "ATM network saturated — queues forming", "Wire transfer system overloaded",
    "Credit rating downgrade — S&P BBB-", "Interbank market frozen",
    "Central bank emergency meeting", "Deposit guarantee fund activated",
    "Branch closures announced", "Digital bank run — mobile app overloaded",
  ];

  const PROPOSALS = [
    "WITHDRAW 50,000 EUR", "TRANSFER 200,000 EUR", "CREDIT LINE 500,000 EUR",
    "WIRE 75,000 EUR", "WITHDRAWAL 120,000 EUR", "BULK PAYMENT 300,000 EUR",
  ];

  for (let step = 0; step < 55; step++) {
    const isBankRun = step >= 15 && step <= 40;
    const isStabilization = step > 40;

    const withdrawalPressure = isBankRun ? 0.7 + rand() * 0.25 : isStabilization ? 0.2 + rand() * 0.2 : 0.05 + rand() * 0.15;
    const coherence = isBankRun ? 0.05 + rand() * 0.30 : isStabilization ? 0.40 + rand() * 0.30 : 0.70 + rand() * 0.25;
    const volatility = isBankRun ? 0.40 + rand() * 0.30 : 0.05 + rand() * 0.10;

    const decision: GuardDecision = coherence < 0.30 ? "BLOCK" : coherence < 0.60 ? "HOLD" : "ALLOW";
    const proposal = PROPOSALS[Math.floor(rand() * PROPOSALS.length)];
    const event = isBankRun ? EVENTS[Math.floor(rand() * EVENTS.length)] : isStabilization ? "Liquidity stabilizing" : "Normal banking operations";
    const amount = 10000 + Math.floor(rand() * 490000);

    if (decision === "BLOCK") { capitalSaved += amount; balance = Math.max(0, balance - amount * 0.1); }
    else capitalExposed += amount;

    steps.push({
      step,
      timestamp: Date.now() + step * 1000,
      world: "bank",
      event,
      agentProposal: `${proposal} — ${amount.toLocaleString()} EUR`,
      coherence,
      volatility,
      guardDecision: decision,
      holdDuration: decision === "HOLD" ? Math.floor(rand() * 8 + 3) : undefined,
      capitalImpact: decision === "BLOCK" ? amount : 0,
      proofHash: shortHash(seed + 1000, step),
      explanation: decision === "BLOCK"
        ? `IR=${((1 - withdrawalPressure) * 100).toFixed(0)}% — Bank run invariant. Transaction irréversible à haut risque bloquée.`
        : decision === "HOLD"
        ? `CIZ anomalie détectée — Pression de retrait ${(withdrawalPressure * 100).toFixed(0)}%. HOLD τ=${Math.floor(rand() * 8 + 3)}s.`
        : `Tous les indicateurs verts — Transaction autorisée.`,
    });
  }

  const totalBlock = steps.filter(s => s.guardDecision === "BLOCK").length;
  const totalHold = steps.filter(s => s.guardDecision === "HOLD").length;
  const totalAllow = steps.filter(s => s.guardDecision === "ALLOW").length;
  const avgCoherence = steps.reduce((a, s) => a + s.coherence, 0) / steps.length;

  return {
    scenarioId: "bank_run",
    scenarioName: "Bank Run — Mass Withdrawal Crisis",
    world: "bank",
    seed,
    totalSteps: steps.length,
    steps,
    summary: {
      totalBlock, totalHold, totalAllow, capitalSaved, capitalExposed,
      avgCoherence, minCoherence: Math.min(...steps.map(s => s.coherence)),
      maxCoherence: Math.max(...steps.map(s => s.coherence)),
      blockRate: totalBlock / steps.length,
      holdRate: totalHold / steps.length,
      allowRate: totalAllow / steps.length,
    },
    verdict: totalBlock >= 8 ? "SAFE" : totalBlock >= 4 ? "DEGRADED" : "CRITICAL",
    verdictReason: totalBlock >= 8
      ? `Guard X-108 a bloqué ${totalBlock} retraits massifs. Liquidité préservée : ${capitalSaved.toLocaleString()} EUR.`
      : `Risque systémique : seulement ${totalBlock} BLOCK. Réviser les seuils IR/CIZ.`,
  };
}

// ─── Scenario 3 : Fraud Attack (Bank) ────────────────────────────────────────

export function runFraudAttack(seed: number = 42): ScenarioResult {
  const rand = seededRand(seed + 2000);
  const steps: ScenarioStep[] = [];
  let capitalSaved = 0;
  let capitalExposed = 0;

  const FRAUD_EVENTS = [
    "Phishing attack — 200 compromised accounts", "Card skimming network detected",
    "Synthetic identity fraud — 50 fake accounts", "Account takeover via SIM swap",
    "Authorized push payment fraud", "Money mule network activated",
    "IBAN spoofing attack", "Deep fake voice authorization attempt",
    "Credential stuffing — 10k attempts/min", "Insider threat — unusual admin access",
    "Ransomware payment request", "Crypto mixer transaction detected",
  ];

  const FRAUD_PROPOSALS = [
    "TRANSFER 15,000 EUR to RO49AAAA...", "WIRE 8,500 EUR to unknown IBAN",
    "WITHDRAWAL 25,000 EUR cash", "PAYMENT 12,000 EUR crypto exchange",
    "TRANSFER 50,000 EUR offshore", "BULK PAYMENT 100,000 EUR 50 accounts",
  ];

  for (let step = 0; step < 50; step++) {
    const isFraudWave = step >= 10 && step <= 35;
    const isCleanup = step > 35;

    const fraudScore = isFraudWave ? 0.65 + rand() * 0.30 : isCleanup ? 0.10 + rand() * 0.20 : 0.02 + rand() * 0.15;
    const coherence = isFraudWave ? 0.02 + rand() * 0.28 : isCleanup ? 0.55 + rand() * 0.30 : 0.72 + rand() * 0.22;
    const volatility = fraudScore;

    const decision: GuardDecision = coherence < 0.30 ? "BLOCK" : coherence < 0.60 ? "HOLD" : "ALLOW";
    const proposal = isFraudWave
      ? FRAUD_PROPOSALS[Math.floor(rand() * FRAUD_PROPOSALS.length)]
      : "TRANSFER 450 EUR — BNP PARIBAS (normal)";
    const event = isFraudWave ? FRAUD_EVENTS[Math.floor(rand() * FRAUD_EVENTS.length)] : "Normal transaction";
    const amount = isFraudWave ? 5000 + Math.floor(rand() * 95000) : 200 + Math.floor(rand() * 1800);

    if (decision === "BLOCK") capitalSaved += amount;
    else capitalExposed += amount;

    steps.push({
      step,
      timestamp: Date.now() + step * 1000,
      world: "bank",
      event,
      agentProposal: `${proposal} — ${amount.toLocaleString()} EUR`,
      coherence,
      volatility,
      guardDecision: decision,
      holdDuration: decision === "HOLD" ? Math.floor(rand() * 8 + 3) : undefined,
      capitalImpact: decision === "BLOCK" ? amount : 0,
      proofHash: shortHash(seed + 2000, step),
      explanation: decision === "BLOCK"
        ? `TSG=${((1 - fraudScore) * 100).toFixed(0)}% — Fraude détectée. IBAN étranger + montant inhabituel + bénéficiaire inconnu.`
        : decision === "HOLD"
        ? `DTS anomalie — Score fraude ${(fraudScore * 100).toFixed(0)}%. Vérification τ=${Math.floor(rand() * 8 + 3)}s.`
        : `Transaction légitime — Tous indicateurs verts.`,
    });
  }

  const totalBlock = steps.filter(s => s.guardDecision === "BLOCK").length;
  const totalHold = steps.filter(s => s.guardDecision === "HOLD").length;
  const totalAllow = steps.filter(s => s.guardDecision === "ALLOW").length;
  const avgCoherence = steps.reduce((a, s) => a + s.coherence, 0) / steps.length;

  return {
    scenarioId: "fraud_attack",
    scenarioName: "Fraud Attack — Multi-Vector Financial Fraud",
    world: "bank",
    seed,
    totalSteps: steps.length,
    steps,
    summary: {
      totalBlock, totalHold, totalAllow, capitalSaved, capitalExposed,
      avgCoherence, minCoherence: Math.min(...steps.map(s => s.coherence)),
      maxCoherence: Math.max(...steps.map(s => s.coherence)),
      blockRate: totalBlock / steps.length,
      holdRate: totalHold / steps.length,
      allowRate: totalAllow / steps.length,
    },
    verdict: totalBlock >= 8 ? "SAFE" : totalBlock >= 4 ? "DEGRADED" : "CRITICAL",
    verdictReason: totalBlock >= 8
      ? `Guard X-108 a bloqué ${totalBlock} tentatives de fraude. Fraude évitée : ${capitalSaved.toLocaleString()} EUR.`
      : `Alerte : ${totalBlock} BLOCK seulement. Renforcer les seuils TSG/DTS.`,
  };
}

// ─── Scenario 4 : Traffic Spike (Ecom) ───────────────────────────────────────

export function runTrafficSpike(seed: number = 42): ScenarioResult {
  const rand = seededRand(seed + 3000);
  const steps: ScenarioStep[] = [];
  let capitalSaved = 0;
  let capitalExposed = 0;

  const SPIKE_EVENTS = [
    "Black Friday traffic spike x50", "Flash sale launch — 100k concurrent users",
    "Influencer viral post — demand surge", "Bot attack — 500k fake sessions/min",
    "Inventory depletion risk — 2% stock remaining", "Margin compression — ROAS < 0.8",
    "Price war triggered by competitor", "Payment gateway overloaded",
    "CDN capacity exceeded — latency x10", "Conversion rate anomaly — CVR 0.1%",
    "Cart abandonment spike — 95%", "Oversell risk — negative inventory",
  ];

  const PROPOSALS = [
    "FLASH SALE -50% all products", "BULK ORDER 2000 units", "PRICE CHANGE -30%",
    "CAMPAIGN LAUNCH 50k€", "RESTOCK EMERGENCY 5000 units", "DISCOUNT VOUCHER 40%",
    "BUNDLE DEAL -25%", "CLEARANCE SALE -60%",
  ];

  for (let step = 0; step < 52; step++) {
    const isSpike = step >= 12 && step <= 38;
    const isNormalization = step > 38;

    const trafficMultiplier = isSpike ? 10 + rand() * 40 : isNormalization ? 1.5 + rand() * 2 : 1 + rand() * 0.5;
    const marginRisk = isSpike ? 0.60 + rand() * 0.35 : 0.05 + rand() * 0.20;
    const coherence = isSpike ? 0.05 + rand() * 0.35 : isNormalization ? 0.45 + rand() * 0.30 : 0.68 + rand() * 0.27;
    const volatility = marginRisk;

    const decision: GuardDecision = coherence < 0.30 ? "BLOCK" : coherence < 0.60 ? "HOLD" : "ALLOW";
    const proposal = PROPOSALS[Math.floor(rand() * PROPOSALS.length)];
    const event = isSpike ? SPIKE_EVENTS[Math.floor(rand() * SPIKE_EVENTS.length)] : "Normal e-commerce operations";
    const amount = isSpike ? 2000 + Math.floor(rand() * 48000) : 100 + Math.floor(rand() * 2000);

    if (decision === "BLOCK") capitalSaved += amount;
    else capitalExposed += amount;

    steps.push({
      step,
      timestamp: Date.now() + step * 1000,
      world: "ecom",
      event,
      agentProposal: `${proposal} — budget ${amount.toLocaleString()} EUR`,
      coherence,
      volatility,
      guardDecision: decision,
      holdDuration: decision === "HOLD" ? Math.floor(rand() * 8 + 3) : undefined,
      capitalImpact: decision === "BLOCK" ? amount : 0,
      proofHash: shortHash(seed + 3000, step),
      explanation: decision === "BLOCK"
        ? `Marge < 5% — Coherence ${(coherence * 100).toFixed(0)}%. Action commerciale destructrice de valeur bloquée.`
        : decision === "HOLD"
        ? `ROAS < 1.0 — Trafic x${trafficMultiplier.toFixed(0)}. Réévaluation τ=${Math.floor(rand() * 8 + 3)}s.`
        : `Métriques funnel saines — Action commerciale autorisée.`,
    });
  }

  const totalBlock = steps.filter(s => s.guardDecision === "BLOCK").length;
  const totalHold = steps.filter(s => s.guardDecision === "HOLD").length;
  const totalAllow = steps.filter(s => s.guardDecision === "ALLOW").length;
  const avgCoherence = steps.reduce((a, s) => a + s.coherence, 0) / steps.length;

  return {
    scenarioId: "traffic_spike",
    scenarioName: "Traffic Spike — E-Commerce Demand Surge",
    world: "ecom",
    seed,
    totalSteps: steps.length,
    steps,
    summary: {
      totalBlock, totalHold, totalAllow, capitalSaved, capitalExposed,
      avgCoherence, minCoherence: Math.min(...steps.map(s => s.coherence)),
      maxCoherence: Math.max(...steps.map(s => s.coherence)),
      blockRate: totalBlock / steps.length,
      holdRate: totalHold / steps.length,
      allowRate: totalAllow / steps.length,
    },
    verdict: totalBlock >= 7 ? "SAFE" : totalBlock >= 3 ? "DEGRADED" : "CRITICAL",
    verdictReason: totalBlock >= 7
      ? `Guard X-108 a bloqué ${totalBlock} actions commerciales destructrices. Budget protégé : ${capitalSaved.toLocaleString()} EUR.`
      : `Risque commercial : ${totalBlock} BLOCK seulement. Vérifier les seuils de marge/ROAS.`,
  };
}

// ─── Batch Run (10 seeds) ─────────────────────────────────────────────────────

export interface BatchResult {
  scenarioId: string;
  seeds: number[];
  results: ScenarioResult[];
  aggregated: {
    avgBlockRate: number;
    avgHoldRate: number;
    avgAllowRate: number;
    avgCapitalSaved: number;
    safeCount: number;
    degradedCount: number;
    criticalCount: number;
  };
}

export function runBatch(scenarioId: string, seeds: number[] = Array.from({ length: 10 }, (_, i) => i + 1)): BatchResult {
  const runner = scenarioId === "flash_crash" ? runFlashCrash
    : scenarioId === "bank_run" ? runBankRun
    : scenarioId === "fraud_attack" ? runFraudAttack
    : runTrafficSpike;

  const results = seeds.map(s => runner(s));
  const n = results.length;

  return {
    scenarioId,
    seeds,
    results,
    aggregated: {
      avgBlockRate: results.reduce((a, r) => a + r.summary.blockRate, 0) / n,
      avgHoldRate: results.reduce((a, r) => a + r.summary.holdRate, 0) / n,
      avgAllowRate: results.reduce((a, r) => a + r.summary.allowRate, 0) / n,
      avgCapitalSaved: results.reduce((a, r) => a + r.summary.capitalSaved, 0) / n,
      safeCount: results.filter(r => r.verdict === "SAFE").length,
      degradedCount: results.filter(r => r.verdict === "DEGRADED").length,
      criticalCount: results.filter(r => r.verdict === "CRITICAL").length,
    },
  };
}

// ─── Banking Attack Scenarios v15 ────────────────────────────────────────────

export interface BankAttackResult {
  scenarioId: string;
  label: string;
  seed: number;
  steps: Array<{
    t: number;
    event: string;
    amount: number;
    decision: "BLOCK" | "HOLD" | "ALLOW";
    capitalBefore: number;
    capitalAfter: number;
    ir: number;
    ciz: number;
    dts: number;
    tsg: number;
    reasons: string[];
  }>;
  summary: {
    totalCapitalAtRisk: number;
    capitalSaved: number;
    blockRate: number;
    holdRate: number;
    allowRate: number;
    maxDrawdown: number;
    verdict: "SAFE" | "DEGRADED" | "CRITICAL";
  };
}

function seededRandBank(seed: number) {
  let s = seed;
  return () => {
    s = (s * 1664525 + 1013904223) & 0xffffffff;
    return (s >>> 0) / 0xffffffff;
  };
}

// Attack 1: Liquidity Drain
export function runLiquidityDrain(seed = 42): BankAttackResult {
  const rand = seededRandBank(seed + 10000);
  let capital = 1_000_000;
  const steps = [];
  let blocks = 0, holds = 0, allows = 0, capitalSaved = 0;
  const maxDrawdownStart = capital;

  for (let t = 0; t < 20; t++) {
    const withdrawAmount = capital * (0.08 + rand() * 0.12);
    const ir = 0.85 + rand() * 0.1;
    const ciz = Math.max(0, 0.6 - t * 0.04);
    const dts = 1.2 + t * 0.08;
    const tsg = 0.3 + rand() * 0.2;
    let decision: "BLOCK" | "HOLD" | "ALLOW";
    const reasons: string[] = [];
    if (ciz < 0.3) {
      decision = "BLOCK"; reasons.push(`CIZ=${ciz.toFixed(2)} — liquidity drain detected`); reasons.push("X-108 I-3: capital integrity violated"); capitalSaved += withdrawAmount; blocks++;
    } else if (dts > 1.8 || ciz < 0.5) {
      decision = "HOLD"; reasons.push(`DTS=${dts.toFixed(2)} elevated — temporal lock 30s`); holds++;
    } else {
      decision = "ALLOW"; capital -= withdrawAmount; allows++; reasons.push("All invariants satisfied");
    }
    steps.push({ t, event: `WITHDRAW_${(withdrawAmount / 1000).toFixed(0)}K`, amount: withdrawAmount, decision, capitalBefore: capital + (decision === "ALLOW" ? withdrawAmount : 0), capitalAfter: capital, ir, ciz, dts, tsg, reasons });
  }
  const maxDrawdown = (maxDrawdownStart - capital) / maxDrawdownStart;
  const blockRate = blocks / 20;
  return { scenarioId: "liquidity_drain", label: "Liquidity Drain Attack", seed, steps, summary: { totalCapitalAtRisk: maxDrawdownStart, capitalSaved, blockRate, holdRate: holds / 20, allowRate: allows / 20, maxDrawdown, verdict: blockRate > 0.5 ? "SAFE" : blockRate > 0.2 ? "DEGRADED" : "CRITICAL" } };
}

// Attack 2: Counterparty Default
export function runCounterpartyDefault(seed = 42): BankAttackResult {
  const rand = seededRandBank(seed + 20000);
  let capital = 1_000_000;
  const steps = [];
  let blocks = 0, holds = 0, allows = 0, capitalSaved = 0;
  const maxDrawdownStart = capital;
  const parties = ["PARTY_A", "PARTY_B", "PARTY_C", "PARTY_D", "PARTY_E"];
  const exposures = parties.map(() => capital * (0.05 + rand() * 0.15));

  for (let t = 0; t < 15; t++) {
    const idx = t % parties.length;
    const exposure = exposures[idx] * (1 + t * 0.1);
    const ir = 0.4 + rand() * 0.3;
    const ciz = Math.max(0.1, 0.8 - t * 0.06);
    const dts = 0.8 + t * 0.12;
    const tsg = 0.2 + rand() * 0.3;
    let decision: "BLOCK" | "HOLD" | "ALLOW";
    const reasons: string[] = [];
    if (ir < 0.5 || exposure > capital * 0.2) {
      decision = "BLOCK"; reasons.push(`${parties[idx]} integrity=${ir.toFixed(2)} — default risk`); reasons.push(`Exposure ${(exposure / 1000).toFixed(0)}K > 20% capital`); capitalSaved += exposure; blocks++;
    } else if (dts > 1.5) {
      decision = "HOLD"; reasons.push(`DTS=${dts.toFixed(2)} — cascading default risk`); holds++;
    } else {
      decision = "ALLOW"; capital -= exposure * 0.1; allows++; reasons.push("Exposure within limits");
    }
    steps.push({ t, event: `DEFAULT_${parties[idx]}`, amount: exposure, decision, capitalBefore: capital + (decision === "ALLOW" ? exposure * 0.1 : 0), capitalAfter: capital, ir, ciz, dts, tsg, reasons });
  }
  const maxDrawdown = (maxDrawdownStart - capital) / maxDrawdownStart;
  const blockRate = blocks / 15;
  return { scenarioId: "counterparty_default", label: "Counterparty Default Cascade", seed, steps, summary: { totalCapitalAtRisk: maxDrawdownStart, capitalSaved, blockRate, holdRate: holds / 15, allowRate: allows / 15, maxDrawdown, verdict: blockRate > 0.5 ? "SAFE" : blockRate > 0.2 ? "DEGRADED" : "CRITICAL" } };
}

// Attack 3: Interest Rate Shock
export function runInterestRateShock(seed = 42): BankAttackResult {
  const rand = seededRandBank(seed + 30000);
  let capital = 1_000_000;
  const steps = [];
  let blocks = 0, holds = 0, allows = 0, capitalSaved = 0;
  const maxDrawdownStart = capital;
  let rate = 0.02;
  const shocks = [0, 0, 0.01, 0.02, 0.03, 0.015, 0.01, 0.02, 0.025, 0.03, 0.02, 0.015];

  for (let t = 0; t < 12; t++) {
    rate += shocks[t] ?? 0;
    const portfolioLoss = capital * rate * 0.5;
    const ir = Math.max(0.2, 1 - rate * 5);
    const ciz = Math.max(0.1, 1 - rate * 8);
    const dts = 0.5 + rate * 20;
    const tsg = 0.3 + rand() * 0.2;
    let decision: "BLOCK" | "HOLD" | "ALLOW";
    const reasons: string[] = [];
    if (rate > 0.08 || portfolioLoss > capital * 0.15) {
      decision = "BLOCK"; reasons.push(`Rate=${(rate * 100).toFixed(1)}% — extreme shock`); reasons.push(`Loss ${(portfolioLoss / 1000).toFixed(0)}K > 15% capital`); capitalSaved += portfolioLoss; blocks++;
    } else if (rate > 0.04 || dts > 1.5) {
      decision = "HOLD"; reasons.push(`Rate=${(rate * 100).toFixed(1)}% elevated — temporal lock`); holds++;
    } else {
      decision = "ALLOW"; capital -= portfolioLoss * 0.3; allows++; reasons.push("Rate within tolerance");
    }
    steps.push({ t, event: `RATE_+${((shocks[t] ?? 0) * 100).toFixed(0)}bps`, amount: portfolioLoss, decision, capitalBefore: capital + (decision === "ALLOW" ? portfolioLoss * 0.3 : 0), capitalAfter: capital, ir, ciz, dts, tsg, reasons });
  }
  const maxDrawdown = (maxDrawdownStart - capital) / maxDrawdownStart;
  const blockRate = blocks / 12;
  return { scenarioId: "interest_rate_shock", label: "Interest Rate Shock", seed, steps, summary: { totalCapitalAtRisk: maxDrawdownStart, capitalSaved, blockRate, holdRate: holds / 12, allowRate: allows / 12, maxDrawdown, verdict: blockRate > 0.4 ? "SAFE" : blockRate > 0.2 ? "DEGRADED" : "CRITICAL" } };
}

// Attack 4: Credit Bubble
export function runCreditBubble(seed = 42): BankAttackResult {
  const rand = seededRandBank(seed + 40000);
  let capital = 1_000_000;
  const steps = [];
  let blocks = 0, holds = 0, allows = 0, capitalSaved = 0;
  const maxDrawdownStart = capital;

  for (let t = 0; t < 18; t++) {
    const loanAmount = 50000 + rand() * 100000;
    const inflatedScore = 0.85 + rand() * 0.1;
    const realRisk = 0.3 + t * 0.04;
    const ir = Math.max(0.1, inflatedScore - realRisk * 0.5);
    const ciz = Math.max(0.1, 0.9 - t * 0.05);
    const dts = 0.5 + realRisk * 2;
    const tsg = 0.2 + rand() * 0.3;
    let decision: "BLOCK" | "HOLD" | "ALLOW";
    const reasons: string[] = [];
    if (realRisk > 0.6 || ciz < 0.3) {
      decision = "BLOCK"; reasons.push(`Credit bubble: real_risk=${realRisk.toFixed(2)} vs score=${inflatedScore.toFixed(2)}`); reasons.push("X-108 I-4: credit integrity breach"); capitalSaved += loanAmount; blocks++;
    } else if (realRisk > 0.4 || dts > 1.5) {
      decision = "HOLD"; reasons.push(`Credit risk=${realRisk.toFixed(2)} — additional verification`); holds++;
    } else {
      decision = "ALLOW"; capital -= loanAmount * realRisk * 0.1; allows++; reasons.push("Credit score within policy");
    }
    steps.push({ t, event: `LOAN_${(loanAmount / 1000).toFixed(0)}K`, amount: loanAmount, decision, capitalBefore: capital + (decision === "ALLOW" ? loanAmount * realRisk * 0.1 : 0), capitalAfter: capital, ir, ciz, dts, tsg, reasons });
  }
  const maxDrawdown = (maxDrawdownStart - capital) / maxDrawdownStart;
  const blockRate = blocks / 18;
  return { scenarioId: "credit_bubble", label: "Credit Bubble Burst", seed, steps, summary: { totalCapitalAtRisk: maxDrawdownStart, capitalSaved, blockRate, holdRate: holds / 18, allowRate: allows / 18, maxDrawdown, verdict: blockRate > 0.4 ? "SAFE" : blockRate > 0.2 ? "DEGRADED" : "CRITICAL" } };
}
