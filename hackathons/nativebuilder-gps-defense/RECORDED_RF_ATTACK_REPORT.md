# RECORDED_RF_ATTACK Report

Date: 2026-08-03
Status: `FGI_HOSTILE_RF_OBTAINED_GNSS_SDR_BLOCKED`
Baseline: `3ee87e4be3a2cbe6ed061b2b43e92672a9682365`

## Verdict

`RECORDED_RF_ATTACK` is **not reached**.

The blocker moved forward: an official hostile RF corpus is now local and hash-verified, but no GNSS-SDR or equivalent receiver runtime is executable in this Windows environment. Therefore no hostile RF observables/PVT, live X-108 decision, receipt, confusion matrix, or reproducibility score can honestly be claimed.

## Corpus Obtained

### FGI-SpoofRepo / FGI-JSDR

- Dataset: `https://etsin.fairdata.fi/dataset/367379a8-7d78-4b08-91f0-8027ce7a621b`
- DOI: `10.23729/7a648509-2ca8-4a7d-8223-0b429182f857`
- License: `CC-BY-4.0`
- Access: open Fairdata/Etsin package flow.
- Scenario scope: `/FGISpoofRepo/UT_DFMC`
- Scenario family: untargeted spoofing, dual-frequency multi-constellation.
- Package downloaded: `367379a8-7d78-4b08-91f0-8027ce7a621b_kg54vio7.zip`
- Package size: `7337029743` bytes.
- Package SHA-256: `1df410917bc853b5ab843667acd47ede4e03bf237ce3e399d791a597ce9713ad`
- Extracted L1/E1 file: `UTD_L1_E1.dat`
- Extracted L1/E1 size: `9825419264` bytes.
- Extracted L1/E1 SHA-256: `e8da962e92cfdbcb677361ce769a54f26dc385417bac9fd618492dcd02fb2d72`

Official metadata used for L1/E1:

- GNSS: GPS L1 C/A and Galileo E1.
- Center frequency: `1569030000` Hz.
- Sample rate: `26000000` samples/s.
- Type: real 8-bit I samples.
- Bandwidth: `4200000` Hz.

The raw files are excluded from Git by `hackathons/nativebuilder-gps-defense/data/fgi-spoofrepo/.gitignore`.

## Receiver Runtime Blocker

GNSS-SDR execution was attempted through the available local routes:

- Local `gnss-sdr`: not found.
- Docker CLI: found.
- Docker Desktop: launch requested.
- Docker daemon: still blocked by `permission denied while trying to connect to the docker API at npipe:////./pipe/docker_engine`.
- WSL2: blocked by `Wsl/EnumerateDistros/Service/E_ACCESSDENIED`.
- Chocolatey search for `gnss-sdr`: no package result.

Because the receiver stage did not run, the chain stopped before:

```text
FGI hostile I/Q
-> receiver software / GNSS-SDR
-> acquisition/tracking
-> observables/PVT
-> Physical Reality Gate
-> DomainState
-> P3-05
-> P4-20
-> live X-108
-> receipt
-> post-hoc truth evaluation
```

## Blind Benchmark Status

- `pipeline_inputs`: no executed cases created.
- `truth_manifest`: not read by the pipeline.
- Label leak check: `NOT_RUN_NO_PIPELINE_INPUTS_CREATED`.
- GNSS-SDR runs: none for FGI hostile RF.
- X-108 live decisions: none for hostile RF.
- Receipts: none for hostile RF.
- Confusion matrix: not computed.
- Reproducibility: not run.

## Why This Is Not A PASS

`RECORDED_RF_ATTACK` requires at least one real hostile RF recording to pass through receiver decoding and then the Obsidia governance chain. The hostile file is now present, but receiver execution is blocked locally. No mock, synthetic substitute, or label-derived shortcut was used.

## Public Wording Allowed

Allowed:

> Obsidia GPS Defense has reached `RECORDED_REAL_RF` on nominal public GNSS I/Q. An official FGI-SpoofRepo hostile RF corpus has now been downloaded and hash-verified locally, but `RECORDED_RF_ATTACK` remains blocked until GNSS-SDR or an equivalent receiver runtime can execute the hostile signal into observables/PVT.

Forbidden:

- `RESISTANT_TO_SPOOFING`
- `PRODUCTION`
- `AVIATION_VALIDATED`
- `RECORDED_RF_ATTACK passed`
- `FGI spoofing benchmark passed`
