# R8 Receipts / Replay / E2E Closure - 2026-10-07

## Status

R8_STATUS=CLOSED
R8_VERDICT=PASS_WITH_DEFERRED
SAFE_TO_DECLARE_R8_CLOSED=YES

R8_CLOSING_OBSIDIA_HEAD=6047da3c
R8_CLOSING_JARJAR_HEAD=a1abae1

BLOCKING_DEFECTS=0

This document freezes the completed OpenJarvis/Obsidia R8 milestone. It records what is proven, what remains deliberately deferred, and the authority boundaries that continue to govern follow-on work.

## Canonical R8 Stack

- R8-A FORENSIC
- R8-B1 CANONICAL RECEIPT
- R8-B2 FAILURE/HOLD/BLOCK/UNCERTAINTY RECEIPTS
- R8-B3 EVIDENCE-ONLY REPLAY
- R8-B4 TAMPER/IMMUTABILITY HARDENING
- R8-B5 DETERMINISTIC GOVERNANCE DECISION REPLAY
- R8-B6 REALIZED-STATE RECONCILIATION
- R8-B7 TRUE E2E CERTIFICATION
- R8-B7R FINAL TOCTOU REPAIR

## Canonical Identities

No V2 receipt/replay/reconciliation object is introduced by this closure.

- CANONICAL_RECEIPT_ENVELOPE_V1
- action_evidence_id
- CANONICAL_RECEIPT_REPLAY_RESULT_V1
- GOVERNANCE_DECISION_REPLAY_RESULT_V1
- REALIZED_STATE_RECONCILIATION_RESULT_V1

## Proven Core Properties

CANONICAL_RECEIPT=YES
SINGLE_ACTION_ID=YES

SUCCESS_RECEIPTS=YES
NOOP_RECEIPTS=YES
FAILURE_RECEIPTS=YES
HOLD_BLOCK_RECEIPTS=YES
UNCERTAINTY_RECEIPTS=YES

IMMUTABLE_CREATE_ONCE=YES
CANONICAL_SERIALIZATION=YES
TAMPER_EVIDENCE=YES

EVIDENCE_ONLY_REPLAY=YES
PHYSICAL_REPLAY_THROUGH_REPLAY_API=NO

DETERMINISTIC_DECISION_REPLAY=YES_WITH_POLICY_VERSION_LIMIT
REALIZED_STATE_RECONCILIATION=YES_FOR_CURRENT_NORMALIZED_BROWSER_SET

REPLAY_AUTHORITY=NONE
RECONCILIATION_AUTHORITY=NONE

AUTOMATIC_RETRY=NO
PHYSICAL_REPLAY_DEFAULT=NO
PLAINTEXT_SECRET_EXPANSION=NO

## TOCTOU Contract

R8 freezes a two-phase TOCTOU model:

- PRE_AUTHORIZATION
- POST_AUTHORIZATION_PRE_EXECUTION

Canonical governed flow:

prepare -> prepared state anchor -> early stale guard -> approval -> KX108 -> Binder -> final state-anchor guard -> executor

EARLY_GUARD_PRESERVED=YES
FINAL_POST_KX_PRE_EXECUTION_GUARD=YES
POST_KX_PRE_EXECUTION_STATE_DRIFT_CAN_ESCAPE=NO for the patched Browser V0 paths.
FINAL_GUARD_ATOMIC=NO

The final guard reduces the stale-authorized-state window. It does not claim hardware/browser atomicity across the state read and browser dispatch boundary.

## Replay Semantics

REPLAY != RE-EXECUTION

Evidence replay asks whether historical artifacts are intact and coherent.

Decision replay asks whether the historical governance result is reproducible from frozen historical governance inputs.

Reconciliation asks whether recorded realized state corresponds to the authorized effect.

These are distinct layers. Valid governance does not imply successful realization.

## Legal Combinations

DECISION_REPLAY=MATCH and RECONCILIATION=MATCH is valid.

DECISION_REPLAY=MATCH and RECONCILIATION=NOOP_CONFIRMED is valid.

DECISION_REPLAY=MATCH and RECONCILIATION=MISMATCH is valid.

DECISION_REPLAY=MATCH and RECONCILIATION=UNCERTAIN is valid.

HOLD/BLOCK with NOT_REALIZED is valid.

VALID_GOVERNANCE != SUCCESSFUL_REALIZATION

## Early TOCTOU

PRE_AUTHORIZATION TOCTOU may stop before approval and KX.

Therefore B5 may be INCOMPLETE under the current contract, or NOT_APPLICABLE semantically in a future explicit contract, because there was no historical KX decision. Historical authorization must not be fabricated to satisfy replay.

## Late TOCTOU

POST_AUTHORIZATION_PRE_EXECUTION TOCTOU has these required properties:

- approval reached
- KX reached
- Binder reached
- executor not called
- physical_effect_dispatched=false

Expected composition:

- B3=VERIFIED or VERIFIED_WITH_LIMITS
- B5=MATCH
- B6=NOT_REALIZED

## E2E Certification

SUCCESS_MUTATION=PASS
SUCCESS_NOOP=PASS
KX108_HOLD=PASS
KX108_BLOCK=PASS
TOCTOU_EARLY=PASS
TOCTOU_LATE=PASS
EXECUTOR_FAIL_BEFORE_ACTION=PASS
POSTCONDITION_MISMATCH=PASS
DISPATCHED_OUTCOME_UNCERTAIN=PASS
PRIVACY=PASS
TAMPER=PASS
MISSING_ARTIFACT=PASS
REPLAY_SAFETY=PASS

## Browser Paths

Final late-TOCTOU protection is recorded for:

- BROWSER_SET_CHECKED
- BROWSER_SET_DISCLOSURE
- BROWSER_SELECT_RADIO
- BROWSER_SELECT_OPTION
- BROWSER_SET_FIELD_VALUE
- BROWSER_SUBMIT_FORM_NAVIGATION_V0

No coverage is claimed for capability families not verified in R8.

## Deferred Limits

Each deferred limit below has BLOCKS_R8_V0=NO.

R8-D01 early PREPARE rejection canonical receipt integration

R8-D02 approval-missing canonical receipt integration

R8-D03 Binder historical replay remains inline-status-only

R8-D04 historical KX policy version not universally persisted/bound

R8-D05 generic uncertainty model not normalized across every future domain

R8-D06 UIA / filesystem / window / app families not all normalized through the B6 reconciliation adapter model

R8-D07 live/current-state reconciliation not implemented

R8-D08 generic rollback not implemented

R8-D09 real physical executor full E2E remains incomplete across capability families

R8-D10 final state-check -> browser dispatch is minimized but not atomic

## Forbidden Overclaims

R8 CLOSED does not mean:

- all domains integrated
- all executors normalized
- all rollback solved
- perfect distributed atomicity
- perfect historical policy reconstruction
- application/business success proof
- generic browser click/fill/submit exposed
- autonomous repair
- self-build
- R9+

## Authority Freeze

KX108_ONLY=YES
OPENJARVIS_AUTHORITY=NONE
JARJAR_AUTHORITY=NONE
REPLAY_AUTHORITY=NONE
RECONCILIATION_AUTHORITY=NONE

MATCH != AUTHORIZATION
MISMATCH != REPAIR_PERMISSION
UNCERTAIN != RETRY_PERMISSION

## Next

NEXT=R9 OBSIDURE BUILDER

R9 must begin with forensic/reentry against the frozen R0-R8 contracts. This closure does not implement R9 and does not blindly reconnect historical Obsidure.
