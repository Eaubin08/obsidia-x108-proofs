# Audit total metrics / preuve / securite / tracabilite - Obsidia X-108

Date : 2026-04-28 22:41:13
Endpoint : `http://localhost:3001/kernel/ragnarok`
Audit dir : `.\audit\local_diag\audit_total_metrics_proof_20260428_224101`

## 1. Git

| Champ | Valeur |
|---|---|
| Branche | `temp-reims` |
| Commit | `977bb2fa5a2ccccd60e8e509f59695dc463ec995` |
| Tags HEAD | `audit-traceability-3-domains-20260428-223139` |
| Status | ` M merkle_seal.json; ?? RUN_AUDIT_TOTAL_METRICS_PROOF.ps1` |

## 2. Tableau decisionnel

| Domaine | Verdict | Gate X-108 | Integrity | Governance | Readiness | Moyenne | Severity | Reason | Nb metriques |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|
| bank | ANALYZE | BLOCK | 0.5 | 0.95 | 0.66 | 0.7033 | S4 | CONTRADICTION_THRESHOLD_REACHED | 111 |
| trading | REVIEW | HOLD | 0.5 | 0.75 | 0.6 | 0.6167 | S2 | RISK_FLAGS_REQUIRE_DELAY | 108 |
| gps_defense_aviation | ABORT_TRAJECTORY | BLOCK | 0.35 | 0.95 | 0.51 | 0.6033 | S4 | CONTRADICTION_THRESHOLD_REACHED | 102 |

## 3. Hashes par domaine

| Domaine | Input SHA | Response SHA | Metrics SHA | Metrics CSV |
|---|---:|---:|---:|---|
| bank | `988680FD35AD` | `30BF5FA50169` | `9D1F69D233EE` | `.\audit\local_diag\audit_total_metrics_proof_20260428_224101\metrics_full_bank.csv` |
| trading | `A09D6DEE2AD5` | `DCAB988639AB` | `F2FBE36E04EC` | `.\audit\local_diag\audit_total_metrics_proof_20260428_224101\metrics_full_trading.csv` |
| gps_defense_aviation | `0E9835CD2BEB` | `08B06D5F7547` | `1C97BBF199CC` | `.\audit\local_diag\audit_total_metrics_proof_20260428_224101\metrics_full_gps_defense_aviation.csv` |

## 4. Compteurs tracabilite

| Compteur | Valeur |
|---|---:|
| Domaines testes | 3 |
| Inputs generes | 3 |
| Responses generees | 3 |
| Fichiers metrics generes | 3 |
| Decisions avant audit | 7231 |
| Decisions apres audit | 7234 |
| Decisions creees pendant audit | 3 |
| Fichiers runtime hashes | 13 |
| Merkle seal present | True |

## 5. Racines et scellage

| Preuve | SHA256 |
|---|---|
| TRACE_MANIFEST | `97C95FB3C3AD14E90187865B262A122F4799D136785971BFD4D4DD5C25C84846` |
| MERKLE_SEAL | `9D1D9AAEDCF8520A4171448F17B21782986060FAE680F714EBF8CAA03FCE8256` |
| SERVER_STDOUT | `570A290942A1861B4865221A2284F456816FD760F13177C1F84A62AFC9348AB6` |
| SERVER_STDERR | `CC6D4867014A95371517C73A16698E333BB256154E7CAD0AD4FE8EFF1DE1F3AC` |
| AUDIT_ROOT | `017a9b089c3c2e83d0c2113a1dec603a6468cc78f995df1a5db84806e4ed9906` |

## 6. Decisions runtime creees pendant audit

| Fichier | Taille | SHA256 court |
|---|---:|---:|
| `decision_bank_1777408869717.json` | 3720 | `A2908A523C87` |
| `decision_gps_defense_aviation_1777408870751.json` | 3448 | `C452139A95B1` |
| `decision_trading_1777408870352.json` | 3461 | `C20744FB4766` |

## 7. Lecture securite par domaine

### bank

