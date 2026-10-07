# GPS Real Passive Capture V0

Status: SOFTWARE VERIFIED / PHYSICAL CLOSURE OPEN

## Purpose

P2 continues the post-freeze GPS plan after verified receiver-readiness P1.

P2 does **not** invent a receiver runtime and does not claim a live capture already exists. It adds the admission boundary for a passive GNSS capture that is actually produced on the local machine and processed by the existing GNSS-SDR path.

## Search-before-build result

Existing reusable pieces:
- `physical_signal_periphery.py`
- GNSS-SDR stdout parser
- recorded RF normalization
- Physical Reality Gate
- GPS domain adapter / X108 gate
- capture/config/source hashing
- `REAL_PASSIVE_GNSS` proof level

Not found as an existing runtime:
- a complete RTL-SDR acquisition runtime;
- a complete HackRF acquisition runtime;
- a hidden hardware-specific live receiver stack.

Therefore P2 does not create a second SDR stack.

## New admission path

```text
physical receiver
      ↓
operator-produced passive capture
      ↓
capture file + exact config + receiver ref
      ↓
GNSS-SDR run/output
      ↓
live_gnss_sdr_capture_to_observation_envelope_v0
      ↓
REAL_PASSIVE_GNSS
      ↓
Physical Reality Gate
      ↓
GPS Domain / KX108
```

## Fail-closed admission requirements

A capture cannot be promoted merely because a file exists.

The admission contract requires:
- non-empty capture file;
- immutable capture SHA-256;
- explicit capture start time;
- explicit capture completion time;
- bound receiver identifier;
- exact processing/receiver configuration file;
- configuration SHA-256;
- completed GNSS-SDR run;
- GNSS tracking or NAV evidence in GNSS-SDR output.

Missing any required element fails closed.

## Claim boundary

`REAL_PASSIVE_GNSS` means a local passive GNSS capture has been admitted with bound capture/config/output evidence.

It does **not** mean:
- receiver identity is cryptographically attested;
- sensor private-key attestation exists;
- multisource corroboration exists;
- physical authenticity is globally proven;
- spoofing resistance is proven;
- causal hostile-RF attribution is proven.

The envelope therefore keeps:

```text
live_capture_observed = true
sensor_attestation_proven = false
receiver_identity_bound = true
receiver_identity_verified = false
```

unless a later independent mechanism proves more.

## Authority

Unchanged:
- KX108_ONLY
- physical capture != decision
- physical evidence != Binder permission
- claim eligibility != sensor attestation
- capture provenance != canonical truth

## Validation split

### Software validation

Tests can prove that:
- fake/missing capture state fails closed;
- capture/config hashes are bound;
- GNSS-SDR evidence is required;
- the GPS chain receives the admitted envelope;
- no sensor attestation is synthesized.

### Physical validation

Software tests cannot prove that the user's hardware has actually captured live RF.

P2 can only be physically closed after a local run produces:
- the capture file;
- exact receiver/config identity;
- GNSS-SDR output;
- resulting P2 evidence artifact.

Until that run exists:

`P2 SOFTWARE = IMPLEMENTED`

`P2 PHYSICAL CLOSURE = OPEN`

## Example local invocation

```powershell
python hackathons/nativebuilder-gps-defense/physical_signal_cli.py \
  --live-gnss-sdr-run "<GNSS_SDR_RUN_DIR>" \
  --live-capture-file "<CAPTURE_FILE>" \
  --config-file "<EXACT_CONFIG_FILE>" \
  --live-receiver-id "<RECEIVER_ID>" \
  --capture-started-at "<ISO8601_START>" \
  --capture-completed-at "<ISO8601_END>" \
  --out artifacts/gps_real_passive_capture_result.json
```

The placeholders must be replaced by evidence from the actual local capture session. They must not be fabricated for closure.


## Software verification

- Verified code HEAD: `4b78fba47c6435e3c709b399a546fe6221c4636e`
- GitHub Actions run: `37582290732`
- Global result: `12570 passed / 11 failed / 46 skipped / 207 deselected`
- P2-specific failures: `0`
- The 11 failures match the historical non-P2 baseline families.

Local operator validation on Windows also reported:

```text
14 passed in 3.08s
```

**Verdict:** P2 software admission path is `VERIFIED`. P2 physical closure remains `OPEN` until an actual local passive GNSS capture is produced and admitted through this path.
