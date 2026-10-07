# GPS REAL PASSIVE CAPTURE — P2 V0

Status: RUNTIME ARMED / PHYSICAL CAPTURE NOT YET VERIFIED  
Branch: `feat/gps-real-passive-capture-p2-v0`  
Authority: `KX108_ONLY`

## Purpose

Close the software side of P2 without faking the physical side.

P2 can be promoted only by a capture produced during a bounded local GNSS-SDR runtime and bound to:
- exact GNSS-SDR binary;
- exact receiver configuration;
- receiver identity evidence;
- receiver identity manifest whose evidence hash matches;
- runtime start/end;
- raw stdout capture hash;
- parsed current observables;
- provenance and limitations.

Configuration alone remains non-proof.

## Runtime states

### Blocked

Any of the following keeps the result at `STRUCTURED_STATE`:
- GNSS-SDR not found;
- config missing;
- receiver manifest missing/incomplete;
- receiver identity evidence missing;
- receiver evidence hash mismatch;
- runtime produces no GNSS observables.

No kernel HTTP submission is attempted from this P2 path while blocked.

### Promoted capture

A runtime capture can become:

`REAL_PASSIVE_GNSS`

only when:
- GNSS-SDR was actually launched by the adapter;
- runtime output exists;
- current GNSS observables were parsed;
- receiver identity evidence is present;
- manifest hash matches the identity evidence;
- config hash is bound.

This still does **not** prove cryptographic sensor authenticity.

Residual limitations include:
- `NO_SENSOR_PRIVATE_KEY_ATTESTATION`
- `NO_INERTIAL_CORROBORATION`
- `LIVE_SOURCE_AUTHENTICITY_BOUND_TO_LOCAL_RUNTIME_NOT_CRYPTOGRAPHIC_ATTESTATION`

## Receiver manifest

Example:

```json
{
  "receiver_id": "receiver-local-001",
  "manufacturer": "REPLACE_WITH_REAL_VALUE",
  "model": "REPLACE_WITH_REAL_VALUE",
  "interface": "USB",
  "identity_evidence_sha256": "REPLACE_WITH_SHA256_OF_RECEIVER_EVIDENCE_FILE"
}
```

The evidence file must come from actual local hardware enumeration or another explicit receiver identity/configuration record.

## Execution

```powershell
python .\hackathons\nativebuilder-gps-defense\physical_signal_periphery.py `
  --live-gnss-sdr-capture `
  --config-file .\PATH\TO\REAL_LIVE_GNSS_SDR.conf `
  --receiver-manifest .\PATH\TO\receiver-manifest.json `
  --receiver-evidence .\PATH\TO\receiver-evidence.txt `
  --capture-dir .\hackathons\nativebuilder-gps-defense\runs\live_passive `
  --capture-duration-seconds 60 `
  --out .\hackathons\nativebuilder-gps-defense\runs\live_passive\p2_result.json
```

Do not substitute a recorded dataset for this command and call it P2.

## P2 closure rule

Repository tests can verify the gate logic.

They cannot close physical P2.

P2 becomes physically VERIFIED only after a real local run yields:
- `p2_capture_promoted = true`
- `proof_level = REAL_PASSIVE_GNSS`
- `live_capture_observed = true`
- `receiver_identity_verified = true`
- immutable input/config/evidence hashes
- KX108 receipt path preserved.

Until then:

`P2 = RUNTIME READY / PHYSICAL CAPTURE PENDING`