- Sens : Transaction bancaire mobile risquee : nouveau beneficiaire, fraude elevee, urgence elevee, delai X-108 non respecte.
- Verdict : `ANALYZE`
- Gate X-108 : `BLOCK`
- Severity : `S4`
- Reason : `CONTRADICTION_THRESHOLD_REACHED`
- Lecture securite : BLOCK : action refusee avant execution. Risque critique, contradiction ou coherence insuffisante.
- Nombre total de metriques retournees : `111`
- Fichier complet metriques : `.\audit\local_diag\audit_total_metrics_proof_20260428_224101\metrics_full_bank.csv`

### trading

- Sens : Ordre de trading risque : levier, exposition, drawdown, slippage et desequilibre carnet eleves.
- Verdict : `REVIEW`
- Gate X-108 : `HOLD`
- Severity : `S2`
- Reason : `RISK_FLAGS_REQUIRE_DELAY`
- Lecture securite : HOLD : action retenue. X-108 impose delai, refroidissement ou validation supplementaire.
- Nombre total de metriques retournees : `108`
- Fichier complet metriques : `.\audit\local_diag\audit_total_metrics_proof_20260428_224101\metrics_full_trading.csv`

### gps_defense_aviation

- Sens : Navigation aviation/GPS degradee : faible qualite signal, conflit source, risque spoofing, deviation et skew temporel.
- Verdict : `ABORT_TRAJECTORY`
- Gate X-108 : `BLOCK`
- Severity : `S4`
- Reason : `CONTRADICTION_THRESHOLD_REACHED`
- Lecture securite : BLOCK : action refusee avant execution. Risque critique, contradiction ou coherence insuffisante.
- Nombre total de metriques retournees : `102`
- Fichier complet metriques : `.\audit\local_diag\audit_total_metrics_proof_20260428_224101\metrics_full_gps_defense_aviation.csv`

## 8. Toutes les metriques retournees

### Metriques completes - bank

