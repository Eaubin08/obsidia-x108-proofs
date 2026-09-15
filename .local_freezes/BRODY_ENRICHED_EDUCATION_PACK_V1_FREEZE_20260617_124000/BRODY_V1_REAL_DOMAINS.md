# BRODY_V1_REAL_DOMAINS.md
# Pack: BRODY_ENRICHED_EDUCATION_PACK_V1 — 2026-06-17
# Statut : VALIDATED_BY_REPO (agents et scénarios canoniques) + HISTORIC_USEFUL (Cowork)
# Sources : sigma/domains/, sigma/examples/, REAL_DOMAINS_BANK_TRADING_GPS_DEFENSE.md (Cowork)

---

## Les domaines réels dans Obsidia X-108

Obsidia X-108 opère sur des **domaines réels** où des décisions incorrectes
ont des conséquences immédiates et coûteuses. Dans chaque domaine, Brody
doit comprendre le contexte sans jamais décider.

---

## Domaine 1 : Banking (Banque)

**Équivalence architecturale :** Bank = économie
**Sources canoniques :** `sigma/domains/bank_agents.py`, `sigma/examples/`

### Ce que Brody doit comprendre :
- Les transactions bancaires peuvent être frauduleuses ou légitimes
- Le score de fraude est calculé par des agents spécialisés
- La contrepartie connue / inconnue est un signal fort
- Le montant relativement au comportement historique du client déclenche des alertes

### Ce que Brody peut expliquer :
- Pourquoi une transaction a été soumise à X-108
- Quels agents ont voté et dans quel sens (advisory)
- Quel type de risque a été détecté

### Ce que Brody ne peut pas décider :
- Si la transaction est frauduleuse ou légitime
- Si la transaction doit être approuvée ou bloquée
- Quelle est la politique de seuil à appliquer

### Agents du domaine (VALIDATED_BY_REPO) :
- `FraudDetectionAgent`
- `BehaviorAnalysisAgent`
- `TransactionValidationAgent`

### Scénarios canoniques :
- `sigma/examples/bank_normal.json` — transaction normale → ACT
- `sigma/examples/bank_suspicious.json` — transaction suspecte → BLOCK
- `sigma/examples/bank_blocked.json` — transaction bloquée

### Cas pédagogique : Transaction 8 000€ suspecte
```
Contexte : amount=8000, counterparty_known=false, fraud_score=0.85
FraudDetectionAgent     → 0.95 (BLOCK)
BehaviorAnalysisAgent   → 0.80 (BLOCK)
TransactionValidationAgent → 0.30 (ALLOW)
Agrégation Sigma        → 0.68 → seuil BLOCK
Verdict X-108           → BLOCK (Fraude probable)
```

### Risques déclenchant HOLD/BLOCK :
- Score de fraude > seuil
- Contrepartie inconnue + montant élevé
- Comportement inhabituel du client
- Correspondance avec des patterns connus de fraude

### Sous autorité KX108 uniquement :
La décision finale ACT/HOLD/BLOCK appartient à X-108.
Brody peut décrire le contexte. Sigma peut recommander.
Ni l'un ni l'autre ne décide.

---

## Domaine 2 : Trading (Marché financier)

**Équivalence architecturale :** Trading = marché
**Sources canoniques :** `sigma/domains/trading_agents.py`, `sigma/examples/`

### Ce que Brody doit comprendre :
- Les ordres de trading peuvent cascader en millisecondes
- La volatilité, la liquidité, le slippage et l'exposition sont les invariants clés
- Un changement de régime (bull → bear) modifie les seuils

### Ce que Brody peut expliquer :
- Pourquoi un ordre a été soumis à X-108
- Quel niveau d'exposition a été mesuré
- Quel régime de marché était actif au moment de l'ordre

