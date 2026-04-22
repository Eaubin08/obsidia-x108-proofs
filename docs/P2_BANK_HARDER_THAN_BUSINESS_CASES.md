# P2 Bank — Harder Than Business Cases

## Status

Derived from the public bank-robo scenario benchmark overlay.

Total harder cases: 6

## 1. Virement-Salaire

- business_expected_decision: `AUTORISER`
- x108_gate_observed: `HOLD`
- severity: `S2`
- reason_code: `RISK_FLAGS_REQUIRE_DELAY`
- description: Réception de salaire mensuel
- why_x108_hardened: X-108 a imposé une temporisation souveraine au lieu d'une lecture métier plus permissive; raison publique observée: RISK_FLAGS_REQUIRE_DELAY; sévérité observée: S2

## 2. Paiement-Abonnement

- business_expected_decision: `AUTORISER`
- x108_gate_observed: `BLOCK`
- severity: `S4`
- reason_code: `CONTRADICTION_THRESHOLD_REACHED`
- description: Paiement d'abonnement mensuel
- why_x108_hardened: X-108 a lu ce cas comme non admissible dans le périmètre public courant; présence de contradiction ou conflit interne dans le signal; sévérité observée: S4

## 3. Virement-Loyer

- business_expected_decision: `AUTORISER`
- x108_gate_observed: `HOLD`
- severity: `S2`
- reason_code: `RISK_FLAGS_REQUIRE_DELAY`
- description: Paiement du loyer mensuel
- why_x108_hardened: X-108 a imposé une temporisation souveraine au lieu d'une lecture métier plus permissive; raison publique observée: RISK_FLAGS_REQUIRE_DELAY; sévérité observée: S2

## 4. Achat-Montant-Eleve

- business_expected_decision: `ANALYSER`
- x108_gate_observed: `BLOCK`
- severity: `S4`
- reason_code: `CONTRADICTION_THRESHOLD_REACHED`
- description: Achat d'un montant inhabituel
- why_x108_hardened: X-108 a lu ce cas comme non admissible dans le périmètre public courant; présence de contradiction ou conflit interne dans le signal; sévérité observée: S4

## 5. Virement-Nouveau-Beneficiaire

- business_expected_decision: `ANALYSER`
- x108_gate_observed: `BLOCK`
- severity: `S4`
- reason_code: `CONTRADICTION_THRESHOLD_REACHED`
- description: Virement vers nouveau bénéficiaire
- why_x108_hardened: X-108 a lu ce cas comme non admissible dans le périmètre public courant; présence de contradiction ou conflit interne dans le signal; sévérité observée: S4

## 6. Retrait-ATM-Etranger

- business_expected_decision: `ANALYSER`
- x108_gate_observed: `BLOCK`
- severity: `S4`
- reason_code: `CONTRADICTION_THRESHOLD_REACHED`
- description: Retrait ATM dans pays étranger
- why_x108_hardened: X-108 a lu ce cas comme non admissible dans le périmètre public courant; présence de contradiction ou conflit interne dans le signal; sévérité observée: S4