| Path | Type | Valeur |
|---|---:|---|
| `domain` | `String` | bank |
| `market_verdict` | `String` | ANALYZE |
| `confidence` | `Decimal` | 0.5 |
| `confidence_integrity` | `Decimal` | 0.5 |
| `confidence_governance` | `Decimal` | 0.95 |
| `confidence_readiness` | `Decimal` | 0.66 |
| `confidence_scope` | `String` | integrity |
| `governance_scope` | `String` | x108_decision_robustness |
| `readiness_scope` | `String` | harmonic_integrity_governance |
| `contradictions[0]` | `String` | URGENT_BEHAVIOR |
| `contradictions[1]` | `String` | IDENTITY_CONTEXT_MISMATCH |
| `contradictions[2]` | `String` | URGENT_BEHAVIOR |
| `contradictions[3]` | `String` | IDENTITY_CONTEXT_MISMATCH |
| `contradictions[4]` | `String` | URGENT_BEHAVIOR |
| `contradictions[5]` | `String` | IDENTITY_CONTEXT_MISMATCH |
| `contradictions[6]` | `String` | URGENT_BEHAVIOR |
| `contradictions[7]` | `String` | IDENTITY_CONTEXT_MISMATCH |
| `unknowns[0]` | `String` | TEMPORAL_LOCK_NOT_MATURE |
| `unknowns[1]` | `String` | RECENT_FAILED_ATTEMPTS |
| `unknowns[2]` | `String` | TEMPORAL_LOCK_NOT_MATURE |
| `unknowns[3]` | `String` | RECENT_FAILED_ATTEMPTS |
| `unknowns[4]` | `String` | TEMPORAL_LOCK_NOT_MATURE |
| `unknowns[5]` | `String` | RECENT_FAILED_ATTEMPTS |
| `unknowns[6]` | `String` | TEMPORAL_LOCK_NOT_MATURE |
| `unknowns[7]` | `String` | RECENT_FAILED_ATTEMPTS |
| `unknowns[8]` | `String` | TICKET_NOT_READY |
| `risk_flags[0]` | `String` | FRAUD_PATTERN |
| `risk_flags[1]` | `String` | FRAUD_PATTERN |
| `x108_gate` | `String` | BLOCK |
| `reason_code` | `String` | CONTRADICTION_THRESHOLD_REACHED |
| `severity` | `String` | S4 |
| `decision_id` | `String` | bank-05110188e7a2 |
| `trace_id` | `String` | 8dbb6398-f49e-4ef6-9265-4c284bc32f9e |
| `ticket_required` | `Boolean` | False |
| `ticket_id` | `null` |  |
| `attestation_ref` | `String` | 07fa66b12974d26f23c49c3d |
| `source` | `String` | canonical_framework |
| `evidence_refs[0]` | `String` | e47a240fff0baf69 |
| `evidence_refs[1]` | `String` | 67ccfa7e13b28f33 |
| `evidence_refs[2]` | `String` | e07af98a0a87c218 |
| `evidence_refs[3]` | `String` | 1b301c649153a7ee |
| `evidence_refs[4]` | `String` | 4fd9e32c9e33d92b |
| `evidence_refs[5]` | `String` | 730dce7d5101307d |
| `evidence_refs[6]` | `String` | 608f5b88ee8cafd9 |
| `evidence_refs[7]` | `String` | 800a13efde5c2904 |
| `evidence_refs[8]` | `String` | 5d506b1f101b616e |
| `evidence_refs[9]` | `String` | 78835d78532fe59d |
| `evidence_refs[10]` | `String` | 4e4fb3735e36ad11 |
| `evidence_refs[11]` | `String` | f503e8b5c49b828d |
| `evidence_refs[12]` | `String` | meta:UnknownsAgent |
| `evidence_refs[13]` | `String` | meta:ConflictResolutionAgent |
| `evidence_refs[14]` | `String` | meta:PolicyScopeAgent |
| `evidence_refs[15]` | `String` | meta:TicketReadinessAgent |
| `evidence_refs[16]` | `String` | meta:TraceIntegrityAgent |
| `evidence_refs[17]` | `String` | meta:AttestationReadinessAgent |
| `evidence_refs[18]` | `String` | meta:HumanOverrideEligibilityAgent |
| `evidence_refs[19]` | `String` | meta:SeverityClassifierAgent |
| `evidence_refs[20]` | `String` | meta:ReplayConsistencyAgent |
| `evidence_refs[21]` | `String` | meta:ProofConsistencyAgent |
| `metrics.authorize_score` | `Int32` | 0 |
| `metrics.analyze_score` | `Int32` | 0 |
| `metrics.block_score` | `Int32` | 0 |
| `metrics.proof_ready` | `Boolean` | True |
| `metrics.deterministic` | `Boolean` | True |
| `raw_engine.domain` | `String` | bank |
| `raw_engine.agent_votes[0]` | `String` | TransactionContextAgent |
| `raw_engine.agent_votes[1]` | `String` | CounterpartyAgent |
| `raw_engine.agent_votes[2]` | `String` | LiquidityExposureAgent |
| `raw_engine.agent_votes[3]` | `String` | BehaviorShiftAgent |
| `raw_engine.agent_votes[4]` | `String` | FraudPatternAgent |
| `raw_engine.agent_votes[5]` | `String` | LimitPolicyAgent |
| `raw_engine.agent_votes[6]` | `String` | AffordabilityAgent |
| `raw_engine.agent_votes[7]` | `String` | TemporalUrgencyAgent |
| `raw_engine.agent_votes[8]` | `String` | IdentityMismatchAgent |
| `raw_engine.agent_votes[9]` | `String` | NarrativeConflictAgent |
| `raw_engine.agent_votes[10]` | `String` | RecoveryPathAgent |
| `raw_engine.agent_votes[11]` | `String` | BankProofAgent |
| `raw_engine.vote_count` | `Int32` | 12 |
| `sigma_override` | `Boolean` | False |
| `sigma_step.step` | `Int32` | 0 |
| `sigma_step.severity` | `String` | S4 |
| `sigma_step.z` | `Decimal` | 1.9 |
| `sigma_step.z_t` | `Decimal` | 1.9 |
| `sigma_step.velocity` | `Int32` | 0 |
| `sigma_step.acceleration` | `Int32` | 0 |
| `sigma_step.stability_status` | `String` | STABLE |
| `sigma_step.violations` | `array_empty` |  |
| `sigma_step.coherence_ok` | `Boolean` | True |
| `sigma_report.pass` | `Boolean` | True |
| `sigma_report.status` | `String` | PASS |
| `sigma_report.steps_evaluated` | `Int32` | 1 |
| `sigma_report.unstable_steps` | `Int32` | 0 |
| `sigma_report.violations_total` | `Int32` | 0 |
| `sigma_report.violation_types` | `array_empty` |  |
| `sigma_report.metrics.mean_velocity` | `Int32` | 0 |
| `sigma_report.metrics.total_steps` | `Int32` | 1 |
| `sigma_report.metrics.tau_max_used` | `Int32` | 5 |
| `sigma_report.metrics.accel_limit_used` | `Decimal` | 0.6 |
| `sigma_report.constraints.vanishing_acceleration` | `String` | OK |
| `sigma_report.constraints.velocity_band` | `String` | OK |
| `sigma_report.constraints.coherence_stationarity` | `String` | OK |
| `sigma_report.steps_detail[0].step` | `Int32` | 0 |
| `sigma_report.steps_detail[0].severity` | `String` | S4 |
| `sigma_report.steps_detail[0].z` | `Decimal` | 1.9 |
| `sigma_report.steps_detail[0].z_t` | `Decimal` | 1.9 |
| `sigma_report.steps_detail[0].velocity` | `Int32` | 0 |
| `sigma_report.steps_detail[0].acceleration` | `Int32` | 0 |
| `sigma_report.steps_detail[0].stability_status` | `String` | STABLE |
| `sigma_report.steps_detail[0].violations` | `array_empty` |  |
| `sigma_report.steps_detail[0].coherence_ok` | `Boolean` | True |
| `sigma_report.stdout` | `String` | V18.9 Sigma Dynamic Stability - PASS Steps evaluated : 1 Unstable steps  : 0 Total violations: 0 Config source   : C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\sigma\sigma_config.json tau_max         : 5.0 accel_limit     : 0.6 No violations detected.  |

