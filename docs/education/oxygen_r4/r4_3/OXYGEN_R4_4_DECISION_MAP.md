# Oxygen R4.4 — carte de décision architecturale (principes seulement)

**Statut :** aucune calibration, aucun paramètre, aucun code, aucune porte P-CAL. Les témoins R4.3 (R4.3.1 `c3626447…`, R4.3.2 `a4b0c28d…`) sont **consommés** : ils ont servi à concevoir et à critiquer R4.3. Ils **ne peuvent pas** valider R4.4. Une validation de R4.4 exigera de **nouveaux** témoins, écrits par un relecteur qui ne les a pas vus, et le curriculum V0.4.

| # | Principe | Ce qu'il change | Révision du pré-enregistrement ? |
|---|---|---|---|
| P1 | **Aucune réponse fondée sur une unique classe non corroborée.** On supprime la voie (b) de R4.3 ; seule une corroboration par des preuves indépendantes autorise une réponse. Exception éventuelle : `RAPPEL` (phrase identique), exclu des métriques. | retire la source d'ADV-3 ; risque de couverture quasi nulle tant que le curriculum est pauvre | **oui, substantielle** : condition 1 et K3 sont modifiées, la voie (b) est retirée |
| P2 | **Validation préalable des classes.** Une classe ne vote que si sa fiabilité a été **vérifiée** sur l'enseignement (N_c ≥ 1, au moins une réussite en leave-one-out interne). L'a priori seul (N_c = 0, r = 0,5) ne suffit jamais. | ferme le trou de la voie (a), qui était satisfaite par l'a priori | oui (K6 et la fiabilité) |
| P3 | **Contrôle des signaux accidentellement discriminants.** Un trait n'est tenu pour discriminant que s'il est **attesté dans au moins deux exemplaires distincts** de l'étiquette. Un trait vu une seule fois ne sert ni de preuve ni de contre-preuve. Ce n'est pas un paramètre réglé : c'est la plus petite répétition possible. | traite la cause d'ADV-3 (un trait propre à un sens par hasard) | oui (C1 et C2) |
| P4 | **Mots inconnus et hors domaine.** Hors domaine = aucun trait **informatif** (P3) en commun avec l'enseignement → `PREUVE_INSUFFISANTE`. En configuration B (sans lemmatisation), la contre-preuve lexicale n'est **pas** fiable, et le rapport doit le **déclarer** ; aucune règle compensatoire ad hoc. | rend explicite la limite de NEG-MIX-UNBAL en B, au lieu de la masquer | précision |
| P5 | **Préserver les réponses justifiées.** Quand au moins deux classes **validées** (P2) désignent la même étiquette, avec des provenances disjointes et sans contre-preuve attestée (P3), la réponse est donnée. | garantit que R4.4 n'est pas une abstention universelle par construction | non (reprend l'esprit de K3) |

**Conséquence attendue, déclarée d'avance :**
- sur l'enseignement V0 (2 à 3 exemples par sens), P1 à P3 rendent l'élève **quasi muet**, ce qui est correct ;
- R4.4 n'a de sens qu'**avec** le curriculum V0.4 (au moins 5 exemples par sens).

**Ordre recommandé :**
1. curriculum V0.4 rédigé et accepté ;
2. décision du fondateur sur P1 à P5 ;
3. rédaction de R4.4, relecture, pré-enregistrement avec **nouveaux** témoins écrits à l'aveugle ;
4. seulement ensuite, build et P-CAL.
