# GPS P6 Tuni2025 Reservation Protocol V0

Status: `SOURCE_AUDITED / NO_FILE_DOWNLOADED / NO_CASE_ADMITTED`

## Source audit

Tuni2025 exposes nine GPS L1 scenarios. The public inventory includes two clear-sky cases and multiple spoofed cases, including delayed injection. Raw files are interleaved 32-bit float I/Q captured at 50 MSps using a USRP-2945R.

For P6, the public scenario names are considered **reference metadata**, not classifier input.

## Blind execution rule

Before P4 sees any downloaded RF file:

1. compute SHA-256 locally;
2. create an opaque classifier-facing ID from the hash;
3. hardlink/copy the raw RF file into a classifier input directory under the opaque ID;
4. do not copy scenario README or truth metadata into that directory;
5. run P4 only against the opaque file;
6. seal classifier output and its SHA-256;
7. only after sealing, consult the scenario reference metadata;
8. build the reference manifest and attempt admission through `gps_p6_heldout_corpus_contract_v0`.

## Candidate strategy

Reserve at least:

- one untouched spoofed GPS L1 scenario as the positive candidate;
- one untouched clear-sky GPS L1 scenario as the negative candidate.

Do not use the current FGI or CTTC development sources.

A useful positive candidate is the delayed-injection scenario because it provides a transition rather than only a static condition. A useful negative candidate is one of the clear-sky scenarios. Exact local reservation mapping should remain outside the classifier-facing path until post-classification unseal.

## Storage note

Tuni2025 files are large: the public records show roughly 30 GB per scenario, with the delayed-injection file around 40 GB. Plan local disk accordingly.

## Boundary

This protocol validates only the frozen P4 trajectory-discontinuity classifier. It does not turn a public spoofing label into a classifier feature and does not establish spoofing causality or certification.
