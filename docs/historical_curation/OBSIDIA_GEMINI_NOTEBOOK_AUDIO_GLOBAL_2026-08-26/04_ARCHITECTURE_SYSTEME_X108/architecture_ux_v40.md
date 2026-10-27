# OS4 — Obsidia Governance Platform
## Architecture UX v40 — Blueprint complet

**Généré le :** 2026-03-06  
**Version :** v40 (checkpoint 73714186)  
**Repository :** https://github.com/Eaubin08/Obsidia-lab-trad

---

## 1. Flux principal du système

```
MARKET (point d'entrée)
    ↓
AGENTS (observation)
    ↓
ANTICIPATION (prédiction)
    ↓
DECISIONS (pipeline Guard X-108)
    ↓
PROOF (Merkle anchor)
    ↓
CONTROL (supervision)
```

Ce flux correspond exactement à l'architecture du moteur Obsidia.

---

## 2. Navigation finale

| # | Page | Route | Description |
|---|------|--------|-------------|
| 1 | **Market** | `/market` | Porte d'entrée — choix du domaine |
| 2 | **Agents** | `/agents` | Alpha · Sentinel · Mercury |
| 3 | **Anticipation** | `/predictions` | Probabilités 24h · Corrélations |
| 4 | **Decisions** | `/decision-flow` | Pipeline visuel complet |
| 5 | **Proof** | `/proof-center` | Merkle · TLA+ · Lean 4 |
| 6 | **Control** | `/control` | Supervision globale |

### Sous-routes Market

| Route | Domaine | Agent |
|-------|---------|-------|
| `/market/trading` | Trading | Alpha |
| `/market/banking` | Banking | Sentinel |
| `/market/ecommerce` | E-Commerce | Mercury |

---

## 3. Pages et composants clés

### 3.1 Market (`/market`)

**Rôle :** Porte d'entrée unique. L'utilisateur choisit son domaine.

**Contenu :**
- 3 cartes domaine (Trading / Banking / E-Commerce)
- Chaque carte affiche : données live, tendances, anomalies, agent actif
- Exemple : BTC price · volatility · trend · Agent Alpha status: HOLD

**Composants :** `Market.tsx`

---

### 3.2 Decision Flow (`/decision-flow`)

**Rôle :** Page centrale — montre le pipeline complet d'une décision.

**Pipeline affiché :**
```
Market Context     → BTC volatility spike
Agent Alpha        → Signal SELL · Confidence 0.41
Prediction Engine  → Flash crash probability 63%
Guard X-108        → Threshold 0.18 · Temporal lock 10s
Decision           → HOLD
Proof              → Merkle anchor generated
```

**Fonctionnalités :**
- Sélection du domaine (Trading / Banking / E-Com)
- Sélection de la décision (ALLOW / HOLD / BLOCK)
- Timeline live des décisions récentes
- Auto-refresh toutes les 10s

**Composants :** `DecisionFlow.tsx`

---

### 3.3 Sidebar Agents (permanente)

**Rôle :** Affiche les 3 agents en permanence avec leurs statuts live.

**Contenu :**
```
ACTIVE AGENTS

📈 Alpha    [✅ ALLOW]  BUY BTC — Coherence OK
🏦 Sentinel [⏳ HOLD]   Invest €20k — Liquidity check
🛒 Mercury  [⛔ BLOCK]  Discount 40% — Margin collapse

⚡ Decision Flow →
Guard X-108 valide chaque action
```

**Fonctionnalités :**
- Statuts simulés mis à jour toutes les 4s
- Clic sur un agent → redirige vers le domaine
- Réductible (mode icônes)
- Lien rapide vers Decision Flow

**Composants :** `AgentsSidebar.tsx`

---

### 3.4 Tooltips Obsidia (ConceptTooltip)

**Rôle :** Expliquer les termes techniques directement dans l'interface.

**Glossaire intégré :**

| Terme | Explication courte |
|-------|-------------------|
| **Guard X-108** | Moteur de décision qui valide chaque action proposée par un agent |
| **Temporal Lock** | Période de refroidissement (10s) empêchant des actions irréversibles trop rapides |
| **ALLOW** | Action exécutée immédiatement |
| **HOLD** | Action valide — en attente du temporal lock |
| **BLOCK** | Action rejetée — risque ou incohérence détectée |
| **Merkle Anchor** | Empreinte cryptographique de la décision dans un arbre de Merkle |
| **Coherence** | Score de cohérence de l'agent (0 à 1) |
| **Confidence** | Niveau de certitude de l'agent sur son signal (0 à 1) |
| **Agent Alpha** | Agent spécialisé dans le trading de cryptomonnaies |
| **Agent Sentinel** | Agent spécialisé dans la sécurité bancaire |
| **Agent Mercury** | Agent spécialisé dans l'optimisation e-commerce |

**Usage :** `<ConceptTooltip term="Guard X-108" showIcon />`

**Composants :** `ConceptTooltip.tsx`, `DecisionLegend` (composant inline)

---

## 4. Domaines

### 4.1 Trading (`/market/trading`)

**Agent :** Alpha  
**Données :** BTC/ETH prix live (GBM), volatilité, flash crash  
**Décisions :** ALLOW (ordre exécuté) · HOLD (τ=10s) · BLOCK (flash crash)  
**Spécificité :** Strasbourg Clock pour le temporal lock

