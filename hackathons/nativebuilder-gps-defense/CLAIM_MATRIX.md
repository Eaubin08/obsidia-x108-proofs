# GPS Physical Signal Periphery Claim Matrix

Date: 2026-08-03
Status: PASS_REAL_RF_WITH_FGI_HOSTILE_RF_PARTIAL_CHAIN_NO_PVT

| Claim | Current status | Evidence | Allowed wording |
|---|---|---|---|
| Physical observation envelope exists | DONE | `schemas/gps_physical_observation.schema.json` | "The GNSS physical observation contract is defined." |
| Physical Reality Gate exists | DONE | `hackathons/nativebuilder-gps-defense/physical_signal_periphery.py` | "The gate classifies physical observation envelopes as `AUTHENTICATED`, `DEGRADED`, `UNKNOWN`, or `REJECTED`." |
| Gate decides flight verdicts | FORBIDDEN | `emits_verdict=false`, `decision_authority=KX108_ONLY` | "The physical gate never decides; it only qualifies input before P3-05/X-108." |
| Synthetic fixture proves physical GNSS | FALSE | `proof_level=SYNTHETIC_TEST_ONLY`, `eligible_for_physical_claim=false` | "Synthetic fixtures test format and fail-closed behavior only." |
| Synthetic observation reaches P3-05 | DONE | `artifacts/gps_physical_observation_synthetic_result.json` | "A structured observation can traverse the bridge and fail closed to `HOLD` when not attested." |
| Real RINEX reaches live X-108 | DONE | `artifacts/gps_rinex_noaa_ab02_2026_210_real_result.json` | "A real NOAA/NGS RINEX observation traversed the chain to a live X-108 HTTP `HOLD` decision." |
| RECORDED_REAL_GNSS minimum | PASS_REAL | `artifacts/gps_rinex_noaa_ab02_2026_210_provenance_manifest.json` | "The minimum real GNSS closure level is reached through recorded RINEX, not RF." |
| Real I/Q reaches GNSS-SDR and live X-108 | DONE | `artifacts/gps_iq_cttc_2013_04_04_recorded_real_rf_result.json` | "A public CTTC I/Q recording was processed by GNSS-SDR, normalized, and sent to live X-108." |
| RECORDED_REAL_RF | PASS_REAL | `hackathons/nativebuilder-gps-defense/REAL_RF_CLOSURE_REPORT.md` | "The real RF closure level is reached for nominal public GNSS I/Q." |
| Live passive hardware available | BLOCKED | `artifacts/gps_live_passive_status.json` | "No local GNSS/SDR receiver was confirmed; live physical ingestion is blocked, not mocked." |
| Blind benchmark path exists | DONE | `artifacts/gps_blind_benchmark_synthetic_result.json` | "The benchmark runner keeps truth labels outside the decision pipeline." |
| Official hostile RF corpus obtained | DONE | `hackathons/nativebuilder-gps-defense/rf_attack_benchmark/dataset_manifest.json` | "An official FGI-SpoofRepo hostile RF corpus was downloaded and hash-verified locally." |
| Official hostile RF benchmark | PARTIAL_NO_PVT | `hackathons/nativebuilder-gps-defense/RECORDED_RF_ATTACK_REPORT.md` | "Official FGI hostile RF traversed GNSS-SDR acquisition/tracking/observables and live X-108 with a `HOLD` receipt, but `RECORDED_RF_ATTACK` is not reached because NAV/PVT and correct spoofing classification are not proven." |
| TEXBAT / OAKBAT / FGI spoofing resistance | FALSE | `hackathons/nativebuilder-gps-defense/rf_attack_benchmark/metrics.json` | "No spoofing-resistance claim is allowed; the hostile RF run produced fail-closed governance evidence, not a validated spoofing classification metric." |
| Production RF certification | BLOCKED | public I/Q is recorded nominal RF, no private sensor attestation | "This is a real RF demo closure, not certified aviation/defense production attestation." |
| Lean L-02/L-06 final closure | BLOCKED_PROTECTED | `hackathons/nativebuilder-gps-defense/GPS_PHYSICAL_TO_LEAN_FUTURE_BRIDGE.md` | "Formal proof mapping is documented; protected Lean proof closure is future work." |
