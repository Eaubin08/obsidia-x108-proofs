# PACK C — M3 conversion

## M3_A1 — mécanique -> électrique
- entrée exacte: rotation omega + couple
- sortie exacte: tension / courant / puissance électrique
- chaîne: rotation -> induction -> courant
- rendement min: 50%
- rendement nominal: 70-85%
- rendement max: ~90%
- pertes: friction, pertes cuivre, pertes fer
- saturation basse: faible vitesse
- saturation haute: échauffement / saturation magnétique
- temps de réponse: rapide
- seuil utile: vitesse minimale critique
- unité pout: W

## M3_B1 — pression -> mécanique
- entrée exacte: flux fluide / pression
- sortie exacte: rotation mécanique
- chaîne: pression -> turbine -> rotation
- rendement min: 30%
- rendement nominal: 60-80%
- rendement max: ~85%
- pertes: turbulence, pertes aérodynamiques, friction
- saturation basse: débit insuffisant
- saturation haute: turbulence destructrice
- temps de réponse: moyen
- seuil utile: débit minimal stable
- unité pout: W

## M3_C1 — thermique -> électrique
- entrée exacte: Delta_T
- sortie exacte: tension / courant
- chaîne: gradient thermique -> effet Seebeck -> courant
- rendement min: 2%
- rendement nominal: 5-8%
- rendement max: ~10%
- pertes: dissipation thermique, faible rendement intrinsèque
- saturation basse: Delta_T faible
- saturation haute: équilibre thermique / limite module
- temps réponse: lent
- seuil utile: Delta_T suffisant
- unité pout: W
