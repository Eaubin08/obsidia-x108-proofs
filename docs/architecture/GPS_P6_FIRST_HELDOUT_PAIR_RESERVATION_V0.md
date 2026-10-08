# GPS P6 First Held-Out Pair Reservation V0

Status: `PAIR_RESERVED_NOT_DOWNLOADED_NOT_ADMITTED`

## Reserved positive

Tuni2025 GPS L1 scenario SS-33 is reserved as the first positive held-out candidate.

Public source facts:

- Zenodo record: 15624648
- DOI: 10.5281/zenodo.15624648
- file: `SS-33 GPS Delayed Spoofer Injection (All PRNs Spoofed).bin`
- public size: 40.0 GB
- public MD5: `2320ab15af06dd66bfe459094e24381e`
- raw interleaved float32 I/Q
- 50 MSps
- GPS L1

The scenario name and reference truth are metadata for reservation/unseal only and must never appear in the classifier-facing path.

## Reserved negative

Tuni2025 GPS L1 clear-sky C-5 is reserved as the first negative held-out candidate.

Public source facts:

- Zenodo record: 15572976
- DOI: 10.5281/zenodo.15572976
- file: `Clear-Sky Signal C-5.bin`
- public size: 30.0 GB
- public MD5: `a03dedd79ac4208f6d60b4c916484dba`
- raw interleaved float32 I/Q
- 50 MSps
- GPS L1

## Reservation boundary

Reservation is not admission.

At this point:

- neither RF file is downloaded;
- no local SHA-256 exists;
- no opaque classifier-facing filename exists;
- P4 has not executed;
- no classifier output has been sealed;
- no reference manifest has been unsealed;
- neither case counts toward P6 readiness;
- the confusion matrix remains blocked.

## Next execution sequence

For each reserved file:

1. download outside the classifier-facing directory;
2. verify the public MD5;
3. compute local SHA-256;
4. prepare opaque classifier input using `p6_prepare_heldout_candidate.py`;
5. run the frozen P4 classifier against only that opaque input;
6. seal classifier output + SHA-256;
7. unseal the reserved reference condition;
8. construct the held-out admission object;
9. run `gps_p6_heldout_corpus_contract_v0`;
10. only after both cases are admitted may P6 compute a first 2-case matrix.

A 2-case matrix is a plumbing proof, not a performance claim.