### Metriques completes - trading

| Path | Type | Valeur |
|---|---:|---|
| `domain` | `String` | trading |
| `market_verdict` | `String` | REVIEW |
| `confidence` | `Decimal` | 0.5 |
| `confidence_integrity` | `Decimal` | 0.5 |
| `confidence_governance` | `Decimal` | 0.75 |
| `confidence_readiness` | `Decimal` | 0.6 |
| `confidence_scope` | `String` | integrity |
| `governance_scope` | `String` | x108_decision_robustness |
| `readiness_scope` | `String` | harmonic_integrity_governance |
| `contradictions` | `array_empty` |  |
| `unknowns` | `array_empty` |  |
| `risk_flags[0]` | `String` | POOR_EXECUTION |
| `risk_flags[1]` | `String` | PORTFOLIO_STRESS |
| `risk_flags[2]` | `String` | POOR_EXECUTION |
| `risk_flags[3]` | `String` | PORTFOLIO_STRESS |
| `x108_gate` | `String` | HOLD |
| `reason_code` | `String` | RISK_FLAGS_REQUIRE_DELAY |
| `severity` | `String` | S2 |
| `decision_id` | `String` | trading-355b8a6d25c6 |
| `trace_id` | `String` | c3a4fb0e-72ff-4f36-b926-8d69c8fecf6b |
| `ticket_required` | `Boolean` | False |
| `ticket_id` | `null` |  |
| `attestation_ref` | `String` | 8498a076da0d7d43100e6bea |
| `source` | `String` | canonical_framework |
| `evidence_refs[0]` | `String` | 447ab2694752451f |
| `evidence_refs[1]` | `String` | 5ec935553d3129f2 |
| `evidence_refs[2]` | `String` | 95c1c421cff63054 |
| `evidence_refs[3]` | `String` | 10bf8377bfaee488 |
| `evidence_refs[4]` | `String` | 65add1cd111e894a |
| `evidence_refs[5]` | `String` | 14882b93afb078c4 |
| `evidence_refs[6]` | `String` | c5bf4eca91759fdd |
| `evidence_refs[7]` | `String` | d567b82ceb48914a |
| `evidence_refs[8]` | `String` | f7c4f72af041c476 |
| `evidence_refs[9]` | `String` | 511e8f94809ed17d |
| `evidence_refs[10]` | `String` | ad28c72d071bc612 |
| `evidence_refs[11]` | `String` | 48b4fb691be8820d |
| `evidence_refs[12]` | `String` | c70875bd1c363cea |
| `evidence_refs[13]` | `String` | 1f80f5687e986e42 |
| `evidence_refs[14]` | `String` | c678c594c3430478 |
| `evidence_refs[15]` | `String` | dc689d962f969ad9 |
| `evidence_refs[16]` | `String` | 07e0186a3e051476 |
| `evidence_refs[17]` | `String` | meta:UnknownsAgent |
| `evidence_refs[18]` | `String` | meta:ConflictResolutionAgent |
| `evidence_refs[19]` | `String` | meta:PolicyScopeAgent |
| `evidence_refs[20]` | `String` | meta:TicketReadinessAgent |
| `evidence_refs[21]` | `String` | meta:TraceIntegrityAgent |
| `evidence_refs[22]` | `String` | meta:AttestationReadinessAgent |
| `evidence_refs[23]` | `String` | meta:HumanOverrideEligibilityAgent |
| `evidence_refs[24]` | `String` | meta:SeverityClassifierAgent |
| `evidence_refs[25]` | `String` | meta:ReplayConsistencyAgent |
| `evidence_refs[26]` | `String` | meta:ProofConsistencyAgent |
| `metrics.buy_score` | `Int32` | 0 |
| `metrics.sell_score` | `Int32` | 0 |
| `metrics.hold_score` | `Int32` | 0 |
| `metrics.proof_ready` | `Boolean` | True |
| `metrics.deterministic` | `Boolean` | True |
| `raw_engine.domain` | `String` | trading |
| `raw_engine.agent_votes[0]` | `String` | MarketDataAgent |
| `raw_engine.agent_votes[1]` | `String` | LiquidityAgent |
| `raw_engine.agent_votes[2]` | `String` | VolatilityAgent |
| `raw_engine.agent_votes[3]` | `String` | MacroAgent |
| `raw_engine.agent_votes[4]` | `String` | CorrelationAgent |
| `raw_engine.agent_votes[5]` | `String` | EventAgent |
| `raw_engine.agent_votes[6]` | `String` | MomentumAgent |
| `raw_engine.agent_votes[7]` | `String` | MeanReversionAgent |
| `raw_engine.agent_votes[8]` | `String` | BreakoutAgent |
| `raw_engine.agent_votes[9]` | `String` | PatternAgent |
| `raw_engine.agent_votes[10]` | `String` | SentimentAgent |
| `raw_engine.agent_votes[11]` | `String` | PredictionAgent |
| `raw_engine.agent_votes[12]` | `String` | PortfolioAgent |
| `raw_engine.agent_votes[13]` | `String` | ExecutionQualityAgent |
| `raw_engine.agent_votes[14]` | `String` | RegimeShiftAgent |
| `raw_engine.agent_votes[15]` | `String` | PortfolioStressAgent |
| `raw_engine.agent_votes[16]` | `String` | ProofConsistencyAgent |
| `raw_engine.vote_count` | `Int32` | 17 |
| `sigma_override` | `Boolean` | False |
| `sigma_step.step` | `Int32` | 0 |
| `sigma_step.severity` | `String` | S2 |
| `sigma_step.z` | `Decimal` | 0.7 |
| `sigma_step.z_t` | `Decimal` | 0.7 |
| `sigma_step.velocity` | `Int32` | 0 |
| `sigma_step.acceleration` | `Int32` | 0 |
| `sigma_step.stability_status` | `String` | STABLE |
| `sigma_step.violations` | `array_empty` |  |
| `sigma_step.coherence_ok` | `Boolean` | True |
| `sigma_report.pass` | `Boolean` | True |
| `sigma_report.status` | `String` | PASS |
| `sigma_report.steps_evaluated` | `Int32` | 1 |
| `sigma_report.unstable_steps` | `Int32` | 0 |
| `sigma_report.violations_total` | `Int32` | 0 |
| `sigma_report.violation_types` | `array_empty` |  |
| `sigma_report.metrics.mean_velocity` | `Int32` | 0 |
| `sigma_report.metrics.total_steps` | `Int32` | 1 |
| `sigma_report.metrics.tau_max_used` | `Int32` | 5 |
| `sigma_report.metrics.accel_limit_used` | `Decimal` | 0.6 |
| `sigma_report.constraints.vanishing_acceleration` | `String` | OK |
| `sigma_report.constraints.velocity_band` | `String` | OK |
| `sigma_report.constraints.coherence_stationarity` | `String` | OK |
| `sigma_report.steps_detail[0].step` | `Int32` | 0 |
| `sigma_report.steps_detail[0].severity` | `String` | S2 |
| `sigma_report.steps_detail[0].z` | `Decimal` | 0.7 |
| `sigma_report.steps_detail[0].z_t` | `Decimal` | 0.7 |
| `sigma_report.steps_detail[0].velocity` | `Int32` | 0 |
| `sigma_report.steps_detail[0].acceleration` | `Int32` | 0 |
| `sigma_report.steps_detail[0].stability_status` | `String` | STABLE |
| `sigma_report.steps_detail[0].violations` | `array_empty` |  |
| `sigma_report.steps_detail[0].coherence_ok` | `Boolean` | True |
| `sigma_report.stdout` | `String` | V18.9 Sigma Dynamic Stability - PASS Steps evaluated : 1 Unstable steps  : 0 Total violations: 0 Config source   : C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\sigma\sigma_config.json tau_max         : 5.0 accel_limit     : 0.6 No violations detected.  |

