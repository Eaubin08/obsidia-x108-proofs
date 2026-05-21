# PACK I — Saturations / anti-emballement

## M2
- seuil bas: perte signal -> HOLD
- seuil haut: saturation capteur -> clamp
- comportement dépassement: réduction progressive ou rejet mesure
- impact vérité: baisse truth_score si mesure non fiable

## M3
- seuil bas: inefficacité conversion
- seuil haut: saturation conversion
- comportement dépassement: limitation output
- impact vérité: baisse sigma/truth si pout artificiel ou non expliqué

## M4
- seuil bas: flux insuffisant
- seuil haut: emballement / turbulence / pertes dominantes
- comportement dépassement: redistribution ou arrêt
- impact vérité: faux ON si topologie masque pertes

## P3
- seuil bas: réserve vide
- seuil haut: saturation stockage
- comportement dépassement: blocage charge ou pertes thermiques
- impact vérité: ON assisté si stockage soutient trop

## P4
- seuil bas: relance inutile
- seuil haut: sur-relance
- comportement dépassement: rejected
- impact vérité: assisted_ratio monte, faux ON probable
