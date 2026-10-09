# CSSA historical → native intake draft V0

2026-10-09. Branch `feat/cssa-v01-active` only. Previous user verification: 172 PASS, 1 SKIP with real F3F/F3G engines in isolated historical checkout.

## New boundary

`periphery/cssa_historical_native_intake_draft_v0.py` consumes a read-only historical assessment projection and returns a `NativeCaseTaskIntakePlanV0` **for review only** when caller explicitly supplies a source reference, evidence references, assigned owner and timezone-aware occurrence/deadline. The plan uses the existing native plan constructor and verification, with distinct non-calendar case types: CONTRACT_REVIEW, COMPLIANCE_REVIEW, INSTITUTIONAL_REVIEW, INCIDENT_REVIEW, MATCHDAY_OPERATIONS_REVIEW, SEASON_CONFLICT_REVIEW.

It never invokes `execute_native_case_task_intake_v0` or `project_native_work_to_action_v0`, never creates `ActionCandidate`, never authorizes any real operator, and never asserts external source authenticity. User-supplied provenance strings are **unverified references**, not proof of a real institution/club. Historical fixture `ALLOW` is not sovereign `ALLOW`.

On contradiction, missing owner, source/evidence, or invalid timezone-aware date the bridge returns HOLD/BLOCK without a plan. The bridge intentionally does **not** import legacy engines into Obsidia runtime, or create any live Calendar/CRM/task changes.

## Validation and pending proof

Eight targeted tests added in `tests/test_cssa_historical_native_intake_draft_v0.py`: plan contract, stable hash, BLOCK, missing source, missing evidence, naive deadline, owner missing, and no escalation. Not run yet by the user: expected scoped total **180 PASS, 1 SKIP**, if both repos and environment remain configured. This is not historical 904-event suite regression nor an operational pilot.

Next stage needs direct old-source assessments through this bridge and real independent authority/provenance verification, before any native commit or Universal execution can be claimed for F3F/F3G. No `main` push, no freeze.
