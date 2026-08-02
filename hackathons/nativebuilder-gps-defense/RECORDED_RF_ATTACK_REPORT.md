# RECORDED_RF_ATTACK Report

Date: 2026-08-02
Status: `BLOCKED_RECORDED_RF_ATTACK`
Baseline: `b4df0cbe825515b675380084d86b921390d78c26`

## Verdict

`RECORDED_RF_ATTACK` is **not reached**.

The current validated level remains `RECORDED_REAL_RF` from the nominal public CTTC I/Q GNSS-SDR run. No hostile RF recording traversed GNSS-SDR, Physical Reality Gate, P3-05, P4-20, live X-108, and receipt generation in this lot.

## Corpus Attempts

### TEXBAT Official

- Official page: `https://radionavlab.ae.utexas.edu/texbat/`
- Public index: `https://rnl-data.ae.utexas.edu/datastore/texbat/`
- Conditions observed: University of Texas research-use notice; do not redistribute data; no warranty.
- Files attempted:
  - `ds1.xml`
  - `ds1.md5`
  - `cleanStatic.xml`
  - `ds1.bin` HEAD and range probes
  - `cleanStatic80.bin` range probe

All TEXBAT commands timed out with zero bytes received, including 1 MiB range probes. Because no hostile RF bytes were obtained, no SHA-256 can be reported for a TEXBAT RF input.

### OAKBAT GPS

- DOI: `10.13139/ORNLNCCS/1664429`
- Landing page: `https://doi.ccs.ornl.gov/dataset/d21dfe58-3af9-5ed8-9c97-693c12045aee`
- Publisher: Oak Ridge National Laboratory.
- Access path observed: Globus file manager.

OAKBAT is a valid recognized RF spoofing fallback, but this run did not obtain a direct unauthenticated RF file. It remains a human/access action, not an executed benchmark.

### FGI-JSDR / FGI-SpoofRepo

- Index: `https://www.maanmittauslaitos.fi/en/research/research/gnss-specialists/fgi-gnss-jamming-and-spoing-dataset-repository-fgi-jsdr`
- Publisher: National Land Survey of Finland.

FGI is a valid recognized RF spoofing fallback if the raw I/Q files are obtained through the dataset portal. It was not executed in this lot.

### Zenodo 13846381

- DOI: `10.5281/zenodo.13846381`
- Small metadata downloaded:
  - `readme.txt` SHA-256 `11378893aa5e3e15e5f77b920e279240a20499d08e47b2a8d515ffacc61be19d`
  - `demo.py` SHA-256 `be9e9e3c81e6a3fcd70522a6a540603c6fe47c86bf91e556a5cd552f62b7e283`

This fallback is not eligible for the requested closure because the open README describes labeled `.mat` fragments for RF fingerprinting/classification, and the demo script reads clean/spoofer labels from file names. It does not provide the required continuous GNSS-SDR acquisition/tracking/PVT chain.

## Blind Benchmark Status

- `pipeline_inputs`: no cases created.
- `truth_manifest`: empty, committed without sensitive labels because no scenario ran.
- Label leak check: `PASS_NO_CASES`.
- Truth read before decisions: `false`.
- GNSS-SDR runs: none.
- X-108 live decisions: none for hostile RF.
- Receipts: none for hostile RF.
- Confusion matrix: not computed.
- Metrics: not computed.
- Reproducibility: not run.

## Why This Is Not A PASS

`RECORDED_RF_ATTACK` requires at least one real hostile RF recording to be processed blind through:

```text
hostile RF -> GNSS-SDR -> observables/PVT -> normalizer -> Physical Reality Gate -> DomainState -> P3-05 -> P4-20 -> live X-108 -> receipt -> post-hoc truth evaluation
```

That did not happen. No mock, synthetic substitute, or label-derived shortcut was used.

## Public Wording Allowed

Allowed:

> Obsidia GPS Defense has reached `RECORDED_REAL_RF` on a nominal public GNSS I/Q recording. The hostile RF spoofing benchmark path is specified and claim-gated, but `RECORDED_RF_ATTACK` is blocked pending access to an official hostile RF corpus such as TEXBAT, OAKBAT, or FGI.

Forbidden:

- `RESISTANT_TO_SPOOFING`
- `PRODUCTION`
- `AVIATION_VALIDATED`
- `RECORDED_RF_ATTACK passed`
- `TEXBAT benchmark passed`