### Ce que Brody ne peut pas décider :
- Si l'ordre doit être exécuté ou retenu
- Quel est le bon moment d'exécution
- Si le marché est en phase BULL ou BEAR (c'est une mesure, pas une décision)

### Agents du domaine (VALIDATED_BY_REPO) :
- `MarketDataAgent`
- `LiquidityAgent`
- `VolatilityAgent`
- `MomentumAgent`

### Scénarios canoniques :
- `sigma/examples/trading_normal.json` → ACT
- `examples/trading_bullish.json` — scénario haussier

### Cas pédagogique : Ordre 500 BTC (~20M€)
```
Contexte : ordre massif en période de faible liquidité
VolatilityAgent    → mesure de volatilité élevée
LiquidityAgent     → liquidité insuffisante
Verdict possible   → HOLD (attendre meilleur prix)
```

### Risques déclenchant HOLD/BLOCK :
- Volatilité > seuil
- Liquidité insuffisante
- Exposition > limite autorisée
- Slippage estimé trop élevé

---

## Domaine 3 : GPS / Défense / Aviation

**Équivalence architecturale :** GPS = trajectoire / source / temps / énergie
**Sources canoniques :** `sigma/domains/gps_defense_aviation_agents.py`, `sigma/examples/`

### Ce que Brody doit comprendre :
- Dans ce domaine, les sources d'information peuvent être corrompues, absentes, ou en conflit
- X-108 gouverne les décisions de navigation et de trajectoire avant qu'elles soient exécutées
- Le skew temporel est un vecteur d'attaque connu

### Ce que Brody peut expliquer :
- Combien de sources GPS sont disponibles et cohérentes
- Si un skew temporel a été détecté
- Quel scénario GPS correspond à la situation décrite

### Ce que Brody ne peut pas décider :
- Quelle source GPS utiliser en cas de conflit
- Si la trajectoire doit être maintenue ou modifiée
- Quel niveau de dégradation est acceptable

### Scénarios canoniques GPS :
| Scénario | Fichier | Verdict |
|---|---|---|
| Nominal | `gps_nominal.json` | ACT |
| Brownout | `gps_brownout.json` | HOLD |
| No source | `gps_no_source.json` | BLOCK |
| Source conflict | `gps_source_conflict.json` | HOLD ou BLOCK |
| Time skew | `gps_time_skew.json` | HOLD ou BLOCK |
| Omega chaos | `gps_omega_chaos.json` | BLOCK |

### Signification éducative :
GPS illustre que X-108 ne se limite pas à la finance. Il gouverne
tout système où des sources conflictuelles doivent être arbitrées
avant action (navigation autonome, défense, aviation).

---

## Domaine 4 : E-Commerce

**Sources canoniques :** `sigma/domains/ecom_agents.py`, `sigma/examples/ecom_normal.json`

### Agents :
- `TrafficQualityAgent`
- `IntentAnalysisAgent`
- `FraudDetectionAgent`

### Cas pédagogique : Commande 500€ suspecte
```
Adresse de livraison suspecte + taux de fraude élevé
Verdict : BLOCK (fraude probable)
Résultat : Aucune expédition, zéro perte
```

---

## Domaine 5 : Meta / Gouvernance

**Sources canoniques :** `sigma/domains/meta_agents.py`

### Agents :
- `IdentityVerificationAgent`
- `AnomalyDetectionAgent`
- `PolicyComplianceAgent`

### Cas pédagogique : Accès suspect administrateur
```
Heure inhabituelle + géolocalisation nouvelle
Verdict : HOLD (clarification nécessaire)
Résultat : Accès retenu jusqu'à vérification
```

---

## Blockchain / Gencoin (domaine économique)

**Source :** `docs/blockchain/GENCOIN_NOT_A_TOKEN_POLICY_V1.md`

- Gencoin n'est **pas** un token crypto
- Pas de clé privée (`NO_PRIVATE_KEY_POLICY_V1.md`)
- Oracle freshness gate, Bridge risk gate, DeFi risk gate documentés

---

## Note sur le scénario Ragnarok

`sigma/contracts.broken-ragnarok.py` documente les modes d'échec **volontairement
cassés** pour les tests. Ce fichier est **EXCLUDE_ABSOLUTE** de tout pack éducatif.
Ne jamais l'inclure dans le contexte Brody. Son existence signale que les
scénarios d'attaque totale multi-vecteurs sont testés, pas que le système a échoué.
