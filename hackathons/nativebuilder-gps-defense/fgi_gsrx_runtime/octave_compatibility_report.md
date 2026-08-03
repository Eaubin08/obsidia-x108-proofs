# FGI-GSRx Octave Compatibility Report

Date: 2026-08-03

## Runtime

- Docker image: `obsidia-fgi-gsrx-octave:ut-dfmc-v0`
- Base: `ubuntu:24.04`
- Octave: `8.4.0`
- FGI-GSRx: `FGI-GSRx-v2.1.3`, commit `7d447b32bc6b76d1e099b46c92c12d1d8717c4cd`
- License: GPL-3.0
- Dataset in image: no
- Dataset mount: read-only

## Compatibility shims

All shims are isolated under `hackathons/nativebuilder-gps-defense/fgi_gsrx_runtime/compatibility_shims/`.

| Shim | Reason | Algorithm changed? |
|---|---|---|
| `gsrx.m` | Force `save("-mat7-binary", ...)` for Octave object persistence and persist final audit products. | No GNSS algorithm change. |
| `contains.m` | Octave 8.4.0 lacks MATLAB `contains`. | No. |
| `gpsl1DecodeEphemeris.m` | Octave `dec2bin` requires integer input; MATLAB accepts logical bits. | No, only casts logical bit vectors to `double`. |
| `calcStatistics.m` | No graphics toolkit in headless container. | No, statistics formulas unchanged; final plot skipped. |

## Results

- Smoke test opened `UTD_L1_E1.dat` as real int8 data and acquired GPS L1 signals.
- Window A `0-60 s` produced full tracking, preambles, ephemerides and NAV/PVT.
- Window C `135-180 s` produced full tracking, preambles, ephemerides and NAV/PVT.
- The wrapper `gsrx` is still memory-sensitive when saving full final MAT products; lightweight JSON extraction is used for audit outputs.

## Remaining runtime limitation

Window B `90-134 s` was not executed in this lot. It remains useful for an immediate pre-onset baseline, but A and C already prove that the official hostile RF file can be decoded to NAV/PVT before and after the official 135 s onset.
