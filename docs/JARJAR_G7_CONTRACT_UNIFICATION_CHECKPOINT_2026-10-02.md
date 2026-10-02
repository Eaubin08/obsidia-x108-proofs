# JARJAR G7 CONTRACT UNIFICATION CHECKPOINT

Date: 2026-10-02
Branch: work/jarjar-g7-contract-unification
Base: G5 CLOSED / PROVED
Scope: additive result-contract unification only

## Goal

Unify the externally consumed shape of governed CREATE / MOVE / PATCH / ROLLBACK results
without reopening or rewriting G1-G5 behavior.

## Canonical contract

Contract version: G7_V0

Canonical phases:
- PREPARE
- EXECUTE
- ROLLBACK_PREPARE
- ROLLBACK_EXECUTE

Canonical authority:
- decision_authority = KX108_ONLY
- jarvis_authority = NONE

Canonical normalized fields include:
- operation_type
- phase
- status / reason
- session_id
- execution_authority_hash
- rollback_authority_hash / rollback_authority
- human_approval_required
- human_authorization_consumed
- kx108_pre_gate
- kx108_invocations_during_rollback
- executor_provider / executor_backend
- target_path / target_paths
- source_path / dest_path
- restored_sha256
- sealed_rollback_evidence_ids
- sealed_apply_receipt_ids

## Design rule

G7 is an adapter layer.

It:
- does not authorize
- does not decide
- does not mutate
- does not execute
- does not persist
- does not change KX108 authority
- does not change G1-G5 internal results

It only maps existing governed outputs to one canonical read-only envelope.

## Fail-closed validation

The canonical validator rejects:
- non-KX108 decision authority
- Jarvis authority other than NONE
- invalid/unknown phase
- missing operation type/status
- phase/status mismatches
- rollback execution with KX108 reinvocation
- successful rollback without consumed human authorization

## Explicitly preserved differences

Operation-specific semantics remain operation-specific:
- CREATE_FILE may have one SRE
- APPLY_PATCH may have multiple SREs
- MOVE rollback uses source/destination paths
- PATCH rollback uses exact preimage restoration
- destructive DELETE remains HOLD

The unified contract normalizes representation; it does not erase semantic differences.

## Current status

IMPLEMENTED:
- scripts/jarjar_governed_contract_v0.py
- tests/test_jarjar_contract_unification_g7.py

CLOSURE EVIDENCE:
- local Windows targeted + regression suite: 79 passed
- canonical adapter validated against real governed CREATE_FILE output
- canonical adapter validated against real governed MOVE_FILE output
- canonical adapter validated against real governed APPLY_PATCH output
- canonical adapter validated against real governed PATCH rollback output
- no authority changes
- no mutation added by G7
- G1-G5 behavior remains untouched

FINAL VERDICT:
G7 CLOSED / PROVED


## Final closure — 2026-10-02

Observed local result:

- 79 passed
- suite duration: 87.62s
- branch: work/jarjar-g7-contract-unification

G7 is closed as an additive read-only contract-normalization layer.
It does not replace operation-specific contracts and does not reopen G1-G5.
