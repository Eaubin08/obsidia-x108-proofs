# Carte d'états

États:
- START
- ON
- HOLD
- SAFE_OFF
- FALSE_ON
- ASSISTED_ON
- DECAY
- REJECTED
- OFF

Transitions:
- START -> ON
- ON -> HOLD
- HOLD -> SAFE_OFF
- ON -> FALSE_ON
- ASSISTED_ON -> REJECTED
- DECAY -> HOLD
- HOLD -> ON
- HOLD -> OFF

Règle dure:
ON réel ≠ ON assisté ≠ faux ON.

ON réel: Delta_G stable, assisted_ratio faible, truth_score haut.
ON assisté: sortie maintenue mais aide visible.
Faux ON: sortie apparente stable mais vérité basse ou assistance dominante.
