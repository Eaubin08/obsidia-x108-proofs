# V0.1 C4.2 — Local offline inter-repository code composition

**Status: HARNESS_IMPLEMENTED / ACTUAL_INTERREPO_RUN_REQUIRES_LOCAL_PINNED_CLONES**

2026-10-08. Base: C4.1 `f08623c28681151703a29c79e3452e45bd323ea0`.

## Purpose

C4.2 must not claim a multi-repository integration merely because the
individual repositories have passing CI. This lot introduces a strict
read-only, zero-network **local cross-repository probe**. It executes real
Python code from *the exact approved feature commits* of the GPS and Trading
repositories, reads the CSSA preflight state, and jointly verifies that
the outputs match the C4/C4.1 claims of the **core V0.1**.

It is a **contract-composition test of real source code using fake inputs**,
not a production enterprise pipeline and not an integration of real Trading
PAPER broker, KX HTTP, or live GPS. It does not implement corporate identity
attestation or cross-process revocation.

## Pinned inputs

| Component | Pin |
|---|---|
| Core C4.2 checkout | Descendant of `f08623c28681151703a29c79e3452e45bd323ea0` |
| GPS public feature | `d1221fce6914274f7b0c445a829739367b0c6abb` (draft PR #1) |
| Trading feature | `4c2438d97191ec780369b230e597c711471243ca` (draft PR #1) |
| CSSA readonly preflight | `a3125ce211e0c55d6608b39396f1f7633dbab72c` |

Each source checkout must have **exact pinned HEAD**, except the current
core checkout, which must descend from the C4.1 freeze. Tracked files
must be clean. A checkout cannot impersonate another checkout using the
same folder. **No network clone/fetch is done by the runner.**

## What actually runs

`scripts/v01_c42_local_crossrepo_probe_v0.py` launches three independent
Python subprocesses with a socket-level network block installed before
loading any domain packages:

1. GPS: loads the **actual** patched public `GpsX108Gate` normalizer and
   `gps_public_claim_guard_v0.py`, reads the historical exported FGI window C
   JSON, observes `RECORDED_RF_ATTACK` and validates quarantine of
   unsupported causal assertions, canonical mock `x108_gate=HOLD`,
   contradictory mock `x108_gate=BLOCK/verdict=ACT -> HOLD`.
2. Trading: imports **actual** `RealKX108Client`, `CycleEngine`,
   `ProofPolicy.REQUIRED` and `ReceiptStore`. A fake HTTP response returns
   `x108_gate=HOLD`; fake PAPER broker receives no order and a local receipt
   is persisted. A conflicting fake HTTP response cannot return
   `verdict=ACT`. No real kernel/broker API is contacted.
3. CSSA: loads **actual** F3H-H public-safe status JSON and confirms no
   internal mailbox, document authority, operational source, real
   promotions or pilot has been claimed.
4. Core: checks the three outputs against C4 allowed/forbidden claims
   and the pinned C4.1 freeze; any escalation => deterministic failure.

The runner prints a small JSON report with hashes and source SHAs; optional
`--output` persists that report OUTSIDE the repositories. It does not
persist secrets, email content, broker orders or GNSS raw samples.

When a clone/dependency is missing, SHA differs, sources have modifications,
any network operation is attempted, or any contract fails, the exit code is
nonzero and the printed status is **BLOCKED_FAIL_CLOSED**.

## Reproduction on Windows PowerShell

The following paths are examples for the fixed PC under
`Desktop\OBSIDIA_WORLDS`; adjust them if you already have checkouts.
The user already has `obsidia-v01-c1` locally, so **do not overwrite it**.

```powershell
$base = "$env:USERPROFILE\Desktop\OBSIDIA_WORLDS"
git -C "$base\obsidia-v01-c1" fetch origin feat/v01-c42-offline-interrepo-conformance-v0
git -C "$base\obsidia-v01-c1" worktree add --detach "$base\obsidia-v01-c42" origin/feat/v01-c42-offline-interrepo-conformance-v0

git clone --single-branch --branch feat/c41-gps-kernel-response-and-claim-boundary-v0 https://github.com/Eaubin08/obsidia-gps-defense-.git "$base\obsidia-gps-c41"
git clone --single-branch --branch test/c41-v01-paper-proof-convergence-v0 https://github.com/Eaubin08/OBSIDIA_TRADING.git "$base\obsidia-trading-c41"
git clone --single-branch --branch feat/f3h-h-cssa-real-readonly-pilot-preflight-v0 https://github.com/Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-.git "$base\obsidia-cssa-readonly"

python -m pip install pytest numpy requests
python "$base\obsidia-v01-c42\scripts\v01_c42_local_crossrepo_probe_v0.py" `
  --core-root "$base\obsidia-v01-c42" `
  --trading-root "$base\obsidia-trading-c41" `
  --gps-root "$base\obsidia-gps-c41" `
  --cssa-root "$base\obsidia-cssa-readonly" `
  --output "$base\v01-c42-local-report.json"
```

**Warning**: Git clone/fetch and pip installation are one-time *setup*
and use the network; the actual C4.2 probe itself is offline. Do not clone
over pre-existing local folders; use known, clean repos or a new directory.
Private repo access may require authorized GitHub credentials. The runner
does not request, receive, or log credentials.

## Actual CI vs unexecuted work

GitHub CI in the **core repo** runs the core runner's unit/adversarial
tests with synthetic probe outputs, compares pinned references, denies
network sockets, validates true absence/failure behavior and exercises
existing C4.1/C4/C3/C2/C1 tests. It does **not** have these three external
checkouts. Therefore a green core CI is **NOT** the actual cross-repo result.

Only the explicit local run with all three pinned repos may produce
`OFFLINE_CROSSREPO_CONTRACT_COMPOSITION_PASS_NO_LIVE_EXECUTION`.

A separate global parity manifest records that 11 named test failures
appear both **before C1** and through C4. The intermittent extra
`TestApprovalConcurrency` also occurred in the original baseline.
The global core CI is still red, and nothing in this lot changes it.

## Remaining gates

- Organizational authority, delegated rights and source-permission
  revocation enforced transactionally at the connector entry (C2).
- Actual cross-repo governed runtime for Trading PAPER with distinct
  **independent** kernel attestation and actual observed/sandbox results.
- GPS source-level contradiction `RECORDED_RF_ATTACK` must be resolved
  at its domain source with real controls, not only quarantined by viewers.
- CSSA real club internal READONLY source and human authorization are still
  absent. No promotion of private personal email to CSSA internal truth.
- No Monde/C5, no `main`/ `master` merge, no kernel mutation.