### Metriques completes - gps_defense_aviation

| Path | Type | Valeur |
|---|---:|---|
| `domain` | `String` | gps_defense_aviation |
| `market_verdict` | `String` | ABORT_TRAJECTORY |
| `confidence` | `Decimal` | 0.35 |
| `confidence_integrity` | `Decimal` | 0.35 |
| `confidence_governance` | `Decimal` | 0.95 |
| `confidence_readiness` | `Decimal` | 0.51 |
| `confidence_scope` | `String` | integrity |
| `governance_scope` | `String` | x108_decision_robustness |
| `readiness_scope` | `String` | harmonic_integrity_governance |
| `contradictions[0]` | `String` | SOURCE_CONFLICT |
| `contradictions[1]` | `String` | SOURCE_CONFLICT |
| `contradictions[2]` | `String` | SOURCE_CONFLICT |
| `contradictions[3]` | `String` | SOURCE_CONFLICT |
| `unknowns[0]` | `String` | INERTIAL_MISSING |
| `unknowns[1]` | `String` | RADIO_MISSING |
| `unknowns[2]` | `String` | ATTESTATION_NOT_READY |
| `unknowns[3]` | `String` | INERTIAL_MISSING |
| `unknowns[4]` | `String` | RADIO_MISSING |
| `unknowns[5]` | `String` | ATTESTATION_NOT_READY |
| `unknowns[6]` | `String` | INERTIAL_MISSING |
| `unknowns[7]` | `String` | RADIO_MISSING |
| `unknowns[8]` | `String` | ATTESTATION_NOT_READY |
| `unknowns[9]` | `String` | INERTIAL_MISSING |
| `unknowns[10]` | `String` | RADIO_MISSING |
| `unknowns[11]` | `String` | ATTESTATION_NOT_READY |
| `unknowns[12]` | `String` | TICKET_NOT_READY |
| `risk_flags` | `array_empty` |  |
| `x108_gate` | `String` | BLOCK |
| `reason_code` | `String` | CONTRADICTION_THRESHOLD_REACHED |
| `severity` | `String` | S4 |
| `decision_id` | `String` | gps_defense_aviation-dd60e251e9b8 |
| `trace_id` | `String` | 503d39a7-dd26-4faf-b5e1-da6c9ab9d120 |
| `ticket_required` | `Boolean` | False |
| `ticket_id` | `null` |  |
| `attestation_ref` | `String` | 19dcee53c80c0da88d349d53 |
| `source` | `String` | canonical_framework |
| `evidence_refs[0]` | `String` | 7d915b7839dbf211 |
| `evidence_refs[1]` | `String` | dc0a11715aac7cfb |
| `evidence_refs[2]` | `String` | 41796663223c12fc |
| `evidence_refs[3]` | `String` | a4f978c39559e013 |
| `evidence_refs[4]` | `String` | 9ff2b803d2b3673c |
| `evidence_refs[5]` | `String` | 9759a0c3387a3987 |
| `evidence_refs[6]` | `String` | meta:UnknownsAgent |
| `evidence_refs[7]` | `String` | meta:ConflictResolutionAgent |
| `evidence_refs[8]` | `String` | meta:PolicyScopeAgent |
| `evidence_refs[9]` | `String` | meta:TicketReadinessAgent |
| `evidence_refs[10]` | `String` | meta:TraceIntegrityAgent |
| `evidence_refs[11]` | `String` | meta:AttestationReadinessAgent |
| `evidence_refs[12]` | `String` | meta:HumanOverrideEligibilityAgent |
| `evidence_refs[13]` | `String` | meta:SeverityClassifierAgent |
| `evidence_refs[14]` | `String` | meta:ReplayConsistencyAgent |
| `evidence_refs[15]` | `String` | meta:ProofConsistencyAgent |
| `metrics.trajectory_valid_score` | `Int32` | 0 |
| `metrics.recalc_score` | `Decimal` | 0.35 |
| `metrics.degraded_score` | `Int32` | 0 |
| `metrics.abort_score` | `Int32` | 0 |
| `metrics.truth_score` | `Int32` | 0 |
| `metrics.sigma_score` | `Decimal` | 0.35 |
| `metrics.mismatch_gap` | `Decimal` | 0.35 |
| `metrics.proof_ready` | `Boolean` | True |
| `metrics.deterministic` | `Boolean` | True |
| `raw_engine.domain` | `String` | gps_defense_aviation |
| `raw_engine.agent_votes[0]` | `String` | SourceAvailabilityAgent |
| `raw_engine.agent_votes[1]` | `String` | TrajectoryIntegrityAgent |
| `raw_engine.agent_votes[2]` | `String` | SourceConflictAgent |
| `raw_engine.agent_votes[3]` | `String` | TimeSkewAgent |
| `raw_engine.agent_votes[4]` | `String` | BrownoutAgent |
| `raw_engine.agent_votes[5]` | `String` | GpsAttestationReadinessAgent |
| `raw_engine.vote_count` | `Int32` | 6 |
| `sigma_override` | `Boolean` | False |
| `sigma_step.step` | `Int32` | 0 |
| `sigma_step.severity` | `String` | S4 |
| `sigma_step.z` | `Decimal` | 1.4 |
| `sigma_step.z_t` | `Decimal` | 1.4 |
| `sigma_step.velocity` | `Int32` | 0 |
| `sigma_step.acceleration` | `Int32` | 0 |
| `sigma_step.stability_status` | `String` | STABLE |
| `sigma_step.violations` | `array_empty` |  |
| `sigma_step.coherence_ok` | `Boolean` | True |
| `sigma_report.pass` | `Boolean` | True |
| `sigma_report.status` | `String` | PASS |
| `sigma_report.steps_evaluated` | `Int32` | 1 |
| `sigma_report.unstable_steps` | `Int32` | 0 |
| `sigma_report.violations_total` | `Int32` | 0 |
| `sigma_report.violation_types` | `array_empty` |  |
| `sigma_report.metrics.mean_velocity` | `Int32` | 0 |
| `sigma_report.metrics.total_steps` | `Int32` | 1 |
| `sigma_report.metrics.tau_max_used` | `Int32` | 5 |
| `sigma_report.metrics.accel_limit_used` | `Decimal` | 0.6 |
| `sigma_report.constraints.vanishing_acceleration` | `String` | OK |
| `sigma_report.constraints.velocity_band` | `String` | OK |
| `sigma_report.constraints.coherence_stationarity` | `String` | OK |
| `sigma_report.steps_detail[0].step` | `Int32` | 0 |
| `sigma_report.steps_detail[0].severity` | `String` | S4 |
| `sigma_report.steps_detail[0].z` | `Decimal` | 1.4 |
| `sigma_report.steps_detail[0].z_t` | `Decimal` | 1.4 |
| `sigma_report.steps_detail[0].velocity` | `Int32` | 0 |
| `sigma_report.steps_detail[0].acceleration` | `Int32` | 0 |
| `sigma_report.steps_detail[0].stability_status` | `String` | STABLE |
| `sigma_report.steps_detail[0].violations` | `array_empty` |  |
| `sigma_report.steps_detail[0].coherence_ok` | `Boolean` | True |
| `sigma_report.stdout` | `String` | V18.9 Sigma Dynamic Stability - PASS Steps evaluated : 1 Unstable steps  : 0 Total violations: 0 Config source   : C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\sigma\sigma_config.json tau_max         : 5.0 accel_limit     : 0.6 No violations detected.  |

