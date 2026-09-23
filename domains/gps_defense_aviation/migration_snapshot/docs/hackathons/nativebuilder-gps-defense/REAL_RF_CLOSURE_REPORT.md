# Real RF Closure Report

Date: 2026-08-02
Status: PASS_REAL_RF

## Environment

- Branch: `hackathon-gps-physical-real-gnss-v0`
- Baseline: `909155cc2124b710ba7c3cbc9b0d4fd609ab77bb`
- Runtime: Docker Desktop `desktop-linux`
- GNSS-SDR image: `carlesfernandez/docker-gnsssdr:latest`
- GNSS-SDR version: `0.0.21.git-next-2a7214a4f`
- Docker image digest: `sha256:716ecd117afecaee709de202b2393a853aa48cfb38d0c76b373eae54d6adc8ff`

## Real I/Q Source

- Official GNSS-SDR tutorial: `https://gnss-sdr.org/my-first-fix/`
- Source URL: `https://sourceforge.net/projects/gnss-sdr/files/data/2013_04_04_GNSS_SIGNAL_at_CTTC_SPAIN.tar.gz/download`
- Archive size observed: `1150716878` bytes
- Extracted I/Q file size: `1600000000` bytes
- Archive SHA-256: `d5b926aefe7462ca4211bcae2129591a810fa4960a214f35d056a883aa2af3ff`
- I/Q `.dat` SHA-256: `6489a6630784478f144f20bf872848410dee3b54a20fd8d1bdd9258afccf2976`
- Official source config SHA-256: `db1a554f919c6471780c9fa82a6579e404b4ce490b9347390e6d4f6136d6ef4c`
- Runtime config SHA-256: `62557c92444c5da035cffdd650b5f4d8f4c7053cc21d3804b1dbb2c348dff650`

## GNSS-SDR Run

Command:

```powershell
docker run --rm -v ${PWD}:/work -w /work/hackathons/nativebuilder-gps-defense/runs/iq_cttc_2013_04_04 carlesfernandez/docker-gnsssdr sh -lc "gnss-sdr --config_file=/work/hackathons/nativebuilder-gps-defense/gnss_sdr_cttc_2013_04_04_modern_runtime.conf --log_dir=/work/hackathons/nativebuilder-gps-defense/runs/iq_cttc_2013_04_04 2>&1 | tee /work/hackathons/nativebuilder-gps-defense/runs/iq_cttc_2013_04_04/gnss_sdr_run_stdout_modern.log"
```

Result:

- Run time: `102.147686` seconds
- Tracked satellites: 22 GPS PRNs
- NAV message satellites with CN0: `G01`, `G11`, `G17`, `G20`, `G32`
- Average CN0: `46.06232876712329 dB-Hz`
- Max CN0: `49.0 dB-Hz`
- First fix: lat `41.2748`, lon `1.98766`, height `77.768 m`, GDOP `5.94463`
- Last parsed PVT: lat `41.274831`, lon `1.987690`, height `74.65 m`
- Position lines parsed: 149
- Loss-of-lock events: 24

Generated outputs:

- `hackathons/nativebuilder-gps-defense/runs/iq_cttc_2013_04_04/gnss_sdr_run_stdout_modern.log`
- `hackathons/nativebuilder-gps-defense/runs/iq_cttc_2013_04_04/gnss-sdr.log`
- `observables.dat`, `PVT.dat`, `observables.mat`, `PVT.mat`
- GNSS-SDR-generated RINEX: `GSDR214v18.26O`, `GSDR214v18.26N`
- PVT exports: `geojson`, `gpx`, `kml`

## Chain Executed

```text
Public CTTC I/Q .dat
-> GNSS-SDR acquisition/tracking/PVT
-> GNSS-SDR stdout/log normalizer
-> GPS Physical Observation Envelope
-> Physical Reality Gate
-> DomainState GPS
-> P3-05
-> P4-20 evidence
-> X-108 live HTTP POST
-> receipt
```

## X-108 Live Evidence

- Artifact: `artifacts/gps_iq_cttc_2013_04_04_recorded_real_rf_result.json`
- Proof level: `RECORDED_REAL_RF`
- Synthetic: `false`
- Physical gate: `AUTHENTICATED`
- Kernel endpoint: `http://127.0.0.1:3001/kernel/ragnarok`
- HTTP status: `200`
- Decision id: `gps_defense_aviation-5d56a56e135a`
- X-108 live verdict: `HOLD`
- Reason code: `UNKNOWNS_OR_CONFIDENCE_LOW`
- Local OS3 ticket id: `251b0dc2838e447ebd3e732591c23fa6`
- Local receipt signature kind: `LOCAL_SHA256_DEMO_NOT_PRODUCTION_SIGNING`

## Why HOLD Is Correct

The RF signal is real and GNSS-SDR produced true acquisition/tracking/PVT outputs. The chain still has no IMU/radar corroboration and no private sensor attestation, so X-108 correctly refuses physical action authority and keeps the result in `HOLD`.

## Claim

Allowed wording:

> Obsidia GPS Defense reached `RECORDED_REAL_RF`: a real public GNSS I/Q recording was processed by GNSS-SDR, normalized into a physical observation envelope, and sent through P3-05/P4-20 to a live X-108 HTTP decision. The live verdict is `HOLD` because real RF GNSS alone is not enough for physical-action authority without inertial corroboration.

