# Exemples Concrets — Flux de Décision Obsidia

**Ce répertoire contient des exemples réels de décisions Obsidia**, du vote des agents à l'attestation cryptographique.

---

## Structure

```
examples/
├── README.md                              (ce fichier)
├── trading_bullish.json                   (Scénario Trading — Marché haussier)
├── bank_normal.json                       (Scénario Banking — Transaction normale)
├── bank_suspicious.json                   (Scénario Banking — Transaction suspecte)
├── ecom_normal.json                       (Scénario E-Commerce — Commande normale)
└── scenarios/
    └── complete_decision_flow.json        (Flux COMPLET — Tous les détails)
```

---

## Comment Lire les Exemples

### Étape 1 : Commencer par les Simples

**Fichier :** `bank_normal.json`

```bash
cat examples/bank_normal.json | jq '.' | head -30
```

**Ce qu'il contient :**
- État d'entrée minimal (montant, destination, profil client)
- Votes de 5 agents (observation + interprétation)
- Décision finale du kernel X-108

**Temps de lecture :** 5 min

---

### Étape 2 : Comparer Cas Normal vs Suspect

**Fichiers :** `bank_normal.json` vs `bank_suspicious.json`

```bash
# Comparer les votes
diff <(jq '.agent_votes' examples/bank_normal.json) \
     <(jq '.agent_votes' examples/bank_suspicious.json)
```

**Ce qu'on observe :**
- Les agents votent différemment selon le contexte
- Les confidences changent
- Le verdict final change

**Temps de lecture :** 10 min

---

### Étape 3 : Étudier le Flux Complet

**Fichier :** `scenarios/complete_decision_flow.json`

```bash
cat examples/scenarios/complete_decision_flow.json | jq '.' | less
```

**Ce qu'il contient :**
- **Input State** — État initial complet
- **Agent Votes** — 11 agents, 4 couches (Observation, Interprétation, Proof, Governance)
- **Sigma Engine Processing** — Stabilisation en détail
- **Kernel X-108 Decision** — Décision déterministe
- **Execution Outcome** — Résultat réel
- **Verification Checklist** — Toutes les vérifications

**Temps de lecture :** 30 min

---

## Vérifier les Exemples

### Vérifier la Syntaxe JSON

```bash
python3 -c "import json; json.load(open('examples/scenarios/complete_decision_flow.json'))" && echo "✓ Valid JSON"
```

### Vérifier avec le Vérificateur Obsidia

```bash
# Depuis le répertoire racine
python3 proofs/verifiers/verify_decision.py examples/scenarios/complete_decision_flow.json
```

**Sortie attendue :**
```
[INFO] Loading decision envelope...
[INFO] Verifying agent votes...
[SUCCESS] All 11 agents accounted for.
[INFO] Verifying Sigma stabilization...
[SUCCESS] Sigma constraints satisfied.
[INFO] Verifying kernel decision...
[SUCCESS] Decision is deterministic.
[INFO] Verifying attestation...
[SUCCESS] RFC 3161 timestamp valid.
[SUCCESS] All verifications passed.
```

---

## Anatomie d'une Décision Complète

### 1. Input State

```json
{
  "transaction_id": "TXN_20260403_001",
  "amount": 250000,
  "currency": "EUR",
  "source_account": "ACCT_12345",
  "destination_country": "KY",
  "customer_profile": {...},
  "market_conditions": {...}
}
```

**Rôle :** Entrée brute du système. Aucune interprétation.

---

### 2. Agent Votes (4 Couches)

#### Couche 1 : Observation (4 agents)

```json
{
  "agent_id": "MarketDataAgent",
  "verdict": "BLOCK",
  "confidence": 0.92,
  "reasoning": "Transaction amount 50x above average for this customer",
  "evidence": {
    "customer_avg": 5000,
    "this_transaction": 250000,
    "ratio": 50,
    "threshold": 10
  }
}
```

**Rôle :** Détection de faits bruts (anomalies, seuils dépassés).

---

#### Couche 2 : Interprétation (3 agents)

```json
{
  "agent_id": "PatternAgent",
  "verdict": "BLOCK",
  "confidence": 0.81,
  "reasoning": "Pattern matches known fraud signature #42 (sudden large transfer to tax haven)",
  "evidence": {
    "pattern_id": "FRAUD_42",
    "similarity_score": 0.87,
    "historical_fraud_rate": 0.94
  }
}
```

**Rôle :** Interprétation des faits (patterns, prédictions, sentiments).

---

#### Couche 3 : Proof (2 agents)

```json
{
  "agent_id": "ProofConsistencyAgent",
  "verdict": "BLOCK",
  "confidence": 0.79,
  "reasoning": "All high-confidence agents agree on BLOCK — consensus strong",
  "evidence": {
    "agents_voting_block": 4,
    "agents_voting_hold": 2,
    "agents_voting_allow": 0,
    "consensus_strength": 0.67
  }
}
```

**Rôle :** Vérification de la cohérence (consensus, intégrité).

---

#### Couche 4 : Governance (2 agents)

```json
{
  "agent_id": "PolicyScopeAgent",
  "verdict": "BLOCK",
  "confidence": 0.90,
  "reasoning": "Transaction violates AML policy #3 (large transfer to high-risk jurisdiction)",
  "evidence": {
    "policy_id": "AML_3",
    "violation_type": "high_risk_jurisdiction_transfer"
  }
}
```

**Rôle :** Application des politiques (AML, compliance).

---

### 3. Sigma Engine Processing

