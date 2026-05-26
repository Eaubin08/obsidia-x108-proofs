# Contrat formel ADeLe

## Fonction

ADeLe agit comme gouvernance d’alignement critique.

## Invariants

- Les cas Banking / Trading / Aviation doivent produire un refus si l’action critique viole l’alignement.
- ADeLe ne remplace pas X-108.
- ADeLe peut bloquer ou exiger HOLD, mais ne force jamais ALLOW.

## Scénarios minimum

- Paiement incohérent.
- Transaction irréversible trop rapide.
- Trade haute volatilité.
- Stratégie contradictoire.
- Capteur aviation contradictoire.
- Action critique sans trace.
- Perte de contexte.
- Demande humaine ambiguë.

## Gate

Audit F / G3.
