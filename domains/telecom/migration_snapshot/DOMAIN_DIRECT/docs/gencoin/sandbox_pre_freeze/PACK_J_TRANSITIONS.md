# PACK J — Transitions d'état

| Transition | Déclencheur | Métrique | Seuil | Action autorisée / interdite |
|---|---|---|---|---|
| START -> ON | M2 actif | pin_real, sigma, truth | theta_on + sigma>=0.7 + truth>=0.8 | autoriser ON |
| ON -> HOLD | chute partielle | pin_real, flux | theta_hold | maintien sans relance excessive |
| HOLD -> SAFE_OFF | perte prolongée | temps_HOLD, truth | timeout ou truth<0.5 | arrêt propre |
| ON -> FALSE_ON | assistance dominante | assisted_ratio | >0.5 | rejeter ON |
| ASSISTED_ON -> REJECTED | relance excessive | Relaunch_cost | seuil_R | bloquer régime |
| DECAY -> HOLD | dégradation contrôlée | Delta_G, sigma | orange | stabiliser |
| HOLD -> ON | récupération | pin_real, truth | theta_on + truth_ok | reprise |
| HOLD -> OFF | absence reprise | temps_HOLD | timeout | arrêt |
