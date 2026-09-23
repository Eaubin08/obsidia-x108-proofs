# FGI UT_DFMC Receiver Compatibility Report

Date: 2026-08-03
Status: `BLOCKED_RECEIVER_CONFIGURATION`
Baseline: `73cedd4353daa3a512836e0a6480c01839e2b868`

## Verdict

`RECORDED_RF_ATTACK` is **not reached**.

The required prerequisite failed: no available receiver configuration produced valid NAV messages or stable PVT before the official `135 s` onset. Therefore the hostile temporal benchmark is blocked before post-onset scoring.

## Official Metadata Used

- Dataset: FGI-SpoofRepo / FGI-JSDR.
- DOI: `10.23729/7a648509-2ca8-4a7d-8223-0b429182f857`.
- License: `CC-BY-4.0`.
- Scenario: `UT_DFMC`.
- Local file: `UTD_L1_E1.dat`.
- L1/E1 SHA-256: `e8da962e92cfdbcb677361ce769a54f26dc385417bac9fd618492dcd02fb2d72`.
- L1/E1 front-end center frequency: `1569.03 MHz`.
- GPS L1 / Galileo E1 signal center: `1575.42 MHz`.
- Sampling rate: `26 MHz`.
- Quantization: real `8-bit I`.
- Bandwidth: `4.2 MHz`.
- True receiver: stationary, approximately `60.182 N`, `24.828 E`, altitude `47.248 m`.

## FGI-GSRx Priority Check

FGI-GSRx is the most faithful receiver path because its `default_param_FGISpoofRepo_GPSL1.txt` declares the same L1/E1 metadata and reads real `sampleSize=8` data as MATLAB `int8`.

Blocker:

- `matlab`: not found locally.
- `octave`: not found locally.
- `octave-cli`: not found locally.
- The existing GNSS-SDR Docker image does not contain MATLAB or Octave.

FGI-GSRx was therefore inspected but not executed.

## GNSS-SDR Compatibility Attempts

### Attempt 1: `ibyte` pre-onset

- Config: `hackathons/nativebuilder-gps-defense/gnss_sdr_fgi_ut_dfmc_l1e1_official_gpsl1_pre135_runtime.conf`.
- Config SHA-256: `6ecf160c1b8e7e18306344ab789fc4622d03e0a41396eecc9880a6a97fddcbe8`.
- Stdout SHA-256: `cf2d02d8c9ccbe0c3082e246cd9b343e3eff4de68ea7cb20bea041d4c3209914`.
- Result: tracking started on 9 GPS PRNs, 5 loss-of-lock events, no NAV messages, no PVT.
- Important limitation: GNSS-SDR reported only `65 s` processed for a `130 s` sample request, so this path does not preserve the intended receiver timing.

### Attempt 2: lossless `int8 -> int16le` promotion with `ishort`

- Derived file: `case_0001_l1e1_pre130_int16le.dat`.
- Conversion: each official `int8` sample promoted to signed `int16le` with identical numeric value.
- Scaling/filtering/resampling: none.
- Derived SHA-256: `a552b3c0e3284c4a19e1fe836d484f1cbfa31845064b4c1e210a95c598a3c093`.
- Config: `hackathons/nativebuilder-gps-defense/gnss_sdr_fgi_ut_dfmc_l1e1_official_gpsl1_pre130_ishort_runtime.conf`.
- Config SHA-256: `d7dca2c170037f19b0f6d95efdf9c1f8af6d19136d36d985a6702bab10cbbc31`.
- Stdout SHA-256: `f006f1552663e2638486c991cd9512bfb0742a39e2aea9910c9782c97d4471a5`.
- Result: tracking started on 12 GPS PRNs, 15 loss-of-lock events, no NAV messages, no PVT.
- Execution note: the container stopped progressing after `59 s` receiver time and was stopped after no log/file progress.

## Temporal Benchmark Decision

The loss of lock before `135 s` is classified as:

`PRE_ATTACK_RECEIVER_FAILURE`

It must not be used as evidence of spoofing detection.

## Next Action Required

To close `RECORDED_RF_ATTACK`, run the official FGI-GSRx receiver with MATLAB/Octave or provide a GNSS-SDR configuration proven to decode the FGI UT_DFMC L1/E1 signal into NAV/PVT before `135 s`. Only after that can the post-onset divergence, Physical Reality Gate alert, X-108 decision delay, and confusion metrics be computed.