## 9. Ce que cet audit prouve

| Axe | Preuve visible | Statut |
|---|---|---:|
| Routage domaine | 3 domaines appellent le meme endpoint `/kernel/ragnarok` | OK |
| Gouvernance X-108 | Chaque domaine retourne un gate X-108 | OK |
| Securite avant action | Cas critiques bloques ou retenus avant execution | OK |
| Tracabilite input | Chaque payload envoye est sauvegarde et hashe | OK |
| Tracabilite output | Chaque reponse est sauvegardee et hashee | OK |
| Tracabilite metrics | Toutes les metriques retournees sont flattenees, comptees et hashees | OK |
| Tracabilite decisions | Les decision_*.json creees pendant audit sont comptees et hashees | OK |
| Tracabilite runtime | Les fichiers critiques moteur sont hashes | OK |
| Logs serveur | stdout/stderr hashes apres arret runtime | OK |
| Scellage | merkle_seal.json present et SHA256 calcule | OK |
| Racine audit | AUDIT_ROOT_SHA256 calcule sur les artefacts | OK |
| Git proof | Branche, commit, tags et status captures | OK |

## 10. Limites

- Ne prouve pas une connexion bancaire reelle.
- Ne prouve pas une connexion avion reelle.
- Ne prouve pas une execution trading reelle.
- Prouve que le moteur recoit, gouverne, refuse/retient, trace, hashe et rend auditable des decisions simulees multi-domaines.

## 11. Fichiers principaux generes

- `AUDIT_TOTAL_METRICS_PROOF.md`
- `TRACE_MANIFEST.json`
- `TRACE_STATS.json`
- `ARTIFACT_HASH_MANIFEST.csv`
- `AUDIT_ROOT_SHA256.txt`
- `audit_summary_3_domains.csv`
- `audit_summary_3_domains.json`
- `metrics_full_bank.csv`
- `metrics_full_trading.csv`
- `metrics_full_gps_defense_aviation.csv`
- `decisions_created_during_audit.csv`
- `runtime_file_hashes.csv`
- `server.stdout.log`
- `server.stderr.log`
