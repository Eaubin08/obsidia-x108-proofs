# GPS P6 Held-Out Corpus Acquisition V0

Status: `CANDIDATE_INVENTORY_ONLY / NOTHING_ADMITTED_YET`

## Objective

Identify new evidence sources that can satisfy the frozen P6 held-out admission contract without recycling the current development sources.

Current development sources remain excluded from held-out use:

- FGI UT_DFMC L1/E1 development case
- CTTC real-RF nominal development control

## Priority 1 — Tuni2025 GNSS / GPS Spoofing

Source: Tampere University / Zenodo.

Why it is the strongest current candidate:

- raw I/Q files are provided;
- controlled laboratory acquisition;
- both spoofed and authentic/clear-sky scenarios exist;
- GPS L1 scenarios are explicitly documented;
- acquisition hardware and spoofing simulator are documented;
- individual scenario files are separable, which allows us to reserve untouched scenarios as held-out before local ingestion.

Important boundary:

No Tuni2025 scenario becomes `HELD_OUT` merely because it is downloaded.
Before any file is processed, we must:

1. select candidate positive and negative scenarios;
2. freeze their split externally;
3. store RF SHA-256;
4. keep reference/scenario truth sealed from the classifier run;
5. seal classifier output first;
6. only then unseal the reference manifest;
7. run the P6 admission contract.

Current state: `CANDIDATE_NOT_DOWNLOADED_NOT_ADMITTED`.

## Priority 2 — TEXBAT

Source: University of Texas Radionavigation Laboratory.

Relevant properties:

- raw RF binary datasets;
- clean baseline data is available;
- multiple spoofing scenarios are available;
- later datasets ds7/ds8 include more subtle attack scenarios.

Potential use:

- reserve one or more untouched spoofing datasets as positive held-out candidates;
- reserve an untouched clean dataset as negative held-out candidate.

Caution:

TEXBAT is a well-known benchmark and some attack metadata is public. The local evaluation harness must therefore prevent that metadata from entering the classifier path before output sealing.

Current state: `CANDIDATE_NOT_DOWNLOADED_NOT_ADMITTED`.

## Priority 3 — Multi-frequency Android GNSS spoofing dataset

Source: public GitHub dataset with synchronized spoofing intervals and a normal clean-data folder.

Useful properties:

- spoofed and clean scenarios;
- L1, L5 and L1+L5;
- exact ground-truth time intervals;
- multiple consumer devices.

Limitation for current P6:

This source contains Android GNSS raw measurements rather than the raw RF I/Q format used by the current P4 physical replay path.

Current state: `SECONDARY_CANDIDATE_FORMAT_MISMATCH_WITH_CURRENT_P4_PIPELINE`.

## Acquisition order

1. Tuni2025: inspect scenario inventory and file sizes; choose one untouched spoofed scenario and one untouched clear-sky scenario.
2. Freeze split + hashes before classifier execution.
3. Adapt only file-format ingestion if required; do not change frozen P4 thresholds.
4. Execute classifier without reference truth.
5. Seal classifier output.
6. Unseal truth/reference manifest.
7. Attempt P6 held-out admission.
8. Only after at least one admitted positive + one admitted negative case, compute first TP/TN/FP/FN matrix.
9. Repeat across more held-out scenarios before making any performance claim.

## Claim boundary

This acquisition work validates only:

`TRAJECTORY_DISCONTINUITY_CLASSIFIER_ONLY_NO_SPOOFING_OR_CAUSAL_ATTRIBUTION`

It does not establish:

- spoofing attribution;
- causal attribution;
- spoofing resistance;
- aviation validation;
- production readiness.

## Governance

- `decision_authority = KX108_ONLY`
- readonly evidence ingestion
- no ACT
- no verdict emission by Brody
- no memory write
- no kernel/X108 mutation
- certification remains `NOT_CERTIFIED`
