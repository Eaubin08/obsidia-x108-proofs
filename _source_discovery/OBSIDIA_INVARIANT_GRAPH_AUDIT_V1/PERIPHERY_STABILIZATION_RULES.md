# PERIPHERY_STABILIZATION_RULES
# OBSIDIA_INVARIANT_GRAPH_AUDIT_V1
# Date: 2026-06-02

---

## Règle fondamentale

```
Une périphérie peut produire :   contexte / signal / candidate / artefact auditable
Une périphérie ne peut pas :     autorité finale / ACT / ALLOW / HOLD / BLOCK direct / verdict moral
```

---

## 5 règles de stabilisation des périphéries

### Règle 1 — Classification avant runtime

Toute extension doit être classifiée dans cet ordre strict :
```
SOURCE_DISCOVERY (Plan 1)
    → SPEC_ONLY (Plan 2)
    → PYTHON_TEST (Plan 3 P5)
    → RUNTIME_CANDIDATE
    → RUNTIME_CODE + tests
    → X108 gate
    → Claim public
```
**Sans spec préalable, aucun runtime.** Cette règle est une politique — elle est renforcée par la taxonomy `RUNTIME_STATUS_TAXONOMY.md`.

---

### Règle 2 — Packet / Boundary / Test obligatoires

Toute extension doit définir avant déploiement :

| Élément | Exemple | Obligatoire |
|---------|---------|-------------|
| Packet schema | `HumanLogicPacket`, `TemporalContextHeader` | OUI |
| Boundary | `SIGNAL_ONLY; NO_ACT` | OUI |
| Test no-ACT | `test_no_act_from_component` | OUI |
| Test no-verdict | `test_no_verdict_final` | OUI |

---

### Règle 3 — Retomber vers X-108 si action critique

```
Si la périphérie produit un signal qui implique une action dans le monde réel :
  → le signal doit traverser X108_EVALUATED dans le cycle d'action
  → jamais bypass direct
  → X108_no_act_before_tau s'applique à toute action irréversible

Cycle obligatoire pour toute action critique :
INPUT_CAPTURED → ... → X108_EVALUATED → OS3_TICKETED → (WORLD_ACTION_DRY_RUN_READY)
```

---

### Règle 4 — Si incertain → HOLD / BLOCK selon couche

```
Couche kernel (OS1)            : incertain → HOLD (X108_no_act_before_tau)
Couche consensus (OS3)         : sans quorum → BLOCK (aggregate4_fail_closed)
Couche périphérique            : incertain → contexte avec provenance_uncertainty explicite
Couche External Signals        : skew négatif → HOLD (skew_negative_implies_hold)
Couche NPL                     : incertain → signal probabiliste + uncertainty [0,1], jamais verdict
Couche GPS                     : source_conflict > threshold → proposer ABORT_TRAJECTORY (proposed_verdict only)
```

---

### Règle 5 — Readonly par défaut, écriture avec gate

```
Lecture  : toujours autorisée
Écriture : gate humain obligatoire (Brody, Graphiti, mémoire)
Décision : X108_ONLY
ACT      : X108_ALLOW + OS3ProofTicket + gate humain pour irréversible
```

---

## Tableau des statuts périphériques

| Composant | Peut lire | Peut écrire | Peut décider | Peut ACT | Gate requise |
|-----------|-----------|-------------|-------------|---------|--------------|
| Brody | OUI | NON (sauf gate humain) | NON | NON | Gate humain pour écriture mémoire |
| Graphiti | OUI | NON (sauf gate humain) | NON | NON | Gate humain pour graphiti_write |
| Sigma | OUI | NON | NON | NON | X108 pour tout verdict |
| Tree34 | OUI (activation) | NON | NON | NON | Aucune — signal contextuel |
| Agents 52 | OUI | NON | NON | NON | X108 pour action critique |
| Balance/BUV | OUI | NON | NON | NON | X108 pour décision basée sur score |
| Gencoin | OUI | ledger append-only si X108 ALLOW | NON (candidat seulement) | NON | X108 ALLOW + OS3ProofTicket |
| GPS | OUI | NON | NON (proposed_verdict) | NON | DecisionTicket pour actuateur |
| NPL | OUI | NON | NON | NON | Gate humain si écriture mémoire |
| External Signals | OUI (préfiltre) | NON | NON | NON | X108 pour toute action découlant |
