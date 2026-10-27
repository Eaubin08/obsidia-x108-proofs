# REAL_DOMAINS_BANK_TRADING_GPS_DEFENSE.md
# Mission: BRODY_WIDE_RND_DISCOVERY_AND_EDUCATION_EXTRACTION_V0
# Mode: READ_ONLY · Date: 2026-06-17

---

## Les domaines réels dans Obsidia X-108

Obsidia X-108 opère sur 4 domaines réels principaux. Chaque domaine a ses agents, ses invariants, ses scénarios de test.

---

## Domaine 1 : Banking (Banque)

**Équivalence architecturale :** Bank = économie

### Opérations jugées par X-108
- Virements de gros montants
- Transactions suspectes
- Changements de comportement client

### Invariants vérifiés
- Montant dans les limites autorisées
- Contrepartie connue
- Score de fraude sous le seuil

### Agents domaine (sigma/domains/bank_agents.py)
- FraudDetectionAgent
- BehaviorAnalysisAgent
- TransactionValidationAgent

### Cas canonique : Transaction suspecte 8 000€
```json
{
  "domain": "bank",
  "amount": 8000,
  "counterparty_known": false,
  "fraud_score": 0.85
}
```
→ Votes : FraudDetectionAgent 0.95 (BLOCK), BehaviorAnalysisAgent 0.80 (BLOCK), TransactionValidationAgent 0.30 (ALLOW)
→ Agrégation : 0.68 → seuil BLOCK atteint
→ Verdict : **BLOCK** (Fraude probable)

### Tests P2 bank (sigma/tests/)
- test_bank_adversarial_pack.py
- test_bank_confusion_matrix_pack.py
- test_bank_enterprise_pack.py
- test_bank_fuzz_scale_pack.py
- test_bank_regulatory_proxy_pack.py
- test_bank_replay_pack_10k.py (10 000 transactions)
- test_bank_robo_scenario_benchmark.py
- test_bank_scale_pack.py
- test_bank_market_pack.py

### Scénarios (sigma/examples/)
- `bank_normal.json` — transaction normale → ACT
- `bank_suspicious.json` — transaction suspecte → BLOCK
- `bank_blocked.json` — transaction bloquée

---

## Domaine 2 : Trading (Marché financier)

**Équivalence architecturale :** Trading = marché

### Opérations jugées par X-108
- Ordres d'achat/vente massifs
- Changements de régime (bull → bear)
- Positions à risque élevé

### Invariants vérifiés
- Volatilité acceptable
- Liquidité suffisante
- Exposition dans les limites
- Slippage acceptable

### Agents domaine (sigma/domains/trading_agents.py)
- MarketDataAgent
- LiquidityAgent
- VolatilityAgent
- MomentumAgent

### Cas canonique : Ordre 500 BTC (~20M€)
→ Kernel vérifie : volatilité, liquidité, exposition, slippage
→ Verdict possible : **ACT** (exécution immédiate) ou **HOLD** (attendre meilleur prix)

### Scénarios (sigma/examples/)
- `trading_normal.json` — ordre standard → ACT

### Exemple fichier root
- `examples/trading_bullish.json` — scénario haussier

---

## Domaine 3 : GPS / Defense / Aviation

**Équivalence architecturale :** GPS = trajectoire / source / temps / énergie

### Agents domaine (sigma/domains/gps_defense_aviation_agents.py)
- Source validation agents
- Time skew detection agents
- Energy/trajectory agents

### Scénarios (sigma/examples/) — tous existants

| Scénario | Fichier | Description |
|---|---|---|
| GPS nominal | `gps_nominal.json` | Toutes sources OK → ACT |
| GPS brownout | `gps_brownout.json` | Perte partielle de signal |
| GPS no source | `gps_no_source.json` | Aucune source disponible → BLOCK |
| GPS source conflict | `gps_source_conflict.json` | Sources en contradiction |
| GPS time skew | `gps_time_skew.json` | Décalage temporel détecté |
| GPS omega chaos | `gps_omega_chaos.json` | Scénario chaos multi-défaillances |

### Signification éducative
Le domaine GPS illustre que X-108 ne se limite pas à la finance. Il peut gouverner n'importe quel système où des **sources d'information conflictuelles** doivent être arbitrées avant action (navigation autonome, défense, aviation).

---

## Domaine 4 : E-Commerce

**Agents domaine (sigma/domains/ecom_agents.py)**
- TrafficQualityAgent
- IntentAnalysisAgent
- FraudDetectionAgent

### Scénarios
- `ecom_normal.json` — commande normale → ACT

### Cas canonique : Commande 500€ suspecte
→ Adresse de livraison suspecte, taux de fraude élevé
→ Verdict : **BLOCK** (fraude probable)
→ Résultat : Aucune expédition, zéro perte

---

## Domaine 5 : Meta / Gouvernance

**Agents domaine (sigma/domains/meta_agents.py)**
- IdentityVerificationAgent
- AnomalyDetectionAgent
- PolicyComplianceAgent

### Cas canonique : Accès suspect administrateur
→ Heure inhabituelle + géolocalisation nouvelle
→ Verdict : **HOLD** (clarification nécessaire)
→ Résultat : Accès retenu jusqu'à vérification SMS/email

---

## Scénario adversarial cross-domaine : Ragnarok

**sigma/examples/ragnarok_full_attack.json** + **sigma/contracts.broken-ragnarok.py**

Ragnarok est le scénario d'attaque totale multi-vecteurs. Il teste la résistance du système face à une attaque coordonnée sur plusieurs domaines simultanément. Les contrats brisés de Ragnarok (`contracts.broken-ragnarok.py`) documentent les modes d'échec connus et volontairement cassés pour les tests.

---

## Blockchain / Gencoin (domaine économique)

Source : `docs/blockchain/`

- **Gencoin n'est PAS un token crypto** (`GENCOIN_NOT_A_TOKEN_POLICY_V1.md`)
- **Pas de clé privée** (`NO_PRIVATE_KEY_POLICY_V1.md`)
- **Oracle freshness gate** — vérification fraîcheur des données oracle
- **Bridge risk gate** — risque de pont inter-chaînes
- **DeFi risk gate** — risque DeFi
- **Onchain audit packet** — paquet d'audit on-chain
- **Blockchain security layer V1**

---

## Synthèse des domaines

| Domaine | Code dans sigma/ | Exemples | Tests P2 |
|---|---|---|---|
| Banking | bank_agents.py | bank_normal, bank_suspicious, bank_blocked | ✅ 9 fichiers de tests |
| Trading | trading_agents.py | trading_normal | Référencé |
| GPS/Defense | gps_defense_aviation_agents.py | 6 scénarios GPS | Référencé |
| E-Commerce | ecom_agents.py | ecom_normal | Référencé |
| Meta | meta_agents.py | (via governance use case) | Référencé |

---

_Généré le 2026-06-17 par BRODY_WIDE_RND_DISCOVERY_AND_EDUCATION_EXTRACTION_V0_
