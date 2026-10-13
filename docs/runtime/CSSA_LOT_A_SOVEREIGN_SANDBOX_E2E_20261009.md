# CSSA Lot A — CSSA-origin native-to-sovereign sandbox E2E

Date: 2026-10-09. Branch: `feat/cssa-v01-active`.

## New integrated route

`CSSA synthetic DEADLINE → CSSA conflict preflight → native intake plan → existing KX108-gated CASE/interaction/TASK/FOLLOW-UP commits in isolated test directory → existing native work projection → ActionCandidate → existing WorldActionRequest → simulated operator HumanApproval → WORLD_ACTION_PRE → KX108 → existing activation policy → sovereign ticket → deterministic calendar sandbox adapter → receipt/replay → duplicate prevention`.

Source: `periphery/cssa_sovereign_sandbox_lot_a_v0.py`; tests: `tests/test_cssa_sovereign_sandbox_lot_a_v0.py`.

Positive-case approval is a **fictional sandbox operator**, never a real user authorization; source is a declared synthetic CSSA dossier, not observed club input. A KX108 ALLOW here is real computation in the existing test-only rail; no externally authorized real action occurs. Persistent native writes are limited to an isolated local test root. `external_actions=[]`, network and external effects zero.

The implementation reuses `_execute_projection` in the existing Universal full-loop module. This is a private interface; follow-up hardening should pin it with compatibility tests or prefer a supported public entry point, without editing shared runtime until specifically authorized.

## Tests

Four new tests cover CSSA-origin positive sandbox execution, receipt/replay and idempotent duplicate block, absence of simulated approval, source contradiction, and unknown regulatory basis. **Not yet run locally by the user**. Prior run before these additions: 140 passed, 1 skipped (reported by user).

Expected scoped result with the four tests: **144 passed, 1 skipped**, subject to actual Windows pytest execution. No global CI claim.

## What this does NOT close

- General season conflict campaign is still a separate synthetic review path, not all scenarios going through KX108/native store.
- F3F source fixture and 904-event historical proof not independently replayed; F3G 11-role matrix and 291 tests not independently reconciled.
- Calendar date and regulatory basis in positive case are synthetic and asserted by fixture, not independently verified against FFF/Ligue.
- No real club data, provider connection, persistent CRM production state or authority granted.
- Integration of mail, partner workflows, staffing, buvette and complete administrative season remains open.
- This is **not** a Lot A freeze; full role-by-role closure and integrated stress proof pending.

## Re-run

```powershell
Set-Location (Join-Path $env:TEMP 'cssa-eol-final')
git pull --ff-only
$cssaTests = @(Get-ChildItem tests -Filter 'test_cssa_*.py' -File | ForEach-Object { $_.FullName })
py -m pytest @cssaTests tests/integration/test_native_tasks_crm_v0.py -q --tb=short
git status --short
```

Never merge/push main or modify shared Universal, kernel, Brody, Native Memory or other domains as part of this lot.
