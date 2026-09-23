# KERNEL_OVERVIEW.md — Spécification du Noyau X-108

**Version :** 1.4.0 · **Dernière mise à jour :** 2026-04-03

---

## I. Rôle du Kernel

Le **Kernel X-108** est le noyau de gouvernance déterministe d'Obsidia. Il est le "juge" qui évalue les actions avant exécution selon des règles mathématiques strictes et auditables.

### Paradigme ex ante

```
Intention / Agent → [KERNEL X-108] → ACT / HOLD / BLOCK → Trace / Preuve
```

Le kernel ne décide **jamais après coup**. Il juge **avant l'exécution**, ce qui garantit qu'aucune action hors-périmètre ne peut être exécutée.

---

## II. Rôle de X-108

**X-108** est le protocole de gouvernance qui implémente le kernel. Il définit :

1. **Les règles de vote** — Comment les agents votent
2. **Les seuils** — Quand bloquer, retenir ou autoriser
3. **Le protocole de veto** — Comment un agent peut bloquer une action
4. **La traçabilité** — Comment chaque décision est scellée et auditée

### Logique ex ante

| Verdict | Signification | Quand | Conséquence |
|---|---|---|---|
| **ACT** (ALLOW) | Action autorisée | Tous les invariants respectés | Exécution immédiate |
| **HOLD** | Action retenue | Seuil de certitude insuffisant | Attendre clarification |
| **BLOCK** | Action bloquée | Violation d'invariant détectée | Refus d'exécution |

---

## III. Opérations Sensibles

Le kernel juge les opérations sensibles dans trois domaines :

### A. Trading (Marché Financier)

**Opérations jugées :**
- Ordres d'achat/vente massifs
- Changements de régime (bull → bear)
- Positions à risque élevé

**Invariants vérifiés :**
- Volatilité acceptable
- Liquidité suffisante
- Exposition dans les limites

**Exemple :** Un ordre de 10M BTC est reçu. Le kernel vérifie la volatilité, la liquidité, l'exposition. Si tout est OK → ACT. Sinon → BLOCK.

### B. Banking (Transactions Financières)

**Opérations jugées :**
- Virements de gros montants
- Transactions suspectes
- Changements de comportement

**Invariants vérifiés :**
- Montant dans les limites
- Contrepartie connue
- Pas de fraude détectée

**Exemple :** Une transaction de 8000€ est reçue. Le kernel vérifie le montant, la contrepartie, les scores de fraude. Si OK → ACT. Sinon → BLOCK.

### C. E-Commerce (Ventes en Ligne)

**Opérations jugées :**
- Commandes à haut risque
- Fraude potentielle
- Abandons de panier

**Invariants vérifiés :**
- Intention d'achat réelle
- Pas de fraude détectée
- Marge acceptable

**Exemple :** Une commande de 500€ est reçue. Le kernel vérifie l'intention, la fraude, la marge. Si OK → ACT. Sinon → BLOCK.

---

## IV. Logique de Traçabilité

Chaque décision du kernel est scellée et auditée :

### A. Decision ID
Identifiant unique de la décision :
```
DEC-{DOMAIN}-{TIMESTAMP}-{HASH}
```

### B. Trace ID
Référence traçable pour audit :
```
TRACE-{DECISION_ID}-{MERKLE_ROOT}
```

### C. Merkle Root
Racine de l'arbre de Merkle qui scelle toutes les décisions :
```
Merkle(decision_1, decision_2, ..., decision_n)
```

### D. RFC 3161 Anchor
Ancrage cryptographique immuable :
```
Signature(Merkle_Root, Timestamp, Authority)
```

**Résultat :** Chaque décision est immuable, vérifiable, et auditée.

---

## V. Ce que le Kernel FAIT

✅ **Juge les actions avant exécution** — Décision ex ante garantie

✅ **Applique des règles déterministes** — Pas d'aléa, pas d'hallucination

✅ **Scelle chaque décision** — Merkle + RFC 3161

✅ **Fournit une trace complète** — Audit trail immuable

✅ **Refuse les actions hors-périmètre** — Aucune exception

✅ **Gère le veto distribué** — Protocole sans deadlock (TLA+ prouvé)

---

## VI. Ce que le Kernel NE FAIT PAS

