# GPS Defense — P6 Resume Plan

Date: 2026-10-08  
Status: `PAUSED_FOR_LOCAL_DISK_CAPACITY`

## Purpose

This file is the canonical restart checkpoint for GPS Defense P6.

Do not restart P6 from memory. Resume from this document and the frozen artifacts referenced below.

## Closed before pause

The following work is complete and merged into `feat/gps-defense-brody-cognitive-bridge-v0`:

- P4 recorded RF temporal trajectory-discontinuity classifier;
- P5 observational support boundary;
- P4/P5 -> Brody/SENS semantic closure;
- P6 confusion-matrix readiness contract;
- P6 held-out corpus admission contract;
- P6 corpus acquisition protocol;
- Tuni2025 blind reservation protocol;
- first held-out positive/negative pair reservation.

Targeted verification reached:

- P6 readiness: `8/8 PASS`;
- held-out admission contract stack: `20/20 PASS`;
- first-pair reservation stack: `24/24 PASS`.

## Current canonical state

```text
P4 anomaly evidence                  CLOSED
P5 observational support             CLOSED
Brody/SENS semantic join             CLOSED
P6 readiness contract                CLOSED
P6 held-out admission contract       CLOSED
P6 acquisition protocol              CLOSED
first Tuni2025 pair                  RESERVED
RF files downloaded                  NO
held-out cases admitted              0
confusion matrix computable          NO
certification                        NOT_CERTIFIED
pause reason                         LOCAL_DISK_CAPACITY
```

## Frozen governance

These boundaries must not be relaxed during restart:

- `decision_authority = KX108_ONLY`
- readonly evidence path
- `allowed_to_decide = false`
- `allowed_to_act = false`
- `emits_act = false`
- `emits_verdict = false`
- `memory_write = false`
- `kernel_mutation = false`
- `x108_mutation = false`

P6 evaluates only:

`TRAJECTORY_DISCONTINUITY_CLASSIFIER_ONLY_NO_SPOOFING_OR_CAUSAL_ATTRIBUTION`

Do not convert P6 into a spoofing classifier.

## Existing development evidence — never relabel as held-out

The following sources are development/control evidence only:

- `FGI_UT_DFMC_L1E1_DEVELOPMENT`
- `CTTC_REAL_RF_NOMINAL_DEVELOPMENT_CONTROL`

They must never be counted as blind P6 validation.

## Reserved first held-out pair

### Positive candidate

- provider: Tampere University
- family: Tuni2025 GPS L1
- reservation: `TUNI2025_POSITIVE_SS33`
- public scenario: SS-33 delayed spoofer injection
- Zenodo record: `15624648`
- DOI: `10.5281/zenodo.15624648`
- public file size: approximately 40 GB
- public MD5: `2320ab15af06dd66bfe459094e24381e`
- expected post-unseal reference: `TRAJECTORY_DISCONTINUITY_PRESENT`

### Negative candidate

- provider: Tampere University
- family: Tuni2025 GPS L1
- reservation: `TUNI2025_NEGATIVE_C5`
- public scenario: C-5 clear-sky
- Zenodo record: `15572976`
- DOI: `10.5281/zenodo.15572976`
- public file size: approximately 30 GB
- public MD5: `a03dedd79ac4208f6d60b4c916484dba`
- expected post-unseal reference: `TRAJECTORY_DISCONTINUITY_ABSENT`

Total local capacity required for the two raw RF files is approximately 70 GB, plus working/output space.

## Restart precondition

Do not resume RF acquisition until sufficient local/external storage exists.

Recommended restart condition:

- raw RF storage available;
- additional working space available for opaque copies/hardlinks, receiver outputs, logs and hashes;
- Git worktree clean;
- frozen P4 thresholds unchanged.

## Exact restart sequence

### 1. Synchronize the canonical branch

```powershell
git fetch origin
git switch feat/gps-defense-brody-cognitive-bridge-v0
git pull --ff-only
git status --short
```

Expected: clean worktree.

### 2. Verify the frozen P6 files exist

Key files:

