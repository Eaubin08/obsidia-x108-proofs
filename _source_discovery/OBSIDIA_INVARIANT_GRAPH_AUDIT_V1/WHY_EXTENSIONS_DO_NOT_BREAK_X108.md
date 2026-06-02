# WHY_EXTENSIONS_DO_NOT_BREAK_X108
# OBSIDIA_INVARIANT_GRAPH_AUDIT_V1
# Date: 2026-06-02

---

## La réponse froide à la question centrale

> Qu'est-ce qui rend Obsidia difficile à copier au-delà de son architecture visible ?

**L'architecture visible est copiable.**

Les dossiers, les noms de fichiers, la structure `periphery/`, `sigma/`, `proofs/lean/` — tout cela peut être reproduit. Ce n'est pas ce qui tient le système.

**Ce qui est difficile à copier, c'est la composition cohérente des invariants.**

---

## Ce que l'architecture seule ne peut pas garantir

Une architecture sans invariants est un ensemble de conventions.
- Copier la structure de dossiers ne reproduit pas les propriétés de sécurité.
- Copier les noms de composants (`Brody`, `Sigma`, `Tree34`) ne reproduit pas les garanties.
- Écrire "KX108_ONLY" dans du code ne prouve pas que le système le respecte.

Ce qui manque dans une copie superficielle :

1. La preuve Lean que le kernel ne peut pas émettre BLOCK
2. La preuve que le raffinement hérite de la propriété no-BLOCK
3. La preuve que l'immutabilité Merkle détecte tout changement
4. La preuve que le consensus échoue fermé sans quorum
5. La preuve que le skew négatif force HOLD
6. La cohérence de ces propriétés sous composition

---

## Pourquoi chaque nouvelle couche retombe vers X-108

### Mécanisme 1 — L'invariant de raffinement est transitif

```lean
-- Refinement.lean
theorem x108_never_blocks (τ : Tau) (i : TInput) :
    Not (decide3X108 τ i = Decision3.BLOCK)

theorem refined_not_block (d : Decision) (d3 : Decision3)
    (h : R_decision d d3) :
    Not (d3 = Decision3.BLOCK)
```

**Ce que cela signifie :** toute couche qui peut être exprimée comme un raffinement du kernel X108 hérite automatiquement de la propriété no-BLOCK. Elle ne peut pas être souveraine parce que le raffinement lui-même l'interdit.

Une couche ajoutée peut faire des choses utiles (contextualiser, filtrer, enrichir). Mais si elle raffine le kernel, elle hérite du contrat de non-BLOCK. Et si elle ne raffine pas le kernel, elle n'a pas d'autorité décisionnelle — elle produit des signaux qui doivent passer par le kernel.

### Mécanisme 2 — La gate temporelle est première

```lean
-- TemporalKernel.lean
theorem X108_no_act_before_tau ... (hIrr : irr = true) (h : elapsed < τ) :
    decideX108 τ metrics theta irr elapsed = Decision.HOLD
```

Toute couche ajoutée qui veut déclencher une action irréversible doit attendre que τ soit écoulé. Ce n'est pas une convention — c'est une propriété Lean-prouvée. Une couche qui essaie de contourner τ ne passe pas par `decideX108`, et si elle ne passe pas par `decideX108`, elle est hors du périmètre X108.

### Mécanisme 3 — Le fail-closed est la position par défaut

```lean
-- Consensus.lean
theorem aggregate4_fail_closed ... (hACT : ...) (hHOLD : ...) (hBLOCK : ...) :
    aggregate4 d1 d2 d3 d4 = Decision3.BLOCK
```

Sans quorum, le système retourne BLOCK. Cela signifie que toute couche distribuée ajoutée qui perd son quorum retombe vers BLOCK — pas vers ACT, pas vers HOLD. La position sûre est le blocage, pas la permissivité.

### Mécanisme 4 — L'immutabilité détecte toute modification

```lean
-- Sensitivity.lean
theorem P15_Immutability_Strong ... (h : repo ≠ repo') :
    globalSeal manifest (merkleRoot repo) ≠ globalSeal manifest (merkleRoot repo')
```

Toute couche qui tente de modifier la trace ou les fichiers du système sans mettre à jour le seal produit un seal différent. La détection est automatique — pas une convention, une preuve.

### Mécanisme 5 — Le skew externe ne peut pas forcer ACT

```lean
-- TemporalBridge.lean
theorem skew_negative_implies_hold ... (hIrr : i.irr = true) (hneg : elapsed_raw i < 0) (hTau : 0 <= τ) :
    decide_with_skew_handling τ i = Decision.HOLD
```

Un signal externe (External Signals C463, C469) qui présente un skew temporel négatif ne peut pas forcer ACT sur une action irréversible. La propriété est Lean-prouvée.

---

## Ce qui manque encore (être honnête)

Les garanties ci-dessus couvrent le **kernel X108 et ses extensions directes**.

Les couches périphériques (Brody, Graphiti, Sigma, Tree34, NPL, Gencoin, GPS) sont stabilisées par des **tests Python** et des **specs contractuelles** — pas par des preuves Lean. Cela signifie :

- Un attaquant sophistiqué pourrait **modifier une couche périphérique** sans déclencher d'invariant Lean.
- La robustesse périphérique repose sur la rigueur des tests et des specs — qui sont solides mais pas formellement prouvées.
- La chaîne complète `periphery → X108 → kernel` est validée par des tests d'intégration (1973 PASS), pas par une preuve bout-en-bout.

**Ce qui rendrait le système encore plus robuste :**
- Formaliser Lyapunov et ProofOfGovernance en Lean (FORMAL_PROOF_PENDING)
- Formaliser la non-souveraineté de Sigma en Lean
- Relancer TLC pour confirmer les specs TLA+