❌ **Ne génère pas de contenu** — Pas une IA générative

❌ **Ne prend pas de décisions métier** — Juge les règles, pas la stratégie

❌ **Ne stocke pas les données** — Juge et scelle, pas une base de données

❌ **Ne se connecte pas directement aux systèmes** — Via Sigma Engine

❌ **Ne fait pas de prédictions** — Évalue les invariants, pas l'avenir

❌ **Ne peut pas être contourné** — Disjoncteur mathématique

---

## VII. Invariants Vérifiés

Le kernel vérifie 5 invariants formels (Lean 4, 0 sorry) :

| Invariant | Domaine | Vérification | Statut |
|---|---|---|---|
| **D1** | Décision | Non-contradiction des règles | PROUVÉ |
| **E2** | Exécution | Déterminisme du vote | PROUVÉ |
| **G1** | Gouvernance | Immuabilité de la trace | PROUVÉ |
| **G2** | Gouvernance | Cohérence du sceau Merkle | PROUVÉ |
| **G3** | Gouvernance | Absence de contradiction circulaire | PROUVÉ |

---

## VIII. Protocole X-108 — Étapes

### Étape 1 : Réception
```
Agent → Sigma Engine → Kernel X-108
```

### Étape 2 : Validation
```
Kernel vérifie les invariants D1, E2, G1, G2, G3
```

### Étape 3 : Vote
```
Agents domaine votent (Trading, Bank, Ecom)
```

### Étape 4 : Agrégation
```
Kernel agrège les votes selon les seuils
```

### Étape 5 : Décision
```
Kernel rend : ACT / HOLD / BLOCK
```

### Étape 6 : Scellement
```
Sigma Engine génère Decision ID, Trace ID, Merkle Root
```

### Étape 7 : Ancrage
```
RFC 3161 anchor immuable
```

### Étape 8 : Exécution
```
Sigma Engine exécute selon la décision
```

---

## IX. Exemple Complet : Transaction Suspecte

```
Événement : Transaction bancaire de 8000€ (suspect)

Étape 1 : Réception
  Input: {
    "domain": "bank",
    "amount": 8000,
    "counterparty_known": false,
    "fraud_score": 0.85
  }

Étape 2 : Validation
  ✓ Montant positif
  ✓ Format canonique valide
  ✓ Invariants locaux OK

Étape 3 : Vote
  - FraudDetectionAgent: 0.95 (BLOCK)
  - BehaviorAnalysisAgent: 0.80 (BLOCK)
  - TransactionValidationAgent: 0.30 (ALLOW)

Étape 4 : Agrégation
  Moyenne pondérée: 0.68 → Seuil BLOCK atteint

Étape 5 : Décision
  Verdict: BLOCK (Fraude probable)

Étape 6 : Scellement
  Decision ID: DEC-BANK-20260403T235959Z-a7f2e8c1
  Trace ID: TRACE-DEC-BANK-20260403T235959Z-a7f2e8c1-3f4e2d1c
  Merkle Root: 0x8f2e3d1c...

Étape 7 : Ancrage
  RFC 3161 Signature: [immuable]

Étape 8 : Exécution
  Action: Transaction BLOQUÉE
  Raison: Fraude détectée
  Audit trail: Immuable et vérifiable

Résultat : La transaction est bloquée avant exécution. Aucune exception possible.
```

---

## X. Limites Structurelles

Le kernel ne couvre pas (voir `docs/LIMITS.md`) :

- ❌ Données de marché en temps réel (intégrées via Sigma)
- ❌ Authentification des utilisateurs (gérée en amont)
- ❌ Vecteurs d'attaque physiques (hors scope)
- ❌ Compromission de clés cryptographiques (hors scope)

---

## XI. Pour Aller Plus Loin

- **Preuves formelles :** `proofs/lean/Obsidia.lean`
- **Protocole TLA+ :** `proofs/tla/X108.tla`
- **Tests :** `tests/test_*.py` (22/22 PASS)
- **Adversariaux :** `tests/adversarial/` (1M+ cas)
- **Audit :** `docs/AUDIT_GUIDE.md`

---

**Dernière mise à jour :** 2026-04-03

**Responsable :** Obsidia Governance
