# Canonical C2 Governed-Remediation Conformance Proof — v0

Purpose: `CANONICAL_C2_GOVERNED_REMEDIATION_CONFORMANCE_V0`

Byte-preserving archive of the first end-to-end governed-remediation proof, run on the
canonical tracked fixture `tests/fixtures/governed_c2_conformance_pilot/pilot_target_v0.txt`.

- `negative/` — the NEGATIVE governed run: HumanApproval -> real KX108_PRE ALLOW ->
  SealedRollbackEvidence -> governed A->B -> SealedApplyReceipt -> genuine TestContract
  FAIL (`REQUIRED_TEST_FAILED`) -> real KX108_POST **BLOCK** -> D1 `MUST_ROLLBACK` ->
  D2 `ROLLBACK_SUCCEEDED` -> exact A restored.
- `positive/` — the POSITIVE governed run: HumanApproval -> real KX108_PRE ALLOW ->
  SealedRollbackEvidence -> governed A->B -> SealedApplyReceipt -> genuine TestContract
  `ALL_REQUIRED_PASS` -> real KX108_POST **ALLOW** -> D1
  `KEEP_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW` -> human-reviewed commit `e3877b5` ->
  fast-forward integration into `feat/terminal-runtime-repair-and-bounded-build-v1`.
- `MANIFEST.json` — machine-readable identities, gates, dispositions and a per-artifact
  hash inventory (`source_sha256` == `archived_sha256` for every file).

## Doctrine

The **governance authority** is the persisted chain
`ExecutionEnvelope/EAH -> HumanApproval -> KX108_PRE -> SealedRollbackEvidence ->
SealedApplyReceipt -> TestContractResult -> KX108_POST -> D1/D2`, archived here verbatim.

Git commit `e3877b5` is the **disposition / integration record**, NOT governance authority.

Files are the original store bytes, copied without normalization or re-serialization.
The temporary store roots the proof was produced in were left untouched by the archival turn.
