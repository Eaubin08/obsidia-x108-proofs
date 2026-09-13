# GPS V0.1 Closure Report

Status: RUNTIME_CLOSED_FOR_DEMO / FORMAL_PRODUCTION_OPEN
Date: 2026-08-02

## Closed Now

1. P3-05 -> kernel live
   - `domains/gps/gps_x108_gate.py` no longer depends on `requests`.
   - It uses `urllib` fallback for POST when `requests` is unavailable.
   - It sends a complete GPS state to `sigma/run_pipeline.py` through the sealed kernel.
   - Captured live result:
     `artifacts/gps_v01_gate_live_nominal_result.json`

2. Complete GPS payload
   - Runtime payload now includes GNSS/source availability, IMU/radio availability, drift, source conflict, time skew, brownout, attestation readiness, rollback, physical scores, and domain state hash.
   - This removes the previous live-kernel unknowns caused by missing inertial/radio/attestation fields.

3. P4-20 runtime guard
   - Added non-sealed pure runtime guard:
     `obsidia_core/guardians/path_fidelity_guard.py`
   - The guard emits evidence only. It never emits `ALLOW` and keeps `decision_authority = KX108_ONLY`.

4. L-02/L-06 mapping
   - Mapping note exists:
     `docs/formalisation_math/GPS_L02_L06_MAPPING_NOTE.md`
   - Lean files were not edited because they are protected.

5. Replay verifier / receipts
   - Dry-run replay verifier passes:
     `artifacts/gps_v01_replay_report.json`
   - OS3 receipts remain explicit with `replay_status = NOT_RUN`.
   - P4-07 demo receipt manifest generated:
     `artifacts/gps_v01_p4_07_receipt_manifest.json`

## Live Kernel Result

Kernel:

`server.kernel.sealed.cjs`

Observed live process:

`PID 15308`

Route:

`POST http://127.0.0.1:3001/kernel/ragnarok`

Observed behavior after full GPS payload:

- kernel reachable
- P3-05 can submit without `requests`
- nominal coherent GPS can reach `KERNEL_X108` and return `ALLOW`
- spoof/replay still fail-close locally before kernel

## Still Not Claimed

- production aviation certification
- real hardware/PKI sensor attestation
- production RFC3161 P4-07 signing
- production replay mutation of `replay_status`
- final Lean closure of L-02/L-06
- physical actuation authorization

## Remaining Formal Work

The remaining work is not demo runtime wiring. It is protected formal promotion:

1. edit Lean proofs only after explicit approval and proof verification plan
2. bind P4-20 evidence to L-06 theorem vocabulary
3. bind `GpsDefenseAviationState.domain_state_hash` to L-02 trajectory state proof
4. define real signing key/certificate handling for P4-07
5. define real sensor attestation provider