```json
{
  "version": "18.9.1",
  "config": {
    "tau_min": 0.05,
    "tau_max": 5.0,
    "accel_limit": 0.60
  },
  "stabilization_applied": {
    "vanishing_acceleration": {...},
    "velocity_band_control": {...},
    "coherence_stationarity": {...}
  },
  "stabilized_votes": {
    "BLOCK": 0.82,
    "HOLD": 0.15,
    "ALLOW": 0.03
  }
}
```

**Rôle :** Stabilisation des votes (pas de retournements brutaux, cohérence).

---

### 4. Kernel X-108 Decision

```json
{
  "decision_id": "DEC_20260403_001_BANKING",
  "market_verdict": "BLOCK",
  "x108_gate": "DENY",
  "reason_code": "CONSENSUS_STRONG_FRAUD_SIGNAL",
  "severity": "HIGH",
  "confidence": 0.82,
  "attestation": {
    "timestamp": "2026-04-03T14:32:16Z",
    "trace_id": "TRACE_20260403_001_BANKING",
    "attestation_ref": "RFC3161:20260403143216Z",
    "merkle_root": "8f2e7d1c9a3b5f6e4d2c1a0b9e8f7d6c",
    "signature": "ECDSA_P256_SHA256_SIGNATURE_HERE"
  }
}
```

**Rôle :** Décision déterministe + attestation cryptographique.

---

### 5. Execution Outcome

```json
{
  "action": "BLOCK_TRANSACTION",
  "status": "EXECUTED",
  "timestamp": "2026-04-03T14:32:17Z",
  "customer_notification": {...},
  "compliance_notification": {...}
}
```

**Rôle :** Résultat réel (action prise, notifications envoyées).

---

### 6. Verification Checklist

```json
{
  "kernel_determinism": { "status": "VERIFIED", "result": true },
  "agent_consensus": { "status": "VERIFIED", "result": true, "value": 0.82 },
  "sigma_stability": { "status": "VERIFIED", "result": true },
  "merkle_integrity": { "status": "VERIFIED", "result": true },
  "rfc3161_timestamp": { "status": "VERIFIED", "result": true },
  "audit_trail_complete": { "status": "VERIFIED", "result": true }
}
```

**Rôle :** Vérification que tout est correct (déterminisme, consensus, stabilité, intégrité).

---

## Cas d'Usage Pédagogiques

### Cas 1 : Comprendre le Consensus

**Fichier :** `scenarios/complete_decision_flow.json`

**Question :** Pourquoi le kernel décide BLOCK malgré un agent votant HOLD ?

**Réponse :** 
- 7 agents votent BLOCK (confidence moyenne 0.85)
- 3 agents votent HOLD (confidence moyenne 0.62)
- 1 agent vote ALLOW (confidence 0.55)
- Consensus = 7/11 = 0.64 > seuil 0.70 ? **Non**, mais confidence moyenne = 0.82 > seuil

Le kernel utilise **consensus + confidence moyenne**, pas juste le vote majoritaire.

---

### Cas 2 : Comprendre Sigma

**Fichier :** `scenarios/complete_decision_flow.json` → `sigma_engine_processing`

**Question :** Pourquoi Sigma change-t-il les votes ?

**Réponse :**
- Avant Sigma : confidence_mean = 0.78, std = 0.12
- Après Sigma : confidence_mean = 0.79, std = 0.10
- **Variance réduite de 17%** → Sigma a lissé les votes extrêmes

Sigma détecte les agents qui votent trop différemment des autres et les rapproche.

---

### Cas 3 : Comprendre l'Attestation

**Fichier :** `scenarios/complete_decision_flow.json` → `attestation`

**Question :** Comment vérifier que cette décision n'a pas été modifiée ?

**Réponse :**
1. Calculer le Merkle Root de la décision
2. Vérifier que `merkle_root = "8f2e7d1c9a3b5f6e4d2c1a0b9e8f7d6c"`
3. Vérifier la signature ECDSA avec la clé publique de Obsidia
4. Vérifier le timestamp RFC 3161 auprès de l'autorité de temps

Si tout match → Décision immuable et authentique.

---

## Comparaison des Scénarios

| Scénario | Verdict | Raison | Consensus |
|---|---|---|---|
| `bank_normal.json` | ALLOW | Transaction conforme | 0.95 |
| `bank_suspicious.json` | BLOCK | Montant anormal | 0.82 |
| `trading_bullish.json` | ALLOW | Marché haussier confirmé | 0.88 |
| `ecom_normal.json` | ALLOW | Commande normale | 0.91 |
| `complete_decision_flow.json` | BLOCK | Fraude détectée + consensus | 0.82 |

---

## Ressources

- **Guide d'Audit :** [`docs/AUDIT_GUIDE.md`](../docs/AUDIT_GUIDE.md)
- **Vérificateur :** [`proofs/verifiers/verify_decision.py`](../proofs/verifiers/verify_decision.py)
- **Sigma Engine :** [`sigma/obsidia_sigma_v130.py`](../sigma/obsidia_sigma_v130.py)
- **Kernel X-108 :** [`../obsidia-engine-proof-core/server/python_agents/guard.py`](https://github.com/Eaubin08/obsidia-engine-proof-core/blob/main/server/python_agents/guard.py)

---

## Prochaines Étapes

1. **Lire** `complete_decision_flow.json` en entier
2. **Vérifier** avec `python3 proofs/verifiers/verify_decision.py examples/scenarios/complete_decision_flow.json`
3. **Comparer** avec `bank_suspicious.json` pour voir les différences
4. **Auditer** les preuves Lean et TLA+ dans `proofs/`

---

**Dernière mise à jour :** 2026-04-03
