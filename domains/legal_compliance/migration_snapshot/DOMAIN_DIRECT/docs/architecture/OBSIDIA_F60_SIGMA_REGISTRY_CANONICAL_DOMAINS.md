# F60 — Sigma Registry Canonical Domains

**Palier:** F60  
**Registry:** `sigma/registry.py`  
**Date:** 2026-05-30  
**Sovereignty:** KX108_ONLY · readonly · advisory_only · no decision · no mutation  

---

## Canonical Domain Surface

The Sigma registry exposes four canonical domains. Each domain contains runtime agent instances that evaluate observations and produce advisory votes. No domain decides. No agent decides. All votes pass through `GuardX108` which is the sole decision authority.

---

## Domain: `bank`

| Property | Value |
|----------|-------|
| Display name | Bank / Risk / Transaction Safety |
| Implementation | RUNTIME_BOUND |
| Agent count | 12 |
| Decision authority | KX108_ONLY |

**Agents:**

| Agent ID | Role |
|----------|------|
| `TransactionContextAgent` | Transaction type and channel observation |
| `CounterpartyAgent` | Counterparty known/age analysis |
| `LiquidityExposureAgent` | Liquidity pressure assessment |
| `BehaviorShiftAgent` | Behavioral anomaly detection |
| `FraudPatternAgent` | Fraud score analysis |
| `LimitPolicyAgent` | Policy limit compliance |
| `RegionPolicyAgent` | Geographic policy gate |
| `VelocityAgent` | Transaction velocity analysis |
| `RecipientRiskAgent` | Recipient risk assessment |
| `CurrencyConversionAgent` | Currency exposure analysis |
| `DataQualityAgent` | Input data quality gate |
| `AnomalyScoreAgent` | Aggregate anomaly scoring |

---

## Domain: `trading`

| Property | Value |
|----------|-------|
| Display name | Trading / Market / Execution Safety |
| Implementation | RUNTIME_BOUND |
| Agent count | 17 |
| Decision authority | KX108_ONLY |

**Key agents (first 6):** `MarketDataAgent`, `LiquidityAgent`, `VolatilityAgent`, `OrderSizeAgent`, `MarketImpactAgent`, `SlippageAgent`

---

## Domain: `ecom`

| Property | Value |
|----------|-------|
| Display name | E-Commerce / Basket / Offer Safety |
| Implementation | RUNTIME_BOUND |
| Agent count | 12 |
| Decision authority | KX108_ONLY |

**Key agents (first 6):** `TrafficQualityAgent`, `BasketIntentAgent`, `OfferHealthAgent`, `PaymentRiskAgent`, `InventorySignalAgent`, `PricingAnomalyAgent`

---

## Domain: `gps_defense_aviation`

| Property | Value |
|----------|-------|
| Display name | GPS / Defense / Aviation Safety |
| Implementation | RUNTIME_BOUND |
| Agent count | 6 |
| Decision authority | KX108_ONLY |

**Agents:** `SourceAvailabilityAgent`, `TrajectoryIntegrityAgent`, `SourceConflictAgent`, `SpoofingDetectionAgent`, `IntegrityScoreAgent`, `AltitudeSpeedAgent`

---

## Shared Boundary — All Domains

```json
{
  "decision_authority": "KX108_ONLY",
  "readonly": true,
  "advisory_only": true,
  "allowed_to_decide": false,
  "emits_act": false,
  "emits_verdict": false,
  "kernel_mutation": false,
  "x108_mutation": false,
  "neo4j_write": false,
  "graphiti_write": false,
  "memory_write": false,
  "brody_decision": false
}
```

---

## API Reference

```python
from sigma.registry import (
    list_sigma_domains,    # () → list[str]
    get_sigma_domain,      # (str) → dict
    get_sigma_registry,    # () → dict
    validate_sigma_registry,  # () → dict
    build_agent_registry,  # () → dict[str, list[Agent]]  (pre-F60)
)
```

### `list_sigma_domains()`

```python
>>> list_sigma_domains()
['bank', 'trading', 'ecom', 'gps_defense_aviation']
```

### `get_sigma_domain("bank")`

```python
{
  "domain": "bank",
  "display_name": "Bank / Risk / Transaction Safety",
  "implementation_status": "RUNTIME_BOUND",
  "runtime_bound": true,
  "agent_count": 12,
  "agents": [
    {"id": "TransactionContextAgent", "role": "TransactionContextAgent",
     "runtime_bound": true, "advisory_only": true,
     "decision_authority": "KX108_ONLY", "emits_act": false, "emits_verdict": false},
    ...
  ],
  "boundary": { "decision_authority": "KX108_ONLY", "readonly": true, ... }
}
```

### `validate_sigma_registry()`

```python
{
  "status": "PASS",
  "canonical_domains_checked": ["bank", "trading", "ecom", "gps_defense_aviation"],
  "errors": [],
  "decision_authority": "KX108_ONLY",
  "readonly": true
}
```

---

## What Sigma Is NOT

| NOT | Reason |
|-----|--------|
| A decision engine | `GuardX108` decides; Sigma only votes |
| An ACT emitter | `emits_act=false` on every agent |
| A command executor | advisory votes only |
| A writer | no storage, no Neo4j, no Graphiti write |
| An orchestrator | no global dispatcher in F60 |

---

*F60 · Sigma Registry Canonical Domains · KX108_ONLY · 2026-05-30*
