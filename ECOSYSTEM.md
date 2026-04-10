# Obsidia Ecosystem — Intégration des Trois Dépôts

**Version :** 1.0.0 · **Date :** 2026-04-03

---

## Vue d'Ensemble

L'écosystème Obsidia repose sur trois dépôts distincts qui forment une chaîne de gouvernance ex ante complète :

| Dépôt | Rôle | Langage | Statut |
|---|---|---|---|
| **[agi-vision](https://github.com/Eaubin08/agi-vision)** | Agents cognitifs + latent space | TypeScript | Production |
| **[obsidia-x108-proofs](https://github.com/Eaubin08/obsidia-x108-proofs)** | Preuves formelles + noyau déterministe | Lean 4, TLA+, Python | Public |
| **[obsidia-engine-proof-core](https://github.com/Eaubin08/obsidia-engine-proof-core)** | Implémentation + tests complets | Python, TypeScript | Développement |

---

## Architecture Globale

```
┌─────────────────────────────────────────────────────────────────┐
│                     OBSIDIA ECOSYSTEM                           │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│   AGI-VISION         │  ← Agents Cognitifs
│  (TypeScript)        │     • MarketDataAgent
├──────────────────────┤     • LiquidityAgent
│ • Agents (27)        │     • VolatilityAgent
│ • Latent Space       │     • PatternAgent
│ • Decision Routing   │     • SentimentAgent
│ • Sigma Bridge       │     • ... (20+ plus)
└──────────┬───────────┘
           │
           │ Confidence Scores
           │ Decision Vectors
           │
           ▼
┌──────────────────────────────────────────────────────────────────┐
│                   SIGMA ENGINE (v18.9.1)                        │
│  Dynamic Stability Monitor — Pont entre IA et Kernel            │
├──────────────────────────────────────────────────────────────────┤
│ • Velocity Band Control (τ_min=0.05, τ_max=5.0)                 │
│ • Acceleration Limit (accel_limit=0.60)                         │
│ • Coherence Stationarity Check                                  │
│ • Fallback-1 Detection                                          │
└──────────┬───────────────────────────────────────────────────────┘
           │
           │ Stabilized Vectors
           │ Verdict Probabilities
           │
           ▼
┌──────────────────────────────────────────────────────────────────┐
│            X-108 KERNEL (DETERMINISTIC CORE)                    │
│  Frozen Decision Governance — Preuves Formelles                 │
├──────────────────────────────────────────────────────────────────┤
│ • Lean 4 Proofs (33 théorèmes, 0 sorry)                         │
│ • TLA+ Verification (1.2M états, 0 violation)                   │
│ • RFC 3161 Anchoring (Merkle Root)                              │
│ • Dual Obsidia (Veto Protocol)                                  │
│ • Decision ID + Trace ID (Auditabilité)                         │
└──────────┬───────────────────────────────────────────────────────┘
           │
           │ Canonical Decision Envelope
           │ • decision_id
           │ • market_verdict (ACT/HOLD/BLOCK)
           │ • x108_gate (ALLOW/DENY)
           │ • attestation_ref (RFC 3161)
           │ • agent_votes (27 confidences)
           │
           ▼
┌──────────────────────────────────────────────────────────────────┐
│                    EXECUTION LAYER                              │
│  Banking / Trading / E-Commerce / Governance                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Flux de Données Détaillé

### 1. Agents Cognitifs → Sigma Engine

**Source :** `agi-vision/agents/*.ts`

Chaque agent produit un tuple `(verdict, confidence, reasoning)` :

```typescript
interface AgentVote {
  agent_id: string;           // "MarketDataAgent"
  layer: "Observation" | "Interpretation" | "Proof" | "Governance";
  verdict: "BUY" | "HOLD" | "BLOCK";
  confidence: number;         // [0.0, 1.0]
  claim: string;              // "Market trending up 3%"
  severity?: "LOW" | "MED" | "HIGH";
}
```

**Exemple :** MarketDataAgent vote `(BUY, 0.85, "Price momentum positive")`

---

### 2. Sigma Engine → Stabilisation

**Source :** `obsidia-x108-proofs/sigma/` + `obsidia-engine-proof-core/agents/obsidia_sigma_v130.py`

Sigma applique trois contraintes :

| Contrainte | Formule | Effet |
|---|---|---|
| **Vanishing Acceleration** | `\|dv/dt\| ≤ accel_limit` | Pas de retournements brutaux |
| **Velocity Band** | `τ_min ≤ τ ≤ τ_max` | Stabilité temporelle |
| **Coherence Stationarity** | `hash(state_t) ≠ hash(state_{t-1})` | Détection de boucles |

**Résultat :** Vecteur stabilisé `v_stable = σ(v_raw, τ, accel_limit)`

---

### 3. Kernel X-108 → Décision Déterministe

**Source :** `obsidia-x108-proofs/proofs/lean/Obsidia.lean` + `obsidia-engine-proof-core/server/python_agents/guard.py`

Le kernel applique les règles de gouvernance :

```lean
theorem x108_determinism :
  ∀ (input : CanonicalInput),
  ∃! (decision : CanonicalDecision),
  decide(input) = decision
```

**Résultat :** Décision `(decision_id, market_verdict, x108_gate, attestation_ref, agent_votes)`

---

### 4. Attestation RFC 3161

**Source :** `obsidia-x108-proofs/proofs/verifiers/verify_merkle.py`

Chaque décision est scellée cryptographiquement :

```
Merkle Root = SHA256(
  SHA256(decision_1) ||
  SHA256(decision_2) ||
  ...
  SHA256(decision_n)
)

RFC 3161 Timestamp = TSA.sign(Merkle Root, timestamp)
```

**Résultat :** Immuabilité prouvée + Auditabilité complète

---

## Intégration Concrète

### Scénario : Transaction Bancaire Suspecte

**Étape 1 : Agents Cognitifs Votent**

```python
# agi-vision/agents/
agents = [
  MarketDataAgent(price=105, volume=2.5M),
  LiquidityAgent(spread=0.02),
  SentimentAgent(news_score=-0.3),
  # ... 24 autres agents
]

votes = [agent.vote() for agent in agents]
# → [
#   {"agent": "MarketDataAgent", "verdict": "BUY", "confidence": 0.72},
#   {"agent": "LiquidityAgent", "verdict": "HOLD", "confidence": 0.55},
#   {"agent": "SentimentAgent", "verdict": "BLOCK", "confidence": 0.81},
#   ...
# ]
```

**Étape 2 : Sigma Stabilise**

```python
# obsidia-engine-proof-core/agents/obsidia_sigma_v130.py
sigma = SigmaEngine(config=sigma_config.json)

stabilized_votes = sigma.stabilize(
  raw_votes=votes,
  tau=0.3,
  accel_limit=0.60
)
# → Filtre les votes extrêmes, détecte les contradictions
```

**Étape 3 : Kernel X-108 Décide**

```python
# obsidia-engine-proof-core/server/python_agents/guard.py
decision = kernel.decide(
  domain="banking",
  input_state=transaction_state,
  agent_votes=stabilized_votes
)
# → {
#   "decision_id": "dec_20260403_001",
#   "market_verdict": "HOLD",
#   "x108_gate": "ALLOW",
#   "reason_code": "CONSENSUS_WEAK",
#   "severity": "MED",
#   "agent_votes": {...},
#   "attestation_ref": "RFC3161:2026-04-03T12:34:56Z"
# }
```

**Étape 4 : Attestation Merkle**

```python
# obsidia-x108-proofs/proofs/verifiers/verify_merkle.py
merkle_root = compute_merkle_root([decision])
timestamp = tsa.sign(merkle_root)
# → Immuable, vérifiable publiquement
```

---

## Fichiers Clés par Dépôt

### agi-vision (Production)

```
agi-vision/
├── agents/
│   ├── MarketDataAgent.ts
│   ├── LiquidityAgent.ts
│   ├── VolatilityAgent.ts
│   ├── SentimentAgent.ts
│   ├── PatternAgent.ts
│   └── ... (22 autres)
├── latent/
│   ├── LatentSpace.ts
│   ├── VectorNormalization.ts
│   └── EmbeddingCache.ts
├── routing/
│   ├── DecisionRouter.ts
│   └── ConfidenceAggregator.ts
└── sigma/
    └── SigmaBridge.ts
```

**Responsabilités :**
- Générer les votes bruts des agents
- Maintenir l'espace latent cohérent
- Router les décisions vers Sigma

---

### obsidia-x108-proofs (Public)

```
obsidia-x108-proofs/
├── proofs/
│   ├── lean/Obsidia.lean           (33 théorèmes)
│   ├── tla/X108.tla                (1.2M états)
│   └── verifiers/
│       ├── verify_merkle.py
│       ├── verify_decision.py
│       └── verify_all.py
├── sigma/
│   ├── obsidia_sigma_v130.py       (Sigma Engine)
│   ├── sigma_monitor.py
│   ├── sigma_config.json
│   └── stress_test_results.json
├── examples/
│   ├── trading_bullish.json
│   ├── bank_suspicious.json
│   └── ecom_normal.json
└── docs/
    ├── KERNEL_OVERVIEW.md
    ├── SIGMA.md
    ├── AUDIT_GUIDE.md
    └── LIMITS.md
```

**Responsabilités :**
- Exposer les preuves formelles
- Documenter le noyau X-108
- Fournir des outils de vérification publics
- Tester Sigma en conditions réelles

---

### obsidia-engine-proof-core (Développement)

```
obsidia-engine-proof-core/
├── agents/
│   ├── obsidia_sigma_v130.py       (Sigma complet)
│   ├── sigma_monitor.py
│   ├── sigma_config.json
│   └── sigma_dashboard.py
├── server/
│   ├── python_agents/
│   │   ├── guard.py                (Kernel X-108)
│   │   ├── contracts.py            (Types)
│   │   └── protocols.py            (Pipelines)
│   └── canonical/
│       ├── canonicalPipeline.ts
│       └── canonicalEngine.ts
├── tests/
│   ├── test_agents_functional.py
│   ├── test_invariants_against_engine.py
│   ├── test_sigma_v18_9.py
│   ├── adversarial/
│   │   ├── test_consensus_split.py
│   │   ├── test_merkle_collision.py
│   │   └── test_monotonic_break.py
│   └── engines.test.ts
└── proofs/
    └── V18_9/
        ├── sigma_dashboard.png
        └── stress_test_results.json
```

**Responsabilités :**
- Implémenter le kernel complet
- Tester exhaustivement (1M+ cas)
- Générer les rapports ProofKit
- Valider Sigma en production

---

## Dépendances Entre Dépôts

```
agi-vision
    ↓ (agent votes)
    
obsidia-engine-proof-core
    ↓ (Sigma stabilization)
    ↓ (Kernel decision)
    
obsidia-x108-proofs
    ↓ (public verification)
    
End Users / Auditors
```

**Flux Unidirectionnel :**
- agi-vision → produit les votes
- obsidia-engine-proof-core → les stabilise et décide
- obsidia-x108-proofs → les vérifie publiquement

**Pas de dépendance inverse** — chaque dépôt est autonome dans son rôle.

---

## Vérification Croisée

### Test 1 : Cohérence Sigma

```bash
# Depuis obsidia-engine-proof-core
python3 tests/test_sigma_v18_9.py

# Vérifie que Sigma ne change pas les verdicts corrects
# Résultat attendu : 10/10 PASS
```

### Test 2 : Déterminisme Kernel

```bash
# Depuis obsidia-engine-proof-core
python3 tests/test_invariants_against_engine.py

# Vérifie que X-108 produit toujours la même décision
# pour la même entrée
# Résultat attendu : 6/6 PASS
```

### Test 3 : Vérification Publique

```bash
# Depuis obsidia-x108-proofs
python3 proofs/verifiers/verify_all.py

# Vérifie les preuves Lean, TLA+, Merkle
# Résultat attendu : ALL PASS
```

---

## Cas d'Usage Intégré

### Scénario 1 : Audit Régulateur

**Qui :** Régulateur financier  
**Quoi :** Vérifier qu'une décision de blocage était justifiée  
**Comment :**

1. Obtenir le `decision_id` de la transaction bloquée
2. Consulter `obsidia-x108-proofs/examples/bank_suspicious.json`
3. Exécuter `python3 proofs/verifiers/verify_decision.py`
4. Lire les 27 votes d'agents + le verdict Sigma + la décision X-108
5. Vérifier le Merkle Root via `verify_merkle.py`

**Résultat :** Preuve cryptographique que la décision était déterministe et justifiée.

---

### Scénario 2 : Intégration Nouvelle Banque

**Qui :** Nouvelle institution financière  
**Quoi :** Intégrer Obsidia dans leur pipeline de compliance  
**Comment :**

1. Cloner `obsidia-engine-proof-core`
2. Adapter `server/python_agents/guard.py` pour leur domaine
3. Entraîner les 27 agents sur leurs données
4. Tester avec `tests/adversarial/` (1M+ cas)
5. Déployer avec Sigma Engine (`agents/obsidia_sigma_v130.py`)
6. Publier les résultats dans `obsidia-x108-proofs/examples/`

**Résultat :** Gouvernance ex ante prouvée, auditable, déterministe.

---

### Scénario 3 : Recherche Académique

**Qui :** Chercheur en gouvernance algorithmique  
**Quoi :** Valider les preuves formelles  
**Comment :**

1. Cloner `obsidia-x108-proofs`
2. Lire `proofs/lean/Obsidia.lean` (33 théorèmes)
3. Vérifier `proofs/tla/X108.tla` (1.2M états)
4. Consulter `docs/LIMITS.md` pour les vecteurs non couverts
5. Contribuer des améliorations via PR

**Résultat :** Validation académique, publication possible.

---

## Roadmap d'Intégration

| Phase | Dépôt | Tâche | ETA |
|---|---|---|---|
| **Phase 1** | agi-vision | Finaliser les 27 agents | Q2 2026 |
| **Phase 2** | obsidia-engine-proof-core | Compléter les 2 théorèmes Lean | Q2 2026 |
| **Phase 3** | obsidia-x108-proofs | Publier les exemples complets | Q3 2026 |
| **Phase 4** | Tous | Intégration avec institutions réelles | Q4 2026 |

---

## Ressources

- **Documentation Sigma :** [`obsidia-x108-proofs/docs/SIGMA.md`](docs/SIGMA.md)
- **Guide d'Audit :** [`obsidia-x108-proofs/docs/AUDIT_GUIDE.md`](docs/AUDIT_GUIDE.md)
- **Preuves Lean :** [`obsidia-x108-proofs/proofs/lean/Obsidia.lean`](proofs/lean/Obsidia.lean)
- **Spécification TLA+ :** [`obsidia-x108-proofs/proofs/tla/X108.tla`](proofs/tla/X108.tla)
- **Exemples :** [`obsidia-x108-proofs/examples/`](examples/)

---

## Contact

Pour des questions sur l'intégration, l'audit ou la contribution :

**Email :** contact@obsidia.io  
**GitHub :** [@Eaubin08](https://github.com/Eaubin08)

---

**Dernière mise à jour :** 2026-04-03
