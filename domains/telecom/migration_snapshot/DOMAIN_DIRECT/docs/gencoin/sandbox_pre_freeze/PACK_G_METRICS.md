# PACK G — Métriques / observabilité

| Variable | Unité | Plage nominale | Orange | Rouge |
|---|---|---|---|---|
| pin | W | 1-100 | <1 | 0 |
| pout | W | ~0.8 pin | <0.5 pin | <0.2 pin |
| Delta_G | ratio | ~1 ou explicable | <1 ou instable | illusion >1 non expliquée / <0.5 |
| flux | relatif | stable | fluctuant | instable |
| L_total | % pertes | <20% | 20-40% | >40% |
| L_M2 | % | <10% | 10-20% | >20% |
| L_M3 | % | <15% | 15-30% | >30% |
| L_M4 | % | <10% | 10-25% | >25% |
| R_storage | relatif | stable | fuite | chute |
| Relaunch_cost | W ou coût relatif | faible | modéré | élevé |
| assisted_ratio | % | <20% | 20-50% | >50% |
| temps_ON | s | stable | oscillant | chute |
| temps_HOLD | s | court | long | bloqué |
| temps_SAFE_OFF | s | contrôlé | lent | chaotique |
| sigma_score | [0,1] | >0.7 | 0.4-0.7 | <0.4 |
| truth_score | [0,1] | >0.8 | 0.5-0.8 | <0.5 |
