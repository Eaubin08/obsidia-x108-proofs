# Audit visuel 3 domaines — Obsidia X-108

Date : 2026-04-28 21:42:51
Endpoint : `http://localhost:3001/kernel/ragnarok`

## Tableau decisionnel

| Domaine | Sens | Verdict | Gate X-108 | Integrity | Governance | Readiness | Moyenne | Severity | Reason |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| bank | Transaction bancaire risquee : nouveau beneficiaire, fraude elevee, urgence elevee, delai X-108 non respecte. | ANALYZE | BLOCK | 0.5 | 0.95 | 0.66 | 0.7033 | S4 | CONTRADICTION_THRESHOLD_REACHED |
| trading | Ordre trading risque : levier, exposition, drawdown, slippage et desequilibre carnet eleves. | REVIEW | HOLD | 0.5 | 0.75 | 0.6 | 0.6167 | S2 | RISK_FLAGS_REQUIRE_DELAY |
| gps_defense_aviation | Navigation aviation/GPS degradee : signal faible, conflit source, spoofing, deviation, skew temporel. | ABORT_TRAJECTORY | BLOCK | 0.35 | 0.95 | 0.51 | 0.6033 | S4 | CONTRADICTION_THRESHOLD_REACHED |

## Lecture par domaine

### bank

- Sens metier : Transaction bancaire risquee : nouveau beneficiaire, fraude elevee, urgence elevee, delai X-108 non respecte.
- Verdict metier : `ANALYZE`
- Gate X-108 : `BLOCK`
- Severity : `S4`
- Reason : `CONTRADICTION_THRESHOLD_REACHED`
- Integrity : 0.5
- Governance : 0.95
- Readiness : 0.66
- Moyenne : 0.7033
- Lecture securite : SECURITE FORTE — action refusee avant execution. Le moteur detecte un risque, une contradiction ou une fiabilite insuffisante.
- Input : `.\audit\local_diag\audit_visuel_3_domaines_20260428_214242\input_bank.json`
- Response : `.\audit\local_diag\audit_visuel_3_domaines_20260428_214242\response_bank.json`
- Hash SHA256 : `A765CA6E62305B82AF4D10BD86987CCBBE1E32ADCFB36D8D8FF86F35088EF687`

### trading

- Sens metier : Ordre trading risque : levier, exposition, drawdown, slippage et desequilibre carnet eleves.
- Verdict metier : `REVIEW`
- Gate X-108 : `HOLD`
- Severity : `S2`
- Reason : `RISK_FLAGS_REQUIRE_DELAY`
- Integrity : 0.5
- Governance : 0.75
- Readiness : 0.6
- Moyenne : 0.6167
- Lecture securite : SECURITE TEMPORELLE — action retenue. X-108 impose une attente / coherence avant action.
- Input : `.\audit\local_diag\audit_visuel_3_domaines_20260428_214242\input_trading.json`
- Response : `.\audit\local_diag\audit_visuel_3_domaines_20260428_214242\response_trading.json`
- Hash SHA256 : `E0E549343221AF06C1B7F4F4E9E92733F740131786EF2BD9C06DA5D22227803D`

### gps_defense_aviation

- Sens metier : Navigation aviation/GPS degradee : signal faible, conflit source, spoofing, deviation, skew temporel.
- Verdict metier : `ABORT_TRAJECTORY`
- Gate X-108 : `BLOCK`
- Severity : `S4`
- Reason : `CONTRADICTION_THRESHOLD_REACHED`
- Integrity : 0.35
- Governance : 0.95
- Readiness : 0.51
- Moyenne : 0.6033
- Lecture securite : SECURITE FORTE — action refusee avant execution. Le moteur detecte un risque, une contradiction ou une fiabilite insuffisante.
- Input : `.\audit\local_diag\audit_visuel_3_domaines_20260428_214242\input_gps_defense_aviation.json`
- Response : `.\audit\local_diag\audit_visuel_3_domaines_20260428_214242\response_gps_defense_aviation.json`
- Hash SHA256 : `3B540A57B37A91FB73F721CB6D57B501083C87B77579962FABDF8B5E748A69CE`

## Ce que cet audit prouve

| Axe | Preuve visible | Statut |
|---|---|---:|
| Routage domaine | Les 3 domaines repondent via /kernel/ragnarok | OK |
| Gouvernance X-108 | Chaque domaine retourne un x108_gate | OK |
| Securite avant action | Les cas risques sont bloques/controles avant execution | OK |
| Tracabilite | Inputs, reponses, logs et hash SHA256 sont sauvegardes | OK |
| Auditabilite | Rapport Markdown + JSON + CSV generes | OK |

## Limites

- Ne prouve pas une connexion bancaire reelle.
- Ne prouve pas une connexion avion reelle.
- Ne prouve pas une execution trading reelle.
- Prouve que le moteur recoit, gouverne, refuse/retient et trace des decisions simulees multi-domaines.