```text
periphery/cognition/gps_p6_confusion_matrix_readiness_v0.py
periphery/cognition/gps_p6_heldout_corpus_contract_v0.py
scripts/gps/p6_prepare_heldout_candidate.py
hackathons/nativebuilder-gps-defense/rf_attack_benchmark/p6_first_heldout_pair_reservation_v0.json
docs/architecture/GPS_P6_HELDOUT_CORPUS_CONTRACT_V0.md
docs/architecture/GPS_P6_TUNI2025_RESERVATION_PROTOCOL_V0.md
docs/architecture/GPS_P6_FIRST_HELDOUT_PAIR_RESERVATION_V0.md
```

### 3. Re-run the frozen regression slice

```powershell
python -m pytest `
  .\tests\test_p6_first_heldout_pair_reservation_v0.py `
  .\tests\test_p6_prepare_heldout_candidate.py `
  .\tests\test_gps_p6_heldout_corpus_contract_v0.py `
  .\tests\test_gps_p6_confusion_matrix_readiness_v0.py `
  .\tests\test_r6_p6_confusion_matrix_readiness_smoke.py `
  -q
```

Any regression must be investigated before RF acquisition.

### 4. Download reserved RF outside classifier-facing paths

Download SS-33 and C-5 into a staging/storage location that is not the P4 classifier input directory.

Do not run P4 directly against source filenames.

### 5. Verify source integrity

For each file:

- verify the public MD5;
- compute local SHA-256;
- record file size;
- preserve source provenance.

Do not change P4 thresholds after inspecting either held-out case.

### 6. Create opaque classifier-facing inputs

Use:

```powershell
python .\scripts\gps\p6_prepare_heldout_candidate.py `
  --source "<SOURCE_RF_FILE>" `
  --out-dir "<OPAQUE_INPUT_DIR>" `
  --manifest-out "<PRECLASSIFICATION_MANIFEST.json>"
```

The resulting classifier-facing path must contain no `SS-33`, `C-5`, `spoof`, `clear`, or other truth-bearing label.

### 7. Execute frozen P4 blindly

Run the existing frozen P4 trajectory-discontinuity classifier against the opaque input only.

Reference/scenario truth must not enter the classifier path.

### 8. Seal classifier output

Before consulting the reserved truth:

- persist classifier output;
- compute its SHA-256;
- freeze the output artifact;
- record algorithm version and frozen thresholds.

### 9. Unseal reference truth

Only after output sealing:

- consult the reservation manifest/reference metadata;
- create the reference manifest;
- hash the reference manifest.

### 10. Attempt P6 admission

Build the admission object and pass it through:

`gps_p6_heldout_corpus_contract_v0`

Expected requirements include:

- `dataset_split = HELD_OUT`
- thresholds frozen before admission;
- not used for development/tuning;
- truth invisible to classifier;
- classifier output sealed before unseal;
- valid RF/output/reference SHA-256;
- complete provenance;
- independent from development corpus.

### 11. Repeat for both positive and negative cases

P6 remains blocked until both classes are admitted.

Required minimum:

```text
heldout_positive_cases >= 1
heldout_negative_cases >= 1
```

### 12. Compute first matrix

Only after both cases are admitted may:

`compute_p6_confusion_matrix_v0`

run.

A 2-case matrix proves plumbing only. It is not a meaningful performance estimate and must not be presented as validation, certification, spoofing resistance, or aviation readiness.

## Expected state after first pair

If both cases are validly admitted:

```text
P6 held-out plumbing             CLOSED
first TP/TN/FP/FN matrix         COMPUTABLE
performance claim                NOT JUSTIFIED
spoofing causal claim            FORBIDDEN
certification                    NOT_CERTIFIED
```

## After first pair

Do not stop at the two-case matrix.

Next acquisition phase should add multiple untouched positive and negative scenarios, potentially including:

- additional Tuni2025 scenarios;
- TEXBAT as an independent external corpus;
- eventually an independent physical live/source path.

The objective is to move from plumbing proof to an actual held-out evaluation corpus without data leakage.

## Current hard blockers beyond P6 plumbing

The broader validation boundary still includes:

- `NO_INDEPENDENT_PHYSICAL_SOURCE_CORROBORATION`
- `NO_CONTROLLED_INTERVENTION`

Those blockers must remain visible even if the first held-out confusion matrix succeeds.

## Resume rule

When storage is ready, start with the exact words:

`Resume GPS P6 from docs/architecture/GPS_P6_RESUME_PLAN_20261008.md`

and continue from step 1 above.