### 4.2 Banking (`/market/banking`)

**Agent :** Sentinel  
**Données :** Capital, liquidité, risque, comptes  
**Décisions :** Basées sur IR · CIZ · DTS · TSG (scores 0-1)  
**Spécificité :** InvestmentChain (séquence de 6 actions enchaînées)

### 4.3 E-Commerce (`/market/ecommerce`)

**Agent :** Mercury (+ Pricing · Inventory · Fulfillment · Marketing)  
**Données :** CTR · CVR · ROAS · Revenue · Margin  
**Décisions :** Basées sur coherence score des agents  
**Spécificité :** Margin négative = attendue sur scénarios stress (badge explicatif)

---

## 5. Modes LIVE / DEMO

Sur chaque domaine, un toggle permet de basculer entre :

| Mode | Description |
|------|-------------|
| **● LIVE** | Données réelles (marché live, transactions réelles) |
| **○ DEMO** | Données synthétiques / scénarios prédéfinis |

**Composant :** `LiveModeBadge` dans `AgentsSidebar.tsx`

---

## 6. Portfolio & Corrélation

### 6.1 Graphique 24h avec annotations de simulation

- Lignes verticales colorées par domaine : Bleu=Trading · Vert=Bank · Violet=Ecom
- Marqueur ▲ en haut avec tooltip (heure, capital, PnL, scénario)
- Rafraîchissement toutes les 2 minutes

### 6.2 Panneau Corrélation (onglet dans Portfolio)

- Fenêtre temporelle : 1 / 3 / 7 / 14 / 30 jours
- 4 KPI : simulations, PnL total, guard blocks, capital saved
- Répartition par domaine avec barres de progression
- Journal complet des simulations

### 6.3 Notifications de seuil PnL

- Alerte automatique au propriétaire si PnL < seuil configuré
- Seuil configurable dans le panneau Corrélation (défaut : -5 000 €)
- Raccourcis : -1k / -5k / -10k / -25k

---

## 7. Proof Center

### 7.1 Download Proof Package

- Route : `GET /api/proof/export`
- Format : ZIP (599 Ko)
- Contenu : Lean 4 proofs · TLA+ specs · Bank adversarial tests · Merkle anchors · Evidence traces · Audit summary

### 7.2 Contenu du package

```
obsidia-proof-package-{date}/
├── lean/                    # 33 théorèmes Lean 4
├── tla/                     # X108.tla + DistributedX108.tla
├── bank-proof/              # 473 tests adversariaux
├── anchors/                 # Merkle roots + RFC 3161
├── evidence/                # Strasbourg Clock traces (4 × 8000 steps)
└── audit_summary.md         # Rapport complet
```

---

## 8. Parcours utilisateur recommandé

```
1. Arriver sur / (Home)
   → Cliquer "▶ Watch 30-second demo" (Flash Crash scenario inline)
   → Ou "Start Demo →" pour le mode démo complet

2. Naviguer vers Market
   → Choisir Trading / Banking / E-Commerce
   → Observer les données live et l'agent actif

3. Consulter Decision Flow (/decision-flow)
   → Voir le pipeline complet d'une décision
   → Comprendre Guard X-108 via les tooltips

4. Explorer Anticipation (/predictions)
   → Voir les probabilités 24h
   → Voir les marqueurs de simulation colorés

5. Vérifier Proof (/proof-center)
   → Télécharger le Proof Package (ZIP)
   → Consulter les preuves formelles

6. Superviser via Control (/control)
   → Voir les statistiques globales
   → Monitorer les agents
```

---

## 9. Stack technique

| Couche | Technologie |
|--------|-------------|
| Frontend | React 19 + Tailwind 4 + tRPC 11 |
| Backend | Express 4 + tRPC |
| Base de données | MySQL/TiDB via Drizzle ORM |
| Auth | Manus OAuth |
| Moteurs | GBM (trading) · Score-based (banking) · Funnel (ecom) |
| Preuves | Lean 4 · TLA+ · Merkle · RFC 3161 |

---

## 10. Fichiers clés

```
client/src/
├── App.tsx                          # Routes + layout + sidebar agents
├── pages/
│   ├── Market.tsx                   # Porte d'entrée
│   ├── DecisionFlow.tsx             # Pipeline visuel central
│   ├── TradingWorld.tsx             # Domaine Trading
│   ├── BankWorld.tsx                # Domaine Banking
│   ├── EcomWorld.tsx                # Domaine E-Commerce
│   ├── Predictions.tsx              # Probabilités 24h + corrélations
│   ├── Portfolio.tsx                # Portefeuille + onglet Corrélation
│   ├── ProofCenter.tsx              # Preuves formelles
│   └── ControlTower.tsx             # Supervision globale
└── components/
    ├── AgentsSidebar.tsx            # Sidebar agents permanente
    ├── ConceptTooltip.tsx           # Tooltips glossaire Obsidia
    ├── ProbabilityChart.tsx         # Graphique 24h + annotations
    └── ...

server/
├── routers.ts                       # Toutes les procédures tRPC
├── engines/
│   ├── tradingEngine.ts             # Moteur GBM
│   ├── bankEngine.ts                # Moteur bancaire
│   └── ecomEngine.ts               # Moteur e-commerce
└── proofExport.ts                   # Génération ZIP proof package
```
