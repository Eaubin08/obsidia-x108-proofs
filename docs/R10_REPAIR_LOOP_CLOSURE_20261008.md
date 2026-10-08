# R10 Repair Loop Closure - 2026-10-08

## Status

R10_STATUS=CLOSED
R10_VERDICT=PASS_WITH_GLOBAL_LIMITATIONS
SAFE_TO_DECLARE_R10_CLOSED=YES

R10_CLOSING_OBSIDIA_HEAD=0899d84c

R10_B1=68373194
R10_B2=a6c386cb
R10_B3=0899d84c

BLOCKING_DEFECTS_R10=0
GLOBAL_REGRESSION_PASS=NO

This document freezes the completed OpenJarvis/Obsidure R10 repair-loop milestone. It records the canonical R10 lineage, the historical machinery reused, the observed validation evidence, and the remaining limitations that are outside the R10 repair-loop closure.

## Canonical R10 Stack

- R10-A REPAIR LOOP FORENSIC
- R10-B1 CANONICAL REPAIR ADAPTER
- R10-B2 BOUNDED REPAIR LOOP RECONNECTION
- R10-B3 REPAIR OUTCOME / R8 EVIDENCE FEEDBACK
- R10-B4 INDEPENDENT ADVERSARIAL CERTIFICATION

## Historical Machinery Reused

R10 does not introduce a parallel repair engine, builder, manifest store, validation system, executor, receipt model, replay model, reconciliation model, mission authority, or memory authority.

Reused components include:

- AgentObsidure failure and disruption cycle
- IterationMemory and ErrorContext failure tracking
- RepairRequest / RepairProposal / RepairVerdict contracts
- obsidure_repair_bridge sandbox validation
- C278 proposal meaning validation
- R9-B1 canonical Obsidure builder proposal
- R9-B2 proposal manifest and provenance contract
- R9-B3 proposal validation gate
- R9-B4 governance handoff
- R9-B5 governed patch PREPARE adapter
- R9-B6 governed APPLY_PATCH evidence fixtures and tests
- R8 canonical receipt envelope
- R8 evidence-only replay
- R8 governance decision replay
- R8 realized-state reconciliation

## AgentObsidure Repair Pipeline

Canonical R10 repair flow:

failure -> ErrorContext / IterationMemory -> classification -> RepairRequest -> RepairProposal -> C278 CONTINUOUS -> sandbox RepairVerdict PASS -> R10-B1 canonical adaptation -> R9-B1/B2/B3/B4/B5 governed PREPARE -> reviewed authorization / KX108 boundary -> existing R9-B6 execution evidence -> R8 receipt / replay / reconciliation -> R10-B3 outcome feedback -> stop / retry candidate / escalation.

PREPARED != EXECUTED

EXECUTED != VERIFIED

UNKNOWN != FAILURE

REPLAY != RE-EXECUTION

R10-B2 reconnects AgentObsidure to the canonical R10-B1 adapter through `prepare_last_validated_repair(...)`. It stops at R9-B5 PREPARE and does not invoke an executor.

R10-B3 adds read-only ingestion of already-persisted R8 execution evidence through `ingest_repair_execution_outcome(...)`. It returns advisory stop/retry/escalation classifications and does not write memory, mutate canonical receipts, call KX108, or execute a retry.

## C278 and Sandbox Validation

C278 remains the semantic/material continuity gate between a RepairRequest and a concrete RepairProposal. R10 accepts only continuous C278 evidence bound to the same request/proposal/attempt identity.

Sandbox validation remains owned by the existing RepairVerdict path. R10-B1 requires a PASS verdict and preserves the tested artifact evidence, tested patch hash, base SHA, sandbox verdict, and evidence provenance.

C278_NON_CONTINUOUS=HOLD
SANDBOX_FAILURE=HOLD_OR_RETRY_CANDIDATE_ONLY_WHEN_BOUNDED
PARTIAL_OR_UNKNOWN_VERDICT=NO_SUCCESS_CLAIM

## R9 Governance Handoff

R10 reuses the R9 pipeline:

- R9-B1 constructs the canonical builder proposal from a validated RepairProposal.
- R9-B2 binds manifest provenance and candidate patch references.
- R9-B3 validates proposal obligations, protected paths, tested artifact integrity, scope, and base evidence.
- R9-B4 creates the governance handoff.
- R9-B5 prepares a governed action.
- R9-B6 remains the existing governed execution/evidence layer and is not automatically invoked by R10.

R10 never treats R9-B5 PREPARED as execution.

## R8 Evidence Feedback

R10-B3 reuses R8 canonical receipt APIs:

- CANONICAL_RECEIPT_ENVELOPE_V1
- CANONICAL_RECEIPT_REPLAY_RESULT_V1
- GOVERNANCE_DECISION_REPLAY_RESULT_V1
- REALIZED_STATE_RECONCILIATION_RESULT_V1

Outcome ingestion binds the action evidence back to:

- mission identity
- repair request ID
- repair proposal ID
- repair verdict ID
- repair attempt identity
- R9 proposal identity
- R9 handoff identity
- prepared action identity
- action_evidence_id
- KX108 decision reference
- realized-state evidence
- original failure identity

No fabricated execution result is created. Canonical receipts remain immutable.

## Mission Scope and Repair Budgets

