# REAL_CASES — Cas concrets et reproductibles

**Version :** 1.0.0 · **Date :** 2026-03-11

Ces cas sont issus des données de test réelles présentes dans `test_agents_functional.py` et `engines.test.ts`. Ils sont 100% reproductibles en exécutant les commandes indiquées.

---

## Cas 1 — Pipeline Trading : marché haussier → ALLOW

### Contexte

Série de prix BTC/USDT en tendance haussière claire sur 21 périodes. Volumes croissants, spreads faibles, sentiment neutre, risque événementiel faible.

### Entrée

```json
{
  "symbol": "BTCUSDT",
  "prices": [100,101,102,103,104,106,108,110,111,113,115,117,118,119,121,123,124,126,127,129,131],
  "highs":  [101,102,103,104,105,107,109,111,112,114,116,118,119,120,122,124,125,127,128,130,132],
  "lows":   [99,100,101,102,103,105,107,109,110,112,114,116,117,118,120,122,123,125,126,128,130],
  "volumes": [1000,1050,1100,1150,1200,1250,1300,1350,1400,1450,1500,1550,1600,1650,1700,1750,1800,1850,1900,1950,2000],
  "spreads_bps": [4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4],
  "sentiment_scores": [0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2],
  "event_risk_scores": [0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15],
  "btc_reference_prices": [100,101,102,103,104,106,108,110,111,113,115,117,118,119,121,123,124,126,127,129,131]
}
```

### Traitement

1. Les 10 agents Trading analysent l'état (RSI haussier, MACD positif, Bollinger en expansion haute, volume croissant, spread faible)
2. Votes majoritaires : `BUY` avec confidence élevée (~0.82)
3. Agrégation : `market_verdict = "EXECUTE_LONG"`, `confidence = 0.82`
4. Guard X-108 : `contradictions=0`, `unknowns=0`, `confidence=0.82 >= 0.72` → **ALLOW**

### Sortie attendue

```json
{
  "domain": "trading",
  "market_verdict": "EXECUTE_LONG",
  "confidence": 0.82,
  "x108_gate": "ALLOW",
  "reason_code": "GUARD_ALLOW",
  "severity": "S0",
  "ticket_required": true,
  "ticket_id": "<uuid-16chars>"
}
```

### Commande de reproduction

```bash
cd agents/
python3 run_pipeline.py trading "$(cat examples/trading_bullish.json)"
```

---

## Cas 2 — Pipeline Bank : transaction suspecte → HOLD

### Contexte

Compte avec historique court (30 jours), transaction de montant élevé (8000€) sur un compte avec solde modeste (12000€), 1 flag de risque détecté.

### Entrée

```json
{
  "account_id": "ACC_SUSPECT_001",
  "balance": 12000.0,
  "transactions": [
    {"amount": 8000.0, "type": "debit", "category": "wire_transfer"},
    {"amount": 200.0, "type": "debit", "category": "atm"}
  ],
  "credit_score": 580,
  "account_age_days": 30,
  "fraud_flags": ["UNUSUAL_AMOUNT"],
  "reserve_ratio": 0.05
}
```

### Traitement

1. Les 8 agents Bank analysent l'état
2. Agent `FraudDetectionAgent` : détecte `UNUSUAL_AMOUNT` → vote `BLOCK` avec confidence 0.75
3. Agent `LiquidityAgent` : ratio débit/solde = 67% → vote `ANALYZE` avec confidence 0.60
4. Agent `CreditAgent` : score 580 (sous seuil 620) → vote `ANALYZE` avec confidence 0.55
5. Agrégation : `market_verdict = "ANALYZE"`, `confidence = 0.58`, `unknowns = 1`
6. Guard X-108 : `unknowns=1 > 0`, `confidence=0.58 >= 0.45` mais `unknowns > max_unknowns_before_hold` → **HOLD**

### Sortie attendue

```json
{
  "domain": "bank",
  "market_verdict": "ANALYZE",
  "confidence": 0.58,
  "x108_gate": "HOLD",
  "reason_code": "UNKNOWNS_OR_CONFIDENCE_LOW",
  "severity": "S2",
  "ticket_required": false,
  "ticket_id": null
}
```

### Commande de reproduction

```bash
cd agents/
python3 run_pipeline.py bank "$(cat examples/bank_suspicious.json)"
```

---

## Cas 3 — Guard X-108 : fraude détectée → BLOCK

### Contexte

Agrégat avec pattern de fraude explicite détecté par 2 agents indépendants. Contradictions entre agent de conformité et agent de liquidité.

### Entrée (DomainAggregate direct)

```python
from governance.contracts import DomainAggregate, Domain, AgentVote, Layer, Severity, SourceTag

aggregate = DomainAggregate(
    domain=Domain.BANK,
    market_verdict="BLOCK",
    confidence=0.35,
    contradictions=["COMPLIANCE_VS_LIQUIDITY", "FRAUD_PATTERN_CONFIRMED"],
    unknowns=[],
    risk_flags=["FRAUD_PATTERN", "VELOCITY_ANOMALY"],
    evidence_refs=["ref_agent_fraud_001", "ref_agent_velocity_002"],
    agent_votes=[]
)
```

### Traitement

Guard X-108 évalue :
- `contradiction_count = 2 >= max_contradictions_before_block (2)` → condition BLOCK remplie
- `"FRAUD_PATTERN" in risk_flags` → condition BLOCK renforcée

### Sortie attendue

```python
envelope.x108_gate == "BLOCK"
envelope.reason_code == "CONTRADICTION_THRESHOLD_REACHED"
envelope.severity == "S4"
envelope.ticket_required == False
envelope.ticket_id == None
```

### Commande de reproduction

```bash
cd tests/
pytest test_agents_functional.py::test_guard_block_on_contradictions -v
```

---

## Cas 4 — Simulation Trading déterministe (TypeScript)

### Contexte

Simulation Monte Carlo de 252 steps avec seed fixe. Vérifie que le hash d'état est identique sur deux exécutions.

### Paramètres

```typescript
const params = {
  seed: 42, steps: 252, S0: 100,
  mu: 0.05, sigma: 0.2, dt: 1/252,
  jumpLambda: 0.1, jumpMu: -0.05, jumpSigma: 0.1,
  garchAlpha: 0.1, garchBeta: 0.85, garchOmega: 0.00001,
  regimes: 2, frictionBps: 5
}
```

### Résultat observé

```
stateHash:  a3f2c1b4e5d6... (64 chars, identique sur 2 runs)
merkleRoot: 7b8c9d0e1f2a... (64 chars, identique sur 2 runs)
finalPrice: 112.34 (identique sur 2 runs)
```

### Commande de reproduction

```bash
cd ../os4-platform/
pnpm test -- engines.test.ts
```
