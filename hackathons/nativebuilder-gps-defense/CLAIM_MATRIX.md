# GPS Physical Signal Periphery Claim Matrix

Date: 2026-08-02
Status: PASS_REAL_RINEX_WITH_BLOCKERS

| Claim | Current status | Evidence | Allowed wording |
|---|---|---|---|
| Physical observation envelope exists | DONE | `schemas/gps_physical_observation.schema.json` | "The GNSS physical observation contract is defined." |
| Physical Reality Gate exists | DONE | `hackathons/nativebuilder-gps-defense/physical_signal_periphery.py` | "The gate classifies physical observation envelopes as `AUTHENTICATED`, `DEGRADED`, `UNKNOWN`, or `REJECTED`." |
| Gate decides flight verdicts | FORBIDDEN | `emits_verdict=false`, `decision_authority=KX108_ONLY` | "The physical gate never decides; it only qualifies input before P3-05/X-108." |
| Synthetic fixture proves physical GNSS | FALSE | `proof_level=SYNTHETIC_TEST_ONLY`, `eligible_for_physical_claim=false` | "Synthetic fixtures test format and fail-closed behavior only." |
| Synthetic observation reaches P3-05 | DONE | `artifacts/gps_physical_observation_synthetic_result.json` | "A structured observation can traverse the bridge and fail closed to `HOLD` when not attested." |
| Real RINEX reaches live X-108 | DONE | `artifacts/gps_rinex_noaa_ab02_2026_210_real_result.json` | "A real NOAA/NGS RINEX observation traversed the chain to a live X-108 HTTP `HOLD` decision." |
| RECORDED_REAL_GNSS minimum | PASS_REAL | `artifacts/gps_rinex_noaa_ab02_2026_210_provenance_manifest.json` | "The minimum real GNSS closure level is reached through recorded RINEX, not RF." |
| Live passive hardware available | BLOCKED | `artifacts/gps_live_passive_status.json` | "No local GNSS/SDR receiver was confirmed; live physical ingestion is blocked, not mocked." |
| Blind benchmark path exists | DONE | `artifacts/gps_blind_benchmark_synthetic_result.json` | "The benchmark runner keeps truth labels outside the decision pipeline." |
| Production RF physical proof | BLOCKED | GNSS-SDR unavailable; Docker daemon unavailable | "RF/IQ proof requires GNSS-SDR execution over a real raw recording." |
| Lean L-02/L-06 final closure | BLOCKED_PROTECTED | `hackathons/nativebuilder-gps-defense/GPS_PHYSICAL_TO_LEAN_FUTURE_BRIDGE.md` | "Formal proof mapping is documented; protected Lean proof closure is future work." |
