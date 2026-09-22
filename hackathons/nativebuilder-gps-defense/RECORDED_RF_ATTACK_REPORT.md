# RECORDED_RF_ATTACK Report

Date: 2026-08-03
Status: `FGI_HOSTILE_RF_FULL_CHAIN_NO_PVT`
Baseline: `1169b5aa3dc64622fb37e3cc22d88376190df3f6`

## Verdict

`RECORDED_RF_ATTACK` is **not reached**.

The blocker moved forward again: an official hostile RF corpus is local and hash-verified, Docker/GNSS-SDR was recovered through the unsandboxed Windows user, and the full L1/E1 RF file was processed offline. GNSS-SDR produced acquisition/tracking/observables and the Obsidia GPS chain reached a live X-108 HTTP decision plus receipt.

The final attack-proof level is still not closed because GNSS-SDR produced no NAV messages and no PVT solution. The first observed lock-loss anomaly occurs before the official attack onset, so the run cannot honestly be counted as a correct spoofing detection or timing-delay measurement.

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

## Receiver Runtime Used

- Docker Desktop context: `desktop-linux`.
- Docker version: `29.4.3`.
- Image: `carlesfernandez/docker-gnsssdr:latest`.
- Image digest: `sha256:716ecd117afecaee709de202b2393a853aa48cfb38d0c76b373eae54d6adc8ff`.
- GNSS-SDR version: `0.0.21.git-next-2a7214a4f`.
- Docker access mode: unsandboxed Windows user with Docker daemon access.

The full run used:

```powershell
docker --config .local\docker-config run --rm -v ${PWD}:/work -w /work/hackathons/nativebuilder-gps-defense/rf_attack_benchmark/gnss_sdr_runs/fgi_ut_dfmc_l1e1_ifneg_full carlesfernandez/docker-gnsssdr sh -lc "gnss-sdr --config_file=/work/hackathons/nativebuilder-gps-defense/gnss_sdr_fgi_ut_dfmc_l1e1_ifneg_full_runtime.conf --log_dir=/work/hackathons/nativebuilder-gps-defense/rf_attack_benchmark/gnss_sdr_runs/fgi_ut_dfmc_l1e1_ifneg_full 2>&1 | tee /work/hackathons/nativebuilder-gps-defense/rf_attack_benchmark/gnss_sdr_runs/fgi_ut_dfmc_l1e1_ifneg_full/gnss_sdr_run_stdout.log"
```

- Configuration: `hackathons/nativebuilder-gps-defense/gnss_sdr_fgi_ut_dfmc_l1e1_ifneg_full_runtime.conf`
- Configuration SHA-256: `5227a4c6cff2e186f306f5bbc44825923a2a6d8f7d0c30902bcd449bcb0951f1`
- Stdout SHA-256: `244acd23848024d6274d8307676369d328ab1d076690eb475937a6fc6130d226`
- Observables SHA-256: `d84ff197ff3c85dd39c0d7e3198afb32386f0cd95dec0c7f0d6490883ef9333c`

## Receiver Output

- Processed RF duration reported by GNSS-SDR: `377.801 s`.
- GNSS-SDR run time: `1331.28 s`.
- Tracked GPS satellites: `G01,G02,G04,G06,G07,G08,G09,G10,G11,G12,G13,G14,G15,G16,G17,G19,G20,G22,G23,G24,G26,G27,G28,G29,G30,G31,G32`.
- Tracking events: `53`.
- Loss-of-lock events: `49`.
- First loss-of-lock time: `14 s`.
- Official attack onset used only post-run: `135 s`.
- NAV message satellites: none.
- PVT positions: `0`.

## Obsidia Chain Result

The following real chain was executed:

```text
FGI hostile I/Q
-> GNSS-SDR acquisition/tracking/observables
-> normalizer
-> Physical Reality Gate
-> DomainState
-> P3-05
-> P4-20
-> live X-108
-> receipt
-> post-hoc truth comparison
```

X-108 evidence:

- HTTP status: `200`.
- Verdict: `HOLD`.
- Source: `REALITY_AUTHENTICITY_GATE_FAIL_CLOSED`.
- Receipt id: `a29e2738bde0446ea7c12c3e31c7d554`.

## Blind Benchmark Status

- `pipeline_inputs`: one opaque hardlink input executed.
- `truth_manifest`: not read by the pipeline before decisions.
- Label leak check: `PASS_FOR_EXECUTED_PIPELINE_INPUT`.
- GNSS-SDR runs: three receiver attempts, including one full-file run.
- X-108 live decisions: one live `HOLD`.
- Receipts: one demo receipt attached to the live decision.
- Confusion matrix: not computed.
- Reproducibility: partial only; repeated receiver attempts reproduce no-PVT, not a full attack benchmark.

## Why This Is Not A PASS

`RECORDED_RF_ATTACK` requires a hostile RF recording to produce enough receiver observables/PVT for a post-hoc attack evaluation without label leakage. This run proves real hostile RF ingestion, tracking instability, fail-closed governance, live X-108, and receipt generation. It does not prove correct spoofing classification because NAV/PVT is absent and the first anomaly predates the official attack onset.

## Public Wording Allowed

Allowed:

> Obsidia GPS Defense has processed official FGI-SpoofRepo hostile RF offline through GNSS-SDR into acquisition/tracking/observables, then through the Physical Reality Gate, P3-05, P4-20, and live X-108, producing a fail-closed `HOLD` receipt. `RECORDED_RF_ATTACK` is not claimed yet because no NAV/PVT solution was produced and spoofing classification was not proven.

Forbidden:

- `RESISTANT_TO_SPOOFING`
- `PRODUCTION`
- `AVIATION_VALIDATED`
- `RECORDED_RF_ATTACK passed`
- `FGI spoofing benchmark passed`
