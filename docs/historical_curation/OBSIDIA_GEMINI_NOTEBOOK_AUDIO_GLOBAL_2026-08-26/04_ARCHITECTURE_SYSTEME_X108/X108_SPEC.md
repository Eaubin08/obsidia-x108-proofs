
# Spécification Technique — Loi X–108

## Loi Fondatrice
Toute action irréversible doit être suspendue jusqu'à démonstration
de constance sous contrainte temporelle.

## Invariants testés
- CSCN : Cohérence sous contraintes non-contradictoires
- CMEC : Convergence multi-états cohérents
- IST : Indice de stabilité de trajectoire

## API minimale
X108.check(state, irreversible=True) -> HOLD | ACT
