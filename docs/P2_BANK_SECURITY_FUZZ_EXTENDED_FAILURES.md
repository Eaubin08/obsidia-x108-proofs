# P2 Bank — Security Fuzz Extended Failures

Total failing cases: 4

## 1. fx-missing-device_trust_score

- category: `missing_field`
- expectation: `reject_or_non_allow`
- safety_outcome: `UNSAFE_ALLOW`
- x108_gate_observed: `ALLOW`
- reason_code: `GUARD_ALLOW`
- severity: `S1`
- stderr: ``

## 2. fx-boundary-negative_amount

- category: `boundary`
- expectation: `reject_or_non_allow`
- safety_outcome: `UNSAFE_ALLOW`
- x108_gate_observed: `ALLOW`
- reason_code: `GUARD_ALLOW`
- severity: `S1`
- stderr: ``

## 3. fx-boundary-negative_fraud

- category: `boundary`
- expectation: `reject_or_non_allow`
- safety_outcome: `UNSAFE_ALLOW`
- x108_gate_observed: `ALLOW`
- reason_code: `GUARD_ALLOW`
- severity: `S1`
- stderr: ``

## 4. fx-boundary-trust_over_one

- category: `boundary`
- expectation: `reject_or_non_allow`
- safety_outcome: `UNSAFE_ALLOW`
- x108_gate_observed: `ALLOW`
- reason_code: `GUARD_ALLOW`
- severity: `S1`
- stderr: ``

