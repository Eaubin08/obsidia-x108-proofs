# Real GNSS Closure Report

Date: 2026-08-02
Status: PASS_REAL_RINEX_ONLY

## Git / Isolation

- Branch at start: `integration/final-local-consolidation-20260722`
- Branch creation attempted: `git switch -c codex/hackathon-gps-physical-real-gnss-v0`
- Branch creation result: blocked.
- Exact error: `fatal: cannot lock ref 'refs/heads/codex/hackathon-gps-physical-real-gnss-v0': unable to create directory for .git/refs/heads/codex/hackathon-gps-physical-real-gnss-v0`
- Isolation obtained: directory-level hackathon isolation under `hackathons/nativebuilder-gps-defense/`, not Git branch isolation.

## PASS_REAL Source

- Proof level reached: `RECORDED_REAL_GNSS`
- Source type: real RINEX observation file
- Synthetic: `false`
- Official URL: `https://geodesy.noaa.gov/corsdata/rinex/2026/210/ab02/ab022100.26o.gz`
- Station log URL: `https://geodesy.noaa.gov/corsdata/station_log/ab02.log.txt`
- Station: `AB02`
- Observation period: `2026-07-29T00:00:00.000Z` to `2026-07-29T23:59:45.000Z`
- Constellations present in parsed observations: `G`
- Unique satellites parsed: 31
- Epochs parsed: 5760
- RINEX SHA-256: `c81c0c78f99cc945d8d4f2074fd46de98974965d897b887c0ba45cdc77e81ea0`
- Station log SHA-256: `0c56f8bf2f068823e3922859bc042db6be4163d3f82675ba75ea0d0fe25075ce`

## Chain Executed

```text
NOAA RINEX .26o.gz
-> RINEX parser
-> GPS Physical Observation Envelope
-> Physical Reality Gate
-> DomainState GPS
-> P3-05
-> P4-20 evidence
-> X-108 live HTTP POST
-> receipt
```

## Runtime Artifacts

- Full result: `artifacts/gps_rinex_noaa_ab02_2026_210_real_result.json`
- Provenance manifest: `artifacts/gps_rinex_noaa_ab02_2026_210_provenance_manifest.json`

## Kernel HTTP Evidence

- Endpoint: `http://127.0.0.1:3001/kernel/ragnarok`
- HTTP status: `200`
- Payload SHA-256: `c019cddb145b26d3b6cb69391a66ba0c2e909464ae30c1ab1be13e6586ccaf21`
- Raw response SHA-256: `8639a34c75f8dbd7eb08784ee48c3636654328ba529fb7bde44791ac7cf201fd`
- Decision id: `gps_defense_aviation-de1a76514344`
- Verdict: `HOLD`
- Reason code: `UNKNOWNS_OR_CONFIDENCE_LOW`

## Why HOLD Is Correct

The RINEX source is real GNSS, but it does not contain inertial/radar corroboration or a live sensor private-key attestation. X-108 therefore receives a real recorded GNSS observation and correctly refuses to upgrade it to full action authorization.

## Blocked Levels

- `RECORDED_REAL_RF`: blocked by missing GNSS-SDR runtime and Docker daemon.
- `RECORDED_RF_ATTACK`: blocked by TEXBAT access timeout and missing GNSS-SDR runtime.
- `REAL_PASSIVE_GNSS`: blocked by no confirmed local GNSS/SDR receiver.
- Lean L-02/L-06 closure: intentionally not touched.
- Kernel sealed file: intentionally not touched.

## Public Wording Allowed

"Obsidia GPS Defense now has one real recorded GNSS execution: a NOAA/NGS RINEX observation file traversed the Physical Signal Periphery, P3-05, P4-20, and a live X-108 HTTP decision. The live verdict is HOLD because the real GNSS source is not multi-source corroborated."

