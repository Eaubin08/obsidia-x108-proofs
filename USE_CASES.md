# USE_CASES.md — Cas d'Usage Concrets

**Version :** 1.0.0 · **Dernière mise à jour :** 2026-04-03

---

## Cas 1 : Blocage d'une Transaction Frauduleuse (Banking)

### Problème
Une banque reçoit une transaction de 8 000€ d'un compte vers un compte inconnu. Les signaux de fraude sont élevés : nouveau destinataire, montant anormal, heure inhabituelle.

### Risque Actuel
- Sans gouvernance : La transaction s'exécute, puis est détectée comme fraude (trop tard)
- Perte : 8 000€ + frais de récupération + dommages réputationnels

### Ce que fait Obsidia X-108
1. **Avant exécution**, le kernel reçoit la transaction
2. **Évalue les invariants** : montant, contrepartie, scores de fraude
3. **Agrège les votes** des agents (Fraude Detection, Behavior Analysis, Transaction Validation)
4. **Rend un verdict** : BLOCK (fraude probable)
5. **Scelle la décision** : Decision ID + Trace ID + Merkle Root
6. **Refuse l'exécution** : La transaction ne s'exécute jamais

### Résultat
- ✅ Transaction bloquée avant dommage
- ✅ Décision auditée et immuable
- ✅ Zéro perte financière
- ✅ Conformité réglementaire garantie

---

## Cas 2 : Autorisation d'un Ordre Massif (Trading)

### Problème
Un fonds de placement veut acheter 500 BTC (environ 20M€). Le marché est volatil. L'ordre est énorme et pourrait impacter le prix.

### Risque Actuel
- Sans gouvernance : L'ordre s'exécute au prix courant, puis le marché s'effondre (slippage massif)
- Perte : Plusieurs millions d'euros en glissement de prix

### Ce que fait Obsidia X-108
1. **Avant exécution**, le kernel reçoit l'ordre
2. **Évalue les invariants** : volatilité, liquidité, exposition, slippage
3. **Agrège les votes** des agents (Market Data, Liquidity, Volatility, Momentum)
4. **Rend un verdict** : ACT (conditions acceptables) ou HOLD (attendre meilleur prix)
5. **Scelle la décision** : Decision ID + Trace ID + Merkle Root
6. **Exécute selon le verdict** : Immédiat ou retardé

### Résultat
- ✅ Ordre exécuté au meilleur moment
- ✅ Glissement de prix minimisé
- ✅ Décision auditée et reproductible
- ✅ Conformité réglementaire garantie

---

## Cas 3 : Refus d'une Commande Frauduleuse (E-Commerce)

### Problème
Une boutique en ligne reçoit une commande de 500€ d'un client inconnu, avec adresse de livraison suspecte et taux de fraude élevé.

### Risque Actuel
- Sans gouvernance : La commande est acceptée, le produit est expédié, puis le paiement est contesté
- Perte : 500€ + coût du produit + frais de traitement

### Ce que fait Obsidia X-108
1. **Avant exécution**, le kernel reçoit la commande
2. **Évalue les invariants** : intention d'achat, fraude, marge, compliance
3. **Agrège les votes** des agents (Traffic Quality, Intent Analysis, Fraud Detection)
4. **Rend un verdict** : BLOCK (fraude probable)
5. **Scelle la décision** : Decision ID + Trace ID + Merkle Root
6. **Refuse la commande** : Aucune expédition, aucune perte

### Résultat
- ✅ Fraude bloquée avant dommage
- ✅ Zéro perte financière
- ✅ Décision auditée et immuable
- ✅ Conformité réglementaire garantie

---

## Cas 4 : Délai d'une Opération Sensible (Gouvernance)

### Problème
Un administrateur système demande un accès à un système critique. L'accès est autorisé, mais le kernel détecte une anomalie : accès à une heure inhabituelle, depuis une géolocalisation nouvelle.

### Risque Actuel
- Sans gouvernance : L'accès est accordé immédiatement (potentiellement à un attaquant)
- Perte : Accès compromis, données exposées

### Ce que fait Obsidia X-108
1. **Avant exécution**, le kernel reçoit la demande d'accès
2. **Évalue les invariants** : heure, géolocalisation, historique, authentification
3. **Agrège les votes** des agents (Identity Verification, Anomaly Detection, Policy Compliance)
4. **Rend un verdict** : HOLD (clarification nécessaire)
5. **Scelle la décision** : Decision ID + Trace ID + Merkle Root
6. **Retient l'accès** : Attend une vérification supplémentaire (SMS, email, appel)

### Résultat
- ✅ Accès retenu jusqu'à clarification
- ✅ Attaquant potentiel bloqué
- ✅ Utilisateur légitime peut se vérifier
- ✅ Décision auditée et immuable

---

## Cas 5 : Audit Complet d'une Décision (Conformité)

### Problème
Un régulateur demande : "Pourquoi cette transaction a-t-elle été bloquée ?" Le système doit prouver que la décision était correcte et auditée.

### Risque Actuel
- Sans gouvernance : Pas de trace complète, décision non reproductible
- Perte : Conformité réglementaire compromise, amende possible

### Ce que fait Obsidia X-108
1. **Récupère la Decision ID** : DEC-BANK-20260403T235959Z-a7f2e8c1
2. **Récupère la Trace ID** : TRACE-DEC-BANK-20260403T235959Z-a7f2e8c1-3f4e2d1c
3. **Récupère le Merkle Root** : 0x8f2e3d1c...
4. **Récupère l'ancrage RFC 3161** : Signature immuable
5. **Exécute verify_decision.py** : Vérifie l'intégrité complète
6. **Fournit le rapport** : Tous les invariants, tous les votes, tous les seuils

### Résultat
- ✅ Décision complètement auditée
- ✅ Immuabilité cryptographique prouvée
- ✅ Conformité réglementaire démontrée
- ✅ Régulateur satisfait

---

## Résumé Comparatif

| Cas | Domaine | Problème | Risque | Solution X-108 | Résultat |
|---|---|---|---|---|---|
| **1** | Banking | Fraude | 8K€ + dommages | BLOCK avant exécution | Zéro perte |
| **2** | Trading | Volatilité | Millions € slippage | ACT/HOLD intelligent | Perte minimisée |
| **3** | E-Commerce | Fraude | 500€ + produit | BLOCK avant expédition | Zéro perte |
| **4** | Gouvernance | Anomalie | Accès compromis | HOLD + clarification | Sécurité renforcée |
| **5** | Conformité | Audit | Amende réglementaire | Trace complète immuable | Conformité prouvée |

---

## Points Clés

1. **Ex ante** — Les décisions sont prises **avant exécution**, pas après
2. **Déterministe** — Même situation → Même décision (reproductible)
3. **Audité** — Chaque décision est scellée et vérifiable
4. **Immuable** — Aucune modification possible après coup
5. **Zéro exception** — Aucun contournement possible du kernel

---

## Pour Aller Plus Loin

- **Spécification du kernel :** `docs/KERNEL_OVERVIEW.md`
- **Preuves formelles :** `proofs/lean/Obsidia.lean`
- **Protocole TLA+ :** `proofs/tla/X108.tla`
- **Audit pratique :** `docs/AUDIT_GUIDE.md`
- **Vérification :** `proofs/verifiers/verify_decision.py`

---

**Dernière mise à jour :** 2026-04-03

**Responsable :** Obsidia Governance
