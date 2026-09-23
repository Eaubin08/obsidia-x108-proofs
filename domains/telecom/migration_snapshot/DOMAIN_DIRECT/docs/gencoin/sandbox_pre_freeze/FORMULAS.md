# Formules noyau sandbox

## assisted_ratio
assisted_ratio = (paux + pstorage_out) / (pin_raw + paux + pstorage_out)

## ΔG
Delta_G = pout / (pin_raw + paux + pstorage_out)

## truth_score
truth = 1 - alpha * assisted_ratio - beta * hidden_loss - gamma * relaunch_dependency

## sigma_score
sigma = w1 * stability + w2 * continuity + w3 * coherence - w4 * saturation - w5 * noise

## Balance
Balance(x) = ponderation(impact, coherence, stabilite, cout)

## Captation inertielle
E = 1/2 * I * omega^2

## Pression / débit
P = Delta_p * Q

## Flux thermique approx
Q_heat = k * Delta_T

## Conversion
pout_conv = eta_M3 * pin_real

## Stockage
R_storage(t+dt) = R_storage(t) + pstorage_in * dt - pstorage_out * dt - L_storage * dt

## Gain vérité
Production réelle + preuve + vérité + audit + admissibilité -> valeur économique
