# Contrat d’isolation OS3 / OS4

## Invariant central

OS3 décide et trace.
OS4 contextualise, explique et raconte.

OS4 ne peut jamais :
- modifier une décision OS3 ;
- transformer HOLD/BLOCK en ALLOW ;
- effacer une trace ;
- court-circuiter X-108 ;
- produire une action irréversible.

## Tests requis

1. OS4 reçoit une décision OS3.
2. OS4 tente une mutation.
3. Le système bloque.
4. Une trace VIOLATION est produite.
5. Le replay prouve la non-contamination.

## Gate

Audit E / G3.
