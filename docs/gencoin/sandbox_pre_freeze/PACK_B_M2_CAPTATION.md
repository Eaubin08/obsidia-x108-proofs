# PACK B — M2 captation

## M2_A — capteur inertiel rotation
- grandeur captée exacte: vitesse angulaire + inertie effective
- zone de captation: axe / rotor / masse en rotation
- interface de prise: encodeur rotatif / IMU
- seuil activation: omega > seuil friction; exemple provisoire > 10 rad/s
- seuil maintien: omega stable ±5%
- seuil extinction: omega < seuil friction
- loi approx: E = 1/2 * I * omega^2
- pertes propres: friction mécanique, frottement air, bruit mesure
- saturation basse: vitesse trop faible -> bruit
- saturation haute: contraintes mécaniques / échauffement
- unité sortie pin: W via dérivée énergie

## M2_B — capteur pression / débit
- grandeur captée exacte: pression + débit
- zone de captation: circuit fluide / air
- interface de prise: capteur pression + débitmètre
- seuil activation: pression stable + débit continu
- seuil maintien: débit constant ±10%
- seuil extinction: chute pression ou stagnation
- loi approx: P = Delta_p * Q
- pertes propres: turbulence, fuite, friction fluide
- saturation basse: débit nul
- saturation haute: cavitation / turbulence forte
- unité sortie pin: W

## M2_C — capteur thermique différentiel
- grandeur captée exacte: gradient thermique
- zone de captation: source chaude / froide
- interface de prise: thermocouple / RTD
- seuil activation: Delta_T > seuil; exemple provisoire > 5°C
- seuil maintien: Delta_T stable
- seuil extinction: Delta_T -> 0
- loi approx: Q = k * Delta_T
- pertes propres: dissipation, conduction parasite
- saturation basse: bruit thermique
- saturation haute: équilibre thermique / limite matériaux
- unité sortie pin: W thermique estimé