R10 preserves bounded mission constraints:

- mission identity is explicit
- allowed targets remain scoped
- protected paths remain protected
- stale base and worktree drift are stop conditions
- repair attempt identity is preserved
- repeated failure and oscillation are stop conditions
- repair budget exhaustion is a stop condition
- revoked or closed mission blocks promotion
- contradictory or tampered evidence blocks promotion

R10 does not reset mission budgets, mint new authority, widen target scope, or promote failed dependencies as PASS.

## Stop / Retry / Escalation Semantics

STOP_SUCCESS is permitted only when existing replay, decision replay, and realized-state reconciliation support the same governed execution lineage.

STOP_BLOCKED is used for tampered evidence, governance mismatch, protected path/scope violations, exhausted or revoked mission boundaries, KX108 HOLD/BLOCK, and unsafe identity mismatches.

RETRY_CANDIDATE is advisory only. It is allowed only when the failure is bounded, the mission remains valid, the budget remains available, the original scope is preserved, and fresh validation/governance would still be required.

ESCALATE is used for uncertain physical outcomes, incomplete replay where success cannot be claimed, crash/partial-write uncertainty, and evidence that is insufficient for a safe retry.

R10 never performs an automatic retry.

## Authority Boundaries

KX108_ONLY=YES
OBSIDURE_AUTHORITY=NONE
AGENTOBSIDURE_AUTHORITY=NONE
R10_ADAPTER_AUTHORITY=NONE
R8_REPLAY_AUTHORITY=NONE
R8_RECONCILIATION_AUTHORITY=NONE

AgentObsidure may classify, propose, test in sandbox, prepare governed repair actions, and ingest immutable evidence. It does not authorize actions.

R10-B1/B2/B3 create no parallel authority. KX108 remains the action decision authority. R8 replay never executes an action. Feedback is not authorization.

## Adversarial Certification Results

Independent R10-B4 certification verified the full repair chain and adversarial cases for:

- missing or substituted repair evidence
- conflicting repair identities
- cross-mission evidence substitution
- wrong builder handoff
- wrong action_evidence_id
- revoked or closed mission
- exhausted agent/mission budget
- repeated failure
- oscillation
- stale Git base / worktree drift
- modified patch or tested artifact
- C278 non-continuous
- sandbox failure or partial verdict
- R8 receipt tampering
- replay mismatch / incomplete replay
- historical policy-version limitations
- Binder evidence limitations
- KX108 HOLD / BLOCK
- pre-dispatch failure
- uncertain physical outcome
- crash/partial-write limitations
- duplicate or replayed feedback
- missing attempt chronology

Observed R10-focused and adjacent certification:

- R10-B1/B2/B3 + R9-B6 focused: 31 passed
- R8 receipt/replay/reconciliation focused: 34 passed
- R10/Agent/C278/bounded mission excluding unrelated Brody drift: 191 passed, 2 deselected
- R9/R8 block: 107 passed
- bounded/governed apply block: 201 passed, 2 skipped, 9 subtests passed

## Known Deferred Evidence Limits

These limits are known and do not block R10 closure:

- R8 early PREPARE rejection receipt integration remains deferred.
- R8 approval-missing receipt integration remains deferred.
- Binder historical replay remains inline-status-only.
- Historical KX policy version is not universally persisted/bound.
- Generic uncertainty normalization is not implemented for every future domain.
- UIA/filesystem/window/app capability families are not all normalized through R8-B6 reconciliation adapters.
- Live/current-state reconciliation is not implemented generically.
- Generic rollback is not implemented.
- Real physical executor full E2E remains incomplete across capability families.
- Final state-check to browser dispatch is minimized but not atomic.
- Brody/OpenJarvis global collection failures are outside R10.

## Unrelated Global Collection Failures

R10 closure does not claim full global regression PASS.

Observed global collection blockers outside the R10 repair-loop scope:

- `tests/api/test_f17c_brody_source_label.py` cannot import `_source_label_from_graphiti_probe` from `apps.obsidia_api.brody_real_response_pipeline`.
- `tests/cli/test_cognitive_ingress_final_surface_v0.py` cannot import module `openjarvis`.
- `tests/cli/test_openjarvis_native_cli_bridge_v0.py` cannot import module `openjarvis`.

Observed unrelated Brody expectation drift:

- `test_brody_pipeline_attaches_repair_request` expected `REPAIR_REQUEST_EMITTED`, observed `C276_CANDIDATE_NOT_READY`.
- `test_brody_pipeline_non_debug_is_unchanged` expected `NOT_A_REPAIR_INTENT`, observed `NO_ACTION_CANDIDATE_REQUESTED`.

These are not repaired or hidden by this closure document.

## Forbidden Overclaims

R10 CLOSED does not mean:

- full global pytest pass
- autonomous self-build
- automatic production repair
- new execution authority
- memory promotion authority
- generic rollback
- complete physical executor normalization
- proof of every capability family
- R11 implementation

## Next

NEXT=R11 CONTROLLED SELF-BUILD FORENSIC

R11 must begin with forensic reuse of existing AgentObsidure, AVDR, bounded mission, governed apply, R9 builder, R10 repair-loop, and R8 receipt/replay/reconciliation components. It must not create another builder or repair engine, and self-build must never grant itself new permissions.
