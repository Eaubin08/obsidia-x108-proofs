# Physical Build Readiness Report

Status: PASS_REAL_RINEX_WITH_BLOCKERS
Date: 2026-08-02

## Environment

- Python: available through Codex bundled runtime.
- Docker: detected at `C:\Program Files\Docker\Docker\resources\bin\docker.exe`.
- GNSS-SDR: not detected in PATH.
- Hardware inventory: blocked by Windows permission error on `Get-CimInstance Win32_PnPEntity`.
- GNSS/SDR receiver: not confirmed.
- Git branch creation: blocked by permission error while creating `feat/hackathon-gps-physical-cockpit-v0`.

## Existing Runtime Chain

- P3-05 GPS gate: implemented.
- P3-09 contract: tested.
- P4-20 runtime guard: implemented as non-sovereign evidence module.
- Kernel X-108 live: launched and POST-tested.
- Nominal structured GPS: `ALLOW`.
- Spoof/replay structured GPS: `HOLD`.
- OS3 receipts: demo receipts generated.
- Replay: dry-run only, `replay_status=NOT_RUN`.

## Physical Chain Readiness

Ready:

- Physical Observation Envelope schema.
- Physical Reality Gate.
- Observation-to-DomainState adapter.
- P3-05 / X-108 runtime bridge.
- Real NOAA/NGS RINEX parser and recorded GNSS execution.
- Synthetic format tests explicitly marked non-physical.
- Live passive no-hardware fallback.

Blocked:

- Real GNSS-SDR execution, because `gnss-sdr` is not installed/detected.
- Local receiver verification, because hardware enumeration is permission-blocked.
- TEXBAT/RINEX download and licensing validation, because no dataset was fetched in this lot.
- Any physical proof claim, until a real dataset or receiver output is provided.

## Claim

This lot can claim one real recorded GNSS execution via NOAA/NGS RINEX. It still cannot claim RF/IQ processing, TEXBAT attack processing, or live passive receiver ingestion.

## Executed Outputs

Generated on 2026-08-02:

| Artifact | Result | SHA256 |
|---|---|---|
| `artifacts/gps_physical_observation_synthetic_result.json` | Synthetic envelope reached P3-05 and failed closed to `HOLD` because the sensor is not physically attested. | `31D903E37FD23554232CECE521F998D3E2C43CABE4D5D0E1FFFFD0CD43089EAD` |
| `artifacts/gps_live_passive_status.json` | Live passive adapter is `BLOCKED`; no GNSS/SDR receiver or GNSS-SDR executable was confirmed. | `547D448E8963CAED6056B541EBFADF9980A3EA86862FFB6FA337C61FB03BC3EA` |
| `artifacts/gps_blind_benchmark_synthetic_result.json` | Blind benchmark runner executed without using a truth manifest in the pipeline; synthetic case ended in `HOLD`. | `CB38F7CA148D9F77FB360BC15F26D27DDF74ADB795FBC764B83604B893368A11` |
| `artifacts/gps_rinex_noaa_ab02_2026_210_real_result.json` | Real NOAA/NGS RINEX observation reached live X-108 HTTP status `200`; verdict `HOLD` because inertial corroboration is missing. | `619C48EF5885245A5B6531EBA9025D507462904CD62DFB968E0FF425BDC684CF` |
| `artifacts/gps_rinex_noaa_ab02_2026_210_provenance_manifest.json` | Separate provenance manifest for the real RINEX execution. | `EEAF668ADBC4BD6AA48F72DB915A48FF4715A915E0C499597129DF32DCABD2CC` |

Schema hash:

- `schemas/gps_physical_observation.schema.json`: `790F7665702A38CCF0EABB27AF0694C24A2ACC00AC6AA04533B1F507996BA4C9`

## Hackathon Truth Boundary

- Demonstrable now: real NOAA/NGS RINEX file, provenance manifest, parsed epochs/satellites, Physical Reality Gate, structured DomainState bridge, P3-05 handoff, P4-20 evidence, live X-108 HTTP `200`, kernel `HOLD` for missing inertial corroboration.
- Not demonstrable yet: decoded RF/IQ, live GNSS-SDR observables/PVT, TEXBAT RF attack processing, production sensor attestation, production cryptographic receipt, Lean L-02/L-06 final proof closure.
- Pitch wording: "we executed one real recorded GNSS chain from NOAA RINEX to live X-108; the kernel correctly returns HOLD because single-source GNSS is not enough for physical action authority."
